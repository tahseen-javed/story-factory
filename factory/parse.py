"""script.md parser (stdlib only). See docs/SHOT_TAGS.md for the grammar."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Optional


class ScriptError(Exception):
    def __init__(self, msg: str, line: int = 0):
        super().__init__(f"line {line}: {msg}" if line else msg)
        self.line = line


@dataclass
class CharRef:
    id: str
    pose: str
    expr: str
    x: Optional[float] = None


@dataclass
class OverlaySpec:
    name: str
    args: list = field(default_factory=list)


@dataclass
class CamSpec:
    preset: str
    z0: float = 1.0
    z1: float = 1.0
    param: Optional[str] = None


@dataclass
class Shot:
    idx: int                      # global shot index (0-based)
    chapter: int
    location: str
    variant: str
    chars: list = field(default_factory=list)
    overlays: list = field(default_factory=list)
    camera: Optional[CamSpec] = None
    fx: list = field(default_factory=list)
    sfx: list = field(default_factory=list)
    track: dict = field(default_factory=dict)
    banner: Optional[str] = None
    cta: Optional[str] = None
    text: str = ""
    line: int = 0
    raw_fields: list = field(default_factory=list)

    @property
    def words(self) -> int:
        return len(re.findall(r"[A-Za-z0-9'’\-]+", self.text))


@dataclass
class Chapter:
    n: int
    time_card: str
    shots: list = field(default_factory=list)
    line: int = 0


@dataclass
class Script:
    title: str = ""
    length_min: float = 0.0
    voice: str = "default"
    characters: dict = field(default_factory=dict)   # id -> {"rig": str, "params": {..}}
    locations: dict = field(default_factory=dict)    # id -> description
    music_moods: dict = field(default_factory=dict)  # "CH1" -> mood
    chapters: list = field(default_factory=list)
    header_lines: dict = field(default_factory=dict)

    @property
    def shots(self):
        return [s for c in self.chapters for s in c.shots]

    @property
    def words(self) -> int:
        return sum(s.words for s in self.shots)


def split_top(s: str, sep: str = ",") -> list:
    """Split on sep at depth 0, outside quotes/parens/braces/brackets."""
    parts, cur, depth, quote = [], [], 0, None
    for ch in s:
        if quote:
            cur.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"“":
            quote = '"' if ch == '"' else "”"
            cur.append(ch)
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == sep and depth == 0:
            parts.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    tail = "".join(cur).strip()
    if tail or parts:
        parts.append(tail)
    return parts


def split_fields(body: str) -> list:
    """Split a shot line on ' | ' (pipe) at depth 0 outside quotes."""
    parts, cur, depth, quote = [], [], 0, None
    for ch in body:
        if quote:
            cur.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"“":
            quote = '"' if ch == '"' else "”"
            cur.append(ch)
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "|" and depth == 0:
            parts.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur).strip())
    return [p for p in parts if p != ""]


def parse_value(tok: str) -> Any:
    tok = tok.strip()
    if len(tok) >= 2 and tok[0] in "\"“" and tok[-1] in "\"”":
        return tok[1:-1]
    if re.fullmatch(r"[-+]?\d+", tok):
        return int(tok)
    if re.fullmatch(r"[-+]?\d*\.\d+", tok):
        return float(tok)
    return tok


def parse_call(text: str):
    """'name(a, "b", 3)' -> ('name', ['a','b',3]); 'name' -> ('name', [])."""
    text = text.strip()
    m = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\s*(?:\((.*)\))?", text, re.S)
    if not m:
        raise ScriptError(f"cannot parse call '{text}'")
    name, inner = m.group(1), m.group(2)
    args = [parse_value(a) for a in split_top(inner)] if inner and inner.strip() else []
    return name, args


def parse_track(val: str) -> dict:
    val = val.strip()
    if not (val.startswith("{") and val.endswith("}")):
        raise ScriptError(f"track must look like track:{{key:value}}, got '{val}'")
    out = {}
    for part in split_top(val[1:-1]):
        if not part:
            continue
        k, _, v = part.partition(":")
        out[k.strip()] = parse_value(v)
    return out


_CAM_RE = re.compile(r"^([a-z_]+)(?:\s+([0-9.]+)\s*>\s*([0-9.]+))?(?:\s+(.+))?$")


def parse_camera(val: str) -> CamSpec:
    m = _CAM_RE.match(val.strip())
    if not m:
        raise ScriptError(f"cannot parse cam '{val}' (expected: preset 1.00>1.15)")
    preset, z0, z1, param = m.groups()
    if z0 is None:
        if param is None:
            return CamSpec(preset, 1.0, 1.0)
        return CamSpec(preset, 1.0, 1.0, param)
    return CamSpec(preset, float(z0), float(z1), param)


_HEADER_KEYS = ("TITLE", "LENGTH_MIN", "VOICE", "CHARACTERS", "LOCATIONS", "MUSIC_MOODS")


def _parse_character(item: str, line: int):
    m = re.fullmatch(r"([a-z][a-z0-9_]*)\s*=\s*([a-z][a-z0-9_]*)\s*(?:\((.*)\))?", item.strip())
    if not m:
        raise ScriptError(f"bad CHARACTERS entry '{item}' (expected id=rig(param=value,...))", line)
    cid, rig, params = m.groups()
    pd = {}
    for p in split_top(params or ""):
        if p:
            k, _, v = p.partition("=")
            pd[k.strip()] = parse_value(v)
    return cid, {"rig": rig, "params": pd}


def parse(text: str) -> Script:
    sc = Script()
    lines = text.replace("\r\n", "\n").split("\n")
    i, n = 0, len(lines)
    cur_key = None
    # ---------- header ----------
    while i < n and not lines[i].startswith("## CH"):
        raw = lines[i]
        s = raw.strip()
        i += 1
        if not s or s.startswith("#") and not s.startswith("##"):
            continue
        m = re.match(r"^([A-Z_]+)\s*:\s*(.*)$", s)
        if m and m.group(1) in _HEADER_KEYS:
            cur_key, val = m.group(1), m.group(2).strip()
            sc.header_lines[cur_key] = i
            if cur_key == "TITLE":
                sc.title = val
            elif cur_key == "LENGTH_MIN":
                try:
                    sc.length_min = float(val)
                except ValueError:
                    raise ScriptError("LENGTH_MIN must be a number", i)
            elif cur_key == "VOICE":
                sc.voice = val or "default"
            elif val:
                _header_item(sc, cur_key, val, i)
            continue
        if s.startswith("- ") and cur_key in ("CHARACTERS", "LOCATIONS", "MUSIC_MOODS"):
            _header_item(sc, cur_key, s[2:].strip(), i)
            continue
        raise ScriptError(f"unexpected header line '{s}'", i)
    # ---------- body ----------
    ch: Optional[Chapter] = None
    shot: Optional[Shot] = None
    gidx = 0
    buf: list = []

    def flush():
        nonlocal buf, shot
        if shot is not None:
            shot.text = " ".join(x.strip() for x in buf if x.strip())
        buf = []

    while i < n:
        raw = lines[i]
        lineno = i + 1
        i += 1
        s = raw.strip()
        if s.startswith("## CH"):
            flush()
            shot = None
            m = re.match(r"^## CH(\d+)\s*\|\s*(.+)$", s)
            if not m:
                raise ScriptError("chapter must look like '## CH1 | FRIDAY 3:12 AM'", lineno)
            ch = Chapter(int(m.group(1)), m.group(2).strip(), line=lineno)
            sc.chapters.append(ch)
            continue
        if s.startswith("@"):
            flush()
            if ch is None:
                raise ScriptError("shot before first chapter", lineno)
            shot = _parse_shot(s[1:], gidx, ch.n, lineno)
            gidx += 1
            ch.shots.append(shot)
            continue
        if not s or s.startswith("//"):
            continue
        if shot is None:
            raise ScriptError(f"narration without a shot line: '{s[:40]}'", lineno)
        buf.append(s)
    flush()
    return sc


def _header_item(sc: Script, key: str, item: str, line: int):
    if key == "CHARACTERS":
        for part in split_top(item):
            cid, spec = _parse_character(part, line)
            sc.characters[cid] = spec
    elif key == "LOCATIONS":
        m = re.match(r"^([a-z][a-z0-9_]*)\s*:\s*(.+)$", item)
        if not m:
            raise ScriptError(f"bad LOCATIONS entry '{item}' (expected id: description)", line)
        sc.locations[m.group(1)] = m.group(2).strip()
    elif key == "MUSIC_MOODS":
        m = re.match(r"^(CH\d+)\s*:\s*([a-z_]+)$", item)
        if not m:
            raise ScriptError(f"bad MUSIC_MOODS entry '{item}' (expected CH1: tense)", line)
        sc.music_moods[m.group(1)] = m.group(2)


def _parse_shot(body: str, idx: int, chapter: int, line: int) -> Shot:
    fields = split_fields(body)
    if not fields:
        raise ScriptError("empty shot line", line)
    loc = fields[0]
    m = re.fullmatch(r"([a-z][a-z0-9_]*)(?:\.([a-z]+))?", loc)
    if not m:
        raise ScriptError(f"first field must be location.variant, got '{loc}'", line)
    shot = Shot(idx=idx, chapter=chapter, location=m.group(1), variant=m.group(2) or "day", line=line, raw_fields=fields)
    for f in fields[1:]:
        key, sep, val = f.partition(":")
        key, val = key.strip(), val.strip()
        if not sep:
            raise ScriptError(f"field '{f}' needs key:value", line)
        if key == "ov":
            name, args = parse_call(val)
            shot.overlays.append(OverlaySpec(name, args))
        elif key == "cam":
            shot.camera = parse_camera(val)
        elif key == "fx":
            shot.fx += [x.strip() for x in val.split(",") if x.strip()]
        elif key == "sfx":
            shot.sfx += [x.strip() for x in val.split(",") if x.strip()]
        elif key == "track":
            shot.track.update(parse_track(val))
        elif key == "banner":
            shot.banner = parse_value(val) if val[:1] in "\"“" else val
        elif key == "cta":
            shot.cta = val
        else:  # character: pose/expr[@x]
            cm = re.fullmatch(r"([a-z_]+)\s*/\s*([a-z_]+)(?:\s*@\s*(left|center|right|[0-9.]+))?", val)
            if not cm:
                raise ScriptError(f"character field '{f}' must be id:pose/expression[@left|center|right|0.35]", line)
            xs = cm.group(3)
            x = {"left": 0.30, "center": 0.5, "right": 0.70}.get(xs) if xs in ("left", "center", "right") else (float(xs) if xs else None)
            shot.chars.append(CharRef(key, cm.group(1), cm.group(2), x))
    return shot

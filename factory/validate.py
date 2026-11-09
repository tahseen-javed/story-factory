"""Script gate + vocabulary validator (stdlib only).  Usage: python -m factory.validate jobs/<slug>  (or pilot/<slug>)"""
from __future__ import annotations

import os
import re
import statistics
import sys
from dataclasses import dataclass

from . import miniyaml, vocab
from .parse import ScriptError, parse
from .textutil import count_numbers, count_words, estimate_seconds, fk_grade, split_sentences

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@dataclass
class Issue:
    level: str   # error | warn
    code: str
    msg: str
    line: int = 0

    def __str__(self):
        loc = f" (line {self.line})" if self.line else ""
        return f"{self.level.upper():5} {self.code}: {self.msg}{loc}"


def load_cfg():
    """factory.yaml plus the v2 data files (style.yaml, pacing.yaml, audio.yaml); audio.yaml overrides cfg["audio"] keys."""
    cfg = miniyaml.load_file(os.path.join(ROOT, "config", "factory.yaml"))
    for name in ("style", "pacing", "audio", "qa_calibration", "characters"):
        p = os.path.join(ROOT, "config", f"{name}.yaml")
        if os.path.exists(p):
            data = miniyaml.load_file(p) or {}
            if name == "audio":
                cfg["audio"] = {**cfg.get("audio", {}), **data}
            else:
                cfg[name] = data
    return cfg


def load_prefs():
    p = os.path.join(ROOT, "config", "preferences.yaml")
    return miniyaml.load_file(p) if os.path.exists(p) else {}


def job_mode(path: str) -> str:
    norm = path.replace("\\", "/")
    return "pilot" if "/pilot/" in "/" + norm.strip("/") + "/" or norm.startswith("pilot/") else "job"


def validate_dir(job_dir: str, cfg=None, prefs=None):
    cfg = cfg or load_cfg()
    prefs = prefs or load_prefs()
    issues: list = []
    script_path = os.path.join(job_dir, "script.md")
    if not os.path.exists(script_path):
        return [Issue("error", "missing-script", f"{script_path} not found")], None
    with open(script_path, "r", encoding="utf-8") as fh:
        raw = fh.read()
    if raw.startswith("\x00GITCRYPT"):
        return [Issue("error", "locked", "script.md is still encrypted (git-crypt locked)")], None
    try:
        sc = parse(raw)
    except ScriptError as e:
        return [Issue("error", "parse", str(e))], None
    mode = job_mode(job_dir)
    _v4, _test = False, False
    if os.path.exists(os.path.join(job_dir, "job.yaml")):
        _jy = miniyaml.load_file(os.path.join(job_dir, "job.yaml")) or {}
        _v4 = int(_jy.get("style_version", 1)) >= 4
        _test = str(_jy.get("kind", "")) == "test"   # owner-approved test exception (short video): format-length rules are skipped, vocabulary and safety rules stay
    if _test:
        mode = "test"
    issues += validate_script(sc, raw, cfg, prefs, mode, _v4)
    if not _test:
        issues += validate_facts(job_dir, sc, cfg)
    return issues, sc


def _err(issues, code, msg, line=0):
    issues.append(Issue("error", code, msg, line))


def _warn(issues, code, msg, line=0):
    issues.append(Issue("warn", code, msg, line))


def validate_script(sc, raw: str, cfg: dict, prefs: dict, mode: str = "job", v4: bool = False) -> list:
    I: list = []
    test = mode == "test"
    sconf, cam, shotsc = cfg["script"], cfg["camera"], cfg["shots"]
    wpm = float(sconf["wpm"])

    # ---------- header ----------
    if not sc.title:
        _err(I, "header", "TITLE missing")
    min_len = sconf["min_len_min"]   # P-011: the 4-minute format is the channel format
    if not test and not (min_len <= sc.length_min <= sconf["max_len_min"]):
        _err(I, "length", f"LENGTH_MIN {sc.length_min} outside {min_len}-{sconf['max_len_min']}")
    if sc.voice not in ("default", "me"):
        _err(I, "voice", f"VOICE must be default or me, got '{sc.voice}'")
    if not sc.characters:
        _err(I, "header", "CHARACTERS missing")
    if not sc.locations:
        _err(I, "header", "LOCATIONS missing")
    if not sc.chapters:
        _err(I, "structure", "no chapters (## CH1 | TIME CARD)")
        return I
    for mname in sc.music_moods.values():
        if mname not in vocab.MUSIC_MOODS:
            _err(I, "music", f"unknown mood '{mname}'.{vocab.suggest(mname, vocab.MUSIC_MOODS)}")
    for ch in sc.chapters:
        if f"CH{ch.n}" not in sc.music_moods:
            _warn(I, "music", f"CH{ch.n} has no MUSIC_MOODS entry (default 'tense')")

    # ---------- prompt denylist (location descriptions feed image prompts) ----------
    for lid, desc in sc.locations.items():
        low = desc.lower()
        for bad in vocab.PROMPT_DENYLIST:
            if re.search(r"\b" + re.escape(bad) + r"\b", low):
                _err(I, "denylist", f"location '{lid}' mentions '{bad}' (no artists/studios/brands/people/characters in image prompts)")

    # ---------- shots ----------
    prefs_banned = [w.lower() for w in ((prefs.get("script") or {}).get("banned_words") or [])]
    total_words = sc.words
    cum = 0
    cta_shots, banner_words, end_screens = [], [], 0
    est_durations = []
    for ch in sc.chapters:
        if not ch.shots:
            _err(I, "structure", f"CH{ch.n} has no shots", ch.line)
        if not any(s.track for s in ch.shots):
            _err(I, "tracker", f"CH{ch.n}: tracker not updated (add track:{{key:value}} to a shot)", ch.line)
        for s in ch.shots:
            L = s.line
            if s.location not in sc.locations and s.location != "insert":
                _err(I, "location", f"location '{s.location}' not declared in LOCATIONS", L)
            if s.variant not in vocab.VARIANTS:
                _err(I, "variant", f"variant '{s.variant}'.{vocab.suggest(s.variant, vocab.VARIANTS)}", L)
            if len(s.chars) > 3:
                _err(I, "chars", "max 3 characters per shot", L)
            for c in s.chars:
                if c.id not in sc.characters:
                    _err(I, "char", f"character '{c.id}' not declared in CHARACTERS", L)
                if c.pose not in vocab.POSES:
                    _err(I, "pose", f"pose '{c.pose}'.{vocab.suggest(c.pose, vocab.POSES)}", L)
                if c.expr not in vocab.EXPRESSIONS:
                    _err(I, "expr", f"expression '{c.expr}'.{vocab.suggest(c.expr, vocab.EXPRESSIONS)}", L)
            if len(s.overlays) > 1:
                _err(I, "overlay", "max 1 overlay at a time per shot", L)
            for ov in s.overlays:
                if ov.name not in vocab.OVERLAYS:
                    _err(I, "overlay", f"overlay '{ov.name}'.{vocab.suggest(ov.name, vocab.OVERLAYS)}", L)
                else:
                    lo, hi = vocab.OVERLAYS[ov.name]
                    if not (lo <= len(ov.args) <= hi):
                        _err(I, "overlay-args", f"{ov.name} takes {lo}-{hi} args, got {len(ov.args)}", L)
                if ov.name == "end_screen":
                    end_screens += 1
            if s.camera:
                if s.camera.preset not in vocab.CAMERA:
                    _err(I, "camera", f"cam '{s.camera.preset}'.{vocab.suggest(s.camera.preset, vocab.CAMERA)}", L)
                for z in (s.camera.z0, s.camera.z1):
                    if not (cam["zoom_min"] <= z <= cam["zoom_max"]):
                        _err(I, "zoom", f"zoom {z} outside {cam['zoom_min']}-{cam['zoom_max']}", L)
            for f in s.fx:
                if f not in vocab.FX:
                    _err(I, "fx", f"fx '{f}'.{vocab.suggest(f, vocab.FX)}", L)
            for f in s.sfx:
                if f not in vocab.SFX:
                    _err(I, "sfx", f"sfx '{f}'.{vocab.suggest(f, vocab.SFX)}", L)
            if s.cta:
                if s.cta not in vocab.CTA_VALUES:
                    _err(I, "cta", f"cta '{s.cta}' (only 'subscribe')", L)
                else:
                    cta_shots.append((s, cum))
                    if "subscribe" not in s.text.lower():
                        _err(I, "cta", "cta:subscribe shot narration must contain a spoken 'subscribe' sentence", L)
            if s.banner:
                banner_words.append((s, cum))
            # narration checks
            if not s.text:
                _err(I, "narration", "shot has no narration", L)
            low = s.text.lower()
            for bad in vocab.CONTENT_BLOCKLIST + tuple(prefs_banned):
                if re.search(r"\b" + re.escape(bad) + r"\b", low):
                    _err(I, "content", f"blocked term '{bad}' (advertiser-friendly / preference rule)", L)
            nsent = len(split_sentences(s.text))
            if nsent > 4:
                _warn(I, "density", f"{nsent} sentences in one shot (target 2-3)", L)
            dur = estimate_seconds(s.text, wpm)
            est_durations.append(dur)
            inner = bool(s.overlays) or (s.camera and s.camera.preset in ("hold", "parallax_drift", "rack_focus")) or bool(s.chars)
            for fh_ in s.fr:
                if fh_ not in vocab.FRAMINGS:
                    _err(I, "framing", f"fr '{fh_}'.{vocab.suggest(fh_, vocab.FRAMINGS)}", L)
            if test:
                cum += s.words
                continue
            if dur > shotsc["max_s"] and not inner:
                _err(I, "shot-long", f"shot ~{dur:.1f}s > {shotsc['max_s']}s without inner animation", L)
            elif dur > shotsc["max_s"] + 2.5:
                _err(I, "shot-long", f"shot ~{dur:.1f}s is too long even with inner animation; split it", L)
            if dur < shotsc["min_s"]:
                _err(I, "shot-short", f"shot ~{dur:.1f}s < {shotsc['min_s']}s", L)
            cum += s.words

    if test:
        return I

    # ---------- word budget ----------
    target = wpm * sc.length_min
    tol = sconf["wpm_tolerance"]
    if not (target * (1 - tol) <= total_words <= target * (1 + tol)):
        _err(I, "words", f"{total_words} words; need {target:.0f} +-{int(tol*100)}% ({target*(1-tol):.0f}-{target*(1+tol):.0f})")

    # ---------- hook ----------
    first = sc.shots[0] if sc.shots else None
    if first:
        low = first.text.lower()
        for g in vocab.GREETINGS:
            if g in low:
                _err(I, "hook", f"first shot starts with a greeting/intro ('{g}')", first.line)
        words_seq = " ".join(s.text for s in sc.shots)
        minute1 = " ".join(words_seq.split()[: int(wpm)])
        if count_numbers(minute1) < 3:
            _err(I, "hook", "minute 1 needs at least 3 concrete numbers")
        if "?" not in minute1:
            _err(I, "hook", "minute 1 needs one big open question (a '?')")
        # v2 hook: the first 2 sentences need a concrete number or a stakes word
        h2 = " ".join(split_sentences(words_seq)[:2]).lower()
        stakes = ("die", "dead", "lose", "lost", "last", "only", "alive", "trapped", "minutes", "seconds", "left", "dark", "never", "swore")
        if count_numbers(h2) < 1 and not any(re.search(r"\b" + w + r"\b", h2) for w in stakes):
            _err(I, "hook", "first 2 sentences need a concrete number or a consequence/stakes word")
    lo_w, hi_w = int(wpm / 60 * 18), int(wpm / 60 * 42)
    if not banner_words:
        _err(I, "hook", "flash-forward banner missing (banner:\"N DAYS FROM NOW\" at 20-40 s)")
    elif not any(lo_w <= w <= hi_w for _, w in banner_words):
        _warn(I, "hook", f"banner not at 20-40 s (shot starts at word {banner_words[0][1]}, want {lo_w}-{hi_w})", banner_words[0][0].line)

    # v2.1 hook rubric: 3 scored options, the picked one is the best and clears the floor
    from . import hookscore

    opts, pick = hookscore.parse_options(raw)
    if len(opts) < 3 or pick not in opts:
        _err(I, "hook-options", "need '// HOOKOPT 1|2|3 | text' (3 options) and '// HOOKPICK n'")
    else:
        sc_ = {n: hookscore.score(t)["total"] for n, t in opts.items()}
        if sc_[pick] < max(sc_.values()) - 1e-9 or sc_[pick] < float(((prefs.get("hooks") or {}).get("min_score", 6.0))):
            _err(I, "hook-options", f"picked option {pick} scores {sc_[pick]} (scores {sc_}); pick the best and reach the floor")

    # ---------- CTA / end screen ----------
    if v4:   # P-011: one soft subscribe line at 45-60% and one at the end, never in the first 20 s; hook inside the problem; one short last line
        if len(cta_shots) != 2:
            _err(I, "cta", f"need exactly two cta:subscribe shots (45-60% and the end), found {len(cta_shots)}")
        else:
            f1, f2 = (cta_shots[0][1] / max(1, total_words)), (cta_shots[1][1] / max(1, total_words))
            if not (float(sconf["cta_v4_min"]) <= f1 <= float(sconf["cta_v4_max"])):
                _err(I, "cta", f"first subscribe line at {f1*100:.0f}%; need 45-60%", cta_shots[0][0].line)
            if f2 < 0.88:
                _err(I, "cta", f"closing subscribe line at {f2*100:.0f}%; it belongs at the end (88%+)", cta_shots[1][0].line)
        if not re.search(r"^//\s*LASTLINE\b", raw, re.M):
            _err(I, "lastline", "add '// LASTLINE' before the final shot (one memorable last line)")
        last_s = (split_sentences(sc.shots[-1].text) or [""])[-1] if sc.shots else ""
        if count_words(last_s) > 14:
            _err(I, "lastline", f"last line has {count_words(last_s)} words; keep it to 14 or fewer")
        first2 = " ".join(split_sentences(" ".join(s.text for s in sc.shots))[:2])
        if count_words(first2) > 26:
            _err(I, "hook", f"first 2 sentences have {count_words(first2)} words; the hook must land inside 8 s (26 words max)")
    elif len(cta_shots) != 1:
        _err(I, "cta", f"need exactly one cta:subscribe shot, found {len(cta_shots)}")
    else:
        frac = cta_shots[0][1] / max(1, total_words)
        if not (sconf["cta_min"] <= frac <= sconf["cta_max"]):
            _err(I, "cta", f"cta at {frac*100:.0f}% of runtime; need {int(sconf['cta_min']*100)}-{int(sconf['cta_max']*100)}%", cta_shots[0][0].line)
    if end_screens:
        _err(I, "end-screen", "frozen end card removed in v2 (P-002): no ov:end_screen; the last scene keeps animating")

    # ---------- chapters ----------
    cmin = 55
    for ch in sc.chapters:
        secs = sum(s.words for s in ch.shots) / (wpm / 60)
        last = ch is sc.chapters[-1]
        if not (cmin <= secs <= sconf["chapter_max_s"]) and not (last and secs <= sconf["chapter_max_s"] + 30):
            _err(I, "chapter-len", f"CH{ch.n} is ~{secs:.0f}s; need {cmin}-{sconf['chapter_max_s']}s", ch.line)
    if mode == "job" and sc.length_min >= 10:
        want = round(sc.length_min * 60 / 120)
        if abs(len(sc.chapters) - want) > 2:
            _warn(I, "chapter-count", f"{len(sc.chapters)} chapters for {sc.length_min} min (about {want} expected)")

    # ---------- shot rhythm ----------
    if est_durations:
        med = statistics.median(est_durations)
        if not (2.4 <= med <= 6.0):
            _err(I, "rhythm", f"median shot ~{med:.1f}s; target ~{shotsc['median_target_s']}s (2.4-6.0 accepted)")
        n1 = [d for d in est_durations[: max(6, len(est_durations) // 12)]]
        if n1 and statistics.median(n1) > 4.6:
            _warn(I, "rhythm", "first minute should be denser (median shot <= ~3.5-4.5 s)")

    # ---------- readability / repetition ----------
    full = " ".join(s.text for s in sc.shots)
    grade = fk_grade(full)
    if grade > 9.5:
        _warn(I, "reading", f"Flesch-Kincaid grade {grade:.1f} (aim for <= 9)")
    sents = [x.lower() for x in split_sentences(full)]
    for x in sents:
        if re.match(r"(so|well|basically|okay|anyway)\b", x):
            _err(I, "filler", f"filler opener: '{x[:30]}'")
    starts = [x.split()[0] for x in sents if x.split()]
    for k in range(len(starts) - 2):
        if starts[k] == starts[k + 1] == starts[k + 2]:
            _err(I, "repeat-start", f"3 sentences in a row start with '{starts[k]}'")
    wl = [count_words(x) for x in sents]
    if wl and not (min(wl) <= 4 and max(wl) >= 14):
        _warn(I, "variety", "mix short (<=4 words) and long (>=14 words) sentences")
    dups = {x for x in sents if sents.count(x) > 1 and count_words(x) > 3}
    for d in sorted(dups):
        _err(I, "repeat", f"repeated sentence: '{d[:60]}'")

    # ---------- self-attested craft markers (comments in script.md) ----------
    I += _markers(raw, sc, mode)
    return I


def _markers(raw: str, sc, mode: str) -> list:
    I: list = []
    loops_open, loops_close, plants, payoffs, cliffs = set(), set(), set(), set(), set()
    ritual_chapters, beats, twist = set(), 0, 0
    ch = 0
    total = max(1, sc.words)
    cum, acts, interrupts, silences = 0, {}, [], 0
    for ln in raw.split("\n"):
        m = re.match(r"^## CH(\d+)", ln)
        if m:
            ch = int(m.group(1))
            continue
        if ch and ln.strip() and not ln.strip().startswith(("//", "@")):
            cum += len(re.findall(r"[A-Za-z0-9'’\-]+", ln))
        ma = re.match(r"^//\s*(ACT|INTERRUPT|SILENCE)\b\s*(\w*)", ln.strip())
        if ma:
            if ma.group(1) == "ACT":
                acts[ma.group(2)] = cum / total
            elif ma.group(1) == "INTERRUPT":
                interrupts.append(cum)
            else:
                silences += 1
            continue
        m = re.match(r"^//\s*([A-Z]+)\b\s*(.*)$", ln.strip())
        if not m:
            continue
        kind = m.group(1)
        toks = [t.strip(":,|") for t in m.group(2).split() if t.strip(":,|")]
        if kind == "LOOP":
            if len(toks) >= 2 and toks[0] in ("open", "close"):
                (loops_open if toks[0] == "open" else loops_close).add(toks[1])
        elif kind == "PLANT":
            plants.add(toks[0] if toks else "?")
        elif kind == "PAYOFF":
            payoffs.add(toks[0] if toks else "?")
        elif kind == "CLIFF":
            cliffs.add(ch)
        elif kind == "RITUAL":
            ritual_chapters.add(ch)
        elif kind == "BEAT":
            beats += 1
        elif kind == "TWIST":
            twist += 1
    need_loops = 3 if mode == "job" else 2
    need_plants = 3 if mode == "job" else 2
    if len(loops_open) < need_loops:
        I.append(Issue("error", "loops", f"need >= {need_loops} open loops (// LOOP open <id>: text); found {len(loops_open)}"))
    if len(plants) < need_plants or not plants <= payoffs:
        I.append(Issue("error", "plants", f"need >= {need_plants} planted details each paid off (// PLANT <id> ... // PAYOFF <id> ...); plants={sorted(plants)} payoffs={sorted(payoffs)}"))
    n = len(sc.chapters)
    for c in sc.chapters:
        if c.n not in ritual_chapters:
            I.append(Issue("error", "ritual", f"CH{c.n}: missing '// RITUAL' marker (recurring opener)", c.line))
        if c.n != sc.chapters[-1].n and c.n not in cliffs:
            I.append(Issue("error", "cliffhanger", f"CH{c.n}: missing '// CLIFF' marker (chapter must end on a cliffhanger)", c.line))
    # v2 story engine: acts present, in order, at the right place; pattern interrupts; silence beats
    want = {"hook": (0, 0.01), "act1": (0.02, 0.16), "act2a": (0.14, 0.28), "midpoint": (0.40, 0.58), "act2b": (0.48, 0.68),
            "sacrifice": (0.55, 0.84), "climax": (0.74, 0.92), "resolution": (0.88, 0.99)}
    for a, (lo, hi) in want.items():
        if a not in acts:
            I.append(Issue("error", "act", f"missing '// ACT {a}' marker"))
        elif not (lo <= acts[a] <= hi):
            I.append(Issue("error", "act", f"ACT {a} at {acts[a]*100:.0f}% of the story; expected {int(lo*100)}-{int(hi*100)}%"))
    order = [acts[a] for a in want if a in acts]
    if order != sorted(order):
        I.append(Issue("error", "act", "ACT markers are out of order"))
    secs = total / 2.83
    need_int = max(1, int(secs / 40))
    gaps = [b - a for a, b in zip([0] + interrupts, interrupts + [total])]
    if len(interrupts) < need_int or (gaps and max(gaps) / 2.83 > 75):
        I.append(Issue("error", "interrupt", f"need a '// INTERRUPT <kind>' pattern interrupt about every 35 s (found {len(interrupts)}, need >= {need_int}, longest gap {max(gaps)/2.83:.0f}s)"))
    if silences < 3:
        I.append(Issue("error", "silence", f"need >= 3 '// SILENCE' beats before reveals, found {silences}"))
    if beats < 1:
        I.append(Issue("error", "beat", "need an emotional beat before the climax (// BEAT emotional: ...)"))
    if twist < 1:
        I.append(Issue("error", "twist", "need a twist ending tied to the opening (// TWIST: ...)"))
    return I


_FACT_RE = re.compile(r"^\s*-\s+(.*?)\s*\|\s*(https://\S+)\s*$")


def validate_facts(job_dir: str, sc, cfg: dict) -> list:
    I: list = []
    path = None
    for name in ("facts.md", "sources.md"):
        p = os.path.join(job_dir, name)
        if os.path.exists(p):
            path = p
            break
    if not path:
        return [Issue("error", "facts", "facts.md (or sources.md in pilot/) missing")]
    with open(path, "r", encoding="utf-8") as fh:
        txt = fh.read()
    if txt.startswith("\x00GITCRYPT"):
        return [Issue("error", "locked", "facts.md is still encrypted")]
    n = 0
    for i, ln in enumerate(txt.split("\n"), 1):
        if ln.strip().startswith("~ "):   # guidance without a number: still needs a source URL
            if not re.search(r"\|\s*https://\S+\s*$", ln):
                I.append(Issue("error", "fact-source", "guidance line needs '| https://source'", i))
            continue
        if ln.strip().startswith("- "):
            m = _FACT_RE.match(ln)
            if not m:
                I.append(Issue("error", "fact-format", "fact must be '- <fact with exact number> | https://source'", i))
                continue
            if not re.search(r"\d", m.group(1)):
                I.append(Issue("error", "fact-number", "fact needs an exact number", i))
            n += 1
    need = max(1, -(-int(cfg["script"]["min_facts_per_10min"] * sc.length_min) // 10))
    if n < need:
        I.append(Issue("error", "facts", f"{n} sourced facts; need >= {need} for {sc.length_min} min"))
    return I


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv:
        print("usage: python -m factory.validate <jobs/slug | pilot/slug>")
        return 2
    rc = 0
    for d in argv:
        issues, sc = validate_dir(d)
        errs = [i for i in issues if i.level == "error"]
        warns = [i for i in issues if i.level == "warn"]
        words = sc.words if sc else 0
        print(f"{d}: {len(errs)} errors, {len(warns)} warnings, {words} words")
        for i in (errs + warns)[:30]:
            print("  " + str(i))
        if errs:
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())

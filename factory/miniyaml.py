"""Tiny YAML-subset reader (stdlib only) so the local validator works without PyYAML.

Supports: nested mappings by 2+ space indentation, "- item" lists (scalars or "key: value" maps),
inline lists [a, b], inline maps {a: 1}, scalars (int, float, bool, null, quoted or bare strings), # comments.
If PyYAML is importable it is used instead (full YAML).
"""
from __future__ import annotations

import re
from typing import Any


def load(text: str) -> Any:
    try:  # full YAML when available (CI)
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ImportError:
        pass
    lines = []
    for raw in text.splitlines():
        stripped = _strip_comment(raw).rstrip()
        if stripped.strip() == "":
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        lines.append((indent, stripped.strip()))
    value, _ = _parse_block(lines, 0, lines[0][0] if lines else 0)
    return value


def load_file(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return load(fh.read())


def _strip_comment(line: str) -> str:
    out, quote = [], None
    for i, ch in enumerate(line):
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            out.append(ch)
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            break
        else:
            out.append(ch)
    return "".join(out)


def _scalar(tok: str) -> Any:
    tok = tok.strip()
    if tok == "" or tok in ("~", "null", "Null", "NULL"):
        return None
    if tok in ("true", "True", "TRUE"):
        return True
    if tok in ("false", "False", "FALSE"):
        return False
    if (tok.startswith('"') and tok.endswith('"') and len(tok) >= 2) or (
        tok.startswith("'") and tok.endswith("'") and len(tok) >= 2
    ):
        return tok[1:-1]
    if tok.startswith("[") and tok.endswith("]"):
        inner = tok[1:-1].strip()
        return [_scalar(p) for p in _split_top(inner)] if inner else []
    if tok.startswith("{") and tok.endswith("}"):
        inner = tok[1:-1].strip()
        result = {}
        for part in _split_top(inner) if inner else []:
            k, _, v = part.partition(":")
            result[k.strip()] = _scalar(v)
        return result
    if re.fullmatch(r"[-+]?\d+", tok):
        return int(tok)
    if re.fullmatch(r"[-+]?(\d+\.\d*|\.\d+|\d+)([eE][-+]?\d+)?", tok):
        return float(tok)
    return tok


def _split_top(s: str) -> list[str]:
    parts, depth, quote, cur = [], 0, None, []
    for ch in s:
        if quote:
            cur.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    if cur:
        parts.append("".join(cur))
    return parts


def _split_key(text: str):
    """Split 'key: value' at the first colon outside quotes. Returns (key, value) or None."""
    quote = None
    for i, ch in enumerate(text):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == ":" and (i + 1 == len(text) or text[i + 1] == " "):
            return text[:i].strip().strip("\"'"), text[i + 1 :].strip()
    return None


def _parse_block(lines, i, indent):
    if i >= len(lines):
        return None, i
    if lines[i][1].startswith("- ") or lines[i][1] == "-":
        return _parse_list(lines, i, lines[i][0])
    return _parse_map(lines, i, lines[i][0])


def _parse_map(lines, i, indent):
    result = {}
    while i < len(lines) and lines[i][0] == indent and not lines[i][1].startswith("- "):
        kv = _split_key(lines[i][1])
        if kv is None:
            raise ValueError(f"miniyaml: cannot parse line: {lines[i][1]!r}")
        key, val = kv
        i += 1
        if val == "":
            if i < len(lines) and lines[i][0] > indent:
                child, i = _parse_block(lines, i, lines[i][0])
                result[key] = child
            elif i < len(lines) and lines[i][0] == indent and lines[i][1].startswith("- "):
                child, i = _parse_list(lines, i, indent)
                result[key] = child
            else:
                result[key] = None
        else:
            result[key] = _scalar(val)
    return result, i


def _parse_list(lines, i, indent):
    result = []
    while i < len(lines) and lines[i][0] == indent and (lines[i][1].startswith("- ") or lines[i][1] == "-"):
        body = lines[i][1][1:].strip()
        i += 1
        if body == "":
            if i < len(lines) and lines[i][0] > indent:
                child, i = _parse_block(lines, i, lines[i][0])
                result.append(child)
            else:
                result.append(None)
            continue
        kv = _split_key(body)
        if kv is not None and not body.startswith(("[", "{", '"', "'")):
            item = {kv[0]: _scalar(kv[1]) if kv[1] != "" else None}
            sub_indent = indent + 2
            while i < len(lines) and lines[i][0] >= sub_indent and not lines[i][1].startswith("- "):
                k2 = _split_key(lines[i][1])
                if k2 is None:
                    break
                item[k2[0]] = _scalar(k2[1]) if k2[1] != "" else None
                i += 1
            result.append(item)
        else:
            result.append(_scalar(body))
    return result, i

"""P-008 B: cute + unique casts. Stdlib only.

cute_check: head-to-body ratio, eye size, rounded/warm style, banned scary words (enforced for style_version >= 3).
unique_check: cast signature similarity against every earlier video in library/history.json (fail above the threshold).
"""
from __future__ import annotations

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYS = ("outfit", "hat", "hair", "age", "skin", "hairColor", "pants", "prop")


def char_sig(params: dict) -> str:
    return "|".join(f"{k}={params.get(k, '')}" for k in KEYS)


def cast_sigs(characters: dict) -> list:
    return sorted(char_sig(c.get("params", {})) for c in characters.values())


def jaccard(a, b) -> float:
    a, b = set(a), set(b)
    return len(a & b) / max(1, len(a | b))


def cute_metrics(params: dict, style: dict, defaults_applied: bool = True) -> dict:
    ch = style["characters"]
    rig = ch["rig"]
    hs = float(params.get("headScale", ch["head_scale"] if defaults_applied else 1.0))
    es = float(params.get("eyeScale", ch["eye_scale"] if defaults_applied else 1.0))
    head = rig["head_height"] * hs
    body = rig["body_height"] + rig["head_height"] * (hs - 1)
    return {"head_to_body": round(head / body, 3), "eye_to_head": round(rig["eye_height"] * es / rig["head_height"], 3)}


def cute_check(characters: dict, style: dict, text: str = "", enforce: bool = True) -> dict:
    ch = style["characters"]
    rows, ok = {}, True
    for cid, c in characters.items():
        m = cute_metrics(c.get("params", {}), style, defaults_applied=enforce)
        good = m["head_to_body"] >= ch["head_to_body_min"] and m["eye_to_head"] >= ch["eye_to_head_min"]
        rows[cid] = {**m, "ok": good}
        ok = ok and good
    blob = (json.dumps(characters) + " " + text).lower()
    banned = [w for w in ch["banned_words"] if re.search(r"\b" + re.escape(w.replace("_", " ")) + r"\b", blob.replace("_", " "))]
    return {"ok": ok and not banned and bool(ch.get("rounded")), "enforced": enforce, "characters": rows, "banned_found": banned}


def load_history(path: str | None = None) -> list:
    p = path or os.path.join(ROOT, "library", "history.json")
    try:
        txt = open(p, encoding="utf-8").read()
        return [] if txt.startswith("\x00GITCRYPT") else json.loads(txt)
    except Exception:  # noqa: BLE001 - unreadable (locked) history is reported, never fatal
        return []


def unique_check(characters: dict, shots_sig: list, history: list, style: dict, nnn=None) -> dict:
    ch = style["characters"]
    mine = cast_sigs(characters)
    worst_cast, worst_shots, vs, same_char = 0.0, 0.0, None, []
    for h in history:
        if nnn is not None and h.get("nnn") == nnn:
            continue
        c = jaccard(mine, h.get("cast", []))
        s = jaccard(zip(shots_sig, shots_sig[1:], shots_sig[2:]), zip(h.get("shots_sig", []), h.get("shots_sig", [])[1:], h.get("shots_sig", [])[2:])) if h.get("shots_sig") else 0.0
        if max(c, s) >= max(worst_cast, worst_shots):
            vs = h.get("short_title") or h.get("nnn")
        worst_cast, worst_shots = max(worst_cast, c), max(worst_shots, s)
        same_char += [x for x in mine if x in h.get("cast", [])]
    return {"ok": worst_cast < ch["cast_similarity_max"] and worst_shots < ch["shot_similarity_max"] and not same_char,
            "cast_similarity": round(worst_cast, 3), "shot_similarity": round(worst_shots, 3), "closest": vs, "identical_characters": sorted(set(same_char)),
            "compared": len(history), "note": "" if history else "history not readable or empty (locked git-crypt or first video)"}


def log_history(nnn: int, characters: dict, shots_sig: list, path: str | None = None) -> None:
    p = path or os.path.join(ROOT, "library", "history.json")
    hist = load_history(p)
    for h in hist:
        if h.get("nnn") == nnn:
            h["cast"], h["shots_sig"] = cast_sigs(characters), shots_sig
    json.dump(hist, open(p, "w", encoding="utf-8"), indent=1)

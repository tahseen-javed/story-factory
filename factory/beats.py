"""Pacing v2 helpers (stdlib only): split shots into beats <= 5 s, then pick framing, camera recipe, transition, acting and captions per beat.

All functions are pure and deterministic (seeded random.Random), so re-runs give identical timelines.
"""
from __future__ import annotations

import math
import re

LOW_CAM = ["pull", "pan_l", "pan_r", "parallax_drift", "push", "tilt_up"]
MID_CAM = ["push", "parallax_drift", "rack_focus", "dutch", "pan_l", "pan_r", "tilt_down"]
HIGH_CAM = ["shake_medium", "push", "whip_to", "dutch", "shake_light"]
CAM_SPEED = {0: 0.030, 1: 0.050, 2: 0.070}

EXPR_ALT = {
    "scared": ["scared", "shocked", "worried"], "shocked": ["shocked", "scared", "worried"], "worried": ["worried", "sad", "scared", "neutral"],
    "determined": ["determined", "worried", "angry"], "sad": ["sad", "worried", "sleepy"], "sleepy": ["sleepy", "worried"],
    "relieved": ["relieved", "neutral", "sly"], "neutral": ["neutral", "worried", "relieved"], "angry": ["angry", "determined"], "sly": ["sly", "neutral"],
}
POSE_ALT = {"stand": ["stand", "point", "hands_up", "stand"], "point": ["point", "stand"], "sit": ["sit"], "sit_bed": ["sit_bed"]}
POSE_KEYWORDS = [(r"\b(look up|sky|sun)\b", "hands_up"), (r"\b(point|there)\b", "point"), (r"\b(hide|duck)\b", "crouch")]


def split_beats(t0: float, t1: float, cands: list, pc: dict) -> list:
    """Split [t0,t1] seconds into beats. cands = [(time, weight)] natural cut points (sentence starts 1.0, clauses 0.6)."""
    L = t1 - t0
    if L <= pc["soft_max_s"]:
        return [(t0, t1)]
    n = max(2, math.ceil(L / pc["target_s"]))
    sp = L / n
    cuts = []
    for k in range(1, n):
        ideal = t0 + sp * k
        best, score = ideal, 1e9
        for t, w in cands:
            d = abs(t - ideal)
            if d <= 0.18 * sp and d - 0.25 * w < score:
                best, score = t, d - 0.25 * w
        cuts.append(best)
    edges = [t0] + cuts + [t1]
    out = []
    for a, b in zip(edges, edges[1:]):
        m = max(1, math.ceil((b - a) / pc["hard_max_s"] - 1e-9))
        for j in range(m):
            out.append((a + (b - a) * j / m, a + (b - a) * (j + 1) / m))
    return out


def clause_cuts(text: str, start: float, end: float) -> list:
    out, L = [], max(1, len(text))
    for m in re.finditer(r"[,;:]\s+|\s+(?:and|but|then|until|because|while)\s+", text):
        pos = m.end() if m.group(0)[0] in ",;:" else m.start()
        out.append((start + (pos / L) * (end - start), 0.6))
    return out


def tension_of(expressions: list, act: str) -> int:
    t = 0
    if any(e in ("scared", "shocked", "angry") for e in expressions):
        t = 2
    elif any(e in ("worried", "determined", "sly", "thinking") for e in expressions):
        t = 1
    if act in ("midpoint", "climax") and t < 2:
        t += 1
    return t


def choose_framing(nchars: int, overlay: bool, tension: int, prev: str | None, last: list, rng) -> str:
    if nchars == 0:
        pool = ["wide", "xwide", "low", "wide"]
    elif overlay:
        pool = ["medium", "wide"]
    elif tension >= 2:
        pool = ["closeup", "insert", "low", "medium", "back", "ots", "silhouette"]
    elif tension == 1:
        pool = ["medium", "ots", "closeup", "profile", "wide", "low"]
    else:
        pool = ["wide", "medium", "xwide", "profile", "back", "closeup"]
    if nchars >= 2:
        pool = [p for p in pool if p not in ("insert", "back", "silhouette")] + ["medium", "ots"]
    cand = [p for p in pool if p != prev and not (p in ("back", "silhouette") and p in last[-3:])]
    return rng.choice(cand or [p for p in pool if p != prev] or pool)


def view_for(framing: str, k: int, prev_views: list) -> str:
    v = {"closeup": "front", "insert": "front", "medium": "front" if k % 2 == 0 else "three_quarter", "back": "back", "ots": "back",
         "silhouette": "front", "profile": "three_quarter", "wide": "three_quarter", "low": "three_quarter", "xwide": "three_quarter"}.get(framing, "front")
    if v == "front" and prev_views[-2:] == ["front", "front"]:
        v = "three_quarter"
    return v


def choose_camera(tension: int, framing: str, dur_s: float, prev: str | None, rng, calm: bool = False) -> dict:
    pool = {0: LOW_CAM, 1: MID_CAM, 2: HIGH_CAM}[min(tension, 1) if calm else tension]
    preset = rng.choice([p for p in pool if p != prev] or pool)
    base = 1.0 if framing in ("closeup", "insert") else 1.05
    if preset in ("push", "pull", "dutch"):
        r = CAM_SPEED[tension] * dur_s
        lo, hi = base, base * (1 + r)
        z0, z1 = (hi, lo) if preset == "pull" else (lo, hi)
    else:
        z0 = z1 = 1.12
    return {"preset": preset, "z0": round(z0, 4), "z1": round(z1, 4), "param": None}


def pick_transition(idx: int, first_in_shot: bool, loc_changed: bool, chapter_start: bool, silence: bool, electronics: bool, impact: bool, prev: str, rng) -> str:
    if idx == 0 or chapter_start:
        return "cut"
    if silence:
        return "smash"
    if electronics:
        tr = "glitch"
    elif impact:
        tr = "flash"
    elif loc_changed:
        tr = "whip"
    elif first_in_shot:
        tr = rng.choice(["cut", "punch", "cut"])
    else:
        tr = rng.choice(["cut", "punch", "cut", "cut"])
    return "cut" if (tr != "cut" and tr == prev) else tr


def acting(text: str, pose: str, expr: str, j: int, rng) -> tuple:
    """Beat j>0 of a shot gets a neighbouring expression / pose so characters never freeze into one look."""
    for pat, p in POSE_KEYWORDS:
        if re.search(pat, text.lower()) and pose in ("stand", "point"):
            pose = p
            break
    if j > 0:
        expr = rng.choice(EXPR_ALT.get(expr, [expr]))
        pose = rng.choice(POSE_ALT.get(pose, [pose]))
    if text.strip().endswith("?") and expr in ("neutral", "worried"):
        expr = "worried"
    return pose, expr


def caption_chunks(text: str, max_chars: int = 36, max_lines: int = 2) -> list:
    """Words -> list of chunks, each chunk = list of lines (lists of words), every line <= max_chars, <= max_lines lines."""
    words = text.split()

    def wrap(ws):
        lines, cur = [], ""
        for w in ws:
            if cur and len(cur) + 1 + len(w) > max_chars:
                lines.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        lines.append(cur)
        return lines

    chunks, cur = [], []
    for w in words:
        if len(wrap(cur + [w])) <= max_lines:
            cur.append(w)
        else:
            chunks.append(cur)
            cur = [w]
    if cur:
        chunks.append(cur)
    out = []
    for ws in chunks:
        lines = wrap(ws)
        if len(lines) == 2:   # balance the two lines
            best = None
            for i in range(1, len(ws)):
                a, b = " ".join(ws[:i]), " ".join(ws[i:])
                if len(a) <= max_chars and len(b) <= max_chars and (best is None or abs(len(a) - len(b)) < best[0]):
                    best = (abs(len(a) - len(b)), i)
            if best:
                out.append([ws[: best[1]], ws[best[1]:]])
                continue
        out.append([ws] if len(lines) == 1 else [w.split() for w in lines])
    return out

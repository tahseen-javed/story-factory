"""Monetization-safety checklist (reused-content / inauthentic-content risk). Stdlib only.

Checks per video: original script (n-gram overlap vs other scripts), visual structure variety (authored shot-list overlap vs other videos),
no long reused segment, no third-party clips (images are generated, no video inputs), no real-person likeness, facts have sources.
"""
from __future__ import annotations

import glob
import os
import re

from . import vocab
from .parse import parse
from .uniqueness import shot_signature

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _shingles(seq, n):
    return {tuple(seq[i:i + n]) for i in range(max(0, len(seq) - n + 1))}


def jaccard(a, b) -> float:
    return len(a & b) / max(1, len(a | b))


def longest_common_run(a: list, b: list) -> int:
    best, prev = 0, [0] * (len(b) + 1)
    for x in a:
        cur = [0] * (len(b) + 1)
        for j, y in enumerate(b, 1):
            if x == y:
                cur[j] = prev[j - 1] + 1
                best = max(best, cur[j])
        prev = cur
    return best


def other_scripts(job_dir: str) -> list:
    out = []
    for p in glob.glob(os.path.join(ROOT, "jobs", "*", "script.md")) + glob.glob(os.path.join(ROOT, "pilot", "*", "script.md")):
        if os.path.abspath(os.path.dirname(p)) == os.path.abspath(job_dir):
            continue
        try:
            txt = open(p, encoding="utf-8").read()
            if not txt.startswith("\x00GITCRYPT"):
                out.append((os.path.basename(os.path.dirname(p)), parse(txt)))
        except Exception:  # noqa: BLE001 - encrypted/unreadable scripts are skipped and reported
            continue
    return out


def _no_claims(job_dir: str) -> bool:
    import json

    try:
        return bool(json.load(open(os.path.join(job_dir, "facts.json"), encoding="utf-8")).get("no_factual_claims"))
    except Exception:  # noqa: BLE001
        return False


def run(plan: dict, timeline: dict, job_dir: str, cfg: dict) -> dict:
    mcfg = cfg.get("monetization", {})
    thr_text, thr_shots, max_run_s = float(mcfg.get("script_similarity_max", 0.35)), float(mcfg.get("shot_similarity_max", 0.5)), float(mcfg.get("reused_segment_max_s", 20))
    if plan.get("kind") == "film":
        words = re.findall(r"[a-z']+", " ".join(s["text"] for s in plan["sentences"]).lower())
        sig = [f"{s['location']}.{s['variant']}|{len(s['chars'])}" for s in plan["shots"]]
        sc = type("S", (), {"locations": plan["locations"], "shots": []})()
    else:
        sc = parse(open(os.path.join(job_dir, "script.md"), encoding="utf-8").read())
        words = re.findall(r"[a-z']+", " ".join(s.text for s in sc.shots).lower())
        sig = shot_signature(sc)
    avg_shot_s = (sum(s["dur"] for s in timeline["shots"]) / max(1, len(timeline["shots"]))) / 30.0
    worst_text, worst_shots, worst_run, vs = 0.0, 0.0, 0, None
    others = other_scripts(job_dir)
    for name, o in others:
        ow = re.findall(r"[a-z']+", " ".join(s.text for s in o.shots).lower())
        t = jaccard(_shingles(words, 5), _shingles(ow, 5))
        osig = shot_signature(o)
        sh = jaccard(_shingles(sig, 3), _shingles(osig, 3))
        run_len = longest_common_run(sig, osig)
        if max(t, sh) >= max(worst_text, worst_shots):
            vs = name
        worst_text, worst_shots, worst_run = max(worst_text, t), max(worst_shots, sh), max(worst_run, run_len)
    people = [w for w in vocab.PROMPT_DENYLIST if re.search(r"\b" + re.escape(w) + r"\b", " ".join(words) + " " + " ".join(sc.locations.values()).lower())]
    media = [s.get("bg") or "" for s in timeline["shots"]] + [v for s in timeline["shots"] for v in (s.get("layers") or {}).values()]
    clips = sorted({os.path.splitext(m)[1] for m in media if m and os.path.splitext(m)[1] not in (".jpg", ".webp", ".png")})
    checks = {
        "original_script": worst_text < thr_text,
        "scene_structure_varies": worst_shots < thr_shots,
        "no_reused_long_segment": worst_run * avg_shot_s < max_run_s,
        "no_third_party_clips": not clips,
        "no_real_person_or_brand": not people,
        "facts_sourced": len(plan.get("sources", [])) >= 1 or _no_claims(job_dir),
    }
    return {"ok": all(checks.values()), "checks": checks, "compared_with": [n for n, _ in others], "closest_video": vs,
            "script_overlap": round(worst_text, 3), "shot_list_overlap": round(worst_shots, 3), "longest_reuse_s": round(worst_run * avg_shot_s, 1),
            "flagged_terms": people, "non_image_media": clips, "sources": len(plan.get("sources", [])),
            "note": "encrypted jobs/ scripts are only comparable when git-crypt is unlocked; none compared otherwise" if not others else ""}

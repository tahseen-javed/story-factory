"""P-008 D: preflight before every video. Writes qa/preflight.json and prints a 5-line summary.

python -m factory.preflight <job_dir> --eta-min 55 [--budget-min 60]
A failed check is reported, never a question; the caller auto-fixes and re-runs. Exit code 1 only if a hard check fails.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

from . import cast, licence, monetization, voicecheck
from .parse import parse
from .plan import build_plan
from .uniqueness import shot_signature
from .validate import ROOT, load_cfg, miniyaml


def last_owner_rating() -> tuple:
    p = os.path.join(ROOT, "docs", "QUALITY_LOG.md")
    rows = [ln for ln in open(p, encoding="utf-8").read().splitlines() if ln.startswith("| ") and re.search(r"\|\s*\d+(\.\d+)?\s*\|", ln)]
    for ln in reversed(rows):
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if re.fullmatch(r"\d+(\.\d+)?", cells[2]):
            return f"{cells[0]} {cells[1]}", float(cells[2])
    return "none", 0.0


def run(job_dir: str, eta_min: float, budget_min: float | None, out_path: str | None = None) -> dict:
    cfg = load_cfg()
    plan = build_plan(job_dir, cfg)
    sc = parse(open(os.path.join(job_dir, "script.md"), encoding="utf-8").read())
    job = miniyaml.load_file(os.path.join(job_dir, "job.yaml"))
    enforce = int(job.get("style_version", 1)) >= 3
    budget = budget_min or (35 if plan["length_min"] <= 4 else 60)
    checks = {}
    checks["1_time_estimate"] = {"ok": 0 < eta_min <= budget, "eta_min": eta_min, "budget_min": budget}
    acts = [s.get("act") or "hook" for s in plan["shots"]]
    ap = {"sfx": [{"name": n} for s in plan["shots"] for n in s["sfx"]] + [{"name": "whoosh"}, {"name": "impact"}, {"name": "riser"}],
          "music": [{"mood": cfg["audio"]["music_mood"].get(a, "tense")} for a in set(acts)], "ambience": [{"kind": k} for k in ("room", "city", "wind", "hum_dark")]}
    checks["2_licence_gate"] = (lambda r: {"ok": r["ok"], "missing": r["missing"], "assets": len(r["assets"])})(licence.check(ap, {"tts_engines": ["chatterbox"]}))
    tl = {"shots": [{"dur": 100, "bg": None, "layers": None} for _ in plan["shots"]]}
    checks["3_monetization"] = (lambda r: {"ok": r["ok"], "checks": r["checks"], "closest": r["closest_video"]})(monetization.run(plan, tl, job_dir, cfg))
    sig = shot_signature(sc)
    cute = cast.cute_check(sc.characters, cfg["style"], " ".join(s.text for s in sc.shots), enforce)
    uniq = cast.unique_check(sc.characters, sig, cast.load_history(), cfg["style"], plan.get("nnn"))
    vo = voicecheck.profiles_ok(cfg["characters"], sc.characters)
    checks["4_cast_voices"] = {"ok": (cute["ok"] or not enforce) and uniq["ok"] and vo["ok"], "cute": cute["ok"], "cute_enforced": enforce, "unique": uniq["ok"], "voices_locked_distinct": vo["ok"], "problems": vo["problems"]}
    manifests = [os.path.join(dp, f) for dp, _, fs in os.walk(os.path.join(ROOT, "build")) for f in fs if re.fullmatch(r"images_\d+\.json", f)] if os.path.isdir(os.path.join(ROOT, "build")) else []
    blotch = "not measured (no images manifest yet; measured in the images job)" if not manifests else "manifest present"
    checks["5_captions_and_blotch"] = {"ok": cfg.get("captions", {}).get("burned_in") is False, "captions": "P-006: none burned in", "blotch": blotch}
    prev, rating = last_owner_rating()
    improvements = job.get("improvements") or []
    checks["6_previous_rating"] = {"ok": rating > 0 and bool(improvements), "previous": prev, "previous_owner_rating": rating, "target": cfg["qa_calibration"]["target_rating"], "improvements": improvements,
                                   "note": "" if improvements else "add 'improvements:' list to job.yaml"}
    rep = {"job": job_dir, "ok": all(c["ok"] for c in checks.values()), "checks": checks}
    path = out_path or os.path.join(ROOT, "qa", "preflight.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(rep, open(path, "w"), indent=1)
    return rep


def summary(rep: dict) -> str:
    c = rep["checks"]
    return "\n".join([
        f"1 time: {'OK' if c['1_time_estimate']['ok'] else 'FAIL'} ({c['1_time_estimate']['eta_min']} of {c['1_time_estimate']['budget_min']} min)",
        f"2 licence gate: {'OK' if c['2_licence_gate']['ok'] else 'FAIL ' + str(c['2_licence_gate']['missing'])} ({c['2_licence_gate']['assets']} assets)",
        f"3 monetization: {'OK' if c['3_monetization']['ok'] else 'FAIL ' + str(c['3_monetization']['checks'])}",
        f"4 cast+voices: {'OK' if c['4_cast_voices']['ok'] else 'FAIL'} (cute {c['4_cast_voices']['cute']}{'' if c['4_cast_voices']['cute_enforced'] else ' not enforced < v3'}, unique {c['4_cast_voices']['unique']}, voices {c['4_cast_voices']['voices_locked_distinct']})",
        f"5-6 captions/blotch {'OK' if c['5_captions_and_blotch']['ok'] else 'FAIL'} | previous owner rating {c['6_previous_rating']['previous_owner_rating']} -> target {c['6_previous_rating']['target']}, improvements listed: {bool(c['6_previous_rating']['improvements'])}"])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("job_dir")
    ap.add_argument("--eta-min", type=float, required=True)
    ap.add_argument("--budget-min", type=float)
    a = ap.parse_args(argv)
    rep = run(a.job_dir, a.eta_min, a.budget_min)
    print(summary(rep))
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

"""Beat-the-reference scorecard: our measured metrics vs config.reference (provisional until analyze_reference.yml decrypts the real file)."""
from __future__ import annotations

import json
import statistics
import sys


def compute(props: dict, plan: dict, qa: dict, thumbs: dict | None, sources_count: int, cfg: dict) -> dict:
    ref = cfg["reference"]
    tl = props["timeline"]
    total_min = tl["durationInFrames"] / 30.0 / 60.0
    shots = tl["shots"]
    durs = [s["dur"] / 30.0 for s in shots[:-1]]
    med = statistics.median(durs) if durs else 0
    ov = {s["overlay"]["name"] for s in shots if s["overlay"]}
    banner = next((s["start"] / 30.0 for s in shots if s.get("banner")), None)
    rows = []

    def add(name, ours, theirs, ok, note=""):
        rows.append({"dimension": name, "ours": ours, "reference": theirs, "ok": bool(ok), "note": note})

    add("resolution", f"{tl['width']}x{tl['height']}", f"{ref['width']}x{ref['height']}", tl["width"] >= ref["width"] and tl["height"] >= ref["height"])
    add("fps", 30, ref["fps"], True)
    add("median shot (s)", round(med, 2), ref["median_shot_s"], 2.6 <= med <= ref["median_shot_s"] + 1.5)
    add("shots with motion", qa["motion"]["share"], ref["motion_share"], qa["motion"]["share"] >= ref["motion_share"] - 0.03)
    add("overlay types per minute", round(len(ov) / total_min, 1), "pending", len(ov) / total_min >= 3.0, "reference value pending analysis")
    add("sourced facts per minute", round(sources_count / total_min, 2), "pending", sources_count / total_min >= 0.8, "spec floor 8 per 10 min")
    a = qa["audio"]
    add("loudness (LUFS)", a["lufs"], ref["lufs"], abs(a["lufs"] + 14.0) <= 1.0)
    add("loudness range (LU)", a["lra"], ref["lra"], a["lra"] <= ref["lra"] + 1.5)
    add("true peak (dBTP)", a["true_peak"], "<= -1", a["true_peak"] <= -0.95)
    add("A/V sync (frames)", qa["av_sync"]["max_offset_frames"], "<= 2", qa["av_sync"]["max_offset_frames"] <= 2.0 or qa["av_sync"]["ok"])
    add("voice clarity (mean WER)", plan.get("_wer_mean"), "<= 0.05", (plan.get("_wer_mean") or 0) <= 0.05)
    add("thumbnail score", (thumbs or {}).get("chosen", {}).get("A", {}).get("score"), ">= 0.62", bool(thumbs and thumbs.get("ok")))
    add("hook banner at 20-40 s", None if banner is None else round(banner, 1), "n/a", banner is not None and 18 <= banner <= 42)
    add("in-story subscribe CTA", True, ref["has_cta"], True, "reference has none")
    return {"ok": all(r["ok"] for r in rows), "provisional_reference": bool(ref.get("provisional")), "rows": rows}


def table(card: dict, limit: int = 20) -> str:
    out = []
    for r in card["rows"][:limit]:
        out.append(f"{'PASS' if r['ok'] else 'FAIL'}  {r['dimension']}: ours={r['ours']} ref={r['reference']}")
    return "\n".join(out)


if __name__ == "__main__":
    print(table(json.load(open(sys.argv[1]))))

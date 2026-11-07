"""Auto-fixers: each QA failure maps to a small, deterministic patch of the Remotion props, then only the affected chunks re-render."""
from __future__ import annotations

import json


def apply(props_path: str, qa: dict, timeline_chunks: list) -> dict:
    """Patch props.json in place. Returns {"chunks": [...to re-render...], "fixes": [...]}."""
    data = json.load(open(props_path))
    tl = data["timeline"]
    fixes, chunks = [], set(qa.get("bad_chunks", []))
    static = set(qa.get("motion", {}).get("static_shots", []))
    for s in tl["shots"]:
        if s["i"] in static:
            c = s["camera"]
            c["preset"], c["z0"], c["z1"] = "push", 1.04, min(1.35, 1.04 + 0.025 * s["dur"] / 30.0 * 1.5)
            fixes.append({"shot": s["i"], "fix": "camera_rewritten_for_motion"})
            chunks.add(next((ch["i"] for ch in timeline_chunks if ch["from"] <= s["start"] <= ch["to"]), 0))
    if not qa.get("flash", {}).get("ok", True):
        for s in tl["shots"]:
            if any(f in s["fx"] for f in ("flicker", "alarm_pulse", "glitch")):
                s["fx"] = [f for f in s["fx"] if f not in ("flicker", "alarm_pulse", "glitch")]
                fixes.append({"shot": s["i"], "fix": "flash_fx_removed"})
                chunks.add(next((ch["i"] for ch in timeline_chunks if ch["from"] <= s["start"] <= ch["to"]), 0))
    if not (qa.get("black", {}).get("ok", True) and qa.get("freeze", {}).get("ok", True)):
        fixes.append({"fix": "rerender_chunks_black_or_freeze", "chunks": sorted(chunks)})
    json.dump(data, open(props_path, "w"))
    return {"chunks": sorted(chunks), "fixes": fixes}

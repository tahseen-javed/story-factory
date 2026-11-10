"""Video Doctor auto-fixes (P-012 Part 4). Pure functions: (params, findings, metrics) -> new params, or stem-level repairs for the fixtures.

config/qa_fixes.yaml documents the failure code -> action -> re-run scope map; this module implements the actions.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import uniform_filter1d

from . import lufs

SR = lufs.SR
UNFIXABLE_AUTO = {"A1-GAP", "A1-BEATS", "A1-BEAT-LONG"}    # need a re-timed script/TTS: rejected with a reason when they remain


def adjust_mix_params(params: dict, findings: list, metrics: dict, th: dict) -> tuple:
    """One fix pass over the mix parameters. Returns (new_params, [log lines])."""
    p, log = dict(params), []
    codes = {f["code"] for f in findings}
    a = th["audio"]
    lo, hi = a["music_below_voice_db"]
    if codes & {"A3-MUSIC-LOUD", "A3-MUSIC-MEDIAN", "A3-MUSIC-ABOVE"}:
        gap = metrics.get("music_below_voice_db")
        target = (lo + hi) / 2.0
        step = (target - gap) if gap is not None else 6.0
        step = float(np.clip(step, -12.0, 12.0))
        # a negative music_trim_db makes the music quieter (the mixer scales the bed so that gap = target - trim)
        p["music_trim_db"] = round(p.get("music_trim_db", 0.0) - step, 2)
        log.append(f"music_trim_db {params.get('music_trim_db', 0.0)} -> {p['music_trim_db']} (gap was {gap and round(gap, 1)} dB, target {target})")
    if codes & {"A3B-MUSIC-MISSING", "A3B-MUSIC-QUIET"}:   # P-014: raise the bed (the mixer always builds it from the music library / synth)
        p["music_trim_db"] = round(min(8.0, p.get("music_trim_db", 0.0) + 4.0), 2)
        log.append(f"music_trim_db -> {p['music_trim_db']} (music not audible enough)")
    if "A3-MUSIC-RISE" in codes:
        p["duck_db"] = max(3.0, round(float(p.get("duck_db", th.get('mix_duck_db', 6.0))) - 2.0, 1))
        log.append(f"duck_db -> {p['duck_db']}")
    if codes & {"A3-MUSIC-JUMP"}:
        p["venv_smooth_s"] = round(min(8.0, max(0.25, float(p.get("venv_smooth_s", th.get("mix_venv_smooth_s", 3.0))) * 2)), 2)
        log.append(f"venv_smooth_s -> {p['venv_smooth_s']}")
    if "A3-MUSIC-DROPOUT" in codes:
        p["music_floor_db"] = -24.0
        log.append("music_floor_db -> -24 (no unplanned dropouts)")
    if "A3-MUSIC-CALM" in codes:
        p["music_lowpass_hz"] = 6000
        log.append("music_lowpass_hz -> 6000")
    if codes & {"A3-TRUEPEAK", "A4-CLIP", "A4-STEM-CLIP"}:
        p["limiter_scale"] = round(float(p.get("limiter_scale", 1.0)) * 0.92, 3)
        log.append(f"limiter_scale -> {p['limiter_scale']}")
    return p, log


# ---- stem-level repairs used on the fixtures (same logic as the pipeline expresses through mix parameters) ----------------
def fix_stems(stems: dict, plan: dict, findings: list, th: dict):
    """Repair the synthetic fixture: returns (stems, plan, log). Gaps are trimmed by moving later audio earlier."""
    st = {k: v.copy() for k, v in stems.items()}
    pl = {"sentences": [dict(s) for s in plan["sentences"]], "silence": [list(w) for w in plan.get("silence", [])]}
    log = []
    codes = {f["code"] for f in findings}
    if "A1-GAP" in codes:
        for f in sorted([x for x in findings if x["code"] == "A1-GAP"], key=lambda x: -x["t0"]):
            cut0, cut1 = int((f["t0"] + 0.35) * SR), int(f["t1"] * SR)
            if cut1 > cut0:
                for k in st:
                    st[k] = np.concatenate([st[k][:cut0], st[k][cut1:], np.zeros(cut1 - cut0)])
                shift = (cut1 - cut0) / SR
                for s in pl["sentences"]:
                    if s["start"] >= f["t1"] - 0.01:
                        s["start"] -= shift
                        s["end"] -= shift
                pl["silence"] = [[w[0] - shift, w[1] - shift] if w[0] >= f["t1"] else w for w in pl["silence"]]
                log.append(f"trimmed {shift:.2f}s of silence at {f['t0']}s (20 ms crossfade)")
    if codes & {"A3-MUSIC-LOUD", "A3-MUSIC-MEDIAN", "A3-MUSIC-ABOVE"}:
        vst, tt = lufs.short_term(st["voice"], 0.5)
        mst, _ = lufs.short_term(st["music"], 0.5)
        from . import audio as A

        n = min(len(vst), len(mst))
        spk = A.speech_fraction([s for s in pl["sentences"]], tt[:n] + 1.5) >= 0.6
        if spk.sum():
            gap = float(np.median(vst[:n][spk]) - np.median(mst[:n][spk]))
            target = sum(th["audio"]["music_below_voice_db"]) / 2.0
            st["music"] = st["music"] * 10 ** ((gap - target) / 20.0)
            log.append(f"music re-levelled: gap {gap:.1f} dB -> {target:.1f} dB under the voice")
    if "A3-MUSIC-DROPOUT" in codes:
        for f in [x for x in findings if x["code"] == "A3-MUSIC-DROPOUT"]:
            a, b = int(f["t0"] * SR), int(f["t1"] * SR)
            lo = max(0, a - int(0.5 * SR))
            ref = st["music"][lo:a]
            if len(ref) and b > a:
                fill = np.resize(ref, b - a) * np.hanning(b - a) ** 0.3
                st["music"][a:b] = fill
                log.append(f"music dropout at {f['t0']}s refilled from the preceding bed")
    if "A3-MUSIC-JUMP" in codes:
        k = int(0.9 * SR)
        env = uniform_filter1d(np.abs(st["music"]), size=k, mode="nearest") + 1e-9
        target = uniform_filter1d(env, size=k, mode="nearest")
        st["music"] = st["music"] * np.clip(target / env, 0.3, 3.0)
        log.append("music gain envelope smoothed over 0.9 s")
    return st, pl, log

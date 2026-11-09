"""Video Doctor audio checks (A1-A5). numpy/scipy only. Every finding: code, severity, t0/t1 seconds, value, threshold, message.

Inputs are the stems as they sit in the final mix (48 kHz): voice, music, sfx, ambience (mono) and the master (stereo).
"""
from __future__ import annotations

import numpy as np

from . import lufs

SR = lufs.SR


def finding(th, code, key, t0, t1, value, thr, msg):
    return {"code": code, "severity": th["severity"][key], "t0": round(float(t0), 2), "t1": round(float(t1), 2), "value": None if value is None else round(float(value), 2),
            "threshold": thr, "msg": msg}


def segments(mask: np.ndarray, times: np.ndarray, step: float, min_len: float = 0.0):
    """Contiguous True runs -> [(t0, t1)] (seconds)."""
    out, start = [], None
    for i, m in enumerate(mask):
        if m and start is None:
            start = i
        if (not m or i == len(mask) - 1) and start is not None:
            end = i if not m else i + 1
            t0, t1 = times[start], times[end - 1] + step
            if t1 - t0 >= min_len:
                out.append((float(t0), float(t1)))
            start = None
    return out


def speech_fraction(plan_sent, centers, win=3.0):
    frac = np.zeros(len(centers))
    for s in plan_sent:
        a, b = s["start"], s["end"]
        for i, c in enumerate(centers):
            lo, hi = c - win / 2, c + win / 2
            ov = max(0.0, min(hi, b) - max(lo, a))
            frac[i] += ov / win
    return np.clip(frac, 0, 1)


def check_master(x, th):
    """A3/A4 integrated, true peak, LRA, hot start, tail, DC, clipping, stereo/mono-compat. x: (2, n) 48 kHz."""
    a = th["audio"]
    f, m = [], {}
    m["integrated_lufs"] = lufs.integrated(x)
    m["true_peak_db"] = lufs.true_peak_db(x)
    m["lra"] = lufs.lra(x)
    lo, hi = a["integrated_lufs"]
    if not (lo <= m["integrated_lufs"] <= hi):
        f.append(finding(th, "A3-INTEGRATED", "integrated", 0, len(x[0]) / SR, m["integrated_lufs"], [lo, hi], "integrated loudness out of range"))
    if m["true_peak_db"] > a["true_peak_max_db"]:
        f.append(finding(th, "A3-TRUEPEAK", "true_peak", 0, len(x[0]) / SR, m["true_peak_db"], a["true_peak_max_db"], "true peak too high"))
    lo, hi = a["lra"]
    if not (lo <= m["lra"] <= hi):
        f.append(finding(th, "A3-LRA", "lra", 0, len(x[0]) / SR, m["lra"], [lo, hi], "loudness range out of range"))
    n = x.shape[1]
    head = x[:, : int(0.03 * SR)]   # the first 30 ms: a fade-in ramp is fine, a click or a full-level start is not
    m["start_rms_dbfs"] = 10 * np.log10(max(float((head ** 2).mean()), 1e-14))
    if m["start_rms_dbfs"] > a["hot_start_dbfs"]:
        f.append(finding(th, "A4-HOTSTART", "hot_start", 0, 0.1, m["start_rms_dbfs"], a["hot_start_dbfs"], "audio starts hot (no fade-in)"))
    tail = x[:, -int(0.5 * SR):]
    m["tail_peak_dbfs"] = 20 * np.log10(max(float(np.abs(tail).max()), 1e-9))
    if m["tail_peak_dbfs"] > a["tail_max_dbfs"]:
        f.append(finding(th, "A4-TAIL", "tail", n / SR - 0.5, n / SR, m["tail_peak_dbfs"], a["tail_max_dbfs"], "last 0.5 s is not a clean tail"))
    m["dc_offset"] = float(np.abs(x.mean(axis=1)).max())
    if m["dc_offset"] > a["dc_offset_max"]:
        f.append(finding(th, "A4-DC", "dc", 0, n / SR, m["dc_offset"], a["dc_offset_max"], "DC offset"))
    clip = int((np.abs(x) >= 0.999).sum())
    m["clipped_samples"] = clip
    if clip:
        idx = np.where(np.abs(x).max(axis=0) >= 0.999)[0]
        f.append(finding(th, "A4-CLIP", "clipping", idx[0] / SR, idx[-1] / SR, clip, 0, "clipped samples in the master"))
    mono = x.mean(axis=0, keepdims=True)
    drop = lufs.integrated(x) - lufs.integrated(np.vstack([mono, mono]))
    m["mono_drop_db"] = float(drop)
    if drop > a["mono_compat_drop_max_db"]:
        f.append(finding(th, "A4-MONO", "mono", 0, n / SR, drop, a["mono_compat_drop_max_db"], "mix loses loudness in mono"))
    return m, f


def check_voice(voice, plan, th):
    """A1 gaps/beats, A2 consistency (stem only): voice mono (n,)."""
    a = th["audio"]
    f, m = [], {}
    env, t = lufs.rms_envelope(voice)
    quiet = env < -55
    gaps = segments(quiet, t, 0.01, 0.12)
    sentences = plan["sentences"]
    last_end = max(s["end"] for s in sentences)
    windows = [(w[0] - 0.15, w[1] + 0.15) for w in plan.get("silence", [])]
    holds = [(h[0] - 0.4, h[1] + 0.4) for h in plan.get("holds", [])]
    total_s = float(plan.get("total_s") or (last_end + 5.0))
    hold_ok = int(max(1, total_s // float(a.get("decision_hold_per_s", 40))))
    m["decision_holds"] = len(holds)
    if len(holds) > hold_ok:
        f.append(finding(th, "A1-HOLD-COUNT", "hold_count", 0, last_end, len(holds), hold_ok, "too many decision holds"))
    for h in plan.get("holds", []):
        if h[1] - h[0] > float(a.get("decision_hold_max_s", 5.0)) + 0.8:
            f.append(finding(th, "A1-HOLD-LONG", "hold_long", h[0], h[1], h[1] - h[0], a.get("decision_hold_max_s", 5.0), "decision hold is too long"))
    beats, bad = 0, []
    for g0, g1 in gaps:
        if g0 < 0.3 or g1 > last_end + 0.5:
            continue                                      # lead-in and tail are not gaps
        if any(h0 <= g0 + 0.3 and g1 - 0.3 <= h1 for h0, h1 in holds):
            continue                                       # marked decision hold (see decision_hold_* limits)
        planned = any(w0 <= g0 + 0.05 and g1 - 0.05 <= w1 + 1.0 for w0, w1 in windows)
        if planned:
            beats += 1
            if g1 - g0 > a["beat_max_s"] + 0.3:
                f.append(finding(th, "A1-BEAT-LONG", "beats", g0, g1, g1 - g0, a["beat_max_s"], "marked silence beat is too long"))
        elif g1 - g0 > a["gap_max_s"]:
            bad.append((g0, g1))
            f.append(finding(th, "A1-GAP", "gap", g0, g1, g1 - g0, a["gap_max_s"], "gap in the voice"))
    m["gaps_over_limit"], m["beats"] = len(bad), beats
    if beats > a["beat_max_count"]:
        f.append(finding(th, "A1-BEATS", "beats", 0, last_end, beats, a["beat_max_count"], "too many dramatic silence beats"))
    # sentence loudness consistency and pace
    levels = []
    for s in sentences:
        seg = voice[int(s["start"] * SR): int(s["end"] * SR)]
        if len(seg) > int(0.4 * SR):
            levels.append(lufs.integrated(seg))
    levels = [v for v in levels if v > -70]
    m["sentence_lufs_std"] = float(np.std(levels)) if levels else 0.0
    if m["sentence_lufs_std"] > a["sentence_loudness_std_max_lu"]:
        f.append(finding(th, "A2-SENTENCE-LEVEL", "sentence_std", 0, last_end, m["sentence_lufs_std"], a["sentence_loudness_std_max_lu"], "sentence loudness varies too much"))
    words = sum(s["words"] for s in sentences)
    speaking = sum(s["end"] - s["start"] for s in sentences if not s.get("parallel"))
    m["wpm"] = words / max(speaking, 1e-6) * 60
    lo, hi = a["wpm_overall"]
    if not (lo <= m["wpm"] <= hi):
        f.append(finding(th, "A2-WPM", "wpm", 0, last_end, m["wpm"], [lo, hi], "speaking pace out of range"))
    if float(np.abs(voice).max()) >= 0.999:
        f.append(finding(th, "A2-CLIP", "stem_clip", 0, last_end, float(np.abs(voice).max()), 0.999, "voice stem clips"))
    return m, f


def check_music(voice, music, sfx, amb, plan, th):
    """A3 music level control + calmness, A4 SFX vs voice. All stems mono 48 kHz in final-mix scale."""
    a = th["audio"]
    f, m = [], {}
    vs, tt = lufs.short_term(voice, 0.5)
    ms, _ = lufs.short_term(music, 0.5)
    n = min(len(vs), len(ms))
    vs, ms, tt = vs[:n], ms[:n], tt[:n]
    centers = tt + 1.5
    sp = speech_fraction([s for s in plan["sentences"] if not s.get("parallel")], centers)
    speaking = sp >= 0.6
    quiet_t = sp <= 0.15
    windows = [(w[0] - 1.6, w[1] + 1.6) for w in plan.get("silence", [])] + [(h[0] - 1.0, h[1] + 1.6) for h in plan.get("holds", [])]
    in_win = np.array([any(w0 <= c <= w1 for w0, w1 in windows) for c in centers])
    if speaking.sum() >= 3:
        m["voice_st_median"] = float(np.median(vs[speaking]))
        m["music_st_median"] = float(np.median(ms[speaking]))
        m["music_below_voice_db"] = m["voice_st_median"] - m["music_st_median"]
        lo, hi = a["voice_short_term_lufs"]
        if not (lo <= m["voice_st_median"] <= hi):
            f.append(finding(th, "A3-VOICE-LEVEL", "voice_level", 0, tt[-1], m["voice_st_median"], [lo, hi], "voice short-term loudness out of range"))
        lo, hi = a["music_below_voice_db"]
        if not (lo <= m["music_below_voice_db"] <= hi):
            f.append(finding(th, "A3-MUSIC-MEDIAN", "music_median", 0, tt[-1], m["music_below_voice_db"], [lo, hi], "music is not 18-22 dB under the voice while speaking"))
        gap = vs - ms
        loud = speaking & (gap < a["music_local_min_gap_db"])
        for t0, t1 in segments(loud, tt, 0.5, 0.5):
            f.append(finding(th, "A3-MUSIC-LOUD", "music_local", t0, t1 + 2.5, float(gap[(tt >= t0) & (tt <= t1)].min()), a["music_local_min_gap_db"], "music too loud under speech"))
        above = speaking & (ms > vs)
        for t0, t1 in segments(above, tt, 0.5, 0.5):
            f.append(finding(th, "A3-MUSIC-ABOVE", "music_above_voice", t0, t1 + 2.5, None, 0, "music louder than the voice"))
        free = quiet_t & ~in_win
        if free.sum():
            rise = ms[free] - m["music_st_median"]
            m["music_rise_max_db"] = float(rise.max())
            if rise.max() > a["music_rise_max_db"]:
                bad = free & (ms - m["music_st_median"] > a["music_rise_max_db"])
                for t0, t1 in segments(bad, tt, 0.5, 0.5):
                    f.append(finding(th, "A3-MUSIC-RISE", "music_rise", t0, t1 + 2.5, float(rise.max()), a["music_rise_max_db"], "music rises more than 6 dB in non-speech moments"))
    mm, mt = lufs.momentary(music, 0.1)
    k = int(1.0 / 0.1)
    if len(mm) > k:
        jump = np.abs(mm[k:] - mm[:-k])
        mid = (mt[:-k] + 0.5)
        # ducking under a sentence start/end is by design: a jump is only a defect when no speech boundary lies in (t-1.0 s, t+3.6 s): the 3 s short-term window smears a ducking release over that range
        bounds = np.sort(np.array([x for s in plan["sentences"] for x in (s["start"], s["end"])] or [1e9]))
        j0 = np.searchsorted(bounds, mt[:-k] - 1.0)
        j1 = np.searchsorted(bounds, mt[:-k] + 3.6)
        near_speech = j1 > j0
        ok_zone = near_speech | np.array([any(w0 <= c <= w1 for w0, w1 in windows) for c in mid]) | (mm[:-k] < -50) | (mm[k:] < -50) | (mid < 2.0) | (mid > mt[-1] - 3.0)
        bad = (jump > a["music_jump_max_lu"]) & ~ok_zone
        m["music_jump_max_lu"] = float(jump[~ok_zone].max()) if (~ok_zone).any() else 0.0
        for t0, t1 in segments(bad, mt[:-k], 0.1, 0.0):
            f.append(finding(th, "A3-MUSIC-JUMP", "music_jump", t0, t1 + 1.0, float(jump[(mt[:-k] >= t0) & (mt[:-k] <= t1)].max()), a["music_jump_max_lu"], "sudden music level jump"))
        drop = (mm < a["music_dropout_lufs"]) & (mt > 2.0) & (mt < mt[-1] - 3.0) & ~np.array([any(w0 <= c <= w1 for w0, w1 in windows) for c in mt + 0.2])
        for t0, t1 in segments(drop, mt, 0.1, a["music_dropout_s"]):
            f.append(finding(th, "A3-MUSIC-DROPOUT", "music_dropout", t0, t1, None, a["music_dropout_lufs"], "music drops to near silence"))
    # calmness: spectral flux, centroid variability and high-frequency share of the music stem
    from scipy import signal as sg

    freqs, _, Z = sg.stft(music, SR, nperseg=2048, noverlap=1536)
    mag = np.abs(Z) + 1e-9
    nm = mag / mag.sum(axis=0, keepdims=True)
    flux = np.maximum(nm[:, 1:] - nm[:, :-1], 0).sum(axis=0)
    cent = (freqs[:, None] * nm).sum(axis=0)
    hf = 10 * np.log10(max(float((mag[freqs > 6000] ** 2).sum()) / float((mag ** 2).sum()), 1e-12))
    m["calm_flux_p99"], m["calm_centroid_std_hz"], m["calm_hf_ratio_db"] = float(np.percentile(flux, 99)), float(np.std(cent)), float(hf)
    for key, val, name in (("calm_flux_p99_max", m["calm_flux_p99"], "spectral flux"), ("calm_centroid_std_max_hz", m["calm_centroid_std_hz"], "centroid variability"), ("calm_hf_ratio_max_db", m["calm_hf_ratio_db"], "high-frequency share")):
        if a.get(key) is not None and val > a[key]:
            f.append(finding(th, "A3-MUSIC-CALM", "music_calm", 0, tt[-1] if len(tt) else 0, val, a[key], f"music is not calm enough ({name})"))
    # SFX never louder than the voice while speaking; ambience stays under the music
    ss, _ = lufs.short_term(sfx, 0.5)
    k2 = min(len(ss), n)
    if k2:
        loud = speaking[:k2] & (ss[:k2] > vs[:k2] - a["sfx_margin_db"]) & (ss[:k2] > -45)
        for t0, t1 in segments(loud, tt[:k2], 0.5, 0.5):
            f.append(finding(th, "A4-SFX-LOUD", "sfx_loud", t0, t1 + 2.5, float((ss[:k2] - vs[:k2])[(tt[:k2] >= t0) & (tt[:k2] <= t1)].max()), -a["sfx_margin_db"], "sfx louder than the voice"))
    for name, st in (("voice", voice), ("music", music), ("sfx", sfx), ("ambience", amb)):
        if len(st) and float(np.abs(st).max()) >= 0.999:
            f.append(finding(th, "A4-STEM-CLIP", "stem_clip", 0, len(st) / SR, float(np.abs(st).max()), 0.999, f"{name} stem clips"))
    return m, f


def check_sync(timeline, plan, th, video_s=None, audio_s=None):
    """A5: first caption of every sentence starts within 80 ms of the audio; audio/video drift at the end."""
    s = th["sync"]
    f = []
    caps = timeline.get("captions") or []
    fps = timeline.get("fps", 30)
    starts = sorted(c["s"] / fps for c in caps)
    worst = 0.0
    for sen in plan["sentences"]:
        if sen.get("parallel"):
            continue
        near = min(starts, key=lambda c: abs(c - sen["start"])) if starts else None
        if near is None:
            continue
        d = abs(near - sen["start"]) * 1000
        worst = max(worst, d)
        if d > s["caption_start_ms"] and caps:
            f.append(finding(th, "A5-CAPTION-SYNC", "caption_sync", sen["start"], sen["start"] + 1, d, s["caption_start_ms"], "caption starts away from the spoken sentence"))
    m = {"caption_start_worst_ms": worst}
    if video_s is not None and audio_s is not None:
        drift = abs(video_s - audio_s) * 1000
        m["av_drift_ms"] = drift
        if drift > s["drift_ms"]:
            f.append(finding(th, "A5-DRIFT", "drift", video_s - 1, video_s, drift, s["drift_ms"], "audio/video length drift"))
    return m, f


def check_music_present(voice, music, plan, th):
    """A3b MUSIC PRESENT (P-014): music audible for >= 90 % of the video (planned beats excluded) and not buried under the voice."""
    a = th["music_present"]
    f, m = [], {}
    vs, tt = lufs.short_term(voice, 0.5)
    ms, _ = lufs.short_term(music, 0.5)
    n = min(len(vs), len(ms))
    vs, ms, c = vs[:n], ms[:n], tt[:n] + 1.5
    win = [(w[0], w[1]) for w in plan.get("silence", [])] + [(h[0], h[1]) for h in plan.get("holds", [])]
    use = ~np.array([any(w0 <= x <= w1 for w0, w1 in win) for x in c])
    live = vs > -60
    vref = float(np.median(vs[live])) if live.any() else -20.0
    frac = float((ms > vref - a["audible_floor_lufs_below_voice"])[use].mean()) if use.any() else 1.0
    m["music_audible_fraction"] = round(frac, 3)
    if frac < a["audible_fraction_min"]:
        f.append(finding(th, "A3B-MUSIC-MISSING", "music_missing", 0, len(music) / SR, frac, a["audible_fraction_min"], "background music is not audible for most of the video"))
    sp = speech_fraction([s for s in plan["sentences"] if not s.get("parallel")], c) >= 0.6
    if sp.sum() >= 3:
        gap = float(np.median(vs[sp]) - np.median(ms[sp]))
        m["music_gap_db"] = round(gap, 1)
        if gap > a["below_voice_db"][1]:
            f.append(finding(th, "A3B-MUSIC-QUIET", "music_quiet", 0, len(music) / SR, gap, a["below_voice_db"], "music is too quiet to be noticed"))
    return m, f

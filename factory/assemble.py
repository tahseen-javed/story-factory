"""Assemble: plan + TTS timings + images -> Remotion props (timeline), audio plan, captions, chapters, render chunks.

Everything here is deterministic. This is where the pre-render auto-fixers live (camera clamp, shot re-split, backdrop fallback).
Stdlib only.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import re
import shutil
import sys
import wave

from . import miniyaml
from .textutil import split_sentences
from .validate import load_cfg

FPS = 30
KEYWORD_SFX = [
    (r"\bknock", "door_knock"), (r"\b(alarm|siren)", "alert_siren"), (r"\bdoor (opens|creak)", "door_creak"),
    (r"\bfootstep", "footsteps"), (r"\bthunder", "thunder"), (r"\bglass", "glass_crack"),
]


def wav_seconds(path: str) -> float:
    with wave.open(path, "rb") as w:
        return w.getnframes() / float(w.getframerate())


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def fix_camera(cam: dict, dur_s: float, cfg: dict, notes: list, shot_i: int) -> dict:
    cc = cfg["camera"]
    lo, hi = float(cc["zoom_min"]), float(cc["zoom_max"])
    smin, smax = float(cc["speed_min_pct_s"]) / 100.0, float(cc["speed_max_pct_s"]) / 100.0
    preset = cam.get("preset", "push")
    z0, z1 = float(cam.get("z0", 1.0)), float(cam.get("z1", 1.0))
    out = dict(cam)
    if preset in ("push", "pull", "dutch"):
        speed = abs(z1 / max(z0, 1e-6) - 1) / max(dur_s, 0.2)
        target = clamp(speed, smin * 1.15, smax * 0.9)
        r = target * dur_s
        low = clamp(min(z0, z1), lo, hi / (1 + r))
        high = low * (1 + r)
        n0, n1 = (high, low) if preset == "pull" else (low, high)
        if abs(n0 - z0) > 0.005 or abs(n1 - z1) > 0.005:
            notes.append({"shot": shot_i, "fix": "camera_clamped", "from": [z0, z1], "to": [round(n0, 3), round(n1, 3)]})
        out["z0"], out["z1"] = round(n0, 4), round(n1, 4)
    else:
        z = clamp((z0 + z1) / 2, lo, hi)
        if preset in ("pan_l", "pan_r", "parallax_drift", "tilt_up", "tilt_down", "whip_to"):
            z = max(z, 1.06)
        if preset in ("rack_focus",):
            z = max(z, 1.04)
        out["z0"] = out["z1"] = round(z, 4)
        if preset == "rack_focus":
            out["z1"] = round(min(hi, z * (1 + smin * dur_s * 1.2)), 4)
    return out


def layout_chars(chars: list, shot_i: int) -> list:
    n = len(chars)
    default = {1: [0.5], 2: [0.30, 0.70], 3: [0.22, 0.5, 0.78]}.get(n, [0.5])
    out = []
    for k, c in enumerate(chars):
        x = c["x"] if c.get("x") is not None else default[k]
        out.append({"id": c["id"], "pose": c["pose"], "expr": c["expr"], "x": x})
    # facing: towards the centre of the group / the other character
    for k, c in enumerate(out):
        if n == 1:
            c["facing"] = 1 if (shot_i % 2 == 0) else -1
        else:
            others = [o["x"] for j, o in enumerate(out) if j != k]
            c["facing"] = 1 if sum(others) / len(others) >= c["x"] else -1
    return out


def voice_env(path: str, fps: int = FPS) -> list:
    """Per-frame mouth-opening envelope (0..1) from a sentence wav (RMS, normalised to its 95th percentile)."""
    import numpy as np

    with wave.open(path, "rb") as w:
        sr, n, sw, ch = w.getframerate(), w.getnframes(), w.getsampwidth(), w.getnchannels()
        raw = w.readframes(n)
    a = np.frombuffer(raw, dtype="<i2" if sw == 2 else "<i4").astype("float32")
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1)
    hop = max(1, int(sr / fps))
    m = len(a) // hop
    if m == 0:
        return []
    rms = np.sqrt((a[: m * hop].reshape(m, hop) ** 2).mean(axis=1))
    e = np.clip(rms / (np.percentile(rms, 95) + 1e-9), 0, 1)
    e = np.where(e < 0.12, 0.0, e)
    return [float(x) for x in e]


def layout_beat(chars: list, frm: str, view: str, beat_no: int, has_ov: bool) -> list:
    n = len(chars)
    flip = beat_no % 2 == 0
    out = []
    if n == 1:
        x = {"closeup": 0.5, "insert": 0.5, "back": 0.30 if flip else 0.70, "ots": 0.27 if flip else 0.73, "wide": 0.28 if flip else 0.72,
             "xwide": 0.3 if flip else 0.7, "low": 0.5}.get(frm, 0.5)
        if has_ov and frm in ("medium", "wide"):
            x = 0.27 if flip else 0.73
        c = chars[0]
        if c.get("x") is not None and frm == "medium":
            x = c["x"]
        out.append({"id": c["id"], "pose": c["pose"], "expr": c["expr"], "x": x, "facing": 1 if x <= 0.5 else -1, "view": view,
                    "silhouette": frm == "silhouette"})
        return out
    base = layout_chars(chars, beat_no)
    for k, c in enumerate(base):
        c["view"] = "back" if (frm == "ots" and k == 0) else ("three_quarter" if k % 2 == 0 else "front")
        if frm == "ots" and k == 0:
            c["x"] = 0.18
        c["silhouette"] = False
    return base


def build_captions(sentences: list, B) -> list:
    """Burned-in captions: <= 2 lines of <= 36 chars; per-word frame timing proportional to word length."""
    caps = []
    for s in sentences:
        words = s["text"].split()
        if not words:
            continue
        weights = [len(w) + 1 for w in words]
        tot = float(sum(weights))
        t, wt = s["start"], []
        for w, wgt in zip(words, weights):
            d = (s["end"] - s["start"]) * wgt / tot
            wt.append((w, t, t + d))
            t += d
        idx = 0
        for chunk in B.caption_chunks(s["text"]):
            lines = []
            for ln in chunk:
                row = []
                for _ in ln:
                    w, a, b = wt[idx]
                    row.append([w, int(round(a * FPS)), int(round(b * FPS))])
                    idx += 1
                lines.append(row)
            caps.append({"s": max(0, lines[0][0][1] - 3), "e": lines[-1][-1][2] + 6, "lines": lines})
    for a, b in zip(caps, caps[1:]):
        a["e"] = min(a["e"], b["s"])
    return caps


def srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def wrap_caption(text: str, width: int = 38) -> str:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return "\n".join(lines)


def run(plan_path: str, tts_dir: str, img_dir: str, out_dir: str, public_dir: str | None):
    cfg = load_cfg()
    plan = json.load(open(plan_path, encoding="utf-8"))
    os.makedirs(out_dir, exist_ok=True)
    notes: list = []

    # ---------- TTS timings ----------
    tmeta = {}
    engines = set()
    for f in glob.glob(os.path.join(tts_dir, "**", "meta_*.json"), recursive=True):
        m = json.load(open(f, encoding="utf-8"))
        engines.add(m.get("engine"))
        for s in m["sentences"]:
            tmeta[s["id"]] = s
    wavs = {os.path.splitext(os.path.basename(p))[0]: p for p in glob.glob(os.path.join(tts_dir, "**", "s*.wav"), recursive=True) if not p.endswith(".try.wav")}
    missing = [s["id"] for s in plan["sentences"] if s["id"] not in wavs]
    if missing:
        raise SystemExit(f"assemble: missing TTS audio for {len(missing)} sentences, first: {missing[:5]}")
    lead_in = 0.6
    t = lead_in
    for s in plan["sentences"]:
        s["file"] = wavs[s["id"]]
        s["dur"] = round(wav_seconds(s["file"]), 4)
        s["start"] = round(t, 4)
        s["end"] = round(t + s["dur"], 4)
        t = s["end"] + s["pause_after_s"]
    last_pause = 1.0
    audio_end = plan["sentences"][-1]["end"] + last_pause
    end_s = float(cfg.get("end_screen_s", 20))
    total_s = audio_end + end_s
    total_frames = int(round(total_s * FPS))
    by_id = {s["id"]: s for s in plan["sentences"]}

    # ---------- shots -> beats (v2 pacing) ----------
    import hashlib
    import random

    from . import beats as B

    pc = cfg["pacing"]["beat"]
    acfg = cfg["audio"]
    grade_map = cfg["style"]["acts"]
    rng = random.Random(int(hashlib.sha1(plan["slug"].encode()).hexdigest()[:8], 16))

    # voice envelope for lip-sync (0..1 per frame, from the real TTS audio)
    env = [0.0] * (total_frames + 2)
    for s in plan["sentences"]:
        e = voice_env(s["file"])
        f0 = int(round(s["start"] * FPS))
        for i, v in enumerate(e):
            if f0 + i < len(env):
                env[f0 + i] = max(env[f0 + i], v)
    for i in range(1, len(env)):
        env[i] = max(env[i], env[i - 1] * 0.55)
    voice_env_q = [round(v, 2) for v in env[:total_frames]]

    shots_in = plan["shots"]
    starts = [0 if k == 0 else int(round(by_id[sh["sentences"][0]]["start"] * FPS)) for k, sh in enumerate(shots_in)]
    bg_dir_out = os.path.join(out_dir, "bg")
    os.makedirs(bg_dir_out, exist_ok=True)
    have = {}
    for f in glob.glob(os.path.join(img_dir, "**", "*.jpg"), recursive=True):
        b = os.path.basename(f)
        if b.count(".") == 2:
            have[b[:-4]] = True
    for f in glob.glob(os.path.join(img_dir, "**", "*.*"), recursive=True):
        if os.path.splitext(f)[1] in (".jpg", ".webp"):
            shutil.copy(f, os.path.join(bg_dir_out, os.path.basename(f)))
    chapter_first = {ch["shots"][0]: ch for ch in plan["chapters"]}
    ELECTRONIC = ("phone_alert", "phone_web", "phone_video", "phone_call", "phone_search", "tv_news", "glitch_text")
    IMPACT = ("thunder", "glass_crack", "power_down", "alert_siren")
    timeline_shots, sfx_events, ambience, music_runs = [], [], [], []
    prev_frm, last_frms, prev_cam, prev_tr, prev_views, prev_loc, beat_no = None, [], None, "cut", [], None, 0
    for k, sh in enumerate(shots_in):
        s_start = starts[k]
        s_end = starts[k + 1] if k + 1 < len(shots_in) else total_frames
        cands = []
        for sid in sh["sentences"]:
            sn = by_id[sid]
            if sid != sh["sentences"][0]:
                cands.append((sn["start"], 1.0))
            cands += B.clause_cuts(sn["text"], sn["start"], sn["end"])
        parts = B.split_beats(s_start / FPS, s_end / FPS, cands, pc)
        edges = [s_start]
        for a, _ in parts[1:]:
            fr = int(round(a * FPS))
            if fr - edges[-1] >= 12 and s_end - fr >= 12:
                edges.append(fr)
        edges.append(s_end)
        key = f"{sh['location']}.{sh['variant']}"
        bg = f"bg/{key}.jpg" if key in have else None
        layers = None
        if bg and os.path.exists(os.path.join(bg_dir_out, f"{key}.far.jpg")):
            layers = {"far": f"bg/{key}.far.jpg"}
            for nm in ("mid", "near"):
                if os.path.exists(os.path.join(bg_dir_out, f"{key}.{nm}.webp")):
                    layers[nm] = f"bg/{key}.{nm}.webp"
        if bg is None:
            notes.append({"shot": k, "fix": "backdrop_fallback", "key": key})
        desc = plan["locations"].get(sh["location"], "").lower()
        indoor = any(w in desc for w in ("apartment", "kitchen", "corridor", "stairwell", "shop", "room"))
        amb = "room" if indoor else "city"
        if sh["variant"] == "blackout":
            amb = "hum_dark" if indoor else "wind"
        act = sh.get("act") or (timeline_shots[-1]["act"] if timeline_shots else "hook")
        tension = B.tension_of([c["expr"] for c in sh["chars"]], act)
        for j in range(len(edges) - 1):
            f0, f1 = edges[j], edges[j + 1]
            dur = f1 - f0
            dur_s = dur / FPS
            first = j == 0
            has_ov = bool(sh["overlay"]) and first
            frm = B.choose_framing(len(sh["chars"]), has_ov, tension, prev_frm, last_frms, rng)
            view = B.view_for(frm, beat_no, prev_views)
            cam = fix_camera(B.choose_camera(tension, frm, dur_s, prev_cam, rng), dur_s, cfg, notes, beat_no)
            prev_cam = cam["preset"]
            chars_in = []
            btext = " ".join(by_id[sid]["text"] for sid in sh["sentences"] if f0 / FPS - 0.2 <= by_id[sid]["start"] < f1 / FPS + 0.2) or sh["text"]
            for ci, c in enumerate(sh["chars"]):
                pose, expr = B.acting(btext, c["pose"], c["expr"], j, rng)
                chars_in.append({**c, "pose": pose, "expr": expr})
            chars = layout_beat(chars_in, frm, view, beat_no, has_ov)
            fullchars = [{**c, "rig": plan["characters"][c["id"]]["rig"], "params": plan["characters"][c["id"]]["params"], "speaks": ci == 0}
                         for ci, c in enumerate(chars)]
            fx_ = 0.5
            if chars:
                fx_ = clamp(sum(c["x"] for c in chars) / len(chars), 0.3, 0.7)
            fy_ = {"closeup": 0.42, "insert": 0.5, "low": 0.38, "wide": 0.6, "xwide": 0.62}.get(frm, 0.55)
            ov = None
            if has_ov:
                ov = {**sh["overlay"], "inFrame": 4, "outFrame": max(24, dur - 3)}
            tc = {"text": chapter_first[sh["i"]]["time_card"], "frames": min(72, dur)} if (first and sh["i"] in chapter_first) else None
            electronics = bool(sh["overlay"] and sh["overlay"]["name"] in ELECTRONIC) or "glitch" in sh["fx"]
            impact = any(x in IMPACT for x in sh["sfx"])
            tr = B.pick_transition(beat_no, first, first and prev_loc is not None and prev_loc != key, first and sh["i"] in chapter_first,
                                   first and bool(sh.get("silence")), first and electronics, first and impact, prev_tr, rng)
            prev_tr, prev_frm, prev_loc = tr, frm, key
            last_frms = (last_frms + [frm])[-3:]
            prev_views = (prev_views + [view])[-3:]
            crowd = ("crowd" in sh["fx"]) or (frm in ("wide", "xwide") and not indoor and sh["variant"] != "blackout" and sh["location"] in ("street", "gas_station"))
            tl_shot = {
                "i": len(timeline_shots), "chapter": sh["chapter"], "start": f0, "dur": dur, "location": sh["location"], "variant": sh["variant"],
                "bg": bg, "layers": layers, "floorY": 0.9, "chars": fullchars, "overlay": ov,
                "camera": {**cam, "fx": round(fx_, 3), "fy": fy_}, "fx": sh["fx"] if first else [x for x in sh["fx"] if x not in ("glitch", "alarm_pulse")] + [],
                "banner": sh["banner"] if first else None, "cta": bool(sh["cta"]) and first, "timeCard": tc, "track": sh["track"], "prevTrack": sh["prev_track"],
                "text": btext, "framing": frm, "trans": tr, "grade": grade_map.get(act, "warm"), "act": act, "crowd": bool(crowd),
                "tension": tension,
            }
            timeline_shots.append(tl_shot)
            t0 = f0 / FPS
            if first:
                for jj, name in enumerate(sh["sfx"]):
                    sfx_events.append({"t": round(t0 + 0.04 + 0.12 * jj, 3), "name": name, "gain": 0.0})
                if sh["i"] in chapter_first:
                    sfx_events.append({"t": round(t0, 3), "name": "stinger_chapter", "gain": 0.0})
                if sh["cta"]:
                    sfx_events.append({"t": round(t0 + 0.2, 3), "name": "click", "gain": -4.0})
                if sh["banner"]:
                    sfx_events.append({"t": round(t0, 3), "name": "whoosh", "gain": -3.0})
            tsfx = {"whip": ("whoosh", -5.0), "smash": ("impact", -2.0), "flash": ("impact", -7.0), "glitch": ("glitch", -6.0), "punch": ("text_pop", -9.0)}.get(tr)
            if tsfx and not (first and sh["banner"]):
                sfx_events.append({"t": round(t0 + 0.02, 3), "name": tsfx[0], "gain": tsfx[1]})
            if cam["preset"] in ("whip_to",):
                sfx_events.append({"t": round(t0 + 0.05, 3), "name": "whoosh", "gain": -7.0})
            if ambience and ambience[-1]["kind"] == amb and abs(ambience[-1]["end"] - t0) < 0.05:
                ambience[-1]["end"] = round(f1 / FPS, 3)
            else:
                ambience.append({"start": round(t0, 3), "end": round(f1 / FPS, 3), "kind": amb})
            if music_runs and music_runs[-1]["act"] == act:
                music_runs[-1]["end"] = round(f1 / FPS, 3)
            else:
                music_runs.append({"act": act, "start": round(t0, 3), "end": round(f1 / FPS, 3)})
            beat_no += 1
        for sid in sh["sentences"]:
            sn = by_id[sid]
            sn["room"] = "indoor" if indoor else "outdoor"
    # silence beats: riser into the gap, silence, impact on the reveal
    silences = []
    for s in plan["sentences"]:
        if s.get("silence_before"):
            prev = plan["sentences"][s["idx"] - 1]
            a, b = prev["end"] + 0.12, s["start"] - 0.02
            if b - a >= 0.4:
                silences.append([round(a, 3), round(b, 3)])
                sfx_events.append({"t": round(max(0.1, a - 1.3), 3), "name": "riser", "gain": -4.0})
                sfx_events.append({"t": round(s["start"], 3), "name": "impact", "gain": -3.0})
    # keyword sfx
    for s in plan["sentences"]:
        for pat, name in KEYWORD_SFX:
            if re.search(pat, s["text"].lower()):
                if not any(e["name"] == name and abs(e["t"] - s["start"]) < 2.0 for e in sfx_events):
                    sfx_events.append({"t": round(s["start"] + 0.1, 3), "name": name, "gain": -6.0})
    # sfx coverage: no gap longer than sfx_gap_max_s (silence beats excluded)
    gap_max = float(acfg.get("sfx_gap_max_s", 3.8))
    fill = ["rustle", "click", "footsteps", "rustle"]
    n_fill, evs = 0, sorted(sfx_events, key=lambda e: e["t"])
    marks = [lead_in] + [e["t"] for e in evs] + [audio_end]
    for a, b in zip(marks, marks[1:]):
        t = a
        while b - t > gap_max:
            t += gap_max * 0.85
            if not any(sa <= t <= sb for sa, sb in silences):
                sfx_events.append({"t": round(t, 3), "name": fill[n_fill % 4], "gain": -5.0})
                n_fill += 1

    timeline = {
        "fps": FPS, "width": 1920, "height": 1080, "durationInFrames": total_frames,
        "style": {"accent": plan["style"].get("accent", "amber"), "lut": plan["style"].get("lut", "cold_night"),
                  "titlecard": plan["style"].get("titlecard", "clock_strip"), "transition": plan["style"].get("transition", "hard_cuts")},
        "shots": timeline_shots, "endScreenFrames": int(end_s * FPS), "fadeOut": 30,
        "captions": build_captions(plan["sentences"], B),
        "voiceEnv": voice_env_q,
    }
    final_shots = timeline_shots
    json.dump({"timeline": timeline}, open(os.path.join(out_dir, "props.json"), "w", encoding="utf-8"))

    # ---------- chunks ----------
    chunk_f = int(cfg["render"]["chunk_seconds"]) * FPS
    nchunks = math.ceil(total_frames / chunk_f)
    while nchunks > int(cfg["render"]["max_chunks"]):
        chunk_f += FPS * 5
        nchunks = math.ceil(total_frames / chunk_f)
    chunks = [{"i": i, "from": i * chunk_f, "to": min(total_frames, (i + 1) * chunk_f) - 1} for i in range(nchunks)]
    json.dump(chunks, open(os.path.join(out_dir, "chunks.json"), "w"))

    # ---------- audio plan ----------
    chapters_out = []
    for ci, ch in enumerate(plan["chapters"]):
        first = starts[ch["shots"][0]] / FPS
        nxt = starts[plan["chapters"][ci + 1]["shots"][0]] / FPS if ci + 1 < len(plan["chapters"]) else total_s
        chapters_out.append({"n": ch["n"], "title": ch["time_card"], "start": round(first, 3), "end": round(nxt, 3), "mood": ch["mood"]})
    audio_plan = {
        "total_s": round(total_s, 3), "audio_end_s": round(audio_end, 3), "lead_in_s": lead_in, "end_screen_s": end_s,
        "voice": [{"id": s["id"], "start": s["start"], "end": s["end"], "file": os.path.basename(s["file"]), "room": s.get("room", "indoor")} for s in plan["sentences"]],
        "music": [{"act": r["act"], "start": r["start"], "end": r["end"] if i + 1 < len(music_runs) else round(total_s, 3),
                   "mood": acfg["music_mood"].get(r["act"], "tense"), "db": float(acfg["intensity_db"].get(r["act"], 0.0))}
                  for i, r in enumerate(music_runs)],
        "ambience": ambience, "silence": silences, "chapters": chapters_out,
        "sfx": sorted(sfx_events, key=lambda e: e["t"]), "style": plan["style"],
    }
    json.dump(audio_plan, open(os.path.join(out_dir, "audio_plan.json"), "w", encoding="utf-8"), indent=1)
    voice_dir = os.path.join(out_dir, "voice")
    os.makedirs(voice_dir, exist_ok=True)
    for s in plan["sentences"]:
        shutil.copy(s["file"], os.path.join(voice_dir, os.path.basename(s["file"])))

    # ---------- captions + chapters ----------
    with open(os.path.join(out_dir, "captions.srt"), "w", encoding="utf-8") as fh:
        for i, s in enumerate(plan["sentences"], 1):
            fh.write(f"{i}\n{srt_time(s['start'])} --> {srt_time(min(s['end'] + 0.25, s['end'] + s['pause_after_s']))}\n{wrap_caption(s['text'])}\n\n")
    json.dump({"chapters": chapters_out, "total_s": round(total_s, 2)}, open(os.path.join(out_dir, "chapters.json"), "w"), indent=1)

    wers = [tmeta[s["id"]]["wer"] for s in plan["sentences"] if s["id"] in tmeta]
    report = {
        "slug": plan["slug"], "total_s": round(total_s, 2), "narration_s": round(audio_end - lead_in, 2), "shots": len(final_shots),
        "sentences": len(plan["sentences"]), "chunks": len(chunks), "tts_engines": sorted(e for e in engines if e),
        "tts_flagged": [i for i, m in tmeta.items() if not m.get("ok", True)], "wer_mean": round(sum(wers) / max(1, len(wers)), 4),
        "fixes": notes, "backdrop_fallbacks": [n["key"] for n in notes if n["fix"] == "backdrop_fallback"],
        "words": plan["total_words"], "wpm_effective": round(plan["total_words"] / (total_s / 60.0), 1),
        "base_name_runtime_min": int(round(total_s / 60.0)),
    }
    json.dump(report, open(os.path.join(out_dir, "assemble_report.json"), "w", encoding="utf-8"), indent=1)
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as fh:
            fh.write("chunks=" + json.dumps([c["i"] for c in chunks]) + "\n")
    if public_dir:
        dst = os.path.join(public_dir, "bg")
        os.makedirs(dst, exist_ok=True)
        for f in glob.glob(os.path.join(bg_dir_out, "*")):
            shutil.copy(f, dst)
    print(json.dumps({k: report[k] for k in ("total_s", "shots", "sentences", "chunks", "tts_engines", "wer_mean", "wpm_effective")}))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--tts", required=True)
    ap.add_argument("--images", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--public", default=None)
    a = ap.parse_args(argv)
    return run(a.plan, a.tts, a.images, a.out, a.public)


if __name__ == "__main__":
    sys.exit(main())

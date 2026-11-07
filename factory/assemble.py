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
    if preset in ("push", "pull"):
        speed = abs(z1 / max(z0, 1e-6) - 1) / max(dur_s, 0.2)
        target = clamp(speed, smin * 1.15, smax * 0.9)
        r = target * dur_s
        low = clamp(min(z0, z1), lo, hi / (1 + r))
        high = low * (1 + r)
        n0, n1 = (low, high) if preset == "push" else (high, low)
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

    # ---------- shots ----------
    shots_in = plan["shots"]
    starts = []
    for k, sh in enumerate(shots_in):
        first = by_id[sh["sentences"][0]]
        starts.append(0 if k == 0 else int(round(first["start"] * FPS)))
    # bg files
    bg_dir_out = os.path.join(out_dir, "bg")
    os.makedirs(bg_dir_out, exist_ok=True)
    have = {}
    for f in glob.glob(os.path.join(img_dir, "**", "*.jpg"), recursive=True):
        b = os.path.basename(f)
        if b.count(".") == 2:  # loc.variant.jpg (layers have .far.jpg etc)
            have[b[:-4]] = True
    for f in glob.glob(os.path.join(img_dir, "**", "*.*"), recursive=True):
        if os.path.splitext(f)[1] in (".jpg", ".webp"):
            shutil.copy(f, os.path.join(bg_dir_out, os.path.basename(f)))
    timeline_shots = []
    chapter_first = {}
    for ch in plan["chapters"]:
        chapter_first[ch["shots"][0]] = ch
    sfx_events = []
    for k, sh in enumerate(shots_in):
        start = starts[k]
        end = starts[k + 1] if k + 1 < len(shots_in) else total_frames
        dur = end - start
        dur_s = dur / FPS
        key = f"{sh['location']}.{sh['variant']}"
        bg = f"bg/{key}.jpg" if key in have else None
        layers = None
        if bg and os.path.exists(os.path.join(bg_dir_out, f"{key}.far.jpg")):
            layers = {"far": f"bg/{key}.far.jpg"}
            if os.path.exists(os.path.join(bg_dir_out, f"{key}.mid.webp")):
                layers["mid"] = f"bg/{key}.mid.webp"
            if os.path.exists(os.path.join(bg_dir_out, f"{key}.near.webp")):
                layers["near"] = f"bg/{key}.near.webp"
        if bg is None:
            notes.append({"shot": k, "fix": "backdrop_fallback", "key": key})
        cam = fix_camera(sh["camera"], dur_s, cfg, notes, k)
        chars = layout_chars(sh["chars"], k)
        params = {c["id"]: plan["characters"][c["id"]]["params"] for c in sh["chars"]}
        fullchars = [{**c, "rig": plan["characters"][c["id"]]["rig"], "params": params[c["id"]]} for c in chars]
        fx = 0.5
        if chars:
            fx = clamp(sum(c["x"] for c in chars) / len(chars), 0.3, 0.7)
        ov = None
        if sh["overlay"]:
            if sh["overlay"]["name"] == "end_screen":
                ov = {**sh["overlay"], "inFrame": max(0, dur - int(end_s * FPS)), "outFrame": dur}
            else:
                ov = {**sh["overlay"], "inFrame": 4, "outFrame": max(24, dur - 3)}
        tc = None
        if sh["i"] in chapter_first:
            tc = {"text": chapter_first[sh["i"]]["time_card"], "frames": min(72, dur)}
        timeline_shots.append({
            "i": sh["i"], "chapter": sh["chapter"], "start": start, "dur": dur, "location": sh["location"], "variant": sh["variant"],
            "bg": bg, "layers": layers, "floorY": 0.9, "chars": fullchars, "overlay": ov,
            "camera": {**cam, "fx": round(fx, 3), "fy": 0.55}, "fx": sh["fx"], "banner": sh["banner"], "cta": sh["cta"],
            "timeCard": tc, "track": sh["track"], "prevTrack": sh["prev_track"], "text": sh["text"],
        })
        # sfx from tags
        t0 = start / FPS
        for j, name in enumerate(sh["sfx"]):
            sfx_events.append({"t": round(t0 + 0.04 + 0.12 * j, 3), "name": name, "gain": 0.0})
        if sh["i"] in chapter_first:
            sfx_events.append({"t": round(t0, 3), "name": "stinger_chapter", "gain": 0.0})
        if sh["cta"]:
            sfx_events.append({"t": round(t0 + 0.2, 3), "name": "click", "gain": -4.0})
        if sh["banner"]:
            sfx_events.append({"t": round(t0, 3), "name": "whoosh", "gain": -3.0})
    # keyword sfx
    for s in plan["sentences"]:
        for pat, name in KEYWORD_SFX:
            if re.search(pat, s["text"].lower()):
                if not any(e["name"] == name and abs(e["t"] - s["start"]) < 2.0 for e in sfx_events):
                    sfx_events.append({"t": round(s["start"] + 0.1, 3), "name": name, "gain": -6.0})

    # long-shot auto-split (shots > max_s): split at a sentence boundary when >= 2 sentences, keep overlay on the first part only
    notes_split = 0
    maxf = int(float(cfg["shots"]["max_s"]) * FPS)
    final_shots = []
    for sh in timeline_shots:
        src = shots_in[sh["i"]]
        if sh["dur"] > maxf and len(src["sentences"]) >= 2 and not (sh["overlay"] and sh["overlay"]["name"] == "end_screen"):
            cut_sent = by_id[src["sentences"][len(src["sentences"]) // 2]]
            cut = int(round(cut_sent["start"] * FPS))
            a = {**sh, "dur": cut - sh["start"]}
            b = {**sh, "start": cut, "dur": sh["start"] + sh["dur"] - cut, "overlay": None, "timeCard": None, "banner": None, "cta": False}
            b["camera"] = fix_camera({**sh["camera"], "z0": sh["camera"]["z1"], "z1": min(1.35, sh["camera"]["z1"] * 1.05)}, b["dur"] / FPS, cfg, [], sh["i"])
            b["camera"]["fx"], b["camera"]["fy"] = sh["camera"]["fx"], sh["camera"]["fy"]
            final_shots += [a, b]
            notes_split += 1
            notes.append({"shot": sh["i"], "fix": "long_shot_split"})
        else:
            final_shots.append(sh)
    for n, sh in enumerate(final_shots):
        sh["i"] = n

    timeline = {
        "fps": FPS, "width": 1920, "height": 1080, "durationInFrames": total_frames,
        "style": {"accent": plan["style"].get("accent", "amber"), "lut": plan["style"].get("lut", "cold_night"),
                  "titlecard": plan["style"].get("titlecard", "clock_strip"), "transition": plan["style"].get("transition", "hard_cuts")},
        "shots": final_shots, "endScreenFrames": int(end_s * FPS),
    }
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
        first = timeline_shots[ch["shots"][0]]["start"] / FPS
        nxt = timeline_shots[plan["chapters"][ci + 1]["shots"][0]]["start"] / FPS if ci + 1 < len(plan["chapters"]) else total_s
        chapters_out.append({"n": ch["n"], "title": ch["time_card"], "start": round(first, 3), "end": round(nxt, 3), "mood": ch["mood"]})
    audio_plan = {
        "total_s": round(total_s, 3), "audio_end_s": round(audio_end, 3), "lead_in_s": lead_in, "end_screen_s": end_s,
        "voice": [{"id": s["id"], "start": s["start"], "end": s["end"], "file": os.path.basename(s["file"])} for s in plan["sentences"]],
        "music": chapters_out, "sfx": sorted(sfx_events, key=lambda e: e["t"]), "style": plan["style"],
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

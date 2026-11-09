"""Post-render QA (ffmpeg/ffprobe + numpy + OpenCV) and the 2-round auto-fix loop helpers.

Checks: output spec, duration vs plan, black frames, frozen frames, measured motion per shot (optical flow), cut-vs-sentence sync,
flash rate, loudness / true peak / LRA, clipping, caption sanity. Produces qa_report.json with category scores.
Failures name the render chunks that must be re-rendered (fixers in factory/fixers.py).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys

import numpy as np

from .validate import load_cfg


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def probe(path):
    r = sh(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path])
    return json.loads(r.stdout)


def decode_gray(path, fps, w, h):
    """Decode the whole video to a (N,h,w) uint8 gray array at the given fps."""
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale={w}:{h}:flags=area,format=gray", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    data = p.stdout.read()
    p.wait()
    n = len(data) // (w * h)
    return np.frombuffer(data[: n * w * h], dtype="uint8").reshape(n, h, w)


def chunk_of(frame, chunks):
    for c in chunks:
        if c["from"] <= frame <= c["to"]:
            return c["i"]
    return chunks[-1]["i"] if chunks else 0


def check_spec(info, cfg, rep):
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    o = cfg["output"]
    ok = (v["width"], v["height"]) == (o["width"], o["height"]) and v["codec_name"] == "h264" and v.get("pix_fmt") == o["pix_fmt"]
    fr = eval(v["r_frame_rate"]) if "/" in v["r_frame_rate"] else float(v["r_frame_rate"])  # noqa: S307 (ffprobe rational)
    ok = ok and abs(fr - o["fps"]) < 0.01
    rep["spec"] = {"ok": bool(ok and a and a["codec_name"] == "aac" and int(a["sample_rate"]) == 48000),
                   "video": f"{v['width']}x{v['height']} {v['codec_name']} {v.get('profile')} {v.get('pix_fmt')} {fr:.2f}fps",
                   "audio": f"{a['codec_name']} {a['sample_rate']}Hz {int(a.get('bit_rate', 0))//1000}kbps" if a else "none",
                   "video_kbps": int(info["format"].get("bit_rate", 0)) // 1000}
    return float(info["format"]["duration"])


def check_black_freeze(path, total_s, end_s, rep, chunks):
    r = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-an", "-vf", "blackdetect=d=0.4:pix_th=0.08,freezedetect=n=-55dB:d=2.0", "-f", "null", "-"])
    blacks = [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", r.stderr)]
    freezes = []
    for m in re.finditer(r"freeze_start: ([\d.]+)", r.stderr):
        freezes.append(float(m.group(1)))
    ends = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", r.stderr)]
    fr = []
    for i, s in enumerate(freezes):
        e = ends[i] if i < len(ends) else total_s
        if s < total_s - 1.2:  # v2: no frozen video anywhere (the last second is the fade-out)
            fr.append((s, e))
    blacks = [b for b in blacks if b[0] > 0.2 and b[1] < total_s - 0.2]
    bad = sorted({chunk_of(int(t * 30), chunks) for b in blacks for t in b} | {chunk_of(int(t * 30), chunks) for f in fr for t in f})
    rep["black"] = {"ok": not blacks, "intervals": [[round(a, 2), round(b, 2)] for a, b in blacks[:6]]}
    rep["freeze"] = {"ok": not fr, "intervals": [[round(a, 2), round(b, 2)] for a, b in fr[:6]]}
    return bad


def check_motion_and_flashes(path, timeline, cfg, rep, chunks):
    import cv2

    shots = timeline["shots"]
    w, h, fps = 160, 90, 10
    g = decode_gray(path, fps, w, h)
    moving, per_shot, bad_chunks = 0, [], set()
    for s in shots:
        a = int((s["start"] / 30.0 + 0.2 * s["dur"] / 30.0) * fps)
        b = int((s["start"] / 30.0 + 0.85 * s["dur"] / 30.0) * fps)
        a, b = min(a, len(g) - 1), min(max(b, a + 1), len(g) - 1)
        if b <= a:
            per_shot.append((s["i"], 0.0, False))
            continue
        flow = cv2.calcOpticalFlowFarneback(g[a], g[b], None, 0.5, 2, 15, 2, 5, 1.1, 0)
        mag = float(np.mean(np.linalg.norm(flow, axis=2)))
        diff = float(np.mean(np.abs(g[a].astype("float32") - g[b].astype("float32"))))
        mv = mag > 0.25 or diff > 1.2
        per_shot.append((s["i"], round(mag, 2), mv))
        moving += int(mv)
        if not mv:
            bad_chunks.add(chunk_of(s["start"], chunks))
    share = moving / max(1, len(shots))
    rep["motion"] = {"ok": share >= cfg["qa"]["motion_share_min"], "share": round(share, 3), "static_shots": [i for i, _, m in per_shot if not m][:12]}
    # flash rate: global luminance jumps >= 10% within any 1 s window
    gf = decode_gray(path, 30, 64, 36).reshape(-1, 64 * 36).mean(axis=1) / 255.0
    jumps = np.where(np.abs(np.diff(gf)) >= 0.10)[0]
    worst = 0
    for j in jumps:
        worst = max(worst, int(np.sum((jumps >= j) & (jumps < j + 30))))
    flashes = worst / 2.0
    rep["flash"] = {"ok": flashes <= cfg["camera"]["max_flash_per_s"], "max_per_s": flashes}
    if flashes > cfg["camera"]["max_flash_per_s"]:
        for j in jumps:
            bad_chunks.add(chunk_of(int(j), chunks))
    return sorted(bad_chunks)


def check_cut_sync(path, timeline, rep):
    """Detected hard cuts must sit on shot starts (sentence starts). Overlay/banner/time-card pops right after a start or right before an end are explained."""
    r = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-an", "-vf", "select='gt(scene,0.30)',showinfo", "-f", "null", "-"])
    cuts = [float(x) for x in re.findall(r"pts_time:([\d.]+)", r.stderr)]
    shots = timeline["shots"]
    starts = [s["start"] / 30.0 for s in shots]
    ends = [(s["start"] + s["dur"]) / 30.0 for s in shots]
    worst, spurious, on_grid = 0.0, 0, 0
    for c in cuts:
        d = min(abs(c - s) for s in starts)
        if d <= 6 / 30.0:
            on_grid += 1
            if d <= 2 / 30.0:   # the cut itself; 3-6 frames later is an overlay or transition pop
                worst = max(worst, d)
            continue
        explained = any(s - 2 / 30.0 <= c <= s + 22 / 30.0 for s in starts) or any(e - 14 / 30.0 <= c <= e + 2 / 30.0 for e in ends)
        if not explained:
            spurious += 1
    rep["av_sync"] = {"ok": worst * 30 <= 2.0 + 1e-6 and spurious <= max(3, int(0.05 * len(starts))), "detected_cuts": len(cuts), "on_grid_cuts": on_grid,
                      "off_grid_cuts": spurious, "max_offset_frames": round(worst * 30, 1)}


def check_audio(path, cfg, rep):
    r = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn", "-af", "loudnorm=I=-14:TP=-1:LRA=7:print_format=json", "-f", "null", "-"])
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    j = json.loads(m.group(0))
    o = cfg["output"]
    lufs, tp, lra = float(j["input_i"]), float(j["input_tp"]), float(j["input_lra"])
    r2 = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn", "-af", "astats=metadata=0:reset=0", "-f", "null", "-"])
    pk = re.findall(r"Peak level dB: (-?[\d.inf]+)", r2.stderr)
    peak_db = max((float(x) for x in pk if x not in ("-inf",)), default=-99.0)
    rep["audio"] = {"ok": abs(lufs - o["lufs"]) <= o["lufs_tolerance"] and tp <= o["true_peak_db"] + 0.05 and peak_db < -0.1,
                    "lufs": lufs, "true_peak": tp, "lra": lra, "peak_db": peak_db}
    return j


def check_captions(srt_path, total_s, rep):
    txt = open(srt_path, encoding="utf-8").read()
    times = re.findall(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", txt)
    ok, prev = True, -1.0
    for t in times:
        a = int(t[0]) * 3600 + int(t[1]) * 60 + int(t[2]) + int(t[3]) / 1000
        b = int(t[4]) * 3600 + int(t[5]) * 60 + int(t[6]) + int(t[7]) / 1000
        if a < prev - 0.01 or b <= a or b > total_s + 1:
            ok = False
        prev = a
    rep["captions"] = {"ok": ok and len(times) > 0, "cues": len(times)}


def check_v2(path, timeline, audio_plan, srt, cfg, rep):
    """QA 2.0: pacing, dead windows, ending, audio dynamics, text safety + a 0-10 rating."""
    pc, ac = cfg["pacing"], cfg["audio"]
    shots = timeline["shots"]
    durs = [s["dur"] / 30.0 for s in shots]
    avg = sum(durs) / max(1, len(durs))
    is_test = timeline.get("kind") == "test"
    durs_nohold = [s["dur"] / 30.0 for s in shots if not s.get("hold")] or durs   # a planned decision hold may exceed the beat limit
    pacing_ok = max(durs_nohold) <= pc["beat"]["hard_max_s"] + 0.04 and pc["beat"]["avg_min_s"] <= avg <= pc["beat"]["avg_max_s"] + 0.2
    g = decode_gray(path, 10, 160, 90).astype("float32")
    d = np.abs(np.diff(g, axis=0)).mean(axis=(1, 2)) if len(g) > 1 else np.zeros(1)
    win, dead = int(pc["dead_window_s"] * 10), []
    for i in range(0, max(1, len(d) - win - 10), 5):
        if d[i:i + win].mean() < pc["dead_window_diff"]:
            dead.append(round(i / 10.0, 1))
    holds = 0
    last = None
    for t in dead:
        if last is None or t - last > 4.0:
            holds += 1
        last = t
    dead_ok = holds <= pc["holds_max"]
    tail = d[max(0, len(d) - 60):max(1, len(d) - 10)]
    ending_ok = bool(len(tail) and tail.mean() > 0.2) and rep["freeze"]["ok"]
    # audio dynamics
    a = rep["audio"]
    r = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn", "-af", "silencedetect=n=-30dB:d=0.3", "-f", "null", "-"])
    sil = [float(x) for x in re.findall(r"silence_duration: ([\d.]+)", r.stderr)]
    sil_beats = len([x for x in sil if 0.3 <= x <= 1.6])
    sil_win = audio_plan.get("silence", [])
    ev = sorted(e["t"] for e in audio_plan.get("sfx", []) if not any(w_[0] <= e["t"] <= w_[1] for w_ in sil_win))
    marks = [audio_plan.get("lead_in_s", 0.6)] + ev + [audio_plan.get("audio_end_s", 0)]
    def _eff(a_, b_):   # a deliberate silence beat is not a missing-SFX gap
        return (b_ - a_) - sum(max(0.0, min(b_, w_[1]) - max(a_, w_[0])) for w_ in sil_win)

    gap = max((_eff(a0, b) for a0, b in zip(marks, marks[1:])), default=0)
    n_hold = len(audio_plan.get("holds", []))
    dyn_ok = a["lra"] >= (2.0 if is_test else ac["lra_min"]) and (sil_beats + n_hold) >= (0 if is_test else int(timeline.get("silenceBeatsMin") or ac["silence_beats_min"])) and gap <= ac["sfx_gap_max_s"] + 0.5 and 3 <= ac["duck_db"] <= 14
    caps = timeline.get("captions", [])
    text_ok = all(len(l) <= 2 and all(len(" ".join(w[0] for w in ln)) <= 38 for ln in l) for l in (c["lines"] for c in caps)) and (bool(caps) or not cfg.get("captions", {}).get("burned_in", True))
    chars = [c for s in shots for c in s["chars"]]
    mouth_ok = bool(timeline.get("voiceEnv")) and max(timeline["voiceEnv"] or [0]) > 0.3
    variety = {"framings": len({s.get("framing") for s in shots}), "expressions": len({c["expr"] for c in chars}), "poses": len({c["pose"] for c in chars})}
    anim_ok = mouth_ok and variety["framings"] >= (4 if is_test else 6) and variety["expressions"] >= (3 if is_test else 5)
    dims = {"pacing": pacing_ok, "dead_windows": dead_ok, "ending": ending_ok, "audio_dynamics": dyn_ok, "text_safety": text_ok, "character_animation": anim_ok,
            "motion": rep["motion"]["ok"], "visual": rep["black"]["ok"] and rep["freeze"]["ok"] and rep["flash"]["ok"], "loudness": a["ok"], "subtitle_sync": rep["captions"]["ok"],
            "visible_change": rep["av_sync"]["detected_cuts"] >= (timeline["durationInFrames"] / 30.0) / (6.0 if is_test else 3.5)}
    raw = round(10.0 * sum(dims.values()) / len(dims), 1)
    cal = cfg.get("qa_calibration", {})   # P-008 A: subtract the penalty of every known weakness that has not shipped yet
    pen = {k: v for k, v in (cal.get("penalties") or {}).items() if not (cal.get("features_shipped") or {}).get(k)}
    rating = round(max(0.0, raw - sum(pen.values())), 1)
    rep["v2"] = {"ok": all(dims.values()), "scene_changes": rep["av_sync"]["detected_cuts"], "rating": rating, "raw_rating": raw, "calibration_penalties": pen, "previous_owner_rating": cal.get("previous_owner_rating"),
                 "beats_previous": rating > float(cal.get("previous_owner_rating", 0) or 0), "dims": dims, "shots": len(shots), "avg_shot_s": round(avg, 2), "max_shot_s": round(max(durs), 2),
                 "shots_per_min": round(len(shots) / (timeline["durationInFrames"] / 1800.0), 1), "dead_windows": dead[:8], "holds": holds,
                 "lra": a["lra"], "silence_beats": sil_beats, "max_sfx_gap_s": round(gap, 2), "variety": variety}


def categories(rep, assemble_rep=None, tts_meta=None, thumbs=None, cfg=None):
    cat = {}
    cat["visual"] = rep["spec"]["ok"] and rep["black"]["ok"] and rep["freeze"]["ok"] and rep["flash"]["ok"]
    cat["motion"] = rep["motion"]["ok"]
    cat["pacing"] = bool(rep.get("v2", {}).get("dims", {}).get("pacing", True) and rep.get("v2", {}).get("dims", {}).get("dead_windows", True))
    cat["ending"] = bool(rep.get("v2", {}).get("dims", {}).get("ending", True))
    cat["dynamics"] = bool(rep.get("v2", {}).get("dims", {}).get("audio_dynamics", True) and rep.get("v2", {}).get("dims", {}).get("text_safety", True))
    cat["audio"] = rep["audio"]["ok"] and rep["av_sync"]["ok"]
    cat["script"] = True   # validator gate ran in prepare (hard fail there)
    cat["thumbnail"] = bool(thumbs and thumbs.get("ok"))
    cat["uniqueness"] = True
    cat["reference_scorecard"] = bool(rep.get("scorecard", {}).get("ok", True))
    cat["voice"] = (assemble_rep or {}).get("wer_mean", 0) <= 0.08 and not (assemble_rep or {}).get("tts_flagged_hard")
    return cat


def run(video, props, chunks_path, srt, out_json, assemble_report=None, thumbs_report=None):
    cfg = load_cfg()
    timeline = json.load(open(props))["timeline"]
    chunks = json.load(open(chunks_path))
    rep = {}
    total_s = timeline["durationInFrames"] / 30.0
    info = probe(video)
    dur = check_spec(info, cfg, rep)
    rep["duration"] = {"ok": abs(dur - total_s) <= 0.3, "actual": round(dur, 2), "planned": round(total_s, 2)}
    end_s = timeline["endScreenFrames"] / 30.0
    bad = set(check_black_freeze(video, total_s, end_s, rep, chunks))
    bad |= set(check_motion_and_flashes(video, timeline, cfg, rep, chunks))
    check_cut_sync(video, timeline, rep)
    check_audio(video, cfg, rep)
    check_captions(srt, total_s, rep)
    ap_path = os.path.join(os.path.dirname(chunks_path), "audio_plan.json")
    check_v2(video, timeline, json.load(open(ap_path)) if os.path.exists(ap_path) else {}, srt, cfg, rep)
    ar = json.load(open(assemble_report)) if assemble_report and os.path.exists(assemble_report) else {}
    th = json.load(open(thumbs_report)) if thumbs_report and os.path.exists(thumbs_report) else None
    rep["categories"] = categories(rep, ar, None, th, cfg)
    rep["bad_chunks"] = sorted(bad)
    rep["pass"] = all(rep["categories"].values()) and rep["duration"]["ok"]
    json.dump(rep, open(out_json, "w"), indent=1)
    print(json.dumps({"pass": rep["pass"], "categories": rep["categories"], "bad_chunks": rep["bad_chunks"]}))
    return 0 if rep["pass"] else 2


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--props", required=True)
    ap.add_argument("--chunks", required=True)
    ap.add_argument("--srt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--assemble-report")
    ap.add_argument("--thumbs-report")
    a = ap.parse_args(argv)
    return run(a.video, a.props, a.chunks, a.srt, a.out, a.assemble_report, a.thumbs_report)


if __name__ == "__main__":
    sys.exit(main())

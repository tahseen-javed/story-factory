"""Reference analysis (runs ONLY on GitHub, on the decrypted reference video). Measurement only: no frames, audio or text of the
reference are published. Outputs counts, timings and statistics (docs/REFERENCE_ANALYSIS.md, config/reference_metrics.json)
plus a contact sheet that the workflow encrypts with age."""
from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import subprocess
import sys

import numpy as np


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def decode_gray(path, fps, w, h):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale={w}:{h}:flags=area,format=gray", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    data = p.stdout.read()
    p.wait()
    n = len(data) // (w * h)
    return np.frombuffer(data[: n * w * h], dtype="uint8").reshape(n, h, w)


def main(argv=None):
    import cv2

    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--md", required=True)
    ap.add_argument("--json", required=True)
    ap.add_argument("--work", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.work, exist_ok=True)
    info = json.loads(sh(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", a.video]).stdout)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    dur = float(info["format"]["duration"])
    num, den = v["r_frame_rate"].split("/")
    fps = float(num) / float(den)
    m = {"duration_s": round(dur, 2), "width": v["width"], "height": v["height"], "fps": round(fps, 2), "video_kbps": int(v.get("bit_rate", 0)) // 1000,
         "total_kbps": int(info["format"].get("bit_rate", 0)) // 1000}

    # ---- cuts / shots ----
    r = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", a.video, "-an", "-vf", "select='gt(scene,0.30)',showinfo", "-f", "null", "-"])
    cuts = [0.0] + [float(x) for x in re.findall(r"pts_time:([\d.]+)", r.stderr)] + [dur]
    shots = [(cuts[i], cuts[i + 1]) for i in range(len(cuts) - 1) if cuts[i + 1] - cuts[i] > 0.3]
    sd = [b - a_ for a_, b in shots]
    m["shots"] = len(shots)
    m["median_shot_s"] = round(statistics.median(sd), 2)
    m["first_minute_median_s"] = round(statistics.median([b - a_ for a_, b in shots if a_ < 60] or [0]), 2)
    m["last_minute_median_s"] = round(statistics.median([b - a_ for a_, b in shots if a_ > dur - 90] or [0]), 2)
    m["max_shot_s"] = round(max(sd), 2)

    # ---- motion per shot (optical flow) + zoom estimate ----
    fps_a, w, h = 10, 160, 90
    g = decode_gray(a.video, fps_a, w, h)
    moving, zooms, pans = 0, [], []
    yy, xx = np.mgrid[0:h, 0:w]
    for s0, s1 in shots:
        i0, i1 = int((s0 + 0.15 * (s1 - s0)) * fps_a), int((s0 + 0.85 * (s1 - s0)) * fps_a)
        i0, i1 = min(i0, len(g) - 2), min(max(i1, i0 + 1), len(g) - 1)
        if i1 <= i0 or (s1 - s0) < 0.8:
            continue
        flow = cv2.calcOpticalFlowFarneback(g[i0], g[i1], None, 0.5, 2, 15, 2, 5, 1.1, 0)
        mag = float(np.mean(np.linalg.norm(flow, axis=2)))
        du, dv = flow[..., 0], flow[..., 1]
        zoom = float(np.mean(du * (xx - w / 2) + dv * (yy - h / 2)) / np.mean((xx - w / 2) ** 2 + (yy - h / 2) ** 2))  # relative scale change over the interval
        mv = mag > 0.25 or abs(zoom) > 0.01
        moving += int(mv)
        if abs(zoom) > 0.01:
            zooms.append(zoom * 100 / max(0.1, (s1 - s0) * 0.7))  # percent per second
        pans.append(float(np.mean(np.abs(du))))
    m["motion_share"] = round(moving / max(1, len(shots)), 3)
    m["zoom_pct_per_s_median"] = round(statistics.median([abs(z) for z in zooms]), 2) if zooms else 0
    m["push_in_share"] = round(sum(1 for z in zooms if z > 0) / max(1, len(zooms)), 2)

    # ---- colour palette per fifth ----
    pal = []
    cap = cv2.VideoCapture(a.video)
    for k in range(5):
        cap.set(cv2.CAP_PROP_POS_MSEC, (dur * (k + 0.5) / 5) * 1000)
        ok, fr = cap.read()
        if not ok:
            continue
        small = cv2.resize(fr, (96, 54)).reshape(-1, 3).astype("float32")
        _, _, centers = cv2.kmeans(small, 4, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 12, 1.0), 2, cv2.KMEANS_PP_CENTERS)
        hsv = cv2.cvtColor(cv2.resize(fr, (96, 54)), cv2.COLOR_BGR2HSV)
        pal.append({"section": k + 1, "palette_hex": ["#%02x%02x%02x" % (int(c[2]), int(c[1]), int(c[0])) for c in centers], "mean_sat": round(float(hsv[..., 1].mean()) / 255, 2), "mean_val": round(float(hsv[..., 2].mean()) / 255, 2)})
    m["palette"] = pal

    # ---- loudness ----
    r = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", a.video, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"])
    def last(pat):
        x = re.findall(pat, r.stderr)
        return float(x[-1]) if x else None
    m["lufs"], m["lra"], m["true_peak"] = last(r"I:\s+(-?[\d.]+) LUFS"), last(r"LRA:\s+(-?[\d.]+) LU"), last(r"Peak:\s+(-?[\d.]+) dBFS")

    # ---- speech: ASR on silence-split segments (words, wpm, pauses, CTA) ----
    wav = os.path.join(a.work, "ref16k.wav")
    sh(["ffmpeg", "-y", "-v", "error", "-i", a.video, "-vn", "-ac", "1", "-ar", "16000", wav])
    sd_out = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", wav, "-af", "silencedetect=noise=-38dB:d=0.18", "-f", "null", "-"]).stderr
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", sd_out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", sd_out)]
    pauses = [e - s for s, e in zip(starts, ends) if e > s]
    m["median_pause_s"] = round(statistics.median(pauses), 2) if pauses else None
    seg_bounds, prev = [], 0.0
    for s, e in zip(starts, ends):
        if s > prev + 0.3:
            seg_bounds.append((prev, s))
        prev = e
    if dur > prev + 0.3:
        seg_bounds.append((prev, dur))
    merged, cur = [], None
    for s, e in seg_bounds:  # merge into windows of <= 25 s for the recogniser
        if cur and e - cur[0] <= 25:
            cur = (cur[0], e)
        else:
            if cur:
                merged.append(cur)
            cur = (s, e)
    if cur:
        merged.append(cur)
    words, cta_t, num_first_min = 0, None, 0
    try:
        import soundfile as sf
        from .asr_check import Asr

        asr = Asr(cache_dir=os.path.join(a.work, ".asr"))
        data, sr = sf.read(wav, dtype="float32")
        for s, e in merged:
            seg = data[int(s * sr): int(e * sr)]
            tmp = os.path.join(a.work, "seg.wav")
            sf.write(tmp, seg, sr, subtype="PCM_16")
            txt = asr.transcribe(tmp).lower()
            n = len(re.findall(r"[a-z0-9']+", txt))
            words += n
            if cta_t is None and "subscribe" in txt:
                cta_t = round(s, 1)
            if s < 60:
                num_first_min += len(re.findall(r"\d+|\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|thirty|hundred)\b", txt))
        m["asr_engine"] = asr.name
    except Exception as ex:  # noqa: BLE001
        m["asr_error"] = repr(ex)[:120]
    speech_s = sum(e - s for s, e in merged)
    m["words"] = words
    m["wpm"] = round(words / (dur / 60.0), 1) if words else None
    m["wpm_speaking"] = round(words / (speech_s / 60.0), 1) if words and speech_s else None
    m["cta_at_s"] = cta_t
    m["has_cta"] = cta_t is not None
    m["numbers_in_first_minute"] = num_first_min

    # ---- on-screen text frequency (OCR every 2 s) ----
    try:
        from rapidocr_onnxruntime import RapidOCR

        ocr = RapidOCR()
        cap = cv2.VideoCapture(a.video)
        texty, total = 0, 0
        for t in np.arange(1.0, dur - 1, 2.0):
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
            ok, fr = cap.read()
            if not ok:
                continue
            res, _ = ocr(cv2.resize(fr, (960, 540)))
            total += 1
            if res and any(len(x[1].strip()) >= 3 and float(x[2]) > 0.6 for x in res):
                texty += 1
        m["text_frame_share"] = round(texty / max(1, total), 2)
    except Exception as ex:  # noqa: BLE001
        m["ocr_error"] = repr(ex)[:120]

    # ---- contact sheet (6 frames) for the encrypted artifact ----
    sh(["ffmpeg", "-y", "-v", "error", "-i", a.video, "-vf", f"fps=6/{dur},scale=640:-1,tile=3x2", "-frames:v", "1", os.path.join(a.work, "contact.jpg")])

    json.dump(m, open(a.json, "w"), indent=1)
    L = ["# REFERENCE_ANALYSIS (measurements only; no frames, audio or text of the reference are published)", "",
         f"Measured by factory/analyze_reference.py on GitHub. Resolution {m['width']}x{m['height']} @ {m['fps']} fps, {m['duration_s']} s, video {m['video_kbps']} kbps.", "",
         "| Metric | Value |", "|---|---|"]
    for k in ("shots", "median_shot_s", "first_minute_median_s", "last_minute_median_s", "max_shot_s", "motion_share", "zoom_pct_per_s_median", "push_in_share",
              "words", "wpm", "wpm_speaking", "median_pause_s", "has_cta", "cta_at_s", "numbers_in_first_minute", "text_frame_share", "lufs", "lra", "true_peak"):
        L.append(f"| {k} | {m.get(k)} |")
    L += ["", "## Palette per fifth of the runtime"] + [f"- {p['section']}: {' '.join(p['palette_hex'])} (sat {p['mean_sat']}, val {p['mean_val']})" for p in pal]
    L += ["", "Owner cross-check numbers: 9:51, 107 shots (median 4.1 s), about 90% shots with camera motion, about 1,720 words at about 175 wpm, -14.6 LUFS, LRA 3.5 LU, no subscribe CTA."]
    open(a.md, "w", encoding="utf-8").write("\n".join(L[:200]) + "\n")
    print(json.dumps({k: m.get(k) for k in ("shots", "median_shot_s", "motion_share", "wpm", "lufs", "lra", "has_cta")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

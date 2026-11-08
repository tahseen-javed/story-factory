"""Thumbnails: >= 8 candidates from the same puppet rig (Remotion ThumbSet), auto-scored, best 2 delivered as different concepts.

Concept A = emotion close-up (face >= 35% of frame height). Concept B = situation/object + big number hook (character smaller).
Score: OCR legibility at 168x94, contrast, warm/cool separation, saliency focus, clutter, clear bottom-right corner.
"""
from __future__ import annotations

import argparse
import difflib
import io
import json
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image

PREF_VARIANTS = ["blackout", "alarm", "night", "dusk", "day"]


def pick_bg(plan, bg_dir, prefer_banner=True, avoid=None):
    have = {f[:-4] for f in os.listdir(bg_dir) if f.endswith(".jpg") and f.count(".") == 2} if bg_dir and os.path.isdir(bg_dir) else set()
    cands = []
    for sh in plan["shots"]:
        key = f"{sh['location']}.{sh['variant']}"
        score = 0
        if prefer_banner and sh.get("banner"):
            score += 5
        score += (len(PREF_VARIANTS) - PREF_VARIANTS.index(sh["variant"])) if sh["variant"] in PREF_VARIANTS else 0
        if key in have:
            score += 2
        if avoid and sh["location"] == avoid:
            score -= 6
        cands.append((score, sh["location"], sh["variant"], key in have))
    cands.sort(reverse=True)
    _, loc, var, ok = cands[0]
    return loc, var, (f"bg/{loc}.{var}.jpg" if ok else None)


def hook_words(plan):
    title = re.findall(r"[A-Za-z0-9]+", plan["short_title"] or plan["title"])
    pair = " ".join(w.upper() for w in title[:2])
    last = title[-1].upper() if title else "STORY"
    q = next((s["text"] for s in plan["sentences"][:40] if s["text"].strip().endswith("?")), "")
    ql = q.lower()
    qhook = "WHY ME?" if re.search(r"\bwhy\b", ql) else "WHAT NOW?" if re.search(r"\bwhat\b", ql) else "WHO KNEW?" if re.search(r"\bwho\b", ql) else "NO WARNING?"
    timers = [a for sh in plan["shots"] if sh.get("overlay") and sh["overlay"]["name"] == "timer" for a in [sh["overlay"]["args"][0]]]
    num = None
    if timers:
        p = [int(x) for x in str(timers[0]).split(":") if x.isdigit()]
        if len(p) == 3 and p[0]:
            num = f"{p[0]} HOURS"
        elif len(p) >= 2 and p[-2] or (len(p) == 3 and p[1]):
            num = f"{p[-2]} MINUTES"
    return {"q": qhook, "pair": pair, "last": last, "num": num or "COUNTDOWN"}


def threat_for(plan):
    t = (plan["title"] + " " + " ".join(plan["locations"].values())).lower()
    if re.search(r"solar|sun|storm|flare", t):
        return "sun"
    if re.search(r"alarm|alert|siren", t):
        return "alert"
    if re.search(r"door|knock|haunt", t):
        return "door"
    return "clock"


def candidates(plan, bg_dir, accent):
    hero_id = next(iter(plan["characters"]))
    params = plan["characters"][hero_id]["params"]
    hw = hook_words(plan)
    loc, var, bg = pick_bg(plan, bg_dir)
    loc2, var2, bg2 = pick_bg(plan, bg_dir, prefer_banner=False, avoid=loc)
    th = threat_for(plan)
    timer = next((sh["overlay"] for sh in plan["shots"] if sh.get("overlay") and sh["overlay"]["name"] == "timer"), None)
    alert = next((sh["overlay"] for sh in plan["shots"] if sh.get("overlay") and sh["overlay"]["name"] == "phone_alert"), None)
    obj_a = {"name": "timer", "args": timer["args"]} if timer else None
    obj_b = {"name": "phone_alert", "args": alert["args"]} if alert else obj_a
    mk = lambda **k: {"hero": {"params": params, "pose": "stand", "expr": k.pop("expr")}, "other": None, "accent": accent, "threat": th, **k}
    out = [
        mk(concept="A", bg=bg, location=loc, variant=var, text=hw["q"], layout="left", expr="shocked", object=None),
        mk(concept="A", bg=bg, location=loc, variant=var, text=hw["pair"], layout="right", expr="scared", object=None),
        mk(concept="A", bg=bg2, location=loc2, variant=var2, text=hw["num"], layout="left", expr="scared", object=None),
        mk(concept="A", bg=bg, location=loc, variant=var, text=hw["last"] + "!", layout="right", expr="shocked", object=None),
        mk(concept="B", bg=bg2, location=loc2, variant=var2, text=hw["num"], layout="left", expr="worried", object=obj_a),
        mk(concept="B", bg=bg, location=loc, variant=var, text=hw["last"], layout="right", expr="scared", object=obj_b),
        mk(concept="B", bg=bg2, location=loc2, variant=var2, text=hw["q"], layout="right", expr="worried", object=obj_b),
        mk(concept="B", bg=bg, location=loc, variant=var, text=hw["pair"], layout="left", expr="scared", object=obj_a),
    ]
    for c in out:
        c["text"] = " ".join(c["text"].split()[:4])
    return out


# ------------------------------------------------------------------ scoring
def _ocr():
    try:
        from rapidocr_onnxruntime import RapidOCR  # type: ignore

        return RapidOCR()
    except Exception:  # noqa: BLE001
        return None


def spectral_saliency(gray):
    g = gray.astype("float32") / 255.0
    f = np.fft.fft2(g)
    amp, ph = np.abs(f), np.angle(f)
    log = np.log(amp + 1e-6)
    import cv2

    sr = log - cv2.blur(log, (3, 3))
    s = np.abs(np.fft.ifft2(np.exp(sr + 1j * ph))) ** 2
    s = cv2.GaussianBlur(s, (0, 0), 3)
    return s / (s.max() + 1e-9)


def score_image(img: Image.Image, expect_text: str, concept: str, ocr) -> dict:
    import cv2

    rgb = np.asarray(img.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    small = img.convert("RGB").resize((168, 94), Image.LANCZOS)
    s = {}
    # legibility at 168x94
    if ocr is not None:
        try:
            up = np.asarray(small.resize((504, 282), Image.BICUBIC))
            res, _ = ocr(up)
            got = " ".join(t for _, t, c in (res or []) if float(c) > 0.3).upper()
            exp = re.sub(r"[^A-Z0-9 ]", "", expect_text.upper())
            got = re.sub(r"[^A-Z0-9 ]", "", got)
            s["ocr"] = difflib.SequenceMatcher(None, exp, got).ratio()
        except Exception:  # noqa: BLE001
            s["ocr"] = 0.5
    else:
        s["ocr"] = 0.5
    s["contrast"] = float(min(1.0, np.std(gray / 255.0) / 0.26))
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    hue = hsv[..., 0].astype(float) * 2
    sat = hsv[..., 1] > 60
    warm = float(np.mean(sat & ((hue < 60) | (hue > 330))))
    cool = float(np.mean(sat & (hue > 170) & (hue < 270)))
    s["separation"] = float(min(1.0, min(warm, cool) / 0.12))
    sal = spectral_saliency(cv2.resize(gray, (320, 180)))
    flat = np.sort(sal.ravel())[::-1]
    top = flat[: max(1, len(flat) // 10)].sum() / (flat.sum() + 1e-9)
    s["saliency"] = float(min(1.0, top / 0.5))
    edges = cv2.Canny(cv2.resize(gray, (320, 180)), 60, 140)
    dens = float(np.mean(edges > 0))
    s["clutter"] = float(max(0.0, 1.0 - max(0.0, dens - 0.06) / 0.12))
    br = edges[int(180 * 0.84):, int(320 * 0.80):]
    s["corner"] = float(max(0.0, 1.0 - float(np.mean(br > 0)) / 0.08))
    s["face_or_object"] = 1.0
    w = dict(ocr=0.25, contrast=0.14, separation=0.14, saliency=0.14, clutter=0.10, corner=0.10, face_or_object=0.13)
    s["total"] = float(sum(s[k] * v for k, v in w.items()))
    return s


def export_jpg(img: Image.Image, path: str, max_bytes: int):
    img = img.convert("RGB").resize((1280, 720), Image.LANCZOS)
    for q in (95, 92, 90, 86, 82, 78):
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=q, subsampling=0 if q >= 90 else 2, optimize=True)
        if buf.tell() <= max_bytes:
            break
    open(path, "wb").write(buf.getvalue())
    return buf.tell()


def render(specs, video_dir, out_dir, tag):
    props = os.path.join(out_dir, f"thumbs_{tag}.json")
    json.dump({"thumbs": specs}, open(props, "w"))
    seq = os.path.join(out_dir, f"seq_{tag}")
    subprocess.run(["npx", "remotion", "render", "src/index.ts", "ThumbSet", os.path.abspath(seq), "--sequence", "--image-format=png",
                    f"--props={os.path.abspath(props)}", "--log=warn", "--concurrency=2"], cwd=video_dir, check=True)
    files = sorted(os.listdir(seq), key=lambda f: int(re.findall(r"\d+", f)[0]))
    return [os.path.join(seq, f) for f in files]


def run(plan_path, bg_dir, video_dir, out_dir, cfg_path=None):
    from .validate import load_cfg

    cfg = load_cfg()
    plan = json.load(open(plan_path, encoding="utf-8"))
    os.makedirs(out_dir, exist_ok=True)
    accent = plan["style"].get("accent", "amber")
    ocr = _ocr()
    thr = 0.62
    best = {}
    pool = []
    all_scores = []
    rounds = 0
    specs = candidates(plan, bg_dir, accent)
    while rounds < 2:
        files = render(specs, video_dir, out_dir, f"r{rounds}")
        for sp, f in zip(specs, files):
            img = Image.open(f)
            sc = score_image(img, sp["text"], sp["concept"], ocr)
            all_scores.append({"concept": sp["concept"], "text": sp["text"], "layout": sp["layout"], "expr": sp["hero"]["expr"], "round": rounds, **{k: round(v, 3) for k, v in sc.items()}})
            pool.append((sc["total"], f, sp))
        best = {}
        a_best = max((x for x in pool if x[2]["concept"] == "A"), key=lambda x: x[0], default=None)
        if a_best:
            best["A"] = a_best
            b_pool = [x for x in pool if x[2]["concept"] == "B" and x[2]["text"] != a_best[2]["text"]] or [x for x in pool if x[2]["concept"] == "B"]
            if b_pool:
                best["B"] = max(b_pool, key=lambda x: x[0])
        if all(best.get(c, (0,))[0] >= thr for c in ("A", "B")):
            break
        rounds += 1  # regenerate with mutated layout/accent
        accent = {"amber": "coral", "coral": "teal", "teal": "amber"}.get(accent, "amber")
        specs = [dict(s, accent=accent, layout=("right" if s["layout"] == "left" else "left")) for s in specs]
    mx = int(cfg["thumbnails"]["max_bytes"])
    sizes = []
    for n, c in ((1, "A"), (2, "B")):
        sizes.append(export_jpg(Image.open(best[c][1]), os.path.join(out_dir, f"thumb{n}.jpg"), mx))
    rep = {"ok": all(best[c][0] >= thr for c in ("A", "B")), "threshold": thr, "chosen": {c: {"score": round(best[c][0], 3), "text": best[c][2]["text"]} for c in best},
           "bytes": sizes, "candidates": len(all_scores), "scores": all_scores, "ocr_engine": "rapidocr" if ocr else "none"}
    json.dump(rep, open(os.path.join(out_dir, "thumbs_report.json"), "w"), indent=1)
    print(json.dumps({k: rep[k] for k in ("ok", "chosen", "bytes", "candidates")}))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--bg", default=None)
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    return run(a.plan, a.bg, a.video, a.out)


if __name__ == "__main__":
    sys.exit(main())

"""Video Doctor Phase 2, stage 3: background blotch, banding and style-consistency check on the generated backgrounds (bg/*.jpg), with automatic soft-grade repair.

V3-BLOTCH   large flat colour patches that do not belong to the picture (chroma outlier blobs on a smooth base)
V3-BANDING  visible staircase in smooth gradients (long plateaus one level apart)
V3-STYLE    an image whose edge density / noise / saturation leaves the family of the other backgrounds of the video

Repair (no GPU, no model): banding -> triangular dither + 3x3 smooth of plateaus; blotch -> chroma pulled 60 % toward a heavily blurred version (soft grade). The repaired jpg replaces the
original in the assembled folder before rendering, then the check runs again (max 2 passes). numpy + scipy + Pillow only.
"""
from __future__ import annotations

import glob
import json
import os
import sys
import time

import numpy as np
from scipy import ndimage as ndi


def load_rgb(path: str, max_w: int = 960) -> np.ndarray:
    from PIL import Image

    im = Image.open(path).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, int(im.height * max_w / im.width)), Image.LANCZOS)
    return np.asarray(im).astype(np.float32)


def ycc(rgb: np.ndarray):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    y = 0.299 * r + 0.587 * g + 0.114 * b
    return y, (b - y) * 0.564, (r - y) * 0.713


def metrics(rgb: np.ndarray) -> dict:
    y, cb, cr = ycc(rgb)
    h, w = y.shape
    gx, gy = ndi.sobel(y, axis=1), ndi.sobel(y, axis=0)
    grad = np.hypot(gx, gy)
    smooth = ndi.uniform_filter(grad, 9) < 6.0
    # banding: horizontal and vertical plateaus (>= 18 px of identical value) inside smooth areas, with a one-level step at the end
    yq = np.round(y).astype(np.int16)
    band = 0
    for arr in (yq, yq.T):
        d = np.diff(arr, axis=1)
        flat = (d == 0)
        steps = (np.abs(d) == 1)
        # run lengths of flat segments terminated by a one-level step
        run = np.zeros_like(flat, dtype=np.int16)
        run[:, 0] = flat[:, 0]
        for i in range(1, flat.shape[1]):
            run[:, i] = np.where(flat[:, i], run[:, i - 1] + 1, 0)
        ends = steps[:, 1:] & (run[:, :-1] >= 18)
        sm = (smooth if arr is yq else smooth.T)[:, 1:-1]
        band += int((ends & sm).sum())
    n_smooth = max(1, int(smooth.sum()))
    banding = band / (n_smooth / 18.0)
    # blotch: chroma outlier blobs. Block-average chroma, compare with a heavily blurred version of the same chroma
    bs = 12
    hb, wb = h // bs, w // bs
    cbb = cb[: hb * bs, : wb * bs].reshape(hb, bs, wb, bs).mean(axis=(1, 3))
    crb = cr[: hb * bs, : wb * bs].reshape(hb, bs, wb, bs).mean(axis=(1, 3))
    tex = ndi.uniform_filter(grad, bs)[: hb * bs : bs, : wb * bs : bs][:hb, :wb]
    dev = np.hypot(cbb - ndi.gaussian_filter(cbb, 8), crb - ndi.gaussian_filter(crb, 8))
    out = (dev > 14.0) & (tex < 9.0)
    lab, n = ndi.label(out)
    big = 0
    if n:
        sizes = ndi.sum(out, lab, range(1, n + 1))
        big = int(sum(s for s in sizes if s >= 14))
    blotch = big / float(hb * wb)
    sat = float(np.mean(np.hypot(cb, cr)))
    return {"banding": round(float(banding), 4), "blotch": round(float(blotch), 4), "edge_density": round(float((grad > 40).mean()), 4), "noise": round(float(np.std(y - ndi.gaussian_filter(y, 1.2))), 3),
            "saturation": round(sat, 2), "luma": round(float(y.mean()), 1)}


def finding(th, code, key, name, value, thr, msg):
    return {"code": code, "severity": th["severity"].get(key, "MINOR"), "t0": 0, "t1": 0, "value": round(float(value), 4), "threshold": thr, "msg": msg, "image": name}


def check_images(items: dict, th: dict) -> tuple:
    """items: {name: metrics}. Returns (findings, summary)."""
    L = th["look"]
    f = []
    for n, m in items.items():
        if m["blotch"] > L["blotch_max"]:
            f.append(finding(th, "V3-BLOTCH", "blotch", n, m["blotch"], L["blotch_max"], "blotchy colour patches in the background"))
        if m["banding"] > L["banding_max"]:
            f.append(finding(th, "V3-BANDING", "banding", n, m["banding"], L["banding_max"], "banding in smooth gradients"))
    if len(items) >= 3:
        med = {k: float(np.median([m[k] for m in items.values()])) for k in ("edge_density", "noise", "saturation")}
        for n, m in items.items():
            if m["edge_density"] < med["edge_density"] * L["style_edge_ratio_min"] or m["noise"] > max(0.5, med["noise"]) * L["style_noise_ratio_max"] or abs(m["saturation"] - med["saturation"]) > L["style_saturation_delta"]:
                f.append(finding(th, "V3-STYLE", "style", n, m["edge_density"], med["edge_density"], "image is outside the style family of the other backgrounds"))
    return f, {"images": len(items)}


def repair(path: str, m: dict, th: dict) -> str:
    """Soft-grade repair, returns what was done."""
    from PIL import Image

    L = th["look"]
    im = Image.open(path).convert("RGB")
    rgb = np.asarray(im).astype(np.float32)
    done = []
    if m["banding"] > L["banding_max"]:
        rng = np.random.default_rng(7)
        noise = (rng.random(rgb.shape[:2]) + rng.random(rgb.shape[:2]) - 1.0) * 1.6
        rgb = rgb + noise[..., None]
        y, _, _ = ycc(rgb)
        grad = np.hypot(ndi.sobel(y, axis=1), ndi.sobel(y, axis=0))
        smooth = (ndi.uniform_filter(grad, 9) < 6.0)[..., None]
        soft = np.stack([ndi.uniform_filter(rgb[..., c], 3) for c in range(3)], axis=-1)
        rgb = np.where(smooth, soft, rgb)
        done.append("dither+smooth")
    if m["blotch"] > L["blotch_max"]:
        y, cb, cr = ycc(rgb)
        cb2, cr2 = ndi.gaussian_filter(cb, 24), ndi.gaussian_filter(cr, 24)
        k = 0.6
        cbn, crn = cb * (1 - k) + cb2 * k, cr * (1 - k) + cr2 * k
        r = y + crn / 0.713
        b = y + cbn / 0.564
        g = (y - 0.299 * r - 0.114 * b) / 0.587
        rgb = np.stack([r, g, b], axis=-1)
        done.append("chroma soft-grade")
    Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).save(path, quality=93, subsampling=0)
    return "+".join(done) or "none"


def run(asm: str, th: dict) -> dict:
    t0 = time.time()
    rep = {"stage": "look", "status": "OK", "findings": [], "metrics": {}, "fixes": []}
    try:
        files = sorted(f for f in glob.glob(os.path.join(asm, "bg", "*.jpg")) if f.count(".") >= 2 and not f.endswith(".far.jpg"))
        files = [f for f in files if not os.path.basename(f).endswith((".far.jpg", ".mid.jpg", ".near.jpg"))]
        items = {os.path.basename(f): metrics(load_rgb(f)) for f in files}
        f, s = check_images(items, th)
        for _pass in range(2):
            fixable = {x["image"] for x in f if x["code"] in ("V3-BLOTCH", "V3-BANDING")}
            if not fixable:
                break
            for name in sorted(fixable):
                rep["fixes"].append(f"{name}: {repair(os.path.join(asm, 'bg', name), items[name], th)}")
                items[name] = metrics(load_rgb(os.path.join(asm, "bg", name)))
            f, s = check_images(items, th)
        rep.update({"findings": f, "metrics": {"images": len(items), "per_image": items, **s}})
    except Exception as e:  # noqa: BLE001
        rep.update({"status": "SKIPPED", "error": f"{e.__class__.__name__}: {str(e)[:200]}"})
    rep["seconds"] = round(time.time() - t0, 1)
    return rep


def main(argv=None) -> int:
    asm = (argv or sys.argv[1:])[0]
    from .run import load_th

    rep = run(asm, load_th())
    os.makedirs(os.path.join(asm, "doctor"), exist_ok=True)
    json.dump(rep, open(os.path.join(asm, "doctor", "LOOK_REPORT.json"), "w", encoding="utf-8"), indent=1)
    if rep["fixes"]:
        open(os.path.join(asm, "doctor", "FIX_LOG.md"), "a", encoding="utf-8").write("## Stage 3 look\n" + "\n".join(f"- {x}" for x in rep["fixes"]) + "\n")
    print(f"DOCTOR look: {rep['status']} {rep.get('error', '')}; images {rep['metrics'].get('images')}; findings {[x['code'] + ':' + x['image'] for x in rep['findings']]}; fixes {len(rep['fixes'])}; {rep['seconds']}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())

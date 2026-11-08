"""Background stage (GitHub runner, CPU): SDXL-Lightning 4-step -> painted-look post-process -> 3 depth layers.

Memory plan (16 GB runner): text encoders are loaded first, every prompt of the shard is encoded, then they are freed
before the fp32 UNet (10 GB) is loaded. Variants (day/night/alarm/dusk/blackout) are img2img of the location's base image.
Failed checks (garbage text via OCR, near-duplicate via phash) trigger a regeneration with a new seed (max 2).
If anything fails for a key, assemble falls back to the procedural SVG backdrop in video/src/scenes/Backdrop.tsx.
"""
from __future__ import annotations

import argparse
import gc
import json
import math
import os
import sys
import time

from . import miniyaml

BASE = "stabilityai/stable-diffusion-xl-base-1.0"
LIGHT = ("ByteDance/SDXL-Lightning", "sdxl_lightning_4step_unet.safetensors")


def _cfg():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cfg = miniyaml.load_file(os.path.join(root, "config", "factory.yaml"))
    sp = os.path.join(root, "config", "style.yaml")
    if os.path.exists(sp):
        cfg["style"] = miniyaml.load_file(sp)
    return cfg


def _palette_lab(cfg):
    """Style-bible palette (hues + accents) as OpenCV 8-bit LAB rows."""
    import cv2
    import numpy as np

    hexes = list(cfg["style"]["palette"]["hues"]) + list(cfg["style"]["palette"]["accents"])
    rgb = np.array([[[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in hexes]], dtype="uint8")
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)[0].astype("float32")


def palette_distance(img, cfg) -> float:
    """Mean chroma (a,b) distance of the image pixels to the nearest bible colour (lower = closer to the style bible)."""
    import cv2
    import numpy as np

    small = np.asarray(img.convert("RGB").resize((192, 108)))
    ab = cv2.cvtColor(small, cv2.COLOR_RGB2LAB).reshape(-1, 3)[:, 1:].astype("float32")
    pal = _palette_lab(cfg)[:, 1:]
    return float(np.sqrt(((ab[:, None, :] - pal[None, :, :]) ** 2).sum(-1)).min(axis=1).mean())


def palette_snap(img, cfg):
    """Flatten (mean shift), quantise to k colours and pull each colour's chroma toward the nearest bible hue (lightness kept)."""
    import cv2
    import numpy as np
    from PIL import Image

    look = cfg["style"]["look"]
    a = np.asarray(img.convert("RGB"))
    sm = cv2.pyrMeanShiftFiltering(a, 6, 18)
    lab = cv2.cvtColor(sm, cv2.COLOR_RGB2LAB).astype("float32")
    flat = lab.reshape(-1, 3)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 12, 1.0)
    _, _, centers = cv2.kmeans(np.ascontiguousarray(flat[::13]), int(look["posterize_colors"]), None, crit, 2, cv2.KMEANS_PP_CENTERS)
    pal = _palette_lab(cfg)[:, 1:]
    near = pal[((centers[:, None, 1:] - pal[None, :, :]) ** 2).sum(-1).argmin(1)]
    pull = float(look["palette_pull"])
    centers[:, 1:] = centers[:, 1:] * (1 - pull) + near * pull
    idx = np.empty(len(flat), dtype="int32")
    for i in range(0, len(flat), 250000):
        idx[i:i + 250000] = ((flat[i:i + 250000, None, :] - centers[None, :, :]) ** 2).sum(-1).argmin(1)
    out = cv2.cvtColor(np.clip(centers[idx], 0, 255).astype("uint8").reshape(lab.shape), cv2.COLOR_LAB2RGB)
    return Image.fromarray(out)


def encode_prompts(prompts: dict):
    """prompts: key -> text. Returns key -> (prompt_embeds, pooled) as CPU tensors; frees the text encoders afterwards."""
    import torch
    from diffusers import StableDiffusionXLPipeline

    from diffusers import UNet2DConditionModel

    with torch.device("meta"):  # config-only UNet stub: the pipeline needs unet.config, not its weights
        stub = UNet2DConditionModel.from_config(BASE, subfolder="unet")
    pipe = StableDiffusionXLPipeline.from_pretrained(BASE, unet=stub, torch_dtype=torch.float32, variant="fp16", use_safetensors=True)
    out = {}
    with torch.no_grad():
        for k, p in prompts.items():
            pe, _, pooled, _ = pipe.encode_prompt(p, device="cpu", num_images_per_prompt=1, do_classifier_free_guidance=False)
            out[k] = (pe.clone(), pooled.clone())
    del pipe
    gc.collect()
    return out


def load_unet_pipe():
    import torch
    from diffusers import AutoencoderKL, EulerDiscreteScheduler, StableDiffusionXLPipeline, UNet2DConditionModel
    from huggingface_hub import hf_hub_download
    from safetensors import safe_open

    unet = UNet2DConditionModel.from_config(BASE, subfolder="unet").to(torch.float32)
    path = hf_hub_download(*LIGHT)
    params = dict(unet.named_parameters())
    bufs = dict(unet.named_buffers())
    with safe_open(path, framework="pt", device="cpu") as f:  # tensor-by-tensor: never holds two copies
        for name in f.keys():
            t = f.get_tensor(name)
            (params[name] if name in params else bufs[name]).data.copy_(t)
    vae = AutoencoderKL.from_pretrained(BASE, subfolder="vae", torch_dtype=torch.float32)
    pipe = StableDiffusionXLPipeline.from_pretrained(
        BASE, unet=unet, vae=vae, text_encoder=None, text_encoder_2=None, tokenizer=None, tokenizer_2=None,
        torch_dtype=torch.float32, variant="fp16", use_safetensors=True,
    )
    pipe.scheduler = EulerDiscreteScheduler.from_config(pipe.scheduler.config, timestep_spacing="trailing")
    return pipe


def painted_post(img, variant: str, scale: float, grain_seed: int):
    """Upscale + ink-line enhancement + muted painted grade + paper grain. Returns an RGB PIL image."""
    import numpy as np
    from PIL import Image, ImageFilter

    w, h = img.size
    try:
        _c = _cfg()
        if float(_c["style"]["look"].get("palette_pull", 0) or 0) > 0:
            img = palette_snap(img, _c)
    except Exception as e:  # noqa: BLE001
        print(f"[images] palette snap skipped: {e!r}")
    big = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    big = big.filter(ImageFilter.UnsharpMask(radius=2.2, percent=90, threshold=3))
    a = np.asarray(big).astype("float32") / 255.0
    try:
        import cv2  # type: ignore

        g = cv2.cvtColor((a * 255).astype("uint8"), cv2.COLOR_RGB2GRAY)
        g = cv2.GaussianBlur(g, (0, 0), 1.6)
        edges = cv2.Canny(g, 40, 110).astype("float32") / 255.0
        edges = cv2.GaussianBlur(cv2.dilate(edges, np.ones((2, 2), "uint8")), (0, 0), 1.1)
        a = a * (1.0 - 0.38 * edges[..., None])
    except Exception as e:  # noqa: BLE001
        print(f"[images] ink pass skipped: {e!r}")
    # muted painted grade: lift blacks a little, soften saturation, gentle S-curve
    lum = a.mean(axis=2, keepdims=True)
    a = lum + (a - lum) * 0.9
    a = 0.04 + a * 0.94
    a = np.clip(a, 0, 1)
    a = a + 0.10 * (a - 0.5) * (1 - np.abs(a - 0.5) * 2)
    # paper grain (fixed per image, fine)
    rng = np.random.default_rng(grain_seed)
    n = rng.normal(0, 0.012, size=(a.shape[0] // 3 + 1, a.shape[1] // 3 + 1)).astype("float32")
    n = np.kron(n, np.ones((3, 3), "float32"))[: a.shape[0], : a.shape[1]]
    a = np.clip(a + n[..., None], 0, 1)
    return Image.fromarray((a * 255).astype("uint8"))


def depth_layers(img, out_prefix: str):
    """Split a background into far/mid/near using Depth-Anything-V2-Small. Writes far.jpg, mid.webp, near.webp."""
    import numpy as np
    from PIL import Image, ImageFilter

    try:
        from transformers import pipeline  # type: ignore
        import cv2  # type: ignore

        dp = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device=-1)
        d = dp(img.resize((518, 294)))["depth"]
        d = np.asarray(d.resize(img.size, Image.BILINEAR)).astype("float32")
        d = (d - d.min()) / max(1e-6, (d.max() - d.min()))  # 1 = near
        near_m = np.clip((d - 0.62) / 0.10, 0, 1)
        mid_m = np.clip((d - 0.34) / 0.10, 0, 1)
        feather = lambda m: np.asarray(Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(10))).astype("float32") / 255.0
        near_m, mid_m = feather(near_m), feather(mid_m)
        mid_m = np.maximum(mid_m, near_m)
        # far plate: inpaint everything that is not far, at low resolution for speed, then blend
        small = cv2.resize(np.asarray(img), (756, 432), interpolation=cv2.INTER_AREA)
        hole = cv2.resize((mid_m > 0.35).astype("uint8") * 255, (756, 432), interpolation=cv2.INTER_NEAREST)
        hole = cv2.dilate(hole, np.ones((9, 9), "uint8"))
        fill = cv2.inpaint(small, hole, 6, cv2.INPAINT_TELEA)
        fill = cv2.resize(fill, img.size, interpolation=cv2.INTER_CUBIC)
        arr = np.asarray(img).astype("float32")
        far = arr * (1 - mid_m[..., None]) + fill.astype("float32") * mid_m[..., None]
        Image.fromarray(np.clip(far, 0, 255).astype("uint8")).save(out_prefix + ".far.jpg", quality=95, subsampling=0)
        for name, m in (("mid", mid_m), ("near", near_m)):
            rgba = np.dstack([arr, (m * 255)[..., None]]).astype("uint8")
            Image.fromarray(rgba, "RGBA").save(f"{out_prefix}.{name}.webp", quality=95, method=4)
        del dp
        return True
    except Exception as e:  # noqa: BLE001
        print(f"[images] depth layers skipped for {out_prefix}: {e!r}")
        return False


def check_image(img, desc: str, seen_hashes: list, ocr, clip) -> list:
    """Return list of failure reasons (empty = pass)."""
    reasons = []
    try:
        if ocr is not None:
            res, _ = ocr(__import__("numpy").asarray(img.resize((960, 540))))
            if res:
                for _, text, conf in res:
                    if float(conf) > 0.7 and len(text.strip()) >= 3 and any(c.isalpha() for c in text):
                        reasons.append(f"garbage_text:{text.strip()[:12]}")
                        break
    except Exception as e:  # noqa: BLE001
        print(f"[images] ocr skipped: {e!r}")
    try:
        import imagehash  # type: ignore

        h = imagehash.phash(img.resize((256, 144)))
        for o in seen_hashes:
            if o is not None and h - o < 6:
                reasons.append("duplicate")
                break
        seen_hashes.append(h)
    except Exception as e:  # noqa: BLE001
        print(f"[images] phash skipped: {e!r}")
    if clip is not None:
        try:
            sim = clip(img, desc)
            if sim < 0.14:
                reasons.append(f"clip_low:{sim:.2f}")
        except Exception as e:  # noqa: BLE001
            print(f"[images] clip skipped: {e!r}")
    return reasons


def make_clip_scorer():
    try:
        import open_clip  # type: ignore
        import torch

        model, _, pre = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k")
        tok = open_clip.get_tokenizer("ViT-B-32")
        model.eval()

        def score(img, text):
            with torch.no_grad():
                i = model.encode_image(pre(img).unsqueeze(0))
                t = model.encode_text(tok([text[:200]]))
                i, t = i / i.norm(dim=-1, keepdim=True), t / t.norm(dim=-1, keepdim=True)
                return float((i @ t.T).item())

        return score
    except Exception as e:  # noqa: BLE001
        print(f"[images] CLIP unavailable: {e!r}")
        return None


def run(plan_path: str, out_dir: str, shard: int, nshards: int):
    import torch
    from PIL import Image

    torch.set_num_threads(os.cpu_count() or 4)
    cfg = _cfg()
    ic = cfg["images"]
    plan = json.load(open(plan_path, encoding="utf-8"))
    groups = [g for i, g in enumerate(plan["image_groups"]) if i % nshards == shard]
    os.makedirs(out_dir, exist_ok=True)
    if not groups:
        print("[images] no groups for this shard")
        return 0
    prompts = {}
    for g in groups:
        prompts[g["base"]["key"]] = g["base"]["prompt"]
        for v in g["variants"]:
            prompts[v["key"]] = v["prompt"]
    t0 = time.time()
    emb = encode_prompts(prompts)
    print(f"[images] encoded {len(emb)} prompts in {time.time()-t0:.0f}s", flush=True)
    pipe = load_unet_pipe()
    from diffusers import StableDiffusionXLImg2ImgPipeline

    i2i = StableDiffusionXLImg2ImgPipeline(**pipe.components)
    print(f"[images] unet ready after {time.time()-t0:.0f}s", flush=True)
    W, H = int(ic["width"]), int(ic["height"])
    raw = {}
    manifest = {}
    seen = []
    ocr = None
    try:
        from rapidocr_onnxruntime import RapidOCR  # type: ignore

        ocr = RapidOCR()
    except Exception as e:  # noqa: BLE001
        print(f"[images] OCR unavailable: {e!r}")
    clip = None  # loaded after the UNet is freed (memory)

    def gen_base(key, seed):
        pe, pooled = emb[key]
        g = torch.Generator().manual_seed(seed)
        im0 = pipe(prompt_embeds=pe, pooled_prompt_embeds=pooled, num_inference_steps=int(ic["steps"]), guidance_scale=0.0, width=W, height=H, generator=g).images[0]
        # v2.1 restyle: one img2img pass (0.35-0.45) so every base shares the bible look; variants then derive from this base
        if float(ic.get("restyle_strength", 0) or 0) <= 0:   # P-011: no restyle pass (it made blotchy backgrounds)
            return im0
        g2 = torch.Generator().manual_seed(seed + 7)
        return i2i(prompt_embeds=pe, pooled_prompt_embeds=pooled, image=im0, strength=float(ic["restyle_strength"]), num_inference_steps=int(ic["steps"]), guidance_scale=0.0, generator=g2).images[0]

    def gen_variant(key, init, seed):
        pe, pooled = emb[key]
        g = torch.Generator().manual_seed(seed)
        return i2i(prompt_embeds=pe, pooled_prompt_embeds=pooled, image=init, strength=float(ic["variant_strength"]), num_inference_steps=int(ic["steps"]), guidance_scale=0.0, generator=g).images[0]

    for grp in groups:
        b = grp["base"]
        for attempt in range(3):
            t1 = time.time()
            img = gen_base(b["key"], b["seed"] + attempt * 101)
            reasons = check_image(img, b["prompt"], seen[:], ocr, None)
            pd_ = palette_distance(img, cfg)
            if attempt == 0 and pd_ > float(cfg["style"]["qa"]["palette_distance_max"]):   # outliers are regenerated once
                reasons = list(reasons) + [f"palette_outlier({pd_:.1f})"]
            print(f"[images] {b['key']} base try {attempt} {time.time()-t1:.0f}s reasons={reasons}", flush=True)
            if not reasons or attempt == 2:
                break
        raw[b["key"]] = img
        manifest[b["key"]] = {"attempt": attempt, "reasons": reasons, "seed": b["seed"] + attempt * 101, "kind": "base", "palette_distance": round(palette_distance(img, cfg), 1)}
        for v in grp["variants"]:
            for attempt in range(2):
                t1 = time.time()
                vi = gen_variant(v["key"], raw[b["key"]], v["seed"] + attempt * 101)
                reasons = check_image(vi, v["prompt"], seen[:], ocr, None)
                print(f"[images] {v['key']} variant try {attempt} {time.time()-t1:.0f}s reasons={reasons}", flush=True)
                if not reasons or attempt == 1:
                    break
            raw[v["key"]] = vi
            manifest[v["key"]] = {"attempt": attempt, "reasons": reasons, "seed": v["seed"] + attempt * 101, "kind": "variant", "palette_distance": round(palette_distance(vi, cfg), 1)}
        if _has("imagehash"):
            seen.append(__import__("imagehash").phash(raw[b["key"]].resize((256, 144))))
    del pipe, i2i
    gc.collect()
    clip = make_clip_scorer()
    desc = {}
    for grp in groups:
        desc[grp["base"]["key"]] = grp["base"]["prompt"]
        for v in grp["variants"]:
            desc[v["key"]] = v["prompt"]
    for key, im in raw.items():
        variant = key.split(".")[1]
        final = painted_post(im, variant, float(ic["upscale"]), grain_seed=int(__import__('hashlib').md5(key.encode()).hexdigest()[:6], 16))
        prefix = os.path.join(out_dir, key)
        final.save(prefix + ".jpg", quality=95, subsampling=0)
        layers = depth_layers(final, prefix) if cfg.get("depth", {}).get("layers") else False
        sim = None
        if clip is not None:
            try:
                sim = round(clip(im, desc[key]), 3)
            except Exception:  # noqa: BLE001
                sim = None
        manifest[key].update({"file": key + ".jpg", "layers": bool(layers), "clip": sim, "size": list(final.size)})
        print(f"[images] wrote {key} {final.size} layers={layers} clip={sim}", flush=True)
    with open(os.path.join(out_dir, f"images_{shard}.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1)
    return 0


def _has(mod: str) -> bool:
    try:
        __import__(mod)
        return True
    except Exception:  # noqa: BLE001
        return False


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--out", required=True)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=1)
    a = ap.parse_args(argv)
    return run(a.plan, a.out, a.shard, a.shards)


if __name__ == "__main__":
    sys.exit(main())

"""Planner: script.md + job.yaml + config -> build/<slug>/plan.json (stdlib only).

The plan is the contract between every later stage: sentences for TTS, locations for images, shots for assembly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

from . import miniyaml, vocab
from .parse import parse
from .textutil import count_words, estimate_seconds, pause_after, split_sentences
from .validate import ROOT, job_mode, load_cfg, validate_dir

VARIANT_PROMPTS = {
    "day": "daytime, soft warm natural light, gentle shadows",
    "night": "night time, deep blue shadows, warm lamp light, a few softly glowing windows",
    "alarm": "night, red emergency lighting, strong red glow on the walls, tense mood",
    "dusk": "dusk, orange and purple sky, long soft shadows, warm last light",
    "blackout": "power outage, near darkness, only faint cold moonlight and a few weak flashlight beams, everything else unlit",
}

TTS_REPLACE = [
    (r"\bWi-Fi\b", "Why-Fy"),
    (r"\bG5\b", "G five"),
    (r"%", " percent"),
    (r"\s+—\s+", ", "),
    (r"\bthree B\b", "three bee"),
    (r"\bOK\b", "okay"),
]


def tts_text(s: str) -> str:
    for pat, rep in TTS_REPLACE:
        s = re.sub(pat, rep, s)
    return s.strip()


def sha(*parts) -> str:
    return hashlib.sha1("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()[:12]


def build_plan(job_dir: str, cfg=None) -> dict:
    cfg = cfg or load_cfg()
    slug = os.path.basename(os.path.normpath(job_dir))
    mode = job_mode(job_dir)
    with open(os.path.join(job_dir, "script.md"), encoding="utf-8") as fh:
        sc = parse(fh.read())
    job = miniyaml.load_file(os.path.join(job_dir, "job.yaml")) if os.path.exists(os.path.join(job_dir, "job.yaml")) else {}
    wpm = float((job.get("style_seed") or {}).get("wpm", cfg["script"]["wpm"]))
    audio_cfg = cfg["audio"]
    img = cfg["images"]

    sentences, shots = [], []
    chapters = []
    state: dict = {}
    sidx = 0
    n_ch = len(sc.chapters)
    for ci, ch in enumerate(sc.chapters):
        chapters.append({"n": ch.n, "time_card": ch.time_card, "shots": [s.idx for s in ch.shots], "mood": sc.music_moods.get(f"CH{ch.n}", "tense")})
        for si, s in enumerate(ch.shots):
            prev = dict(state)
            state.update(s.track)
            sents = split_sentences(s.text)
            ids = []
            for k, t in enumerate(sents):
                last_in_ch = (si == len(ch.shots) - 1) and (k == len(sents) - 1)
                emo = any(c.expr in ("scared", "shocked", "angry") for c in s.chars) or t.rstrip().endswith("!")
                sentences.append({
                    "id": f"s{sidx:04d}", "idx": sidx, "shot": s.idx, "chapter": ch.n, "text": t, "tts_text": tts_text(t),
                    "words": count_words(t), "expected_s": round(count_words(t) / (wpm / 60.0), 2),
                    "pause_after_s": pause_after(t, audio_cfg, chapter_end=last_in_ch and ci < n_ch - 1),
                    "chapter_end": bool(last_in_ch and ci < n_ch - 1), "emotional": bool(emo),
                })
                if s.silence and k == 0 and sentences[:-1]:
                    sentences[-1]["silence_before"] = True
                    sentences[-2]["pause_after_s"] = max(sentences[-2]["pause_after_s"], float(audio_cfg.get("silence_beat_s", 0.9)))
                ids.append(f"s{sidx:04d}")
                sidx += 1
            shots.append({
                "i": s.idx, "chapter": ch.n, "location": s.location, "variant": s.variant,
                "chars": [{"id": c.id, "pose": c.pose, "expr": c.expr, "x": c.x} for c in s.chars],
                "overlay": ({"name": s.overlays[0].name, "args": s.overlays[0].args} if s.overlays else None),
                "camera": ({"preset": s.camera.preset, "z0": s.camera.z0, "z1": s.camera.z1, "param": s.camera.param} if s.camera else {"preset": "push", "z0": 1.0, "z1": 1.1, "param": None}),
                "fx": s.fx, "sfx": s.sfx, "banner": s.banner, "cta": bool(s.cta),
                "track": dict(state), "prev_track": prev, "sentences": ids, "text": s.text, "act": s.act, "silence": s.silence,
            })

    # locations needing images: one base per location (first variant used), others via img2img of the base
    order: dict = {}
    for sh in shots:
        order.setdefault(sh["location"], [])
        if sh["variant"] not in order[sh["location"]]:
            order[sh["location"]].append(sh["variant"])
    stylep = img["style_prompt"]
    bases, variants = [], []
    for loc, vs in order.items():
        desc = sc.locations[loc]
        base_v = vs[0]
        bprompt = f"{desc}, {VARIANT_PROMPTS[base_v]}, {stylep}"
        bseed = int(img["seed"]) + int(sha(loc), 16) % 10000
        bases.append({"key": f"{loc}.{base_v}", "location": loc, "variant": base_v, "prompt": bprompt, "seed": bseed, "hash": sha(bprompt, bseed, img["width"], img["height"], cfg.get("style_version", 1), img.get("restyle_strength", 0))})
        for v in vs[1:]:
            vprompt = f"{desc}, {VARIANT_PROMPTS[v]}, {stylep}"
            variants.append({"key": f"{loc}.{v}", "location": loc, "variant": v, "base": f"{loc}.{base_v}", "prompt": vprompt, "seed": bseed + 1,
                             "hash": sha(vprompt, bseed + 1, img["variant_strength"], cfg.get("style_version", 1))})
    image_groups = []
    for b in bases:
        image_groups.append({"location": b["location"], "base": b, "variants": [v for v in variants if v["location"] == b["location"]]})

    from .metadata import read_sources

    total_words = sum(s["words"] for s in sentences)
    plan = {
        "slug": slug, "mode": mode, "title": sc.title, "length_min": sc.length_min, "voice": sc.voice,
        "nnn": job.get("nnn"), "short_title": job.get("short_title") or sc.title, "base_name": job.get("base_name"),
        "style": dict(job.get("style_seed") or {}), "style_version": job.get("style_version", cfg.get("style_version", 1)),
        "wpm": wpm, "total_words": total_words, "est_narration_s": round(sum(s["expected_s"] + s["pause_after_s"] for s in sentences), 1),
        "characters": sc.characters, "locations": sc.locations, "chapters": chapters, "shots": shots, "sentences": sentences,
        "image_groups": image_groups, "sources": [{"fact": f, "url": u} for f, u in read_sources(job_dir)],
        "tts_shards": int(cfg["tts"]["matrix"]), "image_shards": int(img["matrix"]),
    }
    return plan


def emit_outputs(plan: dict) -> None:
    """Write step outputs for GitHub Actions (no-op elsewhere)."""
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    tts_hash = sha(*[s["tts_text"] for s in plan["sentences"]], plan["voice"], plan["wpm"])
    img_hash = sha(*[g["base"]["hash"] for g in plan["image_groups"]], *[v["hash"] for g in plan["image_groups"] for v in g["variants"]])
    n_tts = min(plan["tts_shards"], max(1, len(plan["sentences"])))
    n_img = min(plan["image_shards"], max(1, len(plan["image_groups"])))
    lines = [
        f"slug={plan['slug']}", f"mode={plan['mode']}", f"tts_hash={tts_hash}", f"img_hash={img_hash}",
        "tts_shards=" + json.dumps(list(range(n_tts))), "img_shards=" + json.dumps(list(range(n_img))),
        f"n_tts={n_tts}", f"n_img={n_img}",
    ]
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(chr(10).join(lines) + chr(10))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("job_dir")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    cfg = load_cfg()
    issues, _ = validate_dir(a.job_dir, cfg)
    errs = [i for i in issues if i.level == "error"]
    if errs:
        print("validation failed:")
        for i in errs[:30]:
            print("  " + str(i))
        return 1
    plan = build_plan(a.job_dir, cfg)
    out = a.out or os.path.join("build", plan["slug"])
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "plan.json"), "w", encoding="utf-8") as fh:
        json.dump(plan, fh, indent=1, ensure_ascii=False)
    emit_outputs(plan)
    from . import hookscore

    opts, pick = hookscore.parse_options(open(os.path.join(a.job_dir, "script.md"), encoding="utf-8").read())
    json.dump({"options": {n: {"text": t, **hookscore.score(t)} for n, t in opts.items()}, "picked": pick}, open(os.path.join(out, "hook_log.json"), "w"), indent=1)
    print(f"plan ok: {len(plan['shots'])} shots, {len(plan['sentences'])} sentences, {plan['total_words']} words, "
          f"~{plan['est_narration_s']}s narration, {len(plan['image_groups'])} locations -> {out}/plan.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())

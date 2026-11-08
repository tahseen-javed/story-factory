"""Film mode (Pocket Change Films, P-009): tag-format script.txt + direction.yaml -> plan.json (same contract as factory.plan).

script.txt keeps the owner's story, lines and timings untouched. Each beat tag [time | emotion | action | camera | sound | voice] starts at its time;
narration and character lines follow. direction.yaml holds the art direction (locations, cast, framing, props, sfx, mood) per beat.
Stdlib only.
"""
from __future__ import annotations

import json
import os
import re

from . import miniyaml
from .parse import parse_call, parse_camera
from .textutil import count_words, split_sentences

SPEAKERS = {"NARRATOR": "narrator", "OTTO": "otto", "JUNE": "june", "MRS. BRAMBLE": "bramble"}
EMO = [(r"dread|ominous|tight|escalation", "scared"), (r"shame|sad|wistful|sorrow", "sad"), (r"laugh|joy|delight|relief|warm|tender|pleased|small win", "relieved"),
       (r"worry|recognition|comparison", "worried"), (r"decision|brave|realization", "determined"), (r"twist", "shocked")]
BANNED = ("invest", "stock market", "crypto", "tax ", "taxes", "mortgage", "interest rate", "loan", "credit card", "budget", "get rich", "gambl", "casino", "porn", "gore")
VARIANT_PROMPTS = {"day": "daytime, soft warm light, cozy", "night": "night time, deep blue shadows, warm glowing windows, falling snow", "dusk": "dusk, warm orange and purple sky, soft long shadows"}


def t2s(t: str) -> float:
    m, s = t.split(":")
    return int(m) * 60 + int(s)


def parse_script(text: str) -> list:
    lines = text.replace("\r\n", "\n").split("\n")
    start = next(i for i, ln in enumerate(lines) if ln.startswith("SCRIPT (tag format")) + 1
    stop = next((i for i, ln in enumerate(lines) if ln.startswith("Music by act:")), len(lines))
    beats, cur, act = [], None, "act1"
    for ln in lines[start:stop]:
        s = ln.strip()
        if not s:
            continue
        m = re.match(r"^ACT (\d):", s)
        if m:
            act = f"act{m.group(1)}"
            continue
        if s.startswith("[") and s.endswith("]"):
            f = s[1:-1].split(" | ")
            tm = f[0].split("-")
            cur = {"key": tm[0], "t": t2s(tm[0]), "t_end": t2s(tm[1]) if len(tm) > 1 else None, "emotion": f[1], "action": " | ".join(f[2:-3]), "camera": f[-3],
                   "sound": f[-2], "voice": f[-1], "act": act, "lines": []}
            beats.append(cur)
            continue
        m = re.match(r"^(NARRATOR|OTTO AND JUNE|OTTO|JUNE|MRS\. BRAMBLE):\s*(.+)$", s)
        if m and cur is not None:
            cur["lines"].append((m.group(1), m.group(2)))
    return beats


def spoken_words(beats: list) -> int:
    return sum(count_words(t.replace("[beat]", " ")) for b in beats for _, t in b["lines"])


def _emo(b: dict) -> str:
    txt = (b["emotion"] + " " + b["voice"]).lower()
    for pat, e in EMO:
        if re.search(pat, txt):
            return e
    return "neutral"


def load_direction(job_dir: str) -> dict:
    return miniyaml.load_file(os.path.join(job_dir, "direction.yaml"))


def validate(job_dir: str, cfg: dict) -> list:
    from .validate import Issue

    I = []
    sp = os.path.join(job_dir, "script.txt")
    raw = open(sp, encoding="utf-8").read()
    if raw.startswith("\x00GITCRYPT"):
        return [Issue("error", "locked", "script.txt is still encrypted")]
    beats, d = parse_script(raw), load_direction(job_dir)
    words = spoken_words(beats)
    if not (1267 * 0.97 <= words <= 1267 * 1.03):
        I.append(Issue("error", "words", f"{words} spoken words; the script says 1,267 (+-3%)"))
    times = [b["t"] for b in beats]
    if times != sorted(times) or len(set(times)) != len(times) or times[0] != 0:
        I.append(Issue("error", "beats", "beat times must start at 0:00 and strictly increase"))
    for b in beats:
        if b["key"] not in d["beats"]:
            I.append(Issue("error", "direction", f"no art direction for beat {b['key']}"))
        for sp_, txt in b["lines"]:
            low = txt.lower()
            for bad in BANNED:
                if bad in low:
                    I.append(Issue("error", "policy", f"beat {b['key']}: '{bad.strip()}' (no advice, no brands, no gambling/sexual/gore)"))
    for k in d["beats"]:
        if k not in [b["key"] for b in beats]:
            I.append(Issue("error", "direction", f"direction beat {k} has no script beat"))
    fp = os.path.join(job_dir, "facts.json")
    if not os.path.exists(fp):
        I.append(Issue("error", "facts", "facts.json missing (use {\"no_factual_claims\": true})"))
    else:
        f = json.load(open(fp, encoding="utf-8"))
        if not f.get("no_factual_claims") and not all(c.get("url", "").startswith("https://") for c in f.get("claims", [])):
            I.append(Issue("error", "facts", "every claim in facts.json needs a source url"))
    for k, c in d["cast"].items():
        if k not in cfg["characters"]["characters"] and k not in ("heron", "mouse", "squirrel"):
            pass
    for sp_ in ("otto", "june", "bramble"):
        if sp_ not in cfg["characters"]["characters"]:
            I.append(Issue("error", "voices", f"no locked voice profile for '{sp_}' in config/characters.yaml"))
    return I


def build_plan(job_dir: str, cfg: dict) -> dict:
    from .plan import sha
    from .validate import ROOT, job_mode

    slug = os.path.basename(os.path.normpath(job_dir))
    beats = parse_script(open(os.path.join(job_dir, "script.txt"), encoding="utf-8").read())
    d = load_direction(job_dir)
    job = miniyaml.load_file(os.path.join(job_dir, "job.yaml"))
    audio_cfg = cfg["audio"]
    sentences, shots, chapters = [], [], []
    sidx = 0
    for bi, b in enumerate(beats):
        dr = d["beats"][b["key"]]
        slow = "120 wpm" in b["voice"] or bool(re.search(r"\bslow\b", b["voice"]))
        emo = _emo(b)
        ids = []
        first = True
        for who, text in b["lines"]:
            names = ["OTTO", "JUNE"] if who == "OTTO AND JUNE" else [who]
            for pi, nm in enumerate(names):
                speaker = SPEAKERS[nm]
                wpm = (120.0 if slow else 145.0) if speaker == "narrator" else 150.0
                segs = [x.strip() for x in text.split("[beat]") if x.strip()]
                for si, seg in enumerate(segs):
                    parts = split_sentences(seg) or [seg]
                    for k, t in enumerate(parts):
                        last = k == len(parts) - 1
                        beat_after = last and si < len(segs) - 1
                        nxt_speaker_change = last and si == len(segs) - 1
                        sentences.append({
                            "id": f"s{sidx:04d}", "idx": sidx, "shot": bi, "chapter": int(b["act"][-1]), "text": t, "tts_text": t.replace("...", "…"), "words": count_words(t),
                            "expected_s": round(max(0.7, count_words(t) / (wpm / 60.0)), 2), "pause_after_s": 0.7 if beat_after else (0.38 if nxt_speaker_change else 0.28),
                            "chapter_end": False, "emotional": emo in ("scared", "shocked", "sad"), "speaker": speaker, "emo": emo, "wpm": wpm,
                            "parallel": bool(pi == 1), "asr_skip": bool(re.search(r"hoo-kay", t, re.I)),
                            **({"at": round(b["t"] + float(dr.get("dly", 0.3)), 2)} if first else {}),
                        })
                        first = False
                        ids.append(f"s{sidx:04d}")
                        sidx += 1
        chars = [{"id": c["id"], "pose": c.get("pose", "stand"), "expr": c.get("expr", "neutral"), "x": c.get("x"), "rot": c.get("rot", 0), "dy": c.get("dy", 0), "s": c.get("s", 1.0),
                  "side": c.get("side")} for c in (dr.get("chars") or [])]
        ov = None
        if dr.get("ov"):
            name, args = parse_call(dr["ov"])
            ov = {"name": name, "args": args}
        cam = {"preset": "push", "z0": 1.0, "z1": 1.1, "param": None}
        if dr.get("cam"):
            c = parse_camera(dr["cam"])
            cam = {"preset": c.preset, "z0": c.z0, "z1": c.z1, "param": c.param}
        loc, var = dr["loc"].split(".")
        shots.append({
            "i": bi, "chapter": int(b["act"][-1]), "location": loc, "variant": var, "chars": chars, "overlay": ov, "camera": cam, "fx": list(dr.get("fx") or []),
            "sfx": list(dr.get("sfx") or []), "banner": None, "cta": bool(dr.get("cta")), "track": {}, "prev_track": {}, "sentences": ids, "text": " ".join(t for _, t in b["lines"]),
            "act": b["act"], "silence": False, "at": b["t"], "props": dr.get("props") or [], "cracks": dr.get("cracks"), "split": dr.get("split"), "hold": bool(dr.get("hold")),
            "endcard": bool(dr.get("endcard")), "silent_s": float(dr.get("silent", 0) or 0), "mood": dr.get("mood"), "grade": dr.get("grade"), "frm_pool": dr.get("frm"), "t_end": b["t_end"],
        })
    for n, a in enumerate(("act1", "act2", "act3"), 1):
        idx = [s["i"] for s in shots if s["act"] == a]
        chapters.append({"n": n, "time_card": d["acts"][a]["title"], "shots": idx, "mood": d["acts"][a]["mood"]})
    # backgrounds: one base per location, other variants by img2img of the base; split shots need their second location too
    order: dict = {}
    for sh in shots:
        order.setdefault(sh["location"], [])
        if sh["variant"] not in order[sh["location"]]:
            order[sh["location"]].append(sh["variant"])
        if sh["split"]:
            l2, v2 = sh["split"].split(".")
            order.setdefault(l2, [])
            if v2 not in order[l2]:
                order[l2].append(v2)
    img = cfg["images"]
    stylep = img["style_prompt"] + ", cute round storybook shapes, no animals, no characters"
    groups = []
    for loc, vs in order.items():
        desc = d["locations"][loc]
        bseed = int(img["seed"]) + int(sha(loc), 16) % 10000
        bprompt = f"{desc}, {VARIANT_PROMPTS[vs[0]]}, {stylep}"
        base = {"key": f"{loc}.{vs[0]}", "location": loc, "variant": vs[0], "prompt": bprompt, "seed": bseed,
                "hash": sha(bprompt, bseed, img["width"], img["height"], cfg.get("style_version", 1), img.get("restyle_strength", 0))}
        variants = []
        for v in vs[1:]:
            vp = f"{desc}, {VARIANT_PROMPTS[v]}, {stylep}"
            variants.append({"key": f"{loc}.{v}", "location": loc, "variant": v, "base": base["key"], "prompt": vp, "seed": bseed + 1, "hash": sha(vp, bseed + 1, img["variant_strength"], cfg.get("style_version", 1))})
        groups.append({"location": loc, "base": base, "variants": variants})
    total_words = sum(s["words"] for s in sentences)
    return {
        "slug": slug, "kind": "film", "mode": job_mode(job_dir), "title": "GIFT | An Animated Short Film", "length_min": 10.55, "voice": "default", "nnn": job.get("nnn", 2),
        "short_title": job.get("short_title", "Gift"), "base_name": job.get("base_name"), "style": dict(job.get("style_seed") or {"accent": "amber", "titlecard": "paper_tab", "lut": "warm_day", "transition": "hard_cuts"}),
        "style_version": job.get("style_version", 3), "wpm": 145.0, "total_words": total_words, "est_narration_s": round(sum(s["expected_s"] + s["pause_after_s"] for s in sentences), 1),
        "characters": {k: {"rig": v.get("rig", "rig_hero"), "params": {kk: vv for kk, vv in v.items() if kk != "rig"}} for k, v in d["cast"].items()},
        "locations": d["locations"], "chapters": chapters, "shots": shots, "sentences": sentences, "image_groups": groups, "sources": [],
        "tts_shards": int(cfg["tts"]["matrix"]), "image_shards": max(1, len(groups)), "film_end_s": float(beats[-1]["t_end"] or beats[-1]["t"] + 20),
    }

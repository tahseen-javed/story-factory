"""Video Doctor Phase 2, stage 1: voice verification against the script with faster-whisper (MIT, CPU, int8).

Checks (numeric, with timestamps):
  A2-WER       word error rate of the whole voice track versus the script, at most 5 %
  A2-SKIP      a script word that was not spoken (skipped words)
  A2-DOUBLE    a word or phrase spoken twice that the script says once
  A2-WPM       speaking speed 130-160 words per minute (speaking time only)
  A2-DRIFT     a sentence whose voice fingerprint (mel + f0) leaves the locked narrator

The stage never raises: if the model cannot load it reports status SKIPPED and the pipeline continues (the other stages still decide).
Pure functions (align, normalise) are unit-tested without the model; the model call is tested in CI.
"""
from __future__ import annotations

import argparse
import difflib
import glob
import json
import os
import re
import sys
import time

NUM = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine", "10": "ten", "11": "eleven", "12": "twelve",
       "13": "thirteen", "14": "fourteen", "15": "fifteen", "16": "sixteen", "17": "seventeen", "18": "eighteen", "19": "nineteen", "20": "twenty"}
SPELL = {"neighbour": "neighbor", "neighbours": "neighbors", "colour": "color", "favourite": "favorite", "grey": "gray", "metre": "meter", "metres": "meters", "centre": "center",
         "realise": "realize", "organise": "organize", "mum": "mom", "draught": "draft", "okay": "ok", "mrs": "missus", "mr": "mister", "ms": "miss", "dr": "doctor"}


def norm_words(text: str) -> list:
    """Same normaliser as the TTS round-trip check (numbers, years, clock times, percent) plus British/American spellings."""
    from .. import asr_check

    return [SPELL.get(w, w).replace("'s", "s") for w in asr_check.normalize(text)]


def _same(a: str, b: str) -> bool:
    if a == b:
        return True
    return len(a) >= 5 and len(b) >= 5 and difflib.SequenceMatcher(None, a, b).ratio() >= 0.86


def align(ref: list, hyp: list) -> dict:
    """Word-level alignment of the script against the recognised words: skipped, changed (substituted), extra and doubled words with their positions."""
    canon = {w: w for w in ref}
    h2 = [w if w in canon else next((r for r in canon if _same(r, w)), w) for w in hyp]
    sm = difflib.SequenceMatcher(None, ref, h2, autojunk=False)
    sub = dele = ins = 0
    skipped, extra, doubled, subs = [], [], [], []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        nr, nh = i2 - i1, j2 - j1
        m = min(nr, nh)
        if op == "replace":
            subs += [(i1 + k, ref[i1 + k], hyp[j1 + k]) for k in range(m)]
        sub += m
        for i in range(i1 + m, i2):
            skipped.append((i, ref[i]))
            dele += 1
        for j in range(j1 + m, j2):
            extra.append((j, hyp[j], i2))
            ins += 1
            if (j > 0 and hyp[j] == hyp[j - 1]) or (j + 1 < len(hyp) and hyp[j] == hyp[j + 1]) or (j >= 2 and hyp[j - 2:j] == hyp[j:j + 2]):
                doubled.append((j, hyp[j], i2))
    return {"wer": (sub + dele + ins) / max(1, len(ref)), "sub": sub, "del": dele, "ins": ins, "skipped": skipped, "extra": extra, "doubled": doubled, "subs": subs, "n_ref": len(ref)}


def sentence_windows(plan_sentences: list, words: list, margin: float = 0.35) -> dict:
    """Assign recognised words (text, t0, t1) to the sentence whose window contains their midpoint."""
    out = {s["id"]: [] for s in plan_sentences}
    for w, t0, t1 in words:
        mid = (t0 + t1) / 2
        best = None
        for s in plan_sentences:
            if s["start"] - margin <= mid <= s["end"] + margin:
                if best is None or abs(mid - (s["start"] + s["end"]) / 2) < abs(mid - (best["start"] + best["end"]) / 2):
                    best = s
        if best is not None:
            out[best["id"]].append(w)
    return out


def finding(th, code, key, t0, t1, value, thr, msg, **extra):
    d = {"code": code, "severity": th["severity"].get(key, "MAJOR"), "t0": round(float(t0), 2), "t1": round(float(t1), 2),
         "value": None if value is None else round(float(value), 3), "threshold": thr, "msg": msg}
    d.update(extra)
    return d


def verify_text(plan_sentences: list, words: list, th: dict, tts_hyp: dict | None = None) -> tuple:
    """(findings, metrics, reroll_ids). Whole-track alignment, defects attributed to sentences by position. A defect is CONFIRMED (BLOCKER/MAJOR, re-roll) when the second,
    independent recogniser used in the TTS stage (tts_hyp: sentence id -> text) also lacks the word; one-recogniser doubts are listed as MINOR A2-UNCONFIRMED."""
    from collections import Counter

    v = th["voice"]
    f, m = [], {}
    refs = [norm_words(s["text"]) for s in plan_sentences]
    own = [k for k, r in enumerate(refs) for _ in r]
    ref_all = [w for r in refs for w in r]
    hyp_all = [x for w, _, _ in words for x in norm_words(w)]
    a = align(ref_all, hyp_all)
    m["wer"], m["words_ref"], m["words_hyp"] = round(a["wer"], 4), a["n_ref"], len(hyp_all)
    end = max([s["end"] for s in plan_sentences] or [0.0])
    if a["wer"] > v["wer_max"]:
        f.append(finding(th, "A2-WER", "voice_wer", 0, end, a["wer"], v["wer_max"], f"word error rate {a['wer']*100:.1f}% versus the script"))

    def bag(k):
        sid = plan_sentences[k]["id"]
        return Counter(norm_words(tts_hyp[sid])) if tts_hyp and sid in tts_hyp else None

    found = {}   # sentence index -> {"skip": [], "double": [], "changed": [], "weak": []}
    for i, w in a["skipped"]:
        k = own[i]
        b = bag(k)
        found.setdefault(k, {}).setdefault("skip" if (b is None or b[w] < Counter(refs[k])[w]) else "weak", []).append(w)
    for i, rw, hw in a["subs"]:
        k = own[i]
        b = bag(k)
        found.setdefault(k, {}).setdefault("changed" if (b is None or b[rw] < Counter(refs[k])[rw]) else "weak", []).append(f"{rw}->{hw}")
    for j, w, rp in a["doubled"]:
        k = own[max(0, min(rp, len(own)) - 1)] if own else 0
        b = bag(k)
        found.setdefault(k, {}).setdefault("double" if (b is None or b[w] > Counter(refs[k])[w]) else "weak", []).append(w)
    reroll = []
    for k, d in sorted(found.items()):
        s = plan_sentences[k]
        for key, code, sev in (("skip", "A2-SKIP", "voice_skip"), ("changed", "A2-CHANGED", "voice_skip"), ("double", "A2-DOUBLE", "voice_double")):
            if d.get(key):
                f.append(finding(th, code, sev, s["start"], s["end"], len(d[key]), 0, f"{key} words: {', '.join(d[key][:4])}", sentence=s["id"]))
        if d.get("weak") and not any(d.get(x) for x in ("skip", "changed", "double")):
            f.append({"code": "A2-UNCONFIRMED", "severity": "MINOR", "t0": s["start"], "t1": s["end"], "value": len(d["weak"]), "threshold": 0, "msg": f"only one recogniser doubts: {', '.join(d['weak'][:4])}", "sentence": s["id"]})
        if any(d.get(x) for x in ("skip", "changed", "double")):
            reroll.append(s["id"])
    speaking = sum(s["end"] - s["start"] for s in plan_sentences)
    m["wpm"] = round(sum(len(r) for r in refs) / max(speaking, 1e-6) * 60, 1)
    lo, hi = v["wpm"]
    if not (lo <= m["wpm"] <= hi):
        f.append(finding(th, "A2-WPM", "voice_wpm", 0, end, m["wpm"], [lo, hi], f"speaking speed {m['wpm']} wpm outside {lo}-{hi}"))
    return f, m, reroll


def fingerprint_check(voice, sr: int, plan_sentences: list, th: dict, reference: dict | None) -> tuple:
    """Per-sentence mel/f0 fingerprint versus the median of this video and (if present) the stored narrator reference."""
    import numpy as np

    from .. import voicecheck

    v = th["voice"]
    fps = []
    for s in plan_sentences:
        seg = voice[int(s["start"] * sr): int(s["end"] * sr)]
        if len(seg) > int(0.8 * sr):
            fps.append((s, voicecheck.fingerprint(seg.astype("float64"), sr)))
    f, m = [], {}
    if len(fps) < 3:
        return f, m, None
    med = {"mel": np.median(np.stack([p["mel"] for _, p in fps]), axis=0), "f0": float(np.median([p["f0"] for _, p in fps if p["f0"] > 0] or [0.0]))}
    worst = 0.0
    for s, p in fps:
        d_mel, d_f0 = voicecheck.distance(p, med)
        if p["f0"] <= 0:
            d_f0 = 0.0
        worst = max(worst, d_mel)
        if d_mel > v["drift_mel_db"] or d_f0 > v["drift_f0_hz"]:
            f.append(finding(th, "A2-DRIFT", "voice_drift", s["start"], s["end"], d_mel, v["drift_mel_db"], f"voice differs from the narrator in this sentence (mel {d_mel:.1f} dB, f0 {d_f0:.0f} Hz)", sentence=s["id"]))
    m["voice_drift_mel_max"] = round(worst, 2)
    if reference:
        ref = {"mel": np.array(reference["mel"]), "f0": float(reference["f0"])}
        d_mel, d_f0 = voicecheck.distance(med, ref)
        m["narrator_distance_mel"], m["narrator_distance_f0"] = round(d_mel, 2), round(d_f0, 1)
        if d_mel > v["narrator_mel_db"] or d_f0 > v["narrator_f0_hz"]:
            f.append(finding(th, "A2-NARRATOR", "voice_drift", 0, plan_sentences[-1]["end"], d_mel, v["narrator_mel_db"], "this is not the locked narrator voice (distance to the stored fingerprint)"))
    return f, m, {"mel": [float(x) for x in med["mel"]], "f0": med["f0"]}


def transcribe(voice_16k, model_name: str = "base.en") -> list:
    from faster_whisper import WhisperModel

    model = WhisperModel(model_name, device="cpu", compute_type="int8", cpu_threads=4)
    segs, _ = model.transcribe(voice_16k, language="en", word_timestamps=True, vad_filter=False, beam_size=5, temperature=0.0, condition_on_previous_text=False)
    return [(w.word.strip(), float(w.start), float(w.end)) for s in segs for w in (s.words or [])]


def run(asm: str, th: dict, model_name: str = "small.en", ref_path: str | None = None, tts_dir: str | None = None) -> dict:
    t0 = time.time()
    rep = {"stage": "voice", "status": "OK", "findings": [], "metrics": {}, "reroll": [], "model": model_name}
    try:
        import numpy as np
        import soundfile as sf
        from scipy.signal import resample_poly

        ap = json.load(open(os.path.join(asm, "audio_plan.json"), encoding="utf-8"))
        texts = {s["id"]: s["text"] for s in json.load(open(os.path.join(asm, "plan.json"), encoding="utf-8"))["sentences"]}
        sents = [{"id": v["id"], "start": float(v["start"]), "end": float(v["end"]), "text": texts[v["id"]]} for v in ap["voice"]]
        x, sr = sf.read(os.path.join(asm, "stem_voice.wav"), dtype="float32")
        x = x if x.ndim == 1 else x.mean(axis=1)
        x16 = resample_poly(x, 16000, sr).astype("float32")
        words = transcribe(x16, model_name)
        tts_hyp = {}
        for mp in glob.glob(os.path.join(tts_dir, "**", "meta_*.json"), recursive=True) if tts_dir else []:
            for x in json.load(open(mp, encoding="utf-8")).get("sentences", []):
                if x.get("hyp"):
                    tts_hyp[x["id"]] = x["hyp"]
        f, m, reroll = verify_text(sents, words, th, tts_hyp)
        m["second_recogniser_sentences"] = len(tts_hyp)
        reference = json.load(open(ref_path)) if ref_path and os.path.exists(ref_path) else None
        f2, m2, med = fingerprint_check(x.astype("float64"), sr, sents, th, reference)
        rep.update({"findings": f + f2, "metrics": {**m, **m2}, "reroll": reroll, "narrator_fingerprint": med, "hypothesis": " ".join(w for w, _, _ in words)})
    except Exception as e:  # noqa: BLE001   the stage must never take the pipeline down
        rep.update({"status": "SKIPPED", "error": f"{e.__class__.__name__}: {str(e)[:200]}"})
    rep["seconds"] = round(time.time() - t0, 1)
    return rep


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--asm", required=True)
    ap.add_argument("--model", default="small.en")
    ap.add_argument("--tts", default=None)
    ap.add_argument("--reference", default=os.path.join(os.path.dirname(__file__), "..", "..", "library", "narrator_fingerprint.json"))
    a = ap.parse_args(argv)
    from .run import load_th

    rep = run(a.asm, load_th(), a.model, a.reference, a.tts)
    os.makedirs(os.path.join(a.asm, "doctor"), exist_ok=True)
    json.dump(rep, open(os.path.join(a.asm, "doctor", "VOICE_REPORT.json"), "w", encoding="utf-8"), indent=1)
    bad = [x["code"] for x in rep["findings"] if x["severity"] in ("BLOCKER", "MAJOR")]
    print(f"DOCTOR voice: {rep['status']} {rep.get('error', '')}; wer {rep['metrics'].get('wer')}; wpm {rep['metrics'].get('wpm')}; BLOCKER/MAJOR {bad}; reroll {rep['reroll']}; {rep['seconds']}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())

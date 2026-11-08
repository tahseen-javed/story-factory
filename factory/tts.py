"""TTS stage (runs on a GitHub runner, CPU). One shard = a contiguous block of sentences.

Chatterbox Turbo (needs a reference clip) -> Chatterbox original (built-in default voice) -> Kokoro fallback.
Every sentence is round-trip checked with ASR (WER <= qa.asr_wer_max, duration within 0.6-1.6x of expected); failing sentences are
regenerated with a new seed (max tts.max_regen) and the best attempt is kept and flagged.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

from . import miniyaml
from .asr_check import Asr, wer


def _cfg():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return miniyaml.load_file(os.path.join(root, "config", "factory.yaml"))


def valid_wav(path: str) -> bool:
    try:
        with open(path, "rb") as fh:
            return fh.read(4) == b"RIFF"
    except OSError:
        return False


def resolve_voice(voice: str) -> str | None:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    name = "me" if voice == "me" else "default"
    p = os.path.join(root, "voices", f"{name}.wav")
    return p if valid_wav(p) else None  # encrypted/locked or missing -> built-in voice


class Engine:
    def __init__(self, name, model, ref):
        self.name, self.model, self.ref = name, model, ref
        self.sr = getattr(model, "sr", 24000)

    def generate(self, text: str, seed: int, exaggeration: float, cfg_weight: float, temperature: float = 0.75):
        import torch

        torch.manual_seed(seed)
        if self.name == "kokoro":
            import numpy as np

            chunks = [a for _, _, a in self.model(text, voice="af_heart", speed=1.0)]
            return np.concatenate([c.numpy() if hasattr(c, "numpy") else c for c in chunks]).astype("float32")
        if self.name == "chatterbox_turbo":
            wav = self.model.generate(text, audio_prompt_path=self.ref)
        else:
            kw = dict(exaggeration=exaggeration, cfg_weight=cfg_weight, temperature=temperature)
            if self.ref:
                kw["audio_prompt_path"] = self.ref
            wav = self.model.generate(text, **kw)
        return wav.squeeze().cpu().numpy().astype("float32")


def load_engine(cfg, voice_ref):
    import torch

    torch.set_num_threads(os.cpu_count() or 4)
    last = None
    for name in cfg["tts"]["engine_order"]:
        try:
            if name == "chatterbox_turbo":
                if not voice_ref:
                    print("[tts] turbo skipped: needs a reference clip (voices/default.wav not available)")
                    continue
                from chatterbox.tts_turbo import ChatterboxTurboTTS  # type: ignore

                return Engine(name, ChatterboxTurboTTS.from_pretrained(device="cpu"), voice_ref)
            if name == "chatterbox":
                from chatterbox.tts import ChatterboxTTS  # type: ignore

                return Engine(name, ChatterboxTTS.from_pretrained(device="cpu"), voice_ref)
            if name == "kokoro":
                from kokoro import KPipeline  # type: ignore

                e = Engine(name, KPipeline(lang_code="a"), None)
                e.sr = 24000
                return e
        except Exception as ex:  # noqa: BLE001
            last = ex
            print(f"[tts] engine {name} failed: {ex!r}")
    raise RuntimeError(f"no TTS engine available: {last!r}")


def postprocess(x, sr, speed=1.0):
    """Trim edge silence, gentle fades, even loudness (-21 dBFS RMS) so sentences sit at one level."""
    import numpy as np

    a = np.asarray(x, dtype="float32")
    thr = 0.006
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx):
        a = a[max(0, idx[0] - int(0.03 * sr)): min(len(a), idx[-1] + int(0.14 * sr))]
    if speed and abs(speed - 1.0) > 1e-3:
        import librosa  # type: ignore

        a = librosa.effects.time_stretch(a, rate=speed)
    n_in, n_out = int(0.006 * sr), int(0.05 * sr)
    if len(a) > n_in + n_out:
        a[:n_in] *= np.linspace(0, 1, n_in)
        a[-n_out:] *= np.linspace(1, 0, n_out)
    rms = float(np.sqrt(np.mean(a ** 2)) + 1e-9)
    a = a * (10 ** (-21 / 20) / rms)
    peak = float(np.max(np.abs(a)) + 1e-9)
    if peak > 0.95:
        a = a * (0.95 / peak)
    return a


def run(plan_path: str, out_dir: str, shard: int, nshards: int, only: list | None = None):
    import soundfile as sf  # type: ignore

    cfg = _cfg()
    t = cfg["tts"]
    plan = json.load(open(plan_path, encoding="utf-8"))
    sents = plan["sentences"]
    per = math.ceil(len(sents) / nshards)
    mine = sents[shard * per: (shard + 1) * per]
    if only:
        mine = [s for s in sents if s["id"] in only]
    os.makedirs(out_dir, exist_ok=True)
    voice_ref = resolve_voice(plan.get("voice", t.get("voice", "default")))
    eng = load_engine(cfg, voice_ref)
    asr = Asr(cache_dir=os.path.join(out_dir, "..", ".asr"))
    print(f"[tts] shard {shard}/{nshards}: {len(mine)} sentences, engine={eng.name}, asr={asr.name}, ref={'yes' if voice_ref else 'built-in'}")
    meta = []
    wer_max = float(cfg["qa"].get("asr_target_wer", cfg["qa"]["asr_wer_max"]))
    prev = {}
    mp = os.path.join(out_dir, f"meta_{shard}.json")
    if os.path.exists(mp):  # cache restore from the previous run: keep sentences that already meet the target, re-synthesise only the rest
        try:
            prev = {m["id"]: m for m in json.load(open(mp, encoding="utf-8"))["sentences"]}
        except Exception:  # noqa: BLE001
            prev = {}
    TEMPS = [0.75, 0.65, 0.85, 0.7, 0.8, 0.6, 0.9, 0.55, 0.75]
    lo, hi = t["duration_ratio"]
    for s in mine:
        pm = prev.get(s["id"])
        if pm and pm.get("ok") and pm.get("wer", 1) <= wer_max and os.path.exists(os.path.join(out_dir, f"{s['id']}.wav")):
            meta.append(pm)
            print(f"[tts] {s['id']} kept (wer={pm.get('wer')})", flush=True)
            continue
        best = None
        t0 = time.time()
        for attempt in range(int(t["max_regen"]) + 1):
            seed = int(t["seed"]) + s["idx"] * 31 + attempt * 1009
            ex = 0.7 if s.get("emotional") else float(t["exaggeration"])
            try:
                cfgw = (float(t["cfg_weight"]) if not s.get("emotional") else 0.35) + [0.0, 0.12, -0.12, 0.2, -0.2, 0.0][attempt % 6]
                raw = eng.generate(s["tts_text"], seed, ex + 0.05 * (attempt % 3), min(0.95, max(0.1, cfgw)), TEMPS[attempt % len(TEMPS)])
            except Exception as e:  # noqa: BLE001
                print(f"[tts] {s['id']} generation error: {e!r}")
                continue
            a = postprocess(raw, eng.sr, float(t.get("speed", 1.0)))
            tmp = os.path.join(out_dir, f"{s['id']}.try.wav")
            sf.write(tmp, a, eng.sr, subtype="PCM_16")
            dur = len(a) / eng.sr
            hyp, w = None, 0.0
            if asr.ok:
                hyp = asr.transcribe(tmp)
                w = wer(s["text"], hyp)
            ratio = dur / max(1.0, s["expected_s"])  # floor: one-word sentences are naturally slower than the wpm average
            ok = w <= wer_max and lo <= ratio <= hi
            cand = {"id": s["id"], "dur": round(dur, 3), "wer": round(w, 3), "ratio": round(ratio, 2), "attempts": attempt + 1,
                    "seed": seed, "engine": eng.name, "hyp": hyp, "ok": ok}
            if best is None or (not best["ok"] and (ok or w < best["wer"])):
                best = cand
                os.replace(tmp, os.path.join(out_dir, f"{s['id']}.wav"))
            else:
                os.remove(tmp)
            if ok:
                break
        if best is None:
            raise RuntimeError(f"TTS failed for {s['id']}")
        best["secs"] = round(time.time() - t0, 1)
        meta.append(best)
        flag = "" if best["ok"] else "  <-- FLAG"
        print(f"[tts] {s['id']} dur={best['dur']}s wer={best['wer']} tries={best['attempts']} {best['secs']}s{flag}", flush=True)
    with open(os.path.join(out_dir, f"meta_{shard}.json"), "w", encoding="utf-8") as fh:
        json.dump({"engine": eng.name, "asr": asr.name, "sentences": meta}, fh, indent=1)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--out", required=True)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=1)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args(argv)
    return run(a.plan, a.out, a.shard, a.shards, a.only)


if __name__ == "__main__":
    sys.exit(main())

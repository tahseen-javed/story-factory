"""Chatterbox / Resemble PerTh watermark check (runs in CI where resemble-perth is installed).

python -m factory.wmcheck <final.mp4> <assembled_dir> <out.json>
Measures three signals: a raw TTS sentence (control), the voice-only master (after our voice chain) and the final mp4 audio (after mix, loudnorm and AAC).
get_watermark returns ~1.0 when the PerTh watermark is detected and ~0.0 when not.
"""
from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
import tempfile


def score(wm, path: str) -> float | None:
    import librosa

    try:
        wav, sr = librosa.load(path, sr=None)
        return round(float(wm.get_watermark(wav, sample_rate=sr)), 3)
    except Exception as e:  # noqa: BLE001
        print(f"[wmcheck] {path}: {e!r}")
        return None


def main(argv=None):
    mp4, asm, out = (argv or sys.argv[1:])[:3]
    import perth

    cls = getattr(perth, "PerthImplicitWatermarker", None)
    if cls is None:  # perth swallows its own import error (usually a missing pkg_resources); surface the real one
        from perth.perth_net.perth_net_implicit.perth_watermarker import PerthImplicitWatermarker as cls
    wm = cls()
    tmp = tempfile.mkdtemp()
    final_wav = os.path.join(tmp, "final.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp4, "-vn", "-ac", "1", "-ar", "24000", final_wav], check=True)
    raws = sorted(glob.glob(os.path.join(asm, "voice", "s*.wav")))
    raw_scores = [score(wm, p) for p in raws[:: max(1, len(raws) // 8)][:8]]
    rep = {"raw_tts_sentences": raw_scores, "voice_only_master": score(wm, os.path.join(asm, "voice_only.wav")), "final_mp4_audio": score(wm, final_wav),
           "note": "1.0 = PerTh watermark detected, 0.0 = not detected; final_mp4_audio is after voice chain, reverb, music/sfx mix, loudnorm and AAC"}
    rep["raw_detected"] = all((s or 0) >= 0.5 for s in raw_scores if s is not None)
    rep["final_detected"] = (rep["final_mp4_audio"] or 0) >= 0.5
    json.dump(rep, open(out, "w"), indent=1)
    print(json.dumps(rep))
    return 0


if __name__ == "__main__":
    sys.exit(main())

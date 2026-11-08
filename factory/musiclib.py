"""Licence-safe music library: 6 moods rendered once by our own synthesiser (original, no third-party audio, dedicated CC0), cached and reused.

build(dir): render missing stems to FLAC + index.json.  segment(dir, mood, seconds, seed): loop a stem with 2 s crossfades to any length.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

from . import synth
from .synth import SR

MOODS = ("calm", "tense", "urgent", "sorrow", "climax", "hopeful")
STEM_S = 60
_cache: dict = {}


def build(lib_dir: str, only: str | None = None) -> int:
    import soundfile as sf

    os.makedirs(lib_dir, exist_ok=True)
    idx_path = os.path.join(lib_dir, "index.json")
    idx = {}
    for m in ([only] if only else MOODS):
        f = os.path.join(lib_dir, f"{m}.flac")
        if os.path.exists(f):
            continue
        x = synth.render_music(m, STEM_S, seed=7)
        sf.write(f, x.T.astype("float32"), SR, format="FLAC", subtype="PCM_24")
        idx[m] = {"file": f"{m}.flac", "seconds": STEM_S, "licence": "original synthesis by story-factory, dedicated CC0", "seed": 7}
        print(f"[musiclib] built {m}", flush=True)
    json.dump(idx, open(os.path.join(lib_dir, f"index_{only or 'all'}.json"), "w"), indent=1)
    return 0


def segment(lib_dir: str, mood: str, seconds: float, seed: int = 0):
    """Stereo float32 (2, n) of the requested length, or None when the library is missing."""
    f = os.path.join(lib_dir or "", f"{mood}.flac")
    if not lib_dir or not os.path.exists(f):
        return None
    import soundfile as sf

    if mood not in _cache:
        _cache[mood] = sf.read(f, dtype="float32")[0].T
    stem = _cache[mood]
    n, L, xf = int(seconds * SR), stem.shape[1], int(2.0 * SR)
    out = np.zeros((2, n), dtype="float32")
    pos, start = 0, int((seed * 13.7 % (L * 0.5 / SR)) * SR)
    while pos < n:
        piece = np.roll(stem, -start, axis=1) if start else stem
        take = min(L, n - pos)
        seg = piece[:, :take].copy()
        if pos > 0:
            k = min(xf, take)
            seg[:, :k] *= np.linspace(0, 1, k)
            out[:, pos:pos + k] *= np.linspace(1, 0, k)
        out[:, pos:pos + take] += seg
        if pos + take >= n:
            break
        pos += max(1, take - xf)
        start = (start + int(11.3 * SR)) % L
    return out


if __name__ == "__main__":
    sys.exit(build(sys.argv[1] if len(sys.argv) > 1 else "build/musiclib", sys.argv[2] if len(sys.argv) > 2 else None))

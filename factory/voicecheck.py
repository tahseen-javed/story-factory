"""P-008 C: locked, distinct character voices. numpy only.

profiles_ok: every script character has a locked profile, engines are allowed, no two voices share the same recipe, the narrator differs from all.
fingerprint/too_similar: a cheap voice fingerprint (level-free mean log-mel + median f0) compared between speakers; QA fails if two voices are too similar.
"""
from __future__ import annotations

import numpy as np


def _mel_bank(sr: int, n_fft: int, n_mels: int = 40):
    mel = lambda f: 2595 * np.log10(1 + f / 700.0)
    inv = lambda m: 700 * (10 ** (m / 2595.0) - 1)
    pts = inv(np.linspace(mel(60), mel(min(8000, sr / 2 - 1)), n_mels + 2))
    bins = np.floor((n_fft + 1) * pts / sr).astype(int)
    fb = np.zeros((n_mels, n_fft // 2 + 1))
    for i in range(1, n_mels + 1):
        a, b, c = bins[i - 1], bins[i], bins[i + 1]
        if b > a:
            fb[i - 1, a:b] = (np.arange(a, b) - a) / (b - a)
        if c > b:
            fb[i - 1, b:c] = (c - np.arange(b, c)) / (c - b)
    return fb


def fingerprint(x: np.ndarray, sr: int) -> dict:
    x = np.asarray(x, dtype="float64")
    n_fft, hop = 1024, 256
    if len(x) < n_fft * 4:
        return {"mel": np.zeros(40), "f0": 0.0}
    win = np.hanning(n_fft)
    frames = np.stack([x[i:i + n_fft] * win for i in range(0, len(x) - n_fft, hop)])
    en = np.sqrt((frames ** 2).mean(axis=1))
    voiced = frames[en > np.median(en)]
    spec = np.abs(np.fft.rfft(voiced, axis=1)) ** 2
    mel = 10 * np.log10(spec @ _mel_bank(sr, n_fft).T + 1e-10).mean(axis=0)
    f0s = []
    lo, hi = int(sr / 400), int(sr / 70)
    for fr in voiced[:: max(1, len(voiced) // 60)]:
        ac = np.correlate(fr, fr, "full")[len(fr) - 1:]
        if ac[0] > 0 and hi < len(ac):
            lag = lo + int(np.argmax(ac[lo:hi]))
            if ac[lag] / ac[0] > 0.3:
                f0s.append(sr / lag)
    return {"mel": mel - mel.mean(), "f0": float(np.median(f0s)) if f0s else 0.0}


def distance(a: dict, b: dict) -> tuple:
    return float(np.mean(np.abs(a["mel"] - b["mel"]))), abs(a["f0"] - b["f0"])


def too_similar(a: dict, b: dict, mel_db: float = 1.5, f0_hz: float = 15.0) -> bool:
    d, df = distance(a, b)
    return d < mel_db and df < f0_hz


def recipe(p: dict) -> tuple:
    return (p.get("engine"), p.get("voice"), p.get("seed"), round(float(p.get("pitch_semitones", 0)), 1))


def profiles_ok(cfg_chars: dict, script_characters: dict) -> dict:
    allowed = set(cfg_chars.get("allowed_engines", []))
    prof = cfg_chars.get("characters", {})
    narrator = cfg_chars.get("narrator", {})
    problems = []
    for cid in script_characters:
        if cid not in prof:
            problems.append(f"no locked voice profile for '{cid}' in config/characters.yaml")
    recs = {"narrator": recipe(narrator), **{cid: recipe(prof[cid]) for cid in script_characters if cid in prof}}
    for cid, p in [("narrator", narrator)] + [(c, prof[c]) for c in script_characters if c in prof]:
        if p.get("engine") not in allowed:
            problems.append(f"{cid}: engine '{p.get('engine')}' not allowed (use chatterbox, kokoro or the owner's recording)")
    seen = {}
    for k, r in recs.items():
        if r in seen:
            problems.append(f"{k} and {seen[r]} share the same voice recipe")
        seen[r] = k
    return {"ok": not problems, "problems": problems, "recipes": {k: list(v) for k, v in recs.items()}}

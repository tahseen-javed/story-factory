"""ITU-R BS.1770-4 / EBU R128 loudness in numpy (48 kHz): momentary, short-term, integrated, LRA, true peak.

Stems are measured as they sit in the stereo mix: a mono stem is treated as two identical channels (+3 dB).
"""
from __future__ import annotations

import numpy as np
from scipy import signal

SR = 48000
_B1 = [1.53512485958697, -2.69169618940638, 1.19839281085285]
_A1 = [1.0, -1.69065929318241, 0.73248077421585]
_B2 = [1.0, -2.0, 1.0]
_A2 = [1.0, -1.99004745483398, 0.99007225036621]
FLOOR = -120.0


def as_channels(x: np.ndarray, stereo: bool = True) -> np.ndarray:
    x = np.asarray(x, dtype="float64")
    if x.ndim == 1:
        x = x[None, :]
    if x.shape[0] == 1 and stereo:
        x = np.vstack([x, x])
    return x


def kweight(x: np.ndarray) -> np.ndarray:
    return signal.lfilter(_B2, _A2, signal.lfilter(_B1, _A1, x, axis=-1), axis=-1)


def _block_ms(xk: np.ndarray, win: int, hop: int) -> np.ndarray:
    """Per-block sum over channels of mean-square, shape (n_blocks,)."""
    n = xk.shape[-1]
    if n < win:
        return np.zeros(0)
    cs = np.concatenate([np.zeros((xk.shape[0], 1)), np.cumsum(xk ** 2, axis=-1)], axis=-1)
    starts = np.arange(0, n - win + 1, hop)
    return ((cs[:, starts + win] - cs[:, starts]) / win).sum(axis=0)


def to_lufs(ms: np.ndarray) -> np.ndarray:
    return np.maximum(-0.691 + 10 * np.log10(np.maximum(ms, 1e-14)), FLOOR)


def series(x: np.ndarray, win_s: float, hop_s: float, stereo: bool = True):
    """Loudness (LUFS) per block and the block start times in seconds."""
    xk = kweight(as_channels(x, stereo))
    win, hop = int(win_s * SR), int(hop_s * SR)
    ms = _block_ms(xk, win, hop)
    return to_lufs(ms), (np.arange(len(ms)) * hop) / SR


def momentary(x, hop_s: float = 0.1, stereo: bool = True):
    return series(x, 0.4, hop_s, stereo)


def short_term(x, hop_s: float = 0.5, stereo: bool = True):
    return series(x, 3.0, hop_s, stereo)


def integrated(x, stereo: bool = True) -> float:
    xk = kweight(as_channels(x, stereo))
    ms = _block_ms(xk, int(0.4 * SR), int(0.1 * SR))
    if not len(ms):
        return FLOOR
    l = to_lufs(ms)
    ms1 = ms[l > -70]
    if not len(ms1):
        return FLOOR
    rel = to_lufs(np.array([ms1.mean()]))[0] - 10
    ms2 = ms1[to_lufs(ms1) > rel]
    return float(to_lufs(np.array([ms2.mean()]))[0]) if len(ms2) else FLOOR


def lra(x, stereo: bool = True) -> float:
    l, _ = series(x, 3.0, 0.1, stereo)
    l = l[l > -70]
    if len(l) < 5:
        return 0.0
    mean_e = 10 * np.log10(np.mean(10 ** (l / 10)))
    l = l[l > mean_e - 20]
    return float(np.percentile(l, 95) - np.percentile(l, 10)) if len(l) > 3 else 0.0


def true_peak_db(x) -> float:
    x = np.asarray(x, dtype="float64")
    x = x if x.ndim > 1 else x[None, :]
    up = signal.resample_poly(x, 4, 1, axis=-1)
    return float(20 * np.log10(max(np.abs(up).max(), 1e-9)))


def rms_envelope(x: np.ndarray, hop_s: float = 0.01, win_s: float = 0.02):
    """dBFS RMS envelope of a mono/stereo signal at hop_s resolution."""
    x = np.asarray(x, dtype="float64")
    m = x.mean(axis=0) if x.ndim > 1 else x
    hop, win = int(hop_s * SR), int(win_s * SR)
    n = (len(m) - win) // hop + 1
    if n <= 0:
        return np.zeros(0), np.zeros(0)
    cs = np.concatenate([[0.0], np.cumsum(m ** 2)])
    idx = np.arange(n) * hop
    ms = (cs[idx + win] - cs[idx]) / win
    return 10 * np.log10(np.maximum(ms, 1e-14)), idx / SR

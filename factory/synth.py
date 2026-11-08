"""Original, procedurally synthesised music beds and sound effects (placeholder library, no third-party material).

numpy + scipy only. Everything is deterministic from (name, seed). 48 kHz. SFX are mono; music is stereo.
Replace with the owner's licensed library any time (docs/SETUP_MUSIC.md): library/music.json / sfx.json take precedence.
"""
from __future__ import annotations

import numpy as np
from scipy import signal

SR = 48000


def _rng(*key):
    import zlib
    return np.random.default_rng(zlib.crc32("|".join(map(str, key)).encode()))


def t_axis(sec):
    return np.arange(int(sec * SR)) / SR


def adsr(n, a=0.01, d=0.1, s=0.7, r=0.2):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    a, d, r = min(a, n), min(d, max(0, n - a)), min(r, n)
    env = np.ones(n) * s
    if a:
        env[:a] = np.linspace(0, 1, a)
    if d:
        env[a:a + d] = np.linspace(1, s, d)
    if r:
        env[n - r:] *= np.linspace(1, 0, r)
    return env


def lp(x, cutoff, order=2):
    b, a = signal.butter(order, min(cutoff, SR * 0.45) / (SR / 2), "low")
    return signal.lfilter(b, a, x)


def hp(x, cutoff, order=2):
    b, a = signal.butter(order, cutoff / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), min(hi, SR * 0.45) / (SR / 2)], "band")
    return signal.lfilter(b, a, x)


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) + 1e-9
    return x * (peak / m)


def reverb(x, t60=2.0, wet=0.25, seed=1, predelay=0.02):
    """Synthetic exponential-decay noise IR. x: (n,) or (2,n)."""
    rng = _rng("ir", seed)
    n = int(t60 * SR)
    t = np.arange(n) / SR
    outs = []
    chans = x if x.ndim == 2 else x[None]
    for c in range(chans.shape[0]):
        ir = rng.normal(0, 1, n) * np.exp(-6.9 * t / t60)
        ir = lp(ir, 5500, 1)
        ir[: int(predelay * SR)] = 0
        ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
        outs.append(signal.oaconvolve(chans[c], ir)[: chans.shape[1]])
    wetsig = np.array(outs)
    res = (1 - wet) * chans + wet * wetsig
    return res if x.ndim == 2 else res[0]


# ------------------------------------------------------------------ music
SCALES = {"minor": [0, 2, 3, 5, 7, 8, 10], "phrygian": [0, 1, 3, 5, 7, 8, 10], "major": [0, 2, 4, 5, 7, 9, 11], "dorian": [0, 2, 3, 5, 7, 9, 10]}

MOOD = {
    "tense": dict(root=65.41, scale="phrygian", tempo=74, prog=[0, 0, 5, 4], cut=900, lead="arp", pulse="heart", level=1.0),
    "dread": dict(root=55.0, scale="minor", tempo=56, prog=[0, 5, 3, 4], cut=650, lead="sparse", pulse="heart", level=1.0),
    "urgent": dict(root=73.42, scale="minor", tempo=112, prog=[0, 3, 5, 4], cut=1500, lead="arp", pulse="drive", level=1.0),
    "climax": dict(root=61.74, scale="minor", tempo=100, prog=[0, 5, 3, 6], cut=1900, lead="arp", pulse="drive", level=1.1),
    "hopeful": dict(root=87.31, scale="major", tempo=80, prog=[0, 4, 5, 3], cut=1800, lead="pluck", pulse="none", level=0.95),
    "sorrow": dict(root=65.41, scale="minor", tempo=60, prog=[0, 5, 2, 4], cut=800, lead="sparse", pulse="none", level=0.9),
    "calm": dict(root=98.0, scale="dorian", tempo=66, prog=[0, 3, 4, 0], cut=1200, lead="pluck", pulse="none", level=0.85),
    "mystery": dict(root=82.41, scale="phrygian", tempo=64, prog=[0, 1, 5, 0], cut=1100, lead="sparse", pulse="tick", level=0.95),
}


def _note(root, scale, degree, octave=0):
    sc = SCALES[scale]
    idx = degree % 7
    oct_up = degree // 7
    return root * (2 ** ((sc[idx] + 12 * (oct_up + octave)) / 12))


def _pad(freq, n, rng, bright=1.0):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for det in (-0.006, 0.0, 0.007):
        f = freq * (1 + det)
        ph = rng.uniform(0, 2 * np.pi)
        for h in range(1, 9):
            out += np.sin(2 * np.pi * f * h * t + ph * h) / (h ** (1.3 / bright))
    return out


def render_music(mood: str, seconds: float, seed: int = 0) -> np.ndarray:
    m = MOOD.get(mood, MOOD["tense"])
    rng = _rng("music", mood, seed)
    n = int(seconds * SR)
    beat = 60.0 / m["tempo"]
    bar = beat * 4
    nbar = int(np.ceil(seconds / bar)) + 1
    L = np.zeros(n + int(bar * SR) * 4)
    R = np.zeros_like(L)
    bn = int(bar * SR)
    for b in range(nbar):
        deg = m["prog"][b % len(m["prog"])]
        s0 = b * bn
        notes = [_note(m["root"] * 2, m["scale"], deg + k) for k in (0, 2, 4)]
        pad_n = bn + int(0.9 * SR)
        env = adsr(pad_n, a=bar * 0.38, d=0.2, s=0.8, r=0.9)
        for k, f in enumerate(notes):
            v = _pad(f, pad_n, rng, bright=m["level"]) * env
            pan = [0.35, 0.5, 0.65][k]
            L[s0:s0 + pad_n] += v * (1 - pan) * 0.9
            R[s0:s0 + pad_n] += v * pan * 0.9
        sub = np.sin(2 * np.pi * _note(m["root"], m["scale"], deg) * np.arange(pad_n) / SR) * adsr(pad_n, 0.25, 0.2, 0.85, 0.7) * 1.4
        L[s0:s0 + pad_n] += sub
        R[s0:s0 + pad_n] += sub
        # lead layer
        if m["lead"] == "arp":
            step = beat / 2
            for k in range(8):
                f = _note(m["root"] * 4, m["scale"], deg + [0, 2, 4, 2, 4, 6, 4, 2][k])
                ln = int(step * 0.9 * SR)
                tt = np.arange(ln) / SR
                note = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * 2 * f * tt)) * np.exp(-tt * 6) * 0.22
                p = s0 + int(k * step * SR)
                pan = 0.3 + 0.4 * ((k % 4) / 3)
                L[p:p + ln] += note * (1 - pan)
                R[p:p + ln] += note * pan
        elif m["lead"] in ("sparse", "pluck"):
            count = 2 if m["lead"] == "sparse" else 4
            for k in range(count):
                if m["lead"] == "sparse" and rng.random() < 0.35:
                    continue
                f = _note(m["root"] * 4, m["scale"], deg + int(rng.integers(0, 7)))
                ln = int(beat * 2.2 * SR)
                tt = np.arange(ln) / SR
                note = (np.sin(2 * np.pi * f * tt) + 0.2 * np.sin(2 * np.pi * 3 * f * tt)) * np.exp(-tt * 2.2) * 0.26
                p = s0 + int((k * (4 / count) * beat + (0.0 if m["lead"] == "pluck" else rng.uniform(0, beat))) * SR)
                pan = rng.uniform(0.25, 0.75)
                seg = note[: len(L) - p]
                L[p:p + len(seg)] += seg * (1 - pan)
                R[p:p + len(seg)] += seg * pan
        # pulse layer
        if m["pulse"] in ("heart", "drive"):
            hits = [0, 0.5] if m["pulse"] == "heart" else [0, 1, 2, 3]
            for h in hits:
                ln = int(0.32 * SR)
                tt = np.arange(ln) / SR
                kick = np.sin(2 * np.pi * (46 + 70 * np.exp(-tt * 28)) * tt) * np.exp(-tt * 9) * (0.9 if h == 0 else 0.6)
                p = s0 + int(h * beat * SR)
                L[p:p + ln] += kick
                R[p:p + ln] += kick
            if m["pulse"] == "drive":
                for k in range(16):
                    ln = int(0.05 * SR)
                    hat = hp(rng.normal(0, 1, ln), 7000) * np.exp(-np.arange(ln) / SR * 90) * 0.12
                    p = s0 + int(k * beat / 4 * SR)
                    L[p:p + ln] += hat
                    R[p:p + ln] += hat
        elif m["pulse"] == "tick":
            for k in range(4):
                ln = int(0.03 * SR)
                tk = hp(rng.normal(0, 1, ln), 3000) * np.exp(-np.arange(ln) / SR * 160) * 0.25
                p = s0 + int(k * beat * SR)
                L[p:p + ln] += tk
                R[p:p + ln] += tk
    out = np.vstack([L[:n], R[:n]])
    out[0] = lp(out[0], m["cut"], 2)
    out[1] = lp(out[1], m["cut"], 2)
    wind = lp(rng.normal(0, 1, n), 380, 2) * 0.05
    out += wind
    out = reverb(out, t60=2.4, wet=0.32, seed=hash(mood) % 1000 if False else 7)
    out = hp(out, 28, 1)
    fade = int(min(1.2, seconds / 4) * SR)
    out[:, :fade] *= np.linspace(0, 1, fade)
    out[:, -fade:] *= np.linspace(1, 0, fade)
    rms = np.sqrt(np.mean(out ** 2)) + 1e-9
    return (out / rms * 10 ** (-20 / 20)).astype("float32")


# ------------------------------------------------------------------ sfx
def _noise(sec, seed):
    return _rng("noise", seed).normal(0, 1, int(sec * SR))


def sfx(name: str, seed: int = 0) -> np.ndarray:
    r = _rng("sfx", name, seed)
    if name == "alert_siren":
        t = t_axis(2.0)
        f = np.where((t * 2.2).astype(int) % 2 == 0, 960, 770)
        ph = 2 * np.pi * np.cumsum(f) / SR
        x = np.sign(np.sin(ph)) * 0.5 + np.sin(ph) * 0.5
        x = bp(x, 500, 4500) * adsr(len(t), 0.02, 0.05, 0.9, 0.2)
        return reverb(x, 0.7, 0.2) * 0.8
    if name == "phone_buzz":
        t = t_axis(1.2)
        gate = (np.sin(2 * np.pi * 3.3 * t) > 0).astype(float)
        x = (np.sin(2 * np.pi * 160 * t) + 0.4 * np.sin(2 * np.pi * 320 * t)) * gate
        return lp(x, 1500) * 0.7
    if name == "door_knock":
        out = np.zeros(int(1.4 * SR))
        for k, off in enumerate((0.0, 0.32, 0.62)):
            n = int(0.18 * SR)
            tt = np.arange(n) / SR
            body = np.sin(2 * np.pi * (120 - 30 * tt / 0.18) * tt) * np.exp(-tt * 28)
            click = lp(hp(r.normal(0, 1, n), 600), 3500) * np.exp(-tt * 70) * 0.5
            p = int(off * SR)
            out[p:p + n] += (body + click) * 0.9
        return reverb(out, 0.5, 0.15)
    if name == "door_creak":
        t = t_axis(1.6)
        f = 180 + 120 * np.sin(2 * np.pi * 0.9 * t) + 60 * t
        ph = 2 * np.pi * np.cumsum(f) / SR
        x = (np.sin(ph) + 0.5 * np.sin(2.01 * ph)) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t))
        x = bp(x, 300, 2200) * np.sin(np.pi * t / 1.6) ** 0.6
        return x * 0.5
    if name == "footsteps":
        out = np.zeros(int(2.4 * SR))
        for k in range(6):
            n = int(0.16 * SR)
            tt = np.arange(n) / SR
            s = (np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 35) + lp(r.normal(0, 1, n), 900) * np.exp(-tt * 40) * 0.5)
            p = int((0.1 + k * 0.38) * SR)
            out[p:p + n] += s * (0.85 if k % 2 else 1.0)
        return out * 0.8
    if name == "whoosh":
        n = int(0.9 * SR)
        x = r.normal(0, 1, n)
        t = np.arange(n) / SR
        out = np.zeros(n)
        for seg in range(12):
            c = 300 + 3200 * np.sin(np.pi * (seg + 0.5) / 12) ** 2
            part = bp(x, c * 0.7, c * 1.3)
            w = np.zeros(n)
            lo, hi = int(seg * n / 12), int((seg + 1.6) * n / 12)
            w[lo:hi] = np.hanning(len(w[lo:hi]))
            out += part * w
        return norm(out, 0.55) * np.sin(np.pi * t / 0.9) ** 0.7
    if name == "paper_slide":
        n = int(0.5 * SR)
        x = bp(r.normal(0, 1, n), 1800, 7000) * np.sin(np.pi * np.arange(n) / n) ** 1.5
        return norm(x, 0.4)
    if name == "stinger_chapter":
        n = int(2.6 * SR)
        t = np.arange(n) / SR
        boom = np.sin(2 * np.pi * (52 + 40 * np.exp(-t * 4)) * t) * np.exp(-t * 1.8)
        hit = (np.sin(2 * np.pi * 220 * t) + np.sin(2 * np.pi * 311 * t) * 0.8 + np.sin(2 * np.pi * 466 * t) * 0.5) * np.exp(-t * 3.0) * 0.3
        swell = lp(r.normal(0, 1, n), 1500) * (t / 2.6) ** 3 * 0.08
        x = reverb(boom + hit + swell, 2.2, 0.3)
        return norm(x, 0.8)
    if name == "heartbeat":
        out = np.zeros(int(3.4 * SR))
        for k in range(4):
            for off in (0.0, 0.26):
                n = int(0.3 * SR)
                tt = np.arange(n) / SR
                p = int((k * 0.85 + off) * SR)
                out[p:p + n] += np.sin(2 * np.pi * (58 + 40 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 12) * (1.0 if off == 0 else 0.7)
        return out * 0.9
    if name == "power_down":
        n = int(2.2 * SR)
        t = np.arange(n) / SR
        f = 320 * np.exp(-t * 1.9)
        ph = 2 * np.pi * np.cumsum(f) / SR
        x = (np.sin(ph) + 0.4 * np.sign(np.sin(ph))) * np.exp(-t * 1.2)
        x += lp(r.normal(0, 1, n), 800) * np.exp(-t * 2.5) * 0.4
        return reverb(lp(x, 1800), 1.2, 0.25) * 0.8
    if name == "radio_static":
        n = int(2.4 * SR)
        x = bp(r.normal(0, 1, n), 900, 5200)
        gate = (lp(r.normal(0, 1, n), 14) > -0.2).astype(float)
        crack = (r.random(n) > 0.9995).astype(float)
        x = x * (0.25 + 0.75 * gate) + lp(hp(crack * r.normal(0, 3, n), 1200), 6000)
        return norm(x, 0.45)
    if name == "glass_crack":
        n = int(0.8 * SR)
        t = np.arange(n) / SR
        x = hp(r.normal(0, 1, n), 2500) * np.exp(-t * 28)
        for k in range(14):
            p = int(r.uniform(0.02, 0.5) * SR)
            m = int(0.02 * SR)
            x[p:p + m] += hp(r.normal(0, 1, m), 3500) * np.exp(-np.arange(m) / SR * 150) * 0.6
        return norm(x, 0.6)
    if name == "water_pour":
        n = int(2.0 * SR)
        t = np.arange(n) / SR
        x = bp(r.normal(0, 1, n), 700, 3800)
        x *= 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * (9 + 6 * t) * t))
        return norm(x, 0.5) * adsr(n, 0.15, 0.2, 0.8, 0.4)
    if name == "car_engine":
        n = int(3.0 * SR)
        t = np.arange(n) / SR
        f = 48 + 8 * np.sin(2 * np.pi * 0.5 * t)
        ph = 2 * np.pi * np.cumsum(f) / SR
        x = (np.sign(np.sin(ph)) * 0.3 + np.sin(ph) + 0.5 * np.sin(2 * ph)) * (0.7 + 0.3 * np.sin(2 * np.pi * 24 * t))
        return lp(x, 650) * 0.5 * adsr(n, 0.4, 0.2, 0.9, 0.8)
    if name == "crowd_murmur":
        n = int(3.2 * SR)
        x = bp(r.normal(0, 1, n), 200, 1800)
        for f0 in (4.0, 6.5, 9.0):
            x *= 0.65 + 0.35 * np.abs(np.sin(2 * np.pi * f0 * t_axis(3.2) + r.uniform(0, 6)))
        return norm(x, 0.35) * adsr(n, 0.5, 0.2, 0.9, 0.9)
    if name == "thunder":
        n = int(3.5 * SR)
        t = np.arange(n) / SR
        x = lp(r.normal(0, 1, n), 220) * np.exp(-t * 1.1) * (1 + 0.6 * np.sin(2 * np.pi * 3 * t))
        return norm(reverb(x, 2.0, 0.3), 0.85)
    if name == "click":
        n = int(0.06 * SR)
        tt = np.arange(n) / SR
        return (hp(r.normal(0, 1, n), 1500) * np.exp(-tt * 140) * 0.8 + np.sin(2 * np.pi * 1800 * tt) * np.exp(-tt * 160) * 0.4)
    if name == "beep":
        n = int(0.16 * SR)
        tt = np.arange(n) / SR
        return np.sin(2 * np.pi * 1000 * tt) * adsr(n, 0.005, 0.02, 0.9, 0.03) * 0.5
    if name == "typing":
        out = np.zeros(int(1.6 * SR))
        for k in range(14):
            n = int(0.03 * SR)
            p = int((0.05 + k * 0.1 + r.uniform(-0.02, 0.02)) * SR)
            out[p:p + n] += hp(r.normal(0, 1, n), 1200) * np.exp(-np.arange(n) / SR * 120) * 0.5
        return out
    if name == "rustle":
        n = int(1.0 * SR)
        x = hp(r.normal(0, 1, n), 2200) * (r.random(n) > 0.55) * np.sin(np.pi * np.arange(n) / n)
        return norm(lp(x, 8000), 0.3)
    if name == "ticking_clock":
        out = np.zeros(int(3.0 * SR))
        for k in range(6):
            n = int(0.04 * SR)
            tt = np.arange(n) / SR
            p = int(k * 0.5 * SR)
            out[p:p + n] += (np.sin(2 * np.pi * (1500 if k % 2 else 1250) * tt) * np.exp(-tt * 110)) * 0.45
        return out
    if name == "spark":
        n = int(0.7 * SR)
        x = np.zeros(n)
        for k in range(18):
            m = int(0.012 * SR)
            p = int(r.uniform(0, 0.6) * SR)
            x[p:p + m] += hp(r.normal(0, 1, m), 3000) * np.exp(-np.arange(m) / SR * 200) * r.uniform(0.3, 1)
        return norm(x, 0.55)
    if name == "wind":
        n = int(3.4 * SR)
        t = np.arange(n) / SR
        x = bp(r.normal(0, 1, n), 200, 1100) * (0.55 + 0.45 * np.sin(2 * np.pi * 0.37 * t + 1))
        return norm(x, 0.3) * adsr(n, 0.8, 0.2, 0.9, 1.0)
    if name == "riser":
        T = 1.4
        t = t_axis(T)
        f = 200 + 1600 * (t / T) ** 2
        x = 0.4 * np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.6 * hp(_noise(T, seed + 5), 1500) * (t / T) ** 2
        return x * (t / T) ** 1.5 * np.minimum(1, (T - t) / 0.015) * 0.8
    if name == "impact":
        t = t_axis(1.6)
        x = np.sin(2 * np.pi * 55 * t) * np.exp(-t * 3.5) + 0.5 * lp(_noise(1.6, seed + 6), 900) * np.exp(-t * 9)
        return reverb(x, 0.9, 0.2) * 0.9
    if name == "glitch":
        n = int(0.35 * SR)
        gate = np.repeat((r.random(max(1, n // int(0.03 * SR) + 1)) > 0.4).astype(float), int(0.03 * SR))[:n]
        return bp(_noise(0.35, seed + 7), 1500, 6000) * gate[: n] * 0.6
    if name == "text_pop":
        t = t_axis(0.12)
        return np.sin(2 * np.pi * 900 * t) * np.exp(-t * 40) * 0.7
    # unknown name: tiny click so the mix never fails
    return sfx("click", seed)


# default relative loudness of each sfx in the final mix (dB re -14 dBFS peak)
SFX_GAIN = {"alert_siren": -9, "phone_buzz": -8, "door_knock": -6, "door_creak": -10, "footsteps": -9, "whoosh": -8, "paper_slide": -10,
            "stinger_chapter": -5, "heartbeat": -7, "power_down": -5, "radio_static": -12, "glass_crack": -8, "water_pour": -13,
            "car_engine": -15, "crowd_murmur": -17, "thunder": -9, "click": -12, "beep": -13, "typing": -15, "rustle": -17,
            "ticking_clock": -15, "spark": -11, "wind": -19, "riser": -9, "impact": -6, "glitch": -12, "text_pop": -13}


def ambience(kind: str, sec: float, seed: int = 0) -> np.ndarray:
    """Mono ambience bed, rms-normalised to ~0.1 (the mixer scales it). kinds: room, city, wind, hum_dark."""
    n = int(sec * SR)
    t = np.arange(n) / SR
    nz = _noise(sec, seed + 11)
    if kind == "wind":
        x = bp(nz, 120, 700) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * t + seed))
    elif kind == "city":
        x = bp(nz, 100, 900) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.07 * t)) + 0.15 * np.sin(2 * np.pi * 60 * t)
    elif kind == "sea":
        x = lp(nz, 520) * (0.55 + 0.45 * np.sin(2 * np.pi * 0.11 * t)) + 0.18 * bp(_noise(sec, seed + 31), 1200, 4200) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * t + 1.3)) ** 2
    elif kind == "engine":
        x = 0.7 * np.sin(2 * np.pi * 48 * t) + 0.4 * np.sin(2 * np.pi * 96 * t) + 0.25 * np.sin(2 * np.pi * 144 * t) + 0.3 * lp(nz, 220)
    elif kind == "crowd":
        x = bp(nz, 300, 1800) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.4 * t))
    elif kind == "hum_dark":
        x = 0.5 * np.sin(2 * np.pi * 60 * t) + 0.25 * np.sin(2 * np.pi * 120 * t) + 0.4 * lp(nz, 120)
    else:
        x = lp(nz, 220) + 0.2 * np.sin(2 * np.pi * 50 * t)
    return (x / (np.sqrt(np.mean(x ** 2)) + 1e-9) * 0.1).astype("float32")

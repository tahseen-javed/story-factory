"""Synthetic clean fixture (60 s) and deliberate defects for the Video Doctor acceptance and mutation tests. numpy only."""
from __future__ import annotations

import numpy as np
from scipy import signal
from scipy.ndimage import uniform_filter1d

from . import lufs

SR = lufs.SR


def _speech(n, rng, seed_phase=0.0):
    t = np.arange(n) / SR
    x = rng.normal(0, 1, n)
    b, a = signal.butter(2, [180 / (SR / 2), 3600 / (SR / 2)], "band")
    x = signal.lfilter(b, a, x)
    return x * (0.45 + 0.55 * np.sin(2 * np.pi * 3.6 * t + seed_phase) ** 2)


def clean(seconds=60.0, seed=1):
    """Return dict(stems, master, plan, timeline) that passes every audio check."""
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    voice = np.zeros(n)
    sentences, t, idx = [], 1.0, 0
    while t + 2.6 < seconds - 3:
        dur = float(rng.uniform(2.0, 2.8))
        seg = _speech(int(dur * SR), rng, idx)
        seg *= np.hanning(len(seg)) ** 0.15
        voice[int(t * SR): int(t * SR) + len(seg)] += seg
        sentences.append({"id": f"s{idx:03d}", "idx": idx, "start": round(t, 3), "end": round(t + dur, 3), "words": int(dur * 2.45), "text": "x", "parallel": False})
        t += dur + 0.35
        idx += 1
    # one planned silence beat of 1.2 s before the last third
    beat_at = sentences[len(sentences) * 2 // 3]["start"]
    plan = {"sentences": sentences, "silence": [[beat_at - 1.3, beat_at - 0.1]]}
    # remove the voice that overlaps the beat window (there is a natural gap only if we shift: simply mute it)
    voice[int((beat_at - 1.3) * SR): int((beat_at - 0.1) * SR)] = 0.0
    sentences[:] = [s for s in sentences if not (s["start"] < beat_at - 0.1 and s["end"] > beat_at - 1.3)]
    # scale the voice so that its short-term loudness while speaking sits at -14.5 LUFS
    cur = lufs.integrated(voice)
    voice *= 10 ** ((-14.5 - cur) / 20)
    # music: slow pad, ducked smoothly 4 dB under speech, 20 dB under the voice
    tt = np.arange(n) / SR
    music = sum(np.sin(2 * np.pi * f * tt + k) * a for k, (f, a) in enumerate([(110, 1.0), (165, 0.6), (220, 0.5), (277, 0.25)]))
    music *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.05 * tt)
    speaking = np.zeros(n)
    for s in sentences:
        speaking[int(s["start"] * SR): int(s["end"] * SR)] = 1.0
    k = int(0.4 * SR)
    sm = uniform_filter1d(speaking, size=k, mode="nearest")
    music *= 10 ** ((-4.0 * sm) / 20)
    music[int((beat_at - 1.3) * SR): int((beat_at - 0.1) * SR)] *= 0.05
    cur = lufs.short_term(music)[0]
    sp_idx = [i for i, c in enumerate(lufs.short_term(voice)[1] + 1.5) if any(s["start"] < c < s["end"] for s in sentences)]
    vst = np.median(lufs.short_term(voice)[0][sp_idx])
    mst = np.median(cur[sp_idx])
    music *= 10 ** ((vst - 20 - mst) / 20)
    sfx = np.zeros(n)
    for s in sentences[::5]:
        i = int((s["end"] + 0.1) * SR)
        sfx[i: i + 2400] += 0.01 * rng.normal(0, 1, 2400) * np.hanning(2400)
    amb = 0.0008 * rng.normal(0, 1, n)
    fade = np.ones(n)
    fade[: int(0.5 * SR)] = np.linspace(0, 1, int(0.5 * SR))
    fade[-int(1.5 * SR):] = np.linspace(1, 0, int(1.5 * SR))
    stems = {"voice": voice * fade, "music": music * fade, "sfx": sfx * fade, "amb": amb * fade}
    master = np.vstack([sum(stems.values()), sum(stems.values())])
    return {"stems": stems, "master": master, "plan": plan, "seconds": seconds}


def mutate(fx, kind):
    """Return a deep-ish copy of the fixture with one deliberate defect."""
    st = {k: v.copy() for k, v in fx["stems"].items()}
    plan = {"sentences": [dict(s) for s in fx["plan"]["sentences"]], "silence": [list(w) for w in fx["plan"]["silence"]]}
    n = len(st["voice"])
    if kind == "music_too_loud":
        st["music"] *= 10 ** (8 / 20)
    elif kind == "music_drops_to_silence":
        i = int((25.0 if fx["seconds"] >= 60 else fx["seconds"] * 0.25) * SR)
        st["music"][i: i + int(2.5 * SR)] = 0.0
    elif kind == "music_pumping":
        t = np.arange(n) / SR
        st["music"] *= 10 ** ((6.0 * np.sign(np.sin(2 * np.pi * 1.2 * t))) / 20)
    elif kind == "voice_gap":
        # cut 3 s of voice out of the middle of speech and shift nothing: leaves a 3 s hole between sentences
        s = plan["sentences"][len(plan["sentences"]) // 3]
        a, b = int(s["start"] * SR), int((s["end"] + 3.0) * SR)
        st["voice"][a:b] = 0.0
        plan["sentences"] = [x for x in plan["sentences"] if not (x["start"] >= s["start"] and x["start"] < s["end"] + 3.0)]
        plan["sentences"].append(dict(s, start=s["start"] - 4.0, end=s["start"] - 3.0))
    elif kind == "music_above_voice":
        st["music"] *= 10 ** (24 / 20)
    elif kind == "clipping":
        st["voice"] = np.clip(st["voice"] * 40, -1, 1)
    elif kind == "hot_start":
        pass
    master = np.vstack([sum(st.values()), sum(st.values())])
    if kind == "hot_start":
        master[:, : int(0.2 * SR)] += 0.3
    if kind == "dc_offset":
        master = master + 0.02
    return {"stems": st, "master": master, "plan": plan, "seconds": fx["seconds"]}


EXPECTED = {
    "music_too_loud": "A3-MUSIC-LOUD",
    "music_drops_to_silence": "A3-MUSIC-DROPOUT",
    "music_pumping": "A3-MUSIC-JUMP",
    "voice_gap": "A1-GAP",
    "music_above_voice": "A3-MUSIC-ABOVE",
    "clipping": "A4-CLIP",
    "hot_start": "A4-HOTSTART",
    "dc_offset": "A4-DC",
}

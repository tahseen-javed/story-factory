"""Audio engine: voice chain + per-chapter music + SFX + ducking -> premaster -> two-pass loudnorm (-14 LUFS, TP <= -1 dBTP).

numpy/scipy for the mix, ffmpeg for loudnorm and measurement. Output: master.wav (48 kHz stereo) and mix_report.json.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys
import wave

import numpy as np
from scipy import signal

from . import musiclib, synth
from .synth import SR


def xfade_ramps(n: int):
    """Equal-power crossfade ramps: fin**2 + fout**2 == 1, so two uncorrelated beds keep one level through the change (a linear fade dips 3 dB)."""
    x = np.linspace(0.0, np.pi / 2, n)
    return np.sin(x).astype("float32"), np.cos(x).astype("float32")


def read_wav(path: str):
    with wave.open(path, "rb") as w:
        n, ch, sw, fr = w.getnframes(), w.getnchannels(), w.getsampwidth(), w.getframerate()
        raw = w.readframes(n)
    a = np.frombuffer(raw, dtype="<i2").astype("float32") / 32768.0 if sw == 2 else np.frombuffer(raw, dtype="<i4").astype("float32") / 2147483648.0
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1)
    return a, fr


def db(x):
    return 20 * np.log10(np.maximum(x, 1e-9))


def biquad_peak(f0, gain_db, q):
    A = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / SR
    al = np.sin(w0) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w0), 1 - al * A]
    a = [1 + al / A, -2 * np.cos(w0), 1 - al / A]
    return np.array(b) / a[0], np.array(a) / a[0]


def compressor(x, thr_db=-22.0, ratio=3.0, attack=0.008, release=0.12, makeup_db=0.0, ctrl_rate=1000):
    """Feed-forward RMS-ish compressor evaluated at a control rate (fast, vectorised gain interpolation)."""
    hop = SR // ctrl_rate
    n = len(x)
    pad = (-n) % hop
    xp = np.pad(np.abs(x), (0, pad)).reshape(-1, hop)
    env = xp.max(axis=1)
    env_db = db(env)
    over = np.maximum(env_db - thr_db, 0)
    target = -over * (1 - 1 / ratio)
    g = np.zeros_like(target)
    a_att, a_rel = np.exp(-1 / (attack * ctrl_rate)), np.exp(-1 / (release * ctrl_rate))
    cur = 0.0
    for i, tg in enumerate(target):  # python loop over ~300k control points: fine
        coef = a_att if tg < cur else a_rel
        cur = coef * cur + (1 - coef) * tg
        g[i] = cur
    gain = 10 ** ((g + makeup_db) / 20)
    full = np.interp(np.arange(n), (np.arange(len(gain)) + 0.5) * hop, gain)
    return x * full


def voice_chain(v):
    b, a = signal.butter(2, 80 / (SR / 2), "high")
    v = signal.lfilter(b, a, v)
    for f0, g, q in ((250, -2.0, 1.0), (3200, 2.0, 0.9), (9500, 1.0, 0.7)):
        b, a = biquad_peak(f0, g, q)
        v = signal.lfilter(b, a, v)
    # de-esser: compress the 5-9 kHz band when it gets loud
    bb, ba = signal.butter(2, [5000 / (SR / 2), 9000 / (SR / 2)], "band")
    sib = signal.lfilter(bb, ba, v)
    sib_c = compressor(sib, thr_db=-34, ratio=4.0, attack=0.002, release=0.05)
    v = v - sib + sib_c
    v = compressor(v, thr_db=-22, ratio=3.0, attack=0.008, release=0.12, makeup_db=3.0)
    return v


def envelope(x, hop_s=0.01, attack=0.05, release=0.45):
    hop = int(hop_s * SR)
    n = len(x)
    pad = (-n) % hop
    rms = np.sqrt(np.mean(np.pad(x, (0, pad)).reshape(-1, hop) ** 2, axis=1))
    lvl = np.clip((db(rms) + 48) / 18.0, 0, 1)  # 0 at -48 dB, 1 at -30 dB
    out = np.zeros_like(lvl)
    a_att, a_rel = np.exp(-hop_s / attack), np.exp(-hop_s / release)
    cur = 0.0
    for i, v in enumerate(lvl):
        coef = a_att if v > cur else a_rel
        cur = coef * cur + (1 - coef) * v
        out[i] = cur
    return np.interp(np.arange(n), (np.arange(len(out)) + 0.5) * hop, out)


def ffmpeg_measure(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "loudnorm=I=-14:TP=-1.0:LRA=7:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    return json.loads(m.group(0))


def loudnorm_two_pass(src, dst, I=-14.0, TP=-2.4, LRA=7.0):
    m = ffmpeg_measure(src)
    flt = (f"loudnorm=I={I}:TP={TP}:LRA={LRA}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
           f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true:print_format=summary,alimiter=limit=0.74:level=disabled")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", src, "-af", flt, "-ar", "48000", "-c:a", "pcm_s24le", dst], check=True)
    return m


def run(audio_plan_path: str, voice_dir: str, out_dir: str, cfg_audio: dict, lufs: float = -14.0, music_dir: str | None = None):
    ap = json.load(open(audio_plan_path, encoding="utf-8"))
    os.makedirs(out_dir, exist_ok=True)
    mp = {}
    mpp = os.path.join(out_dir, "mix_params.json")
    if os.path.exists(mpp):   # P-012: parameters tuned by the Video Doctor fix loop
        mp = json.load(open(mpp, encoding="utf-8"))
    cfg_audio = {**cfg_audio, **{k: v for k, v in mp.items() if k in cfg_audio or k in ("duck_db",)}}
    total = int(ap["total_s"] * SR) + SR
    voice = np.zeros(total, dtype="float32")
    for seg in ap["voice"]:
        a, fr = read_wav(os.path.join(voice_dir, seg["file"]))
        if fr != SR:
            a = signal.resample_poly(a, SR, fr).astype("float32")
        p = int(seg["start"] * SR)
        if seg.get("room"):
            wet = float(cfg_audio.get("reverb_wet", {}).get(seg["room"], 0.08))
            a = synth.reverb(a.astype("float64"), 0.35 if seg["room"] == "indoor" else 0.9, wet, seed=3)[: len(a)].astype("float32")
        voice[p:p + len(a)] += a[: total - p]
    voice = voice_chain(voice).astype("float32")
    venv = envelope(voice)

    # ---- music per chapter, crossfaded ----
    music = np.zeros((2, total), dtype="float32")
    xf = int(float(cfg_audio.get("music_xfade_s", 4.0)) * SR)
    fin, fout = xfade_ramps(xf)
    for ci, ch in enumerate(ap["music"]):
        s0 = int(ch["start"] * SR)
        s1 = min(total, int(ch["end"] * SR) + xf)
        seg = musiclib.segment(os.environ.get("MUSIC_LIB_DIR", ""), ch["mood"], (s1 - s0) / SR, ci)
        if seg is None:
            seg = synth.render_music(ch["mood"], (s1 - s0) / SR, seed=ci)
        seg = seg * (0.1 / (float(np.sqrt(np.mean(seg.astype('float64') ** 2))) + 1e-9))   # same loudness for every mood, so the crossfade has no level step
        n = seg.shape[1]
        if ci > 0:
            seg[:, :xf] *= fin
        if ci < len(ap["music"]) - 1:
            seg[:, -xf:] *= fout
        music[:, s0:s0 + n] += seg[:, : total - s0]
    tail = int(6 * SR)
    end_p = int(ap["audio_end_s"] * SR)
    fade = np.ones(total)
    fade[end_p:end_p + tail] = np.linspace(1, 0.45, min(tail, total - end_p)) if end_p < total else 1
    fade[end_p + tail:] = 0.45
    fade[-int(2 * SR):] *= np.linspace(1, 0, int(2 * SR))
    sil = np.ones(total, dtype="float32")
    floor = 10 ** (float(cfg_audio.get("silence_floor_db", -30)) / 20.0)
    ramp = int(0.06 * SR)
    for w_ in ap.get("silence", []):
        a0, b0 = w_[0], w_[1]
        fl_ = 10 ** (float(w_[2]) / 20.0) if len(w_) > 2 else floor
        i0, i1 = int(a0 * SR), min(total, int(b0 * SR))
        sil[i0:i1] = fl_
        if i0 - ramp >= 0:
            sil[i0 - ramp:i0] = np.linspace(1, fl_, ramp)
        if i1 + ramp <= total:
            sil[i1:i1 + ramp] = np.linspace(fl_, 1, ramp)
    hold_g = np.ones(total, dtype="float32")   # decision hold: the bed stays pinned (no rise, no swell) while the room tone and heartbeat carry the scene
    hg = 10 ** (-float(cfg_audio.get("hold_music_db", 6.0)) / 20.0)
    r2 = int(float(cfg_audio.get("hold_release_s", 1.2)) * SR)   # gentle entry and release of the decision hold
    for w_ in ap.get("holds", []):
        i0, i1 = int(w_[0] * SR), min(total, int(w_[1] * SR))
        hold_g[i0:i1] = hg
        if i0 - r2 >= 0:
            hold_g[i0 - r2:i0] = np.linspace(1, hg, r2)
        if i1 + r2 <= total:
            hold_g[i1:i1 + r2] = np.linspace(hg, 1, r2)
    amb = np.zeros(total, dtype="float32")
    for k, seg in enumerate(ap.get("ambience", [])):
        i0, i1 = int(seg["start"] * SR), min(total, int(seg["end"] * SR) + int(0.5 * SR))
        x = synth.ambience(seg["kind"], (i1 - i0) / SR, seed=k)
        fi = min(len(x) // 2, int(0.5 * SR))
        x[:fi] *= np.linspace(0, 1, fi)
        x[-fi:] *= np.linspace(1, 0, fi)
        amb[i0:i0 + len(x)] += x[: total - i0]
    amb *= 0.25   # ambience bed about -32 dBFS rms
    music_gain_db = np.zeros(total, dtype="float32")
    for seg in ap["music"]:
        music_gain_db[int(seg["start"] * SR):int(seg["end"] * SR)] = float(seg.get("db", 0.0))
    k_sm = int(3.0 * SR)
    cs = np.cumsum(np.pad(music_gain_db, (k_sm // 2, k_sm // 2), mode="edge"))
    intensity_db = ((cs[k_sm:] - cs[:-k_sm]) / k_sm)[:total].astype("float32")
    duck_db = float(cfg_audio.get("duck_db", 6))
    smooth_s = float(mp.get("venv_smooth_s", 0.0))
    if smooth_s > 0:   # extra smoothing of the ducking envelope (fix for pumping / jumps)
        k_ = max(1, int(smooth_s * SR))
        from scipy.ndimage import uniform_filter1d

        venv = uniform_filter1d(venv, size=k_, mode="nearest")
    gain = 10 ** (-(duck_db) * venv / 20.0)
    if "music_floor_db" in mp:   # fix for unplanned music dropouts: never duck deeper than this
        gain = np.maximum(gain, 10 ** (float(mp["music_floor_db"]) / 20.0) * np.where(sil > 0.5, 1.0, 0.0) + 0.0)   # unducked bed sits at -20 dBFS RMS, ducked bed 18 dB lower
    music = music * gain[None, :] * fade[None, :] * sil[None, :] * hold_g[None, :]
    from .doctor import audio as _da, lufs as _lu

    if float(mp.get("music_lowpass_hz", 0) or 0) > 0:   # calmer music: remove harsh highs
        b_, a_ = signal.butter(2, float(mp["music_lowpass_hz"]) / (SR / 2), "low")
        music = signal.lfilter(b_, a_, music, axis=1)
    vst, tt_ = _lu.short_term(voice, 0.5)
    mst, _ = _lu.short_term(music.mean(axis=0), 0.5)
    n_ = min(len(vst), len(mst))
    spk = _da.speech_fraction([{"start": s_["start"], "end": s_["end"]} for s_ in ap["voice"]], tt_[:n_] + 1.5) >= 0.6
    music_trim_db = float(mp.get("music_trim_db", 0.0))
    if spk.sum() >= 3:
        gap_db = float(np.median(vst[:n_][spk]) - np.median(mst[:n_][spk]))
        music = music * 10 ** ((gap_db - float(cfg_audio.get("music_below_voice_db", 20.0)) + music_trim_db) / 20.0)

    # ---- sfx ----
    sfx_bus = np.zeros((2, total), dtype="float32")
    cache = {}
    for ev in ap["sfx"]:
        name = ev["name"]
        if name not in cache:
            cache[name] = synth.sfx(name)
        x = cache[name]
        base = synth.SFX_GAIN.get(name, -12) + ev.get("gain", 0.0)
        peak = float(np.max(np.abs(x)) + 1e-9)
        x = x / peak * 10 ** ((-14 + base) / 20.0) if base is not None else x
        p = int(ev["t"] * SR)
        if p >= total:
            continue
        seg = x[: total - p]
        pan = 0.5 + 0.18 * np.sin(ev["t"] * 3.1)
        sfx_bus[0, p:p + len(seg)] += seg * (1 - pan) * 1.4
        sfx_bus[1, p:p + len(seg)] += seg * pan * 1.4

    vstereo = np.vstack([voice, voice]) * 1.0
    sfx_bus = sfx_bus * sil[None, :]   # silence beats are real: no sfx tail may leak into them
    mix = vstereo + music + sfx_bus + (amb * sil)[None, :]
    # glue compression on the bus (tight dynamics: reference LRA ~3.5 LU)
    mono = mix.mean(axis=0)
    bus_in = np.abs(mono)
    comp = compressor(mono, thr_db=-24, ratio=2.2, attack=0.015, release=0.25, makeup_db=0.0)
    g = np.divide(comp, mono, out=np.ones_like(comp), where=np.abs(mono) > 1e-6)
    mix = mix * np.clip(g, 0.05, 1.5)[None, :]
    mix = mix * (10 ** (intensity_db / 20.0))[None, :]
    mix = mix[:, : int(ap["total_s"] * SR)]
    fi_ = int(0.3 * SR)
    mix[:, :fi_] *= np.linspace(0, 1, fi_)   # clean fade-in (no hot start)
    ntot = mix.shape[1]
    gt = (np.clip(g, 0.05, 1.5) * (10 ** (intensity_db / 20.0)))[:ntot]
    gt[:fi_] *= np.linspace(0, 1, fi_)
    pk = float(np.max(np.abs(mix)) + 1e-9)
    pk_scale = 1.0
    if pk > 0.98:
        pk_scale = 0.98 / pk
        mix = mix * pk_scale
    pre = os.path.join(out_dir, "premaster.wav")
    import soundfile as sf

    sf.write(pre, mix.T.astype("float32"), SR, subtype="FLOAT")
    sf.write(os.path.join(out_dir, "voice_only.wav"), voice[: int(ap["total_s"] * SR)], SR, subtype="PCM_24")
    master = os.path.join(out_dir, "master.wav")
    m = loudnorm_two_pass(pre, master, I=lufs)
    final = ffmpeg_measure(master)
    # stems in final-mix scale for the Video Doctor (mono 48 kHz PCM16): same time-varying gains as the master
    fg = 10 ** ((float(final["input_i"]) - float(m["input_i"])) / 20.0) * pk_scale
    for nm_, st_ in (("voice", voice[:ntot]), ("music", music.mean(axis=0)[:ntot]), ("sfx", sfx_bus.mean(axis=0)[:ntot]), ("amb", (amb * sil)[:ntot])):
        sf.write(os.path.join(out_dir, f"stem_{nm_}.wav"), np.clip(st_ * gt * fg, -1, 1).astype("float32"), SR, subtype="PCM_16")
    rep = {"premaster": {k: m[k] for k in ("input_i", "input_tp", "input_lra")}, "master": {k: final[k] for k in ("input_i", "input_tp", "input_lra")},
           "duration_s": ap["total_s"], "sfx_used": sorted(cache.keys()), "duck_db": duck_db, "silence_beats": len(ap.get("silence", [])), "params": mp}
    json.dump(rep, open(os.path.join(out_dir, "mix_report.json"), "w"), indent=1)
    os.remove(pre)
    print(json.dumps(rep))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--voice", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    from .validate import load_cfg

    cfg = load_cfg()
    return run(a.plan, a.voice, a.out, cfg["audio"], cfg["output"]["lufs"])


if __name__ == "__main__":
    sys.exit(main())

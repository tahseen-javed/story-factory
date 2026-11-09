"""Video Doctor orchestrator (P-012 Phase 1).

python -m factory.doctor.run lint  --asm build/assembled                       Stage 0: face-overlap lint + auto-fix on the scene data (props.json), before render
python -m factory.doctor.run audio --asm build/assembled --voice DIR [--passes 3]   Stage 1: audio Doctor on the final mix stems + fix loop (re-mixes through mix_params.json)
python -m factory.doctor.run final --mp4 FILE --asm build/assembled --out DIR   Stage 2: fast scan of the FINAL mp4 + certificate (PASS / FIXED / NEEDS_REVIEW)

Every command exits 0 and prints one summary line; the certificate decides delivery (factory.bundle and tools/fetch_videos.ps1 verify it).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time

from . import VERSION, cert, tech


def load_th() -> dict:
    from .. import miniyaml

    return miniyaml.load_file(os.path.join(os.path.dirname(__file__), "..", "..", "config", "doctor.yaml"))


def _dump(path, obj):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    json.dump(obj, open(path, "w", encoding="utf-8"), indent=1)


def _bad(findings):
    return [f for f in findings if f.get("severity") in ("BLOCKER", "MAJOR")]


# ---- Stage 0: visual lint -----------------------------------------------------------------------------------------------------
def cmd_lint(asm: str, th: dict) -> dict:
    from . import visual

    path = os.path.join(asm, "props.json")
    props = json.load(open(path, encoding="utf-8"))
    tl = props["timeline"]
    before = visual.lint_timeline(tl, th)
    tl2, left, log = visual.fix_timeline(tl, th)
    if log:
        props["timeline"] = tl2
        _dump(path, props)
    rep = {"stage": "lint", "found": len(before), "fixed": len(before) - len(left), "left": left, "log": log}
    _dump(os.path.join(asm, "doctor", "LINT_REPORT.json"), rep)
    open(os.path.join(asm, "doctor", "FIX_LOG.md"), "a", encoding="utf-8").write("## Stage 0 lint\n" + "\n".join(f"- {x}" for x in log) + "\n")
    print(f"DOCTOR lint: {len(before)} face/graphic findings, {len(left)} left, {len(log)} fixes")
    return rep


# ---- shared audio helpers -----------------------------------------------------------------------------------------------------
def audio_plan_for_checks(asm: str) -> dict:
    ap = json.load(open(os.path.join(asm, "audio_plan.json"), encoding="utf-8"))
    words = {}
    pj = os.path.join(asm, "plan.json")
    if os.path.exists(pj):
        for s in json.load(open(pj, encoding="utf-8")).get("sentences", []):
            words[s.get("id")] = len(str(s.get("text", "")).split())
    sents = [{"id": v["id"], "idx": i, "start": float(v["start"]), "end": float(v["end"]), "words": words.get(v["id"], max(1, int((v["end"] - v["start"]) * 2.4))), "text": "", "parallel": bool(v.get("parallel"))}
             for i, v in enumerate(ap["voice"])]
    return {"sentences": sents, "silence": [list(w) for w in ap.get("silence", [])], "holds": [list(h) for h in ap.get("holds", [])], "total_s": ap.get("total_s")}


def read_stems(asm: str) -> dict:
    import soundfile as sf

    out = {}
    for nm in ("voice", "music", "sfx", "amb"):
        x, sr = sf.read(os.path.join(asm, f"stem_{nm}.wav"), dtype="float64")
        out[nm] = x if x.ndim == 1 else x.mean(axis=1)
    return out


def scan_audio(asm: str, th: dict, master=None) -> tuple:
    """Run every audio check on the final mix. Returns (findings, metrics, seconds)."""
    import numpy as np
    import soundfile as sf

    from . import audio as A

    t0 = time.time()
    plan = audio_plan_for_checks(asm)
    st = read_stems(asm)
    if master is None:
        x, sr = sf.read(os.path.join(asm, "master.wav"), dtype="float64")
        master = x.T if x.ndim == 2 else np.vstack([x, x])
    m1, f1 = A.check_master(master, th)
    m2, f2 = A.check_voice(st["voice"], plan, th)
    m3, f3 = A.check_music(st["voice"], st["music"], st["sfx"], st["amb"], plan, th)
    m4, f4 = A.check_music_present(st["voice"], st["music"], plan, th)
    metrics = {**m1, **m2, **m3, **m4}
    return f1 + f2 + f3 + f4, metrics, round(time.time() - t0, 1)


# ---- Stage 1: audio Doctor + fix loop -----------------------------------------------------------------------------------------
def cmd_audio(asm: str, voice_dir: str, th: dict, passes: int = 3) -> dict:
    from . import fixes

    log, history, findings, metrics, secs = [], [], [], {}, 0.0
    for p in range(1, passes + 1):
        findings, metrics, secs = scan_audio(asm, th)
        bad = _bad(findings)
        history.append({"pass": p, "blockers_majors": [f["code"] for f in bad], "scan_s": secs})
        if not bad:
            break
        fixable = [f for f in bad if f["code"] not in fixes.UNFIXABLE_AUTO]
        if not fixable or p == passes:
            break
        mpp = os.path.join(asm, "mix_params.json")
        params = json.load(open(mpp)) if os.path.exists(mpp) else {}
        new, lg = fixes.adjust_mix_params(params, fixable, metrics, th)
        if new == params:
            log.append(f"pass {p}: no parameter change possible for {[f['code'] for f in fixable]}")
            break
        _dump(mpp, new)
        log += [f"pass {p}: {x}" for x in lg]
        cmd = [sys.executable, "-m", "factory.mix", "--plan", os.path.join(asm, "audio_plan.json"), "--voice", voice_dir, "--out", asm]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            log.append(f"pass {p}: re-mix failed: {(r.stderr or r.stdout)[-300:]}")
            break
    rep = {"stage": "audio", "history": history, "findings": findings, "metrics": metrics, "log": log, "scan_s": secs}
    _dump(os.path.join(asm, "doctor", "AUDIO_REPORT.json"), rep)
    open(os.path.join(asm, "doctor", "FIX_LOG.md"), "a", encoding="utf-8").write("## Stage 1 audio\n" + "\n".join(f"- {x}" for x in log) + "\n")
    bad = _bad(findings)
    print(f"DOCTOR audio: passes {len(history)}, scan {secs}s, BLOCKER/MAJOR left {len(bad)} {[f['code'] for f in bad]}, fixes {len(log)}")
    return rep


# ---- Stage 2: final mp4 -------------------------------------------------------------------------------------------------------
def probe(mp4: str) -> dict:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate,duration", "-of", "json", mp4], capture_output=True, text=True)
    return json.loads(r.stdout or "{}")


def video_checks(mp4: str, th: dict, expect: tuple = (1920, 1080)) -> tuple:
    """Black frames (ffmpeg blackdetect), resolution, fps, audio/video duration match. Returns (findings, metrics)."""
    f, m = [], {}
    pr = probe(mp4)
    v = next((s for s in pr.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in pr.get("streams", []) if s.get("codec_type") == "audio"), {})
    m["resolution"] = f"{v.get('width')}x{v.get('height')}"
    if (v.get("width"), v.get("height")) != tuple(expect):
        f.append({"code": "V4-RESOLUTION", "severity": th["severity"].get("resolution", "BLOCKER"), "t0": 0, "t1": 0, "value": None, "threshold": f"{expect[0]}x{expect[1]}", "msg": f"resolution {m['resolution']}"})
    try:
        num, den = str(v.get("r_frame_rate", "30/1")).split("/")
        fps = float(num) / float(den)
    except Exception:  # noqa: BLE001
        fps = 0.0
    m["fps"] = round(fps, 2)
    if abs(fps - 30.0) > 0.1:
        f.append({"code": "V4-FPS", "severity": "BLOCKER", "t0": 0, "t1": 0, "value": fps, "threshold": 30, "msg": f"fps {fps}"})
    dv, da = float(v.get("duration") or 0), float(a.get("duration") or 0)
    m["video_s"], m["audio_s"] = round(dv, 2), round(da, 2)
    if da and abs(dv - da) > 0.25:
        f.append({"code": "A5-AV-DURATION", "severity": "MAJOR", "t0": 0, "t1": 0, "value": abs(dv - da), "threshold": 0.25, "msg": f"video {dv:.2f}s vs audio {da:.2f}s"})
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", mp4, "-vf", "blackdetect=d=0.05:pix_th=0.04:pic_th=0.98", "-an", "-f", "null", "-"], capture_output=True, text=True)
    blacks = []
    for mt in re.finditer(r"black_start:([\d.]+)\s+black_end:([\d.]+)\s+black_duration:([\d.]+)", r.stderr):
        b0, b1 = float(mt.group(1)), float(mt.group(2))
        if b0 <= 0.01 or b1 >= dv - 0.2:   # deliberate fade-in / fade-out
            continue
        blacks.append((b0, b1))
        f.append({"code": "V4-BLACK", "severity": th["severity"].get("black", "BLOCKER"), "t0": b0, "t1": b1, "value": b1 - b0, "threshold": 0.05, "msg": f"black frame(s) {b0:.2f}-{b1:.2f}s inside the video"})
    m["black_segments"] = len(blacks)
    return f, m


def master_from_mp4(mp4: str, wav: str) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp4, "-vn", "-ac", "2", "-ar", "48000", "-c:a", "pcm_f32le", wav], check=True)


def cmd_final(mp4: str, asm: str, out: str, th: dict, expect: tuple = (1920, 1080)) -> dict:
    import numpy as np
    import soundfile as sf

    from . import visual

    t0 = time.time()
    os.makedirs(out, exist_ok=True)
    wav = os.path.join(out, "final_audio.wav")
    master_from_mp4(mp4, wav)
    x, _ = sf.read(wav, dtype="float64")
    master = x.T if x.ndim == 2 else np.vstack([x, x])
    findings, metrics = [], {}
    stage_a = time.time()
    if os.path.exists(os.path.join(asm, "stem_voice.wav")):
        findings, metrics, _ = scan_audio(asm, th, master=master)
    else:   # no stems (should not happen in production): master checks only
        from . import audio as A

        metrics, findings = A.check_master(master, th)
        findings.append({"code": "A3-NO-STEMS", "severity": "MAJOR", "t0": 0, "t1": 0, "value": None, "threshold": None, "msg": "stems missing: music level cannot be proven"})
    audio_scan_s = round(time.time() - stage_a, 1)
    tl = json.load(open(os.path.join(asm, "props.json"), encoding="utf-8"))["timeline"]
    # Phase 2 stage 4: technical checks on decoded frames (black / frozen / duplicate / flicker / cuts / static poses / pacing), black-frame auto-fix
    fix_notes = []
    tf = tech.run_file(mp4, th, tl)
    if any(x["code"] == "V4-BLACK" for x in tf["findings"]):
        fixed_path = os.path.join(out, "black_fixed.mp4")
        if tech.fix_black(mp4, tf["findings"], fixed_path):
            os.replace(fixed_path, mp4)
            fix_notes.append(f"black frames held over by the previous good frame: {[(x['t0'], x['t1']) for x in tf['findings'] if x['code'] == 'V4-BLACK']}")
            tf = tech.run_file(mp4, th, tl)
    findings += tf["findings"]
    metrics.update({"tech_" + k: v for k, v in tf["metrics"].items()})
    vf, vm = video_checks(mp4, th, expect)
    findings += vf
    metrics.update(vm)
    # reports of the other Phase 2 stages (they run earlier in the pipeline; a stage that could not run is listed, never silent)
    stage_reports = {}
    for nm in ("VOICE", "CHAR", "LOOK"):
        rp = os.path.join(asm, "doctor", f"{nm}_REPORT.json")
        if os.path.exists(rp):
            r = json.load(open(rp, encoding="utf-8"))
            stage_reports[nm] = {"status": r.get("status"), "seconds": r.get("seconds"), "error": r.get("error")}
            if r.get("status") == "OK":
                findings += r.get("findings", [])
                metrics.update({f"{nm.lower()}_{k}": v for k, v in (r.get("metrics") or {}).items()})
            else:
                findings.append({"code": f"{nm}-SKIPPED", "severity": "MINOR", "t0": 0, "t1": 0, "value": None, "threshold": None, "msg": f"{nm.lower()} stage did not run: {r.get('error')}"})
        else:
            stage_reports[nm] = {"status": "NOT_RUN"}
    metrics["stages"] = stage_reports
    lint = visual.lint_timeline(tl, th)
    plan_p = os.path.join(asm, "plan.json")
    findings += tech.check_story(tl, json.load(open(plan_p, encoding="utf-8")) if os.path.exists(plan_p) else {}, th)
    findings += lint
    metrics["face_overlap_findings"] = len([x for x in lint if x["code"] == "V1-FACE-OVERLAP"])
    metrics["audio_scan_s"] = audio_scan_s
    metrics["final_scan_s"] = round(time.time() - t0, 1)
    bad = _bad(findings)
    fl = os.path.join(asm, "doctor", "FIX_LOG.md")
    fixed_any = bool(fix_notes) or (os.path.exists(fl) and any(ln.startswith("- ") for ln in open(fl, encoding="utf-8").read().splitlines()))
    if fix_notes:
        os.makedirs(os.path.dirname(fl), exist_ok=True)
        open(fl, "a", encoding="utf-8").write("## Stage 2 final\n" + "\n".join(f"- {x}" for x in fix_notes) + "\n")
    status = "NEEDS_REVIEW" if bad else ("FIXED" if fixed_any else "PASS")
    checks = {}
    for code in sorted({f["code"] for f in findings} | {"A1-GAP", "A3-MUSIC-LOUD", "A3-MUSIC-DROPOUT", "V1-FACE-OVERLAP", "V4-BLACK"}):
        fs = [f for f in findings if f["code"] == code]
        checks[code] = {"status": "FAIL" if any(x["severity"] in ("BLOCKER", "MAJOR") for x in fs) else ("WARN" if fs else "PASS"), "count": len(fs)}
    for f_ in findings:
        f_.setdefault("class", "LIKELY_FALSE_ALARM" if f_["code"] == "A2-UNCONFIRMED" else "REAL")
    metrics["timings_s"] = {"audio_scan": audio_scan_s, "final_scan_total": metrics["final_scan_s"]}
    report = {"doctor_version": VERSION, "status": status, "findings": findings, "metrics": metrics, "checks": checks}
    _dump(os.path.join(out, "FAST_REPORT.json"), report)
    cp = cert.write(mp4, out, status, report, video_id=os.path.splitext(os.path.basename(mp4))[0])
    if os.path.exists(wav):
        os.remove(wav)
    print(f"DOCTOR final: {status}; BLOCKER/MAJOR {len(bad)} {[f['code'] for f in bad]}; audio scan {audio_scan_s}s; total {metrics['final_scan_s']}s; certificate {cp}")
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("lint")
    s.add_argument("--asm", required=True)
    s = sub.add_parser("audio")
    s.add_argument("--asm", required=True)
    s.add_argument("--voice", required=True)
    s.add_argument("--passes", type=int, default=3)
    s = sub.add_parser("final")
    s.add_argument("--mp4", required=True)
    s.add_argument("--asm", required=True)
    s.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    th = load_th()
    if a.cmd == "lint":
        cmd_lint(a.asm, th)
    elif a.cmd == "audio":
        cmd_audio(a.asm, a.voice, th, a.passes)
    else:
        cmd_final(a.mp4, a.asm, a.out, th)   # production is always 1920x1080; only the fixture tests call cmd_final(expect=...) in code
    return 0


if __name__ == "__main__":
    sys.exit(main())

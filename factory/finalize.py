"""Finalize: concat chunks, mux audio, QA, auto-fix loop (max 2 rounds), scorecard, naming. Runs in the finalize CI job."""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys

from . import fixers, qa, scorecard
from .validate import load_cfg


def run(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd)[:200], flush=True)
    return subprocess.run(cmd, check=True, **kw)


def concat(chunks_dir: str, out: str):
    files = sorted(glob.glob(os.path.join(chunks_dir, "**", "chunk_*.mp4"), recursive=True), key=lambda p: int(re.findall(r"chunk_(\d+)", p)[0]))
    lst = out + ".txt"
    with open(lst, "w") as fh:
        for f in files:
            fh.write(f"file '{os.path.abspath(f)}'\n")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out])
    return len(files)


def reencode(src: str, dst: str, cfg: dict):
    """Final video pass: H.264 High, CRF 18 with a sensible maxrate cap (grain makes raw chunks 16 Mbps) so 30-minute videos stay manageable."""
    o = cfg["output"]
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", src, "-an", "-c:v", "libx264", "-profile:v", o["profile"], "-preset", o["preset"],
         "-crf", str(o["crf"]), "-maxrate", str(o["maxrate"]), "-bufsize", str(o["bufsize"]), "-pix_fmt", o["pix_fmt"], "-g", "60", dst])


def mux(video: str, audio: str, out: str, cfg: dict):
    o = cfg["output"]
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", video, "-i", audio, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
         "-c:a", o["audio_codec"], "-b:a", o["audio_bitrate"], "-ar", str(o["audio_rate"]), "-movflags", "+faststart", "-shortest", out])


def rerender(video_dir: str, props: str, chunks: list, chunk_defs: list, out_dir: str):
    for i in chunks:
        c = next(x for x in chunk_defs if x["i"] == i)
        dst = os.path.join(out_dir, f"chunk_{i}.mp4")
        run(["npx", "remotion", "render", "src/index.ts", "Story", os.path.abspath(dst), f"--props={os.path.abspath(props)}",
             f"--frames={c['from']}-{c['to']}", "--concurrency=4", "--muted", "--log=warn"], cwd=video_dir)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunks-dir", required=True)
    ap.add_argument("--assembled", required=True)
    ap.add_argument("--video-dir", required=True)
    ap.add_argument("--thumbs", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--sources", type=int, default=0)
    a = ap.parse_args(argv)
    cfg = load_cfg()
    os.makedirs(a.out, exist_ok=True)
    props = os.path.join(a.assembled, "props.json")
    chunk_defs = json.load(open(os.path.join(a.assembled, "chunks.json")))
    plan = json.load(open(a.plan))
    ar = json.load(open(os.path.join(a.assembled, "assemble_report.json")))
    plan["_wer_mean"] = ar.get("wer_mean")
    thumbs_rep = os.path.join(a.thumbs, "thumbs_report.json") if a.thumbs else None
    vid_only, vid_enc, final = os.path.join(a.out, "video_only.mp4"), os.path.join(a.out, "video_enc.mp4"), os.path.join(a.out, "final.mp4")
    rounds, fixes_log, rep = 0, [], None
    while True:
        n = concat(a.chunks_dir, vid_only)
        reencode(vid_only, vid_enc, cfg)
        mux(vid_enc, os.path.join(a.assembled, "master.wav"), final, cfg)
        qa_json = os.path.join(a.out, "qa_report.json")
        rc = qa.run(final, props, os.path.join(a.assembled, "chunks.json"), os.path.join(a.assembled, "captions.srt"), qa_json,
                    os.path.join(a.assembled, "assemble_report.json"), thumbs_rep)
        rep = json.load(open(qa_json))
        if rc == 0 or rounds >= int(cfg["qa"]["max_fix_rounds"]):
            break
        rounds += 1
        res = fixers.apply(props, rep, chunk_defs)
        fixes_log.append({"round": rounds, **res})
        if not res["chunks"]:
            break
        rerender(a.video_dir, props, res["chunks"], chunk_defs, a.chunks_dir)
    props_data = json.load(open(props))
    thumbs = json.load(open(thumbs_rep)) if thumbs_rep and os.path.exists(thumbs_rep) else None
    card = scorecard.compute(props_data, plan, rep, thumbs, a.sources, cfg)
    rep["scorecard"] = card
    rep["categories"]["reference_scorecard"] = card["ok"]
    # P-007 gates: audio licence (every asset needs an entry + proof) and monetization safety; failure = needs_review, not delivered
    from . import licence, monetization

    ap = json.load(open(os.path.join(a.assembled, "audio_plan.json")))
    lic = licence.check(ap, ar)
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    job_dir = os.path.join(root, "pilot" if plan.get("mode") == "pilot" else "jobs", plan["slug"])
    mon = monetization.run(plan, props_data["timeline"], job_dir, cfg)
    from . import cast as castmod, voicecheck
    from .parse import parse as parse_script
    from .uniqueness import shot_signature

    sc_ = parse_script(open(os.path.join(job_dir, "script.md"), encoding="utf-8").read())
    enforce = int(plan.get("style_version", 1)) >= 3
    cute = castmod.cute_check(sc_.characters, cfg["style"], " ".join(s.text for s in sc_.shots), enforce)
    uniq = castmod.unique_check(sc_.characters, shot_signature(sc_), castmod.load_history(), cfg["style"], plan.get("nnn"))
    vprof = voicecheck.profiles_ok(cfg["characters"], sc_.characters)
    rep["cast"], rep["voices"] = {"cute": cute, "unique": uniq}, vprof
    rep["categories"]["cast"] = (cute["ok"] or not enforce) and uniq["ok"]
    rep["categories"]["voices"] = vprof["ok"] or not enforce
    rep["licence"], rep["monetization"] = lic, mon
    rep["categories"]["licence"], rep["categories"]["monetization"] = lic["ok"], mon["ok"]
    json.dump(lic, open(os.path.join(a.out, "licence_report.json"), "w"), indent=1)
    rep["pass"] = all(rep["categories"].values()) and rep["duration"]["ok"]
    rep["warnings"] = ([f"procedural backdrops used for: {', '.join(ar['backdrop_fallbacks'])}"] if ar.get("backdrop_fallbacks") else []) +         ([f"TTS flagged sentences: {len(ar['tts_flagged'])}"] if ar.get("tts_flagged") else []) +         (["TTS fallback engine used (voice consistency)"] if any(e != "chatterbox" and e != "chatterbox_turbo" for e in ar.get("tts_engines", [])) else [])
    rep["fix_rounds"] = rounds
    rep["fixes"] = fixes_log
    json.dump(rep, open(os.path.join(a.out, "qa_report.json"), "w"), indent=1)
    with open(os.path.join(a.out, "scorecard.txt"), "w") as fh:
        fh.write(scorecard.table(card) + "\n")
    status = "ok" if rep["pass"] else "needs_review"
    json.dump({"status": status, "fix_rounds": rounds, "runtime_s": rep["duration"]["actual"], "minutes": int(round(rep["duration"]["actual"] / 60.0))},
              open(os.path.join(a.out, "status.json"), "w"))
    print(scorecard.table(card))
    print("STATUS", status)
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as fh:
            fh.write(f"status={status}\nminutes={int(round(rep['duration']['actual'] / 60.0))}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

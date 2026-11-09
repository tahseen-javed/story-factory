"""Bundle a finished video: exact file names, tar, age encryption (public recipient), parts <= 1.9 GB, SHA256 manifest.

Release assets carry only the video number (the repo is public); the real names live inside the encrypted tar.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def base_name(nnn: int, short_title: str, minutes: int) -> str:
    return f"{int(nnn):03d} {short_title} {int(minutes):02d}min"


def run(args):
    from .doctor import cert as _cert

    ok, why = _cert.verify(args.video, args.certificate)   # P-012: no certificate, no bundle
    if not ok:
        raise SystemExit(f"bundle refused: {why}")
    base = base_name(args.nnn, args.short_title, args.minutes)
    work = os.path.join(args.out, "stage")
    os.makedirs(work, exist_ok=True)
    names = {
        args.video: f"{base}.mp4",
        args.thumb1: f"{base} - Thumbnail 1.jpg",
        args.thumb2: f"{base} - Thumbnail 2.jpg",
        args.info: f"{base} - YouTube Info.txt",
        args.srt: f"{base}.srt",
        args.certificate: f"{base}.CERTIFICATE.json",
    }
    for src, dst in names.items():
        shutil.copy(src, os.path.join(work, dst))
    tar_path = os.path.join(args.out, f"video-{int(args.nnn):03d}.tar")
    with tarfile.open(tar_path, "w") as tf:
        for dst in names.values():
            tf.add(os.path.join(work, dst), arcname=dst)
    enc = tar_path + ".age"
    subprocess.run(["age", "-r", args.recipient, "-o", enc, tar_path], check=True)
    os.remove(tar_path)
    parts = []
    part_max = int(float(args.part_gb) * 1024 ** 3)
    size = os.path.getsize(enc)
    if size <= part_max:
        parts = [enc]
    else:
        with open(enc, "rb") as fh:
            i = 1
            while True:
                chunk = fh.read(part_max)
                if not chunk:
                    break
                p = f"{enc}.part{i:02d}"
                open(p, "wb").write(chunk)
                parts.append(p)
                i += 1
        os.remove(enc)
    manifest = {"nnn": int(args.nnn), "format": "tar+age", "parts": [{"name": os.path.basename(p), "bytes": os.path.getsize(p), "sha256": sha256(p)} for p in parts],
                "files": len(names), "created_by": "story-factory"}
    mpath = os.path.join(args.out, f"video-{int(args.nnn):03d}.manifest.json")
    json.dump(manifest, open(mpath, "w"), indent=1)
    shutil.rmtree(work)
    print(json.dumps({"base": base, "parts": [os.path.basename(p) for p in parts], "manifest": os.path.basename(mpath)}))
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as fh:
            fh.write(f"base_name={base}\n")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--nnn", type=int, required=True)
    ap.add_argument("--short-title", required=True)
    ap.add_argument("--minutes", type=int, required=True)
    ap.add_argument("--video", required=True)
    ap.add_argument("--thumb1", required=True)
    ap.add_argument("--thumb2", required=True)
    ap.add_argument("--info", required=True)
    ap.add_argument("--srt", required=True)
    ap.add_argument("--recipient", required=True)
    ap.add_argument("--part-gb", default="1.9")
    ap.add_argument("--certificate", required=True)
    ap.add_argument("--out", required=True)
    return run(ap.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())

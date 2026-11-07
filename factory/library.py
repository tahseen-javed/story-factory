"""Build library/music.json and library/sfx.json from an extracted folder of audio files (mood from file/folder name, duration via ffprobe).

Every entry carries a licence field; publish refuses assets without one. Default licences follow docs/SETUP_MUSIC.md.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

MOODS = {"tense": ("tense", "suspense", "thriller"), "dread": ("dark", "dread", "horror", "ominous"), "urgent": ("urgent", "chase", "action", "driving"),
         "hopeful": ("hope", "uplift", "inspir"), "sorrow": ("sad", "sorrow", "melanchol"), "climax": ("epic", "climax", "intense"), "calm": ("calm", "ambient", "peace"),
         "mystery": ("mystery", "strange", "curious")}


def duration(path: str) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True)
    try:
        return round(float(r.stdout.strip()), 2)
    except ValueError:
        return 0.0


def mood_of(name: str) -> str:
    low = name.lower()
    for m, keys in MOODS.items():
        if any(k in low for k in keys):
            return m
    return "tense"


def main(argv=None):
    src, out = (argv or sys.argv[1:])[:2]
    music, sfx = [], []
    for dp, _, fns in os.walk(src):
        for f in sorted(fns):
            if not f.lower().endswith((".mp3", ".wav", ".ogg", ".flac", ".m4a")):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, src)
            d = duration(p)
            if d >= 45:
                music.append({"file": rel, "mood": mood_of(rel), "bpm": None, "intensity": 3, "loop": [0.0, d], "duration_s": d, "licence": "YouTube Audio Library (no attribution required)"})
            else:
                sfx.append({"file": rel, "tags": [os.path.splitext(f)[0].lower()], "duration_s": d, "licence": "CC0"})
    json.dump(music, open(os.path.join(out, "music.json"), "w"), indent=1)
    json.dump(sfx, open(os.path.join(out, "sfx.json"), "w"), indent=1)
    print(f"music {len(music)} sfx {len(sfx)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

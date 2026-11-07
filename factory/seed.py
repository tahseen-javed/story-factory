"""Style-seed planner (stdlib): next video number + seed values that do not repeat the last 10 videos (and are distinct inside the batch).

python -m factory.seed [count]   -> prints JSON for `count` videos (default 1). Reads library/history.json (needs git-crypt unlocked).
"""
from __future__ import annotations

import json
import os
import sys

from . import vocab
from .validate import ROOT

FIELDS = {
    "opening": ("openers", vocab.OPENING_TYPES), "ritual": ("rituals", vocab.RITUAL_TYPES), "ending": ("endings", vocab.ENDING_TYPES),
    "accent": ("accent", vocab.ACCENT_COLOURS), "lut": ("lut", vocab.LUT_VARIANTS), "titlecard": ("titlecard", vocab.TITLECARD_DESIGNS),
    "camera_rhythm": ("camera_rhythm", vocab.CAMERA_RHYTHMS), "transition": ("transition", vocab.TRANSITION_MIXES),
    "thumbnail_layout": ("thumbnail_layout", vocab.THUMBNAIL_LAYOUTS),
}
MUSIC_SETS = ("dread_pad", "tense_pulse", "urgent_drive", "mystery_tick", "hopeful_pluck", "sorrow_sparse", "calm_dorian", "climax_epic")
OUTFITS = ("teal_cap", "plum_beanie", "mustard_hood", "navy_cap", "olive_hood", "coral_beanie", "grey_hood", "cobalt_cap")


def used_recently(history: list, key: str, n: int = 10) -> set:
    out = set()
    for h in history[-n:]:
        v = h.get(key)
        out.update(v if isinstance(v, list) else [v])
    return out


def pick(history: list, count: int = 1) -> list:
    nxt = max([h["nnn"] for h in history] + [0]) + 1
    batch: list = []
    results = []
    for k in range(count):
        seed = {}
        for name, (hk, options) in FIELDS.items():
            avoid = used_recently(history, hk) | {s[name] for s in batch}
            free = [o for o in options if o not in avoid] or [o for o in options if o not in {s[name] for s in batch}] or list(options)
            seed[name] = free[(nxt + k) % len(free)]
        for name, options in (("music_set", MUSIC_SETS), ("outfit", OUTFITS)):
            avoid = used_recently(history, name) | {s[name] for s in batch}
            free = [o for o in options if o not in avoid] or list(options)
            seed[name] = free[(nxt + k) % len(free)]
        seed["wpm"] = 165 + ((nxt + k) * 5) % 21
        batch.append(seed)
        results.append({"nnn": nxt + k, "style_seed": seed})
    return results


def main(argv=None):
    argv = argv or sys.argv[1:]
    count = int(argv[0]) if argv else 1
    p = os.path.join(ROOT, "library", "history.json")
    raw = open(p, "rb").read()
    if raw.startswith(b"\x00GITCRYPT"):
        print("history.json is encrypted: run git-crypt unlock first")
        return 1
    print(json.dumps(pick(json.loads(raw.decode("utf-8")), count), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

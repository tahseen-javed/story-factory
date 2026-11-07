"""Cross-video uniqueness (stdlib only): script similarity (TF-IDF cosine, unigrams+bigrams), title similarity, shot-tag sequence similarity,
against the last 50 jobs and inside a batch. Threshold from config script.similarity_max (0.35). Script failures go to needs_review."""
from __future__ import annotations

import difflib
import glob
import math
import os
import re
import sys
from collections import Counter

from .parse import parse
from .validate import ROOT, load_cfg

STOP = set("the a an and or but of to in on at for with you your is are was were it its that this as be by from not no so if then than i he she they we".split())


def tokens(text: str) -> list:
    w = [x for x in re.findall(r"[a-z0-9']+", text.lower()) if x not in STOP]
    return w + [f"{a}_{b}" for a, b in zip(w, w[1:])]


def tfidf_vectors(docs: list) -> list:
    toks = [Counter(tokens(d)) for d in docs]
    df = Counter()
    for t in toks:
        df.update(t.keys())
    n = len(docs)
    vecs = []
    for t in toks:
        v = {k: (1 + math.log(c)) * math.log((1 + n) / (1 + df[k]) + 1) for k, c in t.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        vecs.append({k: x / norm for k, x in v.items()})
    return vecs


def cosine(a: dict, b: dict) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(x * b.get(k, 0.0) for k, x in a.items())


def load_script(path: str):
    raw = open(path, "rb").read()
    if raw.startswith(b"\x00GITCRYPT"):
        return None
    return parse(raw.decode("utf-8"))


def shot_signature(sc) -> list:
    return [f"{s.location}.{s.variant}|{s.camera.preset if s.camera else '-'}|{s.overlays[0].name if s.overlays else '-'}" for s in sc.shots]


def check(job_dir: str, others: list, thr: float = 0.35) -> list:
    """Returns a list of (level, message). others: directories to compare against (previous jobs or batch siblings)."""
    me = load_script(os.path.join(job_dir, "script.md"))
    out = []
    if me is None:
        return [("error", "script is encrypted/locked")]
    mine_text = " ".join(s.text for s in me.shots)
    docs, names = [mine_text], []
    sigs = [shot_signature(me)]
    titles = []
    for d in others:
        p = os.path.join(d, "script.md")
        if os.path.abspath(d) == os.path.abspath(job_dir) or not os.path.exists(p):
            continue
        sc = load_script(p)
        if sc is None:
            continue
        docs.append(" ".join(s.text for s in sc.shots))
        names.append(os.path.basename(d))
        sigs.append(shot_signature(sc))
        titles.append(sc.title)
    if not names:
        return [("info", "no earlier scripts to compare with (first video)")]
    vecs = tfidf_vectors(docs)
    for i, nm in enumerate(names, 1):
        sim = cosine(vecs[0], vecs[i])
        if sim >= thr:
            out.append(("error", f"script similarity {sim:.2f} >= {thr} with {nm}"))
        seq = difflib.SequenceMatcher(None, sigs[0], sigs[i]).ratio()
        if seq >= 0.55:
            out.append(("error", f"shot-tag sequence similarity {seq:.2f} with {nm}"))
        if difflib.SequenceMatcher(None, me.title.lower(), titles[i - 1].lower()).ratio() >= 0.7:
            out.append(("error", f"title too similar to {nm}"))
    return out or [("info", f"unique vs {len(names)} scripts")]


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv:
        print("usage: python -m factory.uniqueness <job_dir> [other dirs...]  (default: the last 50 jobs/* and pilot/*)")
        return 2
    job = argv[0]
    others = argv[1:] or sorted(glob.glob(os.path.join(ROOT, "jobs", "*")) + glob.glob(os.path.join(ROOT, "pilot", "*")))[-50:]
    thr = float(load_cfg()["script"]["similarity_max"])
    res = check(job, others, thr)
    for lvl, msg in res:
        print(f"{lvl.upper():5} {msg}")
    return 1 if any(l == "error" for l, _ in res) else 0


if __name__ == "__main__":
    sys.exit(main())

"""YouTube Info file: 3 title options, description with chapters + sources, tags, pinned comment, upload settings. Stdlib only."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

from .textutil import split_sentences


def ts(sec: float) -> str:
    sec = int(sec)
    h, r = divmod(sec, 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def first_question(plan: dict) -> str | None:
    for s in plan["sentences"][:40]:
        if s["text"].strip().endswith("?"):
            return s["text"].strip()
    return None


def read_sources(job_dir: str) -> list:
    out = []
    for name in ("facts.md", "sources.md"):
        p = os.path.join(job_dir, name)
        if os.path.exists(p):
            for ln in open(p, encoding="utf-8"):
                m = re.match(r"^\s*[-~]\s+(.*?)\s*\|\s*(https://\S+)\s*$", ln)
                if m:
                    out.append((m.group(1), m.group(2)))
            break
    return out


def title_options(plan: dict) -> list:
    t = plan["title"]
    q = first_question(plan)
    nums = re.findall(r"\b(\d{1,3})\s*(hours?|days?|minutes?)\b", " ".join(str(a) for sh in plan["shots"] for a in ((sh.get("overlay") or {}).get("args") or [])), re.I)
    opts = [f"{t}: A Survival Story (You Have Hours To Act)"]
    if q:
        q = q.rstrip("?")
        opts.append(f"{q}? | {t}")
    else:
        opts.append(f"What Would You Do? {t}")
    if nums:
        n, u = nums[0]
        opts.append(f"{n} {u.capitalize()} Left: {t} (Animated Story)")
    else:
        opts.append(f"{t} - Can You Survive It? (Animated Story)")
    return [o[:100] for o in opts]


def tags_for(plan: dict) -> list:
    ex = plan.get("extras") or {}
    if ex.get("tags"):
        return [t.strip() for t in str(ex["tags"]).split(",") if t.strip()][:15]
    words = re.findall(r"[A-Za-z]{4,}", plan["title"])
    base = ["animated story", "survival story", "2d animation", "what would you do", "emergency preparedness", "storytelling", "thriller", "second person story"]
    return list(dict.fromkeys([w.lower() for w in words] + [plan["title"].lower()] + base))[:15]


def build_info(plan: dict, chapters: dict, sources: list, base_name: str, settings: dict) -> str:
    ex = plan.get("extras") or {}
    titles = ([t.strip() for t in str(ex["titles"]).split("|")] if ex.get("titles") else ([ex["title"]] if ex.get("title") else []) + title_options(plan))[:3]
    q = first_question(plan) or ""
    hook = ex.get("description") or (plan["sentences"][0]["text"] + (" " + q if q else ""))
    lines = ["TITLE OPTIONS", *[f"{i}. {t}" for i, t in enumerate(titles, 1)], "", "DESCRIPTION", hook, ""]
    if not ex.get("description"):
        lines.append("In this story you are the main character. Follow the countdown and make it to the end.")
    if plan.get("kind") != "test":
        lines += ["", "CHAPTERS"]
        first = True
        for c in chapters["chapters"]:
            lines.append(f"{ts(0 if first else c['start'])} {c['title'].title()}")
            first = False
    lines += ["", "SOURCES (survival facts mentioned in this story)"]
    lines += [f"- {f} {u}" for f, u in sources] or ["- (none)"]
    lines += ["", "This is a fictional story with original illustrations and an AI-generated narration voice. Survival facts come from the official sources above; always follow guidance from your local authorities.", ""]
    lines += ["TAGS", ", ".join(tags_for(plan)), "", "PINNED COMMENT (suggestion)",
              ex.get("pinned_comment") or "Which of the survival rules from this story would you have forgotten? Tell me below, and subscribe for the next story.", "",
              "UPLOAD SETTINGS", *[f"- {k}: {v}" for k, v in settings.items()], f"- base name: {base_name}"]
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--chapters", required=True)
    ap.add_argument("--job-dir", default=None)
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    plan = json.load(open(a.plan, encoding="utf-8"))
    chapters = json.load(open(a.chapters, encoding="utf-8"))
    settings = {"privacy": "private", "madeForKids": "false", "category": "Film & Animation", "language": "en", "captions": "SRT provided",
                "altered/synthetic content": "cartoon visuals + AI narration voice (not realistic people or events)"}
    sources = [(x['fact'], x['url']) for x in plan.get('sources', [])] or (read_sources(a.job_dir) if a.job_dir else [])
    txt = build_info(plan, chapters, sources, a.base, settings)
    open(a.out, "w", encoding="utf-8").write(txt)
    print(f"wrote {a.out} ({len(txt)} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

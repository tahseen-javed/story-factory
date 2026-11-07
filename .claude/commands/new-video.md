---
description: Write one video job (script, facts, job.yaml), validate, commit, push
argument-hint: "<title>" <minutes> [idea]
---
Follow CLAUDE.md section 8 exactly for: $ARGUMENTS
Read docs/SCRIPT_FORMULA.md and docs/SHOT_TAGS.md only if not read this session. Read `python tools/history_tail.py 20` and the top 10 lines of docs/LEARNINGS.md.
Write jobs/<slug>/script.md, facts.md, job.yaml in one pass, add the next entry to library/history.json, run `python -m factory.validate jobs/<slug>`, fix errors, commit "video: <base name>", push (hooks verify encryption). Reply with one status line.

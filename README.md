# story-factory

Open-source toolchain that turns a **script file** (title + length, 3-30 minutes) into a finished 1080p, 30 fps,
2D cut-out animated "you"-POV story video with captions, metadata and two thumbnails.
Everything heavy (speech, images, depth, render, QA) runs on GitHub-hosted runners; there is no paid service and no LLM in the pipeline.

## What is in here
- `factory/` Python pipeline: parse, validate, plan, tts, images, depth, assemble, mix, qa, fixers, thumbnails, metadata, publish.
- `video/` Remotion (React/TypeScript) project: puppet rig, overlays, camera presets, FX, scenes.
- `tools/` helper scripts (QA summary, scorecard, disk report, fetch for Windows).
- `config/factory.yaml` every knob; `config/preferences.yaml` machine-checked preferences.
- `docs/` style bible, script formula, shot-tag vocabulary, QA rules, setup guides, risks, decisions.
- `.github/workflows/` CI, production, library, benchmark workflows (manual or push triggered, no schedules).

## Usage
1. Write `jobs/<slug>/script.md` (see `docs/SHOT_TAGS.md`, `docs/SCRIPT_FORMULA.md`) and push; `produce.yml` does the rest.
2. Run `tools/fetch.cmd` on Windows to pull finished, encrypted bundles into `Documents\Animated Long Video 1st Channel`.
3. Private upload to YouTube happens automatically once the YouTube secrets are set (see `docs/SETUP_YOUTUBE.md`).

## Local checks (standard library only)
```
python -m factory.validate jobs/<slug>
python -m unittest discover -s tests
python tools/risk_check.py
```

Generated videos are outputs and are never committed. Secrets live only in GitHub Secrets; scripts, voices and the
reference material are encrypted with git-crypt. All rights reserved for the factory code.

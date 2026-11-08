# PREFERENCES: standing rules (newest wins; imported into CLAUDE.md)

## P-001 | 2026-11-08 | workflow
Rule: No "go" between build phases. Run Phases 0, 0a, 1-6 back to back, fully autonomously, until the factory is complete and the Definition of Done is met. Proof goes to docs/PROGRESS.md; chat gets only a 3-line Roman Urdu update per finished phase. Owner-only steps (browser logins, GitHub secrets, YouTube OAuth, voice recording, music zip) are collected in docs/USER_CHECKLIST.md while building continues with placeholders/test data. Phase 5 feedback is self-judged against QA + scorecard (review questions go to docs/PROGRESS.md). Stop only for an irreversible/leak risk or a total block only the owner can clear (ask in one line). On a usage limit, write the exact next step into docs/PROGRESS.md; "continue" resumes from it. Speed never lowers quality.
Enforced by: CLAUDE.md section 3 (build mode); docs/BUILD_PROMPT.md STANDING RULE P-001; config/preferences.yaml workflow.phase_gating=false (text-only otherwise)
Status: active

## P-002 | 2026-11-08 | workflow
Rule: Quality bar v2 (owner rated v1 5/10). Hook in the middle of danger (first 2 sentences concrete, open loop paid off at the end). No shot longer than 5.0 s (average 3-4 s, framing and camera recipe never repeat back to back). No frozen end card, no placeholder boxes: the last 8 s keep animating and fade out. Burned-in captions (2 lines, 38 chars, word highlight), lip-sync, 4-layer sound with LRA >= 4 LU and >= 3 silence beats. Story acts (hook, act1, act2a, midpoint, act2b, sacrifice, climax, resolution), a pattern interrupt about every 35 s. Delivery folder gets exactly 3 files per video: mp4 + 2 thumbnails.
Enforced by: config/pacing.yaml, config/audio.yaml, config/style.yaml; factory.validate (ACT/INTERRUPT/SILENCE markers, end_screen forbidden, hook check); factory.qa check_v2 (rating 0-10); tests/test_v2.py
Status: active

## P-003 | 2026-11-08 | visual
Rule: Remaining v2 items. (1) Look: backdrops restyled once through SDXL-Lightning img2img (strength 0.35-0.45) + shared outline/grade pass into a cached library, palette-histogram QA against config/style.yaml, outliers regenerated. (2) Voice: Chatterbox per sentence, ASR match >= 97% (re-synthesise only failed sentences with another seed/pace), pace and emotion per line from tags. (3) Music: licence-safe library (CC0 or credited), 6 moods, crossfade per act, duck 10-14 dB. (4) Animation: extra poses, light beams, dust, kinetic text synced to words. (5) Hooks: 3 options per script, rubric-scored, scores logged. (6) Auto-fix: rating < 8.5 regenerates the weakest dimension and re-renders only affected scenes (max 3 rounds, 1 when time is short).
Enforced by: factory/hookscore.py + validator (3 hook options, picked = best score); config/audio.yaml, config/style.yaml, qa.check_v2; other items tracked in docs/PROGRESS.md until built
Status: active

## P-004 | 2026-11-08 | workflow
Rule: Speed and delivery. Time budgets: up to 4 min video = 35 min start to delivered files, 10-12 min video = 60 min. Always deliver the 3 files (mp4 + 2 thumbnails); if the budget is nearly used, deliver the best ready version and put the small fix list in docs/PROGRESS.md. Cache every scene/audio chunk/asset by content hash; re-render only changed scenes. Run independent stages in parallel (matrix up to 20), concatenate with ffmpeg -c copy. Slow AI generation (SDXL restyle) builds a reusable cached library once, not per video. QA samples frames, max 3 min, runs alongside rendering, fixes only the weakest scene. Measure every stage into qa/timings.json. First line of every reply = ETA + stage, updated every 10 min. Never lowers resolution, bitrate, fps or audio quality (hard rule 8 stays).
Enforced by: config/preferences.yaml delivery.time_budget_min; qa/timings.json; text-only otherwise
Status: active

## P-005 | 2026-11-08 | workflow
Rule: Before starting ANY task, state the exact total time the whole task will take (minutes, per-stage breakdown, slowest stage), then start immediately without waiting. If the estimate is above the budget given, cut scope to what fits and list what moved to the next job. Update the ETA every 10 minutes. If real time goes more than 20% over the estimate, say so in one line with the reason. P-004 clarification: the 35/60-minute budgets apply to producing a normal video from a title only; one-time build jobs follow the scope the owner gives.
Enforced by: text-only (applied by Claude in every reply)
Status: active

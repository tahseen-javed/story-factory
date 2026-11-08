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

## P-006 | 2026-11-08 | visual
Rule: Premium burned-in captions: 2-4 words at a time, lower third, never over faces, 100 ms pop-in, accent colour on the spoken word; the .srt stays in the release bundle (supersedes the earlier "no captions" text).
Enforced by: config/factory.yaml captions.burned_in=true, captions.max_words=4; assemble.py build_captions; qa text_safety; tests/test_v2.py
Status: active

## P-007 | 2026-11-08 | delivery
Rule: Audio licence + monetization safety. Every audio asset (voice model, music mood, ambience, SFX) needs a licence entry with proof (docs/LICENCES.md, library/audio_licences.json) or delivery fails; only CC0/public-domain/own-code audio is allowed (music, ambience, SFX are synthesised by our own code, so no Content ID match is possible). Each video must pass the monetization checklist: original script, varied scene structure vs previous videos, no long reused segment, no third-party clips, no real-person likeness, facts sourced.
Enforced by: factory/licence.py, factory/monetization.py (finalize gate, categories licence + monetization), config/factory.yaml monetization.*, tests/test_v2.py
Status: active

## P-008 | 2026-11-08 | workflow
Rule: PERMANENT, applies to every video. State exact total time first (P-005), no questions.
A. Owner rating + calibration: owner rated 001 v2 = 5.0 and 001 v2.1 = 7.9 while QA 2.0 said 10/10, so QA was too lenient. docs/QUALITY_LOG.md keeps owner ratings per video; QA reports a calibrated rating (config/qa_calibration.yaml: v2.1 = 7.9 until each known weakness ships). Every next video must beat the previous owner rating (target 8.5+, then 9+). Known weaknesses (docs/PROGRESS.md): captions per P-006, blotchy restyled backgrounds, missing poses/light beams/particles/kinetic text, auto-fix loop, character acting, story payoff. Music stays as is.
B. Characters are always cute and unique: big round heads, large friendly eyes, soft shapes, warm readable colours, expressive faces, never scary or gory (config/style.yaml characters.*, QA factory/cast.py). Every video gets a new cast (outfits, colours, props, silhouette, personality) clearly different from earlier ones; casts and shot lists are logged in library/history.json and a video fails if similarity to any earlier video is above the threshold.
C. Character voices locked and different: config/characters.yaml (engine, voice id/seed, pitch, pace, effects). Same character = same voice in every scene and every video of the series; narrator differs from all characters; with 2+ characters all differ (QA voice fingerprint comparison, factory/voicecheck.py). Allowed sources only: Chatterbox default variants, Kokoro-82M (Apache-2.0) built-in voices, the owner's own recordings. Never clone a real person.
D. Preflight before every video (factory/preflight.py -> qa/preflight.json + 5-line summary): 1 time estimate within budget, 2 licence gate (P-007), 3 monetization checklist, 4 cast cute+unique and voices locked+distinct, 5 caption spec P-006 + background blotch check, 6 previous owner rating loaded and this video's improvements listed. A failed check is auto-fixed and work continues; only a hard impossibility is reported in one line.
Enforced by: config/qa_calibration.yaml, config/style.yaml, config/characters.yaml, factory/cast.py, factory/voicecheck.py, factory/preflight.py, docs/QUALITY_LOG.md, tests/test_p008.py
Status: active

## P-011 | 2026-11-08 | workflow
Rule: FORMAT LOCK. The 4-minute countdown-survival format is the channel format. Every video keeps: runtime 3:45-4:20, one locked narrator voice (config/characters.yaml), second person "you" with a visible countdown clock and a survival meter (hours left, water, phone battery, cash), the same graphic language (sticky notes, phone UI, number cards, red banners), the same music identity, premium captions (P-006), cute characters (P-008 B) with a unique cast per video in the same art style. New videos change the story, topic, characters' details and structure, never the format. Time budget per P-004 (35 min for a 4-minute video). Baseline = 001 v2.1, owner rating 7.9 (P-008), target 8.5+.
IMPROVE every video: (1) hook inside the problem in the first 8 s, specific line, rubric 8+; (2) a visible change every 2-3 s, shots 2-5 s, pattern interrupt every 25-35 s, no static pose over 3 s; (3) LRA >= 5 LU, music ducked, a real 1-2 s silence beat before the biggest reveal, 4 sound layers, about -14 LUFS; (4) consistent style, no blotchy backgrounds, light beams, dust, push-ins/parallax, kinetic text for key numbers; (5) one goal, escalation every 30-40 s, midpoint reversal, hero decision at the climax, an ending that closes the hook loop, one memorable last line; (6) captions per P-006; (7) one soft in-world subscribe line at 45-60% runtime and one at the end, never in the first 20 s, no guilt; (8) 2 thumbnails: cute hero with one strong emotion, one big symbolic object, 3-4 words, readable at 160x90; (9) after each video the owner rating goes into docs/QUALITY_LOG.md, QA is recalibrated to it and one improvement is added for the next video.
TOPICS: original fiction or a clearly labelled illustrated reconstruction told to "you" as a countdown survival situation; no gore, respectful tone, no expert persona, no fake claims. Take the next unused topic from library/topics.yaml (30+, unused-first, never repeat) without asking the owner.
Supersedes every earlier channel and niche rule.
Enforced by: library/topics.yaml, config/characters.yaml (locked narrator), config/factory.yaml (captions, 4-minute lengths), docs/V1_REFERENCE.md, factory.validate and factory.qa checks (pacing, hook, silence, loudness), docs/QUALITY_LOG.md
Status: active

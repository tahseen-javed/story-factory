# PREFERENCES: standing rules (newest wins; imported into CLAUDE.md)

## P-001 | 2026-11-08 | workflow
Rule: No "go" between build phases. Run Phases 0, 0a, 1-6 back to back, fully autonomously, until the factory is complete and the Definition of Done is met. Proof goes to docs/PROGRESS.md; chat gets only a 3-line Roman Urdu update per finished phase. Owner-only steps (browser logins, GitHub secrets, YouTube OAuth, voice recording, music zip) are collected in docs/USER_CHECKLIST.md while building continues with placeholders/test data. Phase 5 feedback is self-judged against QA + scorecard (review questions go to docs/PROGRESS.md). Stop only for an irreversible/leak risk or a total block only the owner can clear (ask in one line). On a usage limit, write the exact next step into docs/PROGRESS.md; "continue" resumes from it. Speed never lowers quality.
Enforced by: CLAUDE.md section 3 (build mode); docs/BUILD_PROMPT.md STANDING RULE P-001; config/preferences.yaml workflow.phase_gating=false (text-only otherwise)
Status: active

## P-002 | 2026-11-08 | workflow
Rule: Quality bar v2 (owner rated v1 5/10). Hook in the middle of danger (first 2 sentences concrete, open loop paid off at the end). No shot longer than 5.0 s (average 3-4 s, framing and camera recipe never repeat back to back). No frozen end card, no placeholder boxes: the last 8 s keep animating and fade out. Burned-in captions (2 lines, 38 chars, word highlight), lip-sync, 4-layer sound with LRA >= 4 LU and >= 3 silence beats. Story acts (hook, act1, act2a, midpoint, act2b, sacrifice, climax, resolution), a pattern interrupt about every 35 s. Delivery folder gets exactly 3 files per video: mp4 + 2 thumbnails.
Enforced by: config/pacing.yaml, config/audio.yaml, config/style.yaml; factory.validate (ACT/INTERRUPT/SILENCE markers, end_screen forbidden, hook check); factory.qa check_v2 (rating 0-10); tests/test_v2.py
Status: active

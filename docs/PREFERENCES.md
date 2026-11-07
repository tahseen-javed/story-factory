# PREFERENCES: standing rules (newest wins; imported into CLAUDE.md)

## P-001 | 2026-11-08 | workflow
Rule: No "go" between build phases. Run Phases 0, 0a, 1-6 back to back, fully autonomously, until the factory is complete and the Definition of Done is met. Proof goes to docs/PROGRESS.md; chat gets only a 3-line Roman Urdu update per finished phase. Owner-only steps (browser logins, GitHub secrets, YouTube OAuth, voice recording, music zip) are collected in docs/USER_CHECKLIST.md while building continues with placeholders/test data. Phase 5 feedback is self-judged against QA + scorecard (review questions go to docs/PROGRESS.md). Stop only for an irreversible/leak risk or a total block only the owner can clear (ask in one line). On a usage limit, write the exact next step into docs/PROGRESS.md; "continue" resumes from it. Speed never lowers quality.
Enforced by: CLAUDE.md section 3 (build mode); docs/BUILD_PROMPT.md STANDING RULE P-001; config/preferences.yaml workflow.phase_gating=false (text-only otherwise)
Status: active

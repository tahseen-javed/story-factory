# Defect prevention (P-017): every defect found becomes a pre-render rule or a pipeline default

| Defect (video, run) | Prevention in the pipeline |
|---|---|
| Cards / HUD / banner over faces (004: 64 findings) | Stage 0 lint + auto-fix before render, reframe fallback (calm framing, characters to the sides), re-lint on the final timeline |
| Music step after a hold or silence beat | bed pinned during the hold, release 1.2 s (audio.yaml hold_release_s), all moods matched to one loudness before the crossfade |
| Music inaudible (003) | bed 17 dB under the voice, A3b MUSIC PRESENT BLOCKER, auto-fix raises the bed |
| Voice stage crashed twice (missing requests, shadowed variable) | end-to-end unit test with a fake recogniser (tests/test_voice.py), dependencies installed in the same step |
| ASR errors reported as voice defects | two-recogniser confirmation (TTS-stage ASR + Whisper small.en); one-sided doubts are MINOR A2-UNCONFIRMED |
| Spelling variants, numbers, compounds, homophones | shared normaliser + SPELL map + compound merge |
| Decision hold flagged as gap / dead window / static | decision_hold windows exempt in gap, dead-window and pacing checks |
| Planned dark scene flagged as black frames | blackout variant exempt while a faint picture remains (luma 3 or more) |
| Test-kind videos failing format-length scorecard rows | test kind exemptions in scorecard.py |
| Doctor skipped when legacy QA holds the video | Doctor runs whenever final.mp4 exists; the gate decides delivery |
| Sentence with a real voice defect | per-sentence reroll counter in job.yaml (seed offset, 4 extra attempts) |
| A3-MUSIC-JUMP 3.3-3.6 LU at chapter changes (005, run 42834012559) | linear 1.5 s crossfade of two uncorrelated beds dips 3 dB; now equal-power 4 s crossfade (audio.yaml music_xfade_s, mix.xfade_ramps, test) |
| Same pose + expression for 4-15 s, 92 V6-STATIC (005) | make_script.rotate(): one character never repeats pose+expression in consecutive shots; check stays MINOR until P-018 Doctor checks are built |
| Rare names misheard/mispronounced (berth B, Penhale; 005) | sentence reroll in job.yaml (reroll: {s0055: 1, s0152: 1}) |
| A3-MUSIC-JUMP 3.6 LU inside one sentence and A3-MUSIC-LOUD 10 dB at 404 s (005 round 2): the synthesised beds swell by themselves | mix.level_bed(): bed loudness flattened over a 3 s window (audio.yaml music_level), before the crossfade; test |
| Chatterbox drops the last syllable of a name at a sentence end (Penhale -> Pen, TTS-stage ASR evidence in meta_7.json) | TTS-side respelling in plan.TTS_REPLACE (script words unchanged), reroll 3 |

Open (next): legacy QA video analysis takes about 25 min per 6 min video (this is what breaks the 15 percent Doctor budget); cache its result by chunk hash so audio-only fixes skip it, and run the Doctor tech and voice scans in parallel jobs.

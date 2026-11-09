# PRO-LEVEL VISUAL STANDARD (P-018, permanent, every video; owner review of 004 = 8.0)

Reason: 004 had too many static two-shots with both characters standing, too little camera movement and scene variety, a weak hook and small meters. Script words never change. P-017: one check, one batch fix, one verify.

## 1. Shot and scene budget (computed per video, never a fixed table, never asked)
M = (script words at the locked voice speed + freezes x 4.5 s + intro/outro) in minutes.
- Shots: M x 12 to M x 15 (target the middle; average 4-5 s; max 8 s only for a freeze card or key reveal). Distinct locations: ceil(M x 3), each from at least 3 angles. Pattern interrupts: one every 15-25 s (about M x 3 minimum).
- Shot sizes: close-ups/reactions >= 15 percent, inserts (props, hands, floor, wall) >= 20 percent, wide/establishing >= 15 percent, no size above 40 percent. Poses >= M x 3, expressions >= M x 2 (each main character: 8+ expressions, 15+ poses). One new music mood segment per act, crossfaded.
- Tense/panic shots 3-4 s, calm 5-6 s. Deviation of the render from the budget by more than 10 percent = MAJOR.
- First progress line: "Video length M min | shots X-Y (target Z) | locations L | pattern interrupts P | freezes F | estimated total production time T"; saved to docs/SHOT_BUDGET_<video>.md (tools/shot_budget.py) and used as the Doctor limits. Reference examples (calibrate once on 003 and the rated videos, then fix): 4 min 48-60 shots / 12-14 locations; 6 min 72-90 / 18-20; 8 min 96-120 / 24-28; 10 min 120-150 / 30-36.

## 2. Shot plan before render (pre-render lint)
Full list first: shot no, time range, line, location, shot type, camera move, action, props, meters, music mood. Every concrete noun/action gets its own visual within 0.5 s of being spoken. Cuts on sentence boundaries or emphasis words (+-0.2 s), never mid-word. Rotate: extreme wide, wide, medium, medium close-up, close-up, extreme close-up (eyes), over-the-shoulder, headlamp POV, top-down, low/high angle, inserts, reaction, cutaway.
Rules: never two consecutive shots with the same framing; the same two-shot (both standing side by side) at most twice in a row and not again within 20 s; same background+framing not within 20 s; at most 3 consecutive shots in one size group.
Camera: every shot moves (no fully static shot over 2 s), eased in-out: slow push-in on tension, hard push-in on freeze holds, pull-back on reveals, pans along walls, parallax layers, subtle handheld drift, rack focus. Characters act (walk, wade, reach, squeeze, climb, crouch, point, hand on wall, shine the lamp, turn, laugh, panic, breathe hard), animation basics (anticipation, follow-through, light squash and stretch). Subtle atmosphere (lamp cone flicker, dust/mist, drips, ripples, reflections, light shafts, vignette) never hiding characters or meters.

## 3. Hook and retention
First frame striking and dangerous with motion from frame 1 (no calm bright establishing shot, no logo/title first). Seconds 0-8: montage of 3-4 tense shots synced to the first narration lines. Open loop within 30 s; pattern interrupt every 15-25 s; escalation every 60-90 s; midpoint twist; each freeze a mini cliffhanger; strong final payoff; calm close with question and subscribe cue. Intensity curve saved per video, no more than 40 s flat in a row. Colour script per act, continuous light inside a location.

## 4. Freeze / decision moments
decision_hold 4.5 s: clean three-option card, calm countdown ring, planted clues visible, slow push-in, music tension bed, no voice, no captions. The reveal visually proves the answer (hard or match cut to the proof shot, pull-back, short payoff beat).

## 5. Mobile legibility
Meters at least 2x the size of 004, high contrast, fixed safe zone top-left, readable at 360p; larger bolder option cards and text; banners/callouts never overlap meters, faces or cards (separate safe zones per overlay type). Captions OFF (P-013).

## 6. Audio (P-014 plus)
Music 17 dB under the voice, +6 dB max in gaps, smooth ducking, mood per act with crossfades, tension bed in freezes, warm release; -14 LUFS +-1, true peak <= -1.5 dBFS. Optional ambience/SFX (drips, rock groan, water lap, footsteps) at least 25 dB below the voice, CC0/generated with a licence record, dropped if the Doctor flags masking.

## 7. Asset bible (build once, reuse)
Turnarounds, expression sets, pose library, props, backgrounds (each location 4+ angles, day/dark variants), lighting presets, UI kit. Identical characters in every shot, cute, no morphing/jitter/warped hands. The same asset framing never within 20 s.

## 8. Doctor additions (one pass, fixtures that must FAIL)
Shot count and shots/min vs budget, location count, repeated framing and composition (frame embeddings), same size group runs, motion energy per shot, static stretches over 2 s, same pose over 4 s, camera moves present and eased, hook check (striking first frame, motion in 8 s, montage), cut alignment to sentence boundaries, noun-to-visual timing, legibility at 360p, overlay overlaps. Fixtures that must fail: static two-shot, calm opening, small meter, overlapping banner, repeated framing.

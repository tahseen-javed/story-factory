# SCRIPT_FORMULA (apply every time; the validator enforces what code can check)

- Word budget: 170 wpm x LENGTH_MIN, +-5% (10 min about 1,700 words). TTS speaks about 190-210 wpm, so real runtime lands a little under the budget; pauses (0.15/0.3/0.8 s) fill the rest.
- Hook 0-45 s: line 1 = time + situation + countdown/stakes. A flash-forward with `banner:"..."` at 20-40 s. At least 3 concrete numbers and one big open question ("?") in the first minute. No greeting, no intro.
- Shots: 2-3 short sentences each (8-16 words). First minute denser (median about 3.5 s). Every shot has motion or inner animation; one overlay at a time.
- Chapters 1.5-2.5 min (pilots 1-2.5). Each opens with the recurring ritual (time card + survival-log update) and ends on a cliffhanger. >= 3 open loops (`// LOOP`), >= 3 planted details paid off (`// PLANT` / `// PAYOFF`), tracker updated every chapter (`track:`), escalating signals, an emotional beat before the climax (`// BEAT`), a twist ending tied to the opening (`// TWIST`).
- Facts: a practical, verifiable fact with an exact number every 30-60 s (>= 8 per 10 min), none repeated from the last 10 videos unless essential. Prefer official sources (Ready.gov, CDC, NOAA, Red Cross). Each fact goes into facts.md with its URL; the validator rejects facts without a source.
- CTA: exactly one in-story spoken "subscribe" sentence at 28-38% of the runtime + `cta:subscribe`; the last shot carries `ov:end_screen("teaser line")`.
- Safety: stylised or off-screen violence only, no gore, mild language, no real weapon/drug/self-harm instructions, survival advice must be safety-positive and sourced. Title and thumbnail must match the content.
- Writing for the ear: short sentences, numbers spelled as words in narration (the time card carries digits), second person present tense.
- Variety engine: rotate opening, ritual, ending, accent, LUT, music set, camera rhythm, transition mix, title card, thumbnail layout, outfit, premise, setting, mystery mechanic and twist type; nothing may repeat from the last 10 videos (library/history.json).
- Self-review once against this list before pushing.

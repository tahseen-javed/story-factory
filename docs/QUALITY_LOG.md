# QUALITY LOG: owner ratings per video (the only ground truth; QA is calibrated to it)

| Video | Version | Owner rating | QA 2.0 raw | Calibrated QA | Notes |
|---|---|---|---|---|---|
| 001 Solar Storm Blackout | v1 | n/a | n/a | n/a | first pilot |
| 001 Solar Storm Blackout | v2 | 5.0 | 10.0 | n/a | owner said too flat; QA was too lenient |
| 001 Solar Storm Blackout | v2.1 | 7.9 | 10.0 | 7.9 | known weaknesses: captions (P-006), blotchy restyled backgrounds, missing poses/light beams/particles/kinetic text, no auto-fix loop, character acting, story payoff |
| 002 Last Ferry | 4-min v4 | pending (owner to rate) | 9.1 | 7.0 | inserts + second camera angle + new poses + one real silence beat; measured scene changes still only 24 in 218 s (target 62+), 7 TTS sentences below 97% ASR |

Rule: every next video must beat the previous owner rating (target 8.5+, then 9+). Add the owner's number here as soon as it is given.

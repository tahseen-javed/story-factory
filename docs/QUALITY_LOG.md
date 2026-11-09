# QUALITY LOG: owner ratings per video (the only ground truth; QA is calibrated to it)

| Video | Version | Owner rating | QA 2.0 raw | Calibrated QA | Notes |
|---|---|---|---|---|---|
| 001 Solar Storm Blackout | v1 | n/a | n/a | n/a | first pilot |
| 001 Solar Storm Blackout | v2 | 5.0 | 10.0 | n/a | owner said too flat; QA was too lenient |
| 001 Solar Storm Blackout | v2.1 | 7.9 | 10.0 | 7.9 | known weaknesses: captions (P-006), blotchy restyled backgrounds, missing poses/light beams/particles/kinetic text, no auto-fix loop, character acting, story payoff |
| 002 Last Ferry | 4-min v4 | pending (owner to rate) | 9.1 | 7.0 | inserts + second camera angle + new poses + one real silence beat; measured scene changes still only 24 in 218 s (target 62+), 7 TTS sentences below 97% ASR |

| 003 Three Button Trap (40 s test, 46.9 s) | test kind | 8.8 (owner, FINAL) | n/a | n/a | lost points ONLY for having no background music. Voice, visuals, pacing, decision hold, no captions = GOLDEN BASELINE for all future videos (format locked, P-011/P-014). |
| 004 Sea Cave (6:16, delivered by one-time owner override, no certificate) | v1 | 8.0 (owner) | n/a | n/a | too many static two-shots with both characters standing, too little camera movement and scene variety (7 locations instead of ~19), weak hook, small meters. Music, voice and meters following the narration worked. Led to P-018. |

Rule: every next video must beat the previous owner rating (target above 8.8, i.e. 9.0+). Add the owner's number here as soon as it is given.

# Doctor calibration (P-017): false alarms are checker bugs, fixed once

Golden baseline: 003 (owner 8.8). Evidence: 003 and 004 Sea Cave (147 sentences, 6:16). A good video must give zero MAJOR/BLOCKER false alarms. Change a threshold only together with a row here and a test.

| Date | False alarm (run) | Cause | Fix | Test |
|---|---|---|---|---|
| 2026-11-09 | map maker vs mapmaker = A2-SKIP/CHANGED (42657994372) | recogniser writes compounds as one word | compounds merged on both sides before alignment | tests/test_voice.py |
| 2026-11-09 | Walt's vs waltz = A2-CHANGED | homophone | homophone map in voice.py | tests/test_calibration.py |
| 2026-11-09 | A2-DRIFT on 9-10 same-voice sentences (mel up to 6 dB, f0 up to 81 Hz) | per-sentence fingerprint depends on words and prosody | coarse outlier detector: 9 dB / 100 Hz, narrator 9 / 70 | tests/test_calibration.py |
| 2026-11-09 | A3-MUSIC-JUMP after every silence beat / hold | 3 s window smears a release; release was 0.35 s | jump zone 5 s; hold release 1.2 s (audio.yaml hold_release_s) | tests/test_calibration.py |
| 2026-11-09 | A4-HOTSTART on a 0.3 s fade-in | 100 ms window | 30 ms window | tests/test_doctor.py |
| 2026-11-09 | A2-CLIP / A4-STEM-CLIP BLOCKER | stems are pre-limiter | MINOR; master clipping stays BLOCKER | tests/test_doctor.py |
| 2026-11-09 | CTA sticker flagged over a face | guessed box too big | box (80,830)-(800,975) | tests/test_doctor.py |
| 2026-11-10 | A2-CHANGED berth->birth (005, run 42848053013) | berth and birth are homophones | homophone map in voice.py SPELL | tests/test_calibration.py |
| 2026-11-10 | A3-MUSIC-JUMP 3.3-5.4 LU inside long sentences (005, runs 42834012559/42848053013) | 0.4 s momentary loudness of a note-based bed swings +-2 LU with note onsets; not an audible level step | jump measured between adjacent 1 s block means (a real +8 dB step still fails) | tests/test_calibration.py |
| 2026-11-10 | A3-MUSIC-LOUD 10.2-10.7 dB at 404-407 s (005 round 2) | window 0.6-0.7 speech fraction at the end of the last sentence reads the voice low while the bed rises by design | local loudness check needs speech fraction >= 0.8 (fixture music +8 dB still fails) | tests/test_doctor.py test_30 |

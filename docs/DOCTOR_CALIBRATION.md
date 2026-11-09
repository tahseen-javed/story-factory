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

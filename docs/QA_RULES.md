# QA_RULES (code: factory/validate.py, factory/images.py, factory/tts.py, factory/qa.py, factory/fixers.py, factory/thumbnails.py)

| Stage | Check | Threshold | Auto-fix |
|---|---|---|---|
| Script gate (prepare) | vocabulary, locations/characters declared, 1 overlay/shot, zoom 1.0-1.35, shot 1.2-8 s, words 170 x min +-5%, hook (no greeting, >= 3 numbers, "?", banner 20-40 s), CTA 28-38%, chapters, tracker per chapter, markers, facts with sources, readability, repeated sentences, content blocklist, prompt denylist, preferences | errors block | none (needs_review: rewrite script) |
| TTS | ASR round trip WER per sentence, duration 0.6-1.6x expected | WER <= 8% | regenerate with new seed (max 3), keep best, flag |
| Images | OCR garbage text, near-duplicate (phash), CLIP relevance (>= 0.14 cosine) | fail = regenerate (max 2 more) | new seed; else procedural backdrop + QA warning |
| Assemble | camera zoom 1.0-1.35 and 2-8 %/s, no image upscaling beyond 1.0x stored source (3024 px), shots <= 8 s | clamp | rewrite camera, split long shots |
| Audio | -14 LUFS +-1, true peak <= -1 dBTP, sample peak < -0.1 dB, LRA <= reference + 1.5, silences <= 1.2 s by construction | | re-master (loudnorm 2-pass) |
| Render | 1920x1080, 30 fps, H.264 yuv420p CRF 18, AAC 48 kHz 192 kbps, duration within 0.3 s of plan | | re-render chunk |
| Video | blackdetect, freezedetect (end screen exempt), motion share >= 0.88 (optical flow per shot), flashes <= 3/s, cut vs sentence start <= 2 frames | | camera rewrite / remove flash FX / re-render affected chunks (max 2 rounds) |
| Captions | SRT monotonic, inside runtime | | rebuild |
| Thumbnails | >= 8 candidates scored (OCR at 168x94, contrast, warm/cool separation, saliency, clutter, clear corner) best 2 | score >= 0.62 | regenerate with mutated layout/accent |
| Scorecard | beat or match the reference on every measured dimension (factory/scorecard.py) | | needs_review |

Result: `qa_report.json` (artifact `qa-report`), `scorecard.txt`, `contact.jpg`. A video ships only if every category passes; otherwise `needs_review` (not delivered) and a one-line issue is opened. `python tools/qa_summary.py <slug>` prints max 30 lines.

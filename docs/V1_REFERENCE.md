# V1_REFERENCE: measured facts about the 4-minute format (source of truth for P-011)

Measured 2026-11-08 with ffprobe/ffmpeg (ebur128 loudness, scene-cut detection scene>0.30 at 320 px). The original v1 file was overwritten by v2, so v1 values are the owner's recorded measurements.

## Format
| | v1 (owner measurements) | v2.1 (owner rating 7.9, measured) | outside reference (measurement only) |
|---|---|---|---|
| Video | 1920x1080, 30 fps | 1920x1080, 30 fps, H.264 High, 8.8 Mbps | 1280x720, 30 fps, H.264 Main, 0.6 Mbps |
| Audio | AAC 48 kHz stereo | AAC 48 kHz stereo | AAC 44.1 kHz stereo |
| Duration | 264.7 s | 227.5 s | 590.9 s |
| Loudness | -14.2 LUFS | -14.2 LUFS | -14.6 LUFS |
| Loudness range | 1.4 LU (too flat) | 4.7 LU | 3.5 LU |
| True peak | -1.9 dBFS | -1.7 dBFS | -1.0 dBFS |
| Hard scene changes | about 27-31 (about one per 10 s) | 23 in 227 s (avg 9.5 s; 9 gaps over 8 s; longest 38.1 s) | 115 in 591 s (avg 5.1 s) |

Locked runtime for every video: 3:45 to 4:20.

## Structure (the format to keep)
- Second-person countdown survival story: "you" are one ordinary person; a visible clock (for example 15:00:00 UNTIL IMPACT) drives hour-by-hour beats.
- A survival log / meter that updates every chapter (hours left, water, phone battery, cash).
- Red "FLASH FORWARD" banners, sticky-note rules ("RULE 2: CASH", "3B Check on Mara"), phone UI alerts (red UPDATE card), big number cards (for example "4 G5 storms per solar cycle").
- A neighbour partner character (an older woman in a purple cardigan) who becomes the emotional partner; a twist that closes the opening question.

## Look
Hand-drawn painted dark cinematic backgrounds, colour moving from warm to cold to dusky purple, consistent ink outlines. Hero: small round character in a teal cap with glasses and yellow hands (cute per P-008 B; a unique cast per video in the same art style).

## Sound and voice (locked in config/characters.yaml)
- Narrator: Chatterbox TTS (ResembleAI/chatterbox, MIT) default voice, no cloning; seed 1234, exaggeration 0.5, cfg_weight 0.5, temperature 0.75, speed 1.0, 24 kHz native, every sentence normalised to -21 dBFS RMS. The outside reference voice is not used or imitated.
- Voice chain: high-pass 80 Hz, EQ (-2 dB at 250 Hz, +2 dB at 3.2 kHz, +1 dB at 9.5 kHz), de-esser 5-9 kHz, compressor 3:1 with 3 dB make-up, small room reverb (7% indoor, 13% outdoor), two-pass loudnorm to -14 LUFS, true peak limit, AAC 192 kbps 48 kHz.
- Music identity: original synthesised beds from factory/synth.py (dread, urgent, climax, calm, tense, sorrow, hopeful), crossfaded per act, ducked 12 dB under the voice; SFX and ambience also from our own code (docs/LICENCES.md).
- Captions: P-006 (2-4 words, lower third, never over faces).

## Measured weaknesses to fix next (v2.1 = 7.9)
1. Visible change is too slow: 23 scene changes in 227 s (avg 9.5 s, 9 gaps over 8 s, longest 38.1 s); most beats only reframe the same background. Target a visible change every 2-3 s with 2-5 s shots and new backgrounds or inserts.
2. Loudness range 4.7 LU (v1 was 1.4); target at least 5 LU with a real 1-2 s silence before the biggest reveal.
3. Static poses and thin acting; sound design still only 4 simple layers.
4. Blotchy backgrounds from the posterise/palette pass; consistency between scenes still uneven.
5. Hook and ending: the hook does not start inside the problem fast enough; the ending does not land one memorable last line (owner rating 7.9, docs/QUALITY_LOG.md).
6. Captions: pop-in (100 ms) and accent-colour spoken word are not implemented yet (P-006).
7. Missing: light beams, dust/particles, kinetic text for key numbers, auto-fix loop.

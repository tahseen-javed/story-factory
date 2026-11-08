# LICENSES (every model, package, font and asset; commercial use verified)

Rule: only licences that allow commercial use. Anything else is listed under REJECTED and never added.
Checked 2026-11-08. If a licence or model page changes, switch to the configured fallback (config/factory.yaml).

| Component | Use | Licence | Notes |
|---|---|---|---|
| Chatterbox (original, Turbo, Nano) by Resemble AI | TTS | MIT | PerTh watermark kept; PyPI chatterbox-tts==0.1.7 |
| Kokoro-82M | TTS fallback | Apache-2.0 | |
| SDXL-Lightning (ByteDance) + SDXL base 1.0 | backgrounds | OpenRAIL++ (CreativeML Open RAIL++-M) | commercial use allowed; use restrictions honoured |
| Depth-Anything-V2-Small | depth layers | Apache-2.0 | Base/Large are CC-BY-NC: REJECTED |
| sherpa-onnx + Moonshine (English, int8) | ASR check | Apache-2.0 / MIT | |
| Silero VAD | voice activity | MIT | |
| open_clip (ViT-B-32) | relevance / similarity | MIT | OpenCLIP weights: MIT |
| rembg (u2netp) | prop cutouts | MIT | |
| RapidOCR (onnxruntime) | garbage-text OCR | Apache-2.0 | |
| imagehash | perceptual hash | BSD-2-Clause | |
| all-MiniLM-L6-v2 | script similarity | Apache-2.0 | |
| LAION aesthetic predictor head | thumbnail score | MIT | on CLIP embeddings |
| Remotion | rendering | Remotion licence (free for individuals and companies of up to 3 people) | revisit if the team grows |
| React, TypeScript | video code | MIT | |
| ffmpeg (GPL build from apt) | encode / mix / QA | LGPL/GPL, tool only (not linked) | no code redistributed |
| age (FiloSottile) | artifact encryption | BSD-3-Clause | |
| git-crypt | repo encryption | GPL-3.0, tool only | |
| OpenCV (headless) | optical flow | Apache-2.0 | |
| numpy, scipy, Pillow | image/audio maths | BSD / HPND | |
| PyYAML | config | MIT | |
| Fonts: Permanent Marker, Patrick Hand, Caveat, Inter, Montserrat | on-screen text | SIL OFL 1.1 | files in video/public/fonts with their OFL texts |
| Music and SFX (placeholder set) | audio | original, synthesised by factory/synth.py | no third-party material; owner licence = ours |
| Voice (placeholder) | narration | Chatterbox built-in default voice (no cloning) | replace via voices/default.wav or voices/me.wav |

## REJECTED (never add)
- Depth-Anything-V2 Base / Large (CC-BY-NC-4.0)
- Any non-commercial model, dataset, font or sound (CC-BY-NC, research-only, "personal use only")
- Any attribution-required music unless the description auto-adds the credit (current policy: no-attribution only)
- Cloning of any voice that is not the owner's own recording or a CC0 / explicitly commercial-use sample
- Music library (factory/musiclib.py): 6 moods rendered by our own synthesiser (original code, no third-party audio), dedicated CC0; cached and reused (P-003).

# Licences of the Video Doctor dependencies (P-012, zero cost)

| Dependency | Use | Licence | Commercial use |
|---|---|---|---|
| numpy 1.26.4 | audio/loudness maths | BSD-3-Clause | yes |
| scipy 1.13.1 | filters, smoothing | BSD-3-Clause | yes |
| soundfile 0.12.1 (libsndfile) | read/write WAV stems | BSD-3-Clause / LGPL-2.1 (dynamic link, not redistributed) | yes |
| ffmpeg (apt, GitHub runner) | decode final mp4 audio, blackdetect, ffprobe | LGPL-2.1+/GPL (used as external tool, not redistributed) | yes |
| faster-whisper 1.x + Whisper base.en weights | voice check vs script (Phase 2) | MIT (code and weights) | yes |
| Pillow 10.4 | background look check | HPND (permissive) | yes |
| Python stdlib | certificate, YAML subset reader, orchestration | PSF | yes |
| BS.1770-4 / EBU R128 loudness | own implementation in factory/doctor/lufs.py (published ITU algorithm) | own code | yes |

No model weights, no paid API, no hosted service. Phase 2 additions (Whisper, embeddings) must be added here with their licence before use.

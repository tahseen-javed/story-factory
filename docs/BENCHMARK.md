# BENCHMARK (real GitHub runner measurements; benchmark.yml refreshes and retunes matrix sizes)

Runner: ubuntu-latest, AMD EPYC 7763, 4 vCPU, 16 GB RAM, no GPU (2026-11-08 probe).

| Task | Result |
|---|---|
| Chatterbox original, 1 sentence | 14-29 s per 1.5-3.6 s of audio (RTF 8-13), peak RSS 6.9 GB, model load 36 s |
| Moonshine base int8 ASR | 0.22-0.29 s per sentence |
| SDXL-Lightning fp32 1344x768 | 267-297 s per image, peak RSS 14.4 GB, load 137 s (bf16 rejected: slower on this CPU) |
| Remotion 1080p30 (SVG scenes) | about 8 fps with 4 workers incl. Chrome start |

Matrix defaults: tts 8 shards, images 7 shards, render 30 s chunks. Expected for a 4-minute video: TTS about 12 min wall, images about 15 min wall (parallel), render about 5 min, finalize about 10 min.

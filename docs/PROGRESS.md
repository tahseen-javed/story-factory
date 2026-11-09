# PROGRESS (proof per phase; chat only gets a 3-line summary)

Last updated: 2026-11-08 (UTC 20:15). Repo: https://github.com/tahseen-javed/story-factory (public).

## NEXT STEP (exact, for "continue")
1. Check the pilot run: `gh run list --workflow produce.yml --limit 3` (last dispatched: run 42415916779, pilot/solar-storm-blackout). If status ok, run `tools/fetch.cmd` to deliver "001 Solar Storm Blackout 04min" (5 files) into Documents\Animated Long Video 1st Channel and verify them.
2. If needs_review: `python tools/qa_summary.py latest`, fix, re-dispatch (`gh workflow run produce.yml -f job_dir=pilot/solar-storm-blackout -f until=all`; TTS and images are cached).
3. Then: Phase 0a reference analysis (needs owner secrets), Phase 4 report, Phase 5 self-review, Phase 6 batch (/batch, 5 videos).

## Placeholders in use (replace when the owner finishes docs/USER_CHECKLIST.md)
- Voice: Chatterbox built-in default voice (no cloning). Switch: put voices/me.wav or voices/default.wav, set tts.voice.
- Music + SFX: original, synthesised by factory/synth.py (no third-party audio).
- Reference scorecard: PROVISIONAL numbers from the owner's own measurements (config/factory.yaml: reference.*) until analyze_reference.yml can decrypt reference/reference.mp4 (needs GIT_CRYPT_KEY secret).
- Pilot video lives in public `pilot/solar-storm-blackout` (GitHub secrets cannot be set by Claude). Deliverables are age-encrypted to the public recipient and fetched normally.

## Phase 0 (scaffold, security, CI): done
- Repo public, git-crypt initialised, hooks (.githooks), settings, preferences (P-001), CI green (unit, risk-check, 20 s smoke render).
- Security: secret scanning + push protection on, workflow default perms read, fork PR approval, main protected (no force push/delete).
- Remaining risk: owner must add GIT_CRYPT_KEY / BACKUP_KEY secrets before any encrypted `jobs/` run; key backup is offline owner duty.

## Phase 1 (style, rig, overlays, camera): done (v1)
- Original "Paper Crew" puppet rig, 14 poses, 10 expressions, 20 overlays, 12 camera presets, 8 FX, procedural backdrops. CI artifact `smoke-contact` (rigsheet.png + contact.png).
- Remaining risk: visuals are v1; backdrops use SDXL when available; blackout variants were too dark (brightened in v2).

## Phase 2 (voice, ASR, benchmark): measured
- Chatterbox (CPU, 4 vCPU): ~8-13x real time per sentence, 6.9 GB RSS, model load 36 s. Moonshine ASR 0.25 s per sentence. TTS WER in pilot: 0.0 on all checked sentences.
- SDXL-Lightning fp32 CPU: 267-297 s per 1344x768 image, 14.4 GB peak RSS on 16 GB runner; bf16 is slower on EPYC 7763 (rejected). Text encoders are freed before the UNet loads.

## Phase 3 (end-to-end pilot): DONE 2026-11-08
- Pilot "001 Solar Storm Blackout 04min" (4:25, 1920x1080 30 fps H.264 8 Mbps, AAC 192k) built fully on GitHub (run 42416889542), delivered with tools/fetch_videos.ps1 into Documents\Animated Long Video 1st Channel (5 files, exact names).
- QA pass (all categories): -14.3 LUFS, TP -1.8 dBTP, LRA 1.3, motion share 0.99, flash 0.5/s, A/V sync 0 frames, TTS mean WER 0.017, thumbnails 0.96 / 0.88, scorecard ok (reference numbers provisional).
- Remaining risk: placeholders (voice, music) and public pilot script; TTS has a few ASR-flagged sentences (truncated word endings) accepted under the 5% rule; per-sentence repair loop is the next improvement.

## v2 quality upgrade: DONE 2026-11-08 (run 42464375998, QA 2.0 rating 10/10, status ok)
- Before -> after: shots 31 -> 73 (18.6/min), avg shot 8.5 s -> 3.2 s, max shot 59 s -> 4.8 s, LRA 1.4 -> 4.8 LU, silence beats 0 -> 3, frozen end card 16 s -> none (8 s moving tail + fade), -14.3 LUFS, TP -1.7.
- New: factory/beats.py, burned-in captions, lip-sync, HUD, 10 framings, 6 transitions, story-arc grades, 4-layer audio, QA 2.0 (qa.check_v2), tests/test_v2.py. Delivered: mp4 + 2 thumbnails only (P-002).
- Deferred (honest): SDXL restyle + palette-histogram QA (look unity is a Remotion posterise + grade pass), hook 3-option scorer, new poses/ambience variety, auto-regenerate-weakest-dimension loop, light beams / screen glow, kinetic keyword text.

## v2.1 status (P-003/P-004 saved 2026-11-08)
- Done now: P-003 + P-004 saved; hook rubric (factory/hookscore.py, 3 options + pick enforced by validator, scores in build/<slug>/hook_log.json; shipped hook scored 9.75 vs 8.0 / 4.4); qa/timings.json.
- Measured timings (v2 run, caches warm): render 863 s, finalize/QA 575 s, thumbs 85 s, assemble 60 s, images 15 s, TTS 12 s (cache). Full re-render = ~25 min. Slowest stages to shorten next: render (more chunks, max 20) and finalize (sample-frame QA, run beside render).
- NOT done (needs its own ~30+ min job each; v2 files stay delivered): SDXL img2img restyle library (0.35-0.45) + palette-histogram QA; ASR >= 97% re-synthesis loop for the 4 flagged sentences (voice is already Chatterbox, default voice); licence-safe music library; extra poses, light beams, kinetic text; auto-fix loop on rating < 8.5 (rating is already 10.0).
: DONE (tests/test_faults.py: black, freeze, static motion, flash, resolution, quiet and clipped audio + loudnorm re-master fixer; CI green).
## Phase 0a / 5 / 6: waiting for owner secrets (docs/USER_CHECKLIST.md); then analyze_reference.yml, first encrypted jobs/ video, /batch of 5.

## 2026-11-09 | P-012 Phase 1 DONE (CI run 42581159381 green: unit, doctor, cost-audit, smoke, risk-check)
- Built: certificate gate (sha256, anti-bypass, bundle + fetch verify), audio Doctor on final mix + fix loop (max 3), face-overlap lint + auto-fix (props.json, Remotion honors ovShift/ovScale/hudRight/bannerDy), 5 fixtures + clean (tests/test_doctor.py), zero-cost audit, wired into produce.yml (assemble: Stage 0+1, finalize: Stage 2 + gate) and refinalize.yml.
- Stage 2 audio scan: 7.4 s per 240 s on CI (29.9 s locally). Captions OFF (P-013) in place.
- Not yet proven on a real production mix: first real run is video 003. Known limits: OTS foreground character is exempt from the face-edge check (cropped by design); A1-GAP and V4-BLACK have no auto-fix (-> NEEDS_REVIEW, no certificate); calm_* thresholds uncalibrated.
- Phase 2 NOT started: wait for the owner's message.

# PROGRESS (proof per phase; chat only gets a 3-line summary)

Last updated: 2026-11-08 (UTC 20:15). Repo: https://github.com/tahseen-javed/story-factory (public).

## NEXT STEP (exact, for "continue")
1. Check the pilot run: `gh run list --workflow produce.yml --limit 3`. If finished OK, run `tools\fetch.cmd` (or /fetch) to deliver
   "001 Solar Storm Blackout NNmin" into Documents\Animated Long Video 1st Channel and verify the 5 files.
2. Then continue: Phase 0a reference analysis (needs owner secrets, see USER_CHECKLIST), Phase 2 benchmark, Phase 4 fault injection, Phase 5 self-review, Phase 6 batch.

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

## Phase 3-6: in progress (pilot run is the end-to-end proof)

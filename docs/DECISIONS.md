# DECISIONS (never re-debate; newest at the bottom)

## 2026-11-08 | Repo and identity
Repo `tahseen-javed/story-factory`, PUBLIC forever. Commits use repo-local identity tahseen-javed + GitHub noreply email. git-crypt key lives in `.git/git-crypt` and a copy in `%USERPROFILE%\.story-factory\git-crypt.key` (outside repo, never read by Claude).

## 2026-11-08 | age keys
`age` identity at `%USERPROFILE%\.story-factory\backup.key` (local, never in repo). Its PUBLIC recipient is committed in config/factory.yaml (`delivery.age_recipient`), so CI can ENCRYPT deliverables without any secret; only the owner's laptop (and the BACKUP_KEY secret, once the owner adds it) can decrypt.

## 2026-11-08 | Pilot mode (no secrets yet)
GitHub secrets can only be set by the owner (browser). Until GIT_CRYPT_KEY / BACKUP_KEY exist, CI cannot read `jobs/`. Tonight's first video therefore lives in `pilot/<slug>/` (public, unencrypted, original content written for the pilot, contains no owner data); its deliverables are age-encrypted to the public recipient and fetched with the normal fetch script. Production jobs always use encrypted `jobs/`. Preflight refuses `jobs/` runs when GIT_CRYPT_KEY is missing, and switches automatically once it is set.

## 2026-11-08 | Branch protection
Only "no force-push, no deletion" on main (no PR requirement), because the workflow is "push script -> factory runs".

## 2026-11-08 | Placeholders
Voice: Chatterbox built-in default voice (no cloning) until voices/default.wav or voices/me.wav exists. Music and SFX: original, procedurally synthesised by our own code (no third-party licence). Reference scorecard: provisional metrics from the owner's measurements until analyze_reference.yml can decrypt the real reference.

## 2026-11-08 | Background resolution
SDXL-Lightning renders 1344x768; backgrounds are upscaled 2.25x to 3024x1728 (Lanczos + detail pass) so zoom 1.35 with 12% overscan never exceeds 1.0x of the stored source.

## 2026-11-08 | Delivery space guard and bitrate
min_free_gb lowered 30 -> 15: the laptop had 27 GB free, so the 30 GB guard would block every delivery; a video bundle is about 300 MB. Final video pass: H.264 High CRF 18 maxrate 9M (grain made raw chunks 16 Mbps = 515 MB for 4.4 min), preset medium (slow was too slow for a 30-minute video on 4 vCPU; no visible difference at this bitrate).

## 2026-11-08 | Quality upgrade v2
Pacing is solved in code, not by the script author: factory/beats.py splits every authored shot into beats (target 3.8 s, hard cap 5.0 s) at sentence/clause cuts and assigns framing, camera recipe, transition and acting per beat with a seeded RNG. Camera in the script is now optional. End card removed (validator forbids ov:end_screen); the last 8 s are a real scene with a 1 s fade. Look unity is a Remotion-side pass (shared posterise filter + story-arc colour grade from config/style.yaml) so cached SDXL backdrops are reused; a full restyle of the SDXL prompts and a palette-histogram QA are deferred. Delivery: exactly mp4 + 2 thumbnails in the channel folder (owner request).
- P-021 2026-11-12: calm quiet soft-pad music beds, 21 dB under voice; 006 and 007 re-mixed via refinalize (owner: first beds noisy)

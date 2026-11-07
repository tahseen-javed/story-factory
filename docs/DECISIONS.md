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

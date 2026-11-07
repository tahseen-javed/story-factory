# SETUP_SECRETS (browser only; the exact click list is in docs/USER_CHECKLIST.md step 1)

Secrets live only in GitHub Secrets: `GIT_CRYPT_KEY` (base64 of the git-crypt key), `BACKUP_KEY` (age identity), `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.
- Local copies: `%USERPROFILE%\.story-factory\git-crypt.key` and `backup.key` (never in the repo, never read by Claude). Keep an offline backup.
- Unlock a fresh clone: `git-crypt unlock %USERPROFILE%\.story-factory\git-crypt.key`.
- Rotate: generate a new age key (`age-keygen`), update `delivery.age_recipient` in config/factory.yaml and the BACKUP_KEY secret; old bundles need the old key.
- Preflight (produce.yml) stops an encrypted job with one clear line when a secret is missing.

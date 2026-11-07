# SETUP_LOCAL: laptop setup (Windows)

Only three tools are needed locally. Nothing heavy (no node_modules, no pip installs, no models, no renders).

| Tool | Status (2026-11-07) | Action |
|---|---|---|
| Git for Windows | installed (2.55.0) | none |
| GitHub CLI (gh) | installed (2.97.0), logged in | none |
| Python (stdlib only, for local validator) | installed (3.12.10) | none |
| git-crypt | MISSING | install below |

## Install git-crypt (one command, small download)
```
winget install AGWA.git-crypt
```
Then open a new terminal and check: `git-crypt --version`.
Fallback if winget fails: `winget install ja-ortiz-uniandes.git-crypt-unofficial` (unofficial build, use only if the official one fails).

## Later (done by Claude in Phase 0, no action from you)
- `git config core.hooksPath .githooks` (pre-commit and pre-push run `git-crypt status -e`).
- `git-crypt init`, key export, upload as GitHub secret GIT_CRYPT_KEY: see docs/SETUP_SECRETS.md (browser steps only).
- Portable `age.exe` for /fetch is kept outside the repo in `%USERPROFILE%\.story-factory\`.

## Notes
- ffmpeg and Node are already on this laptop; the factory does not use them locally. Never run `npm install` or `pip install` in the project folder.
- Local footprint cap: 300 MB (target under 100 MB). Check with `python tools/disk_report.py` (created in Phase 0).

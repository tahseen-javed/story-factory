# BACKUP and restore

- Everything except encrypted content is in the public repo. Encrypted content (scripts, voices, reference, history) needs `git-crypt.key`; bundles need `backup.key`. Keep both offline (USB / password manager).
- mirror.yml (manual) pushes the repo, still encrypted, to a second free git host (set `MIRROR_URL` + `MIRROR_TOKEN` secrets first).
- Restore: `git clone <repo>` -> `git-crypt unlock git-crypt.key` -> `tools\fetch.cmd` re-downloads bundles from Releases (needs backup.key).
- Release bundles older than 30 days that are fetched and uploaded can be removed by cleanup.yml (never the reference or library assets).

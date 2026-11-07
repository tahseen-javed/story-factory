# USER CHECKLIST: everything only YOU can do (one list, exact clicks)

Building continues without these (placeholders are in place). When you finish a step the factory switches over automatically.
After steps 1-2, type `continue` in Claude Code.

## 1. GitHub secrets (10 minutes, browser only) - unlocks production jobs and the reference analysis
Two text files are already prepared for you in `C:\Users\Hp Pro Book\.story-factory\` : `SECRET_GIT_CRYPT_KEY.txt` and `SECRET_BACKUP_KEY.txt`.
1. Open https://github.com/tahseen-javed/story-factory/settings/secrets/actions (log in if asked).
2. Click **New repository secret**.
3. Name: `GIT_CRYPT_KEY`. Secret: open `SECRET_GIT_CRYPT_KEY.txt` in Notepad, Ctrl+A, Ctrl+C, paste. Click **Add secret**.
4. Click **New repository secret** again. Name: `BACKUP_KEY`. Secret: open `SECRET_BACKUP_KEY.txt` in Notepad, Ctrl+A, Ctrl+C, paste. Click **Add secret**.
5. Delete both `SECRET_*.txt` files afterwards (the real keys stay: `git-crypt.key` and `backup.key` in the same folder). **Keep an offline copy of those two key files** (USB stick or password manager). Losing them means losing every script and bundle.

## 2. YouTube upload (30-40 minutes, browser only) - see docs/SETUP_YOUTUBE.md for screenshots-free detail
1. https://console.cloud.google.com -> project selector -> **New project** -> name `story-factory` -> Create.
2. Left menu **APIs & Services -> Library** -> search **YouTube Data API v3** -> **Enable**.
3. **APIs & Services -> OAuth consent screen** -> User type **External** -> fill app name `story-factory`, your email -> Save. Scopes: add `.../auth/youtube.upload` and `.../auth/youtube.force-ssl`. Add your Google account as a **Test user**, then click **Publish app** so the status is **In production** (otherwise the token dies after 7 days).
4. **APIs & Services -> Credentials -> Create credentials -> OAuth client ID** -> type **Web application** -> Authorized redirect URI: `https://developers.google.com/oauthplayground` -> Create. Copy the **Client ID** and **Client secret**.
5. https://developers.google.com/oauthplayground -> gear icon (top right) -> tick **Use your own OAuth credentials** -> paste Client ID and secret.
6. In the left list type `https://www.googleapis.com/auth/youtube.upload` and `https://www.googleapis.com/auth/youtube.force-ssl` -> **Authorize APIs** -> choose your channel account -> Allow (click Advanced -> continue if Google warns).
7. **Exchange authorization code for tokens** -> copy the **Refresh token**.
8. Add three more repository secrets (same page as step 1): `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.
Uploads are always PRIVATE; you publish from YouTube Studio.

## 3. Your voice (optional but recommended, 5 minutes) - see docs/SETUP_VOICE.md
Until then every video uses Chatterbox's built-in default voice (clearly marked as placeholder in docs/PROGRESS.md).
1. Quiet room, phone 20 cm from your mouth, record 60 seconds reading the text in docs/SETUP_VOICE.md.
2. Send the file to the laptop, rename it `me.wav` (WAV) and copy it into `D:\Claude projects\Animated Video Creation Factory no 1\voices\` .
   (Do NOT upload it on github.com: only Claude's git commit encrypts it.)
3. Type `continue`; Claude runs the voice audition and sets `tts.voice: me` if you pick it.

## 4. Music library (optional, 20 minutes) - see docs/SETUP_MUSIC.md
Until then the factory uses its own synthesised placeholder music and sound effects (original, no licence issue).
1. YouTube Studio -> Audio library -> download ~30 tracks marked "no attribution required" plus a few free sound effects.
2. Put them in one zip. Drag the zip onto `tools\pack_music.cmd` (it encrypts the zip with your public key).
3. GitHub -> Releases -> **Draft a new release** -> tag `library-music-v1` -> attach the `.age` file -> Publish.

## 5. Housekeeping (when you like)
- The original reference video in `C:\Users\Hp Pro Book\Downloads\reference video .mp4` is safely stored (encrypted) in the repo; you may delete the download copy (Claude will not do it without your yes).
- Tonight's pilot video uses a public script (`pilot/solar-storm-blackout`) because secrets were not set yet; delete that folder any time. From now on scripts go into encrypted `jobs/`.
- GitHub account check: this project uses only `tahseen-javed` (git identity for this repo is set to it).

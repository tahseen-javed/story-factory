# CLAUDE.md: story-factory master rulebook

Owner: Hafiz Tahseen Javed. Channel folder: "Animated Long Video 1st Channel".
This file is loaded in every session. It is the permanent rulebook for building and running the factory.
Precedence when rules clash: my latest chat message > docs/PREFERENCES.md > this file > docs/* > the original build prompt.
This file replaces the "CLAUDE.md under 60 lines" rule from the build prompt. Keep it under 300 lines; move long specs to docs/.

My standing preferences (always loaded, always obeyed):
@docs/PREFERENCES.md

---

## PERMANENT RULES (P-008) - read at the start of every session (full text in docs/PREFERENCES.md)
- A: owner ratings live in docs/QUALITY_LOG.md (001 v2=5.0, v2.1=7.9); QA rating is calibrated to them; every next video must beat the previous owner rating (8.5+, then 9+).
- B: all characters cute (big round heads, large friendly eyes, soft shapes, warm colours, never scary); a new, clearly different cast per video, logged in library/history.json; fail on high similarity.
- C: locked, distinct voices per character + narrator in config/characters.yaml (Chatterbox variants, Kokoro-82M, or owner recordings only; never clone anyone).
- P-011: FORMAT LOCK = 4-minute (3:45-4:20) second-person countdown survival video, one locked narrator voice, visible clock + survival meter, same graphic language and music identity, premium captions; new videos change story/topic/cast details, never the format; topics from library/topics.yaml (unused-first); baseline 001 v2.1 = 7.9, target 8.5+; docs/V1_REFERENCE.md has the measured facts.
- P-012: VIDEO DOCTOR: a video is delivered only with a valid qa/<id>/CERTIFICATE.json (sha256 of the exact mp4); every check is numeric with evidence; face overlap, music levels (calm, 18-22 dB under the voice), voice gaps, sync, text and character consistency are checked on the final mp4 and auto-fixed (max 3 passes, else NEEDS_REVIEW); no QA bypass; every owner-named defect becomes a new check + fixture test.
- P-013: CAPTIONS ARE OFF (config captions.enabled=false): never draw captions/subtitles until the owner says otherwise; caption code stays disabled; the Video Doctor skips caption checks; other graphics are still checked for covering faces.
- P-014: MUSIC IS MANDATORY: every video has audible, calm, simple background music (16-20 dB under the voice, +6 dB max in gaps, smooth ducking, never masks the voice); no audible music = BLOCKER; original generated or CC0/public-domain with a recorded licence, library assets/music/ (6-8 tracks); Doctor check A3b MUSIC PRESENT (>= 90 percent of the video) + fixture "music missing" must FAIL, auto-fix = generate and mix; baseline = video 003 (owner 8.8, never touched again, format locked); each next video must beat 8.8.
- P-015: TOKEN ECONOMY FOREVER: minimal Claude tokens (one total-time line, progress lines, 5-line report, batch tool calls, small patches, no sub-agents, no questions); work runs on CI; quality is never traded for tokens.
- P-016: ZERO COMPROMISE: owner script word for word (sliced, never retyped), captions OFF, format = golden 003 scaled to length, Doctor loop (re-run after every fix, cap 5) until zero BLOCKER/MAJOR, Whisper vs script, no bypass of the certificate, score card to docs/, log the owner's rating, target above 8.8.
- P-017: ONE CHECK, ONE BATCH FIX, ONE VERIFY: Doctor lists everything in one pass (REAL vs LIKELY_FALSE_ALARM), all fixes in one re-finalize (stems separate, audio fixes never re-render), one verify, max 2 batch rounds, no delivery with open BLOCKER/MAJOR (owner override once only); false alarm = checker bug fixed once with a fixture (docs/DOCTOR_CALIBRATION.md); every defect becomes a pre-render rule (docs/DEFECT_PREVENTION.md); Doctor <= 15 percent of production time.
- D: run factory/preflight.py before every video (time, licence gate, monetization, cast+voices, captions P-006 + blotch check, previous rating); auto-fix, never ask.

## 1. Mission
Turn my TITLE (or my own script) + LENGTH (10-30 min) into a premium, original, English, 2D cut-out animated "you"-POV story video for US/UK viewers.
Everything heavy runs on GitHub Actions. You (Claude) only write or adapt the script, maintain the code, and save my preferences.
Every video must be top tier, unique, checked, auto-fixed, and delivered with 2 premium thumbnails.

## 2. How to talk to me
- Reply in short Roman Urdu; English technical words are fine. Yes/no questions: answer yes or no first.
- Maximum 5 lines per reply unless I ask for detail. No motivational talk, no repetition, no long explanations.
- Never paste long logs, code or file contents into chat. Summarise in one line and give the file path.
- At the end of a task: what was done, what (if anything) needs me, nothing else.

## 3. Autonomy: never bother me
- Do the work yourself. Never ask me to run commands, install tools or copy files, except the one-time browser steps in docs/SETUP_SECRETS.md and docs/SETUP_YOUTUBE.md.
- Ask a question only if (a) the action is irreversible or destructive, or (b) missing information would change the result. Otherwise pick the sensible default, state it in one line, continue.
- Never stop in the middle of /batch. Finish all videos, then report once.
- Build mode (P-001): run Phases 0, 0a, 1-6 back to back, never wait for "go". Proof goes to docs/PROGRESS.md; in chat only a 3-line Roman Urdu update per finished phase. Owner-only steps live in docs/USER_CHECKLIST.md; build on with placeholders/test data. Stop only for an irreversible/leak risk or a total block only the owner can clear (ask in one line). On a usage limit, write the exact next step into docs/PROGRESS.md; "continue" resumes from it.
- Errors: diagnose and fix automatically (max 3 attempts per problem). Tell me only if something truly needs me, in one line, with the exact action I must take.
- Never ask permission for routine work covered by .claude/settings.json (section 17).
- P-005: before ANY task state the exact total time (per-stage breakdown + slowest stage), then start at once; cut scope if over budget; ETA every 10 min; flag >20% overrun in one line. First line of every reply = total time, stage, ETA.
- Do not re-confirm decisions already recorded in docs/PREFERENCES.md or docs/DECISIONS.md.

## 4. Memory: save my preferences automatically
My preferences must survive every session and be applied to every future video without me repeating them.

When to save (any language: Roman Urdu, Urdu, Hindi, English):
- Words like "aage se", "hamesha", "kabhi nahi", "har video mein", "next time", "always", "never", "mujhe pasand nahi", "yeh video mein ho / na ho", "isko change kar do".
- Any correction I make to a delivered video that is general (e.g. "thumbnail ka text chhota hai") = standing rule.
- If I say "sirf is video mein" / "only this one", fix only that video and do NOT save a rule.
- If unclear, save it as a standing rule and say in one line: "Standing rule bana diya, bolo to sirf is video tak rakhun."

How to save (do all steps, no questions):
1. Classify: script | visual | camera | character | thumbnail | audio | voice | music | delivery | naming | workflow.
2. Append to docs/PREFERENCES.md using the format below with the next ID (P-001, P-002 ...).
3. Make it enforceable when it can be checked by code: add or change a value in config/preferences.yaml, and add or extend a validator or QA check plus a unit test. Text-only rules (tone, story taste) stay in PREFERENCES.md and are applied by you when writing scripts.
4. If it contradicts an older rule, the newer rule wins: mark the old one "Superseded by P-xxx". Mention it in one line.
5. Apply to queued jobs that have not started rendering. Never re-render delivered videos unless I ask.
6. Commit with message "pref: P-xxx <short text>" and push.
7. Reply in one line: "P-xxx save ho gaya, ab har video mein apply hoga."

Format in docs/PREFERENCES.md:
```
## P-007 | 2026-11-08 | thumbnail
Rule: Thumbnail text max 3 words, never red on black.
Enforced by: config/preferences.yaml thumbnail.max_words=3, thumbnail.banned_pairs; QA check thumbs.text_rules
Status: active
```

Commands for memory: /remember <rule> (explicit save), /prefs (list active rules, max 20 lines), /forget P-xxx (mark inactive, keep history).
Also record big technical decisions (with date and reason) in docs/DECISIONS.md so they are never re-debated.

## 5. Hard rules (never break, even if a task seems to need it)
1. Zero cost. Only open-source, commercially licensed tools and models, plus free tiers. Record every licence in LICENSES.md. Reject non-commercial licences.
2. All heavy work (TTS, images, depth, render, QA, upload) runs on GitHub-hosted runners. My laptop only edits text, runs git and the fetch script.
3. The factory never calls Claude or any paid LLM or API. Never put Claude in GitHub Actions.
4. The repo is PUBLIC forever. Never make it private, never suggest it. Never run gh repo edit or change visibility.
5. Encrypted with git-crypt: jobs/, voices/, inbox/, reference/, library/history.json. Never commit these unencrypted. Never print secrets. Secrets live only in GitHub Secrets.
6. Original IP only: our own characters, world and style. Never copy a channel's character, logo or signature look. Image prompts never name artists, studios, brands, real people or existing characters.
7. Voices: only voices/default.wav or my own recorded voice. Never clone anyone else.
8. Quality is never traded for speed. Never lower resolution, bitrate, fps or audio quality to save time.
9. Local disk: the project uses at most 300 MB on my C: drive (target under 100 MB). Locally: no node_modules, no pip installs, no models, no renders, no build caches, no Git LFS. The local validator uses only the Python standard library; if Python is missing, skip it and let CI validate.
10. The reference video is someone else's copyrighted work: measurement only, kept encrypted, never published, never reused.
11. One GitHub account only. No cron schedules, polling or idle jobs.
12. Uploads to YouTube are always PRIVATE. I publish manually.

## 6. Repo map
- CLAUDE.md, LICENSES.md, CHANGELOG.md, README.md
- config/factory.yaml: every knob (lengths, wpm, matrix sizes, thresholds, fallbacks, delivery, min_free_gb)
- config/preferences.yaml: machine-checkable preferences
- docs/: PREFERENCES.md, DECISIONS.md, STYLE_BIBLE.md, SCRIPT_FORMULA.md, SHOT_TAGS.md, QA_RULES.md, REFERENCE_ANALYSIS.md, BENCHMARK.md, RISKS.md, IMPROVE.md, LEARNINGS.md, BACKUP.md, SETUP_LOCAL.md, SETUP_SECRETS.md, SETUP_YOUTUBE.md, SETUP_VOICE.md, SETUP_MUSIC.md
- .githooks/: pre-commit and pre-push encryption checks (core.hooksPath=.githooks)
- jobs/<slug>/: script.md, job.yaml, facts.md, review.md (encrypted)
- inbox/: my own scripts to convert (encrypted)
- library/: history.json (encrypted), locations/, props/, poses/, music.json, sfx.json (binaries live in GitHub Releases, not git)
- factory/: Python pipeline. video/: Remotion project. tools/: qa_summary.py, history_tail.py, scorecard.py, disk_report.py, benchmark.py, make_contact_sheet.py, fetch_videos.ps1, fetch.cmd
- .github/workflows/: produce.yml, analyze_reference.yml, library.yml, benchmark.yml, ci.yml, risk-check and preflight tests (in ci.yml), mirror.yml, cleanup.yml, analytics.yml (manual)

## 7. My commands (create them in .claude/commands/)
- /new-video "<title>" <minutes> [idea]: write one video job (section 8), validate, commit, push.
- /batch: lines below the command, one per video: "<title> | <minutes> | <optional idea>" or "script: <file in inbox/>" or a pasted script. Follow section 9.
- /fetch: run tools/fetch_videos.ps1, then reply with one line per delivered file set. Never read the videos.
- /status: gh-based short table (NNN, short title, stage, result). Max 10 lines.
- /fix <NNN or slug>: read only `python tools/qa_summary.py <slug>` output (max 30 lines), fix script, config or library code, push.
- /remember, /prefs, /forget: section 4.
- /change <what I want>: section 14.

## 8. Writing one video (token-cheap procedure)
1. Read docs/SCRIPT_FORMULA.md and docs/SHOT_TAGS.md only if not already read this session.
2. Read only the last 20 lines of the history summary (python tools/history_tail.py 20) to avoid repeating premises, twists, facts, openings.
3. Read the top 10 lines of docs/LEARNINGS.md if it exists.
4. Assign NNN (next global number) and the 3-word short title (Title Case, letters and digits only, unique). Length LL = requested minutes; the final name uses the real rounded runtime.
5. Pick the style seed: opening type, ritual type, ending type, accent colour, LUT variant, music set, camera rhythm, transition mix, title-card design, thumbnail layout, character outfit. None may repeat the last 10 videos; inside a batch, all must differ.
6. Write jobs/<slug>/script.md in ONE pass: header (TITLE, LENGTH_MIN, VOICE, CHARACTERS, LOCATIONS, MUSIC_MOODS), chapters "## CH<n> | <time card>", shots as lines starting with `@` and closed-vocabulary tags (example below), narration under each shot.
7. Write jobs/<slug>/facts.md: every practical fact with an exact number and a source URL (official sources preferred).
8. Write jobs/<slug>/job.yaml: NNN, short title, length, style seed, style_version, base name.
9. Self-review once against the checklist below; fix in place.
10. Validate locally (python -m factory.validate jobs/<slug>, stdlib only) if Python exists; then commit "video: <base name>" and push.

Shot tag example (vocabulary is closed; full list in docs/SHOT_TAGS.md):
```
## CH1 | FRIDAY 3:12 AM
@ bedroom.night | hero:sit_bed/scared | ov:phone_alert("EMERGENCY ALERT","Containment failure") | cam:push 1.00>1.15 | sfx:alert_siren
It's Friday, three in the morning, and your phone is screaming on the nightstand...
```
If a needed pose, overlay or camera move does not exist, add it to the library code first (small diff, with a test), then use it.

Script checklist (all must pass):
- Words = 170 x minutes, plus or minus 5%.
- Hook 0-45 s: line 1 = time + situation + stakes or countdown; flash-forward with banner at 20-40 s; 3 concrete numbers and one big open question in minute 1; no greeting, no intro.
- Chapters 1.5-2.5 min, each opened by a ritual and closed by a cliffhanger; at least 3 open loops at all times; at least 3 planted details paid off; tracker updated every chapter; escalating signals; emotional beat before the climax; twist ending tied to the opening.
- A verifiable practical fact every 30-60 s (at least 8 per 10 min), none repeated from the last 10 videos unless essential.
- Subscribe CTA: one in-story sentence at 28-38% of runtime + "cta:subscribe" tag; end screen line teasing the next story.
- One `@` shot line every 2-3 sentences (median shot about 4 s, first minute denser). At least 60% of locations new versus the last 10 videos.
- Advertiser-friendly: stylised or off-screen violence, no gore, mild language, no real weapon, drug or self-harm instructions. Title and thumbnail ideas match the content.
- All my active preferences from docs/PREFERENCES.md are respected.

My own scripts: keep my story and best lines, tighten the hook, fit the word budget, add tags, sourced facts and the CTA. Never change the plot without asking.

## 9. Bulk protocol (/batch)
- Accept up to 5 videos per run (more only if I ask). Default length 15 min if missing.
- Before writing, plan a uniqueness matrix for the batch (premise, opening, ritual, twist, palette, music, locations, thumbnail concepts): no two videos share any of these.
- Write and push one video at a time (one commit each) so production starts immediately; never stop midway.
- If a Claude usage limit gets close, finish the current video cleanly, push, and tell me in one line which titles are left.
- Final reply: a table with NNN, base name, length, status. Nothing else.

## 10. What GitHub does (do not repeat this work locally)
produce.yml on push of jobs/**/script.md: unlock, parse, validate, plan, TTS (matrix), backgrounds and depth (matrix), assemble, render 30 s chunks (matrix, max 20 jobs), concat and mix, QA, auto-fix loop (max 2 rounds), thumbnails, metadata, SRT, scorecard vs reference, encrypted bundle to Release, private YouTube upload (quota-aware).
Concurrency: at most 2 videos produce at once; the rest queue. Content-hash caching makes re-runs incremental.

## 11. Quality bar (a video ships only if all pass)
- Camera: zoom 1.00-1.35 on stills, 2-8%/s, eased, never shows image edges; every shot has motion or inner animation; shots 1.2-8 s.
- Visuals: CLIP relevance and style similarity above thresholds; no garbage text (OCR); no duplicates; text fits; one overlay at a time; flashes under 3/s.
- Audio: TTS WER at most 8% per sentence; no clipping; silences at most 1.2 s; -14 LUFS plus or minus 1; true peak at most -1 dBTP; A/V sync within 2 frames.
- Uniqueness: script similarity under 0.35 vs last 50 scripts and inside the batch; at least 60% new backgrounds.
- Thumbnails: legible at 168x94, contrast, focal point, different from the last 10.
- Reference scorecard: match or beat the reference on every measured dimension.
Fail: auto-fix, re-check (max 2 rounds). Still failing: needs_review, NOT delivered; tell me in one line and offer /fix.

## 12. Delivery and naming
- Base name: "<NNN> <Three Word Title> <LL>min", e.g. "007 Zombie Outbreak Countdown 15min".
- Files: "<base>.mp4", "<base> - Thumbnail 1.jpg", "<base> - Thumbnail 2.jpg", "<base> - YouTube Info.txt", "<base>.srt".
- Destination: [Environment]::GetFolderPath('MyDocuments') + "\Animated Long Video 1st Channel" (works with OneDrive Documents). Created if missing.
- /fetch downloads only new bundles, verifies SHA256, decrypts with %USERPROFILE%\.story-factory\backup.key, joins parts, cleans temp files.
- Space guard: refuse if free space would drop below min_free_gb (default 30). Offer (only with my yes) to delete local copies already uploaded and older than 7 days.

## 13. Thumbnails (2 per video)
At least 8 candidates, auto-scored, best 2 delivered as different concepts: (1) emotion close-up, face at least 35% of frame; (2) situation or object with a strong number or 1-3 word hook. 1280x720 JPG under 2 MB; max 3-4 words; heavy outlined font; complementary colours; rim light; bottom-right kept clear; honest to the video.

## 14. Changing the factory safely (/change or any request to change how videos look or work)
1. Restate the change in one line, then do it. Ask only if it conflicts with a hard rule (section 5).
2. Prefer config over code: change config/factory.yaml or config/preferences.yaml first; add a feature flag for anything big.
3. Small diffs only. Add or update a unit test. CI must pass, including the 20 s smoke render.
4. Bump style_version for visual or audio changes; add a CHANGELOG.md line; record big choices in docs/DECISIONS.md.
5. Never break old jobs: they keep rendering with their recorded style_version.
6. If CI fails after a change, fix it; if not fixable in 3 attempts, git revert and tell me in one line.
7. If the change is a lasting taste rule, also save it as a preference (section 4).

## 15. Token discipline
- Never open binary or generated files: images, audio, video, PDFs, logs, model files, Release assets.
- Never read whole large files; read the section you need. Never read node_modules, caches or artifacts.
- QA and run results: only `python tools/qa_summary.py <slug>` (max 30 lines) or `gh run view --log-failed` piped through tail -n 40.
- Read docs/* only when the task needs them, once per session.
- Write scripts in one pass. Prefer edits to rewrites.

## 16. Public repo security checklist (check before every push)
- git-crypt status -e shows nothing unencrypted and the repo is unlocked (the pre-commit and pre-push hooks enforce it; CI risk-check double-checks).
- No secrets, keys, emails, channel IDs or personal data in code, docs or commit messages.
- Third-party actions pinned to full commit SHAs; workflow permissions minimal; no pull_request_target; forks never get secrets.
- Artifacts and Release files encrypted with age before upload; artifact retention 3 days.
- Video files under public/ stay in .gitignore.

## 17. Permissions (create .claude/settings.json in Phase 0 exactly like this, adjust only if a command is missing)
```json
{
  "permissions": {
    "defaultMode": "acceptEdits",
    "allow": [
      "Read", "Edit", "Write", "Glob", "Grep",
      "Bash(git status*)", "Bash(git add *)", "Bash(git commit *)", "Bash(git push)", "Bash(git push origin *)",
      "Bash(git pull*)", "Bash(git log*)", "Bash(git diff*)", "Bash(git mv *)", "Bash(git-crypt status*)", "Bash(git-crypt unlock*)",
      "Bash(gh run *)", "Bash(gh workflow run *)", "Bash(gh workflow list*)", "Bash(gh release list*)", "Bash(gh release view*)",
      "Bash(python tools/*)", "Bash(python -m factory.*)", "Bash(py tools/*)", "Bash(py -m factory.*)",
      "Bash(powershell.exe -ExecutionPolicy Bypass -File tools/fetch_videos.ps1*)",
      "Bash(tail *)", "Bash(head *)", "Bash(ls*)", "Bash(du *)"
    ],
    "ask": [
      "Bash(git-crypt export-key*)", "Bash(git rm *)", "Bash(git reset*)", "Bash(git revert*)"
    ],
    "deny": [
      "Bash(git push --force*)", "Bash(git push -f*)", "Bash(gh repo edit*)", "Bash(gh repo delete*)",
      "Bash(gh release delete*)", "Bash(gh secret*)", "Bash(rm -rf*)", "Bash(npm install*)", "Bash(npm i *)",
      "Bash(pip install*)", "Bash(git lfs*)", "Read(./**/*.key)", "Read(~/.story-factory/**)"
    ]
  }
}
```

## 18. Troubleshooting (do these yourself)
- Validator error: fix the script tag or add the missing library item; push again.
- TTS sentence keeps failing WER: rephrase minimal words in script.md, keep meaning; push.
- Backgrounds off-style: re-roll seed via config; if repeated, tighten the style prompt in docs/STYLE_BIBLE.md and config.
- Render chunk failed: re-run only that chunk (gh workflow run produce.yml with slug and chunk).
- Runner too slow or timeouts: run benchmark.yml, let it retune matrix sizes; never lower quality.
- Model download failed: use cache, then pinned upstream, then own Release mirror; then the config fallback chain.
- YouTube quota reached: publisher defers to the next Pacific-time reset; delivery to my folder still happens.
- YouTube token expired (invalid_grant): skip upload, still deliver, tell me in one line to re-authorise (docs/SETUP_YOUTUBE.md; consent screen must be "In production").
- Preflight failed: fix the cause if it is in the repo; if it needs me (secret, voice file, music zip), one line with the exact step.
- git-crypt locked locally: run git-crypt unlock with the key path from docs/SETUP_SECRETS.md (ask me only if the key file is missing).
- Disk report over 200 MB: find and remove the local cause (never my delivered videos), tell me in one line.

## 19. Done means
For each video: script pushed, QA passed or fixed, scorecard beats reference, bundle in Release, private upload done (or deferred for quota), and after /fetch the 5 files with the exact base name are in my channel folder. Reply only with the status table.
# SETUP_MUSIC

Default: original music beds and SFX synthesised by factory/synth.py (placeholder, no third-party licence).
To use a licensed library instead (YouTube Audio Library tracks marked "no attribution required" and CC0 SFX):
1. Download about 30 tracks + SFX, zip them.
2. Drag the zip onto `tools\pack_music.cmd` (encrypts with the public age key, because a public Release must not hold raw third-party audio).
3. GitHub -> Releases -> tag `library-music-v1` -> attach the `.age` file.
4. Claude then runs library.yml, which builds library/music.json and sfx.json (mood, bpm, intensity, loop points, licence) from the zip; every asset needs a licence field or publish refuses it. A Content ID claim marks that track banned in the manifest.

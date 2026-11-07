# SETUP_VOICE

Default: Chatterbox built-in voice (no cloning, placeholder). To use your own voice:
1. Record 60 seconds on your phone: quiet room, no music, steady distance (20 cm), no clipping. Read this text twice, naturally:
   "It is three twelve in the morning and the street outside is completely silent. You count your water, your batteries and the hours you have left. Somewhere a door closes. Somebody is awake. And whoever it is, they already know your name."
2. Save as WAV (mono or stereo, 24 kHz or higher) named `me.wav` and copy it to the project's `voices\` folder (never upload it through github.com).
3. Claude commits it (encrypted) and runs the voice audition (same 30 s test with default and me); you pick; the choice is `tts.voice` in config/factory.yaml (`default` or `me`).
- Chatterbox's built-in PerTh watermark stays on. If a fallback TTS (Kokoro) ever has to be used, the video is held as needs_review for voice consistency.

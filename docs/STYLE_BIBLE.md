# STYLE_BIBLE (style_version 1; tokens live in video/src/theme.ts)

- **Look**: hand-drawn ink outlines (6 px ink #1c1a1f), flat gouache colours, paper grain (grain.png overlay), soft vignette, three mood grades: warm day, blue night, red alarm (+ dusk, blackout). Backgrounds: SDXL-Lightning painted plates (3024x1728 after 2.25x upscale, ink-line pass, muted grade) split into 3 depth layers; procedural SVG backdrops are the fallback.
- **Characters** ("Paper Crew", original): chunky cut-out puppets, 3/4 body + frontal face, yellow work gloves, white-soled shoes. One rig for every character (video/src/characters/Rig.tsx): 14 poses, 10 expressions, idle blink 3.4-5 s, breathing, sway, walk/run cycles; variants by params (outfit, hat, hair, age, skin). The same rig draws the thumbnails.
- **Overlays**: paper props (notepad tracker, calendar, sticky note, label tag, receipt, paper diagram, bar chart, hand with pen), gloved hands holding a phone (alert/web/video/call/search), TV news, time card (clock strip / stamped box / marker scrawl), flash-forward banner, timer, numbered circle, arrow callout, dashed path, glitch text, subscribe sticker, end screen. Enter with overshoot, background blur 6-10 px behind overlays, one at a time.
- **Typography** (all OFL/Apache, self-hosted): Anton (display, thumbnails, time cards), Permanent Marker (labels), Patrick Hand (paper text), Caveat (notes), Inter (UI/phones/receipts).
- **Camera**: zoom 1.00-1.35, 2-8 %/s, ease in-out, 12% overscan so edges never show; presets push, pull, pan_l/r, tilt_up/down, parallax_drift, whip_to, rack_focus, shake_light/medium, hold. Parallax layers far 0.55 / mid 0.85 / near 1.2.
- **FX**: grain, vignette, mood tint, flicker, alarm pulse (1.2 Hz, low alpha, under 3 flashes/s), dust, smoke, embers, rain, glitch, snow.
- **Safe areas**: 96 px margins; thumbnails keep the bottom-right 20% x 16% clear.
- **Audio**: continuous synthesised mood bed per chapter, ducked 18 dB under the voice, chapter stingers, per-action foley, master -14 LUFS / TP <= -1 dBTP.
- Changing any of this bumps `style_version` in config/factory.yaml and adds a CHANGELOG line; old jobs keep their recorded version.

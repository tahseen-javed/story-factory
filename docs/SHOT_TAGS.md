# SHOT_TAGS: closed vocabulary (generated from factory/vocab.py; the validator rejects anything else and suggests the nearest valid code)

## Shot line
```
@ <location>.<variant> | <char>:<pose>/<expression>[@left|center|right|0.35] | ov:<overlay>(args) | cam:<preset> <z0>><z1> | fx:<list> | sfx:<list> | track:{key:value} | banner:"TEXT" | cta:subscribe
<narration, 1-3 short sentences>
```
One `@` line per 2-3 short sentences (median shot about 4 s, first minute denser). At most 1 overlay per shot, 0-3 characters. Chapter: `## CH<n> | <TIME CARD>`.

Header keys: `TITLE`, `LENGTH_MIN`, `VOICE` (default|me), `CHARACTERS:` (`- id = rig_name(param=value, ...)`), `LOCATIONS:` (`- id: one-line visual description, no artists/brands/people`), `MUSIC_MOODS:` (`- CH1: dread`).

Craft markers (comments, enforced by the validator): `// RITUAL ...` (every chapter), `// CLIFF` (end of every chapter but the last), `// LOOP open <id>: ...` / `// LOOP close <id>`, `// PLANT <id>` + `// PAYOFF <id>`, `// BEAT emotional: ...`, `// TWIST: ...`.

Facts file (`facts.md`; pilot: `sources.md`): `- <fact with an exact number> | https://official-source` (guidance without a number: `~ ... | https://...`).

## Variants
day, night, alarm, dusk, blackout

## Poses (14)
stand, walk, run, sit, sit_bed, carry, push_cart, phone_hold, point, write, hide, fight, crouch, hands_up

## Expressions (10)
neutral, worried, scared, shocked, determined, relieved, sad, angry, sleepy, sly

## Overlays (name: min-max args)
- `notepad_tracker` (0-8 args)
- `calendar_countdown` (2-3 args)
- `sticky_note` (1-2 args)
- `label_tag` (1-2 args)
- `receipt` (2-10 args)
- `paper_diagram` (3-7 args)
- `phone_alert` (2-2 args)
- `phone_web` (3-3 args)
- `phone_video` (2-2 args)
- `phone_call` (2-2 args)
- `phone_search` (2-4 args)
- `tv_news` (2-3 args)
- `timer` (1-2 args)
- `numbered_circle` (1-2 args)
- `arrow_callout` (1-2 args)
- `dashed_path` (2-3 args)
- `glitch_text` (1-1 args)
- `paper_bar_chart` (3-7 args)
- `hand_pen` (1-2 args)
- `end_screen` (1-1 args)

Arg conventions: `phone_alert(headline, body)`, `phone_web(url, headline, body)`, `phone_video(title, caption)`, `phone_call(name, status)`, `phone_search(query, result1, ...)`, `tv_news(headline, lower_third, ticker)`, `timer("HH:MM:SS", label)` counts down during the shot, `numbered_circle(n, label)`, `arrow_callout(text, left|right|up|down)`, `dashed_path(from, to)`, `paper_bar_chart(title, "label=value", ...)`, `paper_diagram(title, node1, node2, ...)`, `calendar_countdown(days_left, total_days, label)`, `receipt(title, "item   price", ..., "TOTAL   price")`, `notepad_tracker(title)` shows the cumulative `track:` state with changed values struck through, `end_screen(teaser)` on the last shot only.

## Camera presets
push, pull, pan_l, pan_r, tilt_up, tilt_down, parallax_drift, whip_to, rack_focus, shake_light, shake_medium, hold
Zoom 1.00-1.35, speed 2-8 %/s (assemble clamps and rewrites), never shows image edges.

## FX
flicker, smoke, embers, rain, alarm_pulse, dust, glitch, snow

## SFX
alert_siren, phone_buzz, door_knock, door_creak, footsteps, whoosh, paper_slide, stinger_chapter, heartbeat, power_down, radio_static, glass_crack, water_pour, car_engine, crowd_murmur, thunder, click, beep, typing, rustle, ticking_clock, spark, wind

## Music moods
tense, dread, urgent, hopeful, sorrow, climax, calm, mystery

## Style seed values (job.yaml)
- opening: cold_open, flash_forward, question, countdown, in_medias_res
- ritual: radio_check, tracker_update, weather_report, supply_count, message_log
- ending: twist_loop, quiet_reveal, cliff_resolve, final_choice, echo_opening
- accent: amber, teal, crimson, violet, lime, coral, cobalt, gold
- lut: warm_day, cold_night, red_alarm, dusty_dusk, green_haze
- titlecard: clock_strip, paper_tab, stamped_box, ticket, marker_scrawl
- camera_rhythm: steady_push, drift_heavy, pulse_cut, slow_burn
- transition: hard_cuts, zoom_through, paper_slide_mix
- thumbnail_layout: close_left, close_right, object_center, split_pair

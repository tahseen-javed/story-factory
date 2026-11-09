"""Closed vocabulary for script.md shot tags. Single source of truth (docs/SHOT_TAGS.md mirrors it).

Adding a pose, overlay, camera move, fx or sfx: add it here AND implement it in video/ (or factory/synth.py
for sfx/music), then add a test. The validator rejects anything not listed and suggests the nearest match.
"""
from __future__ import annotations

import difflib

VARIANTS = ("day", "night", "alarm", "dusk", "blackout")

POSES = (
    "stand", "walk", "run", "sit", "sit_bed", "carry", "push_cart",
    "phone_hold", "point", "write", "hide", "fight", "crouch", "hands_up", "look_up", "back_away", "reach", "shrug",
)

EXPRESSIONS = (
    "neutral", "worried", "scared", "shocked", "determined",
    "relieved", "sad", "angry", "sleepy", "sly",
)

# overlay name -> (min_args, max_args)
OVERLAYS = {
    "notepad_tracker": (0, 8),
    "calendar_countdown": (2, 3),
    "sticky_note": (1, 2),
    "label_tag": (1, 2),
    "receipt": (2, 10),
    "paper_diagram": (3, 7),
    "phone_alert": (2, 2),
    "phone_web": (3, 3),
    "phone_video": (2, 2),
    "phone_call": (2, 2),
    "phone_search": (2, 4),
    "tv_news": (2, 3),
    "timer": (1, 2),
    "numbered_circle": (1, 2),
    "arrow_callout": (1, 2),
    "dashed_path": (2, 3),
    "glitch_text": (1, 1),
    "paper_bar_chart": (3, 7),
    "hand_pen": (1, 2),
    "end_screen": (1, 1),
    "meter": (2, 3),
    "option_cards": (3, 3),       # three sticky-note options (decision hold)
    "elevator_panel": (1, 2),     # three big buttons: glossy red, worn seven, taped eight
    "loose_cable": (1, 2),        # back of a button with a loose, unwired cable
}
FRAMINGS = ("medium", "closeup", "insert", "wide", "xwide", "low", "back", "ots", "silhouette", "profile")

CAMERA = (
    "push", "pull", "pan_l", "pan_r", "tilt_up", "tilt_down",
    "parallax_drift", "whip_to", "rack_focus", "shake_light", "shake_medium", "hold", "dutch",
)
# presets that are allowed to have (near) zero zoom speed because they move another way / have inner motion
CAMERA_NONZOOM = {"pan_l", "pan_r", "tilt_up", "tilt_down", "parallax_drift", "shake_light", "shake_medium", "hold", "rack_focus"}

FX = ("flicker", "smoke", "embers", "rain", "alarm_pulse", "dust", "glitch", "snow", "crowd")

SFX = (
    "alert_siren", "phone_buzz", "door_knock", "door_creak", "footsteps", "whoosh", "paper_slide",
    "stinger_chapter", "heartbeat", "power_down", "radio_static", "glass_crack", "water_pour",
    "car_engine", "crowd_murmur", "thunder", "click", "beep", "typing", "rustle", "ticking_clock",
    "spark", "wind", "riser", "impact", "glitch", "text_pop", "ding",
)

MUSIC_MOODS = ("tense", "dread", "urgent", "hopeful", "sorrow", "climax", "calm", "mystery")

FIELD_KEYS = ("ov", "cam", "fx", "sfx", "track", "banner", "cta", "fr")

CTA_VALUES = ("subscribe",)

# Words/phrases that must never appear in image prompts (locations) -- artists, studios, brands, real people, existing characters.
PROMPT_DENYLIST = (
    "disney", "pixar", "ghibli", "miyazaki", "dreamworks", "marvel", "dc comics", "batman", "superman", "spiderman",
    "simpsons", "spongebob", "mickey", "pokemon", "nintendo", "mario", "zelda", "star wars", "harry potter", "minecraft",
    "van gogh", "picasso", "monet", "dali", "banksy", "norman rockwell", "rutkowski", "artgerm", "mucha", "warhol",
    "coca-cola", "coca cola", "pepsi", "nike", "adidas", "apple", "google", "microsoft", "amazon", "tesla", "mcdonald",
    "trump", "biden", "obama", "putin", "musk", "taylor swift", "kardashian",
)

# Advertiser-friendliness guard (script narration). Stylised/off-screen violence is fine; these are not.
CONTENT_BLOCKLIST = (
    "gore", "gory", "dismember", "decapitat", "disembowel", "suicide", "kill yourself", "self-harm", "self harm",
    "how to make a bomb", "build a bomb", "make explosives", "cook meth", "synthesize", "porn", "rape",
    "fuck", "motherfucker", "cunt", "nigger", "faggot",
)

GREETINGS = ("hey guys", "hello everyone", "hi everyone", "welcome back", "welcome to", "in this video", "today we", "before we start", "what's up")

OPENING_TYPES = ("cold_open", "flash_forward", "question", "countdown", "in_medias_res")
ENDING_TYPES = ("twist_loop", "quiet_reveal", "cliff_resolve", "final_choice", "echo_opening")
ACCENT_COLOURS = ("amber", "teal", "crimson", "violet", "lime", "coral", "cobalt", "gold")
LUT_VARIANTS = ("warm_day", "cold_night", "red_alarm", "dusty_dusk", "green_haze")
TITLECARD_DESIGNS = ("clock_strip", "paper_tab", "stamped_box", "ticket", "marker_scrawl")
CAMERA_RHYTHMS = ("steady_push", "drift_heavy", "pulse_cut", "slow_burn")
TRANSITION_MIXES = ("hard_cuts", "zoom_through", "paper_slide_mix")
THUMBNAIL_LAYOUTS = ("close_left", "close_right", "object_center", "split_pair")
RITUAL_TYPES = ("radio_check", "tracker_update", "weather_report", "supply_count", "message_log")


def nearest(word: str, options) -> str | None:
    m = difflib.get_close_matches(word, list(options), n=1, cutoff=0.5)
    return m[0] if m else None


def suggest(word: str, options) -> str:
    n = nearest(word, options)
    return f" Did you mean '{n}'?" if n else f" Valid: {', '.join(options)}"

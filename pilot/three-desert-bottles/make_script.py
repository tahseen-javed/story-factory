"""007: owner script 2 word for word + auto shot plan (tools/shot_planner.py). P-018/P-020."""
import os
import sys

D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(D, "..", "..", "tools"))
from shot_planner import C, S, X, R, FZ, build  # noqa: E402

C.update({"h": "hero", "p": "pip", "g": "gran", "b": "abel"})
HO = "h:stand|look_up|point|reach/worried|determined|neutral"
HP = HO + " p:stand|shrug|look_up/neutral|worried|scared"
HPG = HP + " g:stand|reach|shrug/relieved|neutral|worried"
ST_ = "h:stand|look_up/worried|neutral b:stand|shrug/neutral|sly"

P = [
    R("Your car dies on a desert road", "## CH1 | TEN FORTY IN THE MORNING"), R("Your car dies on a desert road", "// ACT hook"),
    X("Your car dies on a desert road", "road.day | fr:xwide,wide | fx:dust | sfx:car_engine | cam:push 1.00>1.15"),
    X("with three bottles of water.", 'seat.day | fr:insert,closeup | cam:push 1.05>1.20 | track:{water:"3 BOTTLES"}'),
    X("The one that saves you today", "cab.day | hero:point/scared | fr:closeup,low | cam:pull 1.18>1.02"),
    X("is the one you refuse to drink.", "road.day | hero:stand/determined | pip:look_up/worried | fr:wide,low | cam:tilt_up"),
    S("It is ten forty in the morning", "road.day", HP, "fx:dust"),
    X("It is ten forty in the morning,", 'road.day | fr:xwide,wide | fx:dust | cam:pull 1.18>1.02 | track:{heat:"98F"}'),
    R("Sunset is eight hours away.", "// ACT act1"),
    X("Sunset is eight hours away.", 'road.day | fr:wide,low | fx:dust | cam:push 1.05>1.20 | track:{hours:"8"}'),
    S("Beside you sits Pip", "cab.day", HP, "fx:dust"),
    S("You remember that station well.", "station.day", ST_, "fx:dust"),
    S("An hour later the engine coughed.", "road.day", HP, "fx:smoke"),
    X("Eight hours of daylight.", 'road.day | fr:xwide,wide | fx:dust | cam:pull 1.18>1.02 | track:{hours:"8",water:"3 BOTTLES"}'),
    R("Then you find a trick.", "## CH2 | ONE BAR"),
    S("Then you find a trick.", "roof.day", HP, "fx:dust"),
    S("Twenty minutes later the phone buzzes.", "cab.day", HP, "fx:dust"),
    X("Battery eleven percent.", 'phone.day | fr:insert,closeup | cam:push 1.05>1.20 | track:{phone:"11%"}'),
    S("Seven and a half hours left.", "road.day", HP, "fx:dust"),
    X("Seven and a half hours left.", 'road.day | fr:wide,low | fx:dust | cam:pull 1.18>1.02 | track:{hours:"7.5",phone:"11%"}'),
    R("Down the road, a sun-bleached sign", "## CH3 | NINE MILES"), R("Down the road, a sun-bleached sign", "// ACT act2a"),
    S("Down the road, a sun-bleached sign", "sign.day", HP, "fx:dust"),
    X("Cobalt Springs, nine miles.", 'sign.day | fr:insert,closeup | cam:push 1.05>1.20 | track:{town:"9 MI",station:"22 MI"}'),
    S("Pip is already tightening her laces.", "road.day", HP, "fx:dust"),
] + FZ(("WALK AHEAD", "WALK BACK", "STAY WITH CAR"), "chalk,rope,star",
       ["Freeze. Option one, walk to Cobalt Springs", "Option two, walk back", "Option three, stay with the car", "Pause the video."],
       "The sun is not waiting.", "road.day", "h:stand/worried p:look_up/worried") + [
    R("You stay. The sign promises", "// HOLD decision 4.5"),
    S("You stay. The sign promises", "road.day", HP, "fx:dust"),
    S("You open every door for airflow", "shade.day", HP, "fx:dust"),
    R("Then the wind stops.", "// ACT midpoint"),
    S("Then the wind stops.", "sky.day", HP, "fx:dust"),
    X("Nothing. No sound at all.", "sky.day | hero:stand/worried | fr:wide,low | fx:flicker | cam:hold"),
    R("Six hours left.", "## CH4 | ONE IN THE AFTERNOON"),
    S("Six hours left.", "shade.day", HP, "fx:dust"),
    X("Six hours left.", 'shade.day | hero:stand/worried | pip:stand/scared | fr:wide,low | fx:dust | cam:push 1.05>1.20 | track:{hours:"6",heat:"108F"}'),
] + FZ(("BIG BOTTLE", "BLUE FLASK", "LEMON HONEY"), "bottle,draught,star",
       ["Freeze. Option one, the big clear bottle", "Option two, your blue flask", "Option three, the lemon and honey", "Pause the video."],
       "She is waiting for your hand.", "shade.day", "h:stand/worried p:stand/scared") + [
    R("Your hand goes to the big bottle.", "// HOLD decision 4.5"),
    S("Your hand goes to the big bottle.", "shade.day", HP, "fx:dust"),
    S("You give Pip the flask.", "shade.day", HP, "fx:dust"),
    S("Pip squeezes your arm.", "shade.day", HP, "fx:dust"),
    X("Subscribe so the next story finds you.", "shade.day | hero:stand/relieved | pip:stand/relieved | fr:medium,closeup | cam:push 1.05>1.20 | cta:subscribe"),
    R("Five hours left.", "## CH5 | THE NEEDLE"),
    S("Five hours left.", "shade.day", HP, "fx:dust"),
    X("Five hours left.", 'dash.day | fr:insert,low | cam:push 1.05>1.20 | track:{hours:"5",flask:"3 SIPS"}'),
    S("Pip keeps talking about Harold.", "shade.day", HP, "fx:dust"),
    R("Everything you believed flips.", "// ACT act2b"),
    S("Everything you believed flips.", "hood.day", HP, "fx:dust"),
    R("Four hours left.", "## CH6 | FOUR HOURS LEFT"), R("Four hours left.", "// ACT sacrifice"),
    S("Four hours left.", "shade.day", HP, "fx:dust"),
    X("Four hours left.", 'shade.day | fr:wide,low | fx:dust | cam:pull 1.18>1.02 | track:{hours:"4"}'),
    S("When Pip finally says it is time,", "hood.day", HP, "fx:dust"),
] + FZ(("LAST SIPS", "LEMON HONEY", "BIG BOTTLE"), "draught,star,bottle",
       ["Freeze. Option one, pour your last three sips", "Option two, pour the lemon and honey", "Option three, pour the big full bottle", "Pause the video."],
       "The shadows are getting longer.", "hood.day", "h:stand/worried p:look_up/scared") + [
    R("Think back. The flask is clean", "// HOLD decision 4.5"), R("Think back. The flask is clean", "// ACT climax"),
    S("Think back. The flask is clean", "hood.day", HP, "fx:dust"),
    S("You turn the key.", "cab.day", HP, "fx:dust"),
    X("Three hours left.", 'dash.day | fr:insert,closeup | cam:push 1.05>1.20 | track:{hours:"3",phone:"9%"}'),
    S("You drive with the windows down", "drive.day", HP, "fx:dust"),
    R("At sunset you pull up to a small blue house.", "// ACT resolution"),
    S("At sunset you pull up to a small blue house.", "house.dusk", HPG),
    S("And now you see what the three bottles really were.", "house.dusk", HPG),
    S("Grandma holds it to the light and smiles.", "house.dusk", HPG),
    R("The bottle that saved you was the one you refused.", "// LASTLINE"),
    S("The bottle that saved you was the one you refused.", "house.dusk", HPG),
    S("So tell me honestly.", "road.dusk", HO, "fx:dust"),
    X("Subscribe if you want to be there.", "road.dusk | hero:stand/determined | fr:wide,low | fx:dust | cam:pull 1.18>1.02 | cta:subscribe"),
]

KW = [
    (r"needle|dashboard", "dash", ""),
    (r"\bphone\b|\bbars?\b|signal|battery|message", "phone", "sfx:phone_buzz"),
    (r"\bflask\b", "flask", ""),
    (r"twist the cap|plastic ring|\bsnap\b", "cap", "sfx:click"),
    (r"\bhood\b|coolant|radiator|\bengine\b|overheated|\bcrust\b|mechanic", "hood", ""),
    (r"\bsign\b|nine miles", "sign", ""),
    (r"attendant|gas station|cooler|\bhose\b|bucket|counter", "station", ""),
    (r"shade|windshield|shadow", "shade", ""),
    (r"\broof\b", "roof", ""),
    (r"\bhawk\b|\bwind\b|insects|\bsky\b|silence", "sky", ""),
    (r"bottle|\bcork\b|lemon and honey|\bsips?\b|three kinds of water", "seat", ""),
]
SP = [("p", r"\bpip\b|\bshe\b|\bher\b|grandad"), ("b", r"attendant|\bhe\b|\bhis\b"), ("g", r"grandma")]

HEAD = """TITLE: The Bottle You Refuse
LENGTH_MIN: 8
VOICE: default
CHARACTERS:
- hero = rig_hero(outfit=plum, hair=short, skin=brown)
- pip = rig_hero(outfit=teal, hat=cap, hair=curly, skin=tan)
- gran = rig_hero(outfit=red, age=old, hair=bun, skin=light)
- abel = rig_hero(outfit=grey, age=old, hat=cap, hair=short, skin=dark)
LOCATIONS:
- road: long empty desert road under a harsh white sun, heat shimmer, orange sand and low rocks, a small broken-down car with its hood up and white steam, empty horizon
- cab: inside a small car, front seats and dashboard with a steering wheel, bright hot light through the windscreen, three bottles on the back seat, dusty glass
- seat: close view of a car back seat with three bottles: a blue metal flask, a big clear water bottle and a small glass bottle with a cork, hot bright light
- flask: close view of a blue metal flask with a screw cap and water drops, hot light, blurred sandy background
- cap: close view of a hand twisting the cap of a clear plastic bottle, the little plastic ring already broken, bright light
- phone: close view of a smartphone in a hand with a nearly empty battery icon and no signal bars, bright sun glare
- station: dusty roadside gas station with one old pump, a broken drinks cooler, a counter, a garden hose coiled in a bucket of empty bottles, sleepy afternoon light
- sign: sun-bleached wooden roadside sign leaning in the sand with a painted arrow, empty desert road behind, hot haze
- roof: top of a small car roof in the desert sun, one hand held high, wide empty desert horizon, bright sky
- shade: small car with all doors open and a silver windshield shade stretched across the back windows, cool blue shadow on the sand, two seats in the shadow
- dash: close view of a car dashboard with a temperature gauge needle leaning all the way to the red, steering wheel, warm dusty light
- hood: raised car hood showing the engine, a dry coolant tank with white crust around the rim, sun glare, tools on the sand
- sky: huge empty desert sky with heat haze, a lone hawk, still dust and shimmering sand, no wind
- drive: small car driving on a desert road with windows down, golden afternoon light, dust trail behind, a mile marker post
- house: small blue house at sunset with a front door and a porch, warm orange sky, desert plants, paper party decorations
MUSIC_MOODS:
- CH1: calm
- CH2: mystery
- CH3: tense
- CH4: tense
- CH5: mystery
- CH6: hopeful

"""
build(D, HEAD, P, KW, SP, mx=11)

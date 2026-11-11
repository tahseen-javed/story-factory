"""script.md = owner-format narration (sliced, never retyped) + shot table. P-018/P-020: shot sizes, locations, poses, expressions and camera moves rotate every beat."""
import os
import re

D = os.path.dirname(os.path.abspath(__file__))
TXT = " ".join(l.strip() for l in open(os.path.join(D, "narration.txt"), encoding="utf-8").read().splitlines() if l.strip())
C = {"h": "hero", "j": "jojo", "b": "bell", "a": "alder"}


def who(s):
    out = []
    for p in s.split():
        k, v = p.split(":")
        out.append(f"{C[k]}:{v}")
    return " | ".join(out)


def shot(loc, ch, fr, extra=""):
    return " | ".join(x for x in [loc, who(ch) if ch else "", f"fr:{fr}", extra.strip(" |")] if x)


def freeze(labels, icons, anchors, hold, loc, ch):
    out = []
    for k, a in enumerate(anchors):
        card = 'ov:option_cards("%s","%s","%s","%d","%s")' % (labels[0], labels[1], labels[2], k + 1 if k < 3 else 0, icons)
        out.append((a, shot(loc, ch, ["ots", "wide", "medium", "wide"][k], card + (" | fx:flicker" if k == 3 else ""))))
    out.append((hold, shot(loc, ch, "ots", 'ov:option_cards("%s","%s","%s","0","%s")' % (labels[0], labels[1], labels[2], icons))))
    out.append(("// HOLD decision 4.5", None))
    return out


T = [
    ("## CH1 | NINE TWELVE AT NIGHT", None), ("// ACT hook", None),
    ("It is 9:12 at night,", shot("street.night", "", "xwide,wide", 'fx:rain | sfx:thunder | track:{hours:"3"}')),
    ("the river is climbing", shot("street.night", "", "insert,low", "fx:rain | sfx:water_pour")),
    ("and the only exit left", shot("exitd.night", "", "insert,closeup", "fx:flicker")),
    ("the one door everyone told you", shot("b3.night", "h:stand/scared", "closeup,back")),
    ("// ACT act1", None),
    ("Three hours until the flood crests.", shot("b3.night", "", "xwide,wide", 'track:{hours:"3"}')),
    ("Your phone buzzes", shot("b3.night", "h:phone_hold/shocked", "insert,closeup", "sfx:phone_buzz")),
    ('"Marlow Street, leave', shot("b3.night", "h:phone_hold/scared", "closeup,ots", 'ov:phone_alert("EMERGENCY ALERT","Marlow Street: leave now")')),
    ("You are on level B3", shot("b3.night", "h:stand/worried", "wide,medium")),
    ("and the shutter at the top", shot("shutter.night", "", "insert,low", "fx:dust | sfx:impact")),
    ("You run for the ramp.", shot("ramp.night", "h:run/scared", "wide,low")),
    ("Water is already sliding", shot("ramp.night", "", "insert,low", "fx:rain | sfx:water_pour")),
    ("like a tongue licking", shot("ramp.night", "", "closeup,wide", "fx:rain")),
    ("Battery at eighty-two percent.", shot("ramp.night", "h:stand/worried", "closeup,medium", 'track:{hours:"3",phone:"82%",tide:"ANKLES"}')),
    ("A delivery rider skids", shot("ramp.night", "j:run/neutral", "wide,low")),
    ("This is Jojo.", shot("ramp.night", "j:stand/neutral", "medium,closeup")),
    ("He has a helmet with ears,", shot("ramp.night", "j:stand/relieved", "closeup,profile")),
    ("and a small tool pouch", shot("ramp.night", "j:reach/neutral", "insert,closeup")),
    ('"Shutter\'s stuck halfway,"', shot("shutter.night", "j:point/worried h:stand/worried", "ots,medium")),
    ("Nobody's driving out", shot("shutter.night", "j:shrug/worried", "closeup,low")),
    ("Behind a pillar,", shot("b3.night", "b:stand/relieved", "medium,wide")),
    ("Mr. Bell, the night attendant", shot("booth.night", "b:stand/neutral", "closeup,ots")),
    ("Beside him, Mrs. Alder,", shot("trolley.night", "a:stand/relieved", "medium,closeup")),
    ("guarding a shopping trolley", shot("trolley.night", "", "insert,low")),
    ("Mr. Bell points the torch", shot("b3.night", "b:point/neutral h:stand/neutral", "ots,wide", "fx:beam")),
    ('"Lift still works.', shot("lift.night", "", "insert,low")),
    ("Fire stairs behind it.", shot("stairs.night", "", "insert,wide")),
    ("And that door at the end", shot("exitd.night", "b:point/worried", "ots,closeup")),
    ("Don't touch it.", shot("exitd.night", "b:stand/worried", "closeup,profile")),
    ("Jojo grins at the sign.", shot("exitd.night", "j:stand/sly", "closeup,low")),
    ('"Everything in this place', shot("exitd.night", "j:shrug/sly h:stand/neutral", "medium,ots")),
    ("Then the lights flicker,", shot("lift.night", "", "wide,xwide", "fx:flicker | sfx:power_down")),
    ("the lift display blinks,", shot("lift.night", "", "insert,closeup", "fx:flicker")),
    ("and the lift pings up", shot("lift.night", "", "low,wide", "sfx:ding")),
    ("## CH2 | THE STAIRS", None), ("// ACT act2a", None),
    ("Water at your knees on the ramp", shot("ramp.night", "h:stand/scared", "medium,low", 'fx:rain | track:{hours:"3",phone:"82%",tide:"KNEES"}')),
    ("and you have to choose", shot("b3.night", "h:stand/worried j:stand/worried", "ots,wide")),
] + freeze(("RAMP", "LIFT", "STAIRS"), "ledge,glow,arch", ["Freeze. Option one, run up", "Option two, take the lift", "Option three, climb the fire", "Pause the video."], "Your clock keeps running.", "b3.night", "h:stand/worried j:stand/worried") + [
    ("You choose option three. Jojo hauls", shot("stairs.night", "j:carry/determined a:push_cart/neutral", "wide,medium", "sfx:footsteps")),
    ("Behind you, the lift sinks", shot("lift.night", "", "insert,low")),
    ("and its lights go out.", shot("lift.night", "", "wide,closeup", "fx:flicker | sfx:power_down")),
    ("The pit at the bottom", shot("lift.night", "", "insert,closeup")),
    ("The moment water touches", shot("stairs.night", "b:point/neutral", "ots,insert")),
    ("And that ramp?", shot("ramp.night", "", "wide,low", "fx:rain")),
    ("Moving water only fifteen", shot("ramp.night", "j:back_away/shocked", "closeup,wide")),
    ("Level ground is a river's", shot("street.night", "", "xwide,wide", "fx:rain")),
    ("Stairs are boring.", shot("stairs.night", "h:walk/relieved j:walk/relieved", "medium,wide", "sfx:footsteps")),
    ("## CH3 | LEVEL B2", None), ("// ACT midpoint", None),
    ("On level B2 the stairwell door", shot("b2.night", "h:walk/worried j:walk/worried b:walk/neutral a:walk/neutral", "wide,xwide", "sfx:footsteps")),
    ("Seventy-one percent battery.", shot("b2.night", "h:stand/worried", "closeup,medium", 'track:{hours:"2.7",phone:"71%"}')),
    ("Jojo checks his phone", shot("b2.night", "j:phone_hold/worried", "closeup,insert")),
    ("Mr. Bell sets his torch", shot("stairs.night", "b:point/neutral h:stand/neutral", "ots,medium", "fx:beam")),
    ("Street door is at the top", shot("chain.night", "", "insert,wide")),
    ("Mrs. Alder pats her trolley.", shot("trolley.night", "a:stand/relieved", "closeup,medium")),
    ("Nobody laughs.", shot("b2.night", "", "insert,low", "fx:rain")),
    ("The water on B2 is still dry", shot("b2.night", "", "wide,low", "sfx:water_pour")),
    ("You walk along the wall", shot("b2.night", "h:walk/worried", "back,wide")),
    ("And there it is.", shot("exitd.night", "", "insert,closeup", "fx:dust")),
    ("Jojo whispers.", shot("exitd.night", "j:stand/worried h:stand/worried", "ots,medium")),
    ("Mr. Bell frowns.", shot("exitd.night", "b:stand/worried", "closeup,profile")),
    ("It jammed years ago.", shot("exitd.night", "b:shrug/neutral", "medium,low")),
    ("Your phone shows no signal", shot("b2.night", "h:phone_hold/worried", "insert,closeup", 'track:{hours:"2.6",phone:"64%"}')),
] + freeze(("ONE MESSAGE", "LONG CALL", "PHONE OFF"), "star,arch,battery", ["Freeze. Option one, hold the phone", "Option two, call the emergency", "Option three, switch the phone", "Pause the video."], "One bar will not last.", "b2.night", "h:phone_hold/worried j:stand/worried") + [
    ("You choose option one.", shot("b2.night", "h:phone_hold/determined", "closeup,insert", "sfx:typing")),
    ("The message climbs out", shot("b2.night", "h:phone_hold/neutral", "insert,wide", 'ov:phone_alert("SENT","Marlow Street car park, level B2")')),
    ("One word, delivered.", shot("stairs.night", "", "insert,closeup", "sfx:ding")),
    ("A call needs a steady signal", shot("b2.night", "h:phone_hold/neutral j:stand/relieved", "medium,ots")),
    ("A message needs only a second.", shot("b2.night", "", "insert,low")),
    ("And if you switch the phone off,", shot("b2.night", "h:stand/worried", "closeup,medium")),
    ("You hold the phone close", shot("b2.night", "h:stand/relieved", "closeup,low", 'track:{phone:"61%"}')),
    ("Mrs. Alder squeezes your hand.", shot("trolley.night", "a:reach/relieved h:stand/relieved", "medium,closeup", "cta:subscribe")),
    ('Jojo grins. "Oh, I heard that."', shot("trolley.night", "j:stand/sly", "closeup,profile")),
    ("Then the first real water arrives.", shot("b2.night", "", "insert,low", 'fx:rain | sfx:water_pour | track:{tide:"ANKLES"}')),
    ("rolling under the stairwell door", shot("stairs.night", "", "wide,low", "fx:rain")),
    ("Mr. Bell looks down", shot("stairs.night", "b:stand/worried", "medium,closeup")),
    ('"At this speed', shot("stairs.night", "b:point/worried", "closeup,ots")),
    ("You glance at the stair door", shot("chain.night", "", "insert,closeup")),
    ("You look back at Exit D.", shot("exitd.night", "h:look_up/worried", "back,wide")),
    ("Mrs. Alder watches your face", shot("b2.night", "a:stand/neutral h:stand/worried", "ots,profile")),
    ("Jojo kneels and opens", shot("exitd.night", "j:crouch/determined", "insert,closeup,low")),
] + freeze(("WAIT UPSTAIRS", "SHOUT AND BANG", "BACK TO EXIT D"), "ledge,wind,gap", ["Freeze. Option one, wait for rescue", "Option two, shout and bang", "Option three, go back to Exit D", "Pause the video."], "The water does not wait.", "stairs.night", "h:stand/scared j:crouch/worried") + [
    ("You choose option three. Jojo presses", shot("exitd.night", "j:stand/determined", "closeup,ots", "sfx:door_creak")),
    ("He wipes his hands", shot("exitd.night", "j:stand/neutral h:stand/worried", "medium,low")),
    ("Rain, rust and a decade", shot("exitd.night", "", "insert,closeup", "fx:dust")),
    ("He picks a flat tool", shot("exitd.night", "j:reach/determined", "insert,closeup")),
    ("and the whole door gives", shot("exitd.night", "", "wide,low", "sfx:door_creak")),
    ("The street door was chained", shot("chain.night", "", "insert,wide")),
    ("Neither sign said it was unsafe.", shot("exitd.night", "h:stand/neutral", "closeup,medium")),
    ("And the old loading bay", shot("bay.dusk", "", "xwide,wide")),
    ("It is half past ten.", shot("b2.night", "h:stand/worried", "closeup,medium", 'fx:rain | track:{hours:"1.7",phone:"52%",tide:"KNEES"}')),
    ("## CH4 | THE LAST HOUR", None), ("// ACT sacrifice", None),
    ("Then the stairwell lights die.", shot("stairs.night", "", "wide,low", "fx:flicker | sfx:power_down")),
    ("Everything goes black,", shot("stairs.blackout", "", "closeup,insert", "fx:flicker")),
    ("A deep metallic groan", shot("b2.blackout", "", "wide,low", "sfx:impact")),
    ("Water at your waist.", shot("b2.night", "h:stand/scared", "medium,low", 'fx:rain | track:{hours:"1",tide:"WAIST"}')),
    ("Forty-one percent.", shot("b2.night", "h:phone_hold/scared", "insert,closeup", 'track:{hours:"1",phone:"41%",tide:"WAIST"}')),
] + freeze(("PUSH TOGETHER", "TAKE OUT PINS", "BREAK THE CHAIN"), "rope,chalk,gap", ["Freeze. Option one, push on the door", "Option two, take the hinge pins", "Option three, run for the chained", "Pause the video."], "The door is your only chance.", "exitd.night", "h:stand/scared j:stand/worried b:stand/worried a:stand/worried") + [
    ("// ACT climax", None),
    ("You choose option two. Jojo kneels", shot("exitd.night", "j:crouch/determined", "insert,closeup,low", "sfx:click")),
    ("A bolt clicks,", shot("exitd.night", "", "insert,closeup", "sfx:click")),
    ("All four of you lift it", shot("exitd.night", "h:reach/determined j:reach/determined b:reach/determined a:reach/determined", "wide,medium", "sfx:impact")),
    ("and a cold, clean wind", shot("exitd.night", "h:look_up/relieved", "closeup,back", "sfx:wind")),
    ("You were not pushing at a lock.", shot("exitd.night", "", "insert,closeup")),
    ("A swollen door fights back", shot("exitd.night", "j:stand/neutral", "medium,low")),
    ("Take out the pins,", shot("exitd.night", "", "insert,wide")),
    ("Beyond the door is", shot("bay.dusk", "", "wide,low")),
    ("climbing out of the dark", shot("bay.dusk", "", "xwide,wide", "fx:dust")),
    ("The loading bay. Two storeys", shot("bay.dusk", "h:look_up/relieved", "back,wide")),
    ("Mr. Bell steps through first,", shot("bay.dusk", "b:walk/relieved", "medium,wide")),
    ("then Mrs. Alder with her trolley", shot("bay.dusk", "a:walk/relieved j:walk/relieved", "wide,medium")),
    ("Water at your hips behind you.", shot("b2.night", "", "insert,low", 'fx:rain | track:{phone:"37%",tide:"WAIST"}')),
    ("// ACT resolution", None),
    ("You climb to the top,", shot("street.dusk", "h:look_up/relieved", "back,wide")),
    ("streetlights standing in it", shot("boat.dusk", "", "xwide,wide", "fx:rain")),
    ("A rescue boat rolls past.", shot("boat.dusk", "", "wide,low")),
    ("A rescue crew waves a torch", shot("boat.dusk", "h:hands_up/relieved j:hands_up/relieved b:hands_up/relieved a:hands_up/relieved", "wide,medium", "fx:beam")),
    ("At midnight the flood crests,", shot("street.dusk", "", "xwide,wide", "sfx:thunder")),
    ("two metres above", shot("ramp.night", "", "insert,wide")),
    ("Mrs. Alder shares peaches", shot("street.dusk", "a:reach/relieved", "medium,closeup")),
    ('"I told you,', shot("street.dusk", "a:stand/sly", "closeup,profile")),
    ("Mr. Bell reads the sign", shot("bay.dusk", "b:stand/relieved", "closeup,medium")),
    ('"I wrote that sign', shot("bay.dusk", "b:point/relieved", "ots,closeup")),
    ('"Thirty years ago.', shot("bay.dusk", "b:stand/neutral", "profile,medium")),
    ("So be honest.", shot("street.dusk", "h:look_up/neutral", "back,wide")),
    ("At the foot of that ramp", shot("ramp.night", "", "insert,low")),
    ("// LASTLINE", None),
    ("The door marked do not use", shot("bay.dusk", "h:stand/relieved j:stand/relieved b:stand/relieved a:stand/relieved", "wide,low")),
    ("Next time, the water", shot("bay.dusk", "h:stand/relieved j:stand/relieved b:stand/relieved a:stand/relieved", "wide,medium", "cta:subscribe")),
]

G1 = ["stand", "look_up", "shrug", "point", "reach"]
CALM = ["neutral", "worried", "determined", "relieved", "sad"]
TENSE = ["scared", "shocked", "worried", "determined"]
CAMS = ["push 1.00>1.14", "pan_l", "pull 1.18>1.02", "tilt_up", "pan_r", "push 1.05>1.20", "parallax_drift", "tilt_down", "pull 1.22>1.06", "rack_focus"]
LAST, CI = {}, [0]


def rotate(tags):
    """Never the same pose+expression twice in a row for one character, and a camera move on every shot (P-018/P-020)."""
    out = []
    for seg in tags.split(" | "):
        m = re.fullmatch(r"(hero|jojo|bell|alder)\:(\w+)/(\w+)", seg.strip())
        if m:
            c, p, e = m.groups()
            if LAST.get(c) == (p, e):
                fam = TENSE if e in TENSE else CALM
                e = fam[(fam.index(e) + 1) % len(fam)] if e in fam else fam[0]
                if p in G1:
                    p = G1[(G1.index(p) + 1) % len(G1)]
            LAST[c] = (p, e)
            seg = f"{c}:{p}/{e}"
        out.append(seg)
    s = " | ".join(out)
    if "cam:" not in s and "ov:option_cards" not in s and "fx:flicker" not in s:
        s += " | cam:" + CAMS[CI[0] % len(CAMS)]
        CI[0] += 1
    return s


HEAD = """TITLE: The Door Marked Do Not Use
LENGTH_MIN: 8
VOICE: default
CHARACTERS:
- hero = rig_hero(outfit=mustard, hair=short, skin=brown)
- jojo = rig_hero(outfit=cobalt, hat=cap, hair=curly, skin=tan)
- bell = rig_hero(outfit=olive, age=old, hair=short, skin=dark)
- alder = rig_hero(outfit=coral, age=old, hair=bun, skin=light)
LOCATIONS:
- street: flooded city street at night seen from a raised pavement, brown river water covering the road, streetlights standing in the water, heavy rain, orange glow in the sky
- b3: lowest level of an underground car park at night with concrete pillars, parked cars, painted bays and dim flickering strip lights, thin water on the floor
- ramp: steep concrete car park ramp sloping down, a thin sheet of shiny water sliding down it, dim strip lights, wet walls
- shutter: roller shutter half closed at the top of a car park ramp, street light shining under the gap, rain outside
- booth: small car park attendant booth with a window, a kettle, a clipboard and a torch, dim yellow light
- trolley: shopping trolley full of tinned peaches and bags in a car park, torch light, concrete pillar behind
- lift: lift lobby in a car park with a metal lift door and a small floor number display, flickering light, painted concrete
- stairs: concrete fire stairwell with metal handrails and painted floor numbers, torch light, echoing, damp walls
- b2: wide grey underground car park floor with pillars and painted bays, dim light, shiny damp concrete, water noise below
- exitd: end of a car park corridor with a tall grey metal door and an old red sign saying Exit D do not use loading bay, rust on the hinges, dim light
- chain: top of a concrete stairwell with a street door wrapped in a heavy chain and padlock, thin light under the door
- bay: dry steep concrete loading bay ramp climbing out of the dark toward a pale orange evening sky, calm and bright
- boat: flooded street at dusk with a rescue boat, streetlights standing in brown water, orange sky, rescue workers with torches
MUSIC_MOODS:
- CH1: calm
- CH2: mystery
- CH3: mystery
- CH4: tense

"""
pos, rows = 0, []
for a, tags in T:
    if tags is None:
        rows.append(("raw", a))
        continue
    i = TXT.find(a, pos)
    assert i >= 0, a
    rows.append(("shot", i, tags))
    pos = i + 1
st = [r[1] for r in rows if r[0] == "shot"]
assert st[0] == 0
en = st[1:] + [len(TXT)]
out, k = [HEAD.rstrip("\n"), ""], 0
for r in rows:
    if r[0] == "raw":
        out.append(r[1])
    else:
        out += ["@ " + rotate(r[2]), TXT[st[k]:en[k]].strip()]
        k += 1
text = "\n".join(out) + "\n"
open(os.path.join(D, "script.md"), "w", encoding="utf-8", newline="\n").write(text)
body = " ".join(l for l in text.splitlines() if l and not l.startswith(("@", "//", "##", "-", "TITLE", "LENGTH", "VOICE", "CHARACTERS", "LOCATIONS", "MUSIC")))
assert re.sub(r"\s+", " ", body).strip() == TXT, "narration changed"
print("shots", k, "words", len(re.findall(r"[A-Za-z0-9'’\-]+", TXT)))

"""script.md = owner narration (sliced, never retyped) + shot table. P-018: shot sizes, locations, poses and expressions rotate every beat."""
import os
import re

D = os.path.dirname(os.path.abspath(__file__))
TXT = " ".join(l.strip() for l in open(os.path.join(D, "narration.txt"), encoding="utf-8").read().splitlines() if l.strip())
C = {"h": "hero", "r": "rosa", "o": "okafor", "t": "theo", "v": "vane"}


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
    ("## CH1 | FIVE HOURS TO SUNRISE", None), ("// ACT hook", None),
    ("Three passengers,", shot("snow.night", "", "xwide", 'track:{hours:"5"}')),
    ("five hours until sunrise,", shot("window.night", "", "insert,closeup")),
    ("and one ticket", shot("corridor.night", "h:look_up/worried", "ots,low")),
    ("By sunrise,", shot("cab.night", "h:stand/scared", "closeup,back")),
    ("// ACT act1", None),
    ("The night train stops", shot("corridor.night", "h:sit/sleepy", "medium,closeup")),
    ("Then the engine dies", shot("corridor.night", "h:stand/shocked", "wide,low,closeup", "fx:flicker")),
    ("Somewhere ahead,", shot("snow.night", "", "xwide,wide")),
    ("The conductor is Rosa", shot("cab.night", "r:stand/neutral h:stand/neutral", "medium,closeup,ots")),
    ("She reaches dispatch", shot("cab.night", "r:phone_hold/worried", "insert,ots,medium")),
    ('"Snowcat reaches you', shot("cab.night", "r:phone_hold/sad h:look_up/worried", "closeup,back")),
    ("Rosa checks the panel.", shot("cab.night", "r:point/worried", "insert,medium", 'track:{phone:"60%"}')),
    ("There are only three", shot("coach2.night", "o:sit/neutral t:sit/neutral v:sit/neutral", "wide,medium")),
    ("Mrs. Okafor,", shot("coach2.night", "o:write/relieved", "medium,insert")),
    ("Theo, sixteen,", shot("coach2.night", "t:reach/determined", "closeup,low")),
    ("And Mr. Vane,", shot("window.night", "v:stand/neutral", "profile,insert,closeup")),
    ("Rosa whispers one more", shot("cab.night", "r:stand/worried h:stand/neutral", "ots,closeup")),
    ("Forty minutes pass.", shot("window.night", "", "insert,closeup", 'track:{phone:"51%"}')),
    ("## CH2 | THE HEATERS", None), ("// ACT act2a", None),
] + freeze(("ALL HEATERS", "LIGHTS ONLY", "ONE ROOM"), "draught,glow,ledge", ["Freeze. Option one, keep the heaters", "Option two, switch the heaters off", "Option three, one heater", "Pause the video."], "Your battery keeps falling.", "corridor.night", "h:stand/worried r:stand/worried") + [
    ("You choose option three.", shot("compartment.night", "h:sit/worried o:sit/relieved t:sit/neutral", "medium,wide")),
    ("Mrs. Okafor hands out wool", shot("compartment.night", "o:reach/relieved", "insert,medium,closeup")),
    ("The drain slows", shot("cab.night", "r:point/relieved", "insert,ots", 'track:{phone:"55%"}')),
    ("Three heaters on low", shot("coach2.night", "", "wide,low,xwide")),
    ("It works.", shot("compartment.night", "h:sit/relieved", "closeup,medium")),
    ("Then Rosa goes pale.", shot("cab.night", "r:back_away/scared h:stand/worried", "closeup,ots")),
    ("Every percent of heat", shot("snow.night", "", "xwide,wide,insert", "fx:dust")),
    ("Four hours left.", shot("cab.night", "r:stand/worried", "insert,closeup", 'track:{hours:"4",phone:"44%"}')),
    ("## CH3 | THE TICKET", None), ("// ACT midpoint", None),
    ("Rescue needs a passenger list", shot("corridor.night", "r:write/neutral h:stand/neutral", "medium,insert,ots")),
    ("Mrs. Okafor, coach two", shot("coach2.night", "o:sit/neutral r:write/neutral", "profile,insert")),
    ("Then Mr. Vane hands over", shot("coach2.night", "v:reach/neutral r:reach/shocked", "insert,closeup,ots")),
    ('"Coach four, berth B,"', shot("coach2.night", "r:stand/shocked v:stand/neutral", "closeup,low,wide")),
    ("Nobody speaks.", shot("window.night", "v:stand/neutral", "silhouette,insert,profile")),
] + freeze(("MOVE HIM", "IGNORE IT", "ASK HIM"), "gap,wind,star", ["Freeze. Option one, move Mr. Vane", "Option two, ignore it", "Option three, ask him one question", "Pause the video."], "Your clock keeps running.", "coach2.night", "h:stand/worried v:stand/neutral") + [
    ('You choose option three. "What was', shot("coach2.night", "h:point/determined v:stand/neutral", "ots,closeup")),
    ("For the first time,", shot("coach2.night", "v:stand/relieved", "closeup,medium")),
    ('"The guard\'s van,"', shot("luggage.night", "v:point/neutral", "wide,insert,ots")),
    ("Remember the latch", shot("window.night", "v:reach/neutral", "insert,closeup")),
    ("A stranger doesn't know", shot("coach2.night", "h:stand/relieved v:stand/neutral", "medium,low")),
    ("Behind a plywood panel", shot("luggage.night", "t:reach/shocked h:crouch/worried", "insert,closeup,wide")),
    ("Theo finds a lighter.", shot("stove.night", "t:reach/determined", "insert,closeup", 'fx:embers')),
    ("Ten minutes later", shot("stove.night", "h:sit/relieved o:sit/relieved v:sit/neutral", "wide,medium,low", 'fx:embers | track:{phone:"41%"}')),
    ("Mrs. Okafor laughs", shot("stove.night", "o:stand/relieved v:stand/relieved", "medium,closeup")),
    ("If you trusted the old man", shot("stove.night", "h:stand/relieved o:stand/relieved t:stand/relieved", "wide,medium", "cta:subscribe | fx:embers")),
    ("Here is what you got wrong.", shot("window.night", "v:stand/relieved", "closeup,profile")),
    ("## CH4 | THREE IN THE MORNING", None), ("// ACT sacrifice", None),
    ("Three in the morning.", shot("snow.night", "", "xwide,wide", 'fx:snow | track:{hours:"3"}')),
    ("At four forty,", shot("cab.night", "r:stand/shocked h:stand/scared", "ots,wide", 'fx:alarm_pulse | track:{hours:"1.5",phone:"20%"}')),
    ("A long crack", shot("coach2.night", "", "low,wide,insert")),
    ("And a soft, steady hiss", shot("stove.night", "", "insert,closeup")),
    ("Earlier, when the fire caught", shot("stove.night", "v:point/neutral h:stand/worried", "closeup,ots")),
] + freeze(("SHUT LIGHTS", "GET DOWN", "CLEAR PIPE"), "battery,gap,chimney", ["Freeze. Option one, the battery alarm", "Option two, the crack in the roof", "Option three, the hiss", "Pause the video."], "The air is getting thick.", "stove.night", "h:stand/scared r:stand/scared") + [
    ("// ACT climax", None),
    ("You choose option three. Rosa holds", shot("roof.night", "h:reach/determined r:crouch/worried", "low,ots,wide")),
    ("A heavy slab of snow", shot("roof.night", "", "insert,wide,low", "fx:snow")),
    ("Grey smoke rises", shot("roof.night", "h:look_up/relieved", "back,wide")),
    ('"The panel cries wolf', shot("cab.night", "r:point/relieved h:stand/relieved", "medium,closeup")),
    ("Silence. Only the stove", shot("stove.night", "", "insert,closeup")),
    ("Five fifty.", shot("snow.dusk", "", "xwide,wide", 'track:{hours:"0.3",phone:"9%"}')),
    ("Theo hears it first.", shot("coach2.dusk", "t:look_up/shocked", "closeup,profile,ots")),
    ("Rosa's hand hovers", shot("cab.dusk", "r:reach/worried", "insert,closeup,ots")),
] + freeze(("ALL LIGHTS", "HORN NOW", "WAIT, THEN HORN"), "glow,wind,star", ["Freeze. Option one, switch on every marker", "Option two, blow all three horn", "Option three, wait until the engine", "Pause the video."], "They might drive right past.", "cab.dusk", "h:stand/scared r:stand/worried") + [
    ("You choose option three. You wait.", shot("snowcat.dusk", "", "xwide,wide,low")),
    ("Three long blasts", shot("snow.dusk", "", "wide,low,xwide", "fx:dust")),
    ("Dispatch said it", shot("cab.dusk", "r:stand/relieved h:stand/relieved", "ots,closeup,medium")),
    ("// ACT resolution", None),
    ("The snowcat crew", shot("valley.day", "h:walk/relieved o:walk/relieved t:walk/relieved", "wide,xwide,medium")),
    ("It is dated forty years", shot("valley.day", "v:reach/neutral r:reach/shocked", "insert,closeup,ots")),
    ('"The guard\'s name,"', shot("valley.day", "v:stand/neutral r:stand/shocked", "profile,closeup,medium")),
    ("Rosa stares down", shot("valley.day", "r:stand/shocked", "closeup,insert")),
    ('"I ride this train', shot("valley.day", "v:stand/relieved r:stand/relieved", "medium,wide,low")),
    ("So be honest.", shot("valley.day", "h:look_up/neutral", "back,wide")),
    ("// LASTLINE", None),
    ("The ticket that should not", shot("valley.day", "v:stand/relieved r:stand/relieved h:stand/relieved", "wide,low")),
    ("Next time, you'll have", shot("valley.day", "v:stand/relieved r:stand/relieved h:stand/relieved", "wide,medium", "cta:subscribe")),
]

HEAD = """TITLE: The Ticket That Should Not Exist
LENGTH_MIN: 8
VOICE: default
CHARACTERS:
- hero = rig_hero(outfit=red, hair=curly, skin=dark)
- rosa = rig_hero(outfit=navy, hat=cap, hair=bun, skin=light)
- okafor = rig_hero(outfit=plum, hair=bun, age=old, skin=dark)
- theo = rig_hero(outfit=olive, hat=beanie, hair=short, skin=tan)
- vane = rig_hero(outfit=grey, hair=short, age=old, skin=light)
LOCATIONS:
- snow: night train stopped in deep snow in a whiteout, amber carriage lights glowing in the white, buried track ahead, cold blue-white night
- window: close view of a frosted train window from inside, frost patterns on the glass, dim amber light, wooden window frame
- corridor: narrow train carriage corridor at night with frosted windows, dim amber ceiling lights, wooden panels
- cab: conductor alcove at the end of a carriage with a small battery panel with dials, a radio handset and a torch, dim amber light
- coach2: seating carriage of an old night train with wooden benches, knitted blankets, frosted windows, dim amber light
- compartment: tiny train compartment with two facing benches, wool blankets, small heater under the window, frost on the glass, warm dim light
- luggage: back of an old carriage with a luggage rack and a plywood panel on the wall, dim amber light, dust
- stove: small train compartment glowing orange from a squat black iron stove with a sack of coal, wool blankets, warm light, frost on the windows
- roof: view up through a train roof hatch at a snow covered chimney pipe and a dark snowy sky, falling snow
- snowcat: a snowcat vehicle with bright headlights driving through a whiteout toward a stopped train, snow swirling
- valley: snowy mountain valley at sunrise with a pink sky, a stopped night train and a snowcat in the snow, calm and bright
MUSIC_MOODS:
- CH1: calm
- CH2: mystery
- CH3: mystery
- CH4: tense

"""
G1 = ["stand", "look_up", "shrug", "point", "reach"]
CALM = ["neutral", "worried", "determined", "relieved", "sad"]
TENSE = ["scared", "shocked", "worried", "determined"]
LAST = {}


def rotate(tags):
    """Never the same pose+expression twice in a row for one character (P-018 / Doctor V6-STATIC)."""
    out = []
    for seg in tags.split(" | "):
        m = re.fullmatch(r"(hero|rosa|okafor|theo|vane):(\w+)/(\w+)", seg.strip())
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
    return " | ".join(out)


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

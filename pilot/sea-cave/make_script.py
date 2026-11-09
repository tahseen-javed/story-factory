"""Builds script.md from narration.txt (the owner's script, never edited) + the shot table below. Narration is sliced, never retyped, so it stays word for word."""
import os
import re

D = os.path.dirname(os.path.abspath(__file__))
TXT = " ".join(l.strip() for l in open(os.path.join(D, "narration.txt"), encoding="utf-8").read().splitlines() if l.strip())


def cards(labels, icons, focus):
    return 'ov:option_cards("%s","%s","%s","%d","%s")' % (labels[0], labels[1], labels[2], focus, icons)


def freeze(labels, icons, anchors, hold_anchor, who):
    """anchors: option 1, 2, 3, 'Pause the video.' ; hold_anchor: the stakes line that carries the 4.5 s decision hold."""
    base = "%s | %s" % (who[0], who[1])
    out = []
    for k, a in enumerate(anchors):
        out.append((a, "%s | %s | %s" % (who[0], who[1], cards(labels, icons, k + 1 if k < 3 else 0)) + (" | fr:ots" if k == 0 else " | fr:wide" if k % 2 else " | fr:medium")))
    out.append((hold_anchor, "%s | %s | %s | fr:ots" % (who[0], who[1], cards(labels, icons, 0))))
    out.append(("// HOLD decision 4.5", None))
    return out


H, W_ = "hero:stand/worried", "walt:stand/worried"
F1 = freeze(("LEFT TUNNEL", "MIDDLE TUNNEL", "RIGHT TUNNEL"), "chalk,draught,wind", ["Freeze. Option one, the wide left", "Option two, the narrow middle", "Option three, the right tunnel", "Pause the video."], "Your light keeps burning.", ("fork.night", "%s | %s | fx:beam" % (H, W_)))
F2 = freeze(("SPARE BATTERY", "ROPE", "WATER BOTTLE"), "battery,rope,bottle", ["Freeze. Option one, the spare battery", "Option two, the rope", "Option three, the full water bottle", "Pause the video."], "The tide does not wait.", ("narrow.night", "%s | %s | fx:beam" % (H, W_)))
F3 = freeze(("GREEN GLOW", "DARK CHIMNEY", "WAIT ON LEDGE"), "glow,chimney,ledge", ["Freeze. Option one, swim", "Option two, climb the dark chimney", "Option three, climb onto the ledge", "Pause the video."], "Three hours and forty minutes of light.", ("chamber.night", "%s | %s | fx:beam" % (H, W_)))
F4 = freeze(("CHIMNEY", "LOW ARCH", "BACK TO GAP"), "star,arch,gap", ["Freeze. Option one, the chimney", "Option two, the low arch", "Option three, back through the gap", "Pause the video."], "The sea is already thinking about coming back.", ("chamber.night", "hero:stand/worried | walt:stand/worried | fx:beam"))


def fz(F, loc_tag, track=None):
    res = []
    for i, (a, t) in enumerate(F):
        if t is None:
            res.append((a, None))
            continue
        loc, rest = t.split(" | ", 1)
        res.append((a, "%s | %s" % (loc, rest) + ((" | track:" + track) if (track and i == 0) else "")))
    return res


TABLE = [
    ("## CH1 | FIVE HOURS OF LIGHT", None), ("// ACT hook", None),
    ("You have five hours", 'mouth.day | hero:stand/neutral | walt:stand/neutral | fx:beam | fr:wide | track:{lamp:"5h",tide:"SHALLOW"}'),
    ("It starts as a quiet Sunday", "mouth.day | hero:stand/neutral | walt:stand/neutral | fr:medium"),
    ('"Twenty minutes in', "mouth.day | hero:stand/neutral | walt:point/neutral | fr:ots"),
    ("Then the rock above", "mouth.day | hero:back_away/scared | walt:back_away/shocked | cam:shake_medium | fr:wide"),
    ("A slab slides down", "mouth.blackout | hero:stand/scared | walt:stand/shocked | fx:dust | fr:wide"),
    ("Your headlamp clicks on", "mouth.night | hero:stand/worried | fx:beam,dust | fr:ots"),
    ("Under your boots", "passage.night | hero:stand/worried | fx:beam | fr:low"),
    ("Walt puts his palm", "passage.night | hero:stand/worried | walt:stand/neutral | fx:beam | fr:medium"),
    ("You walk.", "passage.night | hero:walk/determined | walt:walk/neutral | fx:beam | fr:back"),
    ("The passage splits.", 'fork.night | hero:stand/worried | walt:stand/worried | fx:beam | fr:wide | track:{tide:"ANKLES"}'),
] + fz(F1, "fork") + [
    ("You follow the arrow.", "deadend.night | hero:walk/neutral | walt:walk/neutral | fx:beam | fr:back"),
    ("Visitors drew", 'deadend.night | hero:stand/sad | walt:stand/sad | fx:beam | fr:wide | track:{lamp:"4h30"}'),
    ("The middle tunnel was the answer", "fork.night | hero:point/determined | walt:stand/neutral | fx:beam | fr:medium"),
    ("## CH2 | THE NARROW WAY", None), ("// ACT act2a", None),
    ("Inside the middle tunnel", "narrow.night | hero:walk/neutral | walt:walk/neutral | fx:beam | fr:back"),
    ("You squeeze forward", "narrow.night | hero:crouch/worried | walt:crouch/worried | fx:beam | fr:ots"),
    ('"One thing goes through', "narrow.night | hero:stand/worried | walt:point/neutral | fx:beam | fr:medium"),
    ("You empty your bag", 'narrow.night | hero:crouch/worried | fx:beam | fr:insert | track:{tide:"KNEES"}'),
] + fz(F2, "narrow") + [
    ("Your fingers close", "narrow.night | hero:reach/worried | walt:reach/shocked | fx:beam | fr:insert"),
    ('"The ladder\'s gone', "narrow.night | hero:stand/sad | walt:stand/neutral | fx:beam | fr:ots"),
    ("You keep the rope.", "narrow.night | hero:stand/determined | fx:beam | fr:medium"),
    ("You push through the gap.", "narrow.night | hero:crouch/worried | fx:beam | fr:back"),
    ("Then your lamp flickers.", "narrow.blackout | hero:stand/shocked | fx:flicker | fr:closeup"),
    ("Nothing. No sound", "narrow.blackout | hero:stand/scared | fr:silhouette"),
    ("You slap the lamp.", 'narrow.night | hero:stand/relieved | walt:stand/relieved | fx:beam | fr:medium | track:{lamp:"4h"}'),
    ("If you kept the rope", "narrow.night | hero:stand/relieved | walt:stand/relieved | cta:subscribe | fx:beam | fr:wide"),
    ("## CH3 | THE WHITE LINE", None), ("// ACT midpoint", None),
    ("The new chamber", "chamber.night | hero:stand/scared | walt:stand/worried | fx:beam | fr:wide"),
    ("Then Walt points", "chamber.night | hero:stand/worried | walt:point/determined | fx:beam | fr:ots"),
    ('"That\'s a waterline', "chamber.night | hero:stand/neutral | walt:point/neutral | fx:beam | fr:medium"),
    ("Everything you believed flips.", "chamber.night | hero:stand/shocked | walt:stand/neutral | fx:beam | fr:closeup"),
    ("But the water is at your waist", 'chamber.night | hero:stand/worried | walt:point/worried | fx:beam | fr:wide | track:{tide:"WAIST"}'),
] + fz(F3, "chamber", '{lamp:"3h40"}') + [
    ("You wade toward the glow.", "chamber.night | hero:walk/determined | fx:beam | fr:back"),
    ("It is your own headlamp", "chamber.night | hero:stand/neutral | walt:stand/neutral | fx:beam | fr:medium"),
    ("The ledge was right", "chamber.night | hero:point/neutral | walt:stand/neutral | fx:beam | fr:wide"),
    ("You climb.", "chamber.night | hero:reach/determined | walt:reach/worried | fx:beam | fr:wide"),
    ("Darkness. Real darkness.", 'chamber.blackout | hero:sit/neutral | walt:sit/neutral | fr:silhouette | track:{lamp:"OFF"}'),
    ('"I was lost in this cave once', "chamber.blackout | hero:sit/neutral | walt:sit/sad | fr:silhouette"),
    ("The water touches the white line.", 'chamber.blackout | hero:sit/worried | walt:sit/neutral | fr:silhouette | track:{tide:"SALT LINE"}'),
    ("Then, slowly,", 'chamber.blackout | hero:sit/relieved | walt:sit/relieved | fr:wide | track:{tide:"DRAINING"}'),
    ("## CH4 | THE TIDE TURNS", None), ("// ACT resolution", None),
    ("When you switch the lamp back on", 'chamber.night | hero:stand/relieved | walt:stand/neutral | fx:beam | fr:medium | track:{lamp:"2h"}'),
] + fz(F4, "chamber") + [
    ("Up always feels like out.", "chamber.night | hero:look_up/worried | walt:look_up/neutral | fx:beam | fr:ots"),
    ("You choose the arch.", "chamber.night | hero:walk/determined | walt:walk/neutral | fx:beam | fr:back"),
    ("You crawl, then walk", "beach.night | hero:run/relieved | walt:walk/relieved | fr:wide"),
    ('"This is how he got me out', "beach.night | hero:stand/relieved | walt:stand/neutral | fr:medium"),
    ("The slab that trapped you", "beach.night | hero:stand/relieved | walt:stand/relieved | fr:wide"),
    ("You spent hours", "beach.night | hero:stand/neutral | walt:stand/neutral | fr:ots"),
    ("So tell me honestly.", "beach.night | hero:look_up/neutral | walt:look_up/neutral | fr:back"),
    ("// LASTLINE", None),
    ("The water you feared", "beach.night | hero:stand/relieved | walt:stand/relieved | fr:wide"),
    ("Next time, the clock", "beach.night | hero:stand/relieved | walt:stand/relieved | cta:subscribe | fr:wide"),
]

HEADER = """TITLE: The Water You Fear Is The Only Way Out
LENGTH_MIN: 8
VOICE: default
CHARACTERS:
- hero = rig_hero(outfit=cobalt, hat=cap, hair=curly, skin=brown)
- walt = rig_hero(outfit=olive, hair=short, age=old, skin=light)
LOCATIONS:
- mouth: sea cave entrance chamber with a fallen slab of rock blocking a bright opening, wet stones, a thin film of water on the floor, cold blue-teal rock walls
- passage: narrow natural sea cave passage with wet rock walls, a level white salt crust line running along both walls at chest height, shallow water on the floor, cold blue-teal light
- fork: cave junction where one passage splits into three tunnels, a wide left tunnel with a dry floor and a white chalk arrow painted on the wall, a narrow wet middle tunnel, a right tunnel sloping downward, ankle deep water, cold blue-teal rock
- deadend: smooth dead-end cave wall covered in white chalk scribbles, tally marks and old dates, wet floor, cold blue-teal rock
- narrow: very narrow wet cave tunnel with tight rock walls pinching into a small gap the width of a mailbox slot, dripping water, cold blue-teal rock
- chamber: huge sea cave chamber with a high ceiling, a clear level white salt line all the way around the walls at chest height, water filling the floor, a low arch on the far side with a soft green glow, a dark chimney shaft above and a rock ledge, cold blue-teal rock
- beach: silver moonlit beach in front of a sea cave mouth, wet sand, waves pulled far back, a sky full of stars, calm night, cold blue-teal and silver tones
MUSIC_MOODS:
- CH1: calm
- CH2: mystery
- CH3: mystery
- CH4: hopeful

"""

pos, rows = 0, []
for anchor, tags in TABLE:
    if tags is None:
        rows.append(("raw", anchor))
        continue
    i = TXT.find(anchor, pos)
    assert i >= 0, anchor
    rows.append(("shot", i, tags))
    pos = i + 1
starts = [r[1] for r in rows if r[0] == "shot"]
assert starts[0] == 0, "the first shot must start at the first word"
ends = starts[1:] + [len(TXT)]
out, k = [HEADER.rstrip("\n"), ""], 0
for r in rows:
    if r[0] == "raw":
        out.append(r[1])
    else:
        out.append("@ " + r[2])
        out.append(TXT[starts[k]:ends[k]].strip())
        k += 1
text = "\n".join(out) + "\n"
open(os.path.join(D, "script.md"), "w", encoding="utf-8", newline="\n").write(text)
body = " ".join(l for l in text.splitlines() if l and not l.startswith(("@", "//", "##", "-", "TITLE", "LENGTH", "VOICE", "CHARACTERS", "LOCATIONS", "MUSIC")))
assert re.sub(r"\s+", " ", body).strip() == TXT, "narration changed"
print("shots", k, "words", len(re.findall(r"[A-Za-z0-9'’\-]+", TXT)))

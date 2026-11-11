"""script.md = owner narration (sliced, never retyped) + auto shot plan (scene map + keyword inserts + rotating frames/poses/cameras). P-018/P-020."""
import os
import re

D = os.path.dirname(os.path.abspath(__file__))
TXT = re.sub(r"\s+", " ", open(os.path.join(D, "narration.txt"), encoding="utf-8").read()).strip()
C = {"h": "hero", "m": "maisie", "a": "amos"}
NW = len(TXT.split())


def W(s):
    return len(s.split())


def who(s):
    return " | ".join(f"{C[p.split(':')[0]]}:{p.split(':', 1)[1]}" for p in s.split())


def shot(loc, ch, fr, extra=""):
    return " | ".join(x for x in [loc, who(ch) if ch else "", f"fr:{fr}", extra.strip(" |")] if x)


def S(a, loc, ch="", ex=""):
    return ("S", a, loc, ch, ex)


def X(a, tags, tags2=None):
    return ("X", a, tags, tags2)


def R(a, raw):
    return ("R", a, raw)


def FZ(labels, icons, anchors, hold, loc, ch):
    out = []
    for k, a in enumerate(anchors):
        def card(n):
            return 'ov:option_cards("%s","%s","%s","%d","%s")' % (labels[0], labels[1], labels[2], n, icons)
        n = k + 1 if k < 3 else 0
        fl = " | fx:flicker" if k == 3 else ""
        out.append(X(a, shot(loc, ch, ["ots", "wide", "medium", "wide"][k], card(n) + fl),
                     shot(loc, ch, ["closeup", "medium", "closeup", "closeup"][k], card(n) + fl)))
    out.append(X(hold, shot(loc, ch, "ots", 'ov:option_cards("%s","%s","%s","0","%s")' % (labels[0], labels[1], labels[2], icons))))
    return out


HM = "h:stand|look_up|point|reach/worried|determined|neutral m:stand|look_up|shrug/neutral|worried|scared"
HO = "h:stand|look_up|point|reach/worried|determined|neutral"
HMA = HM + " a:stand|reach|shrug/relieved|neutral|worried"

P = [
    R("You have three logbooks,", "## CH1 | SIX IN THE EVENING"), R("You have three logbooks,", "// ACT hook"),
    X("You have three logbooks,", "desk.night | fr:insert,closeup | fx:flicker | sfx:wind | cam:push 1.00>1.15"),
    X("four hours of lamp oil,", 'burner.night | fr:insert,low | cam:push 1.05>1.20 | track:{oil:"4H"}'),
    X("and one forgery.", "desk.night | hero:point/shocked | fr:closeup,low | sfx:heartbeat | cam:pull 1.18>1.02"),
    X("By sunrise, you will know", "lamp.night | hero:look_up/determined | fr:wide,low | fx:smoke | cam:tilt_up"),
    S("The supply boat drops you on Gull Rock", "dock.dusk", HO, "fx:smoke"),
    R("You are a relief keeper.", "// ACT act1"),
    S("The door opens before you knock.", "door.dusk", HM, "fx:smoke"),
    S("Behind you, the supply boat is already", "dock.dusk", HO, "fx:smoke"),
    S("Here is your clock.", "lamp.night", HM),
    X("The backup is an old oil burner,", 'burner.night | fr:insert,closeup | cam:push 1.05>1.20 | track:{oil:"4H"}'),
    X("The night ferry passes the reef at eleven,", 'reef.night | fr:wide,low | cam:pull 1.18>1.02 | track:{ferry:"5H"}'),
    R("You climb a hundred and twelve steps.", "## CH2 | THE CRACKED PANE"),
    S("You climb a hundred and twelve steps.", "stairs.night", HM),
    R("You strike a match.", "// ACT act2a"),
    S("You strike a match.", "lamp.night", HM, "fx:dust"),
    S("Then you hear it.", "lamp.night", HM, "fx:dust | sfx:wind"),
    X("At this rate, oil for two and a half hours.", 'burner.night | fr:insert,closeup | fx:flicker | track:{oil:"2.5H"}'),
] + FZ(("FULL FLAME", "PLUG THE PANE", "LAMP OUT"), "glow,draught,star",
       ["Freeze. Option one, burn full flame", "Option two, plug the cracked pane", "Option three, put the lamp out", "Pause the video."],
       "Your oil keeps burning.", "lamp.night", "h:stand/worried m:look_up/scared") + [
    R("You choose option two. The coat smells", "// HOLD decision 4.5"),
    S("You choose option two. The coat smells", "lamp.night", HM, "fx:dust"),
    X("Oil for four and a half hours.", 'burner.night | fr:insert,closeup | track:{oil:"4.5H"}'),
    S("And the horn plan?", "stairs.night", HM),
    S("You sit on the cold iron floor.", "lamp.night", HM),
    X("Nothing. No sound at all.", "lamp.night | hero:stand/worried | fr:wide,low | fx:flicker | cam:hold"),
    R("Seven thirty.", "## CH3 | SEVEN THIRTY"),
    S("Seven thirty.", "desk.night", HM),
    X("Seven thirty.", 'desk.night | fr:insert,wide | cam:push 1.05>1.20 | track:{oil:"<4H",ferry:"3H30"}'),
    S("On the gallery rail sits a hand signal lamp", "gallery.night", HM, "fx:smoke"),
] + FZ(("NORTH REEF", "SEAL CAVE", "SOUTH SLIPWAY"), "ledge,arch,rope",
       ["Freeze. Option one, the north reef", "Option two, the seal cave", "Option three, the south slipway", "Pause the video."],
       "The tide keeps rising.", "gallery.night", "h:stand/worried m:look_up/worried") + [
    R("You choose option two. The wind is from the west.", "// HOLD decision 4.5"),
    S("You choose option two. The wind is from the west.", "gallery.night", HM, "fx:smoke"),
    S("You aim the lamp at the east cliffs", "gallery.night", HM, "fx:smoke"),
    S("Maisie grips the rail", "gallery.night", HM, "fx:smoke"),
    X("Subscribe so this light keeps finding you.", "gallery.night | hero:stand/relieved | maisie:stand/relieved | fr:medium,closeup | cam:push 1.05>1.20 | cta:subscribe"),
    R("You go back to the desk to see", "## CH4 | THE GREEN LOG"), R("You go back to the desk to see", "// ACT midpoint"),
    S("You go back to the desk to see", "desk.night", HM),
    X("You thought you came to help an old keeper.", "desk.night | hero:stand/shocked | fr:medium,ots | cam:pull 1.18>1.02"),
    X("The real keeper is twelve.", "desk.night | maisie:stand/worried | fr:closeup,low | sfx:stinger_chapter | cam:push 1.05>1.25"),
    R("Ten forty.", "// ACT act2b"),
    S("Ten forty.", "lamp.night", HM, "fx:flicker"),
    X("Ten forty.", 'burner.night | fr:insert,low | cam:push 1.05>1.20 | track:{oil:"30M",ferry:"20M"}'),
] + FZ(("FLAME AND GREEN", "WAIT FOR HORN", "FLAME FOR BELL"), "glow,star,wind",
       ["Freeze. Option one, full flame now, and follow", "Option two, wait until the horn", "Option three, full flame now", "Pause the video."],
       "Something big is very close.", "lamp.night", "h:stand/scared m:look_up/scared") + [
    R("You choose option three. You turn the wick", "// HOLD decision 4.5"),
    S("You choose option three. You turn the wick", "lamp.night", HM, "fx:flicker"),
    X("The ferry. Two hundred metres", 'ferry.night | fr:wide,low | cam:pull 1.18>1.02 | track:{ferry:"SAFE"}'),
    S("The horn was the ferry too,", "lamp.night", HM),
    S('The radio crackles. "Gull Rock', "lamp.night", HM),
    R("Ten fifty-five.", "## CH5 | TEN FIFTY-FIVE"),
    X("Ten fifty-five.", 'burner.night | fr:insert,low | fx:flicker | track:{oil:"5M"}'),
    R("Then the torch in the seal cave", "// ACT sacrifice"),
    S("Then the torch in the seal cave", "gallery.night", HM, "fx:smoke"),
    S("You open the black book to its last page.", "desk.night", HM),
] + FZ(("MAIN BEAM", "SIGNAL LAMP", "TWO LANTERNS"), "glow,star,chimney",
       ["Freeze. Option one, keep the main beam", "Option two, flash the signal lamp", "Option three, carry two lanterns", "Pause the video."],
       "His boat is already moving.", "desk.night", "h:stand/scared m:look_up/scared") + [
    R("You choose option three. You and Maisie race", "// HOLD decision 4.5"),
    R("You choose option three. You and Maisie race", "// ACT climax"),
    S("You choose option three. You and Maisie race", "stairs.night", HM),
    S("One lantern on the post.", "slipway.night", HM, "fx:smoke"),
    S("Behind you, high above, the main lamp coughs", "slipway.blackout", HM, "fx:smoke"),
    S("Then, out of the fog, the creak of oars.", "slipway.blackout", HM, "fx:smoke"),
    S("Amos climbs onto the slipway", "slipway.blackout", HMA),
    R("At dawn, the coastguard boat noses", "// ACT resolution"),
    S("At dawn, the coastguard boat noses", "harbour.dusk", HMA),
    S("Before anyone climbs the steps", "desk.dusk", HO),
    S("Amos reads it twice.", "desk.dusk", HMA),
    S("So think back.", "lamp.dusk", HO),
    R("Three logbooks. One forgery.", "// LASTLINE"),
    S("Three logbooks. One forgery.", "desk.dusk", HMA),
    X("Subscribe, and keep your lantern lit.", "dock.dusk | hero:stand/determined | fr:wide,low | fx:smoke | cam:pull 1.18>1.02 | cta:subscribe"),
]

KW = [
    (r"tired voice|crackles|\bradio\b", "radio", "sfx:radio_static"),
    (r"\bbell\b|clapper", "reef", ""),
    (r"seal cave|\btorch\b", "cave", "fx:flicker"),
    (r"\bferry|\bhorn\b|pale shape|\bwake\b", "ferry", ""),
    (r"\bgauge\b|\bwick\b|\bburner\b|\bflame\b|\btank\b|\bmatch\b|\boil\b", "burner", ""),
    (r"\bpane\b|whistle|cracked", "lamp", "sfx:wind"),
    (r"logbook|\bdiary\b|\bink\b|green log|green one|red one|black one|black book", "desk", ""),
    (r"\boars\b|\bslipway\b", "slipway", ""),
]
CHF = ["wide,low", "closeup,back", "medium,ots", "closeup,profile", "xwide,wide", "medium,closeup", "low,wide", "ots,wide", "closeup,ots", "wide,medium", "profile,medium", "back,wide", "closeup,low", "medium,wide"]
INSF = ["insert,closeup", "insert,low", "insert,wide", "insert,closeup,low"]
G1 = ["stand", "look_up", "shrug", "point", "reach"]
CALM = ["neutral", "worried", "determined", "relieved", "sad"]
TENSE = ["scared", "shocked", "worried", "determined"]
CAMS = ["push 1.00>1.14", "pan_l", "pull 1.18>1.02", "tilt_up", "pan_r", "push 1.05>1.20", "parallax_drift", "tilt_down", "pull 1.22>1.06", "rack_focus"]
LAST, CI, ST = {}, [0], {"ci": 0, "ii": 0, "run": 0, "k": 0}


def rotate(tags):
    """Never the same pose+expression twice in a row for one character, and a camera move on every shot (P-018/P-020)."""
    out = []
    for seg in tags.split(" | "):
        m = re.fullmatch(r"(hero|maisie|amos)\:(\w+)/(\w+)", seg.strip())
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


def cut(u, mx=14):
    ws = u.split(" ")
    if len(ws) <= mx:
        return [u]
    mid, best, bd = len(ws) / 2, None, 99
    for k in range(4, len(ws) - 3):
        if ws[k - 1][-1] in ",;:" or ws[k] in ("and", "but", "then", "because", "while", "until", "where", "so"):
            if abs(k - mid) < bd:
                best, bd = k, abs(k - mid)
    best = best or len(ws) // 2
    return cut(" ".join(ws[:best]), mx) + cut(" ".join(ws[best:]), mx)


def units(seg):
    ps = [p for p in re.split(r'(?<=[.!?])(?<!\s[A-Z]\.)\s+|(?<=[.!?]")\s+', seg) if p]
    out, buf, bn = [], "", 0
    for p in ps:
        if W(p) < 4 and not buf and out and out[-1][1] < 3 and W(out[-1][0]) + W(p) <= 14:
            out[-1][0] += " " + p
            out[-1][1] += 1
            continue
        buf, bn = f"{buf} {p}".strip(), bn + 1
        if W(buf) >= 5:
            out.append([buf, bn])
            buf, bn = "", 0
    if buf:
        if out:
            out[-1][0] += " " + buf
        else:
            out.append([buf, bn])
    return [x for u, _ in out for x in cut(u)]


def scene(d):
    chs = {}
    for tok in d[3].split():
        k, rest = tok.split(":", 1)
        p, e = rest.split("/")
        chs[k] = (p.split("|"), e.split("|"))
    return (d[2], chs, d[4])


def auto(u, ctx):
    loc, chs, ex = ctx
    low, var = u.lower(), loc.split(".")[1]
    for rx, place, fx in KW:
        if re.search(rx, low) and ST["run"] < 2:
            ST["run"] += 1
            fr = INSF[ST["ii"] % len(INSF)]
            ST["ii"] += 1
            return shot(f"{place}.{var}", "", fr, fx)
    ST["run"] = 0
    fr = CHF[ST["ci"] % len(CHF)]
    ST["ci"] += 1
    keys = list(chs)
    if fr.split(",")[0] in ("wide", "xwide", "medium", "ots", "low") or len(keys) < 2:
        pick = keys
    elif "m" in chs and re.search(r"maisie|\bshe\b|\bher\b|girl", low):
        pick = ["m"]
    elif "a" in chs and re.search(r"amos|\bhe\b|\bhis\b", low):
        pick = ["a"]
    else:
        pick = keys[:1]
    parts = []
    for c in pick:
        ps, es = chs[c]
        parts.append(f"{c}:{ps[ST['k'] % len(ps)]}/{es[(ST['k'] + (c != 'h')) % len(es)]}")
    ST["k"] += 1
    return shot(loc, " ".join(parts), fr, ex)


HEAD = """TITLE: Three Logbooks and One Forgery
LENGTH_MIN: 9
VOICE: default
CHARACTERS:
- hero = rig_hero(outfit=navy, hat=cap, hair=short, skin=tan)
- maisie = rig_hero(outfit=mustard, hair=curly, skin=light)
- amos = rig_hero(outfit=olive, age=old, hat=cap, hair=short, skin=brown)
LOCATIONS:
- dock: small stone landing stage on a rocky island at dusk, wet stone steps, an iron mooring ring, thick grey fog rolling in, a white lighthouse tower fading into the fog, calm dark water
- door: heavy blue wooden door at the base of a white lighthouse tower, brass lamp bracket, wet stone step, evening fog, warm lantern glow spilling out
- stairs: inside a lighthouse tower, curling iron staircase with a handrail winding upward, round whitewashed wall, small round windows, warm lantern light
- lamp: lighthouse lantern room at the top of a tower, large glass lens in the middle, curved glass windows showing dark fog, a brass oil burner, one cracked pane, iron floor
- burner: close view of an old brass oil burner with a round glass chimney and a glowing wick flame, a fuel tank with a round gauge dial and needle, warm light
- gallery: narrow iron balcony railing outside a lighthouse lantern room at night, dark sea and fog far below, a hand signal lamp with green glass on a stand, windy
- desk: old wooden keeper's desk with a brass lamp, three logbooks (one green, one red, one black leather), a pencil jar and a tea mug, warm light
- radio: small marine radio on a wooden shelf with dials and a coiled cable, a tin mug beside it, a window with fog behind, dim warm light
- reef: dark sea at night with jagged black rocks and a leaning iron post carrying a small ship's bell, pale fog and white foam
- cave: sea cave on the east cliffs at night, wet rocks, rising water at the entrance, a small torch glow flashing in the dark, seals on a ledge
- slipway: stone slipway at the foot of a lighthouse at night, two wooden posts, lanterns glowing one high and one low, black water and fog, a small wooden rowing boat
- ferry: huge pale night ferry with rows of tiny lit windows swinging away in thick fog beside black rocks, white wake foam, a green light on its side
- harbour: calm harbour at dawn with a coastguard boat, pink and gold sky, still water, a white lighthouse tower in the distance, soft mist
MUSIC_MOODS:
- CH1: calm
- CH2: mystery
- CH3: mystery
- CH4: tense
- CH5: tense

"""
pos, D2 = 0, []
for d in P:
    i = TXT.find(d[1], pos)
    assert i >= 0, d[1]
    D2.append((i, d))
    pos = i + 1 if d[0] == "X" else i
by = {}
for i, d in D2:
    by.setdefault(i, []).append(d)
bs = sorted(set(by) | {0, len(TXT)})
out, ctx, n, cw, acts = [HEAD.rstrip("\n"), ""], None, 0, 0, []
for a, b in zip(bs, bs[1:]):
    pin = None
    for d in by.get(a, []):
        if d[0] == "R":
            out.append(d[2])
            if d[2].startswith("// ACT"):
                acts.append((d[2][7:], round(cw / NW, 3)))
        elif d[0] == "S":
            ctx = scene(d)
        else:
            pin = d
    seg = TXT[a:b].strip()
    for k, u in enumerate(units(seg) if seg else []):
        tags = (pin[2] if k == 0 else (pin[3] or auto(u, ctx))) if pin else auto(u, ctx)
        out += ["@ " + rotate(tags), u]
        n += 1
        cw += W(u)
text = "\n".join(out) + "\n"
open(os.path.join(D, "script.md"), "w", encoding="utf-8", newline="\n").write(text)
body = " ".join(l for l in text.splitlines() if l and not l.startswith(("@", "//", "##", "-", "TITLE", "LENGTH", "VOICE", "CHARACTERS", "LOCATIONS", "MUSIC")))
assert re.sub(r"\s+", " ", body).strip() == TXT, "narration changed"
print("shots", n, "words", NW, "min", round(NW / 170, 2), "acts", acts)

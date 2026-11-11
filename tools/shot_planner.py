"""Shot planner (P-018/P-020): owner narration sliced word for word + scene map -> script.md.
A per-video make_script.py holds only data (C, P, KW, SP, HEAD) and calls build()."""
import os
import re

C = {}
G1 = ["stand", "look_up", "shrug", "point", "reach"]
CALM = ["neutral", "worried", "determined", "relieved", "sad"]
TENSE = ["scared", "shocked", "worried", "determined"]
CAMS = ["push 1.00>1.14", "pan_l", "pull 1.18>1.02", "tilt_up", "pan_r", "push 1.05>1.20", "parallax_drift", "tilt_down", "pull 1.22>1.06", "rack_focus"]
CHF = ["wide,low", "closeup,back", "medium,ots", "closeup,profile", "xwide,wide", "medium,closeup", "low,wide", "ots,wide", "closeup,ots", "wide,medium", "profile,medium", "back,wide", "closeup,low", "medium,wide"]
INSF = ["insert,closeup", "insert,low", "insert,wide", "insert,closeup,low"]
LAST, CI, ST = {}, [0], {"ci": 0, "ii": 0, "run": 0, "k": 0}


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
    def card(n):
        return 'ov:option_cards("%s","%s","%s","%d","%s")' % (labels[0], labels[1], labels[2], n, icons)
    out = []
    for k, a in enumerate(anchors):
        n = k + 1 if k < 3 else 0
        fl = " | fx:flicker" if k == 3 else ""
        out.append(X(a, shot(loc, ch, ["ots", "wide", "medium", "wide"][k], card(n) + fl),
                     shot(loc, ch, ["closeup", "medium", "closeup", "closeup"][k], card(n) + fl)))
    out.append(X(hold, shot(loc, ch, "ots", card(0))))
    return out


def rotate(tags):
    """Never the same pose+expression twice in a row for one character, and a camera move on every shot."""
    rx = re.compile(r"(%s)\:(\w+)/(\w+)" % "|".join(C.values()))
    out = []
    for seg in tags.split(" | "):
        m = rx.fullmatch(seg.strip())
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


def cut(u, mx):
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


def units(seg, mx):
    ps = [p for p in re.split(r'(?<=[.!?])(?<!\s[A-Z]\.)\s+|(?<=[.!?]")\s+', seg) if p]
    out, buf, bn = [], "", 0
    for p in ps:
        if W(p) < 4 and not buf and out and out[-1][1] < 3 and W(out[-1][0]) + W(p) <= mx:
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
    return [x for u, _ in out for x in cut(u, mx)]


def scene(d):
    chs = {}
    for tok in d[3].split():
        k, rest = tok.split(":", 1)
        p, e = rest.split("/")
        chs[k] = (p.split("|"), e.split("|"))
    return (d[2], chs, d[4])


def auto(u, ctx, KW, SP):
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
    pick = keys[:1]
    if fr.split(",")[0] in ("wide", "xwide", "medium", "ots", "low") or len(keys) < 2:
        pick = keys
    else:
        for k, rx in SP:
            if k in chs and re.search(rx, low):
                pick = [k]
                break
    parts = []
    for c in pick:
        ps, es = chs[c]
        parts.append(f"{c}:{ps[ST['k'] % len(ps)]}/{es[(ST['k'] + (c != 'h')) % len(es)]}")
    ST["k"] += 1
    return shot(loc, " ".join(parts), fr, ex)


def build(D, HEAD, P, KW, SP=(), mx=14):
    TXT = re.sub(r"\s+", " ", open(os.path.join(D, "narration.txt"), encoding="utf-8").read()).strip()
    NW = len(TXT.split())
    HEAD = HEAD.replace("LENGTH_MIN: auto", f"LENGTH_MIN: {round(NW / 170)}")
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
        for k, u in enumerate(units(seg, mx) if seg else []):
            tags = (pin[2] if k == 0 else (pin[3] or auto(u, ctx, KW, SP))) if pin else auto(u, ctx, KW, SP)
            out += ["@ " + rotate(tags), u]
            n += 1
            cw += W(u)
    text = "\n".join(out) + "\n"
    open(os.path.join(D, "script.md"), "w", encoding="utf-8", newline="\n").write(text)
    body = " ".join(l for l in text.splitlines() if l and not l.startswith(("@", "//", "##", "-", "TITLE", "LENGTH", "VOICE", "CHARACTERS", "LOCATIONS", "MUSIC")))
    assert re.sub(r"\s+", " ", body).strip() == TXT, "narration changed"
    print("shots", n, "words", NW, "min", round(NW / 170, 2), "per_min", round(n / (NW / 170), 1), "acts", acts)

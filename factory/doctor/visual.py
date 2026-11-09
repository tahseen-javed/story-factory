"""Video Doctor V1: face boxes and graphics boxes from scene data (Stage 0 lint, also re-run on the final timeline), plus the auto-fix.

Geometry mirrors video/src/scenes/Story.tsx (placeChar) and video/src/characters/Rig.tsx (head position, headScale). Captions are OFF (P-013): no caption checks.
Stdlib only.
"""
from __future__ import annotations

import copy

W, H = 1920, 1080
FRAMING_MULT = {"medium": 1, "closeup": 2.3, "insert": 1.8, "wide": 0.82, "xwide": 0.55, "low": 1.45, "back": 1.15, "ots": 1.2, "silhouette": 1.1, "profile": 1.1}
ROOT_Y = {"sit": 88, "sit_bed": 88, "hide": 104, "fight": 14, "crouch": 92}
OVERLAY_BOX = {  # (w, h) centred at (960, 540); approximations of video/src/overlays (generous, see QA_RULES)
    "timer": (640, 300), "phone_alert": (560, 820), "phone_web": (560, 820), "phone_video": (560, 820), "phone_call": (560, 820), "phone_search": (560, 820),
    "sticky_note": (560, 560), "receipt": (600, 760), "paper_diagram": (1100, 620), "numbered_circle": (620, 640), "notepad_tracker": (900, 720),
    "meter": (760, 600), "option_cards": (1100, 520), "elevator_panel": (1000, 560), "loose_cable": (900, 620), "arrow_callout": (900, 320), "glitch_text": (1100, 300), "hand_pen": (900, 300), "calendar_countdown": (720, 620),
    "tv_news": (1100, 700), "dashed_path": (1200, 600), "paper_bar_chart": (1000, 660), "label_tag": (900, 260), "end_screen": (1500, 800),
}
SAFE_MARGIN = 0.05


def face_box(ch: dict, shot: dict, n: int, z: float = 1.0, fx: float = 0.5, fy: float = 0.55) -> tuple:
    """Screen-space face box (l, t, r, b) in px for one character of a timeline shot."""
    f = shot.get("framing") or "medium"
    base = 1.0 if n >= 3 else (1.12 if n == 2 else 1.28)
    mult = FRAMING_MULT.get(f, 1.0)
    if n >= 2 and f == "closeup":
        mult = 1.45
    if f == "ots":
        mult = 1.9 if shot["chars"].index(ch) == 0 else 1.2
    sc = base * mult * float(ch.get("params", {}).get("bodyScale", 1) or 1)
    root = ROOT_Y.get(ch.get("pose"), 0)
    y = shot.get("floorY", 0.9) * H
    if f == "closeup":
        y = 0.46 * H + (380 - root) * sc
    elif f == "insert":
        y = 0.52 * H + (200 - root) * sc
    elif f == "low":
        y = 1.02 * H
    elif f == "xwide":
        y = 0.84 * H
    elif f == "wide":
        y = 0.88 * H
    elif f == "ots" and shot["chars"].index(ch) == 0:
        y = 1.04 * H
    hs = float(ch.get("params", {}).get("headScale", 1) or 1)
    yh = -380 + root - (hs - 1) * 22
    cx, cy = ch["x"] * W, y + yh * sc
    hw, top, bot = 64 * hs * sc, 70 * hs * sc, 56 * hs * sc
    box = [cx - hw, cy - top, cx + hw, cy + bot]
    ox, oy = fx * W, fy * H
    return (ox + z * (box[0] - ox), oy + z * (box[1] - oy), ox + z * (box[2] - ox), oy + z * (box[3] - oy))


def inter_ratio(face: tuple, g: tuple) -> float:
    iw = max(0.0, min(face[2], g[2]) - max(face[0], g[0]))
    ih = max(0.0, min(face[3], g[3]) - max(face[1], g[1]))
    fa = max(1e-6, (face[2] - face[0]) * (face[3] - face[1]))
    return iw * ih / fa


def graphics(shot: dict) -> list:
    """[(name, box, f0, f1)] for every graphic of the shot; frames relative to the shot start."""
    g, dur = [], shot["dur"]
    ov = shot.get("overlay")
    if ov and ov["name"] != "end_screen":
        w, h = OVERLAY_BOX.get(ov["name"], (700, 500))
        if ov["name"] == "label_tag":
            w = min(1100, len(str(ov["args"][0])) * 52 + 150)
        dx, dy = (shot.get("ovShift") or [0, 0])
        s = float(shot.get("ovScale") or 1.0)
        g.append((f"overlay:{ov['name']}", (960 + dx - w * s / 2, 540 + dy - h * s / 2, 960 + dx + w * s / 2, 540 + dy + h * s / 2), max(0, ov["inFrame"]), min(dur, ov["outFrame"])))
    tr = shot.get("track") or {}
    nh = sum(1 for k in ("hours", "phone", "air", "lamp", "tide") if k in tr)
    if nh:
        left = not shot.get("hudRight")
        wd = 70 + nh * 215
        g.append(("hud", (77, 54, 77 + wd, 150) if left else (W - 77 - wd, 54, W - 77, 150), 0, dur))
    if shot.get("banner"):
        by = float(shot.get("bannerDy") or 0)
        g.append(("banner", (0, 130 + by, W, 330 + by), 0, min(dur, 96)))
    if shot.get("timeCard"):
        g.append(("timecard", (0, 40, 780, 190), 0, min(dur, shot["timeCard"]["frames"])))
    if shot.get("cta"):
        g.append(("cta-sticker", (80, 830, 800, 975), 6, min(dur, 96)))   # bottom-left pill: left 90, bottom 110, about 710 x 130 px
    return g


def lint_shot(shot: dict, th: dict) -> list:
    v = th["visual"]
    out = []
    chars = shot.get("chars") or []
    cam = shot.get("camera") or {}
    zs = sorted({float(cam.get("z0", 1.0)), float(cam.get("z1", 1.0))})
    boxes = []
    for ch in chars:
        for z in zs:
            boxes.append((ch, z, face_box(ch, shot, len(chars), z, cam.get("fx", 0.5), cam.get("fy", 0.55))))
    for ch, z, fb in boxes:
        area = (fb[2] - fb[0]) * (fb[3] - fb[1])
        vis = max(0.0, min(fb[2], W) - max(fb[0], 0.0)) * max(0.0, min(fb[3], H) - max(fb[1], 0.0))
        cut = 1.0 - vis / max(area, 1e-6)
        fg_ots = shot.get("framing") == "ots" and shot["chars"].index(ch) == 0   # over-the-shoulder foreground is cropped by design
        if cut > v["edge_cut_max_ratio"] and not fg_ots:
            out.append({"code": "V1-FACE-EDGE", "severity": th["severity"]["face_edge"], "shot": shot["i"], "char": ch["id"], "ratio": round(cut, 3), "face_box": [round(x) for x in fb],
                        "t0": shot["start"] / 30.0, "t1": (shot["start"] + shot["dur"]) / 30.0, "msg": "face cut by the frame edge"})
        for name, gb, f0, f1 in graphics(shot):
            r = inter_ratio(fb, gb)
            if r > v["face_overlap_max_ratio"] and (f1 - f0) > v["face_overlap_min_frames"]:
                out.append({"code": "V1-FACE-OVERLAP", "severity": th["severity"]["face_overlap"], "shot": shot["i"], "char": ch["id"], "graphic": name, "ratio": round(r, 3),
                            "face_box": [round(x) for x in fb], "graphic_box": [round(x) for x in gb], "t0": (shot["start"] + f0) / 30.0, "t1": (shot["start"] + f1) / 30.0,
                            "msg": f"{name} covers {r*100:.0f}% of {ch['id']}'s face"})
    for i, (a, _, fa) in enumerate(boxes):
        for b, _, fbx in boxes[i + 1:]:
            if a is not b and a["id"] != b["id"]:
                r = inter_ratio(fa, fbx)
                if r > v["face_overlap_max_ratio"]:
                    out.append({"code": "V1-FACE-OVERLAP", "severity": th["severity"]["face_overlap"], "shot": shot["i"], "char": a["id"], "graphic": f"character:{b['id']}", "ratio": round(r, 3),
                                "face_box": [round(x) for x in fa], "graphic_box": [round(x) for x in fbx], "t0": shot["start"] / 30.0, "t1": (shot["start"] + shot["dur"]) / 30.0,
                                "msg": f"{b['id']} covers {r*100:.0f}% of {a['id']}'s face"})
    seen, uniq = set(), []
    for f in out:
        k = (f["code"], f["shot"], f.get("char"), f.get("graphic"))
        if k not in seen:
            seen.add(k)
            uniq.append(f)
    return uniq


def lint_timeline(timeline: dict, th: dict) -> list:
    out = []
    for sh in timeline["shots"]:
        out += lint_shot(sh, th)
    return out


def _clean(sh: dict, th: dict) -> bool:
    return not [x for x in lint_shot(sh, th) if x["code"].startswith("V1")]


def _search_overlay(sh: dict, th: dict) -> bool:
    best = None
    for dx in (0, -380, 380, -600, 600, -220, 220):
        for dy in (0, -140, 140, -240, 240):
            for sc in (1.0, 0.85, 0.7):
                sh["ovShift"], sh["ovScale"] = [dx, dy], sc
                gb = [g for g in graphics(sh) if g[0].startswith("overlay:")][0][1]
                inside = gb[0] >= W * SAFE_MARGIN and gb[2] <= W * (1 - SAFE_MARGIN) and gb[1] >= H * SAFE_MARGIN and gb[3] <= H * (1 - SAFE_MARGIN)
                cost = abs(dx) / 100 + abs(dy) / 100 + (1 - sc) * 10
                if inside and _clean(sh, th) and (best is None or cost < best[0]):
                    best = (cost, [dx, dy], sc)
    if best:
        sh["ovShift"], sh["ovScale"] = best[1], best[2]
        return True
    sh["ovShift"], sh["ovScale"] = None, None
    return False


def reframe(sh: dict, th: dict) -> bool:
    """Last-resort auto-fix for a shot that still has a face problem: calmer framing, lower zoom, characters to the sides, HUD corner and overlay position searched again."""
    n = len(sh["chars"])
    xs = {1: [0.16], 2: [0.15, 0.85], 3: [0.12, 0.5, 0.88]}.get(n, [])
    keep = copy.deepcopy(sh)
    for frm, zmax in (("medium", 1.05), ("wide", 1.05), ("xwide", 1.0)):
        for hud in (bool(keep.get("hudRight")), not keep.get("hudRight")):
            sh["framing"], sh["hudRight"] = frm, hud
            cam = sh.setdefault("camera", {})
            cam["z0"], cam["z1"] = min(cam.get("z0", 1.0), zmax), min(cam.get("z1", 1.0), zmax)
            for c, x in zip(sh["chars"], xs):
                c["x"] = x
            sh["ovShift"], sh["ovScale"] = None, None
            if _clean(sh, th) or (sh.get("overlay") and _search_overlay(sh, th)):
                return True
    sh.clear()
    sh.update(keep)
    return False


def fix_timeline(timeline: dict, th: dict, max_rounds: int = 3) -> tuple:
    """Auto-fix V1 findings on the scene data. Order: move the graphic to a safe zone, shrink it, shift the characters. Returns (timeline, findings_left, log)."""
    tl = copy.deepcopy(timeline)
    log = []
    for _ in range(max_rounds):
        found = [f for f in lint_timeline(tl, th) if f["code"].startswith("V1")]
        if not found:
            break
        for f in found:
            sh = tl["shots"][f["shot"]] if tl["shots"][f["shot"]]["i"] == f["shot"] else next(s for s in tl["shots"] if s["i"] == f["shot"])
            before = f["ratio"]
            if f["code"] == "V1-FACE-OVERLAP" and f["graphic"] == "banner":
                for dy in (0, 630, 420, -60):
                    sh["bannerDy"] = dy
                    if not [x for x in lint_shot(sh, th) if x.get("graphic") == "banner"]:
                        break
                log.append(f"shot {f['shot']}: banner moved down {sh['bannerDy']} px (overlap {before} -> 0)")
            elif f["code"] == "V1-FACE-OVERLAP" and f["graphic"] == "hud":
                sh["hudRight"] = not sh.get("hudRight")
                log.append(f"shot {f['shot']}: HUD moved to the other corner (overlap {before})")
            elif f["code"] == "V1-FACE-OVERLAP" and f["graphic"].startswith("overlay:"):
                best = None
                for dx in (0, -380, 380, -600, 600, -220, 220):
                    for dy in (0, -140, 140, -240, 240):
                        for sc in (1.0, 0.85, 0.7):
                            sh["ovShift"], sh["ovScale"] = [dx, dy], sc
                            gl = [x for x in lint_shot(sh, th) if x["code"] == "V1-FACE-OVERLAP" and x["graphic"] == f["graphic"]]
                            gb = [g for g in graphics(sh) if g[0] == f["graphic"]][0][1]
                            inside = gb[0] >= W * SAFE_MARGIN and gb[2] <= W * (1 - SAFE_MARGIN) and gb[1] >= H * SAFE_MARGIN and gb[3] <= H * (1 - SAFE_MARGIN)
                            cost = abs(dx) / 100 + abs(dy) / 100 + (1 - sc) * 10
                            if not gl and inside and (best is None or cost < best[0]):
                                best = (cost, [dx, dy], sc)
                if best:
                    sh["ovShift"], sh["ovScale"] = best[1], best[2]
                    log.append(f"shot {f['shot']}: {f['graphic']} moved {best[1]} and scaled {best[2]} (face overlap {before} -> 0)")
                else:
                    sh["ovShift"], sh["ovScale"] = None, None
            elif f["code"] == "V1-FACE-OVERLAP" and f["graphic"].startswith("character:"):
                for c in sh["chars"]:
                    c["x"] = 0.25 if c["x"] < 0.5 else 0.75
                log.append(f"shot {f['shot']}: characters spread apart (head overlap {before})")
            elif f["code"] == "V1-FACE-EDGE":
                for c in sh["chars"]:
                    if c["id"] == f["char"]:
                        c["x"] = min(0.8, max(0.2, c["x"]))
                log.append(f"shot {f['shot']}: {f['char']} moved inside the frame")
    for i in sorted({f["shot"] for f in lint_timeline(tl, th) if f["code"].startswith("V1")}):
        sh = next(s for s in tl["shots"] if s["i"] == i)
        was = sh.get("framing")
        if reframe(sh, th):
            log.append(f"shot {i}: reframed {was} -> {sh['framing']} (characters to the sides, zoom <= 1.05) so no graphic covers a face")
    left = [f for f in lint_timeline(tl, th) if f["code"].startswith("V1")]
    return tl, left, log

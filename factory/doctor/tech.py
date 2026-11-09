"""Video Doctor Phase 2, stage 4: technical checks on decoded frames of the final mp4 (or of one rendered chunk), numpy + ffmpeg only.

V4-BLACK     black frame(s) inside the video (auto-fix: the last good frame is held over the black run)
V4-FREEZE    frozen picture (identical frames for 1.2 s or more) outside a planned decision hold
V4-DUP       run of identical frames at 30 fps (6+ frames) outside a planned hold
V4-FLICKER   brightness oscillation (more than 4 jumps per second)
V4-RESOLUTION / V4-FPS   output format
V4-CUT       unplanned hard cut (a big picture change away from every planned shot edge) or cuts closer than 0.5 s
V6-STATIC    the same pose and expression of one character for more than 3 s outside a planned hold
V6-PACING    shots per minute / longest shot outside the limits
"""
from __future__ import annotations

import json
import os
import subprocess

import numpy as np

W, H = 160, 90


def decode_gray(mp4: str, fps: int = 30, w: int = W, h: int = H, max_s: float | None = None) -> np.ndarray:
    cmd = ["ffmpeg", "-v", "error", "-i", mp4, "-vf", f"fps={fps},scale={w}:{h}", "-pix_fmt", "gray", "-f", "rawvideo"]
    if max_s:
        cmd[3:3] = ["-t", str(max_s)]
    cmd.append("-")
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    n = len(raw) // (w * h)
    return np.frombuffer(raw[: n * w * h], dtype=np.uint8).reshape(n, h, w)


def runs(mask: np.ndarray, min_len: int):
    out, start = [], None
    for i, v in enumerate(list(mask) + [False]):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start >= min_len:
                out.append((start, i))
            start = None
    return out


def finding(th, code, key, t0, t1, value, thr, msg, **extra):
    d = {"code": code, "severity": th["severity"].get(key, "MAJOR"), "t0": round(float(t0), 2), "t1": round(float(t1), 2),
         "value": None if value is None else round(float(value), 3), "threshold": thr, "msg": msg}
    d.update(extra)
    return d


def hold_windows(timeline: dict | None, fps: float = 30.0) -> list:
    if not timeline:
        return []
    return [(s["start"] / fps - 0.1, (s["start"] + s["dur"]) / fps + 0.1) for s in timeline.get("shots", []) if s.get("hold")]


def check_frames(g: np.ndarray, th: dict, timeline: dict | None = None, fps: float = 30.0, t_offset: float = 0.0) -> tuple:
    """g: (n,h,w) uint8 at `fps`. Returns (findings, metrics)."""
    t = th["tech"]
    f, m = [], {}
    n = len(g)
    if n < 3:
        return f, {"frames": n}
    holds = hold_windows(timeline, fps)
    in_hold = lambda a, b: any(h0 <= a + t_offset and b + t_offset <= h1 for h0, h1 in holds)   # noqa: E731
    luma = g.reshape(n, -1).mean(axis=1)
    d = np.abs(np.diff(g.astype(np.int16), axis=0)).reshape(n - 1, -1)
    dmean, dmax = d.mean(axis=1), d.max(axis=1)
    m["frames"] = n
    # black
    black = (luma < t["black_luma"]) & (g.reshape(n, -1).std(axis=1) < t["black_std"])
    for a, b in runs(black, 2):
        if a == 0 or b >= n:   # fade-in / fade-out ends are deliberate
            continue
        f.append(finding(th, "V4-BLACK", "black", a / fps + t_offset, b / fps + t_offset, (b - a) / fps, 0.05, "black frames inside the video", frames=[a, b]))
    # frozen / duplicate (identical consecutive frames)
    same = (dmax <= t["dup_diff"]) & (dmean <= t["dup_mean"])
    for a, b in runs(same, int(t["dup_run_frames"])):
        t0, t1 = a / fps + t_offset, (b + 1) / fps + t_offset
        if in_hold(a / fps, (b + 1) / fps) or b + 1 >= n - 2:
            continue
        code = "V4-FREEZE" if (b - a) / fps >= t["freeze_s"] else "V4-DUP"
        f.append(finding(th, code, "freeze" if code == "V4-FREEZE" else "dup", t0, t1, (b - a) / fps, t["freeze_s"] if code == "V4-FREEZE" else t["dup_run_frames"] / fps, "identical frames in a row"))
    # flicker: big luma jumps that are not hard cuts, more than N per second
    jump = np.abs(np.diff(luma))
    cutmask = dmean > t["cut_diff"]
    fl = (jump > t["flicker_luma_jump"]) & ~cutmask
    win = int(fps)
    for i in range(0, max(1, n - win), win // 2):
        k = int(fl[i:i + win].sum())
        if k > t["flicker_max_per_s"]:
            f.append(finding(th, "V4-FLICKER", "flicker", i / fps + t_offset, (i + win) / fps + t_offset, k, t["flicker_max_per_s"], "brightness flicker"))
            break
    # cuts
    cuts = [i + 1 for i in np.where(cutmask)[0]]
    m["cuts"] = len(cuts)
    for a, b in zip(cuts, cuts[1:]):
        if (b - a) / fps < t["cut_min_gap_s"] and not in_hold(a / fps, b / fps):
            f.append(finding(th, "V4-CUT", "cut", a / fps + t_offset, b / fps + t_offset, (b - a) / fps, t["cut_min_gap_s"], "cuts closer than the minimum gap"))
    if timeline:
        starts = [s["start"] / fps for s in timeline["shots"]]
        for c in cuts:
            tc = c / fps + t_offset
            if starts and min(abs(tc - s) for s in starts) > t["unplanned_cut_s"] and dmean[c - 1] > t["unplanned_cut_diff"]:
                f.append(finding(th, "V4-CUT", "cut", tc, tc, float(dmean[c - 1]), t["unplanned_cut_diff"], "hard cut that is not on a planned shot edge"))
    return f, m


def check_timeline(timeline: dict, th: dict, fps: float = 30.0) -> tuple:
    """Pacing and static-pose checks from the scene data."""
    t = th["tech"]
    f, m = [], {}
    shots = timeline["shots"]
    total = (timeline.get("durationInFrames") or max([x["start"] + x["dur"] for x in shots] or [1])) / fps
    durs = [s["dur"] / fps for s in shots if not s.get("hold")]
    m["shots_per_min"] = round(len(shots) / (total / 60.0), 1)
    m["max_shot_s"] = round(max(durs or [0]), 2)
    if durs and max(durs) > t["max_shot_s"]:
        f.append(finding(th, "V6-PACING", "pacing_rate", 0, total, max(durs), t["max_shot_s"], "a shot is longer than the limit"))
    if m["shots_per_min"] < t["shots_per_min_min"]:
        f.append(finding(th, "V6-PACING", "pacing_rate", 0, total, m["shots_per_min"], t["shots_per_min_min"], "too few shots per minute"))
    last = {}
    for s in shots:
        for c in s["chars"]:
            key = (c["id"], c.get("pose"), c.get("expr"))
            cur = last.get(c["id"])
            if cur and cur["key"] == key:
                cur["dur"] += s["dur"] / fps
                cur["end"] = (s["start"] + s["dur"]) / fps
                if not s.get("hold"):
                    cur["nohold"] += s["dur"] / fps
            else:
                if cur and cur["nohold"] > t["static_pose_s"]:
                    f.append(finding(th, "V6-STATIC", "static", cur["start"], cur["end"], cur["nohold"], t["static_pose_s"], f"{c['id']} keeps the same pose and expression", char=cur["key"][0]))
                last[c["id"]] = {"key": key, "start": s["start"] / fps, "end": (s["start"] + s["dur"]) / fps, "dur": s["dur"] / fps, "nohold": 0.0 if s.get("hold") else s["dur"] / fps}
    for cid, cur in last.items():
        if cur["nohold"] > t["static_pose_s"]:
            f.append(finding(th, "V6-STATIC", "static", cur["start"], cur["end"], cur["nohold"], t["static_pose_s"], f"{cid} keeps the same pose and expression", char=cid))
    return f, m


def hold_frames(src: str, dst: str, f0: int, f1: int) -> bool:
    """Replace frames [f0, f1) by the frame before them (picture only, audio copied)."""
    n = max(1, f1 - f0)
    fc = (f"[0:v]split=3[a][b][c];[a]trim=end_frame={f0},setpts=PTS-STARTPTS[v0];"
          f"[b]trim=start_frame={max(0, f0 - 1)}:end_frame={max(1, f0)},setpts=PTS-STARTPTS,loop=loop={n - 1}:size=1:start=0,setpts=N/(30*TB)[v1];"
          f"[c]trim=start_frame={f1},setpts=PTS-STARTPTS[v2];[v0][v1][v2]concat=n=3:v=1:a=0,setpts=N/(30*TB)[v]")
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", fc, "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
                        "-c:a", "copy", "-movflags", "+faststart", dst], capture_output=True, text=True)
    return r.returncode == 0 and os.path.exists(dst)


def fix_black(mp4: str, findings: list, out: str, fps: float = 30.0) -> bool:
    """Auto-fix: hold the last good frame over every black run. Returns True if a new file was written."""
    segs = sorted([x for x in findings if x["code"] == "V4-BLACK" and x.get("frames")], key=lambda x: x["frames"][0])
    if not segs:
        return False
    cur, tmp = mp4, out + ".tmp.mp4"
    for k, x in enumerate(segs):
        dst = out if k == len(segs) - 1 else tmp
        if not hold_frames(cur, dst, x["frames"][0], x["frames"][1]):
            return False
        cur = dst
        if dst == tmp and k < len(segs) - 1:
            os.replace(tmp, tmp + ".keep")
            cur = tmp + ".keep"
    for leftover in (tmp, tmp + ".keep"):
        if os.path.exists(leftover):
            os.remove(leftover)
    return os.path.exists(out)


def run_file(mp4: str, th: dict, timeline: dict | None, max_s: float | None = None, t_offset: float = 0.0) -> dict:
    g = decode_gray(mp4, 30, max_s=max_s)
    f, m = check_frames(g, th, timeline, 30.0, t_offset)
    if timeline and not max_s:
        f2, m2 = check_timeline(timeline, th)
        f, m = f + f2, {**m, **m2}
    return {"findings": f, "metrics": m}


if __name__ == "__main__":
    import sys

    from .run import load_th

    tl = json.load(open(sys.argv[2], encoding="utf-8"))["timeline"] if len(sys.argv) > 2 else None
    print(json.dumps(run_file(sys.argv[1], load_th(), tl), indent=1)[:3000])

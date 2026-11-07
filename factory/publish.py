"""YouTube private upload (stdlib only): resumable video upload, thumbnail, captions. Quota-aware, idempotent, never fails the video.

Secrets (env): YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN. Without them: skipped with a one-line hint.
Ledger: JSON file {"<nnn>": {"video_id": ..., "at": iso}} kept as a Release asset by the workflow (idempotency + daily quota).
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

TOKEN_URL = "https://oauth2.googleapis.com/token"
UNITS = {"video": 1600, "thumbnail": 50, "caption": 400}


def pacific_day(now=None) -> str:
    now = now or datetime.datetime.now(datetime.timezone.utc)
    return (now - datetime.timedelta(hours=8)).strftime("%Y-%m-%d")  # Pacific standard offset; quota resets at midnight Pacific


def quota_used_today(ledger: dict, day: str) -> int:
    return sum(UNITS["video"] + UNITS["thumbnail"] + (UNITS["caption"] if e.get("captions") else 0) for e in ledger.values() if e.get("day") == day)


def can_upload(ledger: dict, cfg: dict, want_captions: bool, day: str) -> tuple[bool, str]:
    yt = cfg["youtube"]
    n_today = sum(1 for e in ledger.values() if e.get("day") == day)
    need = UNITS["video"] + UNITS["thumbnail"] + (UNITS["caption"] if want_captions else 0)
    if n_today >= int(yt["publish_rate_per_day"]):
        return False, f"publish_rate {yt['publish_rate_per_day']}/day reached; deferred to the next Pacific-time day"
    if quota_used_today(ledger, day) + need > int(yt["quota_daily_units"]):
        return False, "daily API quota would be exceeded; deferred to the next Pacific-time reset"
    return True, "ok"


def access_token() -> str:
    data = urllib.parse.urlencode({
        "client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(TOKEN_URL, data=data), timeout=60) as r:
            return json.load(r)["access_token"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        if "invalid_grant" in body:
            raise PermissionError("invalid_grant")
        raise


def _req(url, token, data=None, headers=None, method=None):
    h = {"Authorization": f"Bearer {token}"}
    h.update(headers or {})
    return urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h, method=method), timeout=300)


def upload_video(token, path, title, description, tags):
    meta = {"snippet": {"title": title[:100], "description": description[:4900], "tags": tags[:15], "categoryId": "1", "defaultLanguage": "en"},
            "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False, "containsSyntheticMedia": False}}
    size = os.path.getsize(path)
    r = _req("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status", token, json.dumps(meta).encode(),
             {"Content-Type": "application/json; charset=UTF-8", "X-Upload-Content-Length": str(size), "X-Upload-Content-Type": "video/mp4"}, "POST")
    loc = r.headers["Location"]
    chunk = 16 * 1024 * 1024
    with open(path, "rb") as fh:
        pos = 0
        while pos < size:
            buf = fh.read(chunk)
            end = pos + len(buf) - 1
            try:
                resp = _req(loc, token, buf, {"Content-Length": str(len(buf)), "Content-Range": f"bytes {pos}-{end}/{size}", "Content-Type": "video/mp4"}, "PUT")
                if resp.status in (200, 201):
                    return json.load(resp)["id"]
            except urllib.error.HTTPError as e:
                if e.code != 308:
                    raise
            pos += len(buf)
    raise RuntimeError("upload did not complete")


def set_thumbnail(token, video_id, path):
    _req(f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={video_id}&uploadType=media", token, open(path, "rb").read(), {"Content-Type": "image/jpeg"}, "POST")


def add_captions(token, video_id, srt_path):
    boundary = "sfboundary"
    meta = json.dumps({"snippet": {"videoId": video_id, "language": "en", "name": "English", "isDraft": False}})
    body = (f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{meta}\r\n--{boundary}\r\nContent-Type: application/octet-stream\r\n\r\n").encode() + \
        open(srt_path, "rb").read() + f"\r\n--{boundary}--".encode()
    _req("https://www.googleapis.com/upload/youtube/v3/captions?uploadType=multipart&part=snippet", token, body, {"Content-Type": f"multipart/related; boundary={boundary}"}, "POST")


def parse_info(path):
    txt = open(path, encoding="utf-8").read()
    def sect(name, nxt):
        a = txt.index(name) + len(name)
        b = txt.index(nxt, a) if nxt in txt[a:] else len(txt)
        return txt[a:b].strip()
    desc = sect("DESCRIPTION", "TAGS")
    tags = [t.strip() for t in sect("TAGS", "PINNED COMMENT").split(",") if t.strip()]
    return desc, tags


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--nnn", type=int, required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--video", required=True)
    ap.add_argument("--thumb", required=True)
    ap.add_argument("--srt", required=True)
    ap.add_argument("--info", required=True)
    ap.add_argument("--ledger", required=True)
    a = ap.parse_args(argv)
    from .validate import load_cfg

    cfg = load_cfg()
    if not all(os.environ.get(k) for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN")):
        print("YOUTUBE: skipped (secrets not set; docs/USER_CHECKLIST.md step 2). Bundle is still delivered.")
        return 0
    ledger = json.load(open(a.ledger)) if os.path.exists(a.ledger) else {}
    if str(a.nnn) in ledger:
        print(f"YOUTUBE: video {a.nnn:03d} already uploaded ({ledger[str(a.nnn)]['video_id']}); not uploading again.")
        return 0
    day = pacific_day()
    want_caps = bool(cfg["youtube"]["upload_captions"])
    ok, why = can_upload(ledger, cfg, want_caps, day)
    if not ok:
        print(f"YOUTUBE: {why}")
        return 0
    try:
        token = access_token()
    except PermissionError:
        print("YOUTUBE: token expired/invalid (invalid_grant) - re-authorise in the browser (docs/SETUP_YOUTUBE.md step 5). Bundle is still delivered.")
        return 0
    desc, tags = parse_info(a.info)
    try:
        vid = upload_video(token, a.video, a.base, desc, tags)
        entry = {"video_id": vid, "day": day, "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "captions": False}
        ledger[str(a.nnn)] = entry
        json.dump(ledger, open(a.ledger, "w"), indent=1)
        set_thumbnail(token, vid, a.thumb)
        if want_caps:
            try:
                add_captions(token, vid, a.srt)
                entry["captions"] = True
            except Exception as e:  # noqa: BLE001
                print(f"YOUTUBE: captions skipped ({e!r}); use the SRT manually or YouTube auto-captions")
        json.dump(ledger, open(a.ledger, "w"), indent=1)
        print(f"YOUTUBE: uploaded private as {vid}")
    except Exception as e:  # noqa: BLE001
        print(f"YOUTUBE: upload failed ({e!r}); bundle is still delivered")
    return 0


if __name__ == "__main__":
    sys.exit(main())

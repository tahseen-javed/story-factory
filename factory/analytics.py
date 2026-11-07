"""Learning loop: YouTube Analytics (free API) -> docs/LEARNINGS.md (max 20 lines). Stdlib only. Skips politely without secrets/scope."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

from .publish import access_token


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if not all(os.environ.get(k) for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN")):
        print("ANALYTICS: skipped (YouTube secrets not set)")
        return 0
    try:
        tok = access_token()
        q = urllib.parse.urlencode({"ids": "channel==MINE", "startDate": "2026-01-01", "endDate": "2100-01-01", "dimensions": "video",
                                    "metrics": "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage", "sort": "-views", "maxResults": "10"})
        req = urllib.request.Request("https://youtubeanalytics.googleapis.com/v2/reports?" + q, headers={"Authorization": f"Bearer {tok}"})
        rows = json.load(urllib.request.urlopen(req, timeout=60)).get("rows", [])
    except (PermissionError, urllib.error.HTTPError) as e:
        print(f"ANALYTICS: skipped ({e!r}); re-authorise with the yt-analytics.readonly scope")
        return 0
    lines = ["# LEARNINGS (max 20 lines; top 10 are read by /new-video)", ""]
    for r in rows[:10]:
        lines.append(f"- video {r[0]}: {r[1]} views, avg view duration {r[3]} s, avg viewed {r[4]:.0f}%")
    lines.append("- Steer hooks/pacing toward the videos with the highest average viewed percentage.")
    open(a.out, "w", encoding="utf-8").write("\n".join(lines[:20]) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

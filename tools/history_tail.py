"""python tools/history_tail.py [N]  -> one line per past video (last N, default 20): number, title, premise, twist, openers, facts."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    p = os.path.join(ROOT, "library", "history.json")
    raw = open(p, "rb").read()
    if raw.startswith(b"\x00GITCRYPT"):
        print("history.json is encrypted: run git-crypt unlock first")
        return 1
    hist = json.loads(raw.decode("utf-8"))
    for h in hist[-n:]:
        print(f"{h['nnn']:03d} | {h['short_title']} | {h['length_min']}m | premise: {h['premise']} | twist: {h['twist']} | open: {','.join(h.get('openers', []))} "
              f"| ritual: {','.join(h.get('rituals', []))} | accent: {h.get('accent')} | locs: {','.join(h.get('locations', []))} | facts: {'; '.join(h.get('facts', []))}")
    if not hist:
        print("(no videos yet)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""python tools/disk_report.py -> local footprint of the project (cap 300 MB, target < 100 MB) and free space on the project drive."""
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def size(path):
    total = 0
    for dp, dn, fn in os.walk(path):
        for f in fn:
            try:
                total += os.path.getsize(os.path.join(dp, f))
            except OSError:
                pass
    return total


def main():
    parts = {}
    for d in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, d)
        parts[d] = size(p) if os.path.isdir(p) else os.path.getsize(p)
    total = sum(parts.values())
    for k, v in sorted(parts.items(), key=lambda kv: -kv[1])[:8]:
        print(f"{v/1e6:8.1f} MB  {k}")
    free = shutil.disk_usage(ROOT).free / 1e9
    print(f"TOTAL {total/1e6:.1f} MB (cap 300, target 100) | free on drive {free:.1f} GB")
    if total > 200e6:
        print("WARNING: over 200 MB - find the local cause (never delete delivered videos)")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

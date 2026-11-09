"""Video Doctor certificate (P-012): delivery requires CERTIFICATE.json whose sha256 matches the exact mp4. Stdlib only.

python -m factory.doctor.cert verify <mp4> <certificate.json>     exit 0 = valid, 1 = refused (reason printed)
python -m factory.doctor.cert write  <mp4> <out_dir> <status> <report.json>
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

from . import VERSION

OK_STATUS = ("PASS", "FIXED")


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write(mp4: str, out_dir: str, status: str, report: dict, video_id: str = "") -> str:
    """Write CERTIFICATE.json for exactly this mp4. status is PASS, FIXED or NEEDS_REVIEW (a NEEDS_REVIEW file can never verify)."""
    os.makedirs(out_dir, exist_ok=True)
    findings = report.get("findings", [])
    cert = {
        "doctor_version": VERSION, "id": video_id or os.path.splitext(os.path.basename(mp4))[0], "file": os.path.basename(mp4),
        "sha256": sha256_file(mp4), "bytes": os.path.getsize(mp4), "status": status, "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "blockers": sum(1 for f in findings if f.get("severity") == "BLOCKER"), "majors": sum(1 for f in findings if f.get("severity") == "MAJOR"),
        "minors": sum(1 for f in findings if f.get("severity") == "MINOR"), "checks": report.get("checks", {}), "metrics": report.get("metrics", {}),
    }
    path = os.path.join(out_dir, "CERTIFICATE.json")
    json.dump(cert, open(path, "w", encoding="utf-8"), indent=1)
    return path


def verify(mp4: str, cert_path: str) -> tuple:
    """(ok, reason). Refuses: no certificate, unreadable certificate, status not PASS/FIXED, any blocker/major, other Doctor version (stale), other hash or size."""
    if not os.path.isfile(mp4):
        return False, "mp4 missing"
    if not cert_path or not os.path.isfile(cert_path):
        return False, "no certificate"
    try:
        c = json.load(open(cert_path, encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return False, f"unreadable certificate ({e.__class__.__name__})"
    if c.get("status") not in OK_STATUS:
        return False, f"certificate status is {c.get('status')}"
    if int(c.get("blockers", 1)) or int(c.get("majors", 1)):
        return False, "certificate lists BLOCKER/MAJOR defects"
    if c.get("doctor_version") != VERSION:
        return False, f"stale certificate (Doctor {c.get('doctor_version')} != {VERSION})"
    if int(c.get("bytes", -1)) != os.path.getsize(mp4):
        return False, "certificate does not match this mp4 (size)"
    if c.get("sha256") != sha256_file(mp4):
        return False, "certificate does not match this mp4 (sha256)"
    return True, "valid"


def main(argv=None):
    a = argv if argv is not None else sys.argv[1:]
    if len(a) >= 3 and a[0] == "verify":
        ok, why = verify(a[1], a[2])
        print(("CERTIFICATE OK" if ok else "REFUSED: ") + ("" if ok else why))
        return 0 if ok else 1
    if len(a) >= 5 and a[0] == "write":
        rep = json.load(open(a[4], encoding="utf-8")) if os.path.exists(a[4]) else {}
        print(write(a[1], a[2], a[3], rep))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())

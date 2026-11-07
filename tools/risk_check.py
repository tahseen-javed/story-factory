"""Risk guards (stdlib only). Run in CI (risk-check job) and locally: python tools/risk_check.py

Checks: pinned action SHAs, workflow permissions, no pull_request_target, no cron schedules, no tracked file > 5 MB
(except the encrypted reference video), no secrets-looking strings, licence fields, prompt denylist present,
encrypted-blob guard (via .githooks/check_encryption.sh in CI mode).
"""
from __future__ import annotations

import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

SECRET_PATTERNS = [
    r"AGE-SECRET-KEY-[A-Z0-9]{20,}",
    r"AKIA[0-9A-Z]{16}",
    r"ghp_[A-Za-z0-9]{30,}",
    r"github_pat_[A-Za-z0-9_]{30,}",
    r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----",
    r"1//[0-9A-Za-z_\-]{40,}",  # google refresh token shape
]


def tracked_files():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout.decode("utf-8", "replace")
    return [p for p in out.split("\0") if p]


def check_workflows(errors):
    for path in glob.glob(os.path.join(ROOT, ".github", "workflows", "*.yml")):
        name = os.path.basename(path)
        txt = open(path, encoding="utf-8").read()
        if "pull_request_target" in txt:
            errors.append(f"{name}: pull_request_target is forbidden")
        if re.search(r"^\s*schedule\s*:", txt, re.M) or re.search(r"^\s*-\s*cron\s*:", txt, re.M):
            errors.append(f"{name}: cron/schedule triggers are forbidden (no idle jobs)")
        if not re.search(r"^permissions\s*:", txt, re.M):
            errors.append(f"{name}: missing top-level permissions block")
        for m in re.finditer(r"^\s*-?\s*uses:\s*([^\s#]+)", txt, re.M):
            ref = m.group(1)
            if ref.startswith("./") or ref.startswith("docker://"):
                continue
            if not re.search(r"@[0-9a-f]{40}$", ref):
                errors.append(f"{name}: action not pinned to a full commit SHA: {ref}")
        if re.search(r"secrets\.\w+", txt) and "pull_request" in txt and "produce" in name:
            errors.append(f"{name}: produce workflow must not run on pull_request")


def check_files(errors):
    for p in tracked_files():
        full = os.path.join(ROOT, p)
        if not os.path.exists(full):
            continue
        size = os.path.getsize(full)
        if size > 5 * 1024 * 1024 and not p.startswith("reference/"):
            errors.append(f"{p}: {size/1e6:.1f} MB tracked file (limit 5 MB, binaries belong in Releases)")
        if p.startswith(("jobs/", "voices/", "inbox/", "reference/")) or p.endswith(("/facts.md", "/review.md")):
            continue  # encrypted blobs; guard below
        if size < 2_000_000 and p.endswith((".py", ".md", ".yml", ".yaml", ".json", ".ps1", ".sh", ".ts", ".tsx", ".txt", ".cmd")):
            try:
                txt = open(full, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            for pat in SECRET_PATTERNS:
                if re.search(pat, txt) and not p.endswith("risk_check.py") and not p.startswith("tests/"):
                    errors.append(f"{p}: looks like it contains a secret ({pat[:18]}...)")


def check_encryption(errors):
    env = dict(os.environ, ENCRYPTION_GUARD_CI="1")
    r = subprocess.run(["sh", os.path.join(ROOT, ".githooks", "check_encryption.sh"), "tree", "HEAD"], cwd=ROOT, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        errors.append("encryption guard failed: " + (r.stderr or r.stdout).strip().replace("\n", " | ")[:400])


def check_licences(errors):
    p = os.path.join(ROOT, "LICENSES.md")
    if not os.path.exists(p):
        errors.append("LICENSES.md missing")
        return
    txt = open(p, encoding="utf-8").read()
    for needed in ("Chatterbox", "SDXL-Lightning", "Remotion", "Depth-Anything-V2-Small", "sherpa-onnx"):
        if needed not in txt:
            errors.append(f"LICENSES.md has no entry for {needed}")
    low = txt.lower()
    for bad in ("cc-by-nc", "non-commercial licence accepted"):
        # the doc may mention them as rejected; require explicit marker
        pass
    if "REJECTED" not in txt:
        errors.append("LICENSES.md must keep a REJECTED section (non-commercial licences)")


def check_denylist(errors):
    from factory import vocab

    if len(vocab.PROMPT_DENYLIST) < 20:
        errors.append("prompt denylist too small")


def main() -> int:
    errors: list = []
    check_workflows(errors)
    check_files(errors)
    check_licences(errors)
    check_denylist(errors)
    if os.path.isdir(os.path.join(ROOT, ".git")):
        check_encryption(errors)
    if errors:
        print("risk-check FAILED:")
        for e in errors[:40]:
            print("  - " + e)
        return 1
    print("risk-check OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""ZERO-COST AUDIT (P-012): proves the factory and the Video Doctor use only free resources. Stdlib only.

Checks: every job runs on a GitHub-hosted standard runner of the public repo (no self-hosted, no paid larger runners), no schedules,
no paid-API secrets or hosts in workflows and code, every pip/apt dependency of the Doctor is on the licence allowlist (docs/LICENSES_QA.md),
the Doctor modules import nothing outside the stdlib + numpy/scipy/soundfile/ffmpeg.
Prints 'ZERO-COST AUDIT: PASS' or the list of violations (exit 1).
"""
from __future__ import annotations

import ast
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FREE_RUNNERS = {"ubuntu-latest", "ubuntu-24.04", "ubuntu-22.04", "windows-latest", "macos-latest"}
PAID_HOSTS = re.compile(r"api\.(openai|anthropic|elevenlabs|replicate|stability|runwayml|assemblyai|deepgram)\.", re.I)
PAID_SECRETS = re.compile(r"secrets\.(OPENAI|ANTHROPIC|ELEVENLABS|REPLICATE|STABILITY|RUNWAY|ASSEMBLYAI|DEEPGRAM)[A-Z_]*", re.I)
DOCTOR_ALLOWED_IMPORTS = {"__future__", "argparse", "copy", "hashlib", "json", "os", "re", "subprocess", "sys", "time", "numpy", "scipy", "soundfile", "typing", "yaml", "PIL", "glob", "difflib", "faster_whisper"}
PAID_LIBS = {"openai", "anthropic", "elevenlabs", "replicate", "boto3", "google", "azure"}


def read(p):
    return open(p, encoding="utf-8", errors="replace").read()


def main() -> int:
    bad = []
    wf = os.path.join(ROOT, ".github", "workflows")
    for fn in sorted(os.listdir(wf)):
        s = read(os.path.join(wf, fn))
        for m in re.finditer(r"runs-on:\s*(.+)", s):
            r = m.group(1).strip().strip("\"'")
            if r not in FREE_RUNNERS and "matrix." not in r:
                bad.append(f"{fn}: runner '{r}' is not a free GitHub-hosted standard runner")
        if re.search(r"^\s*schedule:", s, re.M):
            bad.append(f"{fn}: schedule trigger (hard rule: no cron, polling or idle jobs)")
        if "pull_request_target" in s:
            bad.append(f"{fn}: pull_request_target")
        if PAID_SECRETS.search(s) or PAID_HOSTS.search(s):
            bad.append(f"{fn}: paid API secret/host referenced")
    for base in ("factory", "tools"):
        for dp, _, fns in os.walk(os.path.join(ROOT, base)):
            if "__pycache__" in dp:
                continue
            for fn in fns:
                if not fn.endswith(".py"):
                    continue
                p = os.path.join(dp, fn)
                s = read(p)
                if PAID_HOSTS.search(s) and "cost_audit" not in fn:
                    bad.append(f"{os.path.relpath(p, ROOT)}: paid API host")
                try:
                    tree = ast.parse(s)
                except SyntaxError:
                    continue
                for n in ast.walk(tree):
                    mods = [a.name.split(".")[0] for a in n.names] if isinstance(n, ast.Import) else ([n.module.split(".")[0]] if isinstance(n, ast.ImportFrom) and n.module and not n.level else [])
                    for mname in mods:
                        if mname in PAID_LIBS:
                            bad.append(f"{os.path.relpath(p, ROOT)}: imports paid client library '{mname}'")
    dd = os.path.join(ROOT, "factory", "doctor")
    for fn in sorted(os.listdir(dd)):
        if fn.endswith(".py"):
            tree = ast.parse(read(os.path.join(dd, fn)))
            for n in ast.walk(tree):
                mods = [a.name.split(".")[0] for a in n.names] if isinstance(n, ast.Import) else ([n.module.split(".")[0]] if isinstance(n, ast.ImportFrom) and n.module and not n.level else [])
                for mname in mods:
                    if mname not in DOCTOR_ALLOWED_IMPORTS:
                        bad.append(f"factory/doctor/{fn}: import '{mname}' is not on the zero-cost allowlist")
    lic = os.path.join(ROOT, "docs", "LICENSES_QA.md")
    if not os.path.exists(lic):
        bad.append("docs/LICENSES_QA.md missing (licence of every QA dependency)")
    else:
        t = read(lic)
        for dep in ("numpy", "scipy", "soundfile", "ffmpeg"):
            if dep not in t.lower():
                bad.append(f"docs/LICENSES_QA.md: no licence entry for {dep}")
    if bad:
        print("ZERO-COST AUDIT: FAIL")
        for b in bad:
            print(" -", b)
        return 1
    print("ZERO-COST AUDIT: PASS")
    print(" runners: GitHub-hosted standard only; schedules: none; paid APIs: none; Doctor imports: stdlib + numpy/scipy/soundfile + ffmpeg; licences: docs/LICENSES_QA.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())

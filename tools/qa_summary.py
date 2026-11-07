"""python tools/qa_summary.py <slug | path/to/qa_report.json>  -> at most 30 lines.

With a slug it downloads the newest 'qa-report' artifact of produce.yml via gh (decrypting with the local age key for production jobs)."""
import json
import os
import subprocess
import sys
import tempfile
import glob

HOME = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), ".story-factory")


def find_report(arg):
    if os.path.exists(arg):
        return arg
    tmp = tempfile.mkdtemp(prefix="qa-")
    runs = subprocess.run(["gh", "run", "list", "--workflow", "produce.yml", "--limit", "15", "--json", "databaseId,displayTitle,conclusion,headBranch"], capture_output=True, text=True).stdout
    for r in json.loads(runs or "[]"):
        d = os.path.join(tmp, str(r["databaseId"]))
        p = subprocess.run(["gh", "run", "download", str(r["databaseId"]), "-n", "qa-report", "-D", d], capture_output=True, text=True)
        if p.returncode != 0:
            continue
        enc = glob.glob(os.path.join(d, "*.tar.age"))
        if enc:
            subprocess.run([os.path.join(HOME, "age.exe"), "-d", "-i", os.path.join(HOME, "backup.key"), "-o", os.path.join(d, "x.tar"), enc[0]], check=True)
            subprocess.run(["tar", "-xf", os.path.join(d, "x.tar"), "-C", d], check=True)
        hits = glob.glob(os.path.join(d, "**", "qa_report.json"), recursive=True)
        if hits:
            return hits[0]
    return None


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "latest"
    path = find_report(arg)
    if not path:
        print("no qa_report found")
        return 1
    q = json.load(open(path))
    lines = [f"PASS={q['pass']}  duration={q['duration']['actual']}s  fix_rounds={q.get('fix_rounds', 0)}"]
    lines.append("categories: " + ", ".join(f"{k}={'ok' if v else 'FAIL'}" for k, v in q["categories"].items()))
    lines.append(f"spec: {q['spec']['video']} | {q['spec']['audio']} | {q['spec']['video_kbps']} kbps")
    a = q["audio"]
    lines.append(f"audio: {a['lufs']} LUFS, TP {a['true_peak']}, LRA {a['lra']}")
    lines.append(f"motion share {q['motion']['share']}  static {q['motion']['static_shots'][:6]}")
    lines.append(f"flash/s {q['flash']['max_per_s']}  black {q['black']['intervals'][:3]}  freeze {q['freeze']['intervals'][:3]}")
    lines.append(f"A/V sync: max offset {q['av_sync']['max_offset_frames']} frames, off-grid cuts {q['av_sync']['off_grid_cuts']}")
    if q.get("bad_chunks"):
        lines.append(f"bad chunks: {q['bad_chunks']}")
    sc = q.get("scorecard")
    if sc:
        lines.append(f"scorecard ok={sc['ok']} (reference provisional={sc['provisional_reference']})")
        for r in sc["rows"]:
            if not r["ok"]:
                lines.append(f"  FAIL {r['dimension']}: ours={r['ours']} ref={r['reference']}")
    print("\n".join(lines[:30]))
    return 0 if q["pass"] else 2


if __name__ == "__main__":
    sys.exit(main())

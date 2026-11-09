"""P-018: automatic shot / location / interrupt budget for ONE video, from its own length. Usage: python tools/shot_budget.py <slug> <seconds> [freezes] [shots_actual] [locations_actual]
Writes docs/SHOT_BUDGET_<slug>.md and prints the one progress line."""
import math
import os
import sys


def budget(seconds: float, freezes: int = 0) -> dict:
    m = seconds / 60.0
    return {"M": round(m, 2), "shots_min": round(m * 12), "shots_max": round(m * 15), "shots_target": round(m * 13.5), "locations": math.ceil(m * 3),
            "angles_per_location": 3, "interrupts": max(math.ceil(m * 3), round(m * 60 / 20)), "freezes": freezes,
            "closeups_min": 0.15, "inserts_min": 0.20, "wide_min": 0.15, "size_max": 0.40, "poses_min": math.ceil(m * 3), "expressions_min": math.ceil(m * 2),
            "avg_shot_s": "4-5 (max 8 only for a freeze card or key reveal)"}


def main(argv):
    slug, seconds = argv[0], float(argv[1])
    fz = int(argv[2]) if len(argv) > 2 else 0
    b = budget(seconds, fz)
    line = (f"Video length {b['M']} min | shots {b['shots_min']}-{b['shots_max']} (target {b['shots_target']}) | locations {b['locations']} (3+ angles each) | "
            f"pattern interrupts {b['interrupts']}+ | freezes {fz} | production time: see the first progress line")
    rows = "\n".join(f"| {k} | {v} |" for k, v in b.items())
    actual = ""
    if len(argv) > 4:
        sa, la = int(argv[3]), int(argv[4])
        actual = f"\nActual render: {sa} shots ({'OUT OF RANGE' if not b['shots_min']*0.9 <= sa <= b['shots_max']*1.1 else 'ok'}), {la} locations ({'MAJOR: below budget' if la < b['locations']*0.9 else 'ok'}).\n"
    open(os.path.join("docs", f"SHOT_BUDGET_{slug}.md"), "w", encoding="utf-8").write(f"# Shot budget {slug} (P-018)\n\n{line}\n\n| item | value |\n|---|---|\n{rows}\n{actual}")
    print(line)


if __name__ == "__main__":
    main(sys.argv[1:])

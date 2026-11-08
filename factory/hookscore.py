"""Hook rubric (stdlib): specificity, stakes, curiosity gap, visual potential -> 0-10 each. Used by the validator and logged per job."""
from __future__ import annotations

import re

from .textutil import count_numbers

STAKES = ("die", "dead", "lose", "lost", "last", "only", "alive", "trapped", "minutes", "seconds", "left", "dark", "never", "swore", "save", "breath", "oxygen", "before")
CURIOSITY = ("never", "swore", "one thing", "why", "how", "what", "secret", "until", "about to", "?")
VISUAL = ("city", "phone", "dark", "machine", "battery", "screen", "door", "roof", "storm", "sky", "light", "window", "car", "fire")


def _hits(text: str, words) -> int:
    return sum(1 for w in words if (w in text if not w.isalpha() or " " in w else re.search(r"\b" + w + r"\b", text)))


def score(text: str) -> dict:
    t = text.lower()
    named = len(re.findall(r"(?<![.!?]\s)(?<!^)\b[A-Z][a-z]{2,}", text))
    s = {"specificity": min(10.0, 2.5 * count_numbers(t) + 1.5 * named), "stakes": min(10.0, 2.5 * _hits(t, STAKES)),
         "curiosity": min(10.0, 3.0 * _hits(t, CURIOSITY)), "visual": min(10.0, 2.0 * _hits(t, VISUAL))}
    s["total"] = round(sum(s.values()) / 4.0, 2)
    return s


def parse_options(raw: str):
    """'// HOOKOPT 1 | text' lines and '// HOOKPICK n' -> (options {n: text}, picked n or None)."""
    opts = {int(m.group(1)): m.group(2).strip() for m in re.finditer(r"^//\s*HOOKOPT\s+(\d)\s*\|\s*(.+)$", raw, re.M)}
    m = re.search(r"^//\s*HOOKPICK\s+(\d)", raw, re.M)
    return opts, int(m.group(1)) if m else None

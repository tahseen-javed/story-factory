"""Text helpers shared by validator, planner and TTS (stdlib only)."""
from __future__ import annotations

import re

_ABBREV = ("Mr.", "Mrs.", "Ms.", "Dr.", "St.", "vs.", "U.S.", "U.K.", "a.m.", "p.m.", "No.", "approx.", "e.g.", "i.e.")
_NUMBER_WORDS = {
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen",
    "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
    "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "million", "billion", "dozen",
}


def count_words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-]*", text))


def split_sentences(text: str) -> list:
    """Split narration into sentences. Keeps terminal punctuation. Protects common abbreviations."""
    t = text.strip()
    if not t:
        return []
    for i, a in enumerate(_ABBREV):
        t = t.replace(a, a.replace(".", f"․"))  # one-dot leader placeholder
    parts = re.split(r"(?<=[.!?…])[\"”’)\]]*\s+(?=[\"“‘(\[]?[A-Z0-9])", t)
    out = []
    for p in parts:
        p = p.replace("․", ".").strip()
        if p:
            out.append(p)
    return out


def count_numbers(text: str) -> int:
    """Concrete numbers: digit groups and spelled-out number words."""
    digits = re.findall(r"\d[\d,:.]*", text)
    words = [w for w in re.findall(r"[A-Za-z]+", text.lower()) if w in _NUMBER_WORDS]
    return len(digits) + len(words)


def syllables(word: str) -> int:
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups)
    if w.endswith("e") and not w.endswith("le") and n > 1:
        n -= 1
    return max(1, n)


def fk_grade(text: str) -> float:
    """Flesch-Kincaid grade level."""
    sents = split_sentences(text) or [text]
    words = re.findall(r"[A-Za-z']+", text)
    if not words:
        return 0.0
    syl = sum(syllables(w) for w in words)
    return 0.39 * (len(words) / len(sents)) + 11.8 * (syl / len(words)) - 15.59


def pause_after(sentence: str, cfg_audio: dict, chapter_end: bool = False) -> float:
    if chapter_end:
        return float(cfg_audio.get("pause_chapter_s", 0.8))
    s = sentence.rstrip()
    if s.endswith(("...", "…")):
        return float(cfg_audio.get("pause_period_s", 0.3)) + 0.15
    if s.endswith((".", "!", "?")):
        return float(cfg_audio.get("pause_period_s", 0.3))
    return float(cfg_audio.get("pause_comma_s", 0.15))


def estimate_seconds(text: str, wpm: float = 170.0, period_pause: float = 0.30) -> float:
    n = count_words(text)
    return n / (wpm / 60.0) + period_pause * len(split_sentences(text))


def slugify(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s or "untitled"


def safe_short_title(title: str) -> str:
    """Three-word Title Case short name, letters and digits only."""
    words = re.findall(r"[A-Za-z0-9]+", title)
    stop = {"the", "a", "an", "of", "to", "in", "on", "and", "for", "your", "you", "how", "what", "is", "are", "at", "with"}
    keep = [w for w in words if w.lower() not in stop] or words
    return " ".join(w.capitalize() for w in keep[:3])

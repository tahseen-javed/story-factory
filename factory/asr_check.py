"""ASR round-trip check for TTS sentences: sherpa-onnx Moonshine (primary), faster-whisper (fallback).

wer() and normalize() are stdlib only so they can be unit-tested locally.
"""
from __future__ import annotations

import os
import re
import tarfile
import urllib.request

MOONSHINE_URL = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-moonshine-base-en-int8.tar.bz2"

_SMALL = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
          "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]


def int_to_words(n: int) -> str:
    if n < 20:
        return _SMALL[n]
    if n < 100:
        return _TENS[n // 10] + ("" if n % 10 == 0 else " " + _SMALL[n % 10])
    if n < 1000:
        return _SMALL[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + int_to_words(n % 100))
    if n < 1_000_000:
        return int_to_words(n // 1000) + " thousand" + ("" if n % 1000 == 0 else " " + int_to_words(n % 1000))
    return str(n)


# pairs of (pattern, replacement) applied to BOTH reference and hypothesis so spelling variants compare equal
_EQUIV = [
    (r"\bready\.?\s*gov\b", "ready gov"), (r"\bready dot gov\b", "ready gov"),
    (r"\bwi[- ]?fi\b", "wifi"), (r"\bwhy[- ]fy\b", "wifi"),
    (r"\bg\s?5\b", "g five"), (r"\bg five\b", "g five"),
    (r"\b3b\b", "three b"), (r"\bthree bee\b", "three b"), (r"\bthree-b\b", "three b"),
    (r"\bokay\b", "ok"), (r"\bkay\b", "ok"), (r"\btoo\b", "two"),
    (r"\ba (hundred|thousand)\b", r"one \1"), (r"\b(hundred|thousand) and\b", r"\1"),
]


def year_words(n: int) -> str:
    """1989 -> nineteen eighty nine; 1905 -> nineteen oh five; 2005 -> two thousand five."""
    if 1100 <= n <= 1999 or 2010 <= n <= 2099:
        hi, lo = divmod(n, 100)
        lo_w = "hundred" if lo == 0 else (("oh " + int_to_words(lo)) if lo < 10 else int_to_words(lo))
        return f"{int_to_words(hi)} {lo_w}".strip()
    return int_to_words(n)


def _num_tokens(m: "re.Match") -> str:
    s = m.group(0)
    if re.fullmatch(r"\d{4}", s):
        return year_words(int(s))
    if ":" in s:  # clock times like 3:12 -> "three twelve"
        h, mi = s.split(":")[:2]
        mi_w = "" if int(mi) == 0 else (("oh " + int_to_words(int(mi))) if int(mi) < 10 else int_to_words(int(mi)))
        return (int_to_words(int(h)) + " " + mi_w).strip()
    return int_to_words(int(s.replace(",", "")))


_ORD = {"one": "first", "two": "second", "three": "third", "five": "fifth", "eight": "eighth", "nine": "ninth", "twelve": "twelfth"}


def _ord(m: "re.Match") -> str:
    """90th -> ninetieth, 21st -> twenty first (Whisper writes ordinals as digits)."""
    w = int_to_words(int(m.group(1))).split(" ")
    last = w[-1]
    last = _ORD.get(last) or (last[:-1] + "ieth" if last.endswith("y") else last + "th")
    return " ".join(w[:-1] + [last])


def normalize(text: str) -> list:
    t = text.lower().replace("’", "'")
    t = re.sub(r"\b(\d+)([a-z])\b", r"\1 \2", t)  # 3b -> 3 b
    t = re.sub(r"(\d+)\s*%", r"\1 percent", t)
    t = re.sub(r"\$\s*(\d[\d,]*)", r"\1 dollars", t)
    t = re.sub(r"\b(\d+)(?:st|nd|rd|th)\b", _ord, t)
    t = re.sub(r"\d{1,3}(?:,\d{3})+|\d+:\d{2}|\d+", _num_tokens, t)
    t = re.sub(r"[^a-z0-9' ]+", " ", t.replace("-", " "))
    t = re.sub(r"\s+", " ", t).strip()
    for pat, rep in _EQUIV:
        t = re.sub(pat, rep, t)
    return t.split()


def wer(ref: str, hyp: str) -> float:
    r, h = normalize(ref), normalize(hyp)
    if not r:
        return 0.0 if not h else 1.0
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            cur = d[j]
            d[j] = min(d[j] + 1, d[j - 1] + 1, prev + (r[i - 1] != h[j - 1]))
            prev = cur
    return d[len(h)] / len(r)


class Asr:
    """Lazy ASR wrapper. engine: 'sherpa_moonshine' | 'faster_whisper'."""

    def __init__(self, cache_dir: str = ".asr", threads: int = 4):
        self.engine = None
        self.rec = None
        self.name = "none"
        try:
            self._init_sherpa(cache_dir, threads)
        except Exception as e:  # noqa: BLE001
            print(f"[asr] sherpa-onnx unavailable ({e!r}); trying faster-whisper")
            try:
                self._init_whisper(threads)
            except Exception as e2:  # noqa: BLE001
                print(f"[asr] faster-whisper unavailable ({e2!r}); ASR check disabled")

    def _init_sherpa(self, cache_dir, threads):
        import sherpa_onnx  # type: ignore

        d = os.path.join(cache_dir, "sherpa-onnx-moonshine-base-en-int8")
        if not os.path.exists(os.path.join(d, "tokens.txt")):
            os.makedirs(cache_dir, exist_ok=True)
            tgz = os.path.join(cache_dir, "m.tar.bz2")
            urllib.request.urlretrieve(MOONSHINE_URL, tgz)
            with tarfile.open(tgz, "r:bz2") as tf:
                tf.extractall(cache_dir)
            os.remove(tgz)
        self.rec = sherpa_onnx.OfflineRecognizer.from_moonshine(
            preprocessor=d + "/preprocess.onnx", encoder=d + "/encode.int8.onnx",
            uncached_decoder=d + "/uncached_decode.int8.onnx", cached_decoder=d + "/cached_decode.int8.onnx",
            tokens=d + "/tokens.txt", num_threads=threads,
        )
        self.engine = "sherpa"
        self.name = "sherpa-onnx moonshine-base-en-int8"

    def _init_whisper(self, threads):
        from faster_whisper import WhisperModel  # type: ignore

        self.rec = WhisperModel("tiny.en", device="cpu", compute_type="int8", cpu_threads=threads)
        self.engine = "whisper"
        self.name = "faster-whisper tiny.en"

    @property
    def ok(self) -> bool:
        return self.engine is not None

    def transcribe(self, wav_path: str) -> str:
        import soundfile as sf  # type: ignore

        a, sr = sf.read(wav_path, dtype="float32")
        if a.ndim > 1:
            a = a[:, 0]
        if self.engine == "sherpa":
            s = self.rec.create_stream()
            s.accept_waveform(sr, a)
            self.rec.decode_stream(s)
            return s.result.text
        segs, _ = self.rec.transcribe(a, language="en", beam_size=1)
        return " ".join(x.text for x in segs)

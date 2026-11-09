"""Phase 2 stage 1: script-versus-speech comparison logic (pure functions; the Whisper model itself is exercised in CI)."""
import os
import unittest

from factory import miniyaml
from factory.doctor import voice

TH = miniyaml.load_file(os.path.join(os.path.dirname(__file__), "..", "config", "doctor.yaml"))
SENTS = [
    {"id": "s0", "start": 0.0, "end": 3.0, "text": "You have three buttons and four minutes of air."},
    {"id": "s1", "start": 3.4, "end": 5.5, "text": "One was never pressed."},
    {"id": "s2", "start": 6.0, "end": 9.0, "text": "Mrs. Hale, your neighbour, whispers."},
]


def words_for(text, t0, t1):
    ws = text.split()
    step = (t1 - t0) / max(1, len(ws))
    return [(w, t0 + i * step, t0 + (i + 1) * step) for i, w in enumerate(ws)]


def hyp(texts):
    out = []
    for s, t in zip(SENTS, texts):
        out += words_for(t, s["start"], s["end"])
    return out


class TestVoiceLogic(unittest.TestCase):
    def test_perfect_reading_passes(self):
        h = hyp(["You have 3 buttons and 4 minutes of air.", "One was never pressed.", "Mrs Hale, your neighbor, whispers."])
        f, m, rr = voice.verify_text(SENTS, h, TH)
        self.assertEqual([x["code"] for x in f if x["severity"] in ("BLOCKER", "MAJOR")], [], f)
        self.assertEqual(rr, [])
        self.assertLess(m["wer"], 0.05)

    def test_skipped_word_detected(self):
        h = hyp(["You have three buttons and minutes of air.", "One was never pressed.", "Mrs Hale, your neighbour, whispers."])
        f, _, rr = voice.verify_text(SENTS, h, TH)
        self.assertIn("A2-SKIP", {x["code"] for x in f})
        self.assertIn("s0", rr)

    def test_doubled_word_detected(self):
        h = hyp(["You have three buttons and four minutes of air.", "One was was never pressed.", "Mrs Hale, your neighbour, whispers."])
        f, _, rr = voice.verify_text(SENTS, h, TH)
        self.assertIn("A2-DOUBLE", {x["code"] for x in f})
        self.assertIn("s1", rr)

    def test_wer_over_5_percent_fails(self):
        h = hyp(["You have three puttons and four minutes of hair.", "One was never pressed.", "Mrs Hale, your neighbour, whispers."])
        f, m, _ = voice.verify_text(SENTS, h, TH)
        self.assertGreater(m["wer"], 0.05)
        self.assertIn("A2-WER", {x["code"] for x in f})

    def test_speed_window(self):
        slow = [dict(s, end=s["end"] * 2.5) for s in SENTS]
        slow = [dict(s, start=s["start"] * 2.5) for s in slow]
        f, m, _ = voice.verify_text(slow, hyp(["You have three buttons and four minutes of air.", "One was never pressed.", "Mrs Hale, your neighbour, whispers."]), TH)
        self.assertLess(m["wpm"], 130)
        self.assertIn("A2-WPM", {x["code"] for x in f})

    def test_compound_word_is_not_a_defect(self):
        s = [{"id": "s0", "start": 0.0, "end": 3.0, "text": "A retired map maker with a slow smile."}]
        f, m, rr = voice.verify_text(s, words_for("A retired mapmaker with a slow smile.", 0.0, 3.0), TH, None)
        self.assertEqual([x["code"] for x in f if x["severity"] in ("BLOCKER", "MAJOR")], [])

    def test_normalisation(self):
        self.assertEqual(voice.norm_words("Mrs. Hale, 3 minutes, 50%"), ["missus", "hale", "three", "minutes", "fifty", "percent"])


class TestVoiceRun(unittest.TestCase):
    def test_run_end_to_end_with_fake_recogniser(self):
        import json
        import tempfile

        import numpy as np
        import soundfile as sf

        d = tempfile.mkdtemp()
        sr = 48000
        sf.write(os.path.join(d, "stem_voice.wav"), (np.random.default_rng(1).normal(0, 0.05, sr * 10)).astype("float32"), sr)
        json.dump({"voice": [{"id": s["id"], "start": s["start"], "end": s["end"]} for s in SENTS]}, open(os.path.join(d, "audio_plan.json"), "w"))
        json.dump({"sentences": [{"id": s["id"], "text": s["text"]} for s in SENTS]}, open(os.path.join(d, "plan.json"), "w"))
        os.makedirs(os.path.join(d, "tts"))
        json.dump({"sentences": [{"id": s["id"], "hyp": s["text"]} for s in SENTS]}, open(os.path.join(d, "tts", "meta_0.json"), "w"))
        words = [w for s in SENTS for w in words_for(s["text"], s["start"], s["end"])]
        orig, voice.transcribe = voice.transcribe, lambda x16, name="small.en": words
        try:
            rep = voice.run(d, TH, "small.en", None, os.path.join(d, "tts"))
        finally:
            voice.transcribe = orig
        self.assertEqual(rep["status"], "OK", rep.get("error"))
        self.assertEqual(rep["reroll"], [])


if __name__ == "__main__":
    unittest.main()

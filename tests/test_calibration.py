"""P-017: the false alarms of run 42657994372 and the other calibration facts must never come back."""
import os
import unittest

from factory import miniyaml
from factory.doctor import voice

ROOT = os.path.join(os.path.dirname(__file__), "..")
TH = miniyaml.load_file(os.path.join(ROOT, "config", "doctor.yaml"))
AUDIO = miniyaml.load_file(os.path.join(ROOT, "config", "audio.yaml"))


class TestCalibration(unittest.TestCase):
    def test_homophone_walts_waltz(self):
        s = [{"id": "s0", "start": 0.0, "end": 3.0, "text": "Walt's hand stops yours."}]
        ws = [("Waltz", 0.0, 0.5), ("hand", 0.5, 1.0), ("stops", 1.0, 1.5), ("yours", 1.5, 2.0)]
        f, _, _ = voice.verify_text(s, ws, TH, None)
        self.assertEqual([x["code"] for x in f if x["severity"] in ("BLOCKER", "MAJOR")], [])

    def test_same_voice_numbers_from_004_do_not_drift(self):
        v = TH["voice"]
        self.assertGreaterEqual(v["drift_mel_db"], 6.5)    # measured 6.0 dB between sentences of the same narrator
        self.assertGreaterEqual(v["drift_f0_hz"], 85)      # measured 81 Hz
        self.assertGreaterEqual(v["narrator_mel_db"], 6.5)

    def test_hold_release_is_gentle(self):
        self.assertGreaterEqual(float(AUDIO["hold_release_s"]), 1.0)


if __name__ == "__main__":
    unittest.main()

"""P-008: calibration, cute + unique casts, locked distinct voices, preflight."""
import json
import os
import unittest

import numpy as np

from factory import cast, preflight, voicecheck
from factory.parse import parse
from factory.uniqueness import shot_signature
from factory.validate import ROOT, load_cfg

PILOT = os.path.join(ROOT, "pilot", "solar-storm-blackout")


class TestCalibration(unittest.TestCase):
    def test_v21_maps_to_owner_rating(self):
        cal = load_cfg()["qa_calibration"]
        pen = sum(v for k, v in cal["penalties"].items() if not cal["features_shipped"].get(k))
        self.assertAlmostEqual(10.0 - pen, cal["anchor"]["owner_rating"], places=1)


class TestCast(unittest.TestCase):
    def setUp(self):
        self.cfg = load_cfg()

    def test_cute_defaults_pass_and_plain_rig_fails(self):
        chars = {"a": {"params": {"outfit": "red"}}}
        self.assertTrue(cast.cute_check(chars, self.cfg["style"], "", True)["ok"])
        self.assertFalse(cast.cute_check(chars, self.cfg["style"], "", False)["ok"])   # headScale 1.0 is not cute enough
        self.assertFalse(cast.cute_check({"a": {"params": {"outfit": "red", "prop": "knife"}}}, self.cfg["style"], "", True)["ok"])

    def test_identical_character_or_cast_fails_uniqueness(self):
        style = self.cfg["style"]
        mine = {"hero": {"params": {"outfit": "teal", "hat": "cap", "hair": "short"}}}
        hist = [{"nnn": 1, "cast": cast.cast_sigs(mine), "shots_sig": list("abcdefgh")}]
        self.assertFalse(cast.unique_check(mine, list("abcdefgh"), hist, style, nnn=2)["ok"])
        other = {"kid": {"params": {"outfit": "coral", "hat": "beanie", "hair": "curly"}}}
        self.assertTrue(cast.unique_check(other, list("stuvwxyz"), hist, style, nnn=2)["ok"])


class TestVoices(unittest.TestCase):
    def test_profiles_locked_and_distinct(self):
        cfg = load_cfg()["characters"]
        self.assertTrue(voicecheck.profiles_ok(cfg, {"hero": {}, "mara": {}})["ok"])
        self.assertFalse(voicecheck.profiles_ok(cfg, {"stranger": {}})["ok"])           # no locked profile
        bad = json.loads(json.dumps(cfg)); bad["characters"]["mara"] = dict(bad["characters"]["hero"])
        self.assertFalse(voicecheck.profiles_ok(bad, {"hero": {}, "mara": {}})["ok"])    # same recipe
        bad2 = json.loads(json.dumps(cfg)); bad2["characters"]["hero"]["engine"] = "elevenlabs_clone"
        self.assertFalse(voicecheck.profiles_ok(bad2, {"hero": {}})["ok"])               # not an allowed source

    def test_fingerprint_separates_voices(self):
        sr = 16000
        t = np.arange(sr * 2) / sr

        def voice(f0, tilt):
            x = sum(np.sin(2 * np.pi * f0 * k * t) / (k ** tilt) for k in range(1, 30))
            return x * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * t))

        a, b, a2 = (voicecheck.fingerprint(voice(110, 1.0), sr), voicecheck.fingerprint(voice(230, 2.0), sr), voicecheck.fingerprint(voice(110, 1.0), sr))
        self.assertTrue(voicecheck.too_similar(a, a2))
        self.assertFalse(voicecheck.too_similar(a, b))


class TestPreflight(unittest.TestCase):
    def test_preflight_reports_six_checks(self):
        rep = preflight.run(PILOT, 55, 60, out_path=os.path.join(ROOT, "build", "preflight_test.json"))
        self.assertEqual(len(rep["checks"]), 6)
        self.assertTrue(rep["checks"]["1_time_estimate"]["ok"] and rep["checks"]["2_licence_gate"]["ok"] and rep["checks"]["3_monetization"]["ok"])
        self.assertFalse(preflight.run(PILOT, 90, 60, out_path=os.path.join(ROOT, "build", "preflight_test.json"))["checks"]["1_time_estimate"]["ok"])


if __name__ == "__main__":
    unittest.main()

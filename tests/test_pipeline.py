import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from factory import assemble, plan as planmod
from factory.asr_check import normalize, wer
from factory.validate import load_cfg


class TestWer(unittest.TestCase):
    def test_numbers_and_aliases(self):
        self.assertEqual(wer("Fifteen hours. That's all you have.", "15 hours. That's all you have."), 0.0)
        self.assertEqual(normalize("It's Friday, three twelve in the morning."), normalize("It's Friday, 3:12 in the morning."))
        self.assertEqual(wer("Ready dot gov says one gallon.", "Ready.gov says 1 gallon."), 0.0)

    def test_error_rate(self):
        self.assertAlmostEqual(wer("one two three four", "one two four"), 0.25)
        self.assertEqual(wer("a b", ""), 1.0)


class TestCameraFix(unittest.TestCase):
    cfg = load_cfg()

    def test_speed_clamped_into_2_to_8_percent_per_second(self):
        notes = []
        c = assemble.fix_camera({"preset": "push", "z0": 1.0, "z1": 1.30}, 2.0, self.cfg, notes, 0)
        speed = (c["z1"] / c["z0"] - 1) / 2.0
        self.assertLessEqual(speed, 0.081)
        self.assertGreaterEqual(speed, 0.0199)
        self.assertTrue(notes)

    def test_pull_direction_and_bounds(self):
        c = assemble.fix_camera({"preset": "pull", "z0": 1.20, "z1": 1.06}, 4.0, self.cfg, [], 1)
        self.assertGreater(c["z0"], c["z1"])
        self.assertLessEqual(c["z0"], 1.35)
        self.assertGreaterEqual(c["z1"], 1.0)

    def test_static_still_gets_zoom_in_bounds(self):
        c = assemble.fix_camera({"preset": "pan_l", "z0": 1.0, "z1": 1.0}, 3.0, self.cfg, [], 2)
        self.assertGreaterEqual(c["z0"], 1.06)


class TestPlan(unittest.TestCase):
    def test_pilot_plan_shape(self):
        p = planmod.build_plan(os.path.join(ROOT, "pilot", "solar-storm-blackout"))
        self.assertEqual(p["mode"], "pilot")
        self.assertEqual(len(p["chapters"]), 3)
        self.assertTrue(all(s["tts_text"] for s in p["sentences"]))
        locs = {g["location"] for g in p["image_groups"]}
        self.assertEqual(locs, set(p["locations"]))
        # every shot has at least one sentence and sentence ids are unique
        ids = [s["id"] for s in p["sentences"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(sh["sentences"] for sh in p["shots"]))

    def test_layout_and_facing(self):
        out = assemble.layout_chars([{"id": "a", "pose": "stand", "expr": "neutral", "x": None}, {"id": "b", "pose": "stand", "expr": "neutral", "x": None}], 0)
        self.assertEqual([c["x"] for c in out], [0.30, 0.70])
        self.assertEqual([c["facing"] for c in out], [1, -1])

    def test_srt_time(self):
        self.assertEqual(assemble.srt_time(3723.456), "01:02:03,456")


if __name__ == "__main__":
    unittest.main()


class TestPublishQuota(unittest.TestCase):
    def test_quota_and_rate(self):
        from factory import publish

        cfg = load_cfg()
        day = "2026-11-08"
        self.assertEqual(publish.pacific_day(__import__("datetime").datetime(2026, 11, 8, 7, 0, tzinfo=__import__("datetime").timezone.utc)), "2026-11-07")
        ledger = {"1": {"day": day, "captions": True}}
        ok, _ = publish.can_upload(ledger, cfg, True, day)
        self.assertTrue(ok)
        ledger["2"] = {"day": day, "captions": True}
        ok, why = publish.can_upload(ledger, cfg, True, day)
        self.assertFalse(ok)
        self.assertIn("publish_rate", why)
        self.assertEqual(publish.quota_used_today(ledger, day), 2 * (1600 + 50 + 400))

    def test_skips_without_secrets(self):
        from factory import publish

        for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"):
            os.environ.pop(k, None)
        self.assertEqual(publish.main(["--nnn", "1", "--base", "x", "--video", "v", "--thumb", "t", "--srt", "s", "--info", "i", "--ledger", "l"]), 0)

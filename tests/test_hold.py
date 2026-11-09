"""Decision hold (owner test video): parse + plan + Doctor exemption (allowed up to 5 s, max 1 per 40 s), unmarked gaps still fail."""
import json
import os
import tempfile
import unittest

from factory import miniyaml
from factory.doctor import audio as A
from factory.doctor import fixtures
from factory.parse import parse
from factory.plan import build_plan
from factory import assemble
from test_v2 import fake_tts

ROOT = os.path.join(os.path.dirname(__file__), "..")
TH = miniyaml.load_file(os.path.join(ROOT, "config", "doctor.yaml"))


class TestHoldParsing(unittest.TestCase):
    def test_script_and_plan(self):
        sc = parse(open(os.path.join(ROOT, "pilot", "three-button-trap", "script.md"), encoding="utf-8").read())
        holds = [s for ch in sc.chapters for s in ch.shots if s.hold]
        self.assertEqual(len(holds), 1)
        self.assertEqual(holds[0].hold, 4.5)
        plan = build_plan(os.path.join(ROOT, "pilot", "three-button-trap"))
        self.assertEqual(plan["kind"], "test")
        held = [s for s in plan["shots"] if s.get("hold_after")]
        self.assertEqual(len(held), 1)
        prev = [s for s in plan["sentences"] if s["text"].startswith("Your clock keeps running")][0]
        self.assertGreaterEqual(prev["pause_after_s"], 4.5)
        nxt = plan["sentences"][prev["idx"] + 1]
        self.assertEqual(nxt.get("hold_before"), 4.5)

    def test_narration_is_the_owner_script_word_for_word(self):
        sc = parse(open(os.path.join(ROOT, "pilot", "three-button-trap", "script.md"), encoding="utf-8").read())
        got = " ".join(s.text for ch in sc.chapters for s in ch.shots)
        want = ('You have three buttons and four minutes of air. One was never pressed. The elevator jolts between floors. "They taped eight last week," whispers Mrs. Hale, your neighbour. '
                'Three minutes of air. The red button is spotless. Seven is worn smooth. Eight hides under fresh tape. Freeze. Option one, red. Option two, seven. Option three, eight. '
                'Pause the video. Decide now. Your clock keeps running. You press seven. Doors open. Fresh air. Red was spotless because it was never wired. '
                'The cleanest button was the one nobody trusted. Subscribe. The next door lies too.')
        self.assertEqual(got, want)


class TestHoldAssemble(unittest.TestCase):
    def test_hold_window_beat_and_sfx(self):
        job = os.path.join(ROOT, "pilot", "three-button-trap")
        plan = build_plan(job)
        with tempfile.TemporaryDirectory() as d:
            fake_tts(plan, os.path.join(d, "tts"))
            os.makedirs(os.path.join(d, "img"))
            json.dump(plan, open(os.path.join(d, "plan.json"), "w"))
            assemble.run(os.path.join(d, "plan.json"), os.path.join(d, "tts"), os.path.join(d, "img"), os.path.join(d, "out"), None)
            ap = json.load(open(os.path.join(d, "out", "audio_plan.json"), encoding="utf-8"))
            tl = json.load(open(os.path.join(d, "out", "props.json"), encoding="utf-8"))["timeline"]
        self.assertEqual(len(ap["holds"]), 1)
        a, b = ap["holds"][0]
        self.assertTrue(4.0 <= b - a <= 5.0, (a, b))
        self.assertEqual(ap["silence"], [])                               # a hold is not a silence beat
        names = {e["name"] for e in ap["sfx"] if a <= e["t"] <= b}
        self.assertTrue({"heartbeat", "ticking_clock"} <= names, names)
        held = [s for s in tl["shots"] if s.get("hold")]
        self.assertEqual(len(held), 1)                                    # one beat, flagged
        self.assertEqual(held[0]["overlay"]["name"], "option_cards")
        self.assertEqual(tl["kind"], "test")


class TestHoldDoctor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fx = fixtures.clean(24, seed=3)

    def _gap_fixture(self):
        fx = fixtures.mutate(self.fx, "voice_gap")
        plan = {"sentences": fx["plan"]["sentences"], "silence": fx["plan"]["silence"], "total_s": 24}
        _, f = A.check_voice(fx["stems"]["voice"], plan, TH)
        gaps = [x for x in f if x["code"] == "A1-GAP"]
        self.assertTrue(gaps)
        return fx, plan, gaps

    def test_unmarked_gap_fails(self):
        _, _, gaps = self._gap_fixture()
        self.assertGreater(gaps[0]["t1"] - gaps[0]["t0"], 2.5)

    def test_marked_hold_is_exempt(self):
        fx, plan, gaps = self._gap_fixture()
        plan = dict(plan, holds=[[gaps[0]["t0"] - 0.1, gaps[0]["t1"] + 0.1]])
        _, f = A.check_voice(fx["stems"]["voice"], plan, TH)
        self.assertNotIn("A1-GAP", {x["code"] for x in f})
        self.assertNotIn("A1-HOLD-LONG", {x["code"] for x in f})

    def test_hold_longer_than_5s_and_second_hold_fail(self):
        fx, plan, gaps = self._gap_fixture()
        g = gaps[0]
        long_hold = dict(plan, holds=[[g["t0"] - 0.1, g["t0"] + 6.9]])
        _, f = A.check_voice(fx["stems"]["voice"], long_hold, TH)
        self.assertIn("A1-HOLD-LONG", {x["code"] for x in f})
        two = dict(plan, holds=[[g["t0"] - 0.1, g["t1"] + 0.1], [2.0, 3.5]])
        _, f2 = A.check_voice(fx["stems"]["voice"], two, TH)
        self.assertIn("A1-HOLD-COUNT", {x["code"] for x in f2})


if __name__ == "__main__":
    unittest.main()

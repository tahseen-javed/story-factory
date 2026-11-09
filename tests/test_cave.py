"""Sea Cave (004): script == owner narration, four decision holds, meters follow the narration, one look per character."""
import json
import os
import re
import tempfile
import unittest

from factory import assemble, miniyaml
from factory.doctor import tech
from factory.parse import parse
from factory.plan import build_plan
from test_v2 import fake_tts

ROOT = os.path.join(os.path.dirname(__file__), "..")
JOB = os.path.join(ROOT, "pilot", "sea-cave")
TH = miniyaml.load_file(os.path.join(ROOT, "config", "doctor.yaml"))


class TestSeaCave(unittest.TestCase):
    def test_narration_word_for_word_and_holds(self):
        want = " ".join(l.strip() for l in open(os.path.join(JOB, "narration.txt"), encoding="utf-8").read().splitlines() if l.strip())
        sc = parse(open(os.path.join(JOB, "script.md"), encoding="utf-8").read())
        got = " ".join(s.text for ch in sc.chapters for s in ch.shots)
        self.assertEqual(re.sub(r"\s+", " ", got), want)
        self.assertEqual(len([s for ch in sc.chapters for s in ch.shots if s.hold]), 4)

    def test_assembled_meters_cast_and_hold_cards(self):
        plan = build_plan(JOB)
        with tempfile.TemporaryDirectory() as d:
            fake_tts(plan, os.path.join(d, "tts"))
            os.makedirs(os.path.join(d, "img"))
            json.dump(plan, open(os.path.join(d, "plan.json"), "w"))
            assemble.run(os.path.join(d, "plan.json"), os.path.join(d, "tts"), os.path.join(d, "img"), os.path.join(d, "out"), None)
            tl = json.load(open(os.path.join(d, "out", "props.json"), encoding="utf-8"))["timeline"]
            ap = json.load(open(os.path.join(d, "out", "audio_plan.json"), encoding="utf-8"))
        self.assertEqual(len(ap["holds"]), 4)
        self.assertEqual(tech.check_story(tl, plan, TH), [])


if __name__ == "__main__":
    unittest.main()

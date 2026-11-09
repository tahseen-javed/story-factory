"""Phase 2 stage 4: black, frozen, duplicate, flicker and cut checks on real (synthetic) mp4 files, plus the black-frame auto-fix and the timeline pacing/static checks."""
import os
import shutil
import subprocess
import tempfile
import unittest

from factory import miniyaml
from factory.doctor import tech

TH = miniyaml.load_file(os.path.join(os.path.dirname(__file__), "..", "config", "doctor.yaml"))
SRC = "testsrc2=s=320x180:r=30:d=10"


def make(path, vf="null"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", SRC, "-vf", vf, "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", path], check=True)


def codes(res):
    return {f["code"] for f in res["findings"]}


class TestTech(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, ignore_errors=True)

    def p(self, name):
        return os.path.join(self.d, name)

    def test_clean_has_no_blocker(self):
        make(self.p("clean.mp4"))
        res = tech.run_file(self.p("clean.mp4"), TH, None)
        bad = [f for f in res["findings"] if f["severity"] in ("BLOCKER", "MAJOR")]
        self.assertEqual(bad, [], bad)

    def test_black_detected_and_fixed(self):
        make(self.p("black.mp4"), "drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:enable='between(t,4,4.5)'")
        res = tech.run_file(self.p("black.mp4"), TH, None)
        self.assertIn("V4-BLACK", codes(res))
        self.assertTrue(tech.fix_black(self.p("black.mp4"), res["findings"], self.p("black_fixed.mp4")))
        self.assertNotIn("V4-BLACK", codes(tech.run_file(self.p("black_fixed.mp4"), TH, None)))

    def test_freeze_detected(self):
        make(self.p("src.mp4"))
        self.assertTrue(tech.hold_frames(self.p("src.mp4"), self.p("freeze.mp4"), 90, 150))
        self.assertIn("V4-FREEZE", codes(tech.run_file(self.p("freeze.mp4"), TH, None)))

    def test_freeze_inside_planned_hold_is_allowed(self):
        make(self.p("src2.mp4"))
        self.assertTrue(tech.hold_frames(self.p("src2.mp4"), self.p("freeze2.mp4"), 90, 150))
        tl = {"durationInFrames": 300, "shots": [{"i": 0, "start": 0, "dur": 80, "chars": [], "hold": False}, {"i": 1, "start": 80, "dur": 100, "chars": [], "hold": True}, {"i": 2, "start": 180, "dur": 120, "chars": [], "hold": False}]}
        self.assertNotIn("V4-FREEZE", codes(tech.run_file(self.p("freeze2.mp4"), TH, tl)))

    def test_flicker_detected(self):
        make(self.p("flick.mp4"), "eq=brightness='0.03*(mod(n,2)*2-1)':eval=frame")
        self.assertIn("V4-FLICKER", codes(tech.run_file(self.p("flick.mp4"), TH, None)))

    def test_static_pose_and_pacing_from_timeline(self):
        shots = [{"i": i, "start": i * 80, "dur": 80, "chars": [{"id": "hero", "pose": "stand", "expr": "worried"}], "hold": False} for i in range(4)]
        f, m = tech.check_timeline({"durationInFrames": 320, "shots": shots}, TH)
        self.assertIn("V6-STATIC", {x["code"] for x in f})
        for i in (1, 3):
            shots[i]["chars"][0]["pose"] = "point"
        f2, _ = tech.check_timeline({"durationInFrames": 320, "shots": shots}, TH)
        self.assertNotIn("V6-STATIC", {x["code"] for x in f2})


if __name__ == "__main__":
    unittest.main()

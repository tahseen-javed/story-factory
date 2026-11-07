"""Phase 4: inject one deliberate fault per QA check type and prove it is detected (and, where a fixer exists, fixed)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

try:
    import cv2  # noqa: F401
    import numpy as np  # noqa: F401
    HAVE = shutil.which("ffmpeg") is not None
except ImportError:
    HAVE = False


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args], check=True)


def make(path, video_filter, dur=6, size="1920x1080", audio=None):
    a = ["-f", "lavfi", "-i", audio or "sine=frequency=440:sample_rate=48000"]
    sep = ":" if "=" in video_filter else "="
    ff("-f", "lavfi", "-i", f"{video_filter}{sep}size={size}:rate=30:duration={dur}", *a, "-t", str(dur),
       "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", path)


def timeline(n_shots, total_s):
    dur = int(total_s * 30 / n_shots)
    return {"fps": 30, "durationInFrames": int(total_s * 30), "endScreenFrames": 0,
            "shots": [{"i": i, "start": i * dur, "dur": dur} for i in range(n_shots)]}


@unittest.skipUnless(HAVE, "needs ffmpeg + opencv + numpy (CI)")
class TestFaultInjection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from factory import qa
        from factory.validate import load_cfg

        cls.qa, cls.cfg = qa, load_cfg()
        cls.d = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, ignore_errors=True)

    def p(self, name):
        return os.path.join(self.d, name)

    def test_black_frames_detected_and_clean_video_passes(self):
        # 2 s black in the middle
        ff("-f", "lavfi", "-i", "testsrc2=size=1920x1080:rate=30:duration=3", "-f", "lavfi", "-i", "color=c=black:size=1920x1080:rate=30:duration=2",
           "-f", "lavfi", "-i", "testsrc2=size=1920x1080:rate=30:duration=3", "-filter_complex", "[0][1][2]concat=n=3:v=1:a=0", "-c:v", "libx264", "-pix_fmt", "yuv420p", self.p("black.mp4"))
        rep = {}
        bad = self.qa.check_black_freeze(self.p("black.mp4"), 8.0, 0.0, rep, [{"i": 0, "from": 0, "to": 239}])
        self.assertFalse(rep["black"]["ok"])
        self.assertEqual(bad, [0])
        make(self.p("clean.mp4"), "testsrc2", dur=6)
        rep = {}
        self.qa.check_black_freeze(self.p("clean.mp4"), 6.0, 0.0, rep, [{"i": 0, "from": 0, "to": 179}])
        self.assertTrue(rep["black"]["ok"])

    def test_frozen_picture_detected(self):
        make(self.p("freeze.mp4"), "color=c=0x336699", dur=6)
        rep = {}
        self.qa.check_black_freeze(self.p("freeze.mp4"), 6.0, 0.0, rep, [{"i": 0, "from": 0, "to": 179}])
        self.assertFalse(rep["freeze"]["ok"])

    def test_static_shots_fail_motion_check_moving_pass(self):
        rep = {}
        make(self.p("static.mp4"), "color=c=0x336699", dur=6)
        self.qa.check_motion_and_flashes(self.p("static.mp4"), timeline(3, 6), self.cfg, rep, [{"i": 0, "from": 0, "to": 179}])
        self.assertFalse(rep["motion"]["ok"])
        rep = {}
        make(self.p("moving.mp4"), "testsrc2", dur=6)
        self.qa.check_motion_and_flashes(self.p("moving.mp4"), timeline(3, 6), self.cfg, rep, [{"i": 0, "from": 0, "to": 179}])
        self.assertTrue(rep["motion"]["ok"], rep["motion"])

    def test_flash_rate_detected(self):
        ff("-f", "lavfi", "-i", "nullsrc=s=1280x720:r=30:d=4,geq=lum='255*lt(mod(floor(T*8),2),1)':cb=128:cr=128", "-c:v", "libx264", "-pix_fmt", "yuv420p", self.p("flash.mp4"))
        rep = {}
        self.qa.check_motion_and_flashes(self.p("flash.mp4"), timeline(2, 4), self.cfg, rep, [{"i": 0, "from": 0, "to": 119}])
        self.assertFalse(rep["flash"]["ok"], rep["flash"])

    def test_wrong_resolution_fails_spec(self):
        make(self.p("small.mp4"), "testsrc2", dur=2, size="1280x720")
        rep = {}
        self.qa.check_spec(self.qa.probe(self.p("small.mp4")), self.cfg, rep)
        self.assertFalse(rep["spec"]["ok"])
        make(self.p("full.mp4"), "testsrc2", dur=2)
        rep = {}
        self.qa.check_spec(self.qa.probe(self.p("full.mp4")), self.cfg, rep)
        self.assertTrue(rep["spec"]["ok"], rep["spec"])

    def test_quiet_audio_detected_and_remastered(self):
        from factory import mix

        make(self.p("quiet.mp4"), "testsrc2", dur=6, audio="sine=frequency=300:sample_rate=48000,volume=-30dB")
        rep = {}
        self.qa.check_audio(self.p("quiet.mp4"), self.cfg, rep)
        self.assertFalse(rep["audio"]["ok"])
        # fixer: re-master with the 2-pass loudnorm used by the mix stage
        ff("-i", self.p("quiet.mp4"), "-vn", "-ar", "48000", self.p("quiet.wav"))
        mix.loudnorm_two_pass(self.p("quiet.wav"), self.p("fixed.wav"), I=-14.0)
        ff("-i", self.p("quiet.mp4"), "-i", self.p("fixed.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", self.p("fixed.mp4"))
        rep = {}
        self.qa.check_audio(self.p("fixed.mp4"), self.cfg, rep)
        self.assertTrue(rep["audio"]["ok"], rep["audio"])

    def test_clipped_audio_detected(self):
        make(self.p("loud.mp4"), "testsrc2", dur=4, audio="sine=frequency=300:sample_rate=48000,volume=12dB,alimiter=limit=1:level=disabled")
        rep = {}
        self.qa.check_audio(self.p("loud.mp4"), self.cfg, rep)
        self.assertFalse(rep["audio"]["ok"])


if __name__ == "__main__":
    unittest.main()

import json
import os
import shutil
import sys
import tempfile
import unittest
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

try:
    import numpy as np
    import scipy  # noqa: F401
    import soundfile  # noqa: F401
    HAVE = True
except ImportError:
    HAVE = False


@unittest.skipUnless(HAVE, "numpy/scipy/soundfile not installed (CI only)")
class TestSynth(unittest.TestCase):
    def test_every_sfx_is_finite_and_audible(self):
        from factory import synth, vocab

        for name in vocab.SFX:
            x = synth.sfx(name)
            self.assertTrue(np.all(np.isfinite(x)), name)
            self.assertGreater(len(x), 1000, name)
            self.assertGreater(float(np.max(np.abs(x))), 0.01, name)
            self.assertIn(name, synth.SFX_GAIN)

    def test_every_mood_renders(self):
        from factory import synth, vocab

        for mood in vocab.MUSIC_MOODS:
            m = synth.render_music(mood, 4.0, seed=1)
            self.assertEqual(m.shape[0], 2)
            self.assertTrue(np.all(np.isfinite(m)), mood)
            rms = float(np.sqrt(np.mean(m ** 2)))
            self.assertGreater(rms, 0.03)
            self.assertLess(rms, 0.2)


@unittest.skipUnless(HAVE and shutil.which("ffmpeg"), "needs numpy/scipy/soundfile and ffmpeg (CI only)")
class TestMix(unittest.TestCase):
    def test_master_hits_loudness_targets(self):
        from factory import mix
        from factory.validate import load_cfg

        cfg = load_cfg()
        with tempfile.TemporaryDirectory() as d:
            vdir = os.path.join(d, "voice")
            os.makedirs(vdir)
            sr = 24000
            segs = []
            for i in range(4):
                t = np.arange(int(1.6 * sr)) / sr
                x = (0.2 * np.sin(2 * np.pi * (140 + 30 * i) * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 4 * t))).astype("float32")
                with wave.open(os.path.join(vdir, f"s{i}.wav"), "wb") as w:
                    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
                    w.writeframes((x * 32767).astype("<i2").tobytes())
                segs.append({"id": f"s{i}", "start": 0.6 + i * 2.0, "end": 2.2 + i * 2.0, "file": f"s{i}.wav"})
            plan = {"total_s": 11.0, "audio_end_s": 8.6, "lead_in_s": 0.6, "end_screen_s": 2.0, "voice": segs,
                    "music": [{"n": 1, "start": 0.0, "end": 5.0, "mood": "dread"}, {"n": 2, "start": 5.0, "end": 11.0, "mood": "climax"}],
                    "sfx": [{"t": 0.7, "name": "stinger_chapter", "gain": 0.0}, {"t": 3.0, "name": "door_knock", "gain": 0.0}], "style": {}}
            pp = os.path.join(d, "audio_plan.json")
            json.dump(plan, open(pp, "w"))
            mix.run(pp, vdir, os.path.join(d, "out"), cfg["audio"], -14.0)
            rep = json.load(open(os.path.join(d, "out", "mix_report.json")))
            self.assertAlmostEqual(float(rep["master"]["input_i"]), -14.0, delta=1.2)
            self.assertLessEqual(float(rep["master"]["input_tp"]), -0.8)


if __name__ == "__main__":
    unittest.main()

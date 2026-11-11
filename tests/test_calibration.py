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

    def test_homophones_ferry_fairy_rowed_rode(self):
        s = [{"id": "s0", "start": 0.0, "end": 4.0, "text": "The ferry's horn rowed past the ferry."}]
        ws = [("The", 0.0, 0.3), ("fairies", 0.3, 0.7), ("horn", 0.7, 1.0), ("rode", 1.0, 1.4), ("past", 1.4, 1.8), ("the", 1.8, 2.0), ("fairy", 2.0, 2.5)]
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


class TestMusicCrossfade(unittest.TestCase):
    def test_equal_power_ramps_keep_level(self):
        import numpy as np
        from factory.mix import xfade_ramps
        fin, fout = xfade_ramps(4 * 48000)
        self.assertLess(float(np.max(np.abs(fin ** 2 + fout ** 2 - 1.0))), 1e-5)
        rng = np.random.default_rng(1)
        a, b = rng.standard_normal(4 * 48000), rng.standard_normal(4 * 48000)
        mix = a * fout + b * fin
        mid = mix[len(mix) // 2 - 24000:len(mix) // 2 + 24000]
        dip_db = 20 * np.log10(np.sqrt(np.mean(mid ** 2)) / np.sqrt(np.mean(a ** 2)))
        self.assertGreater(dip_db, -0.5)
        self.assertGreaterEqual(float(AUDIO["music_xfade_s"]), 3.0)


class TestRound2(unittest.TestCase):
    def test_berth_birth_homophone(self):
        s = [{"id": "s0", "start": 0.0, "end": 3.0, "text": "Coach four, berth B, Rosa reads."}]
        ws = [("Coach", 0.0, 0.3), ("4", 0.3, 0.6), ("birth", 0.6, 0.9), ("B", 0.9, 1.2), ("Rosa", 1.2, 1.6), ("reads", 1.6, 2.0)]
        f, _, _ = voice.verify_text(s, ws, TH, None)
        self.assertEqual([x["code"] for x in f if x["severity"] in ("BLOCKER", "MAJOR")], [])

    def test_bed_leveler_flattens_swell(self):
        import numpy as np
        from factory.mix import level_bed
        sr = 8000
        t = np.arange(20 * sr) / sr
        amp = np.where((t > 8) & (t < 14), 3.0, 1.0)                    # a 6 s swell of +9.5 dB
        x = (np.sin(2 * np.pi * 220 * t) * amp * 0.1)[None, :].repeat(2, axis=0).astype("float32")
        y = level_bed(x, sr)
        def rms_db(a, s0, s1):
            return 20 * np.log10(np.sqrt(np.mean(a[0, int(s0 * sr):int(s1 * sr)] ** 2)) + 1e-9)
        before = rms_db(x, 10, 12) - rms_db(x, 2, 4)
        after = rms_db(y, 10, 12) - rms_db(y, 2, 4)
        self.assertGreater(before, 8.0)
        self.assertLess(abs(after), 4.5)

    def test_penhale_respelled_for_tts_only(self):
        from factory.plan import tts_text
        self.assertIn("Pen-hale", tts_text("was Penhale."))
        self.assertEqual(tts_text("Rosa Penhale, nineteen"), "Rosa Penhale, nineteen")


class TestMusicMeasures(unittest.TestCase):
    SR_ = 48000

    def _check(self, music):
        import numpy as np
        from factory.doctor import audio as A
        n = 24 * self.SR_
        t = np.arange(n) / self.SR_
        voice = (np.random.default_rng(0).standard_normal(n) * 0.05).astype("float32")
        plan = {"sentences": [{"id": "s0", "start": 0.5, "end": 23.5}], "silence": [], "holds": []}
        _, f = A.check_music(voice, music.astype("float32"), np.zeros(n, "float32"), np.zeros(n, "float32"), plan, TH)
        return {x["code"] for x in f if x["severity"] in ("BLOCKER", "MAJOR")}

    def test_note_articulation_is_not_a_jump(self):
        import numpy as np
        t = np.arange(24 * self.SR_) / self.SR_
        amp = 0.004 * (1.0 + 0.25 * np.sign(np.sin(2 * np.pi * 1.0 * t)))      # about +-2 dB every 0.5 s
        self.assertNotIn("A3-MUSIC-JUMP", self._check(np.sin(2 * np.pi * 330 * t) * amp))

    def test_real_level_step_is_a_jump(self):
        import numpy as np
        t = np.arange(24 * self.SR_) / self.SR_
        amp = 0.004 * np.where(t < 12, 1.0, 2.5)                              # +8 dB step inside one long sentence
        self.assertIn("A3-MUSIC-JUMP", self._check(np.sin(2 * np.pi * 330 * t) * amp))

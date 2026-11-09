"""P-014 / A3b: a clean mix passes MUSIC PRESENT; a mix with no music FAILS (BLOCKER) and the fix raises the bed."""
import os
import unittest

from factory import miniyaml
from factory.doctor import audio as A, fixes, fixtures

TH = miniyaml.load_file(os.path.join(os.path.dirname(__file__), "..", "config", "doctor.yaml"))


class TestMusicPresent(unittest.TestCase):
    def test_clean_passes_and_missing_fails(self):
        fx = fixtures.clean(24, seed=3)
        plan = {"sentences": fx["plan"]["sentences"], "silence": fx["plan"]["silence"]}
        _, f = A.check_music_present(fx["stems"]["voice"], fx["stems"]["music"], plan, TH)
        self.assertEqual([x["code"] for x in f if x["severity"] in ("BLOCKER", "MAJOR")], [])
        bad = fixtures.mutate(fx, "music_missing")
        _, f2 = A.check_music_present(bad["stems"]["voice"], bad["stems"]["music"], plan, TH)
        self.assertEqual({x["code"]: x["severity"] for x in f2}.get("A3B-MUSIC-MISSING"), "BLOCKER")
        p, _ = fixes.adjust_mix_params({}, f2, {}, TH)
        self.assertGreater(p["music_trim_db"], 0)


if __name__ == "__main__":
    unittest.main()

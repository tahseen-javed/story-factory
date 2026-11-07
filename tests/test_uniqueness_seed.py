import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from factory import seed, uniqueness

SCRIPT = """TITLE: {title}
LENGTH_MIN: 4
CHARACTERS:
- hero = rig_hero()
LOCATIONS:
- room: a room

## CH1 | NOW
@ room.{variant} | hero:stand/neutral | cam:{cam} 1.0>1.1
{text}
"""


class TestUniqueness(unittest.TestCase):
    def mk(self, d, name, title, text, variant="day", cam="push"):
        p = os.path.join(d, name)
        os.makedirs(p)
        open(os.path.join(p, "script.md"), "w", encoding="utf-8").write(SCRIPT.format(title=title, text=text, variant=variant, cam=cam))
        return p

    def test_same_story_flagged_different_story_passes(self):
        with tempfile.TemporaryDirectory() as d:
            a = self.mk(d, "a", "Solar Storm Night", "The solar storm warning wakes you at three in the morning and the whole city goes dark while the neighbour knocks.")
            b = self.mk(d, "b", "Solar Storm Night Two", "The solar storm warning wakes you at three in the morning and the whole city goes dark while the neighbour knocks twice.")
            c = self.mk(d, "c", "Flooded Subway", "Water pours into the tunnel under the river and you climb a ladder toward a hatch with a stranger holding a lantern.", variant="night", cam="pan_l")
            self.assertTrue(any(l == "error" for l, _ in uniqueness.check(a, [b])))
            self.assertFalse(any(l == "error" for l, _ in uniqueness.check(a, [c])))

    def test_first_video_has_nothing_to_compare(self):
        with tempfile.TemporaryDirectory() as d:
            a = self.mk(d, "a", "T", "Some text here for the very first story you will ever tell.")
            self.assertEqual(uniqueness.check(a, [])[0][0], "info")


class TestSeed(unittest.TestCase):
    def test_no_repeat_of_last_10_and_distinct_in_batch(self):
        hist = [{"nnn": 1, "openers": ["flash_forward"], "rituals": ["tracker_update"], "endings": ["twist_loop"], "accent": "amber", "lut": "cold_night",
                 "titlecard": "clock_strip", "camera_rhythm": "steady_push", "transition": "hard_cuts", "thumbnail_layout": "close_left", "music_set": "dread_pad", "outfit": "teal_cap"}]
        res = seed.pick(hist, 3)
        self.assertEqual([r["nnn"] for r in res], [2, 3, 4])
        for key in ("accent", "lut", "opening", "ritual", "ending"):
            vals = [r["style_seed"][key] for r in res]
            self.assertEqual(len(set(vals)), 3, key)
        self.assertNotEqual(res[0]["style_seed"]["accent"], "amber")
        self.assertNotEqual(res[0]["style_seed"]["opening"], "flash_forward")
        self.assertTrue(all(165 <= r["style_seed"]["wpm"] <= 185 for r in res))


if __name__ == "__main__":
    unittest.main()

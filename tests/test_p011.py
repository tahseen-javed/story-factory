"""P-011: inserts, second camera angle, new poses, v4 script rules (Last Ferry)."""
import os
import unittest

from factory import plan as planmod, vocab
from factory.validate import ROOT, load_cfg, validate_dir

LF = os.path.join(ROOT, "pilot", "last-ferry")


class TestP011(unittest.TestCase):
    def test_script_passes_v4_gate(self):
        issues, _ = validate_dir(LF)
        self.assertEqual([str(i) for i in issues if i.level == "error"], [])

    def test_inserts_have_no_image_and_every_place_has_two_angles(self):
        p = planmod.build_plan(LF, load_cfg())
        locs = [g["location"] for g in p["image_groups"]]
        self.assertNotIn("insert", locs)
        for l in [x for x in locs if not x.endswith("2")]:
            self.assertIn(l + "2", locs)

    def test_new_poses_and_meter_overlay_exist(self):
        for pose in ("look_up", "back_away", "reach", "shrug"):
            self.assertIn(pose, vocab.POSES)
        self.assertIn("meter", vocab.OVERLAYS)

    def test_big_silence_is_true_silence(self):
        p = planmod.build_plan(LF, load_cfg())
        self.assertTrue(any(s.get("silence_big") for s in p["sentences"]))


if __name__ == "__main__":
    unittest.main()

import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from factory import fixers, scorecard
from factory.validate import load_cfg


def props(shots):
    return {"timeline": {"fps": 30, "width": 1920, "height": 1080, "durationInFrames": 900, "shots": shots, "endScreenFrames": 600}}


def shot(i, start, dur, preset="hold", fx=None, overlay=None):
    return {"i": i, "start": start, "dur": dur, "camera": {"preset": preset, "z0": 1.0, "z1": 1.0, "fx": 0.5, "fy": 0.55}, "fx": fx or [], "overlay": overlay,
            "banner": "X" if i == 0 else None}


class TestFixers(unittest.TestCase):
    def test_static_shot_gets_camera_motion_and_chunk_rerender(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "props.json")
            json.dump(props([shot(0, 0, 100), shot(1, 100, 200), shot(2, 300, 200)]), open(p, "w"))
            qa = {"motion": {"ok": False, "static_shots": [1]}, "flash": {"ok": True}, "black": {"ok": True}, "freeze": {"ok": True}, "bad_chunks": []}
            res = fixers.apply(p, qa, [{"i": 0, "from": 0, "to": 299}, {"i": 1, "from": 300, "to": 899}])
            self.assertEqual(res["chunks"], [0])
            tl = json.load(open(p))["timeline"]
            self.assertEqual(tl["shots"][1]["camera"]["preset"], "push")
            self.assertGreater(tl["shots"][1]["camera"]["z1"], tl["shots"][1]["camera"]["z0"])

    def test_flash_fx_removed(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "props.json")
            json.dump(props([shot(0, 0, 100, fx=["flicker", "dust"])]), open(p, "w"))
            qa = {"motion": {"ok": True, "static_shots": []}, "flash": {"ok": False}, "black": {"ok": True}, "freeze": {"ok": True}, "bad_chunks": []}
            fixers.apply(p, qa, [{"i": 0, "from": 0, "to": 899}])
            self.assertEqual(json.load(open(p))["timeline"]["shots"][0]["fx"], ["dust"])


class TestScorecard(unittest.TestCase):
    def test_beats_reference_on_good_metrics(self):
        cfg = load_cfg()
        shots = [shot(i, i * 120, 120, "push", overlay={"name": ["timer", "receipt", "sticky_note", "notepad_tracker", "label_tag", "paper_diagram", "numbered_circle", "arrow_callout"][i % 8]}) for i in range(60)]
        shots[0]["start"] = 20 * 30
        pr = props(shots)
        pr["timeline"]["durationInFrames"] = 60 * 120
        qa = {"motion": {"share": 0.97}, "audio": {"lufs": -14.0, "lra": 3.8, "true_peak": -1.2}, "av_sync": {"max_offset_frames": 0.5, "ok": True}}
        card = scorecard.compute(pr, {"_wer_mean": 0.0}, qa, {"ok": True, "chosen": {"A": {"score": 0.8}}}, 10, cfg)
        self.assertTrue(card["ok"], scorecard.table(card))

    def test_fails_when_motion_low(self):
        cfg = load_cfg()
        pr = props([shot(i, i * 120, 120, "push", overlay={"name": "timer"}) for i in range(10)])
        pr["timeline"]["shots"][0]["start"] = 25 * 30
        qa = {"motion": {"share": 0.5}, "audio": {"lufs": -14.0, "lra": 3.8, "true_peak": -1.2}, "av_sync": {"max_offset_frames": 0.5, "ok": True}}
        card = scorecard.compute(pr, {"_wer_mean": 0.0}, qa, {"ok": True, "chosen": {"A": {"score": 0.8}}}, 10, cfg)
        self.assertFalse(card["ok"])


if __name__ == "__main__":
    unittest.main()

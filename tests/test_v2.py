"""v2 quality bar regression: pacing, framing/camera rules, captions, story engine gate, ending (no end card)."""
import json
import os
import random
import tempfile
import unittest
import wave

import numpy as np

from factory import assemble, beats, plan as planmod
from factory.validate import ROOT, load_cfg, validate_dir

PILOT = os.path.join(ROOT, "pilot", "solar-storm-blackout")


def fake_tts(plan, d):
    os.makedirs(d, exist_ok=True)
    meta = []
    for s in plan["sentences"]:
        n = int(s["words"] / 2.75 * 24000)
        x = np.random.default_rng(s["idx"]).normal(0, 0.1, n) * (0.5 + 0.5 * np.sin(np.arange(n) / 24000 * 26))
        with wave.open(os.path.join(d, s["id"] + ".wav"), "wb") as w:
            w.setnchannels(1), w.setsampwidth(2), w.setframerate(24000)
            w.writeframes((x * 32767).astype("<i2").tobytes())
        meta.append({"id": s["id"], "dur": n / 24000, "wer": 0.0, "ok": True})
    json.dump({"engine": "chatterbox", "sentences": meta}, open(os.path.join(d, "meta_0.json"), "w"))


class TestBeats(unittest.TestCase):
    def test_split_respects_hard_cap(self):
        pc = load_cfg()["pacing"]["beat"]
        for L in (4.0, 4.9, 6.2, 9.7, 14.0):
            parts = beats.split_beats(0.0, L, [(2.0, 1.0)], pc)
            self.assertAlmostEqual(parts[-1][1], L)
            self.assertTrue(all(b - a <= pc["hard_max_s"] + 1e-6 for a, b in parts), (L, parts))

    def test_no_repeat_framing_or_camera(self):
        rng = random.Random(1)
        prev, last, cam = None, [], None
        for i in range(200):
            f = beats.choose_framing(1, False, i % 3, prev, last, rng)
            c = beats.choose_camera(i % 3, f, 3.0, cam, rng)
            self.assertNotEqual(f, prev)
            self.assertNotEqual(c["preset"], cam)
            prev, cam, last = f, c["preset"], (last + [f])[-3:]

    def test_captions_two_lines_max_38(self):
        for ch in beats.caption_chunks("Mara used to work at the power company. Last winter, you carried her groceries, and she wrote your number on the warning list."):
            self.assertLessEqual(len(ch), 2)
            self.assertTrue(all(len(" ".join(ln)) <= 38 for ln in ch))


class TestStoryAndAssemble(unittest.TestCase):
    def test_pilot_script_passes_v2_gate(self):
        issues, _ = validate_dir(PILOT)
        self.assertEqual([str(i) for i in issues if i.level == "error"], [])

    def test_assembled_timeline_meets_pacing_and_ending(self):
        cfg = load_cfg()
        plan = planmod.build_plan(PILOT, cfg)
        with tempfile.TemporaryDirectory() as d:
            fake_tts(plan, os.path.join(d, "tts"))
            os.makedirs(os.path.join(d, "img"))
            json.dump(plan, open(os.path.join(d, "plan.json"), "w"))
            assemble.run(os.path.join(d, "plan.json"), os.path.join(d, "tts"), os.path.join(d, "img"), os.path.join(d, "out"), None)
            tl = json.load(open(os.path.join(d, "out", "props.json")))["timeline"]
            ap = json.load(open(os.path.join(d, "out", "audio_plan.json")))
        durs = [s["dur"] / 30.0 for s in tl["shots"]]
        self.assertLessEqual(max(durs), 5.04)
        self.assertTrue(2.4 <= sum(durs) / len(durs) <= 4.2, sum(durs) / len(durs))
        self.assertFalse(any(s["overlay"] and s["overlay"]["name"] == "end_screen" for s in tl["shots"]))
        self.assertGreaterEqual(tl["durationInFrames"] / 30.0 - ap["audio_end_s"], 7.5)
        self.assertEqual(sum(1 for a, b in zip(tl["shots"], tl["shots"][1:]) if a["framing"] == b["framing"]), 0)
        self.assertGreaterEqual(len(ap["silence"]), 3)
        self.assertTrue(max(tl["voiceEnv"]) > 0.5)
        self.assertEqual(tl["captions"] == [], not load_cfg().get("captions", {}).get("burned_in", True))
        ev = sorted(e["t"] for e in ap["sfx"])
        self.assertLessEqual(max(b - a for a, b in zip(ev, ev[1:])), 4.5)


if __name__ == "__main__":
    unittest.main()

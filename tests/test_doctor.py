"""P-012 Phase 1 acceptance: five deliberate defects are caught with the right code and (where automatic) fixed; the clean fixture passes.

All fixtures are generated here (short, 480p, synthetic): nothing large is committed.
Defects: (1) graphic over a face, (2) 3 s voice gap, (3) music 8 dB too loud, (4) music drops to silence, (5) black frame.
"""
import copy
import json
import os
import shutil
import subprocess
import tempfile
import unittest

import numpy as np
import soundfile as sf

from factory import miniyaml
from factory.doctor import audio as A
from factory.doctor import cert, fixes, fixtures, run, visual

TH = miniyaml.load_file(os.path.join(os.path.dirname(__file__), "..", "config", "doctor.yaml"))
SECONDS = 24
SR = fixtures.SR


def bad_codes(findings):
    return {f["code"] for f in findings if f["severity"] in ("BLOCKER", "MAJOR")}


def audio_findings(fx):
    plan = {"sentences": fx["plan"]["sentences"], "silence": fx["plan"]["silence"]}
    st = fx["stems"]
    _, f1 = A.check_master(fx["master"], TH)
    _, f2 = A.check_voice(st["voice"], plan, TH)
    _, f3 = A.check_music(st["voice"], st["music"], st["sfx"], st["amb"], plan, TH)
    return f1 + f2 + f3


def timeline(framing="medium", x=0.5, overlay="phone_alert"):
    return {"shots": [{"i": 0, "start": 0, "dur": 90, "framing": framing, "floorY": 0.9,
                       "chars": [{"id": "hero", "pose": "stand", "x": x, "params": {"headScale": 1.5}}],
                       "overlay": {"name": overlay, "args": ["A", "B"], "inFrame": 4, "outFrame": 80} if overlay else None,
                       "camera": {"z0": 1.0, "z1": 1.1, "fx": 0.5, "fy": 0.55}, "track": {}}]}


def make_asm(d, fx, tl):
    """Write the files the Doctor reads from an assembled directory, and a 480p mp4 carrying the fixture mix."""
    os.makedirs(d, exist_ok=True)
    for nm, x in fx["stems"].items():
        sf.write(os.path.join(d, f"stem_{nm}.wav"), np.clip(x, -1, 1).astype("float32"), SR, subtype="PCM_16")
    ap = {"total_s": fx["seconds"], "voice": [{"id": s["id"], "start": s["start"], "end": s["end"]} for s in fx["plan"]["sentences"]], "silence": fx["plan"]["silence"]}
    json.dump(ap, open(os.path.join(d, "audio_plan.json"), "w"))
    json.dump({"timeline": tl}, open(os.path.join(d, "props.json"), "w"))
    wav = os.path.join(d, "mix.wav")
    sf.write(wav, fx["master"].T.astype("float32"), SR, subtype="PCM_16")
    return wav


def encode(wav, mp4, black=None, seconds=SECONDS):
    vf = "null" if not black else f"drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:enable='between(t,{black[0]},{black[1]})'"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=s=854x480:r=30:d={seconds}", "-i", wav, "-vf", vf, "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", mp4], check=True)


class TestFixtures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fx = fixtures.clean(SECONDS, seed=3)
        cls.tmp = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    # ---- clean ---------------------------------------------------------------------------------------------------------
    def test_00_clean_audio_passes(self):
        self.assertEqual(bad_codes(audio_findings(self.fx)), set(), [f for f in audio_findings(self.fx)])

    def test_01_clean_visual_passes(self):
        self.assertEqual(visual.lint_timeline(timeline(overlay="timer", x=0.2), TH), [])

    def test_02_clean_end_to_end_certificate(self):
        d = os.path.join(self.tmp, "clean")
        wav = make_asm(d, self.fx, timeline(overlay="timer", x=0.2))
        mp4 = os.path.join(d, "clean.mp4")
        encode(wav, mp4)
        rep = run.cmd_final(mp4, d, os.path.join(d, "out"), TH, expect=(854, 480))
        self.assertIn(rep["status"], ("PASS", "FIXED"), rep["findings"])
        ok, why = cert.verify(mp4, os.path.join(d, "out", "CERTIFICATE.json"))
        self.assertTrue(ok, why)

    # ---- (1) graphic over a face ---------------------------------------------------------------------------------------------
    def test_10_graphic_over_face(self):
        tl = timeline()
        f = visual.lint_timeline(tl, TH)
        self.assertIn("V1-FACE-OVERLAP", {x["code"] for x in f})
        self.assertEqual(f[0]["severity"], "BLOCKER")
        fixed, left, log = visual.fix_timeline(tl, TH)
        self.assertEqual(left, [], log)
        self.assertEqual(visual.lint_timeline(fixed, TH), [])      # re-verified on the fixed scene data
        self.assertTrue(log)

    def test_11_graphic_over_face_blocks_certificate_when_unfixed(self):
        d = os.path.join(self.tmp, "face")
        wav = make_asm(d, self.fx, timeline())
        mp4 = os.path.join(d, "face.mp4")
        encode(wav, mp4)
        rep = run.cmd_final(mp4, d, os.path.join(d, "out"), TH, expect=(854, 480))
        self.assertEqual(rep["status"], "NEEDS_REVIEW")
        ok, _ = cert.verify(mp4, os.path.join(d, "out", "CERTIFICATE.json"))
        self.assertFalse(ok)

    # ---- (2) 3 s voice gap ---------------------------------------------------------------------------------------------------
    def test_20_voice_gap(self):
        fx = fixtures.mutate(self.fx, "voice_gap")
        f = audio_findings(fx)
        gaps = [x for x in f if x["code"] == "A1-GAP"]
        self.assertTrue(gaps, "3 s gap not detected")
        self.assertGreater(max(g["t1"] - g["t0"] for g in gaps), 2.5)
        st, pl, log = fixes.fix_stems(fx["stems"], fx["plan"], gaps, TH)
        fx2 = dict(fx, stems=st, plan=pl)
        fx2["master"] = np.vstack([sum(st.values()), sum(st.values())])
        self.assertNotIn("A1-GAP", {x["code"] for x in audio_findings(fx2)})

    # ---- (3) music +8 dB -----------------------------------------------------------------------------------------------------
    def test_30_music_too_loud(self):
        fx = fixtures.mutate(self.fx, "music_too_loud")
        f = audio_findings(fx)
        self.assertIn("A3-MUSIC-LOUD", bad_codes(f))
        st, pl, log = fixes.fix_stems(fx["stems"], fx["plan"], f, TH)
        fx2 = dict(fx, stems=st, plan=pl)
        fx2["master"] = np.vstack([sum(st.values()), sum(st.values())])
        self.assertNotIn("A3-MUSIC-LOUD", bad_codes(audio_findings(fx2)))

    # ---- (4) music drops to silence ------------------------------------------------------------------------------------------
    def test_40_music_dropout(self):
        fx = fixtures.mutate(self.fx, "music_drops_to_silence")
        f = audio_findings(fx)
        self.assertIn("A3-MUSIC-DROPOUT", {x["code"] for x in f})
        st, pl, log = fixes.fix_stems(fx["stems"], fx["plan"], f, TH)
        fx2 = dict(fx, stems=st, plan=pl)
        fx2["master"] = np.vstack([sum(st.values()), sum(st.values())])
        self.assertNotIn("A3-MUSIC-DROPOUT", {x["code"] for x in audio_findings(fx2)})

    # ---- (5) black frame -----------------------------------------------------------------------------------------------------
    def test_50_black_frame(self):
        d = os.path.join(self.tmp, "black")
        wav = make_asm(d, self.fx, timeline(overlay="timer", x=0.2))
        mp4 = os.path.join(d, "black.mp4")
        encode(wav, mp4, black=(10.0, 10.4))
        rep = run.cmd_final(mp4, d, os.path.join(d, "out"), TH, expect=(854, 480))
        # Phase 2: the black frame is repaired automatically (previous good frame held), the repaired file is re-scanned and certified as FIXED
        self.assertEqual(rep["status"], "FIXED", rep["findings"])
        self.assertNotIn("V4-BLACK", {x["code"] for x in rep["findings"]})
        self.assertTrue(cert.verify(mp4, os.path.join(d, "out", "CERTIFICATE.json"))[0])
        self.assertIn("black frames", open(os.path.join(d, "doctor", "FIX_LOG.md"), encoding="utf-8").read())


class TestFixLoopParams(unittest.TestCase):
    def test_loud_music_lowers_trim(self):
        p, log = fixes.adjust_mix_params({}, [{"code": "A3-MUSIC-LOUD"}], {"music_below_voice_db": 12.0}, TH)
        self.assertLess(p["music_trim_db"], 0)


if __name__ == "__main__":
    unittest.main()

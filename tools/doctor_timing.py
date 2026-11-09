"""Time the Video Doctor Stage 2 audio scan on a synthetic 4-minute mix (numbers only, nothing committed)."""
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from factory import miniyaml  # noqa: E402
from factory.doctor import audio as A
from factory.doctor import fixtures

th = miniyaml.load_file("config/doctor.yaml")
fx = fixtures.clean(240.0, seed=5)
t0 = time.time()
plan = {"sentences": fx["plan"]["sentences"], "silence": fx["plan"]["silence"]}
st = fx["stems"]
A.check_master(fx["master"], th)
A.check_voice(st["voice"], plan, th)
A.check_music(st["voice"], st["music"], st["sfx"], st["amb"], plan, th)
dt = time.time() - t0
print(f"STAGE 2 AUDIO SCAN: {dt:.1f} s for 240 s of audio (target <= 60 s)")
raise SystemExit(0 if dt <= 60 else 1)

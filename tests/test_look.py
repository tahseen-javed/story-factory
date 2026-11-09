"""Phase 2 stage 3: blotch / banding / style checks on synthetic backgrounds, with the soft-grade repair."""
import os
import shutil
import tempfile
import unittest

import numpy as np
from PIL import Image

from factory import miniyaml
from factory.doctor import look

TH = miniyaml.load_file(os.path.join(os.path.dirname(__file__), "..", "config", "doctor.yaml"))
W, H = 640, 360


def textured(seed=1):
    """A clean outlined cut-out style background: smooth walls with ink outlines and small texture."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:H, 0:W]
    base = np.stack([150 + 30 * np.sin(x / 90.0), 120 + 25 * np.cos(y / 70.0), 100 + 20 * np.sin((x + y) / 120.0)], axis=-1)
    img = base + rng.normal(0, 3.0, base.shape)
    for gx in range(0, W, 80):
        img[:, gx:gx + 3] = 30
    for gy in range(0, H, 90):
        img[gy:gy + 3, :] = 30
    return np.clip(img, 0, 255).astype(np.uint8)


def banded():
    x = np.linspace(0, 1, W)[None, :].repeat(H, 0)
    v = np.floor(x * 14) + 90          # 14 coarse steps over 640 px = 45 px plateaus one visible level apart
    return np.stack([v, v * 0.9, v * 0.8], axis=-1).astype(np.uint8)


def blotchy():
    img = textured(2).astype(np.int16)
    img[60:200, 100:260] = (img[60:200, 100:260] * 0.1 + np.array([40, 230, 60]) * 0.9)
    img[200:330, 380:560] = (img[200:330, 380:560] * 0.1 + np.array([230, 40, 200]) * 0.9)
    return np.clip(img, 0, 255).astype(np.uint8)


class TestLook(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp()
        for name, arr in (("clean1.night", textured(1)), ("clean2.day", textured(3)), ("clean3.dusk", textured(4)), ("blotchy.night", blotchy()), ("banded.night", banded())):
            os.makedirs(os.path.join(cls.d, "bg"), exist_ok=True)
            Image.fromarray(arr).save(os.path.join(cls.d, "bg", name + ".jpg"), quality=95)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, ignore_errors=True)

    def test_clean_images_pass(self):
        for n in ("clean1.night", "clean2.day"):
            m = look.metrics(look.load_rgb(os.path.join(self.d, "bg", n + ".jpg")))
            f, _ = look.check_images({n: m}, TH)
            self.assertEqual([x["code"] for x in f], [], (n, m))

    def test_blotch_detected_and_repaired(self):
        p = os.path.join(self.d, "bg", "blotchy.night.jpg")
        m = look.metrics(look.load_rgb(p))
        f, _ = look.check_images({"blotchy.night.jpg": m}, TH)
        self.assertIn("V3-BLOTCH", [x["code"] for x in f], m)
        look.repair(p, m, TH)
        m2 = look.metrics(look.load_rgb(p))
        self.assertLess(m2["blotch"], m["blotch"])

    def test_banding_detected(self):
        m = look.metrics(look.load_rgb(os.path.join(self.d, "bg", "banded.night.jpg")))
        f, _ = look.check_images({"banded.night.jpg": m}, TH)
        self.assertIn("V3-BANDING", [x["code"] for x in f], m)


if __name__ == "__main__":
    unittest.main()

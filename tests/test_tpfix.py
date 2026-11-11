"""P-017: the AAC true-peak overshoot of 007 (run 43000967103) is parsed and handled after the encode."""
import unittest

from factory import tpfix

SAMPLE = """
  Integrated loudness:
    I:         -14.4 LUFS
  True peak:
    Peak:       -0.6 dBFS
"""


class TestTpfix(unittest.TestCase):
    def test_parse_peak(self):
        self.assertEqual(tpfix.parse_peak(SAMPLE), -0.6)
        self.assertIsNone(tpfix.parse_peak("nothing here"))


if __name__ == "__main__":
    unittest.main()

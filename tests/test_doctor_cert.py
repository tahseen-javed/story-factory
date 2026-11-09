"""P-012 anti-bypass: no certificate, modified mp4 and stale certificate are all refused; a matching certificate is accepted."""
import json
import os
import shutil
import tempfile
import unittest

from factory.doctor import VERSION, cert


class TestCertificate(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.mp4 = os.path.join(self.d, "v.mp4")
        open(self.mp4, "wb").write(os.urandom(5000))
        self.cert = cert.write(self.mp4, self.d, "PASS", {"findings": [], "checks": {"A1": "PASS"}})

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_valid_certificate_is_accepted(self):
        self.assertTrue(cert.verify(self.mp4, self.cert)[0])

    def test_no_certificate_is_refused(self):
        self.assertFalse(cert.verify(self.mp4, "")[0])
        self.assertFalse(cert.verify(self.mp4, os.path.join(self.d, "missing.json"))[0])

    def test_modified_mp4_is_refused(self):
        open(self.mp4, "ab").write(b"x")
        ok, why = cert.verify(self.mp4, self.cert)
        self.assertFalse(ok)
        open(self.mp4, "r+b").write(b"Y")            # same size, different bytes
        self.assertFalse(cert.verify(self.mp4, self.cert)[0])

    def test_stale_certificate_is_refused(self):
        c = json.load(open(self.cert))
        c["doctor_version"] = "0.0.1"
        json.dump(c, open(self.cert, "w"))
        ok, why = cert.verify(self.mp4, self.cert)
        self.assertFalse(ok)
        self.assertIn("stale", why)
        # a certificate that belongs to another file is stale for this one too
        other = os.path.join(self.d, "o.mp4")
        open(other, "wb").write(os.urandom(5000))
        good = cert.write(other, self.d, "PASS", {"findings": []})
        self.assertFalse(cert.verify(self.mp4, good)[0])

    def test_needs_review_or_defects_never_verify(self):
        bad = cert.write(self.mp4, self.d, "NEEDS_REVIEW", {"findings": []})
        self.assertFalse(cert.verify(self.mp4, bad)[0])
        bad2 = cert.write(self.mp4, self.d, "PASS", {"findings": [{"severity": "MAJOR"}]})
        self.assertFalse(cert.verify(self.mp4, bad2)[0])

    def test_cli_exit_codes(self):
        self.assertEqual(cert.main(["verify", self.mp4, self.cert]), 0)
        self.assertEqual(cert.main(["verify", self.mp4, ""]), 1)


if __name__ == "__main__":
    unittest.main()

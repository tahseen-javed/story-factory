import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from factory import miniyaml, vocab
from factory.parse import ScriptError, parse, parse_call, parse_camera, split_fields
from factory.textutil import count_numbers, count_words, safe_short_title, split_sentences
from factory.validate import load_cfg, validate_dir, validate_script


class TestMiniYaml(unittest.TestCase):
    def test_nested_and_lists(self):
        d = miniyaml.load("a:\n  b: 1\n  c: [x, y]\n  d: 'q'\nlist:\n  - one\n  - two: 2\n    three: 3\nflag: true\n")
        self.assertEqual(d["a"]["b"], 1)
        self.assertEqual(d["a"]["c"], ["x", "y"])
        self.assertEqual(d["list"][0], "one")
        self.assertEqual(d["list"][1], {"two": 2, "three": 3})
        self.assertTrue(d["flag"])

    def test_factory_yaml_loads(self):
        cfg = load_cfg()
        self.assertEqual(cfg["output"]["width"], 1920)
        self.assertEqual(cfg["tts"]["engine_order"][0], "chatterbox_turbo")
        self.assertTrue(cfg["delivery"]["age_recipient"].startswith("age1"))


class TestParse(unittest.TestCase):
    def test_split_fields_respects_quotes(self):
        parts = split_fields(' bedroom.night | ov:x("a | b", 2) | cam:push 1.0>1.1')
        self.assertEqual(len(parts), 3)

    def test_call(self):
        self.assertEqual(parse_call('phone_alert("A","B c")'), ("phone_alert", ["A", "B c"]))
        self.assertEqual(parse_call("timer"), ("timer", []))

    def test_camera(self):
        c = parse_camera("push 1.00>1.15")
        self.assertEqual((c.preset, c.z0, c.z1), ("push", 1.0, 1.15))
        self.assertEqual(parse_camera("hold").preset, "hold")

    def test_sentences(self):
        self.assertEqual(len(split_sentences("One. Two! Three? Dr. Smith waits.")), 4)
        self.assertGreaterEqual(count_numbers("At 3 am, fifteen hours, 4 days"), 3)
        self.assertEqual(safe_short_title("The Last Solar Storm Blackout!"), "Last Solar Storm")

    def test_bad_chapter(self):
        with self.assertRaises(ScriptError):
            parse("TITLE: x\n\n## CH1 FRIDAY\n")


class TestValidate(unittest.TestCase):
    def test_pilot_passes(self):
        issues, sc = validate_dir(os.path.join(ROOT, "pilot", "solar-storm-blackout"))
        errs = [str(i) for i in issues if i.level == "error"]
        self.assertEqual(errs, [])
        self.assertGreater(sc.words, 640)

    def test_unknown_vocabulary_is_rejected_with_suggestion(self):
        text = (
            "TITLE: T\nLENGTH_MIN: 4\nVOICE: default\nCHARACTERS:\n- hero = rig_hero()\nLOCATIONS:\n- room: a room\n\n"
            "## CH1 | NOW\n@ room.night | hero:stnad/scared | cam:pussh 1.0>1.1 | fx:smoke\nHello there you.\n"
        )
        sc = parse(text)
        issues = validate_script(sc, text, load_cfg(), {}, "pilot")
        msgs = " ".join(str(i) for i in issues)
        self.assertIn("pose 'stnad'", msgs)
        self.assertIn("stand", msgs)
        self.assertIn("cam 'pussh'", msgs)

    def test_denylist_blocks_brand_in_location(self):
        text = (
            "TITLE: T\nLENGTH_MIN: 4\nCHARACTERS:\n- hero = rig_hero()\nLOCATIONS:\n- room: a room painted like a pixar movie\n\n"
            "## CH1 | NOW\n@ room.night | hero:stand/scared\nOne two three.\n"
        )
        issues = validate_script(parse(text), text, load_cfg(), {}, "pilot")
        self.assertTrue(any(i.code == "denylist" for i in issues))

    def test_vocab_sizes_match_spec(self):
        self.assertGreaterEqual(len(vocab.POSES), 12)
        self.assertGreaterEqual(len(vocab.EXPRESSIONS), 10)
        self.assertGreaterEqual(len(vocab.OVERLAYS), 19)


if __name__ == "__main__":
    unittest.main()

"""Tests for the structural STE linter.

Run with:  python3 -m unittest tests.test_linters
"""
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LINTER = os.path.join(ROOT, "skills", "ste100", "scripts", "ste-lint.py")
PY = sys.executable


def run(args, stdin=None):
    return subprocess.run(
        [PY, LINTER] + args, input=stdin, capture_output=True, text=True
    )


class Selftest(unittest.TestCase):
    def test_selftest_exits_zero(self):
        r = run(["--selftest"])
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)


class RuleFires(unittest.TestCase):
    def test_semicolon(self):
        r = run([], stdin="Do A. Do B; do C.")
        self.assertIn("semicolon", r.stdout)

    def test_phrasal_verb(self):
        r = run([], stdin="The system will spin up after the test.")
        self.assertIn("phrasal-verb", r.stdout)

    def test_marketing_adjective(self):
        r = run([], stdin="This is a seamless integration.")
        self.assertIn("marketing-adjective", r.stdout)

    def test_nominalization(self):
        r = run([], stdin="Perform an analysis of the data.")
        self.assertIn("nominalization", r.stdout)

    def test_passive_voice(self):
        r = run([], stdin="The valve was closed by the operator.")
        self.assertIn("passive-voice", r.stdout)

    def test_present_perfect(self):
        r = run([], stdin="The team has verified the fix.")
        self.assertIn("present-perfect", r.stdout)

    def test_long_sentence(self):
        r = run([], stdin=" ".join(["word"] * 30))
        self.assertIn("long-sentence", r.stdout)

    def test_synonym_rotation(self):
        r = run([], stdin="Use verify to check the value.")
        self.assertIn("synonym-rotation", r.stdout)

    def test_dangling_conjunction(self):
        r = run([], stdin="- Open the valve\n- Check pressure\n- And")
        self.assertIn("dangling-conjunction", r.stdout)


class CleanAndHedges(unittest.TestCase):
    def test_clean_text_clean(self):
        r = run([], stdin="Open the valve. Check the pressure.")
        self.assertNotIn("semicolon", r.stdout)
        self.assertNotIn("passive-voice", r.stdout)

    def test_hedges_never_flagged(self):
        text = (
            "You may have missed a step. The data could be wrong. "
            "Might this be the cause? It should have stopped. "
            "The engine may have failed. They would have seen the warning."
        )
        r = run([], stdin=text)
        self.assertNotIn("passive-voice", r.stdout)
        self.assertNotIn("present-perfect", r.stdout)


class BaselineAndDisable(unittest.TestCase):
    def test_baseline_passes_under_limit(self):
        r = run(["--baseline", "100"], stdin="Do A. Do B; do C.")
        self.assertEqual(r.returncode, 0)

    def test_baseline_fails_over_limit(self):
        r = run(["--baseline", "0"], stdin="Do A. Do B; do C.")
        self.assertEqual(r.returncode, 1)

    def test_disable_silences_rule(self):
        r = run(["--disable", "semicolon"], stdin="Do A. Do B; do C.")
        self.assertEqual(r.returncode, 0)
        self.assertNotIn("semicolon", r.stdout)

    def test_json_output(self):
        r = run(["--json"], stdin="Do A. Do B; do C.")
        self.assertIn('"violations"', r.stdout)
        self.assertIn('"hard_count"', r.stdout)


if __name__ == "__main__":
    unittest.main()

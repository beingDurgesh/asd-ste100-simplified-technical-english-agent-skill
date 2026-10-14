# pylint: disable=missing-function-docstring,missing-class-docstring

"""Tests for the plugin hooks.

Run with:  python skills/ste100/hooks/test_lint_hook.py
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HOOK = os.path.join(HERE, "lint_hook.py")
ACTIVATE = os.path.join(HERE, "ste100-activate.js")
PY = sys.executable


def run_hook(event_dict, cwd=ROOT):
    return subprocess.run(
        [PY, HOOK],
        input=json.dumps(event_dict),
        capture_output=True, text=True, cwd=cwd,
    )


class ActivateHook(unittest.TestCase):
    def test_writes_rules(self):
        r = subprocess.run(
            ["node", ACTIVATE],
            capture_output=True, text=True, cwd=ROOT,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("ASD-STE100 SKILL ACTIVE AUTOMATICALLY", r.stdout)
        self.assertIn("short sentences", r.stdout.lower())
        self.assertIn("skills/ste100/SKILL.md", r.stdout)

    def test_fallback_constant_exists(self):
        # The hook resolves prompts/system-prompt.md relative to its own
        # location (__dirname), not the cwd, so the fallback is reachable
        # only when the file is missing or the install is broken. Verify
        # the fallback text is what we ship.
        with open(os.path.join(HERE, "ste100-activate.js")) as f:
            src = f.read()
        self.assertIn("FALLBACK_CONTEXT", src)
        self.assertIn("ASD-STE100 SKILL ACTIVE AUTOMATICALLY", src)


class PostToolUse(unittest.TestCase):
    def test_clean_md_is_silent(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "clean.md")
            with open(p, "w") as f:
                f.write("Open the valve. Check the pressure.\n")
            r = run_hook({
                "hook_event_name": "PostToolUse",
                "tool_name": "Write",
                "tool_input": {"file_path": p},
            }, cwd=tmp)
            self.assertEqual(r.returncode, 0)
            self.assertEqual(r.stdout, "")
            self.assertEqual(r.stderr, "")

    def test_violation_md_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "bad.md")
            with open(p, "w") as f:
                f.write("This is a seamless integration; do A and do B.\n")
            r = run_hook({
                "hook_event_name": "PostToolUse",
                "tool_name": "Write",
                "tool_input": {"file_path": p},
            }, cwd=tmp)
            self.assertEqual(r.returncode, 2)
            self.assertIn("asd-ste100", r.stderr)
            self.assertIn("violation", r.stderr.lower())

    def test_non_md_is_silent(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "notes.txt")
            with open(p, "w") as f:
                f.write("This is a seamless integration.\n")
            r = run_hook({
                "hook_event_name": "PostToolUse",
                "tool_name": "Write",
                "tool_input": {"file_path": p},
            }, cwd=tmp)
            self.assertEqual(r.returncode, 0)
            self.assertEqual(r.stderr, "")

    def test_skip_claude_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = os.path.join(tmp, ".claude")
            os.makedirs(d)
            p = os.path.join(d, "MEMORY.md")
            with open(p, "w") as f:
                f.write("This is a seamless integration.\n")
            r = run_hook({
                "hook_event_name": "PostToolUse",
                "tool_name": "Write",
                "tool_input": {"file_path": p},
            }, cwd=tmp)
            self.assertEqual(r.returncode, 0)
            self.assertEqual(r.stderr, "")


class StopCheck(unittest.TestCase):
    def test_clean_reply_is_silent(self):
        r = run_hook({
            "hook_event_name": "Stop",
            "last_assistant_message": "Open the valve. Check the pressure.",
        })
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout, "")

    def test_em_dash_warns(self):
        r = run_hook({
            "hook_event_name": "Stop",
            "last_assistant_message": "It works—no further action is needed.",
        })
        self.assertEqual(r.returncode, 0)
        self.assertIn("systemMessage", r.stdout)
        self.assertIn("em-dash", r.stdout)

    def test_bold_warns(self):
        r = run_hook({
            "hook_event_name": "Stop",
            "last_assistant_message": "**This is the answer.**",
        })
        self.assertEqual(r.returncode, 0)
        self.assertIn("bold span", r.stdout)

    def test_header_warns(self):
        r = run_hook({
            "hook_event_name": "Stop",
            "last_assistant_message": "## Title\n\nThe answer.",
        })
        self.assertEqual(r.returncode, 0)
        self.assertIn("header", r.stdout)

    def test_filler_opener_warns(self):
        r = run_hook({
            "hook_event_name": "Stop",
            "last_assistant_message": "Great question. Open the valve.",
        })
        self.assertEqual(r.returncode, 0)
        self.assertIn("filler opener", r.stdout)

    def test_filler_closer_warns(self):
        r = run_hook({
            "hook_event_name": "Stop",
            "last_assistant_message": "Open the valve. Hope this helps.",
        })
        self.assertEqual(r.returncode, 0)
        self.assertIn("filler closer", r.stdout)


if __name__ == "__main__":
    unittest.main()

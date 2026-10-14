"""Eval harness: run the STE linter over a directory of text files.

Usage:
    python3 skills/ste100/evals/ste_lint.py PATH [--json] [--baseline N] [--disable x,y]
"""
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
LINTER = os.path.join(ROOT, "..", "scripts", "ste-lint.py")


def main():
    """Run the STE lint eval and print the result."""
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--baseline", type=int, default=0)
    ap.add_argument("--disable", default="")
    args = ap.parse_args()

    files = []
    for dirpath, _dirs, names in os.walk(args.path):
        for name in names:
            if name.endswith((".md", ".txt")):
                files.append(os.path.join(dirpath, name))

    cmd = [sys.executable, LINTER]
    if args.json:
        cmd.append("--json")
    cmd += ["--baseline", str(args.baseline)]
    if args.disable:
        cmd += ["--disable", args.disable]
    cmd += files

    r = subprocess.run(cmd, capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())

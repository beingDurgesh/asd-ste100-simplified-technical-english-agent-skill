"""Eval: check that numeric style in STE text is plain.

STE wants digits for measurements and counts, spelled-out numbers only for
one through ten when no unit is present. This eval walks a directory and
reports any spelled-out number in a measurement context.
"""
import argparse
import os
import re
import sys

SPelled = re.compile(
    r"\b(one|two|three|four|five|six|seven|eight|nine|ten)\b"
    r"(?:\s*(?:kg|g|mm|cm|km|ml|l|v|a|w|hz|deg|sec|min|hr|in|ft|m))\b",
    re.I,
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    args = ap.parse_args()
    hits = 0
    for dirpath, _dirs, names in os.walk(args.path):
        for name in names:
            if not name.endswith((".md", ".txt")):
                continue
            with open(os.path.join(dirpath, name), encoding="utf-8") as fh:
                for i, line in enumerate(fh, 1):
                    for m in SPelled.finditer(line):
                        print(f"{name}:{i}: {m.group(0)}")
                        hits += 1
    print(f"{hits} spelled-out measurement numbers")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())

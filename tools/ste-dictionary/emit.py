#!/usr/bin/env python3
"""Emit approved.txt and not-approved.tsv from dict.json.

Usage:
    python3 parse_dict.py ste9.txt
    python3 emit.py .

Writes:
    approved.txt       one approved word per line
    not-approved.tsv   TSV: word<TAB>alternatives<TAB>part-of-speech

The approved list is lowercase and sorted. The not-approved list is
sorted by word and includes the approved alternatives from the
dictionary, so a linter can suggest a replacement.
"""
import json
import sys
from pathlib import Path


def emit(dict_path, out_dir):
    with open(dict_path, encoding="utf-8") as fh:
        data = json.load(fh)

    approved = sorted({e["word"] for e in data["approved"]})
    with open(f"{out_dir}/approved.txt", "w", encoding="utf-8") as fh:
        fh.write("\n".join(approved) + "\n")

    rows = []
    for e in data["not_approved"]:
        alts = "; ".join(e.get("alternatives", []))
        rows.append((e["word"], alts, e["pos"]))
    rows.sort()
    with open(f"{out_dir}/not-approved.tsv", "w", encoding="utf-8") as fh:
        fh.write("word\talternatives\tpart-of-speech\n")
        for word, alts, pos in rows:
            fh.write(f"{word}\t{alts}\t{pos}\n")

    print(f"wrote {out_dir}/approved.txt ({len(approved)} words)")
    print(f"wrote {out_dir}/not-approved.tsv ({len(rows)} rows)")


def _find_dict():
    """Locate dict.json: CWD first, then this script's directory."""
    for base in (Path.cwd(), Path(__file__).resolve().parent):
        candidate = base / "dict.json"
        if candidate.is_file():
            return candidate
    return Path("dict.json")


def main():
    if len(sys.argv) == 2:
        out_dir = sys.argv[1]
    else:
        # Default: write next to dict.json.
        out_dir = str(_find_dict().resolve().parent)
    dict_path = str(_find_dict())
    emit(dict_path, out_dir)


if __name__ == "__main__":
    main()

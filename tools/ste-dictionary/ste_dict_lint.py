#!/usr/bin/env python3
"""Dictionary-backed word-choice linter for ASD-STE100.

Usage:
    python3 ste_dict_lint.py file.md
    python3 ste_dict_lint.py --self-test

Reads not-approved.tsv (from emit.py) and reports every word that the
standard does not approve, with the approved alternatives. Also counts
the LLM-tell words from skills/ste100/slop.tsv as a separate number.

Known limit: the match is on the base form and simple inflections, with
no part-of-speech disambiguation. Numbers from this tool compare two
texts run through the same version. They are not a compliance verdict.
"""
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DICT_CANDIDATES = [
    ROOT / "tools" / "ste-dictionary" / "not-approved.tsv",
    Path("not-approved.tsv"),
    Path(__file__).resolve().parent / "not-approved.tsv",
]
SLOP_CANDIDATES = [
    ROOT / "skills" / "ste100" / "slop.tsv",
    ROOT / "evals" / "slop.tsv",
]
SLOP = next((p for p in SLOP_CANDIDATES if p.is_file()), SLOP_CANDIDATES[0])

# Simple inflection rules applied before lookup.
INFLECTIONS = [
    (re.compile(r"ies$"), "y"),
    (re.compile(r"es$"), ""),
    (re.compile(r"ied$"), "y"),
    (re.compile(r"ing$"), ""),
    (re.compile(r"ed$"), ""),
    (re.compile(r"ness$"), ""),
    (re.compile(r"ment$"), ""),
    (re.compile(r"ly$"), ""),
    (re.compile(r"er$"), ""),
    (re.compile(r"est$"), ""),
    (re.compile(r"s$"), ""),
]


def _load(path):
    words = {}
    with open(path, encoding="utf-8") as fh:
        next(fh)  # header
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2:
                continue
            word, alts = parts[0], parts[1]
            words[word] = alts
    return words


def _base_form(word):
    word = word.lower()
    if word in _NOT_APPROVED:
        return word
    for pat, repl in INFLECTIONS:
        if not pat.search(word):
            continue
        cand = pat.sub(repl, word)
        if cand in _NOT_APPROVED:
            return cand
        # Try re-adding a silent "e" (manufactured -> manufacture).
        if pat.pattern == r"ed$" and cand + "e" in _NOT_APPROVED:
            return cand + "e"
    return None


def lint(text):
    """Return (findings, slop_count)."""
    findings = []
    slop_count = 0
    seen = set()
    for tok in re.findall(r"[A-Za-z][A-Za-z\-']*", text):
        base = _base_form(tok)
        if base and base not in seen:
            seen.add(base)
            findings.append((tok, base, _NOT_APPROVED[base]))
    for tok in re.findall(r"[A-Za-z][A-Za-z\-']*", text):
        if tok.lower() in _SLOP:
            slop_count += 1
    return findings, slop_count


def _run(path):
    text = Path(path).read_text(encoding="utf-8")
    findings, slop = lint(text)
    print(f"file: {path}")
    print(f"not-approved words: {len(findings)}")
    print(f"slop words: {slop}")
    for tok, base, alts in findings:
        print(f"  {tok} -> {alts or 'no alternative listed'}")


def _self_test():
    sample = (
        "The unit must be manufactured. Do not damage the fit. "
        "We should utilize the lever to facilitate the procedure."
    )
    findings, slop = lint(sample)
    # _base_form returns the dictionary headword (manufactured -> manufacture).
    expected = {"manufacture", "damage", "fit", "should", "utilize",
                "facilitate"}
    found = {base for _, base, _ in findings}
    assert found == expected, f"expected {expected}, got {found}"
    assert slop == 2, f"expected 2 slop words, got {slop}"
    print("self-test: PASS")
    print(f"  not-approved: {len(findings)}")
    print(f"  slop: {slop}")


DICT = next((p for p in DICT_CANDIDATES if p.is_file()), DICT_CANDIDATES[0])
_NOT_APPROVED = _load(DICT)
_SLOP = {
    line.split("\t")[0].lower()
    for line in Path(SLOP).read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.startswith("slop")
}

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        _self_test()
    elif len(sys.argv) == 2:
        _run(sys.argv[1])
    else:
        sys.exit(__doc__)

#!/usr/bin/env python3
"""Parse ASD-STE100 Issue 9 dictionary text into dict.json.

Usage:
    pdftotext -layout -enc UTF-8 ASD-STE100_ISSUE9.pdf ste9.txt
    python3 parse_dict.py ste9.txt

Writes dict.json with two lists:
  approved:     [{word, pos, meaning}]
  not_approved: [{word, pos, alternatives: [..]}]

How entries are recognised
-------------------------
The layout text (pdftotext -layout) preserves column positions. The
dictionary header gives the column boundaries:

    Word              Approved meaning/     STE EXAMPLE          Non-STE example
    0                 18                     40                   61

Column 2 ([18:40]) tells us the entry type:
  * approved words   -> column 2 begins with lowercase text (the meaning)
  * not-approved     -> column 2 begins with UPPERCASE alternatives

This is exactly how the standard distinguishes them (page 2-0-9: "A word in
lowercase letters is not approved in STE").

Inflected forms (ACCEPTS, ACCEPTED,) appear in column 1 with an empty
column 2; they inherit the approval status of the preceding headword.

The dictionary table is followed by prose ("How to select words
correctly", "List of recurring errors", "List of approved verbs"). We
stop at those sections. Page markers inside the table flush the current
entry but do not stop parsing; each new "Word (part of speech)" header
begins a fresh block.
"""
import json
import re
from pathlib import Path
import sys

POS = r"(?:n|v|adj|adv|art|prep|conj|pron|det)"
ENTRY_RE = re.compile(rf"^([a-zA-Z][a-zA-Z\-]*)\s*\(({POS})\)")
INFLECT_RE = re.compile(rf"^([a-zA-Z][a-zA-Z\-]*)\s*\(({POS})\),?\s*$")
COL_WORD = slice(0, 18)
COL_MEANING = slice(18, 40)
END_MARKERS = (
    "How to select words correctly",
    "List of recurring errors",
    "List of approved verbs",
)


def parse(path):
    """Read the dictionary file and return its entries."""
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()

    # Locate every "Word (part of speech)" header line that belongs to the
    # dictionary proper (Part 2). Part 1 revision notes also use the header
    # but their second line is not "ALTERNATIVES".
    headers = [
        i for i, line in enumerate(lines)
        if line.startswith("Word") and i + 1 < len(lines)
        and "(part of speech)" in lines[i + 1]
        and "ALTERNATIVES" in lines[i + 1]
    ]
    # Restrict to Part 2 - Dictionary. Everything before the first
    # "Part 2 - Dictionary" page marker is Part 1 revision notes.
    part2_start = next(
        (i for i, line in enumerate(lines)
         if "Part 2 - Dictionary" in line),
        0,
    )
    headers = [h for h in headers if h >= part2_start]
    if not headers:
        sys.exit("could not find dictionary header")

    approved = []
    not_approved = []

    for idx, h in enumerate(headers):
        nxt = headers[idx + 1] if idx + 1 < len(headers) else len(lines)
        current = None
        pending_inflected = []

        for line in lines[h + 2:nxt]:
            if line.strip().startswith(END_MARKERS):
                break
            if line.startswith("Page ") or line.startswith("Issue 9") \
               or line.startswith("Part 2 - Dictionary"):
                _flush(current, pending_inflected, approved, not_approved)
                current = None
                pending_inflected = []
                continue

            word_col = line[COL_WORD].strip()
            m = ENTRY_RE.match(word_col)
            if m:
                _flush(current, pending_inflected, approved, not_approved)
                current = {
                    "word": m.group(1),
                    "pos": m.group(2),
                    "col2": line[COL_MEANING].strip(),
                }
                pending_inflected = []
                continue

            # Inflected form in column 1, e.g. "ACCEPTS," or "ACCEPTED,".
            im = INFLECT_RE.match(word_col)
            if im and current is not None:
                pending_inflected.append({
                    "word": im.group(1).lower(),
                    "pos": im.group(2),
                })
                continue

            if current is not None:
                seg = line[COL_MEANING].strip()
                if seg:
                    current["col2"] += " " + seg

        _flush(current, pending_inflected, approved, not_approved)

    return _dedupe({"approved": approved, "not_approved": not_approved})


def _flush(current, inflected, approved, not_approved):
    if current is None:
        return
    col2 = current["col2"].strip()
    # The standard says the WORD column case determines approval:
    #   UPPERCASE word -> approved
    #   lowercase word -> not-approved
    # Column 2 confirms this (lowercase meaning = approved,
    # UPPERCASE alternatives = not-approved) but is not authoritative.
    if current["word"].isupper():
        meaning = _extract_meaning(col2)
        entry = {"word": current["word"], "pos": current["pos"],
                 "meaning": meaning}
        approved.append(entry)
        for inf in inflected:
            approved.append({"word": inf["word"], "pos": inf["pos"],
                             "meaning": meaning})
    else:
        alts = _extract_alternatives(col2)
        entry = {"word": current["word"], "pos": current["pos"],
                 "alternatives": alts}
        not_approved.append(entry)
        for inf in inflected:
            not_approved.append({"word": inf["word"], "pos": inf["pos"],
                                 "alternatives": alts})


def _dedupe(data):
    """Remove duplicate (word, pos) entries, keeping the richer one."""
    for key in ("approved", "not_approved"):
        seen = {}
        for e in data[key]:
            k = (e["word"], e["pos"])
            if k not in seen:
                seen[k] = e
            else:
                if len(json.dumps(e)) > len(json.dumps(seen[k])):
                    seen[k] = e
        data[key] = list(seen.values())
    return data


def _extract_meaning(text):
    """Approved meaning: lowercase tokens only (excludes STE example col)."""
    tokens = re.findall(r"[a-z][a-z'\-]*(?:\s*\([a-z]{2,4}\))?", text)
    return " ".join(tokens).strip()


def _extract_alternatives(text):
    """Not-approved alternatives: UPPERCASE tokens only.

    Each alternative is a run of uppercase words such as "KEEP (v)",
    "HOLD (v)", "MAINTENANCE (n)", "AT THE SAME TIME", "MAKE SURE (v)".
    The match stops at the first lowercase letter, which marks the start
    of the STE example column.
    """
    # Trim at the first lowercase letter to drop the STE example column.
    cut = len(text)
    for i, ch in enumerate(text):
        if ch.islower():
            cut = i
            break
    text = text[:cut]
    alts = re.findall(
        r"(?:[A-Z][A-Z'\-]*(?:\s*\([A-Z]{2,4}\)|\s*\((?:v|n|adj|adv|prep|conj|pron|det|TN|TV)\))?)+",
        text,
    )
    cleaned = []
    for a in alts:
        a = a.strip()
        if len(a) > 1 and a not in cleaned:
            cleaned.append(a)
    return cleaned


def main():
    """Parse the dictionary and save the result."""
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    data = parse(sys.argv[1])
    out = Path(__file__).resolve().parent / "dict.json"
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    print(f"approved: {len(data['approved'])}")
    print(f"not_approved: {len(data['not_approved'])}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
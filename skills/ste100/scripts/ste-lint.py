#!/usr/bin/env python3
"""Deterministic linter for the structural STE rules in SKILL.md.

Checks only rules verifiable without ASD's dictionary. Deliberately never
flags hedges or modality (may/might/could): the skill treats confidence as
content, and a linter that pressures hedges out would rewrite claims.

Usage:
    ste-lint.py FILE [FILE ...]
    echo "text" | ste-lint.py [--json]
    ste-lint.py --baseline 5 FILE      # pass unless hard violations exceed 5
    ste-lint.py --disable passive-voice,present-perfect FILE
    ste-lint.py --selftest
    ste-lint.py --dict FILE             # also flag non-approved words, if
                                        # not-approved.tsv is present

Exit 1 when hard ("advisory-free") violations exceed the baseline (default 0).
Advisory findings (passive voice, compound tenses) never fail the run.
"""
import json
import re
import sys
from pathlib import Path

# ponytail: regex heuristics, not a parser. No noun-cluster rule — needs POS
# tagging to avoid constant false positives; add spaCy-backed rule if ever needed.
# No ellipsis rule by owner's choice: technical writing sometimes earns one.
# Irregular past participles used by the present-perfect heuristic.
IRREGULAR_PARTICIPLES = "given|taken|made|done|found|seen|known|shown|written|built|sent|set|run|read|kept|held|left|put|cut|hit|let|shut|split|spread|begun|become|come|gone|got|gotten|lost|met|paid|said|sold|told|thought|brought|bought|caught|taught|won|worn|torn|born|drawn|grown|thrown|flown|driven|risen|chosen|broken|spoken|frozen|hidden|ridden|forgotten|fallen|eaten|beaten|understood|stood|struck|stuck|swung|hung|led|fed|bled|fled|sped|bound|wound|dug|spun|slid|bit|lit|quit"

# Words that break a noun cluster: articles, prepositions, conjunctions,
# relative pronouns, verbs, and sentence punctuation. A run of 4+ consecutive
# lowercase words not in this set is a likely multi-word noun (Rule 2.1).
NOUN_CLUSTER_BREAKERS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "for", "nor",
    "of", "on", "in", "at", "by", "to", "from", "with", "as", "into",
    "about", "above", "after", "against", "among", "between", "through",
    "during", "before", "without", "within", "under", "over", "per", "vs",
    "is", "are", "was", "were", "be", "been", "being", "am", "do", "does",
    "did", "have", "has", "had", "can", "could", "will", "would", "shall",
    "should", "may", "might", "must", "not", "no", "yes", "this", "that",
    "these", "those", "which", "who", "whom", "whose", "when", "where",
    "why", "how", "all", "any", "both", "each", "few", "more", "most",
    "other", "some", "such", "only", "own", "same", "so", "than", "too",
    "very", "just", "also", "now", "here", "there", "then", "than",
}

NOUN_CLUSTER_MIN = 4  # consecutive content words that flag a noun cluster

# --- Optional dictionary-backed vocabulary check ---------------------------
# Loaded lazily and only when --dict is passed. The standard's approved and
# not-approved lists are copyrighted by ASD; this linter ships no dictionary
# content. Users build not-approved.tsv from their own free PDF copy with
# tools/ste-dictionary/emit.py. When the file is absent, --dict is a no-op.
DICT_CANDIDATES = [
    Path("tools/ste-dictionary/not-approved.tsv"),
    Path("not-approved.tsv"),
    Path(__file__).resolve().parent.parent.parent
    / "tools" / "ste-dictionary" / "not-approved.tsv",
]
_DICT = None
_DICT_PATH = None

# Simple inflection rules applied before lookup. Same set as
# tools/ste-dictionary/ste_dict_lint.py so the two tools agree.
_DICT_INFLECTIONS = [
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


def _load_dict():
    """Return (words, path). words maps base form -> alternatives string."""
    global _DICT, _DICT_PATH
    if _DICT is not None:
        return _DICT, _DICT_PATH
    for cand in DICT_CANDIDATES:
        if cand.is_file():
            words = {}
            with open(cand, encoding="utf-8") as fh:
                next(fh, None)  # header
                for line in fh:
                    parts = line.rstrip("\n").split("\t")
                    if len(parts) >= 2:
                        words[parts[0].lower()] = parts[1]
            _DICT = words
            _DICT_PATH = cand
            return words, cand
    _DICT = {}
    _DICT_PATH = None
    return _DICT, None


def _dict_base_form(word):
    """Return the dictionary headword for word, or None if approved."""
    words, _ = _load_dict()
    if not words:
        return None
    lower = word.lower()
    if lower in words:
        return lower
    for pat, repl in _DICT_INFLECTIONS:
        if not pat.search(lower):
            continue
        cand = pat.sub(repl, lower)
        if cand in words:
            return cand
        if pat.pattern == r"ed$" and cand + "e" in words:
            return cand + "e"
    return None


def _dict_findings(text, filename):
    """Report each non-approved word once, with its line and column."""
    words, path = _load_dict()
    if not words:
        return [], path
    findings = []
    seen = set()
    for m in re.finditer(r"[A-Za-z][A-Za-z\-']*", text):
        base = _dict_base_form(m.group(0))
        if base and base not in seen:
            seen.add(base)
            lineno = text.count("\n", 0, m.start()) + 1
            col = m.start() - text.rfind("\n", 0, m.start())
            findings.append({
                "file": filename, "line": lineno, "col": col,
                "rule": "not-approved-word", "level": "advisory-free",
                "match": m.group(0),
                "message": (
                    f"{m.group(0)} is not in the approved dictionary. "
                    f"Use {words[base] or 'the approved alternative'}."
                ),
            })
    findings.sort(key=lambda f: (f["line"], f["col"]))
    return findings, path

def _find_noun_clusters(line, source_column, lineno, filename, findings):
    """Detect runs of 4+ consecutive lowercase content words (Rule 2.1).

    Uses a simple heuristic: split on spaces, skip words in the breaker set,
    skip capitalized words (likely sentence starts or proper nouns), and
    flag runs of NOUN_CLUSTER_MIN or more. This is not a parser and will
    false-positive on some legitimate prose, but it catches the most common
    and most damaging STE violation: a wall of nouns.
    """
    tokens = re.split(r"\s+", line.strip())
    run = []
    for tok in tokens:
        clean = re.sub(r"[^a-zA-Z]", "", tok)
        if not clean:
            continue
        lower = clean.lower()
        if clean[0].isupper() or lower in NOUN_CLUSTER_BREAKERS:
            run = []
            continue
        run.append((tok, lower))
        if len(run) >= NOUN_CLUSTER_MIN:
            start_col = source_column + 1
            for t, _ in run:
                start_col += len(t) + 1
            start_col -= len(run[-1][0]) + 1
            findings.append({
                "file": filename, "line": lineno, "col": start_col,
                "rule": "noun-cluster", "level": "advisory-free",
                "match": " ".join(t for t, _ in run),
                "message": (
                    f"{len(run)} consecutive nouns. Break with prepositions "
                    f"(of, on, in, for) or use a short form (Rule 2.1)."
                ),
            })
            return  # one finding per line is enough


# Preserve the original passive heuristic; perfects also include intransitive verbs.
PASSIVE_PARTICIPLES = "given|taken|made|done|found|seen|known|shown|written|built|sent|set|run|read|kept|held|left|put"
MODAL_PERFECT_PREFIX = re.compile(
    r"\b(?:may|might|could|should|would|must|can|will|shall)"
    r"(?:\s+not|n['’]t)?\s+$", re.I,
)

RULES = [
    ("semicolon", "advisory-free",
     re.compile(r";"),
     "STE bans the semicolon (Rule 8.1). Split into separate sentences."),
    ("phrasal-verb", "advisory-free",
     re.compile(r"\b(spin(?:ning|s)? up|spun up|reach(?:ing|es|ed)? out|div(?:e|es|ing|ed) into|dove into|kick(?:ing|s|ed)? off|circl(?:e|es|ing|ed) back|touch(?:ing|es|ed)? base)\b", re.I),
     "Soft phrasal verb. Use the single plain verb (start, contact, read, begin)."),
    ("marketing-adjective", "advisory-free",
     re.compile(r"\b(seamless(?:ly)?|robust(?:ly)?|cutting-edge|effortless(?:ly)?|blazing[- ]fast|world-class|state-of-the-art|game-chang(?:ing|er))\b", re.I),
     "Marketing adjective. Delete, or replace with the measurement that earns the claim."),
    ("nominalization", "advisory-free",
     re.compile(r"\b(perform|performs|performed|conduct|conducts|conducted|carry out|carries out|carried out)\s+(?:a|an|the)\s+\w+(?:tion|sion|ment|ance|ence|ysis)\b", re.I),
     "Action frozen into a noun. Use the verb (analyze, not perform an analysis of)."),
    ("passive-voice", "advisory",
     re.compile(r"\b(is|are|was|were|been|being)\s+(\w+ed|" + PASSIVE_PARTICIPLES + r")\b(?!\s+(?:to|for|by)\s+\w+ing)", re.I),
     "Possible passive voice. Name the actor and use an active verb, unless the actor is unknown or irrelevant."),
    ("present-perfect", "advisory",
     # modal + perfect infinitive ("may have failed") is a protected hedge, not present perfect
     re.compile(r"(?<!\bmay )(?<!\bmight )(?<!\bcould )(?<!\bshould )(?<!\bwould )(?<!\bmust )\b(has|have|had)\s+(?:been\s+)?(?:\w+(?:ed|en)|" + IRREGULAR_PARTICIPLES + r")\b", re.I),
     "Compound tense. Use simple past/present unless current relevance is the point (then keep and flag)."),
]# One word, one meaning: groups of verbs commonly rotated for the same action.
# Only pairs where the members are genuinely interchangeable — error/fault/failure
# are distinct concepts and stay out.
SYNONYM_GROUPS = [
    ("check", "verify", "confirm", "validate"),
    ("delete", "remove", "erase"),
    ("start", "launch", "begin", "initiate"),
    ("stop", "halt", "terminate"),
    ("show", "display"),
    ("use", "utilize", "employ"),
    ("fix", "repair", "correct"),
    ("send", "transmit"),
    ("get", "retrieve", "fetch", "obtain"),
    ("change", "modify", "alter"),
]

MAX_WORDS = 25  # descriptions cap; instructions cap is 20 but undetectable without context
# In --terse mode, the cap relaxes to 40 words. Terse mode is for scripts,
# internal tools, and chat replies where full STE grammar is overkill.
# It still bans phrasal verbs, marketing adjectives, nominalizations, and
# semicolons. It drops the anti-contraction rule (4.2) and the long-sentence
# cap. Use it deliberately: it is a relaxation, not a different standard.
TERSE_MAX_WORDS = 40

CODE_FENCE = re.compile(r"^(```|~~~)")
INLINE_CODE = re.compile(r"`[^`]*`")
LIST_ITEM_START = re.compile(
    r"^(?P<indent> {0,3})(?P<marker>[-*+]|[0-9]+[.)])(?P<gap> +)(?P<body>.*)$"
)
CONJUNCTION_END = re.compile(r"\b(?:and|or)\s*$", re.I)
TABLE_SEPARATOR_CELL = re.compile(r"^:?-{3,}:?$")


def _word_re(base):
    return re.compile(r"\b" + base + r"(?:s|es|ed|d|ing)?\b", re.I)


def _leading_spaces(line):
    return len(line) - len(line.lstrip(" "))


def _is_list_continuation(line, content_indent):
    if not line.strip():
        return True
    if LIST_ITEM_START.match(line):
        return False
    return _leading_spaces(line) >= content_indent


def _split_table_row(line):
    """Return trimmed table cells and their zero-based source columns.

    A pipe must separate at least two cells. Escaped pipes stay in their cell.
    This deliberately implements only the ordinary Markdown table shape; it is
    enough to distinguish a table from prose that happens to contain a pipe.
    """
    left = len(line) - len(line.lstrip())
    right = len(line.rstrip())
    content = line[left:right]
    if "|" not in content:
        return None
    if content.startswith("|"):
        content = content[1:]
        left += 1
    if content.endswith("|"):
        content = content[:-1]
    raw_cells = re.split(r"(?<!\\)\|", content)
    if len(raw_cells) < 2:
        return None

    cells = []
    column = left
    for raw_cell in raw_cells:
        leading = len(raw_cell) - len(raw_cell.lstrip())
        cells.append((raw_cell.strip(), column + leading))
        column += len(raw_cell) + 1
    return cells


def _markdown_table_cells(lines):
    """Map ordinary Markdown table rows to their prose cells.

    The separator row anchors detection, so pipe-containing prose is not
    treated as a table. Both leading-pipe and no-leading-pipe table styles are
    accepted when their header and body use the same number of cells.
    """
    table_cells = {}
    index = 1
    while index < len(lines):
        separator = _split_table_row(lines[index])
        header = _split_table_row(lines[index - 1])
        if (not separator or not header or len(separator) != len(header)
                or not all(TABLE_SEPARATOR_CELL.fullmatch(cell)
                           for cell, _ in separator)):
            index += 1
            continue

        table_cells[index - 1] = header
        table_cells[index] = []
        index += 1
        while index < len(lines):
            row = _split_table_row(lines[index])
            if not row or len(row) != len(separator):
                break
            table_cells[index] = row
            index += 1
    return table_cells


def _dangling_conjunction_findings(text, filename):
    lines = text.splitlines()
    findings = []
    in_fence = False
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if CODE_FENCE.match(stripped):
            in_fence = not in_fence
            index += 1
            continue
        if in_fence:
            index += 1
            continue
        start = LIST_ITEM_START.match(line)
        if not start:
            index += 1
            continue
        content_indent = (len(start.group("indent"))
                          + len(start.group("marker"))
                          + len(start.group("gap")))
        item_lines = [(index, start.group("body"))]
        next_index = index + 1
        item_fence = False
        while next_index < len(lines):
            candidate = lines[next_index]
            candidate_stripped = candidate.strip()
            if CODE_FENCE.match(candidate_stripped):
                item_fence = not item_fence
                next_index += 1
                continue
            if item_fence:
                next_index += 1
                continue
            if not _is_list_continuation(candidate, content_indent):
                break
            item_lines.append((next_index, candidate))
            next_index += 1
        meaningful = []
        for line_index, item_line in item_lines:
            cleaned = INLINE_CODE.sub(" CODE ", item_line).strip()
            if cleaned:
                meaningful.append((line_index, cleaned))
        if meaningful:
            end_line_index, end_line = meaningful[-1]
            conjunction = CONJUNCTION_END.search(end_line)
        else:
            end_line_index, end_line, conjunction = None, None, None
        if conjunction:
            if end_line_index == index:
                finding_line = index + 1
                finding_col = start.start("marker") + 1
            else:
                raw_end_line = next(
                    raw for li, raw in item_lines if li == end_line_index
                )
                masked_end_line = INLINE_CODE.sub(
                    lambda match: " " * len(match.group(0)), raw_end_line
                )
                raw_conjunction = CONJUNCTION_END.search(masked_end_line)
                finding_line = end_line_index + 1
                finding_col = raw_conjunction.start() + 1 if raw_conjunction else 1
            findings.append({
                "file": filename,
                "line": finding_line,
                "col": finding_col,
                "rule": "dangling-conjunction",
                "level": "advisory-free",
                "match": end_line,
                "message": "List item ends with a coordinating conjunction. Complete the item or join it with the next item.",
            })
        index = next_index
    return findings
def lint(text, filename="<stdin>", terse=False):
    """Return the STE100 findings for the given text."""
    findings = []
    in_fence = False
    lines = text.splitlines()
    table_cells = _markdown_table_cells(lines)
    seen_synonyms = {}
    for lineno, raw_line in enumerate(lines, 1):
        if CODE_FENCE.match(raw_line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        segments = table_cells.get(lineno - 1, [(raw_line, 0)])
        for segment, source_column in segments:
            line = INLINE_CODE.sub(" ", segment)
            for rule_id, level, pattern, msg in RULES:
                for m in pattern.finditer(line):
                    if rule_id == "present-perfect" and MODAL_PERFECT_PREFIX.search(line[:m.start()]):
                        continue
                    findings.append({"file": filename, "line": lineno,
                                     "col": source_column + m.start() + 1,
                                     "rule": rule_id, "level": level,
                                     "match": m.group(0), "message": msg})
            for gi, group in enumerate(SYNONYM_GROUPS):
                for base in group:
                    if (gi, base) in seen_synonyms:
                        continue
                    m = _word_re(base).search(line)
                    if m:
                        seen_synonyms[(gi, base)] = (lineno, source_column + m.start() + 1, m.group(0))
            for sent in re.split(r"(?<=[.!?])\s+", line):
                n = len(sent.split())
                cap = TERSE_MAX_WORDS if terse else MAX_WORDS
                if n > cap:
                    findings.append({"file": filename, "line": lineno,
                                     "col": source_column + 1,
                                     "rule": "long-sentence", "level": "advisory-free",
                                     "match": f"{n} words",
                                     "message": f"Sentence has {n} words (cap {MAX_WORDS}). Split it."})
            _find_noun_clusters(line, source_column, lineno, filename, findings)
    for gi, group in enumerate(SYNONYM_GROUPS):
        present = [(seen_synonyms[(gi, b)], b) for b in group if (gi, b) in seen_synonyms]
        if len(present) > 1:
            present.sort()
            first_base = present[0][1]
            for (lineno, col, match), base in present[1:]:
                findings.append({"file": filename, "line": lineno, "col": col,
                                 "rule": "synonym-rotation", "level": "advisory-free",
                                 "match": match,
                                 "message": f"{base} and {first_base} name the same action. Pick one and use it every time."})
    findings.extend(_dangling_conjunction_findings(text, filename))
    findings.sort(key=lambda f: (f["line"], f["col"]))
    return findings
def report(findings, words_total, as_json, hard_count, baseline):
    """Print the findings as text or JSON."""
    rate = round(len(findings) * 100 / words_total, 1) if words_total else 0.0
    if as_json:
        print(json.dumps({"violations": findings, "count": len(findings),
                          "hard_count": hard_count, "baseline": baseline,
                          "words": words_total, "per_100_words": rate}, indent=2))
        return
    for f in findings:
        print(f"{f['file']}:{f['line']}:{f['col']} {f['rule']}: {f['message']} [{f['match']}]")
    print(f"\n{len(findings)} violations ({hard_count} hard, baseline {baseline}), "
          f"{words_total} words, {rate} per 100 words")
    print("Hedges/modality (may, might, could) are never flagged: confidence is content.")





# Mechanical fixes for rules that have deterministic replacements.
# Each entry maps a rule id to (pattern, replacement_or_dict).
# Rules that need judgment (passive voice, synonym choice, long sentences)
# are intentionally excluded: a linter cannot know the right actor or
# the right synonym without context.
FIX_RULES = {
    "semicolon": (re.compile(r";"), "."),
    "phrasal-verb": (
        re.compile(
            r"\b(spin(?:ning|s)? up|spun up|reach(?:ing|es|ed)? out|"
            r"div(?:e|es|ing|ed) into|dove into|kick(?:ing|s|ed)? off|"
            r"circl(?:e|es|ing|ed) back|touch(?:ing|es|ed)? base)\b",
            re.I,
        ),
        {
            "spin up": "start", "spinning up": "starting", "spun up": "started",
            "reach out": "contact", "reaching out": "contacting", "reached out": "contacted",
            "dive into": "read", "diving into": "reading", "dived into": "read",
            "dove into": "read",
            "kick off": "begin", "kicking off": "beginning", "kicked off": "began",
            "circle back": "return", "circling back": "returning", "circled back": "returned",
            "touch base": "check", "touching base": "checking", "touched base": "checked",
        },
    ),
    "marketing-adjective": (
        # Consume a leading/trailing bold span together with the word, so
        # **seamless** deletes as one unit instead of leaving **** behind.
        re.compile(
            r"\*\*(seamless(?:ly)?|robust(?:ly)?|cutting-edge|"
            r"effortless(?:ly)?|blazing[- ]fast|world-class|"
            r"state-of-the-art|game-chang(?:ing|er))\*\*"
            r"|\b(seamless(?:ly)?|robust(?:ly)?|cutting-edge|"
            r"effortless(?:ly)?|blazing[- ]fast|world-class|"
            r"state-of-the-art|game-chang(?:ing|er))\b",
            re.I,
        ),
        {
            "seamless": "", "seamlessly": "", "robust": "", "robustly": "",
            "cutting-edge": "", "effortless": "", "effortlessly": "",
            "blazing fast": "", "blazing-fast": "", "world-class": "",
            "state-of-the-art": "", "game-changer": "", "game-changing": "",
        },
    ),
}


def _apply_fixes(text):
    """Apply deterministic fixes. Returns (fixed_text, fixes_applied)."""
    fixes = []
    for rule_id, (pattern, replacement) in FIX_RULES.items():
        if isinstance(replacement, str):
            new_text, count = pattern.subn(replacement, text)
        else:
            def repl(m):
                word = m.group(0)
                # The marketing-adjective pattern may have consumed a bold
                # span (**seamless**). Strip it before the dict lookup.
                stripped = word.strip("*")
                lower = stripped.lower()
                if lower in replacement:
                    new_word = replacement[lower]
                    return new_word if new_word else ""
                return word
            new_text, count = pattern.subn(repl, text)
        if count:
            fixes.append((rule_id, count))
        text = new_text
    # Clean up double spaces left by removed adjectives
    text = re.sub(r"  +", " ", text)
    return text, fixes


def fix_files(files, dry_run=False):
    """Apply mechanical fixes to files. Returns list of (filename, fixes)."""
    results = []
    for filename in files:
        with open(filename, "r") as f:
            original = f.read()
        fixed, fixes = _apply_fixes(original)
        if fixes and not dry_run:
            with open(filename, "w") as f:
                f.write(fixed)
        results.append((filename, fixes))
    return results

def selftest():
    """Run the invariants. Exit 0 on success, 1 on failure."""
    failures = []

    def check(name, cond):
        if not cond:
            failures.append(name)

    positives = {
        "semicolon": "Do A. Do B; do C.",
        "phrasal-verb": "The system will spin up after the test.",
        "marketing-adjective": "This is a seamless integration.",
        "nominalization": "Perform an analysis of the data.",
        "passive-voice": "The valve was closed by the operator.",
        "present-perfect": "The team has verified the fix.",
    }
    for rule, text in positives.items():
        findings = lint(text)
        check(rule + " fires", any(f["rule"] == rule for f in findings))

    check("clean text clean", lint("Open the valve. Check the pressure.") == [])

    hedge_text = (
        "You may have missed a step. The data could be wrong. "
        "Might this be the cause? It should have stopped. "
        "The engine may have failed. They would have seen the warning."
    )
    check("hedges never flagged", lint(hedge_text) == [])

    long_text = " ".join(["word"] * 30)
    check("long sentence flagged", any(f["rule"] == "long-sentence" for f in lint(long_text)))

    check("synonym rotation", any(
        f["rule"] == "synonym-rotation" for f in lint("Use verify to check the value.")
    ))

    list_text = "- Open the valve" + chr(10) + "- Check pressure" + chr(10) + "- And"
    check("dangling conjunction", any(
        f["rule"] == "dangling-conjunction" for f in lint(list_text)
    ))

    noun_text = "The connection pool timeout configuration value is set."
    check("noun cluster fires", any(
        f["rule"] == "noun-cluster" for f in lint(noun_text)
    ))

    normal_text = "Open the valve. Check the pressure."
    check("noun cluster does not fire on normal text", not any(
        f["rule"] == "noun-cluster" for f in lint(normal_text)
    ))

    # --dict is opt-in: the structural linter never checks vocabulary.
    check("structural lint ignores vocabulary", lint("utilize the lever") == [])
    if _DICT_PATH:
        hits, _ = _dict_findings("utilize the lever", "<test>")
        check("dict flags a non-approved word", any(f["rule"] == "not-approved-word" for f in hits))
        clean, _ = _dict_findings("use the lever", "<test>")
        check("dict is silent on approved words", clean == [])

    if failures:
        for name in failures:
            print("SELFTEST FAIL: " + name, file=sys.stderr)
        return 1
    print("selftest: all invariants hold")
    return 0
def main(argv):
    """Parse the arguments and run the linter."""
    args = argv[1:]
    baseline = 0
    disable = set()
    as_json = False
    fix = False
    dry_run = False
    terse = False
    use_dict = False
    files = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--baseline":
            baseline = int(args[i + 1]); i += 2; continue
        if a == "--disable":
            disable = set(x.strip() for x in args[i + 1].split(",") if x.strip()); i += 2; continue
        if a == "--json":
            as_json = True; i += 1; continue
        if a == "--selftest":
            return selftest()
        if a == "--fix":
            fix = True; i += 1; continue
        if a == "--dry-run":
            dry_run = True; i += 1; continue
        if a == "--terse":
            terse = True; i += 1; continue
        if a == "--dict":
            use_dict = True; i += 1; continue
        if a.startswith("-"):
            print(f"unknown flag: {a}", file=sys.stderr); return 2
        files.append(a); i += 1

    if not files:
        text = sys.stdin.read()
        findings = [f for f in lint(text, terse=terse) if f["rule"] not in disable]
        if use_dict:
            dict_findings, dict_path = _dict_findings(text, "<stdin>")
            if dict_path:
                findings.extend(dict_findings)
            else:
                print("--dict: no not-approved.tsv found; vocabulary check skipped")
        hard = [f for f in findings if f["level"] == "advisory-free"]
        report(findings, _count_words(text), as_json, len(hard), baseline)
        return 1 if len(hard) > baseline else 0

    all_findings = []
    total_words = 0
    for path in files:
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except OSError as exc:
            print(f"cannot read {path}: {exc}", file=sys.stderr)
            return 2
        total_words += _count_words(text)
        for f in lint(text, filename=path, terse=terse):
            if f["rule"] not in disable:
                all_findings.append(f)
        if use_dict:
            dict_findings, dict_path = _dict_findings(text, path)
            if dict_path:
                all_findings.extend(dict_findings)
            else:
                print(f"--dict: no not-approved.tsv found; vocabulary check skipped for {path}")
    hard = [f for f in all_findings if f["level"] == "advisory-free"]
    if dry_run:
        for filename, fixes in fix_files(files, dry_run=True):
            for rule_id, count in fixes:
                print(f"{filename}: would fix {count} {rule_id}")
        return 0
    if fix:
        for filename, fixes in fix_files(files):
            for rule_id, count in fixes:
                print(f"{filename}: fixed {count} {rule_id}")
    report(all_findings, total_words, as_json, len(hard), baseline)
    return 1 if len(hard) > baseline else 0


def _count_words(text):
    code_blocks = INLINE_CODE.sub(" ", text)
    return len(re.findall(r"[A-Za-z0-9]+", code_blocks))


if __name__ == "__main__":
    sys.exit(main(sys.argv))

# GEMINI.md — ASD-STE100 Skill

This file gives Gemini CLI the STE100 skill on demand.

## Skill

The skill lives in `skills/ste100/SKILL.md`. It is a front-matter skill that
works with Claude Code, Codex, Cursor, Gemini CLI, and OpenCode.

Load it when the user asks to:

- Write or rewrite text in ASD-STE100 Simplified Technical English
- Disambiguate text, or rewrite so an agent cannot misread it
- Remove jargon, slop, or AI writing from docs, prompts, or replies
- Write or check error messages, runbooks, incident reports, release notes,
  commit messages, agent prompts, or UI copy
- Use any of these trigger phrases: "STE", "Simplified Technical English",
  "plain English", "layman terms", "explain it simply", "no jargon",
  "de-slop", "make this readable", "write for non-native readers",
  "disambiguate this", "controlled-language rewrite"

## Default mode

Plain (structural rules only). The skill itself explains the difference
between Plain and Strict.

## Linter

The repo ships a linter at `skills/ste100/scripts/ste-lint.py` that checks
text against the 53 rules. Run it with:

```
python3 skills/ste100/scripts/ste-lint.py --selftest
python3 skills/ste100/scripts/ste-lint.py path/to/file.md
python3 skills/ste100/scripts/ste-lint.py --json --baseline 5 file.md
```

The eval harness at `skills/ste100/evals/ste_lint.py` walks a directory and
lints every `.md` and `.txt` file:

```
python3 skills/ste100/evals/ste_lint.py examples --baseline 5
```

## Dictionary toolchain

The official ASD dictionary is copyrighted and not redistributed. To build
the dictionary-backed checker from your own free PDF copy:

```
pdftotext -layout -enc UTF-8 your_ste100.pdf ste.txt
python3 tools/ste-dictionary/parse_dict.py ste.txt
python3 tools/ste-dictionary/emit.py
python3 tools/ste-dictionary/ste_dict_lint.py --self-test
```

This produces `tools/ste-dictionary/not-approved.tsv`, which
`ste_dict_lint.py` uses to flag non-approved words with their approved
alternatives.

## Tests

```
python3 -m pytest tests/test_linters.py -q
```

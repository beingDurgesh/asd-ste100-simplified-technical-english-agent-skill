# asd-ste100-skill

An [Agent Skills](https://github.com/agentskills/agentskills) package that makes
your AI agent write and rewrite text in **ASD-STE100 Simplified Technical
English** — the controlled language behind aerospace maintenance manuals.

## What it does

Two registers, both short:

- **Document mode (Plain)** — structural rules only. Short sentences, active
  voice, simple tenses, one word per meaning, condition before command, every
  technical term defined at first use. No AI slop. This is the default.
- **Strict mode** — full STE vocabulary compliance, including the approved-word
  dictionary, when the user names STE, ASD-STE100, or compliance.

The same rules govern the reply the agent types in chat.

## Installation

### As a plugin (recommended)

Loads the rules automatically on every session start. No need to name the skill.

Claude Code:

```
claude plugin marketplace add beingDurgesh/asd-ste100-simplified-technical-english-agent-skill
claude plugin install asd-ste100@asd-ste100
```

Codex:

```
codex plugin marketplace add beingDurgesh/asd-ste100-simplified-technical-english-agent-skill
codex plugin add asd-ste100@asd-ste100
```

The plugin runs a `SessionStart` hook that injects the condensed rule block into
context, plus advisory `PostToolUse` and `Stop` checks under Claude Code that
lint Markdown files and reply register without ever blocking.

### As a skill

```
cp -r asd-ste100-skill ~/.agent/skills/
```

Or drop the `skills/ste100/` folder into any skills directory the agent reads.
No install step, no network calls, no dependencies beyond the standard library.

## Agent integration files

The repo ships the same skill in every agent's native instruction file, so
the agent picks it up without a skills directory:

| File | Agent |
|---|---|
| `CLAUDE.md` | Claude Code |
| `AGENTS.md` | Codex, OpenCode, and any AGENTS.md reader |
| `GEMINI.md` | Gemini CLI |
| `.cursor/rules/ste100.mdc` | Cursor rules |
| `.github/copilot-instructions.md` | GitHub Copilot |
| `.claude-plugin/plugin.json` | Claude Code plugin manifest |
| `skills/ste100/hooks/` | SessionStart, PostToolUse, and Stop hooks |
| `skills/ste100/prompts/system-prompt.md` | Compact rule block for the hook payload |
| `skills/ste100/slop.tsv` | LLM-tell words counted by the dictionary linter |

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
alternatives. The parser classifies entries by **word-column case**
(UPPERCASE = approved, lowercase = not-approved), per the standard's rule on
page 2-0-9. Inflected forms inherit the headword's status.

## Files

```
skills/ste100/
├── SKILL.md              # entry point: mode selection, short rule sets, references
├── references/
│   ├── writing-rules.md  # all 9 rule sections with citations
│   ├── rule-catalog.md   # the 53-rule catalog + modal ladder
│   ├── strict-vocabulary.md  # part-of-speech rulings, dictionary rulings
│   ├── word-swaps.md     # 70+ slop → simple replacements
│   └── use-cases.md      # error messages, runbooks, incident reports, etc.
├── scripts/
│   └── ste-lint.py       # deterministic linter for the structural rules
├── hooks/                # Claude Code and Codex hooks (SessionStart, PostToolUse, Stop)
│   ├── ste100-activate.js
│   ├── lint_hook.py
│   └── test_lint_hook.py
├── prompts/
│   └── system-prompt.md  # compact rule block for the hook payload
└── slop.tsv              # LLM-tell words counted by the dictionary linter
```

## Using the linter

```
python3 skills/ste100/scripts/ste-lint.py README.md
python3 skills/ste100/scripts/ste-lint.py --selftest
echo "text" | python3 skills/ste100/scripts/ste-lint.py --json
python3 skills/ste100/scripts/ste-lint.py --baseline 5 doc.md
python3 skills/ste100/scripts/ste-lint.py --disable passive-voice,present-perfect doc.md
```

Exit 1 when hard (`advisory-free`) violations exceed the baseline (default 0).
Advisory findings (passive voice, compound tenses) never fail the run.

## What the linter checks

Semicolons, phrasal verbs, marketing adjectives, nominalizations, passive voice,
present perfect, long sentences, synonym rotation, dangling conjunctions. It
deliberately never flags hedges or modality (`may`, `might`, `could`): in STE,
confidence is content, and a linter that pressures hedges out would rewrite
claims.

## The official dictionary

ASD-STE100 Issue 9 ships roughly 900 approved words and 1,200 words to avoid
with suggested replacements. That dictionary is copyrighted by ASD and is **not**
redistributed here. Get the free official copy at
[asd-ste100.org](https://www.asd-ste100.org) and make your own word lists from
it. This package teaches the rules; it is lossy on vocabulary.

## License

MIT — see [LICENSE](LICENSE).

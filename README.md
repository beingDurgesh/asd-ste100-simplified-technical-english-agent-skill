# ASD-STE100 Simplified Technical English Skill for AI Agents

An Agent Skills package that makes
your AI agent write and rewrite text in **ASD-STE100 Simplified Technical
English** — the controlled language behind aerospace maintenance manuals.

![Pylint](https://github.com/beingDurgesh/asd-ste100-simplified-technical-english-agent-skill/actions/workflows/pylint.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-FFD43B?logo=python&logoColor=3776AB&labelColor=3776AB)
![License](https://img.shields.io/github/license/beingDurgesh/asd-ste100-simplified-technical-english-agent-skill?color=E67E22&logo=opensourceinitiative&logoColor=white)
![Last commit](https://img.shields.io/github/last-commit/beingDurgesh/asd-ste100-simplified-technical-english-agent-skill?color=8E44AD&logo=git&logoColor=white)
![Stars](https://img.shields.io/github/stars/beingDurgesh/asd-ste100-simplified-technical-english-agent-skill?color=F1C40F&logo=github&logoColor=white)
![Agent Skill](https://img.shields.io/badge/Agent%20Skill-ASD--STE100-E84393)

## What it does

<img width="1024" height="768" alt="ASD-STE100 agent skill social preview 1" src="https://github.com/user-attachments/assets/5ce2f8e9-b80a-4a72-bc91-f049f7d2ea87" />


Two registers, both short:

- **Document mode (Plain)** — structural rules only. Short sentences, active
  voice, simple tenses, one word per meaning, condition before command, every
  technical term defined at first use. No AI slop. This is the default.
- **Strict mode** — full STE vocabulary compliance, including the approved-word
  dictionary, when the user names STE, ASD-STE100, or compliance.

The same rules govern the reply the agent types in chat.

## Install


### Quick install (recommended)

Install the ASD-STE100 Simplified Technical English skill in your project:

```bash
npx skills add beingDurgesh/asd-ste100-simplified-technical-english-agent-skill
```

Update the installed skill:

```bash
npx skills update
```


### As a plugin

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

Copy the skill folder into any skills directory your agent reads. From inside
the cloned repo:

```
cp -r skills/ste100 ~/.agent/skills/ste100
```
No install step, no network calls, no dependencies beyond the standard library.

## Before and after

A rewrite keeps the meaning and drops the parts that a reader outside your
field must guess. Here is the same instruction in Plain mode and in Strict
mode.

### Plain mode

Before:

> To deploy, make sure the build passed. Then run the deploy script. If the
> script fails, check the logs and fix the issue before you try again.

After:

> Build must pass before you deploy. Run `scripts/deploy.sh`. If the script
> fails, read `logs/deploy.log`. Fix the cause. Run the script again.

### Strict mode

Strict mode applies the full vocabulary. Words not in the approved
dictionary are replaced or removed.

Before:

> Utilize the configuration panel to modify the settings. The system will
> subsequently initiate the update procedure.

After:

> Use the configuration panel to change the settings. The system then runs
> the update.

### Hedges and uncertainty

A rewrite can keep a hedge without using a banned modal. The standard
gives the approved adjective for past possibility.

Before:

> The update may have caused the outage.

After:

> It is possible that the update caused the outage.

Strict mode is on when you name STE, ASD-STE100, or compliance. No tool
guarantees full compliance, because the official dictionary is copyrighted
and is a free download at asd-ste100.org.

#### How the hedge rewrite works

The sentence keeps its uncertainty and drops the banned modal. The
adjective POSSIBLE is approved in the standard, and the "It is possible
that" construction is the standard's own example for it. The past tense
(caused) stays simple, which satisfies Rule 3.2. No cause is asserted:
the reader still does not know whether the update was the cause.

A rewrite never turns a hedge into a certainty. If the cause is unknown,
say so directly:

Before:

> The update may or may not have caused the outage.

After:

> It is not known whether the update caused the outage.

The linter does not check this. Rule 3.2 and the modal ladder ban
`may`, `might`, and `could`, but the linter deliberately never flags them:
in STE, confidence is content, and a linter that pressures hedges out
would rewrite claims. The linter cannot tell a factual hedge from a
polite one, so it leaves both alone. A clean linter pass is not a
compliance certificate. The writer restructures. The linter only checks
the result.

## Use it

Ask your agent to:

- Write or rewrite text in ASD-STE100 Simplified Technical English
- Disambiguate text, or rewrite so an agent cannot misread it
- Remove jargon, slop, or AI writing from docs, prompts, or replies
- Write or check error messages, runbooks, incident reports, release notes,
  commit messages, agent prompts, or UI copy

Trigger phrases: "STE", "Simplified Technical English", "plain English",
"layman terms", "explain it simply", "no jargon", "de-slop", "make this
readable", "write for non-native readers", "disambiguate this",
"controlled-language rewrite".

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
| `output-styles/simple-english.md` | Claude Code output style |
| `skills/ste100/hooks/` | SessionStart, PostToolUse, and Stop hooks |
| `skills/ste100/prompts/system-prompt.md` | Compact rule block for the hook payload |
| `skills/ste100/slop.tsv` | LLM-tell words counted by the dictionary linter |

## The skill

```
skills/ste100/
├── SKILL.md              
├── references/
│   ├── writing-rules.md  
│   ├── rule-catalog.md   
│   ├── strict-vocabulary.md  
│   ├── word-swaps.md     
│   └── use-cases.md      
├── scripts/
│   └── ste-lint.py       
├── hooks/               
│   ├── ste100-activate.js
│   ├── lint_hook.py
│   └── test_lint_hook.py
├── prompts/
│   └── system-prompt.md  
└── slop.tsv              
```

## Using the linter

```
python3 skills/ste100/scripts/ste-lint.py README.md
python3 skills/ste100/scripts/ste-lint.py --selftest
python3 skills/ste100/scripts/ste-lint.py --dict README.md
echo "text" | python3 skills/ste100/scripts/ste-lint.py --json
python3 skills/ste100/scripts/ste-lint.py --baseline 5 doc.md
python3 skills/ste100/scripts/ste-lint.py --disable passive-voice,present-perfect doc.md
python3 skills/ste100/scripts/ste-lint.py --fix doc.md
python3 skills/ste100/scripts/ste-lint.py --terse doc.md
```

Exit 1 when hard (`advisory-free`) violations exceed the baseline (default 0).
Advisory findings (passive voice, compound tenses) never fail the run.

`--dict` adds the vocabulary check. It reads `tools/ste-dictionary/not-approved.tsv`
and reports every word the standard does not approve, with the approved
alternatives. It is opt-in: the structural rules work without it. If the word
list is absent, `--dict` says so and checks nothing. Build the list from your
own free PDF copy with the tools in `tools/ste-dictionary/`.

## What the linter checks

Semicolons, phrasal verbs, marketing adjectives, nominalizations, passive
voice, present perfect, long sentences, synonym rotation, dangling
conjunctions, and noun clusters are checked. The linter deliberately never
flags hedges or modality (`may`, `might`, `could`): in STE, confidence is
content, and a linter that pressures hedges out would rewrite claims.

A clean linter pass does not mean the text is compliant. The linter cannot
tell a factual hedge from a polite one, so it leaves both alone and you
decide. Rule 3.2 and the modal ladder still prohibit `may`, `might`, and `could`:
the writer restructures, the linter only checks the result. For past
possibility the standard uses the approved adjective: "It is possible that
the update caused the outage", not "The update may have caused the outage."

## Dictionary toolchain

The official ASD dictionary is copyrighted. It is not redistributed. To build
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

## Tests

```
python3 skills/ste100/scripts/ste-lint.py --selftest
python3 skills/ste100/hooks/test_lint_hook.py
python3 tools/ste-dictionary/ste_dict_lint.py --self-test
python3 -m pytest tests/test_linters.py -q
```

## Why STE100

This package exists because AI agents write prose that is well-formed and
meaningless. A reader who is not a specialist cannot tell that "utilize"
means "use", or that "leverage" means "use", or that "subsequently" means
"then". STE removes that class of error by restricting vocabulary and sentence
form.

The standard was written for aircraft maintenance manuals, where a misread
word can ground a fleet. Its properties make the standard useful for any text
an agent writes that a human must read and act on: error messages, runbooks,
incident reports, release notes, API guides, and prompts that other agents
read.

Two registers keep the cost low. Plain mode applies structural rules
only: short sentences, active voice, simple tenses, condition before
command. It catches most ambiguity without touching vocabulary. Strict
mode applies the full dictionary. It is on when you name STE, ASD-STE100,
or compliance.

The linter is advisory by design. It never flags hedges or modality (`may`,
`might`, `could`): in STE, confidence is content and a linter that pressures
hedges out would rewrite claims. Advisory findings never fail a run. They
include passive voice and compound tenses.

Note that a linter pass with zero findings is not a compliance certificate.
The linter cannot separate a factual hedge from a polite one, so it leaves
both for you. The rules still ban `may`, `might`, and `could`. For past
possibility write "It is possible that the update caused the outage."

## FAQ

**Do I need the official dictionary?**

No. Plain mode works without it. Strict mode is more accurate with it, but
ASD owns the dictionary. It is not redistributed here. Get the free copy at
asd-ste100.org and build your own word lists with the tools in
`tools/ste-dictionary/`. Then run `ste-lint.py --dict` to check vocabulary.

**Will the linter change my files?**

Only if you pass `--fix`. That flag does three mechanical substitutions:
semicolons to periods, banned marketing adjectives to empty strings, and a
small set of phrasal verbs to their one-word equivalents. Nothing else is
changed. Run `--fix` on a copy first.

**Does this work in my editor?**

The repo ships instruction files for every major agent. Drop the matching
file into your project root. The agent picks it up automatically:

| File | Agent |
|---|---|
| `CLAUDE.md` | Claude Code |
| `AGENTS.md` | Codex, OpenCode, any AGENTS.md reader |
| `GEMINI.md` | Gemini CLI |
| `.cursor/rules/ste100.mdc` | Cursor |
| `.github/copilot-instructions.md` | GitHub Copilot |

**What does the linter not check?**

It does not check vocabulary against the approved dictionary. It checks
structure: semicolons, phrasal verbs, marketing adjectives, nominalizations,
passive voice, present perfect, long sentences, synonym rotation, dangling
conjunctions, and noun clusters. It never flags hedges or modality.

**Is this the same as the popular `danyuchn/asd-ste100-skill`?**

No. That is a Claude Code skill with a linter and two modes. This package
follows the Agent Skills standard, so it works in Claude Code, Codex, Cursor,
Gemini CLI, OpenCode, and others. It also ships a dictionary toolchain and
hooks that the other package does not have.

## The official dictionary

ASD-STE100 Issue 9 ships roughly 900 approved words and 1,200 words to avoid
with suggested replacements. ASD owns that dictionary. You cannot download
it here. Get the free official copy at
[asd-ste100.org](https://www.asd-ste100.org) and make your own word lists from
it. This package teaches the rules. It is lossy on vocabulary.

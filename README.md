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

## Install

```
npx skills add beingDurgesh/asd-ste100-simplified-technical-english-agent-skill
```

This pulls the skill from the GitHub repo and installs it for the current
project. Update later with `npx skills update`.

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

## The skill

```
skills/ste100/
├── SKILL.md              # entry point: mode selection, short rule sets, references
├── references/
│   ├── writing-rules.md  # all 9 rule sections with citations
│   ├── rule-catalog.md   # the 53-rule catalog + modal ladder
│   ├── strict-vocabulary.md  # part-of-speech rulings, dictionary rulings
│   ├── word-swaps.md     # 70+ slop → simple replacements
│   └── use-cases.md      # error messages, runbooks, incident reports, etc.
└── scripts/
    └── ste-lint.py       # deterministic linter for the structural rules
```

## The linter

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
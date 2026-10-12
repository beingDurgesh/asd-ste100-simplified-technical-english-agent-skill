# Changelog

## 1.0.4 — 2026-10-12

- Documented how the hedge rewrite preserves uncertainty. The README now
  explains that the "It is possible that" construction is the standard's
  own example for the approved adjective POSSIBLE, that the past tense
  stays simple under Rule 3.2, and that a rewrite never turns a hedge into
  a certainty. Added a second worked example ("It is not known whether
  the update caused the outage.") for the case where the cause is unknown.

## 1.0.3 — 2026-10-11

- Added `opencode/slash: "true"` metadata to `SKILL.md`, exposing the skill
  as a `/ste100` slash command in OpenCode.
- Added `opencode.json` with skill permissions allowing `ste100` for the
  build and plan agents.
- Rewrote the `description` field to be more prominent and action-oriented
  ("Apply ASD-STE100 to ALL writing", "Load this skill proactively"), so
  OpenCode auto-selection is more likely to pick it up for writing tasks.
- Updated `AGENTS.md` with the `/ste100` slash command note.

## 1.0.2 — 2026-10-11

- Added `--dict` to `ste-lint.py`. When `tools/ste-dictionary/not-approved.tsv`
  is present, the linter reports every word the standard does not approve,
  with the approved alternatives. The flag is opt-in: the structural rules
  work without it, and it is a no-op when the word list is absent.
- Added an output style at `output-styles/simple-english.md` and registered it
  in `.claude-plugin/plugin.json`. It makes the agent reply in STE register
  without naming the skill.
- Rewrote the output style to use the same rule set as `SKILL.md` instead of
  its own copy, so the two cannot drift.
- Added Before/after examples, a Why STE100 section, and an FAQ to
  `README.md`.
- Fixed the `--fix` marketing-adjective rule, which previously left `****`
  garbage behind when an adjective was wrapped in bold.
- Restored the `LICENSE` file and all license references.

## 1.0.1 — 2026-10-11

- Restored agent integration files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`,
  `.cursor/rules/ste100.mdc`, `.github/copilot-instructions.md`), plugin
  manifests (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`,
  `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`),
  hooks (`skills/ste100/hooks/`), prompts (`skills/ste100/prompts/`),
  evals (`skills/ste100/evals/`), slop word list, tests, and output styles.
- Added Antigravity CLI to the `compatibility` field in `SKILL.md`.
- Added `npx skills add` quick-install instructions to `README.md`.
- Fixed stale `evals/` paths in `.cursor/rules/ste100.mdc` and
  `.github/copilot-instructions.md` after the reorganization.
- Removed `examples/` directory (not referenced by any install path).

## 1.0.0 — 2026-10-10

- Initial release.
- `SKILL.md` with Plain and Strict registers, 5 reference files, and a
  deterministic structural linter.
- Linter checks semicolons, phrasal verbs, marketing adjectives,
  nominalizations, passive voice, present perfect, long sentences, synonym
  rotation, and dangling conjunctions. Hedges/modality are never flagged.
- `--selftest`, `--baseline`, `--disable`, `--fix`, `--json`, and `--terse`
  flags.

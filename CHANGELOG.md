# Changelog

## 1.0.1 — 2026-10-11

- Added Antigravity CLI to the `compatibility` field in `SKILL.md`.
- Added `npx skills add` quick-install instructions to `README.md`.
- Fixed stale `evals/` paths in `.cursor/rules/ste100.mdc` and
  `.github/copilot-instructions.md` after the reorganization.

## 1.0.0 — 2026-10-10

- Initial release.
- `SKILL.md` with Plain and Strict registers, 5 reference files, and a
  deterministic structural linter.
- Linter checks semicolons, phrasal verbs, marketing adjectives,
  nominalizations, passive voice, present perfect, long sentences, synonym
  rotation, and dangling conjunctions. Hedges/modality are never flagged.
- `--selftest`, `--baseline`, `--disable`, `--fix`, `--json`, and `--terse`
  flags.
# Changelog

## 1.0.1 — 2026-10-11

- Claude Code and Codex plugins with a SessionStart hook that loads the
  writing rules automatically. Install with
  `claude plugin install asd-ste100@asd-ste100`.
- Advisory PostToolUse and Stop hooks under Claude Code: lint Markdown files
  after Write/Edit and check the reply register for em-dashes, bold,
  headers, bullets, and filler openers/closers. Neither hook blocks.
- Output style for Claude Code (`output-styles/simple-english.md`).
- Compact system prompt (`skills/ste100/prompts/system-prompt.md`) for the hook
  payload.
- Hooks, the slop word list, and the compact prompt moved inside
  `skills/ste100/` so `npx skills add` installs them with the skill instead of
  leaving them in the repo root.
- Linter `--fix` no longer leaves `****` behind when it deletes a marketing
  adjective wrapped in bold (`**seamless**`).
- Marketplace catalog (`.claude-plugin/marketplace.json`,
  `.agents/plugins/marketplace.json`).

## 1.0.0 — 2026-10-10

- Initial release.
- SKILL.md with Plain and Strict registers, 5 reference files, and a
  deterministic structural linter.
- Linter checks semicolons, phrasal verbs, marketing adjectives,
  nominalizations, passive voice, present perfect, long sentences, synonym
  rotation, and dangling conjunctions. Hedges/modality are never flagged.
- `--selftest`, `--baseline`, `--disable`, and `--json` flags.

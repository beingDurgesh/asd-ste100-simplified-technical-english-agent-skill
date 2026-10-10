# Linter edge cases

Cases the linter deliberately does **not** flag, and why.

## Hedges and modality

`may`, `might`, `could`, `should`, `would`, `must`, `can`, `will`, `shall` —
including in compound form (`may have failed`) — are never flagged. In STE,
confidence is content, and a linter that pressures hedges out would rewrite
claims.

## Semicolons inside code fences

Code fences are skipped entirely.

## Table cells

Markdown table cells are scanned as separate segments so a semicolon inside a
table does not collide with prose on the same line.

## Inline code

Inline code spans are replaced with a neutral token before scanning, so words
inside backticks cannot trigger rules.

## Irregular participles

The present-perfect heuristic covers both regular (`-ed`/`-en`) and a list of
common irregular past participles. It still defers to the modality prefix
check, so `may have failed` is safe while `has failed` is flagged.

## One word, one meaning

Only pairs where the members are genuinely interchangeable are grouped.
`error`, `fault`, and `failure` are distinct concepts and stay out.

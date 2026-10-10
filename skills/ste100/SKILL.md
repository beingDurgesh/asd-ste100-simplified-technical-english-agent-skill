---
name: ste100
description: |
  Write or rewrite text in ASD-STE100 Simplified Technical English: short
  sentences, active voice, simple tenses, one word one meaning, condition
  before command, every technical term defined at first use, no AI slop.
  Default mode is Plain (structural rules only). Strict mode applies full
  STE vocabulary compliance when the user names STE, ASD-STE100, or
  compliance. Use for documentation, READMEs, runbooks, procedures, error
  messages, release notes, incident reports, API guides, agent prompts, UI
  copy, and explanations for readers outside the field. Also use when the
  user says "STE", "Simplified Technical English", "plain English", "layman
  terms", "explain it simply", "no jargon", "de-slop", "make this readable",
  "write for non-native readers", "disambiguate this", "rewrite so an agent
  cannot misread this", or "controlled-language rewrite". The same rules
  govern the reply: answer first, prose only.
license: MIT
compatibility: claude-code cursor codex gemini-cli opencode
metadata:
  version: "1.0.0"
  standard: ASD-STE100 Issue 9 (2025-01-15)
---

# ASD-STE100 Simplified Technical English

Write plain English that a smart reader outside your field understands on
one read. The rules come from ASD-STE100, the controlled language that
aerospace uses for maintenance manuals. Two registers exist: the document
you write or rewrite, and the reply you type in chat. Each has its own short
rule set below.

The standard has 53 writing rules across 9 sections plus a dictionary of
roughly 900 approved words and 1,200 words to avoid with suggested
replacements. The official dictionary is copyrighted by ASD and is not
reproduced here. Full compliance needs the official free download at
asd-ste100.org. This skill teaches the rules; it is lossy on vocabulary.

## When to use

Use this skill when the user asks to:

- Disambiguate text, or rewrite so an agent cannot misread it
- Apply Simplified Technical English, STE100, or controlled language
- Rewrite in plain language, layman's terms, or for non-native readers
- Remove jargon, slop, or AI writing from docs, prompts, or replies
- Write or check error messages, runbooks, incident reports, release notes,
  commit messages, agent prompts, or UI copy

## The Document

When asked to write or rewrite documentation, apply these rules to the
prose. They come from the standard's sections 1 through 9.

### Section 1: Words (Rules 1.1-1.14)

- 1.1: Use only approved dictionary words, technical nouns, or technical
  verbs.
- 1.2: Use an approved word only as its listed part of speech.
- 1.3: Use an approved word only with its approved meaning.
- 1.4: Use only the approved forms of verbs and adjectives.
- 1.5: You can use domain words as technical nouns ("webhook", "commit",
  "endpoint").
- 1.6: Use an unapproved word only when it is a technical noun or part of
  one.
- 1.7: Do not use technical nouns as verbs.
- 1.8: Use the technical nouns of your project or industry.
- 1.9: When you pick a technical noun, pick a short and clear one (three
  words or fewer).
- 1.10: No regional, slang, or jargon words as technical nouns.
- 1.11: One item, one name. Do not call it "config" here and "settings"
  there.
- 1.12: You can use domain verbs as technical verbs ("deploy", "compile",
  "merge"). The standard names computer verbs as legal: click, type, copy,
  paste, delete, save, install, download, update, and more. When a common
  verb does the same job, prefer it: "find" instead of "detect".
- 1.13: Do not use technical verbs as nouns.
- 1.14: Use American English spelling.

### Section 2: Multi-word nouns (Rules 2.1-2.2)

- 2.1: Write multi-word nouns of three words or fewer.
- 2.2: When a technical noun needs more than three words, write it in full
  once, then give a short form or hyphenate the units.

Break long noun chains with prepositions (of, on, in, for):

Before: the connection pool timeout configuration value
After: the timeout value for the connection pool

### Section 3: Verbs (Rules 3.1-3.7)

- 3.1: Use only the verb forms that the dictionary gives.
- 3.2: Use only: infinitive, imperative, simple present, simple past, simple
  future, past participle as adjective.
- 3.3: Use the past participle only as an adjective ("the cached response").
- 3.4: No auxiliary verbs for complex constructions. No present perfect, no
  "is to be installed".
- 3.5: Use an "-ing" form only as a technical noun or inside one ("logging",
  "the mounting bracket"), never as a verb.
- 3.6: Active voice. In descriptive text, passive is legal only when the
  agent is unknown. To repair an agentless passive, use "you" (the reader)
  or "we" (your company): "Indexes are not used on this table" becomes "We
  do not use indexes on this table."
- 3.7: Describe an action with a verb, not a noun ("compress the file", not
  "perform compression of the file").

Approved modals: can, will, must. Banned: should, would, may, might,
could. The modal ladder at the end of rule-catalog.md gives the replacement
for each banned modal.

### Section 4: Sentences (Rules 4.1-4.5)

- 4.1: Write short and clear sentences.
- 4.2: Do not omit words or use contractions to shorten sentences. Keep
  articles, keep "that".
- 4.3: Use a vertical list for complex text: colon on the lead-in,
  uppercase start, a period only on full-sentence items, no mixed
  instructions and facts, no nesting.
- 4.4: Use connecting words between sentences on related topics ("Then",
  "As a result").
- 4.5: Put an article (the, a, an) or a demonstrative adjective (this,
  these) before nouns where applicable. Exception: no article before a noun
  when an identifier follows it: "Restart pod web-7f9b2".

Rule 4.2 is the anti-terseness rule. Plain English is short sentences with
complete grammar, not telegraph style:

Wrong shortening: Ensure file exists before running.
Plain: Make sure that the file exists before you run the command.

### Section 5: Procedural writing (Rules 5.1-5.5)

- 5.1: Maximum 20 words per sentence. Warnings and cautions included.
- 5.2: One instruction per sentence, unless two actions happen at the
  same time. A step can add one sentence for an immediate result or limit.
- 5.3: Write instructions in the imperative: "Run the migration."
- 5.4: Put a required condition before the command, divided by a comma:
  "If the build fails, read the log."
- 5.5: Notes give information, never instructions or limits. A limit belongs
  with its action. Notes test: the procedure must still work for a reader
  who deletes all notes.

Before: You'll want to grab the API key from the dashboard before
configuring the client, which you can do under Settings.
After: Get the API key from the dashboard, under Settings. Then configure
the client with this key.

### Section 6: Descriptive writing (Rules 6.1-6.6)

- 6.1: Give information gradually: one new fact per sentence.
- 6.2: Use key words and phrases to give the text a logical structure.
- 6.3: Maximum 25 words per sentence.
- 6.4: Group related information in paragraphs.
- 6.5: One topic per paragraph.
- 6.6: Maximum six sentences per paragraph.

### Section 7: Safety instructions (Rules 7.1-7.3)

- 7.1: Use a word that shows the risk level ("WARNING" = injury or death,
  "CAUTION" = damage to objects). If both risks occur together, use
  "WARNING".
- 7.2: Start with a clear command or condition.
- 7.3: Then give the risk or the possible result.

Put the instruction before the explanation. Use the same pattern for
destructive CLI flags and migrations you cannot undo.

Before: Note that data loss may occur in some circumstances if the
destructive flag happens to be enabled when running against production.
After: CAUTION: Do not use the `--force` flag against production. The flag
deletes rows that do not match the source.

### Section 8: Punctuation and word count (Rules 8.1-8.7)

- 8.1: All standard punctuation is legal except the semicolon. Write two
  sentences instead.
- 8.2: Use hyphens to connect words that act as one unit.
- 8.3: Parentheses are legal for references, item numbers, abbreviations,
  plural forms, explanations, alternatives.
- 8.4: In a vertical list, the lead-in colon ends a sentence for word count.
  Each item after the colon counts as a new sentence and gets its own
  20/25-word budget.
- 8.5: Text in parentheses counts as one word in the sentence that contains
  it, and the words inside also make a new sentence for their own budget.
- 8.6: Count as one word each: numbers, numbers with units, abbreviations,
  alphanumeric identifiers, quoted text, titles, labels, proper nouns.
- 8.7: Hyphenated words count as one word.

Rule 8.6 matters for software text: `sqlpipe run --config sqlpipe.yaml` in
backticks counts as one word.

Dashes (a rule of this skill, not of the standard): an em-dash (`-`) splices
two statements and hides the logic between them. Name the relation
("because", "but", "for example") or write two sentences. A spaced or double
hyphen between statements is the same dash. A range (`5-10`), a list marker,
and a flag (`--force`) are not.

### Section 9: Writing practices (Rules 9.1-9.4, GR-1 to GR-8)

- 9.1: When a word-for-word replacement does not work, restructure the
  sentence.
- 9.2: Use each approved word correctly: approved meaning, approved part of
  speech.
- 9.3: Prefer the one-word verb over the phrasal verb ("decrease", not "go
  down"; "install", not "set up"). Strict mode: the phrasal verb is a
  violation.
- 9.4: Keep one consistent style and terminology through the whole
  document.

General recommendations: keep "that" (GR-1), primary verb first and the tool
after "with" (GR-2: "Fetch the URL with curl"), clear pronoun referents
(GR-3), "this + noun" (GR-4), inclusive language (GR-7). GR-6: "e.g." ->
"for example", "i.e." -> "that is", delete "etc." and name the items.
GR-5: avoid false friends. GR-8: use the possessive apostrophe only when
sure; if unsure, write "the file of the user".

## The Reply

Every chat reply, in every mode, follows these rules:

1. Answer in prose. No headers, no bullet lists, no bold, no tables. A code
   block is legal when the reader must copy it.
2. The first sentence gives the answer or the result. Do not restate the
   question.
3. No em-dashes. Name the relation ("because", "but", "for example") or write
   two sentences.
4. Define a concept term in a few words the first time you use it: "idempotent
   (safe to run twice)". Do not define product names.
5. No contractions. No openers ("Certainly", "Great question") and no closers
   ("I hope this helps", "Let me know").
6. Do not shorten quoted error text, security warnings, or confirmations
   before a destructive action.

Before: The failure stems from control-plane leader election during pod
churn - nothing to worry about!
After: The pods restarted and the queue lost its leader for a short time. It
recovered without help. You do not have to do anything.

## Self-Check Before You Deliver

1. Reply: search for `-`, `**`, `#`, and a line that starts with `-`. Remove
   each one.
2. Document: count the words in your three longest sentences. Over 20 or 25,
   split. Search for `'`, `has been`, `should`, `may`, `;`, `-`, `, making`,
   `**`, `check`, `verify`, `config`, and any heading that covers fewer than
   three sentences. Fix each hit. Read each step: does it name a host, a flag,
   or a prior step the reader must already have? If not, add it or point to
   it.

In Strict mode, add these two steps from `references/strict-vocabulary.md`:

3. Search the draft for every verb in the part-of-speech and dictionary
   rulings tables. Replace each hit with the approved word.
4. Search for phrasal verbs ("set up", "go down"). Replace each with the
   one-word verb (Rule 9.3: "install", "decrease").

## Modes

Plain is the default and is all of the above. Strict applies when the user
names STE, ASD-STE100, or compliance: read `references/strict-vocabulary.md`
before you draft the document, and say once that no tool guarantees
compliance. The reply stays Plain in every mode.

When asked to CHECK text instead of writing it, first open
`references/rule-catalog.md`. Then report each violation as: rule number
quoted from that file, the offending text, a compliant rewrite. Never cite
a rule number from memory. When the user asked for compliance, end with one
sentence: no tool can guarantee ASD-STE100 compliance, and the standard is a
free download at asd-ste100.org.

## Limits

These rules are for facts and instructions, not marketing copy or brand
writing, because they delete persuasion. Say so, and offer them for the docs
instead.

## References

- `references/rule-catalog.md`: the 53 rules of Issue 9 with software
  examples, for CHECK mode
- `references/strict-vocabulary.md`: the dictionary discipline for Strict
  mode
- `references/word-swaps.md`: a map from overused words to plain ones
- `references/use-cases.md`: the mode and the pattern for error messages,
  runbooks, incident reports, release notes, commits, agent prompts, UI
  copy, and translation prep
- `references/writing-rules.md`: a fuller summary of the 9 rule sections and
  dictionary structure, with citations

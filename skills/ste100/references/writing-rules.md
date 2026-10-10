---
name: ste100-writing-rules
---

# ASD-STE100 Writing Rules - Summary and Sources

This file summarizes the public, official description of ASD-STE100
(Simplified Technical English). It paraphrases rule categories. It does not
reproduce the standard's text or its ~900-word dictionary verbatim. For the
authoritative document, request the free download at the official site.

## What ASD-STE100 Is

ASD-STE100 is a controlled natural language, first released in 1986 (as
AECMA Document PSC-85-16598) by what is now ASD (the Aerospace and Defense
Industries Association of Europe). It was built at the request of European
airlines - most staffed by non-native English speakers - who needed
maintenance documentation that could not be misread, because a misread
instruction on an aircraft can kill people. The standard is maintained by
the Simplified Technical English Maintenance Group (STEMG) and has been
free to download since Issue 6 (2013). The current edition is Issue 9
(January 2025).

## Structure

- 53 writing rules across 9 sections covering word choice, grammar,
  sentence structure, and style.
- A dictionary of roughly 900 approved words, each restricted to one
  meaning and one part of speech, plus roughly 1,200 words to avoid with
  suggested replacements.
- A terminology allowance: organizations may define their own dictionary of
  approved technical nouns and verbs beyond the base ~900 words, for
  domain-specific vocabulary the base dictionary cannot cover.

## Rule Categories (Paraphrased)

### Section 1 - Words (Rules 1.1-1.14)

- Use approved words only in their approved meaning and part of speech.
- Each word maps to exactly one meaning - do not rely on context to
  disambiguate a word that has several dictionary senses.
- Prefer the plainer, shorter, more common word over a formal or rare
  synonym.
- Use an approved verb for an action, not a noun derived from that verb
  (Rule 3.7).
- Do not make phrasal verbs by putting a verb and a preposition together
  (Rule 9.3). Their meaning is not predictable from the parts, and
  non-native readers and translation systems both mishandle them.

### Section 2 - Multi-word nouns (Rules 2.1-2.2)

- Write multi-word nouns of three words or fewer.
- When a technical noun needs more than three words, write it in full once,
  then give a short form or hyphenate the units.

### Section 3 - Verbs (Rules 3.1-3.7)

- Permitted forms: infinitive, imperative, simple present, simple past,
  simple future, and past participle used only as an adjective.
- No present perfect, past perfect, or other compound/auxiliary
  constructions. "We have received" is not allowed. "We received" is
  allowed.
- "-ing" forms are permitted only as a technical noun or as part of a
  technical noun, not as a verb form.

### Section 4 - Sentences (Rules 4.1-4.5)

- One instruction per sentence.
- Maximum ~20 words per sentence for procedures and instructions.
  Maximum ~25 words for descriptive text.
- Do not omit sentence parts (verb, subject, article) just to shorten the
  sentence - the standard explicitly warns that this creates ambiguity
  rather than clarity.
- Noun clusters (strings of nouns stacked as a modifier) are capped at 3
  words.
- Semicolons are not permitted at all (Rule 8.1): "You can use all standard
  English punctuation marks but not the semicolon (;)." Write separate
  sentences instead. Every other standard mark, including the em dash,
  remains permitted.

### Section 5 - Procedural writing (Rules 5.1-5.5)

- Maximum 20 words per sentence.
- One instruction per sentence unless two actions occur at the same time.
- Write instructions in the imperative (command) form.
- Put a required condition before the command, divided by a comma.
- Notes give information, never instructions or limits.

### Section 6 - Descriptive writing (Rules 6.1-6.6)

- Give information gradually: one new fact per sentence.
- Use key words and phrases to give the text a logical structure.
- Maximum 25 words per sentence.
- Group related information in paragraphs. One topic per paragraph.
- Maximum six sentences per paragraph.

### Section 7 - Safety instructions (Rules 7.1-7.3)

- Use a word that shows the risk level ("WARNING" = injury or death,
  "CAUTION" = damage to objects). If both risks occur together, use
  "WARNING".
- Start with a clear command or condition.
- Then give the risk or the possible result.

### Section 8 - Punctuation and word count (Rules 8.1-8.7)

- All standard punctuation is legal except the semicolon.
- Use hyphens to connect words that act as one unit.
- Parentheses are legal for references, item numbers, abbreviations,
  plural forms, explanations, alternatives.
- In a vertical list, the lead-in colon ends a sentence for word count.
- Text in parentheses counts as one word in the sentence that contains it.
- Count as one word each: numbers, numbers with units, abbreviations,
  alphanumeric identifiers, quoted text, titles, labels, proper nouns.
- Hyphenated words count as one word.

### Section 9 - Writing practices (Rules 9.1-9.4, GR-1 to GR-8)

- When a word-for-word replacement does not work, restructure the sentence.
- Use each approved word correctly: approved meaning, approved part of
  speech.
- Prefer the one-word verb over the phrasal verb.
- Keep one consistent style and terminology through the whole document.

General recommendations: keep "that" (GR-1), primary verb first and the
tool after "with" (GR-2), clear pronoun referents (GR-3), "this + noun"
(GR-4), inclusive language (GR-7). GR-6: "e.g." -> "for example", "i.e."
-> "that is", delete "etc." and name the items. GR-5: avoid false friends.
GR-8: use the possessive apostrophe only when sure.

## Why This Skill Repurposes STE for Agent Output

STE was designed to eliminate ambiguity for a reader who cannot ask a
follow-up question - a technician on a tarmac, working from a manual, with
no author to call. An AI agent parsing another agent's output, a tool
description, or a system message is in the same position: no back-channel
to resolve "does this passive-voice sentence mean the caller does X, or
the callee does X?" The same rule set that protects an airline mechanic
from a misread torque spec protects a downstream agent from a misread
instruction.

## Sources

- ASD-STE100 official site: https://www.asd-ste100.org/
- ASD-STE100 - About STE: https://www.asd-ste100.org/about_STE.html
- ASD Europe - Simplified Technical English: https://www.asd-europe.org/standards-specifications/simplified-technical-english/
- Simplified Technical English - Wikipedia: https://en.wikipedia.org/wiki/Simplified_Technical_English
- TechScribe - ASD-STE100 Simplified Technical English: https://www.techscribe.co.uk/techw/asd-simplified-technical-english.htm
- SKYbrary - Simplified Technical English (STE): https://skybrary.aero/articles/simplified-technical-english-ste
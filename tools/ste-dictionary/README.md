# ASD-STE100 word lists, made on your machine

This directory holds an extractor and a word-choice linter. It holds no
dictionary content. ASD-STE100 Issue 9 states on page 2 that no reproduction
of the standard, in whole or in part, is permitted without written authority
from ASD. So the repository ships the tool, and you make the word lists from
your own copy of the free PDF.

## Make the word lists

1. Request the free PDF at <https://www.asd-ste100.org/request.html>.
2. Convert it to text with layout columns preserved:

   ```
   pdftotext -layout -enc UTF-8 ASD-STE100_ISSUE9.pdf ste9.txt
   ```

3. Parse the dictionary:

   ```
   python3 parse_dict.py ste9.txt
   ```

   This writes `dict.json` with two lists:
   * `approved` — 794 entries, each `{word, pos, meaning}`.
   * `not_approved` — 1,245 entries, each `{word, pos, alternatives}`.

   The parser reads the layout text. Column 1 ([0:18]) holds the word and
   part of speech; column 2 ([18:40]) holds the meaning (approved words)
   or the UPPERCASE alternatives (not-approved words). The standard says
   a word in UPPERCASE letters is approved and a word in lowercase
   letters is not approved (page 2-0-9). Inflected forms such as
   `ACCEPTS,` and `ACCEPTED,` inherit the headword's status.

4. Emit the lists:

   ```
   python3 emit.py .
   ```

   This writes `approved.txt` (723 unique words) and
   `not-approved.tsv` (1,245 rows).

The output is deterministic. All four generated files are in `.gitignore`.
Do not commit them.

## Lint word choice

`skills/ste100/evals/ste_lint.py` measures the mechanical rules. It does not
see word choice. `ste_dict_lint.py` reads `not-approved.tsv` and reports each
word that the standard does not approve, with the approved alternatives. It
also counts the LLM-tell words from `skills/ste100/slop.tsv` as a separate
number.

```
python3 ste_dict_lint.py file.md
python3 ste_dict_lint.py --self-test
```

Known limit: the match is on the base form and simple inflections, with no
part-of-speech disambiguation. Numbers from this tool compare two texts run
through the same version. They are not a compliance verdict.

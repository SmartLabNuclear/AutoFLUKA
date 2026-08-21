# Fortran Columns and Spacing Rules

Use these rules to keep FLUKA and FLAIR parsing stable.

## Hard rules
- Put the card keyword in column 1 (no leading spaces).
- Use spaces only; never use tab characters.
- Keep newly authored lines at 80 characters or less.
- Keep continuation style consistent with local templates (`&` for continued lines).
- Use uppercase card names for readability and consistency with examples.

## Input alignment “gotchas” (fixed format)
- In fixed-format reading, **blanks inside numeric fields can be interpreted as zeros**. Avoid partially written numbers and avoid relying on “implicit zeros” for meaning.
- Avoid ambiguous numeric writing (for example, don’t leave “floating pieces” that could be parsed differently by different readers).
- Keep **keywords and particle/material tokens left-aligned** within their field and prefer **UPPERCASE** for card keywords.

## Practical layout rules
- Keep one space minimum between tokens; do not collapse region/material expressions into ambiguous text.
- Avoid “jammed” tokens where a label touches a number unless you are intentionally using a known-good pattern.
- For fixed-column cards, SDUM can be attached directly after the last numeric field **only if** it is a proven-safe local style and FLAIR still parses the numeric WHAT fields correctly (example: `... 3.0DOSEWAT`).
- In region lines, keep region name, NAZ, and boolean expression clearly separated:
  - `REGION_NAME   5     +BODY1 -BODY2`
- Keep comments on separate lines starting with `*`.

## Fixed-field mental model (WHATs + SDUM)
Most “normal” FLUKA cards behave like:
- **1 keyword**
- **up to 6 numeric fields** (WHAT(1)…WHAT(6))
- **1 trailing string field** (SDUM)

To keep authoring deterministic, prefer a style where each field is visually separated.
Use the alignment ruler line frequently when editing fixed-format inputs:

```text
*...+....1....+....2....+....3....+....4....+....5....+....6....+....7....+....8
```

Safe authoring pattern (do not rely on “glued” SDUM-on-number unless you must):

```text
CARDNAME      w1         w2         w3         w4         w5         w6         SDUM
```

Notes:
- The exact meaning and type of each WHAT depends on the card (some accept names as well as numbers).
- In numeric fields, leaving a field blank can be interpreted as zero in fixed-format reading; don’t use “half-written” numbers.

## Fixed-format field discipline (why “spillover” breaks runs)
When FLUKA reads cards in fixed format, a common mental model is:
- **A8**: card keyword (8-character string field)
- **2X**: spacing
- **6E10.\***: six numeric fields of fixed width (WHAT(1..6))
- **A8**: trailing string field (SDUM)

You will see this described in Fortran-style shorthand like: `A8, 2X, 6E10.*, A8`.

Practical takeaway:
- **Only put numbers in WHAT fields.** Region/material/scorer labels belong in SDUM (or in a card-specific name-enabled WHAT field, when you are copying a validated template).
- If an alphanumeric token (example: a region name like `TG`) shifts into a numeric WHAT field, FLUKA can throw “not a valid real number” errors at runtime.

Example failure mode to avoid (illustrative):
- A `RESNUCLEi` line where a region token accidentally lands in WHAT(3) instead of SDUM due to spacing.

## Name-length safety
- FLUKA can truncate identifiers in fixed-width contexts.
- For user-defined names (regions, materials, scorers), prefer <=8 characters unless a longer form is proven safe in your parser path.
- Use the exact same spelling in body/region/material definitions and references.

## Multi-line scoring formatting
- Preserve the same card grouping style used in your working files:
  - `USRBIN` lines come as a pair
  - `USRBDX` lines come as a pair
  - `USRTRACK` may span two lines
- Keep pair order unchanged when editing values.
- Do not insert placeholder tokens like `RAY` unless that token is explicitly valid for that card/signature.

### WHAT-field spillover prevention (common failure mode)
- Treat each card as: `CARD` + `WHAT(1..6)` + `SDUM`.
- If SDUM (labels like detector names) shifts left due to spacing, it can land in a WHAT field and cause errors/warnings.
- For scorer pairs (`USRBDX`, `USRBIN`, `USRTRACK`), keep the second line aligned and keep SDUM placement consistent across edits.
- When debugging, prefer clarity over density:
  - one region per `ASSIGNMA` line (temporarily)
  - keep SDUM as a separate token (space-separated), not glued to a number

### Continuation lines (scorers and long cards)
- If a card uses a continuation marker (often `&` in validated templates), keep it **in the same field position** used by that template.
- Do not append extra tokens after `&`.
- For paired scorers (`USRBIN`, `USRBDX`) keep both lines together and edit them as a unit.

## Free vs fixed input mode (authoring stability)
- FLUKA can be operated in a more **free** input style (via specific control cards/options), but many teams keep a **fixed-format discipline** because it makes mistakes easier to spot.
- Even if you adopt a freer style for general cards, keep your geometry/scoring blocks consistent with the style used by your validated examples.

## Quick pre-save checks
- Tabs: none
- Max length: <=80 for new outputs
- No trailing garbage tokens after `&`
- No split numeric tokens (for example, `0. 0`)
- Scorers: no alphabetic characters inside numeric WHAT fields
- `START` and `STOP` both present

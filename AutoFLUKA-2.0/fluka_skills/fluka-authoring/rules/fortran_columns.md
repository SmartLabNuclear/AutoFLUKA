# Fortran Columns and Spacing Rules

Use these rules to keep FLUKA and FLAIR parsing stable.

## Hard rules
- Put the card keyword in column 1 (no leading spaces).
- Use spaces only; never use tab characters.
- Keep newly authored lines at 80 characters or less.
- Keep continuation style consistent with local templates (`&` for continued lines).
- Use uppercase card names for readability and consistency with examples.

## Practical layout rules
- Keep one space minimum between tokens; do not collapse region/material expressions into ambiguous text.
- For fixed-column cards, SDUM can be attached directly after the last numeric field if column alignment is correct (for example, `... 3.0DOSEWAT`).
- In region lines, keep region name, NAZ, and boolean expression clearly separated:
  - `REGION_NAME   5     +BODY1 -BODY2`
- Keep comments on separate lines starting with `*`.

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

## Quick pre-save checks
- Tabs: none
- Max length: <=80 for new outputs
- No trailing garbage tokens after `&`
- No split numeric tokens (for example, `0. 0`)
- `START` and `STOP` both present

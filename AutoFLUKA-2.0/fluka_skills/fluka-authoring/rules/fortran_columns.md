# Fortran Columns and Spacing Rules

FLUKA reads every card in fixed columns. A value in the wrong columns is either rejected or, worse, silently read as a different number. Write and repair cards with `fluka_card_formatter_tool` instead of spacing them by hand. The formatter only places values in columns; take each field's meaning and order from the closest working example first, then format.

## The column layout

```text
*...+....1....+....2....+....3....+....4....+....5....+....6....+....7....+....8
KEYWORD   WHAT(1)   WHAT(2)   WHAT(3)   WHAT(4)   WHAT(5)   WHAT(6)   SDUM
cols 1-10 11-20     21-30     31-40     41-50     51-60     61-70     71-80
```

- **Keyword**: starts in column 1. FLUKA reads columns 1-8 and skips 9-10, so no value may start before column 11.
- **WHAT(1)…WHAT(6)**: six fields of exactly 10 columns each.
- **SDUM**: starts exactly in column 71 and may run to column 80. FLUKA keeps leading blanks as part of SDUM, so a name started later is read with blanks in front.

## The rule: right-align every value to the last column of its field

Every value must end exactly at column 20, 30, 40, 50, 60 or 70. Once it is right-aligned, any notation works:

```text
*...+....1....+....2....+....3....+....4....+....5....+....6....+....7....+....8
START         1000.0
START        1.0E+03
START       100000.0
RANDOMIZ         1.0 54217137.
EMFCUT      -1.0E-05   1.0E-05   1.0E-05                              PROD-CUT
BEAM          -0.003       0.0   10000.0       0.0       0.0       1.0PHOTON
```

Decimal, integer and exponent forms (`1000.0`, `1000`, `1.0E+03`, `1.0E-6`) are all accepted when right-aligned. The exponent is never the problem; the position is.

## SDUM touching WHAT(6) is correct

When WHAT(6) is used it ends at column 70 and SDUM starts at column 71, so the two touch: `1.0PHOTON`, `314.159OUTFLU`, `0.0CONCRETE`. That is the correct layout, not a merged token. Do not insert a space: it moves SDUM to column 72, which aborts the run for BEAM.

## Names in WHAT fields

Some cards take names in WHAT fields: regions, materials and particles in `ASSIGNMA`, `EMFCUT`, `USRBDX`, `DETECT` and `COMPOUND`. A name must also stay inside its own 10-column field; right-align it like a number, as FLAIR does. Keep user-defined names to 8 characters or fewer.

## Other hard rules
- Spaces only; never tab characters.
- At most 80 characters per line; FLUKA ignores everything after column 80.
- Uppercase card keywords.
- Comments on their own line starting with `*`.
- The line after `TITLE` is the title text; never put a card there.

## Check before running
- `fluka_inp_validator_tool` reports every misplaced value, including the ones FLUKA would silently misread, and the executor refuses to run a deck that has them.
- When reading a card by eye, put the ruler line above it: `*...+....1....+....2....+....3....+....4....+....5....+....6....+....7....+....8`.

## What a misplaced value does (verified with the installed FLUKA)

| Card as written | What FLUKA does |
|---|---|
| `START          1000.0` (value ends at column 21) | Rejected: "The 2th field 0 … does not contain a valid formatted fortran real number" |
| `START       1.0E+03` (value ends at column 19) | Rejected: an integer or exponent followed by blanks is ambiguous under the blank=0 rule |
| `START          500000.0` (columns 16-23) | **Runs 50,000 primaries with no error**: WHAT(1) holds `50000`, WHAT(2) holds `0.0` |
| `START    1000.0` (value starts at column 10) | **Runs FLUKA's default 5,000 primaries with no error**: column 10 is skipped, WHAT(1) reads 0 |
| `RANDOMIZ         1.0   54217137.0` | **Seed silently read as 5421713** |
| USRTRACK volume `523.599` written across columns 56-62 | **Volume read as 523.5 and 99,120 energy bins instead of 120**, no error |
| BEAM with `PHOTON` starting at column 72 or 73 | Abort: UNKNOWN PROJECTILE |
| Scorer name `NTRKWAT` starting at column 74 | Accepted, but the detector is named `   NTRKWAT` (with the blanks) in the output |

The silent cases are the dangerous ones: the run completes and the numbers look plausible. A value that is not right-aligned is wrong even when FLUKA accepts it.

- **Never trust visual spacing.** `START          100.0` and `START          1000.0` look alike; the first ends at column 20 and is correct, the second spills into WHAT(2) and is rejected.
- **Never retype a value in place.** Changing `1000.0` to `100000.0` without re-aligning pushes it across the field boundary. Rewrite the whole card with `fluka_card_formatter_tool`.

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

### Continuation lines (scorers and long cards)
- A continuation card carries `&` in SDUM, at column 71.
- Do not append extra tokens after `&`.
- For paired scorers (`USRBIN`, `USRBDX`) keep both lines together and edit them as a unit.

## Free vs fixed input mode (authoring stability)
- FLUKA can be operated in a **free** input style (via specific control cards/options), but this project keeps a **fixed-format discipline** because misplaced values are then detectable.
- Even if you adopt a freer style for general cards, keep your geometry/scoring blocks consistent with the style used by your validated examples.

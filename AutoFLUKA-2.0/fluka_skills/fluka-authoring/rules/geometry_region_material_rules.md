# Geometry, Region, and Material Rules

These rules prevent the region parsing and assignment errors seen in FLAIR logs.

## Geometry block structure
- Start with `GEOBEGIN ... COMBNAME`.
- Define bodies first (e.g., `RPP`, `SPH`, `RCC`, planes).
- Close body section with `END`.
- Define regions as boolean combinations of bodies.
- Close region section with `END`, then `GEOEND`.

## Region expression rules
- `+BODY` means inside, `-BODY` means outside.
- Use `|` for union when needed.
- Ensure every referenced body exists exactly as named.
- Keep region expression tokenized with spaces:
  - good: `AIR  5     +AIRBOX -WATBOX`
  - bad: `AIR 5 +AIRBOX-WATBOX` (easy to misread/parse)

## Region hierarchy guidance
- Typical robust stack:
  - outer boundary (`BLCKHOLE`)
  - vacuum shell
  - ambient region (`AIR`)
  - target/detector regions
- Order and boolean signs must make regions non-overlapping unless intentionally shared.

## Material definition and assignment
- Prefer FLUKA built-ins (`BLCKHOLE`, `VACUUM`, `AIR`, `WATER`) unless custom composition is required.
- If custom materials are required, define via `MATERIAL` and `COMPOUND` before `ASSIGNMA`.
- Every transport-relevant region must be assigned exactly once through `ASSIGNMA`.
- In `ASSIGNMA`, verify both names:
  - material exists
  - region exists

## Name consistency safeguards
- Keep region/material identifiers short and consistent to avoid fixed-width truncation confusion.
- Avoid near-colliding names such as `regWAT4` vs `regWA`.
- Reuse one naming scheme across bodies/regions/materials (for example: `body*`, `reg*`, semantic material names).

## Error-to-fix map
- `Bad alignment in region definition`: reformat region line spacing and token separation.
- `material XXXX is not defined`: material token mismatch or truncation; fix name and definition order.
- `Region 'XXXX' is not defined`: `ASSIGNMA` references a typo/truncated region name.
- `Region ... is not assigned any material`: add missing `ASSIGNMA`.

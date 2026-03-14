# Card Order and Required Cards

Follow this sequence unless a validated template requires a deliberate variation.

## Canonical order
1. `TITLE`
2. `DEFAULTS` (or explicit physics block if intentionally custom)
   - Use an exact, valid defaults keyword (for example `HADROTHE` or `PRECISIO`), with no extra prefix/suffix characters.
3. Beam definition:
   - `BEAM`
   - `BEAMPOS`
   - `BEAMAXES` (when directional control is needed)
4. Geometry block:
   - `GEOBEGIN ... COMBNAME`
   - body definitions
   - `END`
   - region definitions
   - `END`
   - `GEOEND`
5. Material definitions:
   - `MATERIAL` / `COMPOUND` as needed
6. Material assignment:
   - `ASSIGNMA` for each region
7. Physics/transport controls:
   - e.g., `EMFCUT`, `PHYSICS`, `MULSOPT`, `EMFFIX`, `PART-THR` (only when valid for the model)
8. Scoring cards:
   - e.g., `USRBIN`, `USRTRACK`, `USRBDX`, `DETECT`
9. Run control:
   - `RANDOMIZ`
   - `START`
   - `STOP`

## Required minimum for runnable transport input
- One valid source (`BEAM` + position).
- One valid geometry (`GEOBEGIN`/`GEOEND`) with at least one physical region.
- At least one `ASSIGNMA` per defined region participating in transport.
- Run termination cards (`START`, `STOP`).

## Strong recommendations
- Include an outer boundary and `BLCKHOLE` region for clean particle termination.
- Include vacuum/air wrapper regions when the physical model needs external space.
- Keep scoring after geometry/material setup so region references are already defined.

## Common failure patterns to avoid
- `ASSIGNMA` appears before region names are defined.
- Region/material name mismatch caused by truncation or typo.
- Missing second line for paired scoring cards.
- `STOP` missing or placed before run/scoring setup.

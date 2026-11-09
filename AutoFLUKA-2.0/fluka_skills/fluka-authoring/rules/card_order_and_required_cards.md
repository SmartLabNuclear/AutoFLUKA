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

## BEAM energy/momentum sign convention
- `BEAM` WHAT(1) is signed: **negative = kinetic energy in GeV**, **positive = momentum in GeV/c**.
- For a massless particle (photon), kinetic energy and momentum are numerically identical, so a wrong sign on a photon `BEAM` card often produces a plausible-looking result and the sign alone is rarely the actual bug for that particle type. Flip-flopping the sign repeatedly on the same symptom wastes a repair cycle — check source position, direction (`BEAMAXES`), and scoring setup first, before re-trying the sign.
- Example minimum photon source (point source, pencil beam along +z, 1 MeV kinetic energy):
  ```text
  BEAM          -0.001                                                  PHOTON
  BEAMPOS          0.0       0.0     -10.0
  ```
  See `working_examples/photon_1mev_lead_slab/` for a complete, verified minimal deck.

## Isotropic point source (no SOURCE routine needed)
- `BEAM` WHAT(3) is the beam divergence in mrad. Above 2000π mrad (about 6283.2; `10000.0` is the usual choice) FLUKA emits the primaries isotropically over 4π and ignores the direction cosines on `BEAMPOS` (FLUKA manual, BEAM Note 7 and BEAMPOS Note 4).
- Keep WHAT(4) = WHAT(5) = 0 (zero beam width) for a true point, and put the point in `BEAMPOS`:
  ```text
  *...+....1....+....2....+....3....+....4....+....5....+....6....+....7....+....8
  BEAM          -0.003       0.0   10000.0       0.0       0.0       1.0PHOTON
  BEAMPOS          0.0       0.0       0.0
  ```
- This is standard card-level FLUKA. Do not write a `SOURCE` user routine to get isotropy. See `working_examples/photon_3mev_iso_pb_sphere/` for a verified deck.

## Required minimum for runnable transport input
- One valid source (`BEAM` + position).
- One valid geometry (`GEOBEGIN`/`GEOEND`) with at least one physical region.
- At least one `ASSIGNMA` per defined region participating in transport.
- Run termination cards (`START`, `STOP`).

## Strong recommendations
- Include an outer boundary and `BLCKHOLE` region for clean particle termination.
- Fill the space between target and that outer boundary with `VACUUM` by default; use `AIR` only when the case explicitly requires it (see `fluka-authoring/rules/geometry_region_material_rules.md`, "Outer boundary and filler medium rule").
- Keep scoring after geometry/material setup so region references are already defined.

## Common failure patterns to avoid
- `ASSIGNMA` appears before region names are defined.
- Region/material name mismatch caused by truncation or typo.
- Missing second line for paired scoring cards.
- `STOP` missing or placed before run/scoring setup.
- A `RANDOMIZ` seed that does not end at column 30. `RANDOMIZ         1.0    54217137.` (ends at column 33) is silently read as seed 542171; `RANDOMIZ         1.0   54217137.0` as 5421713. Correct: `RANDOMIZ         1.0 54217137.` (a right-aligned integer seed such as `    145789` also works).
- A `START` NPS that does not end at column 20. `START          1000.0` is rejected, and `START          100000.0` silently runs 10,000 primaries. Correct: `START         1000.0`, `START       100000.0`, or `START        1.0E+05`; the notation does not matter once the value is right-aligned.
- Any value spaced by hand: use `fluka_card_formatter_tool` and see `fortran_columns.md`.

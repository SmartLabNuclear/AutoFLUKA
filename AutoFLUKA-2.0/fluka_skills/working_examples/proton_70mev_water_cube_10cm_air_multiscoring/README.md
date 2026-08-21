# proton_70mev_water_cube_10cm_air_multiscoring

## Summary
Validated proton transport example for a 70 MeV beam in air irradiating a centered 10 cm water cube with multi-scoring cards.

## Source
Imported from successful run artifacts in `test_run_with_autofluka/test1_70meVprotons`.

## What This Input Includes
- Beam: 70 MeV protons (`BEAM ... PROTON`) from upstream (`BEAMPOS z = -30.0 cm`).
- Geometry: outer boundary, air region, and centered 10 cm water cube (`-5.0 to +5.0` cm in x/y/z).
- Materials/assignment: `BLCKHOLE`, `AIR`, and `WATER` with combinatorial geometry regions.
- Scoring:
  - `USRBIN` dose mesh (unit 30)
  - `USRTRACK` proton track-length in water (unit 31)
  - `USRBDX` boundary crossing from air to water (unit 32)
  - `USRBIN` energy deposition mesh (unit 33)
- Run control: `RANDOMIZ`, `START`, `STOP`.

## Canonical Input
- `proton_70mev_water_cube_10cm_air_multiscoring.inp`

# proton_70mev_water_sphere_5cm_air_multiscoring

## Summary
Validated proton transport example for a 70 MeV beam in air irradiating a centered 5 cm-radius water sphere with multi-scoring cards.

## Source
Imported from successful run artifacts in `test_run_with_autofluka/test3`.

## What This Input Includes
- Beam: 70 MeV protons from upstream (`BEAMPOS z = -25.0 cm`).
- Geometry: outer boundary, air region, and centered water sphere (`SPH`, radius 5.0 cm).
- Materials/assignment: `BLCKHOLE`, `AIR`, and `WATER`.
- Scoring:
  - `USRBIN` dose mesh around sphere (unit 30)
  - `USRTRACK` proton track-length in water region (unit 31)
  - `USRBDX` boundary crossing from air to water (unit 32)
  - `USRBIN` energy deposition mesh (unit 33)
- Run control: `RANDOMIZ`, `START`, `STOP`.

## Canonical Input
- `proton_70mev_water_sphere_5cm_air_multiscoring.inp`

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
  - `USRTRACK` proton track-length in water region (unit 31), volume 523.599 cm³ (4/3·π·5³) in WHAT(5)
  - `USRBDX` boundary crossing from air to water (unit 32), sphere area 314.159 cm² (4π·5²) in WHAT(6)
  - `USRBIN` energy deposition mesh (unit 33)
- Run control: `RANDOMIZ`, `START`, `STOP`.

## Canonical Input
- `proton_70mev_water_sphere_5cm_air_multiscoring.inp`

## Detector normalization
FLUKA does not compute detector areas or volumes. They are set in the cards, so `USRTRACK` and `USRBDX` results are per cm². Updated 2026-10-18: the `USRTRACK` volume had spilled across a field boundary, and FLUKA silently read it as 523.5 cm³ with 99,120 energy bins instead of 523.599 cm³ and 120 bins. The cards are now right-aligned to FLUKA's fixed columns, and the `USRBDX` area, previously left at FLUKA's 1.0 default, is set.

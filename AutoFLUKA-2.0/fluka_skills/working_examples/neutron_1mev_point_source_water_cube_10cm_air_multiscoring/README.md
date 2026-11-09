# neutron_1mev_point_source_water_cube_10cm_air_multiscoring

## Summary
Validated neutron transport example for a monoenergetic 1 MeV point source in air irradiating a centered 5 cm water cube with multi-scoring cards. (The folder name says 10 cm; the deck's cube is 5 cm, ±2.5 cm.)

## Source
Imported from successful run artifacts in `test_run_with_autofluka/test7_1MeVneutrons`.

## What This Input Includes
- Source: monoenergetic 1 MeV neutrons (`BEAM ... NEUTRON`) from upstream.
- Geometry: outer boundary, air region, and centered 5 cm water cube (`-2.5 to +2.5` cm); `USRTRACK` volume 125 cm³ and `USRBDX` area 150 cm² match it.
- Materials/assignment: `BLCKHOLE`, `AIR`, and `WATER`.
- Scoring:
  - `USRTRACK` neutron track-length in water (unit 31)
  - `USRBDX` neutron boundary crossing from air to water (unit 32)
  - `USRBIN` energy deposition mesh (unit 33)
  - `USRBIN` dose mesh (unit 34)
- Run control: `RANDOMIZ`, `START`, `STOP`.

## Canonical Input
- `neutron_1mev_point_source_water_cube_10cm_air_multiscoring.inp`

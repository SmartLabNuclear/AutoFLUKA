# neutron_1mev_point_source_water_cube_10cm_air_multiscoring

## Summary
Validated neutron transport example for a monoenergetic 1 MeV point source in air irradiating a centered 10 cm water cube with multi-scoring cards.

## Source
Imported from successful run artifacts in `test_run_with_autofluka/test7_1MeVneutrons`.

## What This Input Includes
- Source: monoenergetic 1 MeV neutrons (`BEAM ... NEUTRON`) from upstream.
- Geometry: outer boundary, air region, and centered 10 cm water cube (`-5.0 to +5.0` cm).
- Materials/assignment: `BLCKHOLE`, `AIR`, and `WATER`.
- Scoring:
  - `USRTRACK` neutron track-length in water (unit 31)
  - `USRBDX` neutron boundary crossing from air to water (unit 32)
  - `USRBIN` energy deposition mesh (unit 33)
  - `USRBIN` dose mesh (unit 34)
- Run control: `RANDOMIZ`, `START`, `STOP`.

## Canonical Input
- `neutron_1mev_point_source_water_cube_10cm_air_multiscoring.inp`

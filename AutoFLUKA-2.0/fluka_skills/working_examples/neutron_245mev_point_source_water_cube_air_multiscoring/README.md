# neutron_245mev_point_source_water_cube_air_multiscoring

## Summary
Self-contained neutron transport example for a monoenergetic 2.45 MeV point source in air irradiating a centered 10 cm water cube, with multi-scoring for fluence, boundary transport, dose, and energy deposition.

## Problem Statement
Created from this user request:
"Please generate a complete, self-contained, runnable FLUKA input file for the following problem. Goal: Simulate a monoenergetic point neutron source in air irradiating a water cube. Geometry and source: Point source: NEUTRON, monoenergetic 2.45 MeV (D-D neutron energy). Source position is (0.0, 0.0, -20.0 cm). No need for a source routine; define a monoenergetic neutron source. Water phantom is a cube centered at the origin, side = 10 cm (x,y,z from -5.0 to +5.0 cm). The surrounding medium: AIR. Add a proper outer boundary, a BLACKHOLE region as outermost termination. Use valid combinatorial geometry and region/material assignments. Physics and transport: Use appropriate FLUKA defaults/physics for neutron transport and secondaries. Include appropriate production/transport thresholds where needed. Keep cards physically consistent for this neutron problem. Scoring (use scorer unit numbers >= 30 BIN): 1) Neutron track-length fluence in water region (USRTRACK), unit 31. 2) Neutron boundary-crossing fluence/current from AIR to WATER (USRBDX), unit 32. 3) Energy deposited in the cube using mesh scoring (USRBIN ENERGY), unit 33. 4) Dose in/around the cube using mesh scoring (USRBIN DOSE), unit 34. Run control: Use 5,000,000 Primaries, and include RANDOMIZ, START, STOP. Pay attention to strict formatting requirements: FLUKA fixed-format/Fortran-style spacing. Card names start in column 1. Region alignment must be parser-safe with no tabs. Keep ALL lines length <= 80 chars and ensure continuation lines are valid where required. Validation: Run the validator tool on the generated file before finalizing. If the validator reports issues, auto-correct once and re-validate. Save final file as: test_245MeV_neutrons_water_cube.inp. in the provided working directory."

## What This Input Includes
- Source and particle: monoenergetic 2.45 MeV neutrons with `BEAM ... NEUTRON`.
- Geometry: outer boundary box, surrounding air region, and centered water cube (`-5.0 to +5.0` cm in x/y/z).
- Region/material assignments with `BLCKHOLE`, `AIR`, and `WATER`.
- `USRTRACK` neutron track-length fluence in water (unit 31).
- `USRBDX` boundary-crossing neutron fluence/current from air to water (unit 32).
- `USRBIN` energy deposition mesh around the water cube (unit 33).
- `USRBIN` dose mesh around the water cube (unit 34).
- Run control with `RANDOMIZ`, `START 5000000.0`, and `STOP`.

## Canonical Input
- `neutron_245mev_point_source_water_cube_air_multiscoring.inp`

## Note
The canonical input preserves the exact currently validated file content copied from `test5_neutrons/Results/test_245MeV_neutrons_water_cube_01.inp`.

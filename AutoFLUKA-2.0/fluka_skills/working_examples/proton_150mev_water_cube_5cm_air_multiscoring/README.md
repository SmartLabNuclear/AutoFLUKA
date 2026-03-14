# proton_150mev_water_cube_5cm_air_multiscoring

## Summary
Self-contained proton transport example for a 150 MeV beam incident from 20 cm upstream onto a 5 cm x 5 cm x 5 cm water phantom in air.

## Problem Statement
Created from this user request:
"Please generate a self-contained, runnable FLUKA input of a 150 MeV proton beam 20 cm from a water phantom, a cube of sides 5cm. the surrounding is air. Score the dose, track length, fluence, and the energy deposited in the cube. Pay attention do Fortran column and space syntax and rules, production and transport thresholds and appropriate Physics, material and scoring. Use 5000000 primaries. Save the input in the given directory.

## What This Input Includes
- Beam: 150 MeV protons, source 20 cm upstream (`BEAMPOS z = -20.0`).
- Geometry: world, air region, and a centered 5 cm water cube (`-2.5 to +2.5` cm in x/y/z).
- Physics/transport setup: `DEFAULTS`, `EMFCUT`, and `MULSOPT` cards.
- `USRBIN` dose mesh around the water cube (unit 30).
- `USRTRACK` track-length scoring in water (unit 31).
- `USRBDX` boundary-crossing fluence from air to water (unit 32).
- `USRBIN` energy deposition mesh around the water cube (unit 33).
- Primary histories are set by `START` in the canonical file (currently `5000000`).

## Canonical Input
- `proton_150mev_water_cube_5cm_air_multiscoring.inp`

## Note
The canonical input preserves the exact currently validated file content used in this codebase.

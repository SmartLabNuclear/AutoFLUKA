# pion_fluence_current_beryllium_3slabs

## Summary
Validated pion transport example for a three-slab beryllium target with pion fluence and boundary-current scoring.

## Source
Promoted from a validated internal execution record and published here as a canonical, shareable working example.

## What This Input Includes
- Physics preset: `DEFAULTS HADROTHE`.
- Beam: `PION+` with `BEAM -3.000E-01` (300 MeV/c momentum), source at `BEAMPOS (0, 0, -9.0 cm)`.
- Geometry:
  - World box: `-100 to +100 cm` in x/y/z.
  - Vacuum shell and inner airbox.
  - Three Be slabs along +z, each `2 cm x 2 cm` transverse and `3 cm` thick:
    - slab1: `z = 0.0 to 3.0 cm`
    - slab2: `z = 3.0 to 6.0 cm`
    - slab3: `z = 6.0 to 9.0 cm`
  - Total target length: `9 cm`.
- Materials/regions:
  - `BERYLLIU` assigned to `regUP`, `regMID`, `regDWN`.
  - `AIR` assigned to upstream/surrounding/downstream regions.
  - `VACUUM` and `BLCKHOLE` outer regions.
- Scoring:
  - `USRTRACK` pion fluence in `regUP`, `regMID`, `regDWN`, and `regAIR` (units `-30` to `-33`).
  - `USRBDX` pion current (`WHAT(1)=16.0`) across:
    - entrance (`regAUP -> regUP`, unit `-34`)
    - slab1/slab2 interface (`regUP -> regMID`, unit `-35`)
    - slab2/slab3 interface (`regMID -> regDWN`, unit `-36`)
    - exit (`regDWN -> regADN`, unit `-37`)
  - Scoring energy bounds for all listed scorers: `1.0E-6 to 0.12 GeV`, `120` bins.
- Run control: `RANDOMIZ 145789`, `START 200000`, `STOP`.

## Canonical Input
- `pion_fluence_current_beryllium_3slabs.inp`


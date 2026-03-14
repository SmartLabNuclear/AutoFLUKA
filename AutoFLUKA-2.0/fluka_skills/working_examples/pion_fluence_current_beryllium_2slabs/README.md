# pion_fluence_current_beryllium_2slabs

## Summary
Validated charged-pion scoring case for a proton-irradiated beryllium target split into two slabs along the beam axis.

## Source
Promoted from a validated internal execution record and published as a canonical, shareable working example.

## What This Input Includes
- Beam:
  - Primary particle: `PROTON`
  - `BEAM 50.E+00 PROTON`
  - Source position: `BEAMPOS (0.0, 0.0, -50.0 cm)`
- Geometry:
  - Outer black-hole boundary and enclosing vacuum region.
  - Beryllium target body: `x,y = -10 to +10 cm`, `z = 0 to +5 cm`.
  - Target split plane: `XYP z=2.5 cm`, creating two slabs:
    - upstream slab (`regBE3`): `z = 0.0 to 2.5 cm`
    - downstream slab (`regBE4`): `z = 2.5 to 5.0 cm`
- Materials:
  - `BERYLLIU` assigned to both target slabs (`regBE3`, `regBE4`)
  - `VACUUM` assigned to surrounding region
  - `BLCKHOLE` assigned to external boundary region
- Thresholds / physics cards:
  - `EMFCUT -0.010 0.010 1.0 BERYLLIU PROD-CUT` (10 MeV production threshold as documented in-card)
  - `SCORE ENERGY BEAMPART`
- Scoring:
  - `USRBDX` pion boundary fluence across slab interface (`regBE3 -> regBE4`, unit `-46`, label `piFluenUD`)
  - `USRBDX` pion boundary current across slab interface (`regBE3 -> regBE4`, unit `-47`, label `piCurrUD`)
  - `USRTRACK` pion track-length fluence in upstream slab (`regBE3`, unit `-48`, label `piFluenU`)
  - `USRTRACK` pion track-length fluence in downstream slab (`regBE4`, unit `-49`, label `piFluenD`)
  - `USRBIN` 3D pion fluence map (`PIONS+-`, unit `-50`, label `piFluBin`)
    - Mesh bins: `50 x 50 x 50`
    - Extents: `x=-50..+50 cm`, `y=-50..+50 cm`, `z=-10..+60 cm`
  - `USRBIN` 3D deposited-energy map (`ENERGY`, unit `-51`, label `Edeposit`)
    - Mesh bins: `10 x 10 x 5`
    - Extents: `x=-10..+10 cm`, `y=-10..+10 cm`, `z=0..+5 cm`
- Run control:
  - `RANDOMIZ 1.0 100`
  - `START 1000.0`
  - `STOP`

## Canonical Input
- `pion_fluence_current_beryllium_2slabs.inp`


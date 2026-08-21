# Case: USRBIN energy density to dose (Gy) via COMSCW

## Purpose

This worked example follows the FLUKA manual's common `COMSCW` application: convert **energy density** scored by `USRBIN` into **dose in gray (Gy)** by dividing by the local material density at each deposition step.

It is pseudocode and workflow guidance only — not a bundled Fortran template or copied manual source.

## Problem statement

A voxelized phantom mesh uses `USRBIN` to score energy density (MeV/cm³ per primary, per FLUKA normalisation). The user wants output proportional to **absorbed dose in Gy** in each voxel, including voxels that straddle material boundaries where effective density varies step by step.

`COMSCW` applies the conversion at scoring time using `MEDIUM(MREG)` and `RHO(material)` from `flkmat.inc`.

## Prerequisites

- `USRBIN` energy-density binning configured.
- `USERWEIG` with `WHAT(6) > 0` (see `COMSCW_USERWEIG_ACTIVATION.md`).
- Custom `comscw.f` linked.
- Materials and densities assigned correctly in the geometry deck.

## Physics concept

Deposited energy per mass relates to dose. For a scoring step in region `MREG` with material \(m\) and density \(\rho_m\) (g/cm³), a multiplicative factor on the deposited energy density score can be formed using the electron charge constant `ELCMKS` from FLUKA includes — as described conceptually in manual §13.2.2 (p. 402).

The manual presents this pattern for `ISCRNG = 1` (energy density binning) specifically.

## Implementation plan (pseudocode)

```text
INCLUDE dblprc.inc, dimpar.inc, iounit.inc
INCLUDE scohlp.inc
INCLUDE flkmat.inc

LSCZER = .FALSE.

IF ISCRNG == 1 THEN
    ! Energy density binning active
    mat = MEDIUM(MREG)
    COMSCW = ELCMKS * 1.D12 / RHO(mat)
ELSE
    COMSCW = 1.0
ENDIF

RETURN
```

Notes:

- `ISCRNG = 2` would be star density — do not apply the Gy formula unless intentionally desired.
- Restrict to a specific `JSCRNG` if multiple USRBIN binnings exist.
- Verify `ELCMKS` and the `1.D12` scaling against the installed manual and your target output units.

## Optional refinements

| Refinement | Pseudocode idea |
|---|---|
| Limit to one USRBIN | `IF JSCRNG /= N THEN COMSCW = 1` |
| Particle filter | `IF IJ /= desired THEN LSCZER = .TRUE.` |
| Minimum density guard | `IF RHO(mat) < rho_min THEN COMSCW = 0` with care |

## Validation strategy

| Step | Action |
|---|---|
| 1 | Run with `COMSCW = 1` — save baseline USRBIN |
| 2 | Run with uniform `COMSCW = 2` in energy branch — bins should ≈ 2 × baseline |
| 3 | Enable density-based formula in single-material region — compare to hand calc |
| 4 | Check boundary voxel between two materials — weighted average should improve vs post-processing with single bulk density |

## Output interpretation

- FLUKA normalises results to **unit primary weight** regardless of `BEAM` weight.
- Printed USRBIN titles may still say "energy density" — document that values are dose-weighted.
- Compare against analytical single-region dose only after confirming unit chain.

## When not to use this pattern

| Situation | Better approach |
|---|---|
| Track-length fluence mesh | `FLUSCW`, not `COMSCW` |
| Birks quenching in scintillator | `TCQUENCH` on binning |
| `DETECT` pulse-height spectrum | `DETSCW` / `DETECT` workflow |
| Fluence → dose equivalent | `FLUSCW` on `USRTRACK` / `USRBDX` |
| Offline conversion sufficient | Post-process `.bnn` with density map |

## AutoFLUKA notes

- `subroutine_paths: ["comscw.f"]`
- `test-1`: flat `COMSCW = 1`
- `test-2`: dose formula in one material region
- Record material assignments in case manifest for reproducibility

## Manual references

- `COMSCW` dose example pattern, Sec. 13.2.2, p. 402
- `USERWEIG` output interpretation notes, p. 272
- `FLKMAT` / `MEDIUM`, Sec. 13.1.1
- Parent guide: `../COMSCW_GUIDE.md`

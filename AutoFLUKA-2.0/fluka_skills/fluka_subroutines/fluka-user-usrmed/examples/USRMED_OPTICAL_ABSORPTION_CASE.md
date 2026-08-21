# Case: In-medium optical photon absorption via USRMED weight reduction

## Purpose

This worked example implements the manual's primary **in-medium** `USRMED` pattern: when `MREG = NEWREG`, the user may change **`WEE` only**. A common application is simulating **bulk absorption** of optical photons by reducing weight during transport in an absorbing material.

Pseudocode only — not a bundled Fortran template.

## Problem statement

Optical photons (`IJ = -1` in FLUKA optical-photon convention) propagate in a scintillator or absorber material with known linear absorption coefficient \(\mu_{\mathrm{abs}}\) (cm⁻¹) from `OPT-PROP`. The user wants extra weight attenuation per transport step in that material beyond or instead of built-in absorption handling, implemented in `USRMED`.

## Prerequisites

- `OPT-PROP` defines optical transport and absorption for the material.
- `MAT-PROP` `USERDIRE` flags the absorbing material (see `USRMED_MATPROP_USERDIRE.md`).
- `usrmed.f` compiled and linked.
- Regions assigned to the flagged material via `ASSIGNMAt`.

## Transport case identification

Per manual §13.2.29:

```text
IF MREG == NEWREG THEN
    ! particle moving from inside the medium — edit WEE only
ELSE
    ! boundary case — see USRMED_GUIDE for refraction/reflection
ENDIF
```

This case covers only the **`MREG = NEWREG`** branch.

## Implementation plan (pseudocode)

```text
SUBROUTINE USRMED ( ... )

! Optical photon id per manual Chap. 12 (verify in installed FLUKA)
OPTICAL_PHOTON = -1

IF MREG /= NEWREG THEN
    RETURN    ! boundary logic not used in this case
ENDIF

IF IJ /= OPTICAL_PHOTON THEN
    RETURN    ! no change for other particles
ENDIF

! mu_abs in cm^-1 from OPT-PROP or user table for this material/energy
! EKSCO is kinetic energy in GeV; wavelength may be derived if needed
attenuation_factor = compute_step_attenuation(EKSCO, MREG, mu_abs)

WEE = WEE * attenuation_factor

! optional: kill very low weight
IF WEE < weight_cutoff THEN
    WEE = 0.0D0
ENDIF

RETURN
END
```

### Simple constant factor example (test only)

For `test-2` validation:

```text
IF MREG == NEWREG .AND. IJ == OPTICAL_PHOTON THEN
    WEE = WEE * 0.99D0    ! 1% weight loss per USRMED call — diagnostic only
ENDIF
```

Compare photon survival statistics to baseline.

## Important manual constraints

1. **Spot depositions cannot be killed** by `USRMED` — energy may still deposit locally even when weight is reduced or zeroed later in the step logic.

2. **Do not modify** `NEWREG`, `TXX`, `TYY`, `TZZ` when `MREG = NEWREG`.

3. Setting **`WEE = 0`** kills the particle for subsequent transport.

4. Prefer built-in `OPT-PROP` absorption (`µ_abs`) when sufficient; use `USRMED` when custom energy/position dependence is required.

## Validation strategy

| Step | Action |
|---|---|
| 1 | Run with `USERDIRE` off — baseline optical transport |
| 2 | Run with empty `USRMED` + USERDIRE on — should match step 1 |
| 3 | Enable constant `WEE` factor — photon population should decrease faster |
| 4 | Compare deposited energy in absorber vs transmitted photon weight |

## When to use boundary case instead

If the physics need is **refraction or reflection** at an interface (`MREG ≠ NEWREG`), implement direction/`NEWREG` changes per `USRMED_GUIDE.md` Pattern B/C — not this case.

## AutoFLUKA notes

- `subroutine_paths: ["usrmed.f"]`
- Document `mu_abs` source and units in case manifest
- Pair with `OPT-PROP` cards in validation checklist

## Manual references

- `USRMED` case 1 (`MREG = NEWREG`), p. 424
- `MAT-PROP` USERDIRE note on spot depositions, p. 198
- Optical photons Chap. 12
- Parent guide: `../USRMED_GUIDE.md`

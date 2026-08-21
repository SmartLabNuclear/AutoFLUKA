# Case: USRTRACK fluence to dose-equivalent weighting via FLUSCW

## Purpose

This worked example describes a common `FLUSCW` application noted in the FLUKA manual: converting **track-length fluence** to a **dose-equivalent-style** weighted score by returning an energy- and particle-dependent multiplication factor at scoring time.

It is a Markdown implementation pattern using pseudocode only — not a bundled Fortran template or ICRP table.

## Problem statement

Neutron and photon track-length fluence is scored in region `REG_MON` with `USRTRACK`. The user wants each scoring contribution multiplied by an energy-dependent conversion factor \(h(E)\) that depends on particle type `IJ` and kinetic energy, approximating dose equivalent from fluence.

Standard `USRTRACK` output is fluence; `FLUSCW` applies the extra factor at accumulation time.

## Prerequisites

- `USRTRACK` scoring in target region.
- `USERWEIG` with `WHAT(3) > 0` (see `FLUSCW_USERWEIG_ACTIVATION.md`).
- Custom `fluscw.f` compiled into the executable.
- Tabulated \(h(E)\) data in an auxiliary file or inline parameterisation (user responsibility for coefficients and units).

## Deck excerpt

```text
TITLE         Weighted fluence via FLUSCW (dose-equivalent-style response)

USRTRACK         10.0       1.0       -30.0       REG_MON

USERWEIG         0.0       0.0       4.0       0.0       0.0       0.0
```

Add a comment that printed USRTRACK units may still label fluence while values include \(h(E)\) weighting.

## Implementation plan (pseudocode)

### Step 1 — kinetic energy from `PLA`

Manual convention:

```text
IF PLA > 0 THEN
    ! PLA is momentum in GeV/c — derive kinetic energy using particle mass from PAPROP or tabulated mass
    EKIN = momentum_to_kinetic_energy(IJ, PLA)
ELSE
    EKIN = -PLA    ! PLA < 0: kinetic energy in GeV directly
ENDIF
```

Verify mass/energy conversion against the installed FLUKA version and particle coding.

### Step 2 — restrict to USRTRACK detector

```text
INCLUDE scohlp.inc

IF ISCRNG /= 3 THEN          ! 3 = track-length estimator
    FLUSCW = 1.0
    LSCZER = .FALSE.
    RETURN
ENDIF

IF JSCRNG /= TARGET_TRACK_NUMBER THEN
    FLUSCW = 1.0
    LSCZER = .FALSE.
    RETURN
ENDIF
```

Obtain `TARGET_TRACK_NUMBER` from the run listing (`Track n. N` in output).

### Step 3 — optional region filter

```text
IF NREG /= REG_MON_INDEX THEN
    LSCZER = .TRUE.
    FLUSCW = 1.0
    RETURN
ENDIF
```

Alternatively keep all regions in the USRTRACK card and filter only in Fortran.

### Step 4 — response function

```text
SELECT IJ
  CASE neutron_code:
    FLUSCW = interpolate(h_neutron_table, EKIN)
  CASE photon_code:
    FLUSCW = interpolate(h_photon_table, EKIN)
  DEFAULT:
    FLUSCW = 0.0
    LSCZER = .TRUE.    ! or FLUSCW = 0 with LSCZER false
END SELECT
RETURN
```

Document:

- table energy units (GeV vs MeV);
- whether values are dose equivalent per unit fluence in FLUKA's USRTRACK units;
- that FLUKA normalises to unit primary weight regardless of `BEAM` weight card.

## Validation strategy

| Step | Action |
|---|---|
| 1 | Run with template `FLUSCW = 1` — save baseline USRTRACK |
| 2 | Run with flat `FLUSCW = 2` for all accepted scores — all bins should ≈ 2 × baseline |
| 3 | Enable tabulated \(h(E)\) — spot-check one energy bin by hand |
| 4 | Compare shape vs unweighted spectrum — weighted curve should follow \(h(E) \times \Phi(E)\) |

## Units and output interpretation

Manual `USERWEIG` notes:

- Extra weights multiply results at scoring time.
- Printed titles and normalisations may **not** update automatically.
- Incident `BEAM` weight \(\neq 1\) does not change normalisation to unit primary weight.

Record in case documentation:

- meaning of weighted output (e.g. "fluence × dose-equivalent conversion factor");
- source of conversion coefficients;
- FLUKA version used.

## When not to use this pattern

| Situation | Better approach |
|---|---|
| Score deposited energy as dose | `COMSCW` with `USRBIN` energy density or manual dose example in §13.2.2 |
| Boundary current weighting | `USRBDX` + `FLUSCW` with `ISCRNG = 1` |
| Post-process fluence file offline | May avoid recompile if tables change often |
| Activation decay-time factor at scoring | Not available in `FLUSCW` — use other activation workflow |

## AutoFLUKA notes

- Pass `fluscw.f` and any coefficient data file paths in run manifest.
- Use `test-1` flat factor, `test-2` full tables.
- If auxiliary table file missing, expect Fortran `OPEN` failure — fail clearly in user code.

## Manual references

- Introduction: `FLUSCW` for fluence → dose equivalent, p. 89
- `FLUSCW` applications and `SCOHLP`, Sec. 13.2.7, p. 404
- `USERWEIG` notes on output interpretation, p. 272
- Parent guide: `../FLUSCW_GUIDE.md`

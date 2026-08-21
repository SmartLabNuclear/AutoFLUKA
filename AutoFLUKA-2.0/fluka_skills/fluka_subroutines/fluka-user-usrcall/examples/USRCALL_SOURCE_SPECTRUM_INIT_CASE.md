# Case: Custom SOURCE spectrum init via USRGCALL and USRICALL

## Purpose

This worked example sets up a **two-stage initialization pipeline** for a custom `SOURCE` routine that samples from an external energy spectrum file. It follows manual §7.66 Note 4: spectrum reading and normalization can be done in `SOURCE`, `USRINI`, or `USRGLO`.

Pseudocode only — not a bundled Fortran template.

## Problem statement

A user-written `SOURCE` samples primary energies from `spectrum.dat` (two columns: energy in GeV, cumulative probability). Requirements:

1. Open the spectrum file **before** other FLUKA initialization (`USRGLO`).
2. Read and normalize the table **after** materials are defined but **before** `SOURCE` is processed (`USRINI`).
3. Keep `WHAT`/`SDUM` semantics explicit in the deck.

## Deck layout

```text
TITLE
Custom spectrum source with USRCALL init pipeline
DEFAULTS         PRECISIO         0.0
BEAM          -1.0
BEAMPOS       0.0 0.0 0.0

* --- Stage 0: global — open spectrum file on unit 23 ---
USRGCALL      23.0   0.0   0.0   0.0   0.0   0.0   SPECOPEN

* ... geometry, materials, etc. ...

* --- Stage 1: read table after materials exist ---
USRICALL       0.0   0.0   0.0   0.0   0.0   0.0   LOADSP

SOURCE         1.0   0.0   0.0   0.0   0.0   0.0
PHYSICS        ...
USRTRACK       ...

START          1.0E4
STOP
```

### Parameter contract

| Card | `SDUM` | `WHAT` meaning |
|---|---|---|
| `USRGCALL` | `SPECOPEN` | `WHAT(1)` = logical unit `23` for `spectrum.dat` |
| `USRICALL` | `LOADSP` | Reserved for future options (e.g. `WHAT(1)` = renormalization target) |

## Fortran implementation (pseudocode)

### `USRGLO` — open file early

```text
IF SDUM == 'SPECOPEN' THEN
    IUNIT = INT(WHAT(1))
    OPEN( IUNIT, FILE='spectrum.dat', STATUS='OLD', ACTION='READ' )
ENDIF
```

Runs before geometry/material initialization completes.

### `USRINI` — read and normalize table

```text
IF SDUM == 'LOADSP' THEN
    CALL READ_SPECTRUM_FROM_UNIT( 23, NBIN, E_TAB, CDF_TAB )
    CALL NORMALIZE_CDF( NBIN, CDF_TAB )
    ! Store in SAVE arrays or COMMON shared with SOURCE
ENDIF
```

### `SOURCE` — sample using shared table

```text
! Pseudocode inside SOURCE user section:
CALL SAMPLE_FROM_CDF( E_TAB, CDF_TAB, NBIN, E_PRIMARY )
```

Manual: more than one primary may be loaded per `SOURCE` call.

## Why two stages?

| Stage | Routine | Reason |
|---|---|---|
| Open file | `USRGLO` | Unit must exist before any estimator or init that references it; earliest hook |
| Load table | `USRINI` | May depend on material/context cards already read; must finish before `SOURCE` |

If the table is independent of geometry, a single `USRGCALL` with `SDUM='LOADSP'` could suffice — the two-card pattern documents **ordering control**.

## Auxiliary file: `spectrum.dat`

Example format (document in case notes):

```text
! energy_GeV   cumulative_prob
0.050   0.10
0.100   0.35
0.200   0.70
0.500   1.00
```

## Validation strategy

| Step | Check |
|---|---|
| 1 | Low primaries (`START 1.0E3`); confirm no file-open errors |
| 2 | Log sampled energies from `SOURCE` (temporary debug in `USRINI` or `SOURCE`) |
| 3 | Verify histogram of primaries matches input spectrum shape |
| 4 | Remove debug writes before production |

## Common pitfalls

- `USRICALL` placed **after** `SOURCE` → table empty when `SOURCE` first called.
- Unit `23` used without `OPEN` in `USRGLO` → runtime I/O error.
- Unit ≤ 20 → conflicts with FLUKA reserved units (manual §9.8).

## AutoFLUKA notes

```text
subroutine_paths: ["usrglo.f", "usrini.f", "source.f"]
```

Document `SDUM` flags and file names in the case manifest.

## Manual references

- `SOURCE` initialization note, Sec. 7.66, p. 265
- `USRGCALL` / `USRICALL`, Secs. 7.88–7.89
- `USRGLO` / `USRINI`, Secs. 13.2.27–13.2.28
- Parent guide: `../USRCALL_GUIDE.md`

# Case: Slab shielding hadron importance ladder via UBSSET

## Purpose

This worked example follows the FLUKA manual's canonical `UBSSET` pattern: compensate **exponential hadron attenuation** in a slab shield by assigning importances that increase with depth, keeping approximate particle population uniformity across regions.

Pseudocode only — not a bundled Fortran template.

## Problem statement

A simple slab geometry uses regions `IR = 3` … `20`. Each region represents one **half-value layer** of shielding. Without biasing, hadron flux drops exponentially along the stack. The user wants **importance biasing** for hadrons/muons so deeper regions receive higher importance, partially offsetting attenuation.

Manual recommends importance roughly **inversely proportional to attenuation** along the shield path.

## Deck prerequisites

### Base `BIASING` cards (starting point)

Enter minimal hadron biasing so FLUKA populates `UBSSET` arguments (values will be overridden):

```text
* Hadron importance biasing — values overridden in ubsset.f
BIASING     1.0     1.0     1.0     3.0    20.0     1.0
```

| Field | Value | Meaning |
|---|---|---|
| `WHAT(1)` | `1.0` | Hadrons, heavy ions, muons |
| `WHAT(2)` | `1.0` | Multiplicity factor (no RR change) |
| `WHAT(3)` | `1.0` | Placeholder importance (overridden) |
| `WHAT(4)`–`WHAT(5)` | `3`–`20` | Target region range |

Optional tuning output:

```text
BIASING     1.0     0.0     0.0     3.0     8.0     0.0    PRINT
```

### No `USIMBS`

Do **not** set `BIASING` `SDUM = USER` when using region importances via `UBSSET` / `WHAT(3)`.

## Fortran implementation (pseudocode)

In the user section of `ubsset.f` (between template conversion blocks), edit **`HMPHAD`** only for the hadron-importance call pattern:

```text
! ONEONE = 1.D0, TWOTWO = 2.D0 from DBLPRC include

IF IR >= 3 .AND. IR <= 20 THEN
    HMPHAD = ONEONE * TWOTWO**(IR - 3)
ENDIF
```

Interpretation:

- Region 3: importance `1`
- Region 4: importance `2`
- Region 5: importance `4`
- … doubling each slab step

Adjust base and exponent strategy to your geometry numbering.

### What not to do (manual warning)

```text
! WRONG — called many times per region/suboption
GAMCUT = GAMCUT * 0.5D0
```

Use **absolute** assignments from `IR`, never multiply an argument by itself across calls.

## Region numbering plan

Document in the case notes:

| Region range | Physical slice |
|---|---|
| 1–2 | Source / air gap |
| 3–20 | Shield slabs (one HVL each) |
| 21+ | Detector volume |

If geometry uses names, map with `GEOR2N` inside `UBSSET` or pre-plan numeric `IR` values.

## Validation strategy

| Step | Action |
|---|---|
| 1 | Run without custom `UBSSET` logic (dummy) — steep flux falloff in deep regions |
| 2 | Enable ladder — compare region-wise fluence or detector response |
| 3 | Read `BIASING PRINT` counters — tune if RR/splitting excessive |
| 4 | Compare wall-clock and error bars vs unb iased high-statistics run |

## Scoring cautions

- Biased runs change **weights**; interpret scored quantities with care.
- Ratios between regions are more meaningful when weights vary.
- For analog-sensitive estimators, verify biasing compatibility.

## AutoFLUKA notes

- `subroutine_paths: ["ubsset.f"]`
- Document region numbering in case manifest
- `test-1`: dummy `UBSSET`; `test-2`: ladder enabled

## Manual references

- `UBSSET` slab example, Sec. 13.2.22, p. 422
- `BIASING` importance ratios, Sec. 7.7
- Parent guide: `../UBSSET_GUIDE.md`

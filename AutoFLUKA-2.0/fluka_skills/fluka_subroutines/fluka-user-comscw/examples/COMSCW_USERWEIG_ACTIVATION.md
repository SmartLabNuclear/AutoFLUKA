# Case: USERWEIG activation for USRBIN energy density with COMSCW

## Purpose

This worked example activates `COMSCW` for **USRBIN energy-density** scoring using `USERWEIG` `WHAT(6)`. It shows the correct card pairing and call-timing choice for deposition-related weighting.

Use when the user will multiply energy-density scores by a custom factor — not for track-length fluence (`FLUSCW`).

## Problem statement

A user scores **total energy density** in a Cartesian mesh over a phantom with `USRBIN`. They plan to convert energy density to dose (Gy) in `comscw.f` using local material density (see `COMSCW_USRBIN_DOSE_GY_CASE.md`).

## Deck structure

### USRBIN energy-density scoring (conceptual)

Two-card `USRBIN` pattern (Cartesian energy-density mesh):

```text
USRBIN          10.0    ENERGY     -50.0      50.0      50.0      50.0EDEN
USRBIN         -50.0     -50.0       0.0      50.0      50.0      50.0&
```

Checks:

- First card: `WHAT(1)` = `10.0` selects a Cartesian mesh, `WHAT(2)` = `ENERGY` (particle code 208) scores total energy density, `WHAT(3)` = `-50.0` is the output unit (negative = binary), `WHAT(4..6)` = mesh maxima.
- Second card: `WHAT(1..3)` = mesh minima, `WHAT(4..6)` = bin counts, `SDUM` = `&`.
- Every value is right-aligned in its 10-column field (see `fluka-authoring/rules/fortran_columns.md`).

### Activation card

**Recommended — detector-checked calls:**

```text
USERWEIG         0.0       0.0       0.0       0.0       0.0       4.0
```

| Field | Value | Effect |
|---|---|---|
| `WHAT(3)` | `0.0` | No `FLUSCW` |
| `WHAT(6)` | `4.0` | Activate `COMSCW`; call after detector check; also enables `ENDSCP` if implemented |

**Alternative — unconditional calls:**

```text
USERWEIG         0.0       0.0       0.0       0.0       0.0       1.0
```

Matches manual example: dose/star densities multiplied by `COMSCW` with no prior detector check.

### Documentation notice

Add a comment that USRBIN output is multiplied by a user response (e.g. dose conversion). Manual warns printed titles may still describe unweighted energy density.

## Fortran / compile

1. Copy `comscw.f` from your **licensed FLUKA installation** (AutoFLUKA does NOT ship this file).
2. Include `scohlp.inc`; include `flkmat.inc` if using density-based dose.
3. Implement weighting in function body.
4. Compile/link with `subroutine_paths: ["comscw.f"]`.

## Validation checklist

- [ ] `WHAT(6) > 0` and `WHAT(3) <= 0` (COMSCW only).
- [ ] `USRBIN` mode is energy/star density, not track-length fluence.
- [ ] `ISCRNG = 1` branch in Fortran for energy density.
- [ ] `JSCRNG` matches target binning number from output listing.
- [ ] Baseline `COMSCW = 1` matches unweighted reference run.
- [ ] Weighted units documented.

## Common mistakes

| Mistake | Fix |
|---|---|
| `WHAT(3)` instead of `WHAT(6)` | Activates `FLUSCW`, not `COMSCW` |
| USRBIN fluence mode + `COMSCW` | Use `FLUSCW` for track-length fluence `USRBIN` |
| `DETECT` pulse-height tuning via `COMSCW` | Use `DETSCW` (`WHAT(4)`) for hit modification |

## Related

- Dose implementation: `COMSCW_USRBIN_DOSE_GY_CASE.md`
- Parent guide: `../COMSCW_GUIDE.md`

## Manual references

- `USERWEIG` example `WHAT(6) = 1.0`, p. 292
- `COMSCW` Sec. 13.2.2
- `USRBIN` Sec. 7.86

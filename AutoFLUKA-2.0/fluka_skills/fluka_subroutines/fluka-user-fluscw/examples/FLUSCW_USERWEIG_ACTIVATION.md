# Case: USERWEIG activation for USRTRACK with FLUSCW

## Purpose

This worked example shows how to activate `FLUSCW` for a **track-length fluence** scorer (`USRTRACK`) using the `USERWEIG` card. It covers the `WHAT(3)` call-timing choice and the minimum deck structure for a weighted fluence run.

Use this case when the user needs custom weighting of region track-length fluence — not for energy deposition (`COMSCW`) or boundary currents alone.

## Problem statement

A shielding study scores neutron track-length fluence in a monitoring region (`REG_MON`). The user will multiply scores by an energy- and particle-dependent factor implemented in `fluscw.f` (see `FLUSCW_USRTRACK_DOSE_EQUIVALENT_CASE.md` for the response logic).

## Deck structure

### Scoring card

```text
USRTRACK         10.0       1.0       -30.0       REG_MON
```

Conceptual checks (verify against installed manual for exact `WHAT(i)` meanings):

- Logical unit `10` for formatted output (example only).
- Request track-length fluence in region `REG_MON`.

### Activation card

**Recommended — call only when detector applies (efficient):**

```text
USERWEIG         0.0       0.0       4.0       0.0       0.0       0.0
```

| Field | Value | Effect |
|---|---|---|
| `WHAT(3)` | `4.0` | Activate `FLUSCW`; call after detector check; also enables `FLDSCP` if implemented |
| `WHAT(6)` | `0.0` | Do not activate `COMSCW` |

**Alternative — unconditional calls (use sparingly):**

```text
USERWEIG         0.0       0.0       1.0       0.0       0.0       0.0
```

`WHAT(3) = 1.0` calls `FLUSCW` before detector-applicability check. Use only when you need side effects on every call or global logic independent of the active scorer.

### Documentation notice

Add a comment or `TITLE` extension noting that fluence is multiplied by a user response function via `FLUSCW`. Manual recommends informing readers of extra weighting because printed headings may still describe unweighted fluence.

## Fortran / compile requirements

1. Copy `fluscw.f` from your **licensed FLUKA installation** (AutoFLUKA does NOT ship this file).
2. Implement weighting logic in the function body (preserve signature).
3. Include `scohlp.inc` if branching on `ISCRNG` / `JSCRNG`.
4. Compile and link custom executable with `fluscw.f`.

## AutoFLUKA execution

```text
subroutine_paths: ["fluscw.f"]
```

Steps:

1. Verify processed deck contains `USERWEIG` with `WHAT(3) > 0` and `USRTRACK`.
2. Run `test-1` with dummy body returning `1.0` — output should match no-weighting reference.
3. Run `test-2` with response function enabled.
4. Compare first energy bin to hand calculation.

## Validation checklist

- [ ] `WHAT(3) > 0` and `WHAT(6) <= 0` (FLUSCW only, not COMSCW).
- [ ] `USRTRACK` region name/number matches filter in `fluscw.f`.
- [ ] `ISCRNG = 3` branch used for track-length estimator in Fortran.
- [ ] `JSCRNG` matches the track detector index from FLUKA output listing.
- [ ] Baseline `FLUSCW = 1` test matches unweighted run.
- [ ] Weighted run units documented in case notes.

## Common mistakes (this case)

| Mistake | Fix |
|---|---|
| `USERWEIG` `WHAT(6)` instead of `WHAT(3)` | `WHAT(6)` activates `COMSCW`, not `FLUSCW` |
| `USRBIN` energy density with `FLUSCW` | Use `COMSCW` for energy density binning |
| Filter only `JSCRNG` | Also check `ISCRNG = 3` for USRTRACK |
| No custom executable linked | Pass `fluscw.f` in `subroutine_paths` |

## Related

- Response implementation: `FLUSCW_USRTRACK_DOSE_EQUIVALENT_CASE.md`
- Parent guide: `../FLUSCW_GUIDE.md`

## Manual references

- `USERWEIG` Sec. 7.84, example with `WHAT(3) = 4.0`, p. 272
- `FLUSCW` Sec. 13.2.7, p. 404
- `USRTRACK` Sec. 7.86

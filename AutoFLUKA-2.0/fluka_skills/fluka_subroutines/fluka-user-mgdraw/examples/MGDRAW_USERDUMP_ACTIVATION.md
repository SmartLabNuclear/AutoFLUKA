# MGDRAW USERDUMP activation

## Purpose

This example explains how to activate the FLUKA `MGDRAW` user-routine family through the `USERDUMP` input card. It is a Markdown implementation guide, not a bundled Fortran template.

## Activation card

General form:

```text
USERDUMP  WHAT(1)  WHAT(2)  WHAT(3)  WHAT(4)  WHAT(5)  WHAT(6)  SDUM
```

For ordinary MGDRAW use, the key condition is:

```text
WHAT(1) >= 100.0
```

A reset/disable form is described in the manual using negative values, conceptually:

```text
WHAT(1) <= -100.0
```

## Field checklist

| Field | What to check |
|---|---|
| `WHAT(1)` | Activates or disables MGDRAW-family dumping. For ordinary use, require `WHAT(1) >= 100.0`. |
| `WHAT(2)` | Output logical unit. Choose a safe user unit and avoid conflicts with FLUKA-reserved or already-used units. |
| `WHAT(3)` | Selects standard MGDRAW call classes. Choose the value from the manual for the needed entry points. |
| `WHAT(4)` | Used for user-defined dump behavior such as `USDRAW` activation when enabled. Verify exact behavior against the manual. |
| `WHAT(5)` | Advanced/manual-specific behavior; do not infer without checking the installed manual. |
| `WHAT(6)` | Advanced/manual-specific behavior; do not infer without checking the installed manual. |
| `SDUM` | Dump/output identifier or special mode. Treat special values as advanced behavior. |

## Conceptual activation patterns

### Broad diagnostic activation

```text
USERDUMP     100.0      <unit>       0.0       0.0       ...       ...   <dump-name>
```

Use only for a low-NPS diagnostic run unless output is filtered inside the routine.

### Boundary-crossing or phase-space focused activation

```text
USERDUMP     100.0      <unit>       <mode-calling-BXDRAW>       0.0       ...       ...   <dump-name>
```

Then implement the region-pair and particle filters inside `BXDRAW`.

### Interaction/collision focused activation

```text
USERDUMP     100.0      <unit>       <mode>       1.0       ...       ...   <dump-name>
```

Then implement interaction/collision logic inside `USDRAW`.

## Required AutoFLUKA checks

Before running:

- [ ] Input deck has `USERDUMP`.
- [ ] A user-provided MGDRAW `.f` file is supplied explicitly via `subroutine_paths` or is otherwise correctly linked.
- [ ] The routine defines `SUBROUTINE MGDRAW`.
- [ ] Needed entries such as `BXDRAW`, `EEDRAW`, `ENDRAW`, `SODRAW`, or `USDRAW` are present.
- [ ] Output unit is documented.
- [ ] Output is filtered and bounded.
- [ ] Low-NPS `test-n` run is performed before production.

## Common mistakes

| Mistake | Consequence | Fix |
|---|---|---|
| Forgetting `USERDUMP` | MGDRAW is not called | Add/check `USERDUMP`. |
| `WHAT(1)` not activating MGDRAW | No MGDRAW output | Use manual-supported activation; ordinary use requires `WHAT(1) >= 100.0`. |
| Wrong `WHAT(3)`/`WHAT(4)` | Desired entry is not called | Select the mode from the manual for the required entry. |
| Unit conflict | Missing/corrupt output or runtime error | Choose a safe logical unit. |
| No filters | Huge files and slow runs | Filter by region, particle, energy, direction, or event count. |

## Manual references

- FLUKA Manual (2024 PDF edition), FLUKA Collaboration, `USERDUMP` Sec. 7.83, p. 269; `MGDRAW` Sec. 13.2.14, p. 409, manuals page https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals

# Case: Modular calorimeter with explicit user LATTIC routine

## Purpose

This worked example shows how to replicate a detailed calorimeter **prototype cell** along the z axis using the `LATTICE` card with **empty SDUM**, which forces FLUKA to call the user `LATTIC` / `LATNOR` routine. It is a Markdown implementation guide, not a bundled Fortran template.

Use this case when each lattice cell needs a **distinct per-index translation** that is not assigned as a single named `ROT-DEFI` on the `LATTICE` card. If a single `ROT-DEFI` transformation suffices, see `LATTIC_ROTDEFI_REPLICA_CASE.md` instead.

## Problem statement

A sampling calorimeter has one fully detailed prototype module (absorber + scintillator regions). Four identical modules are stacked along z at 10 cm pitch. The prototype is defined once; four container regions hold the replicas.

## Geometry plan

| Item | Description |
|---|---|
| Prototype regions | `ABSORB`, `SCINT` — materials and scoring assigned here only |
| Container regions | `CELL0`, `CELL1`, `CELL2`, `CELL3` — lattice boxes, no materials |
| Lattice numbers | `IRLTGG` = 0, 1, 2, 3 mapped to `CELL0` … `CELL3` |
| Transform | Cell `n` maps to prototype by `z_prototype = z_cell - n * 10 cm`; directions unchanged |

## Input deck sketch (geometry section)

Conceptual combinatorial excerpt (adapt names and body dimensions to your case):

```text
* --- Bodies: one prototype module + four container boxes ---
* (define RCC/ARB bodies for absorber, scintillator, and four cell envelopes)

* --- Regions: prototype unit ---
ABSORB    5 +absorber_body ...
SCINT     5 +scintillator_body ...

* --- Regions: lattice containers (no materials) ---
CELL0     5 +cell_box_0 ...
CELL1     5 +cell_box_1 ...
CELL2     5 +cell_box_2 ...
CELL3     5 +cell_box_3 ...

END

* --- LATTICE: empty SDUM => user LATTIC routine required ---
* From region CELL0 to CELL3, lattice numbers 0 to 3, step 1
LATTICE     CELL0     CELL3     1.0       0.0       3.0       1.0
```

Notes:

- `WHAT(1)`–`WHAT(2)` span container regions `CELL0` … `CELL3`.
- `WHAT(4)` = 0 and `WHAT(5)` = 3 assign lattice indices 0–3.
- **SDUM is omitted/empty**, so FLUKA calls `LATTIC` for transforms.
- If using numeric region indices instead of names, replace `CELL0` etc. with the corresponding region numbers from the region table.

## Fortran implementation plan (pseudocode)

Copy `lattic.f` from your **licensed FLUKA installation** (AutoFLUKA does NOT ship this file) and edit the user branches for `IRLTGG` 0–3.

### `LATTIC` branches

```text
PARAMETER dz = 10.0   ! cm; match geometry pitch

SELECT IRLTGG
  CASE 0:
    SB = XB;  UB = WB
  CASE 1:
    SB_x = XB_x;  SB_y = XB_y;  SB_z = XB_z - dz
    UB = WB
  CASE 2:
    SB_z = XB_z - 2*dz;  UB = WB
  CASE 3:
    SB_z = XB_z - 3*dz;  UB = WB
  DEFAULT:
    error stop unsupported lattice index
END SELECT
```

The shipped template may use a `GO TO` ladder keyed on `IRLTGG + 1`; adapt indices to match your `LATTICE` card assignment.

### `LATNOR` branches

Pure z-translation leaves direction cosines unchanged:

```text
SELECT IRLTNO
  CASE 0, 1, 2, 3:
    UN unchanged
  DEFAULT:
    error stop unsupported lattice index
END SELECT
```

If you add reflections in a variant of this case, update `LATNOR` to invert the reflected component.

## Activation checklist

| Step | Action |
|---|---|
| 1 | Prototype regions fully defined with materials |
| 2 | Four container regions defined, no materials |
| 3 | `LATTICE` card spans containers with lattice numbers 0–3 |
| 4 | SDUM left empty to force user routine |
| 5 | `lattic.f` implements `IRLTGG` 0–3 and matching `LATNOR` |
| 6 | Custom executable compiled with `lattic.f` |
| 7 | AutoFLUKA `subroutine_paths` includes `lattic.f` explicitly |

## AutoFLUKA execution

1. Place `calorimeter.inp` and `lattic.f` in the case folder.
2. Pass `subroutine_paths: ["lattic.f"]` (plus any other user routines).
3. Run `test-1` with geometry plot if available.
4. Run `test-2` with very low primaries; confirm no lattice support errors.
5. Inspect that scoring in `ABSORB`/`SCINT` behaves as one prototype shared by four replicas.

## Validation

- [ ] Geometry plot shows four stacked modules at 10 cm pitch.
- [ ] No `Lattice geometry non supported` message.
- [ ] Low-NPS transport completes.
- [ ] Energy deposition pattern is consistent with four physically separated cells mapping to one prototype.

## When to escalate or change approach

| Situation | Action |
|---|---|
| All cells share one `ROT-DEFI` transform | Use named SDUM on `LATTICE`; see ROT-DEFI replica case |
| Non-uniform transforms still analytical per cell | Keep this pattern; extend `IRLTGG` branches |
| Nested global + local transform | Consider `LATTSNGL` with two `ROT-DEFI` names |
| Regions cross cell boundaries | Redesign prototype; do not patch in `LATTIC` |

## Manual references

- `LATTICE` card Sec. 8.2.10 (empty SDUM calls user routine)
- `LATTIC` / `LATNOR` Sec. 13.2.11
- Parent guide: `../LATTIC_GUIDE.md`

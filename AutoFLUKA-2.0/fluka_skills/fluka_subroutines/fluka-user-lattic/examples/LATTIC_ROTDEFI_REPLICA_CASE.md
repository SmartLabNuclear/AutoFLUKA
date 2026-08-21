# Case: Target replica using ROT-DEFI + LATTICE (no custom Fortran)

## Purpose

This worked example follows the FLUKA manual replica pattern: a **prototype target** region and a **replica** container region linked by `LATTICE` with SDUM naming a `ROT-DEFI` transformation. FLUKA applies the roto-translation internally; a custom `LATTIC` Fortran implementation is **not required** for the mapping itself.

Use this case **before** writing user `LATTIC` code whenever the symmetry can be expressed as a named `ROT-DEFI` transformation on the `LATTICE` card.

## Problem statement

A cylindrical target is defined once as the prototype. A second region (`REPLICA`) represents a displaced/oriented copy of that target in the real geometry. The replica body is built with an inverse roto-translation directive so that FLUKA's lattice machinery maps tracking correctly between replica and prototype.

This pattern is adapted from the manual roto-translation / lattice example (2024 PDF edition, p. 324).

## Geometry structure

| Region / item | Role |
|---|---|
| `TARGET` | Prototype — real geometry of the basic unit; materials assigned here |
| `REPLICA` | Container lattice cell — holds the transformed copy |
| `targRepl` | Body defining replica shape (placed via transform directives) |
| `Rotdefi1` | Named `ROT-DEFI` transformation: translation then rotation |

## Input deck sketch

Conceptual excerpt (ellipses mark omitted bodies/regions):

```text
* --- Roto-translation: shift (0, -2, -30) then rotation -21 deg about x ---
ROT-DEFI    0.0    -2.0   -30.0   Rotdefi1
ROT-DEFI    100.   -21.           Rotdefi1

* --- Replica body built under inverse transform directive ---
$Start_transform
-Rotdefi1
RCC   targRepl   0.0 0.0 -5.0  0.0 0.0 10.0  5.0
$End_transform

* --- Regions ---
TARGET    5 +target
REPLICA   5 +targRepl

* --- Lattice links replica container to Rotdefi1 ---
LATTICE   REPLICA   REPLICA   1.0   1.0   1.0   1.0   Rotdefi1
```

Reading the `LATTICE` line:

- Container region `REPLICA` (first and last cell in this single-cell lattice).
- Lattice number `1` assigned (WHAT(4) and WHAT(5)).
- **SDUM = `Rotdefi1`** — FLUKA uses the named `ROT-DEFI` transformation; user `LATTIC` is not called for this map.

The manual notes that the target replica is transformed with the **inverse** of the lattice transformation inside the `$Start_transform` / `$End_transform` block (leading `-Rotdefi1` on the transform line).

## Decision: ROT-DEFI path vs user LATTIC

| Condition | Path |
|---|---|
| One `ROT-DEFI` (or nested `LATTSNGL`) describes the cell map | **This case** — name it in `LATTICE` SDUM |
| Per-cell-index logic or SDUM empty | **User `LATTIC`** — see `LATTIC_GEOMETRY_ACTIVATION.md` |
| SDUM contains `ROT#12` style integer | ROT-DEFI index path; define index 12 in deck |

## Activation checklist

| Step | Action |
|---|---|
| 1 | Define `ROT-DEFI` cards for `Rotdefi1` before `LATTICE` |
| 2 | Build replica body under `$Start_transform` / `$End_transform` with correct sign |
| 3 | Define prototype region `TARGET` with materials |
| 4 | Define container region `REPLICA` without separate material on container |
| 5 | Issue `LATTICE` with SDUM `Rotdefi1` |
| 6 | Issue PLOTGEOM only after all transforms and lattice cards exist |

## Fortran / compile implications

- The default `lattic.f` from the installation may still be linked if other user routines are present, but the **transform for this lattice is handled by `ROT-DEFI`** via `KROTAT` delegation in the template.
- No edits to per-`IRLTGG` branches are required for this specific replica if SDUM correctly names `Rotdefi1` and the deck defines that transformation.
- If **only** this lattice geometry is used with no other user routines, confirm your build workflow still produces a runnable executable for your FLUKA version.

## AutoFLUKA execution

1. Verify `LATTICE` SDUM names an existing `ROT-DEFI` in the processed deck.
2. If no custom `lattic.f` edits are needed, `subroutine_paths` may omit `lattic.f` unless other routines require linking.
3. Run low-NPS `test-n` with geometry plot after all transforms are defined.
4. Confirm tracking in `REPLICA` maps to prototype `TARGET` physics.

## Validation

- [ ] `ROT-DEFI Rotdefi1` cards precede geometry that references them.
- [ ] `LATTICE` SDUM matches transformation name exactly (including sign convention per manual).
- [ ] PLOTGEOM issued after lattice/ROT-DEFI definitions.
- [ ] Geometry plot shows replica at expected position/orientation.
- [ ] Low-NPS run: no lattice errors; interaction physics consistent with prototype materials.

## When to escalate to user LATTIC

Escalate to `LATTIC_GEOMETRY_ACTIVATION.md` when:

- multiple lattice cells need **different** transforms not expressible as one `ROT-DEFI` per card line;
- SDUM would be empty but transforms are still required;
- per-index branching on `IRLTGG` is easier to maintain in Fortran than many `ROT-DEFI` + `LATTICE` card combinations.

## Manual references

- FLUKA Manual (2024 PDF edition), FLUKA Collaboration, replica example p. 324, manuals page https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals
- `LATTICE` card Sec. 8.2.10 (SDUM names transformation)
- `ROT-DEFI` Sec. 7.63
- `LATTIC` Sec. 13.2.11 (delegation when rotation index assigned)
- Parent guide: `../LATTIC_GUIDE.md`

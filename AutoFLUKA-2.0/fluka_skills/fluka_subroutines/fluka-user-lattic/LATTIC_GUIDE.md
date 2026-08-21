# FLUKA LATTIC user routine

## Purpose

`LATTIC` is the FLUKA user routine for symmetry transformations in modular (lattice) geometries. It maps coordinates and direction cosines from a **lattice cell** (the replicated "real-world" cell) into the **prototype** reference system where the basic unit geometry is defined.

The companion entry `LATNOR` performs the inverse direction transformation for surface normals: from the prototype cell back into the lattice cell.

In practical use, FLUKA tracking alternates between the real lattice-cell system and the prototype system. Particle positions and directions are transformed into the prototype to perform transport in the detailed basic-unit regions and materials, then transformed back to the real cell. The correspondence depends on the symmetry transformation and on the lattice cell number `IRLTGG`.

`LATTIC` is activated by one or more `LATTICE` geometry cards. A user-written `LATTIC` routine is required only when the transformation cannot be expressed through a named `ROT-DEFI` transformation on the `LATTICE` card SDUM field.

## When to use

Use `LATTIC` when the user needs lattice/modular geometry and the symmetry mapping is **not** adequately covered by a `ROT-DEFI` roto-translation referenced from the `LATTICE` card.

Appropriate use cases include:

1. **Replicated detector or calorimeter cells**  
   Model one detailed prototype cell and replicate it across many lattice containers.

2. **Per-cell transforms that differ by lattice index**  
   Each `IRLTGG` value needs a distinct analytical map (translation ladder, reflection sequence, offset reflection) that cannot be assigned as a single named `ROT-DEFI` on the card.

3. **Combined symmetry not expressible as one ROT-DEFI name**  
   When nested `LATTSNGL` or multiple `ROT-DEFI` definitions still do not cover the required cell-index logic.

4. **Custom cell-index logic**  
   When the mapping from container region to lattice number requires user-coded branching on `IRLTGG`.

## When not to use

Do **not** write or link a custom `LATTIC` routine when a standard `ROT-DEFI` transformation can be associated with the lattice through the `LATTICE` card SDUM field.

Prefer the **ROT-DEFI path** when:

- the `LATTICE` card SDUM names a transformation (for example `Rotdefi1`);
- the SDUM contains a `ROT#` / `Rot#` / `rot#` (or `RO#` / `Ro#` / `ro#`) prefix followed by an integer rotation index;
- each lattice cell uses a transformation already defined by `ROT-DEFI` cards.

Do **not** use lattice geometry when:

- the geometry has no replication requirement and standard combinatorial regions suffice;
- regions would span two lattice cells after transformation (this produces unpredictable behaviour);
- the user has not yet defined prototype regions, container regions, and a consistent numbering plan.

See `examples/LATTIC_ROTDEFI_REPLICA_CASE.md` for the ROT-DEFI-first pattern before escalating to a custom routine.

## Activation card or activation condition

`LATTIC` is activated through **`LATTICE`** geometry card(s) in the combinatorial geometry section.

Related optional cards:

| Card | Role |
|---|---|
| `LATTICE` | Defines container regions, lattice cell numbering, and transformation association (SDUM). |
| `LATTSNGL` | Associates two nested signed transformations `R1` and `R2` to a lattice cell (`r' = R2 R1 r`). |
| `ROT-DEFI` | Defines roto-translations usable from `LATTICE` SDUM or from `LATTSNGL`. |

### Critical SDUM decision

On the `LATTICE` card, SDUM controls whether FLUKA calls the user routine:

| SDUM content | Behaviour |
|---|---|
| Character name of a `ROT-DEFI` transformation (with sign) | FLUKA applies the named roto-translation; user `LATTIC` body is not needed for that mapping. |
| `ROT#` / `Rot#` / `rot#` / `RO#` / `Ro#` / `ro#` followed by an integer | Integer identifies the associated roto-translation index. |
| No such string, or null/empty SDUM | **`LATTIC` user routine is called** whenever a transformation is required. |

### Geometry input order

Geometry data must follow the FLUKA geometry chapter order. In summary:

```text
GEOBEGIN
  bodies
  END
  regions
  END
  LATTICE cards (optional, FLUKA standard or free format)
  region volumes (optional)
GEOEND
```

If `PLOTGEOM` is used with lattice geometry, issue it **only after all transformations are defined** (that is, after all `ROT-DEFI` commands and lattice definitions are complete).

## Input-card syntax and required deck checks

### `LATTICE` card form

```text
LATTICE  WHAT(1)  WHAT(2)  WHAT(3)  WHAT(4)  WHAT(5)  WHAT(6)  SDUM
```

| Field | Meaning | Default / notes |
|---|---|---|
| `WHAT(1)` | Container-region number (or name) of the **first** lattice cell | No default |
| `WHAT(2)` | Container-region number (or name) of the **last** lattice cell | `WHAT(1)` |
| `WHAT(3)` | Step in assigning container-region numbers | `1.0` |
| `WHAT(4)` | Lattice number (or name) assigned to region `WHAT(1)` | No default |
| `WHAT(5)` | Lattice number (or name) assigned to region `WHAT(2)` | No default |
| `WHAT(6)` | Step in assigning lattice cell numbers/names | `1.0` |
| `SDUM` | Transformation index or name; see decision table above | — |

Additional manual requirements:

- The **basic unit** (prototype) must be described in full detail in body and region data.
- **Container** regions represent lattice cells ("boxes") where the basic unit is replicated. **No material assignment** is needed for lattice-cell container regions.
- Contiguous lattice numbering is **recommended** for memory management; non-contiguous numbering is possible with multiple `LATTICE` cards.
- Any region in the basic unit must be **fully contained** in each lattice cell after transformation. Regions crossing cell boundaries lead to unpredictable behaviour.
- Materials, thresholds, and biasing must be assigned **only** to regions in the basic unit. All copies share the same material and settings.
- In free-format geometry with alphanumeric body/region names, use names consistently on `LATTICE` cards too.

### `LATTSNGL` card (optional nested transforms)

```text
LATTSNGL  WHAT(1)  WHAT(2)  WHAT(3)  ...
```

| Field | Meaning |
|---|---|
| `WHAT(1)` | Container-region number of the lattice cell |
| `WHAT(2)` | Index or name (with sign) of first transformation `R1` |
| `WHAT(3)` | Index or name (with sign) of second transformation `R2` |

Nested action: `r' = R2 R1 r`.

### Pre-run deck checks

| Check | Required action |
|---|---|
| Prototype geometry complete | All basic-unit bodies and regions defined before lattice cards. |
| Container regions defined | One container region per replicated cell (or stepped range per `LATTICE` card). |
| Numbering plan consistent | `WHAT(4)`–`WHAT(5)` lattice numbers match branches planned in `LATTIC` (`IRLTGG`). |
| SDUM path chosen deliberately | ROT-DEFI name/index vs empty SDUM forcing user routine. |
| No materials on containers | Assign materials only on prototype regions. |
| No spanning regions | Verify each prototype region fits inside every assigned cell after transform. |
| `ROT-DEFI` complete before PLOTGEOM | Plot only after all transforms exist. |
| User routine linked if needed | Empty/null SDUM requires compiled `lattic.f` in the custom executable. |
| Low-NPS test planned | Run geometry plot and short transport test before production. |

## Required Fortran routine identity

A user-provided LATTIC Fortran file must preserve the FLUKA-expected routine identity and entry-point interfaces.

The following routine/entry-point structure may be present in the LATTIC user-routine `.f` file shipped with a licensed FLUKA installation:

```text
SUBROUTINE LATTIC ( XB, WB, DIST, SB, UB, IR, IRLTGG, IRLT, IFLAG )
ENTRY LATNOR ( UN, IRLTNO, IRLT )
```

### `LATTIC` entry — conceptual argument map

| Argument | Role |
|---|---|
| `XB(1:3)` | Input: actual position coordinates in lattice cell `IRLTGG` |
| `WB(1:3)` | Input: actual direction cosines in lattice cell `IRLTGG` |
| `DIST` | Input: current step length |
| `SB(1:3)` | Output: transformed coordinates in prototype cell |
| `UB(1:3)` | Output: transformed direction cosines in prototype cell |
| `IR` | Region number in prototype cell |
| `IRLTGG` | Lattice cell number (user-chosen index from `LATTICE` card) |
| `IRLT` | Array of region indices corresponding to lattice cells |
| `IFLAG` | Reserved variable |

`LATTIC` returns tracking point `SB` and direction `UB` in the prototype system corresponding to real position/direction `XB`, `WB` in cell `IRLTGG`.

### `LATNOR` entry — conceptual argument map

| Argument | Role |
|---|---|
| `UN(1:3)` | Input: normal direction cosines in prototype cell; output: same vector expressed in lattice cell |
| `IRLTNO` | Present lattice cell number |
| `IRLT` | Array of region indices corresponding to lattice cells |

`LATNOR` transforms normal cosines from the prototype system to the real lattice cell `IRLTNO`. This transformation must be the **inverse** of the direction part of `LATTIC` for the same cell: while `LATTIC` maps input `WB` to output `UB`, `LATNOR` maps the `UN` vector to itself in the cell frame.

**Important:** If the transform involves rotation, save incoming `UN` components to local variables before overwriting `UN`, so intermediate steps do not destroy input values.

## Expected user-provided `.f` file checks

Before compile/link, verify:

- [ ] File defines `SUBROUTINE LATTIC` with the expected argument list.
- [ ] File defines `ENTRY LATNOR` with the expected argument list.
- [ ] Branching on `IRLTGG` covers every lattice number assigned on `LATTICE` card(s).
- [ ] Unsupported `IRLTGG` values fail clearly (do not silently return wrong transforms).
- [ ] For each `IRLTGG` branch, position map `XB → SB` and direction map `WB → UB` are consistent.
- [ ] `LATNOR` branch for `IRLTNO` inverts the direction transform used in `LATTIC` for the same index.
- [ ] If the shipped template assigns `KROTAT` from `ROT-DEFI`, do not also hand-code conflicting transforms for the same cell.
- [ ] Includes and common blocks required by the installed FLUKA version are preserved.

## Licensing-safe implementation policy

**AutoFLUKA does NOT ship** FLUKA-distributed LATTIC templates, the FLUKA manual, or other licensed installation materials. This guide contains original prose and pseudocode only.

Users should provide or copy `lattic.f` from their **licensed FLUKA installation**, or supply a user `.f` file in the case workspace. Agents may inspect and edit user-provided Fortran via tools.

Preferred wording when referring to structure:

```text
The following routine/entry-point structure may be present in the `.f` user-routine file shipped with a licensed FLUKA installation:
```

Do not reproduce FLUKA template bodies in Markdown or chat. See `../SKILL.md`.

## Upstream placement in the official FLUKA installation

In a standard FLUKA source tree, the LATTIC template is typically found under the user-routine sources (commonly `src/user/lattic.f` or an equivalent path in the installed distribution).

Workflow:

1. Copy the template from the licensed installation into the case or project workspace.
2. Edit only the user-intended transform branches.
3. Compile and link with other user routines as needed.
4. Run the input deck with the resulting custom executable.

## Mandatory setup before editing

Complete these steps **before** editing Fortran:

1. **Draw the geometry plan** — prototype unit, container cells, and how many replicas exist.
2. **Choose activation path** — ROT-DEFI SDUM on `LATTICE` vs custom `LATTIC` (see decision table).
3. **Assign lattice numbers** — contiguous `WHAT(4)`–`WHAT(5)` ranges unless there is a deliberate reason for gaps.
4. **Define transforms per `IRLTGG`** — on paper or in pseudocode, for both position and direction.
5. **Plan `LATNOR` inverses** — especially for reflections and rotations.
6. **Verify material assignment** — prototype regions only.
7. **Prepare validation** — geometry plot inputs and a low-primary transport test.

## Safe editing rules

- Preserve `SUBROUTINE LATTIC` and `ENTRY LATNOR` signatures and required includes.
- Edit transform logic only in the user branches; do not remove FLUKA infrastructure you do not understand.
- Keep `LATTIC` and `LATNOR` consistent cell by cell.
- For reflections: negate the appropriate direction component in both entries consistently.
- For translations: apply the inverse offset in `LATNOR` if normals must be expressed in the translated frame (identity direction maps often suffice for pure translation).
- When rotations are involved, use local temporaries in `LATNOR` before overwriting `UN`.
- Test with geometry plotting before trusting transport results.
- If the template exposes a `KROTAT` / `DOTRSF` / `DORTNO` path for assigned `ROT-DEFI` indices, prefer that path when SDUM names a rotation index instead of duplicating the transform manually.

## Code implementation sections

### ROT-DEFI delegation branch (template behaviour)

The LATTIC template shipped with a licensed FLUKA installation may first query whether a `ROT-DEFI` index is assigned to the present lattice cell. When `KROTAT > 0` or `KROTAT < 0`, it may delegate position and direction transforms to FLUKA internal routines (`DOTRSF`, `DORTNO`, `UNDOTR`, `UNDRTO`) and return without entering user-coded `IRLTGG` branches.

**Editing guidance:** If your `LATTICE` card SDUM names a `ROT-DEFI` transformation, ensure the deck defines that transformation and expect the template to use the delegation path. User-coded `GO TO` branches apply when no rotation index is assigned.

### User-coded `IRLTGG` branches (conceptual patterns)

The shipped template often illustrates analytical transforms with a computed `GO TO` ladder keyed on `IRLTGG`. Typical pedagogical patterns:

#### Lattice 0 — unitary (identity)

```text
SB = XB
UB = WB
```

Use for the reference cell or a cell that shares the prototype frame.

#### Lattice 1 — reflection (example: z reflection)

```text
SB_x = XB_x;  SB_y = XB_y;  SB_z = -XB_z
UB_x = WB_x;  UB_y = WB_y;  UB_z = -WB_z
```

`LATNOR` for the same index: negate the z component of `UN`.

#### Lattice 2 — translation along z (example)

```text
SB_x = XB_x;  SB_y = XB_y;  SB_z = XB_z - dz
UB = WB
```

Pure translation often leaves direction cosines unchanged in `LATTIC` and `LATNOR`.

#### Lattice 3 — offset reflection (example)

```text
SB_z = -(XB_z - z0) + z0
UB_z = -WB_z
```

Ensure `LATNOR` applies the matching inverse for normals.

Adapt indices, offsets, and axes to the real problem. The template indices are examples; your `LATTICE` card `WHAT(4)`–`WHAT(5)` assignment defines which `IRLTGG` values must be implemented.

### Entry-point editable-section map

| Section / entry | Editable? | Use for | Main caution |
|---|---|---|---|
| Per-`IRLTGG` transform body in `LATTIC` | Yes | Map `XB, WB` → `SB, UB` | Must match `LATTICE` numbering |
| Per-`IRLTNO` branch in `LATNOR` | Yes | Map normal prototype → cell | Must invert `LATTIC` direction map |
| `KROTAT` delegation block | Sometimes | When `ROT-DEFI` index assigned | Do not duplicate/conflict with SDUM |
| `SUBROUTINE LATTIC` signature | No | FLUKA interface | — |
| `ENTRY LATNOR` signature | No | FLUKA interface | — |
| Includes / common blocks | Usually no | FLUKA geometry infrastructure | — |
| Unsupported `IRLTGG` handler | Yes | Clear STOP or error message | Cover all assigned indices |

## Auxiliary input files

`LATTIC` does not require a separate auxiliary input file. All geometry and lattice activation data live in the combinatorial geometry section of the `.inp` deck (`LATTICE`, optional `LATTSNGL`, and `ROT-DEFI` cards).

User implementations may optionally read external tables (cell-offset lists, transformation coefficients). If used:

1. place files beside the run input;
2. document names and units;
3. fail clearly if a file is missing;
4. include them in AutoFLUKA run notes.

## Output files and output patterns

`LATTIC` does not write its own output files. Validation is indirect:

| Validation artefact | What it shows |
|---|---|
| Geometry plot (`PLOTGEOM`) | Replicated cells align with intended symmetry |
| FLUKA geometry test / transport | Tracking does not report impossible region transitions |
| Low-NPS run log | No `LATTIC` / lattice support errors |

Watch for runtime messages indicating unsupported lattice numbers or internal `LATTIC` aborts when `IFLAG < 0` with inconsistent call state.

## Compile/link behavior

`LATTIC` must be compiled and linked into a custom FLUKA executable when the `LATTICE` card requires the user routine (empty/null SDUM or no `ROT#` string and no transformation name).

General concept:

```text
lattic.f (+ other user routines) -> compile objects -> link custom FLUKA executable -> run deck
```

Guidance:

- Pass `lattic.f` explicitly through `subroutine_paths` when using AutoFLUKA.
- If multiple user routines are needed (`SOURCE`, `MGDRAW`, etc.), provide all `.f` files together.
- Keep the selected `lattic.f` beside the `.inp` or pass an absolute path.
- Verify compile/link logs before interpreting geometry or transport results.

When **only** `ROT-DEFI` names appear on `LATTICE` SDUM and the template delegates correctly, a custom executable may still be required if other user routines are present; the `LATTIC` body may remain at template defaults.

## AutoFLUKA execution behavior

For AutoFLUKA:

1. Parse the geometry section for `LATTICE` / `LATTSNGL` cards.
2. Determine whether SDUM forces a user `LATTIC` implementation.
3. If yes, require explicit `subroutine_paths` pointing to the user `lattic.f`.
4. Do **not** rely on `SOURCE`-only auto-detection for `LATTIC`.
5. Copy input and routines into the active `test-n` folder when executing.
6. Run geometry plot or low-primary transport to validate transforms.
7. Only proceed to production after a clean test run.

Recommended test ladder:

```text
test-1: compile/link + geometry plot
test-2: low-NPS transport smoke test
production: after checklist passes
```

## Validation checklist

Before execution:

- [ ] Prototype and container regions are defined.
- [ ] `LATTICE` WHAT fields match the intended region and lattice numbering.
- [ ] SDUM path (ROT-DEFI vs user routine) is intentional.
- [ ] All `ROT-DEFI` transformations referenced on cards exist in the deck.
- [ ] Materials assigned only on prototype regions.
- [ ] No region spans multiple lattice cells after transform.
- [ ] `lattic.f` defines `LATTIC` and `LATNOR` when user routine path is active.
- [ ] Every assigned `IRLTGG` has both `LATTIC` and `LATNOR` logic.
- [ ] PLOTGEOM is scheduled after all transforms are defined.
- [ ] Low-NPS `test-n` is planned.

After execution:

- [ ] Compile/link succeeded.
- [ ] Geometry plot shows correct replica placement (if used).
- [ ] No unsupported-lattice or `LATTIC` abort messages.
- [ ] Transport completes without geometry errors.
- [ ] Spot-check: particle paths behave plausibly in outer vs inner cells.
- [ ] Production run not started until low-NPS validation passes.

## Common errors and fixes

| Error signature / symptom | Typical cause | Suggested fix |
|---|---|---|
| `Lattice geometry non supported` / STOP on `IRLTGG` | Branch missing for an assigned lattice number | Add `LATTIC`/`LATNOR` branches for every `WHAT(4)`–`WHAT(5)` index used. |
| Wrong replica placement in plot | `IRLTGG` numbering mismatch vs `LATTICE` card | Reconcile `WHAT(4)`, `WHAT(5)`, `WHAT(6)` with Fortran branches. |
| Tracking errors / particles lost in lattice | Region spans two cells after transform | Redesign prototype regions to fit inside each cell. |
| Materials wrong in replicas | Material assigned to container regions | Assign materials only on prototype/basic-unit regions. |
| Normals / boundary issues at cell interfaces | `LATNOR` not inverse of `LATTIC` direction map | Fix `LATNOR` branch; use temporaries for rotations. |
| User routine never seems called | SDUM names a `ROT-DEFI` transformation | Expected: FLUKA uses ROT-DEFI path; empty SDUM to force user code. |
| Conflicting transforms | Manual `GO TO` ladder edits while `KROTAT` also set | Use either ROT-DEFI delegation or custom branches, not both for same cell. |
| PLOTGEOM shows wrong layout | Plot issued before all `ROT-DEFI` / lattice defs | Move PLOTGEOM after transform definitions. |
| `LATTIC called with ... Iflag < 0` | Internal call-state error / inconsistent edits | Restore template call structure; review unsupported branches. |
| Geometry OK but results identical in all cells | All `IRLTGG` branches identical or identity | Implement distinct transforms per cell index as intended. |
| Free-format name errors | Numeric region IDs on `LATTICE` while geometry uses names | Use alphanumeric names consistently on `LATTICE` cards. |

## Version drift

Drafted against the **2024 FLUKA Manual PDF edition** from https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals (`LATTICE` Sec. 8.2.10; `LATTIC`/`LATNOR` Sec. 13.2.11; `ROT-DEFI` Sec. 7.63). Verify against the manual for the installed FLUKA version. The [online manual](https://flukafiles.web.cern.ch/manual/index.html) may differ in section numbering.

## Related examples

Read these worked case files when implementing lattice geometry:

- `examples/LATTIC_GEOMETRY_ACTIVATION.md` — modular calorimeter with explicit user `LATTIC` (empty SDUM, per-cell z-translation ladder)
- `examples/LATTIC_ROTDEFI_REPLICA_CASE.md` — target replica using `ROT-DEFI` + `LATTICE` without custom Fortran

## Routine-interface summary without code redistribution

The LATTIC user-routine `.f` file shipped with a licensed FLUKA installation may expose:

```text
SUBROUTINE LATTIC ( XB, WB, DIST, SB, UB, IR, IRLTGG, IRLT, IFLAG )
ENTRY LATNOR ( UN, IRLTNO, IRLT )
```

This guide describes roles, card coupling, and safe editing zones in original prose and pseudocode only. **AutoFLUKA does NOT ship** licensed FLUKA installation files or Fortran templates.

## Manual references

**Agent citation format:** `FLUKA Manual (2024 PDF edition), FLUKA Collaboration, Sec. …, p. …, manuals page https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals` — do not cite local parse filenames. See `../SKILL.md`.

- **Manuals page:** https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals
- **2024 PDF:** https://www.fluka.eu/Fluka/www/html/content/manuals/FM.pdf
- **This routine (2024 PDF edition):** `LATTICE` Sec. 8.2.10, pp. 328–329; `LATTSNGL` Sec. 8.2.11, p. 329; `ROT-DEFI` Sec. 7.63, p. 237; `LATTIC`/`LATNOR` Sec. 13.2.11, p. 407; replica example p. 324

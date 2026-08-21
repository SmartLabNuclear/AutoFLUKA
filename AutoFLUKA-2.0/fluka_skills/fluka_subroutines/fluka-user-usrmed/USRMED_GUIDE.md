# FLUKA USRMED user routine

## Purpose

`USRMED` is a user-written **subroutine** invoked during **transport** whenever a particle is about to move in a material flagged by `MAT-PROP` with `SDUM = USERDIREctive`. It implements **medium-dependent directives**: weight changes, boundary refraction/reflection logic, region reassignment, and direction updates that standard cards do not express.

Unlike `FLUSCW` / `COMSCW` (scoring-time weighting via `USERWEIG`), `USRMED` hooks **into particle transport** in selected materials. It can directly alter weights, directions, and region assignment for continuing transport.

Typical applications (manual §7.44, §13.2.29):

- optical-photon **absorption** simulated by weight reduction inside a medium;
- **refraction** at material boundaries by adjusting direction cosines;
- **reflection (albedo)** at boundaries with `NEWREG` set back to `MREG`;
- user-driven **biasing or particle selection** on a material basis.

## When to use

Use `USRMED` when transport in specific materials requires user logic at **step/boundary** level that cannot be achieved with standard cards alone.

Appropriate use cases include:

1. **Optical photon transport** with `OPT-PROP` — custom refraction, absorption weighting, or boundary behaviour beyond built-in optics (manual notes this is the typical use).

2. **In-medium weight attenuation** (`MREG = NEWREG`) — reduce `WEE` to simulate bulk absorption without killing transport prematurely in other ways.

3. **Boundary refraction** (`MREG ≠ NEWREG`) — modify `TXX`, `TYY`, `TZZ` using surface normal from `FLKSTK` commons.

4. **Boundary reflection / albedo** (`MREG ≠ NEWREG`) — apply reflection law; set `NEWREG = MREG` to keep particle in same region.

5. **Particle killing** — set `WEE = 0` (manual); note spot depositions still occur and cannot be killed by `USRMED`.

## When not to use

Do **not** use `USRMED` for:

| Goal | Use instead |
|---|---|
| Scoring-time fluence weighting | `FLUSCW` + `USERWEIG` `WHAT(3)` |
| Scoring-time energy/star weighting | `COMSCW` + `USERWEIG` `WHAT(6)` |
| Primary source generation | `SOURCE` + `BEAM` / `BEAMPOS` |
| Custom event dumps | `MGDRAW` + `USERDUMP` |
| Standard optical properties only | `OPT-PROP`, `RFRNDX`, `RFLCTV`, `OPHBDX` |
| Material density for dE/dx only | `CORRFACT`, `MAT-PROP` RHOR, `ASSIGNMAt` |
| Region importance biasing | `BIASING`, weight windows |

Prefer built-in optical routines (`RFRNDX`, `RFLCTV`, `FRGHNS`, `OPHBDX`) before custom `USRMED` when they suffice.

`USRMED` affects **transport physics/path**. Validate carefully against reference cases.

## Activation card or activation condition

`USRMED` is activated through **`MAT-PROP`** with **`SDUM = USERDIREctive`** (or `USERDIRE` in fixed columns).

```text
MAT-PROP  WHAT(1)  WHAT(2)  WHAT(3)  WHAT(4)  WHAT(5)  WHAT(6)  USERDIRE
```

### `MAT-PROP` fields for `USERDIREctive`

| Field | Meaning |
|---|---|
| `WHAT(1) > 0.0` | Enable `USRMED` calls for selected materials |
| `WHAT(1) = 0.0` | Ignored |
| `WHAT(1) < 0.0` | Reset previous USERDIRE setting to default (no `USRMED`) |
| `WHAT(2)`, `WHAT(3)` | Not used |
| `WHAT(4)` | Lower bound material index or name |
| `WHAT(5)` | Upper bound material index or name (default `WHAT(4)`) |
| `WHAT(6)` | Step in material index assignment (default `1.0`) |
| `SDUM` | `USERDIREctive` |

### When calls occur

`USRMED` is called **every time a particle is going to be transported** in a user-flagged material.

**Critical limitation (manual):** spot depositions are performed anyway — they **cannot be killed** by `USRMED`.

### Manual activation examples

Pb glass and PMMA (numeric materials 15–18):

```text
MAT-PROP     1.0     0.0     0.0    15.0    18.0     3.0    USERDIRE
```

Optical photons in materials 17 and 21 (with `OPT-PROP`):

```text
MAT-PROP     1.0     0.0     0.0    17.0    21.0     4.0    USERDIRE
```

Name-based variant:

```text
MAT-PROP     1.0     0.0     0.0    PMMA    LEADGLAS     3.0    USERDIRE
```

### Ordering note

`MAT-PROP` for gas pressure must sometimes follow `MATERIAL` immediately (manual §7.44). `MAT-PROP` is one of the cards where **input order matters** (with `GLOBAL`, `DEFAULTS`, `PLOTGEOM`).

## Input-card syntax and required deck checks

| Check | Required action |
|---|---|
| `MAT-PROP` USERDIRE present | `WHAT(1) > 0` and `SDUM = USERDIREctive` |
| Material range correct | `WHAT(4)`–`WHAT(5)` cover intended materials only |
| Materials assigned to regions | `ASSIGNMAt` links regions to flagged materials |
| Optical case | `OPT-PROP` / `OPT-PROD` configured if optical photons involved |
| `usrmed.f` linked | Custom executable includes user routine when non-default |
| Not confused with other MAT-PROP SDUM | `DPA-ENER`, `X-REFLECTivity` are different modes |
| Reference case planned | Compare to built-in optics or no-USRMED baseline |
| Low-NPS test | Transport behaviour validated before production |

## Required Fortran routine identity

The following structure may be present in the `usrmed.f` user-routine file shipped with a licensed FLUKA installation:

```text
SUBROUTINE USRMED ( IJ, EKSCO, PLA, WEE, MREG, NEWREG, XX, YY, ZZ,
     &                TXX, TYY, TZZ, TXXPOL, TYYPOL, TZZPOL )
```

The installed template may include **polarization** direction arguments (`TXXPOL`, `TYYPOL`, `TZZPOL`). Verify the exact signature against the licensed template.

### Conceptual argument map

| Argument | Role |
|---|---|
| `IJ` | Particle type (generalized code) |
| `EKSCO` | Kinetic energy (GeV) |
| `PLA` | Momentum (GeV/c) |
| `WEE` | Particle weight |
| `MREG` | Previous / original region number |
| `NEWREG` | Current / final region number |
| `XX`, `YY`, `ZZ` | Position |
| `TXX`, `TYY`, `TZZ` | Direction cosines |
| `TXXPOL`, `TYYPOL`, `TZZPOL` | Polarization direction (if present in template) |

Manual §13.2.29 argument list documents `IJ` through `TZZ`; polarization may appear in the installed template for optical photon work.

### Two transport cases (core logic)

| Condition | Meaning | User may modify |
|---|---|---|
| `MREG = NEWREG` | Particle moves from a point **inside** the medium | **`WEE` only** (typical: bulk absorption via weight reduction) |
| `MREG ≠ NEWREG` | Particle moves from a point on a **boundary** between regions | **`WEE`**, **`NEWREG`**, **`TXX/TYY/TZZ`** (and polarization if used) |

Template comment (licensed install): change only `WEE` when `MREG = NEWREG`; when `MREG ≠ NEWREG`, also `NEWREG` and direction (and polarization) may change.

### Typical boundary applications (manual)

- **Refraction:** adjust direction cosines so the ray remains in the correct region; often needs surface normal `TXNOR`, `TYNOR`, `TZNOR` from `COMMON FLKSTK` (`flkstk.inc`).
- **Reflection:** apply reflection law; set `NEWREG = MREG`.
- **Weight reduction:** account for reflectivity; `WEE = 0` kills the particle.
- **Surface roughness:** `FRGHNS` user function (§13.2.9) for optical photons.

## Expected user-provided `.f` file checks

- [ ] Defines `SUBROUTINE USRMED` with template signature.
- [ ] Branches correctly on `MREG` vs `NEWREG`.
- [ ] Does not modify disallowed variables in the in-medium branch.
- [ ] Direction cosines renormalized after refraction/reflection edits.
- [ ] `NEWREG = MREG` set explicitly for reflection cases.
- [ ] Optical photon id (`IJ = -1` per manual optical chapter) handled when relevant.
- [ ] Required includes added only when used (`flkstk.inc` for normals, etc.).
- [ ] No assumption that depositions can be suppressed.

## Licensing-safe implementation policy

**AutoFLUKA does NOT ship** FLUKA-distributed `usrmed.f` templates, the FLUKA manual, or other licensed installation materials. This guide contains original prose and pseudocode only.

Users should provide or copy `usrmed.f` from their **licensed FLUKA installation**. See `../SKILL.md`.

## Upstream placement in the official FLUKA installation

Default template typically under user-routine sources (e.g. `src/user/usrmed.f`). Shipped template is empty (`RETURN` only) until the user adds logic.

## Mandatory setup before editing

1. List materials requiring custom transport logic.
2. Issue `MAT-PROP` `USERDIRE` only for those materials.
3. For optical photons: complete `OPT-PROP` baseline first.
4. Decide in-medium vs boundary behaviour per material.
5. Plan validation: weight conservation, ray directions, region counts.
6. Run low-NPS comparison without `USRMED` or with built-in optics only.

## Safe editing rules

- Preserve `SUBROUTINE USRMED` signature.
- Respect the **`MREG = NEWREG` vs `MREG ≠ NEWREG`** edit permissions.
- Renormalize direction cosines after changing `TXX`, `TYY`, `TZZ`.
- Use `WEE = 0` to kill; do not expect to cancel spot depositions.
- For refraction, include `flkstk.inc` and use `TXNOR(NPFLKA)` etc. per manual.
- Do not apply `USERDIRE` globally to all materials unless intentional.
- Document whether logic applies to all particles or only optical photons (`IJ`).
- `GEOR2N` for name-based region lookup when needed.

## Code implementation sections

### Default template behaviour

Empty body with immediate `RETURN` — no effect on transport.

### Pattern A — in-medium absorption (optical photon weight)

When `MREG = NEWREG` and particle is optical photon in absorbing material:

```text
IF MREG == NEWREG THEN
    IF IJ == optical_photon_code THEN
        WEE = WEE * exp(-mu_abs * step_length_estimate)
        ! or use per-step attenuation factor from OPT-PROP absorption coefficient
    ENDIF
ENDIF
RETURN
```

Manual cites reducing photon weight in absorbing media as the typical `MREG = NEWREG` application.

### Pattern B — boundary reflection

When `MREG /= NEWREG`:

```text
IF IJ == optical_photon_code THEN
    ! compute reflected direction from incident TXX,TYY,TZZ and normal TXNOR,TYNOR,TZNOR
    apply_reflection_law(...)
    NEWREG = MREG
    optionally reduce WEE for reflectivity < 1
ENDIF
RETURN
```

### Pattern C — boundary refraction

When `MREG /= NEWREG`:

```text
INCLUDE flkstk.inc
! use TXNOR(NPFLKA), TYNOR(NPFLKA), TZNOR(NPFLKA)
compute_refracted_direction(...)
! ensure particle remains in intended region; may adjust TXX,TYY,TZZ only
RETURN
```

### Pattern D — kill particle

```text
WEE = 0.0D0
RETURN
```

Depositions at the spot still occur per manual.

### Editable-section map

| Case | Editable outputs | Do not change |
|---|---|---|
| `MREG = NEWREG` | `WEE` | `NEWREG`, directions (by convention) |
| `MREG ≠ NEWREG` | `WEE`, `NEWREG`, `TXX/TYY/TZZ`, polarization | `IJ`, `EKSCO`/`PLA` unless documented side effect |
| SUBROUTINE signature | No | FLUKA interface |

## Auxiliary input files

Usually none. Optical cases may read wavelength-dependent tables externally; document and place beside run input if used.

## Output files and output patterns

`USRMED` does not write its own output file. Effects appear in transport results, optical photon counts, energy depositions, and region histories.

Validate indirectly via:

- optical photon survival weights;
- expected reflection/refraction angles;
- energy deposition patterns in detectors;
- comparison to built-in `OPT-PROP` behaviour.

## Compile/link behavior

```text
usrmed.f (+ other routines) -> compile -> link custom executable -> run with MAT-PROP USERDIRE
```

Pass `usrmed.f` explicitly via `subroutine_paths` in AutoFLUKA.

## AutoFLUKA execution behavior

1. Parse deck for `MAT-PROP` with `USERDIRE` / `USERDIREctive`.
2. Confirm `WHAT(1) > 0` and material range.
3. Require `subroutine_paths` for `usrmed.f` when custom logic is needed.
4. Do not rely on `SOURCE`-only auto-detection.
5. Run low-NPS `test-n`; compare to baseline without `USRMED` or with empty template.
6. For optical cases, verify `OPT-PROP` cards are present in processed deck.

Recommended ladder:

```text
test-1: compile/link; empty USRMED — should match no-USRMED if WHAT(1) disabled
test-2: enable USERDIRE on one material; check transport differs as expected
test-3: production only after physics sanity check
```

## Validation checklist

Before execution:

- [ ] `MAT-PROP` `USERDIRE` with `WHAT(1) > 0`.
- [ ] Material indices/names match `ASSIGNMAt`.
- [ ] `usrmed.f` preserves subroutine interface.
- [ ] In-medium vs boundary branches implemented correctly.
- [ ] Optical cards complete if `IJ = -1` logic used.
- [ ] Baseline reference case identified.

After execution:

- [ ] Compile/link succeeded.
- [ ] No unexpected `USRMED`-related aborts.
- [ ] Weight/direction changes match intended physics.
- [ ] No unintended materials affected.
- [ ] Deposition patterns understood (spot deps not suppressible).
- [ ] Production deferred until low-NPS validation passes.

## Common errors and fixes

| Error signature / symptom | Typical cause | Suggested fix |
|---|---|---|
| `USRMED` never called | `WHAT(1) <= 0` or wrong SDUM | Use `USERDIREctive` with `WHAT(1) > 0` |
| Called in wrong materials | `WHAT(4)`–`WHAT(5)` range too wide | Narrow material span |
| Directions non-physical | Cosines not renormalized after edit | Renormalize `TXX/TYY/TZZ` |
| Reflection leaves wrong region | `NEWREG` not reset | Set `NEWREG = MREG` for reflection |
| Tried to edit direction in-medium | `MREG = NEWREG` case | Only change `WEE` inside medium |
| No optical effect | Missing `OPT-PROP` | Add optical property cards |
| Built-in optics duplicated | `USRMED` + default refraction | Prefer `OPT-PROP` or disable redundant logic |
| Depositions still appear when "killed" | Spot deps not killable | Expected; adjust expectations |
| Compile error on `TXNOR` | Missing `flkstk.inc` | Include FLUKA stack common |
| Transport differs from manual | Polarization args in template | Match installed signature |
| MAT-PROP ignored | Wrong SDUM (`DPA-ENER`, etc.) | Use `USERDIREctive` specifically |

## Version drift

Drafted against the **2024 FLUKA Manual PDF edition** from https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals (`MAT-PROP` Sec. 7.44; `USRMED` Sec. 13.2.29; optical photon Chap. 12). Verify against the manual for the installed FLUKA version.

## Related examples

- `examples/USRMED_MATPROP_USERDIRE.md` — `MAT-PROP` activation for PMMA / lead glass (manual p.180)
- `examples/USRMED_OPTICAL_ABSORPTION_CASE.md` — in-medium optical photon weight attenuation (`MREG = NEWREG`)

## Routine-interface summary without code redistribution

The `usrmed.f` shipped with a licensed FLUKA installation may expose `SUBROUTINE USRMED` with particle kinematics, weight, region numbers, position, direction, and possibly polarization arguments.

**AutoFLUKA does NOT ship** licensed FLUKA installation files or Fortran templates.

## Manual references

**Agent citation format:** `FLUKA Manual (2024 PDF edition), FLUKA Collaboration, Sec. …, p. …, manuals page https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals` — do not cite local parse filenames. See `../SKILL.md`.

- **Manuals page:** https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals
- **2024 PDF:** https://www.fluka.eu/Fluka/www/html/content/manuals/FM.pdf
- **This routine (2024 PDF edition):** `MAT-PROP` Sec. 7.44, pp. 177–180; `USRMED` Sec. 13.2.29, p. 424; optical photons Chap. 12

# FLUKA FLUSCW user routine

## Purpose

`FLUSCW` is a user-written **function** that returns an extra multiplication factor applied at **scoring time** to flux-like quantities. It is activated through the `USERWEIG` input card when `WHAT(3) > 0.0`.

The scored quantity is multiplied by the value returned by `FLUSCW` before accumulation. Typical applications include:

- converting track-length fluence to **dose equivalent** or other response functions;
- particle-, energy-, region-, or direction-dependent **fluence weighting**;
- **conditional scoring** (score only when position, energy, or detector conditions are met);
- optical-photon **quantum-efficiency** weighting at detection;
- implementing **energy fluence** scoring when used with special `USRBIN` logic (manual notes this is not available from `USRBIN` alone);
- detector-specific weighting using `ISCRNG` / `JSCRNG` from `COMMON SCOHLP`.

`FLUSCW` affects **how much** of a flux-like score is accumulated. It does **not** replace standard scoring cards; it weights their contributions.

## When to use

Use `FLUSCW` when the user needs custom weighting of **fluence, current, or yield** estimators at scoring time.

Appropriate use cases include:

1. **USRTRACK track-length fluence → response quantity**  
   Apply energy- and particle-dependent conversion factors to region track-length fluence.

2. **USRBDX boundary current/fluence weighting**  
   Weight particles crossing selected region boundaries (current or fluence estimators).

3. **USRCOLL collision-density weighting**  
   Apply user logic to collision-density estimators.

4. **USRBIN track-length fluence binning**  
   When `USRBIN` is used for **track-length fluence** (not energy density), use `FLUSCW` — not `COMSCW`.

5. **USRYIELD yield weighting**  
   Multiply yield estimator contributions by a user function.

6. **Conditional or spatially selective fluence scoring**  
   Return `0.0` or set `LSCZER = .TRUE.` to skip scoring outside a region, energy window, or detector.

7. **Optical photon detection efficiency**  
   Apply quantum-efficiency curves at detection rather than only at production (see manual optical-photon chapters).

## When not to use

Do **not** use `FLUSCW` for deposited-energy, star-density, or dose-from-energy-deposition weighting. Use **`COMSCW`** instead (`USERWEIG` with `WHAT(6) > 0.0`).

| Scored quantity type | Use |
|---|---|
| Track-length fluence (`USRTRACK`, `USRBIN` fluence mode, `USRBDX` fluence) | `FLUSCW` |
| Boundary current (`USRBDX`) | `FLUSCW` |
| Yield (`USRYIELD`) | `FLUSCW` |
| Energy density / star density (`USRBIN`, `SCORE`, `EVENTBIN`) | `COMSCW` |
| Energy deposition in `DETECT` | `DETSCW` (via `USERWEIG` `WHAT(4)`) |
| Residual nuclei custom scoring | `USRRNC` (via `USERWEIG` `WHAT(5)`) |

Other cases where `FLUSCW` is **not** the right tool:

- Defining the primary particle source → use `SOURCE`.
- Event-level custom dumps → use `MGDRAW` / `USERDUMP`.
- Post-processing standard output without recompilation → offline analysis may suffice.
- Activation decay-time buildup factors at scoring → **not available** in `FLUSCW` or `COMSCW` (manual scoring notes).

When energy deposition dose in a region is the goal and standard `USRBIN` energy scoring suffices, prefer `COMSCW` or direct `USRBIN` energy options before writing `FLUSCW`.

## Activation card or activation condition

`FLUSCW` is activated through the **`USERWEIG`** input card.

General form:

```text
USERWEIG  WHAT(1)  WHAT(2)  WHAT(3)  WHAT(4)  WHAT(5)  WHAT(6)  SDUM
```

### `WHAT(3)` — FLUSCW activation and call timing

| `WHAT(3)` value | Behaviour |
|---|---|
| `< 0.0` | Reset default: no `FLUSCW` weighting |
| `= 0.0` | Ignored |
| `> 0.0` | Activate `FLUSCW`; multiply affected scores by returned factor |
| `1.0`–`2.0` | `FLUSCW` called **before** detector-applicability check |
| `> 2.0` | `FLUSCW` called **only after** confirming score applies to current detector |
| `= 2.0` or `4.0` | Also calls **`FLDSCP`** (fluence position shift along scored track) |

Default when `USERWEIG` is absent: `WHAT(3) = -1.0` (no extra weighting).

### Affected estimators (when `WHAT(3) > 0.0`)

Per manual §13.2.7, `FLUSCW` weights:

- yields from **`USRYIELD`**;
- fluences from **`USRBDX`**, **`USRTRACK`**, **`USRCOLL`**, **`USRBIN`**;
- currents from **`USRBDX`**.

### Manual activation examples

Detector-checked fluence weighting:

```text
USERWEIG     0.0     0.0     4.0     0.0     0.0     0.0
```

`FLUSCW` called only when the present score applies to the current detector.

Unconditional `COMSCW` example (shown for contrast — uses `WHAT(6)`, not `WHAT(3)`):

```text
USERWEIG     0.0     0.0     0.0     0.0     0.0     1.0
```

## Input-card syntax and required deck checks

Before compile/run, verify:

| Check | Required action |
|---|---|
| `USERWEIG` present | Card exists with `WHAT(3) > 0.0` for `FLUSCW` |
| Correct weighting family | Fluence/current/yield → `WHAT(3)`; not `WHAT(6)` (`COMSCW`) |
| Matching scorer cards | Deck includes at least one scorer that `FLUSCW` affects (`USRTRACK`, `USRBDX`, etc.) |
| `WHAT(3)` call timing | Choose `1`–`2` (early) vs `> 2` (after detector check) for performance/correctness |
| `FLDSCP` intent | If `WHAT(3) = 2` or `4`, plan for track-segment shifting via `FLDSCP` |
| Output interpretation | Extra weights do not automatically update printed titles/units — document them |
| User notice in output | Manual recommends inserting a user-written notice about extra weighting |
| Low-NPS test | Compare weighted vs unweighted (`FLUSCW = 1`) on small run |
| `fluscw.f` linked | Custom executable includes user `FLUSCW` when non-default logic is required |

### `WHAT(3)` call-timing guidance

| Pattern | When to use |
|---|---|
| `WHAT(3) = 1.0` or `2.0` | Need `FLUSCW` called even when detector does not apply (side effects or global logic) |
| `WHAT(3) = 3.0` or `4.0` | Typical production weighting — only score-relevant calls (more efficient) |

Note: `WHAT(3) = 4.0` also activates `FLDSCP` for fluence position shifts.

## Required Fortran routine identity

A user-provided FLUSCW Fortran file must preserve the FLUKA-expected function identity and argument list from the installed template.

The following structure may be present in the `fluscw.f` user-routine file shipped with a licensed FLUKA installation:

```text
DOUBLE PRECISION FUNCTION FLUSCW ( IJ, PLA, TXX, TYY, TZZ, WEE,
     &                             XX, YY, ZZ, NREG, IOLREG, LLO, NSURF )
```

Argument names in the manual may appear as `NRGFLK` instead of `NREG`; verify against the installed template signature.

### Conceptual argument map

| Argument | Role |
|---|---|
| `IJ` | Generalized particle code (input only — do not modify) |
| `PLA` | Momentum in GeV/c if `> 0`; kinetic energy in GeV if `< 0` (sign convention) |
| `TXX`, `TYY`, `TZZ` | Direction cosines (local copies — may be modified for scoring effect only) |
| `WEE` | Particle weight |
| `XX`, `YY`, `ZZ` | Position |
| `NREG` / `NRGFLK` | Current region (after boundary crossing) |
| `IOLREG` | Previous region — meaningful mainly for boundary-crossing estimators |
| `LLO` | Particle generation (input only — do not modify) |
| `NSURF` | Internal calling flag (not for general use) |

### Return value and `LSCZER`

| Output | Role |
|---|---|
| `FLUSCW` (function value) | Multiplication factor applied to the score |
| `LSCZER` (in `COMMON SCOHLP`) | If set `.TRUE.` before `RETURN`, forces **zero scoring** regardless of `FLUSCW` value — more efficient than returning `0.0` |

Default shipped template returns `FLUSCW = 1.0` and `LSCZER = .FALSE.` (no effect).

### Useful `COMMON SCOHLP` variables (flux-like estimators)

Include `scohlp.inc` (or equivalent) to access detector context:

| Variable | Meaning for `FLUSCW` |
|---|---|
| `ISCRNG = 1` | Boundary-crossing estimator (`USRBDX`) |
| `ISCRNG = 2` | Track-length binning (`USRBIN`) |
| `ISCRNG = 3` | Track-length estimator (`USRTRACK`) |
| `ISCRNG = 4` | Collision-density estimator (`USRCOLL`) |
| `ISCRNG = 5` | Yield estimator (`USRYIELD`) |
| `JSCRNG` | Binning/detector number within that estimator class |

**Important:** the same `JSCRNG` number can appear for different estimator types — always combine `ISCRNG` + `JSCRNG` to identify the active detector.

`ISCRNG` meanings differ between `FLUSCW` and `COMSCW`; do not reuse `COMSCW` logic blindly.

## Expected user-provided `.f` file checks

- [ ] File defines `DOUBLE PRECISION FUNCTION FLUSCW` with template argument list.
- [ ] Required includes present (`dblprc.inc`, `dimpar.inc`, `iounit.inc` at minimum).
- [ ] `scohlp.inc` included when using `ISCRNG`, `JSCRNG`, or `LSCZER`.
- [ ] `FLUSCW` assigned on every code path before `RETURN`.
- [ ] `LSCZER` initialized or explicitly set each call.
- [ ] `IJ`, `LLO`, `NSURF` not modified.
- [ ] Units and response function documented in comments or companion guide.
- [ ] Energy convention for `PLA` handled correctly (sign test).
- [ ] Detector filtering uses `ISCRNG` and `JSCRNG`, not `JSCRNG` alone.

## Licensing-safe implementation policy

**AutoFLUKA does NOT ship** FLUKA-distributed `fluscw.f` templates, the FLUKA manual, or other licensed installation materials. This guide contains original prose and pseudocode only.

Users should provide or copy `fluscw.f` from their **licensed FLUKA installation** or supply a user case file. See `../SKILL.md`.

## Upstream placement in the official FLUKA installation

The default `fluscw.f` template is typically under the user-routine sources in the FLUKA distribution (commonly `src/user/fluscw.f` or equivalent).

The shipped template is a **dummy** returning `1.0` for back-compatibility. User-developed versions replace the body while preserving the function interface.

## Mandatory setup before editing

1. Identify the **scorer type** (`USRTRACK`, `USRBDX`, `USRBIN` fluence, etc.).
2. Confirm **`FLUSCW`** is correct vs `COMSCW` for that quantity.
3. Add **`USERWEIG`** with appropriate `WHAT(3)`.
4. Define the **response function** (tables, formula, units) outside Fortran or in data files.
5. Plan **validation**: unweighted baseline run with `FLUSCW = 1`.
6. Document how output titles/normalisation should be interpreted after weighting.

## Safe editing rules

- Preserve the `FUNCTION FLUSCW` signature from the installed template.
- Do not remove required `INCLUDE` lines unless you understand the dependency.
- Use `LSCZER = .TRUE.` for hard rejections; use `FLUSCW = 0.D0` only when appropriate.
- Branch on `ISCRNG` **and** `JSCRNG` for detector-specific logic.
- Respect `PLA` sign convention for energy vs momentum.
- `IOLREG` is meaningful mainly for `USRBDX`; do not rely on it for `USRTRACK`.
- Argument copies (except `IJ`, `LLO`, `NSURF`) may be modified to affect scoring without changing transport — use cautiously and document side effects.
- Optional includes: `flkmat.inc` (materials), `trackr.inc` (particle age, user flags), `paprop.inc` (particle properties).
- For name-based geometry, use `GEOR2N` to map region numbers to names when needed.

## Code implementation sections

### Default template behaviour

The licensed-installation dummy template typically:

```text
FLUSCW = 1.0
LSCZER = .FALSE.
RETURN
```

This preserves standard scoring until the user adds logic.

### Pattern A — energy-dependent response (dose equivalent style)

Conceptual pseudocode for track-length fluence weighting:

```text
INCLUDE scohlp.inc

EKIN = kinetic energy derived from PLA sign convention
IF ISCRNG == track-length estimator AND JSCRNG == target_detector_number THEN
    FLUSCW = response_function(IJ, EKIN, NREG)
ELSE
    FLUSCW = 1.0
ENDIF
LSCZER = .FALSE.
RETURN
```

Replace `response_function` with tabulated ICRP factors, user coefficients, or energy bins read from an auxiliary file.

### Pattern B — conditional scoring (spatial gate)

```text
IF point_outside_scoring_window(XX, YY, ZZ) THEN
    LSCZER = .TRUE.
    FLUSCW = 1.0
ELSE
    LSCZER = .FALSE.
    FLUSCW = 1.0
ENDIF
RETURN
```

Manual notes this can approximate 2-D fluence binning on a plane boundary.

### Pattern C — particle and region filter

```text
IF IJ /= desired_particle .OR. NREG /= desired_region THEN
    LSCZER = .TRUE.
ELSE
    FLUSCW = user_factor
ENDIF
RETURN
```

### Pattern D — optical photon quantum efficiency

For optical photon transport, apply wavelength/angle-dependent efficiency at detection using position, direction, and `IJ` for optical photons — often combined with `USRBDX` into a photosensor region.

### Editable-section map

| Section | Editable? | Use for | Main caution |
|---|---:|---|---|
| Function body / branching | Yes | Response functions, filters | Preserve all return paths |
| `FLUSCW` assignment | Yes | Multiplicative weight | Document units |
| `LSCZER` assignment | Yes | Efficient zero scoring | Do not leave undefined |
| `INCLUDE scohlp.inc` usage | Yes | `ISCRNG`, `JSCRNG`, `LSCZER` | `ISCRNG` meanings differ from `COMSCW` |
| Optional `FLKMAT`, `TRACKR` | Sometimes | Material, age, user flags | Match installed include names |
| Function signature | No | FLUKA interface | Breaking prevents link/correct calls |
| `IJ`, `LLO`, `NSURF` modification | No | Reserved inputs | Undefined behaviour |

## Auxiliary input files

`FLUSCW` does not require auxiliary files, but implementations often use:

- energy–response tables (dose conversion, efficiency curves);
- region or detector ID maps;
- particle-selection lists.

If used:

1. place files beside the run input;
2. open on safe logical units or use Fortran `OPEN` once in first-call initialization;
3. fail clearly if missing;
4. document units and interpolation method.

## Output files and output patterns

`FLUSCW` does not create its own output file. It modifies how standard scorer output accumulates.

After a weighted run:

| Artefact | What to verify |
|---|---|
| `*_nnn.lis` / USRTRACK files | Values reflect weighting — titles may still say "fluence" |
| Sum over regions | Compare to unweighted test × expected factor |
| Zero regions | Conditional logic may leave empty bins |

Manual warning: printed titles, headings, and normalisations may **not** remain valid after extra weighting. Add a `TITLE` or comment card note describing the applied response function.

## Compile/link behavior

`FLUSCW` must be compiled and linked when non-default weighting is required.

```text
fluscw.f (+ other user routines) -> compile -> link custom executable -> run deck with USERWEIG
```

- Pass `fluscw.f` explicitly via `subroutine_paths` in AutoFLUKA.
- Link with other routines (`SOURCE`, `MGDRAW`, etc.) in one custom executable when needed.
- Verify compile/link log before interpreting scorer output.

## AutoFLUKA execution behavior

1. Detect `USERWEIG` with `WHAT(3) > 0.0` in the processed deck.
2. Confirm at least one FLUSCW-affected scorer card exists.
3. Require explicit `subroutine_paths` for `fluscw.f` when custom logic is needed.
4. Do **not** rely on `SOURCE`-only auto-detection.
5. Run low-NPS `test-n` with and without weighting logic enabled.
6. Compare first bins to hand-calculated factors before production.

Recommended ladder:

```text
test-1: compile/link; FLUSCW returns 1.0 — baseline matches no USERWEIG
test-2: enable weighting; spot-check one region/particle/energy bin
production: after units and detector mapping verified
```

## Validation checklist

Before execution:

- [ ] `USERWEIG` with `WHAT(3) > 0.0`.
- [ ] Scorer cards match FLUSCW family (not COMSCW-only quantities).
- [ ] `WHAT(3)` call timing chosen deliberately.
- [ ] `fluscw.f` preserves function interface.
- [ ] Response function units documented.
- [ ] Baseline unweighted test planned.
- [ ] Output interpretation note planned for weighted quantities.

After execution:

- [ ] Compile/link succeeded.
- [ ] Run completed without `FLUSCW`/scoring errors.
- [ ] Weighted output differs from baseline in expected way.
- [ ] Detector numbers (`JSCRNG`) match intended scorers.
- [ ] No accidental zeroing (`LSCZER` or `FLUSCW = 0` everywhere).
- [ ] Production not started until spot checks pass.

## Common errors and fixes

| Error signature / symptom | Typical cause | Suggested fix |
|---|---|---|
| No weighting effect | `WHAT(3) <= 0` or dummy `FLUSCW` still returns 1 | Activate `USERWEIG`; verify custom `fluscw.f` linked |
| Wrong quantity weighted | Used `FLUSCW` for energy density | Switch to `COMSCW` (`WHAT(6)`) for deposition/star scores |
| `USRBIN` energy scoring wrong | `COMSCW` needed, not `FLUSCW` | Manual note: track-length fluence → `FLUSCW`; energy density → `COMSCW` |
| All scores zero | `LSCZER = .TRUE.` always or `FLUSCW = 0` always | Review branches; use selective `LSCZER` |
| Wrong detector weighted | Used `JSCRNG` without `ISCRNG` | Filter on both variables |
| Energy bins wrong | Misread `PLA` sign (momentum vs kinetic energy) | Branch on `PLA > 0` vs `< 0` per manual |
| `IOLREG` logic fails on USRTRACK | `IOLREG` only meaningful for boundary estimators | Use `NREG` for track-length estimators |
| Output units misleading | Extra weight not reflected in titles | Add user notice; document response in guide |
| Slow run | `WHAT(3) = 1` with heavy logic in non-scoring calls | Use `WHAT(3) > 2` for detector-checked calls |
| Compile error on includes | Wrong include name or missing commons | Match installed FLUKA include conventions |
| Differs across FLUKA versions | Argument names (`NREG` vs `NRGFLK`) | Verify against installed `fluscw.f` template |

## Version drift

Drafted against the **2024 FLUKA Manual PDF edition** from https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals (`USERWEIG` Sec. 7.84; `FLUSCW` Sec. 13.2.7; `SCOHLP` Sec. 13.1.1). Verify against the manual for the installed FLUKA version.

## Related examples

- `examples/FLUSCW_USERWEIG_ACTIVATION.md` — `USERWEIG` + `USRTRACK` activation and call-timing choice
- `examples/FLUSCW_USRTRACK_DOSE_EQUIVALENT_CASE.md` — energy-dependent fluence-to-dose-equivalent weighting pattern

For energy-deposition weighting, see `fluka-user-comscw/COMSCW_GUIDE.md` when available.

## Routine-interface summary without code redistribution

The `fluscw.f` file shipped with a licensed FLUKA installation may expose:

```text
DOUBLE PRECISION FUNCTION FLUSCW ( ... )
```

with arguments for particle type, momentum/energy, direction, weight, position, regions, generation, and internal flags; and may use `COMMON SCOHLP` for `ISCRNG`, `JSCRNG`, and `LSCZER`.

This guide describes roles and safe editing zones in original prose only. **AutoFLUKA does NOT ship** licensed FLUKA installation files or Fortran templates.

## Manual references

**Agent citation format:** `FLUKA Manual (2024 PDF edition), FLUKA Collaboration, Sec. …, p. …, manuals page https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals` — do not cite local parse filenames. See `../SKILL.md`.

- **Manuals page:** https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals
- **2024 PDF:** https://www.fluka.eu/Fluka/www/html/content/manuals/FM.pdf
- **This routine (2024 PDF edition):** `USERWEIG` Sec. 7.84, pp. 271–272; `FLUSCW` Sec. 13.2.7, p. 404; `SCOHLP` Sec. 13.1.1, p. 400

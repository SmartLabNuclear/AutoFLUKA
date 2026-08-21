# FLUKA COMSCW user routine

## Purpose

`COMSCW` is a user-written **function** that returns an extra multiplication factor applied at **scoring time** to **density-like** quantities: deposited energy, star densities, and related scoring contributions. It is activated through the `USERWEIG` input card when `WHAT(6) > 0.0`.

The amount to be deposited (`RULL`, unweighted) is multiplied by the returned factor before accumulation. Typical applications include:

- converting **energy density** to **dose in Gy** using local material density;
- particle-, region-, or detector-dependent **energy-deposition weighting**;
- **star-density** response or filtering;
- **conditional scoring** (reject depositions outside a region or energy window);
- optical-photon **quantum-efficiency** selection on energy deposition steps;
- custom weighting for `SCORE`, `USRBIN`, `EVENTBIN`, and residual-nuclei-related scoring paths described in the manual.

`COMSCW` weights how much of a deposition-related score is accumulated. It does not replace standard scoring cards.

## When to use

Use `COMSCW` when the user needs custom weighting of **energy deposition, star density, or related density-like scores** at scoring time.

Appropriate use cases include:

1. **USRBIN energy-density → dose (Gy)**  
   Divide by local density (manual example pattern) so mesh bins crossing material boundaries average correctly.

2. **SCORE region energy or star density weighting**  
   Apply response factors per region, particle type, or deposited amount.

3. **EVENTBIN event-wise energy/star weighting**  
   Modify per-event binned deposition scores.

4. **RESNUCLEi-related scoring weighting**  
   When manual paths multiply residual-nuclei production scores via `COMSCW`.

5. **Conditional deposition scoring**  
   Return `0.0` or set `LSCZER = .TRUE.` to skip unwanted deposition steps.

6. **Optical photon detection on energy deposition**  
   Select photocathode depositions with extra efficiency logic (manual optical-photon chapter).

7. **Detector-specific factors via `ISCRNG` / `JSCRNG`**  
   Different weighting per USRBIN binning or scoring detector index.

## When not to use

Do **not** use `COMSCW` for fluence, current, or yield weighting. Use **`FLUSCW`** (`USERWEIG` with `WHAT(3) > 0.0`).

| Scored quantity type | Use |
|---|---|
| Energy density (`USRBIN`, `SCORE`, `EVENTBIN`) | `COMSCW` |
| Star density | `COMSCW` |
| Track-length fluence (`USRTRACK`, `USRBIN` fluence mode) | `FLUSCW` |
| Boundary current/fluence (`USRBDX`) | `FLUSCW` |
| Yield (`USRYIELD`) | `FLUSCW` |
| `DETECT` pulse-height hit modification | `DETSCW` (`USERWEIG` `WHAT(4)`) — not `COMSCW` |
| Residual nuclei custom hook logic | `USRRNC` (`USERWEIG` `WHAT(5)`) |

Other cases where `COMSCW` is **not** the right tool:

- Birks quenching alone → consider `TCQUENCH` on selected binnings first.
- Primary source definition → `SOURCE`.
- Activation decay-time buildup factor at scoring → **not available** in `COMSCW` or `FLUSCW`.
- Post-processing only → offline analysis may suffice without recompile.

**USRBIN split rule (manual Note 3):** track-length **fluence** binning → `FLUSCW`; energy or **star density** binning → `COMSCW`.

## Activation card or activation condition

`COMSCW` is activated through **`USERWEIG`**.

```text
USERWEIG  WHAT(1)  WHAT(2)  WHAT(3)  WHAT(4)  WHAT(5)  WHAT(6)  SDUM
```

### `WHAT(6)` — COMSCW activation and call timing

| `WHAT(6)` value | Behaviour |
|---|---|
| `< 0.0` | Reset default: no `COMSCW` weighting |
| `= 0.0` | Ignored |
| `> 0.0` | Activate `COMSCW` |
| `1.0`–`2.0` | `COMSCW` called **before** detector-applicability check |
| `> 2.0` | `COMSCW` called **only after** confirming score applies to current detector |
| `= 2.0` or `4.0` | Also calls **`ENDSCP`** (shift deposited energy along step — instrument drift) |

Default when `USERWEIG` absent: `WHAT(6) = -1.0` (no extra weighting).

### Affected estimators (when `WHAT(6) > 0.0`)

Per manual §13.2.2, `COMSCW` weights quantities from:

- **`SCORE`** (p. 243);
- **`USRBIN`** energy/star density modes (p. 276);
- **`EVENTBIN`** energy and stars (p. 132);
- energy deposition via **`DETECT`** (p. 109) — see also `DETSCW` via `WHAT(4)` for pulse-height hit modification;
- residual nuclei production via **`RESNUCLEi`** (p. 234);
- other density-like quantities documented in `scohlp.inc` / installed template comments.

### Manual activation example

Unconditional dose/star weighting:

```text
USERWEIG     0.0     0.0     0.0     0.0     0.0     1.0
```

`COMSCW` called before detector check. Dose and star densities multiplied per user logic.

Detector-checked fluence example (for contrast — uses `FLUSCW`, not `COMSCW`):

```text
USERWEIG     0.0     0.0     4.0     0.0     0.0     0.0
```

## Input-card syntax and required deck checks

| Check | Required action |
|---|---|
| `USERWEIG` present | `WHAT(6) > 0.0` for `COMSCW` |
| Correct weighting family | Energy/star/density → `WHAT(6)`; not `WHAT(3)` (`FLUSCW`) |
| Matching scorer | Deck includes `SCORE`, `USRBIN`, `EVENTBIN`, `DETECT`, and/or `RESNUCLEi` as intended |
| `USRBIN` scoring type | Energy/star density uses `COMSCW`; track-length fluence uses `FLUSCW` |
| `WHAT(6)` call timing | `1`–`2` early vs `> 2` after detector check |
| `ENDSCP` intent | `WHAT(6) = 2` or `4` enables energy-position shifting |
| No double response | Do not apply same factor in `COMSCW` and offline post-processing |
| Output interpretation | Document weighted units; titles may not auto-update |
| User notice | Manual recommends noting extra weighting in output |
| Low-NPS test | Baseline with `COMSCW = 1` before production |
| `comscw.f` linked | Custom executable when non-default logic required |

### `WHAT(6)` call-timing guidance

| Pattern | When to use |
|---|---|
| `WHAT(6) = 1.0` or `2.0` | Global logic or side effects independent of active detector |
| `WHAT(6) = 3.0` or `4.0` | Typical production weighting — fewer calls, detector-aware |

`WHAT(6) = 2.0` or `4.0` also invokes `ENDSCP` for deposited-energy position shifts.

## Required Fortran routine identity

The following structure may be present in the `comscw.f` user-routine file shipped with a licensed FLUKA installation:

```text
DOUBLE PRECISION FUNCTION COMSCW ( IJ, XA, YA, ZA, MREG, RULL, LLO, ICALL )
```

### Conceptual argument map

| Argument | Role |
|---|---|
| `IJ` | Particle type (generalized code; input only — do not modify) |
| `XA`, `YA`, `ZA` | Current particle position |
| `MREG` | Current geometry region |
| `RULL` | Amount to be deposited (**unweighted**) |
| `LLO` | Particle generation (input only — do not modify) |
| `ICALL` | Internal calling flag (not for general use) |

### Return value and `LSCZER`

| Output | Role |
|---|---|
| `COMSCW` (function value) | Multiplication factor for deposited amount |
| `LSCZER` (in `COMMON SCOHLP`) | If `.TRUE.` before `RETURN`, forces **zero scoring** regardless of `COMSCW` — more efficient than returning `0.0` |

Default shipped template: `COMSCW = 1.0`, `LSCZER = .FALSE.`

### `COMMON SCOHLP` — `ISCRNG` for COMSCW (manual §13.2.2)

| `ISCRNG` | Scored quantity type |
|---|---|
| `1` | Energy density binning |
| `2` | Star density binning |
| `3` | Residual nuclei scoring |

`JSCRNG` = binning/detector number within that class (printed in output as `R-Phi-Z binning n. N`, etc.).

**Important:** the same `JSCRNG` can occur for different estimator types — always use **`ISCRNG` + `JSCRNG`**. `ISCRNG` meanings **differ** between `COMSCW` and `FLUSCW` (manual §13.1.1).

The installed template comments may document additional `ISCRNG` codes (momentum transfer, activity density, pulse-height `DETECT`, etc.). Verify against the FLUKA version matching the installation.

### Useful optional includes

| Include | Use |
|---|---|
| `scohlp.inc` | `ISCRNG`, `JSCRNG`, `LSCZER` |
| `flkmat.inc` | `MEDIUM(MREG)`, `RHO(material)` for dose-from-density |
| `trackr.inc` | Particle age, energy, user flags |
| `souevt.inc` | Source-event particle bank when relevant |

## Expected user-provided `.f` file checks

- [ ] `DOUBLE PRECISION FUNCTION COMSCW` with template argument list.
- [ ] Standard includes (`dblprc.inc`, `dimpar.inc`, `iounit.inc`) preserved.
- [ ] `scohlp.inc` included when using `ISCRNG` / `LSCZER`.
- [ ] `flkmat.inc` included only when using material/density arrays.
- [ ] `COMSCW` assigned on every return path.
- [ ] `LSCZER` set explicitly each call.
- [ ] `IJ`, `LLO`, `ICALL` not modified.
- [ ] Dose/response units documented.
- [ ] Detector filtering uses `ISCRNG` and `JSCRNG`.

## Licensing-safe implementation policy

**AutoFLUKA does NOT ship** FLUKA-distributed `comscw.f` templates, the FLUKA manual, or other licensed installation materials. This guide contains original prose and pseudocode only.

Users should provide or copy `comscw.f` from their **licensed FLUKA installation**. See `../SKILL.md`.

## Upstream placement in the official FLUKA installation

The default template is typically under user-routine sources (e.g. `src/user/comscw.f`). The shipped version is a **dummy** returning `1.0`; user logic replaces the function body while preserving the interface.

## Mandatory setup before editing

1. Identify scored quantity: energy density, stars, or residual-related path.
2. Confirm **`COMSCW`** vs **`FLUSCW`** vs **`DETSCW`**.
3. Add **`USERWEIG`** with appropriate `WHAT(6)`.
4. Define response function and output units.
5. Plan baseline run with `COMSCW = 1`.
6. Check whether `TCQUENCH` Birks quenching already meets the physics need.

## Safe editing rules

- Preserve function signature and required includes.
- Use `LSCZER = .TRUE.` for hard rejections.
- Branch on `ISCRNG` **and** `JSCRNG`.
- For dose from energy density: use `MEDIUM(MREG)` and `RHO(...)` only with `flkmat.inc` included.
- `XA`, `YA`, `ZA`, `MREG`, `RULL` may be modified to affect scoring without changing transport (except `IJ`, `LLO`, `ICALL`) — document any such use.
- Do not double-apply Birks (`TCQUENCH`) and a duplicate quenching factor in `COMSCW` without intent.
- For name-based geometry, `GEOR2N` maps region numbers to names.

## Code implementation sections

### Default template behaviour

```text
LSCZER = .FALSE.
COMSCW = 1.0
RETURN
```

### Pattern A — energy density to dose (Gy) — manual concept

When `ISCRNG = 1` (energy density binning), convert deposited energy density to dose using local density \(\rho\) in g/cm³:

```text
INCLUDE flkmat.inc and scohlp.inc

IF ISCRNG == 1 THEN
    material_index = MEDIUM(MREG)
    COMSCW = ELCMKS * 1.D12 / RHO(material_index)
ELSE
    COMSCW = 1.0
ENDIF
LSCZER = .FALSE.
RETURN
```

`ELCMKS` is the electron charge constant from `dblprc.inc`. Verify the exact formula and constants against the installed manual and template. This pattern is especially useful when USRBIN voxels straddle material boundaries.

Express as pseudocode in user implementations; do not treat manual snippet as copy-paste without version check.

### Pattern B — particle or region filter

```text
IF IJ /= selected_particle .OR. MREG /= selected_region THEN
    LSCZER = .TRUE.
    COMSCW = 1.0
ELSE
    LSCZER = .FALSE.
    COMSCW = user_factor(IJ, RULL)
ENDIF
RETURN
```

### Pattern C — detector-specific weighting

```text
IF ISCRNG == 1 .AND. JSCRNG == target_binning_number THEN
    COMSCW = response(MREG, IJ, RULL)
ELSE
    COMSCW = 1.0
ENDIF
RETURN
```

### Pattern D — optical photon quantum efficiency on deposition

For optical photons (`IJ` corresponding to optical photon id in user's FLUKA version), weight `RULL` in photocathode region by efficiency curve — manual optical-photon chapter discusses `COMSCW` vs production-time efficiency.

### Editable-section map

| Section | Editable? | Use for | Main caution |
|---|---:|---|---|
| Function body / branching | Yes | Response, filters, dose conversion | All paths must set `COMSCW` |
| `LSCZER` assignment | Yes | Efficient zero scoring | Do not leave undefined |
| `INCLUDE flkmat` usage | Sometimes | Density-based dose | `MEDIUM(MREG)` indexing |
| `INCLUDE scohlp` usage | Yes | Detector context | `ISCRNG` ≠ FLUSCW meanings |
| Function signature | No | FLUKA interface | — |
| `IJ`, `LLO`, `ICALL` | No | Reserved inputs | — |

## Auxiliary input files

Optional:

- dose conversion tables;
- quenching or efficiency curves;
- region/material lookup tables.

Place beside run input; document units; fail clearly if missing.

## Output files and output patterns

`COMSCW` modifies standard scorer accumulation (`USRBIN` `.bnn` / listing files, `SCORE` output, etc.). It does not create a separate file.

Document weighted output meaning because printed headings may still describe unweighted energy density.

## Compile/link behavior

```text
comscw.f (+ other routines) -> compile -> link custom executable -> run with USERWEIG
```

Pass `comscw.f` via `subroutine_paths` in AutoFLUKA. Link with other user routines in one executable when needed.

## AutoFLUKA execution behavior

1. Detect `USERWEIG` with `WHAT(6) > 0.0`.
2. Confirm COMSCW-affected scorer cards exist.
3. Require explicit `subroutine_paths` for `comscw.f` when custom logic is needed.
4. Do not rely on `SOURCE`-only auto-detection.
5. Run `test-1` with `COMSCW = 1`; `test-2` with weighting enabled.
6. Spot-check one voxel/region against hand calculation.

## Validation checklist

Before execution:

- [ ] `USERWEIG` with `WHAT(6) > 0.0`.
- [ ] Scorer type matches `COMSCW` (not fluence-only with `FLUSCW`).
- [ ] `WHAT(6)` call timing chosen.
- [ ] `comscw.f` interface preserved.
- [ ] Units documented.
- [ ] Baseline unweighted test planned.
- [ ] No duplicate Birks/response with `TCQUENCH` unless intended.

After execution:

- [ ] Compile/link succeeded.
- [ ] Run completed without scoring errors.
- [ ] Weighted output differs from baseline as expected.
- [ ] `ISCRNG`/`JSCRNG` mapping verified from output listing.
- [ ] Dose values physically plausible.
- [ ] Production deferred until spot checks pass.

## Common errors and fixes

| Error signature / symptom | Typical cause | Suggested fix |
|---|---|---|
| No weighting effect | `WHAT(6) <= 0` or dummy `COMSCW` | Activate `USERWEIG`; link custom `comscw.f` |
| Fluence scorer unchanged/wrong | Used `COMSCW` for track-length fluence | Use `FLUSCW` (`WHAT(3)`) |
| Energy density not weighted | `WHAT(3)` set instead of `WHAT(6)` | Use `WHAT(6)` for `COMSCW` |
| Dose off by density factor | `flkmat.inc` missing or wrong `MEDIUM` | Include `flkmat`; verify `MREG` |
| All scores zero | `LSCZER` always true | Review branches |
| Wrong binning weighted | `JSCRNG` only, wrong `ISCRNG` | Filter both |
| Double quenching | `TCQUENCH` + `COMSCW` Birks-like factor | Use one mechanism |
| DETECT pulse-height wrong hook | Used `COMSCW` instead of `DETSCW` | `USERWEIG` `WHAT(4)` for `DETSCW` |
| Titles misleading | Extra weight not in headings | Add user notice in `TITLE`/comments |
| `ISCRNG` confusion with FLUSCW | Reused FLUSCW detector codes | Use COMSCW table in this guide |
| Activation decay factor missing | Expected in `COMSCW` | Not supported — use other activation workflow |

## Version drift

Drafted against the **2024 FLUKA Manual PDF edition** from https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals (`USERWEIG` Sec. 7.84; `COMSCW` Sec. 13.2.2; `SCOHLP` Sec. 13.1.1). Verify against the manual for the installed FLUKA version.

## Related examples

- `examples/COMSCW_USERWEIG_ACTIVATION.md` — `USERWEIG` + `USRBIN` energy scoring activation
- `examples/COMSCW_USRBIN_DOSE_GY_CASE.md` — energy-density to dose (Gy) weighting pattern

For fluence weighting, see `fluka-user-fluscw/FLUSCW_GUIDE.md`.

## Routine-interface summary without code redistribution

The `comscw.f` shipped with a licensed FLUKA installation may expose `DOUBLE PRECISION FUNCTION COMSCW` with position, region, deposition amount, and generation arguments, and may use `COMMON SCOHLP` for `ISCRNG`, `JSCRNG`, and `LSCZER`.

**AutoFLUKA does NOT ship** licensed FLUKA installation files or Fortran templates.

## Manual references

**Agent citation format:** `FLUKA Manual (2024 PDF edition), FLUKA Collaboration, Sec. …, p. …, manuals page https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals` — do not cite local parse filenames. See `../SKILL.md`.

- **Manuals page:** https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals
- **2024 PDF:** https://www.fluka.eu/Fluka/www/html/content/manuals/FM.pdf
- **This routine (2024 PDF edition):** `USERWEIG` Sec. 7.84, pp. 271–272; `COMSCW` Sec. 13.2.2, pp. 401–402; `SCOHLP` Sec. 13.1.1

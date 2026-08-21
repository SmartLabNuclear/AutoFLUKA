# FLUKA UBSSET user routine

## Purpose

`UBSSET` is a user-written **subroutine** that **overrides biasing parameters** read from the input deck. FLUKA calls it automatically during initialization — once per region for each relevant biasing option or suboption — after input reading completes and before transport calculations begin.

The default template is a dummy that passes input values through unchanged. User logic replaces or scales parameters such as region importances, multiplicity biasing factors, low-energy neutron biasing settings, weight-window levels, and electromagnetic cutoffs/biasing flags.

Typical motivation (manual §13.2.22): geometries with **many regions** where entering each `BIASING`, `LOW-BIAS`, `WW-FACTOR`, or `EMFCUT` value by hand is impractical. A region-numbering scheme plus an algorithm in `UBSSET` can generate consistent parameters.

`UBSSET` does **not** perform biasing during transport itself. It sets the tables FLUKA uses later. For **step-by-step** importance logic during tracking, see **`USIMBS`** (`BIASING` with `SDUM = USER`) — a different routine with different activation.

## When to use

Use `UBSSET` when:

1. **Many regions** need coordinated importance, weight-window, or LOW-BIAS parameters derived from a formula.
2. Input-card values should be **starting points** overridden programmatically at init time.
3. A **shielding ladder** or exponential attenuation compensation is easier to express as `HMPHAD(IR)` than dozens of `BIASING` lines.
4. You need to tie **multiple biasing cards** (`BIASING`, `LOW-BIAS`, `LOW-DOWN`, `WW-FACTOR`, `EMFCUT`, `EMF-BIAS`, `EXPTRANS`) to one region-index algorithm.

## When not to use

Do **not** use `UBSSET` when:

| Situation | Prefer |
|---|---|
| Few regions, static importances | `BIASING` cards only |
| Phase-space importance during every step | `USIMBS` (`BIASING` `SDUM = USER`) |
| No variance reduction needed | Analog run; no biasing |
| Scoring-time weighting only | `FLUSCW` / `COMSCW` |
| Unsure about biasing impact | Standard cards + `BIASING` `PRINT`; avoid custom override |

**Critical:** `USIMBS` and region importances set via `BIASING` `WHAT(3)` **cannot be used together** (manual §7.7 Note 7).

**Warning (manual §7.7):** A `BIASING` card issued only for `PRIMARY`/`NOPRIMARY` with blank `WHAT(2)`–`WHAT(5)` can **turn off all importance biasing** for all particles. Review every `BIASING` line deliberately.

Manual advice: *Do not bias unless you know what you are doing.*

## Activation card or activation condition

**There is no dedicated activation card for `UBSSET`.**

Per manual §13.2.22:

> Subroutine `UBSSET` does not require a special command to be activated: it is always called several times for each region (once for every biasing option or suboption) after the end of input reading and before starting the calculations.

Activation is implicit when:

1. A custom `ubsset.f` is **linked** into the executable, **and**
2. The input deck defines biasing-related options that populate the subroutine arguments (`BIASING`, `LOW-BIAS`, `WW-FACTOR`, etc.).

The shipped dummy template is linked by default in standard builds; replace it only when overrides are needed.

### Related input cards (parameters `UBSSET` can override)

| Input card | Overridable arguments (examples) |
|---|---|
| `BIASING` | `RRHADR`, `HMPHAD` / `HMPLOW` / `HMPEMF` |
| `LOW-BIAS` | `IGCUTO`, `IGNONA`, `PNONAN` |
| `LOW-DOWN` | `IGDWSC`, `FDOWSC` |
| `WW-FACTOR` (+ `WW-THRESH`, `WW-PROFILE`) | `WWLOW`, `WWHIG`, `WWMUL`, `JWSHPP` |
| `EXPTRANS` | `EXPTR` (manual notes not fully implemented) |
| `EMFCUT` | `ELECUT`, `GAMCUT` |
| `EMF-BIAS` | `LPEMF`, `ELPEMF`, `PLPEMF` |

## Input-card syntax and required deck checks

`UBSSET` does not replace the need for biasing cards. It **overrides** values those cards (or defaults) would otherwise set.

| Check | Required action |
|---|---|
| Biasing intent documented | Know which particle classes and regions are biased |
| Base `BIASING` cards present | Provide starting importances or RR factors if needed |
| `WHAT(2)` not accidentally zero | Blank `WHAT(2)` on a `BIASING` line can disable biasing |
| `USIMBS` not combined | Do not use `BIASING` `SDUM = USER` with `WHAT(3)` importances |
| Region numbering plan | Algorithm in `UBSSET` often keys on `IR` |
| Importance range | Manual: 0.0001 to 100000.0 for `BIASING` `WHAT(3)` |
| Weight windows if needed | Manual suggests WW cards when multiplicity reduction causes weight fluctuations |
| `BIASING` `PRINT` for tuning | Request RR/splitting counters on output |
| `ubsset.f` linked | Explicit path when custom logic required |
| Reference analog/low-bias test | Compare to less-biased run before production |

### `BIASING` quick reference (feeds `UBSSET`)

When `WHAT(1) ≥ 0`:

| `WHAT(1)` | Particle class |
|---|---|
| `0.0` | All particles |
| `1.0` | Hadrons, heavy ions, muons |
| `2.0` | Electrons, positrons, photons |
| `3.0` | Low-energy neutrons |

| Field | Role |
|---|---|
| `WHAT(2)` | Multiplicity RR/splitting factor → `RRHADR` |
| `WHAT(3)` | Region importance → `HMPHAD` / `HMPLOW` / `HMPEMF` |
| `WHAT(4)`–`WHAT(5)` | Region range |
| `SDUM` | `PRINT`, `USER` (→ `USIMBS`), `PRIMARY`, etc. |

## Required Fortran routine identity

The following structure may be present in the `ubsset.f` user-routine file shipped with a licensed FLUKA installation:

```text
SUBROUTINE UBSSET ( IR, RRHADR, IMPHAD, IMPLOW, IMPEMF,
     &              IGCUTO, IGNONA, PNONAN, IGDWSC, FDOWSC,
     &              JWSHPP, WWLOW, WWHIG, WWMUL, EXPTR,
     &              ELECUT, GAMCUT, LPEMF, ELPEMF, PLPEMF )
```

### Argument map (overridable outputs)

| Argument | Source card / meaning |
|---|---|
| `IR` | Region number (input) |
| `RRHADR` | `BIASING` `WHAT(2)` — multiplicity biasing |
| `IMPHAD` / `HMPHAD` | Hadron/muon importance (`BIASING` `WHAT(3)`, `WHAT(1)=0 or 1`) |
| `IMPLOW` / `HMPLOW` | Low-energy neutron importance (`WHAT(1)=0 or 3`) |
| `IMPEMF` / `HMPEMF` | e±/photon importance (`WHAT(1)=0 or 2`) |
| `IGCUTO` | `LOW-BIAS` `WHAT(1)` group cutoff |
| `IGNONA` | `LOW-BIAS` `WHAT(2)` non-analogue group |
| `PNONAN` | `LOW-BIAS` `WHAT(3)` survival probability |
| `IGDWSC` | `LOW-DOWN` `WHAT(1)` |
| `FDOWSC` | `LOW-DOWN` `WHAT(2)` |
| `JWSHPP` | `WW-FACTOR` profile index |
| `WWLOW`, `WWHIG`, `WWMUL` | Weight-window parameters |
| `EXPTR` | `EXPTRANS` parameter |
| `ELECUT`, `GAMCUT` | `EMFCUT` cutoffs |
| `LPEMF`, `ELPEMF`, `PLPEMF` | Leading-particle biasing (`EMF-BIAS`) |

### Integer vs double importance (`HMP*` vs `IMP*`)

Manual §13.2.22: subroutine arguments include integers `IMPHAD`, `IMPLOW`, `IMPEMF` equal to importance × 10000. The template provides **double precision** `HMPHAD`, `HMPLOW`, `HMPEMF` for user editing.

The shipped template performs conversion at entry and exit:

```text
! Entry: IMP* -> HMP*  (divide by 10000)
! User edits HMPHAD, HMPLOW, HMPEMF
! Exit: HMP* -> IMP*   (multiply by 10000, NINT)
```

**Do not modify** the conversion block at the beginning and end of the template unless you fully understand the consequences.

Allowed importance range via `HMP*`: approximately **0.0001 to 100000.0** (same as `BIASING` `WHAT(3)`).

### Call-frequency warning

`UBSSET` is called **many times per region** (once per biasing suboption). Therefore:

- Set parameters as **functions of `IR` only**, or absolute assignments independent of prior calls.
- **Never** use recursive self-scaling such as `GAMCUT = GAMCUT * 0.5` — each call would compound (manual example).

## Expected user-provided `.f` file checks

- [ ] `SUBROUTINE UBSSET` signature preserved.
- [ ] Conversion block for `HMP*` / `IMP*` left intact.
- [ ] Every call path sets intended outputs for the active `IR`.
- [ ] No recursive multiplication of argument values.
- [ ] Importances within allowed range.
- [ ] Logic keys on `IR` with clear region numbering documentation.
- [ ] `GEOR2N` used for name-based region logic if needed.

## Licensing-safe implementation policy

**AutoFLUKA does NOT ship** FLUKA-distributed `ubsset.f` templates, the FLUKA manual, or other licensed installation materials. This guide contains original prose and pseudocode only.

Users should provide or copy `ubsset.f` from their **licensed FLUKA installation**. See `../SKILL.md`.

## Upstream placement

Typically `src/user/ubsset.f` in the FLUKA distribution. Default is pass-through dummy.

## Mandatory setup before editing

1. Define variance-reduction goal (leakage, detector rate, deep shield penetration).
2. Choose particle classes to bias (`BIASING` `WHAT(1)`).
3. Plan region numbering (slab indices, radial shells, etc.).
4. Enter baseline biasing cards or accept defaults.
5. Decide `UBSSET` vs `USIMBS`.
6. Plan validation: analog or coarse-importance reference, `BIASING PRINT` counters.

## Safe editing rules

- Edit only the **user-written section** between template conversion blocks.
- Use **`HMPHAD`**, **`HMPLOW`**, **`HMPEMF`** for importances — not raw `IMP*` integers (unless you understand both).
- Assign **`RRHADR`**, weight-window, and LOW-BIAS integers explicitly per `IR` when overriding.
- Keep assignments **idempotent** across repeated calls for the same `IR`.
- Pair aggressive multiplicity biasing with **weight windows** (manual §7.7 Note 6).
- For analog-sensitive scores (`DETECT`, `EVENTBIN`), use **`GLOBAL`** analog mode where required (manual scoring notes).
- Document weight normalization implications for scored quantities.

## Code implementation sections

### Default template behaviour

Copies input-derived values through `HMP*` conversion without changing physics parameters.

### Pattern A — exponential shielding importance ladder (manual example)

Slab geometry: regions 3–20, one half-value layer per region, compensate hadron attenuation:

```text
! ONEONE = 1.D0, TWOTWO = 2.D0 from DBLPRC
IF IR >= 3 .AND. IR <= 20 THEN
    HMPHAD = ONEONE * TWOTWO**(IR - 3)
ENDIF
```

Importance ratios between adjacent regions drive Russian Roulette / splitting at boundaries. Manual: ratios matter more than absolute values.

### Pattern B — piecewise importance zones

```text
SELECT IR
  CASE 1:10
    HMPHAD = 1.0D0
  CASE 11:20
    HMPHAD = 10.0D0
  CASE 21:30
    HMPHAD = 100.0D0
  DEFAULT
    HMPHAD = unchanged from entry conversion
END SELECT
```

### Pattern C — override weight window per region band

```text
IF IR >= detector_region_start .AND. IR <= detector_region_end THEN
    WWLOW = 1.0D-3
    WWHIG = 1.0D-1
ENDIF
```

Coordinate with `WW-FACTOR` / `WW-THRESH` cards in the deck.

### Pattern D — scale LOW-BIAS for deep shield

```text
IF IR > shield_start THEN
    IGCUTO = appropriate_group_index
    PNONAN = 0.90D0
ENDIF
```

Verify against `LOW-NEUT` transport requirements.

### Editable-section map

| Section | Editable? | Use for | Caution |
|---|---:|---|---|
| User block between conversions | Yes | All overrides | Called many times per region |
| `HMPHAD/HMPLOW/HMPEMF` | Yes | Importance ladder | Range 1e-4 – 1e5 |
| `RRHADR` | Yes | Multiplicity biasing | Pair with weight windows |
| `WWLOW/WWHIG/WWMUL` | Yes | Weight control | Idempotent assignments |
| `IGCUTO/IGNONA/PNONAN` | Yes | Thermal neutron bias | Physics consistency |
| Entry/exit `IMP*` conversion | No | FLUKA interface | Do not remove |
| SUBROUTINE signature | No | Linking | — |

## Auxiliary input files

Optional: external tables mapping `IR` to importance factors read at first call with `SAVE`/`DATA` initialization. Document formats; fail clearly if missing.

## Output files and output patterns

`UBSSET` does not write files. Effects appear in:

- standard output region importance / weight-window tables printed at startup;
- `BIASING` `PRINT` RR/splitting counters (end of run);
- changed particle weights and statistical behaviour in scored results.

Insert a user-written notice in `TITLE` or comments when biasing overrides are active.

## Compile/link behavior

```text
ubsset.f -> compile -> link custom executable
```

Always linked in principle; custom **body** required for non-default overrides. Pass `ubsset.f` via `subroutine_paths` in AutoFLUKA when using customized version.

## AutoFLUKA execution behavior

1. Detect biasing-related cards in processed deck.
2. If custom `ubsset.f` provided, include in `subroutine_paths`.
3. Run low-NPS `test-n`; inspect printed importances and `BIASING PRINT` counters.
4. Compare key scores to less-biased reference.
5. Do not treat biased and analog runs as interchangeable without validation.

## Validation checklist

Before execution:

- [ ] Biasing goal and particle classes defined.
- [ ] Baseline `BIASING` / related cards reviewed for accidental disable.
- [ ] Not mixing `USIMBS` with `WHAT(3)` importances.
- [ ] `ubsset.f` preserves template conversion blocks.
- [ ] No recursive parameter scaling.
- [ ] Region numbering documented.
- [ ] Reference case planned.

After execution:

- [ ] Compile/link succeeded.
- [ ] Startup listing shows expected importances per region.
- [ ] `BIASING PRINT` counters look reasonable if requested.
- [ ] Scores stable vs coarse manual biasing test.
- [ ] Weight fluctuations understood; uncertainties not misleading.
- [ ] Production deferred until validation passes.

## Common errors and fixes

| Error signature / symptom | Typical cause | Suggested fix |
|---|---|---|
| No biasing effect | Dummy `UBSSET`; importances only in cards | Add user logic or use cards alone |
| All biasing off | `BIASING` with blank `WHAT(2)` | Fix card per manual warning |
| Importances explode/shrink each init | `GAMCUT = GAMCUT * factor` style | Use absolute assignment from `IR` only |
| Wrong particle class biased | Edited `HMPHAD` when `WHAT(1)=3` line active | Edit `HMPLOW` for thermal neutrons |
| `USIMBS` never called | `WHAT(3)=1` suppresses calls | By design when using region importances |
| Conflicts with `USIMBS` | Both `SDUM=USER` and `WHAT(3)` importances | Choose one mechanism |
| Cutoffs wrong after override | Recursive `ELECUT`/`GAMCUT` edit | Assign from tabulated values per `IR` |
| Biased scores untrustworthy | No weight-window with RR multiplicity | Add `WW-FACTOR` / tune `WWHIG`/`WWLOW` |
| Region algorithm wrong | Poor region numbering | Renumber geometry or use `GEOR2N` |
| Analog score invalid | Biasing on `DETECT`/`EVENTBIN` without care | Use `GLOBAL` analog; validate |

## Version drift

Drafted against the **2024 FLUKA Manual PDF edition** from https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals (`UBSSET` Sec. 13.2.22; `BIASING` Sec. 7.7). Verify against the manual for the installed FLUKA version.

## Related examples

- `examples/UBSSET_IMPORTANCE_LADDER_CASE.md` — slab shielding hadron importance ladder (manual p.422)
- `examples/UBSSET_BIASSING_DECK_SETUP.md` — `BIASING` deck + linking custom `ubsset.f`

For stepwise phase-space importance, see `USIMBS` (Sec. 13.2.24) — not covered by a separate guide in this pack yet.

## Routine-interface summary without code redistribution

`UBSSET` is called at initialization per region per biasing suboption to override table values derived from input cards.

**AutoFLUKA does NOT ship** licensed FLUKA installation files or Fortran templates.

## Manual references

**Agent citation format:** `FLUKA Manual (2024 PDF edition), FLUKA Collaboration, Sec. …, p. …, manuals page https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals` — do not cite local parse filenames. See `../SKILL.md`.

- **Manuals page:** https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals
- **2024 PDF:** https://www.fluka.eu/Fluka/www/html/content/manuals/FM.pdf
- **This routine (2024 PDF edition):** `UBSSET` Sec. 13.2.22, pp. 421–422; `BIASING` Sec. 7.7, pp. 86–89; `USIMBS` Sec. 13.2.24

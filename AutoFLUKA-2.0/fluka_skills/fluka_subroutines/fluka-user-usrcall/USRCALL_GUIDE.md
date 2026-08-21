# FLUKA USRINI, USROUT, and USRGLO user-call routines

## Purpose

The **USRCALL family** is a trio of lightweight user **subroutines** paired with matching **input cards**. Together they provide deck-driven hooks for:

| Routine | Card | When called |
|---|---|---|
| `USRGLO` | `USRGCALL` | Before **any** FLUKA initialization, when the card appears anywhere in input |
| `USRINI` | `USRICALL` | Each time the card is **read** during input processing |
| `USROUT` | `USROCALL` | Each time the card is **read** during input processing |

Each call passes six user-defined numeric parameters `WHAT(1)`–`WHAT(6)` and an eight-character string `SDUM`. The meaning of every field is **entirely user-defined** — FLUKA does not interpret them.

Typical uses (manual §§7.88–7.90, 13.2.27–13.2.30):

- **Early global setup** (`USRGLO`): open logical units, read cross-section or spectrum tables, set flags before geometry/material initialization.
- **Staged initialization** (`USRINI`): read auxiliary files at specific deck positions, normalize spectra for `SOURCE`, prepare counters or COMMON-block state.
- **Custom output** (`USROUT`): print summaries, dump internal tables, or write post-run diagnostics — usually placed **after** `START`.

Manual §7.66 Note 4: source-related initialization can live in `SOURCE`, `USRINI`, or `USRGLO`. Choose based on **when** data must be available relative to other input cards.

This family does **not** transport particles, score fluence, or override biasing. It is a **control and I/O hook layer**.

## When to use

Use the USRCALL family when:

1. **Initialization must run before FLUKA reads geometry** → `USRGCALL` → `USRGLO`.
2. **Initialization must run at a specific point in the input stream** (after certain cards, before others) → `USRICALL` → `USRINI`.
3. **Custom formatted output is needed after transport** → `USROCALL` → `USROUT`, typically after `START`.
4. **Logical units for estimators** must be opened before `USRTRACK` / `USRBIN` write (manual notes: units can be opened in `USRINI`, `USRGLO`, or `SOURCE`).
5. **`SOURCE` parameters are insufficient** and tabulated data or multi-file setup is cleaner in a dedicated init routine.

## When not to use

| Situation | Prefer |
|---|---|
| Per-event setup before each primary | `USREIN` (no card; always linked) |
| Per-event analysis after each event | `USREOU` (no card) |
| Primary particle sampling | `SOURCE` |
| Scoring-time weighting | `FLUSCW` / `COMSCW` |
| Step dumps / collision files | `MGDRAW` / `USERDUMP` |
| Biasing table overrides at init | `UBSSET` |
| Standard estimator post-processing | `ustsuw`, `usbrea`, etc. |

**Do not confuse** `USRINI` with `USREIN` or `USROUT` with `USREOU`. The latter pair are **event-level** routines called automatically every event without input cards.

## Activation cards and call order

### `USRGCALL` → `USRGLO` (Sec. 7.88)

```text
USRGCALL  WHAT(1)  WHAT(2)  WHAT(3)  WHAT(4)  WHAT(5)  WHAT(6)  SDUM
```

- Issued **once per card**; card may appear **anywhere** in the deck.
- `USRGLO` runs **before any other FLUKA initialization**.
- Default: no global user initialization.

Manual example (p. 287):

```text
USRGCALL    789.   321.    18.0   144.0   -27.0    3.14 SPECIAL
```

### `USRICALL` → `USRINI` (Sec. 7.89)

```text
USRICALL  WHAT(1)  WHAT(2)  WHAT(3)  WHAT(4)  WHAT(5)  WHAT(6)  SDUM
```

- Called **every time** the card is encountered while reading input.
- Multiple `USRICALL` lines → multiple `USRINI` calls (use `SDUM` or `WHAT` as stage flags).
- Default: no user initialization.

Manual example (p. 288):

```text
USRICALL    123.   456.     1.0    -2.0    18.0    18. FLAG12
```

### `USROCALL` → `USROUT` (Sec. 7.90)

```text
USROCALL  WHAT(1)  WHAT(2)  WHAT(3)  WHAT(4)  WHAT(5)  WHAT(6)  SDUM
```

- Called **every time** the card is read.
- Manual §9.8: **usually placed after `START`** for end-of-run output.
- Manual §7.1.7: input after `START` is **ignored** except for `USROCALL` and `STOP`.
- Default: no user-defined output.

Manual example (p. 289):

```text
USROCALL     17.0    17.0    -5.5     1.1   654.0   321. OK
```

### Recommended deck ordering

```text
TITLE ...
USRGCALL ...          ! earliest: USRGLO
... geometry, materials, scoring cards ...
USRICALL ...          ! USRINI when this line is read
SOURCE ...
START ...
USROCALL ...          ! USROUT after transport completes
STOP
```

`USRICALL` **before** `SOURCE` if `SOURCE` depends on tables loaded in `USRINI`. `USRGCALL` **before** cards that need pre-opened logical units.

## Input-card syntax and required deck checks

| Check | Action |
|---|---|
| `WHAT`/`SDUM` semantics documented | Define meaning in case notes — FLUKA does not assign them |
| `USRGCALL` placement | Anywhere; runs before all FLUKA init |
| `USRICALL` placement | After cards whose data you need; before dependent cards |
| `USROCALL` placement | After `START` for post-run output (manual §9.8) |
| Logical units ≥ 21 | Units 1–20 reserved by FLUKA (manual §9.8) |
| `usrini.f` / `usrout.f` / `usrglo.f` linked | All three may be customized independently |
| `LUSRIN` / `LUSRGL` lines preserved | Required template flags (see below) |
| Not mixing with event routines | `USREIN`/`USREOU` are separate |
| Low-NPS test | `START 1.0E3` before production |

### Passing parameters to routines

All three subroutines receive the same argument pattern from their cards:

| Argument | Type (manual) | Role |
|---|---|---|
| `WHAT(1)`–`WHAT(6)` | `DOUBLE PRECISION` | User numeric parameters |
| `SDUM` | `CHARACTER*8` | User string flag or label |

Use `SDUM` as a **stage selector** when one `.f` file handles multiple `USRICALL`/`USROCALL` lines.

## Required Fortran routine identities

The following structures may be present in user-routine `.f` files shipped with a licensed FLUKA installation:

```text
SUBROUTINE USRGLO ( WHAT, SDUM )
SUBROUTINE USRINI ( WHAT, SDUM )
SUBROUTINE USROUT ( WHAT, SDUM )
```

Each template typically includes:

```text
INCLUDE 'dblprc.inc'
INCLUDE 'dimpar.inc'
INCLUDE 'iounit.inc'
```

Manual suggests declaring:

```text
DOUBLE PRECISION WHAT(6)
CHARACTER SDUM*8
```

(Shorthand `DIMENSION WHAT(6)` appears in shipped templates.)

### Template flags — do not remove

| Routine | Protected line | Purpose |
|---|---|---|
| `USRINI` | `LUSRIN = .TRUE.` | Marks user initialization active |
| `USRGLO` | `LUSRGL = .TRUE.` | Marks user global initialization active |
| `USROUT` | (none in dummy) | — |

Edit only **below** the `*** Write from here on ***` marker in `USRINI` and `USRGLO`.

### Suggested INCLUDE files (manual)

Minimum: `DBLPRC`, `DIMPAR`, `IOUNIT`.

Depending on problem:

| INCLUDE | Useful for |
|---|---|
| `SOURCM` | Source parameters shared with `SOURCE` |
| `SUMCOU` | Normalisation / counter access |
| `SCOHLP` | Estimator flags (`ISCRNG`, `JSCRNG`) in `USROUT` |
| `BEAMCM` | Beam particle characteristics |
| `CASLIM` | Case limits |
| `FLKMAT` | Material data |
| `PAPROP` | Particle properties |
| `USRBDX`, `USRBIN`, `USRTRC`, `USRYLD` | Detector-specific output in `USROUT` |

See manual §13.1.1 (`SCOHLP`) for estimator identification.

## Licensing-safe implementation policy

**AutoFLUKA does NOT ship** FLUKA-distributed `usrini.f`, `usrout.f`, or `usrglo.f` templates, the FLUKA manual, or other licensed installation materials. This guide contains original prose and pseudocode only.

Users should provide or copy these files from their **licensed FLUKA installation**. See `../SKILL.md`.

## Upstream placement

Typically `src/user/usrini.f`, `usrout.f`, `usrglo.f`. Defaults are empty `RETURN` stubs.

## Mandatory setup before editing

1. Define what each `WHAT` and `SDUM` means for your case.
2. Map **call order**: global (`USRGLO`) → deck-positioned (`USRINI`) → transport → output (`USROUT`).
3. List logical units and files; confirm units ≥ 21.
4. Decide what must be in `SOURCE` vs `USRINI` vs `USRGLO`.
5. Plan validation: low primaries, check opened files and printed summaries.

## Safe editing rules

- Preserve `SUBROUTINE` names and argument lists.
- Keep `LUSRIN` / `LUSRGL` assignment lines in `USRINI` / `USRGLO`.
- Use `SAVE` and one-time init guards when reading large tables.
- Open files once in `USRGLO` or first `USRINI` call; avoid reopening every call without intent.
- In `USROUT`, write to `LUNOUT` (standard output) or user units ≥ 21.
- Use `SDUM` to branch multiple card lines in one subroutine file.
- Do not assume geometry or materials exist in `USRGLO` — it runs **first**.

## Code implementation sections

### Pattern A — `USRGLO`: early file and unit setup

```text
! WHAT(1) = logical unit number for spectrum file (e.g. 23)
! SDUM = 'SPECOPEN'

IF SDUM == 'SPECOPEN' THEN
    OPEN( INT(WHAT(1)), FILE='spectrum.dat', STATUS='OLD' )
ENDIF
```

Runs before geometry input is fully processed.

### Pattern B — `USRINI`: staged table load for `SOURCE`

```text
! USRICALL after MATERIAL cards, before SOURCE
! SDUM = 'LOADSP'

IF SDUM == 'LOADSP' THEN
    CALL READ_SPECTRUM_TABLE( WHAT(1), WHAT(2) )  ! user pseudocode
ENDIF
```

Share data with `SOURCE` via `COMMON` / `SOURCM` or module (user design).

### Pattern C — `USRINI`: open estimator output unit

Manual (USRTRACK notes): logical units for estimators may be opened in `USRINI`, `USRGLO`, or `SOURCE`.

```text
! WHAT(3) from a prior planning card → unit 24
OPEN( 24, FILE='track24.unf', FORM='UNFORMATTED', STATUS='UNKNOWN' )
```

Match `USRTRACK` `WHAT(3) = -24.0` in the deck.

### Pattern D — `USROUT`: post-run summary after `START`

```text
! USROCALL after START; SDUM = 'SUMMARY'

IF SDUM == 'SUMMARY' THEN
    WRITE(LUNOUT,*) ' User run summary'
    ! Include SCOHLP if printing per-detector info
ENDIF
```

Manual §13.2.30: actions **after all particle transport**.

### Pattern E — multiple `USRICALL` stages

```text
SELECT SDUM
  CASE ('STAGE1')
    ! read geometry-dependent table
  CASE ('STAGE2')
    ! normalize weights using WHAT(1) as target integral
  DEFAULT
    ! no-op
END SELECT
```

### Editable-section map

| Section | Editable? | Use for | Caution |
|---|---:|---|---|
| User block after template marker | Yes | All logic | `USRINI`/`USROUT` called per card read |
| `LUSRIN = .TRUE.` | No | FLUKA flag | Removing breaks init detection |
| `LUSRGL = .TRUE.` | No | FLUKA flag | Removing breaks global init detection |
| SUBROUTINE signature | No | Linking | — |
| Standard INCLUDE block | Extend only | `SCOHLP`, `SOURCM`, etc. | Do not redefine COMMON contents |

## Auxiliary input files

Common companions:

| File type | Typical reader | Notes |
|---|---|---|
| Spectrum `.dat` | `USRGLO` or `USRINI` | For custom `SOURCE` sampling |
| Cross-section tables | `USRGLO` | Before material init |
| Run manifest / config | `USRINI` | `WHAT` passes version or path index |
| Template summary `.txt` | `USROUT` | Written post-run |

Document formats in case notes; fail clearly if files are missing.

## Output files and output patterns

| Routine | Typical output |
|---|---|
| `USRGLO` | Opened units; rarely direct WRITE |
| `USRINI` | Opened units; optional log lines to `LUNOUT` |
| `USROUT` | Custom text to `LUNOUT` or units ≥ 21 |

Manual §9.8: unassigned `WRITE(unit,...)` creates `fort.xx` / `ftn.xx` — prefer explicit `OPEN`.

Effects also appear indirectly: units opened in init are consumed by `USRTRACK`, `USRBIN`, etc.

## Compile/link behavior

```text
usrini.f / usrout.f / usrglo.f → compile → link together with other user routines
```

Any subset may remain default stubs. Pass customized paths via `subroutine_paths` in AutoFLUKA.

## AutoFLUKA execution behavior

1. Parse deck for `USRGCALL`, `USRICALL`, `USROCALL` lines and document `WHAT`/`SDUM` meanings.
2. Include customized `.f` files in `subroutine_paths`.
3. Verify card order relative to `SOURCE`, scoring cards, and `START`.
4. Run low-NPS `test-n`; confirm init messages and post-`START` `USROUT` output.
5. If `USROUT` missing, check whether `USROCALL` was placed before `START` by mistake.

## Validation checklist

Before execution:

- [ ] `WHAT`/`SDUM` contract documented.
- [ ] `USRGCALL` before dependent init if early setup required.
- [ ] `USRICALL` after prerequisite cards.
- [ ] `USROCALL` after `START` for post-run actions.
- [ ] Logical units ≥ 21 for user files.
- [ ] `LUSRIN` / `LUSRGL` lines intact.
- [ ] Auxiliary files present in run directory.

After execution:

- [ ] Compile/link succeeded.
- [ ] `USRGLO` side effects visible (opened files, logged parameters).
- [ ] `USRINI` stages executed in deck order.
- [ ] Transport and scoring ran normally.
- [ ] `USROUT` produced expected summary or files.
- [ ] No stray `fort.xx` from unassigned units.

## Common errors and fixes

| Error signature / symptom | Typical cause | Suggested fix |
|---|---|---|
| `USROUT` never runs | `USROCALL` before `START` | Move after `START` (manual §9.8) |
| Input after `START` ignored | Cards placed after `START` | Only `USROCALL` and `STOP` allowed there |
| Spectrum not ready in `SOURCE` | `USRICALL` after `SOURCE` | Move `USRICALL` before `SOURCE` |
| Geometry unavailable in `USRGLO` | Too-early access | Defer geometry-dependent reads to `USRINI` |
| `fort.23` surprise file | `WRITE(23)` without `OPEN` | Explicit `OPEN`; unit ≥ 21 |
| Unit conflict | User unit ≤ 20 | Use units ≥ 21 only |
| Init flag ignored | Removed `LUSRIN`/`LUSRGL` | Restore template lines |
| Empty `USROUT` output | Dummy template still linked | Add user logic or verify custom link |
| Wrong init stage | Same `SDUM` on multiple lines | Use distinct `SDUM` flags per stage |
| Confused with `USREIN` | Expected per-event init | Use `USREIN` instead |

## Distinction: USRCALL vs USREIN / USREOU

| Feature | USRCALL family | `USREIN` / `USREOU` |
|---|---|---|
| Activation | Input cards | None (always linked) |
| Call timing | Input read / post-`START` | Every event start / end |
| Arguments | `WHAT(6)`, `SDUM` | No arguments |
| Typical use | Deck-driven setup/output | Event counters, per-event dumps |

## Version drift

Drafted against the **2024 FLUKA Manual PDF edition** from https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals (`USRGCALL`–`USROCALL` Secs. 7.88–7.90; `USRGLO`/`USRINI`/`USROUT` Secs. 13.2.27–13.2.30). Verify against the manual for the installed FLUKA version.

## Related examples

- `examples/USRCALL_SOURCE_SPECTRUM_INIT_CASE.md` — `USRGCALL` + `USRICALL` pipeline for custom `SOURCE` data
- `examples/USROCALL_POSTSTART_SUMMARY_CASE.md` — `USROCALL` after `START` for run summary output

## Routine-interface summary without code redistribution

`USRGCALL`, `USRICALL`, and `USROCALL` are input cards that invoke `USRGLO`, `USRINI`, and `USROUT` with user-defined parameters. `USRGLO` runs before all FLUKA initialization; `USRINI` and `USROUT` run when their cards are read; `USROUT` is normally used after transport via a post-`START` card.

**AutoFLUKA does NOT ship** licensed FLUKA installation files or Fortran templates.

## Manual references

**Agent citation format:** `FLUKA Manual (2024 PDF edition), FLUKA Collaboration, Sec. …, p. …, manuals page https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals` — do not cite local parse filenames. See `../SKILL.md`.

- **Manuals page:** https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals
- **2024 PDF:** https://www.fluka.eu/Fluka/www/html/content/manuals/FM.pdf
- **This routine family (2024 PDF edition):** `USRGCALL` Sec. 7.88; `USRICALL` Sec. 7.89; `USROCALL` Sec. 7.90; `USRGLO` Sec. 13.2.27; `USRINI` Sec. 13.2.28; `USROUT` Sec. 13.2.30; user output Sec. 9.8

# Case: Post-run summary via USROCALL after START

## Purpose

This worked example uses `USROCALL` **after** `START` to invoke `USROUT` for a custom run summary once all particle transport is complete. This matches manual §9.8: `USROUT` is designed for user output, usually requested at the end of the run after `START`.

Pseudocode only — not a bundled Fortran template.

## Problem statement

A shielding case with `USRTRACK` detectors writes unformatted fluence to unit 24. The user wants a **short formatted summary** on standard output listing run metadata and reminding which post-processing utility (`ustsuw`) to run — without parsing the full FLUKA output by hand.

## Deck excerpt

```text
TITLE
Shielding run with post-START USROUT summary
DEFAULTS         SHIELDIN         0.0

* Open track file unit in init (see USRCALL_SOURCE_SPECTRUM_INIT_CASE for USRINI OPEN pattern)
USRICALL      24.0   0.0   0.0   0.0   0.0   0.0   OPENTRK

USRTRACK      1.0   NEUTRON   -24.0   10.0   1000.0   50.   DetNeut
USRTRACK      0.0   0.001   0.0   0.0   0.0   0.0   &

PHYSICS        ...
START          5.0E5

* Only USROCALL and STOP are read after START (manual Sec. 7.1.7)
USROCALL       24.0   50.0   10.0   0.0   0.0   0.0   SUMMARY

STOP
```

### Parameter contract

| Field | Value | Meaning |
|---|---|---|
| `WHAT(1)` | `24.0` | Logical unit of `USRTRACK` unformatted file |
| `WHAT(2)` | `50.0` | Number of energy bins (echo for summary) |
| `WHAT(3)` | `10.0` | Detector region number |
| `SDUM` | `SUMMARY` | Select summary branch in `USROUT` |

## Fortran implementation (pseudocode)

### `USRINI` — open track unit (prerequisite)

```text
IF SDUM == 'OPENTRK' THEN
    OPEN( 24, FILE='detneut24.unf', FORM='UNFORMATTED', STATUS='UNKNOWN' )
ENDIF
```

### `USROUT` — post-transport summary

```text
INCLUDE 'scohlp.inc'   ! if referencing estimator metadata

IF SDUM == 'SUMMARY' THEN
    WRITE(LUNOUT,*) '=== User run summary (USROUT) ==='
    WRITE(LUNOUT,*) ' Neutron track file on unit', INT(WHAT(1))
    WRITE(LUNOUT,*) ' Region', INT(WHAT(3)), ', bins', INT(WHAT(2))
    WRITE(LUNOUT,*) ' Post-process with ustsuw on detneut24.unf'
ENDIF
```

Manual §13.2.30: actions **after all particle transport has taken place**.

For deeper per-detector logic, include `SCOHLP` and map `ISCRNG` / `JSCRNG` (manual §13.1.1) — optional extension beyond this case.

## Why after START?

Manual input rules (§7.1.7):

- Only the **first** `START` executes.
- Input after `START` is **ignored** except **`USROCALL`** and **`STOP`**.

Placing `USROCALL` before `START` would call `USROUT` **before** transport — wrong for fluence summaries.

## Output expectations

| Stream | Content |
|---|---|
| Standard FLUKA output | Normal estimator tables |
| `USROUT` via `LUNOUT` | Short user summary block |
| `detneut24.unf` | Binary `USRTRACK` data for `ustsuw` |

## Validation strategy

| Step | Action |
|---|---|
| 1 | Run `START 1.0E3` test |
| 2 | Confirm `detneut24.unf` exists and has non-zero size |
| 3 | Confirm summary block appears **after** transport section in output |
| 4 | Run `ustsuw` on unit-24 file as production step |

## Common pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| No summary in output | `USROCALL` before `START` | Move after `START` |
| Summary before primaries | Same | Same |
| Empty track file | `OPEN` missing in `USRINI` | Add `OPENTRK` init |
| `fort.24` instead of named file | Implicit `WRITE` | Explicit `OPEN` in `USRINI` |

## AutoFLUKA notes

```text
subroutine_paths: ["usrini.f", "usrout.f"]
```

`usrglo.f` may remain default stub for this case.

## Manual references

- User-generated output, Sec. 9.8, p. 370
- `USROCALL`, Sec. 7.90, p. 289
- `USROUT`, Sec. 13.2.30
- `START` input rules, Sec. 7.1.7, p. 73
- Parent guide: `../USRCALL_GUIDE.md`

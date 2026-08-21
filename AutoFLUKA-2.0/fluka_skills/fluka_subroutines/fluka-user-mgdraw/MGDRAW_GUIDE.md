# FLUKA MGDRAW user routine

## Purpose

`MGDRAW` is the FLUKA user-routine family for custom event, trajectory, boundary-crossing, source-particle, energy-deposition, and interaction/collision output. It is used when the standard FLUKA scoring cards do not provide the required event-level or particle-level record.

In practical AutoFLUKA usage, `MGDRAW` is most often used to create controlled custom output such as:

- phase-space records at a region boundary;
- leakage records from a shield or target;
- source-particle diagnostic records;
- event-end summaries;
- local energy-deposition records;
- interaction/collision secondary diagnostics;
- track or trajectory dumps for a small number of histories.

`MGDRAW` is not a single-purpose routine. It is a main routine plus multiple FLUKA-called entry points. Each entry point corresponds to a different transport or event hook.

## When to use

Use `MGDRAW` when the user explicitly needs information that is difficult or impossible to obtain with standard FLUKA scorers alone. Appropriate use cases include:

1. **Boundary-crossing or phase-space output**  
   Use the `BXDRAW` entry to record particles crossing from one region to another.

2. **Detector-entry or leakage records**  
   Use `BXDRAW` to record selected particles entering a detector region, exiting a target, or leaking from a shield.

3. **Event-level summaries**  
   Use `EEDRAW` to write one compact summary record at the end of each primary history.

4. **Local energy-deposition diagnostics**  
   Use `ENDRAW` when the user needs point-like or event-wise deposition information beyond normal scoring-card output.

5. **Source-particle diagnostics**  
   Use `SODRAW` to log source particles for verification. This is for observation/logging, not for defining the source.

6. **Interaction/collision secondary diagnostics**  
   Use `USDRAW` to inspect products of interactions or selected collision events.

7. **Trajectory-style diagnostic output**  
   Use the main `MGDRAW` body when track or trajectory records are needed for a deliberately small diagnostic run.

## When not to use

Do not use `MGDRAW` when a standard scoring card already provides the needed quantity more efficiently and with built-in statistical treatment.

Prefer standard scorers when possible, for example:

- `USRBDX` for boundary fluence/current spectra;
- `USRTRACK` for track-length fluence spectra in regions;
- `USRBIN` for mesh/region binned dose, energy deposition, fluence, or related quantities;
- `DETECT` for event-by-event energy deposition in detector regions;
- `SCORE` for simple region-wise quantities;
- `RESNUCLEi` for residual nuclei;
- other standard cards when they match the requested observable.

Do **not** use `MGDRAW` to define the primary source. Use the `SOURCE` user routine and the `SOURCE` input card for custom source generation.

Do **not** run unfiltered `MGDRAW` output in a production-scale simulation unless the user explicitly accepts very large output files and slow runtime.

## Activation card or activation condition

`MGDRAW` is activated through the FLUKA `USERDUMP` input card.

The important activation concept is:

```text
USERDUMP with WHAT(1) >= 100.0 activates MGDRAW-family calls for ordinary user-dump operation.
```

Additional `USERDUMP` fields determine which classes of `MGDRAW` entry points are called and which output unit/name are used.

A negative reset/disable form is also described in the manual, commonly represented conceptually as:

```text
USERDUMP with WHAT(1) <= -100.0 resets/disables the corresponding dump behavior.
```

Always verify the exact `WHAT(i)` meanings against the FLUKA manual version matching the installed FLUKA release.

## Input-card syntax and required deck checks

General `USERDUMP` card form:

```text
USERDUMP  WHAT(1)  WHAT(2)  WHAT(3)  WHAT(4)  WHAT(5)  WHAT(6)  SDUM
```

For AutoFLUKA guide usage, apply these checks before compiling/running an `MGDRAW` case:

| Check | Required action |
|---|---|
| `USERDUMP` exists | Confirm the input deck contains a `USERDUMP` card if `MGDRAW` is expected to be called. |
| `WHAT(1)` activates MGDRAW | For ordinary use, check that `WHAT(1) >= 100.0`. |
| Output unit is safe | If using `WHAT(2)` as an output logical unit, avoid low-numbered units that can conflict with FLUKA-reserved/predefined units. Prefer a documented user unit. |
| Entry selection is intentional | Check `WHAT(3)` and `WHAT(4)` against the manual and against the intended entry points. |
| `SDUM` is intentional | Use a clear dump/output identifier. Treat special `SDUM` values, such as quenching-related options, as advanced behavior requiring manual verification. |
| Output volume is bounded | Require region, particle, energy, direction, or event filters before any large run. |
| Low-NPS test exists | Run a low-primary `test-n` first before production. |

### Practical activation patterns

These patterns are intentionally conceptual. They should be adapted to the installed manual version and the specific problem.

#### Broad MGDRAW activation

```text
USERDUMP     100.0      <unit>       0.0       0.0       ...       ...   <dump-name>
```

Use only for small diagnostic tests unless output is heavily filtered inside the routine.

#### MGDRAW with user collision/interactions hook

```text
USERDUMP     100.0      <unit>       <mode>    1.0       ...       ...   <dump-name>
```

This pattern is used when the user wants `USDRAW`-style custom interaction/collision information. Verify the exact `WHAT(3)`/`WHAT(4)` behavior in the manual.

#### Boundary-crossing / phase-space focus

```text
USERDUMP     100.0      <unit>       <mode-calling-BXDRAW>       0.0       ...       ...   <dump-name>
```

Then implement the actual boundary/particle/direction filtering in `BXDRAW`.

## Required Fortran routine identity

A user-provided MGDRAW Fortran file must preserve the FLUKA-expected routine identity and entry-point interfaces.

The following routine/entry-point structure may be present in the MGDRAW user-routine `.f` file shipped with a licensed FLUKA installation:

```text
SUBROUTINE MGDRAW
ENTRY BXDRAW
ENTRY EEDRAW
ENTRY ENDRAW
ENTRY SODRAW
ENTRY USDRAW
```

Conceptual interface map:

| Entry point | Conceptual role |
|---|---|
| `MGDRAW(ICODE, MREG)` | Main track/trajectory drawing hook. |
| `BXDRAW(ICODE, MREG, NEWREG, XSCO, YSCO, ZSCO)` | Boundary-crossing hook. |
| `EEDRAW(ICODE)` | End-of-event/history hook. |
| `ENDRAW(ICODE, MREG, RULL, XSCO, YSCO, ZSCO)` | Local energy-deposition hook. |
| `SODRAW` | Source-particle drawing/logging hook. |
| `USDRAW(ICODE, MREG, XSCO, YSCO, ZSCO)` | User-dependent interaction/collision hook. |

Do not rename these entry points. Do not alter their argument lists unless the user is intentionally adapting to a documented FLUKA version difference and accepts the risk.

## Expected user-provided `.f` file checks

Before editing, compiling, or passing a file to AutoFLUKA execution, check that the user-provided MGDRAW file:

1. is a Fortran source file intended for FLUKA user-routine linking;
2. defines `SUBROUTINE MGDRAW`;
3. contains the expected `ENTRY` points required for the intended use;
4. preserves the expected entry names and argument lists;
5. contains required FLUKA include/common-block infrastructure for variables used by the routine;
6. does not contain FLAIR project metadata pasted into the Fortran body;
7. does not contain multiple conflicting definitions of `SUBROUTINE MGDRAW`;
8. opens/writes user output units safely;
9. does not perform uncontrolled output in every call without filtering;
10. is co-located with the run input or supplied explicitly to AutoFLUKA via `subroutine_paths`.

## Licensing-safe implementation policy

**AutoFLUKA does NOT ship** FLUKA-distributed MGDRAW templates, the FLUKA manual, or other licensed installation materials. This guide contains original prose and pseudocode only.

Users should provide or copy `mgdraw.f` (and related entry points) from their **licensed FLUKA installation**. Agents may inspect and edit user-provided `.f` files via tools.

Do not reproduce FLUKA template bodies in Markdown or chat. See `../SKILL.md`.

## Upstream placement in the official FLUKA installation

In a licensed FLUKA installation, MGDRAW user-routine template/reference files are commonly found under the FLUKA user-routine source area. The exact file names and locations can vary by installation and FLUKA release.

For AutoFLUKA skill content, keep only original Markdown guidance and examples. **AutoFLUKA does NOT ship** FLUKA-distributed Fortran templates.

Recommended separation for users and agents:

```text
fluka-user-mgdraw/MGDRAW_GUIDE.md       <- original AutoFLUKA guidance
fluka-user-mgdraw/examples/*.md         <- original AutoFLUKA examples
licensed FLUKA installation/user area   <- user obtains official MGDRAW .f templates, if needed
case/run folder                         <- user-provided edited .f file for a specific run
```

When an agent needs to edit an MGDRAW routine for a case, it should work on a user-provided `.f` file in the case/run workspace, or ask the user to provide/copy the appropriate routine template from their own licensed FLUKA installation.

## Mandatory setup before editing

Before editing an MGDRAW routine for a user case:

1. Identify the requested output objective.
2. Decide whether standard scoring cards can solve the problem without MGDRAW.
3. If MGDRAW is needed, identify the correct entry point.
4. Confirm the input deck contains the correct `USERDUMP` activation.
5. Confirm the Fortran file defines `SUBROUTINE MGDRAW` and the needed entry point.
6. Decide output format: text, binary/unformatted, CSV-like, or compact event summary.
7. Decide output unit and filename policy.
8. Add filters before writing output.
9. Run a low-primary `test-n` simulation first.
10. Inspect output size and meaning before production.

## Safe editing rules

### Edit only the intended entry bodies

For most tasks, the safe editing zones are inside the body of one or more entry points, before the corresponding `RETURN` statement.

| Entry / section | Editable? | Use for | Main caution |
|---|---:|---|---|
| Main `MGDRAW` body | Yes | Track/trajectory records | Can be called very often; output can become enormous. |
| `BXDRAW` | Yes | Boundary crossings, leakage, phase-space files | Filter by region pair, particle, energy, and direction. |
| `EEDRAW` | Yes | End-of-event summaries and accumulator flushes | Do not close/reopen files every event unless necessary. |
| `ENDRAW` | Yes | Local energy-deposition events | Very frequent; prefer accumulation and thresholds. |
| `SODRAW` | Yes | Source-particle diagnostics/output | Not a source generator; use `SOURCE` for generation. |
| `USDRAW` | Yes | Interaction/collision secondary records | Stack interpretation depends on the interaction context. |
| Signatures / `ENTRY` argument lists | No | Required FLUKA interface | Breaking these can prevent calls or linking. |
| Include/common-block infrastructure | Usually no | Provides FLUKA variables | Removing/redefining can break compilation or meaning. |
| FLUKA common-block variable meanings | No | Internal FLUKA data | Read them; do not redefine their semantics. |
| Default output unit handling | Only deliberately | Output control | Repeated open/close or wrong unit can corrupt output. |

### Preserve FLUKA interfaces

Do not change:

- `SUBROUTINE MGDRAW` name;
- `ENTRY` names;
- expected argument lists;
- precision/include infrastructure;
- FLUKA common-block declarations needed by variables used in the routine.

### Filter early

MGDRAW hooks may be called extremely often. Always filter as early as possible. Common filters include:

- old region (`MREG`);
- new region (`NEWREG`);
- particle type;
- energy threshold;
- particle direction;
- event number or history number;
- `ICODE` class;
- random down-sampling for diagnostics;
- maximum number of records.

### Avoid uncontrolled I/O

Avoid:

- writing every step/call in a production run;
- printing to screen/log on every call;
- opening output files repeatedly inside high-frequency hooks;
- closing output files in the wrong entry point;
- using logical units reserved by FLUKA or already used by the input deck;
- mixing formatted and unformatted records in the same file without a clear reader.

## Code implementation sections

### Main `MGDRAW` body — track or trajectory records

Use the main `MGDRAW` body when the user wants trajectory-like information from track segments. Typical variables accessed through FLUKA common blocks may include track coordinates, track length, particle identity, energy, weight, and related track-state values.

Typical implementation pattern:

```text
IF this track segment is relevant:
    WRITE compact selected track variables
END IF
```

Use this only for low-NPS diagnostics or heavily filtered production tasks.

### `BXDRAW` — boundary-crossing records

`BXDRAW` is usually the correct entry point for boundary-crossing and phase-space output.

Use it when the requested record is tied to a particle crossing from one region to another.

Typical implementation pattern:

```text
IF MREG is the upstream/source-side region AND NEWREG is the downstream/detector-side region:
    IF particle, energy, direction, and weight pass user filters:
        WRITE one compact boundary-crossing record
    END IF
END IF
```

Common boundary-crossing outputs:

- particle identifier;
- kinetic or total energy as appropriate;
- statistical weight;
- crossing coordinates `XSCO, YSCO, ZSCO`;
- direction cosines if available from common-block state;
- old/new region;
- event/history identifier when available.

### `EEDRAW` — end-of-event summaries

Use `EEDRAW` to write one compact row per primary history, especially if other entries accumulate event-level quantities.

Typical implementation pattern:

```text
AT event end:
    WRITE accumulated event summary
    RESET event accumulators
END
```

This is often safer than writing every `ENDRAW` or `BXDRAW` call directly.

### `ENDRAW` — local energy-deposition records

Use `ENDRAW` for local deposition events when standard scorers or `DETECT` do not provide the desired event-by-event detail.

Typical implementation pattern:

```text
IF MREG is a sensitive region:
    IF deposited amount RULL is above threshold:
        ACCUMULATE event deposition
    END IF
END IF
```

Prefer accumulation and event-end output for production-like workflows.

### `SODRAW` — source-particle diagnostics

Use `SODRAW` to record source particles for diagnostics. Do not use it to define or sample the primary source.

Typical implementation pattern:

```text
IF source logging is enabled and record count is below limit:
    WRITE selected source-particle diagnostic variables
END IF
```

If the user wants to generate particles from a spectrum, file, phase-space source, or custom spatial distribution, route to the `SOURCE` guide instead.

### `USDRAW` — interaction/collision secondary diagnostics

Use `USDRAW` when the user needs information about selected interactions, collision products, decay products, or secondaries.

Typical implementation pattern:

```text
IF interaction occurs in selected region and ICODE is selected:
    READ the appropriate secondary stack for this interaction class
    WRITE compact secondary summary
END IF
```

Do not assume every interaction class stores secondary information in the same stack. Validate the relevant stack/common-block usage for the specific physics process and FLUKA version.

## Auxiliary input files

MGDRAW does not normally require an auxiliary input file.

However, user implementations may introduce auxiliary files such as:

- particle-selection tables;
- region-pair filter lists;
- energy-bin or threshold tables;
- output-configuration files;
- phase-space reader/writer metadata.

If auxiliary files are used:

1. place them beside the run input or copy them into the active run folder;
2. document their names and formats;
3. open them using safe logical units;
4. fail clearly if the file is missing;
5. include them in any AutoFLUKA run manifest or execution notes.

## Output files and output patterns

MGDRAW output may be formatted text, unformatted/binary data, or a user-defined compact format.

Recommended patterns:

| Pattern | Preferred entry | Notes |
|---|---|---|
| Boundary phase-space file | `BXDRAW` | Write one row per selected crossing. |
| Leakage record | `BXDRAW` | Filter by source/target region and outgoing direction. |
| Event energy summary | `ENDRAW` + `EEDRAW` | Accumulate in `ENDRAW`, write at event end. |
| Source diagnostic log | `SODRAW` | Limit number of records. |
| Collision secondary summary | `USDRAW` | Filter by region and `ICODE`. |
| Track diagnostic dump | `MGDRAW` | Low-NPS only unless heavily filtered. |

Always document:

- output file name;
- logical unit;
- formatted vs unformatted mode;
- one-line description of each column/record;
- units of energy, length, and weight;
- event/history normalization;
- whether records are per primary, per crossing, per deposition, or per interaction.

## Compile/link behavior

MGDRAW must be compiled and linked into a FLUKA executable before the input deck can call it.

General concept:

```text
Fortran user routine(s) -> compile object(s) -> link custom FLUKA executable -> run input deck using that executable
```

AutoFLUKA execution guidance:

- Pass MGDRAW files explicitly through `subroutine_paths` when possible.
- If the deck has `USERDUMP` and needs MGDRAW, do not rely on SOURCE-only auto-detection behavior.
- If multiple user routines are needed, provide all relevant `.f` files together.
- Keep the selected MGDRAW file beside the `.inp` or pass an absolute path through the execution tool.
- Verify the compile/link log before interpreting runtime output.

Common command concepts in a FLUKA environment include compiling user routines and linking a custom executable using FLUKA-provided build utilities. Exact commands depend on the installed FLUKA distribution, operating system, and local wrapper scripts.

## AutoFLUKA execution behavior

For AutoFLUKA:

1. Identify that the input deck uses `USERDUMP`.
2. Determine whether a custom MGDRAW routine is required.
3. Prefer explicit `subroutine_paths` pointing to the user-provided MGDRAW file.
4. Copy the input and user routine into the active `test-n` folder when executing.
5. Use low primaries for preflight.
6. Confirm compile/link success.
7. Confirm the expected MGDRAW output artifact exists and is nonempty when output is expected.
8. Only proceed to production after a clean test run and output sanity check.

Important: the SOURCE auto-detection convenience is not a general substitute for explicit MGDRAW path specification. Other routines such as `MGDRAW` should be provided explicitly when possible.

## Validation checklist

Before execution:

- [ ] The user objective truly requires MGDRAW rather than standard scorers.
- [ ] The input deck contains `USERDUMP`.
- [ ] `WHAT(1)` is consistent with MGDRAW activation.
- [ ] `WHAT(2)` output unit is safe and documented if used.
- [ ] `WHAT(3)`/`WHAT(4)` are consistent with the intended entries.
- [ ] The Fortran file defines `SUBROUTINE MGDRAW`.
- [ ] Required entry points are present.
- [ ] Signatures and entry argument lists are preserved.
- [ ] The implementation writes only bounded, filtered output.
- [ ] Any output file format is documented.
- [ ] Auxiliary files are present if used.
- [ ] The case is run first as low-NPS `test-n`.

After execution:

- [ ] Compile/link completed successfully.
- [ ] FLUKA runtime completed without fatal errors.
- [ ] Expected output files exist.
- [ ] Output file sizes are plausible.
- [ ] First few records match expected columns/units.
- [ ] Region filters selected the intended boundary or region.
- [ ] Event/crossing/deposition counts are plausible for the primary count.
- [ ] No production run is started until the low-NPS output is understood.

## Common errors and fixes

| Error signature / symptom | Typical cause | Suggested fix |
|---|---|---|
| MGDRAW routine appears not to be called | Missing or inactive `USERDUMP` card | Add/check `USERDUMP`; for ordinary use verify `WHAT(1) >= 100.0`. |
| Compile/link failure involving `MGDRAW` | Routine name, entry name, argument list, or include infrastructure changed | Restore FLUKA-expected interfaces; edit only entry bodies. |
| No custom output file appears | Output unit not opened, wrong `USERDUMP` settings, or filters reject all events | Test with very low NPS and temporarily relaxed filters; verify output unit policy. |
| Huge output files | Unfiltered writing from high-frequency entries | Add region, particle, energy, direction, `ICODE`, or maximum-record filters. |
| Runtime slows dramatically | Excessive I/O in `MGDRAW`, `ENDRAW`, or `USDRAW` | Accumulate and write in `EEDRAW`; reduce output frequency. |
| Output columns are physically unclear | File format not documented | Add a guide/readme for output columns and units. |
| Boundary crossing records are wrong | Incorrect `MREG`/`NEWREG` region-pair filter | Verify region names/numbers in the processed input and geometry. |
| Source generation confused with `SODRAW` | User expects `SODRAW` to sample primaries | Route to `SOURCE` routine for generation; use `SODRAW` only for diagnostics. |
| Secondary stack values are misread | Assuming all `USDRAW` calls use the same stack conventions | Check `ICODE` and relevant FLUKA common-block documentation for that interaction class. |
| File-unit conflict | User reuses a FLUKA-reserved or already-open logical unit | Choose a documented user unit and keep it consistent with `USERDUMP` and code. |
| Output differs across FLUKA versions | Manual/version drift in routine internals or card interpretation | Verify against the manual matching the installed FLUKA release. |

## Version drift

Drafted against the **2024 FLUKA Manual PDF edition** from https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals (`USERDUMP` Sec. 7.83; `MGDRAW` Sec. 13.2.14). Verify against the manual for the installed FLUKA version.

## Related examples

Read these focused example files when implementing specific MGDRAW patterns:

- `examples/MGDRAW_USERDUMP_ACTIVATION.md`
- `examples/MGDRAW_BOUNDARY_CROSSING_OUTPUT.md`
- `examples/MGDRAW_FILE_IO_SAFETY.md`

## Routine-interface summary without code redistribution

The MGDRAW user-routine `.f` file shipped with a licensed FLUKA installation may expose the following routine/entry-point structure. Check the installed FLUKA version before relying on exact arguments or available common-block variables.

```text
SUBROUTINE MGDRAW
ENTRY BXDRAW
ENTRY EEDRAW
ENTRY ENDRAW
ENTRY SODRAW
ENTRY USDRAW
```

This guide describes the routine roles and safe editing zones in original prose and pseudocode only. **AutoFLUKA does NOT ship** licensed FLUKA installation files or Fortran templates.

## Manual references

**Agent citation format:** `FLUKA Manual (2024 PDF edition), FLUKA Collaboration, Sec. …, p. …, manuals page https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals` — do not cite local parse filenames. See `../SKILL.md`.

- **Manuals page:** https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals
- **2024 PDF:** https://www.fluka.eu/Fluka/www/html/content/manuals/FM.pdf
- **This routine (2024 PDF edition):** `USERDUMP`, Sec. 7.83, pp. 269–270; `MGDRAW`, Sec. 13.2.14, p. 409

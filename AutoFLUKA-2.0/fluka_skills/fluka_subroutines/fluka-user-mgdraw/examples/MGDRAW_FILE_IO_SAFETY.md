# MGDRAW file-I/O safety pattern

## Purpose

MGDRAW routines can be called very frequently. Poor file-I/O practice can make simulations extremely slow, produce enormous files, or cause file-unit conflicts. This example records safe file-output principles for MGDRAW implementations.

This is a Markdown implementation guide only. It does not reproduce FLUKA-distributed Fortran code.

## Core rule

Open files deliberately, write compact filtered records, and avoid opening/closing files inside high-frequency calls.

## Recommended output policy

Before coding, decide:

- output file name;
- logical unit;
- formatted text vs unformatted/binary output;
- one-line record schema;
- units for every column;
- maximum number of records for debugging;
- whether records are per event, per track, per crossing, per deposition, or per interaction.

## Logical-unit safety

- Use a documented user logical unit.
- Avoid units reserved or already used by FLUKA or the input deck.
- Keep the unit consistent with `USERDUMP` when applicable.
- Do not reuse the same unit for unrelated output files.

## High-frequency entries

The following entries can create very large output if unfiltered:

| Entry | Risk |
|---|---|
| Main `MGDRAW` | Track/trajectory calls can be frequent. |
| `BXDRAW` | Many boundary crossings may occur. |
| `ENDRAW` | Local deposition calls can be extremely frequent. |
| `USDRAW` | Interaction/collision events may produce many secondary records. |

## Safer strategy

Prefer:

```text
filter early -> accumulate if possible -> write compact summary -> validate with low NPS
```

For energy-deposition work, a safer design is often:

```text
ENDRAW accumulates selected deposition
EEDRAW writes one event-level summary
EEDRAW resets accumulators
```

## Avoid

Avoid:

- writing every call during production;
- printing to screen on every call;
- opening a file every time `BXDRAW`, `ENDRAW`, or `USDRAW` is called;
- closing files inside the wrong entry;
- using undocumented binary formats without a reader;
- writing records without units or column definitions;
- mixing formatted and unformatted records in the same file.

## Validation checklist

- [ ] Output file appears in the expected run folder.
- [ ] File size is plausible for the number of primaries.
- [ ] First few records match the documented schema.
- [ ] Values have plausible units and ranges.
- [ ] Filters select the expected regions/particles/events.
- [ ] A low-NPS run completes before any production run.

## Common errors

| Symptom | Typical cause | Fix |
|---|---|---|
| Simulation becomes very slow | Too much I/O | Add filters; accumulate and write in `EEDRAW`. |
| Huge files | Unbounded per-call writing | Add maximum-record and physics filters. |
| Empty file | File never opened or filters reject all records | Test with relaxed filters and low NPS. |
| Runtime I/O error | Unit conflict or invalid file mode | Choose a safe unit and use one consistent mode. |
| Output cannot be parsed | No documented schema | Add column names, units, and a reader description. |

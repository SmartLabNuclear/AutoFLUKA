# MGDRAW boundary-crossing output pattern

## Purpose

Use this example when the user wants to record particles crossing a selected FLUKA region boundary, for example to create a phase-space-like file or leakage record.

The relevant MGDRAW entry point is:

```text
BXDRAW
```

This is a conceptual implementation guide only. It does not reproduce FLUKA-distributed Fortran code.

## When to use

Use `BXDRAW` when the requested observable is tied to a particle crossing from one region to another, such as:

- particles exiting a target;
- particles entering a detector;
- particles leaking from shielding;
- particles crossing a scoring plane represented by a region boundary;
- particles recorded for later phase-space source reuse.

## Required activation

The input deck must contain a `USERDUMP` card that activates MGDRAW-family calls and selects a mode that calls `BXDRAW` for the intended transport classes.

Conceptual form:

```text
USERDUMP     100.0      <unit>       <mode-calling-BXDRAW>       0.0       ...       ...   <dump-name>
```

Verify the exact `WHAT(3)` mode in the FLUKA manual matching the installed version.

## Editable section

Edit the body of the `BXDRAW` entry only. Preserve the entry name and argument list.

Conceptual argument meaning:

| Argument | Meaning |
|---|---|
| `ICODE` | Call category or transport-origin code. |
| `MREG` | Region before crossing. |
| `NEWREG` | Region after crossing. |
| `XSCO, YSCO, ZSCO` | Crossing coordinates. |

## Recommended logic

Use this conceptual logic:

```text
IF old region is the desired source-side region:
    IF new region is the desired target-side region:
        IF particle/energy/direction/weight filters pass:
            WRITE one compact crossing record
        END IF
    END IF
END IF
```

## Recommended output columns

A boundary-crossing record often includes:

- event/history identifier if available;
- particle identifier;
- old region `MREG`;
- new region `NEWREG`;
- crossing position `XSCO, YSCO, ZSCO`;
- direction cosines if available from the relevant common-block state;
- energy;
- statistical weight;
- optional time or age if needed and available;
- `ICODE` for call-class diagnostics.

Document units explicitly.

## Required filters

At minimum, apply a region-pair filter. Additional useful filters are:

- particle type;
- energy threshold or energy window;
- direction sign or angular cone;
- maximum record count;
- selected histories only for debugging.

## Validation

For a first test:

1. Run with very low primaries.
2. Temporarily print/write a small number of records only.
3. Confirm that `MREG` and `NEWREG` match the intended boundary.
4. Confirm coordinates lie on the expected boundary.
5. Confirm particle energies and weights are plausible.
6. Confirm file size remains bounded.

## Common errors

| Symptom | Typical cause | Fix |
|---|---|---|
| No records written | Wrong region numbers, inactive `USERDUMP`, or wrong `WHAT(3)` | Verify region mapping and `USERDUMP` mode. |
| Records from many boundaries | Missing region-pair filter | Add `MREG` and `NEWREG` checks. |
| File too large | Writing every crossing | Add filters or maximum-record limit. |
| Wrong physical interpretation | Confusing current, fluence, and phase-space records | Document that BXDRAW output is user-defined records, not automatically a normalized scorer. |

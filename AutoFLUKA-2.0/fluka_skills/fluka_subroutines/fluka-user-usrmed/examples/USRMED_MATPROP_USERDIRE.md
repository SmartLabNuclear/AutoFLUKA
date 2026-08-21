# Case: MAT-PROP USERDIRE activation for USRMED

## Purpose

This worked example shows how to **activate** `USRMED` for selected materials using `MAT-PROP` with `SDUM = USERDIREctive`. It follows the manual pattern for calling `USRMED` when particles are transported in lead glass (Pb glass) and PMMA.

Use this case before implementing any `usrmed.f` logic. Activation alone does nothing until the user routine contains code (the shipped template is empty).

## Problem statement

An optical-photon or multi-material geometry includes **PMMA** and **LEADGLAS** compounds. The user wants `USRMED` called whenever transport occurs in these materials — for example to add custom absorption, refraction, or boundary handling in `usrmed.f`.

## Deck excerpt (name-based, from manual p.180)

After defining constituent elements, compounds, and materials:

```text
* Materials PMMA and LEADGLAS already defined via MATERIAL/COMPOUND cards

MAT-PROP     1.0     0.0     0.0    PMMA    LEADGLAS     3.0    USERDIRE
```

### Numeric-material variant (manual Example 1)

```text
MAT-PROP     1.0     0.0     0.0    15.0    18.0     3.0    USERDIRE
```

Materials 15 (PMMA) and 18 (LEADGLAS) in the manual numbering example.

## Field reading

| Field | Value | Meaning |
|---|---|---|
| `WHAT(1)` | `1.0` | Enable `USRMED` calls (`> 0`) |
| `WHAT(2)`, `WHAT(3)` | `0.0` | Unused for USERDIRE |
| `WHAT(4)` | `PMMA` or `15.0` | First material in range |
| `WHAT(5)` | `LEADGLAS` or `18.0` | Last material in range |
| `WHAT(6)` | `3.0` | Step between material indices (numeric mode) |
| `SDUM` | `USERDIRE` | USERDIREctive mode |

To disable later:

```text
MAT-PROP    -1.0     0.0     0.0     ...
```

`WHAT(1) < 0` resets USERDIRE to default (no `USRMED` calls).

## Optical-photon companion pattern (manual p.220)

When only specific optical materials need `USRMED`:

```text
OPT-PROP     3.E-5   5.E-5   6.E-5   16.0    22.0     0.0    WV-LIMIT

MAT-PROP     1.0     0.0     0.0    17.0    21.0     4.0    USERDIRE
```

`OPT-PROP` enables optical transport; `MAT-PROP` limits `USRMED` to materials 17 and 21.

## Fortran / compile

1. Copy `usrmed.f` from your **licensed FLUKA installation** (AutoFLUKA does NOT ship this file).
2. Implement logic for in-medium (`MREG = NEWREG`) and boundary (`MREG ≠ NEWREG`) cases.
3. Link custom executable; AutoFLUKA `subroutine_paths: ["usrmed.f"]`.

With empty template, enabling USERDIRE should not change results until body logic is added.

## Validation checklist

- [ ] `ASSIGNMAt` assigns PMMA/LEADGLAS to intended regions.
- [ ] `WHAT(4)`–`WHAT(5)` span only target materials.
- [ ] Not using `DPA-ENER` or blank SDUM MAT-PROP by mistake.
- [ ] `test-1`: USERDIRE off — baseline transport.
- [ ] `test-2`: USERDIRE on, empty `USRMED` — should match baseline.
- [ ] `test-3`: USERDIRE on, custom logic — verify intended effect.

## Common mistakes

| Mistake | Fix |
|---|---|
| `MAT-PROP` without `USERDIRE` SDUM | Sets gas pressure/RHOR, not USRMED |
| `WHAT(1) = 0` | Ignored; use `> 0` to activate |
| All materials flagged | Narrow `WHAT(4)`–`WHAT(5)` |
| Expect scoring changes only | USRMED affects transport, not USERWEIG scorers |

## Related

- In-medium absorption: `USRMED_OPTICAL_ABSORPTION_CASE.md`
- Parent guide: `../USRMED_GUIDE.md`

## Manual references

- `MAT-PROP` USERDIRE, pp. 198–200
- Optical example, p. 220
- `USRMED` Sec. 13.2.29

# Case: BIASING deck setup with custom UBSSET linked

## Purpose

This worked example walks through a complete **variance-reduction deck setup** where standard `BIASING` cards define the biasing framework and a custom `ubsset.f` overrides region importances at initialization. It is the operational checklist case for shielding/detector problems before writing ladder logic.

## Problem statement

A shielding problem biases **electromagnetic** particles (`e±`, photons) in detector regions 7–11 with one importance level, and **hadrons** in regions 3–8 with multiplicity reduction. The user will override hadron importances in `UBSSET` while keeping the card structure as documentation and fallback.

Adapted from manual `BIASING` examples (p. 89).

## Input deck excerpt

```text
* --- Electromagnetic importance in detector shells ---
BIASING     2.0     0.0    10.0     7.0    11.0     2.0

* --- Higher e/g importance in inner detector slice ---
BIASING     2.0     0.0    15.0     8.0     9.0     0.0

* --- Hadron multiplicity reduction + base importance (override in UBSSET) ---
BIASING     1.0     0.7     0.4     3.0     8.0     0.0    PRINT

* --- Apply importance biasing to primaries too ---
BIASING    -1.0     0.0     0.0     0.0     0.0     0.0    PRIMARY
```

### Reading the lines

| Line | `WHAT(1)` | Effect |
|---|---|---|
| 1 | `2.0` | e±/photons; importance `10` in regions 7–11 step 2 |
| 2 | `2.0` | e±/photons; importance `15` in regions 8–9 |
| 3 | `1.0` | Hadrons; RR factor `0.7`; importance `0.4` regions 3–8; print counters |
| 4 | `-1.0` | Modifier card: apply biasing to primaries (`PRIMARY`) |

**Warning:** Line 4 alone with blank `WHAT(2)` would disable biasing — here it is a deliberate `PRIMARY` flag after active cards.

Name-based equivalent (manual p. 89):

```text
BIASING     2.0     0.0    10.0   Seventh  Eleventh     2.0
BIASING     1.0     0.7     0.4    Third    Eighth       0.0    PRINT
```

## `UBSSET` role in this case

1. FLUKA reads `BIASING` cards → fills per-region tables.
2. At init, `UBSSET` called per region/suboption.
3. Custom logic replaces `HMPHAD` for regions 3–8 (see `UBSSET_IMPORTANCE_LADDER_CASE.md` for formula).
4. `HMPHAD` / `HMPEMF` left unchanged where not edited.

No activation card — linking custom `ubsset.f` is sufficient.

## Weight windows (optional, manual advice)

When `WHAT(2) < 1` (multiplicity reduction), manual suggests adding weight windows:

```text
WW-FACTOR    ...
WW-THRESH    ...
WW-PROFILE   ...
```

Tune `WWLOW` / `WWHIG` in `UBSSET` per region band if card entry is too coarse.

## Compile and AutoFLUKA

```text
subroutine_paths: ["ubsset.f"]
```

Steps:

1. Copy `ubsset.f` from your **licensed FLUKA installation** (AutoFLUKA does NOT ship this file).
2. Add override logic in user section only.
3. Compile/link with other user routines if present.
4. Run `test-n` with low primaries.

## Validation checklist

- [ ] Every `BIASING` line intentional — no stray blank `WHAT(2)` card.
- [ ] `SDUM = USER` **not** set (would invoke `USIMBS` instead of card importances).
- [ ] Startup output lists importances matching `UBSSET` overrides for regions 3–8.
- [ ] `PRINT` counters reviewed at end of run.
- [ ] Detector scores compared to coarse analog or unmodified `UBSSET` run.
- [ ] Document that results used variance reduction.

## When to escalate

| Need | Action |
|---|---|
| Importance depends on position/angle each step | Consider `USIMBS` instead |
| Only scoring weighting | `FLUSCW` / `COMSCW`, not `UBSSET` |
| >100 regions with simple ladder | Keep `UBSSET`; refine region numbering |

## Manual references

- `BIASING` examples, p. 89
- `UBSSET` activation note, p. 421
- Parent guide: `../UBSSET_GUIDE.md`

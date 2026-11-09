# Scoring Rules

Use scoring cards in patterns already validated by your local working examples.

## Energy ranges and mesh limits FLUKA accepts but cannot use
These cards pass FLUKA's input check, then crash the run or leave the scorer at exactly 0 (checked with the installed FLUKA). `fluka_inp_validator_tool` and the executor flag them.

| Card as written | What FLUKA does |
|---|---|
| `USRTRACK` or `USRBDX` continuation with WHAT(1) (Emax) below WHAT(2) (Emin) | Runs; the scorer stays exactly 0. The `.out` prints the energy grid high-to-low |
| Continuation with Emax equal to Emin | Crashes with a floating-point exception |
| Continuation with Emax blank or 0 and Emin at or above the beam energy | Crashes: a blank Emax means "the beam energy" |
| `USRBIN` axis min (2nd card) equal to its max (1st card) | Stops with a zero-width axis |
| `USRBIN` axis min above its max | Swaps them without an error |
| Blank or 0 bin count | Uses FLUKA's default (10 energy bins) |

Order to remember: a `USRTRACK` or `USRBDX` continuation card holds Emax in WHAT(1) and Emin in WHAT(2), high before low.

## Detector area and volume: FLUKA does not compute them
FLUKA never computes a surface area or a region volume for you. It uses the value you give, defaulting to 1.0:
- `USRBDX` WHAT(6) = detector **area** in cm², default 1.0. With the default, the result is fluence or current integrated over the boundary, not per cm² (FLUKA manual, USRBDX).
- `USRTRACK` WHAT(5) = detector **volume** in cm³, default 1.0. With the default, the result is track length integrated over the region, not fluence per cm² (FLUKA manual, USRTRACK).

So either set the true value in the card, or divide by it afterward and say so. Both are standard; setting it in the card is the usual choice. If a card with the area in WHAT(6) fails to parse, the cause is column alignment (see `fortran_columns.md`), not the approach.

Common values:

| Detector | Area (USRBDX) or volume (USRTRACK) |
|---|---|
| Sphere boundary of radius r | area 4πr² |
| Plane crossing a box face of sides a × b | area a·b |
| Cylinder side of radius r and length h | area 2πrh |
| Spherical shell r1 < r < r2 | volume 4/3·π(r2³ − r1³) |
| `RPP` box | volume Δx·Δy·Δz |
| `RCC` cylinder of radius r, height h | volume πr²h |

The `.out` file prints what FLUKA actually used (for example `detector area: 1.0000E+00 cm**2`); check it before reporting a per-cm² result. `fluka_inp_validator_tool` warns when the area or volume is left at 1.0.

## Pair-card discipline
- Keep the exact two-line structure for cards that require it in your templates:
  - `USRBIN` line 1 + `USRBIN` line 2
  - `USRBDX` line 1 + `USRBDX` line 2
  - `USRTRACK` additional line when energy/bin settings are split
- Do not reorder paired lines.
- Keep continuation lines numeric and card-valid; avoid non-numeric placeholders that are not defined in that card signature.

## Scorer selection
- `USRBIN`: mesh or region binning for dose/energy/fluence maps.
- `USRTRACK`: track-length fluence in a named region.
- `USRBDX`: boundary crossing fluence/current across two regions.
- `DETECT`: detector-style energy deposition setups (microdosimetric workflows).

## `USRBIN` mode consistency
- Do not mix mesh mode and region mode fields in one card.
- Mesh style (common for dose/energy maps):
  - line 1 uses numeric mesh half-widths/extents in `WHAT(4..6)` plus SDUM label
  - line 2 uses numeric lower bounds and bin counts
- Region style:
  - use a region name in `WHAT(4)` only with a region-compatible `USRBIN` type/pattern from a validated example.
- If uncertain, copy a known-good local pattern exactly and only change values.

## Identifier and output hygiene
- Keep detector/output unit identifiers unique across all scorers in one input.
- Project convention: use scoring unit numbers with absolute value >= 30 (for example `-30`, `-31`, ...).
- Keep scorer labels concise and parser-safe.
- Use consistent sign/type conventions copied from a known working template for the same scorer type.

## Geometry coupling checks
- `USRTRACK`: target region must exist and be assigned material.
- `USRBDX`: both boundary regions must exist and share a physical interface.
- `USRBIN`: mesh bounds and bin counts must cover intended volume and be physically meaningful.
- `DETECT`: region and cut settings must match detector size/physics intent.

## Physics coupling checks
- Ensure transport/production thresholds are compatible with scored quantities.
- For low-energy or microdosimetry cases, verify `EMFCUT`/related cards are aligned with scorer intent.
- Keep physics cards before `START` and after geometry/material sections.

## Minimal scoring QA before save
- Every scorer references existing region/material names.
- No duplicated scorer unit IDs.
- Required continuation/pair lines are present.
- Scoring labels are unique and readable.
- Numeric fields are parseable and separated (no merged tokens like `100.0TRKFLU`).
- For `USRBDX` continuation lines, prefer the minimal validated signature (`Emax Emin Nbins &`) unless a validated template requires extra fields.

# Scoring Rules

Use scoring cards in patterns already validated by your local working examples.

## Scorer selection
- `USRBIN`: mesh or region binning for dose/energy/fluence maps.
- `USRTRACK`: track-length fluence in a named region.
- `USRBDX`: boundary crossing fluence/current across two regions.
- `DETECT`: detector-style energy deposition setups (microdosimetric workflows).

## Pair-card discipline
- Keep the exact two-line structure for cards that require it in your templates:
  - `USRBIN` line 1 + `USRBIN` line 2
  - `USRBDX` line 1 + `USRBDX` line 2
  - `USRTRACK` additional line when energy/bin settings are split
- Do not reorder paired lines.
- Keep continuation lines numeric and card-valid; avoid non-numeric placeholders that are not defined in that card signature.

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

---
name: FLUKA Authoring
description: Create parser-safe FLUKA input decks from user requirements using local templates, working examples, and authoring rules.
---

# fluka-authoring

Create parser-safe FLUKA `.inp` files from user requirements, using local templates and working examples as the primary source of truth.

## Scope
- Translate user requirements into valid FLUKA `.inp` files.
- Reuse local templates and known-good examples before writing new cards from scratch.
- Enforce canonical card order, fixed-format discipline, and geometry/material/scoring consistency.

## Extensible content
- Add reusable authoring patterns to `rules/` only when they are broadly applicable.
- Add new reusable starting points under `../templates/`.
- Add full known-good cases under `../working_examples/`.

## When to use
- The user asks to generate, fix, or review FLUKA input files.
- The task mentions geometry/region/material/scoring errors in FLUKA or FLAIR.
- The task requires strict formatting preservation for column-sensitive FLUKA cards.

## Local references (priority order)
1. `../templates/**` for reusable skeletons and parameterized patterns.
2. `../working_examples/**` for known working card combinations and scoring setups.
3. `./rules/*.md` for authoring constraints and validation checks.

## Workflow
1. Parse the request into simulation requirements: particle, energy, source position, geometry, materials, physics toggles, scoring, and number of primaries.
2. Select the closest template/example and copy its card layout before changing values.
3. Apply edits section by section in canonical FLUKA order (see `rules/card_order_and_required_cards.md`).
4. Enforce column and continuation discipline (see `rules/fortran_columns.md`). Write each card with `fluka_card_formatter_tool` as the last step, with field meanings taken from the example in step 2, not from memory; check the scorer field names it prints.
5. Validate geometry and assignments (see `rules/geometry_region_material_rules.md`):
   - every region expression references defined bodies
   - every non-void region has `ASSIGNMA`
   - material and region names used in `ASSIGNMA` match exactly
6. Validate scoring cards (see `rules/scoring_rules.md`):
   - correct multi-line card pairs
   - unique detector/unit identifiers
   - scorer placement matches the intended region/interface/mesh
7. Final lint pass:
   - no tabs
   - target <=80 characters per line for newly generated files
   - `START` and `STOP` present and ordered correctly
8. Return:
   - final `.inp` content
   - short changelog of what was chosen from template vs customized
   - any assumptions that affect physics interpretation

## Source definition: cards vs. SOURCE routine (CRITICAL)
- A source with a fixed particle type, energy (or energy spectrum expressible as a simple card-level distribution), starting position, and direction needs **only `BEAM` + `BEAMPOS`** (plus `BEAMAXES` if the direction isn't the default) — **no `SOURCE` user routine is required**, including for a simple point source. This is standard, manual-documented FLUKA usage, not a simplification or workaround.
- Do not tell the user a point source "needs" a `SOURCE` routine, and do not default to generating one, unless the request genuinely requires something standard cards cannot express: a custom/external energy spectrum, a spatially extended or non-trivial spatial distribution, correlated energy-angle sampling, phase-space replay, or time-dependent source behavior. See `../fluka_subroutines/fluka-user-source/SOURCE_GUIDE.md`, "When to use" / "When not to use" for the exact boundary.
- An isotropic point source is card-level too: `BEAM` WHAT(3) above 2000π mrad (e.g. `10000.0`) with WHAT(4)=WHAT(5)=0 and the point in `BEAMPOS` makes FLUKA emit uniformly over 4π (FLUKA manual, BEAM Note 7). Use this, not a `SOURCE` routine, for any "isotropic"/"4π" point-source request. See `rules/card_order_and_required_cards.md`, "Isotropic point source", and `working_examples/photon_3mev_iso_pb_sphere/`.
- Nearly every file under `../working_examples/` is a plain point/pencil source using only `BEAM`/`BEAMPOS` (optionally `BEAMAXES`) with no `SOURCE` card at all — these are the default pattern to follow, not the exception.
- If uncertain whether a request needs a routine, ask what specifically about the source (spectrum shape, spatial extent, angular distribution) standard cards can't express — if the answer is "nothing, it's just a fixed point/pencil source," use cards.

## Authoring policy
- Prefer adapting a known working local `.inp` over writing cards from scratch.
- Keep names short and stable to avoid truncation confusion in FLUKA output.
- If user requirements conflict with parser safety, prioritize parser-safe syntax and state the tradeoff.

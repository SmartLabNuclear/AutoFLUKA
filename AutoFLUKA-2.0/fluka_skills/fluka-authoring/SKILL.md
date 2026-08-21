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
4. Enforce column and continuation discipline (see `rules/fortran_columns.md`).
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

## Authoring policy
- Prefer adapting a known working local `.inp` over writing cards from scratch.
- Keep names short and stable to avoid truncation confusion in FLUKA output.
- If user requirements conflict with parser safety, prioritize parser-safe syntax and state the tradeoff.

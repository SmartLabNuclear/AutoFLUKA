# photon_1mev_lead_slab

## Summary
Minimal verified photon transport example: a 1 MeV point-source pencil beam on a 2 cm lead slab in vacuum. Added because no photon examples existed under `working_examples/`, which contributed to the `BEAM` energy/momentum sign convention being re-derived from scratch each time (see `fluka-authoring/rules/card_order_and_required_cards.md`, "BEAM energy/momentum sign convention").

## Source
Authored fresh for this gap; verified via a real `rfluka -M 1` run (NPS=1000) with a clean energy balance (~68% deposited as EM showers, ~32% escaping — consistent with 2 cm Pb attenuation at 1 MeV) and no errors.

## What This Input Includes
- Beam: 1 MeV photons from upstream (`BEAMPOS z = -10.0 cm`), no `BEAMAXES` needed (default local +z axis matches the intended global direction).
- Geometry: outer `BLCKHOLE` boundary, `VACUUM` filler region (per the outer-boundary/filler-medium rule — not `AIR`, since this case doesn't call for it), and a 2 cm-thick lead slab (`RPP`).
- Materials/assignment: `BLCKHOLE`, `VACUUM`, `LEAD`.
- Scoring:
  - `USRBIN` dose mesh around the slab (unit 30)
  - `USRTRACK` photon track-length fluence in the slab (unit 31), slab volume 3200 cm³ in WHAT(5)
  - `USRBDX` boundary crossing from the vacuum filler into the slab (unit 32), slab surface 3520 cm² in WHAT(6) (set 2026-10-18; it was left at FLUKA's 1.0 default before)
  - `USRBIN` energy deposition mesh (unit 33)
- Run control: `RANDOMIZ`, `START`, `STOP`.

## Canonical Input
- `photon_1mev_lead_slab.inp`

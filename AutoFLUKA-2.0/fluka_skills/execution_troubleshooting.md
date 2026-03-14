# FLUKA Execution Troubleshooting

Use this guide for requests like "run FLUKA", "execute this file", "decrypt results", or "fix run errors".

## Scope
- Focus on execution/decryption reliability, not input-authoring from scratch.
- Prefer deterministic checks over repeated blind retries.

## Deterministic workflow
1. Identify runnable `.inp` files in the requested directory.
2. Exclude templates/placeholders and generated run trees (`fluka_<digits>`, nested `Results*` when scanning parent).
3. Execute once.
4. Verify evidence before claiming success:
   - at least one run artifact (`*.out` or `*_fort.*`)
   - no fatal errors in `AutoFLUKA_job*.log`
5. Decrypt `*_fort.xx` files and verify `_tab.lis` / `_sum.lis` are produced.
6. Only then report completed execution/decryption.

## Common failure signatures and fixes

### `STOP INVALID EMFCUT/PROD-CUT WHAT(3)`
- Signature:
  - `.log` contains `STOP INVALID EMFCUT/PROD-CUT WHAT(3)`
  - `.out` mentions `EMFCUT card, PROD-CUT, what(3), execution stopped`
- Typical cause:
  - `EMFCUT ... PROD-CUT` line has missing or zero `WHAT(3)`.
- Suggested Fix:
  - Set positive `WHAT(3)` (project convention: `1.0E-5`) on the PROD-CUT EMFCUT line.
  - Re-run.

### Re-run recursion / apparent infinite loop
- Signature:
  - repeated execution of nested `fluka_<digits>` and/or `Results*` directories.
- Cause:
  - recursive `.inp` scan includes generated run folders.
- Suggested Fix:
  - only execute primary user inputs; skip generated run trees.

### Fortran runtime parse crash (`cncprs.f` / bad real number)
- Signature:
  - `.log` shows `At line ... of file main/cncprs.f` and bad floating-point read.
- Typical cause:
  - malformed card fields after auto-edits (often EMFCUT/scoring field shifts).
- Suggested Fix:
  - revert to the closest known working input and apply minimal changes.
  - revalidate field positions, numeric tokens, and continuation lines.

### Fixed-format BEAM/scoring field shift causing FLUKA parse failure
- Signature:
  - Runtime .out/.err reported: 'does not contain a valid formatted fortran real number' on the BEAM card, with merged field text like '.0 7000.0'
- Typical cause:
  - Control-card numeric/string fields were not aligned to FLUKA fixed-width field boundaries, so adjacent WHAT/SDUM tokens merged during parsing
- Suggested Fix:
  - Rewrite the affected control cards using parser-safe fixed-width formatting (10-character card/WHAT/SDUM fields), preserving the original physics content and scorer definitions
- Context:
  - logged_on: `2026-03-09 05:16:43 UTC`
  - affected_file: `test_245MeV_neutrons_water_cube.inp`

### Unknown DEFAULTS option
- Signature:
  - Runtime .out reported: 'No/unknown default specified, run stopped' with DEFAULTS SDUM read as PRECISIO
- Typical cause:
  - The DEFAULTS SDUM was truncated and did not match a recognized FLUKA preset keyword
- Suggested Fix:
  - Replace the truncated DEFAULTS SDUM with the full recognized option name PRECISION
- Context:
  - logged_on: `2026-03-09 05:17:22 UTC`
  - affected_file: `test_245MeV_neutrons_water_cube.inp`

### Merged token on BEAM card
- Signature:
  - Validator reported: merged numeric/text token `0.0NEUTRON` on the BEAM line.
- Typical cause:
  - A missing separator between the last numeric WHAT field and the particle SDUM on a fixed-format FLUKA BEAM card.
- Suggested Fix:
  - Insert a space so the field reads `0.0 NEUTRON`, then revalidate the input.
- Context:
  - logged_on: `2026-03-09 05:38:38 UTC`
  - affected_file: `test_245MeV_neutrons_water_cube.inp`

### Invalid DEFAULTS keyword / non-run directive cleanup
- Signature:
  - Prior execution evidence indicated `**** No/unknown default specified, run stopped ****`; input also contained `DEFAULTS ... PRECISION` and a non-run line `!@scale=100`.
- Typical cause:
  - Using a non-valid DEFAULTS keyword (`PRECISION` instead of exact FLUKA keyword `PRECISIO`) and leaving a GUI/export directive in the run input.
- Suggested Fix:
  - Use the exact FLUKA DEFAULTS keyword `PRECISIO` and remove the non-run directive line before execution, then revalidate/run.
- Context:
  - logged_on: `2026-03-09 05:38:38 UTC`
  - affected_file: `test_245MeV_neutrons_water_cube.inp`

### BEAM card projectile/source definition runtime abort
- Signature:
  - Run output showed `Abort called from FLUKAM reason  UNKNOWN PROJECTILE OR "OLD" HEAVY ION OPTION (NO LONGER SUPPORTED)` immediately after the BEAM card.
- Typical cause:
  - The BEAM card used a non-working field combination for this neutron case (including the isotropic shorthand attempt), causing FLUKA to interpret the projectile/source definition incorrectly at runtime.
- Suggested Fix:
  - Simplify the BEAM card to a parser-safe monoenergetic neutron definition with only WHAT(1) and the SDUM particle name, e.g. `BEAM -2.45E-03 ... NEUTRON`, and keep the source position on BEAMPOS. Re-run after validation.
- Context:
  - logged_on: `2026-03-09 05:39:51 UTC`
  - affected_file: `test_245MeV_neutrons_water_cube.inp`

### Unknown DEFAULTS option from shifted SDUM / non-parser-safe control-card formatting
- Signature:
  - Run output contained: '**** No/unknown default specified, run stopped ****' immediately after DEFAULTS.
- Typical cause:
  - The input used visually readable spacing, but key FLUKA control/scoring cards were not aligned to parser-safe fixed-width fields, so the DEFAULTS SDUM (PRECISIO) was not read in the expected field.
- Suggested Fix:
  - Rewrite the affected control cards using parser-safe 10-character fields for keyword/WHAT/SDUM placement, preserve the exact DEFAULTS keyword PRECISIO, refresh the generated copies, and re-run before attempting decryption.
- Context:
  - logged_on: `2026-03-09 08:33:44 UTC`
  - affected_file: `test1_70MeV_protons_on_water.inp`

### DEFAULTS keyword mismatch for current FLUKA version
- Signature:
  - After parser-safe realignment, the run output still reported: '**** No/unknown default specified, run stopped ****' while echoing SDUM=PRECISIO on the DEFAULTS card.
- Typical cause:
  - The installed FLUKA version recognizes the precision preset as PRECISIOn (10-character form), not the older truncated PRECISIO keyword.
- Suggested Fix:
  - Replace DEFAULTS SDUM PRECISIO with PRECISIOn in the source input and regenerated copies, then rerun once before attempting decryption. Because the same fatal DEFAULTS signature repeated after one automatic fix attempt, stop automatic retries here and request user direction.
- Context:
  - logged_on: `2026-03-09 08:34:25 UTC`
  - affected_file: `test1_70MeV_protons_on_water.inp`

### USRBDX solid-angle fields explicitly zeroed instead of using defaults
- Signature:
  - FLAIR review flagged the USRBDX continuation line with WHAT(10), WHAT(11), and WHAT(12) set to 0.0 for solid-angle fields.
- Typical cause:
  - The USRBDX second line explicitly filled the optional solid-angle fields with zeros, even though this case should rely on FLUKA defaults for those entries.
- Suggested Fix:
  - Remove the three trailing 0.0 entries from the USRBDX continuation card so FLUKA uses its default solid-angle handling. The line was rewritten with only the energy binning terms populated, leaving the remaining optional fields blank.
- Context:
  - logged_on: `2026-03-09 17:36:31 UTC`
  - run_directory: `Results`
  - affected_file: `test1_70MeV_protons_on_water_01.inp`

### BEAM card projectile/source definition runtime abort
- Signature:
  - Run output showed: 'Abort called from FLUKAM reason  UNKNOWN PROJECTILE OR "OLD" HEAVY ION OPTION (NO LONGER SUPPORTED)' immediately after the BEAM card.
- Typical cause:
  - The BEAM control card used a non-working field layout with extra numeric entries, so the projectile/source definition was not being interpreted robustly at runtime even though parser validation passed.
- Suggested Fix:
  - Rewrite the BEAM card in strict 10-character FLUKA fixed-width format, keeping only WHAT(1) = -7.000E-02 and SDUM = PROTON, with the remaining WHAT fields left blank. The copied inputs were updated consistently before rerunning.
- Context:
  - logged_on: `2026-03-09 17:37:38 UTC`
  - run_directory: `Results`
  - affected_file: `test1_70MeV_protons_on_water_01.inp`

### BEAM card projectile/source definition runtime abort
- Signature:
  - Run output showed: 'Abort called from FLUKAM reason UNKNOWN PROJECTILE OR "OLD" HEAVY ION OPTION (NO LONGER SUPPORTED)' immediately after the BEAM card.
- Typical cause:
  - The copied input used a runtime-incompatible or parser-fragile pion/source card combination and other control cards were not written in the most parser-safe form for this FLUKA runtime.
- Suggested Fix:
  - Rewrite the copied run input in parser-safe fixed-format style, keep the beam/scoring particle consistently as PION+, simplify material assignment using FLUKA built-in materials, clean prior run artifacts, then revalidate and rerun.
- Context:
  - logged_on: `2026-03-12 13:39:40 UTC`
  - affected_file: `pion_fluence_current_beryllium_3slabs.inp`

### Geometry/source boundary startup causing GEOFAR abort
- Signature:
  - Run output ended with: 'Abort called from GEOFAR reason TOO MANY ERRORS IN GEOMETRY: STOP' while the beam started on a region boundary and the echoed beam direction in the geometry frame was not aligned with the intended target axis.
- Typical cause:
  - The source was initialized on or too near a region boundary and the BEAMAXES setting rotated the default beam direction away from the intended +z transport axis, leading to repeated geometry-tracking failures.
- Suggested Fix:
  - Place the source safely inside the upstream air region (e.g., z = -9 cm here) and remove the problematic BEAMAXES override so the beam follows the default +z direction through the three slabs; then revalidate and rerun.
- Context:
  - logged_on: `2026-03-12 13:40:24 UTC`
  - affected_file: `pion_fluence_current_beryllium_3slabs.inp`

## Logged Fixes
- Append new runtime fixes here using this exact schema:
  - `### <Error type heading>`
  - `- Signature:`
  - `- Typical cause:`
  - `- Suggested Fix:`

## Retry policy
- Try at most one targeted fix per unique fatal signature.
- If the same signature repeats, stop auto-retries and report:
  - exact failing signature
  - file and line candidates
  - next manual action requested from user

## Documentation policy
- After applying an auto-fix, call `fluka_fix_note_logger_tool` and append a structured record to a sidecar markdown next to the affected `.inp`.
- Keep this shared file curated and stable for reusable patterns only.
- Promote sidecar notes into this file manually after review.

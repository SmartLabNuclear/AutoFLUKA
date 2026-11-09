# FLUKA Error Resolution Knowledge Base

Unified troubleshooting records for AutoFLUKA. Each entry covers one FLUKA parser,
runtime, or workflow failure pattern. The `Detection hint` field holds observable clues
that can be matched against evidence before reading the full signature list.

---

### Geometry/beam axis convention mismatch

- Detection hint:
  - Geometry is visually inconsistent in FLAIR.
  - Beam appears to miss the intended target stack or enters unexpected regions.
- Signature:
  - Geometry is visually inconsistent in FLAIR.
  - Beam appears to miss the intended target stack or enters unexpected regions.
  - Geometry-tracking aborts after repeated boundary issues.
- Typical cause:
  - The input assumed a different axis orientation than the FLUKA/FLAIR inspection convention.
  - A `BEAMAXES` override rotated the beam away from the intended +z direction.
- Suggested Fix:
  - Lock one convention and document it at the top of the input.
  - Project convention: x up, z horizontal left-to-right, beam along +z unless the user explicitly requests otherwise.
  - Remove accidental `BEAMAXES` overrides and verify the beam direction before execution.
- Confidence: 0.85
- Logged: 2026-03-12
- Source:
  - ADS-derived curated regression case
  - Curated AutoFLUKA troubleshooting record

### Geometry tracking abort due to source on or near region boundary

- Detection hint:
  - Too many geometry errors.
  - `Abort called from GEOFAR reason TOO MANY ERRORS IN GEOMETRY: STOP`
- Signature:
  - Too many geometry errors.
  - `Abort called from GEOFAR reason TOO MANY ERRORS IN GEOMETRY: STOP`
  - Source starts exactly on a plane, window, or region boundary.
- Typical cause:
  - `BEAMPOS` starts the primary particle exactly on or numerically too close to a region boundary.
  - The first step is ambiguous because the source point is not inside one well-defined transport region.
- Suggested Fix:
  - Move `BEAMPOS` slightly inside a single upstream region, for example a few mm to cm inside AIR or VACUUM.
  - Remove accidental `BEAMAXES` overrides if they rotate the beam away from the intended target axis.
- Confidence: 0.90
- Logged: 2026-03-12
- Source:
  - Curated AutoFLUKA troubleshooting record

### Invalid EMFCUT PROD-CUT WHAT(3)

- Detection hint:
  - `STOP INVALID EMFCUT/PROD-CUT WHAT(3)`
  - `EMFCUT card, PROD-CUT, what(3), execution stopped`
- Signature:
  - `STOP INVALID EMFCUT/PROD-CUT WHAT(3)`
  - `EMFCUT card, PROD-CUT, what(3), execution stopped`
- Typical cause:
  - `EMFCUT ... PROD-CUT` line has missing or zero `WHAT(3)`.
- Suggested Fix:
  - Set positive `WHAT(3)` on the PROD-CUT EMFCUT line and rerun the next low-statistics `test-n` attempt.
  - Example project convention (every value ends at column 20/30/40; PROD-CUT starts at column 71):
    ```text
    *...+....1....+....2....+....3....+....4....+....5....+....6....+....7....+....8
    EMFCUT      -1.0E-05   1.0E-05   1.0E-05                              PROD-CUT
    ```
- Confidence: 0.90
- Logged: 2026-03-09
- Source:
  - Curated AutoFLUKA troubleshooting record

### Re-run recursion or apparent infinite loop

- Detection hint:
  - Repeated execution of nested `fluka_<digits>` folders.
  - Repeated execution of nested `Results*` directories.
- Signature:
  - Repeated execution of nested `fluka_<digits>` folders.
  - Repeated execution of nested `Results*` directories.
- Typical cause:
  - Recursive `.inp` scanning includes generated run folders instead of only primary user inputs.
- Suggested Fix:
  - Execute only primary user inputs unless the user explicitly targets a generated run folder.
  - Skip generated run trees such as `fluka_<digits>` and nested `Results*` folders during parent-directory scans.
- Confidence: 0.95
- Logged: 2026-03-09
- Source:
  - Curated AutoFLUKA troubleshooting record

### Fortran runtime parse crash from bad floating-point read

- Detection hint:
  - `Fortran runtime error: Bad value during floating point read`
  - `At line ... of file main/cncprs.f`
- Signature:
  - `Fortran runtime error: Bad value during floating point read`
  - `At line ... of file main/cncprs.f`
  - `At line ... of file main/echinp.f`
- Typical cause:
  - Malformed fixed-format card fields after auto-edits.
  - Numeric WHAT fields contain shifted text, guessed LOW-MAT values, or merged tokens.
- Suggested Fix:
  - Revert to the closest known working input and apply minimal card changes.
  - Revalidate fixed-width field positions, numeric tokens, continuation lines, and SDUM placement.
  - Do not guess `LOW-MAT` numeric fields; use only verified library-compatible patterns.
- Confidence: 0.88
- Logged: 2026-03-09
- Source:
  - Curated AutoFLUKA troubleshooting record
  - ADS-derived curated regression case

### Fixed-column formatting error on scoring cards

- Detection hint:
  - WHAT field does not contain a valid formatted Fortran real number.
  - Alphanumeric region, material, or label token appears where FLUKA expects a numeric WHAT field.
- Signature:
  - WHAT field does not contain a valid formatted Fortran real number.
  - Alphanumeric region, material, or label token appears where FLUKA expects a numeric WHAT field.
  - `Invalid what(s)` appears for `USRTRACK`, `USRBDX`, `USRBIN`, or `RESNUCLEi`.
- Typical cause:
  - Fixed-column field spillover because labels, region names, or material names shifted into numeric fields.
  - Mixed free-format and fixed-format repair passes left cards in inconsistent layout.
- Suggested Fix:
  - Rewrite the affected scorer lines with `fluka_card_formatter_tool`, which right-aligns every value to the last column of its 10-column field.
  - Keep WHAT fields numeric and labels in SDUM or in name-enabled fields from a validated template.
  - Use the mental model `A8, 2X, 6E10.*, A8` for classic fixed-format cards: every value ends at column 20, 30, …, 70.
  - Example alignment reminder:
    ```text
    *...+....1....+....2....+....3....+....4....+....5....+....6....+....7....
    ```
- Confidence: 0.92
- Logged: 2026-03-09
- Source:
  - Curated AutoFLUKA troubleshooting record
  - ADS-derived curated regression case

### START card numeric field overflow or misread NPS

- Detection hint:
  - `.out` shows `Total number of primaries run:` smaller than the NPS written on `START` (e.g. 10000 instead of 100000), with no error.
  - The executor reports "START asks for N primaries but FLUKA read WHAT(1) = M".
  - FLUKA fails to parse the `START` line after an edit.
- Signature:
  - Run echo shows an unexpected number of primaries.
  - `Total number of primaries run:` differs from the NPS on the `START` card.
  - A long numeric literal spills into the next fixed-format field.
- Typical cause:
  - The NPS does not end at column 20, so part of it falls into WHAT(2). FLUKA reads only columns 11-20 for WHAT(1) and accepts the fragment without complaint: `START          100000.0` (columns 16-23) ran **10,000** primaries per cycle in a real run, and `START          500000.0` ran 50,000.
  - A value starting at column 10 (inside the keyword field) leaves WHAT(1) as 0, so FLUKA silently runs its default (5,000).
  - A `test-n` low-NPS value was accidentally propagated into production copies.
- Suggested Fix:
  - Rewrite the card so the NPS ends exactly at column 20, preferably with `fluka_card_formatter_tool`. Decimal or exponent both work once right-aligned.
  - After any production run, compare `Total number of primaries run:` in each `.out` with the requested NPS before reporting statistics.
  - Before seeded production runs, restore the intended production NPS after a `test-n` attempt succeeds.
  - Example:
    ```text
    *...+....1....+....2....+....3....+....4....+....5....+....6....+....7....+....8
    START      1000000.0
    START       100000.0
    START        1.0E+05
    ```
- Confidence: 0.84
- Logged: 2026-03-09
- Source:
  - Curated AutoFLUKA troubleshooting record

### Fixed-format BEAM field shift causing parse failure

- Detection hint:
  - BEAM card does not contain a valid formatted Fortran real number.
  - Merged field text appears, such as `.0 7000.0`.
- Signature:
  - BEAM card does not contain a valid formatted Fortran real number.
  - Merged field text appears, such as `.0 7000.0`.
  - Validator reports merged numeric/text token such as `0.0NEUTRON`.
- Typical cause:
  - Numeric and SDUM fields on the `BEAM` card are not aligned to fixed-width field boundaries.
  - A missing separator lets the particle name merge into a numeric WHAT field.
- Suggested Fix:
  - Rewrite the `BEAM` card with `fluka_card_formatter_tool` (every value right-aligned to column 20, 30, …, 70).
  - Keep the projectile name in SDUM, starting exactly at column 71. When WHAT(6) is used it ends at column 70 and touches SDUM (`1.0PHOTON`); that is correct. A particle name starting at column 72 or later aborts with UNKNOWN PROJECTILE.
  - Example minimal monoenergetic proton style:
    ```text
    BEAM      -7.000E-02                                                  PROTON
    ```
- Confidence: 0.90
- Logged: 2026-03-09
- Source:
  - Curated AutoFLUKA troubleshooting record
  - ADS-derived curated regression case

### Unknown DEFAULTS option or shifted DEFAULTS SDUM

- Detection hint:
  - `No/unknown default specified, run stopped`
  - `STOP  NO/UNKNOWN DEFAULT`
- Signature:
  - `No/unknown default specified, run stopped`
  - `STOP  NO/UNKNOWN DEFAULT`
  - `**** No/unknown default specified, run stopped ****`
- Typical cause:
  - `DEFAULTS` SDUM is invalid, truncated, shifted into the wrong field, or not recognized by the installed FLUKA version.
  - Visually readable spacing was used, but the card was not parser-safe for fixed-format interpretation.
  - Two concrete mechanisms confirmed in practice: (a) the SDUM keyword itself exceeded FLUKA's 8-character limit, e.g. `PRECISIOn` (9 characters, invalid) instead of `PRECISIO` (8 characters); (b) the generated card used a 10-character card-name field instead of the parser-expected 8-character card-name field, shifting the SDUM one column late even when the keyword text itself was spelled correctly.
- Suggested Fix:
  - Check the exact `DEFAULTS` keyword accepted by the installed FLUKA version.
  - Rewrite the `DEFAULTS` card in parser-safe fixed-width style: an 8-character card-name field, not 10.
  - Verify the SDUM keyword itself is within FLUKA's 8-character limit — a trailing lowercase letter is a common generator artifact (`PRECISIOn` vs. `PRECISIO`).
  - Do not web-search first; compare local examples/templates and local troubleshooting records before broader lookup.
  - Example parser-safe DEFAULTS cards:
    ```text
    DEFAULTS                                                              HADROTHE
    DEFAULTS                                                              PRECISIO
    ```
- Confidence: 0.93
- Logged: 2026-03-09 (updated 2026-09-08)
- Source:
  - Curated AutoFLUKA troubleshooting record
  - ADS-derived curated regression case
  - AutoFLUKA curated run fix

### Invalid DEFAULTS keyword with non-run directive contamination

- Detection hint:
  - `No/unknown default specified, run stopped`
  - Input contains non-run directive lines such as `!@scale=100`.
- Signature:
  - `No/unknown default specified, run stopped`
  - Input contains non-run directive lines such as `!@scale=100`.
- Typical cause:
  - A GUI/export directive or invalid keyword remained in the run input and contributed to parser/runtime confusion.
- Suggested Fix:
  - Remove non-run directive lines before execution.
  - Keep the exact FLUKA `DEFAULTS` keyword from a validated local template for the installed version.
- Confidence: 0.82
- Logged: 2026-03-09
- Source:
  - Curated AutoFLUKA troubleshooting record

### BEAM card projectile or source definition runtime abort

- Detection hint:
  - `UNKNOWN PROJECTILE OR "OLD" HEAVY ION OPTION (NO LONGER SUPPORTED)`
  - `Abort called from FLUKAM reason UNKNOWN PROJECTILE`
- Signature:
  - `UNKNOWN PROJECTILE OR "OLD" HEAVY ION OPTION (NO LONGER SUPPORTED)`
  - `Abort called from FLUKAM reason UNKNOWN PROJECTILE`
  - Runtime abort appears immediately after the `BEAM` card.
- Typical cause:
  - The `BEAM` control card uses a runtime-incompatible or parser-fragile projectile/source layout.
  - Extra numeric entries or shifted fields cause FLUKA to misread the projectile name.
- Suggested Fix:
  - Rewrite the `BEAM` card in strict fixed-width format.
  - Keep only the required WHAT values and put the particle name in SDUM.
  - Keep source position on `BEAMPOS`.
  - Example proton pattern:
    ```text
    BEAM      -8.000E-01                                                  PROTON
    BEAMPOS          0.0       0.0     -25.0
    ```
- Confidence: 0.90
- Logged: 2026-03-09
- Source:
  - Curated AutoFLUKA troubleshooting record
  - ADS-derived curated regression case

### USRBDX solid-angle fields explicitly zeroed

- Detection hint:
  - FLAIR flags the `USRBDX` continuation line with WHAT(10), WHAT(11), and WHAT(12) set to `0.0`.
- Signature:
  - FLAIR flags the `USRBDX` continuation line with WHAT(10), WHAT(11), and WHAT(12) set to `0.0`.
- Typical cause:
  - Optional solid-angle fields were explicitly filled with zeros even though the scorer should rely on FLUKA defaults.
- Suggested Fix:
  - Remove the trailing zero entries from the `USRBDX` continuation card when defaults are intended.
  - Keep only required energy/binning terms populated and leave optional fields blank.
- Confidence: 0.80
- Logged: 2026-03-09
- Source:
  - Curated AutoFLUKA troubleshooting record

### Custom material missing low-energy neutron mapping

- Detection hint:
  - Run fails during initialization when low-energy neutrons are relevant.
  - Output indicates missing or unknown neutron cross-section mapping for a user-defined material name.
- Signature:
  - Run fails during initialization when low-energy neutrons are relevant.
  - Output indicates missing or unknown neutron cross-section mapping for a user-defined material name.
- Typical cause:
  - A custom `MATERIAL` or `COMPOUND` name was introduced without a compatible low-energy neutron library mapping.
- Suggested Fix:
  - Prefer built-in material tokens when low-energy neutron transport is important.
  - If a custom material is required, add a verified `LOW-MAT` mapping for the installed library/configuration.
  - Avoid redefining built-in material names.
- Confidence: 0.86
- Logged: 2026-03-12
- Source:
  - Curated AutoFLUKA troubleshooting record

### LOW-MAT repair attempt causes parser crash

- Detection hint:
  - Fortran runtime error or bad floating-point read after introducing or editing `LOW-MAT`.
  - Error points to fixed-format parsing such as `main/cncprs.f`.
- Signature:
  - Fortran runtime error or bad floating-point read after introducing or editing `LOW-MAT`.
  - Error points to fixed-format parsing such as `main/cncprs.f`.
- Typical cause:
  - `LOW-MAT` fields were populated with guessed numeric triplets or mixed identifier styles that do not match the installed neutron library.
- Suggested Fix:
  - Do not guess `LOW-MAT` numeric fields.
  - Prefer exact built-in/library-compatible material names.
  - Use only a verified `LOW-MAT` pattern for the specific FLUKA library/configuration.
- Confidence: 0.86
- Logged: 2026-03-12
- Source:
  - Curated AutoFLUKA troubleshooting record

### Stack overflow during transport

- Detection hint:
  - `Stack overflow in Feeder. Execution terminated.`
- Signature:
  - `Stack overflow in Feeder. Execution terminated.`
- Typical cause:
  - A single history generates excessive branching or secondaries, often due to an overly aggressive multiplying configuration.
- Suggested Fix:
  - Reduce the severity of multiplying geometry/material setup while preserving intent.
  - Shrink the most reactive volumes and rerun a low-statistics `test-n` attempt before scaling up.
- Confidence: 0.80
- Logged: 2026-03-12
- Source:
  - Curated AutoFLUKA troubleshooting record

### Residual nuclei scoring missing EVAPORAT physics

- Detection hint:
  - After adding `RESNUCLEi`, FLUKA reports that residual nuclei predictions require evaporation or heavy-fragment settings.
  - `RESNUCLEi` scorer fails even though output unit definitions appear valid.
- Signature:
  - After adding `RESNUCLEi`, FLUKA reports that residual nuclei predictions require evaporation or heavy-fragment settings.
  - `RESNUCLEi` scorer fails even though output unit definitions appear valid.
- Typical cause:
  - `RESNUCLEi` scorers were added without enabling the hadronic evaporation option used by FLUKA for residual nuclei production.
- Suggested Fix:
  - Add a validated `PHYSICS` card with `SDUM=EVAPORAT` and appropriate WHAT settings from a known-good local template.
  - Rerun a low-NPS `test-n` attempt before seeded production.
- Confidence: 0.84
- Logged: 2026-03-12
- Source:
  - Curated AutoFLUKA troubleshooting record
  - ADS-derived curated regression case

### Multiple or ambiguous material assignment warnings

- Detection hint:
  - FLAIR warns that a region has multiple material assignments.
  - Runtime output implies ambiguous or duplicate region assignment.
- Signature:
  - FLAIR warns that a region has multiple material assignments.
  - Runtime output implies ambiguous or duplicate region assignment.
- Typical cause:
  - `ASSIGNMA` lines were grouped or packed in a way that duplicated region references or caused ambiguous parsing.
- Suggested Fix:
  - Rewrite `ASSIGNMA` in a clear style while debugging, often one region per line.
  - Confirm each transport region has exactly one material except pure blackhole regions.
- Confidence: 0.82
- Logged: 2026-03-12
- Source:
  - Curated AutoFLUKA troubleshooting record

### FLAIR invalid bounding box geometry warnings

- Detection hint:
  - FLAIR reports invalid bounding boxes for multiple regions or bodies.
- Signature:
  - FLAIR reports invalid bounding boxes for multiple regions or bodies.
- Typical cause:
  - Overly complex region slicing, near-touching surfaces, or fragile combinations of infinite bodies.
- Suggested Fix:
  - Prefer finite bodies for main components, such as finite `RCC` cylinders and `RPP` boxes.
  - Simplify surrounding medium into a single air region where possible and re-check overlaps/holes.
- Confidence: 0.78
- Logged: 2026-03-12
- Source:
  - Curated AutoFLUKA troubleshooting record

### Concrete COMPOUND overflow or material-name parsing failure

- Detection hint:
  - `COMPOUND` line contains overflow artifacts such as `ONC`, `CONC`, or `CALCIUMCCONCRETE`.
  - Material-name parsing fails after concrete edits.
- Signature:
  - `COMPOUND` line contains overflow artifacts such as `ONC`, `CONC`, or `CALCIUMCCONCRETE`.
  - Material-name parsing fails after concrete edits.
  - Concrete composition appears malformed in echo output.
- Typical cause:
  - Concrete `MATERIAL`/`COMPOUND` cards are misaligned or crowded, causing names and numeric fractions to spill across fields.
  - Repairs changed the compound block before stabilizing the base material definition.
- Suggested Fix:
  - Keep concrete as a clear `MATERIAL` plus `COMPOUND` definition when a custom composition is required.
  - Use short material names and parser-safe fixed-format fields.
  - Repair material definitions before rewriting scorers.
- Confidence: 0.88
- Logged: 2026-04-29
- Source:
  - ADS-derived curated regression case

### Missing compound constituent material

- Detection hint:
  - `*** Unable to resolve name element POTASSIU in card ***`
  - FLUKA reports that a referenced compound constituent does not exist.
  - Example: `item 'POTASSIU' do not exist`
- Signature:
  - `*** Unable to resolve name element POTASSIU in card ***`
  - `COMPOUND   -0.337021   SILICON    -0.013  POTASSIU    -0.044   CALCIUMCONCRETE`
  - `*** run stopped ***`
  - FLUKA reports that a referenced compound constituent does not exist.
  - Example: `item 'POTASSIU' do not exist`
- Typical cause:
  - A `COMPOUND` references an element/material token that is not available in the current setup.
  - A repair pass removed an explicitly defined constituent required by the chosen composition path.
- Suggested Fix:
  - Define the missing constituent with a FLUKA-compatible 8-character material name before referencing it in `COMPOUND`.
  - Do not assume every compound requires `POTASSIU`; define whichever constituent FLUKA reports as missing.
  - Example:
    ```text
    MATERIAL         19.   39.0983     0.862                              POTASSIU
    ```
- Confidence: 0.90
- Logged: 2026-04-29
- Source:
  - ADS-derived curated regression case

### Non-sequential user material number / deprecated MATERIAL WHAT(2) setting

- Detection hint:
  - `Input material CONCRETE number changed from 27 to 26`
  - `Input material <TOKEN> number changed from <N> to <M>`
  - `Abort called from MATCRD reason DEPRECATED MATERIAL WHAT(2) SETTING`
  - `Material <NAME> WHAT(2)=<value> Atomic Weight manual setting deprecated. To FORCE it please use a negative value`
- Signature:
  - `Input material CONCRETE number changed from 27 to 26`
  - `Input material <TOKEN> number changed from <N> to <M>`
  - `Abort called from MATCRD reason NON SEQUENTIAL MATERIAL NUMBER`
  - `NON SEQUENTIAL MATERIAL NUMBER`
  - `Abort called from MATCRD reason DEPRECATED MATERIAL WHAT(2) SETTING`
- Typical cause — **two distinct root causes share this abort reason text; check which field triggered it before applying a fix:**
  1. **Explicit material number** — a user `MATERIAL` card forced an explicit material index/number that did not match FLUKA's expected uninterrupted user-material numbering sequence. The material definition may be physically correct, but the explicit number conflicts with FLUKA's internal/user material ordering. Confirmed to recur with the same abort reason text.
  2. **Positive atomic-weight override** — a user `MATERIAL` card set `WHAT(2)` (atomic weight) to a positive manual value to override the built-in default. Recent FLUKA versions treat a positive manual override as deprecated and require a negative value to force it. The FLUKA error text itself names the field when this is the cause (`... Atomic Weight manual setting deprecated ...`), e.g. for `MATERIAL COPPER WHAT(2)=63.55`.
- Suggested Fix:
  - Preserve the intended material or compound composition; do not delete or substitute the material just to make the run continue.
  - If the error text mentions "Atomic Weight" or "manual setting deprecated": keep the override but make it negative, e.g. `COPPER -63.546`, `SILICON -28.0855` — this preserves densities/names while satisfying the new sign convention.
  - If the error text is only the generic `NON SEQUENTIAL MATERIAL NUMBER` reason with no atomic-weight framing: remove the explicit material number field entirely and let FLUKA assign the next valid number.
  - If custom `MATERIAL` alignment itself becomes parser-unsafe after either fix (e.g. the name shifts into a numeric WHAT field), consider using FLUKA's built-in material tokens (e.g. `COPPER`, `SILICON`) instead of a custom `MATERIAL` card when the built-in composition is acceptable — confirmed as a working simplification.
  - Keep the corrected `MATERIAL`/`COMPOUND` definition stable before changing scoring cards.
  - Example corrected patterns:
    ```text
    MATERIAL                                                              CONCRETE
    MATERIAL         29.   -63.546      8.96                              COPPER
    ```
- Confidence: 0.95
- Logged: 2026-04-29 (updated 2026-09-08)
- Source:
  - ADS-derived curated regression case
  - AutoFLUKA curated run fix

### Duplicate primary source or beam card

- Detection hint:
  - Two `BEAM` cards appear before the first `BEAMPOS` or before the transport setup is complete.
  - Duplicate primary source definition cards are present in one input.
- Signature:
  - Two `BEAM` cards appear before the first `BEAMPOS` or before the transport setup is complete.
  - Duplicate primary source definition cards are present in one input.
- Typical cause:
  - A previous repair, template merge, or manual paste duplicated the source definition.
  - FLUKA may parse the later card as an override or may enter runtime initialization with conflicting source information.
- Suggested Fix:
  - Keep one intentional source/beam definition and remove accidental duplicates.
  - Preserve the user's intended particle, energy, and source position from the correct card.
  - Re-run the next `test-n` attempt after the duplicate is removed.
- Confidence: 0.88
- Logged: 2026-04-29
- Source:
  - ADS-derived curated regression case

### Valid fixed-format SDUM adjacency mistaken for merged-token error

- Detection hint:
  - Validator reports merged numeric/text tokens on cards where the trailing text is an SDUM label.
  - Examples include trailing labels adjacent to the last WHAT field on `MATERIAL`, `PHYSICS`, `BEAM`, `COMPOUND`, or scorer cards.
- Signature:
  - Validator reports merged numeric/text tokens on cards where the trailing text is an SDUM label.
  - Examples include trailing labels adjacent to the last WHAT field on `MATERIAL`, `PHYSICS`, `BEAM`, `COMPOUND`, or scorer cards.
- Typical cause:
  - Fixed-format FLUKA cards can place SDUM text in the final field; visually tight numeric/text adjacency is not always a parse error.
  - A generic whitespace validator treated valid fixed-column SDUM placement as a missing separator.
- Suggested Fix:
  - Do not automatically rewrite accepted fixed-format SDUM adjacency.
  - Flag the line only when an alphanumeric token lands in a numeric-only WHAT position, shifts later fields, or is confirmed by FLUKA echo/error evidence.
  - Preserve the original physics and scorer intent while correcting only true spillover.
- Confidence: 0.86
- Logged: 2026-04-29
- Source:
  - ADS-derived curated regression case

### Unknown projectile from crowded or conflicting BEAM definition

- Detection hint:
  - `Abort called from FLUKAM reason UNKNOWN PROJECTILE OR "OLD" HEAVY ION OPTION (NO LONGER SUPPORTED)`
  - Runtime abort appears during beam/source initialization even though the particle name looks valid.
- Signature:
  - `Abort called from FLUKAM reason UNKNOWN PROJECTILE OR "OLD" HEAVY ION OPTION (NO LONGER SUPPORTED)`
  - Runtime abort appears during beam/source initialization even though the particle name looks valid.
- Typical cause:
  - The `BEAM` card is duplicated, crowded, or contains extra shifted WHAT fields that cause FLUKA to misread the projectile/source definition.
- Suggested Fix:
  - Remove accidental duplicate `BEAM` cards.
  - Rewrite the source definition using the smallest parser-safe card that preserves the intended particle and energy.
  - If the same projectile error persists after apparent SDUM alignment, remove ambiguous optional WHAT fields and keep only the required beam energy/particle fields.
  - Keep source location/orientation on `BEAMPOS` or intentional source cards instead of adding extra BEAM fields.
  - Example minimal pattern:
    ```text
    BEAM          -0.600                                                  PROTON
    BEAMPOS          0.0       0.0     -29.0
    ```
- Confidence: 0.90
- Logged: 2026-04-29
- Source:
  - ADS-derived curated regression case

### Windows CRLF line endings interfere with Linux-side FLUKA parsing

- Detection hint:
  - Persistent parser/runtime misread under WSL or Linux execution even after cards match known-good local examples.
  - Fixed-format cards look correct in a Windows editor, but FLUKA still misreads `DEFAULTS`, `BEAM`, material, or scoring SDUM fields.
- Signature:
  - Persistent parser/runtime misread under WSL or Linux execution even after cards match known-good local examples.
  - Fixed-format cards look correct in a Windows editor, but FLUKA still misreads `DEFAULTS`, `BEAM`, material, or scoring SDUM fields.
  - The same deck changes behavior after newline normalization.
- Typical cause:
  - A Windows-edited deck contains CRLF line endings or hidden carriage-return characters that interact poorly with fixed-format parsing in the Linux/WSL FLUKA execution path.
  - The visible card text may be correct, but the runtime receives extra carriage-return characters at line endings.
- Suggested Fix:
  - Normalize the input deck to Unix LF line endings before running through Linux/WSL.
  - Keep the physics/card repairs unchanged while converting only the newline format.
  - Re-run the next isolated `test-n` attempt after normalization.
  - Example shell normalization:
    ```text
    python -c "from pathlib import Path; p=Path('case.inp'); p.write_text(p.read_text().replace('\r\n','\n'), newline='\n')"
    ```
- Confidence: 0.82
- Logged: 2026-04-30
- Source:
  - ADS-derived curated regression case

### Ambiguous formatted real field in FLUKA card

- Detection hint:
  - `*** The 4th field ... MATERIAL        19.0      39.10      0.862                           POTASSIU ... does not contain a valid formatted fortran real number`
  - `The <N>th field ... MATERIAL ... does not contain a valid formatted fortran real number`
- Signature:
  - `*** The 4th field ... MATERIAL        19.0      39.10      0.862                           POTASSIU ... does not contain a valid formatted fortran real number`
  - `The <N>th field ... MATERIAL ... does not contain a valid formatted fortran real number`
  - FLUKA rejects a numeric WHAT field after an inserted or repaired fixed-format card.
- Typical cause:
  - A value is not right-aligned in its 10-column field. FLUKA reads blanks as nothing, but rejects an integer or exponent that is followed by blanks inside its field, because under the "blank=0" rule those blanks would become extra digits (`1.0E4␣␣` could be `1.0E400`). That is what "It is ambiguous … blank=0 formatted input rule" means.
  - A value that runs past the end of its field leaves a fragment in the next field (e.g. `0`), which is then an integer followed by blanks and is rejected.
  - The visible card may look reasonable in an editor, but the Fortran fixed-format reader sees the field by column.
- Suggested Fix:
  - Rewrite the whole card with `fluka_card_formatter_tool` so every value ends exactly at column 20, 30, 40, 50, 60 or 70. Do not change the notation (exponent vs decimal); change the position.
  - Keep unused numeric fields as truly blank aligned columns before the SDUM/name field.
  - Preserve the intended material/source/scoring physics while correcting only the field alignment.
  - Example material pattern:
    ```text
    MATERIAL        19.0      39.1     0.862                              POTASSIU
    ```
- Confidence: 0.88
- Logged: 2026-04-30
- Source:
  - ADS-derived curated regression case

### START card integer-like field rejected as formatted real

- Detection hint:
  - `The 1th field 1000 of the START input card does not contain a valid formatted fortran real number`
  - `START          1000`
  - `*** The 2th field ... START        1000.         0 ... does not contain a valid formatted fortran real number`
  - `The 2th field ... START`
- Signature:
  - `The 1th field 1000 of the START input card does not contain a valid formatted fortran real number`
  - `START          1000`
  - `*** The 2th field ... START        1000.         0 ... does not contain a valid formatted fortran real number`
  - `The 2th field ... START`
  - `START        1000.         0`
- Typical cause:
  - The NPS does not end at column 20. `START          1000` ends at column 19, so it is an integer followed by a blank: rejected. `START          1000.0` ends at column 21, so its last `0` lands in WHAT(2) as an integer followed by blanks: rejected ("The 2th field 0").
  - `START       1.0E+03` ends at column 19 (an exponent followed by a blank): rejected. The notation is not the cause; a right-aligned `START        1.0E+03` runs fine (verified with the installed FLUKA).
  - The test-run NPS cap was correct, but the card was spaced by hand.
- Suggested Fix:
  - Rewrite the card with `fluka_card_formatter_tool` so the NPS ends exactly at column 20. Decimal, integer and exponent forms all work once right-aligned.
  - Avoid adding extra WHAT fields when only the primary count is being changed.
  - For production runs, restore the requested production NPS the same way, and check `Total number of primaries run:` in the `.out` afterwards (a value spilling into WHAT(2) can also run silently with the wrong count; see "START card numeric field overflow or misread NPS").
  - Example:
    ```text
    *...+....1....+....2....+....3....+....4....+....5....+....6....+....7....+....8
    * correct (decimal and exponent, both ending at column 20):
    START         1000.0
    START        1.0E+03
    * rejected (the first ends at column 21, the second at column 19):
    START          1000.0
    START       1.0E+03
    ```
- Confidence: 0.90
- Logged: 2026-04-30
- Source:
  - ADS-derived curated regression case
  - AutoFLUKA curated run fix

### Unresolved material or element token in FLUKA card

- Detection hint:
  - `*** Unable to resolve name element POTASSIU in card ***`
  - `*** Unable to resolve name element <TOKEN> in card ***`
- Signature:
  - ` *** Unable to resolve name element POTASSIU in card ***`
  - `*** Unable to resolve name element <TOKEN> in card ***`
  - A `COMPOUND`, `ASSIGNMA`, or related material card references a material/element token that FLUKA cannot resolve.
- Typical cause:
  - The referenced token is not defined before use, exceeds the parser-safe name form, is shifted out of the expected SDUM/name field, or is unavailable in the current FLUKA setup.
- Suggested Fix:
  - Preserve the intended material composition and repair the definition/reference relationship.
  - If a compound constituent is missing, define that constituent before the `COMPOUND` card or use a valid built-in/material identifier for that constituent.
  - If an assignment token is unresolved, verify the material SDUM placement and name length; use the resolved numeric material identifier only when it preserves the same intended material.
  - Do not delete a custom compound or replace it with a different material unless the user explicitly accepts that physics simplification.
- Confidence: 0.92
- Logged: 2026-04-29
- Source:
  - ADS-derived curated regression case

### Residual-nuclei scoring requires EVAPORAT activation

- Detection hint:
  - `Predictions for residual nuclei production and decays require the activation of heavy fragment evaporation by means of the PHYSICS/EVAPORAT card`
  - `PHYSICS/EVAPORAT`
- Signature:
  - `Predictions for residual nuclei production and decays require the activation of heavy fragment evaporation by means of the PHYSICS/EVAPORAT card`
  - `PHYSICS/EVAPORAT`
  - `Execution terminated` after `RESNUCLE` cards are echoed.
- Typical cause:
  - `RESNUCLE` scoring is requested, but FLUKA did not interpret a valid heavy-fragment evaporation activation card before execution.
  - The `PHYSICS` card may be missing, placed too late for the runtime setup, or formatted so `EVAPORAT` is not read as the intended SDUM.
- Suggested Fix:
  - Preserve `RESNUCLE` scoring if the user requested residual-nuclei results.
  - Add or repair a parser-safe `PHYSICS` card with `EVAPORAT` before residual-nuclei scoring is used, following a known-good local pattern for the installed FLUKA version.
  - Example pattern:
    ```text
    PHYSICS          3.0       0.0       0.0       0.0       0.0       0.0EVAPORAT
    ```
- Confidence: 0.92
- Logged: 2026-04-29
- Source:
  - ADS-derived curated regression case

### Material mixture initialization crash in mulmix

- Detection hint:
  - `At line 391 of file cascade/mulmix.f`
  - `Fortran runtime error: Index '0' of dimension 1 of array 'fclmbz' below lower bound of 1`
- Signature:
  - `At line 391 of file cascade/mulmix.f`
  - `Fortran runtime error: Index '0' of dimension 1 of array 'fclmbz' below lower bound of 1`
  - `Subroutine Mulmix: medium n.`
  - Material echo shows zero density, zero atomic number, or a one-element placeholder mixture for a material that should be compound.
- Typical cause:
  - FLUKA reached material mixture initialization with an invalid, unresolved, or partially defined material/compound.
  - A prior repair may have substituted a numeric material identifier or altered the compound block without preserving the intended composition.
- Suggested Fix:
  - Inspect the material echoed immediately before the `mulmix.f` failure.
  - Restore the intended `MATERIAL`/`COMPOUND` definition and ensure all constituents resolve before assignment.
  - Avoid substituting a different material or deleting a compound unless the user explicitly accepts the physics change.
- Confidence: 0.88
- Logged: 2026-04-29
- Source:
  - ADS-derived curated regression case

### Physics-changing repair attempted without user approval

- Detection hint:
  - A repair removes a custom `MATERIAL`/`COMPOUND`, deletes a requested scorer, disables source terms, or substitutes a different material to make execution continue.
  - The run may proceed, but the simulation no longer represents the user's requested physics.
- Signature:
  - A repair removes a custom `MATERIAL`/`COMPOUND`, deletes a requested scorer, disables source terms, or substitutes a different material to make execution continue.
  - The run may proceed, but the simulation no longer represents the user's requested physics.
- Typical cause:
  - Troubleshooting prioritized parser success over preserving the scientific intent of the input.
- Suggested Fix:
  - Treat material definitions, source definitions, and scoring cards as physics intent.
  - Apply the smallest correction that preserves the requested setup.
  - Ask the user before disabling scorers, replacing custom materials, removing compounds, or changing source physics.
- Confidence: 0.95
- Logged: 2026-04-29
- Source:
  - ADS-derived curated regression case

### Scorer rewrites before material stability

- Detection hint:
  - Repeated `USRTRACK`, `USRBDX`, `USRBIN`, or `RESNUCLEi` repairs do not change the fatal runtime blocker.
  - Material-related errors remain in echo/runtime output.
- Signature:
  - Repeated `USRTRACK`, `USRBDX`, `USRBIN`, or `RESNUCLEi` repairs do not change the fatal runtime blocker.
  - Material-related errors remain in echo/runtime output.
- Typical cause:
  - The repair process changed scoring cards while the material block or fixed-format foundations were still unstable.
- Suggested Fix:
  - Stabilize geometry/material/defaults/beam first.
  - Only then revise scoring cards.
  - Prefer known-good local examples before introducing broad scorer rewrites.
- Confidence: 0.82
- Logged: 2026-04-29
- Source:
  - ADS-derived curated regression case

### Echo-input or launcher noise confused with core FLUKA failure

- Detection hint:
  - `AutoFLUKA_job*.log` reports missing continuation/random files after failed jobs.
  - Echo-input runs are launched and wrapper logs appear noisy.
- Signature:
  - `AutoFLUKA_job*.log` reports missing continuation/random files after failed jobs.
  - Echo-input runs are launched and wrapper logs appear noisy.
  - The same fatal FLUKA signature appears in `*-echo*.err`, `*-echo*.log`, or `*-echo*.out`.
- Typical cause:
  - Launcher/tool side effects are being treated as the root cause instead of checking FLUKA-generated echo/runtime files first.
- Suggested Fix:
  - Ignore `AutoFLUKA_job*.log` by default for physics/parser diagnosis.
  - Diagnose `*-echo*.err`, then `*-echo*.log`, then bounded `*-echo*.out` tail before consulting launcher logs.
- Confidence: 0.90
- Logged: 2026-04-29
- Source:
  - ADS-derived curated regression case

### RANDOMIZ seed fixed-format parse failure

- Detection hint:
  - RANDOMIZ card reports a formatted Fortran real parse error.
  - The 2th or 3th field of RANDOMIZ does not contain a valid formatted fortran real number.
- Signature:
  - `RANDOMIZ          1.0         6.0 *** does not contain a valid formatted fortran real number`
  - `RANDOMIZ          1.         6. *** does not contain a valid formatted fortran real number`
  - `The 3th field ... of the following input card RANDOMIZ ... does not contain a valid formatted fortran real number`
  - `The 2th field ... of the following input card RANDOMIZ ... does not contain a valid formatted fortran real number`
- Typical cause:
  - Seeded-copy generation edited the `RANDOMIZ` line by token replacement instead of reconstructing the card in parser-safe fixed-format columns.
  - Digits or decimal points can land in the next fixed-format field, making the seed ambiguous or invalid for FLUKA formatted input.
- Suggested Fix:
  - Rewrite the entire `RANDOMIZ` line when changing seeds (`fluka_card_formatter_tool`, or the seeded-copy generator, which now rewrites by column); do not patch the seed token in place.
  - The seed must end exactly at column 30. A seed that crosses column 30 is either rejected (its tail in WHAT(3) is an integer followed by blanks) or **silently truncated**: `RANDOMIZ         1.0   54217137.0` runs with seed 5421713, and `RANDOMIZ         1.0    54217137.` with seed 542171. If seeded copies differ only in the truncated digits, every "independent" cycle uses the same seed.
  - `54217137.0` is not too long by itself: right-aligned it fills columns 21-30 exactly and works. It failed only because it started at column 22.
  - Correct patterns:
    ```text
    *...+....1....+....2....+....3....+....4....+....5....+....6....+....7....+....8
    RANDOMIZ         1.0 54217137.
    RANDOMIZ          1.         6
    RANDOMIZ          1.       10.
    ```
- Confidence: 0.90
- Logged: 2026-05-24
- Source:
  - AutoFLUKA curated run fix — seeded RANDOMIZ formatting regression

### FLUKA user routine compile failure from FLAIR metadata contamination

- Detection hint:
  - `fff` fails on `source_newgen.f` or another user routine.
  - Compiler output includes `invalid preprocessing directive #flair` or non-numeric character in statement label.
- Signature:
  - `fff failed for source_newgen.f`
  - `invalid preprocessing directive #flair`
  - `Non-numeric character in statement label`
  - A file named like `source_newgen.f` contains FLAIR project, run, plot, or GUI metadata around the Fortran routine.
- Typical cause:
  - The file supplied as a FLUKA user routine is not clean Fortran source.
  - It is a mixed FLAIR project/export file with metadata before or after the real `SUBROUTINE SOURCE` code.
  - `fff` compiles the whole file, so FLAIR metadata is interpreted as invalid Fortran or invalid preprocessing text.
- Suggested Fix:
  - Extract or regenerate a Fortran-only routine file containing the actual modules and user subroutine declarations.
  - Remove FLAIR project/run/plot metadata before calling `fff`.
  - Add a pre-compile hygiene check for lines beginning with FLAIR metadata markers when routine files are staged.
- Confidence: 0.90
- Logged: 2026-05-24
- Source:
  - AutoFLUKA curated run fix — FLAIR metadata contamination in Fortran routine

### SOURCE routine auxiliary data file missing in staged run directory

- Detection hint:
  - SOURCE routine aborts while opening a histogram or fluence data file.
  - Runtime output says unable or impossible to open an auxiliary data file.
- Signature:
  - `Impossible to open file AmBedNdE_Fluence.dat`
  - `Unable to open histogram file`
  - `Abort called from sample_histogram_momentum_energy reason Unable to open histogram file`
  - SOURCE routine reads an external `.dat` file by a relative path, then fails inside an isolated `test-n` or seeded run folder.
- Typical cause:
  - The FLUKA deck and user routine were staged into a fresh execution directory, but the SOURCE routine depends on an external data file that was not copied into the same relative location.
  - Relative file opens inside Fortran user routines are resolved from the runtime working directory, not necessarily from the original project directory.
- Suggested Fix:
  - Stage required SOURCE auxiliary files together with the input deck and routine, or rewrite the routine path to a stable relative location for the staged folder.
  - Treat routine data dependencies as part of the execution bundle, like the `.inp` and `.f` files.
  - After repair, confirm the routine debug/log output appears and the run uses the linked executable.
  - Observed repair pattern: keep `AmBedNdE_Fluence.dat` in the seeded-run root and open it from staged test folders via `../AmBedNdE_Fluence.dat`.
- Confidence: 0.90
- Logged: 2026-05-24
- Source:
  - AutoFLUKA curated run fix — SOURCE routine auxiliary data file staging

### rfluka random sidecar not generated after seeded input failure

- Detection hint:
  - AutoFLUKA job logs report `No ran<input><cycle> generated` after a seeded run attempt.
  - Missing `ran*` random sidecar appears alongside failed FLUKA jobs.
- Signature:
  - `Error: No ranTEPC_seed__01002 generated!`
  - `No ran<INPUT><CYCLE> generated`
  - The message appears for seeded inputs after FLUKA aborts or after using long/crowded generated input stems.
- Typical cause:
  - The missing `ran*` message can be a launcher-side symptom after the true FLUKA failure has already occurred.
  - In the observed workflow it appeared with long generated stems and concurrent upstream failures, so it should not be treated as the first root cause without checking the FLUKA `.err` and `.out` files.
- Suggested Fix:
  - Inspect the paired FLUKA `.err` or bounded `.out` tail first for the real parser/runtime failure.
  - Prefer short, simple seeded input stems such as `TEPC_01` when launching many seeded jobs.
  - Do not diagnose missing `ran*` sidecars as a physics problem unless the FLUKA deck itself otherwise completed initialization cleanly.
- Confidence: 0.75
- Logged: 2026-05-24
- Source:
  - AutoFLUKA curated run fix — rfluka seeded run sidecar diagnosis

### echinp.f path truncation — run aborts before transport due to long or space-containing working directory

- Detection hint:
  - Run terminates immediately before any particle transport begins.
  - The `.log` file shows a Fortran runtime error from `echinp.f` at approximately line 42.
  - The error path contains a mangled or truncated segment (e.g., `/te/` instead of `/test-1/`) or a partial directory name cut at a space character (e.g., `Texas A` truncated to `Texas A`).
- Signature:
  - `At line 42 of file main/echinp.f (unit = 8) Fortran runtime error: Cannot open file '<path>': No such file or directory`
  - `Error termination. Backtrace: #0  0x...`
  - Path in error contains a truncated directory segment or a space-split component
- Typical cause:
  - FLUKA constructs the echo-file path by concatenating the run directory and input basename inside a fixed-size Fortran character buffer. When the combined path exceeds the buffer limit, or when the path contains spaces that are treated as delimiters, the resulting filename is malformed and cannot be opened.
- Suggested Fix:
  - Shorten the input basename to ≤8 characters (e.g., rename `carbon_290mevu_waterphantom.inp` to `c12bp.inp`).
  - Move the run directory to a path with no spaces and a short total length.
  - Always run the corrected deck in a fresh `test-n` folder — never reuse the failed folder.
  - As a preventive rule: keep input basenames short and ensure the full absolute path to the run directory contains no spaces.
- Confidence: 0.95
- Logged: 2026-07-04
- Source:
  - AutoFLUKA curated run fix — Bragg-peak carbon ion water phantom test run

### BEAM card HEAVYION SDUM misalignment — field spills into WHAT(6) causing "not a valid real number" abort

- Detection hint:
  - Run aborts during input card parsing, before geometry or transport initialise.
  - The `.out` or `.log` echo shows the BEAM card with `HE` or a fragment of `HEAVYION` appearing in the numeric WHAT(6) position.
- Signature:
  - `*** The 6th field         HE of the following input card ***`
  - `BEAM          -0.290                                                HEAVYION`
  - `*** does not contain a valid formatted fortran real number ***`
- Typical cause:
  - The SDUM field `HEAVYION` was not aligned to the fixed column 71–80 slot. When it drifts left into the WHAT(6) numeric field, FLUKA attempts to parse the leading characters as a real number and fails.
- Suggested Fix:
  - Rewrite the BEAM card in strict fixed-column format with blank WHAT(2)–WHAT(6) fields and `HEAVYION` right-padded to the 10-character SDUM slot at columns 71–80.
  - Safe example (ruler shown for reference):
    ```
    *...+....1....+....2....+....3....+....4....+....5....+....6....+....7....+....8
    BEAM          -0.290                                                  HEAVYION
    ```
  - Verify alignment by counting: keyword (cols 1–8), two blanks (cols 9–10), then six 10-character WHAT fields, then the 10-character SDUM. `HEAVYION` should begin at column 71.
- Confidence: 0.95
- Logged: 2026-07-04
- Source:
  - AutoFLUKA curated run fix — Bragg-peak carbon ion water phantom test run

### RANDOMIZE seed written as bare integer — Fortran fixed-format parsing failure

- Detection hint:
  - Run aborts during input card parsing or produces unexpected random-sequence behaviour.
  - RANDOMIZE card in the `.inp` has the seed written without a decimal point (e.g., `145789` instead of `145789.`).
- Signature:
  - Fortran runtime error or silent misread during RANDOMIZE card parsing.
  - WHAT(2) of RANDOMIZE contains an integer literal (no decimal point) in a fixed-format E10 field.
- Typical cause:
  - The integer is not right-aligned. FLUKA rejects an integer (or exponent) that is followed by blanks inside its 10-column field, because under the blank=0 rule those blanks would become extra digits. A right-aligned integer such as `    145789` in columns 21-30 is read correctly; the missing decimal point is not the cause.
- Suggested Fix:
  - Rewrite the card with `fluka_card_formatter_tool` so each value ends at column 20 and 30. A decimal point is fine but not required.
  - Correct forms: `RANDOMIZ         1.0 54217137.` and `RANDOMIZ         1.0    145789`
  - Wrong form: `RANDOMIZ         1    145789` (`1` ends at column 18 and `145789` at column 28; both are followed by blanks)
  - The same applies to START: `START         1000.0` and `START        1.0E+03` are correct; see "START card integer-like field rejected as formatted real".
- Confidence: 0.85
- Logged: 2026-07-04
- Source:
  - AutoFLUKA authoring rule — fixed-format numeric field discipline

### Obsolete "old style interaction forcing" abort — three confirmed trigger fields

- Detection hint:
  - Run aborts very early (immediately after `BEAMPOS` echo, or immediately after `PHYSICS EVAPORAT`), before geometry/transport begins.
  - `*** The old style interaction forcing is obsolete, use LAM-BIAS instead ***`
- Signature:
  - `**************************************** *** The old style interaction forcing is obsolete, use LAM-BIAS instead *** ****************************************`
- Typical cause — **confirmed from three independent runs to have more than one trigger; check both fields before assuming which one applies:**
  1. `BEAMPOS` WHAT(4)–WHAT(6) set nonzero for what was intended as a simple pencil beam. This FLUKA build interprets nonzero values there as obsolete interaction-forcing/direction fields, not a beam-direction specification. Confirmed independently on more than one occasion.
  2. `PHYSICS ... EVAPORAT` card with `WHAT(1)=1.0` — this selects the obsolete old-style evaporation/interaction-forcing model.
- Suggested Fix:
  - For a simple pencil beam along the default beam axis, specify only the beam starting coordinates on `BEAMPOS` and leave WHAT(4)–WHAT(6) blank/zero, e.g. `BEAMPOS` with WHAT(1..3) = 0.0, 0.0, -5.0 (written with `fluka_card_formatter_tool`).
  - For evaporation physics, use `WHAT(1)=3.0` on the `PHYSICS EVAPORAT` card (new evaporation model with heavy-fragment support), not `1.0`. Keep a `LAM-BIAS` card for inelastic interaction biasing if that was the actual intent.
  - If the error persists after fixing one field, check the other — both are independently capable of producing the identical error text.
- Confidence: 0.90
- Logged: 2026-09-08
- Source:
  - AutoFLUKA curated run fix

### GEOBEGIN/COMBNAME embedded geometry header format

- Detection hint:
  - Run aborts immediately after the `GEOBEGIN` card, before any body/region echo.
  - `.log` shows a Fortran runtime error in `comlat/flkcgi.f` (around line 226) or `geolat/geoinp.f`: `Bad integer for item 1 in list input`.
  - Alternatively, FLUKA reports `ITYPE = <text>` does not equal any valid body type (`ARB SPH RCC ... END`), or the SDUM (`COMBNAME`) itself is rejected as "not a valid formatted fortran real number."
- Signature:
  - `At line 226 of file comlat/flkcgi.f Fortran runtime error: Bad integer for item 1 in list input`
  - `ITYPE = <first characters of a stray text line> does not equal any of the following: ARB SPH RCC REC TRC ELL BOX WED RPP ZCC ZEC XYP XZP YZP PLA XCC XEC YCC YEC QUA END`
  - `The 1th field COMBNAME of the following input card GEOBEGIN ... COMBNAME does not contain a valid formatted fortran real number when one is expected`
- Typical cause — **discovered across five separate failed attempts before converging on the correct format:**
  - Embedded combinatorial geometry (`GEOBEGIN ... COMBNAME`) requires an exact record sequence immediately after the `GEOBEGIN` card: (1) in `FREE` format, `GEOBEGIN` needs six numeric WHAT placeholders before the `COMBNAME` SDUM, otherwise the SDUM itself is parsed as WHAT(1); (2) a geometry title/comment line; (3) a numeric geometry control record (`0    0`); only then do body cards begin.
  - Any stray prose/title line placed where a body card or the numeric control record is expected gets parsed as geometry input and crashes either as "bad integer" (control-record position) or "ITYPE does not equal" (body-card position).
  - Inserting an *extra* title line, or omitting the numeric control line entirely, both produce the same class of failure — the exact record count and order matters, not just "some title text exists somewhere."
- Suggested Fix:
  - Use exactly this record order after `GEOBEGIN`:
    1. `GEOBEGIN` card with SDUM `COMBNAME` — in `FREE` format, pad with six `0.0` WHAT placeholders before the SDUM.
    2. One geometry title/comment line.
    3. One numeric geometry control record: `    0    0`.
    4. Body cards (e.g. `SPH ...`), each a genuine body definition — never a bare descriptive line. Prefix any human-readable notes in this section with `*` (FLUKA comment) or remove them.
  - Always write the repaired deck into a fresh `test-n` folder rather than editing in place.
  - In a fixed-format deck, `COMBNAME` starts at column 71 with the WHAT fields left blank. In `FREE` format, use the space-separated form in the next entry. The bundled working examples (fixed format) put the title on the control record itself: `    0    0          <title>`.
  - Example (fixed format):
    ```text
    GEOBEGIN                                                              COMBNAME
    Bragg-peak dosimetry geometry
        0    0
    SPH BLKBODY    0.0 0.0 0.0 100000.0
    END
    ```
- Confidence: 0.90
- Logged: 2026-09-08
- Source:
  - AutoFLUKA curated run fix

### Free-format SDUM-only card missing numeric WHAT placeholders (DEFAULTS, GEOBEGIN)

- Detection hint:
  - `FREE` format is active, and a card that is normally "SDUM only" (e.g. `DEFAULTS PRECISIO`, `GEOBEGIN ... COMBNAME`) is rejected with the SDUM text itself flagged as an invalid formatted real number.
- Signature:
  - `The 1th field PRECISIOn of the following input card DEFAULTS PRECISIOn does not contain a valid formatted fortran real number`
  - `The 1th field COMBNAME of the following input card GEOBEGIN ... COMBNAME does not contain a valid formatted fortran real number when one is expected`
- Typical cause:
  - In fixed-format mode, blank WHAT fields before an SDUM are implicit. In `FREE` format, they are not — writing `DEFAULTS PRECISIO` with no numeric fields makes the parser treat the SDUM token itself as WHAT(1).
- Suggested Fix:
  - When `FREE` is active, always write six explicit numeric WHAT placeholders before an SDUM-only card's keyword, e.g.:
    ```text
    DEFAULTS  0.0 0.0 0.0 0.0 0.0 0.0 PRECISIO
    GEOBEGIN  0.0 0.0 0.0 0.0 0.0 0.0 COMBNAME
    ```
  - This is specific to `FREE` format — fixed-format decks do not need this and should follow the column-based examples elsewhere in this KB instead.
- Confidence: 0.88
- Logged: 2026-09-08
- Source:
  - AutoFLUKA curated run fix

### TITLE card format — neither a plain first line nor an argument-bearing TITLE card

- Detection hint:
  - `*** Unknown control code: TITLE <text>, ignored ***` when title text was passed as an argument on a `TITLE` card.
  - `*** Unknown control code: <title text>, ignored ***` when the title text was instead written as a bare first line with no `TITLE` keyword at all.
- Signature:
  - `*** Unknown control code: TITLE 23, ignored ***`
  - `*** Unknown control code: 230 MeV , ignored ***`
  - `**** Unknown Input card !!!!!!!!! ****`
- Typical cause:
  - Two incorrect forms were both tried and both failed: `TITLE <text>` as a single card with the text as an argument, and a bare title-text line with no `TITLE` card at all. This FLUKA parser requires a `TITLE` card with **no arguments**, immediately followed by the title text on its own next line.
- Suggested Fix:
  - Write exactly two lines at the top of the deck: `TITLE` alone on the first line, then the descriptive title text on the line immediately after it — before `FREE`/`DEFAULTS` and the rest of the control cards.
  - Example:
    ```text
    TITLE
    Bragg-peak dosimetry — copper degrader, silicon detector
    ```
- Confidence: 0.88
- Logged: 2026-09-08
- Source:
  - AutoFLUKA curated run fix

### Duplicate built-in material names in name-based (COMBNAME) input

- Detection hint:
  - Run progresses past geometry and material card parsing, then terminates with FLUKA reporting two material numbers sharing the same name.
- Signature:
  - `!!!! Materials n. 12 (COPPER  ) and n. 25(COPPER  ) share the same name, n. 12 will be used for all name based inputs !!!!`
  - `Materials n. <A> (<NAME>) and n. <B> (<NAME>) share the same name in a (possibly) name based input Execution terminated.`
- Typical cause:
  - A user-defined `MATERIAL` card reused a name that also matches one of FLUKA's own built-in materials (e.g. `COPPER`, `SILICON`). In name-based (`COMBNAME`) geometry, FLUKA cannot disambiguate which numbered material a name-based reference (`ASSIGNMA`, `LAM-BIAS`, etc.) means, and terminates rather than guess.
  - Note this is the reverse situation from cases where switching *to* a built-in material resolves a different problem (see "Non-sequential user material number / deprecated MATERIAL WHAT(2) setting") — here the conflict is a custom material colliding with an existing built-in of the same name, not a custom material's own card being malformed.
- Suggested Fix:
  - Preserve the intended material composition and density; rename the user-defined material to a name that does not collide with any FLUKA built-in (e.g. `CUMAT` instead of `COPPER`, `SIMAT` instead of `SILICON`).
  - Update every reference to the renamed material (`ASSIGNMA`, `LAM-BIAS`, scoring cards, etc.) to the new name.
- Confidence: 0.90
- Logged: 2026-09-08
- Source:
  - AutoFLUKA curated run fix

### Empty scoring from reversed XYP half-space sign convention

- Detection hint:
  - The run completes successfully (return code 0), but `USRTRACK`/`USRYIELD`/other scorer responses are all exactly zero.
  - The energy balance shows essentially all primary beam energy escaping the system with no measurable dE/dx or nuclear interaction losses, even though the geometry visually looks correct.
- Signature:
  - `USRTRACK total response 0.000000` for every scorer bin; energy balance dominated by particles escaping with the full primary energy.
- Typical cause:
  - This is a **silent correctness failure, not a parser/runtime crash** — the run reports success. The sign convention for `XYP` plane half-spaces on the axial slab regions was used backwards, so the intended detector/degrader regions were empty or effectively displaced out of the beam path.
- Suggested Fix:
  - For a slab bounded by `z=a` and `z=b` defined via `XYP` planes `Za` and `Zb`, the region should be expressed as `-Za +Zb`, not `+Za -Zb`.
  - Update every surrounding black-hole/body region consistently with the corrected sign convention, then re-run a fresh low-statistics `test-n` attempt and confirm nonzero scorer responses before trusting a "success" return code.
  - Treat return-code-0 as necessary but not sufficient — always sanity-check that scorer output is nonzero and energy balance is physically plausible before proceeding to production.
- Confidence: 0.85
- Logged: 2026-09-08
- Source:
  - AutoFLUKA curated run fix

### USRYIELD LET scoring SIGFPE (floating-point exception)

- Detection hint:
  - Run aborts with a floating-point exception during transport, shortly after the first histories reach a scoring boundary, in a deck using `USRYIELD` with a LET (linear energy transfer) generalized quantity.
- Signature:
  - `Program received signal SIGFPE: Floating-point exception`
  - Backtrace through `dpdxio.f`, `getlet_`, `usrscy_`/`usrsco_` during `USRYIELD` LET boundary scoring.
- Typical cause — **three distinct causes confirmed across a single debugging session; check each in order:**
  1. **Neutral particles or a zero LET bin edge.** LET is a charged-particle stopping-power quantity. Selecting `ALL-PART` includes neutral particles with undefined LET, and a lower LET bin edge of exactly zero can trigger an invalid arithmetic path.
  2. **Global `EMF-OFF` combined with LET scoring.** A global `EMF-OFF` card can leave stopping-power/LET support unavailable or inconsistent for generalized LET scoring in some FLUKA builds, even after fixing cause 1.
  3. **Wrong material index in the LET continuation card.** The `USRYIELD` LET continuation WHAT(6) encodes `ixa + 100*ixm`, where `ixm` must be the material number FLUKA actually assigned in geometry — not the element's atomic number/charge. A deck using the atomic-number-like value (e.g. `26` for a material later assigned number `14`) produces the same SIGFPE.
- Suggested Fix:
  - Restrict the LET `USRYIELD` particle selector to charged particles (`ALL-CHAR`) and use a strictly positive lower LET bin edge, preserving the requested upper limit and charge-selection windows.
  - Remove any global `EMF-OFF` card; if the intent was to suppress EM secondary transport, use `DISCARD ELECTRON POSITRON PHOTON` instead, which does not disable LET support.
  - Verify the actual assigned material number from the FLUKA run echo (not the atomic number) and use it in WHAT(6) as `ixa + 100*ixm`, e.g. `1403` for plain double-differential yield (`ixa=3`) with LET in material 14.
  - Apply each fix in a fresh `test-n` deck and re-validate before moving to the next candidate cause.
- Confidence: 0.85
- Logged: 2026-09-08
- Source:
  - AutoFLUKA curated run fix

### Merged numeric/SDUM token on LAM-BIAS

- Detection hint:
  - Input validator reports a merged numeric/text token (missing separator) on a `LAM-BIAS` card, e.g. `1.INEALL`.
- Signature:
  - `Merged numeric/text tokens found (missing separator): 1.INEALL`
- Typical cause:
  - The fixed-column card writer placed the SDUM (e.g. `INEALL`) immediately after a full 10-character WHAT(6) field with no separating blank, which is ambiguous to both the validator and, in some cases, the FLUKA parser itself.
- Suggested Fix:
  - Force at least one blank separator before every SDUM label that follows a full WHAT field, on `LAM-BIAS` as on any other card.
  - As a project convention, prefer scorer/logical unit numbers of 30 or higher to avoid collisions with FLUKA's own reserved low unit numbers.
  - Regenerate the corrected input in a fresh `test-n` folder rather than patching in place.
- Confidence: 0.80
- Logged: 2026-09-08
- Source:
  - AutoFLUKA curated run fix

---

### FLUKA abort "NO INPUT FILE" caused by an oversized absolute path, not deck content

- Detection hint:
  - `rfluka` exits immediately (well under a second of real CPU time) with `Error: No ran<basename>002 generated!`, right after printing the version banner, with no further parsing progress.
  - `.out` log shows only the FLUKA banner followed directly by `Abort called from CMSPPR reason NO INPUT FILE Run stopped!`
- Signature:
  - `Error: No ran<basename>002 generated!`
  - `Abort called from CMSPPR reason NO INPUT FILE Run stopped!`
  - `STOP NO INPUT FILE`
- Typical cause:
  - The input deck's content is not the problem — this is a path-length overflow, not a parser error. FLUKA/`rfluka` has an internal fixed-size buffer (observed boundary: a working absolute path of 224 characters succeeded, an otherwise byte-identical deck at 257 characters failed, both in the same environment) for the full absolute path to the `.inp` file. When this WSL environment's execution path is resolved through Docker Desktop's bind-mount layer (`/mnt/wsl/docker-desktop-bind-mounts/Ubuntu/<container-hash>/...`), the fixed prefix alone can already run 150-200+ characters before the repo-relative path even starts — and that prefix length is **not stable**: it includes a container ID hash that can change across container restarts, so a folder/file name that fits today is not guaranteed to fit after an unrelated Docker restart.
  - Confirmed empirically: identical card content, run from a short scratch folder (`_t1/photon_....inp`, absolute path 224 chars) completed normally; the same content from a long, descriptive folder name (absolute path 257 chars) aborted instantly and reproducibly, across multiple retries, in both a fresh and a previously-used folder.
- Suggested Fix:
  - Keep new `working_examples/` (and other long-lived) case folder and file base names reasonably short — the folder name and `.inp` filename are typically identical by convention in this codebase, so a long descriptive name doubles its cost in the final path. Prefer a short, unambiguous name (e.g. `photon_1mev_lead_slab` over `photon_1mev_point_source_pencil_beam_on_lead_slab`) and put the descriptive detail in the case's `README.md` instead of the folder/file name.
  - If a run aborts this way immediately (no real CPU time elapsed) and the deck is otherwise known-good (e.g. verified working elsewhere, or passes when copied to a short scratch path), suspect path length before re-auditing the deck's cards.
  - Do not confuse this with a genuinely slow run: a real abort here happens in well under a second; a deck that's merely doing heavy physics (e.g. full hadronic cascades) will show real, accumulating CPU time in `ps aux` instead.
- Confidence: 0.85
- Logged: 2026-10-12
- Source:
  - Curated AutoFLUKA troubleshooting record — discovered while authoring and verifying a new working example

---

### USRTRACK/USRBDX silently empty despite a clean return code — four consolidated sub-causes

- Detection hint:
  - Run completes with return code 0, geometry/beam setup is plausible, but the `USRTRACK` or `USRBDX` scorer's reported quantity is implausibly low or exactly zero.
  - The `.out` prints the scorer's energy grid high-to-low, e.g. `linear energy binning from 1.0000E-03 to 1.0000E-12 GeV, 100 bins (-1.0000E-05 GeV wide)`, or a logarithmic grid with `ratio` below 1: Emax and Emin are swapped (sub-cause 2).
- Signature:
  - rc=0, no FLUKA-reported error, but the scorer's total response in `_tab.lis`/`_sum.lis` is zero or far below what the geometry and beam intensity would predict.
- Typical cause:
  - Four distinct, previously-scattered sub-causes all share the signature above:
  1. Continuation-card field order mistake: a value meant for the first line's WHAT field was written on the continuation line (or vice versa), so the scorer silently binds to the wrong quantity/region/energy range instead of failing outright.
  2. `Emin` > `Emax` inversion on the energy-binning continuation line. The continuation card holds Emax in WHAT(1) and Emin in WHAT(2); written low-to-high, FLUKA accepts it, prints the grid high-to-low in the `.out`, and the scorer stays exactly 0, behind a shield or in vacuum alike (verified with the installed FLUKA).
  3. A negative bin-count field intended to request log-spaced bins was malformed (e.g. a stray sign or an out-of-range magnitude) and silently fell back to FLUKA's own default of 10 bins instead of the intended count — not a crash, just a silently different (and sometimes effectively-empty) binning than authored.
  4. A missing continuation marker (the trailing `&`-style SDUM, or the repeated keyword on the second line, depending on card) caused the continuation line to be read as a brand-new, incomplete card instead of extending the first — the scorer is defined but its energy/angular range never gets set.
- Suggested Fix:
  - Because all four sub-causes share the same "rc=0, plausible setup, implausible/zero result" signature, don't assume the first thing you check is the actual cause — verify the continuation line's field order, `Emin < Emax`, the bin-count field's sign/magnitude, and the continuation marker, in that order, against a known-working sibling card before concluding the geometry or beam itself is at fault.
  - Compare the suspect card byte-for-byte against a verified working example of the same scorer type (e.g. `working_examples/`) rather than re-deriving the card format from the manual each time.
  - `fluka_inp_validator_tool` and the executor flag sub-cause 2 before a run, and the executor reads the energy grid in the `.out` after it. Changing only the value at the boundary (e.g. 0.001 to 0.0011 GeV) does not help while the two fields stay swapped.
- Confidence: 0.80
- Logged: 2026-10-12
- Source:
  - Curated AutoFLUKA troubleshooting record — consolidated from recurring run-fix notes across multiple unrelated case categories, previously never promoted to this KB

---

### FLUKA crash (SIGFPE in the USRTRACK/USRBDX scorer) from an empty energy range

- Detection hint:
  - The run stops with return code 136 after the primaries are transported, while the scorer results are written.
  - The job log shows a floating-point exception with `usrtrk` or `usrbdx` in the backtrace.
- Signature:
  - `Program received signal SIGFPE: Floating-point exception - erroneous arithmetic operation.`
  - `at score/usrtrk.f:908` (or the `usrbdx` equivalent)
  - `Error: "/usr/local/fluka/bin/fluka" executable returned RC=136`
- Typical cause:
  - The continuation card's energy range has no width. Either WHAT(1) (Emax) equals WHAT(2) (Emin), or Emax is blank or 0, which FLUKA replaces with the beam energy, while Emin is at or above the beam energy (for example Emin set to the beam energy itself).
  - A blank or 0 bin count is not the cause: FLUKA then uses its default of 10 bins.
- Suggested Fix:
  - Put the upper energy in WHAT(1) and the lower one in WHAT(2). For a scorer that must include unscattered primaries, set Emax a little above the beam energy (e.g. 1.1 times).
  - Write the card with `fluka_card_formatter_tool` and check the scorer field names it prints. `fluka_inp_validator_tool` and the executor flag this before the run.
- Confidence: 0.95
- Logged: 2026-10-21
- Source:
  - FLUKA probe runs with the installed FLUKA: USRTRACK and USRBDX with Emax equal to Emin, and Emax 0 with Emin equal to the beam energy, all stopped with SIGFPE; the same decks with Emax above Emin ran normally.
  - Curated AutoFLUKA troubleshooting record: a run-fix note had blamed a blank bin count for this crash.

---

### USRBDX double-counting from an oversized AIR margin around the target

- Detection hint:
  - A boundary-crossing scorer (`USRBDX`) between an ambient region and the target reports a response noticeably higher than the beam intensity alone would predict, with no corresponding error.
- Signature:
  - rc=0, plausible geometry and beam alignment, but `USRBDX` response exceeds the expected one-crossing-per-primary rate.
- Typical cause:
  - The ambient filler region between the target and the outer `BLCKHOLE` boundary was assigned `AIR` with a generously sized margin "to be safe." Backscattered and side-wall-leaking particles re-cross the same air/target boundary multiple times within that margin, and `USRBDX` counts every crossing — inflating the scored response well above the true primary-beam crossing rate.
- Suggested Fix:
  - This is not a "size the margin more carefully" problem — there is no safe margin size to compute, since a target can legitimately share a boundary with air with no buffer at all. Apply the standing rule instead: fill the space between target and outer boundary with `VACUUM` by default, and only use `AIR` when the case explicitly calls for it (skyshine, facility/room-return physics). See `fluka-authoring/rules/geometry_region_material_rules.md`, "Outer boundary and filler medium rule." Under vacuum, this double-counting mode doesn't arise at all.
- Confidence: 0.85
- Logged: 2026-10-12
- Source:
  - Curated AutoFLUKA troubleshooting record

---

### Intermittent failure on a structurally similar deck — suspect reformatting before the stated error

- Detection hint:
  - A deck fails intermittently across nominally-identical retries, or fails on one structurally similar case but not a sibling, with the originally-reported error mechanism (e.g. an angular/divergence threshold) not actually changing between the failing and passing attempts.
- Signature:
  - Two "fixes" that target different, unrelated causes both appear to resolve the same failure (e.g. a manual FLAIR resave succeeds, and a from-scratch agent regeneration of the same deck also succeeds, despite targeting different suspected mechanisms).
- Typical cause:
  - FLAIR silently reformats and repads fixed-column fields whenever a deck is opened and resaved through it. A from-scratch regeneration has the same side effect (clean, consistent column alignment) even when the agent believes it fixed something else entirely. The real, underlying cause in these cases was column misalignment reintroduced by earlier in-place editing — not whatever mechanism the error message or the agent's hypothesis pointed to.
- Suggested Fix:
  - Before trusting a stated error mechanism on an intermittent, structurally-similar-deck failure, diff the failing card(s) byte-for-byte against a known-good prior version to check for column drift, rather than first reaching for a physics- or threshold-level explanation.
  - When a FLAIR resave or full regeneration "fixes" a failure, treat that as weak evidence for column misalignment as the real cause, not confirmation of whatever the original hypothesis was.
- Confidence: 0.65
- Logged: 2026-10-12
- Source:
  - Curated AutoFLUKA troubleshooting record — a manual FLAIR resave and an independent from-scratch regeneration of the same deck both succeeded despite targeting different suspected causes

---

### USRBDX or USRTRACK result off by the detector area or volume (left at FLUKA's default 1.0)

- Detection hint:
  - The `.out` file reports `detector area:  1.0000E+00 cm**2` (USRBDX) or `detector volume:  1.0000E+00 cm**3` (USRTRACK) for a detector that is not 1 cm2 or 1 cm3.
  - A reported fluence differs from an analytic estimate by roughly the detector's area or volume (e.g. a factor of 4*pi*r^2 for a spherical boundary).
  - `fluka_inp_validator_tool` warns that USRBDX WHAT(6) or USRTRACK WHAT(5) is FLUKA's default 1.0.
- Signature:
  - `detector area:  1.0000E+00 cm**2`
  - `detector volume:  1.0000E+00 cm**3`
  - USRBDX WHAT(6) or USRTRACK WHAT(5) blank or 1.0 on a detector larger than 1 cm2 / 1 cm3.
- Typical cause:
  - FLUKA does not compute surface areas or region volumes. USRBDX WHAT(6) (area, cm2) and USRTRACK WHAT(5) (volume, cm3) default to 1.0, so the scored quantity is integrated over the detector rather than per cm2.
  - A failed attempt to write the area into the card was taken to mean "the area cannot be set in the card". The real cause of such failures is column alignment, not the approach.
- Suggested Fix:
  - Set the true area or volume in the card, written with `fluka_card_formatter_tool` so it ends at column 70 (USRBDX WHAT(6)) or column 60 (USRTRACK WHAT(5)). Typical values: sphere boundary 4*pi*r^2, plane a*b, RPP volume dx*dy*dz, RCC volume pi*r^2*h, spherical shell 4/3*pi*(r2^3 - r1^3).
  - Or keep the default and divide the result by the true area or volume afterward. State which one you did, and never do both.
  - Example (spherical boundary of radius 5 cm, area 4*pi*5^2 = 314.159 cm2):
    ```text
    *...+....1....+....2....+....3....+....4....+....5....+....6....+....7....+....8
    USRBDX          99.0    PHOTON     -31.0     regIN    regOUT   314.159OUTFLU
    USRBDX         0.002    1.0E-6     100.0                              &
    ```
- Confidence: 0.95
- Logged: 2026-10-18
- Source:
  - FLUKA manual: USRBDX WHAT(6) and USRTRACK WHAT(5), both "Default = 1.0"
  - Curated AutoFLUKA troubleshooting record: an agent abandoned setting the area in the card after column-alignment failures; a later run set it in the card without problems

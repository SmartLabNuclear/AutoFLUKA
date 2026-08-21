# FLUKA Error/Solution Pairs

### Geometry/beam axis convention mismatch
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
- Signature:
  - `STOP INVALID EMFCUT/PROD-CUT WHAT(3)`
  - `EMFCUT card, PROD-CUT, what(3), execution stopped`
- Typical cause:
  - `EMFCUT ... PROD-CUT` line has missing or zero `WHAT(3)`.
- Suggested Fix:
  - Set positive `WHAT(3)` on the PROD-CUT EMFCUT line and rerun the next low-statistics `test-n` attempt.
  - Example project convention:
    ```text
    EMFCUT    -1.0E-05   1.0E-05   1.0E-05                              PROD-CUT
    ```
- Confidence: 0.90
- Logged: 2026-03-09
- Source:
  - Curated AutoFLUKA troubleshooting record

### Re-run recursion or apparent infinite loop
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
- Signature:
  - WHAT field does not contain a valid formatted Fortran real number.
  - Alphanumeric region, material, or label token appears where FLUKA expects a numeric WHAT field.
  - `Invalid what(s)` appears for `USRTRACK`, `USRBDX`, `USRBIN`, or `RESNUCLEi`.
- Typical cause:
  - Fixed-column field spillover because labels, region names, or material names shifted into numeric fields.
  - Mixed free-format and fixed-format repair passes left cards in inconsistent layout.
- Suggested Fix:
  - Rewrite affected scorer lines using strict fixed-format discipline.
  - Keep WHAT fields numeric and labels in SDUM or in name-enabled fields from a validated template.
  - Use the mental model `A8, 2X, 6E10.*, A8` for classic fixed-format cards.
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
- Signature:
  - Run echo shows an unexpected number of primaries.
  - FLUKA fails to parse the `START` line after an edit.
  - A long numeric literal spills into the next fixed-format field.
- Typical cause:
  - `START` value exceeds expected field width or is misaligned for the active input style.
  - A `test-n` low-NPS value was accidentally propagated into production copies.
- Suggested Fix:
  - Use compact scientific notation and keep the line parser-safe.
  - Before seeded production runs, restore the intended production NPS after a `test-n` attempt succeeds.
  - Example:
    ```text
    START        1.0E+06
    ```
- Confidence: 0.84
- Logged: 2026-03-09
- Source:
  - Curated AutoFLUKA troubleshooting record

### Fixed-format BEAM field shift causing parse failure
- Signature:
  - BEAM card does not contain a valid formatted Fortran real number.
  - Merged field text appears, such as `.0 7000.0`.
  - Validator reports merged numeric/text token such as `0.0NEUTRON`.
- Typical cause:
  - Numeric and SDUM fields on the `BEAM` card are not aligned to fixed-width field boundaries.
  - A missing separator lets the particle name merge into a numeric WHAT field.
- Suggested Fix:
  - Rewrite the `BEAM` card in parser-safe fixed-width style.
  - Keep projectile name in SDUM and avoid glued numeric/text tokens.
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
- Signature:
  - `No/unknown default specified, run stopped`
  - `STOP  NO/UNKNOWN DEFAULT`
  - `**** No/unknown default specified, run stopped ****`
- Typical cause:
  - `DEFAULTS` SDUM is invalid, truncated, shifted into the wrong field, or not recognized by the installed FLUKA version.
  - Visually readable spacing was used, but the card was not parser-safe for fixed-format interpretation.
- Suggested Fix:
  - Check the exact `DEFAULTS` keyword accepted by the installed FLUKA version.
  - Rewrite the `DEFAULTS` card in parser-safe fixed-width style.
  - Do not web-search first; compare local examples/templates and local troubleshooting records before broader lookup.
  - Example parser-safe DEFAULTS cards:
    ```text
    DEFAULTS                                                              HADROTHE
    DEFAULTS                                                              PRECISIO
    ```
- Confidence: 0.93
- Logged: 2026-03-09
- Source:
  - Curated AutoFLUKA troubleshooting record
  - ADS-derived curated regression case

### Invalid DEFAULTS keyword with non-run directive contamination
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
    BEAMPOS       0.0       0.0     -25.0
    ```
- Confidence: 0.90
- Logged: 2026-03-09
- Source:
  - Curated AutoFLUKA troubleshooting record
  - ADS-derived curated regression case

### USRBDX solid-angle fields explicitly zeroed
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
    MATERIAL         19.    39.0983     0.862                              POTASSIU
    ```
- Confidence: 0.90
- Logged: 2026-04-29
- Source:
  - ADS-derived curated regression case

### Non-sequential user material number
- Signature:
  - `Input material CONCRETE number changed from 27 to 26`
  - `Input material <TOKEN> number changed from <N> to <M>`
  - `Abort called from MATCRD reason NON SEQUENTIAL MATERIAL NUMBER`
  - `NON SEQUENTIAL MATERIAL NUMBER`
- Typical cause:
  - A user `MATERIAL` card forced an explicit material number that did not match FLUKA's expected uninterrupted user-material numbering sequence.
  - The material definition may be physically correct, but the explicit number conflicts with FLUKA's internal/user material ordering.
- Suggested Fix:
  - Preserve the intended material or compound composition; do not delete or substitute the material just to make the run continue.
  - Remove or correct only the explicit material number from the affected user material and let FLUKA assign the next valid number.
  - Keep the corrected `MATERIAL`/`COMPOUND` definition stable before changing scoring cards.
  - Example corrected pattern:
    ```text
    MATERIAL                                                  CONCRETE
    ```
- Confidence: 0.95
- Logged: 2026-04-29
- Source:
  - ADS-derived curated regression case

### Duplicate primary source or beam card
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
- Signature:
  - `*** The 4th field ... MATERIAL        19.0      39.10      0.862                           POTASSIU ... does not contain a valid formatted fortran real number`
  - `The <N>th field ... MATERIAL ... does not contain a valid formatted fortran real number`
  - FLUKA rejects a numeric WHAT field after an inserted or repaired fixed-format card.
- Typical cause:
  - A repair inserted a card with misaligned 10-column numeric fields, leaving a blank or shifted numeric WHAT field where FLUKA expects a formatted real.
  - The visible card may look reasonable in a proportional editor, but the Fortran fixed-format reader sees an ambiguous field.
- Suggested Fix:
  - Rewrite the affected card with explicit fixed-width 10-character WHAT fields and real-valued numeric tokens where FLUKA expects reals.
  - Keep unused numeric fields as truly blank aligned columns before the SDUM/name field; do not collapse spacing around the SDUM.
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
- Signature:
  - `The 1th field 1000 of the START input card does not contain a valid formatted fortran real number`
  - `START          1000`
  - `*** The 2th field ... START        1000.         0 ... does not contain a valid formatted fortran real number`
  - `The 2th field ... START`
  - `START        1000.         0`
- Typical cause:
  - A generated low-NPS preflight cap was written as an integer (`START          1000`) instead of an explicit Fortran real.
  - A generated or repaired `START` card used an integer-like second field such as `0` where the installed FLUKA parser expected a formatted real value.
  - The test-run NPS cap was correct, but the START fields were not written with parser-safe real formatting.
- Suggested Fix:
  - Rewrite low-statistics preflight `START` with an explicit real-valued primary count, preferably scientific notation, while preserving the bounded `test-n` NPS limit.
  - Avoid adding unnecessary integer-like extra WHAT fields when only the primary count is being changed.
  - For production runs, restore the requested production NPS using the same real-valued fixed-width style.
  - Example:
    ```text
    START          1.0E3
    ```
- Confidence: 0.90
- Logged: 2026-04-30
- Source:
  - ADS-derived curated regression case

### Unresolved material or element token in FLUKA card
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
- Signature:
  - `RANDOMIZ          1.0         6.0 *** does not contain a valid formatted fortran real number`
  - `RANDOMIZ          1.         6. *** does not contain a valid formatted fortran real number`
  - `The 3th field ... of the following input card RANDOMIZ ... does not contain a valid formatted fortran real number`
  - `The 2th field ... of the following input card RANDOMIZ ... does not contain a valid formatted fortran real number`
- Typical cause:
  - Seeded-copy generation edited the `RANDOMIZ` line by token replacement instead of reconstructing the card in parser-safe fixed-format columns.
  - Digits or decimal points can land in the next fixed-format field, making the seed ambiguous or invalid for FLUKA formatted input.
- Suggested Fix:
  - Rewrite the entire `RANDOMIZ` line from scratch when changing seeds; do not patch the seed token in-place.
  - Keep WHAT fields aligned for fixed-format parsing and verify with the FLUKA echo before launching production statistics.
  - If a local FLUKA build is sensitive to seed width, prefer the exact known-good local pattern from the successful preflight run rather than a visually similar variant.
  - Observed successful pattern from the 100 nm SOURCE workflow:
    ```text
    RANDOMIZ          1.         6
    RANDOMIZ          1.         7
    RANDOMIZ          1.         8
    RANDOMIZ          1.         9
    RANDOMIZ          1.         10.
    ```
- Confidence: 0.90
- Logged: 2026-05-24
- Source:
  - AutoFLUKA curated run fix
  - AutoFLUKA curated run fix

### FLUKA user routine compile failure from FLAIR metadata contamination
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
  - AutoFLUKA curated run fix

### SOURCE routine auxiliary data file missing in staged run directory
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
  - AutoFLUKA curated run fix
  - AutoFLUKA curated run fix
  - AutoFLUKA curated run fix

### rfluka random sidecar not generated after seeded input failure
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
  - AutoFLUKA curated run fix

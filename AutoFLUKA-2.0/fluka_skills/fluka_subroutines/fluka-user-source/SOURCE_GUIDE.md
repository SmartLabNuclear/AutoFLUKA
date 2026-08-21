# FLUKA SOURCE user routine

`SOURCE` is the FLUKA user routine family for custom primary-particle generation. This guide is the canonical detailed guide for AutoFLUKA's `fluka-user-source` subroutine folder and is intended to be the style/master reference for future `<ROUTINE>_GUIDE.md` files.

This guide synthesizes the previous standalone SOURCE skill content into stable guide headings. It does not bundle or reproduce FLUKA-distributed Fortran template files.

## Purpose

Use `SOURCE` when the simulation needs a custom primary-particle generator rather than only standard FLUKA source-card behavior.

A SOURCE routine can define or sample, according to the user's physics prescription:

- primary particle type or ion identity,
- kinetic energy, momentum, or spectrum sampling,
- starting position and spatial distribution,
- direction cosines and angular distribution,
- source weight and normalization conventions,
- time or event-dependent source parameters,
- external phase-space replay or tabulated-source replay, when implemented by the user routine.

The routine participates at primary-history generation time. It is not a scoring routine and it is not an event-dump routine.

## When to use

Use `SOURCE` for cases such as:

- external or proprietary energy spectra,
- spatially extended sources,
- Gaussian, pencil, annular, isotropic, divergent, or correlated beams beyond what the standard deck conveniently expresses,
- correlated energy-angle or energy-position sampling,
- time-dependent source behavior,
- phase-space replay or source particles read from an external user file,
- laboratory-specific source models that must be version-controlled in Fortran or in auxiliary source tables,
- source models requiring `WHASOU`/`SDUSOU` parameters to switch modes without rewriting Fortran.

Prefer modifying an existing working SOURCE routine or a routine copied from the user's licensed FLUKA installation over generating a complex routine from scratch.

## When not to use

Do not use `SOURCE` for tasks better handled by other FLUKA mechanisms:

| User objective | Preferred mechanism |
|---|---|
| Boundary-crossing records, event dumps, phase-space output during transport | `MGDRAW` with the appropriate activation pattern, commonly `USERDUMP` |
| Fluence-like scoring response weighting | `FLUSCW` with `USERWEIG` activation |
| Energy-deposition, dose-like, or star-density-like scoring response weighting | `COMSCW` with `USERWEIG` activation |
| Medium/material-dependent transport intervention | `USRMED` through the appropriate material-property/user-directive activation |
| Lattice/repeated-geometry transformations | `LATTIC` with lattice geometry activation |
| Post-processing of FLUKA binary/unit outputs | FLUKA utilities such as `usbsuw`, `usbrea`, `detsuw`, etc.; these are not user subroutines |

Do not use `SOURCE` as a workaround for geometry, scoring, or transport-card errors. Fix those problems in the input deck unless the physics objective genuinely requires custom source sampling.

## Activation card or activation condition

A real `SOURCE` card in the FLUKA input deck activates the user-written `SUBROUTINE SOURCE` primary generator.

Important deck-level points:

- The `SOURCE` card enables the customized primary generator.
- `BEAM` still matters for defaults, bookkeeping, maximum expected energy consistency, and source/transport setup. Do not delete or ignore it just because a user source is present.
- `HI-PROPE` remains relevant for ion/heavy-ion source cases where applicable.
- `WHASOU(1)` through `WHASOU(18)` and `SDUSOU` are the conventional input-to-Fortran hooks associated with the `SOURCE` card. Use them to pass numeric parameters, flags, mode selectors, normalization values, filenames, or compact string selectors without embedding large tables directly in the `.inp` file.
- `SDUSOU` is limited by the FLUKA card/string convention; treat it as a compact selector or filename fragment, not as a general long-path mechanism.

## Input-card syntax and required deck checks

Before editing or compiling a SOURCE routine, AutoFLUKA should inspect the input deck for:

1. A real `SOURCE` card, not just a commented line or text in a title/comment.
2. A compatible `BEAM` card and, where relevant, `HI-PROPE` for ion settings.
3. `SOURCE` card `WHAT(i)` values that intentionally map to the user's Fortran logic through `WHASOU(i)`.
4. Any `SDUM`/`SDUSOU` use that must match a source mode, file selector, or compact flag in the Fortran routine.
5. Unit consistency between the input deck, the Fortran routine, and any auxiliary source tables.
6. Region/material geometry consistency for the sampled starting coordinates.
7. A `START` value suitable for the requested stage. For AutoFLUKA preflight runs, cap test attempts at low primaries according to the global `test-n` ladder.

Conceptual mapping:

```text
SOURCE card in .inp
    -> WHASOU(1)...WHASOU(18), SDUSOU available to Fortran source logic
    -> SUBROUTINE SOURCE is called to generate primaries
    -> BEAM / HI-PROPE and other deck cards still define important bookkeeping and physics context
```

For exact `SOURCE` card field meanings, always check the manual version corresponding to the installed FLUKA release.

## Required Fortran routine identity

The user routine file must define exactly one primary SOURCE routine for the executable:

```text
SUBROUTINE SOURCE
```

AutoFLUKA should treat the basename as non-authoritative. A file named `source_newgen.f`, `source.f`, `my_source_model.f`, or another user-chosen name can be valid if it actually defines `SUBROUTINE SOURCE` and compiles with the installed FLUKA environment.

Do not link two different Fortran files that both define `SUBROUTINE SOURCE` into the same executable. Use exactly one SOURCE implementation per run executable.

## Expected user-provided `.f` file checks

Before modifying or compiling a SOURCE `.f` file, check that:

- The file is plain Fortran source, not a FLAIR project/export wrapper.
- It contains one `SUBROUTINE SOURCE` implementation.
- It does not contain a second competing `SUBROUTINE SOURCE` in another linked file.
- It preserves the routine declaration and FLUKA-required include/common-block expectations for the user's installed FLUKA version.
- It was copied from the user's licensed FLUKA installation or created by the user, not redistributed as part of AutoFLUKA.
- The routine's source model is understandable enough to edit safely: variable names, spectra, file paths, region assumptions, and normalization choices should be documented or inferable.
- Any required auxiliary files are present beside the deck or in a documented relative location.
- If the routine uses `source_library.inc` or other compile-time helper includes, the installed FLUKA include path or local copy strategy is compatible with the user's build environment.

## Licensing-safe implementation policy

**AutoFLUKA does NOT ship** FLUKA-distributed SOURCE templates, the FLUKA manual, or other licensed installation materials. This guide contains original prose and pseudocode only.

Users should provide or copy `source_newgen.f`, `source.f`, or related files from their **licensed FLUKA installation**. Agents may inspect and edit user-provided `.f` files via tools.

Do not reproduce FLUKA template bodies in Markdown or chat. See `../SKILL.md`.

## Upstream placement in the official FLUKA installation

FLUKA installations commonly provide user-routine templates and examples under the installation tree. Exact layout varies by FLUKA release and operating system.

Common conceptual layout:

```text
FLUKA_ROOT/
  bin/              # fluka, fff, lfluka, rfluka, ...
  src/user/         # user-routine templates and helper includes
  examples/         # worked examples, including some SOURCE-oriented cases
  include/          # include files, depending on installation layout
  doc/              # local documentation, depending on installation layout
```

SOURCE-related starting points commonly include:

- `source_newgen.f`: a newer/modular SOURCE route, often using helper infrastructure such as `source_library.inc` and runtime-loaded spectra or tables. Treat APIs and helper paths as version-specific.
- `source.f`: the classic SOURCE example route, often using include files plus compiled-in `DATA` blocks for spectra/CDF arrays.

Guidance:

- Prefer `source_newgen.f` when the user's installed version supports it and the case benefits from modular helpers or external tables.
- Prefer `source.f` when the user has an existing classic source implementation or wants a simpler compiled-in-array workflow.
- Do not customize both as parallel primary generators for the same executable.
- Older customized SOURCE routines may remain valid after FLUKA upgrades, but should be compared against the newly shipped routine/template for the installed version.

### Finding bundled `.f` files on disk, high-level

If `$FLUPRO` is set, it often points to the FLUKA installation root or to a release-specific root used by FLUKA helper scripts.

If `$FLUPRO` is unset, one POSIX-style way to infer the installation root is:

```text
which fluka
# If this returns FLUKA_ROOT/bin/fluka, then FLUKA_ROOT is one level above bin.
```

Illustrative search sketch; adapt to the local installation:

```text
which fluka
cd "$(dirname "$(dirname "$(which fluka)")")"
find . -maxdepth 4 \( -name 'source.f' -o -name 'source_newgen.f' \) | head
cd ./src/user
ls *.f *.inc 2>/dev/null | head
```

This is only a discovery sketch. The installed FLUKA release and the user's site policies determine the canonical path.

## Mandatory setup before editing

Before AutoFLUKA or a human edits the source model:

1. Copy exactly one SOURCE implementation from the user's licensed FLUKA installation or select one user-authored SOURCE file.
2. Place the chosen `.f` file in the same case directory as the primary `.inp` file, unless the run system explicitly uses a documented alternative path.
3. Place required auxiliary source data files beside the deck or in documented relative paths.
4. Verify that the input deck contains the `SOURCE` card and compatible source/beam setup.
5. Pass the SOURCE `.f` explicitly through `subroutine_paths` whenever possible.

This setup avoids:

- ambiguous multiple SOURCE definitions,
- missing auxiliary files at runtime,
- FLAIR project files masquerading as Fortran,
- path inconsistencies between deck, Fortran, and executor,
- accidental reliance on stale parent-directory source files.

## Safe editing rules

Apply the SOURCE-specific sandwich rule:

1. Preserve the FLUKA-required routine shell, includes, common blocks, and stack/source interface required by the installed version.
2. Edit only user-declared variables, documented/labeled customization regions, sampling helper functions, and clearly owned source-model logic.
3. Do not regenerate the entire FLUKA-distributed routine structure from memory.
4. Keep units explicit in comments and variable names where practical.
5. Preserve the user's intended particle identity, spectrum, spatial distribution, angular distribution, weight convention, and normalization unless the user explicitly requests a change.
6. Do not silently move source starting positions onto region boundaries. Sampling exactly on boundaries is a common geometry-tracking failure mode.
7. Avoid uncontrolled per-primary file I/O or verbose logging.
8. Keep random sampling reproducible through FLUKA-compatible random-number practices used by the user's routine/template.
9. Keep external file formats documented: delimiter, columns, units, interpolation method, normalization, and ordering.
10. Confirm every deck-passed `WHASOU(i)`/`SDUSOU` value is used intentionally or documented as unused.

Safe automation targets:

- user-declared Fortran variables,
- user-owned sampling functions,
- labeled customizable regions in the user's copied routine,
- source-model constants,
- auxiliary `.dat`/`.txt` spectra and manifests,
- deck cards that activate and parameterize the source: `SOURCE`, `BEAM`, `HI-PROPE` where applicable.

Unsafe targets unless explicitly justified:

- FLUKA-required stack handling or routine boilerplate,
- include/common-block structure,
- random-number generator infrastructure,
- region/material definitions unrelated to the requested source change,
- physics cards unrelated to the requested source prescription.

## Code implementation sections

A well-maintained SOURCE routine should have clearly identifiable implementation sections. The exact section names are user-defined and version-specific, but AutoFLUKA should look for or create user-owned comments separating:

1. **User parameters**  
   Source mode, normalization, file names, spectrum table sizes, spatial parameters, angular parameters, particle identity, and unit conventions.

2. **Initialization / one-time setup**  
   Read external tables, normalize CDFs, validate file format, allocate or initialize arrays if the chosen source style supports it.

3. **Primary sampling**  
   Sample particle type, energy/momentum, position, direction cosines, time, and weight according to the user's prescription.

4. **Deck parameter ingestion**  
   Interpret `WHASOU(i)` values and `SDUSOU` selector(s) consistently with the input deck.

5. **Auxiliary file handling**  
   Open and read source tables safely. Fail early with clear messages if required files are missing or malformed.

6. **Diagnostics**  
   Optional limited output during initialization or for a bounded number of histories, never uncontrolled per-primary logging in production.

7. **Return / handoff to FLUKA**  
   Preserve the stack/source-particle handoff semantics required by the installed FLUKA SOURCE interface.

Illustrative pseudocode only, not FLUKA template code:

```fortran
! Example: use a SOURCE-card parameter as a user mode or normalization value.
! double precision :: user_norm
! user_norm = WHASOU(1)
```

```fortran
! Example: sample from user-owned arrays after they have been initialized.
! call sample_from_histogram(user_energy_grid, user_cdf, nbin, sampled_energy)
```

Replace pseudocode with conformant implementation inside the user's own/copy-authorized SOURCE routine.

## Auxiliary input files

SOURCE routines often require auxiliary files that are not part of the `.inp` deck:

- energy spectra,
- angular distributions,
- phase-space records,
- time structure tables,
- particle-type probability tables,
- normalization manifests,
- lab-specific source configuration files.

For every auxiliary file, document:

- filename and relative path,
- file role,
- delimiter and column definitions,
- units,
- whether probabilities are differential, integral, cumulative, or already normalized,
- interpolation method,
- ordering requirements,
- behavior for out-of-range values,
- checksum or version label when reproducibility matters.

`source_newgen.f` style workflows commonly favor runtime-loaded ASCII tables. Classic `source.f` style workflows commonly use compiled-in `DATA` arrays, although user-modified variants may do either. Verify against the user's installed FLUKA version and copied routine.

## Output files and output patterns

A SOURCE routine should normally produce little or no per-history output. Its main effect is to define primary particles for FLUKA transport.

Acceptable output patterns:

- one-time initialization summary,
- bounded diagnostic printout for a small number of histories,
- explicit error message if a required source file is missing or malformed,
- optional source-sampling audit file for debugging only, disabled or bounded for production.

Avoid:

- writing a line for every primary in production unless the user explicitly requests an audit and accepts the file-size cost,
- opening/closing files inside every primary call,
- writing to logical units that conflict with FLUKA output files,
- using absolute paths that will fail after AutoFLUKA copies the case to `test-n` or production folders.

If the user's real goal is event-by-event transport output, route to `MGDRAW`, not `SOURCE`.

## Compile/link behavior

SOURCE follows the same broad FLUKA user-routine build concept as other user routines:

```text
Fortran user routine(s) + FLUKA libraries -> custom FLUKA executable -> run input deck with that executable
```

For SOURCE:

- Compile exactly one Fortran file defining `SUBROUTINE SOURCE` for the executable.
- The filename is not semantically important; the declared routine is.
- Link the object into a custom FLUKA executable.
- Run the deck with the custom executable.
- Ensure helper include paths match the installed FLUKA release.
- Compile/link all required user routines together if the case legitimately uses multiple different routines, but avoid multiple definitions of the same routine.

Manual CLI sketch for one SOURCE routine; adapt paths and names to the installed FLUKA release:

```text
# Current directory contains MYINPUT.inp and source_newgen.f.
fff source_newgen.f
lfluka -o autofluka_user_routines source_newgen.o
rfluka -e ./autofluka_user_routines -M N MYINPUT.inp
```

Equivalent sketch when helper scripts are not on `PATH`:

```text
$FLUPRO/flutil/fff source_newgen.f
$FLUPRO/flutil/lfluka -o myfluka source_newgen.o
rfluka -e ./myfluka -M N MYINPUT.inp
```

Notes:

- Replace `source_newgen.f` with the actual selected Fortran file, such as `source.f` or a user-named source file.
- The object stem generally follows the Fortran basename.
- `N` is the usual `rfluka` parallelism/number-of-cycles convention used by the user's batch setup.
- Drop `-e` only when using the stock executable and no user routine is linked.
- If `fff` or `lfluka` are not on `PATH`, use full paths or executor configuration variables appropriate to the local AutoFLUKA deployment.

## AutoFLUKA execution behavior

For AutoFLUKA workflows:

- Prefer explicit `subroutine_paths` naming the SOURCE `.f` file.
- Use a narrow run scope: a single case folder or active `test-n` folder, not a broad parent directory.
- The executor recursively scans the given run root and prints `[PLAN]` lines; use those lines as the execution manifest rather than guessing.
- If `subroutine_paths` is omitted and the deck has a real `SOURCE` card, AutoFLUKA may auto-detect a SOURCE file only when exactly one `*.f` file defining `SUBROUTINE SOURCE` is found beside the input.
- Optional parent search for SOURCE auto-detection is controlled by `AUTOFLUKA_SOURCE_PARENT_SEARCH_LEVELS`; default behavior should avoid broad parent searching.
- Multiple SOURCE matches in the same directory are ambiguous and must not be auto-resolved.
- Other user routines such as `MGDRAW` are not covered by SOURCE auto-detection and should be supplied explicitly.
- Always perform the low-primary `test-n` ladder before production or seeded runs.
- After compile/link and run, verify artifacts; do not claim success based only on the absence of immediate console errors.

Recommended AutoFLUKA order:

1. Inspect the deck for a real `SOURCE` card.
2. Confirm the selected `.f` file defines `SUBROUTINE SOURCE`.
3. Confirm only one SOURCE implementation will be linked.
4. Confirm required auxiliary files are available to the run folder.
5. Compile/link through the executor using explicit `subroutine_paths` where possible.
6. Run a capped low-NPS `test-1` attempt.
7. If a bounded repair is needed, write the corrected deck into a fresh `test-2`, then `test-3`, etc.
8. Proceed to production only after a clean test attempt.

## Validation checklist

Before production, confirm:

- [ ] The input deck contains a real `SOURCE` card.
- [ ] `BEAM` and any ion-related setup remain consistent with the SOURCE routine.
- [ ] Exactly one linked Fortran file defines `SUBROUTINE SOURCE`.
- [ ] The `.f` file is clean Fortran, not a FLAIR export wrapper.
- [ ] The source file was copied from the user's licensed installation or authored by the user.
- [ ] No FLUKA-distributed `.f` template has been bundled into the skill pack.
- [ ] `WHASOU(i)` / `SDUSOU` usage is documented and matches the deck.
- [ ] Units are documented for energy, position, direction, time, and weight.
- [ ] Source starting positions are not sampled exactly on geometry boundaries unless intentionally and safely handled.
- [ ] Direction cosines are normalized and consistent with the intended beam/coordinate convention.
- [ ] Energy/momentum values are physically valid and within the expected maximum-energy envelope.
- [ ] Auxiliary files exist in locations copied into `test-n` and production folders.
- [ ] File I/O is bounded and does not conflict with FLUKA logical units.
- [ ] A low-NPS `test-n` run has compiled, linked, and produced expected FLUKA artifacts.
- [ ] No fatal signatures appear in relevant `.err`, `.log`, or bounded `.out` tails.

## Common errors and fixes

### FLAIR wrapper or metadata compiled as Fortran

- **Signature:** Compiler rejects lines such as `#flair`, unexpected labels, non-Fortran prologues, or project metadata.
- **Typical cause:** The selected `.f` is not a clean SOURCE routine; it is a FLAIR project/export wrapper or mixed file.
- **Suggested fix:** Trim to pure Fortran containing `SUBROUTINE SOURCE`, or recopy the routine from the installed FLUKA `src/user/` tree and reapply the user edits.

### Multiple SOURCE definitions

- **Signature:** Linker reports duplicate `SOURCE` symbols, or AutoFLUKA refuses ambiguous auto-detection.
- **Typical cause:** Both `source_newgen.f` and `source.f`, or another user-named file, define `SUBROUTINE SOURCE` in the same linked set.
- **Suggested fix:** Choose exactly one SOURCE implementation for the executable and pass it explicitly in `subroutine_paths`.

### Missing helper include or library file

- **Signature:** Compile failure referencing missing include files such as helper/source-library files.
- **Typical cause:** The build environment cannot find the installed FLUKA include/helper path, or a companion include expected by the copied routine is absent.
- **Suggested fix:** Ensure `$FLUPRO`/include paths match the installed FLUKA release, or copy only the required companion includes into the run folder if the local toolchain expects that.

### Missing auxiliary spectrum or phase-space file

- **Signature:** Runtime abort or source initialization error when opening a `.dat`, `.txt`, or phase-space file.
- **Typical cause:** Auxiliary files were not copied into the `test-n` folder or file names differ between deck, Fortran, and filesystem.
- **Suggested fix:** Use relative paths, copy auxiliary files with the case, and document filenames in the guide/case manifest.

### Source sampled on a region boundary

- **Signature:** Geometry tracking aborts, repeated boundary errors, or unstable transport immediately after primary generation.
- **Typical cause:** Source positions are sampled exactly on or numerically too close to a geometry boundary.
- **Suggested fix:** Move the source slightly inside the intended region, sample with a safe tolerance, and verify region assignment with a low-NPS run.

### Unit mismatch

- **Signature:** Particles have unexpectedly high/low range, source misses target, dose/fluence scale is implausible, or transport fails due to invalid energies.
- **Typical cause:** MeV/GeV, cm/mm, degree/radian, or momentum/kinetic-energy conventions are mixed between deck, Fortran, and auxiliary tables.
- **Suggested fix:** Document units at the top of the routine and in auxiliary-file headers; convert explicitly at ingestion.

### Unbounded diagnostic output

- **Signature:** Huge output files, slow run, filled disk, or excessive stdout/log output.
- **Typical cause:** Debug prints inside the per-primary SOURCE call or repeated file open/close operations.
- **Suggested fix:** Restrict diagnostics to initialization or a bounded number of histories and disable verbose output for production.

## Version drift

After a FLUKA upgrade:

- Compare the user's customized SOURCE file against the newly shipped `src/user/` version for the same route.
- Apply differences surgically rather than overwriting the user's physics logic.
- Expect `source_newgen.f` and helper-library behavior to change more than classic compiled-array styles.
- Reconfirm include paths, helper APIs, and any initialization routines against the installed release.
- Re-run the low-NPS `test-n` validation ladder after migration.

## Related examples

Routine-specific examples should live under this folder's `examples/` directory. Current example:

- `examples/SOURCE_CARD_ACTIVATION.md` — minimal conceptual activation and deck linkage pattern for `SOURCE`.

Future useful examples:

- `examples/SOURCE_SPECTRUM_SAMPLING.md`
- `examples/SOURCE_PHASE_SPACE_INPUT.md`
- `examples/SOURCE_EXTERNAL_TABLE_FORMAT.md`
- `examples/SOURCE_COMMON_ERRORS.md`

Examples should be Markdown explanations and original pseudocode/patterns, not copied FLUKA-distributed Fortran template files.

## Manual references

**Agent citation format:** `FLUKA Manual (2024 PDF edition), FLUKA Collaboration, Sec. …, p. …, manuals page https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals` — do not cite local parse filenames. See `../SKILL.md`.

- **Manuals page:** https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals
- **2024 PDF:** https://www.fluka.eu/Fluka/www/html/content/manuals/FM.pdf
- **This routine (2024 PDF edition):** `SOURCE` Sec. 7.66; see parent `fluka_subroutines/SKILL.md` for full routing table

Verify exact routine interfaces, card syntax, and `WHAT(i)` meanings against the manual for the **installed FLUKA version**. Newer releases may differ from the 2024 PDF edition used to draft this guide.

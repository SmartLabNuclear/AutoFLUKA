---
name: FLUKA User Subroutines
description: Router and policy skill for FLUKA Fortran user routines. Use this skill to distinguish user subroutines from FLUKA post-processing utilities, select the correct routine guide, map routines to activation cards or activation conditions, and apply AutoFLUKA distribution and manual-citation policy without shipping licensed FLUKA materials.
---

# FLUKA User Subroutines

This bundled AutoFLUKA skill is the main router for FLUKA Fortran user-routine workflows.

Use this skill when a user asks AutoFLUKA to create, inspect, modify, compile, link, or run a FLUKA case involving a user routine such as `SOURCE`, `MGDRAW`, `FLUSCW`, `COMSCW`, `USRMED`, `LATTIC`, `UBSSET`, `USRINI`, `USROUT`, or `USRGLO`.

This skill pack contains **original Markdown guidance only**. **AutoFLUKA does NOT ship** FLUKA-distributed `.f` templates, the FLUKA manual, or other licensed installation materials. Routine-specific guides explain how to work with **user-provided** Fortran files and how to activate each routine from the input deck. Citation and distribution rules are in **FLUKA manual references, citation format, and version policy** below.

---

## Required branching rule

When a request involves a FLUKA user subroutine:

1. Identify the intended routine from the routing and activation tables below.
2. Read the matching `<ROUTINE>_GUIDE.md` in the relevant `fluka-user-<routine>/` folder.
3. If the request asks for a specific implementation pattern, read the relevant Markdown file under that routine's `examples/` folder.
4. Do **not** assume `SOURCE` syntax applies to other user routines.
5. Do **not** copy, reproduce, or bundle FLUKA-distributed user-routine template files.
6. Prefer modifying user-provided `.f` files over generating new routines from scratch.
7. If generating new code, generate only original minimal scaffolds and pseudocode-derived implementation sections consistent with the manual and the routine-specific guide.
8. For execution, pass all required user Fortran files explicitly to the FLUKA execution workflow whenever possible.

---

## Folder structure

The expected structure of this skill family is:

```text
fluka_subroutines/
├── SKILL.md
├── fluka-user-source/
│   ├── SOURCE_GUIDE.md
│   └── examples/
├── fluka-user-mgdraw/
│   ├── MGDRAW_GUIDE.md
│   └── examples/
├── fluka-user-fluscw/
│   ├── FLUSCW_GUIDE.md
│   └── examples/
├── fluka-user-comscw/
│   ├── COMSCW_GUIDE.md
│   └── examples/
├── fluka-user-usrmed/
│   ├── USRMED_GUIDE.md
│   └── examples/
├── fluka-user-lattic/
│   ├── LATTIC_GUIDE.md
│   └── examples/
├── fluka-user-ubsset/
│   ├── UBSSET_GUIDE.md
│   └── examples/
└── fluka-user-usrcall/
    ├── USRCALL_GUIDE.md
    └── examples/
```

Subroutine subfolders do not require their own `SKILL.md` files. This top-level `SKILL.md` is the discoverable entry point and must remain explicit enough for the agent to route into the correct guide file.

---

## User subroutines versus FLUKA utilities

FLUKA user subroutines and FLUKA utilities are different workflow objects.

### FLUKA user subroutines

User subroutines are Fortran hooks compiled and linked into a custom FLUKA executable. They participate during source generation, tracking, scoring, geometry transformations, biasing, or selected transport decisions.

Examples include:

- `SOURCE`
- `MGDRAW`
- `FLUSCW`
- `COMSCW`
- `USRMED`
- `LATTIC`
- `UBSSET`
- `USRINI`
- `USROUT`
- `USRGLO`

A user subroutine can affect the simulation itself or can create additional event-level output during transport.

### FLUKA utilities

FLUKA utilities are standalone or auxiliary post-processing programs used after a run to process output files. They are not user subroutines and are not compiled into the user executable as transport hooks.

Examples include utilities such as:

- `usbsuw`
- `usbrea`
- `detsuw`
- other FLUKA output-processing helpers used to convert binary scoring data into readable/tabulated output

### Core distinction

| Object type | When used | Effect | Typical AutoFLUKA handling |
|---|---|---|---|
| User subroutine | Before and during the FLUKA run | Can alter source generation, scoring weights, tracking output, geometry transforms, biasing, or selected transport behavior | Compile/link with FLUKA executable, then run input deck with the custom executable |
| FLUKA utility | After the FLUKA run | Processes FLUKA outputs into readable or analysis-ready files | Run during decryption/post-processing, then verify `_tab.lis`, `_sum.lis`, or related artifacts |

Do not route FLUKA utility questions to a user-subroutine guide unless the user is explicitly asking about both execution-time hooks and post-processing.

---

## General compile/link policy for user routines

Most FLUKA user routines share the same broad build concept:

```text
user Fortran routine(s) + FLUKA libraries → custom FLUKA executable → run input deck with that executable
```

However, the following are routine-specific and must be handled by the matching guide:

- Fortran routine signature and entry points
- Required includes or common blocks
- Activation card or activation condition
- Safe editable sections
- Output-file policy
- Scoring or transport interpretation
- Validation checks

### AutoFLUKA execution policy

1. Prefer explicit `subroutine_paths` when executing FLUKA cases with user Fortran routines.
2. If multiple `.f` files are present, do not guess which ones to link unless routine declarations are unambiguous.
3. For `SOURCE`, AutoFLUKA may auto-detect a single nearby Fortran file defining `SUBROUTINE SOURCE`, but explicit paths remain preferred.
4. Other user routines, such as `MGDRAW`, `FLUSCW`, `COMSCW`, `USRMED`, `LATTIC`, and additional hooks, should normally be passed explicitly.
5. If multiple routines are required, compile/link them together into the same user executable.
6. Before production execution, run the deterministic low-primary `test-n` ladder and troubleshoot the active failed attempt first.
7. Do not claim compile/link success unless execution artifacts support that claim.

### AutoFLUKA distribution and licensed-material policy

**AutoFLUKA does NOT ship:**

- FLUKA-distributed Fortran user-routine templates (`.f` files)
- The FLUKA manual (PDF, HTML, or parsed knowledge-base exports)
- FLUKA libraries, binaries, include trees, or other licensed installation content

This pack is **original Markdown guidance only** — prose, routing tables, pseudocode, and worked examples.

Users are advised to provide, from their licensed installation or case workspace:

- The `.f` file(s) to compile and link
- Any required includes or auxiliary data files
- The FLUKA manual edition matching their install (or a configured manual knowledge base) when exact card syntax or section evidence is needed
- Runnable input decks and explicit `subroutine_paths` when executing

Agents may read user-provided files via tools; AutoFLUKA does not bundle substitutes.

Allowed:

- Explain routine purpose and manual-supported activation syntax.
- Inspect and modify a **user-provided** `.f` file.
- Generate original minimal scaffolding where technically appropriate.
- Provide pseudocode and Markdown examples.

Not allowed:

- Claim AutoFLUKA bundles `source.f`, `mgdraw.f`, or other FLUKA templates.
- Reproduce large FLUKA template bodies in Markdown or chat.
- Remove FLUKA license context from user-provided files.

---

## Routine routing table

| User objective | Likely routine | Read guide |
|---|---|---|
| Define custom primary particles, distributions, or phase-space source sampling | `SOURCE` | `fluka-user-source/SOURCE_GUIDE.md` |
| Record event-level, track-level, boundary-crossing, collision, or phase-space output | `MGDRAW` | `fluka-user-mgdraw/MGDRAW_GUIDE.md` |
| Apply user weighting to fluence-like scoring contributions | `FLUSCW` | `fluka-user-fluscw/FLUSCW_GUIDE.md` |
| Apply user weighting to energy-deposition, dose-like, or star-density-like contributions | `COMSCW` | `fluka-user-comscw/COMSCW_GUIDE.md` |
| Apply user-defined medium/material transport directives | `USRMED` | `fluka-user-usrmed/USRMED_GUIDE.md` |
| Implement repeated-geometry/lattice transformations | `LATTIC` | `fluka-user-lattic/LATTIC_GUIDE.md` |
| Customize user biasing setup/control logic | `UBSSET` | `fluka-user-ubsset/UBSSET_GUIDE.md` |
| Add user initialization, output/finalization, or global-call hooks | `USRINI`, `USROUT`, `USRGLO` | `fluka-user-usrcall/USRCALL_GUIDE.md` |

---

## Routine to activation-card / activation-condition map

This table is a routing aid. Always verify detailed syntax against the routine-specific guide and the official FLUKA manual for the installed FLUKA version.

| Routine | Main purpose | Activation card or condition | Routing note |
|---|---|---|---|
| `SOURCE` | Custom primary-particle source | `SOURCE` card | The input deck uses the `SOURCE` card to request sampling through the user `SOURCE` routine. A `BEAM` card is generally still used to define beam/particle defaults and maximum expected energy context. |
| `MGDRAW` | General event interface for event/track/boundary/collision/custom dump output | `USERDUMP`; manual states activation of the collision tape/event interface depends on `USERDUMP` settings, commonly with `WHAT(1)` selecting dump behavior | Route to `MGDRAW_GUIDE.md`; do not use it to define primary particles. |
| `FLUSCW` | User weighting for fluence-like scoring | `USERWEIG`; `WHAT(3)` controls calls to `FLUSCW` | Route to `FLUSCW_GUIDE.md`; distinguish fluence response weighting from energy-deposition weighting. |
| `COMSCW` | User weighting for energy deposition, dose-like, star-density-like, or residual-dose-like scoring contributions | `USERWEIG`; `WHAT(6)` controls calls to `COMSCW` | Route to `COMSCW_GUIDE.md`; avoid double-counting response factors. |
| `USRMED` | User medium-dependent transport directives | `MAT-PROP` with `SDUM = USERDIRE` / `USERDIREctive` | Route to `USRMED_GUIDE.md`; this can affect transport behavior and requires careful physics validation. |
| `LATTIC` | Lattice/repeated-geometry transformations | `LATTICE` geometry card(s) | Route to `LATTIC_GUIDE.md`; verify transform direction and replicated-cell geometry. |
| `UBSSET` | User biasing setup/control | No single dedicated activation card; FLUKA calls `UBSSET` after input processing and before calculation for regions/biasing options. Biasing-related input must still be consistent with the intended variance-reduction setup. | Route to `UBSSET_GUIDE.md`; validate weight preservation and compare against reference/analog cases where feasible. |
| `USRINI` | User initialization call | `USRICALL` | Route to `USRCALL_GUIDE.md`. |
| `USROUT` | User output/finalization call | `USROCALL` | Route to `USRCALL_GUIDE.md`. |
| `USRGLO` | User global call/control hook | `USRGCALL` | Route to `USRCALL_GUIDE.md`. |

---

## Routine-specific guide expectations

Each `<ROUTINE>_GUIDE.md` should include:
```markdown
# FLUKA <ROUTINE> user routine

## Purpose
## When to use
## When not to use
## Activation card or activation condition
## Input-card syntax and required deck checks
## Required Fortran routine identity
## Expected user-provided `.f` file checks
## Licensing-safe implementation policy
## Upstream placement in the official FLUKA installation
## Mandatory setup before editing
## Safe editing rules
## Code implementation sections
## Auxiliary input files
## Output files and output patterns
## Compile/link behavior
## AutoFLUKA execution behavior
## Validation checklist
## Common errors and fixes
## Version drift
## Related examples
## Manual references
```

This is the **canonical 21-section schema** (plus title) for every `*_GUIDE.md`. It matches `SESSION_HANDOFF.md` § Stable master guide structure.

**`## Manual references`** must follow the citation format in **FLUKA manual references, citation format, and version policy** later in this file.

**Optional routine-specific sections** (when useful, e.g. MGDRAW):

- `## Routine-interface summary without code redistribution`
- `## Entry-point editable-section map`
- `## Activation examples`

Do not add publication-facing sections that reference private local study paths or quote FLUKA template bodies.

Example-specific files should remain under the relevant `examples/` directory and should use `.md` filenames, for example:

```text
fluka-user-mgdraw/examples/MGDRAW_USERDUMP_ACTIVATION.md
fluka-user-mgdraw/examples/MGDRAW_BOUNDARY_CROSSING_OUTPUT.md
fluka-user-fluscw/examples/FLUSCW_USERWEIG_ACTIVATION.md
fluka-user-fluscw/examples/FLUSCW_USRTRACK_DOSE_EQUIVALENT_CASE.md
fluka-user-comscw/examples/COMSCW_USERWEIG_ACTIVATION.md
fluka-user-comscw/examples/COMSCW_USRBIN_DOSE_GY_CASE.md
fluka-user-usrmed/examples/USRMED_MATPROP_USERDIRE.md
fluka-user-usrmed/examples/USRMED_OPTICAL_ABSORPTION_CASE.md
fluka-user-ubsset/examples/UBSSET_IMPORTANCE_LADDER_CASE.md
fluka-user-ubsset/examples/UBSSET_BIASSING_DECK_SETUP.md
fluka-user-usrcall/examples/USRCALL_SOURCE_SPECTRUM_INIT_CASE.md
fluka-user-usrcall/examples/USROCALL_POSTSTART_SUMMARY_CASE.md
```

## Safety and validation checklist

Before AutoFLUKA edits, compiles, links, or executes a user-routine case:

1. Confirm which routine is needed.
2. Confirm the input deck contains the required activation card or activation condition.
3. Confirm the `.f` file defines the expected routine name when a user file is supplied.
4. Confirm required auxiliary files are present.
5. Avoid copying FLUKA-distributed templates.
6. Preserve user physics intent.
7. Compile/link all required user routines together.
8. Run a low-primary `test-n` attempt before production.
9. If a compile/runtime failure occurs, troubleshoot the active `test-n` folder and log bounded fixes.
10. Only decrypt, structure, plot, or report results after artifact-based execution evidence exists.


## FLUKA manual references, citation format, and version policy

### Manual edition for this skill pack

Routine guides were drafted against the **2024 FLUKA Manual PDF edition** from the official [FLUKA manuals page](https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals):

- **Manuals page (authority for releases):** https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals
- **2024 PDF used for this pack:** https://www.fluka.eu/Fluka/www/html/content/manuals/FM.pdf
- **Online manual (may differ in section numbering):** https://flukafiles.web.cern.ch/manual/index.html

Newer releases (for example FLUKA 2025.x) may change section numbers, wording, and defaults. Users must verify against the manual matching their **installed FLUKA version**.

### How agents must cite the manual in answers

When citing manual evidence in user-facing responses, use the official edition wording.

**Required form:**

```text
FLUKA Manual (2024 PDF edition), FLUKA Collaboration, Sec. <section>, p. <page>, manuals page https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals
```

**Example:**

```text
FLUKA Manual (2024 PDF edition), FLUKA Collaboration, Sec. 7.83, p. 269; Sec. 13.2.14, p. 409, manuals page https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals
```

**Do not cite in user-facing answers:**

- Local parse filenames (for example `fluka_manual_fom_fluka_org.pdf`) — developer ingest labels only, not the official manual title
- Internal knowledge-base document IDs
- Absolute paths to a user's parsed manual tree

**When the user's manual edition differs from 2024:** state that explicitly. Prefer the user's edition for exact `WHAT(i)` behavior and section numbers, while noting this skill pack was synthesized from the 2024 PDF edition above.

### Version policy

- Verify exact card syntax, `WHAT(i)` meanings, and section numbers against the manual for the **installed FLUKA version**.
- Newer releases on the [manuals page](https://www.fluka.eu/Fluka/www/html/fluka.php?id=manuals) may reorganize content relative to the 2024 PDF used here.

### Sections consulted when drafting this router (2024 PDF edition)

`SOURCE` Sec. 7.66; `USERDUMP` Sec. 7.83 and `MGDRAW` Sec. 13.2.14; `USERWEIG` Sec. 7.84 with `FLUSCW` / `COMSCW`; `MAT-PROP` Sec. 7.44 with `USRMED`; `LATTICE` Sec. 8.2.10 with `LATTIC`; `UBSSET` Sec. 13.2.22; `USRICALL`, `USROCALL`, and `USRGCALL` Secs. 7.88–7.90.
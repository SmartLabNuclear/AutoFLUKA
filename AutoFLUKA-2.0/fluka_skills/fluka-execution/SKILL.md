---
name: FLUKA Execution
description: Execute, validate, decrypt, and verify FLUKA runs using artifact-based evidence, low-NPS preflight attempts, and troubleshooting handoff.
---

# fluka-execution

Execute, validate, decrypt, and verify FLUKA runs without breaking the authoring workflow.

## Scope
- Decide what should be run.
- Verify success from artifacts, not assumptions.
- Run isolated low-NPS `test-n` attempts before seeded or production execution.
- Hand validation/runtime failures to `../fluka-troubleshooting/` before broad reasoning or web search.

## Inputs
- Runnable `.inp` files in the user-selected working directory or requested results subdirectory.

## Outputs
- Verified run artifacts (`*.out`, `*_fort.*`)
- Decrypted `_tab.lis` and `_sum.lis` files
- One root `autofluka_run_fixes.md` trail for `test-n` attempts and fixes

## Shared knowledge
- Runtime and validation failure patterns live under `../fluka-troubleshooting/Error_Resolution_KB.md`.
- Shared workflow guide lives in `../SKILL.md` (global workflow contract).

## Responsibilities
- Reuse shared workflow guidance from the global `../SKILL.md`.
- Keep execution focused on selecting runnable inputs, creating/running `test-n` attempts, running production jobs, and verifying artifacts.
- Reusable validation/runtime failure signatures live under `../fluka-troubleshooting/Error_Resolution_KB.md`, searched by TF-IDF cosine + fuzzy matching across `Detection hint`, `Signature`, and title fields.

## Simple run-and-fix requests
- A user request such as "run this FLUKA input and correct any errors" is an execution/troubleshooting workflow.
- Invoke `fluka_executor_tool` for this workflow; do not manually emulate execution with `PythonREPLTool`.
- **`output_dir` contract:** Pass the absolute path of the folder that contains (or cleanly scopes by subtree) **only** the runnable `.inp` files for this request—normally the case folder or the active `test-n` folder. The executor **recursively** scans roots and prints **`[PLAN]`** lines listing every batch directory; avoid user home directories or whole-drive paths unless batching many cases is deliberate.
- Let `fluka_executor_tool` handle FLUKA user routines. If a deck has a real `SOURCE` card, the executor can compile/link whichever `.f` you pass in `subroutine_paths`, or **auto-detect** a **single** Fortran file that defines `SUBROUTINE SOURCE` beside the input (basename-agnostic); optional ancestor search uses env `AUTOFLUKA_SOURCE_PARENT_SEARCH_LEVELS`. Prefer explicit `subroutine_paths` whenever there could be ambiguity.
- Detailed SOURCE and other user-routine workflow lives in **`../fluka_subroutines/SKILL.md`** and the matching routine guide under `../fluka_subroutines/fluka-user-*/`. Ensure the bundled **Subroutines** skill module is enabled (or rely on fallback + Alerts).
- Do not use web search, file downloading, or PDF processing for run-error repair unless the user explicitly asks for online/PDF research.
- If the run fails, use the local Error_Resolution_KB troubleshooting path and then consult local `.md` skill rules plus `.inp` working examples/templates before changing cards.

## Phase 1 — Test-run sequence (validation)

- First run request: create `test-1/`, copy the original input, and cap `START`/NPS at `<=1000`.
- Write capped `START` values as explicit real literals, never integers; prefer `START          1.0E3` for the standard low-statistics preflight cap.
- Each bounded repair must be run in a fresh `test-2/`, `test-3/`, etc.
- Keep FLUKA-generated files inside their own `test-n` folder.
- Log the run/fix trail in one root `autofluka_run_fixes.md` file.
- **Phase 1 exit condition**: one `test-N` completes successfully (return code 0, valid `.out` file, plausible energy deposition in the intended region). That input is the validated canonical deck. Advance to Phase 2. Do not restart Phase 1 unless the user explicitly asks for a new preflight.

## Phase 2 — Production (seeded, full NPS)

This phase is entered **only** after a clean Phase 1 `test-N`. It is a **one-way transition** — the test ladder does not restart here.

### What production means
- Create a single `production-1/` folder.
- Populate it with N seeded copies of the validated canonical input: only the RANDOMIZE seed changes per copy; all other cards (including `START` at full user-requested NPS) remain identical.
- Run all N copies in **one** executor call. Do not run them one at a time.

### Hard rules for production
- **No test-N inside production-N.** Never create `test-1/`, `test-2/`, etc. inside a production folder.
- **No NPS cap.** Never reduce `START` in a production run. Full NPS always.
- **No re-validation.** The canonical deck is already validated. Do not run a single-copy preflight inside production.
- **Anti-loop rule.** If `production-N/` already exists with any run artifacts (`.log`, `.out`, `.err`, rng files), do NOT create `production-(N+1)/` automatically. Inspect the existing artifacts and report status to the user. Only create a new production folder when the user explicitly requests it.
- **Wait rule.** If a production run is launched, wait for all N copies to finish before starting post-processing. Do not re-launch while the run is active or the status is ambiguous — report the ambiguity instead.

### Post-production (runs once, not in a loop)
After all N copies finish: decrypt outputs → extract JSON → plot. This sequence runs once per production attempt and stops.

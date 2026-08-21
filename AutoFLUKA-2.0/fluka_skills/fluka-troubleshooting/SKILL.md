---
name: FLUKA Troubleshooting
description: Diagnose FLUKA validation, echo, compile, and runtime failures with local-first evidence, bounded fixes, and deterministic retry rules.
---

# fluka-troubleshooting

Run-readiness and failure-recovery guidance for AutoFLUKA.

## Files
- `SKILL.md`: policy for validation/runtime diagnosis, evidence priority, `test-n` execution, and retry limits.
- `Error_Resolution_KB.md`: unified knowledge base used by the deterministic resolver. Each entry includes a `Detection hint` field for fast matching, `Signature`, `Typical cause`, `Suggested Fix`, `Confidence`, `Logged`, and `Source`.

## Use
- Use this lane when validation fails, FLUKA execution aborts, echo files contain parser/runtime errors, or downstream decryption/post-processing is blocked by a failed run.
- Prefer local records and working examples before local manuals, and use broader external searching only after local evidence is exhausted.

## Scope
- Diagnose validation failures, echo/input failures, and runtime failures before broad reasoning or web search.
- Treat validation and runtime failures as the same troubleshooting workflow when they share the same root cause.
- Use deterministic evidence extraction and local error/solution records before asking the agent to improvise a fix.

## User SOURCE / Fortran compile errors
- Fatal compile errors on **`source_newgen.f`**, **`source.f`**, or mixed **FLAIR** metadata in Fortran are often orthogonal to `.inp` card fixes. Prefer **`../fluka_subroutines/SKILL.md`** and the matching routine guide (enable the **Subroutines** bundled module).

## Local-first priority order
1. Local troubleshooting records in `Error_Resolution_KB.md` — searched with TF-IDF cosine + fuzzy matching across `Detection hint`, `Signature`, and title.
2. Local `.md` guidance in authoring rules and troubleshooting skills.
3. Local `.inp` working examples and templates for concrete card-format patterns.
4. Optional local FLUKA manuals and lecture-note knowledge base, if the user provided it.
5. Broader external search only if local sources do not resolve the issue or the user explicitly asks.

## Evidence priority
Prefer FLUKA-generated evidence over AutoFLUKA launcher logs:

1. `*-echo*.err`
2. `*-echo*.log`
3. `*-echo*.out` tail only
4. non-echo `*.err`
5. non-echo `*.log`
6. non-echo `*.out` tail only

Ignore `AutoFLUKA_job*.log` by default unless diagnosing launcher/tool failure. These files often contain wrapper status rather than the FLUKA parser/runtime signature.

## Test-run rule
- Before seeded or production execution, run a copied `.inp` in `test-1/` with low primaries (`START`/NPS must be `<=1000`).
- Low-primary `START` edits must use explicit real formatting, not integers; use forms such as `START          1.0E3`.
- If `test-1` fails and one bounded fix is applied, place the corrected input in a fresh `test-2/`; continue as `test-3/`, etc.
- Diagnose only the active `test-n` folder unless the user explicitly asks to compare old attempts.
- Only after a clean `test-n` attempt should AutoFLUKA generate seeded copies and run the requested production batch.

## Retry policy
- Apply at most one targeted fix per unique fatal signature.
- If the same signature repeats, stop automatic retries and ask the user for direction.
- Do not proceed to decryption, JSON extraction, plotting, or reporting while a fatal execution signature is unresolved.
- Preserve physics intent: do not remove custom materials, compounds, scorers, source definitions, or requested physics cards unless the user explicitly approves the simplification.
- Record the progress in one root `autofluka_run_fixes.md` file rather than scattered per-attempt diagnosis files.

## Record policy
- `Error_Resolution_KB.md` is the single authoritative troubleshooting knowledge base.
- Each record must start with `### <Title>` and use exact field labels in this order:
  - `Detection hint` — observable clue(s) that appear before or during the error; used for fast pre-scan matching.
  - `Signature` — verbatim or near-verbatim FLUKA output lines.
  - `Typical cause`
  - `Suggested Fix`
  - `Confidence`
  - `Logged`
  - `Source`
- Small fenced `text` examples are allowed inside `Suggested Fix` when a corrected FLUKA card is useful.
- Keep full input decks, private paths, and license-restricted manual excerpts out of the records.
- Run `python maintenance_scripts/validate_kb.py` after adding or editing entries.

---
name: FLUKA Post-Processing
description: Analyze verified FLUKA outputs into structured artifacts, plots, derived data products, and report-ready summaries.
---

# fluka-post-processing

Use verified FLUKA outputs to build structured analysis products without changing the upstream authoring or execution workflow.

## Scope
- Parse `_tab.lis`, `_sum.lis`, and JSON outputs.
- Apply detector- or scorer-specific analysis recipes.
- Generate derived CSV, JSON, and plot artifacts.
- Generate minimal reproducible technical reports in Markdown when the user asks for a report-ready summary of completed simulations.
- Keep reusable analysis routines modular and easy to contribute.

## Contribution areas
- `scripts/` for reusable code assets (optional).
- `technical_reporting/` for report-generation guidance and templates.

## Boundaries
- This folder extends analysis capability.
- It must not redefine the core authoring or execution flow.

## Policy
- Do not overwrite raw FLUKA outputs.
- Prefer small reusable recipes and scripts over one large monolithic analysis module.
- Add reusable code assets under `scripts/` only when needed.
- Put report-generation assets under a dedicated `technical_reporting/` subfolder so they remain distinct from numerical post-processing logic.

## Technical reporting recipe (summary)
- Use technical reporting when the user asks for a simulation report after execution and analysis are complete.
- Use real artifacts as evidence: `autofluka_results/fluka_data.json`, plots under `autofluka_results/`, and any fix notes (`*_autofluka_fixes.md`).
- Do not invent missing inputs or results; write explicit `TODO:` placeholders.
- Do not claim validation unless a real benchmark/experiment comparison exists.
- Preserve FLUKA-specific reproducibility details:
  - source and beam definition
  - geometry and materials
  - physics and transport settings
  - thresholds and important defaults
  - scoring cards and what they measure
  - number of primaries and uncertainty level
- Use `image_analysis_tool` only as a figure-caption aid when plots already exist and a short description is needed (do not replace structured interpretation).

### Required inputs
- Problem statement / objective.
- Canonical input deck.
- Verified outputs (plots, JSON, `_tab.lis`, `_sum.lis`, uncertainties when available).

### Expected outputs
- One report file (Markdown by default; LaTeX when explicitly requested).
- Figures/tables reference existing artifacts by relative paths.

### Output policy (report writing)
- Default output should be one Markdown report unless the user explicitly requests LaTeX.
- If figures exist, embed them by relative path and include short technical captions.
- If figures do not exist, omit the figure subsection cleanly or leave a clearly labeled placeholder.
- Tables may be written directly in Markdown.
- Treat the generated report as a technical draft that can be expanded into a paper later.

### Report templates (files)
- Markdown scaffold: `fluka-post-processing/technical_reporting/minimal_simulation_report.md`
- LaTeX template: `fluka-post-processing/technical_reporting/technical_report_template.tex`

### Recommended structure
1. Title / metadata
2. Abstract
3. Introduction + objective
4. Campaign overview
5. Methodology (compact)
6. Troubleshooting and repairs (before results)
7. Results and discussion
8. Reproducibility notes (incl. lessons learned)
9. Conclusion
10. References

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

## Statistics and uncertainty interpretation (decrypt/summary outputs)
- A per-cycle `_sum.lis` uncertainty from a single FLUKA cycle (N=1) is **not a measured error bar** — it is FLUKA's own undefined-statistic placeholder, not a bug in AutoFLUKA's decrypt tooling. Variance can only be computed from batch-to-batch spread across ≥2 independent cycles. Per FLUKA's own training material (*Monte Carlo Basics*, ULB course, May 2022, slide 28): "if you run just one cycle (N=1), the above expression cannot be evaluated and FLUKA will return 100% uncertainty."
- Never read or report a *per-cycle* `_sum.lis` uncertainty as a meaningful result. Only the combined multi-cycle summary carries a real uncertainty, and only once ≥2 cycles exist.
- Recommended minimum: 5-10 cycles of comparable size (same source material's own recommendation, slide 29) before trusting a reported uncertainty.
- Quality-of-result guideline by relative error (MCNP-derived, broadly applicable across codes, slide 30): ≥50% = garbage, 20-50% = factor of a few, 10-20% = questionable, <10% = generally reliable. Flag a result as statistically insufficient rather than reporting whatever number comes out when the relative error falls outside the reliable band.

## Area and volume normalization (check before reporting fluence)
- FLUKA does not compute detector areas or volumes. A `USRBDX` result is per cm² only if WHAT(6) held the true boundary area; a `USRTRACK` result is fluence only if WHAT(5) held the true region volume. Both default to 1.0, which gives results integrated over the detector.
- Before reporting a per-cm² value, read the area/volume FLUKA used from the `.out` file (e.g. `detector area: 1.0000E+00 cm**2`). If it is 1.0 but the detector is not 1 cm², divide by the true area/volume (e.g. 4πr² for a sphere boundary) and state that you did.
- Do not normalize twice: if the card already held the true area, the output is already per cm².

## Multi-configuration analysis
- Do not pool outputs from multiple distinct configurations of the same case (e.g. with/without a degrader, different target thicknesses) into one decrypt/report pass. Segregate by configuration — decrypt and analyze each one on its own, even when they share a scorer layout — so a configuration-dependent effect isn't averaged away or misattributed.

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

## Policy
- Do not overwrite raw FLUKA outputs.
- Prefer small reusable recipes and scripts over one large monolithic analysis module.
- Add reusable code assets under `scripts/` only when needed.
- Put report-generation assets under a dedicated `technical_reporting/` subfolder so they remain distinct from numerical post-processing logic.

## Boundaries
- This folder extends analysis capability.
- It must not redefine the core authoring or execution flow.

## Contribution areas
- `scripts/` for reusable code assets (optional).
- `technical_reporting/` for report-generation guidance and templates.

# {{title}}

## Abstract
{{brief_summary_of_problem_setup_main_findings_and_significance}}

## 1. Problem Statement and Objective
- **Application area:** {{dosimetry | shielding | activation | detector response | accelerator | medical physics | other}}
- **Problem being studied:** {{describe_the_physical_or_engineering_problem}}
- **Objective:** {{state_the_question_the_simulation_is_answering}}
- **Scope and limitations:** {{state_main_assumptions_and_boundaries}}

## 2. Simulation Methodology
- **Code:** FLUKA
- **FLUKA version:** {{version_if_known}}
- **Execution environment:** {{local | docker | wsl_linux | other}}
- **Geometry/materials:** {{summary}}
- **Source/beam:** {{summary}}
- **Physics/transport settings:** {{summary}}
- **Scoring plan:** {{summary}}
- **Statistical strategy:** {{nps_runs_uncertainty_strategy}}

## 3. FLUKA Input Summary
- **Canonical input file:** `{{input_filename}}`
- **Important non-default cards:** {{summary}}
- **Reproducibility note:** {{what_must_remain_unchanged}}

## 4. Troubleshooting and Repairs
{{run_specific_fix_notes_or_TODO}}

## 5. Results and Discussion
| Metric | Value | Uncertainty | Notes |
| --- | --- | --- | --- |
| {{metric}} | {{value}} | {{uncertainty}} | {{note}} |

## 6. Reproducibility Notes
- **Files required to reproduce:** {{list_required_files}}
- **Generated artifacts used:** {{list_artifacts}}
- **TODO items remaining:** {{list_or_none}}

### Lessons learned
- {{lesson_1}}

## 7. Conclusion
{{main_takeaway_and_next_steps}}

## References
1. {{FLUKA_manual_or_primary_reference}}
# {{title}}

## Abstract
{{brief_summary_of_problem_setup_main_findings_and_significance}}

## 1. Problem Statement and Objective
- **Application area:** {{dosimetry | shielding | activation | detector response | accelerator | medical physics | other}}
- **Problem being studied:** {{describe_the_physical_or_engineering_problem}}
- **Objective:** {{state_the_question_the_simulation_is_answering}}
- **Scope and limitations:** {{state_main_assumptions_and_boundaries}}

## 2. Simulation Methodology

### 2.1 Code and Execution Context
- **Code:** FLUKA
- **FLUKA version:** {{version_if_known}}
- **Workflow:** {{AutoFLUKA_workflow_summary}}
- **Execution environment:** {{local | docker | wsl_linux | other}}

### 2.2 Geometry and Materials
- **Geometry summary:** {{describe_geometry}}
- **Materials:** {{list_main_materials}}
- **Key dimensions:** {{list_important_dimensions}}
- **Modeling assumptions:** {{state_simplifications}}

### 2.3 Source Definition and Beam Conditions
- **Particle/source type:** {{particle}}
- **Energy:** {{energy}}
- **Source position and direction:** {{source_definition}}
- **Irradiation conditions:** {{beam_or_source_conditions}}

### 2.4 Physics and Transport Settings
- **Important defaults/physics cards:** {{list_defaults_and_physics_controls}}
- **Transport or production thresholds:** {{list_threshold_values_and_units}}
- **Reason for these settings:** {{justify_nondefault_choices}}

### 2.5 Scoring and Quantities of Interest
| Scoring card or output | Quantity reported | Units | Reason for inclusion |
| --- | --- | --- | --- |
| {{card_name}} | {{quantity}} | {{units}} | {{why_needed}} |
| {{card_name}} | {{quantity}} | {{units}} | {{why_needed}} |

### 2.6 Statistical Strategy
- **Number of primaries:** {{nps_or_start_primaries}}
- **Number of runs/copies:** {{number_of_runs}}
- **Uncertainty target:** {{target_if_used}}
- **Convergence strategy:** {{describe_if_used}}

## 3. FLUKA Input Summary
- **Canonical input file:** `{{input_filename}}`
- **Key regions/material assignments:** {{summary}}
- **Important non-default cards:** {{summary}}
- **Reproducibility note:** {{what_a_user_must_keep_unchanged_to_reproduce}}

## 4. Post-Processing Workflow
- **Decryption workflow:** {{summary}}
- **Structured data products used:** {{json_lis_csv_outputs}}
- **Derived analyses performed:** {{plots_rebinning_spectra_activation_summary}}
- **Custom scripts or recipes used:** {{list_if_any}}

## 5. Results

### 5.1 Main Numerical Results
| Metric | Value | Uncertainty | Notes |
| --- | --- | --- | --- |
| {{metric}} | {{value}} | {{uncertainty}} | {{note}} |
| {{metric}} | {{value}} | {{uncertainty}} | {{note}} |

### 5.2 Figures
<!-- If relevant plot files exist, include them by relative path. If no figures exist, remove this subsection or replace it with a TODO note. -->
<!-- If a caption is needed, it may be generated from existing plots using image analysis, but numerical claims should still come from structured outputs. -->
![{{figure_1_caption}}]({{relative_path_to_figure_1}})

*Figure 1. {{figure_1_caption}}. Quantitative interpretation should be read together with the reported values and uncertainties.*

![{{figure_2_caption}}]({{relative_path_to_figure_2}})

*Figure 2. {{figure_2_caption}}. Quantitative interpretation should be read together with the reported values and uncertainties.*

### 5.3 Statistical Quality
- **Average uncertainties:** {{summary}}
- **Low-statistics regions or detectors:** {{summary}}
- **Quality/reliability note:** {{summary}}

## 6. Discussion
- **Physical interpretation:** {{interpret_main_findings}}
- **Sensitivity to assumptions:** {{important_sensitivities}}
- **Comparison to expectation/benchmark/literature:** {{only_if_available_otherwise_todo}}
- **Main limitations:** {{limitations}}

## 7. Reproducibility Notes
- **Files required to reproduce the case:** {{list_required_files}}
- **Generated artifacts used in this report:** {{list_artifacts}}
- **Important run settings:** {{summarize_settings_that_must_match}}
- **TODO items remaining:** {{list_missing_but_needed_items_or_write_none}}

## 8. Conclusion
- **Main takeaway:** {{main_conclusion}}
- **Was the objective achieved?** {{yes_no_with_reason}}
- **Recommended next steps:** {{follow_up_work}}

## References
1. {{FLUKA_manual_or_primary_reference}}
2. {{paper_report_or_benchmark_reference_if_used}}

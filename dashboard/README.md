# Dashboard

This Streamlit dashboard presents validated results from the Hillstrom email experiment for executive and product decision-making.

## Validated sources

- outputs/tables/executive_kpi_summary.csv
- outputs/tables/primary_treatment_effects.csv
- outputs/tables/experiment_descriptive_summary.csv
- outputs/tables/experiment_validation_summary.csv
- outputs/tables/power_mde_summary.csv
- outputs/tables/segment_treatment_effects.csv
- outputs/tables/interaction_tests.csv
- outputs/tables/robustness_analysis_summary.csv
- outputs/reports/business_interpretation.md
- outputs/figures/spend_treatment_effects.png, when available
- outputs/figures/baseline_balance_smd.png, when available
- outputs/figures/conversion_mde_curve.png and visit_mde_curve.png, when available
- outputs/figures/segment_spend_forest.png, segment_conversion_forest.png, and segment_visit_forest.png, when available
- outputs/figures/adjusted_vs_unadjusted_spend.png and adjusted_vs_unadjusted_binary.png, when available

The dashboard displays validated outputs and does not re-run the complete statistical pipeline. It includes executive results, funnel and reliability context, power/MDE sensitivity, interactive exploratory segment analysis, supporting robustness displays, a business decision framework, methodology, architecture, and limitations. Subgroup exploration is exploratory and hypothesis-generating.

## Installation

pip install -r requirements.txt

## Launch

streamlit run dashboard/app.py

## Public Deployment

The dashboard is compatible with a standard Streamlit deployment using `dashboard/app.py` as the entry point and the repository-root `requirements.txt` for dependencies. The validated tables, figures, and report listed above must remain available in the repository. No secrets, database connection, or Streamlit configuration file is required.

**Live Dashboard:** [https://hillstrom-ab-testing-analysis-cnezxrwubpb8twdcudvwrp.streamlit.app/](https://hillstrom-ab-testing-analysis-cnezxrwubpb8twdcudvwrp.streamlit.app/)

"""Reusable exploratory subgroup and interaction-analysis utilities."""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

from src.metrics import absolute_effect, relative_lift
from src.statistical_tests import bootstrap_mean_difference, proportion_treatment_effect


def subgroup_treatment_effects(
    data: pd.DataFrame,
    treatment_groups: Sequence[str],
    control_group: str,
    segment_variables: Sequence[str],
    random_generator: np.random.Generator,
    bootstrap_resamples: int = 1_000,
    minimum_arm_size: int = 1_000,
    sparse_event_threshold: int = 5,
) -> pd.DataFrame:
    """Generate exploratory subgroup treatment-effect results from supplied columns.

    Spend uses a percentile-bootstrap confidence interval. Conversion and visit
    use the validated Wald interval and retain sparse-event and small-arm flags.
    """
    effect_rows: list[dict[str, Any]] = []

    for variable in segment_variables:
        for level in sorted(data[variable].unique()):
            subgroup = data.loc[data[variable] == level]
            for treatment in treatment_groups:
                treatment_data = subgroup.loc[subgroup["segment"] == treatment]
                control_data = subgroup.loc[subgroup["segment"] == control_group]
                treatment_n = len(treatment_data)
                control_n = len(control_data)
                if min(treatment_n, control_n) == 0:
                    raise ValueError(
                        "Each subgroup level must contain treatment and control observations."
                    )
                small_arm = min(treatment_n, control_n) < minimum_arm_size

                treatment_spend = treatment_data["spend"].mean()
                control_spend = control_data["spend"].mean()
                spend_bootstrap = bootstrap_mean_difference(
                    treatment_data["spend"].to_numpy(),
                    control_data["spend"].to_numpy(),
                    random_generator,
                    bootstrap_resamples,
                )
                effect_rows.append(
                    {
                        "Segment Variable": variable,
                        "Segment Level": level,
                        "Treatment": treatment,
                        "Control": control_group,
                        "Outcome": "Spend",
                        "Treatment N": treatment_n,
                        "Control N": control_n,
                        "Treatment Metric": treatment_spend,
                        "Control Metric": control_spend,
                        "Absolute Effect": absolute_effect(
                            treatment_spend, control_spend
                        ),
                        "Relative Lift": relative_lift(
                            treatment_spend, control_spend
                        ),
                        "CI Lower": spend_bootstrap["ci_lower"],
                        "CI Upper": spend_bootstrap["ci_upper"],
                        "Sparse Event Flag": "Not applicable",
                        "Small Arm Flag": small_arm,
                        "Inference Method": "1,000-resample percentile bootstrap CI",
                    }
                )

                for outcome in ["conversion", "visit"]:
                    effect = proportion_treatment_effect(
                        int(treatment_data[outcome].sum()),
                        treatment_n,
                        int(control_data[outcome].sum()),
                        control_n,
                    )
                    sparse_event = (
                        min(
                            int(treatment_data[outcome].sum()),
                            int(control_data[outcome].sum()),
                        )
                        < sparse_event_threshold
                        if outcome == "conversion"
                        else False
                    )
                    effect_rows.append(
                        {
                            "Segment Variable": variable,
                            "Segment Level": level,
                            "Treatment": treatment,
                            "Control": control_group,
                            "Outcome": outcome.title(),
                            "Treatment N": treatment_n,
                            "Control N": control_n,
                            "Treatment Metric": effect["treatment_rate"],
                            "Control Metric": effect["control_rate"],
                            "Absolute Effect": effect["effect"],
                            "Relative Lift": effect["relative_lift"],
                            "CI Lower": effect["ci_lower"],
                            "CI Upper": effect["ci_upper"],
                            "Sparse Event Flag": sparse_event,
                            "Small Arm Flag": small_arm,
                            "Inference Method": "Wald CI for proportion difference",
                        }
                    )

    return pd.DataFrame(effect_rows)


def interaction_test(
    data: pd.DataFrame,
    outcome: str,
    treatment: str,
    variable: str,
    control_group: str,
) -> dict[str, Any]:
    """Return a robust joint Wald test for treatment-by-segment interactions."""
    model_data = data.loc[data["segment"].isin([control_group, treatment])].copy()
    model_data["treatment_indicator"] = (
        model_data["segment"] == treatment
    ).astype(int)
    formula = f"{outcome} ~ treatment_indicator * C({variable})"

    try:
        if outcome in ["conversion", "visit"]:
            fit = smf.glm(
                formula, data=model_data, family=sm.families.Binomial()
            ).fit(cov_type="HC3")
            test_name = "Logistic GLM robust joint Wald test"
        else:
            fit = smf.ols(formula, data=model_data).fit(cov_type="HC3")
            test_name = "OLS mean model HC3 robust joint Wald test"
        positions = [
            index for index, parameter in enumerate(fit.params.index) if ":" in parameter
        ]
        p_value = float(
            fit.wald_test(np.eye(len(fit.params))[positions], scalar=True).pvalue
        )
        return {
            "p_value": p_value,
            "test_name": test_name,
            "model_status": "Model fit successfully",
        }
    except Exception as error:
        return {
            "p_value": np.nan,
            "test_name": "Model not available",
            "model_status": f"Model issue: {str(error)[:140]}",
        }


def add_fdr_interpretation(
    interaction_results: pd.DataFrame, alpha: float = 0.05
) -> pd.DataFrame:
    """Add Benjamini-Hochberg adjusted p-values and exploratory labels."""
    results = interaction_results.copy()
    valid = results["Raw P-Value"].notna()
    results.loc[valid, "FDR Adjusted P-Value"] = multipletests(
        results.loc[valid, "Raw P-Value"], method="fdr_bh"
    )[1]
    results["Interpretation"] = np.where(
        results["FDR Adjusted P-Value"] < alpha,
        "Exploratory interaction notable after FDR adjustment",
        "No interaction notable after FDR adjustment",
    )
    return results

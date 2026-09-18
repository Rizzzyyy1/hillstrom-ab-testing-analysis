"""Tests for exploratory subgroup and interaction utilities."""

import numpy as np
import pandas as pd
import pytest
from statsmodels.stats.multitest import multipletests

from src.segmentation import add_fdr_interpretation, subgroup_treatment_effects


def synthetic_segment_data() -> pd.DataFrame:
    """Return a small balanced dataset with two supplied segment levels."""
    return pd.DataFrame(
        {
            "segment": [
                "No E-Mail", "No E-Mail", "Mens E-Mail", "Mens E-Mail",
                "No E-Mail", "No E-Mail", "Mens E-Mail", "Mens E-Mail",
            ],
            "audience": ["new", "new", "new", "new", "existing", "existing", "existing", "existing"],
            "spend": [1.0, 3.0, 4.0, 6.0, 2.0, 4.0, 3.0, 5.0],
            "conversion": [0, 1, 1, 1, 0, 0, 1, 0],
            "visit": [0, 1, 1, 1, 0, 1, 1, 1],
        }
    )


def test_subgroup_effects_include_expected_metrics_and_flags() -> None:
    results = subgroup_treatment_effects(
        synthetic_segment_data(),
        treatment_groups=["Mens E-Mail"],
        control_group="No E-Mail",
        segment_variables=["audience"],
        random_generator=np.random.default_rng(9),
        bootstrap_resamples=100,
        minimum_arm_size=3,
        sparse_event_threshold=2,
    )
    new_spend = results.loc[
        (results["Segment Level"] == "new") & (results["Outcome"] == "Spend")
    ].iloc[0]
    new_conversion = results.loc[
        (results["Segment Level"] == "new") & (results["Outcome"] == "Conversion")
    ].iloc[0]

    assert len(results) == 6
    assert new_spend["Treatment N"] == 2
    assert new_spend["Control N"] == 2
    assert new_spend["Treatment Metric"] == pytest.approx(5.0)
    assert new_spend["Control Metric"] == pytest.approx(2.0)
    assert new_spend["Absolute Effect"] == pytest.approx(3.0)
    assert bool(new_spend["Small Arm Flag"])
    assert bool(new_conversion["Sparse Event Flag"])


def test_subgroup_effects_reject_empty_treatment_arm() -> None:
    data = synthetic_segment_data()
    data.loc[data["audience"] == "new", "segment"] = "No E-Mail"

    with pytest.raises(ValueError, match="treatment and control"):
        subgroup_treatment_effects(
            data,
            treatment_groups=["Mens E-Mail"],
            control_group="No E-Mail",
            segment_variables=["audience"],
            random_generator=np.random.default_rng(1),
            bootstrap_resamples=10,
        )


def test_fdr_interpretation_preserves_raw_values_and_matches_statsmodels() -> None:
    results = pd.DataFrame({"Raw P-Value": [0.01, 0.04, 0.50]})
    actual = add_fdr_interpretation(results)
    expected = multipletests(results["Raw P-Value"], method="fdr_bh")[1]

    np.testing.assert_allclose(actual["FDR Adjusted P-Value"], expected)
    np.testing.assert_allclose(actual["Raw P-Value"], results["Raw P-Value"])
    assert actual.loc[0, "Interpretation"] == "Exploratory interaction notable after FDR adjustment"
    assert actual.loc[2, "Interpretation"] == "No interaction notable after FDR adjustment"

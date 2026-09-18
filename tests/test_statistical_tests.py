"""Tests for reusable frequentist inference utilities."""

import numpy as np
import pytest
from statsmodels.stats.multitest import multipletests

from src.statistical_tests import (
    binary_standardized_mean_difference,
    bootstrap_mean_difference,
    continuous_standardized_mean_difference,
    holm_adjusted_p_values,
    proportion_treatment_effect,
    welch_mean_comparison,
)


def test_bootstrap_is_reproducible_with_fixed_seed() -> None:
    treatment = np.array([2.0, 3.0, 4.0, 5.0])
    control = np.array([1.0, 2.0, 3.0, 4.0])
    first = bootstrap_mean_difference(
        treatment, control, np.random.default_rng(42), n_resamples=500
    )
    second = bootstrap_mean_difference(
        treatment, control, np.random.default_rng(42), n_resamples=500
    )

    np.testing.assert_array_equal(first["differences"], second["differences"])
    assert first["ci_lower"] < 1.0 < first["ci_upper"]


def test_bootstrap_identical_samples_is_centered_near_zero() -> None:
    values = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    result = bootstrap_mean_difference(
        values, values, np.random.default_rng(7), n_resamples=1_000
    )

    assert result["differences"].mean() == pytest.approx(0.0, abs=0.1)
    assert result["ci_lower"] < result["ci_upper"]


def test_welch_mean_comparison_reverses_effect_direction() -> None:
    treatment = np.array([3.0, 4.0, 5.0, 6.0])
    control = np.array([1.0, 2.0, 3.0, 4.0])
    forward = welch_mean_comparison(treatment, control)
    reverse = welch_mean_comparison(control, treatment)

    assert forward["effect"] == pytest.approx(2.0)
    assert reverse["effect"] == pytest.approx(-2.0)
    assert 0.0 <= forward["p_value"] <= 1.0


def test_welch_mean_comparison_identical_arrays_has_zero_effect() -> None:
    values = np.array([1.0, 2.0, 3.0, 4.0])
    result = welch_mean_comparison(values, values)

    assert result["effect"] == pytest.approx(0.0)
    assert result["p_value"] == pytest.approx(1.0)


def test_proportion_treatment_effect_known_counts() -> None:
    result = proportion_treatment_effect(20, 100, 10, 100)

    assert result["treatment_rate"] == pytest.approx(0.20)
    assert result["control_rate"] == pytest.approx(0.10)
    assert result["effect"] == pytest.approx(0.10)
    assert result["relative_lift"] == pytest.approx(1.0)
    assert result["ci_lower"] < result["effect"] < result["ci_upper"]
    assert 0.0 <= result["p_value"] <= 1.0


def test_holm_adjustment_matches_statsmodels_and_preserves_bounds() -> None:
    raw_p_values = np.array([0.01, 0.03, 0.20])
    actual = holm_adjusted_p_values(raw_p_values)
    expected = multipletests(raw_p_values, method="holm")[1]

    np.testing.assert_allclose(actual, expected)
    assert np.all(actual >= raw_p_values)
    assert np.all((0.0 <= actual) & (actual <= 1.0))


def test_continuous_smd_identical_groups_and_direction() -> None:
    control = np.array([1.0, 2.0, 3.0])
    treatment = np.array([2.0, 3.0, 4.0])

    assert continuous_standardized_mean_difference(control, control) == pytest.approx(0.0)
    assert continuous_standardized_mean_difference(treatment, control) > 0
    assert continuous_standardized_mean_difference(control, treatment) < 0


def test_binary_smd_identical_groups_and_direction() -> None:
    control = np.array([0, 0, 1, 1])
    treatment = np.array([0, 1, 1, 1])

    assert binary_standardized_mean_difference(control, control) == pytest.approx(0.0)
    assert binary_standardized_mean_difference(treatment, control) > 0
    assert binary_standardized_mean_difference(control, treatment) < 0

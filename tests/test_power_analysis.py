"""Tests for power and MDE utilities."""

import numpy as np
import pytest
from statsmodels.stats.power import NormalIndPower

from src.power_analysis import (
    binary_mde,
    mde_curve,
    required_binary_sample_size,
    simulated_spend_matrix,
    spend_simulation_power,
)


def test_mde_has_expected_monotonic_behavior() -> None:
    baseline = 0.0057260865
    small_sample = binary_mde(baseline, 5_000, 5_000, 0.80)
    large_sample = binary_mde(baseline, 20_000, 20_000, 0.80)
    higher_power = binary_mde(baseline, 5_000, 5_000, 0.90)
    stricter_alpha = binary_mde(baseline, 5_000, 5_000, 0.80, alpha_value=0.01)

    assert 0 < small_sample["Detectable Treatment Rate"] < 1
    assert large_sample["MDE Absolute Effect"] < small_sample["MDE Absolute Effect"]
    assert higher_power["MDE Absolute Effect"] > small_sample["MDE Absolute Effect"]
    assert stricter_alpha["MDE Absolute Effect"] > small_sample["MDE Absolute Effect"]


def test_mde_matches_direct_statsmodels_calculation() -> None:
    baseline = 0.10
    result = binary_mde(baseline, 1_000, 1_200, 0.80)
    effect_size = NormalIndPower().solve_power(
        effect_size=None,
        nobs1=1_000,
        alpha=0.05,
        power=0.80,
        ratio=1.2,
        alternative="two-sided",
    )
    expected_rate = np.sin(np.arcsin(np.sqrt(baseline)) + effect_size / 2) ** 2

    assert result["Detectable Treatment Rate"] == pytest.approx(expected_rate)


def test_required_sample_size_has_expected_monotonic_behavior() -> None:
    baseline = 0.0057260865
    small_effect = required_binary_sample_size(baseline, 0.001, 0.80)
    large_effect = required_binary_sample_size(baseline, 0.003, 0.80)
    higher_power = required_binary_sample_size(baseline, 0.001, 0.90)
    stricter_alpha = required_binary_sample_size(baseline, 0.001, 0.80, alpha_value=0.01)

    assert small_effect > large_effect
    assert higher_power > small_effect
    assert stricter_alpha > small_effect
    assert np.isnan(required_binary_sample_size(0.99, 0.02, 0.80))


def test_mde_curve_decreases_with_sample_size() -> None:
    sample_sizes = np.array([2_000, 5_000, 10_000])
    curve = mde_curve(0.10, sample_sizes, 0.80)

    assert curve.shape == sample_sizes.shape
    assert np.all(curve > 0)
    assert np.all(np.diff(curve) < 0)


def test_simulated_spend_matrix_is_reproducible_and_zero_inflated() -> None:
    positive_values = np.array([5.0, 10.0, 20.0])
    first = simulated_spend_matrix(
        np.random.default_rng(5), 100, 0.20, positive_values, batch_size=4
    )
    second = simulated_spend_matrix(
        np.random.default_rng(5), 100, 0.20, positive_values, batch_size=4
    )

    np.testing.assert_array_equal(first, second)
    assert np.any(first == 0)
    assert set(np.unique(first)).issubset({0.0, 5.0, 10.0, 20.0})


def test_spend_simulation_power_is_bounded_and_increases_with_effect() -> None:
    values = np.array([5.0, 10.0, 20.0])
    common_inputs = {
        "control_n": 200,
        "treatment_n": 200,
        "control_positive_spend_rate": 0.20,
        "control_positive_spend_mean": values.mean(),
        "control_positive_spend_values": values,
        "alpha_value": 0.05,
        "n_simulations": 120,
    }
    no_effect = spend_simulation_power(0.0, np.random.default_rng(11), **common_inputs)
    larger_effect = spend_simulation_power(1.0, np.random.default_rng(12), **common_inputs)

    assert 0.0 <= no_effect["estimated_power"] <= 0.20
    assert 0.0 <= larger_effect["estimated_power"] <= 1.0
    assert larger_effect["estimated_power"] >= no_effect["estimated_power"]

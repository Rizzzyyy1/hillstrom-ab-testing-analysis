"""Reusable power and minimum-detectable-effect utilities."""

from __future__ import annotations

import numpy as np
from scipy.stats import ttest_ind
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize


def binary_mde(
    baseline_rate: float,
    control_n: int,
    treatment_n: int,
    power: float,
    alpha_value: float = 0.05,
) -> dict[str, float]:
    """Calculate a two-sided binary-outcome MDE using the validated normal model."""
    power_solver = NormalIndPower()
    effect_size = power_solver.solve_power(
        effect_size=None,
        nobs1=control_n,
        alpha=alpha_value,
        power=power,
        ratio=treatment_n / control_n,
        alternative="two-sided",
    )
    treatment_rate = np.sin(
        np.arcsin(np.sqrt(baseline_rate)) + effect_size / 2
    ) ** 2
    absolute_effect = treatment_rate - baseline_rate
    return {
        "Power": power,
        "Alpha": alpha_value,
        "Baseline Rate": baseline_rate,
        "MDE Absolute Effect": absolute_effect,
        "MDE Percentage Points": absolute_effect * 100,
        "Detectable Treatment Rate": treatment_rate,
        "Relative MDE": absolute_effect / baseline_rate,
    }


def required_binary_sample_size(
    baseline_rate: float,
    absolute_effect: float,
    power: float,
    alpha_value: float = 0.05,
) -> float:
    """Return the equal-arm sample size for a positive binary absolute effect."""
    treatment_rate = baseline_rate + absolute_effect
    if not 0 < treatment_rate < 1:
        return np.nan
    power_solver = NormalIndPower()
    effect_size = proportion_effectsize(treatment_rate, baseline_rate)
    return float(
        power_solver.solve_power(
            effect_size=effect_size,
            nobs1=None,
            alpha=alpha_value,
            power=power,
            ratio=1.0,
            alternative="two-sided",
        )
    )


def mde_curve(
    baseline_rate: float,
    sample_size_grid: np.ndarray,
    power: float,
    alpha_value: float = 0.05,
) -> np.ndarray:
    """Return equal-arm binary MDEs in percentage points across sample sizes."""
    return np.array(
        [
            binary_mde(baseline_rate, group_n, group_n, power, alpha_value)[
                "MDE Percentage Points"
            ]
            for group_n in sample_size_grid
        ]
    )


def simulated_spend_matrix(
    random_generator: np.random.Generator,
    n_observations: int,
    positive_probability: float,
    positive_values: np.ndarray,
    batch_size: int,
) -> np.ndarray:
    """Generate zero-inflated spend samples with empirical positive-spend resampling."""
    positive_mask = (
        random_generator.random((batch_size, n_observations)) < positive_probability
    )
    simulated_values = np.zeros((batch_size, n_observations))
    simulated_values[positive_mask] = random_generator.choice(
        positive_values, size=positive_mask.sum(), replace=True
    )
    return simulated_values


def spend_simulation_power(
    mean_effect: float,
    random_generator: np.random.Generator,
    control_n: int,
    treatment_n: int,
    control_positive_spend_rate: float,
    control_positive_spend_mean: float,
    control_positive_spend_values: np.ndarray,
    alpha_value: float,
    n_simulations: int = 1_000,
    batch_size: int = 50,
) -> dict[str, float]:
    """Estimate Welch-test power under the validated zero-inflated spend scenario."""
    treatment_positive_probability = (
        control_positive_spend_rate + mean_effect / control_positive_spend_mean
    )
    rejections = 0
    completed = 0

    while completed < n_simulations:
        batch = min(batch_size, n_simulations - completed)
        simulated_control = simulated_spend_matrix(
            random_generator,
            control_n,
            control_positive_spend_rate,
            control_positive_spend_values,
            batch,
        )
        simulated_treatment = simulated_spend_matrix(
            random_generator,
            treatment_n,
            treatment_positive_probability,
            control_positive_spend_values,
            batch,
        )
        p_values = ttest_ind(
            simulated_treatment, simulated_control, axis=1, equal_var=False
        ).pvalue
        rejections += int((p_values < alpha_value).sum())
        completed += batch

    estimated_power = rejections / n_simulations
    monte_carlo_se = np.sqrt(
        (rejections + 2)
        * (n_simulations - rejections + 2)
        / (n_simulations + 4) ** 3
    )
    return {
        "treatment_positive_probability": treatment_positive_probability,
        "estimated_power": estimated_power,
        "monte_carlo_se": monte_carlo_se,
    }

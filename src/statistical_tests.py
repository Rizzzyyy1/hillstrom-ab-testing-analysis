"""Reusable frequentist utilities used in the validated analyses."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import confint_proportions_2indep, proportions_ztest

from src.metrics import absolute_effect, relative_lift


def bootstrap_mean_difference(
    treatment_values: np.ndarray,
    control_values: np.ndarray,
    random_generator: np.random.Generator,
    n_resamples: int = 10_000,
    batch_size: int = 100,
) -> dict[str, Any]:
    """Estimate a mean difference with a percentile bootstrap interval.

    Sampling is performed independently within treatment and control arms.
    The supplied generator makes the result reproducible.
    """
    treatment_array = np.asarray(treatment_values)
    control_array = np.asarray(control_values)
    differences = np.empty(n_resamples)
    start = 0

    while start < n_resamples:
        batch = min(batch_size, n_resamples - start)
        treatment_indices = random_generator.integers(
            0, len(treatment_array), size=(batch, len(treatment_array))
        )
        control_indices = random_generator.integers(
            0, len(control_array), size=(batch, len(control_array))
        )
        differences[start : start + batch] = (
            treatment_array[treatment_indices].mean(axis=1)
            - control_array[control_indices].mean(axis=1)
        )
        start += batch

    ci_lower, ci_upper = np.quantile(differences, [0.025, 0.975])
    return {
        "differences": differences,
        "standard_error": differences.std(ddof=1),
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
    }


def welch_mean_comparison(
    treatment_values: np.ndarray, control_values: np.ndarray
) -> dict[str, float]:
    """Return the Welch reference p-value and mean difference."""
    treatment_array = np.asarray(treatment_values)
    control_array = np.asarray(control_values)
    test_result = ttest_ind(treatment_array, control_array, equal_var=False)
    return {
        "effect": absolute_effect(treatment_array.mean(), control_array.mean()),
        "p_value": float(test_result.pvalue),
    }


def proportion_treatment_effect(
    treatment_successes: int,
    treatment_n: int,
    control_successes: int,
    control_n: int,
) -> dict[str, float]:
    """Return a binary treatment effect, Wald CI, and two-sided z-test p-value."""
    treatment_rate = treatment_successes / treatment_n
    control_rate = control_successes / control_n
    ci_lower, ci_upper = confint_proportions_2indep(
        treatment_successes,
        treatment_n,
        control_successes,
        control_n,
        compare="diff",
        method="wald",
    )
    _, p_value = proportions_ztest(
        [treatment_successes, control_successes],
        [treatment_n, control_n],
        alternative="two-sided",
    )
    return {
        "treatment_rate": treatment_rate,
        "control_rate": control_rate,
        "effect": absolute_effect(treatment_rate, control_rate),
        "relative_lift": relative_lift(treatment_rate, control_rate),
        "ci_lower": float(ci_lower),
        "ci_upper": float(ci_upper),
        "p_value": float(p_value),
    }


def holm_adjusted_p_values(p_values: np.ndarray, alpha: float = 0.05) -> np.ndarray:
    """Return Holm-adjusted p-values for one family of hypotheses."""
    return multipletests(p_values, alpha=alpha, method="holm")[1]


def continuous_standardized_mean_difference(
    treatment_values: np.ndarray, control_values: np.ndarray
) -> float:
    """Return the continuous standardized mean difference using pooled SD."""
    treatment_array = np.asarray(treatment_values)
    control_array = np.asarray(control_values)
    pooled_sd = np.sqrt(
        (treatment_array.var(ddof=1) + control_array.var(ddof=1)) / 2
    )
    return float((treatment_array.mean() - control_array.mean()) / pooled_sd)


def binary_standardized_mean_difference(
    treatment_values: np.ndarray, control_values: np.ndarray
) -> float:
    """Return the binary standardized mean difference using pooled Bernoulli SD."""
    treatment_rate = np.asarray(treatment_values).mean()
    control_rate = np.asarray(control_values).mean()
    pooled_sd = np.sqrt(
        (
            treatment_rate * (1 - treatment_rate)
            + control_rate * (1 - control_rate)
        )
        / 2
    )
    return float((treatment_rate - control_rate) / pooled_sd)

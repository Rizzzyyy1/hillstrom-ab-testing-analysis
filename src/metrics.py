"""Reusable treatment-level metric calculations."""

from __future__ import annotations

import math


def absolute_effect(treatment_value: float, control_value: float) -> float:
    """Return the treatment-minus-control absolute effect."""
    return treatment_value - control_value


def relative_lift(treatment_value: float, control_value: float) -> float:
    """Return relative lift versus control, or NaN when control is zero."""
    if control_value == 0:
        return math.nan
    return absolute_effect(treatment_value, control_value) / control_value


def scale_effect_per_1000(effect: float) -> float:
    """Scale a per-assigned-customer effect to 1,000 assigned customers."""
    return effect * 1_000

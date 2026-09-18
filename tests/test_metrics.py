"""Tests for reusable treatment-level metric calculations."""

import math

import pytest

from src.metrics import absolute_effect, relative_lift, scale_effect_per_1000


def test_absolute_effect_known_values() -> None:
    assert absolute_effect(0.15, 0.10) == pytest.approx(0.05)


def test_relative_lift_known_values() -> None:
    assert relative_lift(0.15, 0.10) == pytest.approx(0.50)


def test_relative_lift_returns_nan_for_zero_control() -> None:
    assert math.isnan(relative_lift(0.15, 0.0))


def test_scale_effect_per_1000_known_value() -> None:
    assert scale_effect_per_1000(0.05) == pytest.approx(50.0)

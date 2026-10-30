import pytest
from wildlife_robustness.evaluation.robustness import (
    absolute_drop, relative_retention, robustness_summary
)

def test_metrics():
    assert absolute_drop(0.8, 0.6) == pytest.approx(0.2)
    assert relative_retention(0.8, 0.6) == pytest.approx(0.75)
    summary = robustness_summary(0.8, [0.6, 0.7])
    assert summary["mean_absolute_drop"] == pytest.approx(0.15)
    assert summary["mean_relative_retention"] == pytest.approx(0.8125)

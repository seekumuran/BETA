import numpy as np
import pytest
from wildlife_robustness.augmentations import apply_degradation, degradation_names

@pytest.mark.parametrize("fault", degradation_names())
@pytest.mark.parametrize("severity", ["low", "medium", "high"])
def test_degradation_shape_dtype_and_repeatability(fault, severity):
    image = np.full((128, 160, 3), 120, dtype=np.uint8)
    first = apply_degradation(image, fault, severity, seed=123)
    second = apply_degradation(image, fault, severity, seed=123)
    assert first.shape == image.shape
    assert first.dtype == np.uint8
    assert np.array_equal(first, second)

def test_invalid_fault_raises():
    image = np.zeros((20, 20, 3), dtype=np.uint8)
    with pytest.raises(ValueError):
        apply_degradation(image, "not_a_fault")

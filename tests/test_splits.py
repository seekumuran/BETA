import pytest
from wildlife_robustness.data.splits import validate_disjoint_locations

def test_disjoint_splits_pass():
    assert validate_disjoint_locations(["a"], ["b"], ["c"])

def test_location_leakage_fails():
    with pytest.raises(ValueError):
        validate_disjoint_locations(["a"], ["b"], ["a"])

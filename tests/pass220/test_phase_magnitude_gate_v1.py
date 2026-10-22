import pytest
from hhs_runtime.pass220_phase_magnitude_gate_v1 import (
    COMPOSITION, CANCELLATION, EXPECTED_CHAIN,
    split_ordered_equals, candidate_gate_receipt,
)
def test_ordered_source_and_commutator():
    receipt=candidate_gate_receipt()
    assert receipt["composition_operands"] == ("(x/2)+(a²/b²)", "x⁴/a²")
    assert receipt["cancellation_operands"] == EXPECTED_CHAIN
    assert receipt["cancellation_gates"] == 7
    assert receipt["preserve_ordered_commutator"] == "xy-yx"
    assert not receipt["canonical_hash216_minted"]
def test_fail_closed_malformed():
    for source in ("x==y", "x=(y", "x=y)", "=x", "x="):
        with pytest.raises(ValueError):
            split_ordered_equals(source)
def test_original_sources():
    assert CANCELLATION.count("=") == 7
    assert COMPOSITION.count("=") == 1

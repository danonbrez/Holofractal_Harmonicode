"""Dependency-scoped P-only index conformance; inherited radix is authoritative."""
import pytest
from hhs_runtime.hhs_pass220_p_window_inherited_bigint_index_v1 import (
    lookup_window, PWindowIndexError,
)
from hhs_runtime.pass219.nonary_qudit_bigint_assembly_probe import (
    HASH72_MANIFOLD_CARDINALITY, encode_radix_digits,
)

@pytest.mark.parametrize("P", (1, 2, 179971, 2**100, HASH72_MANIFOLD_CARDINALITY//2))
def test_full_exact_window_and_glyph_inverse(P):
    receipt = lookup_window(P)
    assert receipt["P_bigint_decimal"] == str(P)
    assert receipt["sole_free_parameter"] == "P"
    assert receipt["carrier_positions"] == receipt["alternate_lattice_positions"] == 5184
    assert [int(item["bigint_decimal"]) for item in receipt["ordered_window"]] == [P-1,P,P+1]
    assert all(item["rational_den_decimal"] == "1" for item in receipt["ordered_window"])
    for item in receipt["ordered_window"]:
        assert encode_radix_digits(item["glyph72"],72) == int(item["bigint_decimal"])
        assert len(item["glyph72"]) == 72
    assert receipt["differences"] == {"P_minus_p":1,"q_minus_P":1,"q_minus_p":2}
    assert receipt["lookup_only"] is True
    assert receipt["lean4_native_proof_verified"] is False
    assert receipt["global_hnan_closure_verified"] is False
    assert receipt["canonical_vm81_mutation_authority"] is False
    assert receipt["canonical_hash72_mint_authority"] is False
    assert receipt["canonical_hash216_persistence_authority"] is False
    assert len(receipt["witness_sha256"]) == 64

def test_no_fixed_depth_modulo_aliasing():
    for invalid in (0,-1,HASH72_MANIFOLD_CARDINALITY-1,HASH72_MANIFOLD_CARDINALITY):
        with pytest.raises(PWindowIndexError,match="DEFER_TO_HYDRATION"):
            lookup_window(invalid)

def test_non_integer_rejected_and_deterministic():
    with pytest.raises(PWindowIndexError,match="EXACT_BIGINT"):
        lookup_window(1.0)
    with pytest.raises(PWindowIndexError,match="EXACT_BIGINT"):
        lookup_window(True)
    assert lookup_window(179971) == lookup_window(179971)
    assert lookup_window(179971)["witness_sha256"] != lookup_window(179972)["witness_sha256"]

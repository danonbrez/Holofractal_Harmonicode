"""Exact P-only parallel I073 generator reconciliation."""
import pytest
from hhs_runtime.hhs_pass220_i073_lean_parallel_generator_equivalence_v1 import (
    compare_p_generators, GeneratorEquivalenceError,
)

@pytest.mark.parametrize("P", [0, 1, 179971, 10**20+17])
def test_parallel_generators_preserve_one_canonical_state(P):
    receipt = compare_p_generators(P)
    assert receipt["P_decimal"] == str(P)
    assert receipt["same_exact_reconstruction"]
    assert receipt["distinct_generator_roots"]
    assert receipt["nesting_depths"] == (0,1)
    assert len(receipt["reconstructed_5184_sha256"]) == 64
    assert receipt["lean_theorem"] == "parallel_generator_equivalence"
    assert receipt["lean_kernel_proof_bound_to_runtime"] is False
    assert receipt["candidate_only"] is True
    assert receipt["canonical_vm81_mutation_authority"] is False
    assert receipt["canonical_hash72_mint_authority"] is False
    assert receipt["canonical_hash216_persistence_authority"] is False

def test_deterministic_reconstruction_and_source_identity():
    assert compare_p_generators(179971) == compare_p_generators(179971)
    assert (compare_p_generators(179971)["reconstructed_5184_sha256"] !=
            compare_p_generators(179972)["reconstructed_5184_sha256"])

@pytest.mark.parametrize("bad", [True, -1, 1.5, "179971"])
def test_invalid_parameter_fails_closed(bad):
    with pytest.raises(GeneratorEquivalenceError,match="P_EXACT_NONNEGATIVE"):
        compare_p_generators(bad)

def test_invalid_nesting_fails_closed():
    with pytest.raises(GeneratorEquivalenceError,match="NESTING_DEPTH"):
        compare_p_generators(7, second_depth=-1)

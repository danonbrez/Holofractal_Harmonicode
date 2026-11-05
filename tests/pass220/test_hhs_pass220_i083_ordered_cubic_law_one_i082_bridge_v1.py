"""Pass 220 I083 typed cubic Law-of-1 source extension tests."""
from __future__ import annotations

import pytest

from hhs_runtime.hhs_pass220_i083_ordered_cubic_law_one_i082_bridge_v1 import (
    CHAIN_OPERANDS,
    SOURCE_FRAGMENT,
    SOURCE_OPERATOR_OBLIGATIONS,
    I083OrderedCubicError,
    formalize_i083,
)


def test_original_ordered_chain_and_open_group_are_preserved():
    result = formalize_i083()
    assert SOURCE_FRAGMENT == "(t³=t+(m²-m)=a²+t"
    assert result["source_fragment_exact"] == SOURCE_FRAGMENT
    assert result["source_open_parenthesis_preserved"] is True
    assert result["ordered_equality_operands"] == list(CHAIN_OPERANDS)
    assert result["ordered_equality_operands"] == [
        "t³", "t+(m²-m)", "a²+t",
    ]
    assert result["equality_edge_order"] == [[0, 1], [1, 2]]
    assert result["full_source_parenthesis_closed"] is False
    assert len(result["source_identity_sha256"]) == 64
    assert result["native_operator_obligations"] == list(SOURCE_OPERATOR_OBLIGATIONS)


def test_original_pass219_law_one_and_cubic_units_are_composed_not_redefined():
    r = formalize_i083()
    assert r["inherited_cubic_original_source"] == "t³=t+a²"
    assert r["inherited_cubic_original_residual"] == "t³-t=a²=∆=1"
    assert list(r["original_law_one_receipts"]) == ["t³-t", "m²-m", "a²"]
    for witness in r["original_law_one_receipts"].values():
        assert witness["projection_value"] == {
            "type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1,
        }
        assert witness["projection_only"] is True
        assert witness["canonical_admission_authority"] is False
    assert r["projected_addend_residual"] == {"numerator": 0, "denominator": 1}
    assert r["projected_cubic_residual"] == {"numerator": 0, "denominator": 1}
    assert r["scalar_projection_units_equal"] is True
    assert r["i082_a2_cell_address"] == 7
    assert r["i082_c_root_relation"] == "c=+sqrt(a²+b²)=+sqrt(3)"


def test_native_noncommuting_additive_edge_not_scalar_cancelled():
    r = formalize_i083()
    assert r["status"] == "HOLD_NATIVE_ORDERED_EDGE_PROOF"
    assert r["native_t_plus_a2_equals_a2_plus_t_proven"] is False
    assert r["native_chain_admitted"] is False
    assert r["native_t_solved"] is False
    assert r["native_m_solved"] is False
    assert r["tensor_pair_witness_executed"] is False
    assert r["tensor_pair_three_set_receipt"] is None
    assert r["tensor_pair_provenance_independently_verified"] is False
    assert r["candidate_only"] is True
    assert r["projection_only"] is True
    assert r["canonical_vm81_mutation_authority"] is False
    assert r["canonical_hash72_commit_authority"] is False
    assert r["canonical_hash216_commit_authority"] is False


def test_existing_tensor_pair_cubic_normalizer_is_really_invoked_if_provided():
    result = formalize_i083(
        pair_layer_id="TEST:LOSHU-SOURCE-TO-TARGET",
        source_tensor_id="TEST:I082-NATIVE-SOURCE",
        target_tensor_id="TEST:I082-NATIVE-TARGET",
        source_shape=(3, 3),
        target_shape=(3, 3),
        equal_sum_normalized=True,
    )
    assert result["tensor_pair_witness_executed"] is True
    original = result["tensor_pair_three_set_receipt"]
    assert original["source_relation"] == "t³=t+a²"
    assert original["three_set"] == ["t³", "t", "a²"]
    assert original["projected_relation_residual"] == {
        "type": "EXACT_RATIONAL", "numerator": 0, "denominator": 1,
    }
    assert original["native_t_solved"] is False
    assert original["vm81_mutation_authority"] is False
    assert result["native_chain_admitted"] is False
    assert result["tensor_pair_provenance_independently_verified"] is False


def test_no_partial_or_unclosed_tensor_pair_is_accepted():
    with pytest.raises(I083OrderedCubicError, match="complete original"):
        formalize_i083(pair_layer_id="TEST:PARTIAL")
    with pytest.raises(ValueError, match="equal-sum"):
        formalize_i083(
            pair_layer_id="TEST:LOS",
            source_tensor_id="TEST:SOURCE",
            target_tensor_id="TEST:TARGET",
            source_shape=(3, 3),
            target_shape=(3, 3),
            equal_sum_normalized=False,
        )
    with pytest.raises(ValueError, match="same-sized"):
        formalize_i083(
            pair_layer_id="TEST:LOS",
            source_tensor_id="TEST:SOURCE",
            target_tensor_id="TEST:TARGET",
            source_shape=(3, 3),
            target_shape=(9,),
            equal_sum_normalized=True,
        )


def test_inherited_i070_i071_phase_gear_and_i082_c_root_remain_available():
    r = formalize_i083(phase_gear_hydration=True)
    assert r["i082_c_root_relation"] == "c=+sqrt(a²+b²)=+sqrt(3)"
    assert r["native_chain_admitted"] is False
    assert r["tensor_pair_witness_executed"] is False


def test_deterministic_source_and_original_receipts():
    first = formalize_i083()
    second = formalize_i083()
    assert first == second

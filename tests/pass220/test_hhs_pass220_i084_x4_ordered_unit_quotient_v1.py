"""I084 exact ordered x⁴/cubic-quotient/Law-of-1 projection regressions."""
from __future__ import annotations

from copy import deepcopy

import pytest

from hhs_runtime import hhs_pass220_i084_x4_ordered_unit_quotient_v1 as cycle

UNIT = {"numerator": 1, "denominator": 1}


def test_verbatim_ordered_quotient_hierarchy_does_not_reorder_or_solve():
    result = cycle.formalize_i084()
    assert result["original_source"] == "x⁴=(t³-t)/(m²-m)=a²"
    assert result["ordered_equality_operands"] == ["x⁴", "(t³-t)/(m²-m)", "a²"]
    ast = result["typed_expression"]
    assert ast["head"] == "HHS_ORDERED_EQUALITY_CHAIN"
    assert ast["directed_edges"] == [[0, 1], [1, 2]]
    assert ast["operands"][0] == {"head": "PHASE_POW", "symbol": "x", "exponent": 4}
    division = ast["operands"][1]
    assert division["head"] == "NATIVE_ORDERED_DIVISION"
    assert division["numerator"]["left"]["symbol"] == "t"
    assert division["numerator"]["right"]["symbol"] == "t"
    assert division["denominator"]["left"]["symbol"] == "m"
    assert division["denominator"]["right"]["symbol"] == "m"
    assert division["native_inverse_direction_proven"] is False
    assert ast["operands"][2] == {"head": "ROOT_ADDRESS", "symbol": "a²"}
    assert ast["native_equality_not_host_scalar_substitution"] is True


def test_registered_original_exact_witnesses_close_projected_ratio():
    result = cycle.formalize_i084()
    assert result["law_of_one_member_order"] == ["x⁴", "t³-t", "m²-m", "a²"]
    for member, witness in result["inherited_law_of_one_receipts"].items():
        assert witness["native_source_expression"] == member
        assert witness["projection_relation"] == f"pi({member})=1"
        assert witness["projection_value"] == {
            "type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1
        }
        assert witness["projection_only"] is True
        assert witness["vm81_mutation_authority"] is False
        assert witness["native_commutation_authorized"] is False
        assert witness["canonical_hash216_authority"] is False
    assert result["exact_projected_numerator"] == UNIT
    assert result["exact_projected_denominator"] == UNIT
    assert result["exact_projected_quotient"] == UNIT
    assert result["exact_projected_x4"] == UNIT
    assert result["exact_projected_a2"] == UNIT
    assert result["denominator_nonzero_in_exact_projection"] is True
    assert result["projected_quotient_unit_closed"] is True
    assert result["projected_equality_chain_closed"] is True
    assert result["x4_member_evidence_kind"] == (
        "OPERATOR_SUPPLIED_PHASE_QUARTIC_PROJECTION_AXIOM"
    )
    assert result["x4_registered_phase_quartic_axiom_is_not_native_execution"] is True


def test_previous_i083_and_i082_source_ancestry_remains_addressed():
    result = cycle.formalize_i084()
    assert result["inherited_i083_open_group"] is True
    assert result["inherited_i082_a2_cell_address"] == 7
    assert result["inherited_i082_c_geometric_root"] == "c=+sqrt(a²+b²)=+sqrt(3)"
    assert len(result["source_identity_sha256"]) == 64
    assert len(result["inherited_i083_source_identity_sha256"]) == 64
    assert result["source_identity_sha256"] != result["inherited_i083_source_identity_sha256"]


def test_original_scalar_unit_not_misrepresented_as_native_operator_proof():
    result = cycle.formalize_i084()
    assert result["status"] == "HOLD_NATIVE_ORDERED_QUOTIENT_PROOF"
    assert result["native_division_direction_verified"] is False
    assert result["native_quotient_projector_homomorphism_proven"] is False
    assert result["native_x4_equality_chain_proven"] is False
    assert result["native_x4_operator_executed"] is False
    assert result["native_source_address_phase_witness_proven"] is False
    assert result["native_chain_admitted"] is False
    assert result["projection_only"] is True
    assert result["candidate_only"] is True
    assert result["canonical_vm81_mutation_authority"] is False
    assert result["canonical_hash72_mint_authority"] is False
    assert result["canonical_hash216_mint_authority"] is False
    assert result["canonical_persistence_authority"] is False


@pytest.mark.parametrize("altered", [
    {"type": "EXACT_RATIONAL", "numerator": 0, "denominator": 1},
    {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 2},
    {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 0},
    {"type": "EXACT_RATIONAL", "numerator": 1.0, "denominator": 1},
    {"type": "EXACT_RATIONAL", "numerator": True, "denominator": 1},
    {"type": "FLOAT", "numerator": 1, "denominator": 1},
])
def test_corrupt_denominator_source_refused_before_division(monkeypatch, altered):
    original = cycle.member_witness

    def corrupt(member):
        value = deepcopy(original(member))
        if member == "m²-m":
            value["projection_value"] = altered
        return value

    monkeypatch.setattr(cycle, "member_witness", corrupt)
    with pytest.raises(cycle.I084OrderedQuotientError):
        cycle.formalize_i084()


def test_swapped_source_member_receipt_refused(monkeypatch):
    original = cycle.member_witness

    def wrong(member):
        return original("a²") if member == "x⁴" else original(member)

    monkeypatch.setattr(cycle, "member_witness", wrong)
    with pytest.raises(cycle.I084OrderedQuotientError, match="source mismatch"):
        cycle.formalize_i084()


def test_i070_i071_native_phase_geometry_optional_and_still_candidate_only():
    result = cycle.formalize_i084(hydrate_existing_phase_gear=True)
    assert result["projected_equality_chain_closed"] is True
    assert result["native_chain_admitted"] is False


def test_source_receipts_are_deterministic_on_identical_inherited_state():
    assert cycle.formalize_i084() == cycle.formalize_i084()

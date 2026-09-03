from __future__ import annotations

from pathlib import Path

import pytest

from hhs_runtime.pass219.harmonicode_modular_pivot_phase_binding import (
    HarmonicodeModularPivotError,
    build_phase_lane,
    execute_i159_modular_pivot_phase_bindings,
    i159_modular_pivot_self_test,
    prove_p_fold_closure_to_renewed_unit,
    prove_renewed_unit_phase_class_join,
    verify_pass157_modular_normalization_profile,
)
from hhs_runtime.pass219.typed_full_symbolic_candidate_values import (
    CANDIDATE_SCHEMA,
    COMBINED_SOURCE_SHA256,
    PROVENANCE_SCHEMA,
    produce_candidate_bound_value_graph,
)


def _snapshot() -> dict[str, object]:
    return {
        "schema": "HHS_PASS219_I153_LOCAL_HASH216_5184_P_SNAPSHOT_V1",
        "snapshot_hash216": "2" * 64,
        "snapshot_hash216_format": "PASS150_HASH216_GENOME_ROOT_SHA256",
        "P": 30,
        "hydration_bits": 5184,
    }


def _provenance() -> dict[str, object]:
    return {
        "schema": PROVENANCE_SCHEMA,
        "combined_source_sha256": COMBINED_SOURCE_SHA256,
        "source_hash216": "0" * 216,
        "tokens_hash216": "1" * 216,
        "cst_hash216": "2" * 216,
        "ast_hash216": "3" * 216,
        "type_environment_hash216": "4" * 216,
        "constraint_graph_hash216": "5" * 216,
        "hir_hash216": "6" * 216,
        "vmir_hash216": "7" * 216,
        "global_symbol_environment_root": "b" * 64,
        "source_identity_exact": True,
        "gate_occurrence_provenance_exact": True,
        "frontend_chain_complete": True,
        "source_root_lineage_exact": True,
        "pass159_whole_expression_provenance_verified": True,
        "boolean_gate_results_available": False,
        "membrane_input_ready": False,
        "canonical_monolithic_proof": False,
        "floating_point_authority": False,
        "vm81_mutation_authority": False,
        "hash72_commit_authority": False,
        "persistence_mutation_authority": False,
    }


def _symbols(*, m: int = 267) -> dict[str, object]:
    return {
        "schema": CANDIDATE_SCHEMA,
        "P": 30,
        "p": 29,
        "q": 31,
        "t": 30,
        "m": m,
        "s": {"numerator": 2, "denominator": 25},
        "f": 900,
        "At": 1,
        "Bt": 1,
        "x": 18,
        "y": 54,
        "z": 18,
        "w": 54,
    }


def _graph(*, m: int = 267) -> dict[str, object]:
    return produce_candidate_bound_value_graph(
        _snapshot(), _provenance(), _symbols(m=m)
    )


def test_pass157_modular_profile_is_bound_to_typed_ast_and_contract() -> None:
    profile = verify_pass157_modular_normalization_profile()
    assert profile["typed_node"] == {
        "node": "HHS_MODULAR_NORMALIZATION",
        "authority": "P^2",
        "state": "pq",
    }
    assert profile["phase_identity"] == "n=q*M+r; 0<=r<M"
    assert profile["quotient_retained"] is True
    assert profile["residue_retained"] is True
    assert profile["residue_only_authority"] is False
    assert profile["ordinary_scalar_equality_claimed"] is False
    assert all(profile["checks"].values())
    assert len(profile["profile_sha256"]) == 64
    assert all(
        len(row["sha256"]) == 64
        for row in profile["repository_sources"].values()
    )


def test_full_phase_lanes_retain_quotient_and_residue() -> None:
    left = build_phase_lane(26970, 899)
    authority = build_phase_lane(900, 899)
    right = build_phase_lane(71022, 899)
    assert (left["quotient"], left["residue"], left["phase_class"]) == (
        30,
        0,
        "CLOSURE_RESIDUE",
    )
    assert (
        authority["quotient"],
        authority["residue"],
        authority["phase_class"],
    ) == (1, 1, "RENEWED_UNIT")
    assert (right["quotient"], right["residue"], right["phase_class"]) == (
        79,
        1,
        "RENEWED_UNIT",
    )
    for lane in (left, authority, right):
        assert lane["reconstruction_exact"] is True
        assert lane["quotient_retained"] is True
        assert lane["residue_retained"] is True
        assert lane["residue_only_authority"] is False


def test_edge2_closure_to_renewed_unit_is_exact_typed_relation() -> None:
    profile = verify_pass157_modular_normalization_profile()
    witness = prove_p_fold_closure_to_renewed_unit(
        P=30,
        modulus=899,
        left_value=26970,
        authority_value=900,
        candidate_binding_sha256="a" * 64,
        profile_sha256=profile["profile_sha256"],
    )
    assert witness["status"] == "PROVED"
    assert witness["relation"] == "P_FOLD_CLOSURE_TO_RENEWED_UNIT"
    assert witness["left_lane"]["quotient"] == 30
    assert witness["left_lane"]["residue"] == 0
    assert witness["authority_lane"]["quotient"] == 1
    assert witness["authority_lane"]["residue"] == 1
    assert all(witness["checks"].values())
    assert witness["ordinary_scalar_identity_claimed"] is False
    assert witness["ordinary_scalar_zero_equals_one_claimed"] is False
    assert witness["full_phase_lane_identity_claimed"] is False
    assert witness["typed_relation_only"] is True


def test_edge2_rejects_if_full_fold_quotient_is_not_P() -> None:
    profile = verify_pass157_modular_normalization_profile()
    witness = prove_p_fold_closure_to_renewed_unit(
        P=30,
        modulus=899,
        left_value=29 * 899,
        authority_value=900,
        candidate_binding_sha256="a" * 64,
        profile_sha256=profile["profile_sha256"],
    )
    assert witness["status"] == "REJECTED"
    assert witness["checks"]["left_quotient_is_P"] is False
    assert witness["checks"]["left_exactly_P_full_periods"] is False


def test_edge3_renewed_unit_join_retains_right_fold_quotient() -> None:
    profile = verify_pass157_modular_normalization_profile()
    witness = prove_renewed_unit_phase_class_join(
        modulus=899,
        authority_value=900,
        right_value=71022,
        m=267,
        candidate_binding_sha256="b" * 64,
        profile_sha256=profile["profile_sha256"],
    )
    assert witness["status"] == "PROVED"
    assert witness["relation"] == "RENEWED_UNIT_PHASE_CLASS_JOIN"
    assert witness["authority_lane"]["quotient"] == 1
    assert witness["right_lane"]["quotient"] == 79
    assert witness["right_lane"]["residue"] == 1
    assert all(witness["checks"].values())
    assert witness["same_residue_is_sufficient_authority"] is False
    assert witness["full_phase_lane_identity_claimed"] is False
    assert witness["typed_phase_class_relation_only"] is True


def test_same_residue_without_m_binding_is_not_sufficient() -> None:
    profile = verify_pass157_modular_normalization_profile()
    witness = prove_renewed_unit_phase_class_join(
        modulus=899,
        authority_value=900,
        right_value=2 * 899 + 1,
        m=267,
        candidate_binding_sha256="b" * 64,
        profile_sha256=profile["profile_sha256"],
    )
    assert witness["right_lane"]["residue"] == 1
    assert witness["status"] == "REJECTED"
    assert witness["checks"]["right_is_exact_m2_minus_m"] is False
    assert witness["same_residue_is_sufficient_authority"] is False


def test_i159_resolves_exactly_two_modular_pivots() -> None:
    result = execute_i159_modular_pivot_phase_bindings(_graph())
    assert result["decision"] == "PARTIALLY_RESOLVED_TYPED_GRAPH"
    assert result["counts"] == {
        "join_count": 10,
        "proved": 7,
        "unresolved": 3,
        "rejected": 0,
        "newly_resolved_modular_pivots": 2,
    }
    assert result["executed_joins"][2]["execution_status"] == "PROVED"
    assert result["executed_joins"][3]["execution_status"] == "PROVED"
    assert (
        result["executed_joins"][2]["execution_reason"]
        == "EXACT_TYPED_CLOSURE_RESIDUE_TO_RENEWED_UNIT_PIVOT"
    )
    assert (
        result["executed_joins"][3]["execution_reason"]
        == "EXACT_TYPED_RENEWED_UNIT_PHASE_CLASS_JOIN"
    )
    assert result["remaining_blockers"] == [
        {
            "edge_index": 7,
            "join_kind": "AB_ROOT_CORRESPONDENCE",
            "reason": "BOUNDARY_PRODUCT_BINDING_REQUIRED",
        },
        {
            "edge_index": 8,
            "join_kind": "MONOLITHIC_BOUNDARY_EQUALITY",
            "reason": "COMPLETE_MONOLITHIC_BOUNDARY_EXECUTOR_REQUIRED",
        },
        {
            "edge_index": 9,
            "join_kind": "DELTA_RADICAL_PROJECTION",
            "reason": "PASS191_X_SQUARED_PHASE_BINDING_REQUIRED",
        },
    ]


def test_i159_does_not_use_conventional_projection_as_authority() -> None:
    result = execute_i159_modular_pivot_phase_bindings(_graph())
    guards = result["semantic_guards"]
    assert guards == {
        "conventional_modular_projection_used_as_authority": False,
        "ordinary_scalar_equality_claimed": False,
        "ordinary_scalar_zero_equals_one_claimed": False,
        "residue_only_authority": False,
        "quotients_retained": True,
        "full_phase_lane_identity_claimed": False,
        "typed_phase_relation_only": True,
    }
    # I158's diagnostic mismatch remains part of inherited provenance.
    assert (
        result["inherited_i158_execution_membrane_sha256"]
        == execute_i159_modular_pivot_phase_bindings(_graph())[
            "inherited_i158_execution_membrane_sha256"
        ]
    )


def test_bad_m_candidate_rejects_registered_edge3_adapter() -> None:
    result = execute_i159_modular_pivot_phase_bindings(_graph(m=268))
    assert result["decision"] == "REJECTED"
    assert result["executed_joins"][2]["execution_status"] == "PROVED"
    assert result["executed_joins"][3]["execution_status"] == "REJECTED"
    assert result["counts"]["rejected"] == 1
    assert result["next_boundary"] == "REPAIR_REJECTED_MODULAR_PIVOT"


def test_i157_graph_tamper_is_still_rejected_upstream() -> None:
    graph = _graph()
    graph["value_nodes"][3]["payload"]["modulus"] = 900
    with pytest.raises(
        TypedDomainExecutionError,
        match="I157_GRAPH_SHA256_MISMATCH",
    ):
        execute_i159_modular_pivot_phase_bindings(graph)


def test_authority_stays_below_vm81_and_pass169_terminal_proof() -> None:
    result = execute_i159_modular_pivot_phase_bindings(_graph())
    authority = result["authority"]
    assert authority["typed_modular_pivot_profile_registered"] is True
    assert authority["typed_modular_pivots_resolved"] is True
    assert authority["typed_join_execution_complete"] is False
    assert authority["canonical_monolithic_boundary_proof"] is False
    assert authority["pass169_terminal_proof"] is False
    assert authority["vm81_execution_verified"] is False
    assert authority["vm81_mutation_authority"] is False
    assert authority["hash72_execution_receipt_verified"] is False
    assert authority["hash72_mint_authority"] is False
    assert authority["hash216_persistence_authority"] is False
    assert authority["deterministic_replay_verified"] is False
    assert authority["floating_point_authority"] is False
    assert (
        result["next_boundary"]
        == "SOURCE_BOUND_AB_PRODUCT_AND_X2_PHASE_EXPONENT_BINDINGS"
    )


def test_i159_is_deterministic() -> None:
    first = execute_i159_modular_pivot_phase_bindings(_graph())
    second = execute_i159_modular_pivot_phase_bindings(_graph())
    assert first == second
    assert len(first["i159_execution_sha256"]) == 64


def test_public_self_test() -> None:
    receipt = i159_modular_pivot_self_test()
    assert receipt["ok"] is True
    assert receipt["decision"] == "PARTIALLY_RESOLVED_TYPED_GRAPH"
    assert receipt["proved"] == 7
    assert receipt["unresolved"] == 3
    assert receipt["rejected"] == 0
    assert receipt["newly_resolved_modular_pivots"] == 2
    assert receipt["left_lane"]["quotient"] == 30
    assert receipt["left_lane"]["residue"] == 0
    assert receipt["authority_lane"]["quotient"] == 1
    assert receipt["authority_lane"]["residue"] == 1
    assert receipt["right_lane"]["quotient"] == 79
    assert receipt["right_lane"]["residue"] == 1
    assert receipt["canonical_monolithic_boundary_proof"] is False
    assert receipt["vm81_mutation_authority"] is False
    assert receipt["hash72_mint_authority"] is False
    assert receipt["hash216_persistence_authority"] is False


def test_new_surface_has_no_approximate_or_scalar_collapse_path() -> None:
    path = (
        Path(__file__).resolve().parents[2]
        / "hhs_runtime/pass219/harmonicode_modular_pivot_phase_binding.py"
    )
    text = path.read_text(encoding="utf-8")
    for forbidden in (
        "float(",
        "math.sqrt",
        "numpy",
        "isclose",
        "tolerance",
    ):
        assert forbidden not in text
    assert "residue_only_authority" in text
    assert "ordinary_scalar_identity_claimed" in text
    assert "ordinary_scalar_zero_equals_one_claimed" in text
    assert "P_FOLD_CLOSURE_TO_RENEWED_UNIT" in text
    assert "RENEWED_UNIT_PHASE_CLASS_JOIN" in text

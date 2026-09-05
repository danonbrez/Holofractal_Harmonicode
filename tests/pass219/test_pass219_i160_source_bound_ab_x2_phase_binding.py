from __future__ import annotations

from copy import deepcopy

import pytest

from hhs_runtime.pass219.source_bound_ab_x2_phase_binding import (
    SourceBoundBindingError,
    _self_test_graph,
    execute_i160_source_bound_bindings,
    i160_source_bound_binding_self_test,
    prove_pass191_x_squared_phase_exponent,
    prove_source_bound_ab_product,
    verify_pass191_source_binding_profile,
)


def test_i160_source_bound_self_test_closes_two_and_leaves_boundary_fail_closed() -> None:
    row = i160_source_bound_binding_self_test()
    assert row["ok"] is True
    assert row["counts"] == {
        "join_count": 10,
        "proved": 9,
        "unresolved": 1,
        "rejected": 0,
        "newly_resolved_source_bound_bindings": 2,
    }
    assert row["next_boundary"] == "COMPLETE_MONOLITHIC_BOUNDARY_EXECUTOR"
    assert row["remaining_blockers"] == [
        {
            "edge_index": 8,
            "join_kind": "MONOLITHIC_BOUNDARY_EQUALITY",
            "reason": "COMPLETE_MONOLITHIC_BOUNDARY_EXECUTOR_REQUIRED",
        }
    ]


def test_i160_inherits_product_membrane_without_redefining_A_or_B() -> None:
    graph = _self_test_graph()
    profile = verify_pass191_source_binding_profile()
    witness = prove_source_bound_ab_product(
        P=30,
        ratio_node=graph["value_nodes"][9],
        radical_node=graph["value_nodes"][10],
        candidate_binding_sha256=graph["candidate_binding_sha256"],
        profile_sha256=profile["profile_sha256"],
    )
    assert witness["status"] == "PROVED"
    assert witness["AB"] == 30**4
    assert witness["AB_over_P2"] == {"numerator": 900, "denominator": 1}
    assert witness["sqrt_AB"] == 900
    assert witness["boundary_product_binding_only"] is True
    assert witness["ordinary_scalar_A_equals_P2_claimed"] is False
    assert witness["ordinary_scalar_B_equals_P2_claimed"] is False


def test_i160_phase_square_retains_dyadic_coordinate_but_uses_ordered_basis_lane() -> None:
    graph = _self_test_graph()
    profile = verify_pass191_source_binding_profile()
    witness = prove_pass191_x_squared_phase_exponent(
        P=30,
        p=29,
        q=31,
        delta=1,
        left_node=graph["value_nodes"][13],
        radical_node=graph["value_nodes"][14],
        candidate_binding_sha256=graph["candidate_binding_sha256"],
        profile_sha256=profile["profile_sha256"],
    )
    assert witness["status"] == "PROVED"
    assert witness["phase_square"]["input"]["basis"] == "i"
    assert witness["phase_square"]["output"]["basis"] == "-1"
    assert witness["phase_square"]["output"]["dyadic_level"] == 1
    assert witness["phase_square"]["output"]["dyadic_magnitude"] == "2"
    assert witness["phase_square"]["ordered_phase_basis_exponent"] == -1
    assert witness["phase_square"]["dyadic_magnitude_used_as_scalar_exponent"] is False
    assert witness["right_phase_radical"] == {"numerator": 1, "denominator": 30}
    assert witness["ordinary_scalar_x_squared_assumed"] is False
    assert witness["ordinary_18_squared_used"] is False
    assert witness["pass191_dyadic_coordinate_discarded"] is False


def test_i160_rejects_definitional_A_or_B_equals_P2_shortcut() -> None:
    graph = _self_test_graph()
    ratio = deepcopy(graph["value_nodes"][9])
    ratio["payload"]["A_or_B_definitionally_P2"] = True
    profile = verify_pass191_source_binding_profile()
    with pytest.raises(SourceBoundBindingError, match="A_OR_B_DEFINITIONALLY_P2_FORBIDDEN"):
        prove_source_bound_ab_product(
            P=30,
            ratio_node=ratio,
            radical_node=graph["value_nodes"][10],
            candidate_binding_sha256=graph["candidate_binding_sha256"],
            profile_sha256=profile["profile_sha256"],
        )


def test_i160_rejects_nonreal_phase_basis_exponent_in_adapter() -> None:
    graph = _self_test_graph()
    radical = deepcopy(graph["value_nodes"][14])
    radical["payload"]["phase_exponent"]["x_phase"] = 0
    profile = verify_pass191_source_binding_profile()
    with pytest.raises(SourceBoundBindingError, match="X2_PHASE_BASIS_NOT_REAL_INTEGER"):
        prove_pass191_x_squared_phase_exponent(
            P=30,
            p=29,
            q=31,
            delta=1,
            left_node=graph["value_nodes"][13],
            radical_node=radical,
            candidate_binding_sha256=graph["candidate_binding_sha256"],
            profile_sha256=profile["profile_sha256"],
        )


def test_i160_boundary_audit_does_not_promote_zero_projection_to_equality() -> None:
    row = execute_i160_source_bound_bindings(_self_test_graph())
    audit = row["boundary_blocker_audit"]
    assert audit["status"] == "UNRESOLVED"
    assert audit["reason"] == "COMPLETE_MONOLITHIC_BOUNDARY_EXECUTOR_REQUIRED"
    assert audit["known_exact_relations"]["right_closure_numerator"] == {
        "numerator": 0,
        "denominator": 1,
    }
    assert audit["known_exact_relations"]["right_conventional_scalar_projection"] == {
        "numerator": 0,
        "denominator": 1,
    }
    assert audit["ordinary_scalar_boundary_equality_claimed"] is False
    assert audit["right_scalar_zero_promoted_to_typed_boundary_identity"] is False
    assert audit["typed_zero_boundary_rule_invented"] is False
    assert row["authority"]["complete_monolithic_boundary_executor_registered"] is False
    assert row["authority"]["typed_join_execution_complete"] is False


def test_i160_source_profile_is_additive_over_pass191() -> None:
    profile = verify_pass191_source_binding_profile()
    assert profile["checks"]["pass191_historical_x2_binding_remains_unresolved"] is True
    assert profile["historical_A_equals_P2_reused_as_full_boundary_definition"] is False
    assert profile["historical_B_equals_P2_reused_as_full_boundary_definition"] is False
    assert profile["inherited_AB_equals_P4_used_as_product_membrane_only"] is True
    assert profile["pass191_source_rewritten"] is False
    assert profile["floating_point_authority"] is False

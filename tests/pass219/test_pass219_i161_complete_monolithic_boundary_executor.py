from __future__ import annotations

from copy import deepcopy

import pytest

from hhs_runtime.pass219.complete_monolithic_boundary_executor import (
    CompleteBoundaryExecutorError,
    execute_i161_complete_monolithic_boundary,
    i161_complete_monolithic_boundary_self_test,
    prove_complete_monolithic_boundary,
    prove_renewed_unit_closure_relation,
    prove_scalar_zero_phase_relation,
    verify_i161_typed_zero_renewed_unit_profile,
)
from hhs_runtime.pass219.source_bound_ab_x2_phase_binding import (
    _self_test_graph,
    execute_i160_source_bound_bindings,
)


def test_i161_profile_binds_inherited_typed_zero_sources() -> None:
    profile = verify_i161_typed_zero_renewed_unit_profile()
    assert all(profile["checks"].values())
    assert profile["zero_fourth_operator"] == "TYPED_FOURTH_PHASE_CLOSURE"
    assert profile["zero_fourth_host_scalar_pow"] is False
    assert profile["xy_over_zw_operator"] == "TYPED_CLOSURE_QUOTIENT"
    assert profile["xy_over_zw_host_zero_division"] is False
    assert profile["scalar_zero_equals_scalar_one"] is False


def test_scalar_zero_is_exact_phase_projection_without_type_collapse() -> None:
    graph = _self_test_graph()
    profile = verify_i161_typed_zero_renewed_unit_profile()
    witness = prove_scalar_zero_phase_relation(
        graph["symbol_environment"]["phase_state"],
        profile_sha256=profile["profile_sha256"],
    )
    assert witness["status"] == "PROVED"
    assert witness["xyzw_sum_coefficients"] == [0, 0]
    assert witness["I_plus_I3_coefficients"] == [0, 0]
    assert witness["scalar_zero_equals_scalar_one"] is False


def test_renewed_unit_closure_never_executes_zero_division_or_scalar_zero_fourth_power() -> None:
    graph = _self_test_graph()
    env = graph["symbol_environment"]
    profile = verify_i161_typed_zero_renewed_unit_profile()
    scalar_zero = prove_scalar_zero_phase_relation(
        env["phase_state"],
        profile_sha256=profile["profile_sha256"],
    )
    witness = prove_renewed_unit_closure_relation(
        P=env["P"],
        p=env["p"],
        q=env["q"],
        phase_state=env["phase_state"],
        scalar_zero_witness=scalar_zero,
        profile_sha256=profile["profile_sha256"],
    )
    assert witness["status"] == "PROVED"
    assert witness["typed_views"]["u^0"]["projection"] == 1
    assert witness["typed_views"]["xy_over_zw"]["host_division_used"] is False
    assert witness["typed_views"]["zero_fourth"]["host_scalar_pow_used"] is False
    assert witness["scalar_zero_equals_scalar_one"] is False

    with pytest.raises(CompleteBoundaryExecutorError, match="HOST_ZERO_DIVISION_FORBIDDEN"):
        prove_renewed_unit_closure_relation(
            P=env["P"],
            p=env["p"],
            q=env["q"],
            phase_state=env["phase_state"],
            scalar_zero_witness=scalar_zero,
            profile_sha256=profile["profile_sha256"],
            use_host_zero_division=True,
        )
    with pytest.raises(CompleteBoundaryExecutorError, match="HOST_ZERO_FOURTH_POWER_FORBIDDEN"):
        prove_renewed_unit_closure_relation(
            P=env["P"],
            p=env["p"],
            q=env["q"],
            phase_state=env["phase_state"],
            scalar_zero_witness=scalar_zero,
            profile_sha256=profile["profile_sha256"],
            use_host_zero_pow=True,
        )


def test_scalar_zero_relation_fails_closed_when_xyzw_phase_sum_is_not_zero() -> None:
    graph = _self_test_graph()
    phase = deepcopy(graph["symbol_environment"]["phase_state"])
    phase["x"] = 0
    profile = verify_i161_typed_zero_renewed_unit_profile()
    witness = prove_scalar_zero_phase_relation(
        phase,
        profile_sha256=profile["profile_sha256"],
    )
    assert witness["status"] == "REJECTED"
    assert witness["checks"]["xyzw_scalar_phase_projection_is_zero"] is False


def test_boundary_adapter_forbids_ordinary_scalar_equality_claim() -> None:
    graph = _self_test_graph()
    i160 = execute_i160_source_bound_bindings(graph)
    env = graph["symbol_environment"]
    profile = verify_i161_typed_zero_renewed_unit_profile()
    scalar_zero = prove_scalar_zero_phase_relation(
        env["phase_state"],
        profile_sha256=profile["profile_sha256"],
    )
    renewed = prove_renewed_unit_closure_relation(
        P=env["P"],
        p=env["p"],
        q=env["q"],
        phase_state=env["phase_state"],
        scalar_zero_witness=scalar_zero,
        profile_sha256=profile["profile_sha256"],
    )
    with pytest.raises(
        CompleteBoundaryExecutorError,
        match="ORDINARY_SCALAR_BOUNDARY_EQUALITY_FORBIDDEN",
    ):
        prove_complete_monolithic_boundary(
            graph,
            i160,
            scalar_zero_witness=scalar_zero,
            renewed_unit_witness=renewed,
            profile_sha256=profile["profile_sha256"],
            claim_ordinary_scalar_equality=True,
        )


def test_i161_resolves_only_final_typed_join_and_preserves_downstream_authority_gates() -> None:
    row = execute_i161_complete_monolithic_boundary(_self_test_graph())
    assert row["counts"] == {
        "join_count": 10,
        "proved": 10,
        "unresolved": 0,
        "rejected": 0,
        "newly_resolved_complete_boundary_bindings": 1,
    }
    edge8 = row["executed_joins"][8]
    assert edge8["execution_status"] == "PROVED"
    assert edge8["i161_typed_profile"] == "TYPED_MONOLITHIC_BOUNDARY_CLOSURE_EQUIVALENCE"
    assert row["boundary_witness"]["equality_frame"] == "CLOSURE_EQ"
    assert row["boundary_witness"]["ordinary_scalar_A_equals_B_claimed"] is False
    assert row["authority"]["canonical_monolithic_boundary_proof"] is True
    assert row["authority"]["pass169_terminal_proof"] is False
    assert row["authority"]["vm81_execution_verified"] is False
    assert row["authority"]["vm81_mutation_authority"] is False
    assert row["authority"]["hash72_mint_authority"] is False
    assert row["authority"]["hash216_persistence_authority"] is False
    assert row["next_boundary"] == "PASS169_VM81_EXACT_SYMBOLIC_CONSTRAINT_EXECUTION"


def test_i161_public_self_test() -> None:
    row = i161_complete_monolithic_boundary_self_test()
    assert row["ok"] is True
    assert row["result"] == "PASS"

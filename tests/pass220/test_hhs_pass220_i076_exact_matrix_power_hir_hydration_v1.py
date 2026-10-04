from __future__ import annotations

import copy

import pytest

from hhs_runtime.hhs_pass220_i076_exact_matrix_power_hir_hydration_v1 import (
    AUTHORITY_BOUNDARY,
    HIR_NODE_KIND,
    PASS169_CANONICAL_TYPE,
    PASS169_CONTRACT_ID,
    Pass220I076Error,
    build_candidate,
    exact_matrix_power_hir_nodes,
    hir_lowering_descriptor,
    self_test,
    validate_candidate,
)


def test_exact_matrix_power_hir_nodes_preserve_source_identity() -> None:
    nodes = exact_matrix_power_hir_nodes()
    assert len(nodes) == 2
    assert [row["canonical_pass169_type"] for row in nodes] == [
        PASS169_CANONICAL_TYPE,
        PASS169_CANONICAL_TYPE,
    ]
    assert [row["node_kind"] for row in nodes] == [HIR_NODE_KIND, HIR_NODE_KIND]
    assert [row["pass169_contract_id"] for row in nodes] == [
        PASS169_CONTRACT_ID,
        PASS169_CONTRACT_ID,
    ]
    assert [row["source_node"] for row in nodes] == [
        "MatrixPower[M_wz,x^2]",
        "MatrixPower[M_xy,x^4]",
    ]
    assert [row["base_shape"] for row in nodes] == [(4, 2), (4, 2)]
    assert [row["exponent_token"] for row in nodes] == ["x^2", "x^4"]


def test_hir_nodes_do_not_claim_host_or_vm81_execution() -> None:
    for row in exact_matrix_power_hir_nodes():
        assert row["source_identity_preserved"] is True
        assert row["ordered_cell_topology_preserved"] is True
        assert row["exact_symbolic_node"] is True
        assert row["host_matrixpower_evaluated"] is False
        assert row["host_square_matrix_requirement_imported"] is False
        assert row["numeric_exponent_evaluated"] is False
        assert row["matrix_power_value_derived"] is False
        assert row["vm81_execution_verified"] is False
        assert row["vm81_admission_required"] is True
        assert row["candidate_only"] is True


def test_hir_descriptor_is_exact_and_compact() -> None:
    descriptor = hir_lowering_descriptor()
    assert descriptor["canonical_type"] == "ExactMatrixPower"
    assert descriptor["node_kind"] == "EXACT_SYMBOLIC_MATRIX_POWER"
    assert descriptor["node_count"] == 2
    assert descriptor["rectangular_shapes"] == ((4, 2), (4, 2))
    assert descriptor["source_nodes"] == (
        "MatrixPower[M_wz,x^2]",
        "MatrixPower[M_xy,x^4]",
    )
    assert descriptor["exponent_tokens"] == ("x^2", "x^4")
    assert descriptor["host_matrixpower_evaluations"] == 0
    assert descriptor["numeric_exponent_evaluations"] == 0
    assert descriptor["matrix_power_values_derived"] == 0
    assert descriptor["vm81_executions_verified"] == 0
    assert descriptor["vm81_admission_required"] is True
    assert len(descriptor["hir_node_roots_sha256"]) == 2
    assert len(descriptor["hir_forest_root_sha256"]) == 64


def test_candidate_hash216_hydration_is_exact() -> None:
    candidate = build_candidate()
    assert validate_candidate(candidate)
    assert len(candidate["candidate_previous_hash72"]) == 72
    assert len(candidate["candidate_change_hash72"]) == 72
    assert len(candidate["candidate_receipt_hash72"]) == 72
    assert len(candidate["candidate_hash216"]) == 216
    assert candidate["candidate_hash216"] == (
        candidate["candidate_previous_hash72"]
        + candidate["candidate_change_hash72"]
        + candidate["candidate_receipt_hash72"]
    )
    assert candidate["hydration"]["roundtrip_exact"] is True
    assert candidate["hydration"]["full_attached_components"] == 15552
    assert candidate["hydration"]["expanded_geometry_persisted"] is False
    assert len(candidate["plane_roots"]) == 3


def test_authority_boundary_is_fail_closed() -> None:
    assert AUTHORITY_BOUNDARY["candidate_only"] is True
    assert AUTHORITY_BOUNDARY["exact_matrix_power_hir_typed"] is True
    assert AUTHORITY_BOUNDARY["source_identity_preserved"] is True
    assert AUTHORITY_BOUNDARY["ordered_cell_topology_preserved"] is True
    assert AUTHORITY_BOUNDARY["host_matrixpower_authority"] is False
    assert AUTHORITY_BOUNDARY["host_square_matrix_requirement_authority"] is False
    assert AUTHORITY_BOUNDARY["numeric_exponent_evaluation_authority"] is False
    assert AUTHORITY_BOUNDARY["matrix_power_value_derivation_authority"] is False
    assert AUTHORITY_BOUNDARY["vm81_execution_verified"] is False
    assert AUTHORITY_BOUNDARY["vm81_admission_verified"] is False
    assert AUTHORITY_BOUNDARY["canonical_vm81_mutation_authority"] is False
    assert AUTHORITY_BOUNDARY["canonical_hash72_commit_authority"] is False
    assert AUTHORITY_BOUNDARY["canonical_hash216_commit_authority"] is False
    assert AUTHORITY_BOUNDARY["canonical_hash216_persistence_authority"] is False


def test_mutated_hir_node_fails_closed() -> None:
    candidate = build_candidate()
    mutated = copy.deepcopy(candidate)
    mutated["hir_lowering"]["nodes"][0]["canonical_pass169_type"] = "HostMatrixPower"
    with pytest.raises(Pass220I076Error):
        validate_candidate(mutated)


def test_self_test_passes() -> None:
    report = self_test()
    assert report["status"] == "PASS"
    assert report["check_count"] == report["pass_count"]
    assert report["failed"] == []

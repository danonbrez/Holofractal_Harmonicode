from __future__ import annotations

import copy

import pytest

from hhs_runtime.hhs_pass220_i075_native_rectangular_tensor_power_hydration_v1 import (
    AUTHORITY_BOUNDARY,
    Pass220I075Error,
    build_candidate,
    native_tensor_power_nodes,
    self_test,
    tensor_power_hydration_descriptor,
    validate_candidate,
)


def test_native_tensor_power_nodes_are_typed_and_held() -> None:
    nodes = native_tensor_power_nodes()
    assert len(nodes) == 2
    assert [node.base_role for node in nodes] == ["M_WZ", "M_XY"]
    assert [node.exponent_token for node in nodes] == ["x^2", "x^4"]
    for node in nodes:
        assert node.operator == "HARMONICODE_RECTANGULAR_TENSOR_POWER"
        assert (node.rows, node.columns) == (4, 2)
        assert node.host_evaluated is False
        assert node.numeric_exponent_evaluated is False
        assert len(node.ordered_cells) == 4
        assert all(len(row) == 2 for row in node.ordered_cells)


def test_descriptor_preserves_all_source_occurrences() -> None:
    descriptor = tensor_power_hydration_descriptor()
    assert descriptor["node_count"] == 2
    assert descriptor["rectangular_shapes"] == ((4, 2), (4, 2))
    assert descriptor["cell_occurrences"] == 16
    assert descriptor["all_occurrence_witnesses_retained"] is True
    assert descriptor["host_matrixpower_evaluations"] == 0
    assert descriptor["numeric_exponent_evaluations"] == 0
    assert descriptor["source_nodes_reconstructible"] is True
    assert len(descriptor["occurrence_ids"]) == 16


def test_candidate_hash216_and_hydration_close_exactly() -> None:
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
    assert candidate["hydration"]["reconstructible_on_demand"] is True


def test_parent_i074_is_bound() -> None:
    candidate = build_candidate()
    parent = candidate["parent_i074"]
    assert len(parent["binding_hash72"]) == 72
    assert len(parent["candidate_hash216"]) == 216
    assert len(parent["candidate_root_sha256"]) == 64
    assert parent["authority"]["candidate_only"] is True


def test_authority_is_not_widened() -> None:
    assert AUTHORITY_BOUNDARY["candidate_only"] is True
    assert AUTHORITY_BOUNDARY["native_rectangular_tensor_power_typed"] is True
    assert AUTHORITY_BOUNDARY["host_matrixpower_authority"] is False
    assert AUTHORITY_BOUNDARY["host_rectangular_matrixpower_authority"] is False
    assert AUTHORITY_BOUNDARY["numeric_exponent_evaluation_authority"] is False
    assert AUTHORITY_BOUNDARY["projection_substitution_authorized"] is False
    assert AUTHORITY_BOUNDARY["floating_point_authority"] is False
    assert AUTHORITY_BOUNDARY["canonical_vm81_mutation_authority"] is False
    assert AUTHORITY_BOUNDARY["canonical_hash72_commit_authority"] is False
    assert AUTHORITY_BOUNDARY["canonical_hash216_commit_authority"] is False
    assert AUTHORITY_BOUNDARY["canonical_hash216_persistence_authority"] is False


def test_mutation_fails_closed() -> None:
    candidate = build_candidate()
    mutated = copy.deepcopy(candidate)
    mutated["tensor_power_descriptor"]["nodes"][0]["host_evaluated"] = True
    with pytest.raises(Pass220I075Error):
        validate_candidate(mutated)


def test_self_test_passes() -> None:
    report = self_test()
    assert report["status"] == "PASS"
    assert report["check_count"] == report["pass_count"]
    assert report["failed"] == []

from __future__ import annotations

import copy

import pytest

from hhs_runtime.hhs_pass220_i074_full_tensor_hnan_closure_hydration_v1 import (
    AUTHORITY_BOUNDARY,
    CLOSURE_MATRIX,
    E_MEMBRANE_SOURCE,
    MATRIX_POWER_NODES,
    M_WZ,
    M_XY,
    Pass220I074Error,
    TARGET_MATRIX,
    VERBATIM_SOURCE,
    build_candidate,
    closure_witness,
    left_generator_witness,
    right_symbolic_cse_witness,
    self_test,
    source_bundle_witness,
    validate_candidate,
)


def test_verbatim_full_tensor_surface_is_preserved() -> None:
    assert VERBATIM_SOURCE.startswith("u^((")
    assert VERBATIM_SOURCE.endswith("==1)")
    assert VERBATIM_SOURCE.count(E_MEMBRANE_SOURCE) == 3
    assert VERBATIM_SOURCE.count("MatrixPower(") == 2
    assert "/u/(x*y)" in VERBATIM_SOURCE
    assert "/(w*z)" in VERBATIM_SOURCE
    assert "==0),1)" in VERBATIM_SOURCE


def test_left_i069_generator_closes_exactly() -> None:
    witness = left_generator_witness()
    assert all(witness["checks"].values())
    assert witness["phase_kernel"] == ((8, 1, 3), (1, 3, 5), (3, 5, 7))
    assert witness["determinants"] == (-18432, 18432, 32256)
    assert witness["normalized_determinants"] == (-36, 36, 63)
    assert witness["matrix_c"][1][1] == 72
    assert witness["e_membrane"]["source_occurrences"] == 3
    assert witness["e_membrane"]["value_nodes"] == 1
    assert witness["e_membrane"]["value_evaluations_avoided"] == 2


def test_right_symbolic_matrices_remain_held_4x2_nodes() -> None:
    for matrix in (M_WZ, M_XY, TARGET_MATRIX, CLOSURE_MATRIX):
        assert len(matrix) == 4
        assert all(len(row) == 2 for row in matrix)
    witness = right_symbolic_cse_witness()
    assert witness["matrix_shapes"] == ((4, 2), (4, 2), (4, 2), (4, 2))
    assert witness["matrix_power_nodes"] == MATRIX_POWER_NODES
    assert witness["matrix_power_host_evaluated"] is False
    assert witness["rectangular_matrixpower_promoted_to_host_semantics"] is False


def test_right_symbolic_cse_is_lossless_and_witness_preserving() -> None:
    witness = right_symbolic_cse_witness()
    assert witness["cell_occurrences"] == 32
    assert witness["unique_cell_expressions"] == 12
    assert witness["materializations_avoided"] == 20
    assert witness["all_occurrence_witnesses_retained"] is True
    assert len(witness["occurrence_ids"]) == 32
    assert len(witness["unique_cells"]) == 12


def test_native_closure_witness_rejects_host_coercions() -> None:
    witness = closure_witness()
    assert witness["selected_interpretation"] == "HARMONICODE_NATIVE"
    assert witness["interpretation_locked"] is True
    assert witness["hnan_mod_unit_gate_preserved"] is True
    assert witness["hnan_pole_is_native_gate_state"] is True
    assert witness["u72_closure_unit"] == "Delta"
    assert witness["universal_denominator_unit"] == "Delta"
    assert witness["closure_readout"] == "1_H"
    assert witness["delta_e"] == "0"
    assert witness["psi"] == "0"
    assert witness["omega"] is True
    assert witness["host_boolean_coercion_used"] is False
    assert witness["host_modulo_one_used"] is False
    assert witness["host_division_by_zero_used"] is False
    assert witness["host_rectangular_matrixpower_used"] is False
    assert witness["projection_substitution_used"] is False


def test_source_bundle_is_deterministic() -> None:
    first = source_bundle_witness()
    second = source_bundle_witness()
    assert first == second
    assert first["source_count"] == 5
    assert first["roles_unique"] is True
    assert first["paths_unique"] is True
    assert len(first["source_bundle_root_sha256"]) == 64


def test_candidate_hydrates_and_recompresses_exactly() -> None:
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
    assert len(candidate["plane_roots"]) == 3


def test_candidate_optimization_keeps_provenance() -> None:
    candidate = build_candidate()
    optimization = candidate["optimization"]
    assert optimization["left_27_matrix_cells_generated_not_independently_persisted"]
    assert optimization["e_membrane_source_occurrences"] == 3
    assert optimization["e_membrane_value_nodes"] == 1
    assert optimization["e_membrane_value_evaluations_avoided"] == 2
    assert optimization["right_cell_occurrences"] == 32
    assert optimization["right_unique_cell_expressions"] == 12
    assert optimization["right_materializations_avoided"] == 20
    assert optimization["right_occurrence_witnesses_retained"] is True
    assert optimization["hash216_expansion_persisted"] is False


def test_mutated_right_cse_fails_closed() -> None:
    candidate = build_candidate()
    mutated = copy.deepcopy(candidate)
    mutated["right_symbolic_cse"]["unique_cells"] = tuple(
        list(mutated["right_symbolic_cse"]["unique_cells"])[:-1]
    )
    with pytest.raises(Pass220I074Error):
        validate_candidate(mutated)


def test_mutated_closure_readout_fails_closed() -> None:
    candidate = build_candidate()
    mutated = copy.deepcopy(candidate)
    mutated["closure"]["closure_readout"] = "HOST_SCALAR_1"
    with pytest.raises(Pass220I074Error):
        validate_candidate(mutated)


def test_no_authority_widening() -> None:
    assert AUTHORITY_BOUNDARY["candidate_only"] is True
    assert AUTHORITY_BOUNDARY["verbatim_source_authoritative"] is True
    assert AUTHORITY_BOUNDARY["ordered_xy_yx_preserved"] is True
    assert AUTHORITY_BOUNDARY["ordered_zw_wz_preserved"] is True
    assert AUTHORITY_BOUNDARY["e_membrane_host_boolean_division_authority"] is False
    assert AUTHORITY_BOUNDARY["rectangular_host_matrixpower_authority"] is False
    assert AUTHORITY_BOUNDARY["host_mod_one_rewrite_authority"] is False
    assert AUTHORITY_BOUNDARY["host_division_by_zero_authority"] is False
    assert AUTHORITY_BOUNDARY["host_float_arithmetic_authority"] is False
    assert AUTHORITY_BOUNDARY["projection_substitution_authorized"] is False
    assert AUTHORITY_BOUNDARY["canonical_vm81_mutation_authority"] is False
    assert AUTHORITY_BOUNDARY["canonical_hash72_commit_authority"] is False
    assert AUTHORITY_BOUNDARY["canonical_hash216_commit_authority"] is False
    assert AUTHORITY_BOUNDARY["canonical_hash216_persistence_authority"] is False


def test_self_test_closes() -> None:
    report = self_test()
    assert report["status"] == "PASS"
    assert report["check_count"] == report["pass_count"]
    assert report["failed"] == []

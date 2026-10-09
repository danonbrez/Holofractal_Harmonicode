"""I087: original RML10/RML11 48x48 exact Clifford matrix inverse proof."""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction

import pytest

from hhs_runtime import hhs_pass220_i087_exact_rml11_clifford_matrix_inverse_v1 as mod
from hhs_runtime.pass219.phase_clifford_intertwiner import (
    _matmul, _scale, _identity, _add
)


def test_real_original_rml11_generators_include_distinct_new_wx_composite():
    matrices = mod._original_rml11_actions()
    assert list(matrices) == ["x","y","z","w","xy","yx","zw","wz","wx"]
    assert matrices["wx"] == _matmul(matrices["w"], matrices["x"])
    assert matrices["wx"] != _matmul(matrices["w"],matrices["z"])
    assert matrices["wx"] != matrices["wz"]
    assert matrices["xy"] != matrices["yx"]
    assert matrices["zw"] != matrices["wz"]
    assert _add(matrices["wx"],_matmul(matrices["x"],matrices["w"])) == (
        tuple(tuple(0 for _ in range(16)) for _ in range(16))
    )
    assert all(len(matrix) == 16 and all(len(row) == 16 for row in matrix)
               for matrix in matrices.values())


def test_original_nine_i086_sources_are_actual_48x48_integer_blocks():
    M = mod.original_i086_rml11_block_matrix()
    assert len(M) == 48 and all(len(row) == 48 for row in M)
    assert all(isinstance(v,int) and not isinstance(v,bool) for row in M for v in row)
    assert all(abs(v) <= 2 for row in M for v in row)
    # Matrix first row, third block equals original ordered w*x.
    actions = mod._original_rml11_actions()
    assert tuple(tuple(row[32:48]) for row in M[0:16]) == actions["wx"]
    assert tuple(tuple(row[0:16]) for row in M[0:16]) == actions["yx"]


def test_exact_both_sided_inverse_uses_only_inherited_rml11_actions():
    result = mod.verify_i087_exact_clifford_inverse(include_inverse=True)
    assert result["schema"] == mod.SCHEMA
    assert result["determinant"] == {
        "numerator":10485760000,"denominator":1
    }
    assert result["determinant_nonzero"] is True
    assert result["matrix_order"] == 48
    assert result["actual_rml11_generator_matrices_executed"] is True
    assert result["mathematically_exact_48x48_lift_executed"] is True
    assert result["exact_left_product_identity"] is True
    assert result["exact_right_product_identity"] is True
    assert result["exact_two_sided_inverse_verified"] is True
    assert len(result["original_rml11_channel_witness_sha256"]) == 64
    assert len(result["original_rml10_cl08_witness_sha256"]) == 64
    assert len(result["matrix_clifford_projection_sha256"]) == 64
    assert len(result["inverse_clifford_projection_sha256"]) == 64
    inv = result["exact_inverse_coefficients"]
    assert len(inv) == 48 and all(len(row)==48 for row in inv)
    values = tuple(tuple(Fraction(v["numerator"],v["denominator"])
                         for v in row) for row in inv)
    M = mod.original_i086_rml11_block_matrix()
    assert _matmul(M,values) == _identity(48)
    assert _matmul(values,M) == _identity(48)


def test_deterministic_bounded_witness_and_native_authority_is_held():
    a = mod.verify_i087_exact_clifford_inverse()
    b = mod.verify_i087_exact_clifford_inverse()
    assert a == b
    assert "exact_inverse_coefficients" not in a
    assert a["projection_only"] is True
    assert a["candidate_only"] is True
    assert a["original_vm81_native_tensor_invertibility_proven"] is False
    assert a["native_5184_over_matrix_equals_canonical_hash72_proven"] is False
    assert a["native_matrix_inverse_operator_admitted"] is False
    assert a["canonical_hash72_minted"] is False
    assert a["canonical_hash216_transition_admitted"] is False
    assert a["signed_vm81_mutation"] is False
    assert a["floating_point_authority"] is False


def test_matrix_lift_does_not_silently_correct_wx_to_wz(monkeypatch):
    original = mod.MATRIX
    modified = tuple(
        tuple("wz" if (i,j)==(0,2) else expr
              for j,expr in enumerate(row))
        for i,row in enumerate(original)
    )
    monkeypatch.setattr(mod,"MATRIX",modified)
    with pytest.raises(mod.I087ExactCliffordError,match="wx source product"):
        mod.original_i086_rml11_block_matrix()


def test_singular_matrix_fails_closed_with_exact_zero_determinant():
    singular = tuple(tuple(0 for _ in range(48)) for _ in range(48))
    result, determinant, _ = mod._exact_inverse(singular)
    assert result is None
    assert determinant == Fraction(0)


def test_clifford_rml11_projection_is_separate_from_tensor_universality():
    receipt = mod.verify_i087_exact_clifford_inverse()
    assert receipt["wx_constructed_as_ordered_w_times_x"] is True
    assert receipt["wx_not_promoted_to_original_registered_phase8"] is True
    assert receipt["original_hnan_center_preserved"] is True
    assert receipt["original_i086_nine_ordered_cells_executed_in_clifford_projection"] is True
    assert receipt["original_vm81_native_tensor_invertibility_proven"] is False

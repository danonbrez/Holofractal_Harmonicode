"""I082 ordered bilateral tensor / exact vertex proof regressions."""
from __future__ import annotations

from fractions import Fraction

import pytest

from hhs_runtime.hhs_pass220_i082_chiral_bilateral_loshu_bifurcation_v1 import (
    BASELINE_GATE,
    CANONICAL_VALUES,
    CELL_EXPRESSIONS,
    FINAL_LO_SHU_SOURCE,
    MASK_SOURCE_ORDER,
    NATIVE_OPERATOR_OBLIGATIONS,
    ROOT_SEED,
    SOURCE_EQUATION,
    I082BifurcationError,
    QuadraticSurd3,
    bifurcation_branches,
    formalize_i082,
    original_typed_topology,
    scalar_vertices,
)
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import LO_SHU


def test_verbatim_nested_list_equality_and_negative_mask_not_booleanized():
    topology = original_typed_topology()
    assert topology["source_equation"] == SOURCE_EQUATION
    assert topology["source_equation"].startswith("List((u^72==xy)/List(")
    assert topology["source_equation"].count("-List(") >= 2
    assert "xA==-yB" in SOURCE_EQUATION
    assert "u^36==(yxwz)/a^2" in SOURCE_EQUATION
    assert topology["ordered_negative_list_mask"] == list(MASK_SOURCE_ORDER)
    assert topology["original_head"] == "List"
    assert topology["ordered_top_equality_operands"][1] == "xA"
    assert topology["mask_truth_values_not_evaluated_as_numbers"] is True
    assert topology["positioned_equality_is_not_scalar_symmetric_substitution"] is True
    assert len(NATIVE_OPERATOR_OBLIGATIONS) == 9


def test_nine_distinct_positioned_polynomial_vertices_reconstruct_loshu():
    cells = scalar_vertices()
    assert cells == tuple(tuple(Fraction(x) for x in row) for row in LO_SHU)
    assert CELL_EXPRESSIONS[0] == ("b⁴", "P⁴=AB=c⁴", "b²=c²-a²")
    assert CELL_EXPRESSIONS[1][2] == "((b⁶-a²)(c²+b⁴))/(d²+b²)"
    assert FINAL_LO_SHU_SOURCE.startswith("((b⁴,P⁴=AB=c⁴")
    witness = formalize_i082()
    assert [[v["numerator"] for v in row] for row in witness["matrix_exact"]] == [
        [4, 9, 2], [3, 5, 7], [8, 1, 6]
    ]
    assert [(cell["row"], cell["column"], cell["lo_shu_address"]) for cell in witness["cell_witnesses"]] == [
        (i, j, 3*i+j) for i in range(3) for j in range(3)
    ]
    assert [cell["source_polynomial"] for cell in witness["cell_witnesses"]] == [
        expr for row in CELL_EXPRESSIONS for expr in row
    ]
    assert all(cell["native_tensor_identity_reduced_to_scalar"] is False for cell in witness["cell_witnesses"])
    assert witness["eight_outer_vertices"] == [1, 2, 3, 4, 6, 7, 8, 9]
    assert witness["center_vertex"]["value"] == 5
    assert witness["sum45"] is True
    assert witness["magic15"] is True
    assert [x["numerator"] for x in witness["row_sums"]] == [15, 15, 15]
    assert [x["numerator"] for x in witness["column_sums"]] == [15, 15, 15]
    assert [x["numerator"] for x in witness["diagonal_sums"]] == [15, 15]


def test_exact_four_branch_quadratic_radicals_and_ordered_pq():
    branches = bifurcation_branches()
    assert len(branches) == 4
    assert {(b["P_sign"], b["q_minus_p_sign"]) for b in branches} == {
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    }
    assert all(b["P2_minus_pq"] == {"rational": {"numerator":1,"denominator":1}, "sqrt3":{"numerator":0,"denominator":1}} for b in branches)
    assert all(b["phase_ratio"] == b["P2_minus_pq"] for b in branches)
    assert all(b["pq"] == {"rational": {"numerator":2,"denominator":1}, "sqrt3":{"numerator":0,"denominator":1}} for b in branches)
    assert len({(str(b["P"]),str(b["p"]),str(b["q"])) for b in branches}) == 4
    plus = [b for b in branches if b["P_sign"] == 1 and b["q_minus_p_sign"] == 1][0]
    assert plus["p"]["sqrt3"]["numerator"] == 1
    assert plus["p"]["rational"]["numerator"] == -1
    assert plus["q"]["sqrt3"]["numerator"] == 1
    assert plus["q"]["rational"]["numerator"] == 1


def test_scalar_shadow_never_promotes_native_mask_or_chiral_theorem():
    r = formalize_i082()
    assert r["P2_branch_selected"] == 3
    assert r["P4_outer_scale"] == 9
    assert r["typed_mask_collapse_to_one_proven"] is False
    assert r["delta_e_zero_for_full_tensor_proven"] is False
    assert r["ordered_chiral_A_over_B_phase_transport_proven"] is False
    assert r["u36_half_turn_proven"] is False
    assert r["P_n_plus_1_equals_q_n_proven"] is False
    assert r["candidate_only"] is True
    assert r["canonical_vm81_mutation_authority"] is False
    assert r["canonical_hash72_commit_authority"] is False
    assert r["canonical_hash216_commit_authority"] is False
    assert r["phase_gear_hydration"]["executed"] is False
    assert r["inherited_phase_gear"]["coordinate_closure"] is True
    assert r["inherited_phase_gear"]["qudit_phase_slots"] == 72


def test_baseline_gate_metadata_distinct_from_arithmetic_unit():
    r = formalize_i082()
    assert r["root_metadata_seed"] == ROOT_SEED == "179971.179971"
    assert r["invariant_gate_metadata"] == BASELINE_GATE == "1.001"
    assert Fraction(1001, 1000) != Fraction(1)
    assert r["metadata_gate_is_not_scalar_unit"] is True


def test_surds_are_exact_and_no_float_or_bool_admission():
    with pytest.raises(I082BifurcationError, match="exact rational"):
        QuadraticSurd3(1.0, 0)
    with pytest.raises(I082BifurcationError, match="exact rational"):
        QuadraticSurd3(True, 0)
    with pytest.raises(I082BifurcationError, match="noninvertible"):
        QuadraticSurd3(0, 0).inverse()
    assert QuadraticSurd3(-1, 1) * QuadraticSurd3(1, 1) == QuadraticSurd3(2, 0)


def test_scalar_root_drift_is_rejected_without_changing_kernel(monkeypatch):
    monkeypatch.setitem(CANONICAL_VALUES, "b²", 3)
    with pytest.raises(I082BifurcationError, match="Lo Shu address mismatch"):
        scalar_vertices()


def test_native_i070_i071_lane5_phase_grid_binds_all_72_exact_positions():
    r = formalize_i082(hydrate_existing_phase_gear=True)
    hydration = r["phase_gear_hydration"]
    assert hydration["executed"] is True
    assert hydration["phase_slots"] == 72
    assert hydration["nucleus"] == 0
    assert hydration["candidate_only"] is True
    assert hydration["shared_root_sha256"] == r["source_topology"]["source_equation_sha256"]
    assert hydration["ordered_phase_basis"] == [
        "x", "y", "z", "w", "xy", "yx", "zw", "wz"
    ]
    assert r["delta_e_zero_for_full_tensor_proven"] is False

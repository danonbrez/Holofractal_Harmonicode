import inspect

import pytest

from hhs_runtime.hhs_kernel_conformance_registration_interposer_v1 import (
    interpose_service_registration,
)
from hhs_runtime.hhs_pass220_multidimensional_constraint_manifold_v1 import (
    PHASE_CELLS,
    VERBATIM_CONSTRAINT_EQUATIONS,
    Pass220MultidimensionalConstraintError,
    admit_multidimensional_constraint_state,
    decimal_nested_layer_witness,
    dimensional_phase_ladder_witness,
    hash72_algebraic_projection_witness,
    invariant_nucleus_addresses,
    multidimensional_constraint_manifold_self_test,
    ordered_curvature_tensor_witness,
    phase_index,
    phase_turn,
    ternary_address_to_board,
    transport_addresses,
    transport_loop_address,
    wrap_board_step,
)
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry


def test_3_power_4_geometry_decomposes_exactly_into_72_plus_9():
    witness = dimensional_phase_ladder_witness()
    geometry = witness["ternary_geometry"]
    assert geometry["3_power_4"] == 81
    assert geometry["nucleus_3_power_2"] == 9
    assert geometry["decomposition"] == (72, 9)
    assert geometry["transport_cells"] == 72
    assert geometry["nucleus_cells"] == 9
    assert geometry["visible_board_unique_addresses"] == 81
    assert geometry["address_symmetry_cardinality_81_power_4"] == 81**4


def test_z3_power_4_to_9x9_projection_is_bijective():
    addresses = [
        (a, b, c, d)
        for a in range(3)
        for b in range(3)
        for c in range(3)
        for d in range(3)
    ]
    board = {ternary_address_to_board(*address) for address in addresses}
    assert len(addresses) == len(board) == 81
    assert min(r for r, _ in board) == 0
    assert max(r for r, _ in board) == 8
    assert min(c for _, c in board) == 0
    assert max(c for _, c in board) == 8


def test_invariant_nucleus_is_central_3x3_and_complement_is_72():
    nucleus = invariant_nucleus_addresses()
    transport = transport_addresses()
    assert len(nucleus) == 9
    assert len(transport) == 72
    assert set(nucleus).isdisjoint(transport)
    assert {
        ternary_address_to_board(*address)
        for address in nucleus
    } == {
        (r, c)
        for r in range(3, 6)
        for c in range(3, 6)
    }


def test_pacman_wrap_is_exact_on_all_visible_edges():
    assert wrap_board_step(8, 4, 1, 0) == (0, 4)
    assert wrap_board_step(0, 4, -1, 0) == (8, 4)
    assert wrap_board_step(4, 8, 0, 1) == (4, 0)
    assert wrap_board_step(4, 0, 0, -1) == (4, 8)


def test_72_phase_quantization_and_transport_loop_are_periodic():
    assert PHASE_CELLS == 72
    for index in range(72):
        assert phase_index(index + 72) == phase_index(index)
        assert phase_turn(index + 72) == phase_turn(index)
        assert transport_loop_address(index + 72) == transport_loop_address(index)
    assert phase_turn(0) == (0, 72)
    assert phase_turn(71) == (71, 72)
    assert phase_turn(72) == (0, 72)


def test_dimensional_ladder_preserves_symbolic_no_float_geometry():
    witness = dimensional_phase_ladder_witness()
    assert witness["one_dimensional_phase"]["carrier"] == "u^n"
    assert witness["two_dimensional_circular_projection"] == (
        "cos(theta_n)",
        "sin(theta_n)",
    )
    assert witness["three_dimensional_spherical_projection"] == (
        "r*sin(phi)*cos(theta_n)",
        "r*sin(phi)*sin(theta_n)",
        "r*cos(phi)",
    )
    assert witness["four_dimensional_phase_pairs"] == (("x", "y"), ("z", "w"))
    assert witness["phase_periodicity_all_72"] is True
    assert witness["transport_loop_periodicity_all_72"] is True


def test_hash72_algebraic_projection_locks_9_36_45_exactly():
    witness = hash72_algebraic_projection_witness()
    assert witness["a2"] == 1
    assert witness["b2"] == 2
    assert witness["b4"] == 4
    assert witness["P4"] == 9
    assert witness["L2"] == 9
    assert witness["b2_over_a4"] == 2
    assert witness["u_cycle_exponent"] == 144
    assert witness["HASH72_projection"] == 36
    assert witness["Q_P4_squared"] == 45
    assert witness["Q_P4_squared_over_P4"] == 5
    assert witness["hash72_equals_q_square_minus_l2"] is True
    assert witness["hash72_over_b4_equals_P4"] is True
    assert witness["L2_equals_P4"] is True
    assert witness["C4_equals_b4"] is True
    assert witness["C5_equals_Q_ratio"] is True
    assert witness["C9_equals_P4"] is True
    assert "NO_HASH72_DIGEST_MINT_AUTHORITY" in witness["authority_scope"]


def test_ordered_curvature_tensor_preserves_wz_distinct_from_zw():
    witness = ordered_curvature_tensor_witness()
    assert witness["ordered_products_commuted"] is False
    assert witness["ordered_phase"] == {
        "sx": 0,
        "sz": 0,
        "xy": 1,
        "yx": -1,
        "zw": 1,
        "wz": -1,
    }
    assert witness["directional_curvature_xy_minus_wz"] == 2
    assert witness["forward_circumference_zw_plus_xy"] == 2
    assert witness["directional_curvature_equals_b2"] is True
    assert witness["forward_circumference_equals_b2"] is True


def test_ordered_curvature_tensor_projects_1_2_4_and_c6_without_flattening():
    witness = ordered_curvature_tensor_witness()
    assert witness["matrix"] == (
        (1, 0, 1),
        (2, 4, -2),
        (-1, 0, -1),
    )
    assert witness["row_sums"] == (2, 4, -2)
    assert witness["column_sums"] == (2, 4, -2)
    assert witness["trace"] == 4
    assert witness["determinant"] == 0
    assert witness["rank_projection"] == 2
    assert witness["nonzero_scalar_curvature"] == 4
    assert witness["outer_scalar_projection_C6"] == 6
    assert witness["outer_projection_equals_C6"] is True
    assert witness["ordinary_scalar_flattening_performed"] is False


def test_decimal_symbols_are_9_plus_zero_nested_layers_with_carry():
    witness = decimal_nested_layer_witness()
    assert witness["symbols"] == tuple(range(10))
    assert witness["cell_values"] == {index: index for index in range(10)}
    assert witness["nine_plus_zero"] is True
    assert witness["C0_ordered_identity_preserved"] is True
    assert witness["radix"] == 10
    assert witness["C9_plus_C1_equals_radix"] is True
    assert witness["carry_9_plus_1"] == {
        "input": (9, 1),
        "local_closed_digit": 0,
        "parent_increment": 1,
        "scalar_projection": 10,
    }


def test_verbatim_constraint_surfaces_are_retained():
    assert "(u^72)^2=HASH72" in VERBATIM_CONSTRAINT_EQUATIONS
    assert (
        "HASH72=Q(P^4)^2-((P^4/(P^2-pq))=L^2)"
        in VERBATIM_CONSTRAINT_EQUATIONS
    )
    assert any(
        equation.startswith("(((x*y)*(a^2+b^2==c^2))")
        for equation in VERBATIM_CONSTRAINT_EQUATIONS
    )


def test_joint_admission_enforces_all_inherited_and_new_constraints():
    witness = admit_multidimensional_constraint_state()
    assert witness["ok"] is True
    assert all(witness["checks"].values())
    assert witness["g41_summary"] == {
        "oriented": 81,
        "classes": 41,
        "fixed_positions": (41,),
    }
    assert witness["palindromic_phase_summary"]["combined_classes"] == 41
    assert witness["palindromic_phase_summary"]["forward_projection"] == (
        1, -1, 1, -1
    )
    assert witness["palindromic_phase_summary"]["mirror_projection"] == (
        1, -1, 1, -1
    )
    assert witness["floating_point_authority"] is False
    assert witness["canonical_hash72_mint_authority"] is False


@pytest.mark.parametrize(
    "kwargs",
    (
        {"a2": 1.0},
        {"b2": True},
        {"c2": 4},
        {"p2_minus_pq": 2},
        {"xy": 2},
        {"wz": 1},
        {"zw": -1},
        {"sx": 1},
    ),
)
def test_constraint_drift_fails_closed(kwargs):
    with pytest.raises(Pass220MultidimensionalConstraintError):
        admit_multidimensional_constraint_state(**kwargs)


def test_invalid_geometric_inputs_fail_closed():
    with pytest.raises(Pass220MultidimensionalConstraintError):
        phase_index(1.0)
    with pytest.raises(Pass220MultidimensionalConstraintError):
        phase_index(True)
    with pytest.raises(Pass220MultidimensionalConstraintError):
        ternary_address_to_board(3, 0, 0, 0)
    with pytest.raises(Pass220MultidimensionalConstraintError):
        wrap_board_step(9, 0, 1, 0)


def test_self_test_closes_without_authority_escalation():
    result = multidimensional_constraint_manifold_self_test()
    assert result["ok"] is True
    assert "HHS-I014" in result["invariant_ids"]
    assert "HHS-I015" in result["invariant_ids"]
    assert result["floating_point_authority"] is False
    assert result["canonical_hash72_authority"] is False
    assert result["canonical_hash216_authority"] is False
    assert result["canonical_vm81_mutation_authority"] is False


def test_service_registry_declares_i017_constraint_manifold():
    source = inspect.getsource(make_default_service_registry)
    assert "pass220.multidimensional_constraint_manifold.self_test" in source
    assert "hhs_pass220_multidimensional_constraint_manifold_v1" in source

    decision = interpose_service_registration({
        "name": "pass220.multidimensional_constraint_manifold.self_test",
        "module": (
            "hhs_runtime."
            "hhs_pass220_multidimensional_constraint_manifold_v1"
        ),
        "function": "multidimensional_constraint_manifold_self_test",
        "service_type": "pass220_exact_multidimensional_constraint_projection",
        "invariant_ids": [
            "HHS-I008",
            "HHS-I010",
            "HHS-I011",
            "HHS-I012",
            "HHS-I014",
            "HHS-I015",
        ],
        "contract_schemas": [
            "HHS_PASS_220_MULTIDIMENSIONAL_CONSTRAINT_MANIFOLD_V1",
        ],
        "witness_schemas": [
            "HHS_PASS_220_MULTIDIMENSIONAL_CONSTRAINT_WITNESS_V1",
        ],
        "validators": [
            "validate_multidimensional_constraint_manifold",
            "multidimensional_constraint_manifold_self_test",
        ],
        "rejection_codes": [
            "REJECT_MULTIDIMENSIONAL_CONSTRAINT_DRIFT",
            "REJECT_ORDERED_CURVATURE_COLLAPSE",
            "REJECT_HASH72_ALGEBRAIC_PROJECTION_MISMATCH",
            "REJECT_UNDERIVED_RUNTIME_SURFACE",
        ],
        "mutation_policy": (
            "READ_ONLY_EXACT_CONSTRAINT_ADMISSION_NO_VM81_MUTATION"
        ),
        "persistence_policy": "NO_CANONICAL_PERSISTENCE",
    })
    assert decision["ok"] is True
    assert decision["decision"]["derivation_complete"] is True

from fractions import Fraction

import pytest

from hhs_runtime.hhs_pass220_144cell_epsilon_lo_shu_closure_v1 import (
    DEVELOPMENT_EQUATION,
    FRACTAL_ORBIT,
    G72_OPERATOR,
    G72_ROOT_ORDER,
    HARMONIC_BLOCKS,
    HARMONIC_CELLS,
    ROOT_IDENTITY,
    TRINARY,
    VM5184,
    ZERO_CENTERED_LO_SHU,
    Pass220I021ClosureError,
    epsilon_phase_triplet,
    full_i021_witness,
    g72_advance,
    g72_close,
    g72_generator_descriptor,
    g72_initial_state,
    harmonic_root_closure_witness,
    lo_shu_phase_block,
    p_mod_144,
    phase_matrix_144_witness,
    sgn3,
    tessellate_144_phase_matrix,
    zero_centered_lo_shu_line_sums,
)


def test_zero_centered_lo_shu_is_exact_magic_square():
    assert ZERO_CENTERED_LO_SHU == ((-1, 4, -3), (-2, 0, 2), (3, -4, 1))
    sums = zero_centered_lo_shu_line_sums()
    assert sums["rows"] == (Fraction(0),) * 3
    assert sums["columns"] == (Fraction(0),) * 3
    assert sums["diagonals"] == (Fraction(0),) * 2


def test_local_epsilon_tuple_is_exact_trinary_zero_mean():
    epsilon = Fraction(7, 13)
    phase = epsilon_phase_triplet(epsilon)
    assert phase == (-epsilon, Fraction(0), epsilon)
    assert sum(phase, Fraction(0)) == 0
    assert tuple(sgn3(value) for value in phase) == TRINARY


def test_scaled_lo_shu_block_closes_for_exact_rational_epsilon():
    epsilon = Fraction(11, 17)
    block = lo_shu_phase_block(epsilon)
    sums = zero_centered_lo_shu_line_sums(block)
    assert block[0][0] == -epsilon
    assert block[1][1] == 0
    assert block[2][2] == epsilon
    assert all(value == 0 for group in sums.values() for value in group)


def test_12x12_is_sixteen_3x3_blocks_and_144_cells():
    epsilons = tuple(Fraction(i, i + 1) for i in range(1, HARMONIC_BLOCKS + 1))
    matrix = tessellate_144_phase_matrix(epsilons)
    assert len(matrix) == 12
    assert all(len(row) == 12 for row in matrix)
    assert HARMONIC_BLOCKS == 16
    assert HARMONIC_CELLS == 144
    assert sum(len(row) for row in matrix) == 144


def test_variable_block_epsilon_preserves_whole_144_cell_closure():
    epsilons = tuple(Fraction(i, 2 * i + 1) for i in range(1, 17))
    witness = phase_matrix_144_witness(epsilons)
    assert witness["all_local_blocks_closed"] is True
    assert witness["row_sums"] == ("0/1",) * 12
    assert witness["column_sums"] == ("0/1",) * 12
    assert witness["diagonal_sums"] == ("0/1",) * 2
    assert witness["total_epsilon"] == "0/1"
    assert witness["closed"] is True


def test_p_mod_144_is_exact_bounded_cell_address():
    assert p_mod_144(0) == 0
    assert p_mod_144(143) == 143
    assert p_mod_144(144) == 0
    assert p_mod_144(145) == 1
    assert p_mod_144(-1) == 143


def test_g72_is_an_unresolved_generator_not_a_scalar_root():
    descriptor = g72_generator_descriptor()
    assert descriptor["operator"] == G72_OPERATOR == "G72"
    assert descriptor["source_term"] == "2^(1/72)"
    assert descriptor["root_order"] == G72_ROOT_ORDER == 72
    assert descriptor["immutable_generator"] is True
    assert descriptor["noncommutative_ordered_transition"] is True
    assert descriptor["scalar_evaluation_allowed"] is False
    assert descriptor["epsilon_symbolic_magnitude"] is True
    assert descriptor["lo_shu_route_required"] is True
    assert descriptor["floating_point_authority"] is False


def test_g72_cannot_close_before_all_72_routed_teeth():
    state = g72_initial_state()
    with pytest.raises(Pass220I021ClosureError):
        g72_close(state)

    for tooth in range(71):
        state, route = g72_advance(state)
        assert route["from_tooth"] == tooth
        assert route["to_tooth"] == tooth + 1
        assert route["epsilon_symbol"] == "e"
        assert route["epsilon_magnitude_unresolved"] is True
        assert route["epsilon_phase_orientation"] == TRINARY
        assert route["lo_shu_zero_sum"] is True
        assert route["local_zero_sum"] is True
        assert route["generator_unresolved_before"] is True
        assert route["generator_unresolved_after"] is True
        assert route["scalar_resolution_performed"] is False
        with pytest.raises(Pass220I021ClosureError):
            g72_close(state)

    state, route = g72_advance(state)
    assert state.completed_routes == 72
    assert route["to_tooth"] == 72
    closure = g72_close(state)
    assert closure["routed_cycles"] == 72
    assert closure["emergent_binary_coefficient"] == 2
    assert closure["generator_still_unresolved"] is True
    assert closure["premature_scalar_resolution"] is False


def test_72_fold_root_identity_emerges_only_after_routing():
    witness = harmonic_root_closure_witness()
    assert ROOT_IDENTITY == "f¹⁴⁴=(2^(1/72))u⁷²"
    assert VM5184 == 5184 == 72 * 72
    assert FRACTAL_ORBIT == 10368 == 144 * 72
    assert witness["routed_cycles"] == 72
    assert witness["all_routes_generator_unresolved"] is True
    assert witness["all_routes_scalar_resolution_performed"] is False
    assert witness["all_routes_lo_shu_zero_sum"] is True
    assert witness["all_routes_local_zero_sum"] is True
    assert witness["emergent_binary_coefficient"] == 2
    assert witness["f_exponent"] == 10368
    assert witness["u_exponent"] == 5184
    assert witness["resolved_identity"] == "f^10368=2u^5184"
    assert witness["generator_still_unresolved"] is True
    assert witness["fractional_exponent_approximated"] is False


def test_full_witness_preserves_source_order_and_authority_boundaries():
    witness = full_i021_witness()
    assert witness["development_equation"] == DEVELOPMENT_EQUATION
    assert witness["root_identity"] == ROOT_IDENTITY
    assert witness["local_trinary"] == TRINARY
    assert witness["local_epsilon_sum"] == "0/1"
    assert witness["g72_operator"] == "G72"
    assert witness["g72_routed_cycles"] == 72
    assert witness["g72_generator_still_unresolved"] is True
    assert witness["g72_no_scalar_preemption"] is True
    assert witness["phase_matrix_closed"] is True
    assert witness["root_identity_closed"] is True
    assert witness["closed"] is True
    assert witness["floating_point_authority"] is False
    assert witness["projection_only"] is True
    assert witness["canonical_admission_authority"] is False


def test_nonexact_inputs_fail_closed_without_float_coercion():
    with pytest.raises(Pass220I021ClosureError):
        epsilon_phase_triplet(0.5)
    with pytest.raises(Pass220I021ClosureError):
        lo_shu_phase_block(1.0)
    with pytest.raises(Pass220I021ClosureError):
        p_mod_144(144.0)
    with pytest.raises(Pass220I021ClosureError):
        tessellate_144_phase_matrix((1,) * 15)

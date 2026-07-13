from fractions import Fraction

from hhs_backend.runtime.hhs_holofractal_phase_gear_pathfinder_v1 import (
    lo_shu_weight,
    make_normalized_phase_gear,
    normalized_matrix,
    rotate,
    run_holofractal_phase_gear_pathfinder,
    shortest_nonempty_closed_orbit,
)


def test_reciprocal_normalization_is_exact_and_float_free():
    gear = make_normalized_phase_gear(Fraction(2, 1), Fraction(3, 1))
    assert gear["x"] == {"numerator": 2, "denominator": 1}
    assert gear["y"] == {"numerator": 1, "denominator": 2}
    assert gear["z"] == {"numerator": 3, "denominator": 1}
    assert gear["w"] == {"numerator": 1, "denominator": 3}
    assert gear["reciprocal_normalization_valid"] is True
    assert gear["floating_point_used"] is False


def test_declared_matrix_normalizes_xy_and_wz_to_one():
    matrix = normalized_matrix(Fraction(2, 1), Fraction(3, 1))
    assert matrix[0][1] == -1
    assert matrix[1][0] == 1
    assert matrix[1][2] == 1
    assert matrix[2][1] == -1
    assert matrix[1][1] == Fraction(5, 2)


def test_shortest_nonempty_rotational_orbit_has_period_four():
    loop = shortest_nonempty_closed_orbit(normalized_matrix())
    assert loop["orientation_path"] == [0, 1, 2, 3, 0]
    assert loop["transition_count"] == 4
    assert loop["nonempty"] is True
    assert loop["closed"] is True
    assert loop["intermediate_states_nonidentical"] is True


def test_lo_shu_positional_weighting_changes_intermediate_states():
    base = normalized_matrix()
    weighted_roots = []
    for orientation in range(4):
        weighted = lo_shu_weight(rotate(base, orientation))
        weighted_roots.append(tuple(tuple(value for value in row) for row in weighted))
    assert len(set(weighted_roots)) == 4
    assert rotate(base, 4) == base


def test_reciprocal_invariants_survive_every_rotation_transition():
    loop = shortest_nonempty_closed_orbit(normalized_matrix(), start_orientation=2)
    assert loop["orientation_path"] == [2, 3, 0, 1, 2]
    assert loop["reciprocal_invariants_preserved"] is True
    assert all(step["reciprocal_relations_preserved"] for step in loop["transitions"])


def test_nine_local_loops_cover_the_entire_81_cell_hierarchy():
    result = run_holofractal_phase_gear_pathfinder()
    assert result["local_loop_count"] == 9
    assert result["local_periods"] == [4] * 9
    assert result["total_rotation_steps"] == 36
    assert result["cell_coverage_count"] == 81
    assert result["kernel_global_closure"] is True
    assert result["holofractal_closure"] is True


def test_macro_loop_hash72_witness_is_deterministic():
    first = run_holofractal_phase_gear_pathfinder()
    macro_root = first["macro_loop"]["macro_loop_root_hash72"]
    run_root = first["run_root_hash72"]
    run_holofractal_phase_gear_pathfinder.cache_clear()
    second = run_holofractal_phase_gear_pathfinder()
    assert second["macro_loop"]["macro_loop_root_hash72"] == macro_root
    assert second["run_root_hash72"] == run_root
    assert second["holofractal_closure"] is True

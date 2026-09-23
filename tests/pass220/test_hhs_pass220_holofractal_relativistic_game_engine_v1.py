from copy import deepcopy
import inspect

import pytest

from hhs_runtime.hhs_kernel_conformance_registration_interposer_v1 import (
    interpose_service_registration,
)
from hhs_runtime.hhs_pass220_holofractal_relativistic_game_engine_v1 import (
    HASH72_LEN,
    LOCAL_CONSTRAINTS,
    Pass220I041GameEngineError,
    build_game_engine_cycle,
    build_relativistic_game_frame,
    color_wheel_q144,
    euclidean_trig_q144,
    h36_coordinate,
    h36_full_coverage_witness,
    h36_music_state,
    holofractal_relativistic_game_engine_self_test,
    holofractal_relativistic_game_engine_witness,
    holofractal_sprite216,
    platonic_scene_geometry,
    shader_ir,
    validate_game_engine_cycle,
)
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry


def test_euclidean_q144_trig_is_exact_symbolic_cyclotomic():
    zero = euclidean_trig_q144(0)
    quarter = euclidean_trig_q144(36)
    half = euclidean_trig_q144(72)
    full = euclidean_trig_q144(144)

    assert zero["q144_index"] == 0
    assert zero["angle_turns"] == {"numerator": 0, "denominator": 1}
    assert zero["angle_degrees"] == {"numerator": 0, "denominator": 1}

    assert quarter["q144_index"] == 36
    assert quarter["angle_turns"] == {"numerator": 1, "denominator": 4}
    assert quarter["angle_degrees"] == {"numerator": 90, "denominator": 1}

    assert half["q144_index"] == 72
    assert half["angle_turns"] == {"numerator": 1, "denominator": 2}
    assert half["angle_degrees"] == {"numerator": 180, "denominator": 1}

    assert full["q144_index"] == 0
    assert full["P"] == 144
    assert full["cyclotomic_field"] == "Q(zeta_144)"

    for row in (zero, quarter, half, full):
        assert row["scalar_trig_evaluation_performed"] is False
        assert row["host_float_arithmetic_used"] is False
        assert len(row["rotation_matrix_exact"]) == 2
        assert "zeta_144" in row["cos_exact"]
        assert "zeta_144" in row["sin_exact"]


def test_h36_coordinate_exactly_mirrors_native_factorization_boundaries():
    first = h36_coordinate(0)
    last = h36_coordinate(5183)

    assert first == {
        "linear5184": 0,
        "word144": 0,
        "bit36": 0,
        "et_bank3": 0,
        "et_pitch12": 0,
        "q144_row12": 0,
        "q144_col12": 0,
        "vm81_cell81": 0,
        "vm81_operation64": 0,
        "hash72_row72": 0,
        "hash72_col72": 0,
        "phase_left8": 0,
        "phase_right8": 0,
        "harmonic_rule64": 1,
    }
    assert last == {
        "linear5184": 5183,
        "word144": 143,
        "bit36": 35,
        "et_bank3": 2,
        "et_pitch12": 11,
        "q144_row12": 11,
        "q144_col12": 11,
        "vm81_cell81": 80,
        "vm81_operation64": 63,
        "hash72_row72": 71,
        "hash72_col72": 71,
        "phase_left8": 7,
        "phase_right8": 7,
        "harmonic_rule64": 64,
    }

    with pytest.raises(Pass220I041GameEngineError):
        h36_coordinate(-1)
    with pytest.raises(Pass220I041GameEngineError):
        h36_coordinate(5184)


def test_h36_music_state_binds_equal_temperament_rule_and_phase_pair():
    state = h36_music_state(143, 35)
    c = state["coordinate"]
    et = state["equal_temperament"]

    assert c["linear5184"] == 5183
    assert et["bank3"] == 2
    assert et["pitch_class12"] == 11
    assert et["all_transpositions12"] == (
        11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
    )
    assert state["harmonic_rule64"] == 64
    assert state["ordered_phase_pair8x8"] == (7, 7)
    assert state["host_float_arithmetic_used"] is False
    assert state["canonical_music_authority"] is False


def test_h36_full_coverage_matches_all_5184_factorizations():
    witness = h36_full_coverage_witness()
    assert witness["coordinate_count"] == 5184
    assert witness["unique_linear5184"] == 5184
    assert witness["unique_word144"] == 144
    assert witness["unique_bit36"] == 36
    assert witness["unique_et_bank3"] == 3
    assert witness["unique_et_pitch12"] == 12
    assert witness["unique_q144_coordinates"] == 144
    assert witness["unique_vm81_cells"] == 81
    assert witness["unique_operation64"] == 64
    assert witness["unique_hash72_coordinates"] == 5184
    assert witness["unique_phase_pairs8x8"] == 64
    assert witness["unique_harmonic_rules64"] == 64
    assert witness["exact_factorizations"] == {
        "144x36": 5184,
        "12x12x3x12": 5184,
        "81x64": 5184,
        "72x72": 5184,
    }
    assert witness["host_float_arithmetic_used"] is False


def test_platonic_scene_derives_all_five_exact_incidence_closures():
    scene = platonic_scene_geometry()
    by_name = {item["name"]: item for item in scene["solids"]}

    assert scene["solid_count"] == 5
    assert scene["all_euler_two"] is True
    assert scene["all_face_edge_incidence_closed"] is True
    assert scene["all_vertex_edge_incidence_closed"] is True

    assert (by_name["tetrahedron"]["vertices"], by_name["tetrahedron"]["edges"], by_name["tetrahedron"]["faces"]) == (4, 6, 4)
    assert (by_name["cube"]["vertices"], by_name["cube"]["edges"], by_name["cube"]["faces"]) == (8, 12, 6)
    assert (by_name["octahedron"]["vertices"], by_name["octahedron"]["edges"], by_name["octahedron"]["faces"]) == (6, 12, 8)
    assert (by_name["dodecahedron"]["vertices"], by_name["dodecahedron"]["edges"], by_name["dodecahedron"]["faces"]) == (20, 30, 12)
    assert (by_name["icosahedron"]["vertices"], by_name["icosahedron"]["edges"], by_name["icosahedron"]["faces"]) == (12, 30, 20)

    assert scene["pentagonal_quantization"]["half_sector"] == 36
    assert scene["pentagonal_quantization"]["external"] == 72
    assert scene["pentagonal_quantization"]["supplementary"] == 144
    assert scene["authoritative_vertex_table_used"] is False
    assert scene["render_mesh_is_projection_only"] is True


def test_color_wheel_is_q144_and_reciprocal_half_turn():
    zero = color_wheel_q144(0)
    last = color_wheel_q144(143)

    assert zero["q144_index"] == 0
    assert zero["sector12"] == 0
    assert zero["substep12"] == 0
    assert zero["reciprocal_q144"] == 72
    assert zero["reciprocal_is_half_turn"] is True

    assert last["q144_index"] == 143
    assert last["sector12"] == 11
    assert last["substep12"] == 11
    assert last["reciprocal_q144"] == 71
    assert last["reciprocal_is_half_turn"] is True
    assert last["rgb_projection_authority"] is False
    assert last["host_float_arithmetic_used"] is False


def test_holofractal_sprite216_is_deterministic_and_exact_before_render_projection():
    seed = "a" * 64
    first = holofractal_sprite216(seed)
    second = holofractal_sprite216(seed)
    different = holofractal_sprite216("b" * 64)

    assert first == second
    assert first != different
    assert len(first["prev_hash72"]) == HASH72_LEN
    assert len(first["state_hash72"]) == HASH72_LEN
    assert len(first["receipt_hash72"]) == HASH72_LEN
    assert first["sprite216_length"] == 216
    assert len(first["sprite216"]) == 216
    assert len(first["state_phase_indices72"]) == 72
    assert len(first["reciprocal_phase_indices72"]) == 72
    assert all(0 <= v < 72 for v in first["state_phase_indices72"])
    assert all(
        r == (v + 36) % 72
        for v, r in zip(
            first["state_phase_indices72"],
            first["reciprocal_phase_indices72"],
        )
    )
    assert len(first["lo_shu_core"]) == 3
    assert first["render_float_projection_allowed"] is True
    assert first["canonical_float_authority"] is False
    assert first["host_float_arithmetic_used_by_exact_descriptor"] is False


def test_shader_ir_binds_same_q144_music_color_sprite_state():
    sprite = holofractal_sprite216("shader-seed")
    music = h36_music_state(73, 17)
    color = color_wheel_q144(73)
    ir = shader_ir(
        q144_index=73,
        sprite=sprite,
        music=music,
        color=color,
    )

    assert ir["shader_language"] == "HHS_TYPED_SHADER_IR"
    assert ir["vertex_stage"]["q144_index"] == 73
    assert ir["vertex_stage"]["rotation_field"] == "Q(zeta_144)"
    assert ir["fragment_stage"]["color_wheel_q144"] == 73
    assert ir["fragment_stage"]["reciprocal_color_q144"] == 1
    assert ir["fragment_stage"]["music_pitch_class12"] == 5
    assert ir["fragment_stage"]["music_bank3"] == 1
    assert ir["fragment_stage"]["sprite_geometry_seed"] == sprite["geometry_seed"]
    assert ir["exact_source_identity_preserved"] is True
    assert ir["backend_float_values_may_be_generated_for_rendering"] is True
    assert ir["backend_float_is_canonical_authority"] is False
    assert ir["shader_executes_canonical_mutation"] is False


def test_relativistic_game_frame_unifies_all_surfaces_on_one_q144_state():
    frame = build_relativistic_game_frame(
        143,
        bit36=35,
        platonic_pair=(5, 3),
    )

    assert frame["tick"] == 143
    assert frame["q144"]["q144_index"] == 143
    assert frame["euclidean_trig"]["q144_index"] == 143
    assert frame["h36_music"]["coordinate"]["word144"] == 143
    assert frame["h36_music"]["coordinate"]["bit36"] == 35
    assert frame["color_wheel"]["q144_index"] == 143
    assert frame["shader_ir"]["vertex_stage"]["q144_index"] == 143
    assert frame["platonic_solid"]["name"] == "dodecahedron"
    assert frame["platonic_solid"]["vertices"] == 20
    assert frame["platonic_solid"]["edges"] == 30
    assert frame["platonic_solid"]["faces"] == 12
    assert frame["same_q144_drives_trig_music_color_shader"] is True
    assert frame["relativistic_physics"]["u_data_close"] is True
    assert frame["game_state_is_exact"] is True
    assert frame["rendering_is_projection"] is True
    assert frame["host_float_arithmetic_used_by_game_state"] is False
    assert frame["probability_used"] is False
    assert frame["likelihood_used"] is False
    assert frame["mcmc_used"] is False
    assert frame["parameter_refit_performed"] is False
    assert frame["canonical_vm81_mutation_authority"] is False
    assert frame["canonical_hash72_authority"] is False
    assert frame["canonical_hash216_authority"] is False


def test_full_game_engine_cycle_closes():
    cycle = build_game_engine_cycle()
    result = validate_game_engine_cycle(cycle)

    assert result["ok"] is True
    assert result["q144_frames"] == 144
    assert result["h36_coordinates"] == 5184
    assert result["platonic_solids"] == 5
    assert result["sprite216_length"] == 216
    assert result["harmonic_rules64"] == 64
    assert result["phase_pairs8x8"] == 64
    assert result["et_banks3"] == 3
    assert result["et_pitch_classes12"] == 12
    assert result["vm81_cells"] == 81
    assert result["exact_cycle_closed"] is True

    assert cycle["all_q144_indices_exactly_once"] is True
    assert cycle["all_q144_cyclotomic_trig_exact"] is True
    assert cycle["all_color_reciprocals_half_turn"] is True
    assert cycle["dimension_closure"] == {
        "144x36": 5184,
        "81x64": 5184,
        "72x72": 5184,
        "12x12": 144,
        "3x12": 36,
        "8x8": 64,
    }
    assert cycle["render_backend_is_projection_only"] is True
    assert cycle["host_float_arithmetic_used_by_exact_cycle"] is False
    assert cycle["canonical_admission_authority"] is False


def test_cycle_tampering_fails_closed():
    cycle = build_game_engine_cycle()
    tampered = deepcopy(cycle)
    tampered["all_color_reciprocals_half_turn"] = False
    with pytest.raises(Pass220I041GameEngineError, match="receipt mismatch"):
        validate_game_engine_cycle(tampered)


def test_witness_and_self_test_close_without_authority_escalation():
    witness = holofractal_relativistic_game_engine_witness()
    assert witness["ok"] is True
    assert witness["result"]["exact_cycle_closed"] is True
    assert tuple(witness["local_constraints"]) == LOCAL_CONSTRAINTS
    assert witness["graphics_shader_surface"] == "TYPED_SHADER_IR_PROJECTION"
    assert witness["music_surface"] == (
        "PASS219_H36_144X36_EXACT_COORDINATE_PROJECTION"
    )
    assert witness["physics_surface"] == (
        "I040_EXACT_RELATIVISTIC_OBSERVATION_PROJECTION"
    )
    assert witness["canonical_admission_authority"] is False

    self_test = holofractal_relativistic_game_engine_self_test()
    assert self_test["ok"] is True


def test_service_registry_declares_i041_constructor():
    source = inspect.getsource(make_default_service_registry)
    assert "pass220.holofractal_relativistic_game_engine.self_test" in source
    assert "hhs_pass220_holofractal_relativistic_game_engine_v1" in source

    decision = interpose_service_registration({
        "name": "pass220.holofractal_relativistic_game_engine.self_test",
        "module": (
            "hhs_runtime."
            "hhs_pass220_holofractal_relativistic_game_engine_v1"
        ),
        "function": "holofractal_relativistic_game_engine_self_test",
        "service_type": "pass220_validated_multimodal_game_projection_constructor",
        "invariant_ids": [
            "HHS-I008",
            "HHS-I010",
            "HHS-I011",
            "HHS-I012",
            "HHS-I014",
            "HHS-I015",
        ],
        "contract_schemas": [
            "HHS_PASS_220_I041_HOLOFRACTAL_RELATIVISTIC_GAME_ENGINE_V1",
        ],
        "witness_schemas": [
            "HHS_PASS_220_I041_GAME_ENGINE_WITNESS_V1",
        ],
        "validators": [
            "validate_game_engine_cycle",
            "holofractal_relativistic_game_engine_self_test",
        ],
        "rejection_codes": [
            "REJECT_I041_Q144_DRIFT",
            "REJECT_I041_TRIG_SYMBOLIC_DRIFT",
            "REJECT_I041_H36_COORDINATE_DRIFT",
            "REJECT_I041_PLATONIC_CLOSURE_FAILURE",
            "REJECT_I041_SPRITE216_DRIFT",
            "REJECT_I041_COLOR_RECIPROCAL_FAILURE",
            "REJECT_I041_SHADER_IR_DRIFT",
            "REJECT_I041_RELATIVISTIC_ROOT_DRIFT",
            "REJECT_I041_FLOAT_OR_PROBABILITY_PATH",
            "REJECT_I041_AUTHORITY_ESCALATION",
            "REJECT_UNDERIVED_RUNTIME_SURFACE",
        ],
        "mutation_policy": "READ_ONLY_GAME_PROJECTION_NO_VM81_MUTATION",
        "persistence_policy": (
            "REPOSITORY_OS_HYDRATION_ONLY_NO_DIRECT_CANONICAL_PERSISTENCE"
        ),
    })
    assert decision["ok"] is True
    assert decision["decision"]["derivation_complete"] is True

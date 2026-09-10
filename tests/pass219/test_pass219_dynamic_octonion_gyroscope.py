from __future__ import annotations

import pytest

from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    AMBIENT_STATE_COUNT,
    CHANNELS,
    PRODUCTS,
    UNIFIED_ROTATION_PRIMITIVE,
    DynamicGyroscopeError,
    advance_gyroscope,
    build_dynamic_gyroscopes_from_rml3_source,
    build_gyroscope_state,
    decode_ambient_state,
    encode_ambient_state,
    expected_product_phase,
    phase_to_exact_angle,
    unified_phase_operation,
)
from hhs_runtime.pass219.production_phase_geometry_binding import build_raw5184_phase_source


def _signs() -> dict[str, int]:
    return {"xy": 1, "yx": -1, "zw": 1, "wz": -1}


def _phases() -> dict[str, int]:
    signs = _signs()
    primitives = {"x": 0, "y": 12, "z": 24, "w": 36}
    return {
        "x": primitives["x"],
        "y": primitives["y"],
        "z": primitives["z"],
        "w": primitives["w"],
        "xy": expected_product_phase(primitives["x"], signs["xy"]),
        "yx": expected_product_phase(primitives["y"], signs["yx"]),
        "zw": expected_product_phase(primitives["z"], signs["zw"]),
        "wz": expected_product_phase(primitives["w"], signs["wz"]),
    }


def _state() -> dict[str, object]:
    return build_gyroscope_state(_phases(), _signs(), state_id="test:g0")


def test_ambient_phase_space_is_exactly_72_pow_8() -> None:
    assert AMBIENT_STATE_COUNT == 722_204_136_308_736
    state = _state()
    assert state["ambient_state_count"] == 72 ** 8
    assert state["ambient_72_pow_8_is_admissible_cardinality_claim"] is False


def test_ambient_state_encoder_is_bijective_at_boundaries_and_fixture() -> None:
    zero = {channel: 0 for channel in CHANNELS}
    maximum = {channel: 71 for channel in CHANNELS}
    fixture = _phases()
    assert encode_ambient_state(zero) == 0
    assert encode_ambient_state(maximum) == AMBIENT_STATE_COUNT - 1
    for phases in (zero, maximum, fixture):
        assert decode_ambient_state(encode_ambient_state(phases)) == phases


def test_product_channels_are_same_gyroscope_quarter_turn_images() -> None:
    state = _state()
    assert state["admissible_product_geometry"] is True
    relations = {row["product"]: row for row in state["product_constraints"]["relations"]}
    for product in PRODUCTS:
        assert relations[product]["quarter_turn_magnitude_steps"] == 18
        assert relations[product]["quarter_turn_magnitude_degrees"] == 90
        assert relations[product]["quarter_turn_direction"] == "TOWARD_ORDERED_RECIPROCAL"
        assert relations[product]["same_gyroscope_not_second_gyroscope"] is True
        assert state["channels"][product]["role"] == "RECIPROCAL_QUARTER_TURN_IMAGE_OF_SAME_GYROSCOPE"


def test_all_eight_channels_have_exact_360_degree_phase_coordinates() -> None:
    state = _state()
    assert tuple(state["channels"].keys()) == CHANNELS
    for channel in CHANNELS:
        phase = state["phases"][channel]
        angle = state["channels"][channel]
        assert angle["angle_degrees"] == phase * 5
        assert angle["full_cycle_degrees"] == 360
        assert angle["continuously_rotating"] is True
    assert phase_to_exact_angle(0)["u_phase"] == "u^0"
    assert phase_to_exact_angle(36)["angle_degrees"] == 180
    assert phase_to_exact_angle(71)["angle_degrees"] == 355


def test_signed_motion_of_all_eight_channels_preserves_quarter_turn_when_coupled() -> None:
    state = _state()
    deltas = {
        "x": 1,
        "y": -2,
        "z": 3,
        "w": -4,
        "xy": 1,
        "yx": -2,
        "zw": 3,
        "wz": -4,
    }
    transition = advance_gyroscope(state, deltas, transition_id="t1")
    next_state = transition["next_state"]
    assert next_state["admissible_product_geometry"] is True
    assert transition["rotation_directions"] == {
        "x": "PLUS",
        "y": "MINUS",
        "z": "PLUS",
        "w": "MINUS",
        "xy": "PLUS",
        "yx": "MINUS",
        "zw": "PLUS",
        "wz": "MINUS",
    }
    assert transition["underlying_primitive"] == UNIFIED_ROTATION_PRIMITIVE


def test_independent_product_motion_is_visible_as_typed_disequilibrium() -> None:
    state = _state()
    deltas = {channel: 0 for channel in CHANNELS}
    deltas["xy"] = 1
    transition = advance_gyroscope(state, deltas, transition_id="break-quarter-turn")
    next_state = transition["next_state"]
    assert next_state["admissible_product_geometry"] is False
    assert next_state["product_constraints"]["quarter_turn_disequilibrium_units"] == 1
    rows = {row["product"]: row for row in next_state["product_constraints"]["relations"]}
    assert rows["xy"]["satisfied"] is False
    assert rows["yx"]["satisfied"] is True
    assert rows["zw"]["satisfied"] is True
    assert rows["wz"]["satisfied"] is True


def test_add_multiply_and_power_use_one_rotation_primitive_without_scalarizing() -> None:
    state = _state()
    addition = unified_phase_operation(
        state,
        operator="+",
        ordered_operands=["x", "y"],
        signed_step=1,
    )
    multiplication = unified_phase_operation(
        state,
        operator="*",
        ordered_operands=["x", "y"],
        product_channel="xy",
    )
    power = unified_phase_operation(
        state,
        operator="^",
        ordered_operands=["x"],
        signed_step=18,
        repetitions=4,
    )
    assert {addition["underlying_primitive"], multiplication["underlying_primitive"], power["underlying_primitive"]} == {UNIFIED_ROTATION_PRIMITIVE}
    assert addition["mode"] == "COUPLED_PHASE_ROTATION"
    assert multiplication["mode"] == "ORDERED_RECIPROCAL_QUARTER_TURN"
    assert power["mode"] == "RECURSIVE_PHASE_ORBIT"
    assert addition["witness"]["scalar_sum_materialized"] is False
    assert multiplication["witness"]["scalar_product_materialized"] is False
    assert power["witness"]["scalar_power_materialized"] is False
    assert power["witness"]["phase_orbit72"] == [0, 18, 36, 54, 0]


def test_multiplication_keeps_order_and_reciprocal_identity() -> None:
    state = _state()
    xy = unified_phase_operation(
        state,
        operator="*",
        ordered_operands=["x", "y"],
        product_channel="xy",
    )
    yx = unified_phase_operation(
        state,
        operator="*",
        ordered_operands=["y", "x"],
        product_channel="yx",
    )
    assert xy["witness"]["generator"] == "x"
    assert xy["witness"]["reciprocal"] == "y"
    assert yx["witness"]["generator"] == "y"
    assert yx["witness"]["reciprocal"] == "x"
    assert xy["operation_sha256"] != yx["operation_sha256"]
    with pytest.raises(DynamicGyroscopeError, match="PRODUCT_OPERAND_ORDER_DRIFT"):
        unified_phase_operation(
            state,
            operator="*",
            ordered_operands=["y", "x"],
            product_channel="xy",
        )


def test_rml3_physical_source_lifts_primitives_without_reinterpreting_frozen_products() -> None:
    raw = bytes((i * 37 + 11) % 256 for i in range(648))
    source = build_raw5184_phase_source(raw)
    binding = build_dynamic_gyroscopes_from_rml3_source(source, _signs())
    assert binding["gyroscope_count"] == 20
    assert binding["ambient_state_count_per_gyroscope"] == 72 ** 8
    assert binding["rml3_raw5184_sha256"] == source["raw5184_sha256"]
    assert binding["rml3_phase_circuit_root_sha256"] == source["phase_circuit_root_sha256"]
    assert binding["legacy_i148_products_preserved_as_provenance_not_reinterpreted"] is True
    first_legacy = source["channel_ledger"][0]["ordered_channel_phase72"]
    first = binding["gyroscopes"][0]
    for channel in ("x", "y", "z", "w"):
        assert first["phases"][channel] == first_legacy[channel]
    assert first["legacy_i148_product_phase72"] == {
        product: first_legacy[product] for product in PRODUCTS
    }
    assert first["legacy_i148_product_phase_is_dynamic_product_identity"] is False
    assert first["admissible_product_geometry"] is True


def test_rml4_fails_closed_on_floats_and_bad_quarter_turn_signs() -> None:
    phases = _phases()
    phases["x"] = 1.0
    with pytest.raises(DynamicGyroscopeError, match="FLOAT_CANONICAL_AUTHORITY_FORBIDDEN"):
        build_gyroscope_state(phases, _signs(), state_id="float")

    bad_signs = _signs()
    bad_signs["xy"] = 0
    with pytest.raises(DynamicGyroscopeError, match="MUST_BE_PLUS_OR_MINUS_ONE"):
        build_gyroscope_state(_phases(), bad_signs, state_id="bad-sign")


def test_rml4_has_no_canonical_mutation_or_hash_authority() -> None:
    state = _state()
    assert state["canonical_vm81_mutation_authority"] is False
    assert state["canonical_hash72_mint_authority"] is False
    assert state["canonical_hash216_persistence_authority"] is False
    assert state["floating_point_authority"] is False
    assert state["scalar_projection_substitution_authority"] is False

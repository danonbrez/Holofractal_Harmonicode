from __future__ import annotations

from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    CHANNELS,
    advance_gyroscope,
    build_gyroscope_state,
    expected_product_phase,
)
from hhs_runtime.pass219.phase_clifford_intertwiner import (
    QUARTER_CYCLE_STEPS,
    audit_rml5_generators_on_phase_clifford_bridge,
    build_one_gyroscope_clifford_channel_actions,
    build_phase_transport_clifford_lift,
    build_unified_phase_operation_clifford_bridge,
    classify_chiral_pair_flip_clifford,
    classify_coupled_generator_clifford,
    classify_rml4_transition_clifford,
    decompose_signed_phase_step,
)


def _state(*, state_id: str = "rml11:test") -> dict[str, object]:
    signs = {"xy": 1, "yx": -1, "zw": 1, "wz": -1}
    primitives = {"x": 7, "y": 19, "z": 31, "w": 43}
    phases = {
        "x": primitives["x"],
        "y": primitives["y"],
        "z": primitives["z"],
        "w": primitives["w"],
        "xy": expected_product_phase(primitives["x"], signs["xy"]),
        "yx": expected_product_phase(primitives["y"], signs["yx"]),
        "zw": expected_product_phase(primitives["z"], signs["zw"]),
        "wz": expected_product_phase(primitives["w"], signs["wz"]),
    }
    return build_gyroscope_state(phases, signs, state_id=state_id)


def _steps(**updates: int) -> dict[str, int]:
    result = {channel: 0 for channel in CHANNELS}
    result.update(updates)
    return result


def test_signed_phase_decomposition_preserves_full_u72_resolution() -> None:
    assert QUARTER_CYCLE_STEPS == 18
    cases = {
        -72: (-4, 0),
        -71: (-3, -17),
        -54: (-3, 0),
        -19: (-1, -1),
        -18: (-1, 0),
        -17: (0, -17),
        0: (0, 0),
        17: (0, 17),
        18: (1, 0),
        19: (1, 1),
        54: (3, 0),
        71: (3, 17),
        72: (4, 0),
    }
    for delta, expected in cases.items():
        quarter, residual = decompose_signed_phase_step(delta)
        assert (quarter, residual) == expected
        assert delta == 18 * quarter + residual
        assert abs(residual) < 18


def test_one_gyroscope_clifford_actions_make_products_ordered_bivectors() -> None:
    witness = build_one_gyroscope_clifford_channel_actions()
    assert witness["primitive_action_generators"] == ["x", "y", "z", "w"]
    assert witness["product_channels_constructed_from_primitive_actions"] is True
    assert witness["product_channels_are_not_promoted_to_independent_gyroscope_axes"] is True
    assert witness["xy_equals_negative_yx_matrix_projection"] is True
    assert witness["zw_equals_negative_wz_matrix_projection"] is True
    assert witness["cl08_chirality_volume_squared_is_identity"] is True

    rows = {row["channel"]: row for row in witness["rows"]}
    for primitive in ("x", "y", "z", "w"):
        assert rows[primitive]["role"] == "PRIMITIVE_GENERATOR"
        assert rows[primitive]["anticommutes_with_cl08_chirality_volume"] is True
        assert rows[primitive]["commutes_with_cl08_chirality_volume"] is False
    for product in ("xy", "yx", "zw", "wz"):
        assert rows[product]["role"] == "ORDERED_DEPENDENT_BIVECTOR"
        assert rows[product]["commutes_with_cl08_chirality_volume"] is True
        assert rows[product]["anticommutes_with_cl08_chirality_volume"] is False
        assert rows[product]["same_gyroscope_dependent_product_view"] is True


def test_complete_lifts_distinguish_full_intertwiner_even_and_odd_sector_motion() -> None:
    state = _state()

    identity = build_phase_transport_clifford_lift(
        state, _steps(), transport_id="identity"
    )
    assert identity["complete_clifford_lift"] is True
    assert identity["full_cl08_module_intertwiner"] is True
    assert identity["full_phase_transform_classification"] == "FULL_CL08_MODULE_INTERTWINER"

    primitive_quarter = build_phase_transport_clifford_lift(
        state, _steps(x=18), transport_id="x-quarter"
    )
    assert primitive_quarter["complete_clifford_lift"] is True
    assert primitive_quarter["full_transform_chirality_sector_swapping"] is True
    assert primitive_quarter["full_phase_transform_classification"] == "ODD_CLIFFORD_CHIRALITY_SECTOR_SWAPPING"

    product_quarter = build_phase_transport_clifford_lift(
        state, _steps(xy=18), transport_id="xy-quarter"
    )
    assert product_quarter["complete_clifford_lift"] is True
    assert product_quarter["full_cl08_module_intertwiner"] is False
    assert product_quarter["full_transform_chirality_sector_preserving"] is True
    assert product_quarter["full_phase_transform_classification"] == "EVEN_CLIFFORD_CHIRALITY_SECTOR_PRESERVING"

    coupled_half = build_phase_transport_clifford_lift(
        state, _steps(x=36, xy=36), transport_id="x-xy-half"
    )
    assert coupled_half["complete_clifford_lift"] is True
    assert coupled_half["full_cl08_module_intertwiner"] is True
    assert coupled_half["ordered_reverse_factor_inverse_verified"] is True


def test_residual_phase_is_preserved_instead_of_collapsed_to_clifford_state() -> None:
    state = _state()
    lift = build_phase_transport_clifford_lift(
        state, _steps(x=19, xy=19), transport_id="residual"
    )
    assert lift["complete_clifford_lift"] is False
    assert lift["residual_u72_phase_preserved"] is True
    assert lift["residual_phase_rounded_or_discarded"] is False
    assert lift["full_cl08_module_intertwiner"] is False
    assert lift["full_phase_transform_classification"] == "RESIDUAL_U72_PHASE_PRESERVED_NO_COMPLETE_CLIFFORD_LIFT"
    rows = {row["channel"]: row for row in lift["factors"]}
    assert rows["x"]["signed_quarter_units"] == 1
    assert rows["x"]["residual_phase_steps"] == 1
    assert rows["xy"]["signed_quarter_units"] == 1
    assert rows["xy"]["residual_phase_steps"] == 1


def test_unified_add_multiply_power_use_same_clifford_bridge_without_operator_collapse() -> None:
    state = _state()
    addition = build_unified_phase_operation_clifford_bridge(
        state,
        operator="+",
        ordered_operands=["x", "y"],
        signed_step=18,
    )
    assert addition["source_operation_mode"] == "COUPLED_PHASE_ROTATION"
    assert addition["phase_transport_clifford_lift"]["full_transform_chirality_sector_preserving"] is True
    assert addition["phase_transport_clifford_lift"]["full_cl08_module_intertwiner"] is False

    xy = build_unified_phase_operation_clifford_bridge(
        state,
        operator="*",
        ordered_operands=["x", "y"],
        product_channel="xy",
    )
    yx = build_unified_phase_operation_clifford_bridge(
        state,
        operator="*",
        ordered_operands=["y", "x"],
        product_channel="yx",
    )
    assert xy["source_operation_mode"] == "ORDERED_RECIPROCAL_QUARTER_TURN"
    assert yx["source_operation_mode"] == "ORDERED_RECIPROCAL_QUARTER_TURN"
    assert xy["ordered_operands"] != yx["ordered_operands"]
    assert xy["bridge_sha256"] != yx["bridge_sha256"]
    assert xy["phase_transport_clifford_lift"]["full_transform_chirality_sector_preserving"] is True
    assert yx["phase_transport_clifford_lift"]["full_transform_chirality_sector_preserving"] is True
    # With the opposed construction signs in this state, the matrix projections
    # coincide, but ordered xy/yx identities remain distinct and receipt-visible.
    assert (
        xy["phase_transport_clifford_lift"]["quarter_component_matrix_sha256"]
        == yx["phase_transport_clifford_lift"]["quarter_component_matrix_sha256"]
    )
    assert xy["coincident_clifford_projection_collapses_operator_identity"] is False
    assert yx["coincident_clifford_projection_collapses_operator_identity"] is False

    power_one = build_unified_phase_operation_clifford_bridge(
        state,
        operator="^",
        ordered_operands=["x"],
        signed_step=18,
        repetitions=1,
    )
    power_two = build_unified_phase_operation_clifford_bridge(
        state,
        operator="^",
        ordered_operands=["x"],
        signed_step=18,
        repetitions=2,
    )
    assert power_one["phase_transport_clifford_lift"]["full_transform_chirality_sector_swapping"] is True
    assert power_two["phase_transport_clifford_lift"]["full_cl08_module_intertwiner"] is True


def test_rml4_transition_can_be_classified_read_only() -> None:
    state = _state()
    transition = advance_gyroscope(
        state,
        _steps(x=18, xy=18),
        transition_id="rml11-transition",
    )
    witness = classify_rml4_transition_clifford(transition)
    assert witness["source_transition_sha256"] == transition["transition_sha256"]
    assert witness["source_next_state_sha256"] == transition["next_state"]["state_sha256"]
    assert witness["phase_transport_clifford_lift"]["complete_clifford_lift"] is True
    assert witness["phase_transport_clifford_lift"]["full_transform_chirality_sector_swapping"] is True
    assert witness["rml4_transition_mutated"] is False


def test_rml5_coupled_and_pair_flip_exact_quarter_cases_have_expected_classes() -> None:
    state = _state()
    q0 = classify_coupled_generator_clifford(
        state, generator="x", signed_steps=0, transition_id="q0"
    )
    q1 = classify_coupled_generator_clifford(
        state, generator="x", signed_steps=18, transition_id="q1"
    )
    q2 = classify_coupled_generator_clifford(
        state, generator="x", signed_steps=36, transition_id="q2"
    )
    q3 = classify_coupled_generator_clifford(
        state, generator="x", signed_steps=54, transition_id="q3"
    )
    assert q0["clifford_lift"]["full_cl08_module_intertwiner"] is True
    assert q1["clifford_lift"]["full_transform_chirality_sector_swapping"] is True
    assert q2["clifford_lift"]["full_cl08_module_intertwiner"] is True
    assert q3["clifford_lift"]["full_transform_chirality_sector_swapping"] is True

    for pair_index in (0, 1):
        pair = classify_chiral_pair_flip_clifford(
            state, pair_index=pair_index, transition_id=f"pair:{pair_index}"
        )
        assert pair["pair_flip_self_inverse"] is True
        assert pair["clifford_lift"]["complete_clifford_lift"] is True
        assert pair["clifford_lift"]["full_cl08_module_intertwiner"] is True


def test_complete_290_case_rml5_generator_family_gets_exact_clifford_partition() -> None:
    audit = audit_rml5_generators_on_phase_clifford_bridge(_state())
    assert audit["coupled_z72_cases"] == 288
    assert audit["u36_pair_flip_cases"] == 2
    assert audit["total_generator_cases"] == 290
    assert audit["complete_clifford_lift_cases"] == 18
    assert audit["residual_u72_phase_cases"] == 272
    assert audit["full_cl08_module_intertwiner_cases"] == 10
    assert audit["even_chirality_sector_preserving_nonintertwiner_cases"] == 0
    assert audit["odd_chirality_sector_swapping_cases"] == 8
    assert audit["complete_lift_partition_complete"] is True
    assert audit["all_290_cases_partitioned"] is True
    assert audit["inherited_same_hopf_base_cases"] == 4
    assert audit["inherited_base_moving_hopf_cases"] == 286
    assert audit["inherited_inverse_hopf_restoration_failures"] == 0
    assert audit["hopf_and_clifford_classifications_are_orthogonal_not_substitutions"] is True
    assert audit["phase_transition_authority_expanded"] is False
    assert audit["canonical_vm81_mutation_authority"] is False
    assert audit["canonical_hash72_mint_authority"] is False
    assert audit["canonical_hash216_persistence_authority"] is False
    assert audit["floating_point_authority"] is False
    assert audit["scalar_projection_substitution_authority"] is False

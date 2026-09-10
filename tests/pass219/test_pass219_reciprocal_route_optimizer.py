from __future__ import annotations

from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    build_gyroscope_state,
    expected_product_phase,
)
from hhs_runtime.pass219.reciprocal_route_optimizer import (
    COMPLEMENTARY_POLICY,
    SHORTEST_POLICY,
    audit_rml5_generator_route_metadata,
    build_and_select_reciprocal_route,
    build_reciprocal_route_plan,
    complementary_wrap_delta,
    select_preferred_reciprocal_route,
    shortest_signed_delta,
)


def _state(
    *,
    state_id: str,
    primitives: dict[str, int] | None = None,
    signs: dict[str, int] | None = None,
) -> dict[str, object]:
    primitives = primitives or {"x": 7, "y": 19, "z": 31, "w": 43}
    signs = signs or {"xy": 1, "yx": -1, "zw": 1, "wz": -1}
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


def _target() -> dict[str, object]:
    return _state(
        state_id="rml12:target",
        primitives={"x": 25, "y": 38, "z": 67, "w": 48},
        signs={"xy": -1, "yx": 1, "zw": 1, "wz": -1},
    )


def test_shortest_and_complementary_z72_representatives_are_exact() -> None:
    cases = [
        (0, 0, 0, 0),
        (7, 25, 18, -54),
        (19, 38, 19, -53),
        (31, 67, 36, 36),
        (43, 48, 5, -67),
        (70, 2, 4, -68),
        (2, 70, -4, 68),
    ]
    for source, target, shortest, complementary in cases:
        assert shortest_signed_delta(source, target) == shortest
        assert complementary_wrap_delta(shortest) == complementary
        assert (source + shortest) % 72 == target % 72
        assert (source + complementary) % 72 == target % 72
        if abs(shortest) not in (0, 36):
            assert abs(shortest) < abs(complementary)


def test_route_plan_reaches_target_and_reverse_restores_source_exactly() -> None:
    source = _state(state_id="rml12:source")
    target = _target()
    plan = build_reciprocal_route_plan(
        source,
        target,
        route_id="rml12:test:shortest",
        delta_policy=SHORTEST_POLICY,
    )
    assert plan["target_reached_exactly"] is True
    assert plan["reverse_edge_sequence_restores_source_exactly"] is True
    assert plan["all_edges_reversible"] is True
    assert plan["all_edges_remain_in_admissible_product_geometry"] is True
    assert plan["delta_policy"] == SHORTEST_POLICY
    assert plan["metrics"]["move_count"] == 5
    assert plan["metrics"]["pair_flip_edges"] == 1
    assert plan["metrics"]["coupled_move_edges"] == 4
    assert plan["gradient_descent_used"] is False
    assert plan["loss_function_used"] is False
    assert plan["floating_score_used"] is False
    assert plan["probabilistic_search_used"] is False
    assert plan["route_selector_has_canonical_transition_authority"] is False


def test_every_route_edge_carries_orthogonal_hopf_and_clifford_metadata() -> None:
    plan = build_reciprocal_route_plan(
        _state(state_id="rml12:metadata-source"),
        _target(),
        route_id="rml12:test:metadata",
    )
    assert plan["edges"]
    saw_residual = False
    saw_complete = False
    saw_base_move = False
    saw_clifford_swap = False
    for edge in plan["edges"]:
        assert edge["hopf_classification"] in {
            "FIBER_PRESERVING_SAME_HOPF_BASE",
            "BASE_MOVING_HOPF_TRANSPORT",
        }
        assert edge["clifford_full_phase_classification"] in {
            "FULL_CL08_MODULE_INTERTWINER",
            "EVEN_CLIFFORD_CHIRALITY_SECTOR_PRESERVING",
            "ODD_CLIFFORD_CHIRALITY_SECTOR_SWAPPING",
            "RESIDUAL_U72_PHASE_PRESERVED_NO_COMPLETE_CLIFFORD_LIFT",
        }
        assert edge["classification_metadata_has_transition_authority"] is False
        assert edge["exact_inverse_restores_source_phase_state"] is True
        saw_residual |= edge["residual_u72_phase_preserved"] is True
        saw_complete |= edge["complete_clifford_lift"] is True
        saw_base_move |= edge["same_hopf_base"] is False
        saw_clifford_swap |= edge["clifford_chirality_sector_swapping"] is True
    assert saw_residual is True
    assert saw_complete is True
    assert saw_base_move is True
    assert saw_clifford_swap is True


def test_exact_lexicographic_selector_prefers_shortest_mechanical_route() -> None:
    source = _state(state_id="rml12:select-source")
    target = _target()
    shortest = build_reciprocal_route_plan(
        source,
        target,
        route_id="rml12:test:select:shortest",
        delta_policy=SHORTEST_POLICY,
    )
    complementary = build_reciprocal_route_plan(
        source,
        target,
        route_id="rml12:test:select:complementary",
        delta_policy=COMPLEMENTARY_POLICY,
    )
    assert shortest["metrics"]["move_count"] == complementary["metrics"]["move_count"]
    assert shortest["metrics"]["total_phase_transport_units"] < complementary["metrics"]["total_phase_transport_units"]

    selection = select_preferred_reciprocal_route([complementary, shortest])
    assert selection["selected_route_sha256"] == shortest["route_sha256"]
    assert selection["selected_delta_policy"] == SHORTEST_POLICY
    assert selection["selection_method"] == "EXACT_LEXICOGRAPHIC_INTEGER_VECTOR"
    assert selection["weighted_scalar_objective_used"] is False
    assert selection["gradient_descent_used"] is False
    assert selection["selection_changes_transition_authority"] is False


def test_selected_route_bundle_is_deterministic_and_authority_neutral() -> None:
    source = _state(state_id="rml12:bundle-source")
    target = _target()
    first = build_and_select_reciprocal_route(source, target, route_id="rml12:bundle")
    second = build_and_select_reciprocal_route(source, target, route_id="rml12:bundle")
    assert first["bundle_sha256"] == second["bundle_sha256"]
    assert first["selected_shortest_signed_route"] is True
    assert first["canonical_transition_authority_expanded"] is False
    assert first["selection"]["selected_delta_policy"] == SHORTEST_POLICY


def test_complete_290_case_route_metadata_cross_tab_is_reversible() -> None:
    audit = audit_rml5_generator_route_metadata(_state(state_id="rml12:audit"))
    assert audit["total_generator_cases"] == 290
    assert audit["cross_tab_partition_complete"] is True
    assert sum(audit["route_metadata_cross_tab"].values()) == 290
    assert audit["exact_inverse_failures"] == 0
    assert audit["all_generator_edges_reversible"] is True
    assert audit["inherited_complete_clifford_lift_cases"] == 18
    assert audit["inherited_residual_u72_phase_cases"] == 272
    assert audit["inherited_full_cl08_module_intertwiner_cases"] == 10
    assert audit["inherited_odd_chirality_sector_swapping_cases"] == 8
    assert audit["inherited_same_hopf_base_cases"] == 4
    assert audit["inherited_base_moving_hopf_cases"] == 286
    assert audit["hopf_and_clifford_metadata_retained_as_orthogonal_axes"] is True
    assert audit["classification_metadata_has_transition_authority"] is False
    print("RML12_ROUTE_METADATA_CROSS_TAB", audit["route_metadata_cross_tab"])

"""Pass 219 RML12 exact reciprocal route metadata and deterministic selector.

RML12 composes the validated RML5 reciprocal-path mechanics, RML7 Hopf
classification, and RML11 phase/Clifford classification into one read-only
navigation layer.

The selector does not use gradients, floating scores, probabilistic search, or
an authority-bearing cost function.  It constructs reversible admissible
routes from the existing RML5 generators:

1. align the two reciprocal chirality sign sectors with exact self-inverse
   u^36 pair flips;
2. align x,y,z,w in canonical order with coupled generator/product moves;
3. choose exact signed Z_72 displacements deterministically;
4. annotate every selected edge with independent Hopf and Clifford metadata;
5. execute the reverse edge sequence and require exact source restoration.

Two finite displacement candidates may be materialized for the same endpoints:
the shortest signed Z_72 representative and, where distinct, its complementary
wrap representative.  Selection is a lexicographic exact-integer comparison,
not a weighted scalar objective.  Classification metadata is advisory only and
never receives VM81 mutation, Hash72 mint, or Hash216 persistence authority.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

from hhs_runtime.pass219.discrete_hopf_projection import (
    classify_chiral_pair_flip_hopf,
    classify_coupled_generator_hopf,
)
from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    CHANNELS,
    GYROSCOPE_SCHEMA,
    PHASE_MODULUS,
    PRODUCT_RELATIONS,
    advance_gyroscope,
)
from hhs_runtime.pass219.gyroscope_admission_membrane import (
    CHIRAL_PAIRS,
    build_chirality_polarity_witness,
    construct_admissible_reciprocal_path,
    flip_chiral_pair_half_turn,
)
from hhs_runtime.pass219.phase_clifford_intertwiner import (
    audit_rml5_generators_on_phase_clifford_bridge,
    classify_chiral_pair_flip_clifford,
    classify_coupled_generator_clifford,
)

PASS = 219
ITERATION = "RML12_RECIPROCAL_ROUTE_OPTIMIZER"

EDGE_SCHEMA = "HHS_PASS219_RML12_RECIPROCAL_ROUTE_EDGE_V1"
PLAN_SCHEMA = "HHS_PASS219_RML12_RECIPROCAL_ROUTE_PLAN_V1"
SELECTION_SCHEMA = "HHS_PASS219_RML12_DETERMINISTIC_ROUTE_SELECTION_V1"
AUDIT_SCHEMA = "HHS_PASS219_RML12_ROUTE_METADATA_GENERATOR_AUDIT_V1"

GENERATOR_ORDER = ("x", "y", "z", "w")
GENERATOR_TO_PRODUCT = {
    relation["generator"]: product for product, relation in PRODUCT_RELATIONS.items()
}

SHORTEST_POLICY = "SHORTEST_SIGNED_Z72"
COMPLEMENTARY_POLICY = "COMPLEMENTARY_WRAP_Z72"
SUPPORTED_DELTA_POLICIES = (SHORTEST_POLICY, COMPLEMENTARY_POLICY)


class ReciprocalRouteOptimizerError(RuntimeError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise ReciprocalRouteOptimizerError(f"FLOAT_ROUTE_AUTHORITY_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _canonical(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _exact_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ReciprocalRouteOptimizerError(f"{label}_EXACT_INTEGER_REQUIRED")
    return value


def _require_admissible_state(state: Mapping[str, Any]) -> Mapping[str, Any]:
    _reject_float(state)
    if state.get("schema") != GYROSCOPE_SCHEMA:
        raise ReciprocalRouteOptimizerError("RML4_GYROSCOPE_STATE_REQUIRED")
    if state.get("admissible_product_geometry") is not True:
        raise ReciprocalRouteOptimizerError("RML12_ADMISSIBLE_PRODUCT_GEOMETRY_REQUIRED")
    phases = state.get("phases")
    signs = state.get("quarter_turn_signs")
    if not isinstance(phases, Mapping) or tuple(phases.keys()) != CHANNELS:
        raise ReciprocalRouteOptimizerError("RML12_ORDERED_EIGHT_PHASE_STATE_REQUIRED")
    if not isinstance(signs, Mapping):
        raise ReciprocalRouteOptimizerError("RML12_PRODUCT_SIGN_MAPPING_REQUIRED")
    chirality = build_chirality_polarity_witness(state)
    if chirality["all_chiral_pairs_opposed"] is not True:
        raise ReciprocalRouteOptimizerError("RML12_BALANCED_CHIRALITY_REQUIRED")
    return state


def _same_phase_state(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return (
        left.get("phases") == right.get("phases")
        and left.get("quarter_turn_signs") == right.get("quarter_turn_signs")
        and left.get("ambient_state_index") == right.get("ambient_state_index")
    )


def shortest_signed_delta(source: int, target: int) -> int:
    """Exact deterministic shortest representative in Z_72.

    The u^36 tie is resolved in the positive direction, matching the existing
    RML5 constructive path operator.
    """
    a = _exact_int(source, "SOURCE_PHASE") % PHASE_MODULUS
    b = _exact_int(target, "TARGET_PHASE") % PHASE_MODULUS
    forward = (b - a) % PHASE_MODULUS
    backward = forward - PHASE_MODULUS
    return forward if abs(forward) <= abs(backward) else backward


def complementary_wrap_delta(shortest_delta: int) -> int:
    """Return the other Z_72 representative when it is strictly longer.

    At 0 and the u^36 antipode there is no strictly longer canonical
    complementary representative used by RML12, so the shortest value is kept.
    """
    delta = _exact_int(shortest_delta, "SHORTEST_DELTA")
    if delta == 0 or abs(delta) == PHASE_MODULUS // 2:
        return delta
    return delta - PHASE_MODULUS if delta > 0 else delta + PHASE_MODULUS


def _selected_delta(source: int, target: int, policy: str) -> int:
    shortest = shortest_signed_delta(source, target)
    if policy == SHORTEST_POLICY:
        return shortest
    if policy == COMPLEMENTARY_POLICY:
        return complementary_wrap_delta(shortest)
    raise ReciprocalRouteOptimizerError("RML12_DELTA_POLICY_UNSUPPORTED")


def _edge_class_tags(hopf: Mapping[str, Any], clifford_lift: Mapping[str, Any]) -> list[str]:
    tags: list[str] = []
    tags.append(
        "HOPF_SAME_BASE"
        if hopf.get("same_hopf_base") is True
        else "HOPF_BASE_MOVING"
    )
    if clifford_lift.get("complete_clifford_lift") is not True:
        tags.append("RESIDUAL_U72_PHASE")
    elif clifford_lift.get("full_cl08_module_intertwiner") is True:
        tags.append("FULL_CL08_INTERTWINER")
    elif clifford_lift.get("full_transform_chirality_sector_swapping") is True:
        tags.append("CLIFFORD_CHIRALITY_SWAP")
    else:
        tags.append("CLIFFORD_SECTOR_PRESERVING_NONINTERTWINER")
    return tags


def build_coupled_route_edge(
    state: Mapping[str, Any],
    *,
    generator: str,
    signed_steps: int,
    edge_id: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build and classify one reversible coupled generator/product edge."""
    state = _require_admissible_state(state)
    if generator not in GENERATOR_TO_PRODUCT:
        raise ReciprocalRouteOptimizerError("RML12_GENERATOR_UNSUPPORTED")
    delta = _exact_int(signed_steps, "SIGNED_STEPS")
    product = GENERATOR_TO_PRODUCT[generator]
    steps = {channel: 0 for channel in CHANNELS}
    steps[generator] = delta
    steps[product] = delta

    transition = advance_gyroscope(state, steps, transition_id=edge_id)
    target = transition["next_state"]
    if target["admissible_product_geometry"] is not True:
        raise AssertionError("RML12_COUPLED_EDGE_LEFT_ADMISSIBLE_MANIFOLD")

    hopf = classify_coupled_generator_hopf(
        state,
        generator=generator,
        signed_steps=delta,
        transition_id=edge_id,
    )
    clifford = classify_coupled_generator_clifford(
        state,
        generator=generator,
        signed_steps=delta,
        transition_id=edge_id,
    )
    if clifford["transition_sha256"] != transition["transition_sha256"]:
        raise AssertionError("RML12_CLIFFORD_TRANSITION_IDENTITY_DRIFT")
    if clifford["target_state_sha256"] != target["state_sha256"]:
        raise AssertionError("RML12_CLIFFORD_TARGET_STATE_DRIFT")
    if hopf["explicit_inverse_restores_exact_hopf_base"] is not True:
        raise AssertionError("RML12_HOPF_INVERSE_RESTORATION_REQUIRED")

    inverse_steps = {channel: -steps[channel] for channel in CHANNELS}
    inverse = advance_gyroscope(
        target,
        inverse_steps,
        transition_id=f"inverse:{edge_id}:rml12",
    )
    restored = inverse["next_state"]
    inverse_restores = _same_phase_state(restored, state)
    if not inverse_restores:
        raise AssertionError("RML12_COUPLED_EDGE_INVERSE_FAILED")

    lift = clifford["clifford_lift"]
    edge = {
        "schema": EDGE_SCHEMA,
        "edge_id": str(edge_id),
        "kind": "COUPLED_GENERATOR_PRODUCT_PHASE_MOVE",
        "generator": generator,
        "dependent_product": product,
        "signed_steps": delta,
        "ordered_signed_steps": steps,
        "source_ambient_state_index": state["ambient_state_index"],
        "target_ambient_state_index": target["ambient_state_index"],
        "source_state_sha256": state["state_sha256"],
        "target_state_sha256": target["state_sha256"],
        "transition_sha256": transition["transition_sha256"],
        "hopf_classification": hopf["classification"],
        "same_hopf_base": hopf["same_hopf_base"],
        "clifford_full_phase_classification": lift["full_phase_transform_classification"],
        "complete_clifford_lift": lift["complete_clifford_lift"],
        "residual_u72_phase_preserved": lift["residual_u72_phase_preserved"],
        "full_cl08_module_intertwiner": lift["full_cl08_module_intertwiner"],
        "clifford_chirality_sector_swapping": lift["full_transform_chirality_sector_swapping"],
        "clifford_chirality_sector_preserving": lift["full_transform_chirality_sector_preserving"],
        "route_class_tags": _edge_class_tags(hopf, lift),
        "exact_inverse_restores_source_phase_state": True,
        "inverse_transition_sha256": inverse["transition_sha256"],
        "phase_transport_units": 2 * abs(delta),
        "target_product_geometry_admissible": True,
        "classification_metadata_has_transition_authority": False,
        "gradient_descent_used": False,
        "floating_score_used": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    edge["edge_sha256"] = _sha256(edge)
    return edge, target


def build_pair_flip_route_edge(
    state: Mapping[str, Any],
    *,
    pair_index: int,
    edge_id: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build and classify one exact self-inverse u^36 chiral-pair edge."""
    state = _require_admissible_state(state)
    index = _exact_int(pair_index, "PAIR_INDEX")
    if index < 0 or index >= len(CHIRAL_PAIRS):
        raise ReciprocalRouteOptimizerError("RML12_PAIR_INDEX_OUT_OF_RANGE")

    flip = flip_chiral_pair_half_turn(state, pair_index=index, transition_id=edge_id)
    target = flip["next_state"]
    hopf = classify_chiral_pair_flip_hopf(
        state,
        pair_index=index,
        transition_id=edge_id,
    )
    clifford = classify_chiral_pair_flip_clifford(
        state,
        pair_index=index,
        transition_id=edge_id,
    )
    if clifford["transition_sha256"] != flip["transition_sha256"]:
        raise AssertionError("RML12_PAIR_FLIP_CLIFFORD_TRANSITION_DRIFT")
    if clifford["target_state_sha256"] != target["state_sha256"]:
        raise AssertionError("RML12_PAIR_FLIP_TARGET_STATE_DRIFT")
    if hopf["explicit_inverse_restores_exact_hopf_base"] is not True:
        raise AssertionError("RML12_PAIR_FLIP_HOPF_INVERSE_RESTORATION_REQUIRED")

    inverse = flip_chiral_pair_half_turn(
        target,
        pair_index=index,
        transition_id=f"inverse:{edge_id}:rml12",
    )
    if not _same_phase_state(inverse["next_state"], state):
        raise AssertionError("RML12_PAIR_FLIP_INVERSE_FAILED")

    lift = clifford["clifford_lift"]
    edge = {
        "schema": EDGE_SCHEMA,
        "edge_id": str(edge_id),
        "kind": "CHIRAL_PAIR_U36_FLIP",
        "pair_index": index,
        "pair": list(CHIRAL_PAIRS[index]),
        "phase_inversion_steps_per_product": PHASE_MODULUS // 2,
        "source_ambient_state_index": state["ambient_state_index"],
        "target_ambient_state_index": target["ambient_state_index"],
        "source_state_sha256": state["state_sha256"],
        "target_state_sha256": target["state_sha256"],
        "transition_sha256": flip["transition_sha256"],
        "hopf_classification": hopf["classification"],
        "same_hopf_base": hopf["same_hopf_base"],
        "clifford_full_phase_classification": lift["full_phase_transform_classification"],
        "complete_clifford_lift": lift["complete_clifford_lift"],
        "residual_u72_phase_preserved": lift["residual_u72_phase_preserved"],
        "full_cl08_module_intertwiner": lift["full_cl08_module_intertwiner"],
        "clifford_chirality_sector_swapping": lift["full_transform_chirality_sector_swapping"],
        "clifford_chirality_sector_preserving": lift["full_transform_chirality_sector_preserving"],
        "route_class_tags": _edge_class_tags(hopf, lift),
        "exact_inverse_restores_source_phase_state": True,
        "self_inverse_u36_pair_flip": True,
        "phase_transport_units": PHASE_MODULUS,
        "target_product_geometry_admissible": target["admissible_product_geometry"],
        "classification_metadata_has_transition_authority": False,
        "gradient_descent_used": False,
        "floating_score_used": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    edge["edge_sha256"] = _sha256(edge)
    return edge, target


def _reverse_route_exact(
    terminal_state: Mapping[str, Any],
    edges: Sequence[Mapping[str, Any]],
    source: Mapping[str, Any],
    *,
    route_id: str,
) -> bool:
    current = dict(terminal_state)
    for reverse_index, edge in enumerate(reversed(edges)):
        kind = edge.get("kind")
        if kind == "COUPLED_GENERATOR_PRODUCT_PHASE_MOVE":
            generator = str(edge.get("generator"))
            product = str(edge.get("dependent_product"))
            delta = _exact_int(edge.get("signed_steps"), "EDGE_SIGNED_STEPS")
            steps = {channel: 0 for channel in CHANNELS}
            steps[generator] = -delta
            steps[product] = -delta
            transition = advance_gyroscope(
                current,
                steps,
                transition_id=f"{route_id}:reverse:{reverse_index}:{generator}",
            )
            current = transition["next_state"]
        elif kind == "CHIRAL_PAIR_U36_FLIP":
            pair_index = _exact_int(edge.get("pair_index"), "EDGE_PAIR_INDEX")
            flip = flip_chiral_pair_half_turn(
                current,
                pair_index=pair_index,
                transition_id=f"{route_id}:reverse:{reverse_index}:pair:{pair_index}",
            )
            current = flip["next_state"]
        else:
            raise ReciprocalRouteOptimizerError("RML12_ROUTE_EDGE_KIND_UNSUPPORTED")
        if current.get("admissible_product_geometry") is not True:
            raise AssertionError("RML12_REVERSE_ROUTE_LEFT_ADMISSIBLE_MANIFOLD")
    return _same_phase_state(current, source)


def _plan_metrics(edges: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {
        "move_count": len(edges),
        "pair_flip_edges": sum(edge.get("kind") == "CHIRAL_PAIR_U36_FLIP" for edge in edges),
        "coupled_move_edges": sum(edge.get("kind") == "COUPLED_GENERATOR_PRODUCT_PHASE_MOVE" for edge in edges),
        "total_phase_transport_units": sum(int(edge.get("phase_transport_units", 0)) for edge in edges),
        "hopf_same_base_edges": sum(edge.get("same_hopf_base") is True for edge in edges),
        "hopf_base_moving_edges": sum(edge.get("same_hopf_base") is not True for edge in edges),
        "complete_clifford_lift_edges": sum(edge.get("complete_clifford_lift") is True for edge in edges),
        "residual_u72_edges": sum(edge.get("residual_u72_phase_preserved") is True for edge in edges),
        "full_cl08_intertwiner_edges": sum(edge.get("full_cl08_module_intertwiner") is True for edge in edges),
        "clifford_chirality_swap_edges": sum(edge.get("clifford_chirality_sector_swapping") is True for edge in edges),
    }


def _selection_vector(metrics: Mapping[str, int], *, policy_preference: int) -> list[int]:
    """Exact lexicographic selector; no weighted scalar objective is formed."""
    return [
        _exact_int(metrics["move_count"], "MOVE_COUNT"),
        _exact_int(metrics["total_phase_transport_units"], "TOTAL_PHASE_TRANSPORT_UNITS"),
        _exact_int(metrics["residual_u72_edges"], "RESIDUAL_U72_EDGES"),
        _exact_int(metrics["hopf_base_moving_edges"], "HOPF_BASE_MOVING_EDGES"),
        _exact_int(metrics["clifford_chirality_swap_edges"], "CLIFFORD_CHIRALITY_SWAP_EDGES"),
        _exact_int(policy_preference, "POLICY_PREFERENCE"),
    ]


def build_reciprocal_route_plan(
    source: Mapping[str, Any],
    target: Mapping[str, Any],
    *,
    route_id: str,
    delta_policy: str = SHORTEST_POLICY,
) -> dict[str, Any]:
    """Construct one exact reversible source->target route with orthogonal metadata."""
    source = _require_admissible_state(source)
    target = _require_admissible_state(target)
    if delta_policy not in SUPPORTED_DELTA_POLICIES:
        raise ReciprocalRouteOptimizerError("RML12_DELTA_POLICY_UNSUPPORTED")

    current = dict(source)
    edges: list[dict[str, Any]] = []

    # Stage 1: exact chirality-sector alignment.
    for pair_index, (forward, reverse) in enumerate(CHIRAL_PAIRS):
        if current["quarter_turn_signs"][forward] != target["quarter_turn_signs"][forward]:
            edge, current = build_pair_flip_route_edge(
                current,
                pair_index=pair_index,
                edge_id=f"{route_id}:flip:{forward}:{reverse}",
            )
            edges.append(edge)

    # Stage 2: exact direct coordinate alignment in canonical primitive order.
    for generator in GENERATOR_ORDER:
        delta = _selected_delta(
            int(current["phases"][generator]),
            int(target["phases"][generator]),
            delta_policy,
        )
        if delta == 0:
            continue
        edge, current = build_coupled_route_edge(
            current,
            generator=generator,
            signed_steps=delta,
            edge_id=f"{route_id}:move:{generator}:{delta}",
        )
        edges.append(edge)

    target_reached = _same_phase_state(current, target)
    if not target_reached:
        raise AssertionError("RML12_ROUTE_DID_NOT_REACH_TARGET")
    reverse_restores = _reverse_route_exact(current, edges, source, route_id=route_id)
    if not reverse_restores:
        raise AssertionError("RML12_REVERSE_ROUTE_DID_NOT_RESTORE_SOURCE")

    metrics = _plan_metrics(edges)
    policy_preference = 0 if delta_policy == SHORTEST_POLICY else 1
    reference = construct_admissible_reciprocal_path(
        source,
        target,
        path_id=f"{route_id}:rml5-reference",
    )
    if reference["target_reached_exactly"] is not True or reference["all_moves_reversible"] is not True:
        raise AssertionError("RML12_INHERITED_RML5_PATH_PROOF_DRIFT")

    plan = {
        "schema": PLAN_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "route_id": str(route_id),
        "source_state_sha256": source["state_sha256"],
        "target_state_sha256": target["state_sha256"],
        "source_ambient_state_index": source["ambient_state_index"],
        "target_ambient_state_index": target["ambient_state_index"],
        "delta_policy": delta_policy,
        "construction_stages": [
            "ALIGN_CHIRAL_SECTORS_WITH_SELF_INVERSE_U36_PAIR_FLIPS",
            "ALIGN_X_Y_Z_W_WITH_COUPLED_GENERATOR_PRODUCT_Z72_MOVES",
        ],
        "generator_order": list(GENERATOR_ORDER),
        "edges": edges,
        "metrics": metrics,
        "selection_vector": _selection_vector(metrics, policy_preference=policy_preference),
        "selection_vector_is_lexicographic_not_weighted_sum": True,
        "target_reached_exactly": True,
        "reverse_edge_sequence_restores_source_exactly": True,
        "all_edges_reversible": all(edge["exact_inverse_restores_source_phase_state"] for edge in edges),
        "all_edges_remain_in_admissible_product_geometry": all(edge["target_product_geometry_admissible"] for edge in edges),
        "rml5_reference_path_sha256": reference["path_sha256"],
        "rml5_reference_move_count": reference["move_count"],
        "rml5_reference_strong_connectivity_witness_retained": reference[
            "strong_connectivity_proven_for_rml5_balanced_chirality_manifold"
        ],
        "hopf_metadata_has_transition_authority": False,
        "clifford_metadata_has_transition_authority": False,
        "route_selector_has_canonical_transition_authority": False,
        "gradient_descent_used": False,
        "loss_function_used": False,
        "floating_score_used": False,
        "probabilistic_search_used": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "floating_point_authority": False,
        "scalar_projection_substitution_authority": False,
    }
    plan["route_sha256"] = _sha256(plan)
    return plan


def select_preferred_reciprocal_route(plans: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Select among already-valid routes with exact lexicographic metadata."""
    if not isinstance(plans, Sequence) or isinstance(plans, (str, bytes)) or not plans:
        raise ReciprocalRouteOptimizerError("RML12_NONEMPTY_ROUTE_PLAN_SEQUENCE_REQUIRED")
    normalized = list(plans)
    source_indices = {plan.get("source_ambient_state_index") for plan in normalized}
    target_indices = {plan.get("target_ambient_state_index") for plan in normalized}
    if len(source_indices) != 1 or len(target_indices) != 1:
        raise ReciprocalRouteOptimizerError("RML12_ROUTE_CANDIDATES_MUST_SHARE_ENDPOINTS")
    for plan in normalized:
        if plan.get("schema") != PLAN_SCHEMA:
            raise ReciprocalRouteOptimizerError("RML12_ROUTE_PLAN_SCHEMA_REQUIRED")
        if plan.get("target_reached_exactly") is not True or plan.get("reverse_edge_sequence_restores_source_exactly") is not True:
            raise ReciprocalRouteOptimizerError("RML12_ONLY_EXACT_REVERSIBLE_ROUTE_CANDIDATES_ALLOWED")
        vector = plan.get("selection_vector")
        if not isinstance(vector, list) or any(isinstance(v, bool) or not isinstance(v, int) for v in vector):
            raise ReciprocalRouteOptimizerError("RML12_EXACT_INTEGER_SELECTION_VECTOR_REQUIRED")

    ordered = sorted(
        normalized,
        key=lambda plan: (tuple(plan["selection_vector"]), str(plan["route_sha256"])),
    )
    selected = ordered[0]
    result = {
        "schema": SELECTION_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "candidate_count": len(ordered),
        "candidate_route_sha256": [plan["route_sha256"] for plan in ordered],
        "candidate_selection_vectors": [list(plan["selection_vector"]) for plan in ordered],
        "selected_route_sha256": selected["route_sha256"],
        "selected_route_id": selected["route_id"],
        "selected_delta_policy": selected["delta_policy"],
        "selection_method": "EXACT_LEXICOGRAPHIC_INTEGER_VECTOR",
        "weighted_scalar_objective_used": False,
        "gradient_descent_used": False,
        "probabilistic_search_used": False,
        "selection_changes_transition_authority": False,
        "canonical_vm81_mutation_authority": False,
    }
    result["selection_sha256"] = _sha256(result)
    return result


def build_and_select_reciprocal_route(
    source: Mapping[str, Any],
    target: Mapping[str, Any],
    *,
    route_id: str,
) -> dict[str, Any]:
    """Materialize bounded exact alternatives and select the deterministic route."""
    shortest = build_reciprocal_route_plan(
        source,
        target,
        route_id=f"{route_id}:shortest",
        delta_policy=SHORTEST_POLICY,
    )
    complementary = build_reciprocal_route_plan(
        source,
        target,
        route_id=f"{route_id}:complementary",
        delta_policy=COMPLEMENTARY_POLICY,
    )
    selection = select_preferred_reciprocal_route([shortest, complementary])
    result = {
        "schema": "HHS_PASS219_RML12_SELECTED_RECIPROCAL_ROUTE_BUNDLE_V1",
        "shortest_candidate": shortest,
        "complementary_candidate": complementary,
        "selection": selection,
        "selected_shortest_signed_route": selection["selected_route_sha256"] == shortest["route_sha256"],
        "canonical_transition_authority_expanded": False,
    }
    result["bundle_sha256"] = _sha256(result)
    return result


def audit_rml5_generator_route_metadata(state: Mapping[str, Any]) -> dict[str, Any]:
    """Cross-tab the complete 290-case generator family by Hopf x Clifford metadata."""
    state = _require_admissible_state(state)
    cross_tab: dict[str, int] = {}
    total = 0
    inverse_failures = 0

    for generator in GENERATOR_ORDER:
        for phase_step in range(PHASE_MODULUS):
            edge, _ = build_coupled_route_edge(
                state,
                generator=generator,
                signed_steps=phase_step,
                edge_id=f"rml12:audit:{generator}:{phase_step}",
            )
            key = f"{edge['hopf_classification']}|{edge['clifford_full_phase_classification']}"
            cross_tab[key] = cross_tab.get(key, 0) + 1
            total += 1
            if edge["exact_inverse_restores_source_phase_state"] is not True:
                inverse_failures += 1

    for pair_index in range(len(CHIRAL_PAIRS)):
        edge, _ = build_pair_flip_route_edge(
            state,
            pair_index=pair_index,
            edge_id=f"rml12:audit:pair:{pair_index}",
        )
        key = f"{edge['hopf_classification']}|{edge['clifford_full_phase_classification']}"
        cross_tab[key] = cross_tab.get(key, 0) + 1
        total += 1
        if edge["exact_inverse_restores_source_phase_state"] is not True:
            inverse_failures += 1

    inherited = audit_rml5_generators_on_phase_clifford_bridge(state)
    if total != 290 or total != inherited["total_generator_cases"]:
        raise AssertionError("RML12_GENERATOR_AUDIT_CARDINALITY_DRIFT")
    if sum(cross_tab.values()) != total:
        raise AssertionError("RML12_ROUTE_METADATA_CROSS_TAB_DRIFT")

    result = {
        "schema": AUDIT_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "source_state_sha256": state["state_sha256"],
        "total_generator_cases": total,
        "route_metadata_cross_tab": dict(sorted(cross_tab.items())),
        "cross_tab_partition_complete": sum(cross_tab.values()) == total,
        "exact_inverse_failures": inverse_failures,
        "all_generator_edges_reversible": inverse_failures == 0,
        "inherited_complete_clifford_lift_cases": inherited["complete_clifford_lift_cases"],
        "inherited_residual_u72_phase_cases": inherited["residual_u72_phase_cases"],
        "inherited_full_cl08_module_intertwiner_cases": inherited["full_cl08_module_intertwiner_cases"],
        "inherited_odd_chirality_sector_swapping_cases": inherited["odd_chirality_sector_swapping_cases"],
        "inherited_same_hopf_base_cases": inherited["inherited_same_hopf_base_cases"],
        "inherited_base_moving_hopf_cases": inherited["inherited_base_moving_hopf_cases"],
        "hopf_and_clifford_metadata_retained_as_orthogonal_axes": True,
        "gradient_descent_used": False,
        "classification_metadata_has_transition_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    result["audit_sha256"] = _sha256(result)
    return result


__all__ = [
    "AUDIT_SCHEMA",
    "COMPLEMENTARY_POLICY",
    "EDGE_SCHEMA",
    "GENERATOR_ORDER",
    "PLAN_SCHEMA",
    "SELECTION_SCHEMA",
    "SHORTEST_POLICY",
    "ReciprocalRouteOptimizerError",
    "audit_rml5_generator_route_metadata",
    "build_and_select_reciprocal_route",
    "build_coupled_route_edge",
    "build_pair_flip_route_edge",
    "build_reciprocal_route_plan",
    "complementary_wrap_delta",
    "select_preferred_reciprocal_route",
    "shortest_signed_delta",
]

from __future__ import annotations

import hashlib
import json

import pytest

from hhs_runtime.pass219.phase_geometry_learning import (
    GEOMETRY_WITNESS_SCHEMA,
    HALF_CYCLE,
    LANES,
    OCTONION_STRING_SCHEMA,
    PHASE_CANDIDATE_SCHEMA,
    PHASE_CHANNELS,
    PHASE_CIRCUIT_SCHEMA,
    PhaseGeometryError,
    canonical_phase_geometry,
    evaluate_octonion_string,
    evaluate_phase_circuit,
    evaluate_phase_geometric_candidate,
    learn_phase_geometric_frontier,
)
from hhs_runtime.pass219.recursive_manifold_learning import (
    CANDIDATE_SCHEMA,
    EDGE_SCHEMA,
    PLAN_SCHEMA,
)


def _sha(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _phase_nodes(prefix: str) -> dict[str, str]:
    return {channel: f"{prefix}:{channel}" for channel in PHASE_CHANNELS}


def _plan() -> dict[str, object]:
    workloads = [
        {
            "lane": lane,
            "provider_decision": "PROPAGATE",
            "i153_survives": True,
            "authority_packet_sha256": f"{i + 1:064x}",
            "transition_hash216": chr(65 + i) * 216,
            "proof_hash216": chr(69 + i) * 216,
            "receipt_hash72": chr(73 + i) * 72,
            "replay_hash72": chr(77 + i) * 72,
        }
        for i, lane in enumerate(LANES)
    ]
    plan: dict[str, object] = {
        "schema": PLAN_SCHEMA,
        "pass": 219,
        "iteration": "I154",
        "classification": "TEST_ONLY_FOUR_LANE_PLUMBING_WITHIN_81_OVER_7",
        "lanes": list(LANES),
        "workloads": workloads,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "result": "PASS",
    }
    plan["receipt_sha256"] = _sha(plan)
    return plan


def _edge(edge_id: str, offset: int, mismatch: bool = False) -> dict[str, object]:
    return {
        "schema": EDGE_SCHEMA,
        "edge_id": edge_id,
        "operator": "==" if offset % 2 else "=",
        "source_offset": offset,
        "nesting_path": [0, offset + 1],
        "lhs_node_id": f"{edge_id}:lhs",
        "rhs_node_id": f"{edge_id}:rhs",
        "lhs_source_sha256": _sha([edge_id, "lhs"]),
        "rhs_source_sha256": _sha([edge_id, "rhs"]),
        "parenthesization_sha256": _sha([edge_id, "paren"]),
        "ordered_operands_sha256": _sha([edge_id, "order"]),
        "commutative_reorder_permitted": False,
        "nonassociative_rewrite_permitted": False,
        "scalar_projection_substitution_authority": False,
        "A_state": "OTHER" if mismatch else "P2",
        "P2_state": "P2",
        "B_state": "P2",
        "sqrt_AB_state": "P2",
        "sqrt_BA_state": "P2",
        "pq_plus_one_state": "P2",
    }


def _candidate(
    plan: dict[str, object],
    candidate_id: str,
    constraint_mismatch_lane: int | None = None,
) -> dict[str, object]:
    by_lane = {row["lane"]: row for row in plan["workloads"]}
    root = _sha({"candidate": candidate_id})
    lane_witnesses = []
    for i, lane in enumerate(LANES):
        parent = by_lane[lane]
        lane_witnesses.append(
            {
                "lane": lane,
                "authority_packet_sha256": parent["authority_packet_sha256"],
                "parent_transition_hash216": parent["transition_hash216"],
                "candidate_transition_hash216": chr(81 + i) * 216,
                "candidate_receipt_hash72": chr(85 + i) * 72,
                "candidate_manifold_root_sha256": root,
                "ordered_phase_node_ids": _phase_nodes(lane),
                "equality_edges": [
                    _edge(f"{lane}:e0", i * 10, constraint_mismatch_lane == i),
                    _edge(f"{lane}:e1", i * 10 + 1),
                ],
            }
        )
    return {
        "schema": CANDIDATE_SCHEMA,
        "candidate_id": candidate_id,
        "plan_receipt_sha256": plan["receipt_sha256"],
        "candidate_manifold_root_sha256": root,
        "variable_nodes": [
            {"symbol": symbol, "node_id": f"var:{symbol}", "state_token": token}
            for symbol, token in (
                ("A", "P2"), ("B", "P2"), ("P", "P"), ("p", "p"), ("q", "q"),
                ("x", "x"), ("y", "y"), ("z", "z"), ("w", "w"),
                ("xy", "xy"), ("yx", "yx"), ("zw", "zw"), ("wz", "wz"),
            )
        ],
        "lane_witnesses": lane_witnesses,
    }


def _string(
    string_id: str,
    parent: str,
    steps: tuple[int, int, int, int] = (0, 0, 0, 0),
    fold_tree: object | None = None,
) -> dict[str, object]:
    x, y, z, w = steps
    return {
        "schema": OCTONION_STRING_SCHEMA,
        "string_id": string_id,
        "parent_circuit_id": parent,
        "phase_steps": {"x": x, "y": y, "z": z, "w": w},
        "ordered_phase_node_ids": _phase_nodes(f"oct:{string_id}"),
        "fold_tree": fold_tree if fold_tree is not None else [["x", "y"], ["z", "w"]],
    }


def _circuit(
    circuit_id: str,
    steps: tuple[int, int, int, int] = (0, 0, 0, 0),
) -> dict[str, object]:
    return {
        "schema": PHASE_CIRCUIT_SCHEMA,
        "circuit_id": circuit_id,
        "parent_circuit_id": None,
        "children": [_string(f"{circuit_id}:leaf", circuit_id, steps)],
    }


def _package(
    plan: dict[str, object],
    candidate_id: str,
    steps: tuple[int, int, int, int] = (0, 0, 0, 0),
    constraint_mismatch_lane: int | None = None,
) -> dict[str, object]:
    candidate = _candidate(plan, candidate_id, constraint_mismatch_lane)
    circuit = _circuit(f"circuit:{candidate_id}", steps)
    circuit_root = evaluate_phase_circuit(circuit)["circuit_root_sha256"]
    geometry = {
        "schema": GEOMETRY_WITNESS_SCHEMA,
        "candidate_manifold_root_sha256": candidate["candidate_manifold_root_sha256"],
        "root_circuit": circuit,
        "lane_bindings": [
            {
                "lane": lane["lane"],
                "candidate_transition_hash216": lane["candidate_transition_hash216"],
                "ordered_phase_node_ids": dict(lane["ordered_phase_node_ids"]),
                "phase_circuit_root_sha256": circuit_root,
            }
            for lane in candidate["lane_witnesses"]
        ],
    }
    return {"schema": PHASE_CANDIDATE_SCHEMA, "candidate": candidate, "phase_geometry": geometry}


def test_canonical_two_plane_rotor_orientation_is_exact() -> None:
    geometry = canonical_phase_geometry()
    assert geometry["rotors"]["x"] == {"plane": "PRIMARY_XZ", "direction": "CW", "signed_orientation": 1}
    assert geometry["rotors"]["z"] == {"plane": "PRIMARY_XZ", "direction": "CCW", "signed_orientation": -1}
    assert geometry["rotors"]["y"] == {"plane": "ORTHOGONAL_YW", "direction": "CCW", "signed_orientation": -1}
    assert geometry["rotors"]["w"] == {"plane": "ORTHOGONAL_YW", "direction": "CW", "signed_orientation": 1}
    assert (geometry["quarter_cycle"], geometry["half_cycle"], geometry["full_cycle"]) == (18, 36, 72)


def test_typed_u0_is_legal_phase_position_and_not_scalar_zero() -> None:
    result = evaluate_octonion_string(_string("u0", "root"), expected_parent_circuit_id="root")
    assert result["phase_positions"] == {"x": "u^0", "y": "u^0", "z": "u^0", "w": "u^0"}
    assert result["phase_closed"] is True
    assert result["typed_u0_is_scalar_zero"] is False


def test_u36_half_cycle_closes_for_all_four_rotors() -> None:
    result = evaluate_octonion_string(
        _string("half", "root", (HALF_CYCLE,) * 4),
        expected_parent_circuit_id="root",
    )
    assert result["phase_closed"] is True
    assert result["half_cycle_rotors"] == ["x", "y", "z", "w"]


def test_phase_pair_mismatch_is_typed_not_scalarized() -> None:
    result = evaluate_octonion_string(
        _string("mismatch", "root", (5, 7, 3, 7)),
        expected_parent_circuit_id="root",
    )
    assert result["primary_pair_disequilibrium_units"] == 2
    assert result["orthogonal_pair_disequilibrium_units"] == 0
    assert result["net_signed_phase_disequilibrium_units"] == 2
    assert result["phase_closed"] is False


def test_fold_order_and_nonassociative_parenthesization_are_identity() -> None:
    ordered = evaluate_octonion_string(
        _string("ordered", "root", fold_tree=[["x", "y"], ["z", "w"]]),
        expected_parent_circuit_id="root",
    )
    reordered = evaluate_octonion_string(
        _string("reordered", "root", fold_tree=[["y", "x"], ["z", "w"]]),
        expected_parent_circuit_id="root",
    )
    left = evaluate_octonion_string(
        _string("left", "root", fold_tree=[[ ["x", "y"], "z"], "w"]),
        expected_parent_circuit_id="root",
    )
    right = evaluate_octonion_string(
        _string("right", "root", fold_tree=["x", ["y", ["z", "w"]]]),
        expected_parent_circuit_id="root",
    )
    assert ordered["fold_word_sha256"] != reordered["fold_word_sha256"]
    assert left["fold_word"] == right["fold_word"] == ["x", "y", "z", "w"]
    assert left["parenthesization_sha256"] != right["parenthesization_sha256"]


def test_nested_entangled_circuits_preserve_child_order_and_depth() -> None:
    inner = {
        "schema": PHASE_CIRCUIT_SCHEMA,
        "circuit_id": "inner",
        "parent_circuit_id": "outer",
        "children": [_string("inner:leaf", "inner", (18, 18, 18, 18))],
    }
    outer = {
        "schema": PHASE_CIRCUIT_SCHEMA,
        "circuit_id": "outer",
        "parent_circuit_id": None,
        "children": [inner, _string("outer:leaf", "outer")],
    }
    result = evaluate_phase_circuit(outer)
    assert result["ordered_child_ids"] == ["inner", "outer:leaf"]
    assert result["leaf_string_count"] == 2
    assert result["nested_circuit_count"] == 1
    assert result["phase_closed"] is True


def test_swapping_entangled_children_changes_circuit_identity() -> None:
    a = _string("a", "root")
    b = _string("b", "root")
    first = {"schema": PHASE_CIRCUIT_SCHEMA, "circuit_id": "root", "parent_circuit_id": None, "children": [a, b]}
    second = {"schema": PHASE_CIRCUIT_SCHEMA, "circuit_id": "root", "parent_circuit_id": None, "children": [b, a]}
    assert evaluate_phase_circuit(first)["circuit_root_sha256"] != evaluate_phase_circuit(second)["circuit_root_sha256"]


def test_phase_geometry_binds_to_all_four_rml_lanes_without_new_authority() -> None:
    plan = _plan()
    result = evaluate_phase_geometric_candidate(plan, _package(plan, "zero"))
    assert result["typed_disequilibrium_vector"] == {
        "constraint_units": 0,
        "primary_pair_units": 0,
        "orthogonal_pair_units": 0,
        "net_signed_phase_units": 0,
        "nonclosed_leaf_count": 0,
    }
    assert result["zero_disequilibrium"] is True
    assert result["canonical_vm81_mutation_authority"] is False
    assert result["canonical_hash72_mint_authority"] is False
    assert result["canonical_hash216_persistence_authority"] is False


def test_phase_lane_binding_drift_fails_closed() -> None:
    plan = _plan()
    package = _package(plan, "drift")
    package["phase_geometry"]["lane_bindings"][0]["ordered_phase_node_ids"]["xy"] = "wrong:xy"
    with pytest.raises(PhaseGeometryError, match="PHASE_NODE_BINDING_DRIFT"):
        evaluate_phase_geometric_candidate(plan, package)


def test_pareto_frontier_preserves_constraint_and_phase_as_typed_axes() -> None:
    plan = _plan()
    phase_only = _package(plan, "phase-only", (2, 0, 0, 0))
    constraint_only = _package(plan, "constraint-only", constraint_mismatch_lane=0)
    both = _package(plan, "both", (2, 0, 0, 0), constraint_mismatch_lane=0)
    result = learn_phase_geometric_frontier(plan, [both, constraint_only, phase_only], learning_depth=2)
    assert result["cross_domain_scalar_loss_forbidden"] is True
    assert result["pareto_frontier_candidate_ids"] == ["constraint-only", "phase-only"]
    assert result["zero_disequilibrium_candidate_ids"] == []


def test_zero_phase_geometric_frontier_routes_only_to_existing_vm81_authority() -> None:
    plan = _plan()
    package = _package(plan, "zero")
    first = learn_phase_geometric_frontier(plan, [package], learning_depth=3)
    second = learn_phase_geometric_frontier(plan, [package], learning_depth=3)
    assert first == second
    assert first["decision"] == "ZERO_PHASE_GEOMETRIC_FRONTIER_READY_FOR_VM81_ADMISSION"
    assert first["zero_disequilibrium_candidate_ids"] == ["zero"]
    assert first["canonical_vm81_mutation_authority"] is False


def test_float_phase_input_is_forbidden() -> None:
    value = _string("float", "root")
    value["phase_steps"]["x"] = 1.0
    with pytest.raises(PhaseGeometryError, match="FLOAT_CANONICAL_AUTHORITY_FORBIDDEN"):
        evaluate_octonion_string(value, expected_parent_circuit_id="root")

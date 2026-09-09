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
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _plan() -> dict[str, object]:
    rows = []
    for index, lane in enumerate(LANES):
        rows.append(
            {
                "lane": lane,
                "provider_decision": "PROPAGATE",
                "i153_survives": True,
                "authority_packet_sha256": f"{index + 1:064x}",
                "transition_hash216": chr(65 + index) * 216,
                "proof_hash216": chr(69 + index) * 216,
                "receipt_hash72": chr(73 + index) * 72,
                "replay_hash72": chr(77 + index) * 72,
            }
        )
    plan: dict[str, object] = {
        "schema": PLAN_SCHEMA,
        "pass": 219,
        "iteration": "I154",
        "classification": "TEST_ONLY_FOUR_LANE_PLUMBING_WITHIN_81_OVER_7",
        "lanes": list(LANES),
        "workloads": rows,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "result": "PASS",
    }
    plan["receipt_sha256"] = _sha(plan)
    return plan


def _edge(*, edge_id: str, offset: int, mismatch: bool = False) -> dict[str, object]:
    return {
        "schema": EDGE_SCHEMA,
        "edge_id": edge_id,
        "operator": "==" if offset % 2 else "=",
        "source_offset": offset,
        "nesting_path": [0, offset + 1],
        "lhs_node_id": f"{edge_id}:lhs",
        "rhs_node_id": f"{edge_id}:rhs",
        "lhs_source_sha256": _sha({"edge": edge_id, "side": "lhs"}),
        "rhs_source_sha256": _sha({"edge": edge_id, "side": "rhs"}),
        "parenthesization_sha256": _sha({"edge": edge_id, "kind": "paren"}),
        "ordered_operands_sha256": _sha({"edge": edge_id, "kind": "order"}),
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


def _phase_nodes(prefix: str) -> dict[str, str]:
    return {channel: f"{prefix}:{channel}" for channel in PHASE_CHANNELS}


def _candidate(
    plan: dict[str, object],
    *,
    candidate_id: str,
    constraint_mismatch_lane: int | None = None,
) -> dict[str, object]:
    rows = {row["lane"]: row for row in plan["workloads"]}
    root = _sha({"candidate": candidate_id})
    lane_witnesses = []
    for index, lane in enumerate(LANES):
        row = rows[lane]
        lane_witnesses.append(
            {
                "lane": lane,
                "authority_packet_sha256": row["authority_packet_sha256"],
                "parent_transition_hash216": row["transition_hash216"],
                "candidate_transition_hash216": chr(81 + index) * 216,
                "candidate_receipt_hash72": chr(85 + index) * 72,
                "candidate_manifold_root_sha256": root,
                "ordered_phase_node_ids": _phase_nodes(lane),
                "equality_edges": [
                    _edge(
                        edge_id=f"{lane}:edge0",
                        offset=index * 10,
                        mismatch=(constraint_mismatch_lane == index),
                    ),
                    _edge(
                        edge_id=f"{lane}:edge1",
                        offset=index * 10 + 1,
                    ),
                ],
            }
        )
    return {
        "schema": CANDIDATE_SCHEMA,
        "candidate_id": candidate_id,
        "plan_receipt_sha256": plan["receipt_sha256"],
        "candidate_manifold_root_sha256": root,
        "variable_nodes": [
            {"symbol": "A", "node_id": "var:A", "state_token": "P2"},
            {"symbol": "B", "node_id": "var:B", "state_token": "P2"},
            {"symbol": "P", "node_id": "var:P", "state_token": "P"},
            {"symbol": "p", "node_id": "var:p", "state_token": "p"},
            {"symbol": "q", "node_id": "var:q", "state_token": "q"},
            {"symbol": "x", "node_id": "var:x", "state_token": "x"},
            {"symbol": "y", "node_id": "var:y", "state_token": "y"},
            {"symbol": "z", "node_id": "var:z", "state_token": "z"},
            {"symbol": "w", "node_id": "var:w", "state_token": "w"},
            {"symbol": "xy", "node_id": "var:xy", "state_token": "xy"},
            {"symbol": "yx", "node_id": "var:yx", "state_token": "yx"},
            {"symbol": "zw", "node_id": "var:zw", "state_token": "zw"},
            {"symbol": "wz", "node_id": "var:wz", "state_token": "wz"},
        ],
        "lane_witnesses": lane_witnesses,
    }


def _string(
    *,
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


def _root_circuit(
    *,
    circuit_id: str,
    steps: tuple[int, int, int, int] = (0, 0, 0, 0),
) -> dict[str, object]:
    return {
        "schema": PHASE_CIRCUIT_SCHEMA,
        "circuit_id": circuit_id,
        "parent_circuit_id": None,
        "children": [
            _string(string_id=f"{circuit_id}:leaf", parent=circuit_id, steps=steps)
        ],
    }


def _geometry(candidate: dict[str, object], circuit: dict[str, object]) -> dict[str, object]:
    circuit_eval = evaluate_phase_circuit(circuit)
    return {
        "schema": GEOMETRY_WITNESS_SCHEMA,
        "candidate_manifold_root_sha256": candidate["candidate_manifold_root_sha256"],
        "root_circuit": circuit,
        "lane_bindings": [
            {
                "lane": lane["lane"],
                "candidate_transition_hash216": lane["candidate_transition_hash216"],
                "ordered_phase_node_ids": lane["ordered_phase_node_ids"],
                "phase_circuit_root_sha256": circuit_eval["circuit_root_sha256"],
            }
            for lane in candidate["lane_witnesses"]
        ],
    }


def _package(
    plan: dict[str, object],
    *,
    candidate_id: str,
    steps: tuple[int, int, int, int] = (0, 0, 0, 0),
    constraint_mismatch_lane: int | None = None,
) -> dict[str, object]:
    candidate = _candidate(
        plan,
        candidate_id=candidate_id,
        constraint_mismatch_lane=constraint_mismatch_lane,
    )
    circuit = _root_circuit(circuit_id=f"circuit:{candidate_id}", steps=steps)
    return {
        "schema": PHASE_CANDIDATE_SCHEMA,
        "candidate": candidate,
        "phase_geometry": _geometry(candidate, circuit),
    }


def test_canonical_two_plane_rotor_orientation_is_exact() -> None:
    geometry = canonical_phase_geometry()
    rotors = geometry["rotors"]
    assert rotors["x"] == {"plane": "PRIMARY_XZ", "direction": "CW", "signed_orientation": 1}
    assert rotors["z"] == {"plane": "PRIMARY_XZ", "direction": "CCW", "signed_orientation": -1}
    assert rotors["y"] == {"plane": "ORTHOGONAL_YW", "direction": "CCW", "signed_orientation": -1}
    assert rotors["w"] == {"plane": "ORTHOGONAL_YW", "direction": "CW", "signed_orientation": 1}
    assert geometry["quarter_cycle"] == 18
    assert geometry["half_cycle"] == 36
    assert geometry["full_cycle"] == 72
    assert geometry["typed_u0_is_scalar_zero"] is False


def test_typed_u0_is_legal_phase_position_and_closes() -> None:
    value = _string(string_id="u0", parent="root", steps=(0, 0, 0, 0))
    result = evaluate_octonion_string(value, expected_parent_circuit_id="root")
    assert result["phase_positions"] == {"x": "u^0", "y": "u^0", "z": "u^0", "w": "u^0"}
    assert result["phase_closed"] is True
    assert result["typed_u0_is_scalar_zero"] is False


def test_u36_half_cycle_is_preserved_for_all_four_rotors() -> None:
    value = _string(
        string_id="half",
        parent="root",
        steps=(HALF_CYCLE, HALF_CYCLE, HALF_CYCLE, HALF_CYCLE),
    )
    result = evaluate_octonion_string(value, expected_parent_circuit_id="root")
    assert result["phase_closed"] is True
    assert result["half_cycle_rotors"] == ["x", "y", "z", "w"]


def test_phase_pair_mismatch_produces_typed_disequilibrium() -> None:
    value = _string(string_id="mismatch", parent="root", steps=(5, 7, 3, 7))
    result = evaluate_octonion_string(value, expected_parent_circuit_id="root")
    assert result["primary_pair_disequilibrium_units"] == 2
    assert result["orthogonal_pair_disequilibrium_units"] == 0
    assert result["net_signed_phase_disequilibrium_units"] == 2
    assert result["phase_closed"] is False


def test_fold_order_and_parenthesization_are_semantic_identity() -> None:
    ordered = evaluate_octonion_string(
        _string(string_id="ordered", parent="root", fold_tree=[["x", "y"], ["z", "w"]]),
        expected_parent_circuit_id="root",
    )
    reordered = evaluate_octonion_string(
        _string(string_id="reordered", parent="root", fold_tree=[["y", "x"], ["z", "w"]]),
        expected_parent_circuit_id="root",
    )
    left_assoc = evaluate_octonion_string(
        _string(string_id="left", parent="root", fold_tree=[[ ["x", "y"], "z"], "w"]),
        expected_parent_circuit_id="root",
    )
    right_assoc = evaluate_octonion_string(
        _string(string_id="right", parent="root", fold_tree=["x", ["y", ["z", "w"]]]),
        expected_parent_circuit_id="root",
    )
    assert ordered["fold_word_sha256"] != reordered["fold_word_sha256"]
    assert left_assoc["fold_word"] == right_assoc["fold_word"] == ["x", "y", "z", "w"]
    assert left_assoc["parenthesization_sha256"] != right_assoc["parenthesization_sha256"]


def test_nested_circuit_entanglement_preserves_child_order() -> None:
    a = _string(string_id="a", parent="root")
    b = _string(string_id="b", parent="root")
    first = {
        "schema": PHASE_CIRCUIT_SCHEMA,
        "circuit_id": "root",
        "parent_circuit_id": None,
        "children": [a, b],
    }
    second = {
        "schema": PHASE_CIRCUIT_SCHEMA,
        "circuit_id": "root",
        "parent_circuit_id": None,
        "children": [b, a],
    }
    first_eval = evaluate_phase_circuit(first)
    second_eval = evaluate_phase_circuit(second)
    assert first_eval["ordered_child_ids"] == ["a", "b"]
    assert second_eval["ordered_child_ids"] == ["b", "a"]
    assert first_eval["circuit_root_sha256"] != second_eval["circuit_root_sha256"]


def test_nested_circuit_can_contain_another_entangled_circuit() -> None:
    inner = {
        "schema": PHASE_CIRCUIT_SCHEMA,
        "circuit_id": "inner",
        "parent_circuit_id": "outer",
        "children": [_string(string_id="inner:leaf", parent="inner", steps=(18, 18, 18, 18))],
    }
    outer = {
        "schema": PHASE_CIRCUIT_SCHEMA,
        "circuit_id": "outer",
        "parent_circuit_id": None,
        "children": [inner, _string(string_id="outer:leaf", parent="outer")],
    }
    result = evaluate_phase_circuit(outer)
    assert result["leaf_string_count"] == 2
    assert result["nested_circuit_count"] == 1
    assert result["phase_closed"] is True


def test_phase_geometry_binds_to_all_four_rml_lanes_without_new_authority() -> None:
    plan = _plan()
    package = _package(plan, candidate_id="zero")
    result = evaluate_phase_geometric_candidate(plan, package)
    assert result["typed_disequilibrium_vector"] == {
        "constraint_units": 0,
        "primary_pair_units": 0,
        "orthogonal_pair_units": 0,
        "net_signed_phase_units": 0,
        "nonclosed_leaf_count": 0,
    }
    assert result["zero_disequilibrium"] is True
    assert result["nested_octonion_circuits_enabled"] is True
    assert result["canonical_vm81_mutation_authority"] is False
    assert result["canonical_hash72_mint_authority"] is False
    assert result["canonical_hash216_persistence_authority"] is False


def test_phase_lane_binding_drift_fails_closed() -> None:
    plan = _plan()
    package = _package(plan, candidate_id="drift")
    package["phase_geometry"]["lane_bindings"][0]["ordered_phase_node_ids"]["xy"] = "wrong:xy"
    with pytest.raises(PhaseGeometryError, match="PHASE_NODE_BINDING_DRIFT"):
        evaluate_phase_geometric_candidate(plan, package)


def test_pareto_frontier_does_not_scalarize_constraint_and_phase_error() -> None:
    plan = _plan()
    phase_only = _package(plan, candidate_id="phase-only", steps=(2, 0, 0, 0))
    constraint_only = _package(
        plan,
        candidate_id="constraint-only",
        constraint_mismatch_lane=0,
    )
    both = _package(
        plan,
        candidate_id="both",
        steps=(2, 0, 0, 0),
        constraint_mismatch_lane=0,
    )
    result = learn_phase_geometric_frontier(
        plan,
        [both, constraint_only, phase_only],
        learning_depth=2,
    )
    assert result["cross_domain_scalar_loss_forbidden"] is True
    assert result["frontier_rule"] == "PARETO_NONDOMINATED_TYPED_DISEQUILIBRIUM"
    assert result["pareto_frontier_candidate_ids"] == ["constraint-only", "phase-only"]
    assert result["zero_disequilibrium_candidate_ids"] == []
    assert result["decision"] == "CONTINUE_RECURSIVE_PHASE_GEOMETRIC_SEARCH_FROM_PARETO_FRONTIER"


def test_zero_phase_geometric_frontier_is_ready_for_existing_vm81_admission() -> None:
    plan = _plan()
    zero = _package(plan, candidate_id="zero")
    first = learn_phase_geometric_frontier(plan, [zero], learning_depth=3)
    second = learn_phase_geometric_frontier(plan, [zero], learning_depth=3)
    assert first == second
    assert first["zero_disequilibrium_candidate_ids"] == ["zero"]
    assert first["decision"] == "ZERO_PHASE_GEOMETRIC_FRONTIER_READY_FOR_VM81_ADMISSION"
    assert first["canonical_vm81_mutation_authority"] is False


def test_float_phase_input_is_forbidden() -> None:
    value = _string(string_id="float", parent="root")
    value["phase_steps"]["x"] = 1.0
    with pytest.raises(PhaseGeometryError, match="FLOAT_CANONICAL_AUTHORITY_FORBIDDEN"):
        evaluate_octonion_string(value, expected_parent_circuit_id="root")

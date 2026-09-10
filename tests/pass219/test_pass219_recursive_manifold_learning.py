from __future__ import annotations

import hashlib
import json

import pytest

from hhs_runtime.pass219.recursive_manifold_learning import (
    CANDIDATE_SCHEMA,
    EDGE_SCHEMA,
    LANES,
    PLAN_SCHEMA,
    RecursiveManifoldLearningError,
    evaluate_candidate,
    learn_recursive_frontier,
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


def _edge(*, edge_id: str, offset: int, state: str = "P2", mismatch: bool = False) -> dict[str, object]:
    other = "OTHER" if mismatch else state
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
        "A_state": other,
        "P2_state": state,
        "B_state": state,
        "sqrt_AB_state": state,
        "sqrt_BA_state": state,
        "pq_plus_one_state": state,
    }


def _candidate(plan: dict[str, object], *, candidate_id: str, mismatch_lane: int | None = None) -> dict[str, object]:
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
                "ordered_phase_node_ids": {
                    "x": f"{lane}:x",
                    "y": f"{lane}:y",
                    "z": f"{lane}:z",
                    "w": f"{lane}:w",
                    "xy": f"{lane}:xy",
                    "yx": f"{lane}:yx",
                    "zw": f"{lane}:zw",
                    "wz": f"{lane}:wz",
                },
                "equality_edges": [
                    _edge(
                        edge_id=f"{lane}:edge0",
                        offset=index * 10,
                        mismatch=(mismatch_lane == index),
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


def test_zero_disequilibrium_candidate_is_vm81_admission_frontier() -> None:
    plan = _plan()
    candidate = _candidate(plan, candidate_id="zero")
    evaluated = evaluate_candidate(plan, candidate)
    assert evaluated["constraint_disequilibrium_units"] == 0
    assert evaluated["zero_disequilibrium"] is True
    assert evaluated["node_identity_preserved_under_equal_state"] is True
    assert evaluated["scalar_projection_is_substitution_authority"] is False

    learned = learn_recursive_frontier(
        plan,
        [candidate],
        learning_depth=0,
    )
    assert learned["minimum_constraint_disequilibrium_units"] == 0
    assert learned["minimum_frontier_candidate_ids"] == ["zero"]
    assert learned["zero_disequilibrium_candidate_ids"] == ["zero"]
    assert learned["decision"] == "ZERO_DISEQUILIBRIUM_FRONTIER_READY_FOR_VM81_ADMISSION"
    assert learned["canonical_vm81_mutation_authority"] is False
    assert learned["canonical_hash72_mint_authority"] is False
    assert learned["canonical_hash216_persistence_authority"] is False


def test_nonzero_candidate_recurses_from_minimum_frontier() -> None:
    plan = _plan()
    worse = _candidate(plan, candidate_id="worse", mismatch_lane=2)
    better = _candidate(plan, candidate_id="better", mismatch_lane=1)
    worse["lane_witnesses"][2]["equality_edges"][0]["B_state"] = "OTHER2"

    learned = learn_recursive_frontier(
        plan,
        [worse, better],
        learning_depth=7,
        parent_learning_receipt_sha256="a" * 64,
    )
    assert learned["minimum_constraint_disequilibrium_units"] == 1
    assert learned["minimum_frontier_candidate_ids"] == ["better"]
    assert learned["zero_disequilibrium_candidate_ids"] == []
    assert learned["decision"] == "CONTINUE_RECURSIVE_SEARCH_FROM_MINIMUM_DISEQUILIBRIUM_FRONTIER"
    assert learned["learning_depth"] == 7
    assert learned["parent_learning_receipt_sha256"] == "a" * 64


def test_equal_state_does_not_collapse_lhs_rhs_node_identity() -> None:
    plan = _plan()
    candidate = _candidate(plan, candidate_id="identity")
    edge = candidate["lane_witnesses"][0]["equality_edges"][0]
    edge["rhs_node_id"] = edge["lhs_node_id"]
    with pytest.raises(RecursiveManifoldLearningError, match="LHS_RHS_NODE_ID_COLLAPSE"):
        evaluate_candidate(plan, candidate)


def test_scalar_projection_cannot_be_promoted_to_substitution_authority() -> None:
    plan = _plan()
    candidate = _candidate(plan, candidate_id="projection")
    candidate["lane_witnesses"][0]["equality_edges"][0][
        "scalar_projection_substitution_authority"
    ] = True
    with pytest.raises(
        RecursiveManifoldLearningError,
        match="SCALAR_PROJECTION_SUBSTITUTION_FORBIDDEN",
    ):
        evaluate_candidate(plan, candidate)


def test_noncommutative_directional_channels_cannot_collapse() -> None:
    plan = _plan()
    candidate = _candidate(plan, candidate_id="phase")
    phase = candidate["lane_witnesses"][0]["ordered_phase_node_ids"]
    phase["yx"] = phase["xy"]
    with pytest.raises(
        RecursiveManifoldLearningError,
        match="DIRECTIONAL_PHASE_NODE_ID_COLLAPSE",
    ):
        evaluate_candidate(plan, candidate)


def test_reassociation_and_commutative_reorder_fail_closed() -> None:
    plan = _plan()
    reassociate = _candidate(plan, candidate_id="assoc")
    reassociate["lane_witnesses"][0]["equality_edges"][0][
        "nonassociative_rewrite_permitted"
    ] = True
    with pytest.raises(RecursiveManifoldLearningError, match="REASSOCIATION_FORBIDDEN"):
        evaluate_candidate(plan, reassociate)

    reorder = _candidate(plan, candidate_id="order")
    reorder["lane_witnesses"][0]["equality_edges"][0][
        "commutative_reorder_permitted"
    ] = True
    with pytest.raises(RecursiveManifoldLearningError, match="COMMUTATIVE_REORDER_FORBIDDEN"):
        evaluate_candidate(plan, reorder)


def test_all_four_authorized_parent_lanes_are_required() -> None:
    plan = _plan()
    candidate = _candidate(plan, candidate_id="lanes")
    candidate["lane_witnesses"].pop()
    with pytest.raises(
        RecursiveManifoldLearningError,
        match="EXACTLY_FOUR_LANE_WITNESSES_REQUIRED",
    ):
        evaluate_candidate(plan, candidate)


def test_rejected_i154_parent_lane_cannot_feed_learning() -> None:
    plan = _plan()
    plan["workloads"][1]["provider_decision"] = "REJECT"
    plan["workloads"][1]["i153_survives"] = False
    plan.pop("receipt_sha256")
    plan["receipt_sha256"] = _sha(plan)
    candidate = _candidate(plan, candidate_id="rejected")
    with pytest.raises(
        RecursiveManifoldLearningError,
        match="PARENT_LANE_NOT_AUTHORIZED_TO_PROPAGATE",
    ):
        evaluate_candidate(plan, candidate)


def test_float_input_is_forbidden() -> None:
    plan = _plan()
    candidate = _candidate(plan, candidate_id="float")
    candidate["variable_nodes"][0]["state_token"] = 1.0
    with pytest.raises(
        RecursiveManifoldLearningError,
        match="FLOAT_CANONICAL_AUTHORITY_FORBIDDEN",
    ):
        evaluate_candidate(plan, candidate)


def test_learning_receipt_is_deterministic() -> None:
    plan = _plan()
    a = _candidate(plan, candidate_id="a")
    b = _candidate(plan, candidate_id="b", mismatch_lane=0)
    first = learn_recursive_frontier(plan, [b, a], learning_depth=3)
    second = learn_recursive_frontier(plan, [a, b], learning_depth=3)
    assert first["receipt_sha256"] == second["receipt_sha256"]
    assert first == second

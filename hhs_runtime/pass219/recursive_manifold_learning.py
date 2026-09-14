"""Pass 219 recursive constraint-manifold learning over authorized four-lane hydration.

This layer consumes an already-produced I154 four-lane planner receipt and ranks
candidate successor manifolds by exact constraint disequilibrium.  It does not
scalarize the canonical equation source, reorder operands, reassociate syntax,
mint Hash72/Hash216 authority, or mutate VM81.

Each ``=``/``==`` occurrence is represented as one preserved constraint edge:
A := LHS, B := RHS.  The admitted edge state is A = P^2 = B while the node
identities remain distinct.  The user-declared closure correspondence
P^2 = sqrt(AB) = sqrt(BA) = pq + 1 is tracked as state correspondence only;
it is never promoted to substitution authority.
"""
from __future__ import annotations

import hashlib
import json
import string
from typing import Any, Iterable, Mapping

PASS = 219
ITERATION = "RML1"
SCHEMA = "HHS_PASS219_RECURSIVE_MANIFOLD_LEARNING_RECEIPT_V1"
CANDIDATE_SCHEMA = "HHS_PASS219_RECURSIVE_MANIFOLD_LEARNING_CANDIDATE_V1"
EDGE_SCHEMA = "HHS_PASS219_RECURSIVE_EQUALITY_EDGE_V1"
PLAN_SCHEMA = "HHS_PASS219_I154_AUTHORIZED_FOUR_LANE_EXHAUSTION_PLAN_V1"

LANES = (
    "RAW5184_X86_64",
    "VM81_HASH72_HASH216",
    "OCTONION_DUAL_STEREO_TERNARY",
    "HARMONIC36_144X36",
)
PHASE_CHANNELS = ("x", "y", "z", "w", "xy", "yx", "zw", "wz")
OPERATORS = frozenset({"=", "=="})
HEX = frozenset(string.hexdigits)


class RecursiveManifoldLearningError(RuntimeError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise RecursiveManifoldLearningError(f"FLOAT_CANONICAL_AUTHORITY_FORBIDDEN:{path}")
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


def _hex64(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(ch not in HEX for ch in value):
        raise RecursiveManifoldLearningError(f"{label}_SHA256_REQUIRED")
    lowered = value.lower()
    if lowered == "0" * 64:
        raise RecursiveManifoldLearningError(f"{label}_ZERO_FORBIDDEN")
    return lowered


def _identity(value: Any, length: int, label: str) -> str:
    if not isinstance(value, str) or len(value) != length:
        raise RecursiveManifoldLearningError(f"{label}_LENGTH_{length}_REQUIRED")
    if any(ord(ch) < 33 or ord(ch) > 126 for ch in value):
        raise RecursiveManifoldLearningError(f"{label}_PRINTABLE_ASCII_REQUIRED")
    return value


def _nonempty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise RecursiveManifoldLearningError(f"{label}_NONEMPTY_STRING_REQUIRED")
    return value


def _exact_int(value: Any, label: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RecursiveManifoldLearningError(f"{label}_EXACT_INTEGER_REQUIRED")
    if minimum is not None and value < minimum:
        raise RecursiveManifoldLearningError(f"{label}_OUT_OF_RANGE")
    return value


def _flag(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise RecursiveManifoldLearningError(f"{label}_BOOLEAN_REQUIRED")
    return value


def _validate_plan(plan: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    _reject_float(plan)
    if plan.get("schema") != PLAN_SCHEMA or plan.get("pass") != PASS:
        raise RecursiveManifoldLearningError("I154_PLAN_SCHEMA_MISMATCH")
    if plan.get("result") != "PASS":
        raise RecursiveManifoldLearningError("I154_PLAN_PASS_REQUIRED")
    if tuple(plan.get("lanes", ())) != LANES:
        raise RecursiveManifoldLearningError("I154_FOUR_LANE_TOPOLOGY_DRIFT")
    if plan.get("canonical_vm81_mutation_authority") is not False:
        raise RecursiveManifoldLearningError("I154_SECOND_VM81_AUTHORITY_FORBIDDEN")
    if plan.get("canonical_hash72_mint_authority") is not False:
        raise RecursiveManifoldLearningError("I154_HASH72_MINT_AUTHORITY_FORBIDDEN")
    if plan.get("canonical_hash216_persistence_authority") is not False:
        raise RecursiveManifoldLearningError("I154_HASH216_PERSISTENCE_AUTHORITY_FORBIDDEN")

    receipt = _hex64(plan.get("receipt_sha256"), "I154_PLAN_RECEIPT")
    unsigned = dict(plan)
    unsigned.pop("receipt_sha256", None)
    if _sha256(unsigned) != receipt:
        raise RecursiveManifoldLearningError("I154_PLAN_RECEIPT_DRIFT")

    rows = plan.get("workloads")
    if not isinstance(rows, list) or len(rows) != len(LANES):
        raise RecursiveManifoldLearningError("I154_EXACTLY_FOUR_WORKLOADS_REQUIRED")
    by_lane: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise RecursiveManifoldLearningError("I154_WORKLOAD_MAPPING_REQUIRED")
        lane = row.get("lane")
        if lane not in LANES or lane in by_lane:
            raise RecursiveManifoldLearningError("I154_WORKLOAD_LANE_DRIFT")
        if row.get("provider_decision") != "PROPAGATE" or row.get("i153_survives") is not True:
            raise RecursiveManifoldLearningError(f"I154_PARENT_LANE_NOT_AUTHORIZED_TO_PROPAGATE:{lane}")
        _hex64(row.get("authority_packet_sha256"), f"{lane}_AUTHORITY_PACKET")
        _identity(row.get("transition_hash216"), 216, f"{lane}_PARENT_TRANSITION_HASH216")
        _identity(row.get("proof_hash216"), 216, f"{lane}_PROOF_HASH216")
        _identity(row.get("receipt_hash72"), 72, f"{lane}_RECEIPT_HASH72")
        _identity(row.get("replay_hash72"), 72, f"{lane}_REPLAY_HASH72")
        by_lane[str(lane)] = row
    if set(by_lane) != set(LANES):
        raise RecursiveManifoldLearningError("I154_ALL_FOUR_LANES_REQUIRED")
    return by_lane


def _validate_variable_nodes(candidate: Mapping[str, Any]) -> list[dict[str, str]]:
    rows = candidate.get("variable_nodes")
    if not isinstance(rows, list) or not rows:
        raise RecursiveManifoldLearningError("VARIABLE_NODE_TABLE_REQUIRED")
    normalized: list[dict[str, str]] = []
    symbols: set[str] = set()
    node_ids: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping):
            raise RecursiveManifoldLearningError("VARIABLE_NODE_MAPPING_REQUIRED")
        symbol = _nonempty(row.get("symbol"), "VARIABLE_SYMBOL")
        node_id = _nonempty(row.get("node_id"), "VARIABLE_NODE_ID")
        state = _nonempty(row.get("state_token"), "VARIABLE_STATE_TOKEN")
        if state == "0":
            raise RecursiveManifoldLearningError(f"VARIABLE_ZERO_STATE_FORBIDDEN:{symbol}")
        if symbol in symbols:
            raise RecursiveManifoldLearningError(f"DUPLICATE_VARIABLE_SYMBOL:{symbol}")
        if node_id in node_ids:
            raise RecursiveManifoldLearningError(f"DUPLICATE_VARIABLE_NODE_ID:{node_id}")
        symbols.add(symbol)
        node_ids.add(node_id)
        normalized.append({"symbol": symbol, "node_id": node_id, "state_token": state})
    return normalized


def _validate_phase_nodes(lane: Mapping[str, Any], lane_name: str) -> dict[str, str]:
    phase = lane.get("ordered_phase_node_ids")
    if not isinstance(phase, Mapping) or tuple(phase.keys()) != PHASE_CHANNELS:
        raise RecursiveManifoldLearningError(f"{lane_name}_ORDERED_PHASE_CHANNELS_REQUIRED")
    normalized = {
        channel: _nonempty(phase.get(channel), f"{lane_name}_{channel}_NODE_ID")
        for channel in PHASE_CHANNELS
    }
    if len(set(normalized.values())) != len(PHASE_CHANNELS):
        raise RecursiveManifoldLearningError(f"{lane_name}_DIRECTIONAL_PHASE_NODE_ID_COLLAPSE")
    return normalized


def _evaluate_edge(edge: Mapping[str, Any], *, lane_name: str) -> dict[str, Any]:
    if edge.get("schema") != EDGE_SCHEMA:
        raise RecursiveManifoldLearningError(f"{lane_name}_EDGE_SCHEMA_MISMATCH")
    edge_id = _nonempty(edge.get("edge_id"), f"{lane_name}_EDGE_ID")
    operator = edge.get("operator")
    if operator not in OPERATORS:
        raise RecursiveManifoldLearningError(f"{lane_name}_{edge_id}_OPERATOR_UNSUPPORTED")

    source_offset = _exact_int(
        edge.get("source_offset"),
        f"{lane_name}_{edge_id}_SOURCE_OFFSET",
        minimum=0,
    )
    nesting_path = edge.get("nesting_path")
    if not isinstance(nesting_path, list):
        raise RecursiveManifoldLearningError(f"{lane_name}_{edge_id}_NESTING_PATH_REQUIRED")
    normalized_path = [
        _exact_int(value, f"{lane_name}_{edge_id}_NESTING_PATH", minimum=0)
        for value in nesting_path
    ]

    lhs_node_id = _nonempty(edge.get("lhs_node_id"), f"{lane_name}_{edge_id}_LHS_NODE_ID")
    rhs_node_id = _nonempty(edge.get("rhs_node_id"), f"{lane_name}_{edge_id}_RHS_NODE_ID")
    if lhs_node_id == rhs_node_id:
        raise RecursiveManifoldLearningError(f"{lane_name}_{edge_id}_LHS_RHS_NODE_ID_COLLAPSE")

    syntax = {
        "lhs_source_sha256": _hex64(
            edge.get("lhs_source_sha256"), f"{lane_name}_{edge_id}_LHS_SOURCE"
        ),
        "rhs_source_sha256": _hex64(
            edge.get("rhs_source_sha256"), f"{lane_name}_{edge_id}_RHS_SOURCE"
        ),
        "parenthesization_sha256": _hex64(
            edge.get("parenthesization_sha256"),
            f"{lane_name}_{edge_id}_PARENTHESIZATION",
        ),
        "ordered_operands_sha256": _hex64(
            edge.get("ordered_operands_sha256"),
            f"{lane_name}_{edge_id}_ORDERED_OPERANDS",
        ),
    }

    if _flag(
        edge.get("commutative_reorder_permitted"),
        f"{lane_name}_{edge_id}_COMMUTATIVE_REORDER_PERMITTED",
    ):
        raise RecursiveManifoldLearningError(f"{lane_name}_{edge_id}_COMMUTATIVE_REORDER_FORBIDDEN")
    if _flag(
        edge.get("nonassociative_rewrite_permitted"),
        f"{lane_name}_{edge_id}_NONASSOCIATIVE_REWRITE_PERMITTED",
    ):
        raise RecursiveManifoldLearningError(f"{lane_name}_{edge_id}_REASSOCIATION_FORBIDDEN")
    if _flag(
        edge.get("scalar_projection_substitution_authority"),
        f"{lane_name}_{edge_id}_SCALAR_PROJECTION_SUBSTITUTION_AUTHORITY",
    ):
        raise RecursiveManifoldLearningError(
            f"{lane_name}_{edge_id}_SCALAR_PROJECTION_SUBSTITUTION_FORBIDDEN"
        )

    states = {
        "A": _nonempty(edge.get("A_state"), f"{lane_name}_{edge_id}_A_STATE"),
        "P2": _nonempty(edge.get("P2_state"), f"{lane_name}_{edge_id}_P2_STATE"),
        "B": _nonempty(edge.get("B_state"), f"{lane_name}_{edge_id}_B_STATE"),
        "sqrt_AB": _nonempty(
            edge.get("sqrt_AB_state"), f"{lane_name}_{edge_id}_SQRT_AB_STATE"
        ),
        "sqrt_BA": _nonempty(
            edge.get("sqrt_BA_state"), f"{lane_name}_{edge_id}_SQRT_BA_STATE"
        ),
        "pq_plus_one": _nonempty(
            edge.get("pq_plus_one_state"), f"{lane_name}_{edge_id}_PQ_PLUS_ONE_STATE"
        ),
    }
    if any(value == "0" for value in states.values()):
        raise RecursiveManifoldLearningError(f"{lane_name}_{edge_id}_ZERO_STATE_FORBIDDEN")

    p2 = states["P2"]
    correspondences = {
        "A_eq_P2": states["A"] == p2,
        "B_eq_P2": states["B"] == p2,
        "sqrt_AB_eq_P2": states["sqrt_AB"] == p2,
        "sqrt_BA_eq_P2": states["sqrt_BA"] == p2,
        "pq_plus_one_eq_P2": states["pq_plus_one"] == p2,
    }
    disequilibrium = sum(0 if satisfied else 1 for satisfied in correspondences.values())
    return {
        "edge_id": edge_id,
        "operator": operator,
        "source_offset": source_offset,
        "nesting_path": normalized_path,
        "lhs_node_id": lhs_node_id,
        "rhs_node_id": rhs_node_id,
        "syntax_identity": syntax,
        "state_correspondences": correspondences,
        "constraint_disequilibrium_units": disequilibrium,
        "admitted_A_eq_P2_eq_B": correspondences["A_eq_P2"] and correspondences["B_eq_P2"],
        "admitted_global_closure_correspondence": all(correspondences.values()),
        "node_identity_collapsed": False,
        "scalar_projection_substitution_authority": False,
        "commutative_reorder_permitted": False,
        "nonassociative_rewrite_permitted": False,
    }


def evaluate_candidate(
    plan: Mapping[str, Any],
    candidate: Mapping[str, Any],
) -> dict[str, Any]:
    """Evaluate one candidate without creating canonical runtime authority."""

    _reject_float(candidate)
    by_lane = _validate_plan(plan)
    if candidate.get("schema") != CANDIDATE_SCHEMA:
        raise RecursiveManifoldLearningError("CANDIDATE_SCHEMA_MISMATCH")

    candidate_id = _nonempty(candidate.get("candidate_id"), "CANDIDATE_ID")
    if _hex64(candidate.get("plan_receipt_sha256"), "CANDIDATE_PLAN_RECEIPT") != plan["receipt_sha256"]:
        raise RecursiveManifoldLearningError("CANDIDATE_PLAN_RECEIPT_BINDING_DRIFT")
    manifold_root = _hex64(
        candidate.get("candidate_manifold_root_sha256"),
        "CANDIDATE_MANIFOLD_ROOT",
    )
    variables = _validate_variable_nodes(candidate)

    lanes_raw = candidate.get("lane_witnesses")
    if not isinstance(lanes_raw, list) or len(lanes_raw) != len(LANES):
        raise RecursiveManifoldLearningError("CANDIDATE_EXACTLY_FOUR_LANE_WITNESSES_REQUIRED")
    lane_map: dict[str, Mapping[str, Any]] = {}
    for lane in lanes_raw:
        if not isinstance(lane, Mapping):
            raise RecursiveManifoldLearningError("CANDIDATE_LANE_WITNESS_MAPPING_REQUIRED")
        lane_name = lane.get("lane")
        if lane_name not in LANES or lane_name in lane_map:
            raise RecursiveManifoldLearningError("CANDIDATE_LANE_TOPOLOGY_DRIFT")
        lane_map[str(lane_name)] = lane
    if set(lane_map) != set(LANES):
        raise RecursiveManifoldLearningError("CANDIDATE_ALL_FOUR_LANES_REQUIRED")

    evaluated_lanes: list[dict[str, Any]] = []
    total_disequilibrium = 0
    for lane_name in LANES:
        lane = lane_map[lane_name]
        parent = by_lane[lane_name]
        if _hex64(
            lane.get("authority_packet_sha256"),
            f"{lane_name}_CANDIDATE_AUTHORITY_PACKET",
        ) != parent["authority_packet_sha256"]:
            raise RecursiveManifoldLearningError(f"{lane_name}_AUTHORITY_PACKET_BINDING_DRIFT")
        if _identity(
            lane.get("parent_transition_hash216"),
            216,
            f"{lane_name}_CANDIDATE_PARENT_TRANSITION_HASH216",
        ) != parent["transition_hash216"]:
            raise RecursiveManifoldLearningError(f"{lane_name}_PARENT_TRANSITION_BINDING_DRIFT")
        if _hex64(
            lane.get("candidate_manifold_root_sha256"),
            f"{lane_name}_CANDIDATE_MANIFOLD_ROOT",
        ) != manifold_root:
            raise RecursiveManifoldLearningError(f"{lane_name}_MANIFOLD_ROOT_BINDING_DRIFT")

        phase_nodes = _validate_phase_nodes(lane, lane_name)
        candidate_transition = _identity(
            lane.get("candidate_transition_hash216"),
            216,
            f"{lane_name}_CANDIDATE_TRANSITION_HASH216",
        )
        candidate_receipt = _identity(
            lane.get("candidate_receipt_hash72"),
            72,
            f"{lane_name}_CANDIDATE_RECEIPT_HASH72",
        )
        edges_raw = lane.get("equality_edges")
        if not isinstance(edges_raw, list) or not edges_raw:
            raise RecursiveManifoldLearningError(f"{lane_name}_EQUALITY_EDGE_SET_REQUIRED")

        evaluated_edges: list[dict[str, Any]] = []
        seen_edge_ids: set[str] = set()
        seen_locations: set[tuple[int, tuple[int, ...]]] = set()
        for edge in edges_raw:
            if not isinstance(edge, Mapping):
                raise RecursiveManifoldLearningError(f"{lane_name}_EDGE_MAPPING_REQUIRED")
            evaluated = _evaluate_edge(edge, lane_name=lane_name)
            edge_id = str(evaluated["edge_id"])
            location = (
                int(evaluated["source_offset"]),
                tuple(int(v) for v in evaluated["nesting_path"]),
            )
            if edge_id in seen_edge_ids:
                raise RecursiveManifoldLearningError(f"{lane_name}_DUPLICATE_EDGE_ID:{edge_id}")
            if location in seen_locations:
                raise RecursiveManifoldLearningError(
                    f"{lane_name}_DUPLICATE_EQUALITY_LOCATION:{location}"
                )
            seen_edge_ids.add(edge_id)
            seen_locations.add(location)
            evaluated_edges.append(evaluated)

        lane_disequilibrium = sum(
            int(edge["constraint_disequilibrium_units"])
            for edge in evaluated_edges
        )
        total_disequilibrium += lane_disequilibrium
        evaluated_lanes.append(
            {
                "lane": lane_name,
                "authority_packet_sha256": parent["authority_packet_sha256"],
                "parent_transition_hash216": parent["transition_hash216"],
                "candidate_transition_hash216": candidate_transition,
                "candidate_receipt_hash72": candidate_receipt,
                "candidate_manifold_root_sha256": manifold_root,
                "ordered_phase_node_ids": phase_nodes,
                "equality_edge_count": len(evaluated_edges),
                "constraint_disequilibrium_units": lane_disequilibrium,
                "zero_disequilibrium": lane_disequilibrium == 0,
                "equality_edges": evaluated_edges,
            }
        )

    result = {
        "schema": "HHS_PASS219_RECURSIVE_MANIFOLD_CANDIDATE_EVALUATION_V1",
        "pass": PASS,
        "iteration": ITERATION,
        "candidate_id": candidate_id,
        "candidate_manifold_root_sha256": manifold_root,
        "variable_nodes": variables,
        "lanes": evaluated_lanes,
        "constraint_disequilibrium_units": total_disequilibrium,
        "zero_disequilibrium": total_disequilibrium == 0,
        "admission_target": "A=P^2=B",
        "global_closure_correspondence": "P^2=sqrt(AB)=sqrt(BA)=pq+1",
        "scalar_projection_is_substitution_authority": False,
        "node_identity_preserved_under_equal_state": True,
        "noncommutative_order_preserved": True,
        "nonassociative_parenthesization_preserved": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    result["candidate_evaluation_sha256"] = _sha256(result)
    return result


def learn_recursive_frontier(
    plan: Mapping[str, Any],
    candidates: Iterable[Mapping[str, Any]],
    *,
    learning_depth: int,
    parent_learning_receipt_sha256: str | None = None,
) -> dict[str, Any]:
    """Rank authorized candidates by whole-manifold disequilibrium.

    The minimum frontier is returned rather than autonomously committing a
    winner.  A zero-disequilibrium frontier is eligible to proceed to the
    existing VM81 admission authority; a non-zero frontier is the recursive
    continuation set for the next learning step.
    """

    depth = _exact_int(learning_depth, "LEARNING_DEPTH", minimum=0)
    parent_receipt = (
        None
        if parent_learning_receipt_sha256 is None
        else _hex64(parent_learning_receipt_sha256, "PARENT_LEARNING_RECEIPT")
    )
    _validate_plan(plan)

    material = list(candidates)
    if not material:
        raise RecursiveManifoldLearningError("EMPTY_LEARNING_CANDIDATE_SET")

    evaluations = [evaluate_candidate(plan, candidate) for candidate in material]
    ids = [str(row["candidate_id"]) for row in evaluations]
    if len(ids) != len(set(ids)):
        raise RecursiveManifoldLearningError("DUPLICATE_LEARNING_CANDIDATE_ID")

    minimum = min(int(row["constraint_disequilibrium_units"]) for row in evaluations)
    frontier = sorted(
        str(row["candidate_id"])
        for row in evaluations
        if int(row["constraint_disequilibrium_units"]) == minimum
    )
    zero = sorted(
        str(row["candidate_id"])
        for row in evaluations
        if row["zero_disequilibrium"] is True
    )
    decision = (
        "ZERO_DISEQUILIBRIUM_FRONTIER_READY_FOR_VM81_ADMISSION"
        if zero
        else "CONTINUE_RECURSIVE_SEARCH_FROM_MINIMUM_DISEQUILIBRIUM_FRONTIER"
    )

    receipt = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "learning_depth": depth,
        "parent_learning_receipt_sha256": parent_receipt,
        "i154_plan_receipt_sha256": plan["receipt_sha256"],
        "candidate_count": len(evaluations),
        "constraint_disequilibrium_metric": (
            "COUNT_OF_UNSATISFIED_ADMITTED_STATE_CORRESPONDENCES_PER_PRESERVED_EQUALITY_EDGE"
        ),
        "minimum_constraint_disequilibrium_units": minimum,
        "minimum_frontier_candidate_ids": frontier,
        "zero_disequilibrium_candidate_ids": zero,
        "decision": decision,
        "candidate_evaluations": sorted(evaluations, key=lambda row: str(row["candidate_id"])),
        "learning_semantics": {
            "edge_constructor": "A:=LHS;B:=RHS",
            "admitted_truth_state": "A=P^2=B",
            "global_closure_correspondence": "P^2=sqrt(AB)=sqrt(BA)=pq+1",
            "equal_state_collapses_variable_identity": False,
            "scalar_projection_substitution_authority": False,
            "operand_reordering_authority": False,
            "reassociation_authority": False,
            "four_lane_views_are_one_entangled_manifold": True,
        },
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "result": "PASS",
    }
    receipt["receipt_sha256"] = _sha256(receipt)
    return receipt

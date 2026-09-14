"""Pass 219 RML2 two-plane octonion phase geometry and nested circuit learning.

This module binds the system-internal x/y/z/w rotor geometry to the RML1
constraint-manifold learner without scalarizing either domain.

Canonical rotor geometry:
    x : primary XZ plane, clockwise
    z : primary XZ plane, counterclockwise
    y : orthogonal YW plane, counterclockwise
    w : orthogonal YW plane, clockwise

Phase position is an oriented distance from u^0 on the 72-state cycle. The
integer residue 0 therefore denotes the typed phase position u^0; it is not
ordinary scalar zero. u^36 is the half-cycle inversion and u^72 closes to u^0.

Octonion strings preserve the eight directional channel identities
x,y,z,w,xy,yx,zw,wz, an explicit nonassociative fold tree, and exact phase
positions. Strings can be grouped recursively into ordered nested circuits.
Circuit order and parenthesization are semantic identity.

The layer is read-only with respect to canonical runtime authority: it does not
mutate VM81, mint Hash72, or persist Hash216.
"""
from __future__ import annotations

import hashlib
import json
import string
from typing import Any, Iterable, Mapping

from hhs_runtime.pass219.recursive_manifold_learning import (
    LANES,
    evaluate_candidate as evaluate_rml_candidate,
)

PASS = 219
ITERATION = "RML2_PHASE_GEOMETRY"

PHASE_MODULUS = 72
QUARTER_CYCLE = 18
HALF_CYCLE = 36
FULL_CYCLE = 72

PRIMARY_PLANE = "PRIMARY_XZ"
ORTHOGONAL_PLANE = "ORTHOGONAL_YW"
CW = "CW"
CCW = "CCW"

ROTOR_ORDER = ("x", "y", "z", "w")
PHASE_CHANNELS = ("x", "y", "z", "w", "xy", "yx", "zw", "wz")
ROTOR_GEOMETRY = {
    "x": {"plane": PRIMARY_PLANE, "direction": CW, "signed_orientation": 1},
    "y": {"plane": ORTHOGONAL_PLANE, "direction": CCW, "signed_orientation": -1},
    "z": {"plane": PRIMARY_PLANE, "direction": CCW, "signed_orientation": -1},
    "w": {"plane": ORTHOGONAL_PLANE, "direction": CW, "signed_orientation": 1},
}

OCTONION_STRING_SCHEMA = "HHS_PASS219_RML2_OCTONION_PHASE_STRING_V1"
PHASE_CIRCUIT_SCHEMA = "HHS_PASS219_RML2_NESTED_PHASE_CIRCUIT_V1"
GEOMETRY_WITNESS_SCHEMA = "HHS_PASS219_RML2_PHASE_GEOMETRY_WITNESS_V1"
PHASE_CANDIDATE_SCHEMA = "HHS_PASS219_RML2_PHASE_GEOMETRIC_CANDIDATE_V1"
EVALUATION_SCHEMA = "HHS_PASS219_RML2_PHASE_GEOMETRIC_EVALUATION_V1"
LEARNING_SCHEMA = "HHS_PASS219_RML2_PHASE_GEOMETRIC_LEARNING_RECEIPT_V1"

HEX = frozenset(string.hexdigits)
MAX_VALIDATION_NESTING_DEPTH = 81


class PhaseGeometryError(RuntimeError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise PhaseGeometryError(f"FLOAT_CANONICAL_AUTHORITY_FORBIDDEN:{path}")
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


def _nonempty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise PhaseGeometryError(f"{label}_NONEMPTY_STRING_REQUIRED")
    return value


def _hex64(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(ch not in HEX for ch in value):
        raise PhaseGeometryError(f"{label}_SHA256_REQUIRED")
    lowered = value.lower()
    if lowered == "0" * 64:
        raise PhaseGeometryError(f"{label}_ZERO_HASH_FORBIDDEN")
    return lowered


def _identity(value: Any, length: int, label: str) -> str:
    if not isinstance(value, str) or len(value) != length:
        raise PhaseGeometryError(f"{label}_LENGTH_{length}_REQUIRED")
    if any(ord(ch) < 33 or ord(ch) > 126 for ch in value):
        raise PhaseGeometryError(f"{label}_PRINTABLE_ASCII_REQUIRED")
    return value


def _exact_int(
    value: Any,
    label: str,
    *,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise PhaseGeometryError(f"{label}_EXACT_INTEGER_REQUIRED")
    if minimum is not None and value < minimum:
        raise PhaseGeometryError(f"{label}_OUT_OF_RANGE")
    if maximum is not None and value > maximum:
        raise PhaseGeometryError(f"{label}_OUT_OF_RANGE")
    return value


def canonical_phase_geometry() -> dict[str, Any]:
    core = {
        "schema": "HHS_PASS219_RML2_CANONICAL_PHASE_GEOMETRY_V1",
        "phase_modulus": PHASE_MODULUS,
        "quarter_cycle": QUARTER_CYCLE,
        "half_cycle": HALF_CYCLE,
        "full_cycle": FULL_CYCLE,
        "closure": "u^72=u^0",
        "typed_u0_is_scalar_zero": False,
        "rotor_order": list(ROTOR_ORDER),
        "rotors": {name: dict(ROTOR_GEOMETRY[name]) for name in ROTOR_ORDER},
        "reciprocal_pairs": [
            {"plane": PRIMARY_PLANE, "cw": "x", "ccw": "z"},
            {"plane": ORTHOGONAL_PLANE, "cw": "w", "ccw": "y"},
        ],
        "directional_products_preserved": ["xy", "yx", "zw", "wz"],
        "commutative_reorder_permitted": False,
        "nonassociative_rewrite_permitted": False,
        "scalar_projection_substitution_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    core["geometry_sha256"] = _sha256(core)
    return core


def _cyclic_distance(a: int, b: int) -> int:
    forward = (a - b) % PHASE_MODULUS
    reverse = (b - a) % PHASE_MODULUS
    return min(forward, reverse)


def _normalize_phase_steps(value: Any, label: str) -> dict[str, int]:
    if not isinstance(value, Mapping) or tuple(value.keys()) != ROTOR_ORDER:
        raise PhaseGeometryError(f"{label}_ORDERED_XYZW_PHASE_STEPS_REQUIRED")
    return {
        rotor: _exact_int(
            value.get(rotor),
            f"{label}_{rotor.upper()}_PHASE_STEP",
            minimum=0,
            maximum=PHASE_MODULUS - 1,
        )
        for rotor in ROTOR_ORDER
    }


def _normalize_phase_node_ids(value: Any, label: str) -> dict[str, str]:
    if not isinstance(value, Mapping) or tuple(value.keys()) != PHASE_CHANNELS:
        raise PhaseGeometryError(f"{label}_ORDERED_PHASE_CHANNELS_REQUIRED")
    nodes = {
        channel: _nonempty(value.get(channel), f"{label}_{channel}_NODE_ID")
        for channel in PHASE_CHANNELS
    }
    if len(set(nodes.values())) != len(PHASE_CHANNELS):
        raise PhaseGeometryError(f"{label}_DIRECTIONAL_PHASE_NODE_ID_COLLAPSE")
    return nodes


def _normalize_fold_tree(
    node: Any,
    *,
    depth: int = 0,
) -> tuple[Any, list[str]]:
    if depth > MAX_VALIDATION_NESTING_DEPTH:
        raise PhaseGeometryError("FOLD_TREE_VALIDATION_DEPTH_EXCEEDED")
    if isinstance(node, str):
        if node not in ROTOR_GEOMETRY:
            raise PhaseGeometryError(f"FOLD_TREE_ROTOR_UNSUPPORTED:{node}")
        return node, [node]
    if not isinstance(node, list) or len(node) != 2:
        raise PhaseGeometryError("FOLD_TREE_BINARY_NONASSOCIATIVE_NODE_REQUIRED")
    left, left_word = _normalize_fold_tree(node[0], depth=depth + 1)
    right, right_word = _normalize_fold_tree(node[1], depth=depth + 1)
    return [left, right], left_word + right_word


def evaluate_octonion_string(
    value: Mapping[str, Any],
    *,
    expected_parent_circuit_id: str,
) -> dict[str, Any]:
    _reject_float(value)
    if value.get("schema") != OCTONION_STRING_SCHEMA:
        raise PhaseGeometryError("OCTONION_STRING_SCHEMA_MISMATCH")
    string_id = _nonempty(value.get("string_id"), "OCTONION_STRING_ID")
    if _nonempty(value.get("parent_circuit_id"), "OCTONION_PARENT_CIRCUIT_ID") != expected_parent_circuit_id:
        raise PhaseGeometryError(f"OCTONION_PARENT_CIRCUIT_DRIFT:{string_id}")

    phase_steps = _normalize_phase_steps(value.get("phase_steps"), string_id)
    phase_nodes = _normalize_phase_node_ids(value.get("ordered_phase_node_ids"), string_id)
    fold_tree, fold_word = _normalize_fold_tree(value.get("fold_tree"))

    primary = _cyclic_distance(phase_steps["x"], phase_steps["z"])
    orthogonal = _cyclic_distance(phase_steps["y"], phase_steps["w"])
    signed = (
        phase_steps["x"]
        - phase_steps["z"]
        - phase_steps["y"]
        + phase_steps["w"]
    ) % PHASE_MODULUS
    net = _cyclic_distance(signed, 0)

    cross_plane_transitions = 0
    direction_reversals = 0
    for left, right in zip(fold_word, fold_word[1:]):
        if ROTOR_GEOMETRY[left]["plane"] != ROTOR_GEOMETRY[right]["plane"]:
            cross_plane_transitions += 1
        if ROTOR_GEOMETRY[left]["direction"] != ROTOR_GEOMETRY[right]["direction"]:
            direction_reversals += 1

    core = {
        "schema": "HHS_PASS219_RML2_OCTONION_PHASE_STRING_EVALUATION_V1",
        "string_id": string_id,
        "parent_circuit_id": expected_parent_circuit_id,
        "phase_steps": phase_steps,
        "phase_positions": {rotor: f"u^{phase_steps[rotor]}" for rotor in ROTOR_ORDER},
        "ordered_phase_node_ids": phase_nodes,
        "fold_tree": fold_tree,
        "fold_word": fold_word,
        "fold_word_sha256": _sha256({"ordered_fold_word": fold_word}),
        "parenthesization_sha256": _sha256({"fold_tree": fold_tree}),
        "cross_plane_transitions": cross_plane_transitions,
        "direction_reversals": direction_reversals,
        "primary_pair_disequilibrium_units": primary,
        "orthogonal_pair_disequilibrium_units": orthogonal,
        "net_signed_phase_residue": signed,
        "net_signed_phase_disequilibrium_units": net,
        "half_cycle_rotors": [
            rotor for rotor in ROTOR_ORDER if phase_steps[rotor] == HALF_CYCLE
        ],
        "quarter_cycle_rotors": [
            rotor
            for rotor in ROTOR_ORDER
            if phase_steps[rotor] in (QUARTER_CYCLE, HALF_CYCLE, 3 * QUARTER_CYCLE)
        ],
        "phase_closed": primary == 0 and orthogonal == 0 and net == 0,
        "typed_u0_is_scalar_zero": False,
        "scalar_projection_substitution_authority": False,
        "commutative_reorder_permitted": False,
        "nonassociative_rewrite_permitted": False,
    }
    core["octonion_string_root_sha256"] = _sha256(core)
    return core


def evaluate_phase_circuit(
    value: Mapping[str, Any],
    *,
    expected_parent_circuit_id: str | None = None,
    depth: int = 0,
) -> dict[str, Any]:
    _reject_float(value)
    if depth > MAX_VALIDATION_NESTING_DEPTH:
        raise PhaseGeometryError("PHASE_CIRCUIT_VALIDATION_DEPTH_EXCEEDED")
    if value.get("schema") != PHASE_CIRCUIT_SCHEMA:
        raise PhaseGeometryError("PHASE_CIRCUIT_SCHEMA_MISMATCH")

    circuit_id = _nonempty(value.get("circuit_id"), "PHASE_CIRCUIT_ID")
    parent = value.get("parent_circuit_id")
    if expected_parent_circuit_id is None:
        if parent is not None:
            raise PhaseGeometryError(f"ROOT_CIRCUIT_PARENT_FORBIDDEN:{circuit_id}")
    else:
        if _nonempty(parent, "PHASE_CIRCUIT_PARENT_ID") != expected_parent_circuit_id:
            raise PhaseGeometryError(f"PHASE_CIRCUIT_PARENT_DRIFT:{circuit_id}")

    children = value.get("children")
    if not isinstance(children, list) or not children:
        raise PhaseGeometryError(f"PHASE_CIRCUIT_CHILDREN_REQUIRED:{circuit_id}")

    evaluated_children: list[dict[str, Any]] = []
    child_ids: set[str] = set()
    leaf_count = 0
    nested_count = 0
    primary = 0
    orthogonal = 0
    net = 0
    nonclosed = 0

    for child in children:
        if not isinstance(child, Mapping):
            raise PhaseGeometryError(f"PHASE_CIRCUIT_CHILD_MAPPING_REQUIRED:{circuit_id}")
        schema = child.get("schema")
        if schema == OCTONION_STRING_SCHEMA:
            evaluated = evaluate_octonion_string(
                child,
                expected_parent_circuit_id=circuit_id,
            )
            child_id = str(evaluated["string_id"])
            child_root = str(evaluated["octonion_string_root_sha256"])
            leaf_count += 1
            primary += int(evaluated["primary_pair_disequilibrium_units"])
            orthogonal += int(evaluated["orthogonal_pair_disequilibrium_units"])
            net += int(evaluated["net_signed_phase_disequilibrium_units"])
            if evaluated["phase_closed"] is not True:
                nonclosed += 1
            record = {
                "kind": "OCTONION_STRING",
                "child_id": child_id,
                "child_root_sha256": child_root,
                "evaluation": evaluated,
            }
        elif schema == PHASE_CIRCUIT_SCHEMA:
            evaluated = evaluate_phase_circuit(
                child,
                expected_parent_circuit_id=circuit_id,
                depth=depth + 1,
            )
            child_id = str(evaluated["circuit_id"])
            child_root = str(evaluated["circuit_root_sha256"])
            leaf_count += int(evaluated["leaf_string_count"])
            nested_count += 1 + int(evaluated["nested_circuit_count"])
            primary += int(evaluated["phase_disequilibrium_vector"]["primary_pair_units"])
            orthogonal += int(evaluated["phase_disequilibrium_vector"]["orthogonal_pair_units"])
            net += int(evaluated["phase_disequilibrium_vector"]["net_signed_phase_units"])
            nonclosed += int(evaluated["phase_disequilibrium_vector"]["nonclosed_leaf_count"])
            record = {
                "kind": "PHASE_CIRCUIT",
                "child_id": child_id,
                "child_root_sha256": child_root,
                "evaluation": evaluated,
            }
        else:
            raise PhaseGeometryError(
                f"PHASE_CIRCUIT_CHILD_SCHEMA_UNSUPPORTED:{circuit_id}:{schema}"
            )

        if child_id in child_ids:
            raise PhaseGeometryError(f"DUPLICATE_PHASE_CIRCUIT_CHILD_ID:{circuit_id}:{child_id}")
        child_ids.add(child_id)
        evaluated_children.append(record)

    vector = {
        "primary_pair_units": primary,
        "orthogonal_pair_units": orthogonal,
        "net_signed_phase_units": net,
        "nonclosed_leaf_count": nonclosed,
    }
    core = {
        "schema": "HHS_PASS219_RML2_NESTED_PHASE_CIRCUIT_EVALUATION_V1",
        "circuit_id": circuit_id,
        "parent_circuit_id": expected_parent_circuit_id,
        "nesting_depth": depth,
        "ordered_child_ids": [row["child_id"] for row in evaluated_children],
        "ordered_child_roots_sha256": [
            row["child_root_sha256"] for row in evaluated_children
        ],
        "children": evaluated_children,
        "leaf_string_count": leaf_count,
        "nested_circuit_count": nested_count,
        "phase_disequilibrium_vector": vector,
        "phase_closed": all(item == 0 for item in vector.values()),
        "child_order_is_semantic_identity": True,
        "parenthesization_is_semantic_identity": True,
        "scalarized_phase_loss": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    core["circuit_root_sha256"] = _sha256(core)
    return core


def evaluate_phase_geometry_witness(
    evaluated_candidate: Mapping[str, Any],
    witness: Mapping[str, Any],
) -> dict[str, Any]:
    _reject_float(witness)
    if witness.get("schema") != GEOMETRY_WITNESS_SCHEMA:
        raise PhaseGeometryError("PHASE_GEOMETRY_WITNESS_SCHEMA_MISMATCH")
    candidate_root = _hex64(
        evaluated_candidate.get("candidate_manifold_root_sha256"),
        "RML_CANDIDATE_MANIFOLD_ROOT",
    )
    if _hex64(
        witness.get("candidate_manifold_root_sha256"),
        "PHASE_WITNESS_CANDIDATE_MANIFOLD_ROOT",
    ) != candidate_root:
        raise PhaseGeometryError("PHASE_WITNESS_MANIFOLD_ROOT_BINDING_DRIFT")

    root_raw = witness.get("root_circuit")
    if not isinstance(root_raw, Mapping):
        raise PhaseGeometryError("PHASE_WITNESS_ROOT_CIRCUIT_REQUIRED")
    circuit = evaluate_phase_circuit(root_raw)

    lanes_raw = witness.get("lane_bindings")
    if not isinstance(lanes_raw, list) or len(lanes_raw) != len(LANES):
        raise PhaseGeometryError("PHASE_WITNESS_EXACTLY_FOUR_LANE_BINDINGS_REQUIRED")
    evaluated_lanes = {
        str(row["lane"]): row for row in evaluated_candidate.get("lanes", [])
    }
    if set(evaluated_lanes) != set(LANES):
        raise PhaseGeometryError("RML_EVALUATED_FOUR_LANE_TOPOLOGY_REQUIRED")

    lane_bindings: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in lanes_raw:
        if not isinstance(row, Mapping):
            raise PhaseGeometryError("PHASE_LANE_BINDING_MAPPING_REQUIRED")
        lane = row.get("lane")
        if lane not in LANES or lane in seen:
            raise PhaseGeometryError("PHASE_LANE_BINDING_TOPOLOGY_DRIFT")
        seen.add(str(lane))
        parent = evaluated_lanes[str(lane)]
        phase_nodes = _normalize_phase_node_ids(
            row.get("ordered_phase_node_ids"),
            f"{lane}_PHASE_BINDING",
        )
        if phase_nodes != parent["ordered_phase_node_ids"]:
            raise PhaseGeometryError(f"{lane}_PHASE_NODE_BINDING_DRIFT")
        transition = _identity(
            row.get("candidate_transition_hash216"),
            216,
            f"{lane}_PHASE_BINDING_TRANSITION_HASH216",
        )
        if transition != parent["candidate_transition_hash216"]:
            raise PhaseGeometryError(f"{lane}_PHASE_TRANSITION_BINDING_DRIFT")
        if _hex64(
            row.get("phase_circuit_root_sha256"),
            f"{lane}_PHASE_CIRCUIT_ROOT",
        ) != circuit["circuit_root_sha256"]:
            raise PhaseGeometryError(f"{lane}_PHASE_CIRCUIT_ROOT_BINDING_DRIFT")
        lane_bindings.append(
            {
                "lane": lane,
                "candidate_transition_hash216": transition,
                "ordered_phase_node_ids": phase_nodes,
                "phase_circuit_root_sha256": circuit["circuit_root_sha256"],
            }
        )

    result = {
        "schema": "HHS_PASS219_RML2_PHASE_GEOMETRY_WITNESS_EVALUATION_V1",
        "candidate_manifold_root_sha256": candidate_root,
        "canonical_geometry": canonical_phase_geometry(),
        "root_circuit": circuit,
        "lane_bindings": lane_bindings,
        "phase_disequilibrium_vector": circuit["phase_disequilibrium_vector"],
        "zero_phase_disequilibrium": circuit["phase_closed"],
        "four_lanes_share_one_phase_circuit_root": True,
        "typed_u0_is_scalar_zero": False,
        "scalarized_phase_loss": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    result["phase_geometry_evaluation_sha256"] = _sha256(result)
    return result


def evaluate_phase_geometric_candidate(
    plan: Mapping[str, Any],
    package: Mapping[str, Any],
) -> dict[str, Any]:
    _reject_float(package)
    if package.get("schema") != PHASE_CANDIDATE_SCHEMA:
        raise PhaseGeometryError("PHASE_GEOMETRIC_CANDIDATE_SCHEMA_MISMATCH")
    candidate = package.get("candidate")
    witness = package.get("phase_geometry")
    if not isinstance(candidate, Mapping) or not isinstance(witness, Mapping):
        raise PhaseGeometryError("PHASE_GEOMETRIC_CANDIDATE_BINDINGS_REQUIRED")

    rml = evaluate_rml_candidate(plan, candidate)
    phase = evaluate_phase_geometry_witness(rml, witness)
    vector = {
        "constraint_units": int(rml["constraint_disequilibrium_units"]),
        **{
            key: int(value)
            for key, value in phase["phase_disequilibrium_vector"].items()
        },
    }
    zero = all(value == 0 for value in vector.values())
    result = {
        "schema": EVALUATION_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "candidate_id": rml["candidate_id"],
        "candidate_manifold_root_sha256": rml["candidate_manifold_root_sha256"],
        "rml1_candidate_evaluation_sha256": rml["candidate_evaluation_sha256"],
        "phase_geometry_evaluation_sha256": phase["phase_geometry_evaluation_sha256"],
        "phase_circuit_root_sha256": phase["root_circuit"]["circuit_root_sha256"],
        "typed_disequilibrium_vector": vector,
        "typed_disequilibrium_scalarized": False,
        "zero_disequilibrium": zero,
        "constraint_zero": rml["zero_disequilibrium"],
        "phase_zero": phase["zero_phase_disequilibrium"],
        "ordered_higher_dimensional_fold_paths_preserved": True,
        "nested_octonion_circuits_enabled": True,
        "noncommutative_transport_order_preserved": True,
        "nonassociative_parenthesization_preserved": True,
        "scalar_projection_substitution_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    result["candidate_phase_evaluation_sha256"] = _sha256(result)
    return result


_VECTOR_FIELDS = (
    "constraint_units",
    "primary_pair_units",
    "orthogonal_pair_units",
    "net_signed_phase_units",
    "nonclosed_leaf_count",
)


def _dominates(left: Mapping[str, int], right: Mapping[str, int]) -> bool:
    le_all = all(int(left[field]) <= int(right[field]) for field in _VECTOR_FIELDS)
    lt_any = any(int(left[field]) < int(right[field]) for field in _VECTOR_FIELDS)
    return le_all and lt_any


def learn_phase_geometric_frontier(
    plan: Mapping[str, Any],
    packages: Iterable[Mapping[str, Any]],
    *,
    learning_depth: int,
    parent_learning_receipt_sha256: str | None = None,
) -> dict[str, Any]:
    depth = _exact_int(learning_depth, "PHASE_LEARNING_DEPTH", minimum=0)
    parent_receipt = (
        None
        if parent_learning_receipt_sha256 is None
        else _hex64(parent_learning_receipt_sha256, "PARENT_PHASE_LEARNING_RECEIPT")
    )
    material = list(packages)
    if not material:
        raise PhaseGeometryError("EMPTY_PHASE_GEOMETRIC_CANDIDATE_SET")

    evaluations = [evaluate_phase_geometric_candidate(plan, row) for row in material]
    ids = [str(row["candidate_id"]) for row in evaluations]
    if len(ids) != len(set(ids)):
        raise PhaseGeometryError("DUPLICATE_PHASE_GEOMETRIC_CANDIDATE_ID")

    frontier: list[str] = []
    for candidate in evaluations:
        vector = candidate["typed_disequilibrium_vector"]
        dominated = any(
            other["candidate_id"] != candidate["candidate_id"]
            and _dominates(other["typed_disequilibrium_vector"], vector)
            for other in evaluations
        )
        if not dominated:
            frontier.append(str(candidate["candidate_id"]))
    frontier.sort()

    zero = sorted(
        str(row["candidate_id"])
        for row in evaluations
        if row["zero_disequilibrium"] is True
    )
    decision = (
        "ZERO_PHASE_GEOMETRIC_FRONTIER_READY_FOR_VM81_ADMISSION"
        if zero
        else "CONTINUE_RECURSIVE_PHASE_GEOMETRIC_SEARCH_FROM_PARETO_FRONTIER"
    )

    receipt = {
        "schema": LEARNING_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "learning_depth": depth,
        "parent_learning_receipt_sha256": parent_receipt,
        "candidate_count": len(evaluations),
        "disequilibrium_fields": list(_VECTOR_FIELDS),
        "cross_domain_scalar_loss_forbidden": True,
        "frontier_rule": "PARETO_NONDOMINATED_TYPED_DISEQUILIBRIUM",
        "pareto_frontier_candidate_ids": frontier,
        "zero_disequilibrium_candidate_ids": zero,
        "decision": decision,
        "candidate_evaluations": sorted(
            evaluations,
            key=lambda row: str(row["candidate_id"]),
        ),
        "phase_geometry_semantics": {
            "x": "PRIMARY_XZ:CW",
            "z": "PRIMARY_XZ:CCW",
            "y": "ORTHOGONAL_YW:CCW",
            "w": "ORTHOGONAL_YW:CW",
            "u0_to_u36": "HALF_CYCLE",
            "u72_equals_u0": True,
            "typed_u0_is_scalar_zero": False,
            "nested_octonion_circuits": True,
            "fold_order_is_semantic_identity": True,
            "parenthesization_is_semantic_identity": True,
        },
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "result": "PASS",
    }
    receipt["receipt_sha256"] = _sha256(receipt)
    return receipt

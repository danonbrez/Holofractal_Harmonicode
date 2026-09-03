"""Pass 219 I153 local/global equation search-space filter.

This is a read-only candidate filter.  It binds the already-preserved monolithic
UQCEL equation to the I152 fixed target/work manifold and to one local Hash216
5184-hydration parameter snapshot P.  It does not evaluate the Harmonicode
algebra, mint Hash72/Hash216 authority, or mutate VM81.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import string
from typing import Any, Iterable, Mapping

from hhs_runtime.core_sandbox.hhs_pass219_combined_equation_optimizer_1_21_8 import (
    COMBINED_SHA256,
    NUMERATOR_BYTES,
    NUMERATOR_PATH,
    NUMERATOR_SHA256,
)
from hhs_runtime.core_sandbox.hhs_pass219_proof_preserving_optimizer_1_21_12 import (
    EXPECTED_GATE_OFFSETS,
    activate_proof_preserving_optimization,
)
from hhs_runtime.pass219.fixed_cardinality_optimization import (
    ROUTE_MULTIPLICITY_PER_TARGET,
    TARGET_CARDINALITY,
    WORKING_MANIFOLD_CARDINALITY,
    encode_working_route,
    validate_fixed_cardinalities,
)

PASS = 219
ITERATION = "I153"
SCHEMA = "HHS_PASS219_I153_LOCAL_GLOBAL_EQUATION_SEARCH_FILTER_V1"
SNAPSHOT_SCHEMA = "HHS_PASS219_I153_LOCAL_HASH216_5184_P_SNAPSHOT_V1"
CANDIDATE_SCHEMA = "HHS_PASS219_I153_EQUATION_FILTER_CANDIDATE_V1"
WITNESS_SCHEMA = "HHS_PASS219_I153_EQUATION_FILTER_WITNESS_V1"

HYDRATION_BITS = 5184
GATE_OFFSETS = tuple(EXPECTED_GATE_OFFSETS)
GATE_COUNT = len(GATE_OFFSETS)
MAX_FILTER_CANDIDATES = 65536

HASH216_FORMAT_GENOME_ROOT = "PASS150_HASH216_GENOME_ROOT_SHA256"
HASH216_FORMAT_THREE_HASH72 = "HASH216_THREE_HASH72_216_GLYPH"

HEX = frozenset(string.hexdigits)


class EquationSearchFilterError(RuntimeError):
    pass


def _exact_int(value: Any, name: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise EquationSearchFilterError(f"{name}_EXACT_INTEGER_REQUIRED")
    if minimum is not None and value < minimum:
        raise EquationSearchFilterError(f"{name}_OUT_OF_RANGE")
    return value


def _flag(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise EquationSearchFilterError(f"{name}_BOOLEAN_REQUIRED")
    return value


def _hex64(value: Any, name: str, *, nonzero: bool = False) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(ch not in HEX for ch in value):
        raise EquationSearchFilterError(f"{name}_SHA256_HEX_REQUIRED")
    lowered = value.lower()
    if nonzero and lowered == "0" * 64:
        raise EquationSearchFilterError(f"{name}_ZERO_FORBIDDEN")
    return lowered


def _canonical_json(value: Mapping[str, Any]) -> bytes:
    def reject_float(node: Any) -> None:
        if isinstance(node, float):
            raise EquationSearchFilterError("FLOAT_CANONICAL_INPUT_FORBIDDEN")
        if isinstance(node, Mapping):
            for child in node.values():
                reject_float(child)
        elif isinstance(node, (list, tuple)):
            for child in node:
                reject_float(child)

    reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _diagnostic_sha256(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def validate_hash216_identity(value: Any, identity_format: Any) -> tuple[str, str]:
    if not isinstance(identity_format, str):
        raise EquationSearchFilterError("SNAPSHOT_HASH216_FORMAT_REQUIRED")
    if not isinstance(value, str):
        raise EquationSearchFilterError("SNAPSHOT_HASH216_STRING_REQUIRED")

    if identity_format == HASH216_FORMAT_GENOME_ROOT:
        return _hex64(value, "SNAPSHOT_HASH216"), identity_format

    if identity_format == HASH216_FORMAT_THREE_HASH72:
        if len(value) != 216:
            raise EquationSearchFilterError("SNAPSHOT_HASH216_216_GLYPHS_REQUIRED")
        if any(ord(ch) < 33 or ord(ch) > 126 for ch in value):
            raise EquationSearchFilterError("SNAPSHOT_HASH216_216_GLYPHS_PRINTABLE_REQUIRED")
        return value, identity_format

    raise EquationSearchFilterError("SNAPSHOT_HASH216_FORMAT_UNSUPPORTED")


def normalize_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    if snapshot.get("schema") != SNAPSHOT_SCHEMA:
        raise EquationSearchFilterError("SNAPSHOT_SCHEMA_MISMATCH")
    identity, identity_format = validate_hash216_identity(
        snapshot.get("snapshot_hash216"),
        snapshot.get("snapshot_hash216_format"),
    )
    p_value = _exact_int(snapshot.get("P"), "P", minimum=1)
    hydration_bits = _exact_int(snapshot.get("hydration_bits"), "HYDRATION_BITS", minimum=1)
    if hydration_bits != HYDRATION_BITS:
        raise EquationSearchFilterError("HYDRATION_BITS_DRIFT")

    normalized = {
        "schema": SNAPSHOT_SCHEMA,
        "snapshot_hash216": identity,
        "snapshot_hash216_format": identity_format,
        "P": p_value,
        "hydration_bits": hydration_bits,
        "equation_source_path": str(NUMERATOR_PATH),
        "equation_source_bytes": NUMERATOR_BYTES,
        "equation_source_sha256": NUMERATOR_SHA256,
        "combined_source_sha256": COMBINED_SHA256,
        "target_cardinality_decimal": str(TARGET_CARDINALITY),
        "working_manifold_cardinality_decimal": str(WORKING_MANIFOLD_CARDINALITY),
        "route_multiplicity_per_target_decimal": str(ROUTE_MULTIPLICITY_PER_TARGET),
        "P_scope": "LOCAL_HASH216_5184_HYDRATION_PARAMETER_SNAPSHOT",
        "P_changes_global_cardinality": False,
    }
    normalized["snapshot_binding_sha256"] = _diagnostic_sha256(normalized)
    return normalized


def make_snapshot(
    *,
    snapshot_hash216: str,
    snapshot_hash216_format: str,
    P: int,
) -> dict[str, Any]:
    return normalize_snapshot(
        {
            "schema": SNAPSHOT_SCHEMA,
            "snapshot_hash216": snapshot_hash216,
            "snapshot_hash216_format": snapshot_hash216_format,
            "P": P,
            "hydration_bits": HYDRATION_BITS,
        }
    )


def _validate_gate(
    gate: Mapping[str, Any],
    *,
    expected_index: int,
    expected_offset: int,
    snapshot_binding_sha256: str,
    global_root: str,
) -> dict[str, Any]:
    index = _exact_int(gate.get("gate_index"), "GATE_INDEX", minimum=0)
    offset = _exact_int(gate.get("source_offset"), "GATE_SOURCE_OFFSET", minimum=0)
    if index != expected_index or offset != expected_offset:
        raise EquationSearchFilterError("GATE_TOPOLOGY_DRIFT")
    result = _flag(gate.get("boolean_result"), "GATE_BOOLEAN_RESULT")
    if _hex64(
        gate.get("snapshot_binding_sha256"),
        "GATE_SNAPSHOT_BINDING",
        nonzero=True,
    ) != snapshot_binding_sha256:
        raise EquationSearchFilterError("GATE_LOCAL_SNAPSHOT_BINDING_DRIFT")
    if _hex64(
        gate.get("global_symbol_environment_root"),
        "GATE_GLOBAL_ENVIRONMENT_ROOT",
        nonzero=True,
    ) != global_root:
        raise EquationSearchFilterError("GATE_GLOBAL_ENVIRONMENT_BINDING_DRIFT")
    return {
        "gate_index": index,
        "source_offset": offset,
        "boolean_result": result,
        "snapshot_binding_sha256": snapshot_binding_sha256,
        "global_symbol_environment_root": global_root,
    }


def evaluate_candidate(
    snapshot: Mapping[str, Any],
    candidate: Mapping[str, Any],
) -> dict[str, Any]:
    fixed = validate_fixed_cardinalities()
    snap = normalize_snapshot(snapshot)
    if candidate.get("schema") != CANDIDATE_SCHEMA:
        raise EquationSearchFilterError("CANDIDATE_SCHEMA_MISMATCH")

    block = _exact_int(candidate.get("target_block_index"), "TARGET_BLOCK_INDEX", minimum=0)
    route = _exact_int(candidate.get("route_index"), "ROUTE_INDEX", minimum=0)
    expected_working = encode_working_route(block, route)
    working = _exact_int(candidate.get("working_index"), "WORKING_INDEX", minimum=0)
    if working != expected_working:
        raise EquationSearchFilterError("WORKING_INDEX_ROUTE_BINDING_DRIFT")

    witness = candidate.get("equation_witness")
    if not isinstance(witness, Mapping) or witness.get("schema") != WITNESS_SCHEMA:
        raise EquationSearchFilterError("EQUATION_WITNESS_SCHEMA_MISMATCH")
    if witness.get("equation_source_sha256") != NUMERATOR_SHA256:
        raise EquationSearchFilterError("EQUATION_SOURCE_IDENTITY_DRIFT")
    if witness.get("combined_source_sha256") != COMBINED_SHA256:
        raise EquationSearchFilterError("COMBINED_SOURCE_IDENTITY_DRIFT")
    if witness.get("snapshot_binding_sha256") != snap["snapshot_binding_sha256"]:
        raise EquationSearchFilterError("LOCAL_P_SNAPSHOT_BINDING_DRIFT")

    global_root = _hex64(
        witness.get("global_symbol_environment_root"),
        "GLOBAL_SYMBOL_ENVIRONMENT_ROOT",
        nonzero=True,
    )
    gates_raw = witness.get("gates")
    if not isinstance(gates_raw, list) or len(gates_raw) != GATE_COUNT:
        raise EquationSearchFilterError("GATE_COUNT_DRIFT")
    gates = [
        _validate_gate(
            gate,
            expected_index=index,
            expected_offset=GATE_OFFSETS[index],
            snapshot_binding_sha256=str(snap["snapshot_binding_sha256"]),
            global_root=global_root,
        )
        for index, gate in enumerate(gates_raw)
    ]

    environment_complete = _flag(
        witness.get("global_symbol_environment_complete"),
        "GLOBAL_SYMBOL_ENVIRONMENT_COMPLETE",
    )
    revalidation_complete = _flag(
        witness.get("cross_layer_revalidation_complete"),
        "CROSS_LAYER_REVALIDATION_COMPLETE",
    )
    local_shadowing = _flag(
        witness.get("local_symbol_shadowing_detected"),
        "LOCAL_SYMBOL_SHADOWING_DETECTED",
    )

    all_true = all(gate["boolean_result"] for gate in gates)
    first_false = next(
        (gate["gate_index"] for gate in gates if not gate["boolean_result"]),
        None,
    )
    reasons: list[str] = []
    if not all_true:
        reasons.append("BOOLEAN_GATE_FALSE")
    if not environment_complete:
        reasons.append("GLOBAL_ENVIRONMENT_INCOMPLETE")
    if not revalidation_complete:
        reasons.append("CROSS_LAYER_REVALIDATION_INCOMPLETE")
    if local_shadowing:
        reasons.append("LOCAL_SYMBOL_SHADOWING_DETECTED")

    survives = not reasons
    decision = "SURVIVES_LOCAL_GLOBAL_EQUATION_FILTER" if survives else "REJECTED_BY_LOCAL_GLOBAL_EQUATION_FILTER"

    return {
        "schema": "HHS_PASS219_I153_EQUATION_FILTER_DECISION_V1",
        "pass": PASS,
        "iteration": ITERATION,
        "decision": decision,
        "survives_equation_filter": survives,
        "rejection_reasons": reasons,
        "first_false_gate": first_false,
        "target_block_index": block,
        "route_index": route,
        "working_index": working,
        "snapshot_binding_sha256": snap["snapshot_binding_sha256"],
        "snapshot_hash216": snap["snapshot_hash216"],
        "snapshot_hash216_format": snap["snapshot_hash216_format"],
        "P": snap["P"],
        "P_scope": snap["P_scope"],
        "global_symbol_environment_root": global_root,
        "equation_source_sha256": NUMERATOR_SHA256,
        "combined_source_sha256": COMBINED_SHA256,
        "gate_offsets": list(GATE_OFFSETS),
        "gate_results": [gate["boolean_result"] for gate in gates],
        "global_symbol_environment_complete": environment_complete,
        "cross_layer_revalidation_complete": revalidation_complete,
        "local_symbol_shadowing_detected": local_shadowing,
        "fixed_cardinality_receipt": fixed,
        "pass169_whole_expression_authority_required": True,
        "canonical_admission_claimed": False,
        "canonical_vm81_mutation": False,
        "canonical_hash72_mint": False,
        "canonical_hash216_persistence": False,
    }


def filter_search_space(
    snapshot: Mapping[str, Any],
    candidates: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    snap = normalize_snapshot(snapshot)
    schedule = activate_proof_preserving_optimization()
    if schedule["source_binding"]["combined_source_sha256"] != COMBINED_SHA256:
        raise EquationSearchFilterError("I12112_COMBINED_SOURCE_BINDING_DRIFT")
    if schedule["authority_boundary"]["pass169_whole_expression_admission_required"] is not True:
        raise EquationSearchFilterError("I12112_PASS169_AUTHORITY_DRIFT")

    material = list(candidates)
    if len(material) > MAX_FILTER_CANDIDATES:
        raise EquationSearchFilterError("CANDIDATE_BATCH_BOUND_EXCEEDED")

    decisions: list[dict[str, Any]] = []
    seen_working: set[int] = set()
    for candidate in material:
        decision = evaluate_candidate(snap, candidate)
        working = int(decision["working_index"])
        if working in seen_working:
            raise EquationSearchFilterError("DUPLICATE_WORKING_INDEX")
        seen_working.add(working)
        decisions.append(decision)

    survivors = [row for row in decisions if row["survives_equation_filter"]]
    rejected = [row for row in decisions if not row["survives_equation_filter"]]
    reasons = Counter(
        reason
        for row in rejected
        for reason in row["rejection_reasons"]
    )

    input_count = len(decisions)
    survivor_count = len(survivors)
    reduction_numerator = input_count
    reduction_denominator = survivor_count if survivor_count else 1

    receipt = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "classification": "READ_ONLY_LOCAL_GLOBAL_EQUATION_SEARCH_FILTER",
        "equation_source": {
            "path": str(NUMERATOR_PATH),
            "bytes": NUMERATOR_BYTES,
            "sha256": NUMERATOR_SHA256,
            "combined_source_sha256": COMBINED_SHA256,
            "preserved_verbatim": True,
        },
        "snapshot": snap,
        "fixed_search_space": {
            "target_cardinality_decimal": str(TARGET_CARDINALITY),
            "working_manifold_cardinality_decimal": str(WORKING_MANIFOLD_CARDINALITY),
            "route_multiplicity_per_target_decimal": str(ROUTE_MULTIPLICITY_PER_TARGET),
            "P_changes_cardinality": False,
        },
        "candidate_count": input_count,
        "survivor_count": survivor_count,
        "rejected_count": len(rejected),
        "rejection_reason_counts": dict(sorted(reasons.items())),
        "candidate_reduction_fraction": {
            "numerator": reduction_numerator,
            "denominator": reduction_denominator,
        },
        "candidate_reduction_x1000_floor": (
            reduction_numerator * 1000 // reduction_denominator
        ),
        "survivor_working_indices": [row["working_index"] for row in survivors],
        "decisions": decisions,
        "proof_preserving_schedule_sha256": schedule["optimization_schedule_sha256"],
        "pass169_whole_expression_authority_required": True,
        "filter_produces_boolean_gate_truth": False,
        "filter_produces_canonical_monolithic_proof": False,
        "canonical_vm81_mutation": False,
        "canonical_hash72_mint": False,
        "canonical_hash216_persistence": False,
        "physical_full_manifold_enumeration_claim": False,
        "result": "PASS",
    }
    receipt["receipt_sha256"] = _diagnostic_sha256(receipt)
    return receipt


def make_candidate(
    *,
    snapshot: Mapping[str, Any],
    target_block_index: int,
    route_index: int,
    global_symbol_environment_root: str,
    gate_results: Iterable[bool],
    global_symbol_environment_complete: bool = True,
    cross_layer_revalidation_complete: bool = True,
    local_symbol_shadowing_detected: bool = False,
) -> dict[str, Any]:
    snap = normalize_snapshot(snapshot)
    root = _hex64(
        global_symbol_environment_root,
        "GLOBAL_SYMBOL_ENVIRONMENT_ROOT",
        nonzero=True,
    )
    results = list(gate_results)
    if len(results) != GATE_COUNT or any(not isinstance(value, bool) for value in results):
        raise EquationSearchFilterError("GATE_RESULTS_REQUIRE_FIVE_BOOLEANS")
    block = _exact_int(target_block_index, "TARGET_BLOCK_INDEX", minimum=0)
    route = _exact_int(route_index, "ROUTE_INDEX", minimum=0)
    working = encode_working_route(block, route)

    gates = [
        {
            "gate_index": index,
            "source_offset": GATE_OFFSETS[index],
            "boolean_result": result,
            "snapshot_binding_sha256": snap["snapshot_binding_sha256"],
            "global_symbol_environment_root": root,
        }
        for index, result in enumerate(results)
    ]
    return {
        "schema": CANDIDATE_SCHEMA,
        "target_block_index": block,
        "route_index": route,
        "working_index": working,
        "equation_witness": {
            "schema": WITNESS_SCHEMA,
            "equation_source_sha256": NUMERATOR_SHA256,
            "combined_source_sha256": COMBINED_SHA256,
            "snapshot_binding_sha256": snap["snapshot_binding_sha256"],
            "global_symbol_environment_root": root,
            "gates": gates,
            "global_symbol_environment_complete": global_symbol_environment_complete,
            "cross_layer_revalidation_complete": cross_layer_revalidation_complete,
            "local_symbol_shadowing_detected": local_symbol_shadowing_detected,
        },
    }

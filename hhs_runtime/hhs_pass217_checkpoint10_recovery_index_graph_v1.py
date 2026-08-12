"""Pass 217 Checkpoint 10 physical recovery, exact receipt indexing, and SQL context graph.

This checkpoint extends the validated Checkpoint 9 cumulative authority slice with:

* physical_recovery -> Pass 212 ``FullHydrationRecoveryRuntime.recover_payload``;
* receipt_vector_indexing -> repaired exact-integer ``HHSReceiptVectorIndex``;
* sql_context_graph -> Pass 145 ``HHS145Database.get_object`` plus immutable
  database-root/integrity verification, aligned with the later Pass 194 SQL
  context-graph contract.

The receipt index repair preserves the intended historical ranking geometry while
removing all float authority: character coordinates are exact ordinals, witness
bits are scaled by 127, and squared integer distance is used instead of sqrt.

Absent domains are mechanically NOT_APPLICABLE. Partial or malformed applicable
context fails closed. Preflight SQL traversal is read-only; physical recovery
operates on an ephemeral erasure view; receipt indexing mutates only the supplied
exact acceleration index and never alters the validated receipt object.
"""

from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from hhs_runtime.hhs_cumulative_execution_authority_v1 import (
    ACTIVE_IN_PATH,
    EXPLICITLY_SUPERSEDED,
    NOT_APPLICABLE,
    build_authority_reachability,
)
from hhs_runtime.hhs_pass217_checkpoint9_rom_compression_v1 import (
    CHECKPOINT9_REQUIRED_AUTHORITIES,
    build_checkpoint9_inherited_authority_reachability,
)


VERSION = "PASS_217_CUMULATIVE_EXECUTION_COMPOSER_CHECKPOINT_10_V1"
PHYSICAL_RECOVERY_REQUEST_SCHEMA = "HHS_PASS217_PHYSICAL_RECOVERY_REQUEST_V1"
RECEIPT_VECTOR_INDEX_REQUEST_SCHEMA = "HHS_PASS217_RECEIPT_VECTOR_INDEX_REQUEST_V1"
SQL_CONTEXT_GRAPH_REQUEST_SCHEMA = "HHS_PASS217_SQL_CONTEXT_GRAPH_REQUEST_V1"

CHECKPOINT10_AUTHORITIES = (
    "physical_recovery",
    "receipt_vector_indexing",
    "sql_context_graph",
)
CHECKPOINT10_REQUIRED_AUTHORITIES = CHECKPOINT9_REQUIRED_AUTHORITIES + CHECKPOINT10_AUTHORITIES

CHECKPOINT10_AUTHORITY_MAP: Dict[str, Dict[str, Any]] = {
    "physical_recovery": {
        "origin_pass": 212,
        "module": "hhs_backend.runtime.hhs_pass212_full_hydration_recovery_v1",
        "symbol": "FullHydrationRecoveryRuntime.recover_payload",
        "callable_role": (
            "GF(256) two-parity physical shard erasure recovery with exact shard "
            "hash and protected-root verification"
        ),
        "runtime_authority": True,
    },
    "receipt_vector_indexing": {
        "origin": "inherited receipt-memory runtime used by Pass 044 and later execution routing",
        "module": "hhs_runtime.hhs_receipt_vector_index_v1",
        "symbol": "HHSReceiptVectorIndex.insert_receipt",
        "lookup_symbol": "HHSReceiptVectorIndex.get_receipt_node",
        "root_symbol": "HHSReceiptVectorIndex.index_root_hash216",
        "repair_contract_pass": 216,
        "numeric_authority": "EXACT_INTEGER_ONLY",
        "distance_metric": "SQUARED_INTEGER_EQUIVALENT_OF_NORMALIZED_EUCLIDEAN_V1",
        "runtime_authority": True,
    },
    "sql_context_graph": {
        "origin_pass": 145,
        "later_contract_alignment_pass": 194,
        "module": "hhs_runtime.pass145.database",
        "symbol": "HHS145Database.get_object",
        "root_symbol": "HHS145Database.database_root",
        "integrity_symbol": "HHS145Database.integrity_check",
        "callable_role": (
            "transactional SQLite object/relation graph lookup under canonical "
            "database root and receipt-linked state"
        ),
        "preflight_mutation_authority": False,
    },
}


def _walk_mappings(value: Any) -> Iterable[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        yield value
        for child in value.values():
            yield from _walk_mappings(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from _walk_mappings(child)


def _unique_mappings(values: Iterable[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    seen: set[int] = set()
    output: List[Mapping[str, Any]] = []
    for value in values:
        marker = id(value)
        if marker in seen:
            continue
        seen.add(marker)
        output.append(value)
    return output


def _request_candidates(
    payload: Optional[Mapping[str, Any]],
    *,
    named_key: str,
    schema: str,
) -> List[Mapping[str, Any]]:
    found: List[Mapping[str, Any]] = []
    for mapping in _walk_mappings(dict(payload or {})):
        named = mapping.get(named_key)
        if isinstance(named, Mapping):
            found.append(named)
        if mapping.get("schema") == schema:
            found.append(mapping)
    return _unique_mappings(found)


def _physical_candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    return _request_candidates(
        payload,
        named_key="physical_recovery",
        schema=PHYSICAL_RECOVERY_REQUEST_SCHEMA,
    )


def _receipt_index_candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    return _request_candidates(
        payload,
        named_key="receipt_vector_indexing",
        schema=RECEIPT_VECTOR_INDEX_REQUEST_SCHEMA,
    )


def _sql_graph_candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    return _request_candidates(
        payload,
        named_key="sql_context_graph",
        schema=SQL_CONTEXT_GRAPH_REQUEST_SCHEMA,
    )


def checkpoint10_context_facts(payload: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    physical = _physical_candidates(payload)
    receipt = _receipt_index_candidates(payload)
    sql = _sql_graph_candidates(payload)
    return {
        "schema": "HHS_PASS217_CHECKPOINT10_APPLICABILITY_FACTS_V1",
        "physical_recovery_domain_present": bool(physical),
        "physical_recovery_candidate_count": len(physical),
        "physical_recovery_exact_schema_count": sum(
            row.get("schema") == PHYSICAL_RECOVERY_REQUEST_SCHEMA for row in physical
        ),
        "receipt_vector_indexing_domain_present": bool(receipt),
        "receipt_vector_indexing_candidate_count": len(receipt),
        "receipt_vector_indexing_exact_schema_count": sum(
            row.get("schema") == RECEIPT_VECTOR_INDEX_REQUEST_SCHEMA for row in receipt
        ),
        "sql_context_graph_domain_present": bool(sql),
        "sql_context_graph_candidate_count": len(sql),
        "sql_context_graph_exact_schema_count": sum(
            row.get("schema") == SQL_CONTEXT_GRAPH_REQUEST_SCHEMA for row in sql
        ),
    }


def _active_failure(authority_id: str, reason: str, facts: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "observed": False,
        "path": ["kernel_runtime_autocomposer", authority_id],
        "traversal_witness": {
            "schema": "HHS_PASS217_CHECKPOINT10_TRAVERSAL_FAILURE_V1",
            "status": "REJECT_CHECKPOINT10_INHERITED_TRAVERSAL",
            "authority_id": authority_id,
            "reason": str(reason),
            "authority_map": dict(CHECKPOINT10_AUTHORITY_MAP[authority_id]),
            "applicability_facts": dict(facts),
        },
        "witness_root": "",
    }


def _exact_string_list(value: Any, label: str, *, nonempty: bool = True) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValueError(f"REJECT_CHECKPOINT10_{label}_SEQUENCE_REQUIRED")
    output: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item:
            raise ValueError(f"REJECT_CHECKPOINT10_{label}_STRING_INVALID")
        output.append(item)
    if nonempty and not output:
        raise ValueError(f"REJECT_CHECKPOINT10_{label}_EMPTY")
    if len(output) != len(set(output)):
        raise ValueError(f"REJECT_CHECKPOINT10_{label}_DUPLICATE")
    return tuple(output)


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise TypeError("REJECT_CHECKPOINT10_FLOAT_CANONICAL_AUTHORITY_FORBIDDEN")
    if isinstance(value, Mapping):
        for child in value.values():
            _reject_float(child)
    elif isinstance(value, (list, tuple, set)):
        for child in value:
            _reject_float(child)


def observe_physical_recovery(
    payload: Optional[Mapping[str, Any]],
    *,
    facts: Optional[Mapping[str, Any]] = None,
    physical_recovery_runtime: Any = None,
    physical_protected_payload: Any = None,
) -> Dict[str, Any]:
    applicability = dict(facts or checkpoint10_context_facts(payload))
    candidates = _physical_candidates(payload)
    if len(candidates) != 1:
        return _active_failure(
            "physical_recovery",
            "REJECT_PASS212_PHYSICAL_RECOVERY_REQUEST_BUNDLE_COUNT",
            applicability,
        )
    request = candidates[0]
    if request.get("schema") != PHYSICAL_RECOVERY_REQUEST_SCHEMA:
        return _active_failure(
            "physical_recovery",
            "REJECT_PASS212_PHYSICAL_RECOVERY_REQUEST_SCHEMA",
            applicability,
        )
    try:
        if physical_protected_payload is None:
            raise ValueError("REJECT_PASS212_PHYSICAL_PROTECTED_PAYLOAD_MISSING")
        if physical_recovery_runtime is None:
            from hhs_backend.runtime.hhs_pass212_full_hydration_recovery_v1 import (
                FullHydrationRecoveryRuntime,
            )
            physical_recovery_runtime = FullHydrationRecoveryRuntime()

        expected_root = request.get("protected_root216")
        expected_sha = request.get("expected_recovered_sha256")
        expected_length = request.get("expected_recovered_length")
        if not isinstance(expected_root, str) or len(expected_root) != 64:
            raise ValueError("REJECT_PASS212_PHYSICAL_PROTECTED_ROOT_INVALID")
        if not isinstance(expected_sha, str) or len(expected_sha) != 64:
            raise ValueError("REJECT_PASS212_PHYSICAL_EXPECTED_SHA256_INVALID")
        if not isinstance(expected_length, int) or isinstance(expected_length, bool) or expected_length <= 0:
            raise ValueError("REJECT_PASS212_PHYSICAL_EXPECTED_LENGTH_INVALID")
        if getattr(physical_protected_payload, "root216", None) != expected_root:
            raise ValueError("REJECT_PASS212_PHYSICAL_PROTECTED_ROOT_MISMATCH")
        if getattr(physical_protected_payload, "original_length", None) != expected_length:
            raise ValueError("REJECT_PASS212_PHYSICAL_ORIGINAL_LENGTH_MISMATCH")

        missing_refs = _exact_string_list(request.get("missing_shard_refs"), "PHYSICAL_MISSING_REFS")
        known_refs = {str(shard.ref) for shard in physical_protected_payload.shards}
        if not set(missing_refs) <= known_refs:
            raise ValueError("REJECT_PASS212_PHYSICAL_UNKNOWN_SHARD_REFERENCE")

        damaged_shards = tuple(
            replace(shard, payload=None) if shard.ref in set(missing_refs) else shard
            for shard in physical_protected_payload.shards
        )
        damaged = replace(physical_protected_payload, shards=damaged_shards)
        recovered = physical_recovery_runtime.recover_payload(damaged)
        recovered_sha = sha256(recovered).hexdigest()
        if len(recovered) != expected_length or recovered_sha != expected_sha:
            raise ValueError("REJECT_PASS212_PHYSICAL_RECOVERY_EXACTNESS_MISMATCH")

        info = CHECKPOINT10_AUTHORITY_MAP["physical_recovery"]
        return {
            "observed": True,
            "path": [
                "kernel_runtime_autocomposer",
                "physical_recovery",
                f"{info['module']}.{info['symbol']}",
            ],
            "traversal_witness": {
                "schema": "HHS_PASS217_PHYSICAL_RECOVERY_TRAVERSAL_V1",
                "status": "ADMIT_PHYSICAL_RECOVERY_TRAVERSAL",
                "repository_native_callable": dict(info),
                "protected_root216": expected_root,
                "protected_receipt_hash72": getattr(
                    physical_protected_payload, "receipt_hash72", ""
                ),
                "missing_shard_refs": list(missing_refs),
                "missing_shard_count": len(missing_refs),
                "recovered_length": len(recovered),
                "recovered_sha256": recovered_sha,
                "exact_recovery_verified": True,
                "applicability_facts": applicability,
            },
            "witness_root": expected_root,
        }
    except Exception as exc:
        return _active_failure(
            "physical_recovery",
            f"REJECT_PASS212_PHYSICAL_RECOVERY_TRAVERSAL:{type(exc).__name__}:{exc}",
            applicability,
        )


def observe_receipt_vector_indexing(
    payload: Optional[Mapping[str, Any]],
    *,
    facts: Optional[Mapping[str, Any]] = None,
    receipt_vector_index: Any = None,
    receipt_vector_receipt: Any = None,
) -> Dict[str, Any]:
    applicability = dict(facts or checkpoint10_context_facts(payload))
    candidates = _receipt_index_candidates(payload)
    if len(candidates) != 1:
        return _active_failure(
            "receipt_vector_indexing",
            "REJECT_RECEIPT_VECTOR_INDEX_REQUEST_BUNDLE_COUNT",
            applicability,
        )
    request = candidates[0]
    if request.get("schema") != RECEIPT_VECTOR_INDEX_REQUEST_SCHEMA:
        return _active_failure(
            "receipt_vector_indexing",
            "REJECT_RECEIPT_VECTOR_INDEX_REQUEST_SCHEMA",
            applicability,
        )
    try:
        if receipt_vector_index is None:
            from hhs_runtime.hhs_receipt_vector_index_v1 import HHSReceiptVectorIndex
            receipt_vector_index = HHSReceiptVectorIndex()
        if receipt_vector_receipt is None:
            raise ValueError("REJECT_RECEIPT_VECTOR_VALIDATED_RECEIPT_MISSING")
        if getattr(receipt_vector_receipt, "validation_passed", None) is not True:
            raise ValueError("REJECT_RECEIPT_VECTOR_UNVALIDATED_RECEIPT")

        receipt_hash72 = request.get("receipt_hash72")
        state_hash72 = request.get("state_hash72")
        witness_flags = request.get("witness_flags")
        route_trace = _exact_string_list(request.get("route_trace"), "RECEIPT_ROUTE_TRACE")
        expected_pre_root = request.get("expected_pre_index_root_hash216")
        if not isinstance(receipt_hash72, str) or len(receipt_hash72) != 72:
            raise ValueError("REJECT_RECEIPT_VECTOR_RECEIPT_HASH72_INVALID")
        if not isinstance(state_hash72, str) or len(state_hash72) != 72:
            raise ValueError("REJECT_RECEIPT_VECTOR_STATE_HASH72_INVALID")
        if not isinstance(witness_flags, int) or isinstance(witness_flags, bool) or witness_flags < 0:
            raise ValueError("REJECT_RECEIPT_VECTOR_WITNESS_FLAGS_INVALID")
        if not isinstance(expected_pre_root, str) or len(expected_pre_root) != 64:
            raise ValueError("REJECT_RECEIPT_VECTOR_PRE_INDEX_ROOT_INVALID")

        if receipt_hash72 != getattr(receipt_vector_receipt, "receipt_hash72", None):
            raise ValueError("REJECT_RECEIPT_VECTOR_RECEIPT_HASH_BINDING_MISMATCH")
        if state_hash72 != getattr(receipt_vector_receipt, "state_hash72", None):
            raise ValueError("REJECT_RECEIPT_VECTOR_STATE_HASH_BINDING_MISMATCH")
        if witness_flags != getattr(receipt_vector_receipt, "witness_flags", None):
            raise ValueError("REJECT_RECEIPT_VECTOR_WITNESS_BINDING_MISMATCH")
        if list(route_trace) != list(getattr(receipt_vector_receipt, "route_trace", []) or []):
            raise ValueError("REJECT_RECEIPT_VECTOR_ROUTE_BINDING_MISMATCH")

        before_root = receipt_vector_index.index_root_hash216()
        if before_root != expected_pre_root:
            raise ValueError("REJECT_RECEIPT_VECTOR_PRE_INDEX_ROOT_MISMATCH")
        for node in receipt_vector_index.nodes.values():
            _reject_float(node.vector)
            _reject_float(node.witness_flags)

        node = receipt_vector_index.insert_receipt(receipt_vector_receipt)
        located = receipt_vector_index.get_receipt_node(receipt_hash72)
        if located is not node:
            raise ValueError("REJECT_RECEIPT_VECTOR_EXACT_LOOKUP_MISMATCH")
        _reject_float(node.vector)
        _reject_float(node.timestamp)
        if not isinstance(node.timestamp, int) or isinstance(node.timestamp, bool):
            raise ValueError("REJECT_RECEIPT_VECTOR_TIMESTAMP_NOT_INTEGER_NS")
        if any(not isinstance(value, int) or isinstance(value, bool) for value in node.vector):
            raise ValueError("REJECT_RECEIPT_VECTOR_NONINTEGER_COORDINATE")
        if receipt_vector_index.vector_distance(node.vector, node.vector) != 0:
            raise ValueError("REJECT_RECEIPT_VECTOR_ZERO_DISTANCE_IDENTITY_FAILED")
        after_root = receipt_vector_index.index_root_hash216()

        info = CHECKPOINT10_AUTHORITY_MAP["receipt_vector_indexing"]
        return {
            "observed": True,
            "path": [
                "kernel_runtime_autocomposer",
                "receipt_vector_indexing",
                f"{info['module']}.{info['symbol']}",
            ],
            "traversal_witness": {
                "schema": "HHS_PASS217_RECEIPT_VECTOR_INDEX_TRAVERSAL_V1",
                "status": "ADMIT_RECEIPT_VECTOR_INDEX_TRAVERSAL",
                "repository_native_callable": dict(info),
                "receipt_hash72": node.receipt_hash72,
                "state_hash72": node.state_hash72,
                "witness_flags": node.witness_flags,
                "route_trace": list(node.route_trace),
                "vector_coordinate_count": len(node.vector),
                "numeric_authority": "EXACT_INTEGER_ONLY",
                "float_coordinates_present": False,
                "timestamp_integer_nanoseconds": True,
                "pre_index_root_hash216": before_root,
                "post_index_root_hash216": after_root,
                "exact_receipt_lookup_verified": True,
                "zero_self_distance_verified": True,
                "applicability_facts": applicability,
            },
            "witness_root": after_root,
        }
    except Exception as exc:
        return _active_failure(
            "receipt_vector_indexing",
            f"REJECT_RECEIPT_VECTOR_INDEX_TRAVERSAL:{type(exc).__name__}:{exc}",
            applicability,
        )


def observe_sql_context_graph(
    payload: Optional[Mapping[str, Any]],
    *,
    facts: Optional[Mapping[str, Any]] = None,
    sql_context_db: Any = None,
) -> Dict[str, Any]:
    applicability = dict(facts or checkpoint10_context_facts(payload))
    candidates = _sql_graph_candidates(payload)
    if len(candidates) != 1:
        return _active_failure(
            "sql_context_graph",
            "REJECT_SQL_CONTEXT_GRAPH_REQUEST_BUNDLE_COUNT",
            applicability,
        )
    request = candidates[0]
    if request.get("schema") != SQL_CONTEXT_GRAPH_REQUEST_SCHEMA:
        return _active_failure(
            "sql_context_graph",
            "REJECT_SQL_CONTEXT_GRAPH_REQUEST_SCHEMA",
            applicability,
        )
    try:
        if sql_context_db is None:
            raise ValueError("REJECT_SQL_CONTEXT_GRAPH_DATABASE_MISSING")
        object_id = request.get("object_id")
        expected_object_hash = request.get("expected_object_hash72")
        expected_database_root = request.get("expected_database_root_hash72")
        expected_relation_count = request.get("expected_relation_count")
        expected_relation_types = tuple(
            sorted(_exact_string_list(
                request.get("expected_relation_types", []),
                "SQL_EXPECTED_RELATION_TYPES",
                nonempty=False,
            ))
        )
        if not isinstance(object_id, str) or not object_id:
            raise ValueError("REJECT_SQL_CONTEXT_GRAPH_OBJECT_ID_INVALID")
        if not isinstance(expected_object_hash, str) or not expected_object_hash:
            raise ValueError("REJECT_SQL_CONTEXT_GRAPH_OBJECT_HASH_INVALID")
        if not isinstance(expected_database_root, str) or not expected_database_root:
            raise ValueError("REJECT_SQL_CONTEXT_GRAPH_DATABASE_ROOT_INVALID")
        if (
            not isinstance(expected_relation_count, int)
            or isinstance(expected_relation_count, bool)
            or expected_relation_count < 0
        ):
            raise ValueError("REJECT_SQL_CONTEXT_GRAPH_RELATION_COUNT_INVALID")

        before = sql_context_db.integrity_check()
        if before.get("ok") is not True:
            raise ValueError("REJECT_SQL_CONTEXT_GRAPH_DATABASE_INTEGRITY_FAILED")
        if before.get("database_root_hash72") != expected_database_root:
            raise ValueError("REJECT_SQL_CONTEXT_GRAPH_DATABASE_ROOT_MISMATCH")
        before_sequence = before.get("transaction_sequence")
        before_tip = before.get("receipt_tip")

        record = sql_context_db.get_object(object_id)
        if not isinstance(record, Mapping):
            raise ValueError("REJECT_SQL_CONTEXT_GRAPH_OBJECT_NOT_FOUND")
        if record.get("object_hash72") != expected_object_hash:
            raise ValueError("REJECT_SQL_CONTEXT_GRAPH_OBJECT_HASH_MISMATCH")
        relations = list(record.get("relations") or [])
        relation_types = tuple(sorted(str(rel.get("relation_type")) for rel in relations))
        if len(relations) != expected_relation_count:
            raise ValueError("REJECT_SQL_CONTEXT_GRAPH_RELATION_COUNT_MISMATCH")
        if relation_types != expected_relation_types:
            raise ValueError("REJECT_SQL_CONTEXT_GRAPH_RELATION_TYPES_MISMATCH")

        after = sql_context_db.integrity_check()
        if after.get("ok") is not True:
            raise ValueError("REJECT_SQL_CONTEXT_GRAPH_POST_READ_INTEGRITY_FAILED")
        if after.get("database_root_hash72") != expected_database_root:
            raise ValueError("REJECT_SQL_CONTEXT_GRAPH_READ_MUTATED_DATABASE_ROOT")
        if after.get("transaction_sequence") != before_sequence or after.get("receipt_tip") != before_tip:
            raise ValueError("REJECT_SQL_CONTEXT_GRAPH_READ_MUTATED_RECEIPT_STATE")

        info = CHECKPOINT10_AUTHORITY_MAP["sql_context_graph"]
        return {
            "observed": True,
            "path": [
                "kernel_runtime_autocomposer",
                "sql_context_graph",
                f"{info['module']}.{info['symbol']}",
            ],
            "traversal_witness": {
                "schema": "HHS_PASS217_SQL_CONTEXT_GRAPH_TRAVERSAL_V1",
                "status": "ADMIT_SQL_CONTEXT_GRAPH_TRAVERSAL",
                "repository_native_callable": dict(info),
                "object_id": object_id,
                "object_hash72": record.get("object_hash72"),
                "object_type": record.get("object_type"),
                "namespace": record.get("namespace"),
                "relation_count": len(relations),
                "relation_types": list(relation_types),
                "database_root_hash72": expected_database_root,
                "transaction_sequence": before_sequence,
                "receipt_tip": before_tip,
                "preflight_mutation_authority": False,
                "read_mutated_database": False,
                "integrity_verified_before_and_after": True,
                "applicability_facts": applicability,
            },
            "witness_root": expected_database_root,
        }
    except Exception as exc:
        return _active_failure(
            "sql_context_graph",
            f"REJECT_SQL_CONTEXT_GRAPH_TRAVERSAL:{type(exc).__name__}:{exc}",
            applicability,
        )


def _import_prior_decisions(
    record: Mapping[str, Any],
    active: Dict[str, Mapping[str, Any]],
    not_applicable: Dict[str, Mapping[str, Any]],
    superseded: Dict[str, Mapping[str, Any]],
) -> None:
    for row in record.get("decisions", []) or []:
        if not isinstance(row, Mapping):
            continue
        authority_id = str(row.get("authority_id") or "")
        proof = row.get("proof")
        if not authority_id or not isinstance(proof, Mapping):
            continue
        state = row.get("state")
        if state == ACTIVE_IN_PATH or "observed" in proof:
            active[authority_id] = dict(proof)
        elif state == NOT_APPLICABLE or "mechanically_proven" in proof:
            not_applicable[authority_id] = dict(proof)
        elif state == EXPLICITLY_SUPERSEDED or "later_pass" in proof:
            superseded[authority_id] = dict(proof)


def build_checkpoint10_inherited_authority_reachability(
    preflight: Mapping[str, Any],
    surface: Mapping[str, Any],
    payload: Optional[Mapping[str, Any]] = None,
    *,
    semantic_cache: Any = None,
    retrieval_runtime: Any = None,
    pattern_repo_root: Any = None,
    source_reuse_service: Any = None,
    projection_service: Any = None,
    delta_compiled_tensor: Any = None,
    parametric_template: Any = None,
    parametric_base_entry: Any = None,
    parametric_opening_boundary: Any = None,
    parametric_validation_key: Optional[bytes] = None,
    compiled_rom_store: Any = None,
    physical_recovery_runtime: Any = None,
    physical_protected_payload: Any = None,
    receipt_vector_index: Any = None,
    receipt_vector_receipt: Any = None,
    sql_context_db: Any = None,
) -> Dict[str, Any]:
    prior = build_checkpoint9_inherited_authority_reachability(
        preflight,
        surface,
        payload,
        semantic_cache=semantic_cache,
        retrieval_runtime=retrieval_runtime,
        pattern_repo_root=pattern_repo_root,
        source_reuse_service=source_reuse_service,
        projection_service=projection_service,
        delta_compiled_tensor=delta_compiled_tensor,
        parametric_template=parametric_template,
        parametric_base_entry=parametric_base_entry,
        parametric_opening_boundary=parametric_opening_boundary,
        parametric_validation_key=parametric_validation_key,
        compiled_rom_store=compiled_rom_store,
    )
    active: Dict[str, Mapping[str, Any]] = {}
    not_applicable: Dict[str, Mapping[str, Any]] = {}
    superseded: Dict[str, Mapping[str, Any]] = {}
    _import_prior_decisions(prior, active, not_applicable, superseded)
    facts = checkpoint10_context_facts(payload)

    if facts["physical_recovery_domain_present"] is False:
        not_applicable["physical_recovery"] = {
            "mechanically_proven": True,
            "predicate": "physical_recovery_domain_present == false",
            "observed_facts": facts,
            "reason": "operation contains no Pass 212 physical-erasure recovery domain",
        }
    else:
        active["physical_recovery"] = observe_physical_recovery(
            payload,
            facts=facts,
            physical_recovery_runtime=physical_recovery_runtime,
            physical_protected_payload=physical_protected_payload,
        )

    if facts["receipt_vector_indexing_domain_present"] is False:
        not_applicable["receipt_vector_indexing"] = {
            "mechanically_proven": True,
            "predicate": "receipt_vector_indexing_domain_present == false",
            "observed_facts": facts,
            "reason": "operation contains no validated receipt indexing domain",
        }
    else:
        active["receipt_vector_indexing"] = observe_receipt_vector_indexing(
            payload,
            facts=facts,
            receipt_vector_index=receipt_vector_index,
            receipt_vector_receipt=receipt_vector_receipt,
        )

    if facts["sql_context_graph_domain_present"] is False:
        not_applicable["sql_context_graph"] = {
            "mechanically_proven": True,
            "predicate": "sql_context_graph_domain_present == false",
            "observed_facts": facts,
            "reason": "operation contains no canonical SQL context-graph lookup domain",
        }
    else:
        active["sql_context_graph"] = observe_sql_context_graph(
            payload,
            facts=facts,
            sql_context_db=sql_context_db,
        )

    operation_id = str(preflight.get("operation") or surface.get("symbol") or "operation")
    record = build_authority_reachability(
        operation_id,
        active_in_path=active,
        not_applicable=not_applicable,
        explicitly_superseded=superseded,
        required_authorities=CHECKPOINT10_REQUIRED_AUTHORITIES,
    )
    record["checkpoint_scope"] = list(CHECKPOINT10_REQUIRED_AUTHORITIES)
    record["checkpoint10_authority_map"] = {
        key: dict(value) for key, value in CHECKPOINT10_AUTHORITY_MAP.items()
    }
    record["checkpoint10_applicability_facts"] = facts
    for key in (
        "continuation_applicability_facts",
        "pattern_cache_applicability_facts",
        "retrieval_reuse_applicability_facts",
        "checkpoint6_native_callable_map",
        "content_reuse_applicability_facts",
        "checkpoint7_authority_map",
        "checkpoint8_applicability_facts",
        "checkpoint8_authority_map",
        "checkpoint9_applicability_facts",
        "checkpoint9_authority_map",
    ):
        if key in prior:
            value = prior[key]
            record[key] = dict(value) if isinstance(value, Mapping) else value
    record["prior_checkpoint_reachability_root_hash72"] = prior.get(
        "reachability_root_hash72"
    )
    record["checkpoint"] = 10
    return record


__all__ = [
    "VERSION",
    "PHYSICAL_RECOVERY_REQUEST_SCHEMA",
    "RECEIPT_VECTOR_INDEX_REQUEST_SCHEMA",
    "SQL_CONTEXT_GRAPH_REQUEST_SCHEMA",
    "CHECKPOINT10_AUTHORITIES",
    "CHECKPOINT10_REQUIRED_AUTHORITIES",
    "CHECKPOINT10_AUTHORITY_MAP",
    "checkpoint10_context_facts",
    "observe_physical_recovery",
    "observe_receipt_vector_indexing",
    "observe_sql_context_graph",
    "build_checkpoint10_inherited_authority_reachability",
]

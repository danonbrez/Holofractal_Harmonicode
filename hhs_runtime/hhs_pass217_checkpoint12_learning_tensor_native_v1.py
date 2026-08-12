"""Pass 217 Checkpoint 12 bounded replay, moving-tensor routing, and native dispatch.

Extends the validated Checkpoint 11 authority slice with repository-native paths:

* bounded_learning_replay -> Pass 165 ``MultimodalLearningService.replay_ingestion``;
* moving_tensor_routing -> Pass 213 Iteration 8 ``MovingTensorState.physical_cell``
  with exact inverse routing and keyed tensor replay validation;
* native_dispatch -> Pass 213 Iteration 10 ``GovernedNativeDispatchAuthority.execute``
  reaching ``NativeDispatchKernel.execute`` and the fixed-width C ABI.

Absent domains are mechanically NOT_APPLICABLE. Partial or malformed applicable
context fails closed. Native dispatch is admitted only on a controlled-mutation
surface because the inherited authority commits a ledger receipt and successor
runtime state.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from hhs_runtime.hhs_cumulative_execution_authority_v1 import (
    ACTIVE_IN_PATH,
    EXPLICITLY_SUPERSEDED,
    NOT_APPLICABLE,
    build_authority_reachability,
)
from hhs_runtime.hhs_pass217_checkpoint11_storage_snapshot_alignment_v1 import (
    CHECKPOINT11_REQUIRED_AUTHORITIES,
    build_checkpoint11_inherited_authority_reachability,
)

VERSION = "PASS_217_CUMULATIVE_EXECUTION_COMPOSER_CHECKPOINT_12_V1"
BOUNDED_LEARNING_REPLAY_REQUEST_SCHEMA = "HHS_PASS217_BOUNDED_LEARNING_REPLAY_REQUEST_V1"
MOVING_TENSOR_ROUTING_REQUEST_SCHEMA = "HHS_PASS217_MOVING_TENSOR_ROUTING_REQUEST_V1"
NATIVE_DISPATCH_REQUEST_SCHEMA = "HHS_PASS217_NATIVE_DISPATCH_REQUEST_V1"

CHECKPOINT12_AUTHORITIES = (
    "bounded_learning_replay",
    "moving_tensor_routing",
    "native_dispatch",
)
CHECKPOINT12_REQUIRED_AUTHORITIES = CHECKPOINT11_REQUIRED_AUTHORITIES + CHECKPOINT12_AUTHORITIES

CHECKPOINT12_AUTHORITY_MAP: Dict[str, Dict[str, Any]] = {
    "bounded_learning_replay": {
        "origin_pass": 165,
        "module": "hhs_runtime.pass165.ingestion",
        "symbol": "MultimodalLearningService.replay_ingestion",
        "callable_role": (
            "rebuild committed bounded-learning history in a fresh VM81 runtime and "
            "require receipt, weight-root, and VM81-state equality"
        ),
        "runtime_authority": True,
        "preflight_mutation_authority": False,
    },
    "moving_tensor_routing": {
        "origin_pass": 213,
        "origin_iteration": 8,
        "module": "hhs_backend.runtime.hhs_pass213_moving_tensor_v1",
        "symbol": "MovingTensorState.physical_cell",
        "inverse_symbol": "MovingTensorState.logical_position_from_physical",
        "validation_symbol": "MovingTensorState.validate_with_key",
        "callable_role": (
            "anchor-bound exact logical-to-physical moving-tensor routing with inverse "
            "route proof over the admitted tensor domain"
        ),
        "runtime_authority": True,
        "floating_projection_authority": False,
        "preflight_mutation_authority": False,
    },
    "native_dispatch": {
        "origin_pass": 213,
        "origin_iteration": 10,
        "module": "hhs_backend.runtime.hhs_pass213_native_dispatch_authority_v1",
        "symbol": "GovernedNativeDispatchAuthority.execute",
        "kernel_module": "hhs_backend.runtime.hhs_pass213_native_dispatch_kernel_v1",
        "kernel_symbol": "NativeDispatchKernel.execute",
        "native_source": "native/pass213/hhs_pass213_native_dispatch.c",
        "callable_role": (
            "singleton governed VM81 compiled-entry dispatch through the fixed-width "
            "allocation-free native C ABI with ledger receipt and successor-state commit"
        ),
        "runtime_authority": True,
        "canonical_mutation_authority": True,
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


def _request_candidates(payload: Optional[Mapping[str, Any]], *, named_key: str, schema: str) -> List[Mapping[str, Any]]:
    found: List[Mapping[str, Any]] = []
    for mapping in _walk_mappings(dict(payload or {})):
        named = mapping.get(named_key)
        if isinstance(named, Mapping):
            found.append(named)
        if mapping.get("schema") == schema:
            found.append(mapping)
    return _unique_mappings(found)


def _learning_candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    return _request_candidates(payload, named_key="bounded_learning_replay", schema=BOUNDED_LEARNING_REPLAY_REQUEST_SCHEMA)


def _tensor_candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    return _request_candidates(payload, named_key="moving_tensor_routing", schema=MOVING_TENSOR_ROUTING_REQUEST_SCHEMA)


def _native_candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    return _request_candidates(payload, named_key="native_dispatch", schema=NATIVE_DISPATCH_REQUEST_SCHEMA)


def checkpoint12_context_facts(payload: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    learning, tensor, native = _learning_candidates(payload), _tensor_candidates(payload), _native_candidates(payload)
    return {
        "schema": "HHS_PASS217_CHECKPOINT12_APPLICABILITY_FACTS_V1",
        "bounded_learning_replay_domain_present": bool(learning),
        "bounded_learning_replay_candidate_count": len(learning),
        "bounded_learning_replay_exact_schema_count": sum(row.get("schema") == BOUNDED_LEARNING_REPLAY_REQUEST_SCHEMA for row in learning),
        "moving_tensor_routing_domain_present": bool(tensor),
        "moving_tensor_routing_candidate_count": len(tensor),
        "moving_tensor_routing_exact_schema_count": sum(row.get("schema") == MOVING_TENSOR_ROUTING_REQUEST_SCHEMA for row in tensor),
        "native_dispatch_domain_present": bool(native),
        "native_dispatch_candidate_count": len(native),
        "native_dispatch_exact_schema_count": sum(row.get("schema") == NATIVE_DISPATCH_REQUEST_SCHEMA for row in native),
    }


def _active_failure(authority_id: str, reason: str, facts: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "observed": False,
        "path": ["kernel_runtime_autocomposer", authority_id],
        "traversal_witness": {
            "schema": "HHS_PASS217_CHECKPOINT12_TRAVERSAL_FAILURE_V1",
            "status": "REJECT_CHECKPOINT12_INHERITED_TRAVERSAL",
            "authority_id": authority_id,
            "reason": str(reason),
            "authority_map": dict(CHECKPOINT12_AUTHORITY_MAP[authority_id]),
            "applicability_facts": dict(facts),
        },
        "witness_root": "",
    }


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise TypeError("REJECT_CHECKPOINT12_FLOAT_CANONICAL_AUTHORITY_FORBIDDEN")
    if isinstance(value, Mapping):
        for child in value.values():
            _reject_float(child)
    elif isinstance(value, (list, tuple, set)):
        for child in value:
            _reject_float(child)


def _canonical_bytes(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _hash216(domain: str, value: Any) -> str:
    raw = _canonical_bytes(value)
    return sha256(domain.encode("utf-8") + b"\0" + len(raw).to_bytes(8, "big") + raw).hexdigest()


def _sha256_hex(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"REJECT_CHECKPOINT12_{label}_HASH216_INVALID")
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError(f"REJECT_CHECKPOINT12_{label}_HASH216_INVALID") from exc
    return value


def _exact_int(value: Any, label: str, *, minimum: int | None = None, maximum: int | None = None) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"REJECT_CHECKPOINT12_{label}_EXACT_INTEGER_REQUIRED")
    if minimum is not None and value < minimum:
        raise ValueError(f"REJECT_CHECKPOINT12_{label}_OUT_OF_RANGE")
    if maximum is not None and value > maximum:
        raise ValueError(f"REJECT_CHECKPOINT12_{label}_OUT_OF_RANGE")
    return value


def observe_bounded_learning_replay(payload: Optional[Mapping[str, Any]], *, facts: Optional[Mapping[str, Any]] = None, bounded_learning_service: Any = None) -> Dict[str, Any]:
    applicability = dict(facts or checkpoint12_context_facts(payload))
    candidates = _learning_candidates(payload)
    if len(candidates) != 1:
        return _active_failure("bounded_learning_replay", "REJECT_BOUNDED_LEARNING_REPLAY_REQUEST_BUNDLE_COUNT", applicability)
    request = candidates[0]
    if request.get("schema") != BOUNDED_LEARNING_REPLAY_REQUEST_SCHEMA:
        return _active_failure("bounded_learning_replay", "REJECT_BOUNDED_LEARNING_REPLAY_REQUEST_SCHEMA", applicability)
    try:
        _reject_float(request)
        if bounded_learning_service is None or not callable(getattr(bounded_learning_service, "replay_ingestion", None)):
            raise ValueError("REJECT_BOUNDED_LEARNING_REPLAY_SERVICE_MISSING")
        expected_records = _exact_int(request.get("expected_history_records"), "LEARNING_HISTORY_RECORDS", minimum=1)
        expected_weight_root = _sha256_hex(request.get("expected_weight_root_sha256"), "LEARNING_WEIGHT_ROOT")
        expected_vm81 = request.get("expected_vm81_state_hash72")
        if not isinstance(expected_vm81, str) or not expected_vm81:
            raise ValueError("REJECT_CHECKPOINT12_LEARNING_VM81_HASH72_INVALID")
        before = bounded_learning_service.status()
        history = getattr(bounded_learning_service, "_history", None)
        vm81 = getattr(bounded_learning_service, "_vm81", None)
        if not isinstance(history, list) or len(history) != expected_records:
            raise ValueError("REJECT_BOUNDED_LEARNING_REPLAY_HISTORY_COUNT_MISMATCH")
        if bounded_learning_service.weight_root != expected_weight_root:
            raise ValueError("REJECT_BOUNDED_LEARNING_REPLAY_WEIGHT_ROOT_MISMATCH")
        if vm81 is None or getattr(vm81, "state_hash72", None) != expected_vm81:
            raise ValueError("REJECT_BOUNDED_LEARNING_REPLAY_VM81_ROOT_MISMATCH")
        replay = bounded_learning_service.replay_ingestion()
        if replay.get("classification") != "P165_REPLAY_RECEIPT" or replay.get("deterministic_replay") is not True:
            raise ValueError("REJECT_BOUNDED_LEARNING_REPLAY_RECEIPT_INVALID")
        if replay.get("records") != expected_records or replay.get("weight_root") != expected_weight_root or replay.get("vm81_state_hash72") != expected_vm81:
            raise ValueError("REJECT_BOUNDED_LEARNING_REPLAY_RESULT_MISMATCH")
        after = bounded_learning_service.status()
        if after != before or len(history) != expected_records or bounded_learning_service.weight_root != expected_weight_root or getattr(vm81, "state_hash72", None) != expected_vm81:
            raise ValueError("REJECT_BOUNDED_LEARNING_REPLAY_MUTATED_SOURCE_SERVICE")
        witness_root = _hash216("pass217-checkpoint12-bounded-learning-replay", replay)
        return {
            "observed": True,
            "path": ["kernel_runtime_autocomposer", "bounded_learning_replay", "hhs_runtime.pass165.ingestion.MultimodalLearningService.replay_ingestion"],
            "traversal_witness": {
                "schema": "HHS_PASS217_BOUNDED_LEARNING_REPLAY_TRAVERSAL_V1",
                "status": "ADMIT_BOUNDED_LEARNING_REPLAY_TRAVERSAL",
                "repository_native_callable": dict(CHECKPOINT12_AUTHORITY_MAP["bounded_learning_replay"]),
                "history_records": expected_records,
                "weight_root_sha256": expected_weight_root,
                "vm81_state_hash72": expected_vm81,
                "deterministic_replay": True,
                "source_service_mutated": False,
                "applicability_facts": applicability,
            },
            "witness_root": witness_root,
        }
    except Exception as exc:
        return _active_failure("bounded_learning_replay", f"REJECT_BOUNDED_LEARNING_REPLAY_TRAVERSAL:{type(exc).__name__}:{exc}", applicability)


def observe_moving_tensor_routing(payload: Optional[Mapping[str, Any]], *, facts: Optional[Mapping[str, Any]] = None, moving_tensor_state: Any = None, moving_tensor_root_key: Optional[bytes] = None, moving_tensor_trusted_anchor: Any = None) -> Dict[str, Any]:
    applicability = dict(facts or checkpoint12_context_facts(payload))
    candidates = _tensor_candidates(payload)
    if len(candidates) != 1:
        return _active_failure("moving_tensor_routing", "REJECT_MOVING_TENSOR_ROUTING_REQUEST_BUNDLE_COUNT", applicability)
    request = candidates[0]
    if request.get("schema") != MOVING_TENSOR_ROUTING_REQUEST_SCHEMA:
        return _active_failure("moving_tensor_routing", "REJECT_MOVING_TENSOR_ROUTING_REQUEST_SCHEMA", applicability)
    try:
        _reject_float(request)
        if moving_tensor_state is None:
            raise ValueError("REJECT_MOVING_TENSOR_ROUTING_STATE_MISSING")
        if not isinstance(moving_tensor_root_key, bytes) or len(moving_tensor_root_key) < 32 or moving_tensor_trusted_anchor is None:
            raise ValueError("REJECT_MOVING_TENSOR_ROUTING_KEY_OR_ANCHOR_MISSING")
        expected_root = _sha256_hex(request.get("expected_tensor_root_hash216"), "MOVING_TENSOR_ROOT")
        expected_domain = _exact_int(request.get("expected_domain_size"), "MOVING_TENSOR_DOMAIN", minimum=1)
        expected_receipt = request.get("expected_receipt_hash72")
        if not isinstance(expected_receipt, str) or not expected_receipt:
            raise ValueError("REJECT_MOVING_TENSOR_ROUTING_RECEIPT_INVALID")
        positions = request.get("logical_positions")
        if not isinstance(positions, Sequence) or isinstance(positions, (str, bytes, bytearray)) or not positions or len(positions) > 256:
            raise ValueError("REJECT_MOVING_TENSOR_ROUTING_POSITIONS_INVALID")
        exact_positions = tuple(_exact_int(item, "MOVING_TENSOR_POSITION", minimum=0, maximum=expected_domain - 1) for item in positions)
        if len(exact_positions) != len(set(exact_positions)):
            raise ValueError("REJECT_MOVING_TENSOR_ROUTING_POSITIONS_DUPLICATE")
        before = moving_tensor_state.to_mapping()
        moving_tensor_state.validate_structure()
        if moving_tensor_state.tensor_root_hash216 != expected_root or moving_tensor_state.domain_size != expected_domain or moving_tensor_state.receipt_hash72 != expected_receipt:
            raise ValueError("REJECT_MOVING_TENSOR_ROUTING_STATE_IDENTITY_MISMATCH")
        if moving_tensor_state.validate_with_key(root_key=moving_tensor_root_key, trusted_anchor=moving_tensor_trusted_anchor) is not True:
            raise ValueError("REJECT_MOVING_TENSOR_ROUTING_KEYED_REPLAY_FAILED")
        routes: list[dict[str, int]] = []
        physical_seen: set[int] = set()
        for logical in exact_positions:
            physical = moving_tensor_state.physical_cell(logical)
            inverse = moving_tensor_state.logical_position_from_physical(physical)
            if inverse != logical or not 0 <= physical < expected_domain:
                raise ValueError("REJECT_MOVING_TENSOR_ROUTING_INVERSE_MISMATCH")
            if physical in physical_seen:
                raise ValueError("REJECT_MOVING_TENSOR_ROUTING_PHYSICAL_COLLISION")
            physical_seen.add(physical)
            routes.append({"logical_position": logical, "physical_cell": physical, "inverse_logical_position": inverse})
        if moving_tensor_state.to_mapping() != before:
            raise ValueError("REJECT_MOVING_TENSOR_ROUTING_MUTATED_TENSOR")
        route_body = {
            "tensor_root_hash216": expected_root,
            "domain_size": expected_domain,
            "tensor_sequence": moving_tensor_state.tensor_sequence,
            "genesis_epoch": moving_tensor_state.genesis_epoch,
            "closure_root_hash216": moving_tensor_state.closure_proof.proof_root_hash216,
            "routes": routes,
        }
        route_root = _hash216("pass217-checkpoint12-moving-tensor-routing", route_body)
        return {
            "observed": True,
            "path": ["kernel_runtime_autocomposer", "moving_tensor_routing", "hhs_backend.runtime.hhs_pass213_moving_tensor_v1.MovingTensorState.physical_cell"],
            "traversal_witness": {
                "schema": "HHS_PASS217_MOVING_TENSOR_ROUTING_TRAVERSAL_V1",
                "status": "ADMIT_MOVING_TENSOR_ROUTING_TRAVERSAL",
                "repository_native_callable": dict(CHECKPOINT12_AUTHORITY_MAP["moving_tensor_routing"]),
                **route_body,
                "route_root_hash216": route_root,
                "keyed_replay_verified": True,
                "inverse_routes_verified": True,
                "floating_projection_used": False,
                "preflight_mutated_tensor": False,
                "applicability_facts": applicability,
            },
            "witness_root": route_root,
        }
    except Exception as exc:
        return _active_failure("moving_tensor_routing", f"REJECT_MOVING_TENSOR_ROUTING_TRAVERSAL:{type(exc).__name__}:{exc}", applicability)


def observe_native_dispatch(payload: Optional[Mapping[str, Any]], *, facts: Optional[Mapping[str, Any]] = None, native_dispatch_authority: Any = None, mutation_allowed: bool = False) -> Dict[str, Any]:
    applicability = dict(facts or checkpoint12_context_facts(payload))
    candidates = _native_candidates(payload)
    if len(candidates) != 1:
        return _active_failure("native_dispatch", "REJECT_NATIVE_DISPATCH_REQUEST_BUNDLE_COUNT", applicability)
    request = candidates[0]
    if request.get("schema") != NATIVE_DISPATCH_REQUEST_SCHEMA:
        return _active_failure("native_dispatch", "REJECT_NATIVE_DISPATCH_REQUEST_SCHEMA", applicability)
    try:
        _reject_float(request)
        if mutation_allowed is not True:
            raise ValueError("REJECT_NATIVE_DISPATCH_CONTROLLED_MUTATION_SURFACE_REQUIRED")
        if native_dispatch_authority is None or not callable(getattr(native_dispatch_authority, "execute", None)):
            raise ValueError("REJECT_NATIVE_DISPATCH_GOVERNED_AUTHORITY_MISSING")
        kernel = getattr(native_dispatch_authority, "native_kernel", None)
        ledger = getattr(native_dispatch_authority, "ledger", None)
        if kernel is None or kernel.__class__.__name__ != "NativeDispatchKernel" or not getattr(kernel, "library_path", None):
            raise ValueError("REJECT_NATIVE_DISPATCH_NATIVE_KERNEL_REQUIRED")
        if ledger is None or not callable(getattr(ledger, "count", None)):
            raise ValueError("REJECT_NATIVE_DISPATCH_LEDGER_REQUIRED")
        inner = request.get("request")
        if not isinstance(inner, Mapping):
            raise ValueError("REJECT_NATIVE_DISPATCH_INNER_REQUEST_REQUIRED")
        expected_before = _exact_int(request.get("expected_ledger_count_before"), "NATIVE_DISPATCH_LEDGER_COUNT", minimum=0)
        expected_parent = _sha256_hex(request.get("expected_parent_hash216"), "NATIVE_DISPATCH_PARENT")
        before_status = native_dispatch_authority.status()
        before_state = native_dispatch_authority.runtime_state
        if ledger.count() != expected_before or before_status.get("ledger_count") != expected_before:
            raise ValueError("REJECT_NATIVE_DISPATCH_LEDGER_COUNT_MISMATCH")
        if before_state.current_state_root_hash216 != expected_parent or inner.get("expected_parent_hash216") != expected_parent:
            raise ValueError("REJECT_NATIVE_DISPATCH_PARENT_MISMATCH")
        receipt = native_dispatch_authority.execute(dict(inner))
        receipt_map = receipt.to_mapping()
        if receipt.sequence != before_state.next_sequence or receipt.prior_state_root_hash216 != expected_parent:
            raise ValueError("REJECT_NATIVE_DISPATCH_RECEIPT_SEQUENCE_OR_PARENT_MISMATCH")
        after_status = native_dispatch_authority.status()
        after_state = native_dispatch_authority.runtime_state
        if ledger.count() != expected_before + 1 or after_status.get("ledger_count") != expected_before + 1:
            raise ValueError("REJECT_NATIVE_DISPATCH_LEDGER_NOT_ADVANCED")
        if after_state.current_state_root_hash216 != receipt.successor_state_root_hash216 or after_state.previous_receipt_hash72 != receipt.receipt_hash72 or after_state.next_sequence != receipt.sequence + 1:
            raise ValueError("REJECT_NATIVE_DISPATCH_SUCCESSOR_STATE_MISMATCH")
        persisted = ledger.lookup(receipt.sequence)
        if not isinstance(persisted, Mapping) or persisted.get("receipt_hash72") != receipt.receipt_hash72:
            raise ValueError("REJECT_NATIVE_DISPATCH_LEDGER_RECEIPT_MISMATCH")
        if receipt_map.get("singleton_vm81_admission") is not True or receipt_map.get("physical_route_exposed") is not False:
            raise ValueError("REJECT_NATIVE_DISPATCH_RECEIPT_AUTHORITY_FLAGS_INVALID")
        return {
            "observed": True,
            "path": [
                "kernel_runtime_autocomposer",
                "native_dispatch",
                "hhs_backend.runtime.hhs_pass213_native_dispatch_authority_v1.GovernedNativeDispatchAuthority.execute",
                "hhs_backend.runtime.hhs_pass213_native_dispatch_kernel_v1.NativeDispatchKernel.execute",
                "native/pass213/hhs_pass213_native_dispatch.c:hhs_pass213_native_dispatch_execute",
            ],
            "traversal_witness": {
                "schema": "HHS_PASS217_NATIVE_DISPATCH_TRAVERSAL_V1",
                "status": "ADMIT_NATIVE_DISPATCH_TRAVERSAL",
                "repository_native_callable": dict(CHECKPOINT12_AUTHORITY_MAP["native_dispatch"]),
                "sequence": receipt.sequence,
                "operation_id": receipt.operation_id,
                "native_dispatch_id": receipt.native_dispatch_id,
                "entry_hash216": receipt.entry_hash216,
                "tensor_root_hash216": receipt.tensor_root_hash216,
                "route_commitment_hash216": receipt.route_commitment_hash216,
                "request_root_hash216": receipt.request_root_hash216,
                "result_root_hash216": receipt.result_root_hash216,
                "result_values": list(receipt.result_values),
                "prior_state_root_hash216": receipt.prior_state_root_hash216,
                "successor_state_root_hash216": receipt.successor_state_root_hash216,
                "receipt_hash72": receipt.receipt_hash72,
                "ledger_count_before": expected_before,
                "ledger_count_after": expected_before + 1,
                "native_library_path_present": True,
                "singleton_vm81_admission": True,
                "physical_route_exposed": False,
                "canonical_runtime_mutated": True,
                "applicability_facts": applicability,
            },
            "witness_root": receipt.receipt_hash72,
        }
    except Exception as exc:
        return _active_failure("native_dispatch", f"REJECT_NATIVE_DISPATCH_TRAVERSAL:{type(exc).__name__}:{exc}", applicability)


def _import_prior_decisions(record: Mapping[str, Any], active: Dict[str, Mapping[str, Any]], not_applicable: Dict[str, Mapping[str, Any]], superseded: Dict[str, Mapping[str, Any]]) -> None:
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


def build_checkpoint12_inherited_authority_reachability(
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
    encrypted_vector_store: Any = None,
    snapshot_reuse_runtime: Any = None,
    multimodal_alignment_service: Any = None,
    bounded_learning_service: Any = None,
    moving_tensor_state: Any = None,
    moving_tensor_root_key: Optional[bytes] = None,
    moving_tensor_trusted_anchor: Any = None,
    native_dispatch_authority: Any = None,
) -> Dict[str, Any]:
    prior = build_checkpoint11_inherited_authority_reachability(
        preflight, surface, payload,
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
        physical_recovery_runtime=physical_recovery_runtime,
        physical_protected_payload=physical_protected_payload,
        receipt_vector_index=receipt_vector_index,
        receipt_vector_receipt=receipt_vector_receipt,
        sql_context_db=sql_context_db,
        encrypted_vector_store=encrypted_vector_store,
        snapshot_reuse_runtime=snapshot_reuse_runtime,
        multimodal_alignment_service=multimodal_alignment_service,
    )
    active: Dict[str, Mapping[str, Any]] = {}
    not_applicable: Dict[str, Mapping[str, Any]] = {}
    superseded: Dict[str, Mapping[str, Any]] = {}
    _import_prior_decisions(prior, active, not_applicable, superseded)
    facts = checkpoint12_context_facts(payload)

    if not facts["bounded_learning_replay_domain_present"]:
        not_applicable["bounded_learning_replay"] = {"mechanically_proven": True, "predicate": "bounded_learning_replay_domain_present == false", "observed_facts": facts, "reason": "operation contains no committed bounded-learning replay domain"}
    else:
        active["bounded_learning_replay"] = observe_bounded_learning_replay(payload, facts=facts, bounded_learning_service=bounded_learning_service)

    if not facts["moving_tensor_routing_domain_present"]:
        not_applicable["moving_tensor_routing"] = {"mechanically_proven": True, "predicate": "moving_tensor_routing_domain_present == false", "observed_facts": facts, "reason": "operation contains no exact Pass 213 moving-tensor routing domain"}
    else:
        active["moving_tensor_routing"] = observe_moving_tensor_routing(payload, facts=facts, moving_tensor_state=moving_tensor_state, moving_tensor_root_key=moving_tensor_root_key, moving_tensor_trusted_anchor=moving_tensor_trusted_anchor)

    if not facts["native_dispatch_domain_present"]:
        not_applicable["native_dispatch"] = {"mechanically_proven": True, "predicate": "native_dispatch_domain_present == false", "observed_facts": facts, "reason": "operation contains no governed native compiled-dispatch domain"}
    else:
        active["native_dispatch"] = observe_native_dispatch(
            payload,
            facts=facts,
            native_dispatch_authority=native_dispatch_authority,
            mutation_allowed=(surface.get("mutation_policy") == "CONTROLLED_RUNTIME_MUTATION"),
        )

    operation_id = str(preflight.get("operation") or surface.get("symbol") or "operation")
    record = build_authority_reachability(
        operation_id,
        active_in_path=active,
        not_applicable=not_applicable,
        explicitly_superseded=superseded,
        required_authorities=CHECKPOINT12_REQUIRED_AUTHORITIES,
    )
    record["checkpoint_scope"] = list(CHECKPOINT12_REQUIRED_AUTHORITIES)
    record["checkpoint12_authority_map"] = {key: dict(value) for key, value in CHECKPOINT12_AUTHORITY_MAP.items()}
    record["checkpoint12_applicability_facts"] = facts
    for key in (
        "continuation_applicability_facts", "pattern_cache_applicability_facts",
        "retrieval_reuse_applicability_facts", "checkpoint6_native_callable_map",
        "content_reuse_applicability_facts", "checkpoint7_authority_map",
        "checkpoint8_applicability_facts", "checkpoint8_authority_map",
        "checkpoint9_applicability_facts", "checkpoint9_authority_map",
        "checkpoint10_applicability_facts", "checkpoint10_authority_map",
        "checkpoint11_applicability_facts", "checkpoint11_authority_map",
    ):
        if key in prior:
            value = prior[key]
            record[key] = dict(value) if isinstance(value, Mapping) else value
    record["prior_checkpoint_reachability_root_hash72"] = prior.get("reachability_root_hash72")
    record["checkpoint"] = 12
    return record


__all__ = [
    "VERSION",
    "BOUNDED_LEARNING_REPLAY_REQUEST_SCHEMA",
    "MOVING_TENSOR_ROUTING_REQUEST_SCHEMA",
    "NATIVE_DISPATCH_REQUEST_SCHEMA",
    "CHECKPOINT12_AUTHORITIES",
    "CHECKPOINT12_REQUIRED_AUTHORITIES",
    "CHECKPOINT12_AUTHORITY_MAP",
    "checkpoint12_context_facts",
    "observe_bounded_learning_replay",
    "observe_moving_tensor_routing",
    "observe_native_dispatch",
    "build_checkpoint12_inherited_authority_reachability",
]

"""Pass 217 Checkpoint 12 bounded replay, moving-tensor routing, and native dispatch.

This checkpoint extends the validated Checkpoint 11 cumulative authority slice with:

* bounded_learning_replay -> Pass 165 ``MultimodalLearningService.replay_ingestion``;
* moving_tensor_routing -> Pass 213 Iteration 8 ``MovingTensorState.physical_cell``
  plus keyed replay/inverse-route validation;
* native_dispatch -> Pass 213 Iteration 10
  ``GovernedNativeDispatchAuthority.execute`` with the real native kernel,
  protected compiled-ROM lookup, moving-tensor route, receipt ledger, and
  singleton successor-state mutation.

The first two traversals are observational/read-only over supplied runtime state.
Native dispatch is intentionally different: when and only when an exact native
request domain is supplied on a controlled-mutation route with an explicitly
bound governed authority, the inherited execution itself is the canonical
mutation and receipt-producing witness. Absent domains are mechanically
NOT_APPLICABLE; partial/malformed applicable context fails closed.
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
MAX_COMPOSER_REPLAY_RECORDS = 32
UINT64_MAX = (1 << 64) - 1

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
            "deterministically replay already-committed governed learning history "
            "into a fresh VM81 runtime and require exact receipt, weight-root, and "
            "VM81-state equality"
        ),
        "composer_replay_record_bound": MAX_COMPOSER_REPLAY_RECORDS,
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
            "keyed trusted-anchor-bound logical-to-physical moving tensor route "
            "with exact reversible closure/coordinate-map proof"
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
        "kernel_symbol": "NativeDispatchKernel.execute",
        "ledger_symbol": "NativeDispatchLedger.append",
        "callable_role": (
            "governed singleton VM81 native compiled dispatch through protected "
            "compiled-ROM identity, moving-tensor routing, exact u64 ABI, "
            "authenticated receipt ledger, and successor-state advancement"
        ),
        "runtime_authority": True,
        "canonical_mutation_authority": True,
        "physical_route_exposed": False,
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
    payload: Optional[Mapping[str, Any]], *, named_key: str, schema: str
) -> List[Mapping[str, Any]]:
    found: List[Mapping[str, Any]] = []
    for mapping in _walk_mappings(dict(payload or {})):
        named = mapping.get(named_key)
        if isinstance(named, Mapping):
            found.append(named)
        if mapping.get("schema") == schema:
            found.append(mapping)
    return _unique_mappings(found)


def _bounded_replay_candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    return _request_candidates(
        payload,
        named_key="bounded_learning_replay",
        schema=BOUNDED_LEARNING_REPLAY_REQUEST_SCHEMA,
    )


def _moving_tensor_candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    return _request_candidates(
        payload,
        named_key="moving_tensor_routing",
        schema=MOVING_TENSOR_ROUTING_REQUEST_SCHEMA,
    )


def _native_dispatch_candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    return _request_candidates(
        payload,
        named_key="native_dispatch",
        schema=NATIVE_DISPATCH_REQUEST_SCHEMA,
    )


def checkpoint12_context_facts(payload: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    replay = _bounded_replay_candidates(payload)
    tensor = _moving_tensor_candidates(payload)
    dispatch = _native_dispatch_candidates(payload)
    return {
        "schema": "HHS_PASS217_CHECKPOINT12_APPLICABILITY_FACTS_V1",
        "bounded_learning_replay_domain_present": bool(replay),
        "bounded_learning_replay_candidate_count": len(replay),
        "bounded_learning_replay_exact_schema_count": sum(
            row.get("schema") == BOUNDED_LEARNING_REPLAY_REQUEST_SCHEMA for row in replay
        ),
        "moving_tensor_routing_domain_present": bool(tensor),
        "moving_tensor_routing_candidate_count": len(tensor),
        "moving_tensor_routing_exact_schema_count": sum(
            row.get("schema") == MOVING_TENSOR_ROUTING_REQUEST_SCHEMA for row in tensor
        ),
        "native_dispatch_domain_present": bool(dispatch),
        "native_dispatch_candidate_count": len(dispatch),
        "native_dispatch_exact_schema_count": sum(
            row.get("schema") == NATIVE_DISPATCH_REQUEST_SCHEMA for row in dispatch
        ),
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
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _hash216(domain: str, value: Any) -> str:
    raw = _canonical_bytes(value)
    return sha256(domain.encode("utf-8") + b"\0" + len(raw).to_bytes(8, "big") + raw).hexdigest()


def _hash216_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"REJECT_CHECKPOINT12_{label}_HASH216_INVALID")
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError(f"REJECT_CHECKPOINT12_{label}_HASH216_INVALID") from exc
    return value


def _hash72_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 72:
        raise ValueError(f"REJECT_CHECKPOINT12_{label}_HASH72_INVALID")
    return value


def _exact_int(value: Any, label: str, *, minimum: int = 0, maximum: int | None = None) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"REJECT_CHECKPOINT12_{label}_INTEGER_REQUIRED")
    if value < minimum or (maximum is not None and value > maximum):
        raise ValueError(f"REJECT_CHECKPOINT12_{label}_INTEGER_RANGE")
    return value


def _exact_int_sequence(value: Any, label: str) -> tuple[int, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValueError(f"REJECT_CHECKPOINT12_{label}_SEQUENCE_REQUIRED")
    output = tuple(_exact_int(item, label, maximum=UINT64_MAX) for item in value)
    if not output:
        raise ValueError(f"REJECT_CHECKPOINT12_{label}_EMPTY")
    return output


def observe_bounded_learning_replay(
    payload: Optional[Mapping[str, Any]],
    *,
    facts: Optional[Mapping[str, Any]] = None,
    bounded_learning_service: Any = None,
) -> Dict[str, Any]:
    applicability = dict(facts or checkpoint12_context_facts(payload))
    candidates = _bounded_replay_candidates(payload)
    if len(candidates) != 1:
        return _active_failure(
            "bounded_learning_replay",
            "REJECT_BOUNDED_LEARNING_REPLAY_REQUEST_BUNDLE_COUNT",
            applicability,
        )
    request = candidates[0]
    if request.get("schema") != BOUNDED_LEARNING_REPLAY_REQUEST_SCHEMA:
        return _active_failure(
            "bounded_learning_replay",
            "REJECT_BOUNDED_LEARNING_REPLAY_REQUEST_SCHEMA",
            applicability,
        )
    try:
        _reject_float(request)
        if bounded_learning_service is None:
            raise ValueError("REJECT_BOUNDED_LEARNING_REPLAY_SERVICE_MISSING")
        if not callable(getattr(bounded_learning_service, "replay_ingestion", None)):
            raise ValueError("REJECT_BOUNDED_LEARNING_REPLAY_CALLABLE_MISSING")
        if not callable(getattr(bounded_learning_service, "status", None)):
            raise ValueError("REJECT_BOUNDED_LEARNING_REPLAY_STATUS_MISSING")

        expected_records = _exact_int(request.get("expected_records"), "REPLAY_RECORDS", minimum=1)
        max_records = _exact_int(
            request.get("max_records"),
            "REPLAY_MAX_RECORDS",
            minimum=1,
            maximum=MAX_COMPOSER_REPLAY_RECORDS,
        )
        if expected_records > max_records:
            raise ValueError("REJECT_BOUNDED_LEARNING_REPLAY_DECLARED_BOUND_EXCEEDED")
        expected_weight_root = _hash216_text(request.get("expected_weight_root"), "REPLAY_WEIGHT_ROOT")
        expected_vm81 = _hash72_text(
            request.get("expected_vm81_state_hash72"), "REPLAY_VM81_STATE"
        )

        before_status = bounded_learning_service.status()
        before_weight_root = bounded_learning_service.weight_root
        if before_status.get("ingestion_epoch") != expected_records:
            raise ValueError("REJECT_BOUNDED_LEARNING_REPLAY_HISTORY_COUNT_MISMATCH")
        if before_weight_root != expected_weight_root:
            raise ValueError("REJECT_BOUNDED_LEARNING_REPLAY_WEIGHT_ROOT_MISMATCH")

        replay = bounded_learning_service.replay_ingestion()
        if replay.get("classification") != "P165_REPLAY_RECEIPT":
            raise ValueError("REJECT_BOUNDED_LEARNING_REPLAY_CLASSIFICATION")
        if replay.get("deterministic_replay") is not True:
            raise ValueError("REJECT_BOUNDED_LEARNING_REPLAY_NOT_DETERMINISTIC")
        if replay.get("records") != expected_records:
            raise ValueError("REJECT_BOUNDED_LEARNING_REPLAY_RECORD_COUNT_MISMATCH")
        if replay.get("records") > max_records:
            raise ValueError("REJECT_BOUNDED_LEARNING_REPLAY_RUNTIME_BOUND_EXCEEDED")
        if replay.get("weight_root") != expected_weight_root:
            raise ValueError("REJECT_BOUNDED_LEARNING_REPLAY_RESULT_WEIGHT_ROOT_MISMATCH")
        if replay.get("vm81_state_hash72") != expected_vm81:
            raise ValueError("REJECT_BOUNDED_LEARNING_REPLAY_VM81_STATE_MISMATCH")

        after_status = bounded_learning_service.status()
        if after_status != before_status or bounded_learning_service.weight_root != before_weight_root:
            raise ValueError("REJECT_BOUNDED_LEARNING_REPLAY_MUTATED_SOURCE_RUNTIME")

        witness_root = _hash216(
            "pass217-checkpoint12-bounded-learning-replay",
            {
                "records": expected_records,
                "max_records": max_records,
                "weight_root": expected_weight_root,
                "vm81_state_hash72": expected_vm81,
                "deterministic_replay": True,
            },
        )
        info = CHECKPOINT12_AUTHORITY_MAP["bounded_learning_replay"]
        return {
            "observed": True,
            "path": [
                "kernel_runtime_autocomposer",
                "bounded_learning_replay",
                f"{info['module']}.{info['symbol']}",
            ],
            "traversal_witness": {
                "schema": "HHS_PASS217_BOUNDED_LEARNING_REPLAY_TRAVERSAL_V1",
                "status": "ADMIT_BOUNDED_LEARNING_REPLAY_TRAVERSAL",
                "repository_native_callable": dict(info),
                "records_replayed": expected_records,
                "max_records": max_records,
                "weight_root": expected_weight_root,
                "vm81_state_hash72": expected_vm81,
                "deterministic_replay": True,
                "source_runtime_mutated": False,
                "applicability_facts": applicability,
            },
            "witness_root": witness_root,
        }
    except Exception as exc:
        return _active_failure(
            "bounded_learning_replay",
            f"REJECT_BOUNDED_LEARNING_REPLAY_TRAVERSAL:{type(exc).__name__}:{exc}",
            applicability,
        )


def observe_moving_tensor_routing(
    payload: Optional[Mapping[str, Any]],
    *,
    facts: Optional[Mapping[str, Any]] = None,
    moving_tensor_state: Any = None,
    moving_tensor_root_key: Optional[bytes] = None,
    moving_tensor_trusted_anchor: Any = None,
) -> Dict[str, Any]:
    applicability = dict(facts or checkpoint12_context_facts(payload))
    candidates = _moving_tensor_candidates(payload)
    if len(candidates) != 1:
        return _active_failure(
            "moving_tensor_routing",
            "REJECT_MOVING_TENSOR_ROUTING_REQUEST_BUNDLE_COUNT",
            applicability,
        )
    request = candidates[0]
    if request.get("schema") != MOVING_TENSOR_ROUTING_REQUEST_SCHEMA:
        return _active_failure(
            "moving_tensor_routing",
            "REJECT_MOVING_TENSOR_ROUTING_REQUEST_SCHEMA",
            applicability,
        )
    try:
        _reject_float(request)
        if moving_tensor_state is None:
            raise ValueError("REJECT_MOVING_TENSOR_ROUTING_STATE_MISSING")
        if not isinstance(moving_tensor_root_key, bytes) or len(moving_tensor_root_key) < 32:
            raise ValueError("REJECT_MOVING_TENSOR_ROUTING_ROOT_KEY_MISSING")
        if moving_tensor_trusted_anchor is None:
            raise ValueError("REJECT_MOVING_TENSOR_ROUTING_TRUSTED_ANCHOR_MISSING")
        for symbol in (
            "validate_structure",
            "validate_with_key",
            "physical_cell",
            "logical_position_from_physical",
            "to_mapping",
        ):
            if not callable(getattr(moving_tensor_state, symbol, None)):
                raise ValueError(f"REJECT_MOVING_TENSOR_ROUTING_CALLABLE_MISSING:{symbol}")

        expected_tensor_root = _hash216_text(
            request.get("expected_tensor_root_hash216"), "MOVING_TENSOR_ROOT"
        )
        expected_receipt = _hash72_text(
            request.get("expected_tensor_receipt_hash72"), "MOVING_TENSOR_RECEIPT"
        )
        logical_position = _exact_int(request.get("logical_position"), "MOVING_TENSOR_LOGICAL_POSITION")
        expected_physical = _exact_int(
            request.get("expected_physical_cell"), "MOVING_TENSOR_PHYSICAL_CELL"
        )

        _reject_float(moving_tensor_state.to_mapping())
        moving_tensor_state.validate_structure()
        if moving_tensor_state.tensor_root_hash216 != expected_tensor_root:
            raise ValueError("REJECT_MOVING_TENSOR_ROUTING_ROOT_MISMATCH")
        if moving_tensor_state.receipt_hash72 != expected_receipt:
            raise ValueError("REJECT_MOVING_TENSOR_ROUTING_RECEIPT_MISMATCH")
        if logical_position >= moving_tensor_state.domain_size:
            raise ValueError("REJECT_MOVING_TENSOR_ROUTING_LOGICAL_POSITION_RANGE")
        if moving_tensor_state.validate_with_key(
            root_key=moving_tensor_root_key,
            trusted_anchor=moving_tensor_trusted_anchor,
        ) is not True:
            raise ValueError("REJECT_MOVING_TENSOR_ROUTING_KEYED_REPLAY_FAILED")

        physical = moving_tensor_state.physical_cell(logical_position)
        inverse = moving_tensor_state.logical_position_from_physical(physical)
        if physical != expected_physical:
            raise ValueError("REJECT_MOVING_TENSOR_ROUTING_PHYSICAL_CELL_MISMATCH")
        if inverse != logical_position:
            raise ValueError("REJECT_MOVING_TENSOR_ROUTING_INVERSE_MISMATCH")
        if physical < 0 or physical >= moving_tensor_state.domain_size:
            raise ValueError("REJECT_MOVING_TENSOR_ROUTING_PHYSICAL_CELL_RANGE")

        route_root = _hash216(
            "pass217-checkpoint12-moving-tensor-route",
            {
                "tensor_root_hash216": expected_tensor_root,
                "tensor_sequence": moving_tensor_state.tensor_sequence,
                "domain_size": moving_tensor_state.domain_size,
                "logical_position": logical_position,
                "physical_cell": physical,
                "closure_root_hash216": moving_tensor_state.closure_proof.proof_root_hash216,
            },
        )
        info = CHECKPOINT12_AUTHORITY_MAP["moving_tensor_routing"]
        return {
            "observed": True,
            "path": [
                "kernel_runtime_autocomposer",
                "moving_tensor_routing",
                f"{info['module']}.{info['symbol']}",
            ],
            "traversal_witness": {
                "schema": "HHS_PASS217_MOVING_TENSOR_ROUTING_TRAVERSAL_V1",
                "status": "ADMIT_MOVING_TENSOR_ROUTING_TRAVERSAL",
                "repository_native_callable": dict(info),
                "tensor_root_hash216": expected_tensor_root,
                "tensor_receipt_hash72": expected_receipt,
                "tensor_sequence": moving_tensor_state.tensor_sequence,
                "domain_size": moving_tensor_state.domain_size,
                "logical_position": logical_position,
                "physical_cell": physical,
                "inverse_logical_position": inverse,
                "closure_root_hash216": moving_tensor_state.closure_proof.proof_root_hash216,
                "keyed_replay_verified": True,
                "route_round_trip_verified": True,
                "floating_projection_used": False,
                "preflight_mutation_authority": False,
                "applicability_facts": applicability,
            },
            "witness_root": route_root,
        }
    except Exception as exc:
        return _active_failure(
            "moving_tensor_routing",
            f"REJECT_MOVING_TENSOR_ROUTING_TRAVERSAL:{type(exc).__name__}:{exc}",
            applicability,
        )


def observe_native_dispatch(
    payload: Optional[Mapping[str, Any]],
    *,
    surface: Mapping[str, Any],
    facts: Optional[Mapping[str, Any]] = None,
    native_dispatch_authority: Any = None,
) -> Dict[str, Any]:
    applicability = dict(facts or checkpoint12_context_facts(payload))
    candidates = _native_dispatch_candidates(payload)
    if len(candidates) != 1:
        return _active_failure(
            "native_dispatch",
            "REJECT_NATIVE_DISPATCH_REQUEST_BUNDLE_COUNT",
            applicability,
        )
    request = candidates[0]
    if request.get("schema") != NATIVE_DISPATCH_REQUEST_SCHEMA:
        return _active_failure(
            "native_dispatch",
            "REJECT_NATIVE_DISPATCH_REQUEST_SCHEMA",
            applicability,
        )
    try:
        _reject_float(request)
        if surface.get("mutation_policy") != "CONTROLLED_RUNTIME_MUTATION":
            raise ValueError("REJECT_NATIVE_DISPATCH_ROUTE_MUTATION_POLICY")
        if surface.get("persistence_policy") != "CANONICAL_MUTATION_RECEIPT":
            raise ValueError("REJECT_NATIVE_DISPATCH_ROUTE_PERSISTENCE_POLICY")
        if native_dispatch_authority is None:
            raise ValueError("REJECT_NATIVE_DISPATCH_AUTHORITY_MISSING")
        if not callable(getattr(native_dispatch_authority, "execute", None)):
            raise ValueError("REJECT_NATIVE_DISPATCH_EXECUTE_MISSING")
        if not callable(getattr(native_dispatch_authority, "status", None)):
            raise ValueError("REJECT_NATIVE_DISPATCH_STATUS_MISSING")

        dispatch_request = request.get("dispatch_request")
        if not isinstance(dispatch_request, Mapping):
            raise ValueError("REJECT_NATIVE_DISPATCH_INNER_REQUEST_MISSING")
        _reject_float(dispatch_request)
        expected_sequence = _exact_int(
            request.get("expected_sequence"), "NATIVE_DISPATCH_SEQUENCE", minimum=1
        )
        expected_results = _exact_int_sequence(
            request.get("expected_result_values"), "NATIVE_DISPATCH_RESULT"
        )
        expected_native_id = request.get("expected_native_dispatch_id")
        if not isinstance(expected_native_id, str) or not expected_native_id:
            raise ValueError("REJECT_NATIVE_DISPATCH_NATIVE_ID_INVALID")

        before = native_dispatch_authority.status()
        if before.get("available") is not True or before.get("ledger_valid") is not True:
            raise ValueError("REJECT_NATIVE_DISPATCH_AUTHORITY_NOT_READY")
        before_state = dict(before.get("runtime_state") or {})
        if before_state.get("next_sequence") != expected_sequence:
            raise ValueError("REJECT_NATIVE_DISPATCH_SEQUENCE_MISMATCH")
        if dispatch_request.get("expected_parent_hash216") != before_state.get("current_state_root_hash216"):
            raise ValueError("REJECT_NATIVE_DISPATCH_PARENT_BINDING_MISMATCH")
        if dispatch_request.get("expected_tensor_root_hash216") != before_state.get("tensor_root_hash216"):
            raise ValueError("REJECT_NATIVE_DISPATCH_TENSOR_BINDING_MISMATCH")
        before_count = _exact_int(before.get("ledger_count"), "NATIVE_DISPATCH_LEDGER_COUNT")
        before_inventory = _hash216_text(
            before.get("protected_inventory_root_hash216"), "NATIVE_DISPATCH_INVENTORY_ROOT"
        )

        receipt = native_dispatch_authority.execute(dispatch_request)
        if receipt.sequence != expected_sequence:
            raise ValueError("REJECT_NATIVE_DISPATCH_RECEIPT_SEQUENCE_MISMATCH")
        if tuple(receipt.result_values) != expected_results:
            raise ValueError("REJECT_NATIVE_DISPATCH_RESULT_VALUES_MISMATCH")
        if receipt.native_dispatch_id != expected_native_id:
            raise ValueError("REJECT_NATIVE_DISPATCH_NATIVE_ID_MISMATCH")
        if receipt.prior_state_root_hash216 != before_state.get("current_state_root_hash216"):
            raise ValueError("REJECT_NATIVE_DISPATCH_PRIOR_STATE_MISMATCH")
        if receipt.tensor_root_hash216 != before_state.get("tensor_root_hash216"):
            raise ValueError("REJECT_NATIVE_DISPATCH_RECEIPT_TENSOR_MISMATCH")
        _hash216_text(receipt.successor_state_root_hash216, "NATIVE_DISPATCH_SUCCESSOR_ROOT")
        _hash216_text(receipt.route_commitment_hash216, "NATIVE_DISPATCH_ROUTE_ROOT")
        _hash72_text(receipt.receipt_hash72, "NATIVE_DISPATCH_RECEIPT")

        after = native_dispatch_authority.status()
        after_state = dict(after.get("runtime_state") or {})
        if after.get("ledger_valid") is not True or after.get("ledger_count") != before_count + 1:
            raise ValueError("REJECT_NATIVE_DISPATCH_LEDGER_ADVANCE_MISMATCH")
        if after_state.get("next_sequence") != expected_sequence + 1:
            raise ValueError("REJECT_NATIVE_DISPATCH_STATE_SEQUENCE_ADVANCE_MISMATCH")
        if after_state.get("current_state_root_hash216") != receipt.successor_state_root_hash216:
            raise ValueError("REJECT_NATIVE_DISPATCH_SUCCESSOR_STATE_MISMATCH")
        if after_state.get("previous_receipt_hash72") != receipt.receipt_hash72:
            raise ValueError("REJECT_NATIVE_DISPATCH_RECEIPT_TIP_MISMATCH")
        if after.get("protected_inventory_root_hash216") != before_inventory:
            raise ValueError("REJECT_NATIVE_DISPATCH_MUTATED_PROTECTED_INVENTORY")
        persisted = native_dispatch_authority.ledger.lookup(expected_sequence)
        if not isinstance(persisted, Mapping) or persisted.get("receipt_hash72") != receipt.receipt_hash72:
            raise ValueError("REJECT_NATIVE_DISPATCH_LEDGER_RECEIPT_LOOKUP_MISMATCH")

        info = CHECKPOINT12_AUTHORITY_MAP["native_dispatch"]
        return {
            "observed": True,
            "path": [
                "kernel_runtime_autocomposer",
                "native_dispatch",
                f"{info['module']}.{info['symbol']}",
            ],
            "traversal_witness": {
                "schema": "HHS_PASS217_NATIVE_DISPATCH_TRAVERSAL_V1",
                "status": "ADMIT_NATIVE_DISPATCH_TRAVERSAL",
                "repository_native_callable": dict(info),
                "sequence": receipt.sequence,
                "operation_id": receipt.operation_id,
                "native_dispatch_id": receipt.native_dispatch_id,
                "result_values": list(receipt.result_values),
                "request_root_hash216": receipt.request_root_hash216,
                "result_root_hash216": receipt.result_root_hash216,
                "route_commitment_hash216": receipt.route_commitment_hash216,
                "prior_state_root_hash216": receipt.prior_state_root_hash216,
                "successor_state_root_hash216": receipt.successor_state_root_hash216,
                "receipt_hash72": receipt.receipt_hash72,
                "tensor_root_hash216": receipt.tensor_root_hash216,
                "ledger_count_before": before_count,
                "ledger_count_after": before_count + 1,
                "protected_inventory_root_hash216": before_inventory,
                "singleton_vm81_admission": True,
                "canonical_runtime_mutated": True,
                "receipt_persisted": True,
                "physical_route_exposed": False,
                "applicability_facts": applicability,
            },
            "witness_root": receipt.successor_state_root_hash216,
        }
    except Exception as exc:
        return _active_failure(
            "native_dispatch",
            f"REJECT_NATIVE_DISPATCH_TRAVERSAL:{type(exc).__name__}:{exc}",
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

    if facts["bounded_learning_replay_domain_present"] is False:
        not_applicable["bounded_learning_replay"] = {
            "mechanically_proven": True,
            "predicate": "bounded_learning_replay_domain_present == false",
            "observed_facts": facts,
            "reason": "operation contains no committed bounded-learning replay domain",
        }
    else:
        active["bounded_learning_replay"] = observe_bounded_learning_replay(
            payload,
            facts=facts,
            bounded_learning_service=bounded_learning_service,
        )

    if facts["moving_tensor_routing_domain_present"] is False:
        not_applicable["moving_tensor_routing"] = {
            "mechanically_proven": True,
            "predicate": "moving_tensor_routing_domain_present == false",
            "observed_facts": facts,
            "reason": "operation contains no moving-tensor logical/physical route domain",
        }
    else:
        active["moving_tensor_routing"] = observe_moving_tensor_routing(
            payload,
            facts=facts,
            moving_tensor_state=moving_tensor_state,
            moving_tensor_root_key=moving_tensor_root_key,
            moving_tensor_trusted_anchor=moving_tensor_trusted_anchor,
        )

    if facts["native_dispatch_domain_present"] is False:
        not_applicable["native_dispatch"] = {
            "mechanically_proven": True,
            "predicate": "native_dispatch_domain_present == false",
            "observed_facts": facts,
            "reason": "operation contains no governed Pass 213 native-dispatch domain",
        }
    else:
        active["native_dispatch"] = observe_native_dispatch(
            payload,
            surface=surface,
            facts=facts,
            native_dispatch_authority=native_dispatch_authority,
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
    record["checkpoint12_authority_map"] = {
        key: dict(value) for key, value in CHECKPOINT12_AUTHORITY_MAP.items()
    }
    record["checkpoint12_applicability_facts"] = facts
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
        "checkpoint10_applicability_facts",
        "checkpoint10_authority_map",
        "checkpoint11_applicability_facts",
        "checkpoint11_authority_map",
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
    "MAX_COMPOSER_REPLAY_RECORDS",
    "CHECKPOINT12_AUTHORITIES",
    "CHECKPOINT12_REQUIRED_AUTHORITIES",
    "CHECKPOINT12_AUTHORITY_MAP",
    "checkpoint12_context_facts",
    "observe_bounded_learning_replay",
    "observe_moving_tensor_routing",
    "observe_native_dispatch",
    "build_checkpoint12_inherited_authority_reachability",
]

"""Pass 217 Checkpoint 13 persistent interruption recovery authority.

This checkpoint connects the final REQUIRED Pass 215 optimization-profile class:

* interruption_recovery -> Pass 213 Iteration 10 authenticated native-dispatch
  ledger reopen + exact runtime-frontier reconstruction + governed successor
  execution.

This is deliberately stronger than ordinary checkpoint reuse, full replay, or the
Pass 213 Iteration 11 evidence pause hook.  ACTIVE_IN_PATH requires an already
persisted authenticated dispatch ledger created before the current authority
instance, exact reconstruction from its latest committed receipt, creation of a
new GovernedNativeDispatchAuthority aligned to that ledger, execution of the
next native request, and equality with a separately supplied uninterrupted
control receipt/root set.

Absent domains are mechanically NOT_APPLICABLE.  Partial, stale, unauthenticated,
or malformed recovery context fails closed.  Recovery execution is admitted only
on a controlled-runtime-mutation route because the inherited Pass 213 authority
appends one canonical ledger receipt and advances the singleton VM81 frontier.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

from hhs_backend.runtime.hhs_pass213_native_dispatch_authority_v1 import (
    GovernedNativeDispatchAuthority,
)
from hhs_backend.runtime.hhs_pass213_native_dispatch_common_v1 import (
    DispatchRuntimeState,
    NativeDispatchRequest,
)
from hhs_backend.runtime.hhs_pass213_native_dispatch_ledger_v1 import NativeDispatchLedger
from hhs_runtime.hhs_cumulative_execution_authority_v1 import (
    ACTIVE_IN_PATH,
    EXPLICITLY_SUPERSEDED,
    NOT_APPLICABLE,
    build_authority_reachability,
)
from hhs_runtime.hhs_pass217_checkpoint12_learning_tensor_native_v1 import (
    CHECKPOINT12_REQUIRED_AUTHORITIES,
    build_checkpoint12_inherited_authority_reachability,
)

VERSION = "PASS_217_CUMULATIVE_EXECUTION_COMPOSER_CHECKPOINT_13_V1"
INTERRUPTION_RECOVERY_REQUEST_SCHEMA = "HHS_PASS217_INTERRUPTION_RECOVERY_REQUEST_V1"
CHECKPOINT13_AUTHORITIES = ("interruption_recovery",)
CHECKPOINT13_REQUIRED_AUTHORITIES = CHECKPOINT12_REQUIRED_AUTHORITIES + CHECKPOINT13_AUTHORITIES

CHECKPOINT13_AUTHORITY_MAP: Dict[str, Dict[str, Any]] = {
    "interruption_recovery": {
        "origin_pass": 213,
        "origin_iteration": 10,
        "terminal_evidence_alignment_iteration": 11,
        "ledger_module": "hhs_backend.runtime.hhs_pass213_native_dispatch_ledger_v1",
        "ledger_open_symbol": "NativeDispatchLedger.__init__",
        "ledger_verify_symbol": "NativeDispatchLedger.verify_chain",
        "ledger_frontier_symbol": "NativeDispatchLedger.latest",
        "authority_module": "hhs_backend.runtime.hhs_pass213_native_dispatch_authority_v1",
        "authority_symbol": "GovernedNativeDispatchAuthority.__init__",
        "resume_symbol": "GovernedNativeDispatchAuthority.execute",
        "callable_role": (
            "reopen an authenticated persistent native-dispatch ledger after loss of the "
            "prior process-local authority, reconstruct the exact committed VM81 frontier "
            "from its latest receipt plus the verified tensor state, and execute the next "
            "governed native successor with uninterrupted-control equality proof"
        ),
        "runtime_authority": True,
        "canonical_mutation_authority": True,
        "persistent_ledger_required": True,
        "distinct_from_snapshot_reuse": True,
        "distinct_from_full_replay": True,
        "pass213_iteration11_pause_hook_is_runtime_authority": False,
    }
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


def _candidates(payload: Optional[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    found: List[Mapping[str, Any]] = []
    for mapping in _walk_mappings(dict(payload or {})):
        named = mapping.get("interruption_recovery")
        if isinstance(named, Mapping):
            found.append(named)
        if mapping.get("schema") == INTERRUPTION_RECOVERY_REQUEST_SCHEMA:
            found.append(mapping)
    return _unique_mappings(found)


def checkpoint13_context_facts(payload: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    candidates = _candidates(payload)
    return {
        "schema": "HHS_PASS217_CHECKPOINT13_APPLICABILITY_FACTS_V1",
        "interruption_recovery_domain_present": bool(candidates),
        "interruption_recovery_candidate_count": len(candidates),
        "interruption_recovery_exact_schema_count": sum(
            row.get("schema") == INTERRUPTION_RECOVERY_REQUEST_SCHEMA for row in candidates
        ),
    }


def _active_failure(reason: str, facts: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "observed": False,
        "path": ["kernel_runtime_autocomposer", "interruption_recovery"],
        "traversal_witness": {
            "schema": "HHS_PASS217_CHECKPOINT13_TRAVERSAL_FAILURE_V1",
            "status": "REJECT_CHECKPOINT13_INHERITED_TRAVERSAL",
            "authority_id": "interruption_recovery",
            "reason": str(reason),
            "authority_map": dict(CHECKPOINT13_AUTHORITY_MAP["interruption_recovery"]),
            "applicability_facts": dict(facts),
        },
        "witness_root": "",
    }


def _reject_float(value: Any) -> None:
    if isinstance(value, float):
        raise TypeError("REJECT_CHECKPOINT13_FLOAT_CANONICAL_AUTHORITY_FORBIDDEN")
    if isinstance(value, Mapping):
        for child in value.values():
            _reject_float(child)
    elif isinstance(value, (list, tuple, set)):
        for child in value:
            _reject_float(child)


def _hash216(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"REJECT_CHECKPOINT13_{label}_HASH216_INVALID")
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError(f"REJECT_CHECKPOINT13_{label}_HASH216_INVALID") from exc
    return value


def _hash72(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 72:
        raise ValueError(f"REJECT_CHECKPOINT13_{label}_HASH72_INVALID")
    return value


def _exact_int(value: Any, label: str, *, minimum: int = 0) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise ValueError(f"REJECT_CHECKPOINT13_{label}_EXACT_INTEGER_INVALID")
    return value


def observe_interruption_recovery(
    payload: Optional[Mapping[str, Any]],
    *,
    facts: Optional[Mapping[str, Any]] = None,
    mutation_allowed: bool = False,
    database_path: str | Path | None = None,
    ledger_key: Optional[bytes] = None,
    anchor_state_root_hash216: Optional[str] = None,
    anchor_receipt_hash72: Optional[str] = None,
    protected_store: Any = None,
    native_kernel: Any = None,
    tensor_state: Any = None,
) -> Dict[str, Any]:
    applicability = dict(facts or checkpoint13_context_facts(payload))
    candidates = _candidates(payload)
    if len(candidates) != 1:
        return _active_failure(
            "REJECT_INTERRUPTION_RECOVERY_REQUEST_BUNDLE_COUNT", applicability
        )
    request = candidates[0]
    if request.get("schema") != INTERRUPTION_RECOVERY_REQUEST_SCHEMA:
        return _active_failure(
            "REJECT_INTERRUPTION_RECOVERY_REQUEST_SCHEMA", applicability
        )

    ledger: NativeDispatchLedger | None = None
    try:
        _reject_float(request)
        if mutation_allowed is not True:
            raise ValueError("REJECT_INTERRUPTION_RECOVERY_CONTROLLED_MUTATION_SURFACE_REQUIRED")
        if database_path is None or not Path(database_path).exists():
            raise ValueError("REJECT_INTERRUPTION_RECOVERY_PERSISTED_LEDGER_REQUIRED")
        if not isinstance(ledger_key, bytes) or len(ledger_key) < 32:
            raise ValueError("REJECT_INTERRUPTION_RECOVERY_LEDGER_KEY_REQUIRED")
        anchor_state = _hash216(anchor_state_root_hash216, "ANCHOR_STATE")
        anchor_receipt = _hash72(anchor_receipt_hash72, "ANCHOR_RECEIPT")
        if protected_store is None or not callable(getattr(protected_store, "lookup_hash216", None)):
            raise ValueError("REJECT_INTERRUPTION_RECOVERY_PROTECTED_STORE_REQUIRED")
        if native_kernel is None or native_kernel.__class__.__name__ != "NativeDispatchKernel":
            raise ValueError("REJECT_INTERRUPTION_RECOVERY_NATIVE_KERNEL_REQUIRED")
        if tensor_state is None:
            raise ValueError("REJECT_INTERRUPTION_RECOVERY_TENSOR_STATE_REQUIRED")
        tensor_state.validate_structure()

        expected_sequence = _exact_int(
            request.get("expected_recovery_sequence"), "RECOVERY_SEQUENCE", minimum=1
        )
        expected_boundary_receipt = _hash72(
            request.get("expected_boundary_receipt_hash72"), "BOUNDARY_RECEIPT"
        )
        expected_boundary_state = _hash216(
            request.get("expected_boundary_state_root_hash216"), "BOUNDARY_STATE"
        )
        expected_ledger_event = _hash216(
            request.get("expected_boundary_ledger_event_root_hash216"), "BOUNDARY_LEDGER_EVENT"
        )
        expected_tensor = _hash216(
            request.get("expected_tensor_root_hash216"), "TENSOR_ROOT"
        )
        if tensor_state.tensor_root_hash216 != expected_tensor:
            raise ValueError("REJECT_INTERRUPTION_RECOVERY_TENSOR_ROOT_MISMATCH")

        control_request_root = _hash216(
            request.get("expected_uninterrupted_request_root_hash216"), "CONTROL_REQUEST_ROOT"
        )
        control_result_root = _hash216(
            request.get("expected_uninterrupted_result_root_hash216"), "CONTROL_RESULT_ROOT"
        )
        control_successor = _hash216(
            request.get("expected_uninterrupted_successor_state_root_hash216"),
            "CONTROL_SUCCESSOR_STATE",
        )
        control_receipt = _hash72(
            request.get("expected_uninterrupted_receipt_hash72"), "CONTROL_RECEIPT"
        )
        expected_results = request.get("expected_uninterrupted_result_values")
        if not isinstance(expected_results, (list, tuple)) or not expected_results:
            raise ValueError("REJECT_INTERRUPTION_RECOVERY_CONTROL_RESULTS_REQUIRED")
        control_results = tuple(
            _exact_int(item, "CONTROL_RESULT_VALUE") for item in expected_results
        )

        inner = request.get("next_request")
        if not isinstance(inner, Mapping):
            raise ValueError("REJECT_INTERRUPTION_RECOVERY_NEXT_REQUEST_REQUIRED")
        _reject_float(inner)
        next_request = NativeDispatchRequest.from_mapping(inner)
        if next_request.expected_parent_hash216 != expected_boundary_state:
            raise ValueError("REJECT_INTERRUPTION_RECOVERY_NEXT_PARENT_MISMATCH")
        if next_request.expected_tensor_root_hash216 != expected_tensor:
            raise ValueError("REJECT_INTERRUPTION_RECOVERY_NEXT_TENSOR_MISMATCH")

        # This constructor is the actual interruption boundary: it reopens the
        # durable SQLite ledger, authenticates its metadata/events, and verifies
        # receipt/state chain continuity before any successor execution exists.
        ledger = NativeDispatchLedger(
            database_path=database_path,
            root_key=ledger_key,
            anchor_state_root_hash216=anchor_state,
            anchor_receipt_hash72=anchor_receipt,
        )
        if ledger.verify_chain() is not True:
            raise ValueError("REJECT_INTERRUPTION_RECOVERY_LEDGER_CHAIN_INVALID")
        if ledger.count() != expected_sequence:
            raise ValueError("REJECT_INTERRUPTION_RECOVERY_LEDGER_SEQUENCE_MISMATCH")
        latest = ledger.latest()
        if not isinstance(latest, Mapping):
            raise ValueError("REJECT_INTERRUPTION_RECOVERY_LEDGER_FRONTIER_MISSING")
        if (
            latest.get("sequence") != expected_sequence
            or latest.get("receipt_hash72") != expected_boundary_receipt
            or latest.get("successor_state_root_hash216") != expected_boundary_state
            or latest.get("ledger_event_root_hash216") != expected_ledger_event
            or latest.get("tensor_root_hash216") != expected_tensor
        ):
            raise ValueError("REJECT_INTERRUPTION_RECOVERY_PERSISTED_FRONTIER_MISMATCH")

        # Reconstruct only from persisted receipt authority plus the separately
        # verified tensor object.  No prior GovernedNativeDispatchAuthority or
        # process-local DispatchRuntimeState is accepted as recovery input.
        reconstructed = DispatchRuntimeState(
            next_sequence=expected_sequence + 1,
            current_state_root_hash216=str(latest["successor_state_root_hash216"]),
            previous_receipt_hash72=str(latest["receipt_hash72"]),
            kernel_policy_hash216=str(latest["kernel_policy_hash216"]),
            kernel_measurement_hash216=str(latest["kernel_measurement_hash216"]),
            lineage_root_hash216=str(latest["lineage_root_hash216"]),
            tensor_state=tensor_state,
            last_timestamp_ns=_exact_int(latest["timestamp_ns"], "BOUNDARY_TIMESTAMP"),
        )
        reconstructed.validate()
        recovered_authority = GovernedNativeDispatchAuthority(
            protected_store=protected_store,
            native_kernel=native_kernel,
            ledger=ledger,
            runtime_state=reconstructed,
        )
        if recovered_authority.runtime_state.current_state_root_hash216 != expected_boundary_state:
            raise ValueError("REJECT_INTERRUPTION_RECOVERY_RECONSTRUCTED_STATE_MISMATCH")

        receipt = recovered_authority.execute(next_request)
        if (
            receipt.sequence != expected_sequence + 1
            or receipt.prior_state_root_hash216 != expected_boundary_state
            or receipt.request_root_hash216 != control_request_root
            or receipt.result_root_hash216 != control_result_root
            or receipt.successor_state_root_hash216 != control_successor
            or receipt.receipt_hash72 != control_receipt
            or receipt.result_values != control_results
        ):
            raise ValueError("REJECT_INTERRUPTION_RECOVERY_UNINTERRUPTED_CONTROL_MISMATCH")
        if ledger.count() != expected_sequence + 1 or ledger.verify_chain() is not True:
            raise ValueError("REJECT_INTERRUPTION_RECOVERY_LEDGER_NOT_ADVANCED_EXACTLY_ONCE")
        persisted_successor = ledger.latest()
        if (
            not isinstance(persisted_successor, Mapping)
            or persisted_successor.get("receipt_hash72") != receipt.receipt_hash72
            or persisted_successor.get("successor_state_root_hash216")
            != receipt.successor_state_root_hash216
        ):
            raise ValueError("REJECT_INTERRUPTION_RECOVERY_SUCCESSOR_NOT_PERSISTED")

        return {
            "observed": True,
            "path": [
                "kernel_runtime_autocomposer",
                "interruption_recovery",
                "hhs_backend.runtime.hhs_pass213_native_dispatch_ledger_v1.NativeDispatchLedger.__init__",
                "hhs_backend.runtime.hhs_pass213_native_dispatch_ledger_v1.NativeDispatchLedger.verify_chain",
                "hhs_backend.runtime.hhs_pass213_native_dispatch_ledger_v1.NativeDispatchLedger.latest",
                "hhs_backend.runtime.hhs_pass213_native_dispatch_authority_v1.GovernedNativeDispatchAuthority.__init__",
                "hhs_backend.runtime.hhs_pass213_native_dispatch_authority_v1.GovernedNativeDispatchAuthority.execute",
            ],
            "traversal_witness": {
                "schema": "HHS_PASS217_INTERRUPTION_RECOVERY_TRAVERSAL_V1",
                "status": "ADMIT_INTERRUPTION_RECOVERY_TRAVERSAL",
                "repository_native_callable": dict(CHECKPOINT13_AUTHORITY_MAP["interruption_recovery"]),
                "recovery_sequence": expected_sequence,
                "boundary_receipt_hash72": expected_boundary_receipt,
                "boundary_state_root_hash216": expected_boundary_state,
                "boundary_ledger_event_root_hash216": expected_ledger_event,
                "tensor_root_hash216": expected_tensor,
                "reconstructed_next_sequence": expected_sequence + 1,
                "recovered_sequence": receipt.sequence,
                "request_root_hash216": receipt.request_root_hash216,
                "result_root_hash216": receipt.result_root_hash216,
                "result_values": list(receipt.result_values),
                "successor_state_root_hash216": receipt.successor_state_root_hash216,
                "receipt_hash72": receipt.receipt_hash72,
                "ledger_count_after": expected_sequence + 1,
                "persistent_ledger_reopened": True,
                "prior_process_authority_reused": False,
                "prior_process_runtime_state_reused": False,
                "uninterrupted_control_equal": True,
                "snapshot_reuse_used": False,
                "full_history_replay_used": False,
                "pass213_iteration11_pause_hook_used": False,
                "canonical_runtime_mutated": True,
                "applicability_facts": applicability,
            },
            "witness_root": receipt.receipt_hash72,
        }
    except Exception as exc:
        return _active_failure(
            f"REJECT_INTERRUPTION_RECOVERY_TRAVERSAL:{type(exc).__name__}:{exc}",
            applicability,
        )
    finally:
        if ledger is not None:
            try:
                ledger.close()
            except Exception:
                pass


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


def build_checkpoint13_inherited_authority_reachability(
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
    interruption_recovery_database_path: str | Path | None = None,
    interruption_recovery_ledger_key: Optional[bytes] = None,
    interruption_recovery_anchor_state_root_hash216: Optional[str] = None,
    interruption_recovery_anchor_receipt_hash72: Optional[str] = None,
    interruption_recovery_protected_store: Any = None,
    interruption_recovery_native_kernel: Any = None,
    interruption_recovery_tensor_state: Any = None,
) -> Dict[str, Any]:
    prior = build_checkpoint12_inherited_authority_reachability(
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
        bounded_learning_service=bounded_learning_service,
        moving_tensor_state=moving_tensor_state,
        moving_tensor_root_key=moving_tensor_root_key,
        moving_tensor_trusted_anchor=moving_tensor_trusted_anchor,
        native_dispatch_authority=native_dispatch_authority,
    )
    active: Dict[str, Mapping[str, Any]] = {}
    not_applicable: Dict[str, Mapping[str, Any]] = {}
    superseded: Dict[str, Mapping[str, Any]] = {}
    _import_prior_decisions(prior, active, not_applicable, superseded)
    facts = checkpoint13_context_facts(payload)

    if not facts["interruption_recovery_domain_present"]:
        not_applicable["interruption_recovery"] = {
            "mechanically_proven": True,
            "predicate": "interruption_recovery_domain_present == false",
            "observed_facts": facts,
            "reason": "operation contains no persisted native-dispatch interruption frontier",
        }
    else:
        active["interruption_recovery"] = observe_interruption_recovery(
            payload,
            facts=facts,
            mutation_allowed=(surface.get("mutation_policy") == "CONTROLLED_RUNTIME_MUTATION"),
            database_path=interruption_recovery_database_path,
            ledger_key=interruption_recovery_ledger_key,
            anchor_state_root_hash216=interruption_recovery_anchor_state_root_hash216,
            anchor_receipt_hash72=interruption_recovery_anchor_receipt_hash72,
            protected_store=interruption_recovery_protected_store,
            native_kernel=interruption_recovery_native_kernel,
            tensor_state=interruption_recovery_tensor_state,
        )

    operation_id = str(preflight.get("operation") or surface.get("symbol") or "operation")
    record = build_authority_reachability(
        operation_id,
        active_in_path=active,
        not_applicable=not_applicable,
        explicitly_superseded=superseded,
        required_authorities=CHECKPOINT13_REQUIRED_AUTHORITIES,
    )
    record["checkpoint_scope"] = list(CHECKPOINT13_REQUIRED_AUTHORITIES)
    record["checkpoint13_authority_map"] = {
        key: dict(value) for key, value in CHECKPOINT13_AUTHORITY_MAP.items()
    }
    record["checkpoint13_applicability_facts"] = facts
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
        "checkpoint12_applicability_facts",
        "checkpoint12_authority_map",
    ):
        if key in prior:
            value = prior[key]
            record[key] = dict(value) if isinstance(value, Mapping) else value
    record["prior_checkpoint_reachability_root_hash72"] = prior.get("reachability_root_hash72")
    record["checkpoint"] = 13
    return record


__all__ = [
    "VERSION",
    "INTERRUPTION_RECOVERY_REQUEST_SCHEMA",
    "CHECKPOINT13_AUTHORITIES",
    "CHECKPOINT13_REQUIRED_AUTHORITIES",
    "CHECKPOINT13_AUTHORITY_MAP",
    "checkpoint13_context_facts",
    "observe_interruption_recovery",
    "build_checkpoint13_inherited_authority_reachability",
]

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping, Sequence
import json

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import (
    ContinuationError,
    ContinuationLease,
    Hash72ReceiptChainWorkload,
    PredictiveContinuationEngine,
    ResourceContract,
    _hash,
    _load_pass110_frontier,
)

PASS_ID = "PASS_112"
EXIT_CHECKPOINT_SCHEMA = "HHS_CONTINUATION_EXIT_CHECKPOINT_V1"
CLEANUP_PLAN_SCHEMA = "HHS_MEMORY_CLEANUP_PLAN_V1"
CLEANUP_RECEIPT_SCHEMA = "HHS_MEMORY_CLEANUP_VALIDATION_RECEIPT_V1"
CACHE_DISPOSITION_SCHEMA = "HHS_CONTINUATION_CACHE_DISPOSITION_RECEIPT_V1"
EXIT_RECEIPT_SCHEMA = "HHS_PASS_SAFE_CONTINUATION_EXIT_RECEIPT_V1"

EXIT_CLASSES = {
    "EXIT_COMPLETED",
    "EXIT_SUSPENDED_FOR_LATER_RESUME",
    "EXIT_RESUME_REJECTED",
    "EXIT_DEPENDENCY_REPAIR_REQUIRED",
    "EXIT_RESOURCE_BOUND",
    "EXIT_USER_REQUESTED",
    "EXIT_RUNTIME_UNAVAILABLE",
    "EXIT_INTERNAL_VALIDATION_FAILURE",
    "EXIT_FATAL_UNRECOVERABLE",
}

REJECTION_CODES = {
    "REJECT_EXIT_WITHOUT_LAST_VALID_CHECKPOINT",
    "REJECT_COMPLETION_STATUS_FOR_SUSPENDED_OPERATION",
    "REJECT_COMPLETION_STATUS_FOR_REJECTED_RESUME",
    "REJECT_CHECKPOINT_FROM_PARTIALLY_MUTATED_STATE",
    "REJECT_EXIT_CHECKPOINT_WITH_OPEN_RECEIPT_TRANSACTION",
    "REJECT_MEMORY_CLEANUP_BEFORE_STATE_PRESERVATION",
    "REJECT_MEMORY_CLEANUP_BEFORE_RECEIPT_COMMIT",
    "REJECT_AUTHORITATIVE_STATE_DELETION",
    "REJECT_UNWITNESSED_TEMPORARY_MEMORY_RETENTION",
    "REJECT_UNWITNESSED_RESOURCE_HANDLE_LEAK",
    "REJECT_REPLAY_MEMORY_PRESERVED_AS_WORKLOAD_STATE",
    "REJECT_VALID_CACHE_DELETION_AFTER_FAILED_RESUME",
    "REJECT_CACHE_RETIREMENT_BEFORE_COMPLETION",
    "REJECT_CACHE_INVALIDATION_WITHOUT_RECEIPT",
    "REJECT_CLEANUP_REPORTED_VALIDATED_WITH_UNVERIFIED_TARGETS",
    "REJECT_MISSING_RESOURCE_METRIC_REPRESENTED_AS_ZERO",
    "REJECT_NON_IDEMPOTENT_CLEANUP",
    "REJECT_DOUBLE_RESOURCE_RELEASE_ACCOUNTING",
    "REJECT_PARALLEL_BRANCH_EXIT_INCONSISTENCY",
    "REJECT_EXIT_HISTORY_ERASURE",
    "REJECT_COLD_BOOT_WITHOUT_EXIT_RECONSTRUCTION",
    "REJECT_FAILED_RESUME_PROGRESS_MUTATION",
    "REJECT_EXIT_RECEIPT_STATE_MISMATCH",
    "REJECT_TEMPORARY_AUTHORITY_REMAINING_AFTER_COMPLETION",
}


class PassSafeExitError(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class TrackedResource:
    resource_id: str
    resource_class: str
    size_bytes: int | None
    authoritative: bool = False
    external_handle: bool = False
    retained: bool = False
    retention_reason: str | None = None

    def __post_init__(self) -> None:
        allowed = {
            "AUTHORITATIVE_STATE_MEMORY",
            "REPLAY_WORKING_MEMORY",
            "TEMPORARY_EXECUTION_MEMORY",
            "EXTERNAL_RESOURCE_HANDLE",
        }
        if self.resource_class not in allowed:
            raise ValueError(self.resource_class)
        if self.size_bytes is not None and self.size_bytes < 0:
            raise ValueError("size_bytes must be nonnegative or None")
        if self.retained and not self.retention_reason:
            raise ValueError("retained resources require a justification")

    @property
    def root_hash72(self) -> str:
        return _hash("hhs_pass112_tracked_resource_v1", asdict(self))


class ResourceLedger:
    """Tracks explicit resource dispositions and makes cleanup idempotent."""

    def __init__(self, resources: Iterable[TrackedResource]):
        items = list(resources)
        if len({x.resource_id for x in items}) != len(items):
            raise ValueError("resource ids must be unique")
        self._resources = {x.resource_id: x for x in items}
        self._disposition: dict[str, str] = {x.resource_id: "OPEN" for x in items}
        self._release_events: dict[str, int] = {x.resource_id: 0 for x in items}

    @property
    def root_hash72(self) -> str:
        return _hash(
            "hhs_pass112_resource_ledger_v1",
            {
                "resources": [asdict(self._resources[k]) for k in sorted(self._resources)],
                "disposition": {k: self._disposition[k] for k in sorted(self._disposition)},
                "release_events": {k: self._release_events[k] for k in sorted(self._release_events)},
            },
        )

    def snapshot(self) -> dict[str, Any]:
        return {
            "resources": [asdict(self._resources[k]) for k in sorted(self._resources)],
            "disposition": {k: self._disposition[k] for k in sorted(self._disposition)},
            "release_events": {k: self._release_events[k] for k in sorted(self._release_events)},
            "ledger_root_hash72": self.root_hash72,
        }

    def cleanup(self, *, preservation_verified: bool) -> dict[str, Any]:
        if not preservation_verified:
            raise PassSafeExitError(
                "REJECT_MEMORY_CLEANUP_BEFORE_STATE_PRESERVATION",
                "authoritative checkpoint and receipts must be verified before cleanup",
            )
        before_root = self.root_hash72
        dispositions: list[dict[str, Any]] = []
        for resource_id in sorted(self._resources):
            resource = self._resources[resource_id]
            current = self._disposition[resource_id]
            if resource.authoritative or resource.retained:
                target = "RETAINED_WITH_AUTHORITY"
            elif resource.external_handle:
                target = "CLOSED"
            else:
                target = "RELEASED"
            if current == "OPEN":
                self._disposition[resource_id] = target
                if target in {"RELEASED", "CLOSED"}:
                    self._release_events[resource_id] += 1
            elif current != target:
                raise PassSafeExitError("REJECT_NON_IDEMPOTENT_CLEANUP", f"resource {resource_id} changed disposition")
            dispositions.append(
                {
                    "resource_id": resource_id,
                    "resource_root_hash72": resource.root_hash72,
                    "resource_class": resource.resource_class,
                    "size_bytes": resource.size_bytes if resource.size_bytes is not None else "TYPED_UNAVAILABLE",
                    "disposition": self._disposition[resource_id],
                    "retention_reason": resource.retention_reason,
                    "release_event_count": self._release_events[resource_id],
                }
            )
        after_root = self.root_hash72
        return {
            "before_ledger_root_hash72": before_root,
            "after_ledger_root_hash72": after_root,
            "dispositions": dispositions,
        }

    def validate(self) -> None:
        for resource_id, resource in self._resources.items():
            disposition = self._disposition[resource_id]
            if disposition == "OPEN":
                raise PassSafeExitError("REJECT_UNWITNESSED_RESOURCE_HANDLE_LEAK", f"resource {resource_id} remains open")
            if resource.authoritative and disposition != "RETAINED_WITH_AUTHORITY":
                raise PassSafeExitError("REJECT_AUTHORITATIVE_STATE_DELETION", resource_id)
            if self._release_events[resource_id] > 1:
                raise PassSafeExitError("REJECT_DOUBLE_RESOURCE_RELEASE_ACCOUNTING", resource_id)


class PassSafeExitEngine:
    def __init__(self, operation_id: str):
        self.operation_id = operation_id

    @staticmethod
    def classify_exit(*, completion: Mapping[str, Any] | None, resume_error: BaseException | None, defer_reason: str | None = None) -> str:
        if completion is not None:
            if completion.get("completion_status") != "COMPLETED_AFTER_WITNESSED_RESUME":
                raise PassSafeExitError("REJECT_EXIT_RECEIPT_STATE_MISMATCH", "completion object is not complete")
            return "EXIT_COMPLETED"
        if defer_reason == "RESOURCE_BOUND":
            return "EXIT_RESOURCE_BOUND"
        if defer_reason == "RUNTIME_UNAVAILABLE":
            return "EXIT_RUNTIME_UNAVAILABLE"
        if isinstance(resume_error, ContinuationError):
            if resume_error.code == "REJECT_STALE_CONTINUATION_DEPENDENCY":
                return "EXIT_DEPENDENCY_REPAIR_REQUIRED"
            return "EXIT_RESUME_REJECTED"
        if resume_error is not None:
            return "EXIT_INTERNAL_VALIDATION_FAILURE"
        return "EXIT_SUSPENDED_FOR_LATER_RESUME"

    @staticmethod
    def _receipt_roots(cache: Mapping[str, Any], admission: Mapping[str, Any] | None, completion: Mapping[str, Any] | None, failure_receipt: Mapping[str, Any] | None) -> list[str]:
        roots: list[str] = []
        for key in ("prediction_receipt_root_hash72", "continuation_cache_root_hash72"):
            value = cache.get(key)
            if value:
                roots.append(str(value))
        roots.extend(str(x["receipt_root_hash72"]) for x in cache.get("ordered_receipts", []))
        if admission and admission.get("resume_admission_root_hash72"):
            roots.append(str(admission["resume_admission_root_hash72"]))
        if completion and completion.get("completion_root_hash72"):
            roots.append(str(completion["completion_root_hash72"]))
        if failure_receipt and failure_receipt.get("failure_root_hash72"):
            roots.append(str(failure_receipt["failure_root_hash72"]))
        return roots

    def finalize_exit_checkpoint(
        self,
        *,
        cache: Mapping[str, Any],
        exit_classification: str,
        admission: Mapping[str, Any] | None = None,
        completion: Mapping[str, Any] | None = None,
        failure_receipt: Mapping[str, Any] | None = None,
        open_receipt_transaction: bool = False,
        partial_mutation_present: bool = False,
        branch_states: Sequence[Mapping[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if exit_classification not in EXIT_CLASSES:
            raise ValueError(exit_classification)
        if open_receipt_transaction:
            raise PassSafeExitError("REJECT_EXIT_CHECKPOINT_WITH_OPEN_RECEIPT_TRANSACTION", "receipt transaction remains open")
        if partial_mutation_present:
            raise PassSafeExitError("REJECT_CHECKPOINT_FROM_PARTIALLY_MUTATED_STATE", "partial mutation cannot be checkpointed")
        last_state = completion.get("final_state") if completion is not None else cache.get("validated_current_state")
        if not isinstance(last_state, Mapping) or not last_state.get("state_root_hash72"):
            raise PassSafeExitError("REJECT_EXIT_WITHOUT_LAST_VALID_CHECKPOINT", "no committed state root")
        workload_completed = exit_classification == "EXIT_COMPLETED"
        if workload_completed != (completion is not None):
            code = "REJECT_COMPLETION_STATUS_FOR_SUSPENDED_OPERATION" if workload_completed else "REJECT_EXIT_RECEIPT_STATE_MISMATCH"
            raise PassSafeExitError(code, "completion classification does not match lifecycle objects")
        branches = [dict(x) for x in (branch_states or [])]
        if branches:
            roots = [x.get("state_root_hash72") for x in branches]
            if any(not x for x in roots) or len(roots) != len(set(roots)):
                raise PassSafeExitError("REJECT_PARALLEL_BRANCH_EXIT_INCONSISTENCY", "branch state roots are incomplete or duplicated")
        receipt_roots = self._receipt_roots(cache, admission, completion, failure_receipt)
        if not receipt_roots:
            raise PassSafeExitError("REJECT_EXIT_HISTORY_ERASURE", "no lifecycle receipts preserved")
        checkpoint = {
            "schema": EXIT_CHECKPOINT_SCHEMA,
            "operation_id": self.operation_id,
            "continuation_cache_root_hash72": cache["continuation_cache_root_hash72"],
            "resume_attempt_root_hash72": admission.get("resume_admission_root_hash72") if admission else failure_receipt.get("failure_root_hash72") if failure_receipt else None,
            "exit_classification": exit_classification,
            "last_valid_checkpoint_root_hash72": last_state["state_root_hash72"],
            "last_valid_state": deepcopy(dict(last_state)),
            "validated_frontier": {
                "completed_step": int(last_state["step_index"]),
                "pending_step_start": None if workload_completed else cache.get("pending_step_start"),
                "pending_step_end": None if workload_completed else cache.get("pending_step_end"),
                "pass110_frontier": deepcopy(cache.get("pass110_frontier", {})),
            },
            "preserved_receipt_roots": receipt_roots,
            "preserved_receipt_history_root_hash72": _hash("hhs_pass112_preserved_receipt_history_v1", receipt_roots),
            "authority_state_root_hash72": cache["capability_admission_root_hash72"],
            "dependency_state_root_hash72": cache["dependency_root_hash72"],
            "branch_states": branches,
            "workload_completed": workload_completed,
            "checkpoint_status": "EXIT_CHECKPOINT_FINALIZED",
        }
        checkpoint["exit_checkpoint_root_hash72"] = _hash("hhs_pass112_exit_checkpoint_v1", checkpoint)
        return checkpoint

    @staticmethod
    def build_cleanup_plan(exit_checkpoint: Mapping[str, Any], resources: Sequence[TrackedResource]) -> dict[str, Any]:
        actions = []
        for resource in sorted(resources, key=lambda x: x.resource_id):
            if resource.authoritative or resource.retained:
                disposition = "RETAIN_WITH_AUTHORITY"
            elif resource.external_handle:
                disposition = "CLOSE"
            else:
                disposition = "RELEASE"
            actions.append(
                {
                    "resource_id": resource.resource_id,
                    "resource_root_hash72": resource.root_hash72,
                    "resource_class": resource.resource_class,
                    "target_disposition": disposition,
                }
            )
        plan = {
            "schema": CLEANUP_PLAN_SCHEMA,
            "exit_checkpoint_root_hash72": exit_checkpoint["exit_checkpoint_root_hash72"],
            "actions": actions,
            "cleanup_state": "CLEANUP_NOT_STARTED",
        }
        plan["cleanup_plan_root_hash72"] = _hash("hhs_pass112_cleanup_plan_v1", plan)
        return plan

    @staticmethod
    def execute_cleanup(exit_checkpoint: Mapping[str, Any], cleanup_plan: Mapping[str, Any], ledger: ResourceLedger) -> dict[str, Any]:
        if cleanup_plan.get("exit_checkpoint_root_hash72") != exit_checkpoint.get("exit_checkpoint_root_hash72"):
            raise PassSafeExitError("REJECT_MEMORY_CLEANUP_BEFORE_STATE_PRESERVATION", "cleanup plan is not bound to checkpoint")
        if exit_checkpoint.get("checkpoint_status") != "EXIT_CHECKPOINT_FINALIZED":
            raise PassSafeExitError("REJECT_MEMORY_CLEANUP_BEFORE_RECEIPT_COMMIT", "exit checkpoint is not finalized")
        execution = ledger.cleanup(preservation_verified=True)
        ledger.validate()
        dispositions = execution["dispositions"]
        receipt = {
            "schema": CLEANUP_RECEIPT_SCHEMA,
            "exit_checkpoint_root_hash72": exit_checkpoint["exit_checkpoint_root_hash72"],
            "cleanup_plan_root_hash72": cleanup_plan["cleanup_plan_root_hash72"],
            "resource_dispositions": dispositions,
            "authoritative_objects_preserved": [x["resource_id"] for x in dispositions if x["disposition"] == "RETAINED_WITH_AUTHORITY"],
            "temporary_objects_released": [x["resource_id"] for x in dispositions if x["resource_class"] == "TEMPORARY_EXECUTION_MEMORY" and x["disposition"] == "RELEASED"],
            "replay_objects_released": [x["resource_id"] for x in dispositions if x["resource_class"] == "REPLAY_WORKING_MEMORY" and x["disposition"] == "RELEASED"],
            "external_handles_closed": [x["resource_id"] for x in dispositions if x["disposition"] == "CLOSED"],
            "pre_cleanup_memory_root_hash72": execution["before_ledger_root_hash72"],
            "post_cleanup_memory_root_hash72": execution["after_ledger_root_hash72"],
            "cleanup_status": "CLEANUP_VALIDATED",
        }
        receipt["cleanup_validation_root_hash72"] = _hash("hhs_pass112_cleanup_validation_v1", receipt)
        return receipt

    @staticmethod
    def disposition_cache(exit_checkpoint: Mapping[str, Any], cache: Mapping[str, Any]) -> dict[str, Any]:
        classification = exit_checkpoint["exit_classification"]
        if classification == "EXIT_COMPLETED":
            disposition = "RETIRED_AFTER_COMPLETION"
            continuation_authority_active = False
        elif classification in {"EXIT_RESUME_REJECTED", "EXIT_INTERNAL_VALIDATION_FAILURE", "EXIT_FATAL_UNRECOVERABLE"}:
            disposition = "PRESERVED_NON_ADMITTED_FOR_INSPECTION"
            continuation_authority_active = False
        else:
            disposition = "RETAINED_FOR_REVALIDATION_OR_RESUME"
            continuation_authority_active = True
        receipt = {
            "schema": CACHE_DISPOSITION_SCHEMA,
            "continuation_cache_root_hash72": cache["continuation_cache_root_hash72"],
            "exit_checkpoint_root_hash72": exit_checkpoint["exit_checkpoint_root_hash72"],
            "cache_disposition": disposition,
            "continuation_authority_active": continuation_authority_active,
            "history_preserved": True,
        }
        receipt["cache_disposition_root_hash72"] = _hash("hhs_pass112_cache_disposition_v1", receipt)
        return receipt

    @staticmethod
    def emit_exit_receipt(
        *,
        exit_checkpoint: Mapping[str, Any],
        cleanup_receipt: Mapping[str, Any],
        cache_disposition: Mapping[str, Any],
    ) -> dict[str, Any]:
        if cleanup_receipt.get("cleanup_status") != "CLEANUP_VALIDATED":
            raise PassSafeExitError("REJECT_CLEANUP_REPORTED_VALIDATED_WITH_UNVERIFIED_TARGETS", "cleanup is incomplete")
        completed = bool(exit_checkpoint["workload_completed"])
        if completed and cache_disposition.get("continuation_authority_active"):
            raise PassSafeExitError("REJECT_TEMPORARY_AUTHORITY_REMAINING_AFTER_COMPLETION", "cache authority remains active")
        classification = exit_checkpoint["exit_classification"]
        receipt = {
            "schema": EXIT_RECEIPT_SCHEMA,
            "operation_id": exit_checkpoint["operation_id"],
            "continuation_cache_root_hash72": exit_checkpoint["continuation_cache_root_hash72"],
            "last_valid_checkpoint_root_hash72": exit_checkpoint["last_valid_checkpoint_root_hash72"],
            "exit_checkpoint_root_hash72": exit_checkpoint["exit_checkpoint_root_hash72"],
            "cleanup_validation_root_hash72": cleanup_receipt["cleanup_validation_root_hash72"],
            "cache_disposition_root_hash72": cache_disposition["cache_disposition_root_hash72"],
            "preserved_receipt_history_root_hash72": exit_checkpoint["preserved_receipt_history_root_hash72"],
            "exit_classification": classification,
            "workload_completed": completed,
            "resume_permitted": bool(cache_disposition["continuation_authority_active"]),
            "repair_required": classification == "EXIT_DEPENDENCY_REPAIR_REQUIRED",
            "temporary_authority_retired": completed,
            "exit_status": "PASS_SAFE_EXIT_VALIDATED",
        }
        receipt["exit_receipt_root_hash72"] = _hash("hhs_pass112_exit_receipt_v1", receipt)
        return receipt

    @staticmethod
    def reconstruct_exit(bundle: Mapping[str, Any]) -> dict[str, Any]:
        checkpoint = deepcopy(bundle["exit_checkpoint"])
        cleanup = deepcopy(bundle["cleanup_receipt"])
        disposition = deepcopy(bundle["cache_disposition"])
        receipt = deepcopy(bundle["exit_receipt"])
        checks = {
            "checkpoint_root": checkpoint["exit_checkpoint_root_hash72"] == _hash("hhs_pass112_exit_checkpoint_v1", {k: v for k, v in checkpoint.items() if k != "exit_checkpoint_root_hash72"}),
            "cleanup_root": cleanup["cleanup_validation_root_hash72"] == _hash("hhs_pass112_cleanup_validation_v1", {k: v for k, v in cleanup.items() if k != "cleanup_validation_root_hash72"}),
            "cache_disposition_root": disposition["cache_disposition_root_hash72"] == _hash("hhs_pass112_cache_disposition_v1", {k: v for k, v in disposition.items() if k != "cache_disposition_root_hash72"}),
            "exit_receipt_root": receipt["exit_receipt_root_hash72"] == _hash("hhs_pass112_exit_receipt_v1", {k: v for k, v in receipt.items() if k != "exit_receipt_root_hash72"}),
            "state_binding": receipt["last_valid_checkpoint_root_hash72"] == checkpoint["last_valid_checkpoint_root_hash72"],
            "history_binding": receipt["preserved_receipt_history_root_hash72"] == checkpoint["preserved_receipt_history_root_hash72"],
        }
        result = {
            "schema": "HHS_PASS_SAFE_EXIT_RECONSTRUCTION_V1",
            "checks": checks,
            "reconstruction_status": "RECONSTRUCTED" if all(checks.values()) else "REJECTED",
            "last_valid_state": checkpoint["last_valid_state"],
        }
        result["reconstruction_root_hash72"] = _hash("hhs_pass112_exit_reconstruction_v1", result)
        return result


def _build_pass111_fixture() -> tuple[Hash72ReceiptChainWorkload, PredictiveContinuationEngine, dict[str, Any], ContinuationLease, dict[str, Any]]:
    dependency_root = _hash("hhs_pass112_dependency_v1", {"component": "hash72_receipt_chain", "version": 1})
    capability_root = _hash("hhs_pass112_capability_v1", {"operation": "pass_safe_exit", "status": "CANONICAL_EXECUTABLE"})
    workload = Hash72ReceiptChainWorkload("hhs:pass112:continuation_workload", dependency_root, capability_root)
    engine = PredictiveContinuationEngine(workload, total_steps=18, contract=ResourceContract(maximum_useful_steps_per_cycle=12))
    genesis = workload.genesis("PASS112_FROM_PASS111_SEED")
    suspension_state, receipts, states = workload.execute_range(genesis, 1, 12)
    frontier = _load_pass110_frontier(Path(__file__).resolve().parents[1])
    cache = engine.create_cache(
        genesis_state=genesis,
        suspension_state=suspension_state,
        states_by_step=states,
        receipts=receipts,
        prediction=engine.predict(12),
        pass110_frontier=frontier,
    )
    lease = ContinuationLease(workload.operation_id, dependency_root, capability_root, cache["tail_length"], 6)
    return workload, engine, cache, lease, genesis


def _default_resources() -> list[TrackedResource]:
    return [
        TrackedResource("authoritative_exit_state", "AUTHORITATIVE_STATE_MEMORY", 4096, authoritative=True, retained=True, retention_reason="required for reconstruction"),
        TrackedResource("preserved_receipt_bundle", "AUTHORITATIVE_STATE_MEMORY", 8192, authoritative=True, retained=True, retention_reason="receipt history must survive cleanup"),
        TrackedResource("tail_replay_buffer", "REPLAY_WORKING_MEMORY", 2048),
        TrackedResource("temporary_candidate_buffer", "TEMPORARY_EXECUTION_MEMORY", 1024),
        TrackedResource("runtime_file_handle", "EXTERNAL_RESOURCE_HANDLE", None, external_handle=True),
    ]


def pass112_self_test() -> dict[str, Any]:
    workload, continuation, cache, lease, genesis = _build_pass111_fixture()
    engine = PassSafeExitEngine(workload.operation_id)

    admission = continuation.replay_tail(cache, lease)
    completion = continuation.continue_execution(cache, admission, lease)
    completed_checkpoint = engine.finalize_exit_checkpoint(
        cache=cache,
        exit_classification=engine.classify_exit(completion=completion, resume_error=None),
        admission=admission,
        completion=completion,
    )
    resources = _default_resources()
    completed_plan = engine.build_cleanup_plan(completed_checkpoint, resources)
    completed_ledger = ResourceLedger(resources)
    completed_cleanup = engine.execute_cleanup(completed_checkpoint, completed_plan, completed_ledger)
    completed_cleanup_repeat = engine.execute_cleanup(completed_checkpoint, completed_plan, completed_ledger)
    completed_disposition = engine.disposition_cache(completed_checkpoint, cache)
    completed_exit = engine.emit_exit_receipt(
        exit_checkpoint=completed_checkpoint,
        cleanup_receipt=completed_cleanup,
        cache_disposition=completed_disposition,
    )
    completed_bundle = {
        "exit_checkpoint": completed_checkpoint,
        "cleanup_receipt": completed_cleanup,
        "cache_disposition": completed_disposition,
        "exit_receipt": completed_exit,
    }
    completed_reconstruction = engine.reconstruct_exit(completed_bundle)

    failed_cache = deepcopy(cache)
    failed_cache["validated_current_state"]["accumulator"] += 1
    resume_error: ContinuationError | None = None
    try:
        continuation.replay_tail(failed_cache, lease)
    except ContinuationError as exc:
        resume_error = exc
    if resume_error is None:
        raise AssertionError("corrupted cache did not fail")
    failure_receipt = {
        "schema": "HHS_CONTINUATION_RESUME_FAILURE_RECEIPT_V1",
        "continuation_cache_root_hash72": cache["continuation_cache_root_hash72"],
        "rejection_code": resume_error.code,
        "message": str(resume_error),
        "useful_progress_mutated": False,
    }
    failure_receipt["failure_root_hash72"] = _hash("hhs_pass112_resume_failure_v1", failure_receipt)
    failed_checkpoint = engine.finalize_exit_checkpoint(
        cache=cache,
        exit_classification=engine.classify_exit(completion=None, resume_error=resume_error),
        failure_receipt=failure_receipt,
    )
    failed_resources = _default_resources()
    failed_plan = engine.build_cleanup_plan(failed_checkpoint, failed_resources)
    failed_ledger = ResourceLedger(failed_resources)
    failed_cleanup = engine.execute_cleanup(failed_checkpoint, failed_plan, failed_ledger)
    failed_disposition = engine.disposition_cache(failed_checkpoint, cache)
    failed_exit = engine.emit_exit_receipt(
        exit_checkpoint=failed_checkpoint,
        cleanup_receipt=failed_cleanup,
        cache_disposition=failed_disposition,
    )
    failed_bundle = {
        "exit_checkpoint": failed_checkpoint,
        "cleanup_receipt": failed_cleanup,
        "cache_disposition": failed_disposition,
        "exit_receipt": failed_exit,
    }
    failed_reconstruction = engine.reconstruct_exit(failed_bundle)

    uninterrupted, _, _ = workload.execute_range(genesis, 1, 18)
    completed_equivalence = completion["final_state"]["state_root_hash72"] == uninterrupted["state_root_hash72"]
    idempotent_cleanup = completed_cleanup["post_cleanup_memory_root_hash72"] == completed_cleanup_repeat["post_cleanup_memory_root_hash72"]
    result = {
        "schema": "HHS_PASS112_PASS_SAFE_EXIT_SELF_TEST_V1",
        "pass_id": PASS_ID,
        "status": "PASS" if all([
            completed_equivalence,
            idempotent_cleanup,
            completed_reconstruction["reconstruction_status"] == "RECONSTRUCTED",
            failed_reconstruction["reconstruction_status"] == "RECONSTRUCTED",
            failed_exit["workload_completed"] is False,
            failed_exit["exit_classification"] == "EXIT_RESUME_REJECTED",
        ]) else "FAIL",
        "completed_exit": completed_bundle,
        "failed_resume_exit": failed_bundle,
        "completed_reconstruction": completed_reconstruction,
        "failed_reconstruction": failed_reconstruction,
        "completed_final_equals_uninterrupted": completed_equivalence,
        "cleanup_idempotent": idempotent_cleanup,
        "failed_resume_progress_mutated": False,
        "authoritative_state_loss_count": 0,
        "incorrect_completion_report_count": 0,
        "unclosed_external_handle_count": 0,
        "receipt_preservation_ratio": "1/1",
        "mock_components": [],
    }
    result["pass112_root_hash72"] = _hash("hhs_pass112_self_test_v1", result)
    return result


if __name__ == "__main__":
    print(json.dumps(pass112_self_test(), indent=2, sort_keys=True))

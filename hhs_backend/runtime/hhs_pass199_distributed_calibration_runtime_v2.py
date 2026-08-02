"""Pass 199 V2: atomic durable worker-slot registration and 64-claim batches."""
from __future__ import annotations

import copy
import os
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass199_distributed_calibration_fabric_v1 import (
    BRANCH_OPERATION_ID,
    COMMIT_OPERATION_ID,
    COMPLETE_OPERATION_ID,
    DEFAULT_DATABASE,
    DEFAULT_LEASE_TTL_NS,
    DEFAULT_LEASE_WAIT_NS,
    DEFAULT_REGISTRY,
    HHSAuthorityContext,
    PASS199_CAPABILITY,
    PASS199_OPERATION_IDS,
    RegistryValidationError,
    ResourceRegistryStore,
    StateConflictError,
    _EXECUTION_IMPLEMENTATIONS,
    _RESOURCE_IMPLEMENTATIONS,
    _pass199_operation,
    evaluate_branch_candidate,
)
from hhs_backend.runtime.hhs_pass199_distributed_calibration_runtime_v1 import (
    BATCH_CLAIM_OPERATION_ID,
    BATCH_COMPLETE_OPERATION_ID,
    BATCH_OPERATION_IDS,
    Pass199BatchOperationRegistry,
    Pass199DistributedCalibrationRuntime as Pass199DistributedCalibrationRuntimeV1,
)
from hhs_pass190 import ArgumentValidationError, OperationRecord
from hhs_pass190_iteration7_registry import WORKER_SCHEMA

ENSURE_WORKERS_OPERATION_ID = "calibration.ensure_workers"
V2_CONTRACT = "HHS-P199-P198-P190-DCT-WORKER-SLOTS64-VM81-H72"


def _ensure_workers_record() -> dict[str, Any]:
    return _pass199_operation(
        ENSURE_WORKERS_OPERATION_ID,
        "Ensure durable calibration worker slots atomically",
        "CalibrationEnsureWorkers",
        "worker:admin",
        "mutation",
        {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "worker_ids": {
                    "type": "array",
                    "maxItems": 64,
                    "items": {"type": "string", "maxLength": 256},
                },
                "now_ns": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 9_223_372_036_854_775_807,
                },
                "lease_timeout_ns": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 3_600_000_000_000,
                },
            },
            "required": ["worker_ids", "now_ns", "lease_timeout_ns"],
        },
        "calibration-ensure-workers",
    )


ENSURE_WORKERS_RECORD = _ensure_workers_record()


class Pass199WorkerSlotRegistry(Pass199BatchOperationRegistry):
    """Pass 199 registry with one additional atomic worker-slot mutation."""

    def __init__(self, registry_path: Any = DEFAULT_REGISTRY) -> None:
        parent = Pass199BatchOperationRegistry(registry_path)
        combined = [copy.deepcopy(dict(record.raw)) for record in parent.records]
        combined.append(copy.deepcopy(ENSURE_WORKERS_RECORD))
        identity = {
            "schema": parent.payload["schema"],
            "contract": V2_CONTRACT,
            "parent_contract": parent.payload.get("contract"),
            "parent_registry_hash216": parent.payload.get("registry_hash216"),
            "pass": 199,
            "operations": combined,
        }
        from hhs_backend.runtime.hhs_pass199_distributed_calibration_fabric_v1 import pass190_hash216

        self.payload = {
            **identity,
            "registry_hash216": pass190_hash216("pass199.worker.slot.registry", identity),
            "native_operation_count": int(parent.payload["native_operation_count"]),
            "governed_operation_count": len(combined),
            "execution_operation_count": int(parent.payload["execution_operation_count"]),
            "distributed_calibration_operation_count": int(parent.payload["distributed_calibration_operation_count"]) + 1,
        }
        self.records = tuple(OperationRecord(record) for record in combined)
        self.by_id = {}
        self.by_constructor = {}
        self.by_python = {}
        self.by_shell = {}
        self._validate_and_index()
        expected_tail = (*PASS199_OPERATION_IDS, *BATCH_OPERATION_IDS, ENSURE_WORKERS_OPERATION_ID)
        if tuple(record.operation_id for record in self.records[-len(expected_tail):]) != expected_tail:
            raise RegistryValidationError("Pass 199 V2 operation order mismatch")


class Pass199WorkerSlotContext(
    __import__(
        "hhs_backend.runtime.hhs_pass199_distributed_calibration_runtime_v1",
        fromlist=["RestartSafePass199DurableCalibrationContext"],
    ).RestartSafePass199DurableCalibrationContext
):
    """Durable authority with atomic worker-slot registration."""

    def __init__(
        self,
        database_path: Any = DEFAULT_DATABASE,
        registry_path: Any = DEFAULT_REGISTRY,
        *,
        holder_id: str | None = None,
        lease_ttl_ns: int = DEFAULT_LEASE_TTL_NS,
        lease_wait_ns: int = DEFAULT_LEASE_WAIT_NS,
        clock_ns: Any = time.time_ns,
        sleeper: Any = time.sleep,
    ) -> None:
        self.holder_id = holder_id or f"pass199-slots:{os.getpid()}:{uuid.uuid4().hex}"
        self.lease_ttl_ns = lease_ttl_ns
        self.lease_wait_ns = lease_wait_ns
        self.store = ResourceRegistryStore(database_path, clock_ns=clock_ns, sleeper=sleeper)
        HHSAuthorityContext.__init__(self, registry_path)
        self.registry = Pass199WorkerSlotRegistry(registry_path)
        self._implementations.update({name: getattr(self, method) for name, method in _RESOURCE_IMPLEMENTATIONS.items()})
        self._implementations.update({name: getattr(self, method) for name, method in _EXECUTION_IMPLEMENTATIONS.items()})
        self._implementations.update(
            {
                BRANCH_OPERATION_ID: self._op_calibration_evaluate_branch,
                COMPLETE_OPERATION_ID: self._op_calibration_complete_claimed,
                COMMIT_OPERATION_ID: self._op_calibration_commit_tree,
                BATCH_OPERATION_IDS[0]: self._op_calibration_submit_tree,
                BATCH_CLAIM_OPERATION_ID: self._op_calibration_claim_batch,
                BATCH_COMPLETE_OPERATION_ID: self._op_calibration_complete_batch,
                ENSURE_WORKERS_OPERATION_ID: self._op_calibration_ensure_workers,
            }
        )
        if set(self._implementations) != set(self.registry.by_id):
            missing = set(self.registry.by_id) - set(self._implementations)
            extra = set(self._implementations) - set(self.registry.by_id)
            raise RegistryValidationError(
                f"Pass 199 V2 registry mismatch missing={sorted(missing)} extra={sorted(extra)}"
            )
        self.store.restore_into(self)

    def _op_calibration_ensure_workers(self, args: dict[str, Any]) -> dict[str, Any]:
        worker_ids = [self._identifier(value, "worker_id") for value in args["worker_ids"]]
        if not worker_ids or len(worker_ids) != len(set(worker_ids)):
            raise ArgumentValidationError("worker_ids must contain unique workers")
        definitions = self._resource_registries()["capabilities"]
        if PASS199_CAPABILITY not in definitions:
            raise ArgumentValidationError(f"undefined worker capability: {PASS199_CAPABILITY}")
        current_workers = self._execution_runtime()["workers"]
        payloads: dict[str, Mapping[str, Any]] = {}
        existing = 0
        for worker_id in worker_ids:
            current = current_workers.get(worker_id)
            if current is None:
                payloads[worker_id] = {
                    "schema": WORKER_SCHEMA,
                    "worker_id": worker_id,
                    "capabilities": [PASS199_CAPABILITY],
                    "labels": ["pass199", "immutable-candidate", "durable-slot"],
                    "enabled": True,
                    "registered_at_ns": int(args["now_ns"]),
                    "last_heartbeat_ns": int(args["now_ns"]),
                    "lease_timeout_ns": int(args["lease_timeout_ns"]),
                    "current_job_id": None,
                    "current_claim_token_hash72": None,
                    "completed_job_count": 0,
                    "failed_attempt_count": 0,
                    "version": 1,
                }
                continue
            existing += 1
            if current.get("current_job_id") is not None:
                raise StateConflictError(f"worker slot is already active: {worker_id}")
            capabilities = sorted(set(current.get("capabilities", [])) | {PASS199_CAPABILITY})
            payloads[worker_id] = self._updated_payload(
                current,
                {
                    "capabilities": capabilities,
                    "enabled": True,
                    "last_heartbeat_ns": max(int(current["last_heartbeat_ns"]), int(args["now_ns"])),
                    "lease_timeout_ns": int(args["lease_timeout_ns"]),
                },
            )
        _jobs, committed = self._commit_execution_records(worker_payloads=payloads)
        return {
            "worker_slot_count": len(worker_ids),
            "created_or_refreshed_count": len(committed),
            "existing_worker_count": existing,
            "one_job_per_worker": True,
            "atomic_state_commit": True,
            "state_root": self._state_root,
        }


class Pass199DistributedCalibrationRuntime(Pass199DistributedCalibrationRuntimeV1):
    """Pass 199 production runtime with 64 durable slots and bounded compute threads."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.context.close()
        self.context = Pass199WorkerSlotContext(
            self.database_path,
            holder_id="pass199-worker-slot-runtime",
        )

    def execute_workers(self, prepared: Mapping[str, Any], *, worker_count: int = 4) -> dict[str, Any]:
        if not 1 <= worker_count <= 64:
            raise ValueError("worker_count must be in [1,64]")
        claim_slot_count = min(64, int(prepared["expected_job_count"]))
        worker_ids = [f"p199.slot.{index:02d}" for index in range(claim_slot_count)]
        self._invoke(
            self.context,
            ENSURE_WORKERS_OPERATION_ID,
            {
                "worker_ids": worker_ids,
                "now_ns": time.time_ns(),
                "lease_timeout_ns": 300_000_000_000,
            },
            "worker:admin",
        )
        active = 0
        peak = 0
        active_lock = threading.Lock()
        completed_ids: list[str] = []
        claim_batch_count = 0
        completion_batch_count = 0

        def compute(claim: Mapping[str, Any]) -> dict[str, Any]:
            nonlocal active, peak
            with active_lock:
                active += 1
                peak = max(peak, active)
            try:
                return {
                    "job_id": claim["job_id"],
                    "worker_id": claim["worker_id"],
                    "claim_token_hash72": claim["claim_token_hash72"],
                    "candidate_result": evaluate_branch_candidate(claim["job"]["arguments"]),
                }
            finally:
                with active_lock:
                    active -= 1

        while True:
            claim_result = self._invoke(
                self.context,
                BATCH_CLAIM_OPERATION_ID,
                {
                    "workspace_id": prepared["workspace_id"],
                    "worker_ids": worker_ids,
                    "now_ns": time.time_ns(),
                    "lease_duration_ns": 300_000_000_000,
                },
                "worker:execute",
            ).result
            if not claim_result["claimed"]:
                break
            claim_batch_count += 1
            claims = claim_result["claims"]
            with ThreadPoolExecutor(max_workers=min(worker_count, len(claims))) as pool:
                completions = list(pool.map(compute, claims))
            completion_result = self._invoke(
                self.context,
                BATCH_COMPLETE_OPERATION_ID,
                {"completions": completions, "now_ns": time.time_ns()},
                "worker:execute",
            ).result
            completion_batch_count += 1
            completed_ids.extend(item["job_id"] for item in completion_result["completions"])
        return {
            "worker_count": worker_count,
            "compute_worker_count": worker_count,
            "durable_worker_slot_count": claim_slot_count,
            "completed_job_count": len(completed_ids),
            "completed_job_ids": sorted(completed_ids),
            "peak_parallel_candidate_workers": peak,
            "candidate_computation_outside_authority_lock": True,
            "one_job_per_worker": True,
            "claim_batch_count": claim_batch_count,
            "completion_batch_count": completion_batch_count,
            "authority_mutations_reduced": True,
            "maximum_claim_batch_size": 64,
        }


PASS199_DISTRIBUTED_CALIBRATION_RUNTIME = Pass199DistributedCalibrationRuntime()

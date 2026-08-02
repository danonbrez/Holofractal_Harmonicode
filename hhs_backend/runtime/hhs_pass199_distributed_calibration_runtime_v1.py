"""Restart-safe batched durable execution runtime for Pass 199."""
from __future__ import annotations

import copy
import json
import os
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass199_distributed_calibration_fabric_v1 import (
    ADDRESS_COUNT,
    BRANCH_OPERATION_ID,
    COMMIT_OPERATION_ID,
    COMPLETE_OPERATION_ID,
    CONTRACT,
    DEFAULT_DATABASE,
    DEFAULT_LEASE_TTL_NS,
    DEFAULT_LEASE_WAIT_NS,
    DEFAULT_REGISTRY,
    HHSAuthorityContext,
    PASS199_ADMISSION_CAPABILITY,
    PASS199_CAPABILITY,
    PASS199_OPERATION_IDS,
    REGISTRY_SCHEMA,
    VERSION,
    OperationRecord,
    Pass199DistributedCalibrationFabric,
    Pass199DurableCalibrationContext,
    Pass199OperationRegistry,
    RegistryValidationError,
    ResourceRegistryStore,
    StateConflictError,
    _EXECUTION_IMPLEMENTATIONS,
    _RESOURCE_IMPLEMENTATIONS,
    _pass199_operation,
    evaluate_branch_candidate,
    hhs_hash72,
    pass190_hash72,
    pass190_hash216,
)
from hhs_pass190 import ArgumentValidationError, _validate_schema
from hhs_pass190_iteration6 import RESOURCE_SCHEMAS
from hhs_pass190_iteration7_registry import EXECUTION_JOB_SCHEMA_VERSION

BATCH_SUBMIT_OPERATION_ID = "calibration.submit_tree"
BATCH_CLAIM_OPERATION_ID = "calibration.claim_batch"
BATCH_COMPLETE_OPERATION_ID = "calibration.complete_batch"
BATCH_OPERATION_IDS = (
    BATCH_SUBMIT_OPERATION_ID,
    BATCH_CLAIM_OPERATION_ID,
    BATCH_COMPLETE_OPERATION_ID,
)
BATCH_CONTRACT = "HHS-P199-P198-P190-DCT-BATCH-WORKER-VM81-H72"


def _rational_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "numerator": {"type": "integer"},
            "denominator": {"type": "integer"},
        },
        "required": ["numerator", "denominator"],
    }


def _batch_operation_records() -> tuple[dict[str, Any], ...]:
    exact_ns = {"type": "integer", "minimum": 0, "maximum": 9_223_372_036_854_775_807}
    identifier = {"type": "string", "maxLength": 256}
    state = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "ordinal": {"type": "integer", "minimum": 0, "maximum": 49_999},
            "x": _rational_schema(),
            "y": _rational_schema(),
            "xy_symbol": {"type": "integer", "minimum": -16, "maximum": 16},
        },
        "required": ["ordinal", "x", "y", "xy_symbol"],
    }
    completion = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "job_id": identifier,
            "worker_id": identifier,
            "claim_token_hash72": {"type": "string", "maxLength": 72},
            "candidate_result": {"type": "object"},
        },
        "required": ["job_id", "worker_id", "claim_token_hash72", "candidate_result"],
    }
    return (
        _pass199_operation(
            BATCH_SUBMIT_OPERATION_ID,
            "Submit complete durable calibration tree",
            "CalibrationSubmitTree",
            "job:write",
            "mutation",
            {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "run_id": identifier,
                    "workspace_id": identifier,
                    "operation_id": identifier,
                    "operation_spec_hash72": {"type": "string", "maxLength": 72},
                    "tree_hash72": {"type": "string", "maxLength": 72},
                    "submitted_at_ns": exact_ns,
                    "states": {"type": "array", "maxItems": 50_000, "items": state},
                },
                "required": [
                    "run_id", "workspace_id", "operation_id", "operation_spec_hash72",
                    "tree_hash72", "submitted_at_ns", "states",
                ],
            },
            "calibration-submit-tree",
        ),
        _pass199_operation(
            BATCH_CLAIM_OPERATION_ID,
            "Claim one calibration job per worker atomically",
            "CalibrationClaimBatch",
            "worker:execute",
            "mutation",
            {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "workspace_id": identifier,
                    "worker_ids": {"type": "array", "maxItems": 64, "items": identifier},
                    "now_ns": exact_ns,
                    "lease_duration_ns": {"type": "integer", "minimum": 1, "maximum": 3_600_000_000_000},
                },
                "required": ["workspace_id", "worker_ids", "now_ns", "lease_duration_ns"],
            },
            "calibration-claim-batch",
        ),
        _pass199_operation(
            BATCH_COMPLETE_OPERATION_ID,
            "Complete a claimed calibration worker batch atomically",
            "CalibrationCompleteBatch",
            "worker:execute",
            "mutation",
            {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "completions": {"type": "array", "maxItems": 64, "items": completion},
                    "now_ns": exact_ns,
                },
                "required": ["completions", "now_ns"],
            },
            "calibration-complete-batch",
        ),
    )


BATCH_OPERATION_RECORDS = _batch_operation_records()


class Pass199BatchOperationRegistry(Pass199OperationRegistry):
    """Pass 199 registry with atomic submission, claim, and completion batches."""

    def __init__(self, registry_path: Any = DEFAULT_REGISTRY) -> None:
        parent = Pass199OperationRegistry(registry_path)
        combined = [copy.deepcopy(dict(record.raw)) for record in parent.records]
        combined.extend(copy.deepcopy(record) for record in BATCH_OPERATION_RECORDS)
        identity = {
            "schema": REGISTRY_SCHEMA,
            "contract": BATCH_CONTRACT,
            "parent_contract": parent.payload.get("contract"),
            "parent_registry_hash216": parent.payload.get("registry_hash216"),
            "pass": 199,
            "operations": combined,
        }
        self.payload = {
            **identity,
            "registry_hash216": pass190_hash216("pass199.batch.operation.registry", identity),
            "native_operation_count": int(parent.payload["native_operation_count"]),
            "governed_operation_count": len(combined),
            "execution_operation_count": int(parent.payload["execution_operation_count"]),
            "distributed_calibration_operation_count": len(PASS199_OPERATION_IDS) + len(BATCH_OPERATION_IDS),
        }
        self.records = tuple(OperationRecord(record) for record in combined)
        self.by_id = {}
        self.by_constructor = {}
        self.by_python = {}
        self.by_shell = {}
        self._validate_and_index()
        expected_tail = (*PASS199_OPERATION_IDS, *BATCH_OPERATION_IDS)
        if tuple(record.operation_id for record in self.records[-len(expected_tail):]) != expected_tail:
            raise RegistryValidationError("Pass 199 batch operation order mismatch")


class RestartSafePass199DurableCalibrationContext(Pass199DurableCalibrationContext):
    """Pass 199 authority with bounded batched worker mutations."""

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
        self.holder_id = holder_id or f"pass199-batch:{os.getpid()}:{uuid.uuid4().hex}"
        self.lease_ttl_ns = lease_ttl_ns
        self.lease_wait_ns = lease_wait_ns
        self.store = ResourceRegistryStore(database_path, clock_ns=clock_ns, sleeper=sleeper)
        HHSAuthorityContext.__init__(self, registry_path)
        self.registry = Pass199BatchOperationRegistry(registry_path)
        self._implementations.update({name: getattr(self, method) for name, method in _RESOURCE_IMPLEMENTATIONS.items()})
        self._implementations.update({name: getattr(self, method) for name, method in _EXECUTION_IMPLEMENTATIONS.items()})
        self._implementations.update(
            {
                BRANCH_OPERATION_ID: self._op_calibration_evaluate_branch,
                COMPLETE_OPERATION_ID: self._op_calibration_complete_claimed,
                COMMIT_OPERATION_ID: self._op_calibration_commit_tree,
                BATCH_SUBMIT_OPERATION_ID: self._op_calibration_submit_tree,
                BATCH_CLAIM_OPERATION_ID: self._op_calibration_claim_batch,
                BATCH_COMPLETE_OPERATION_ID: self._op_calibration_complete_batch,
            }
        )
        if set(self._implementations) != set(self.registry.by_id):
            missing = set(self.registry.by_id) - set(self._implementations)
            extra = set(self._implementations) - set(self.registry.by_id)
            raise RegistryValidationError(
                f"Pass 199 batch registry mismatch missing={sorted(missing)} extra={sorted(extra)}"
            )
        self.store.restore_into(self)

    def find_tree_commit_receipt(self, run_id: str) -> dict[str, Any] | None:
        cursor = 0
        match: dict[str, Any] | None = None
        while True:
            page = self.receipts_after(cursor, 1000)
            if not page:
                break
            for receipt in page:
                if receipt.get("operation_id") == COMMIT_OPERATION_ID and receipt.get("arguments", {}).get("run_id") == run_id:
                    self._verify_receipt_identity(receipt)
                    match = copy.deepcopy(receipt)
            cursor = int(page[-1]["receipt_index"])
        return match

    def _job_payload(
        self,
        *,
        job_id: str,
        workspace_id: str,
        operation: Any,
        arguments: Mapping[str, Any],
        submitted_at_ns: int,
        metadata: Mapping[str, Any],
    ) -> dict[str, Any]:
        _validate_schema(arguments, operation.argument_schema)
        definitions = self._resource_registries()["capabilities"]
        if PASS199_CAPABILITY not in definitions:
            raise ArgumentValidationError(f"undefined required capability: {PASS199_CAPABILITY}")
        request = {
            "workspace_id": workspace_id,
            "operation_id": operation.operation_id,
            "operation_hash216": operation.raw["Hash216_identity"],
            "arguments": copy.deepcopy(dict(arguments)),
            "dependency_job_ids": [],
            "input_artifact_ids": [],
            "required_capabilities": [PASS199_CAPABILITY],
            "submitted_at_ns": submitted_at_ns,
            "schedule_not_before_ns": submitted_at_ns,
            "max_attempts": 3,
            "retry_backoff_ns": 0,
            "priority": 0,
        }
        return {
            "schema": RESOURCE_SCHEMAS["jobs"],
            "execution_schema_version": EXECUTION_JOB_SCHEMA_VERSION,
            "job_id": job_id,
            **request,
            "execution_request": copy.deepcopy(request),
            "execution_request_hash72": pass190_hash72("pass190.job.execution.request", request),
            "request_hash72": pass190_hash72("pass190.job.request", request),
            "provider_id": None,
            "metadata": copy.deepcopy(dict(metadata)),
            "status": "queued",
            "attempt": 0,
            "next_attempt_ns": submitted_at_ns,
            "worker_id": None,
            "claim_token_hash72": None,
            "lease_expires_ns": None,
            "cancel_requested": False,
            "started_at_ns": None,
            "finished_at_ns": None,
            "result": None,
            "error": None,
            "execution_hash72": None,
            "output_artifact_ids": [],
            "version": 1,
        }

    def _op_calibration_submit_tree(self, args: dict[str, Any]) -> dict[str, Any]:
        workspace_id = self._identifier(args["workspace_id"], "workspace_id")
        self._active_workspace(workspace_id)
        if args["operation_id"] != "pass197.reciprocal_matrix_gate":
            raise StateConflictError("Pass 199 batch adapter is not registered for operation")
        operation = self.registry.resolve(BRANCH_OPERATION_ID)
        if operation.effect_class != "pure":
            raise StateConflictError("calibration branch operation must remain pure")
        jobs = self._resource_registries()["jobs"]
        payloads: dict[str, dict[str, Any]] = {}
        existing = 0
        ordinals: list[int] = []
        for state in args["states"]:
            ordinal = int(state["ordinal"])
            ordinals.append(ordinal)
            for branch in ("A", "B"):
                job_id = f"p199.{args['run_id'][:20]}.{ordinal:05d}.{branch.lower()}"
                arguments = {
                    "run_id": args["run_id"],
                    "operation_id": args["operation_id"],
                    "operation_spec_hash72": args["operation_spec_hash72"],
                    "tree_hash72": args["tree_hash72"],
                    "ordinal": ordinal,
                    "branch": branch,
                    "x": copy.deepcopy(state["x"]),
                    "y": copy.deepcopy(state["y"]),
                    "xy_symbol": int(state["xy_symbol"]),
                }
                current = jobs.get(job_id)
                if current is not None:
                    if current.get("workspace_id") != workspace_id or current.get("arguments") != arguments:
                        raise StateConflictError(f"existing job conflicts with tree identity: {job_id}")
                    existing += 1
                    continue
                payloads[job_id] = self._job_payload(
                    job_id=job_id,
                    workspace_id=workspace_id,
                    operation=operation,
                    arguments=arguments,
                    submitted_at_ns=int(args["submitted_at_ns"]),
                    metadata={
                        "pass199_run_id": args["run_id"],
                        "ordinal": ordinal,
                        "branch": branch,
                        "tree_hash72": args["tree_hash72"],
                        "deterministic_schedule_key": job_id,
                        "contract": CONTRACT,
                    },
                )
        if sorted(ordinals) != list(range(len(args["states"]))):
            raise StateConflictError("batch parameter ordinals must be contiguous and canonical")
        committed, _workers = self._commit_execution_records(job_payloads=payloads) if payloads else ({}, {})
        body = {
            "run_id": args["run_id"],
            "workspace_id": workspace_id,
            "tree_hash72": args["tree_hash72"],
            "state_count": len(args["states"]),
            "expected_job_count": len(args["states"]) * 2,
            "submitted_job_count": len(committed),
            "existing_job_count": existing,
            "atomic_state_commit": True,
            "individual_jobs_remain_durable": True,
        }
        return {**body, "batch_hash72": pass190_hash72("pass199.batch.submission", body)}

    def _op_calibration_claim_batch(self, args: dict[str, Any]) -> dict[str, Any]:
        workspace_id = self._identifier(args["workspace_id"], "workspace_id")
        worker_ids = [self._identifier(value, "worker_id") for value in args["worker_ids"]]
        if not worker_ids or len(worker_ids) != len(set(worker_ids)):
            raise ArgumentValidationError("worker_ids must contain unique workers")
        now_ns = int(args["now_ns"])
        job_payloads, scheduler_workers, _counts, _changed = self._scheduler_payloads(now_ns, 1000)
        if job_payloads or scheduler_workers:
            self._commit_execution_records(job_payloads=job_payloads, worker_payloads=scheduler_workers)
        workers = {worker_id: self._worker_lookup(worker_id) for worker_id in worker_ids}
        for worker_id, worker in workers.items():
            if not worker["enabled"]:
                raise StateConflictError(f"worker is disabled: {worker_id}")
            if now_ns > int(worker["last_heartbeat_ns"]) + int(worker["lease_timeout_ns"]):
                raise StateConflictError(f"worker heartbeat lease expired: {worker_id}")
            if worker.get("current_job_id") is not None:
                raise StateConflictError(f"worker already owns a running job: {worker_id}")
        eligible = [
            job for job in self._resource_registries()["jobs"].values()
            if self._is_execution_job(job)
            and job["status"] == "queued"
            and job.get("provider_id") is None
            and job["workspace_id"] == workspace_id
            and now_ns >= int(job["next_attempt_ns"])
            and self._dependency_state(job) == (True, [])
        ]
        eligible.sort(key=lambda item: (-int(item["priority"]), item["job_id"]))
        claimed_jobs: dict[str, Mapping[str, Any]] = {}
        claimed_workers: dict[str, Mapping[str, Any]] = {}
        claim_records: list[dict[str, Any]] = []
        available = list(eligible)
        for worker_id in worker_ids:
            worker = workers[worker_id]
            index = next(
                (
                    idx for idx, job in enumerate(available)
                    if set(job["required_capabilities"]).issubset(set(worker["capabilities"]))
                ),
                None,
            )
            if index is None:
                continue
            job = available.pop(index)
            attempt = int(job["attempt"]) + 1
            if attempt > int(job["max_attempts"]):
                raise StateConflictError(f"job exhausted its attempt budget: {job['job_id']}")
            lease_duration = min(int(args["lease_duration_ns"]), int(worker["lease_timeout_ns"]))
            claim_payload = {
                "job_id": job["job_id"],
                "worker_id": worker_id,
                "attempt": attempt,
                "claimed_at_ns": now_ns,
                "lease_duration_ns": lease_duration,
                "preclaim_state_root": self._state_root,
            }
            claim_token = pass190_hash72("pass190.execution.claim", claim_payload)
            claimed_jobs[job["job_id"]] = self._updated_payload(
                job,
                {
                    "status": "running",
                    "attempt": attempt,
                    "worker_id": worker_id,
                    "claim_token_hash72": claim_token,
                    "lease_expires_ns": now_ns + lease_duration,
                    "cancel_requested": False,
                    "started_at_ns": now_ns,
                    "finished_at_ns": None,
                },
            )
            claimed_workers[worker_id] = self._updated_payload(
                worker,
                {
                    "current_job_id": job["job_id"],
                    "current_claim_token_hash72": claim_token,
                    "last_heartbeat_ns": max(int(worker["last_heartbeat_ns"]), now_ns),
                },
            )
            claim_records.append(
                {
                    "job_id": job["job_id"],
                    "worker_id": worker_id,
                    "claim_token_hash72": claim_token,
                }
            )
        if not claim_records:
            return {"claimed": False, "claims": [], "state_root": self._state_root}
        committed_jobs, _committed_workers = self._commit_execution_records(
            job_payloads=claimed_jobs,
            worker_payloads=claimed_workers,
        )
        claims = [
            {
                **record,
                "job": committed_jobs[record["job_id"]],
            }
            for record in claim_records
        ]
        return {
            "claimed": True,
            "claims": claims,
            "claim_count": len(claims),
            "one_job_per_worker": True,
            "state_root": self._state_root,
        }

    def _op_calibration_complete_batch(self, args: dict[str, Any]) -> dict[str, Any]:
        completions = args["completions"]
        if not completions:
            raise ArgumentValidationError("completions must not be empty")
        job_ids = [self._identifier(item["job_id"], "job_id") for item in completions]
        worker_ids = [self._identifier(item["worker_id"], "worker_id") for item in completions]
        if len(job_ids) != len(set(job_ids)) or len(worker_ids) != len(set(worker_ids)):
            raise ArgumentValidationError("batch completion jobs and workers must be unique")
        now_ns = int(args["now_ns"])
        job_payloads: dict[str, Mapping[str, Any]] = {}
        worker_payloads: dict[str, Mapping[str, Any]] = {}
        completed: list[dict[str, Any]] = []
        for item in completions:
            job_id = self._identifier(item["job_id"], "job_id")
            worker_id = self._identifier(item["worker_id"], "worker_id")
            job = self._lookup("jobs", job_id)
            worker = self._worker_lookup(worker_id)
            token = item["claim_token_hash72"]
            if job.get("operation_id") != BRANCH_OPERATION_ID or job.get("status") != "running":
                raise StateConflictError(f"job is not a running calibration branch: {job_id}")
            if job.get("worker_id") != worker_id or job.get("claim_token_hash72") != token:
                raise StateConflictError(f"job claim token mismatch: {job_id}")
            if worker.get("current_job_id") != job_id or worker.get("current_claim_token_hash72") != token:
                raise StateConflictError(f"worker claim token mismatch: {worker_id}")
            if now_ns >= int(job["lease_expires_ns"]):
                raise StateConflictError(f"candidate completion lease expired: {job_id}")
            if not worker["enabled"] or now_ns > int(worker["last_heartbeat_ns"]) + int(worker["lease_timeout_ns"]):
                raise StateConflictError(f"worker authority expired: {worker_id}")
            candidate = copy.deepcopy(item["candidate_result"])
            self._validate_candidate_binding(job, candidate)
            execution = {
                "job_id": job_id,
                "worker_id": worker_id,
                "attempt": job["attempt"],
                "execution_request_hash72": job["execution_request_hash72"],
                "candidate_hash72": candidate["candidate_hash72"],
                "finished_at_ns": now_ns,
            }
            execution_hash = pass190_hash72("pass199.candidate.execution", execution)
            job_payloads[job_id] = self._updated_payload(
                job,
                {
                    "status": "completed",
                    "result": candidate,
                    "error": None,
                    "execution_hash72": execution_hash,
                    "worker_id": None,
                    "claim_token_hash72": None,
                    "lease_expires_ns": None,
                    "finished_at_ns": now_ns,
                },
            )
            worker_payloads[worker_id] = self._updated_payload(
                worker,
                {
                    "current_job_id": None,
                    "current_claim_token_hash72": None,
                    "last_heartbeat_ns": max(int(worker["last_heartbeat_ns"]), now_ns),
                    "completed_job_count": int(worker["completed_job_count"]) + 1,
                },
            )
            completed.append(
                {
                    "job_id": job_id,
                    "worker_id": worker_id,
                    "candidate_hash72": candidate["candidate_hash72"],
                    "execution_hash72": execution_hash,
                }
            )
        committed_jobs, _committed_workers = self._commit_execution_records(
            job_payloads=job_payloads,
            worker_payloads=worker_payloads,
        )
        return {
            "completed": True,
            "completion_count": len(completed),
            "completions": [
                {**item, "job_status": committed_jobs[item["job_id"]]["status"]}
                for item in completed
            ],
            "candidate_workers_are_authority": False,
            "state_root": self._state_root,
        }


class Pass199DistributedCalibrationRuntime(Pass199DistributedCalibrationFabric):
    """Public runtime preserving exact durable jobs with bounded authority mutations."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.context.close()
        self.context = RestartSafePass199DurableCalibrationContext(
            self.database_path,
            holder_id="pass199-public-runtime",
        )

    def prepare_tree(self, operation_id: str, config_payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        operation = self.pass198.get_operation(operation_id)
        tree = self.pass198.parameter_tree(operation_id, config_payload)
        run_id = pass190_hash72(
            "pass199.distributed.run",
            {
                "version": VERSION,
                "operation_id": operation_id,
                "spec_hash72": operation["spec_hash72"],
                "tree_hash72": tree["tree_hash72"],
            },
        )
        workspace_id = f"calibration.{run_id[:32]}"
        self._ensure_capability(PASS199_CAPABILITY)
        self._ensure_capability(PASS199_ADMISSION_CAPABILITY)
        self._ensure_workspace(workspace_id)
        submission = self._invoke(
            self.context,
            BATCH_SUBMIT_OPERATION_ID,
            {
                "run_id": run_id,
                "workspace_id": workspace_id,
                "operation_id": operation_id,
                "operation_spec_hash72": operation["spec_hash72"],
                "tree_hash72": tree["tree_hash72"],
                "submitted_at_ns": time.time_ns(),
                "states": [
                    {
                        "ordinal": int(state["ordinal"]),
                        "x": state["x"],
                        "y": state["y"],
                        "xy_symbol": int(state["xy_symbol"]),
                    }
                    for state in tree["states"]
                ],
            },
            "job:write",
        ).result
        return {
            "schema": "HHS_PASS_199_PREPARED_TREE_V1",
            "run_id": run_id,
            "workspace_id": workspace_id,
            "operation": operation,
            "tree": tree,
            "expected_job_count": int(tree["state_count"]) * 2,
            "submitted_job_count": int(submission["submitted_job_count"]),
            "existing_job_count": int(submission["existing_job_count"]),
            "submission_receipt_mode": "ONE_GOVERNED_BATCH_RECEIPT",
            "individual_jobs_remain_durable": True,
            "deterministic_ordering": "CANONICAL_JOB_ID_THEN_ORDINAL_COMMIT",
        }

    def execute_workers(self, prepared: Mapping[str, Any], *, worker_count: int = 4) -> dict[str, Any]:
        if not 1 <= worker_count <= 64:
            raise ValueError("worker_count must be in [1,64]")
        worker_ids = [f"p199.worker.{index:02d}" for index in range(worker_count)]
        now = time.time_ns()
        for worker_id in worker_ids:
            self._ensure_worker(worker_id, now)
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
                candidate = evaluate_branch_candidate(claim["job"]["arguments"])
                return {
                    "job_id": claim["job_id"],
                    "worker_id": claim["worker_id"],
                    "claim_token_hash72": claim["claim_token_hash72"],
                    "candidate_result": candidate,
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
            "completed_job_count": len(completed_ids),
            "completed_job_ids": sorted(completed_ids),
            "peak_parallel_candidate_workers": peak,
            "candidate_computation_outside_authority_lock": True,
            "one_job_per_worker": True,
            "claim_batch_count": claim_batch_count,
            "completion_batch_count": completion_batch_count,
            "authority_mutations_reduced": True,
        }

    def run(
        self,
        operation_id: str = "pass197.reciprocal_matrix_gate",
        config_payload: Mapping[str, Any] | None = None,
        *,
        worker_count: int = 4,
        vm81_receipt_hash72: str | None = None,
        resume: bool = True,
        full_replay: bool = True,
    ) -> dict[str, Any]:
        prepared = self.prepare_tree(operation_id, config_payload)
        if resume and self.report_path.exists():
            prior = json.loads(self.report_path.read_text(encoding="utf-8"))
            identity = {
                key: value
                for key, value in prior.items()
                if key not in {"report_hash72", "pass198_run"}
            }
            expected = hhs_hash72("pass199.report", identity)
            if prior.get("run_id") == prepared["run_id"] and prior.get("report_hash72") == expected:
                self._last_report = prior
                return copy.deepcopy(prior)
        return super().run(
            operation_id,
            config_payload,
            worker_count=worker_count,
            vm81_receipt_hash72=vm81_receipt_hash72,
            resume=False,
            full_replay=full_replay,
        )


PASS199_DISTRIBUTED_CALIBRATION_RUNTIME = Pass199DistributedCalibrationRuntime()

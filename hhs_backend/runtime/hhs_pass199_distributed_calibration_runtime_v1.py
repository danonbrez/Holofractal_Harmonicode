"""Restart-safe public runtime and bounded batch submission for Pass 199."""
from __future__ import annotations

import copy
import json
import os
import time
import uuid
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass199_distributed_calibration_fabric_v1 import (
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
    hhs_hash72,
    pass190_hash72,
    pass190_hash216,
)
from hhs_pass190 import ArgumentValidationError, _validate_schema
from hhs_pass190_iteration6 import RESOURCE_SCHEMAS
from hhs_pass190_iteration7_registry import EXECUTION_JOB_SCHEMA_VERSION

BATCH_OPERATION_ID = "calibration.submit_tree"
BATCH_CONTRACT = "HHS-P199-P198-P190-DCT-BATCH-WORKER-VM81-H72"


def _batch_operation_record() -> dict[str, Any]:
    rational = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "numerator": {"type": "integer"},
            "denominator": {"type": "integer"},
        },
        "required": ["numerator", "denominator"],
    }
    state = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "ordinal": {"type": "integer", "minimum": 0, "maximum": 49_999},
            "x": rational,
            "y": rational,
            "xy_symbol": {"type": "integer", "minimum": -16, "maximum": 16},
        },
        "required": ["ordinal", "x", "y", "xy_symbol"],
    }
    return _pass199_operation(
        BATCH_OPERATION_ID,
        "Submit complete durable calibration tree",
        "CalibrationSubmitTree",
        "job:write",
        "mutation",
        {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "run_id": {"type": "string", "maxLength": 256},
                "workspace_id": {"type": "string", "maxLength": 256},
                "operation_id": {"type": "string", "maxLength": 256},
                "operation_spec_hash72": {"type": "string", "maxLength": 72},
                "tree_hash72": {"type": "string", "maxLength": 72},
                "submitted_at_ns": {"type": "integer", "minimum": 0, "maximum": 9_223_372_036_854_775_807},
                "states": {"type": "array", "maxItems": 50_000, "items": state},
            },
            "required": [
                "run_id", "workspace_id", "operation_id", "operation_spec_hash72",
                "tree_hash72", "submitted_at_ns", "states",
            ],
        },
        "calibration-submit-tree",
    )


BATCH_OPERATION_RECORD = _batch_operation_record()


class Pass199BatchOperationRegistry(Pass199OperationRegistry):
    """Pass 199 registry with one atomic durable-tree submission mutation."""

    def __init__(self, registry_path: Any = DEFAULT_REGISTRY) -> None:
        parent = Pass199OperationRegistry(registry_path)
        combined = [copy.deepcopy(dict(record.raw)) for record in parent.records]
        combined.append(copy.deepcopy(BATCH_OPERATION_RECORD))
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
            "distributed_calibration_operation_count": len(PASS199_OPERATION_IDS) + 1,
        }
        self.records = tuple(OperationRecord(record) for record in combined)
        self.by_id = {}
        self.by_constructor = {}
        self.by_python = {}
        self.by_shell = {}
        self._validate_and_index()
        if tuple(record.operation_id for record in self.records[-4:]) != (*PASS199_OPERATION_IDS, BATCH_OPERATION_ID):
            raise RegistryValidationError("Pass 199 batch operation order mismatch")


class RestartSafePass199DurableCalibrationContext(Pass199DurableCalibrationContext):
    """Pass 199 authority with batch submission and bounded receipt recovery."""

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
                BATCH_OPERATION_ID: self._op_calibration_submit_tree,
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
                if (
                    receipt.get("operation_id") == COMMIT_OPERATION_ID
                    and receipt.get("arguments", {}).get("run_id") == run_id
                ):
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


class Pass199DistributedCalibrationRuntime(Pass199DistributedCalibrationFabric):
    """Public runtime preserving bounded scheduler and resume identities."""

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
            BATCH_OPERATION_ID,
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

#!/usr/bin/env python3
"""Pass 190 Iteration 7 durable worker, scheduler, cancellation, and retry overlay."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from hhs_pass190 import DEFAULT_REGISTRY, REGISTRY_SCHEMA, OperationRecord, RegistryValidationError, hash216
from hhs_pass190_iteration6_registry import (
    ExpandedOperationRegistry,
    _object,
    _operation,
    _string,
    _string_array,
)

ITERATION7_CONTRACT = "HHS-P190-I7-DWE-DSCR-WL-VM81-H72-H216"
ITERATION7_CLASSIFICATION = "HHS_PASS_190_ITERATION_7_DURABLE_WORKER_EXECUTION_SCHEDULING_CANCELLATION_RETRY_VERIFIED"
EXECUTION_RUNTIME_SCHEMA = "HHS_PASS_190_EXECUTION_RUNTIME_V1"
WORKER_SCHEMA = "HHS_PASS_190_WORKER_V1"
EXECUTION_JOB_SCHEMA_VERSION = 1


def execution_operation_records() -> tuple[dict[str, Any], ...]:
    string = _string
    obj = _object()
    ids = _string_array()
    exact_ns = {"type": "integer", "minimum": 0, "maximum": 9_223_372_036_854_775_807}
    duration_ns = {"type": "integer", "minimum": 1, "maximum": 3_600_000_000_000}
    records = (
        _operation(
            "worker.register", "Register durable worker", "WorkerRegister", "worker:admin", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "worker_id": string(), "capabilities": ids, "labels": ids,
                "lease_timeout_ns": duration_ns, "now_ns": exact_ns,
            }, "required": ["worker_id", "now_ns"]},
            "object", "worker-register", operation_class="execution-worker",
        ),
        _operation(
            "worker.get", "Get durable worker", "WorkerGet", "worker:read", "pure",
            {"type": "object", "additionalProperties": False, "properties": {
                "worker_id": string(), "now_ns": exact_ns,
            }, "required": ["worker_id"]},
            "object", "worker-get", operation_class="execution-worker",
        ),
        _operation(
            "worker.list", "List durable workers", "WorkerList", "worker:read", "pure",
            {"type": "object", "additionalProperties": False, "properties": {
                "enabled_only": {"type": "boolean"}, "now_ns": exact_ns,
            }, "required": []},
            "array", "worker-list", operation_class="execution-worker",
        ),
        _operation(
            "worker.heartbeat", "Record worker heartbeat", "WorkerHeartbeat", "worker:execute", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "worker_id": string(), "now_ns": exact_ns,
            }, "required": ["worker_id", "now_ns"]},
            "object", "worker-heartbeat", operation_class="execution-worker",
        ),
        _operation(
            "worker.set_enabled", "Set worker enabled state", "WorkerSetEnabled", "worker:admin", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "worker_id": string(), "enabled": {"type": "boolean"},
            }, "required": ["worker_id", "enabled"]},
            "object", "worker-set-enabled", operation_class="execution-worker",
        ),
        _operation(
            "job.submit_execution", "Submit durable executable job", "JobSubmitExecution", "job:write", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "job_id": string(), "workspace_id": string(), "operation_id": string(256),
                "arguments": obj, "dependency_job_ids": ids, "input_artifact_ids": ids, "required_capabilities": ids,
                "submitted_at_ns": exact_ns, "schedule_not_before_ns": exact_ns,
                "max_attempts": {"type": "integer", "minimum": 1, "maximum": 10},
                "retry_backoff_ns": {"type": "integer", "minimum": 0, "maximum": 3_600_000_000_000},
                "priority": {"type": "integer", "minimum": -100, "maximum": 100},
                "metadata": obj,
            }, "required": ["job_id", "workspace_id", "operation_id", "arguments", "submitted_at_ns"]},
            "object", "job-submit-execution", operation_class="execution-job",
        ),
        _operation(
            "job.cancel", "Cancel durable job", "JobCancel", "job:write", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "job_id": string(), "reason": obj, "now_ns": exact_ns,
            }, "required": ["job_id", "now_ns"]},
            "object", "job-cancel", operation_class="execution-job",
        ),
        _operation(
            "job.retry", "Retry terminal durable job", "JobRetry", "job:write", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "job_id": string(), "now_ns": exact_ns, "not_before_ns": exact_ns,
            }, "required": ["job_id", "now_ns"]},
            "object", "job-retry", operation_class="execution-job",
        ),
        _operation(
            "job.claim_next", "Claim next eligible durable job", "JobClaimNext", "worker:execute", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "worker_id": string(), "now_ns": exact_ns, "lease_duration_ns": duration_ns,
                "workspace_id": string(),
            }, "required": ["worker_id", "now_ns"]},
            "object", "job-claim-next", operation_class="execution-job",
        ),
        _operation(
            "job.execute_claimed", "Execute claimed durable job", "JobExecuteClaimed", "worker:execute", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "job_id": string(), "worker_id": string(), "claim_token_hash72": string(72),
                "now_ns": exact_ns,
            }, "required": ["job_id", "worker_id", "claim_token_hash72", "now_ns"]},
            "object", "job-execute-claimed", operation_class="execution-job",
        ),
        _operation(
            "scheduler.tick", "Advance durable scheduler", "SchedulerTick", "scheduler:write", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "now_ns": exact_ns, "limit": {"type": "integer", "minimum": 1, "maximum": 1000},
            }, "required": ["now_ns"]},
            "object", "scheduler-tick", operation_class="execution-scheduler",
        ),
    )
    return tuple(copy.deepcopy(record) for record in records)


EXECUTION_OPERATION_RECORDS = execution_operation_records()
EXECUTION_OPERATION_IDS = tuple(record["operation_id"] for record in EXECUTION_OPERATION_RECORDS)


class Iteration7OperationRegistry(ExpandedOperationRegistry):
    """Iteration 6 governed resources plus deterministic durable execution operations."""

    def __init__(self, registry_path: Path = DEFAULT_REGISTRY):
        parent = ExpandedOperationRegistry(registry_path)
        combined_records = [copy.deepcopy(dict(record.raw)) for record in parent.records]
        combined_records.extend(copy.deepcopy(record) for record in EXECUTION_OPERATION_RECORDS)
        identity = {
            "schema": REGISTRY_SCHEMA,
            "contract": ITERATION7_CONTRACT,
            "parent_contract": parent.payload.get("contract"),
            "parent_registry_hash216": parent.payload.get("registry_hash216"),
            "iteration": 7,
            "operations": combined_records,
        }
        self.payload = {
            **identity,
            "registry_hash216": hash216("pass190.iteration7.registry", identity),
            "native_operation_count": int(parent.payload["native_operation_count"]),
            "governed_operation_count": len(combined_records),
            "execution_operation_count": len(EXECUTION_OPERATION_RECORDS),
        }
        self.records = tuple(OperationRecord(record) for record in combined_records)
        self.by_id = {}
        self.by_constructor = {}
        self.by_python = {}
        self.by_shell = {}
        self._validate_and_index()
        if tuple(record.operation_id for record in self.records[-len(EXECUTION_OPERATION_RECORDS):]) != EXECUTION_OPERATION_IDS:
            raise RegistryValidationError("execution operation order mismatch")
        if len(self.records) != len(parent.records) + len(EXECUTION_OPERATION_RECORDS):
            raise RegistryValidationError("Iteration 7 governed operation count mismatch")


def registry_document(registry_path: Path = DEFAULT_REGISTRY) -> dict[str, Any]:
    registry = Iteration7OperationRegistry(registry_path)
    return json.loads(json.dumps(registry.payload, sort_keys=True))

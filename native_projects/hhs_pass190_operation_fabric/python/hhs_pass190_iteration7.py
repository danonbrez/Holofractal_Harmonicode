#!/usr/bin/env python3
"""Pass 190 Iteration 7 durable worker execution and deterministic scheduling authority."""
from __future__ import annotations

import copy
import threading
from pathlib import Path
from typing import Any, Iterable, Mapping

from hhs_pass190 import (
    ArgumentValidationError,
    DEFAULT_REGISTRY,
    HHSOperationError,
    InvocationResult,
    RegistryValidationError,
    ReplayMismatchError,
    StateConflictError,
    _validate_schema,
    hash72,
    hash216,
)
from hhs_pass190_iteration2 import PersistentStoreError
from hhs_pass190_iteration3_hardening import DEFAULT_DATABASE
from hhs_pass190_iteration6 import (
    RESOURCE_ID_FIELDS,
    RESOURCE_KINDS,
    RESOURCE_SCHEMAS,
    _HASH72,
    _SCOPE,
)
from hhs_pass190_iteration6_runtime import UnifiedResourceRegistryContext
from hhs_pass190_iteration7_registry import (
    EXECUTION_JOB_SCHEMA_VERSION,
    EXECUTION_OPERATION_IDS,
    EXECUTION_RUNTIME_SCHEMA,
    ITERATION7_CLASSIFICATION,
    ITERATION7_CONTRACT,
    WORKER_SCHEMA,
    Iteration7OperationRegistry,
)

EXECUTION_JOB_STATUSES = (
    "queued",
    "scheduled",
    "retry_wait",
    "running",
    "completed",
    "failed",
    "cancelled",
)
ACTIVE_JOB_STATUSES = frozenset({"queued", "scheduled", "retry_wait", "running"})
TERMINAL_JOB_STATUSES = frozenset({"completed", "failed", "cancelled"})


class DurableExecutionContext(UnifiedResourceRegistryContext):
    """Resource authority extended with durable workers and exact job execution."""

    def __init__(self, database_path: Path | str = DEFAULT_DATABASE, registry_path: Path = DEFAULT_REGISTRY, **kwargs: Any):
        super().__init__(database_path, registry_path, **kwargs)
        self.registry = Iteration7OperationRegistry(registry_path)
        self._implementations.update({
            "worker.register": self._op_worker_register,
            "worker.get": self._op_worker_get,
            "worker.list": self._op_worker_list,
            "worker.heartbeat": self._op_worker_heartbeat,
            "worker.set_enabled": self._op_worker_set_enabled,
            "job.submit_execution": self._op_job_submit_execution,
            "job.cancel": self._op_job_cancel,
            "job.retry": self._op_job_retry,
            "job.claim_next": self._op_job_claim_next,
            "job.execute_claimed": self._op_job_execute_claimed,
            "scheduler.tick": self._op_scheduler_tick,
        })
        if set(self._implementations) != set(self.registry.by_id):
            missing = set(self.registry.by_id) - set(self._implementations)
            extra = set(self._implementations) - set(self.registry.by_id)
            raise RegistryValidationError(
                f"Iteration 7 registry/implementation mismatch missing={sorted(missing)} extra={sorted(extra)}"
            )
        self.store.restore_into(self)

    def _op_status(self, _args: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "ok",
            "classification": ITERATION7_CLASSIFICATION,
            "contract": ITERATION7_CONTRACT,
            "operations": len(self.registry.records),
            "native_operations": int(self.registry.payload["native_operation_count"]),
            "state_root": self._state_root,
            "receipt_index": self._receipt_index,
        }

    def integrity_report(self) -> dict[str, Any]:
        report = super().integrity_report()
        execution = self.execution_runtime_report()
        return {
            **report,
            "classification": ITERATION7_CLASSIFICATION,
            "contract": ITERATION7_CONTRACT,
            "execution_runtime_verified": True,
            "execution_runtime_schema": EXECUTION_RUNTIME_SCHEMA,
            "worker_count": execution["worker_count"],
            "enabled_worker_count": execution["enabled_worker_count"],
            "running_execution_job_count": execution["running_job_count"],
            "scheduled_execution_job_count": execution["scheduled_job_count"],
            "execution_runtime_hash72": execution["execution_runtime_hash72"],
            "governed_operation_count": len(self.registry.records),
            "compiler_fallback_operation_count": len(self.registry.records) - int(self.registry.payload["native_operation_count"]),
        }

    def resource_registry_report(self) -> dict[str, Any]:
        report = super().resource_registry_report()
        jobs = self._resource_registries()["jobs"].values()
        return {
            **report,
            "classification": ITERATION7_CLASSIFICATION,
            "contract": ITERATION7_CONTRACT,
            "registry_hash216": self.registry.payload["registry_hash216"],
            "governed_operation_count": len(self.registry.records),
            "compiler_fallback_operation_count": len(self.registry.records) - int(self.registry.payload["native_operation_count"]),
            "active_job_count": sum(1 for job in jobs if job["status"] in ACTIVE_JOB_STATUSES),
        }

    def execution_runtime_report(self) -> dict[str, Any]:
        self._validate_resource_state()
        runtime = copy.deepcopy(self._execution_runtime())
        workers = runtime["workers"].values()
        jobs = [job for job in self._resource_registries()["jobs"].values() if self._is_execution_job(job)]
        return {
            "schema": EXECUTION_RUNTIME_SCHEMA,
            "classification": ITERATION7_CLASSIFICATION,
            "contract": ITERATION7_CONTRACT,
            "registry_hash216": self.registry.payload["registry_hash216"],
            "governed_operation_count": len(self.registry.records),
            "native_operation_count": int(self.registry.payload["native_operation_count"]),
            "execution_operation_count": int(self.registry.payload["execution_operation_count"]),
            "worker_count": len(runtime["workers"]),
            "enabled_worker_count": sum(1 for worker in workers if worker["enabled"]),
            "running_job_count": sum(1 for job in jobs if job["status"] == "running"),
            "scheduled_job_count": sum(1 for job in jobs if job["status"] in {"scheduled", "retry_wait"}),
            "queued_job_count": sum(1 for job in jobs if job["status"] == "queued"),
            "execution_runtime_hash72": hash72("pass190.execution.runtime", runtime),
            "state_root": self._state_root,
        }

    def _execution_runtime(self) -> dict[str, Any]:
        value = self._state.get("execution_runtime", {})
        if not isinstance(value, dict):
            raise PersistentStoreError("execution runtime state must be an object")
        workers = value.get("workers", {})
        if not isinstance(workers, dict):
            raise PersistentStoreError("execution worker registry must be an object")
        return {"workers": workers}

    @staticmethod
    def _worker_hash(payload: Mapping[str, Any]) -> str:
        return hash72("pass190.execution.worker", payload)

    def _with_worker_hash(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        clean = copy.deepcopy(dict(payload))
        return {**clean, "record_hash72": self._worker_hash(clean)}

    def _validate_worker_record(self, key: str, worker: Mapping[str, Any]) -> None:
        if not isinstance(worker, dict):
            raise PersistentStoreError("worker record must be an object")
        if worker.get("schema") != WORKER_SCHEMA or worker.get("worker_id") != key:
            raise PersistentStoreError("worker identity or schema mismatch")
        version = worker.get("version")
        if isinstance(version, bool) or not isinstance(version, int) or version < 1:
            raise PersistentStoreError("worker version is invalid")
        payload = {name: copy.deepcopy(value) for name, value in worker.items() if name != "record_hash72"}
        if worker.get("record_hash72") != self._worker_hash(payload):
            raise PersistentStoreError("worker record Hash72 mismatch")
        for name in ("registered_at_ns", "last_heartbeat_ns", "lease_timeout_ns"):
            value = worker.get(name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise PersistentStoreError(f"worker {name} is invalid")
        if worker["lease_timeout_ns"] < 1:
            raise PersistentStoreError("worker lease timeout is invalid")
        if not isinstance(worker.get("enabled"), bool):
            raise PersistentStoreError("worker enabled state is invalid")
        capabilities = worker.get("capabilities")
        labels = worker.get("labels")
        if not isinstance(capabilities, list) or len(capabilities) != len(set(capabilities)):
            raise PersistentStoreError("worker capabilities are invalid")
        if not isinstance(labels, list) or len(labels) != len(set(labels)):
            raise PersistentStoreError("worker labels are invalid")

    @staticmethod
    def _is_execution_job(job: Mapping[str, Any]) -> bool:
        return job.get("execution_schema_version") == EXECUTION_JOB_SCHEMA_VERSION

    def _validate_resource_state(self) -> None:
        raw = self._state.get("resource_registries", {})
        if not isinstance(raw, dict):
            raise PersistentStoreError("resource registries must be an object")
        extra = set(raw) - set(RESOURCE_KINDS)
        if extra:
            raise PersistentStoreError(f"unknown resource registry kinds: {sorted(extra)}")
        registries = self._resource_registries()
        for kind, records in registries.items():
            if not isinstance(records, dict):
                raise PersistentStoreError(f"{kind} registry must be an object")
            for key, record in records.items():
                self._validate_record(kind, key, record)

        workspaces = registries["workspaces"]
        artifacts = registries["artifacts"]
        providers = registries["providers"]
        capabilities = registries["capabilities"]
        jobs = registries["jobs"]
        for artifact in artifacts.values():
            if artifact["workspace_id"] not in workspaces:
                raise PersistentStoreError("artifact references an unknown workspace")
            if not _HASH72.fullmatch(artifact["content_hash72"]):
                raise PersistentStoreError("artifact content Hash72 is invalid")
        for scope in capabilities:
            if scope in {"public", "none"} or not _SCOPE.fullmatch(scope):
                raise PersistentStoreError("capability scope is invalid")

        for job_id, job in jobs.items():
            allowed = EXECUTION_JOB_STATUSES if self._is_execution_job(job) else ("queued", "running", "completed", "failed")
            if job["status"] not in allowed:
                raise PersistentStoreError("job status is invalid")
            if job["workspace_id"] not in workspaces:
                raise PersistentStoreError("job references an unknown workspace")
            if job["operation_id"] not in self.registry.by_id:
                raise PersistentStoreError("job references an unknown operation")
            provider_id = job.get("provider_id")
            if provider_id is not None and provider_id not in providers:
                raise PersistentStoreError("job references an unknown provider")
            for artifact_id in [*job.get("input_artifact_ids", []), *job.get("output_artifact_ids", [])]:
                if artifact_id not in artifacts:
                    raise PersistentStoreError("job references an unknown artifact")
            for scope in job.get("required_capabilities", []):
                if scope not in capabilities:
                    raise PersistentStoreError("job references an undefined capability")
            if not self._is_execution_job(job):
                continue
            operation = self.registry.resolve(job["operation_id"])
            if operation.effect_class != "pure":
                raise PersistentStoreError("durable internal job targets a mutating operation")
            if provider_id is not None:
                raise PersistentStoreError("durable internal job cannot bind a provider adapter")
            dependencies = job.get("dependency_job_ids")
            if not isinstance(dependencies, list) or len(dependencies) != len(set(dependencies)) or job_id in dependencies:
                raise PersistentStoreError("job dependency set is invalid")
            for dependency_id in dependencies:
                dependency = jobs.get(dependency_id)
                if dependency is None or dependency["workspace_id"] != job["workspace_id"]:
                    raise PersistentStoreError("job dependency is absent or cross-workspace")
            for name in ("submitted_at_ns", "schedule_not_before_ns", "next_attempt_ns", "retry_backoff_ns"):
                value = job.get(name)
                if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                    raise PersistentStoreError(f"job {name} is invalid")
            for name in ("attempt", "max_attempts", "priority"):
                value = job.get(name)
                if isinstance(value, bool) or not isinstance(value, int):
                    raise PersistentStoreError(f"job {name} is invalid")
            if job["max_attempts"] < 1 or not 0 <= job["attempt"] <= job["max_attempts"]:
                raise PersistentStoreError("job attempt bounds are invalid")
            request = job.get("execution_request")
            if not isinstance(request, dict) or job.get("execution_request_hash72") != hash72("pass190.job.execution.request", request):
                raise PersistentStoreError("job execution request Hash72 mismatch")
            if job["status"] == "running":
                if not isinstance(job.get("worker_id"), str) or not _HASH72.fullmatch(str(job.get("claim_token_hash72", ""))):
                    raise PersistentStoreError("running job claim identity is invalid")
                lease = job.get("lease_expires_ns")
                if isinstance(lease, bool) or not isinstance(lease, int) or lease < 1:
                    raise PersistentStoreError("running job lease is invalid")

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(job_id: str) -> None:
            if job_id in visited:
                return
            if job_id in visiting:
                raise PersistentStoreError("job dependency cycle detected")
            visiting.add(job_id)
            job = jobs[job_id]
            if self._is_execution_job(job):
                for dependency_id in job["dependency_job_ids"]:
                    visit(dependency_id)
            visiting.remove(job_id)
            visited.add(job_id)

        for job_id in jobs:
            visit(job_id)

        runtime_raw = self._state.get("execution_runtime", {})
        if not isinstance(runtime_raw, dict) or set(runtime_raw) - {"workers"}:
            raise PersistentStoreError("execution runtime shape mismatch")
        workers = self._execution_runtime()["workers"]
        for worker_id, worker in workers.items():
            self._validate_worker_record(worker_id, worker)
            for scope in worker["capabilities"]:
                if scope not in capabilities:
                    raise PersistentStoreError("worker references an undefined capability")
            current_job_id = worker.get("current_job_id")
            if current_job_id is not None:
                job = jobs.get(current_job_id)
                if job is None or not self._is_execution_job(job) or job["status"] != "running":
                    raise PersistentStoreError("worker current job is invalid")
                if job.get("worker_id") != worker_id or job.get("claim_token_hash72") != worker.get("current_claim_token_hash72"):
                    raise PersistentStoreError("worker and job claim identities diverge")
        for job in jobs.values():
            if self._is_execution_job(job) and job["status"] == "running":
                worker = workers.get(job["worker_id"])
                if worker is None or worker.get("current_job_id") != job["job_id"]:
                    raise PersistentStoreError("running job is not owned by a registered worker")

    def _worker_lookup(self, worker_id: str) -> dict[str, Any]:
        worker = self._execution_runtime()["workers"].get(worker_id)
        if worker is None:
            raise ArgumentValidationError(f"unknown worker: {worker_id}")
        return copy.deepcopy(worker)

    @staticmethod
    def _updated_payload(record: Mapping[str, Any], changes: Mapping[str, Any]) -> dict[str, Any]:
        payload = {name: copy.deepcopy(value) for name, value in record.items() if name != "record_hash72"}
        payload.update(copy.deepcopy(dict(changes)))
        payload["version"] = int(record["version"]) + 1
        return payload

    def _commit_execution_records(
        self,
        *,
        job_payloads: Mapping[str, Mapping[str, Any]] | None = None,
        worker_payloads: Mapping[str, Mapping[str, Any]] | None = None,
    ) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
        state = copy.deepcopy(self._state)
        resource_root = state.setdefault("resource_registries", {})
        for kind in RESOURCE_KINDS:
            resource_root.setdefault(kind, {})
        runtime_root = state.setdefault("execution_runtime", {})
        workers = runtime_root.setdefault("workers", {})
        committed_jobs: dict[str, dict[str, Any]] = {}
        committed_workers: dict[str, dict[str, Any]] = {}
        for job_id, payload in (job_payloads or {}).items():
            record = self._with_record_hash("jobs", payload)
            resource_root["jobs"][job_id] = copy.deepcopy(record)
            committed_jobs[job_id] = copy.deepcopy(record)
        for worker_id, payload in (worker_payloads or {}).items():
            record = self._with_worker_hash(payload)
            workers[worker_id] = copy.deepcopy(record)
            committed_workers[worker_id] = copy.deepcopy(record)
        self._state = state
        self._state_root = hash72("pass190.state", self._state)
        self._validate_resource_state()
        return committed_jobs, committed_workers

    def _dependency_state(self, job: Mapping[str, Any]) -> tuple[bool, list[str]]:
        jobs = self._resource_registries()["jobs"]
        blocked: list[str] = []
        for dependency_id in job.get("dependency_job_ids", []):
            dependency = jobs[dependency_id]
            if dependency["status"] in {"failed", "cancelled"}:
                blocked.append(dependency_id)
            elif dependency["status"] != "completed":
                return False, []
        return not blocked, blocked

    def _job_retry_payload(self, job: Mapping[str, Any], now_ns: int, error: Mapping[str, Any]) -> dict[str, Any]:
        if int(job["attempt"]) < int(job["max_attempts"]):
            next_attempt = now_ns + int(job["retry_backoff_ns"]) * max(1, int(job["attempt"]))
            status = "retry_wait" if next_attempt > now_ns else "queued"
        else:
            next_attempt = now_ns
            status = "failed"
        return self._updated_payload(job, {
            "status": status,
            "next_attempt_ns": next_attempt,
            "error": copy.deepcopy(dict(error)),
            "result": None,
            "worker_id": None,
            "claim_token_hash72": None,
            "lease_expires_ns": None,
            "cancel_requested": False,
            "finished_at_ns": now_ns if status == "failed" else None,
        })

    def _op_workspace_archive(self, args: dict[str, Any]) -> dict[str, Any]:
        workspace_id = self._identifier(args["workspace_id"], "workspace_id")
        workspace = self._lookup("workspaces", workspace_id)
        if workspace["archived"]:
            return workspace
        active = sorted(job["job_id"] for job in self._resource_registries()["jobs"].values()
                        if job["workspace_id"] == workspace_id and job["status"] in ACTIVE_JOB_STATUSES)
        if active:
            raise StateConflictError(f"workspace has active jobs: {active}")
        return self._replace_record("workspaces", workspace_id, {"archived": True})

    def _op_provider_set_enabled(self, args: dict[str, Any]) -> dict[str, Any]:
        provider_id = self._identifier(args["provider_id"], "provider_id")
        provider = self._lookup("providers", provider_id)
        enabled = args["enabled"]
        if provider["enabled"] == enabled:
            return provider
        if not enabled:
            active = sorted(job["job_id"] for job in self._resource_registries()["jobs"].values()
                            if job.get("provider_id") == provider_id and job["status"] in ACTIVE_JOB_STATUSES)
            if active:
                raise StateConflictError(f"provider has active jobs: {active}")
        return self._replace_record("providers", provider_id, {"enabled": enabled})

    def _op_job_list(self, args: dict[str, Any]) -> list[dict[str, Any]]:
        workspace_id = args.get("workspace_id")
        status = args.get("status")
        if workspace_id is not None:
            self._identifier(workspace_id, "workspace_id")
        if status is not None and status not in EXECUTION_JOB_STATUSES:
            raise ArgumentValidationError("unknown job status")
        records = self._resource_registries()["jobs"].values()
        return [copy.deepcopy(item) for item in sorted(records, key=lambda item: item["job_id"])
                if (workspace_id is None or item["workspace_id"] == workspace_id)
                and (status is None or item["status"] == status)]

    def _op_job_claim(self, args: dict[str, Any]) -> dict[str, Any]:
        job = self._lookup("jobs", self._identifier(args["job_id"], "job_id"))
        if self._is_execution_job(job):
            raise StateConflictError("durable execution jobs require job.claim_next")
        return super()._op_job_claim(args)

    def _op_job_complete(self, args: dict[str, Any]) -> dict[str, Any]:
        job = self._lookup("jobs", self._identifier(args["job_id"], "job_id"))
        if self._is_execution_job(job):
            raise StateConflictError("durable execution jobs require job.execute_claimed")
        return super()._op_job_complete(args)

    def _op_job_fail(self, args: dict[str, Any]) -> dict[str, Any]:
        job = self._lookup("jobs", self._identifier(args["job_id"], "job_id"))
        if self._is_execution_job(job):
            raise StateConflictError("durable execution jobs require scheduler or job.execute_claimed")
        return super()._op_job_fail(args)

    def _op_worker_register(self, args: dict[str, Any]) -> dict[str, Any]:
        worker_id = self._identifier(args["worker_id"], "worker_id")
        if worker_id in self._execution_runtime()["workers"]:
            raise StateConflictError("worker already exists")
        capabilities = self._unique(list(args.get("capabilities", [])), "capabilities")
        definitions = self._resource_registries()["capabilities"]
        for scope in capabilities:
            self._scope(scope)
            if scope not in definitions:
                raise ArgumentValidationError(f"undefined worker capability: {scope}")
        labels = self._unique(list(args.get("labels", [])), "labels")
        payload = {
            "schema": WORKER_SCHEMA,
            "worker_id": worker_id,
            "capabilities": capabilities,
            "labels": labels,
            "enabled": True,
            "registered_at_ns": args["now_ns"],
            "last_heartbeat_ns": args["now_ns"],
            "lease_timeout_ns": args.get("lease_timeout_ns", 30_000_000_000),
            "current_job_id": None,
            "current_claim_token_hash72": None,
            "completed_job_count": 0,
            "failed_attempt_count": 0,
            "version": 1,
        }
        _jobs, workers = self._commit_execution_records(worker_payloads={worker_id: payload})
        return workers[worker_id]

    def _op_worker_get(self, args: dict[str, Any]) -> dict[str, Any]:
        return self._worker_lookup(self._identifier(args["worker_id"], "worker_id"))

    def _op_worker_list(self, args: dict[str, Any]) -> list[dict[str, Any]]:
        enabled_only = bool(args.get("enabled_only", False))
        workers = self._execution_runtime()["workers"].values()
        return [copy.deepcopy(worker) for worker in sorted(workers, key=lambda item: item["worker_id"])
                if not enabled_only or worker["enabled"]]

    def _op_worker_heartbeat(self, args: dict[str, Any]) -> dict[str, Any]:
        worker_id = self._identifier(args["worker_id"], "worker_id")
        worker = self._worker_lookup(worker_id)
        if not worker["enabled"]:
            raise StateConflictError("worker is disabled")
        if args["now_ns"] < worker["last_heartbeat_ns"]:
            raise StateConflictError("worker heartbeat time moved backwards")
        payload = self._updated_payload(worker, {"last_heartbeat_ns": args["now_ns"]})
        _jobs, workers = self._commit_execution_records(worker_payloads={worker_id: payload})
        return workers[worker_id]

    def _op_worker_set_enabled(self, args: dict[str, Any]) -> dict[str, Any]:
        worker_id = self._identifier(args["worker_id"], "worker_id")
        worker = self._worker_lookup(worker_id)
        enabled = args["enabled"]
        if worker["enabled"] == enabled:
            return worker
        if not enabled and worker.get("current_job_id") is not None:
            raise StateConflictError("worker owns a running job")
        payload = self._updated_payload(worker, {"enabled": enabled})
        _jobs, workers = self._commit_execution_records(worker_payloads={worker_id: payload})
        return workers[worker_id]

    def _op_job_submit_execution(self, args: dict[str, Any]) -> dict[str, Any]:
        job_id = self._identifier(args["job_id"], "job_id")
        workspace_id = self._identifier(args["workspace_id"], "workspace_id")
        self._active_workspace(workspace_id)
        jobs = self._resource_registries()["jobs"]
        if job_id in jobs:
            raise StateConflictError("job already exists")
        operation = self.registry.resolve(args["operation_id"])
        if operation.effect_class != "pure":
            raise StateConflictError("durable internal execution accepts pure operations only")
        _validate_schema(args["arguments"], operation.argument_schema)
        dependencies = self._unique(list(args.get("dependency_job_ids", [])), "dependency_job_ids")
        if job_id in dependencies:
            raise ArgumentValidationError("job cannot depend on itself")
        for dependency_id in dependencies:
            dependency = jobs.get(self._identifier(dependency_id, "dependency_job_id"))
            if dependency is None:
                raise ArgumentValidationError(f"unknown dependency job: {dependency_id}")
            if dependency["workspace_id"] != workspace_id:
                raise StateConflictError("job dependency belongs to another workspace")
        input_artifacts = self._unique(list(args.get("input_artifact_ids", [])), "input_artifact_ids")
        for artifact_id in input_artifacts:
            artifact = self._lookup("artifacts", self._identifier(artifact_id, "artifact_id"))
            if artifact["workspace_id"] != workspace_id:
                raise StateConflictError("job input artifact belongs to another workspace")
        required_capabilities = self._unique(list(args.get("required_capabilities", [])), "required_capabilities")
        definitions = self._resource_registries()["capabilities"]
        for scope in required_capabilities:
            self._scope(scope)
            if scope not in definitions:
                raise ArgumentValidationError(f"undefined required capability: {scope}")
        if operation.capability not in {"public", "none"} and operation.capability not in required_capabilities:
            raise ArgumentValidationError(f"job must declare target operation capability: {operation.capability}")
        submitted_at_ns = args["submitted_at_ns"]
        not_before_ns = args.get("schedule_not_before_ns", submitted_at_ns)
        if not_before_ns < submitted_at_ns:
            raise ArgumentValidationError("schedule_not_before_ns precedes submission")
        dependencies_complete = all(jobs[dependency_id]["status"] == "completed" for dependency_id in dependencies)
        status = "queued" if dependencies_complete and not_before_ns <= submitted_at_ns else "scheduled"
        request = {
            "workspace_id": workspace_id,
            "operation_id": operation.operation_id,
            "operation_hash216": operation.raw["Hash216_identity"],
            "arguments": copy.deepcopy(args["arguments"]),
            "dependency_job_ids": dependencies,
            "input_artifact_ids": input_artifacts,
            "required_capabilities": required_capabilities,
            "submitted_at_ns": submitted_at_ns,
            "schedule_not_before_ns": not_before_ns,
            "max_attempts": args.get("max_attempts", 3),
            "retry_backoff_ns": args.get("retry_backoff_ns", 0),
            "priority": args.get("priority", 0),
        }
        payload = {
            "schema": RESOURCE_SCHEMAS["jobs"],
            "execution_schema_version": EXECUTION_JOB_SCHEMA_VERSION,
            "job_id": job_id,
            **request,
            "execution_request": copy.deepcopy(request),
            "execution_request_hash72": hash72("pass190.job.execution.request", request),
            "request_hash72": hash72("pass190.job.request", request),
            "provider_id": None,
            "metadata": copy.deepcopy(args.get("metadata", {})),
            "status": status,
            "attempt": 0,
            "next_attempt_ns": not_before_ns,
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
        committed, _workers = self._commit_execution_records(job_payloads={job_id: payload})
        return committed[job_id]

    def _op_job_cancel(self, args: dict[str, Any]) -> dict[str, Any]:
        job_id = self._identifier(args["job_id"], "job_id")
        job = self._lookup("jobs", job_id)
        if not self._is_execution_job(job):
            raise StateConflictError("job is outside durable execution authority")
        if job["status"] in TERMINAL_JOB_STATUSES:
            return job
        job_payload = self._updated_payload(job, {
            "status": "cancelled",
            "cancel_requested": True,
            "error": {"type": "cancelled", "reason": copy.deepcopy(args.get("reason", {}))},
            "result": None,
            "worker_id": None,
            "claim_token_hash72": None,
            "lease_expires_ns": None,
            "finished_at_ns": args["now_ns"],
        })
        worker_payloads: dict[str, Mapping[str, Any]] = {}
        worker_id = job.get("worker_id")
        if isinstance(worker_id, str) and worker_id in self._execution_runtime()["workers"]:
            worker = self._worker_lookup(worker_id)
            worker_payloads[worker_id] = self._updated_payload(worker, {
                "current_job_id": None,
                "current_claim_token_hash72": None,
                "failed_attempt_count": int(worker["failed_attempt_count"]) + 1,
            })
        committed, _workers = self._commit_execution_records(
            job_payloads={job_id: job_payload}, worker_payloads=worker_payloads
        )
        return committed[job_id]

    def _op_job_retry(self, args: dict[str, Any]) -> dict[str, Any]:
        job_id = self._identifier(args["job_id"], "job_id")
        job = self._lookup("jobs", job_id)
        if not self._is_execution_job(job) or job["status"] not in {"failed", "cancelled"}:
            raise StateConflictError("only failed or cancelled durable jobs can retry")
        if int(job["attempt"]) >= int(job["max_attempts"]):
            raise StateConflictError("job exhausted its attempt budget")
        not_before = args.get("not_before_ns", args["now_ns"])
        if not_before < args["now_ns"]:
            raise ArgumentValidationError("retry not_before_ns is in the past")
        dependencies_ready, terminal_dependencies = self._dependency_state(job)
        if terminal_dependencies:
            raise StateConflictError(f"job has terminal dependencies: {terminal_dependencies}")
        status = "queued" if dependencies_ready and not_before <= args["now_ns"] else "retry_wait"
        payload = self._updated_payload(job, {
            "status": status,
            "next_attempt_ns": not_before,
            "cancel_requested": False,
            "error": None,
            "result": None,
            "execution_hash72": None,
            "finished_at_ns": None,
        })
        committed, _workers = self._commit_execution_records(job_payloads={job_id: payload})
        return committed[job_id]

    def _scheduler_payloads(self, now_ns: int, limit: int) -> tuple[dict[str, Mapping[str, Any]], dict[str, Mapping[str, Any]], dict[str, int], list[str]]:
        jobs = self._resource_registries()["jobs"]
        workers = self._execution_runtime()["workers"]
        job_payloads: dict[str, Mapping[str, Any]] = {}
        worker_payloads: dict[str, Mapping[str, Any]] = {}
        counts = {"queued": 0, "retried": 0, "failed": 0, "released": 0}
        changed: list[str] = []
        for job_id in sorted(jobs):
            if len(changed) >= limit:
                break
            job = jobs[job_id]
            if not self._is_execution_job(job):
                continue
            if job["status"] == "running":
                worker = workers.get(job.get("worker_id"))
                worker_stale = (
                    worker is None
                    or not worker["enabled"]
                    or now_ns > int(worker["last_heartbeat_ns"]) + int(worker["lease_timeout_ns"])
                )
                if now_ns >= int(job["lease_expires_ns"]) or worker_stale:
                    error = {
                        "type": "worker_lease_expired",
                        "worker_id": job.get("worker_id"),
                        "observed_at_ns": now_ns,
                    }
                    job_payloads[job_id] = self._job_retry_payload(job, now_ns, error)
                    counts["retried" if int(job["attempt"]) < int(job["max_attempts"]) else "failed"] += 1
                    changed.append(job_id)
                    worker_id = job.get("worker_id")
                    if isinstance(worker_id, str) and worker_id in workers:
                        worker_payloads[worker_id] = self._updated_payload(workers[worker_id], {
                            "current_job_id": None,
                            "current_claim_token_hash72": None,
                            "failed_attempt_count": int(workers[worker_id]["failed_attempt_count"]) + 1,
                        })
                        counts["released"] += 1
                continue
            if job["status"] not in {"queued", "scheduled", "retry_wait"}:
                continue
            dependencies_ready, terminal_dependencies = self._dependency_state(job)
            if terminal_dependencies:
                job_payloads[job_id] = self._updated_payload(job, {
                    "status": "failed",
                    "error": {"type": "dependency_terminal", "dependency_job_ids": terminal_dependencies},
                    "finished_at_ns": now_ns,
                })
                counts["failed"] += 1
                changed.append(job_id)
            elif dependencies_ready and now_ns >= int(job["next_attempt_ns"]):
                if job["status"] != "queued":
                    job_payloads[job_id] = self._updated_payload(job, {"status": "queued"})
                    counts["queued"] += 1
                    changed.append(job_id)
            elif job["status"] == "queued":
                job_payloads[job_id] = self._updated_payload(job, {"status": "scheduled"})
                changed.append(job_id)
        return job_payloads, worker_payloads, counts, changed

    def _op_scheduler_tick(self, args: dict[str, Any]) -> dict[str, Any]:
        limit = args.get("limit", 100)
        job_payloads, worker_payloads, counts, changed = self._scheduler_payloads(args["now_ns"], limit)
        if job_payloads or worker_payloads:
            self._commit_execution_records(job_payloads=job_payloads, worker_payloads=worker_payloads)
        return {
            "observed_at_ns": args["now_ns"],
            "changed_job_ids": changed,
            "counts": counts,
            "state_root": self._state_root,
        }

    def _op_job_claim_next(self, args: dict[str, Any]) -> dict[str, Any]:
        worker_id = self._identifier(args["worker_id"], "worker_id")
        worker = self._worker_lookup(worker_id)
        now_ns = args["now_ns"]
        if not worker["enabled"]:
            raise StateConflictError("worker is disabled")
        if now_ns > int(worker["last_heartbeat_ns"]) + int(worker["lease_timeout_ns"]):
            raise StateConflictError("worker heartbeat lease expired")
        if worker.get("current_job_id") is not None:
            raise StateConflictError("worker already owns a running job")
        job_payloads, worker_payloads, _counts, _changed = self._scheduler_payloads(now_ns, 1000)
        if job_payloads or worker_payloads:
            self._commit_execution_records(job_payloads=job_payloads, worker_payloads=worker_payloads)
            worker = self._worker_lookup(worker_id)
        workspace_id = args.get("workspace_id")
        if workspace_id is not None:
            self._identifier(workspace_id, "workspace_id")
        eligible = []
        for job in self._resource_registries()["jobs"].values():
            if not self._is_execution_job(job) or job["status"] != "queued" or job.get("provider_id") is not None:
                continue
            if workspace_id is not None and job["workspace_id"] != workspace_id:
                continue
            if not set(job["required_capabilities"]).issubset(set(worker["capabilities"])):
                continue
            ready, terminal = self._dependency_state(job)
            if ready and not terminal and now_ns >= int(job["next_attempt_ns"]):
                eligible.append(job)
        if not eligible:
            return {"claimed": False, "job": None, "claim_token_hash72": None, "state_root": self._state_root}
        job = sorted(eligible, key=lambda item: (-int(item["priority"]), item["job_id"]))[0]
        attempt = int(job["attempt"]) + 1
        if attempt > int(job["max_attempts"]):
            raise StateConflictError("job exhausted its attempt budget")
        lease_duration = min(args.get("lease_duration_ns", int(worker["lease_timeout_ns"])), int(worker["lease_timeout_ns"]))
        claim_payload = {
            "job_id": job["job_id"],
            "worker_id": worker_id,
            "attempt": attempt,
            "claimed_at_ns": now_ns,
            "lease_duration_ns": lease_duration,
            "preclaim_state_root": self._state_root,
        }
        claim_token = hash72("pass190.execution.claim", claim_payload)
        job_payload = self._updated_payload(job, {
            "status": "running",
            "attempt": attempt,
            "worker_id": worker_id,
            "claim_token_hash72": claim_token,
            "lease_expires_ns": now_ns + lease_duration,
            "cancel_requested": False,
            "started_at_ns": now_ns,
            "finished_at_ns": None,
        })
        worker_payload = self._updated_payload(worker, {
            "current_job_id": job["job_id"],
            "current_claim_token_hash72": claim_token,
            "last_heartbeat_ns": max(int(worker["last_heartbeat_ns"]), now_ns),
        })
        committed_jobs, _workers = self._commit_execution_records(
            job_payloads={job["job_id"]: job_payload}, worker_payloads={worker_id: worker_payload}
        )
        return {
            "claimed": True,
            "job": committed_jobs[job["job_id"]],
            "claim_token_hash72": claim_token,
            "state_root": self._state_root,
        }

    def _op_job_execute_claimed(self, args: dict[str, Any]) -> dict[str, Any]:
        job_id = self._identifier(args["job_id"], "job_id")
        worker_id = self._identifier(args["worker_id"], "worker_id")
        job = self._lookup("jobs", job_id)
        worker = self._worker_lookup(worker_id)
        token = args["claim_token_hash72"]
        now_ns = args["now_ns"]
        if not self._is_execution_job(job) or job["status"] != "running":
            raise StateConflictError("job is not a running durable execution")
        if job.get("worker_id") != worker_id or job.get("claim_token_hash72") != token:
            raise StateConflictError("job claim token mismatch")
        if worker.get("current_job_id") != job_id or worker.get("current_claim_token_hash72") != token:
            raise StateConflictError("worker claim token mismatch")
        if now_ns >= int(job["lease_expires_ns"]):
            raise StateConflictError("job execution lease expired")
        if not worker["enabled"] or now_ns > int(worker["last_heartbeat_ns"]) + int(worker["lease_timeout_ns"]):
            raise StateConflictError("worker authority expired")
        if job.get("cancel_requested"):
            raise StateConflictError("job cancellation is pending")
        if not set(job["required_capabilities"]).issubset(set(worker["capabilities"])):
            raise StateConflictError("worker lacks job capabilities")
        operation = self.registry.resolve(job["operation_id"])
        if operation.effect_class != "pure":
            raise StateConflictError("durable worker cannot execute mutating targets")
        try:
            target_result = self._implementations[operation.operation_id](copy.deepcopy(job["arguments"]))
        except (HHSOperationError, ValueError, TypeError, OverflowError) as exc:
            error = {"type": type(exc).__name__, "message": str(exc), "observed_at_ns": now_ns}
            job_payload = self._job_retry_payload(job, now_ns, error)
            worker_payload = self._updated_payload(worker, {
                "current_job_id": None,
                "current_claim_token_hash72": None,
                "last_heartbeat_ns": max(int(worker["last_heartbeat_ns"]), now_ns),
                "failed_attempt_count": int(worker["failed_attempt_count"]) + 1,
            })
            committed_jobs, _workers = self._commit_execution_records(
                job_payloads={job_id: job_payload}, worker_payloads={worker_id: worker_payload}
            )
            return {
                "executed": False,
                "job": committed_jobs[job_id],
                "target_result": None,
                "execution_hash72": None,
                "error": error,
                "state_root": self._state_root,
            }
        execution_payload = {
            "job_id": job_id,
            "worker_id": worker_id,
            "attempt": job["attempt"],
            "operation_id": operation.operation_id,
            "operation_hash216": operation.raw["Hash216_identity"],
            "arguments": copy.deepcopy(job["arguments"]),
            "result": copy.deepcopy(target_result),
            "executed_at_ns": now_ns,
            "claim_token_hash72": token,
        }
        execution_hash = hash72("pass190.execution.result", execution_payload)
        job_payload = self._updated_payload(job, {
            "status": "completed",
            "result": copy.deepcopy(target_result),
            "error": None,
            "execution_hash72": execution_hash,
            "worker_id": worker_id,
            "claim_token_hash72": None,
            "lease_expires_ns": None,
            "finished_at_ns": now_ns,
        })
        worker_payload = self._updated_payload(worker, {
            "current_job_id": None,
            "current_claim_token_hash72": None,
            "last_heartbeat_ns": max(int(worker["last_heartbeat_ns"]), now_ns),
            "completed_job_count": int(worker["completed_job_count"]) + 1,
        })
        committed_jobs, _workers = self._commit_execution_records(
            job_payloads={job_id: job_payload}, worker_payloads={worker_id: worker_payload}
        )
        return {
            "executed": True,
            "job": committed_jobs[job_id],
            "target_result": copy.deepcopy(target_result),
            "execution_hash72": execution_hash,
            "state_root": self._state_root,
        }

    def replay(self, receipt_hash72: str) -> InvocationResult:
        self.store.restore_into(self)
        receipt = self._receipts.get(receipt_hash72)
        if receipt is None:
            raise ReplayMismatchError("unknown receipt")
        operation_id = str(receipt["operation_id"])
        if operation_id not in EXECUTION_OPERATION_IDS and operation_id != "system.status":
            return super().replay(receipt_hash72)
        with self._lock:
            grant = self.store.acquire_lease(self.holder_id, ttl_ns=self.lease_ttl_ns, wait_ns=self.lease_wait_ns)
            try:
                with self.store.admission(grant):
                    self.store.restore_into(self)
                    receipt = self._receipts.get(receipt_hash72)
                    if receipt is None:
                        raise ReplayMismatchError("unknown receipt")
                    self._verify_receipt_identity(receipt)
                    result = copy.deepcopy(receipt["result"])
                    if operation_id == "system.status":
                        expected = {
                            "status": "ok",
                            "classification": ITERATION7_CLASSIFICATION,
                            "contract": ITERATION7_CONTRACT,
                            "operations": len(self.registry.records),
                            "native_operations": int(self.registry.payload["native_operation_count"]),
                            "state_root": receipt["state_before"],
                            "receipt_index": receipt["receipt_index"] - 1,
                        }
                        if result != expected:
                            raise ReplayMismatchError("semantic replay mismatch")
                    else:
                        self._validate_execution_replay(operation_id, result)
                    invocation = InvocationResult(operation_id, result, receipt, "replay", True)
                    self.store.append_fenced_event(
                        "operation.replayed",
                        {"operation_id": operation_id, "hash72": receipt_hash72, "replay_verified": True},
                        grant,
                    )
                    return invocation
            except Exception:
                self.store.restore_into(self)
                raise

    def _validate_execution_replay(self, operation_id: str, result: Any) -> None:
        if operation_id == "worker.list":
            if not isinstance(result, list):
                raise ReplayMismatchError("worker list replay result is invalid")
            identities = []
            for worker in result:
                key = worker.get("worker_id") if isinstance(worker, dict) else None
                if not isinstance(key, str):
                    raise ReplayMismatchError("worker replay identity is invalid")
                self._validate_worker_record(key, worker)
                identities.append(key)
            if identities != sorted(identities):
                raise ReplayMismatchError("worker replay order is invalid")
            return
        if operation_id.startswith("worker."):
            if not isinstance(result, dict) or not isinstance(result.get("worker_id"), str):
                raise ReplayMismatchError("worker replay result is invalid")
            self._validate_worker_record(result["worker_id"], result)
            return
        if operation_id in {"job.submit_execution", "job.cancel", "job.retry"}:
            if not isinstance(result, dict) or not isinstance(result.get("job_id"), str):
                raise ReplayMismatchError("job replay result is invalid")
            self._validate_record("jobs", result["job_id"], result)
            return
        if operation_id == "job.claim_next":
            if not isinstance(result, dict) or not isinstance(result.get("claimed"), bool):
                raise ReplayMismatchError("claim replay result is invalid")
            job = result.get("job")
            if job is not None:
                self._validate_record("jobs", job["job_id"], job)
            return
        if operation_id == "job.execute_claimed":
            if not isinstance(result, dict) or not isinstance(result.get("executed"), bool):
                raise ReplayMismatchError("execution replay result is invalid")
            job = result.get("job")
            if not isinstance(job, dict):
                raise ReplayMismatchError("execution replay job is invalid")
            self._validate_record("jobs", job["job_id"], job)
            return
        if operation_id == "scheduler.tick":
            if not isinstance(result, dict) or not isinstance(result.get("changed_job_ids"), list):
                raise ReplayMismatchError("scheduler replay result is invalid")
            return
        raise ReplayMismatchError("unknown Iteration 7 replay operation")


_CONTEXT: DurableExecutionContext | None = None
_CONTEXT_LOCK = threading.Lock()
_CONTEXT_PATH: Path | None = None


def get_iteration7_context(database_path: Path | str | None = None) -> DurableExecutionContext:
    global _CONTEXT, _CONTEXT_PATH
    requested = Path(database_path or DEFAULT_DATABASE)
    if _CONTEXT is None:
        with _CONTEXT_LOCK:
            if _CONTEXT is None:
                _CONTEXT = DurableExecutionContext(requested)
                _CONTEXT_PATH = requested
    elif _CONTEXT_PATH != requested:
        raise PersistentStoreError("process authority context already bound to another database")
    return _CONTEXT

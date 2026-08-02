#!/usr/bin/env python3
"""Pass 190 Iteration 6: governed resource registries and job lifecycle authority."""
from __future__ import annotations

import copy
import os
import re
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from hhs_pass190 import (
    DEFAULT_REGISTRY,
    HHSAuthorityContext,
    InvocationResult,
    RegistryValidationError,
    ReplayMismatchError,
    ArgumentValidationError,
    StateConflictError,
    _validate_schema,
    hash72,
    hash216,
)
from hhs_pass190_iteration2 import PersistentStoreError
from hhs_pass190_iteration3_hardening import DEFAULT_DATABASE
from hhs_pass190_iteration4 import DEFAULT_LEASE_TTL_NS, DEFAULT_LEASE_WAIT_NS
from hhs_pass190_iteration5 import CorrectedAuthorityStore
from hhs_pass190_iteration5_runtime import AtomicKernelAuthorityStore
from hhs_pass190_iteration6_registry import (
    ITERATION6_CLASSIFICATION,
    ITERATION6_CONTRACT,
    RESOURCE_KINDS,
    RESOURCE_OPERATION_IDS,
    RESOURCE_REGISTRY_SCHEMA,
    ExpandedOperationRegistry,
)

_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SCOPE = re.compile(r"^[a-z][a-z0-9_.-]*:[a-z0-9_.-]+$")
_HASH72 = re.compile(r"^[0-9a-f]{72}$")
JOB_STATUSES = ("queued", "running", "completed", "failed")
RESOURCE_SCHEMAS = {
    "workspaces": "HHS_PASS_190_WORKSPACE_V1",
    "artifacts": "HHS_PASS_190_ARTIFACT_V1",
    "providers": "HHS_PASS_190_PROVIDER_V1",
    "capabilities": "HHS_PASS_190_CAPABILITY_DEFINITION_V1",
    "jobs": "HHS_PASS_190_JOB_V1",
}
RESOURCE_ID_FIELDS = {
    "workspaces": "workspace_id",
    "artifacts": "artifact_id",
    "providers": "provider_id",
    "capabilities": "scope",
    "jobs": "job_id",
}


class ResourceRegistryStore(AtomicKernelAuthorityStore):
    """Atomic kernel store that validates resource state inside the restore snapshot."""

    def restore_into(self, context: HHSAuthorityContext) -> None:
        with self._lock:
            started = not self._connection.in_transaction
            try:
                if started:
                    self._connection.execute("BEGIN")
                CorrectedAuthorityStore.restore_into(self, context)
                validator = getattr(context, "_validate_resource_state", None)
                if validator is not None:
                    validator()
                if started:
                    self._connection.commit()
            except Exception:
                if started and self._connection.in_transaction:
                    self._connection.rollback()
                raise


class ResourceRegistryContext(HHSAuthorityContext):
    """One VM81 authority for operations, resources, providers, capabilities, and jobs."""

    def __init__(
        self,
        database_path: Path | str = DEFAULT_DATABASE,
        registry_path: Path = DEFAULT_REGISTRY,
        *,
        holder_id: str | None = None,
        lease_ttl_ns: int = DEFAULT_LEASE_TTL_NS,
        lease_wait_ns: int = DEFAULT_LEASE_WAIT_NS,
        clock_ns: Callable[[], int] = time.time_ns,
        sleeper: Callable[[float], None] = time.sleep,
    ):
        self.holder_id = holder_id or f"{os.getpid()}:{uuid.uuid4().hex}"
        self.lease_ttl_ns = lease_ttl_ns
        self.lease_wait_ns = lease_wait_ns
        self.store = ResourceRegistryStore(database_path, clock_ns=clock_ns, sleeper=sleeper)
        HHSAuthorityContext.__init__(self, registry_path)
        self.registry = ExpandedOperationRegistry(registry_path)
        self._implementations.update({
            "workspace.create": self._op_workspace_create,
            "workspace.get": self._op_workspace_get,
            "workspace.list": self._op_workspace_list,
            "workspace.update": self._op_workspace_update,
            "workspace.archive": self._op_workspace_archive,
            "artifact.register": self._op_artifact_register,
            "artifact.get": self._op_artifact_get,
            "artifact.list": self._op_artifact_list,
            "provider.register": self._op_provider_register,
            "provider.get": self._op_provider_get,
            "provider.list": self._op_provider_list,
            "provider.set_enabled": self._op_provider_set_enabled,
            "capability.define": self._op_capability_define,
            "capability.get": self._op_capability_get,
            "capability.list": self._op_capability_list,
            "job.submit": self._op_job_submit,
            "job.get": self._op_job_get,
            "job.list": self._op_job_list,
            "job.claim": self._op_job_claim,
            "job.complete": self._op_job_complete,
            "job.fail": self._op_job_fail,
        })
        if set(self._implementations) != set(self.registry.by_id):
            missing = set(self.registry.by_id) - set(self._implementations)
            extra = set(self._implementations) - set(self.registry.by_id)
            raise RegistryValidationError(
                f"expanded registry/implementation mismatch missing={sorted(missing)} extra={sorted(extra)}"
            )
        self.store.restore_into(self)

    def close(self) -> None:
        self.store.close()

    def invoke(
        self,
        operation_id: str,
        arguments: Mapping[str, Any] | None = None,
        *,
        surface: str = "canonical",
        capabilities: Iterable[str] = (),
        idempotency_key: str | None = None,
        expected_state: str | None = None,
    ) -> InvocationResult:
        with self._lock:
            grant = self.store.acquire_lease(
                self.holder_id, ttl_ns=self.lease_ttl_ns, wait_ns=self.lease_wait_ns
            )
            try:
                with self.store.admission(grant):
                    self.store.restore_into(self)
                    before_index = self._receipt_index
                    result = HHSAuthorityContext.invoke(
                        self,
                        operation_id,
                        arguments,
                        surface=surface,
                        capabilities=capabilities,
                        idempotency_key=idempotency_key,
                        expected_state=expected_state,
                    )
                    if self._receipt_index > before_index:
                        self.store.persist_fenced_invocation(self, result, idempotency_key, grant)
                    return result
            except Exception:
                self.store.restore_into(self)
                raise

    def replay(self, receipt_hash72: str) -> InvocationResult:
        with self._lock:
            grant = self.store.acquire_lease(
                self.holder_id, ttl_ns=self.lease_ttl_ns, wait_ns=self.lease_wait_ns
            )
            try:
                with self.store.admission(grant):
                    self.store.restore_into(self)
                    receipt = self._receipts.get(receipt_hash72)
                    if receipt is None:
                        raise ReplayMismatchError("unknown receipt")
                    operation_id = receipt["operation_id"]
                    if operation_id == "system.status":
                        expected = copy.deepcopy(receipt["result"])
                        recomputed = {
                            "status": "ok",
                            "classification": ITERATION6_CLASSIFICATION,
                            "contract": ITERATION6_CONTRACT,
                            "operations": len(self.registry.records),
                            "native_operations": int(self.registry.payload["native_operation_count"]),
                            "state_root": receipt["state_before"],
                            "receipt_index": receipt["receipt_index"] - 1,
                        }
                        if recomputed != expected:
                            raise ReplayMismatchError("semantic replay mismatch")
                        self._verify_receipt_identity(receipt)
                        result = InvocationResult(operation_id, expected, receipt, "replay", True)
                    elif operation_id in RESOURCE_OPERATION_IDS:
                        result = self._replay_resource(receipt)
                    else:
                        result = HHSAuthorityContext.replay(self, receipt_hash72)
                    self.store.append_fenced_event(
                        "operation.replayed",
                        {"operation_id": result.operation_id, "hash72": receipt_hash72, "replay_verified": True},
                        grant,
                    )
                    return result
            except Exception:
                self.store.restore_into(self)
                raise

    def integrity_report(self) -> dict[str, Any]:
        report = self.store.integrity_report()
        self.store.restore_into(self)
        resource = self.resource_registry_report()
        return {
            **report,
            "classification": ITERATION6_CLASSIFICATION,
            "contract": ITERATION6_CONTRACT,
            "resource_registry_verified": True,
            "resource_registry_schema": RESOURCE_REGISTRY_SCHEMA,
            "resource_registry_hash72": resource["resource_registry_hash72"],
            "resource_counts": resource["counts"],
            "active_job_count": resource["active_job_count"],
            "governed_operation_count": len(self.registry.records),
            "native_operation_count": int(self.registry.payload["native_operation_count"]),
            "compiler_fallback_operation_count": len(RESOURCE_OPERATION_IDS),
        }

    def resource_registry_report(self) -> dict[str, Any]:
        self._validate_resource_state()
        registries = copy.deepcopy(self._resource_registries())
        counts = {kind: len(registries[kind]) for kind in RESOURCE_KINDS}
        jobs = registries["jobs"].values()
        return {
            "schema": RESOURCE_REGISTRY_SCHEMA,
            "classification": ITERATION6_CLASSIFICATION,
            "contract": ITERATION6_CONTRACT,
            "registry_hash216": self.registry.payload["registry_hash216"],
            "governed_operation_count": len(self.registry.records),
            "native_operation_count": int(self.registry.payload["native_operation_count"]),
            "compiler_fallback_operation_count": len(RESOURCE_OPERATION_IDS),
            "resource_kinds": list(RESOURCE_KINDS),
            "counts": counts,
            "active_job_count": sum(1 for job in jobs if job["status"] in {"queued", "running"}),
            "resource_registry_hash72": hash72("pass190.resource.registry", registries),
            "state_root": self._state_root,
        }

    def _op_status(self, _args: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "ok",
            "classification": ITERATION6_CLASSIFICATION,
            "contract": ITERATION6_CONTRACT,
            "operations": len(self.registry.records),
            "native_operations": int(self.registry.payload["native_operation_count"]),
            "state_root": self._state_root,
            "receipt_index": self._receipt_index,
        }

    def _resource_registries(self) -> dict[str, dict[str, Any]]:
        value = self._state.get("resource_registries", {})
        if not isinstance(value, dict):
            raise PersistentStoreError("resource registry state must be an object")
        return {kind: value.get(kind, {}) for kind in RESOURCE_KINDS}

    @staticmethod
    def _identifier(value: str, field: str) -> str:
        if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
            raise ArgumentValidationError(f"{field} is not a canonical identifier")
        return value

    @staticmethod
    def _scope(value: str) -> str:
        if value in {"public", "none"} or not isinstance(value, str) or not _SCOPE.fullmatch(value):
            raise ArgumentValidationError("scope must be a non-public canonical capability")
        return value

    @staticmethod
    def _unique(values: list[str], field: str) -> list[str]:
        if len(values) != len(set(values)):
            raise ArgumentValidationError(f"{field} contains duplicate identifiers")
        return list(values)

    @staticmethod
    def _record_hash(kind: str, payload: Mapping[str, Any]) -> str:
        return hash72(f"pass190.resource.{kind}", payload)

    def _with_record_hash(self, kind: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        clean = copy.deepcopy(dict(payload))
        return {**clean, "record_hash72": self._record_hash(kind, clean)}

    def _validate_record(self, kind: str, key: str, record: Mapping[str, Any]) -> None:
        if not isinstance(record, dict):
            raise PersistentStoreError(f"{kind} record must be an object")
        identity_field = RESOURCE_ID_FIELDS[kind]
        if record.get("schema") != RESOURCE_SCHEMAS[kind]:
            raise PersistentStoreError(f"{kind} schema mismatch")
        if record.get(identity_field) != key:
            raise PersistentStoreError(f"{kind} key mismatch")
        version = record.get("version")
        if isinstance(version, bool) or not isinstance(version, int) or version < 1:
            raise PersistentStoreError(f"{kind} version is invalid")
        supplied = record.get("record_hash72")
        payload = {name: copy.deepcopy(value) for name, value in record.items() if name != "record_hash72"}
        if supplied != self._record_hash(kind, payload):
            raise PersistentStoreError(f"{kind} record Hash72 mismatch")

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
        for artifact in artifacts.values():
            if artifact["workspace_id"] not in workspaces:
                raise PersistentStoreError("artifact references an unknown workspace")
            if not _HASH72.fullmatch(artifact["content_hash72"]):
                raise PersistentStoreError("artifact content Hash72 is invalid")
        for scope in capabilities:
            if scope in {"public", "none"} or not _SCOPE.fullmatch(scope):
                raise PersistentStoreError("capability scope is invalid")
        for job in registries["jobs"].values():
            if job["status"] not in JOB_STATUSES:
                raise PersistentStoreError("job status is invalid")
            if job["workspace_id"] not in workspaces:
                raise PersistentStoreError("job references an unknown workspace")
            if job["operation_id"] not in self.registry.by_id:
                raise PersistentStoreError("job references an unknown operation")
            provider_id = job.get("provider_id")
            if provider_id is not None and provider_id not in providers:
                raise PersistentStoreError("job references an unknown provider")
            for artifact_id in [*job["input_artifact_ids"], *job["output_artifact_ids"]]:
                if artifact_id not in artifacts:
                    raise PersistentStoreError("job references an unknown artifact")
            for scope in job["required_capabilities"]:
                if scope not in capabilities:
                    raise PersistentStoreError("job references an undefined capability")

    def _lookup(self, kind: str, key: str) -> dict[str, Any]:
        record = self._resource_registries()[kind].get(key)
        if record is None:
            raise ArgumentValidationError(f"unknown {kind[:-1]}: {key}")
        return copy.deepcopy(record)

    def _commit_record(self, kind: str, key: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        record = self._with_record_hash(kind, payload)
        state = copy.deepcopy(self._state)
        root = state.setdefault("resource_registries", {})
        for resource_kind in RESOURCE_KINDS:
            root.setdefault(resource_kind, {})
        root[kind][key] = copy.deepcopy(record)
        self._state = state
        self._state_root = hash72("pass190.state", self._state)
        self._validate_resource_state()
        return copy.deepcopy(record)

    def _replace_record(self, kind: str, key: str, changes: Mapping[str, Any]) -> dict[str, Any]:
        current = self._lookup(kind, key)
        payload = {name: copy.deepcopy(value) for name, value in current.items() if name != "record_hash72"}
        payload.update(copy.deepcopy(dict(changes)))
        payload["version"] = int(current["version"]) + 1
        return self._commit_record(kind, key, payload)

    def _active_workspace(self, workspace_id: str) -> dict[str, Any]:
        workspace = self._lookup("workspaces", workspace_id)
        if workspace["archived"]:
            raise StateConflictError("workspace is archived")
        return workspace

    def _op_workspace_create(self, args: dict[str, Any]) -> dict[str, Any]:
        workspace_id = self._identifier(args["workspace_id"], "workspace_id")
        if workspace_id in self._resource_registries()["workspaces"]:
            raise StateConflictError("workspace already exists")
        return self._commit_record("workspaces", workspace_id, {
            "schema": RESOURCE_SCHEMAS["workspaces"],
            "workspace_id": workspace_id,
            "name": args["name"],
            "metadata": copy.deepcopy(args.get("metadata", {})),
            "archived": False,
            "version": 1,
        })

    def _op_workspace_get(self, args: dict[str, Any]) -> dict[str, Any]:
        return self._lookup("workspaces", self._identifier(args["workspace_id"], "workspace_id"))

    def _op_workspace_list(self, args: dict[str, Any]) -> list[dict[str, Any]]:
        include_archived = bool(args.get("include_archived", False))
        records = self._resource_registries()["workspaces"].values()
        return [copy.deepcopy(item) for item in sorted(records, key=lambda item: item["workspace_id"])
                if include_archived or not item["archived"]]

    def _op_workspace_update(self, args: dict[str, Any]) -> dict[str, Any]:
        workspace_id = self._identifier(args["workspace_id"], "workspace_id")
        self._active_workspace(workspace_id)
        changes = {name: copy.deepcopy(args[name]) for name in ("name", "metadata") if name in args}
        if not changes:
            raise ArgumentValidationError("workspace update requires name or metadata")
        return self._replace_record("workspaces", workspace_id, changes)

    def _op_workspace_archive(self, args: dict[str, Any]) -> dict[str, Any]:
        workspace_id = self._identifier(args["workspace_id"], "workspace_id")
        workspace = self._lookup("workspaces", workspace_id)
        if workspace["archived"]:
            return workspace
        active = [job["job_id"] for job in self._resource_registries()["jobs"].values()
                  if job["workspace_id"] == workspace_id and job["status"] in {"queued", "running"}]
        if active:
            raise StateConflictError(f"workspace has active jobs: {active}")
        return self._replace_record("workspaces", workspace_id, {"archived": True})

    def _op_artifact_register(self, args: dict[str, Any]) -> dict[str, Any]:
        artifact_id = self._identifier(args["artifact_id"], "artifact_id")
        workspace_id = self._identifier(args["workspace_id"], "workspace_id")
        self._active_workspace(workspace_id)
        if artifact_id in self._resource_registries()["artifacts"]:
            raise StateConflictError("artifact already exists and is immutable")
        content_hash = args["content_hash72"]
        if not _HASH72.fullmatch(content_hash):
            raise ArgumentValidationError("content_hash72 must be 72 lowercase hexadecimal glyphs")
        return self._commit_record("artifacts", artifact_id, {
            "schema": RESOURCE_SCHEMAS["artifacts"],
            "artifact_id": artifact_id,
            "workspace_id": workspace_id,
            "media_type": args["media_type"],
            "content_hash72": content_hash,
            "size_bytes": args["size_bytes"],
            "metadata": copy.deepcopy(args.get("metadata", {})),
            "version": 1,
        })

    def _op_artifact_get(self, args: dict[str, Any]) -> dict[str, Any]:
        return self._lookup("artifacts", self._identifier(args["artifact_id"], "artifact_id"))

    def _op_artifact_list(self, args: dict[str, Any]) -> list[dict[str, Any]]:
        workspace_id = args.get("workspace_id")
        if workspace_id is not None:
            self._identifier(workspace_id, "workspace_id")
        records = self._resource_registries()["artifacts"].values()
        return [copy.deepcopy(item) for item in sorted(records, key=lambda item: item["artifact_id"])
                if workspace_id is None or item["workspace_id"] == workspace_id]

    def _op_provider_register(self, args: dict[str, Any]) -> dict[str, Any]:
        provider_id = self._identifier(args["provider_id"], "provider_id")
        if provider_id in self._resource_registries()["providers"]:
            raise StateConflictError("provider already exists")
        return self._commit_record("providers", provider_id, {
            "schema": RESOURCE_SCHEMAS["providers"],
            "provider_id": provider_id,
            "provider_kind": args["provider_kind"],
            "endpoint": args.get("endpoint", ""),
            "enabled": bool(args.get("enabled", True)),
            "metadata": copy.deepcopy(args.get("metadata", {})),
            "secret_material_present": False,
            "version": 1,
        })

    def _op_provider_get(self, args: dict[str, Any]) -> dict[str, Any]:
        return self._lookup("providers", self._identifier(args["provider_id"], "provider_id"))

    def _op_provider_list(self, args: dict[str, Any]) -> list[dict[str, Any]]:
        enabled_only = bool(args.get("enabled_only", False))
        records = self._resource_registries()["providers"].values()
        return [copy.deepcopy(item) for item in sorted(records, key=lambda item: item["provider_id"])
                if not enabled_only or item["enabled"]]

    def _op_provider_set_enabled(self, args: dict[str, Any]) -> dict[str, Any]:
        provider_id = self._identifier(args["provider_id"], "provider_id")
        provider = self._lookup("providers", provider_id)
        enabled = args["enabled"]
        if provider["enabled"] == enabled:
            return provider
        if not enabled:
            active = [job["job_id"] for job in self._resource_registries()["jobs"].values()
                      if job.get("provider_id") == provider_id and job["status"] in {"queued", "running"}]
            if active:
                raise StateConflictError(f"provider has active jobs: {active}")
        return self._replace_record("providers", provider_id, {"enabled": enabled})

    def _op_capability_define(self, args: dict[str, Any]) -> dict[str, Any]:
        scope = self._scope(args["scope"])
        if scope in self._resource_registries()["capabilities"]:
            raise StateConflictError("capability already exists")
        return self._commit_record("capabilities", scope, {
            "schema": RESOURCE_SCHEMAS["capabilities"],
            "scope": scope,
            "description": args["description"],
            "risk_class": args.get("risk_class", "bounded"),
            "version": 1,
        })

    def _op_capability_get(self, args: dict[str, Any]) -> dict[str, Any]:
        return self._lookup("capabilities", self._scope(args["scope"]))

    def _op_capability_list(self, _args: dict[str, Any]) -> list[dict[str, Any]]:
        records = self._resource_registries()["capabilities"].values()
        return [copy.deepcopy(item) for item in sorted(records, key=lambda item: item["scope"])]

    def _op_job_submit(self, args: dict[str, Any]) -> dict[str, Any]:
        job_id = self._identifier(args["job_id"], "job_id")
        workspace_id = self._identifier(args["workspace_id"], "workspace_id")
        self._active_workspace(workspace_id)
        if job_id in self._resource_registries()["jobs"]:
            raise StateConflictError("job already exists")
        operation = self.registry.resolve(args["operation_id"])
        _validate_schema(args["arguments"], operation.argument_schema)
        provider_id = args.get("provider_id")
        if provider_id is not None:
            provider_id = self._identifier(provider_id, "provider_id")
            provider = self._lookup("providers", provider_id)
            if not provider["enabled"]:
                raise StateConflictError("provider is disabled")
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
            raise CapabilityDeniedErrorForJob(
                f"job must declare target operation capability: {operation.capability}"
            )
        request_payload = {
            "workspace_id": workspace_id,
            "operation_id": operation.operation_id,
            "operation_hash216": operation.raw["Hash216_identity"],
            "arguments": copy.deepcopy(args["arguments"]),
            "provider_id": provider_id,
            "input_artifact_ids": input_artifacts,
            "required_capabilities": required_capabilities,
        }
        return self._commit_record("jobs", job_id, {
            "schema": RESOURCE_SCHEMAS["jobs"],
            "job_id": job_id,
            **request_payload,
            "request_hash72": hash72("pass190.job.request", request_payload),
            "metadata": copy.deepcopy(args.get("metadata", {})),
            "status": "queued",
            "worker_id": None,
            "result": None,
            "error": None,
            "output_artifact_ids": [],
            "version": 1,
        })

    def _op_job_get(self, args: dict[str, Any]) -> dict[str, Any]:
        return self._lookup("jobs", self._identifier(args["job_id"], "job_id"))

    def _op_job_list(self, args: dict[str, Any]) -> list[dict[str, Any]]:
        workspace_id = args.get("workspace_id")
        status = args.get("status")
        if workspace_id is not None:
            self._identifier(workspace_id, "workspace_id")
        if status is not None and status not in JOB_STATUSES:
            raise ArgumentValidationError("unknown job status")
        records = self._resource_registries()["jobs"].values()
        return [copy.deepcopy(item) for item in sorted(records, key=lambda item: item["job_id"])
                if (workspace_id is None or item["workspace_id"] == workspace_id)
                and (status is None or item["status"] == status)]

    def _op_job_claim(self, args: dict[str, Any]) -> dict[str, Any]:
        job_id = self._identifier(args["job_id"], "job_id")
        worker_id = self._identifier(args["worker_id"], "worker_id")
        job = self._lookup("jobs", job_id)
        if job["status"] != "queued":
            raise StateConflictError("only queued jobs can be claimed")
        return self._replace_record("jobs", job_id, {"status": "running", "worker_id": worker_id})

    def _op_job_complete(self, args: dict[str, Any]) -> dict[str, Any]:
        job_id = self._identifier(args["job_id"], "job_id")
        job = self._lookup("jobs", job_id)
        if job["status"] != "running":
            raise StateConflictError("only running jobs can complete")
        output_artifacts = self._unique(list(args.get("output_artifact_ids", [])), "output_artifact_ids")
        for artifact_id in output_artifacts:
            artifact = self._lookup("artifacts", self._identifier(artifact_id, "artifact_id"))
            if artifact["workspace_id"] != job["workspace_id"]:
                raise StateConflictError("job output artifact belongs to another workspace")
        return self._replace_record("jobs", job_id, {
            "status": "completed",
            "result": copy.deepcopy(args["result"]),
            "error": None,
            "output_artifact_ids": output_artifacts,
        })

    def _op_job_fail(self, args: dict[str, Any]) -> dict[str, Any]:
        job_id = self._identifier(args["job_id"], "job_id")
        job = self._lookup("jobs", job_id)
        if job["status"] not in {"queued", "running"}:
            raise StateConflictError("only queued or running jobs can fail")
        return self._replace_record("jobs", job_id, {
            "status": "failed",
            "error": copy.deepcopy(args["error"]),
            "result": None,
        })

    @staticmethod
    def _verify_receipt_identity(receipt: Mapping[str, Any]) -> None:
        payload = {key: copy.deepcopy(value) for key, value in receipt.items() if key not in {"hash72", "hash216"}}
        if hash72("pass190.receipt", payload) != receipt["hash72"]:
            raise ReplayMismatchError("Hash72 replay mismatch")
        if hash216("pass190.receipt.topology", payload) != receipt["hash216"]:
            raise ReplayMismatchError("Hash216 replay mismatch")

    def _replay_resource(self, receipt: Mapping[str, Any]) -> InvocationResult:
        self._verify_receipt_identity(receipt)
        operation_id = str(receipt["operation_id"])
        arguments = copy.deepcopy(receipt["arguments"])
        result = copy.deepcopy(receipt["result"])
        if operation_id.endswith(".list"):
            if not isinstance(result, list):
                raise ReplayMismatchError("resource list replay result is not an array")
            kind = operation_id.split(".", 1)[0] + "s"
            id_field = RESOURCE_ID_FIELDS[kind]
            identities = []
            for item in result:
                key = item.get(id_field) if isinstance(item, dict) else None
                if not isinstance(key, str):
                    raise ReplayMismatchError("resource list item identity is invalid")
                self._validate_record(kind, key, item)
                identities.append(key)
            if identities != sorted(identities):
                raise ReplayMismatchError("resource list is not canonically ordered")
            if operation_id == "workspace.list" and not arguments.get("include_archived", False):
                if any(item["archived"] for item in result):
                    raise ReplayMismatchError("workspace list includes archived entries")
            if operation_id == "artifact.list" and arguments.get("workspace_id") is not None:
                if any(item["workspace_id"] != arguments["workspace_id"] for item in result):
                    raise ReplayMismatchError("artifact list workspace filter mismatch")
            if operation_id == "provider.list" and arguments.get("enabled_only", False):
                if any(not item["enabled"] for item in result):
                    raise ReplayMismatchError("provider list enabled filter mismatch")
            if operation_id == "job.list":
                if arguments.get("workspace_id") is not None and any(
                    item["workspace_id"] != arguments["workspace_id"] for item in result
                ):
                    raise ReplayMismatchError("job list workspace filter mismatch")
                if arguments.get("status") is not None and any(
                    item["status"] != arguments["status"] for item in result
                ):
                    raise ReplayMismatchError("job list status filter mismatch")
        else:
            if not isinstance(result, dict):
                raise ReplayMismatchError("resource replay result is not an object")
            prefix = operation_id.split(".", 1)[0]
            kind = prefix + "s"
            id_field = RESOURCE_ID_FIELDS[kind]
            key = result.get(id_field)
            if not isinstance(key, str):
                raise ReplayMismatchError("resource replay identity is invalid")
            self._validate_record(kind, key, result)
            argument_key = arguments.get(id_field)
            if argument_key is not None and argument_key != key:
                raise ReplayMismatchError("resource replay argument identity mismatch")
            required_status = {
                "job.submit": "queued",
                "job.claim": "running",
                "job.complete": "completed",
                "job.fail": "failed",
            }.get(operation_id)
            if required_status is not None and result.get("status") != required_status:
                raise ReplayMismatchError("job lifecycle replay status mismatch")
            if operation_id == "workspace.archive" and not result.get("archived"):
                raise ReplayMismatchError("workspace archive replay mismatch")
            if operation_id == "provider.set_enabled" and result.get("enabled") != arguments.get("enabled"):
                raise ReplayMismatchError("provider state replay mismatch")
        return InvocationResult(operation_id, result, receipt, "replay", True)


class CapabilityDeniedErrorForJob(ArgumentValidationError):
    """A queued job omitted a capability required by its target operation."""


_CONTEXT: ResourceRegistryContext | None = None
_CONTEXT_LOCK = threading.Lock()
_CONTEXT_PATH: Path | None = None


def get_iteration6_context(database_path: Path | str | None = None) -> ResourceRegistryContext:
    global _CONTEXT, _CONTEXT_PATH
    requested = Path(database_path or DEFAULT_DATABASE)
    if _CONTEXT is None:
        with _CONTEXT_LOCK:
            if _CONTEXT is None:
                _CONTEXT = ResourceRegistryContext(requested)
                _CONTEXT_PATH = requested
    elif _CONTEXT_PATH != requested:
        raise PersistentStoreError("process authority context already bound to another database")
    return _CONTEXT

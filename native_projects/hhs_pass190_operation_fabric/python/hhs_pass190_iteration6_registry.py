#!/usr/bin/env python3
"""Pass 190 Iteration 6 generated resource-operation registry overlay."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Mapping

from hhs_pass190 import (
    DEFAULT_REGISTRY,
    REGISTRY_SCHEMA,
    OperationRecord,
    OperationRegistry,
    RegistryValidationError,
    hash216,
)

ITERATION6_CONTRACT = "HHS-P190-I6-URR-JLC-CF-VM81-H72-H216"
ITERATION6_CLASSIFICATION = "HHS_PASS_190_ITERATION_6_UNIFIED_RESOURCE_REGISTRY_JOB_LIFECYCLE_FOUNDATION_VERIFIED"
RESOURCE_REGISTRY_SCHEMA = "HHS_PASS_190_RESOURCE_REGISTRY_V1"
RESOURCE_KINDS = ("workspaces", "artifacts", "providers", "capabilities", "jobs")


def _string(max_length: int = 128) -> dict[str, Any]:
    return {"type": "string", "maxLength": max_length}


def _object() -> dict[str, Any]:
    return {"type": "object"}


def _string_array(max_items: int = 4096, max_length: int = 256) -> dict[str, Any]:
    return {"type": "array", "maxItems": max_items, "items": _string(max_length)}


def _operation(
    operation_id: str,
    canonical_name: str,
    constructor: str,
    capability: str,
    effect_class: str,
    argument_schema: Mapping[str, Any],
    result_type: str,
    shell_form: str,
    *,
    operation_class: str = "resource-registry",
) -> dict[str, Any]:
    namespace = operation_id.split(".", 1)[0]
    record: dict[str, Any] = {
        "operation_id": operation_id,
        "canonical_name": canonical_name,
        "harmonicode_constructor": constructor,
        "constructor_version": "6.0.0",
        "namespace": namespace,
        "aliases": [],
        "introduced_by_pass": 190,
        "semantic_version": "1.0.0",
        "operation_class": operation_class,
        "effect_class": effect_class,
        "mutation_class": "registry" if effect_class == "mutation" else "none",
        "argument_schema": copy.deepcopy(dict(argument_schema)),
        "result_schema": {"type": result_type},
        "streaming_schema": {"type": "none"},
        "error_schema": {"typed": True},
        "exception_mappings": [],
        "capability_scope": capability,
        "authorization_scope": "local-or-remote",
        "admission_policy": "registry-validation-capability-zero-bypass",
        "resource_bounds": {"max_payload_bytes": 65536},
        "timeout_policy": {"milliseconds": 5000},
        "idempotency_policy": "supported",
        "determinism_class": "deterministic",
        "replay_supported": True,
        "reverse_supported": False,
        "VM81_binding": f"VM81:{operation_id}",
        "native_ABI_symbols": [],
        "HTTP_method": "POST",
        "HTTP_path": f"/api/pass190/operations/{operation_id}",
        "WebSocket_channel": "pass190.receipts",
        "CLI_command": shell_form,
        "shell_forms": [shell_form],
        "Python_identities": [],
        "SDK_symbols": {"python": operation_id.replace(".", "_")},
        "GUI_action_ids": [f"pass190.invoke.{operation_id}"],
        "hydration_adapters": ["json", "harmonicode", "shell", "workflow"],
        "receipt_class": "HHS_PASS_190_RECEIPT_V1",
        "test_vectors": [],
        "deprecated_aliases": [],
        "implementation_status": "EXECUTABLE_VERIFIED",
    }
    identity = dict(record)
    record["Hash216_identity"] = hash216("pass190.operation", identity)
    return record


def resource_operation_records() -> tuple[dict[str, Any], ...]:
    string = _string
    obj = _object()
    ids = _string_array()
    records = (
        _operation(
            "workspace.create", "Create workspace", "WorkspaceCreate", "workspace:write", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "workspace_id": string(), "name": string(256), "metadata": obj,
            }, "required": ["workspace_id", "name"]},
            "object", "workspace-create",
        ),
        _operation(
            "workspace.get", "Get workspace", "WorkspaceGet", "workspace:read", "pure",
            {"type": "object", "additionalProperties": False, "properties": {
                "workspace_id": string(),
            }, "required": ["workspace_id"]},
            "object", "workspace-get",
        ),
        _operation(
            "workspace.list", "List workspaces", "WorkspaceList", "workspace:read", "pure",
            {"type": "object", "additionalProperties": False, "properties": {
                "include_archived": {"type": "boolean"},
            }, "required": []},
            "array", "workspace-list",
        ),
        _operation(
            "workspace.update", "Update workspace", "WorkspaceUpdate", "workspace:write", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "workspace_id": string(), "name": string(256), "metadata": obj,
            }, "required": ["workspace_id"]},
            "object", "workspace-update",
        ),
        _operation(
            "workspace.archive", "Archive workspace", "WorkspaceArchive", "workspace:write", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "workspace_id": string(),
            }, "required": ["workspace_id"]},
            "object", "workspace-archive",
        ),
        _operation(
            "artifact.register", "Register immutable artifact", "ArtifactRegister", "artifact:write", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "artifact_id": string(), "workspace_id": string(), "media_type": string(256),
                "content_hash72": string(72), "size_bytes": {"type": "integer", "minimum": 0},
                "metadata": obj,
            }, "required": ["artifact_id", "workspace_id", "media_type", "content_hash72", "size_bytes"]},
            "object", "artifact-register",
        ),
        _operation(
            "artifact.get", "Get artifact", "ArtifactGet", "artifact:read", "pure",
            {"type": "object", "additionalProperties": False, "properties": {
                "artifact_id": string(),
            }, "required": ["artifact_id"]},
            "object", "artifact-get",
        ),
        _operation(
            "artifact.list", "List artifacts", "ArtifactList", "artifact:read", "pure",
            {"type": "object", "additionalProperties": False, "properties": {
                "workspace_id": string(),
            }, "required": []},
            "array", "artifact-list",
        ),
        _operation(
            "provider.register", "Register governed provider", "ProviderRegister", "provider:admin", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "provider_id": string(), "provider_kind": string(128), "endpoint": string(2048),
                "enabled": {"type": "boolean"}, "metadata": obj,
            }, "required": ["provider_id", "provider_kind"]},
            "object", "provider-register",
        ),
        _operation(
            "provider.get", "Get provider", "ProviderGet", "provider:read", "pure",
            {"type": "object", "additionalProperties": False, "properties": {
                "provider_id": string(),
            }, "required": ["provider_id"]},
            "object", "provider-get",
        ),
        _operation(
            "provider.list", "List providers", "ProviderList", "provider:read", "pure",
            {"type": "object", "additionalProperties": False, "properties": {
                "enabled_only": {"type": "boolean"},
            }, "required": []},
            "array", "provider-list",
        ),
        _operation(
            "provider.set_enabled", "Set provider enabled state", "ProviderSetEnabled", "provider:admin", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "provider_id": string(), "enabled": {"type": "boolean"},
            }, "required": ["provider_id", "enabled"]},
            "object", "provider-set-enabled",
        ),
        _operation(
            "capability.define", "Define capability scope", "CapabilityDefine", "capability:admin", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "scope": string(256), "description": string(2048), "risk_class": string(64),
            }, "required": ["scope", "description"]},
            "object", "capability-define",
        ),
        _operation(
            "capability.get", "Get capability scope", "CapabilityGet", "capability:read", "pure",
            {"type": "object", "additionalProperties": False, "properties": {
                "scope": string(256),
            }, "required": ["scope"]},
            "object", "capability-get",
        ),
        _operation(
            "capability.list", "List capability scopes", "CapabilityList", "capability:read", "pure",
            {"type": "object", "additionalProperties": False, "properties": {}, "required": []},
            "array", "capability-list",
        ),
        _operation(
            "job.submit", "Submit governed job", "JobSubmit", "job:write", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "job_id": string(), "workspace_id": string(), "operation_id": string(256),
                "arguments": obj, "provider_id": string(), "input_artifact_ids": ids,
                "required_capabilities": ids, "metadata": obj,
            }, "required": ["job_id", "workspace_id", "operation_id", "arguments"]},
            "object", "job-submit", operation_class="job-registry",
        ),
        _operation(
            "job.get", "Get job", "JobGet", "job:read", "pure",
            {"type": "object", "additionalProperties": False, "properties": {
                "job_id": string(),
            }, "required": ["job_id"]},
            "object", "job-get", operation_class="job-registry",
        ),
        _operation(
            "job.list", "List jobs", "JobList", "job:read", "pure",
            {"type": "object", "additionalProperties": False, "properties": {
                "workspace_id": string(), "status": string(64),
            }, "required": []},
            "array", "job-list", operation_class="job-registry",
        ),
        _operation(
            "job.claim", "Claim queued job", "JobClaim", "job:write", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "job_id": string(), "worker_id": string(256),
            }, "required": ["job_id", "worker_id"]},
            "object", "job-claim", operation_class="job-registry",
        ),
        _operation(
            "job.complete", "Complete running job", "JobComplete", "job:write", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "job_id": string(), "result": obj, "output_artifact_ids": ids,
            }, "required": ["job_id", "result"]},
            "object", "job-complete", operation_class="job-registry",
        ),
        _operation(
            "job.fail", "Fail queued or running job", "JobFail", "job:write", "mutation",
            {"type": "object", "additionalProperties": False, "properties": {
                "job_id": string(), "error": obj,
            }, "required": ["job_id", "error"]},
            "object", "job-fail", operation_class="job-registry",
        ),
    )
    return tuple(copy.deepcopy(item) for item in records)


RESOURCE_OPERATION_RECORDS = resource_operation_records()
RESOURCE_OPERATION_IDS = tuple(record["operation_id"] for record in RESOURCE_OPERATION_RECORDS)


class ExpandedOperationRegistry(OperationRegistry):
    """Canonical Pass 190 registry plus deterministic Iteration 6 resource operations."""

    def __init__(self, registry_path: Path = DEFAULT_REGISTRY):
        base = OperationRegistry(registry_path)
        combined_records = [copy.deepcopy(dict(record.raw)) for record in base.records]
        combined_records.extend(copy.deepcopy(record) for record in RESOURCE_OPERATION_RECORDS)
        identity = {
            "schema": REGISTRY_SCHEMA,
            "contract": ITERATION6_CONTRACT,
            "parent_contract": base.payload.get("contract"),
            "parent_registry_hash216": base.payload.get("registry_hash216"),
            "iteration": 6,
            "operations": combined_records,
        }
        self.payload = {
            **identity,
            "registry_hash216": hash216("pass190.iteration6.registry", identity),
            "native_operation_count": len(base.records),
            "governed_operation_count": len(combined_records),
        }
        self.records = tuple(OperationRecord(record) for record in combined_records)
        self.by_id = {}
        self.by_constructor = {}
        self.by_python = {}
        self.by_shell = {}
        self._validate_and_index()
        if len(self.records) != len(base.records) + len(RESOURCE_OPERATION_RECORDS):
            raise RegistryValidationError("expanded registry operation count mismatch")
        if tuple(record.operation_id for record in self.records[-len(RESOURCE_OPERATION_RECORDS):]) != RESOURCE_OPERATION_IDS:
            raise RegistryValidationError("resource operation order mismatch")


def registry_document(registry_path: Path = DEFAULT_REGISTRY) -> dict[str, Any]:
    registry = ExpandedOperationRegistry(registry_path)
    return json.loads(json.dumps(registry.payload, sort_keys=True))

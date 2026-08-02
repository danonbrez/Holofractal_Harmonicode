#!/usr/bin/env python3
"""Final Iteration 6 runtime surface with persistent event and arbitration APIs."""
from __future__ import annotations

import copy
import threading
from pathlib import Path
from typing import Any, Mapping

from hhs_pass190 import InvocationResult, ReplayMismatchError
from hhs_pass190_iteration2 import PersistentStoreError
from hhs_pass190_iteration3_hardening import DEFAULT_DATABASE
from hhs_pass190_iteration6 import (
    RESOURCE_ID_FIELDS,
    RESOURCE_OPERATION_IDS,
    ResourceRegistryContext,
)

_KIND_BY_PREFIX = {
    "workspace": "workspaces",
    "artifact": "artifacts",
    "provider": "providers",
    "capability": "capabilities",
    "job": "jobs",
}


class UnifiedResourceRegistryContext(ResourceRegistryContext):
    """Resource authority plus all inherited persistent transport projections."""

    def receipts_after(self, receipt_index: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        return self.store.receipts_after(receipt_index, limit)

    def events_after(self, sequence: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        return self.store.events_after(sequence, limit)

    def wait_for_events(self, sequence: int, timeout: float = 15.0) -> list[dict[str, Any]]:
        return self.store.wait_for_events(sequence, timeout)

    def arbitration_report(self) -> dict[str, Any]:
        return self.store.arbitration_report()

    def lease_receipts_after(self, sequence: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        return self.store.lease_receipts_after(sequence, limit)

    def _replay_resource(self, receipt: Mapping[str, Any]) -> InvocationResult:
        self._verify_receipt_identity(receipt)
        operation_id = str(receipt["operation_id"])
        if operation_id not in RESOURCE_OPERATION_IDS:
            raise ReplayMismatchError("operation is outside the resource overlay")
        arguments = copy.deepcopy(receipt["arguments"])
        result = copy.deepcopy(receipt["result"])
        prefix = operation_id.split(".", 1)[0]
        kind = _KIND_BY_PREFIX[prefix]
        id_field = RESOURCE_ID_FIELDS[kind]
        if operation_id.endswith(".list"):
            if not isinstance(result, list):
                raise ReplayMismatchError("resource list replay result is not an array")
            identities: list[str] = []
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


_CONTEXT: UnifiedResourceRegistryContext | None = None
_CONTEXT_LOCK = threading.Lock()
_CONTEXT_PATH: Path | None = None


def get_iteration6_runtime(database_path: Path | str | None = None) -> UnifiedResourceRegistryContext:
    global _CONTEXT, _CONTEXT_PATH
    requested = Path(database_path or DEFAULT_DATABASE)
    if _CONTEXT is None:
        with _CONTEXT_LOCK:
            if _CONTEXT is None:
                _CONTEXT = UnifiedResourceRegistryContext(requested)
                _CONTEXT_PATH = requested
    elif _CONTEXT_PATH != requested:
        raise PersistentStoreError("process authority context already bound to another database")
    return _CONTEXT

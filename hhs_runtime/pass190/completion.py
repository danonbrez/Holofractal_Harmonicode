"""Pass 190 full-contract completion coordinator.

This layer composes the already-implemented Pass 190 Iteration-7 authority
with the frozen I135 repository hydration runtime. It does not implement a
parallel operation engine or persistence path.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping, Optional

from hhs_runtime.pass191.repository_hydration import RepositoryHydrationRuntime

from .python_compat import (
    EXECUTABLE_MAPPINGS,
    build_python_compatibility_registry,
    compatibility_summary,
)

CONTRACT_ID = "HHS-P190-OVRA-HOSS-PCA-FHF-VM81-H72-H216"
CONTRACT_AUTHORIZATION_COMMIT = "88e7ae935990b1c36db6d39bc46d3b89b2e465cb"
FROZEN_I135 = "5e593b384732ffb065480cdd2d1098f1f32a990e"
ITERATION7_MERGE = "7b4825ae1437c2325bc9bb348086c0957cfd5c28"
COMPLETION_CLASSIFICATION = (
    "HHS_PASS_190_I136_COMPLETION_COORDINATOR_IMPLEMENTED_PENDING_ACCEPTANCE"
)

ROOT = Path(__file__).resolve().parents[2]
PASS190_NATIVE_PYTHON = (
    ROOT / "native_projects" / "hhs_pass190_operation_fabric" / "python"
)


def _load_native() -> tuple[Any, Any, Any, Any]:
    text = str(PASS190_NATIVE_PYTHON)
    if text not in sys.path:
        sys.path.insert(0, text)
    from hhs_pass190 import parse_constructor  # type: ignore
    from hhs_pass190_iteration7 import DurableExecutionContext  # type: ignore
    from hhs_pass190_iteration7_registry import Iteration7OperationRegistry  # type: ignore
    from hhs_pass190_capability import verify_capability_token  # type: ignore

    return DurableExecutionContext, Iteration7OperationRegistry, parse_constructor, verify_capability_token


DurableExecutionContext, Iteration7OperationRegistry, parse_constructor, verify_capability_token = _load_native()

from .acceptance import Pass190AcceptanceAuthorityContext


class Pass190CompletionError(RuntimeError):
    pass


@dataclass(frozen=True)
class PythonInvocation:
    identity: str
    operation_id: str
    arguments: Mapping[str, Any]


def _adapt_python(identity: str, args: list[Any], kwargs: Mapping[str, Any]) -> PythonInvocation:
    if identity not in EXECUTABLE_MAPPINGS:
        raise Pass190CompletionError(f"HHS_P190_PYTHON_ADAPTER_REQUIRED:{identity}")

    operation_id = EXECUTABLE_MAPPINGS[identity][0]
    if identity == "builtins.len":
        if len(args) != 1 or kwargs:
            raise Pass190CompletionError("HHS_P190_PYTHON_SIGNATURE_MISMATCH:builtins.len")
        payload = {"value": args[0]}
    elif identity == "builtins.abs":
        if len(args) != 1 or kwargs:
            raise Pass190CompletionError("HHS_P190_PYTHON_SIGNATURE_MISMATCH:builtins.abs")
        payload = {"value": args[0]}
    elif identity == "builtins.sorted":
        if len(args) != 1 or set(kwargs) - {"reverse"}:
            raise Pass190CompletionError("HHS_P190_PYTHON_SIGNATURE_MISMATCH:builtins.sorted")
        payload = {"values": list(args[0]), "reverse": bool(kwargs.get("reverse", False))}
    elif identity == "builtins.str.join":
        if len(args) != 2 or kwargs:
            raise Pass190CompletionError("HHS_P190_PYTHON_SIGNATURE_MISMATCH:builtins.str.join")
        payload = {"separator": args[0], "values": list(args[1])}
    elif identity == "builtins.dict.get":
        if len(args) not in {2, 3} or kwargs:
            raise Pass190CompletionError("HHS_P190_PYTHON_SIGNATURE_MISMATCH:builtins.dict.get")
        payload = {
            "mapping": dict(args[0]),
            "key": args[1],
            "default": args[2] if len(args) == 3 else None,
        }
    elif identity == "math.gcd":
        if len(args) != 2 or kwargs:
            raise Pass190CompletionError("HHS_P190_PYTHON_SIGNATURE_MISMATCH:math.gcd")
        payload = {"a": args[0], "b": args[1]}
    else:
        raise Pass190CompletionError(f"HHS_P190_PYTHON_ADAPTER_REQUIRED:{identity}")
    return PythonInvocation(identity, operation_id, payload)


class Pass190CompletionContext:
    """One composed authority context for Pass 190 completion surfaces."""

    def __init__(
        self,
        *,
        database_path: Path | str,
        repository_root: Path | str = ROOT,
        hydration_state_root: Path | str | None = None,
        capability_secret: str | bytes | None = None,
        require_pinned_python: bool = True,
    ) -> None:
        self.database_path = Path(database_path)
        self.authority = Pass190AcceptanceAuthorityContext(self.database_path)
        self.registry = self.authority.registry
        self.capability_secret = capability_secret
        state_root = hydration_state_root or (
            self.database_path.parent / "pass190-hydration"
        )
        self.hydration = RepositoryHydrationRuntime(repository_root, state_root)
        self.python_compat = build_python_compatibility_registry(
            require_pinned_version=require_pinned_python
        )
        if len(self.registry.records) != 52:
            raise Pass190CompletionError("HHS_P190_I136_OPERATION_COUNT_DRIFT")

    @property
    def runtime_mode(self) -> str:
        return (
            "FULL_CANONICAL_RUNTIME"
            if self.capability_secret is not None
            else "READ_ONLY_CANONICAL_RUNTIME"
        )

    def status(self) -> dict[str, Any]:
        return {
            "contract": CONTRACT_ID,
            "authorization_commit": CONTRACT_AUTHORIZATION_COMMIT,
            "iteration7_merge": ITERATION7_MERGE,
            "frozen_predecessor_i135": FROZEN_I135,
            "classification": COMPLETION_CLASSIFICATION,
            "runtime_mode": self.runtime_mode,
            "governed_operation_count": len(self.registry.records),
            "historical_iteration7_operation_count": 42,
            "i136_project_acceptance_operation_count": 10,
            "registry_hash216": self.registry.payload["registry_hash216"],
            "python_compatibility": compatibility_summary(self.python_compat),
            "full_hydration": "REUSED_FROM_FROZEN_I135",
            "singleton_vm81_authority": "INHERITED_PASS190_DURABLE_AUTHORITY",
            "new_vm81_authority": False,
            "new_receipt_clock": False,
            "floating_point_canonical_authority": False,
        }

    def operations(self) -> list[dict[str, Any]]:
        return [dict(record.raw) for record in self.registry.records]

    def resolve_operation(self, operation_id: str) -> dict[str, Any]:
        return dict(self.registry.resolve(operation_id).raw)

    def verify_capability(
        self,
        authorization_token: str | None,
        required_scope: str,
    ) -> frozenset[str]:
        if required_scope in {"public", "none"}:
            return frozenset()
        if self.capability_secret is None:
            raise Pass190CompletionError("HHS_P190_FULL_RUNTIME_CAPABILITY_SECRET_REQUIRED")
        if not authorization_token:
            raise Pass190CompletionError("HHS_P190_CAPABILITY_REQUIRED")
        principal = verify_capability_token(
            authorization_token,
            self.capability_secret,
            required_scope=required_scope,
        )
        return principal.scopes

    def invoke(
        self,
        operation_id: str,
        arguments: Mapping[str, Any] | None = None,
        *,
        surface: str,
        authorization_token: str | None = None,
        idempotency_key: str | None = None,
        expected_state: str | None = None,
    ) -> dict[str, Any]:
        record = self.registry.resolve(operation_id)
        capabilities = self.verify_capability(
            authorization_token,
            str(record.raw["capability_scope"]),
        )
        result = self.authority.invoke(
            operation_id,
            arguments,
            surface=surface,
            capabilities=capabilities,
            idempotency_key=idempotency_key,
            expected_state=expected_state,
        )
        return result.to_dict()

    def invoke_constructor(
        self,
        expression: str,
        *,
        authorization_token: str | None = None,
    ) -> dict[str, Any]:
        operation_id, arguments = parse_constructor(expression, self.registry)
        return self.invoke(
            operation_id,
            arguments,
            surface="harmonicode",
            authorization_token=authorization_token,
        )

    def invoke_python(
        self,
        identity: str,
        args: list[Any],
        kwargs: Mapping[str, Any] | None = None,
        *,
        authorization_token: str | None = None,
    ) -> dict[str, Any]:
        adapted = _adapt_python(identity, args, kwargs or {})
        return self.invoke(
            adapted.operation_id,
            adapted.arguments,
            surface="python",
            authorization_token=authorization_token,
        )

    def replay(self, receipt_hash72: str) -> dict[str, Any]:
        return self.authority.replay(receipt_hash72).to_dict()

    def hydration_preview(
        self,
        *,
        commit: str = "HEAD",
        since_commit: Optional[str] = None,
    ) -> dict[str, Any]:
        manifest = self.hydration.preview(
            commit=commit,
            since_commit=since_commit,
        )
        return self.hydration.compact(manifest)

    def compatibility_registry(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.python_compat, sort_keys=True))

    def openapi_registry_document(self) -> dict[str, Any]:
        paths: dict[str, Any] = {}
        for record in self.registry.records:
            operation_id = record.operation_id
            public_path = f"/v1/operations/{operation_id}"
            paths[public_path] = {
                "post": {
                    "operationId": operation_id,
                    "summary": record.raw["canonical_name"],
                    "x-hhs-constructor": record.constructor,
                    "x-hhs-hash216": record.raw["Hash216_identity"],
                    "x-hhs-capability": record.raw["capability_scope"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": record.argument_schema
                            }
                        },
                    },
                    "responses": {
                        "200": {"description": "Canonical operation result"},
                        "400": {"description": "Typed validation failure"},
                        "401": {"description": "Missing or invalid capability"},
                        "409": {"description": "State conflict"},
                    },
                }
            }
        return {
            "openapi": "3.1.0",
            "info": {
                "title": "HHS Pass 190 Canonical Public Operation Gateway",
                "version": "1.0.0",
            },
            "paths": paths,
            "x-hhs-contract": CONTRACT_ID,
            "x-hhs-runtime-mode": self.runtime_mode,
            "x-hhs-registry-hash216": self.registry.payload["registry_hash216"],
            "x-hhs-operation-count": len(self.registry.records),
            "x-hhs-python-compatibility-registry-hash216": self.python_compat[
                "registry_hash216"
            ],
        }


__all__ = [
    "CONTRACT_ID",
    "CONTRACT_AUTHORIZATION_COMMIT",
    "FROZEN_I135",
    "ITERATION7_MERGE",
    "COMPLETION_CLASSIFICATION",
    "Pass190CompletionContext",
    "Pass190CompletionError",
]

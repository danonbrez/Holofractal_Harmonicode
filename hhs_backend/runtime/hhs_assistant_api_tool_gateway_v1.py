"""Governed read-only HHS API tools for the Gemma 4 assistant thread.

The gateway exposes canonical HHS API route functions as model tools without
allowing a model-generated call to cross a mutation boundary. Every tool result
is returned in a Hash72-witnessed envelope and retains the route's own guarded
I/O receipts.
"""
from __future__ import annotations

import inspect
import time
from typing import Any, Awaitable, Callable, Dict, List, Mapping

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

VERSION = "HHS_ASSISTANT_API_TOOL_GATEWAY_V1"
AUTHORITY = "HHS_ASSISTANT_READ_ONLY_API_TOOL_AUTHORITY_V1"
TOOL_RECEIPT_SCHEMA = "HHS_ASSISTANT_API_TOOL_RECEIPT_V1"
TOOL_REGISTRY_SCHEMA = "HHS_ASSISTANT_API_TOOL_REGISTRY_V1"


ToolCallable = Callable[..., Any]


def _now_ms() -> int:
    return int(time.time() * 1000)


def _function_tool(name: str, description: str, properties: Dict[str, Any] | None = None, required: List[str] | None = None) -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties or {},
                "required": required or [],
                "additionalProperties": False,
            },
        },
    }


DEFAULT_HHS_ASSISTANT_TOOLS: List[Dict[str, Any]] = [
    _function_tool(
        "hhs_runtime_state",
        "Read the latest guarded HHS/VM81 runtime state through the canonical runtime API.",
    ),
    _function_tool(
        "hhs_runtime_services",
        "List services registered on the canonical HHS runtime API.",
    ),
    _function_tool(
        "hhs_runtime_service_status",
        "Read status for all registered HHS runtime services.",
    ),
    _function_tool(
        "hhs_kernel_invariants",
        "List the active kernel conformance invariants and their Hash72-governed definitions.",
    ),
    _function_tool(
        "hhs_kernel_conformance_status",
        "Read the current kernel invariant and conformance-surface status.",
    ),
    _function_tool(
        "hhs_pass152_status",
        "Read the current Pass 152 elastic-closure status and latest execution projection.",
    ),
    _function_tool(
        "hhs_pass152_capabilities",
        "Read the Pass 152 lifecycle, dependency, authority, and control-vector capabilities.",
    ),
]


async def _runtime_state(_: Mapping[str, Any]) -> Dict[str, Any]:
    from hhs_backend.api.runtime_routes import get_runtime_state
    return await get_runtime_state()


async def _runtime_services(_: Mapping[str, Any]) -> Dict[str, Any]:
    from hhs_backend.api.runtime_routes import list_runtime_services
    return await list_runtime_services()


async def _runtime_service_status(_: Mapping[str, Any]) -> Dict[str, Any]:
    from hhs_backend.api.runtime_routes import runtime_services_status
    return await runtime_services_status()


async def _kernel_invariants(_: Mapping[str, Any]) -> Dict[str, Any]:
    from hhs_backend.api.runtime_routes import list_kernel_conformance_invariants
    return await list_kernel_conformance_invariants()


async def _kernel_conformance_status(_: Mapping[str, Any]) -> Dict[str, Any]:
    from hhs_backend.api.runtime_routes import kernel_conformance_status
    return await kernel_conformance_status()


async def _pass152_status(_: Mapping[str, Any]) -> Dict[str, Any]:
    from hhs_backend.api.pass152_elastic_closure_routes import pass152_status
    result = pass152_status()
    return await result if inspect.isawaitable(result) else result


async def _pass152_capabilities(_: Mapping[str, Any]) -> Dict[str, Any]:
    from hhs_backend.api.pass152_elastic_closure_routes import pass152_capabilities
    result = pass152_capabilities()
    return await result if inspect.isawaitable(result) else result


_READ_ONLY_EXECUTORS: Dict[str, Callable[[Mapping[str, Any]], Awaitable[Dict[str, Any]]]] = {
    "hhs_runtime_state": _runtime_state,
    "hhs_runtime_services": _runtime_services,
    "hhs_runtime_service_status": _runtime_service_status,
    "hhs_kernel_invariants": _kernel_invariants,
    "hhs_kernel_conformance_status": _kernel_conformance_status,
    "hhs_pass152_status": _pass152_status,
    "hhs_pass152_capabilities": _pass152_capabilities,
}


def assistant_api_tool_registry() -> Dict[str, Any]:
    registry = {
        "schema": TOOL_REGISTRY_SCHEMA,
        "version": VERSION,
        "tools": DEFAULT_HHS_ASSISTANT_TOOLS,
        "tool_names": sorted(_READ_ONLY_EXECUTORS),
        "read_only": True,
        "model_self_authorization_allowed": False,
        "mutating_tool_execution_allowed": False,
        "authority": AUTHORITY,
    }
    registry["tool_registry_root_hash72"] = hash72(TOOL_REGISTRY_SCHEMA, registry)
    return registry


async def execute_hhs_assistant_api_tool(
    tool_name: str,
    arguments: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    name = str(tool_name or "")
    args = dict(arguments or {})
    executor = _READ_ONLY_EXECUTORS.get(name)
    if executor is None:
        receipt = {
            "schema": TOOL_RECEIPT_SCHEMA,
            "version": VERSION,
            "ok": False,
            "status": "REJECT_HHS_ASSISTANT_API_TOOL_CALL",
            "tool_name": name,
            "arguments": args,
            "reason": "tool is not registered as a read-only HHS assistant API surface",
            "read_only": True,
            "runtime_mutation_admitted": False,
            "model_self_authorized": False,
            "created_at_unix_ms": _now_ms(),
            "authority": AUTHORITY,
        }
        receipt["tool_receipt_root_hash72"] = hash72(TOOL_RECEIPT_SCHEMA, receipt)
        return receipt

    try:
        response = await executor(args)
        ok = True
        status = "ADMIT_READ_ONLY_HHS_ASSISTANT_API_TOOL_RESULT"
        error = None
    except Exception as exc:
        response = None
        ok = False
        status = "HHS_ASSISTANT_API_TOOL_EXECUTION_ERROR"
        error = f"{type(exc).__name__}: {exc}"

    receipt = {
        "schema": TOOL_RECEIPT_SCHEMA,
        "version": VERSION,
        "ok": ok,
        "status": status,
        "tool_name": name,
        "arguments": args,
        "response": response,
        "error": error,
        "read_only": True,
        "runtime_mutation_admitted": False,
        "model_self_authorized": False,
        "created_at_unix_ms": _now_ms(),
        "authority": AUTHORITY,
    }
    receipt["tool_receipt_root_hash72"] = hash72(TOOL_RECEIPT_SCHEMA, receipt)
    return receipt


async def assistant_api_tool_gateway_self_test() -> Dict[str, Any]:
    registry = assistant_api_tool_registry()
    status_receipt = await execute_hhs_assistant_api_tool("hhs_pass152_status", {})
    rejected = await execute_hhs_assistant_api_tool("hhs_runtime_halt", {})
    ok = bool(
        registry.get("tool_registry_root_hash72")
        and status_receipt.get("ok")
        and status_receipt.get("tool_receipt_root_hash72")
        and not status_receipt.get("runtime_mutation_admitted")
        and not rejected.get("ok")
        and rejected.get("status") == "REJECT_HHS_ASSISTANT_API_TOOL_CALL"
    )
    return {
        "schema": "HHS_ASSISTANT_API_TOOL_GATEWAY_SELF_TEST_V1",
        "version": VERSION,
        "ok": ok,
        "registry": registry,
        "status_receipt": status_receipt,
        "rejected_mutation_attempt": rejected,
    }

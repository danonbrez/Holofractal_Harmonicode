"""Pass 196 repository-integration, encrypted vector-memory, and API-tool routes."""
from __future__ import annotations

import asyncio
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_backend.api.runtime_routes import (
    _contract_response,
    io_gateway,
    runtime_controller,
    runtime_graph,
)
from hhs_backend.runtime.hhs_pass196_integrated_environment_v1 import (
    PASS196_INTEGRATED_ENVIRONMENT,
    Pass196Error,
)

router = APIRouter(
    prefix="/api/runtime/integration",
    tags=[
        "runtime",
        "vm81",
        "hash216",
        "repository-hydration",
        "encrypted-vector-memory",
        "linux-environment",
        "api-tool-server",
        "visual-ide",
        "pass196",
    ],
)


class IntegrationScanRequest(BaseModel):
    persist_vector: bool = True


class IntegrationToolInvokeRequest(BaseModel):
    tool: str = Field(min_length=1, max_length=128)
    arguments: Dict[str, Any] = Field(default_factory=dict)


def _ingress(operation: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return io_gateway.ingress(operation, payload)


def _egress(operation: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return io_gateway.egress(operation, payload)


def _receipt_hash72(authorized_tick: Dict[str, Any]) -> str | None:
    receipt = authorized_tick.get("receipt") if isinstance(authorized_tick, dict) else None
    if not isinstance(receipt, dict):
        return None
    value = receipt.get("receipt_hash72")
    return value if isinstance(value, str) and value else None


def _project_runtime_graph() -> None:
    packet = runtime_controller.export_multimodal_packet()
    runtime_graph.ingest_runtime_state(packet)


async def _run_scan(*, persist_vector: bool, source: str) -> Dict[str, Any]:
    authorized_tick = runtime_controller.authorized_tick(source=source)
    receipt_hash72 = _receipt_hash72(authorized_tick)
    result = await asyncio.to_thread(
        PASS196_INTEGRATED_ENVIRONMENT.scan,
        vm81_receipt_hash72=receipt_hash72,
        persist_vector=persist_vector,
    )
    _project_runtime_graph()
    result["vm81_authorized_tick"] = {
        "source": source,
        "receipt_hash72": receipt_hash72,
        "runtime_step": (
            authorized_tick.get("runtime", {}).get("step")
            if isinstance(authorized_tick, dict)
            else None
        ),
        "parallel_workers_grant_mutation_authority": False,
        "vector_projection_grants_source_authority": False,
    }
    return result


@router.get("/status")
def integration_status() -> Dict[str, Any]:
    operation = "api.runtime.integration.status"
    ingress = _ingress(operation, {"method": "GET"})
    result = PASS196_INTEGRATED_ENVIRONMENT.status()
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(
            operation,
            {
                "phase": result.get("phase"),
                "scanned": result.get("scanned"),
                "integration_closed": result.get("integration_closed", False),
                "manifest_hash72": result.get("manifest_hash72"),
            },
        ),
    }
    return _contract_response("/api/runtime/integration/status", "GET", result)


@router.post("/scan")
async def integration_scan(request: IntegrationScanRequest) -> Dict[str, Any]:
    operation = "api.runtime.integration.scan"
    ingress = _ingress(
        operation,
        {"method": "POST", "persist_vector": request.persist_vector},
    )
    try:
        result = await _run_scan(
            persist_vector=request.persist_vector,
            source=operation,
        )
    except (Pass196Error, OSError, ValueError, RuntimeError) as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "schema": "HHS_PASS_196_INTEGRATION_SCAN_FAILURE_V1",
                "ok": False,
                "reason": str(exc),
            },
        ) from exc
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(
            operation,
            {
                "phase": result.get("phase"),
                "integration_closed": result.get("integration_closed"),
                "manifest_hash72": result.get("manifest_hash72"),
                "file_count": result.get("file_count"),
                "vector_object_id": (result.get("vector") or {}).get("vector_object_id"),
            },
        ),
    }
    return _contract_response("/api/runtime/integration/scan", "POST", result)


@router.get("/manifest")
def integration_manifest() -> Dict[str, Any]:
    operation = "api.runtime.integration.manifest"
    ingress = _ingress(operation, {"method": "GET"})
    try:
        result = PASS196_INTEGRATED_ENVIRONMENT.manifest()
    except Pass196Error as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(
            operation,
            {
                "manifest_hash72": result.get("manifest_hash72"),
                "file_count": result.get("file_count"),
                "maximum_discovered_pass": result.get("maximum_discovered_pass"),
            },
        ),
    }
    return _contract_response("/api/runtime/integration/manifest", "GET", result)


@router.get("/gaps")
def integration_gaps() -> Dict[str, Any]:
    operation = "api.runtime.integration.gaps"
    ingress = _ingress(operation, {"method": "GET"})
    try:
        result = PASS196_INTEGRATED_ENVIRONMENT.gaps()
    except Pass196Error as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(
            operation,
            {
                "complete": result.get("complete"),
                "unresolved_pass_count": result.get("unresolved_pass_count"),
                "missing_mandatory_surfaces": result.get("missing_mandatory_surfaces"),
            },
        ),
    }
    return _contract_response("/api/runtime/integration/gaps", "GET", result)


@router.get("/tools")
def integration_tools() -> Dict[str, Any]:
    operation = "api.runtime.integration.tools"
    ingress = _ingress(operation, {"method": "GET"})
    result = PASS196_INTEGRATED_ENVIRONMENT.tools()
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(operation, {"tool_count": len(result["tools"])}),
    }
    return _contract_response("/api/runtime/integration/tools", "GET", result)


@router.post("/tools/invoke")
async def integration_tool_invoke(request: IntegrationToolInvokeRequest) -> Dict[str, Any]:
    operation = "api.runtime.integration.tools.invoke"
    ingress = _ingress(
        operation,
        {"method": "POST", "tool": request.tool},
    )
    try:
        if request.tool == "integration.status":
            result = PASS196_INTEGRATED_ENVIRONMENT.status()
        elif request.tool == "integration.scan":
            result = await _run_scan(
                persist_vector=bool(request.arguments.get("persist_vector", True)),
                source=operation,
            )
        elif request.tool == "integration.manifest":
            result = PASS196_INTEGRATED_ENVIRONMENT.manifest()
        elif request.tool == "integration.gaps":
            result = PASS196_INTEGRATED_ENVIRONMENT.gaps()
        else:
            raise Pass196Error(f"unknown integration tool: {request.tool}")
    except Pass196Error as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["tool_invocation"] = {
        "schema": "HHS_PASS_196_API_TOOL_INVOCATION_V1",
        "tool": request.tool,
        "tool_server_is_authority": False,
    }
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(
            operation,
            {
                "tool": request.tool,
                "ok": result.get("ok", True),
                "manifest_hash72": result.get("manifest_hash72"),
            },
        ),
    }
    return _contract_response("/api/runtime/integration/tools/invoke", "POST", result)

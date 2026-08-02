"""Pass 198 operation-calibration registry API and tool-server projection."""
from __future__ import annotations

import asyncio
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_backend.api.runtime_routes import _contract_response, io_gateway, runtime_controller
from hhs_backend.runtime.hhs_pass198_operation_calibration_registry_v1 import (
    PASS198_OPERATION_CALIBRATION_REGISTRY,
    Pass198RegistryError,
)

router = APIRouter(
    prefix="/api/runtime/calibration-registry",
    tags=["runtime", "vm81", "hash72", "calibration", "operation-registry", "simplification", "pass198"],
)


class OperationRegisterRequest(BaseModel):
    operation: Dict[str, Any]


class ParameterTreeRequest(BaseModel):
    operation_id: str = Field(min_length=1, max_length=256)
    overrides: Dict[str, Any] = Field(default_factory=dict)


class OperationRunRequest(BaseModel):
    operation_id: str = Field(min_length=1, max_length=256)
    config: Dict[str, Any] = Field(default_factory=dict)
    resume: bool = True


class SimplificationPromoteRequest(BaseModel):
    simplification_id: str = Field(min_length=1, max_length=256)
    target_status: str = Field(min_length=1, max_length=64)
    evidence_run_ids: List[str] = Field(min_length=1)


class SimplificationRevokeRequest(BaseModel):
    simplification_id: str = Field(min_length=1, max_length=256)
    reason: Dict[str, Any]


class RegistryToolInvokeRequest(BaseModel):
    tool: str = Field(min_length=1, max_length=128)
    arguments: Dict[str, Any] = Field(default_factory=dict)


def _ingress(operation: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return io_gateway.ingress(operation, payload)


def _egress(operation: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return io_gateway.egress(operation, payload)


def _authorized_receipt(source: str) -> tuple[Dict[str, Any], str | None]:
    tick = runtime_controller.authorized_tick(source=source)
    receipt = tick.get("receipt") if isinstance(tick, dict) else None
    value = receipt.get("receipt_hash72") if isinstance(receipt, dict) else None
    return tick, value if isinstance(value, str) and value else None


def _tick_projection(source: str, tick: Dict[str, Any], receipt_hash72: str | None) -> Dict[str, Any]:
    return {
        "source": source,
        "receipt_hash72": receipt_hash72,
        "runtime_step": tick.get("runtime", {}).get("step") if isinstance(tick, dict) else None,
        "api_or_worker_grants_authority": False,
    }


@router.get("/status")
def registry_status() -> Dict[str, Any]:
    operation = "api.runtime.calibration_registry.status"
    ingress = _ingress(operation, {"method": "GET"})
    result = PASS198_OPERATION_CALIBRATION_REGISTRY.status()
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(operation, {"ok": result.get("ok"), "operation_count": result.get("operation_count"), "run_count": result.get("run_count")}),
    }
    return _contract_response("/api/runtime/calibration-registry/status", "GET", result)


@router.get("/operations")
def operation_list() -> Dict[str, Any]:
    operation = "api.runtime.calibration_registry.operations.list"
    ingress = _ingress(operation, {"method": "GET"})
    items = PASS198_OPERATION_CALIBRATION_REGISTRY.list_operations()
    result = {"schema": "HHS_PASS_198_OPERATION_LIST_V1", "operations": items, "count": len(items)}
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"count": len(items)})}
    return _contract_response("/api/runtime/calibration-registry/operations", "GET", result)


@router.get("/operations/{operation_id}")
def operation_get(operation_id: str) -> Dict[str, Any]:
    operation = "api.runtime.calibration_registry.operations.get"
    ingress = _ingress(operation, {"method": "GET", "operation_id": operation_id})
    try:
        result = PASS198_OPERATION_CALIBRATION_REGISTRY.get_operation(operation_id)
    except Pass198RegistryError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"operation_id": operation_id, "spec_hash72": result.get("spec_hash72")})}
    return _contract_response(f"/api/runtime/calibration-registry/operations/{operation_id}", "GET", result)


@router.post("/operations")
def operation_register(request: OperationRegisterRequest) -> Dict[str, Any]:
    operation = "api.runtime.calibration_registry.operations.register"
    ingress = _ingress(operation, {"method": "POST", "operation_id": request.operation.get("operation_id")})
    tick, receipt_hash72 = _authorized_receipt(operation)
    try:
        result = PASS198_OPERATION_CALIBRATION_REGISTRY.register_operation(request.operation, source=operation)
    except (Pass198RegistryError, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["vm81_authorized_tick"] = _tick_projection(operation, tick, receipt_hash72)
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"operation_id": result.get("operation_id"), "spec_hash72": result.get("spec_hash72")})}
    return _contract_response("/api/runtime/calibration-registry/operations", "POST", result)


@router.post("/parameter-tree")
def parameter_tree(request: ParameterTreeRequest) -> Dict[str, Any]:
    operation = "api.runtime.calibration_registry.parameter_tree"
    ingress = _ingress(operation, {"method": "POST", "operation_id": request.operation_id})
    try:
        result = PASS198_OPERATION_CALIBRATION_REGISTRY.parameter_tree(request.operation_id, request.overrides)
    except (Pass198RegistryError, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"tree_hash72": result.get("tree_hash72"), "state_count": result.get("state_count")})}
    return _contract_response("/api/runtime/calibration-registry/parameter-tree", "POST", result)


@router.post("/run")
async def operation_run(request: OperationRunRequest) -> Dict[str, Any]:
    operation = "api.runtime.calibration_registry.run"
    ingress = _ingress(operation, {"method": "POST", "operation_id": request.operation_id, "resume": request.resume})
    tick, receipt_hash72 = _authorized_receipt(operation)
    try:
        result = await asyncio.to_thread(
            PASS198_OPERATION_CALIBRATION_REGISTRY.run_operation,
            request.operation_id,
            request.config,
            resume=request.resume,
            vm81_receipt_hash72=receipt_hash72,
        )
    except (Pass198RegistryError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail={"schema": "HHS_PASS_198_RUN_FAILURE_V1", "reason": str(exc)}) from exc
    result["vm81_authorized_tick"] = _tick_projection(operation, tick, receipt_hash72)
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"run_id": result.get("run_id"), "status": result.get("status"), "report_hash72": result.get("report_hash72")})}
    return _contract_response("/api/runtime/calibration-registry/run", "POST", result)


@router.get("/runs")
def run_list(operation_id: str | None = None) -> Dict[str, Any]:
    operation = "api.runtime.calibration_registry.runs.list"
    ingress = _ingress(operation, {"method": "GET", "operation_id": operation_id})
    items = PASS198_OPERATION_CALIBRATION_REGISTRY.list_runs(operation_id)
    result = {"schema": "HHS_PASS_198_RUN_LIST_V1", "runs": items, "count": len(items)}
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"count": len(items)})}
    return _contract_response("/api/runtime/calibration-registry/runs", "GET", result)


@router.get("/simplifications")
def simplification_list(operation_id: str | None = None) -> Dict[str, Any]:
    operation = "api.runtime.calibration_registry.simplifications.list"
    ingress = _ingress(operation, {"method": "GET", "operation_id": operation_id})
    items = PASS198_OPERATION_CALIBRATION_REGISTRY.list_simplifications(operation_id)
    result = {"schema": "HHS_PASS_198_SIMPLIFICATION_LIST_V1", "simplifications": items, "count": len(items)}
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"count": len(items)})}
    return _contract_response("/api/runtime/calibration-registry/simplifications", "GET", result)


@router.post("/simplifications/promote")
def simplification_promote(request: SimplificationPromoteRequest) -> Dict[str, Any]:
    operation = "api.runtime.calibration_registry.simplifications.promote"
    ingress = _ingress(operation, {"method": "POST", "simplification_id": request.simplification_id, "target_status": request.target_status})
    tick, receipt_hash72 = _authorized_receipt(operation)
    try:
        result = PASS198_OPERATION_CALIBRATION_REGISTRY.promote_simplification(
            request.simplification_id,
            request.target_status,
            evidence_run_ids=request.evidence_run_ids,
            vm81_receipt_hash72=receipt_hash72,
        )
    except (Pass198RegistryError, ValueError, IndexError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["vm81_authorized_tick"] = _tick_projection(operation, tick, receipt_hash72)
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"simplification_id": request.simplification_id, "status": result.get("status")})}
    return _contract_response("/api/runtime/calibration-registry/simplifications/promote", "POST", result)


@router.post("/simplifications/revoke")
def simplification_revoke(request: SimplificationRevokeRequest) -> Dict[str, Any]:
    operation = "api.runtime.calibration_registry.simplifications.revoke"
    ingress = _ingress(operation, {"method": "POST", "simplification_id": request.simplification_id})
    tick, receipt_hash72 = _authorized_receipt(operation)
    try:
        result = PASS198_OPERATION_CALIBRATION_REGISTRY.revoke_simplification(
            request.simplification_id,
            request.reason,
            vm81_receipt_hash72=receipt_hash72,
        )
    except Pass198RegistryError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["vm81_authorized_tick"] = _tick_projection(operation, tick, receipt_hash72)
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"simplification_id": request.simplification_id, "status": result.get("status")})}
    return _contract_response("/api/runtime/calibration-registry/simplifications/revoke", "POST", result)


@router.get("/tools")
def registry_tools() -> Dict[str, Any]:
    operation = "api.runtime.calibration_registry.tools"
    ingress = _ingress(operation, {"method": "GET"})
    tools = [
        {"name": "calibration_registry.status", "method": "GET", "path": "/api/runtime/calibration-registry/status", "mutation": False},
        {"name": "calibration_registry.operations", "method": "GET", "path": "/api/runtime/calibration-registry/operations", "mutation": False},
        {"name": "calibration_registry.parameter_tree", "method": "POST", "path": "/api/runtime/calibration-registry/parameter-tree", "mutation": False},
        {"name": "calibration_registry.run", "method": "POST", "path": "/api/runtime/calibration-registry/run", "mutation": True},
        {"name": "calibration_registry.simplifications", "method": "GET", "path": "/api/runtime/calibration-registry/simplifications", "mutation": False},
        {"name": "calibration_registry.promote", "method": "POST", "path": "/api/runtime/calibration-registry/simplifications/promote", "mutation": True},
        {"name": "calibration_registry.revoke", "method": "POST", "path": "/api/runtime/calibration-registry/simplifications/revoke", "mutation": True},
    ]
    result = {"schema": "HHS_PASS_198_TOOL_REGISTRY_V1", "tools": tools, "mutation_requires_vm81_authorized_tick": True, "tool_server_is_authority": False}
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"tool_count": len(tools)})}
    return _contract_response("/api/runtime/calibration-registry/tools", "GET", result)


@router.post("/tools/invoke")
async def registry_tool_invoke(request: RegistryToolInvokeRequest) -> Dict[str, Any]:
    operation = "api.runtime.calibration_registry.tools.invoke"
    ingress = _ingress(operation, {"method": "POST", "tool": request.tool})
    try:
        if request.tool == "calibration_registry.status":
            result = PASS198_OPERATION_CALIBRATION_REGISTRY.status()
        elif request.tool == "calibration_registry.operations":
            result = {"operations": PASS198_OPERATION_CALIBRATION_REGISTRY.list_operations()}
        elif request.tool == "calibration_registry.parameter_tree":
            result = PASS198_OPERATION_CALIBRATION_REGISTRY.parameter_tree(
                str(request.arguments["operation_id"]), request.arguments.get("overrides") or {}
            )
        elif request.tool == "calibration_registry.simplifications":
            result = {"simplifications": PASS198_OPERATION_CALIBRATION_REGISTRY.list_simplifications(request.arguments.get("operation_id"))}
        elif request.tool == "calibration_registry.run":
            tick, receipt_hash72 = _authorized_receipt(operation)
            result = await asyncio.to_thread(
                PASS198_OPERATION_CALIBRATION_REGISTRY.run_operation,
                str(request.arguments["operation_id"]),
                request.arguments.get("config") or {},
                resume=bool(request.arguments.get("resume", True)),
                vm81_receipt_hash72=receipt_hash72,
            )
            result["vm81_authorized_tick"] = _tick_projection(operation, tick, receipt_hash72)
        elif request.tool == "calibration_registry.promote":
            tick, receipt_hash72 = _authorized_receipt(operation)
            result = PASS198_OPERATION_CALIBRATION_REGISTRY.promote_simplification(
                str(request.arguments["simplification_id"]),
                str(request.arguments["target_status"]),
                evidence_run_ids=list(request.arguments["evidence_run_ids"]),
                vm81_receipt_hash72=receipt_hash72,
            )
            result["vm81_authorized_tick"] = _tick_projection(operation, tick, receipt_hash72)
        elif request.tool == "calibration_registry.revoke":
            tick, receipt_hash72 = _authorized_receipt(operation)
            result = PASS198_OPERATION_CALIBRATION_REGISTRY.revoke_simplification(
                str(request.arguments["simplification_id"]),
                dict(request.arguments["reason"]),
                vm81_receipt_hash72=receipt_hash72,
            )
            result["vm81_authorized_tick"] = _tick_projection(operation, tick, receipt_hash72)
        else:
            raise Pass198RegistryError(f"unknown calibration-registry tool: {request.tool}")
    except (KeyError, TypeError, ValueError, Pass198RegistryError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["tool_invocation"] = {"schema": "HHS_PASS_198_TOOL_INVOCATION_V1", "tool": request.tool, "tool_server_is_authority": False}
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"tool": request.tool, "ok": result.get("ok", True)})}
    return _contract_response("/api/runtime/calibration-registry/tools/invoke", "POST", result)

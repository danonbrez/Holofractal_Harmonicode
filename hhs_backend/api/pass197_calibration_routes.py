"""Pass 197 exact A/B hydration-calibration API routes."""
from __future__ import annotations

import asyncio
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_backend.api.runtime_routes import _contract_response, io_gateway, runtime_controller
from hhs_backend.runtime.hhs_pass197_ab_hydration_calibration_v1 import (
    PASS197_AB_HYDRATION_CALIBRATION,
    Pass197CalibrationError,
)

router = APIRouter(
    prefix="/api/runtime/calibration",
    tags=["runtime", "vm81", "hash72", "hydration", "calibration", "ab-test", "pass197"],
)


class ABHydrationCalibrationRequest(BaseModel):
    x_values: List[Any] | None = None
    y_values: List[Any] | None = None
    xy_symbol_values: List[int] | None = None
    include_domain_rejections: bool = True
    full_replay: bool = True
    resume: bool = True


class CalibrationToolInvokeRequest(BaseModel):
    tool: str = Field(min_length=1, max_length=128)
    arguments: Dict[str, Any] = Field(default_factory=dict)


def _ingress(operation: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return io_gateway.ingress(operation, payload)


def _egress(operation: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return io_gateway.egress(operation, payload)


def _receipt_hash72(authorized_tick: Dict[str, Any]) -> str | None:
    receipt = authorized_tick.get("receipt") if isinstance(authorized_tick, dict) else None
    value = receipt.get("receipt_hash72") if isinstance(receipt, dict) else None
    return value if isinstance(value, str) and value else None


def _request_payload(request: ABHydrationCalibrationRequest) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "include_domain_rejections": request.include_domain_rejections,
        "full_replay": request.full_replay,
    }
    if request.x_values is not None:
        payload["x_values"] = request.x_values
    if request.y_values is not None:
        payload["y_values"] = request.y_values
    if request.xy_symbol_values is not None:
        payload["xy_symbol_values"] = request.xy_symbol_values
    return payload


async def _run_calibration(request: ABHydrationCalibrationRequest, *, source: str) -> Dict[str, Any]:
    authorized_tick = runtime_controller.authorized_tick(source=source)
    receipt_hash72 = _receipt_hash72(authorized_tick)
    result = await asyncio.to_thread(
        PASS197_AB_HYDRATION_CALIBRATION.run,
        _request_payload(request),
        resume=request.resume,
        vm81_receipt_hash72=receipt_hash72,
    )
    result["vm81_authorized_tick"] = {
        "source": source,
        "receipt_hash72": receipt_hash72,
        "runtime_step": authorized_tick.get("runtime", {}).get("step") if isinstance(authorized_tick, dict) else None,
        "api_or_worker_grants_authority": False,
    }
    return result


@router.get("/status")
def calibration_status() -> Dict[str, Any]:
    operation = "api.runtime.calibration.status"
    ingress = _ingress(operation, {"method": "GET"})
    result = PASS197_AB_HYDRATION_CALIBRATION.status()
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(operation, {"closed": result.get("closed"), "report_hash72": result.get("report_hash72")}),
    }
    return _contract_response("/api/runtime/calibration/status", "GET", result)


@router.post("/run")
async def calibration_run(request: ABHydrationCalibrationRequest) -> Dict[str, Any]:
    operation = "api.runtime.calibration.run"
    ingress = _ingress(operation, {"method": "POST", "resume": request.resume, "full_replay": request.full_replay})
    try:
        result = await _run_calibration(request, source=operation)
    except (Pass197CalibrationError, OSError, ValueError, RuntimeError, ZeroDivisionError) as exc:
        raise HTTPException(
            status_code=409,
            detail={"schema": "HHS_PASS_197_CALIBRATION_FAILURE_V1", "ok": False, "reason": str(exc)},
        ) from exc
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(
            operation,
            {
                "closed": result.get("closed"),
                "report_hash72": result.get("report_hash72"),
                "evaluated_parameter_states": result.get("summary", {}).get("evaluated_parameter_states"),
                "address_comparisons": result.get("summary", {}).get("address_comparisons"),
            },
        ),
    }
    return _contract_response("/api/runtime/calibration/run", "POST", result)


@router.get("/report")
def calibration_report() -> Dict[str, Any]:
    operation = "api.runtime.calibration.report"
    ingress = _ingress(operation, {"method": "GET"})
    try:
        result = PASS197_AB_HYDRATION_CALIBRATION.report()
    except Pass197CalibrationError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(operation, {"report_hash72": result.get("report_hash72"), "closed": result.get("closed")}),
    }
    return _contract_response("/api/runtime/calibration/report", "GET", result)


@router.get("/tools")
def calibration_tools() -> Dict[str, Any]:
    operation = "api.runtime.calibration.tools"
    ingress = _ingress(operation, {"method": "GET"})
    result = {
        "schema": "HHS_PASS_197_CALIBRATION_TOOL_REGISTRY_V1",
        "tools": [
            {"name": "calibration.status", "method": "GET", "path": "/api/runtime/calibration/status", "mutation": False},
            {"name": "calibration.run", "method": "POST", "path": "/api/runtime/calibration/run", "mutation": True},
            {"name": "calibration.report", "method": "GET", "path": "/api/runtime/calibration/report", "mutation": False},
        ],
        "mutation_requires_vm81_authorized_tick": True,
        "tool_server_is_authority": False,
    }
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"tool_count": len(result["tools"])})}
    return _contract_response("/api/runtime/calibration/tools", "GET", result)


@router.post("/tools/invoke")
async def calibration_tool_invoke(request: CalibrationToolInvokeRequest) -> Dict[str, Any]:
    operation = "api.runtime.calibration.tools.invoke"
    ingress = _ingress(operation, {"method": "POST", "tool": request.tool})
    try:
        if request.tool == "calibration.status":
            result = PASS197_AB_HYDRATION_CALIBRATION.status()
        elif request.tool == "calibration.report":
            result = PASS197_AB_HYDRATION_CALIBRATION.report()
        elif request.tool == "calibration.run":
            run_request = ABHydrationCalibrationRequest(**request.arguments)
            result = await _run_calibration(run_request, source=operation)
        else:
            raise Pass197CalibrationError(f"unknown calibration tool: {request.tool}")
    except (Pass197CalibrationError, ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["tool_invocation"] = {
        "schema": "HHS_PASS_197_CALIBRATION_TOOL_INVOCATION_V1",
        "tool": request.tool,
        "tool_server_is_authority": False,
    }
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(operation, {"tool": request.tool, "closed": result.get("closed"), "report_hash72": result.get("report_hash72")}),
    }
    return _contract_response("/api/runtime/calibration/tools/invoke", "POST", result)

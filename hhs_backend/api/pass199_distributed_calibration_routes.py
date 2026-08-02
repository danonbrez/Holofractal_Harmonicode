"""Pass 199 durable distributed calibration API and tool projection."""
from __future__ import annotations

import asyncio
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_backend.api.runtime_routes import _contract_response, io_gateway, runtime_controller
from hhs_backend.runtime.hhs_pass199_distributed_calibration_fabric_v1 import Pass199CalibrationError
from hhs_backend.runtime.hhs_pass199_distributed_calibration_runtime_v1 import (
    PASS199_DISTRIBUTED_CALIBRATION_RUNTIME,
)

router = APIRouter(
    prefix="/api/runtime/distributed-calibration",
    tags=["runtime", "pass190", "pass198", "pass199", "vm81", "hash72", "durable-worker", "calibration"],
)

PASS199_DISTRIBUTED_CALIBRATION_FABRIC = PASS199_DISTRIBUTED_CALIBRATION_RUNTIME


class DistributedCalibrationRunRequest(BaseModel):
    operation_id: str = Field(default="pass197.reciprocal_matrix_gate", min_length=1, max_length=256)
    config: Dict[str, Any] = Field(default_factory=dict)
    worker_count: int = Field(default=4, ge=1, le=64)
    resume: bool = True
    full_replay: bool = True


class DistributedCalibrationPrepareRequest(BaseModel):
    operation_id: str = Field(default="pass197.reciprocal_matrix_gate", min_length=1, max_length=256)
    config: Dict[str, Any] = Field(default_factory=dict)


class DistributedCalibrationToolInvokeRequest(BaseModel):
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
        "candidate_workers_are_authority": False,
        "api_is_authority": False,
    }


@router.get("/status")
def distributed_calibration_status() -> Dict[str, Any]:
    operation = "api.runtime.distributed_calibration.status"
    ingress = _ingress(operation, {"method": "GET"})
    result = PASS199_DISTRIBUTED_CALIBRATION_FABRIC.status()
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(operation, {"closed": result.get("closed"), "report_hash72": result.get("report_hash72")}),
    }
    return _contract_response("/api/runtime/distributed-calibration/status", "GET", result)


@router.post("/prepare")
def distributed_calibration_prepare(request: DistributedCalibrationPrepareRequest) -> Dict[str, Any]:
    operation = "api.runtime.distributed_calibration.prepare"
    ingress = _ingress(operation, {"method": "POST", "operation_id": request.operation_id})
    try:
        result = PASS199_DISTRIBUTED_CALIBRATION_FABRIC.prepare_tree(request.operation_id, request.config)
    except (Pass199CalibrationError, ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    projection = {
        "schema": result["schema"],
        "run_id": result["run_id"],
        "workspace_id": result["workspace_id"],
        "tree_hash72": result["tree"]["tree_hash72"],
        "state_count": result["tree"]["state_count"],
        "expected_job_count": result["expected_job_count"],
        "submitted_job_count": result["submitted_job_count"],
        "candidate_workers_are_authority": False,
    }
    projection["io"] = {
        "ingress": ingress,
        "egress": _egress(operation, {"run_id": projection["run_id"], "expected_job_count": projection["expected_job_count"]}),
    }
    return _contract_response("/api/runtime/distributed-calibration/prepare", "POST", projection)


@router.post("/run")
async def distributed_calibration_run(request: DistributedCalibrationRunRequest) -> Dict[str, Any]:
    operation = "api.runtime.distributed_calibration.run"
    ingress = _ingress(
        operation,
        {"method": "POST", "operation_id": request.operation_id, "worker_count": request.worker_count, "resume": request.resume},
    )
    tick, receipt_hash72 = _authorized_receipt(operation)
    try:
        result = await asyncio.to_thread(
            PASS199_DISTRIBUTED_CALIBRATION_FABRIC.run,
            request.operation_id,
            request.config,
            worker_count=request.worker_count,
            vm81_receipt_hash72=receipt_hash72,
            resume=request.resume,
            full_replay=request.full_replay,
        )
    except (Pass199CalibrationError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(
            status_code=409,
            detail={"schema": "HHS_PASS_199_DISTRIBUTED_RUN_FAILURE_V1", "reason": str(exc)},
        ) from exc
    result["vm81_authorized_tick"] = _tick_projection(operation, tick, receipt_hash72)
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(
            operation,
            {
                "run_id": result.get("run_id"),
                "closed": result.get("closed"),
                "report_hash72": result.get("report_hash72"),
                "branch_job_count": result.get("summary", {}).get("branch_job_count"),
                "canonical_commit_operation_count": result.get("singleton_commit", {}).get("canonical_commit_operation_count"),
            },
        ),
    }
    return _contract_response("/api/runtime/distributed-calibration/run", "POST", result)


@router.get("/report")
def distributed_calibration_report() -> Dict[str, Any]:
    operation = "api.runtime.distributed_calibration.report"
    ingress = _ingress(operation, {"method": "GET"})
    try:
        result = PASS199_DISTRIBUTED_CALIBRATION_FABRIC.report()
    except Pass199CalibrationError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(operation, {"run_id": result.get("run_id"), "closed": result.get("closed"), "report_hash72": result.get("report_hash72")}),
    }
    return _contract_response("/api/runtime/distributed-calibration/report", "GET", result)


@router.get("/tools")
def distributed_calibration_tools() -> Dict[str, Any]:
    operation = "api.runtime.distributed_calibration.tools"
    ingress = _ingress(operation, {"method": "GET"})
    tools = [
        {"name": "distributed_calibration.status", "method": "GET", "path": "/api/runtime/distributed-calibration/status", "mutation": False},
        {"name": "distributed_calibration.prepare", "method": "POST", "path": "/api/runtime/distributed-calibration/prepare", "mutation": True},
        {"name": "distributed_calibration.run", "method": "POST", "path": "/api/runtime/distributed-calibration/run", "mutation": True},
        {"name": "distributed_calibration.report", "method": "GET", "path": "/api/runtime/distributed-calibration/report", "mutation": False},
    ]
    result = {
        "schema": "HHS_PASS_199_TOOL_REGISTRY_V1",
        "tools": tools,
        "mutation_requires_vm81_authorized_tick": True,
        "candidate_workers_are_authority": False,
        "tool_server_is_authority": False,
    }
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"tool_count": len(tools)})}
    return _contract_response("/api/runtime/distributed-calibration/tools", "GET", result)


@router.post("/tools/invoke")
async def distributed_calibration_tool_invoke(request: DistributedCalibrationToolInvokeRequest) -> Dict[str, Any]:
    operation = "api.runtime.distributed_calibration.tools.invoke"
    ingress = _ingress(operation, {"method": "POST", "tool": request.tool})
    try:
        if request.tool == "distributed_calibration.status":
            result = PASS199_DISTRIBUTED_CALIBRATION_FABRIC.status()
        elif request.tool == "distributed_calibration.prepare":
            prepared = PASS199_DISTRIBUTED_CALIBRATION_FABRIC.prepare_tree(
                str(request.arguments.get("operation_id", "pass197.reciprocal_matrix_gate")),
                dict(request.arguments.get("config") or {}),
            )
            result = {
                "run_id": prepared["run_id"],
                "workspace_id": prepared["workspace_id"],
                "tree_hash72": prepared["tree"]["tree_hash72"],
                "state_count": prepared["tree"]["state_count"],
                "expected_job_count": prepared["expected_job_count"],
            }
        elif request.tool == "distributed_calibration.run":
            tick, receipt_hash72 = _authorized_receipt(operation)
            result = await asyncio.to_thread(
                PASS199_DISTRIBUTED_CALIBRATION_FABRIC.run,
                str(request.arguments.get("operation_id", "pass197.reciprocal_matrix_gate")),
                dict(request.arguments.get("config") or {}),
                worker_count=int(request.arguments.get("worker_count", 4)),
                vm81_receipt_hash72=receipt_hash72,
                resume=bool(request.arguments.get("resume", True)),
                full_replay=bool(request.arguments.get("full_replay", True)),
            )
            result["vm81_authorized_tick"] = _tick_projection(operation, tick, receipt_hash72)
        elif request.tool == "distributed_calibration.report":
            result = PASS199_DISTRIBUTED_CALIBRATION_FABRIC.report()
        else:
            raise Pass199CalibrationError(f"unknown distributed-calibration tool: {request.tool}")
    except (KeyError, TypeError, ValueError, RuntimeError, Pass199CalibrationError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["tool_invocation"] = {
        "schema": "HHS_PASS_199_TOOL_INVOCATION_V1",
        "tool": request.tool,
        "tool_server_is_authority": False,
        "candidate_workers_are_authority": False,
    }
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"tool": request.tool, "ok": result.get("closed", True)})}
    return _contract_response("/api/runtime/distributed-calibration/tools/invoke", "POST", result)

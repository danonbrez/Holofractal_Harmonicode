"""Pass 200A governed holdout, bundle, and compiler-shadow API."""
from __future__ import annotations

import asyncio
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_backend.api.runtime_routes import _contract_response, io_gateway, runtime_controller
from hhs_backend.runtime.hhs_pass200a_proof_carrying_optimization_v1 import (
    DEFAULT_SHADOW_CONFIG,
    PASS200A_OPTIMIZATION_AUTHORITY,
    Pass200AError,
)

router = APIRouter(
    prefix="/api/runtime/optimization-authority",
    tags=["runtime", "pass198", "pass199", "pass200a", "compiler", "shadow", "optimization"],
)


class HoldoutRunRequest(BaseModel):
    worker_count: int = Field(default=8, ge=1, le=64)


class ShadowCompileRequest(BaseModel):
    bundle_id: str = Field(min_length=1, max_length=256)
    invocation: Dict[str, Any] = Field(default_factory=dict)


class ShadowRunRequest(BaseModel):
    worker_count: int = Field(default=8, ge=1, le=64)
    config: Dict[str, Any] = Field(default_factory=lambda: dict(DEFAULT_SHADOW_CONFIG))


class OptimizationToolInvokeRequest(BaseModel):
    tool: str = Field(min_length=1, max_length=128)
    arguments: Dict[str, Any] = Field(default_factory=dict)


def _ingress(operation: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return io_gateway.ingress(operation, payload)


def _egress(operation: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return io_gateway.egress(operation, payload)


def _authorized_receipt(source: str) -> tuple[Dict[str, Any], str]:
    tick = runtime_controller.authorized_tick(source=source)
    receipt = tick.get("receipt") if isinstance(tick, dict) else None
    value = receipt.get("receipt_hash72") if isinstance(receipt, dict) else None
    if not isinstance(value, str) or len(value) != 72:
        raise HTTPException(status_code=503, detail="VM81 authorized tick did not produce a Hash72 receipt")
    return tick, value


def _tick_projection(source: str, tick: Dict[str, Any], receipt_hash72: str) -> Dict[str, Any]:
    return {
        "source": source,
        "receipt_hash72": receipt_hash72,
        "runtime_step": tick.get("runtime", {}).get("step") if isinstance(tick, dict) else None,
        "api_is_authority": False,
        "compiler_shadow_is_authority": False,
        "candidate_execution_is_authority": False,
    }


@router.get("/status")
def optimization_status() -> Dict[str, Any]:
    operation = "api.runtime.optimization_authority.status"
    ingress = _ingress(operation, {"method": "GET"})
    try:
        result = PASS200A_OPTIMIZATION_AUTHORITY.status()
    except (Pass200AError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(operation, {"closed": result.get("closed"), "status_hash72": result.get("status_hash72")}),
    }
    return _contract_response("/api/runtime/optimization-authority/status", "GET", result)


@router.post("/holdouts/run")
async def optimization_holdouts_run(request: HoldoutRunRequest) -> Dict[str, Any]:
    operation = "api.runtime.optimization_authority.holdouts.run"
    ingress = _ingress(operation, {"method": "POST", "worker_count": request.worker_count})
    tick, receipt_hash72 = _authorized_receipt(operation)
    try:
        result = await asyncio.to_thread(
            PASS200A_OPTIMIZATION_AUTHORITY.run_holdouts,
            worker_count=request.worker_count,
            vm81_receipt_hash72=receipt_hash72,
        )
    except (Pass200AError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(
            status_code=409,
            detail={"schema": "HHS_PASS_200A_HOLDOUT_FAILURE_V1", "reason": str(exc)},
        ) from exc
    result["vm81_authorized_tick"] = _tick_projection(operation, tick, receipt_hash72)
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(
            operation,
            {
                "closed": result.get("closed"),
                "independent_envelope_count": result.get("independent_envelope_count"),
                "bundle_count": result.get("bundle_count"),
                "qualification_hash72": result.get("qualification_hash72"),
            },
        ),
    }
    return _contract_response("/api/runtime/optimization-authority/holdouts/run", "POST", result)


@router.get("/envelopes")
def optimization_envelopes() -> Dict[str, Any]:
    operation = "api.runtime.optimization_authority.envelopes"
    ingress = _ingress(operation, {"method": "GET"})
    try:
        envelopes = PASS200A_OPTIMIZATION_AUTHORITY.list_envelopes()
    except (Pass200AError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result = {
        "schema": "HHS_PASS_200A_ENVELOPE_LIST_V1",
        "count": len(envelopes),
        "envelopes": envelopes,
        "receipt_only_variation_counts": False,
    }
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"count": len(envelopes)})}
    return _contract_response("/api/runtime/optimization-authority/envelopes", "GET", result)


@router.get("/bundles")
def optimization_bundles() -> Dict[str, Any]:
    operation = "api.runtime.optimization_authority.bundles"
    ingress = _ingress(operation, {"method": "GET"})
    try:
        bundles = PASS200A_OPTIMIZATION_AUTHORITY.list_bundles()
    except (Pass200AError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result = {
        "schema": "HHS_PASS_200A_BUNDLE_LIST_V1",
        "count": len(bundles),
        "bundles": bundles,
        "compiler_auto_activation": False,
        "runtime_auto_admission": False,
    }
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"count": len(bundles)})}
    return _contract_response("/api/runtime/optimization-authority/bundles", "GET", result)


@router.post("/compiler/shadow/compile")
def optimization_shadow_compile(request: ShadowCompileRequest) -> Dict[str, Any]:
    operation = "api.runtime.optimization_authority.compiler.shadow.compile"
    ingress = _ingress(operation, {"method": "POST", "bundle_id": request.bundle_id})
    try:
        result = PASS200A_OPTIMIZATION_AUTHORITY.compile_shadow_plan(
            request.bundle_id,
            request.invocation,
        )
    except (Pass200AError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(operation, {"program_hash72": result.get("program_hash72"), "mode": "SHADOW"}),
    }
    return _contract_response("/api/runtime/optimization-authority/compiler/shadow/compile", "POST", result)


@router.post("/compiler/shadow/run")
async def optimization_shadow_run(request: ShadowRunRequest) -> Dict[str, Any]:
    operation = "api.runtime.optimization_authority.compiler.shadow.run"
    ingress = _ingress(operation, {"method": "POST", "worker_count": request.worker_count})
    tick, receipt_hash72 = _authorized_receipt(operation)
    try:
        result = await asyncio.to_thread(
            PASS200A_OPTIMIZATION_AUTHORITY.execute_all_shadows,
            worker_count=request.worker_count,
            vm81_receipt_hash72=receipt_hash72,
            config_payload=request.config,
        )
    except (Pass200AError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(
            status_code=409,
            detail={"schema": "HHS_PASS_200A_SHADOW_FAILURE_V1", "reason": str(exc)},
        ) from exc
    result["vm81_authorized_tick"] = _tick_projection(operation, tick, receipt_hash72)
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(
            operation,
            {
                "closed": result.get("closed"),
                "shadow_match_count": result.get("shadow_match_count"),
                "reference_return_count": result.get("reference_return_count"),
                "candidate_activation_count": result.get("candidate_activation_count"),
                "shadow_suite_hash72": result.get("shadow_suite_hash72"),
            },
        ),
    }
    return _contract_response("/api/runtime/optimization-authority/compiler/shadow/run", "POST", result)


@router.get("/compiler/shadow/runs")
def optimization_shadow_runs() -> Dict[str, Any]:
    operation = "api.runtime.optimization_authority.compiler.shadow.runs"
    ingress = _ingress(operation, {"method": "GET"})
    try:
        records = PASS200A_OPTIMIZATION_AUTHORITY.list_shadow_runs()
    except (Pass200AError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result = {
        "schema": "HHS_PASS_200A_SHADOW_RUN_LIST_V1",
        "count": len(records),
        "records": records,
        "reference_result_remains_authoritative": True,
        "candidate_activation_count": sum(bool(item.get("candidate_activated")) for item in records),
    }
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"count": len(records)})}
    return _contract_response("/api/runtime/optimization-authority/compiler/shadow/runs", "GET", result)


@router.get("/verify")
def optimization_verify() -> Dict[str, Any]:
    operation = "api.runtime.optimization_authority.verify"
    ingress = _ingress(operation, {"method": "GET"})
    try:
        result = PASS200A_OPTIMIZATION_AUTHORITY.verify()
    except (Pass200AError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"ok": result.get("ok")})}
    return _contract_response("/api/runtime/optimization-authority/verify", "GET", result)


@router.get("/tools")
def optimization_tools() -> Dict[str, Any]:
    operation = "api.runtime.optimization_authority.tools"
    ingress = _ingress(operation, {"method": "GET"})
    tools = [
        {"name": "optimization.status", "method": "GET", "path": "/api/runtime/optimization-authority/status", "mutation": False},
        {"name": "optimization.run_holdouts", "method": "POST", "path": "/api/runtime/optimization-authority/holdouts/run", "mutation": True},
        {"name": "optimization.list_envelopes", "method": "GET", "path": "/api/runtime/optimization-authority/envelopes", "mutation": False},
        {"name": "optimization.list_bundles", "method": "GET", "path": "/api/runtime/optimization-authority/bundles", "mutation": False},
        {"name": "optimization.compile_shadow", "method": "POST", "path": "/api/runtime/optimization-authority/compiler/shadow/compile", "mutation": False},
        {"name": "optimization.run_shadows", "method": "POST", "path": "/api/runtime/optimization-authority/compiler/shadow/run", "mutation": True},
        {"name": "optimization.verify", "method": "GET", "path": "/api/runtime/optimization-authority/verify", "mutation": False},
    ]
    result = {
        "schema": "HHS_PASS_200A_TOOL_REGISTRY_V1",
        "tools": tools,
        "mutation_requires_vm81_authorized_tick": True,
        "tool_server_is_authority": False,
        "compiler_auto_activation": False,
        "runtime_auto_admission": False,
    }
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"tool_count": len(tools)})}
    return _contract_response("/api/runtime/optimization-authority/tools", "GET", result)


@router.post("/tools/invoke")
async def optimization_tool_invoke(request: OptimizationToolInvokeRequest) -> Dict[str, Any]:
    operation = "api.runtime.optimization_authority.tools.invoke"
    ingress = _ingress(operation, {"method": "POST", "tool": request.tool})
    try:
        if request.tool == "optimization.status":
            result = PASS200A_OPTIMIZATION_AUTHORITY.status()
        elif request.tool == "optimization.run_holdouts":
            tick, receipt_hash72 = _authorized_receipt(operation)
            result = await asyncio.to_thread(
                PASS200A_OPTIMIZATION_AUTHORITY.run_holdouts,
                worker_count=int(request.arguments.get("worker_count", 8)),
                vm81_receipt_hash72=receipt_hash72,
            )
            result["vm81_authorized_tick"] = _tick_projection(operation, tick, receipt_hash72)
        elif request.tool == "optimization.list_envelopes":
            records = PASS200A_OPTIMIZATION_AUTHORITY.list_envelopes()
            result = {"count": len(records), "envelopes": records}
        elif request.tool == "optimization.list_bundles":
            records = PASS200A_OPTIMIZATION_AUTHORITY.list_bundles()
            result = {"count": len(records), "bundles": records}
        elif request.tool == "optimization.compile_shadow":
            result = PASS200A_OPTIMIZATION_AUTHORITY.compile_shadow_plan(
                str(request.arguments["bundle_id"]),
                dict(request.arguments.get("invocation") or {}),
            )
        elif request.tool == "optimization.run_shadows":
            tick, receipt_hash72 = _authorized_receipt(operation)
            result = await asyncio.to_thread(
                PASS200A_OPTIMIZATION_AUTHORITY.execute_all_shadows,
                worker_count=int(request.arguments.get("worker_count", 8)),
                vm81_receipt_hash72=receipt_hash72,
                config_payload=dict(request.arguments.get("config") or DEFAULT_SHADOW_CONFIG),
            )
            result["vm81_authorized_tick"] = _tick_projection(operation, tick, receipt_hash72)
        elif request.tool == "optimization.verify":
            result = PASS200A_OPTIMIZATION_AUTHORITY.verify()
        else:
            raise Pass200AError(f"unknown optimization tool: {request.tool}")
    except (KeyError, TypeError, ValueError, RuntimeError, Pass200AError, OSError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["tool_invocation"] = {
        "schema": "HHS_PASS_200A_TOOL_INVOCATION_V1",
        "tool": request.tool,
        "tool_server_is_authority": False,
        "candidate_execution_is_authority": False,
    }
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"tool": request.tool, "ok": result.get("closed", result.get("ok", True))})}
    return _contract_response("/api/runtime/optimization-authority/tools/invoke", "POST", result)

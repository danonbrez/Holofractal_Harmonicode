"""Pass 200B governed canary admission, probe, rollback, and audit API."""
from __future__ import annotations

import time
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_backend.api.runtime_routes import _contract_response, io_gateway, runtime_controller
from hhs_backend.runtime.hhs_pass200b_governed_canary_admission import (
    MAX_INVOCATION_LIMIT,
    PASS200B_CANARY_AUTHORITY,
    Pass200BError,
)

router = APIRouter(
    prefix="/api/runtime/optimization-canary",
    tags=["runtime", "pass200a", "pass200b", "compiler", "canary", "rollback"],
)


class CanaryAdmissionRequest(BaseModel):
    bundle_id: str = Field(min_length=1, max_length=256)
    invocation_limit: int = Field(default=8, ge=1, le=MAX_INVOCATION_LIMIT)
    canary_numerator: int = Field(default=1, ge=1, le=64)
    canary_denominator: int = Field(default=4, ge=1, le=64)
    expires_in_seconds: int = Field(default=900, ge=30, le=3600)


class CanaryProbeRequest(BaseModel):
    frontier_id: str = Field(min_length=1, max_length=256)


class CanaryRollbackRequest(BaseModel):
    frontier_id: str = Field(min_length=1, max_length=256)
    reason: str = Field(default="EXPLICIT_OPERATOR_ROLLBACK", min_length=1, max_length=256)


class CanaryToolInvokeRequest(BaseModel):
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


def _tick_projection(role: str, source: str, tick: Dict[str, Any], receipt_hash72: str) -> Dict[str, Any]:
    return {
        "role": role,
        "source": source,
        "receipt_hash72": receipt_hash72,
        "runtime_step": tick.get("runtime", {}).get("step") if isinstance(tick, dict) else None,
        "api_is_authority": False,
        "candidate_self_authorization": False,
    }


def _admit(request: CanaryAdmissionRequest) -> Dict[str, Any]:
    if request.canary_numerator > request.canary_denominator:
        raise Pass200BError("canary numerator cannot exceed denominator")
    operation = "api.runtime.optimization_canary.admit"
    current = PASS200B_CANARY_AUTHORITY.current_frontier()
    bundle = PASS200B_CANARY_AUTHORITY.pass200a.get_bundle(request.bundle_id)
    now_ns = time.time_ns()
    expires_at_ns = now_ns + request.expires_in_seconds * 1_000_000_000
    compiler_source = f"{operation}.compiler_approval"
    runtime_source = f"{operation}.runtime_approval"
    activation_source = f"{operation}.singleton_activation"
    compiler_tick, compiler_receipt = _authorized_receipt(compiler_source)
    runtime_tick, runtime_receipt = _authorized_receipt(runtime_source)
    activation_tick, activation_receipt = _authorized_receipt(activation_source)
    approvals = [
        PASS200B_CANARY_AUTHORITY.build_approval(
            principal_id="vm81:compiler-promotion-authority",
            capability="COMPILER_PROMOTION_APPROVE",
            receipt_hash72=compiler_receipt,
            bundle_hash72=bundle["bundle_hash72"],
            expected_frontier_hash72=current["frontier_hash72"],
            expires_at_ns=expires_at_ns,
        ),
        PASS200B_CANARY_AUTHORITY.build_approval(
            principal_id="vm81:runtime-promotion-authority",
            capability="RUNTIME_PROMOTION_APPROVE",
            receipt_hash72=runtime_receipt,
            bundle_hash72=bundle["bundle_hash72"],
            expected_frontier_hash72=current["frontier_hash72"],
            expires_at_ns=expires_at_ns,
        ),
    ]
    result = PASS200B_CANARY_AUTHORITY.admit_canary(
        request.bundle_id,
        invocation_limit=request.invocation_limit,
        canary_numerator=request.canary_numerator,
        canary_denominator=request.canary_denominator,
        approvals=approvals,
        vm81_activation_receipt_hash72=activation_receipt,
        expires_at_ns=expires_at_ns,
        now_ns=now_ns,
    )
    result["vm81_authority"] = {
        "compiler_approval": _tick_projection("compiler_approval", compiler_source, compiler_tick, compiler_receipt),
        "runtime_approval": _tick_projection("runtime_approval", runtime_source, runtime_tick, runtime_receipt),
        "singleton_activation": _tick_projection("singleton_activation", activation_source, activation_tick, activation_receipt),
    }
    return result


@router.get("/status")
def canary_status() -> Dict[str, Any]:
    operation = "api.runtime.optimization_canary.status"
    ingress = _ingress(operation, {"method": "GET"})
    try:
        result = PASS200B_CANARY_AUTHORITY.status()
    except (Pass200BError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"closed": result.get("closed"), "current_mode": result.get("current_mode")})}
    return _contract_response("/api/runtime/optimization-canary/status", "GET", result)


@router.post("/admit")
def canary_admit(request: CanaryAdmissionRequest) -> Dict[str, Any]:
    operation = "api.runtime.optimization_canary.admit"
    ingress = _ingress(operation, request.model_dump())
    try:
        result = _admit(request)
    except (Pass200BError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail={"schema": "HHS_PASS_200B_ADMISSION_FAILURE_V1", "reason": str(exc)}) from exc
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"frontier_id": result.get("frontier_id"), "mode": result.get("mode")})}
    return _contract_response("/api/runtime/optimization-canary/admit", "POST", result)


@router.post("/probe")
def canary_probe(request: CanaryProbeRequest) -> Dict[str, Any]:
    operation = "api.runtime.optimization_canary.probe"
    ingress = _ingress(operation, request.model_dump())
    tick, receipt = _authorized_receipt(operation)
    try:
        result = PASS200B_CANARY_AUTHORITY.execute_verified_probe(
            request.frontier_id,
            invocation_receipt_hash72=receipt,
        )
    except (Pass200BError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail={"schema": "HHS_PASS_200B_PROBE_FAILURE_V1", "reason": str(exc)}) from exc
    result["vm81_authorized_tick"] = _tick_projection("canary_invocation", operation, tick, receipt)
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"status": result.get("status"), "returned_path": result.get("returned_path")})}
    return _contract_response("/api/runtime/optimization-canary/probe", "POST", result)


@router.post("/rollback")
def canary_rollback(request: CanaryRollbackRequest) -> Dict[str, Any]:
    operation = "api.runtime.optimization_canary.rollback"
    ingress = _ingress(operation, request.model_dump())
    tick, receipt = _authorized_receipt(operation)
    try:
        result = PASS200B_CANARY_AUTHORITY.rollback(
            request.frontier_id,
            reason=request.reason,
            vm81_rollback_receipt_hash72=receipt,
        )
    except (Pass200BError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail={"schema": "HHS_PASS_200B_ROLLBACK_FAILURE_V1", "reason": str(exc)}) from exc
    result["vm81_authorized_tick"] = _tick_projection("rollback", operation, tick, receipt)
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"frontier_id": result.get("frontier_id"), "mode": result.get("mode")})}
    return _contract_response("/api/runtime/optimization-canary/rollback", "POST", result)


@router.get("/frontiers")
def canary_frontiers() -> Dict[str, Any]:
    operation = "api.runtime.optimization_canary.frontiers"
    ingress = _ingress(operation, {"method": "GET"})
    try:
        records = PASS200B_CANARY_AUTHORITY.list_frontiers()
    except (Pass200BError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result = {"schema": "HHS_PASS_200B_FRONTIER_LIST_V1", "count": len(records), "frontiers": records}
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"count": len(records)})}
    return _contract_response("/api/runtime/optimization-canary/frontiers", "GET", result)


@router.get("/invocations")
def canary_invocations() -> Dict[str, Any]:
    operation = "api.runtime.optimization_canary.invocations"
    ingress = _ingress(operation, {"method": "GET"})
    try:
        records = PASS200B_CANARY_AUTHORITY.list_invocations()
    except (Pass200BError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result = {"schema": "HHS_PASS_200B_INVOCATION_LIST_V1", "count": len(records), "invocations": records}
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"count": len(records)})}
    return _contract_response("/api/runtime/optimization-canary/invocations", "GET", result)


@router.get("/verify")
def canary_verify() -> Dict[str, Any]:
    operation = "api.runtime.optimization_canary.verify"
    ingress = _ingress(operation, {"method": "GET"})
    try:
        result = PASS200B_CANARY_AUTHORITY.verify()
    except (Pass200BError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"ok": result.get("ok")})}
    return _contract_response("/api/runtime/optimization-canary/verify", "GET", result)


@router.get("/tools")
def canary_tools() -> Dict[str, Any]:
    operation = "api.runtime.optimization_canary.tools"
    ingress = _ingress(operation, {"method": "GET"})
    tools = [
        {"name": "canary.status", "method": "GET", "path": "/api/runtime/optimization-canary/status", "mutation": False},
        {"name": "canary.admit", "method": "POST", "path": "/api/runtime/optimization-canary/admit", "mutation": True},
        {"name": "canary.probe", "method": "POST", "path": "/api/runtime/optimization-canary/probe", "mutation": True},
        {"name": "canary.rollback", "method": "POST", "path": "/api/runtime/optimization-canary/rollback", "mutation": True},
        {"name": "canary.frontiers", "method": "GET", "path": "/api/runtime/optimization-canary/frontiers", "mutation": False},
        {"name": "canary.invocations", "method": "GET", "path": "/api/runtime/optimization-canary/invocations", "mutation": False},
        {"name": "canary.verify", "method": "GET", "path": "/api/runtime/optimization-canary/verify", "mutation": False},
    ]
    result = {
        "schema": "HHS_PASS_200B_TOOL_REGISTRY_V1",
        "tools": tools,
        "mutation_requires_vm81_authorized_tick": True,
        "dual_approval_required_for_admission": True,
        "candidate_self_authorization": False,
        "automatic_active_promotion": False,
        "automatic_frozen_constraint_promotion": False,
    }
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"tool_count": len(tools)})}
    return _contract_response("/api/runtime/optimization-canary/tools", "GET", result)


@router.post("/tools/invoke")
def canary_tool_invoke(request: CanaryToolInvokeRequest) -> Dict[str, Any]:
    operation = "api.runtime.optimization_canary.tools.invoke"
    ingress = _ingress(operation, {"tool": request.tool})
    try:
        if request.tool == "canary.status":
            result = PASS200B_CANARY_AUTHORITY.status()
        elif request.tool == "canary.admit":
            result = _admit(CanaryAdmissionRequest(**request.arguments))
        elif request.tool == "canary.probe":
            tick, receipt = _authorized_receipt(operation)
            result = PASS200B_CANARY_AUTHORITY.execute_verified_probe(
                str(request.arguments["frontier_id"]),
                invocation_receipt_hash72=receipt,
            )
            result["vm81_authorized_tick"] = _tick_projection("canary_invocation", operation, tick, receipt)
        elif request.tool == "canary.rollback":
            tick, receipt = _authorized_receipt(operation)
            result = PASS200B_CANARY_AUTHORITY.rollback(
                str(request.arguments["frontier_id"]),
                reason=str(request.arguments.get("reason") or "EXPLICIT_TOOL_ROLLBACK"),
                vm81_rollback_receipt_hash72=receipt,
            )
            result["vm81_authorized_tick"] = _tick_projection("rollback", operation, tick, receipt)
        elif request.tool == "canary.frontiers":
            records = PASS200B_CANARY_AUTHORITY.list_frontiers()
            result = {"count": len(records), "frontiers": records}
        elif request.tool == "canary.invocations":
            records = PASS200B_CANARY_AUTHORITY.list_invocations()
            result = {"count": len(records), "invocations": records}
        elif request.tool == "canary.verify":
            result = PASS200B_CANARY_AUTHORITY.verify()
        else:
            raise Pass200BError(f"unknown canary tool: {request.tool}")
    except (KeyError, TypeError, ValueError, RuntimeError, Pass200BError, OSError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["tool_invocation"] = {
        "schema": "HHS_PASS_200B_TOOL_INVOCATION_V1",
        "tool": request.tool,
        "tool_server_is_authority": False,
        "candidate_self_authorization": False,
    }
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"tool": request.tool, "ok": result.get("ok", True)})}
    return _contract_response("/api/runtime/optimization-canary/tools/invoke", "POST", result)

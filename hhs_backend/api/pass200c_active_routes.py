"""Pass 200C guarded active admission, probe, rollback, and audit API."""
from __future__ import annotations

import time
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_backend.api.runtime_routes import _contract_response, io_gateway, runtime_controller
from hhs_backend.runtime.hhs_pass200c_guarded_active_admission import (
    MAX_ACTIVE_LEASE_INVOCATIONS,
    PASS200C_ACTIVE_AUTHORITY,
    Pass200CError,
)

router = APIRouter(
    prefix="/api/runtime/optimization-active",
    tags=["runtime", "pass200a", "pass200b", "pass200c", "compiler", "active", "rollback"],
)


class ActiveAdmissionRequest(BaseModel):
    bundle_id: str = Field(min_length=1, max_length=256)
    lease_invocation_limit: int = Field(default=16, ge=1, le=MAX_ACTIVE_LEASE_INVOCATIONS)
    expires_in_seconds: int = Field(default=1800, ge=60, le=7200)


class ActiveProbeRequest(BaseModel):
    frontier_id: str = Field(min_length=1, max_length=256)


class ActiveRollbackRequest(BaseModel):
    frontier_id: str = Field(min_length=1, max_length=256)
    reason: str = Field(default="EXPLICIT_OPERATOR_ACTIVE_ROLLBACK", min_length=1, max_length=256)


class ActiveToolInvokeRequest(BaseModel):
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


def _admit(request: ActiveAdmissionRequest) -> Dict[str, Any]:
    operation = "api.runtime.optimization_active.admit"
    current = PASS200C_ACTIVE_AUTHORITY.current_frontier()
    evidence = PASS200C_ACTIVE_AUTHORITY.aggregate_canary_evidence(request.bundle_id)
    bundle = PASS200C_ACTIVE_AUTHORITY.pass200b.pass200a.get_bundle(request.bundle_id)
    now_ns = time.time_ns()
    expires_at_ns = now_ns + request.expires_in_seconds * 1_000_000_000
    roles = [
        (
            "compiler_approval",
            "vm81:compiler-active-authority",
            "COMPILER_ACTIVE_APPROVE",
        ),
        (
            "runtime_approval",
            "vm81:runtime-active-authority",
            "RUNTIME_ACTIVE_APPROVE",
        ),
        (
            "operations_approval",
            "vm81:operations-active-authority",
            "OPERATIONS_ACTIVE_APPROVE",
        ),
    ]
    approvals = []
    projections: Dict[str, Any] = {}
    for role, principal, capability in roles:
        source = f"{operation}.{role}"
        tick, receipt = _authorized_receipt(source)
        approvals.append(
            PASS200C_ACTIVE_AUTHORITY.build_approval(
                principal_id=principal,
                capability=capability,
                receipt_hash72=receipt,
                bundle_hash72=bundle["bundle_hash72"],
                evidence_hash72=evidence["evidence_hash72"],
                expected_frontier_hash72=current["frontier_hash72"],
                expires_at_ns=expires_at_ns,
            )
        )
        projections[role] = _tick_projection(role, source, tick, receipt)
    activation_source = f"{operation}.singleton_activation"
    activation_tick, activation_receipt = _authorized_receipt(activation_source)
    result = PASS200C_ACTIVE_AUTHORITY.admit_active(
        request.bundle_id,
        lease_invocation_limit=request.lease_invocation_limit,
        approvals=approvals,
        vm81_activation_receipt_hash72=activation_receipt,
        expires_at_ns=expires_at_ns,
        now_ns=now_ns,
    )
    projections["singleton_activation"] = _tick_projection(
        "singleton_activation",
        activation_source,
        activation_tick,
        activation_receipt,
    )
    result["vm81_authority"] = projections
    return result


@router.get("/status")
def active_status() -> Dict[str, Any]:
    operation = "api.runtime.optimization_active.status"
    ingress = _ingress(operation, {"method": "GET"})
    try:
        result = PASS200C_ACTIVE_AUTHORITY.status()
    except (Pass200CError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(operation, {"closed": result.get("closed"), "current_mode": result.get("current_mode")}),
    }
    return _contract_response("/api/runtime/optimization-active/status", "GET", result)


@router.get("/evidence/{bundle_id}")
def active_evidence(bundle_id: str) -> Dict[str, Any]:
    operation = "api.runtime.optimization_active.evidence"
    ingress = _ingress(operation, {"method": "GET", "bundle_id": bundle_id})
    try:
        result = PASS200C_ACTIVE_AUTHORITY.aggregate_canary_evidence(bundle_id)
    except (Pass200CError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(operation, {"bundle_id": bundle_id, "evidence_hash72": result.get("evidence_hash72")}),
    }
    return _contract_response("/api/runtime/optimization-active/evidence/{bundle_id}", "GET", result)


@router.post("/admit")
def active_admit(request: ActiveAdmissionRequest) -> Dict[str, Any]:
    operation = "api.runtime.optimization_active.admit"
    ingress = _ingress(operation, request.model_dump())
    try:
        result = _admit(request)
    except (Pass200CError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail={"schema": "HHS_PASS_200C_ADMISSION_FAILURE_V1", "reason": str(exc)}) from exc
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(operation, {"frontier_id": result.get("frontier_id"), "mode": result.get("mode")}),
    }
    return _contract_response("/api/runtime/optimization-active/admit", "POST", result)


@router.post("/probe")
def active_probe(request: ActiveProbeRequest) -> Dict[str, Any]:
    operation = "api.runtime.optimization_active.probe"
    ingress = _ingress(operation, request.model_dump())
    tick, receipt = _authorized_receipt(operation)
    try:
        result = PASS200C_ACTIVE_AUTHORITY.execute_verified_probe(
            request.frontier_id,
            invocation_receipt_hash72=receipt,
        )
    except (Pass200CError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail={"schema": "HHS_PASS_200C_PROBE_FAILURE_V1", "reason": str(exc)}) from exc
    result["vm81_authorized_tick"] = _tick_projection("active_invocation", operation, tick, receipt)
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(operation, {"status": result.get("status"), "returned_path": result.get("returned_path")}),
    }
    return _contract_response("/api/runtime/optimization-active/probe", "POST", result)


@router.post("/rollback")
def active_rollback(request: ActiveRollbackRequest) -> Dict[str, Any]:
    operation = "api.runtime.optimization_active.rollback"
    ingress = _ingress(operation, request.model_dump())
    tick, receipt = _authorized_receipt(operation)
    try:
        result = PASS200C_ACTIVE_AUTHORITY.rollback(
            request.frontier_id,
            reason=request.reason,
            vm81_rollback_receipt_hash72=receipt,
        )
    except (Pass200CError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail={"schema": "HHS_PASS_200C_ROLLBACK_FAILURE_V1", "reason": str(exc)}) from exc
    result["vm81_authorized_tick"] = _tick_projection("active_rollback", operation, tick, receipt)
    result["io"] = {
        "ingress": ingress,
        "egress": _egress(operation, {"frontier_id": result.get("frontier_id"), "mode": result.get("mode")}),
    }
    return _contract_response("/api/runtime/optimization-active/rollback", "POST", result)


@router.get("/frontiers")
def active_frontiers() -> Dict[str, Any]:
    operation = "api.runtime.optimization_active.frontiers"
    ingress = _ingress(operation, {"method": "GET"})
    try:
        records = PASS200C_ACTIVE_AUTHORITY.list_frontiers()
    except (Pass200CError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result = {"schema": "HHS_PASS_200C_FRONTIER_LIST_V1", "count": len(records), "frontiers": records}
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"count": len(records)})}
    return _contract_response("/api/runtime/optimization-active/frontiers", "GET", result)


@router.get("/invocations")
def active_invocations() -> Dict[str, Any]:
    operation = "api.runtime.optimization_active.invocations"
    ingress = _ingress(operation, {"method": "GET"})
    try:
        records = PASS200C_ACTIVE_AUTHORITY.list_invocations()
    except (Pass200CError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result = {"schema": "HHS_PASS_200C_INVOCATION_LIST_V1", "count": len(records), "invocations": records}
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"count": len(records)})}
    return _contract_response("/api/runtime/optimization-active/invocations", "GET", result)


@router.get("/verify")
def active_verify() -> Dict[str, Any]:
    operation = "api.runtime.optimization_active.verify"
    ingress = _ingress(operation, {"method": "GET"})
    try:
        result = PASS200C_ACTIVE_AUTHORITY.verify()
    except (Pass200CError, ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"ok": result.get("ok")})}
    return _contract_response("/api/runtime/optimization-active/verify", "GET", result)


@router.get("/tools")
def active_tools() -> Dict[str, Any]:
    operation = "api.runtime.optimization_active.tools"
    ingress = _ingress(operation, {"method": "GET"})
    tools = [
        {"name": "active.status", "method": "GET", "path": "/api/runtime/optimization-active/status", "mutation": False},
        {"name": "active.evidence", "method": "GET", "path": "/api/runtime/optimization-active/evidence/{bundle_id}", "mutation": True},
        {"name": "active.admit", "method": "POST", "path": "/api/runtime/optimization-active/admit", "mutation": True},
        {"name": "active.probe", "method": "POST", "path": "/api/runtime/optimization-active/probe", "mutation": True},
        {"name": "active.rollback", "method": "POST", "path": "/api/runtime/optimization-active/rollback", "mutation": True},
        {"name": "active.frontiers", "method": "GET", "path": "/api/runtime/optimization-active/frontiers", "mutation": False},
        {"name": "active.invocations", "method": "GET", "path": "/api/runtime/optimization-active/invocations", "mutation": False},
        {"name": "active.verify", "method": "GET", "path": "/api/runtime/optimization-active/verify", "mutation": False},
    ]
    result = {
        "schema": "HHS_PASS_200C_TOOL_REGISTRY_V1",
        "tools": tools,
        "three_approvals_required_for_admission": True,
        "mutation_requires_vm81_authorized_tick": True,
        "guard_every_active_invocation": True,
        "candidate_self_authorization": False,
        "automatic_frozen_constraint_promotion": False,
    }
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"tool_count": len(tools)})}
    return _contract_response("/api/runtime/optimization-active/tools", "GET", result)


@router.post("/tools/invoke")
def active_tool_invoke(request: ActiveToolInvokeRequest) -> Dict[str, Any]:
    operation = "api.runtime.optimization_active.tools.invoke"
    ingress = _ingress(operation, {"tool": request.tool})
    try:
        if request.tool == "active.status":
            result = PASS200C_ACTIVE_AUTHORITY.status()
        elif request.tool == "active.evidence":
            result = PASS200C_ACTIVE_AUTHORITY.aggregate_canary_evidence(str(request.arguments["bundle_id"]))
        elif request.tool == "active.admit":
            result = _admit(ActiveAdmissionRequest(**request.arguments))
        elif request.tool == "active.probe":
            tick, receipt = _authorized_receipt(operation)
            result = PASS200C_ACTIVE_AUTHORITY.execute_verified_probe(
                str(request.arguments["frontier_id"]),
                invocation_receipt_hash72=receipt,
            )
            result["vm81_authorized_tick"] = _tick_projection("active_invocation", operation, tick, receipt)
        elif request.tool == "active.rollback":
            tick, receipt = _authorized_receipt(operation)
            result = PASS200C_ACTIVE_AUTHORITY.rollback(
                str(request.arguments["frontier_id"]),
                reason=str(request.arguments.get("reason") or "EXPLICIT_TOOL_ACTIVE_ROLLBACK"),
                vm81_rollback_receipt_hash72=receipt,
            )
            result["vm81_authorized_tick"] = _tick_projection("active_rollback", operation, tick, receipt)
        elif request.tool == "active.frontiers":
            records = PASS200C_ACTIVE_AUTHORITY.list_frontiers()
            result = {"count": len(records), "frontiers": records}
        elif request.tool == "active.invocations":
            records = PASS200C_ACTIVE_AUTHORITY.list_invocations()
            result = {"count": len(records), "invocations": records}
        elif request.tool == "active.verify":
            result = PASS200C_ACTIVE_AUTHORITY.verify()
        else:
            raise Pass200CError(f"unknown active tool: {request.tool}")
    except (KeyError, TypeError, ValueError, RuntimeError, Pass200CError, OSError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    result["tool_invocation"] = {
        "schema": "HHS_PASS_200C_TOOL_INVOCATION_V1",
        "tool": request.tool,
        "tool_server_is_authority": False,
        "candidate_self_authorization": False,
    }
    result["io"] = {"ingress": ingress, "egress": _egress(operation, {"tool": request.tool, "ok": result.get("ok", True)})}
    return _contract_response("/api/runtime/optimization-active/tools/invoke", "POST", result)

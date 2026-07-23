"""Callable Pass 132 reconstructed consequence API routes."""
from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, HTTPException

from hhs_runtime.hhs_zero_bypass_runtime_interposer_v1 import interpose_runtime_surface

from hhs_runtime.hhs_pass132_reconstructed_replay_v1 import (
    Pass132ReconstructionError,
    get_pass132_reconstructed_service,
)

router = APIRouter(prefix="/api/runtime/consequences", tags=["pass132-reconstructed"])


def _interpose(method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    decision = interpose_runtime_surface(
        surface=f"runtime.executable_consequence_ab_control.pass132_reconstructed.{method}",
        request_class="canonical_full_witness_chain",
        payload=payload,
    )
    if not decision.get("execution_allowed"):
        raise HTTPException(status_code=403, detail={
            "code": "ZERO_BYPASS_INTERPOSITION_REJECTED",
            "status": decision.get("status"),
            "reason_code": decision.get("reason_code"),
        })
    return {
        "status": decision.get("status"),
        "reason_code": decision.get("reason_code"),
        "token_digest72": decision.get("interposition_token", {}).get("token_digest72"),
    }


def _call(method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        interposition = _interpose(method, payload)
        service = get_pass132_reconstructed_service()
        result = getattr(service, method)(payload)
        if isinstance(result, dict):
            result = dict(result)
            result["zero_bypass_interposition"] = interposition
        return result
    except Pass132ReconstructionError as exc:
        raise HTTPException(status_code=409, detail={"code": exc.code, "message": str(exc)}) from exc


@router.post("/execute")
def execute(payload: Dict[str, Any]):
    return _call("execute", payload)


@router.post("/replay")
def replay(payload: Dict[str, Any]):
    return _call("replay", payload)


@router.post("/compare")
def compare(payload: Dict[str, Any]):
    return _call("compare", payload)


@router.post("/foreign-model")
def foreign_model(payload: Dict[str, Any]):
    return _call("foreign_model", payload)


def _get(method: str, execution_root: str):
    try:
        interposition = _interpose(method, {"execution_root": execution_root})
        service = get_pass132_reconstructed_service()
        result = getattr(service, method)(execution_root)
        if isinstance(result, dict):
            result = dict(result)
            result["zero_bypass_interposition"] = interposition
        return result
    except Pass132ReconstructionError as exc:
        raise HTTPException(status_code=404, detail={"code": exc.code, "message": str(exc)}) from exc


@router.get("/{execution_root:path}/graph")
def graph(execution_root: str):
    return _get("graph", execution_root)


@router.get("/{execution_root:path}/logical")
def logical(execution_root: str):
    return _get("logical", execution_root)


@router.get("/{execution_root:path}/computational")
def computational(execution_root: str):
    return _get("computational", execution_root)


@router.get("/{execution_root:path}/receipts")
def receipts(execution_root: str):
    return _get("receipts", execution_root)


# The base path route is intentionally last because the path converter is
# greedy. It admits native Hash72 roots containing slash characters.
@router.get("/{execution_root:path}")
def get_execution(execution_root: str):
    return _get("get_execution", execution_root)

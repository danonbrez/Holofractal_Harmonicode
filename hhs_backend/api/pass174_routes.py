"""Pass 174 public API workflow projection.

The router is mounted by the canonical HHS visual server. It owns no worker,
ledger, scheduler, or alternate VM. All mutations call one explicit
Pass174Runtime whole-frame candidate/commit authority component.
"""
from __future__ import annotations

import os
import threading
from fractions import Fraction
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ConfigDict, Field

from hhs_runtime.pass174 import (
    AdmissionError,
    AuditResult,
    HarmonicOperator,
    Pass174Runtime,
    RetrievalError,
)

router = APIRouter(prefix="/api/v1/pass174", tags=["pass174"])

_RUNTIME: Pass174Runtime | None = None
_RUNTIME_LOCK = threading.RLock()


def _store_path() -> str:
    configured = os.environ.get("HHS174_STORE_PATH")
    if configured:
        return configured
    home = Path(os.environ.get("HHS_HOME", str(Path.home() / ".hhs"))).expanduser().resolve()
    return str(home / "state" / "vector-store" / "pass174.sqlite3")


def runtime() -> Pass174Runtime:
    global _RUNTIME
    with _RUNTIME_LOCK:
        if _RUNTIME is None:
            _RUNTIME = Pass174Runtime(store_path=_store_path())
        return _RUNTIME


def set_runtime_for_tests(instance: Pass174Runtime | None) -> None:
    global _RUNTIME
    with _RUNTIME_LOCK:
        _RUNTIME = instance


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ExecuteRequest(StrictModel):
    operator: dict[str, Any]
    mode: str = Field(default="auto", pattern="^(auto|direct|retrieval|hybrid)$")
    commit: bool = True


class QueryRequest(StrictModel):
    operator: dict[str, Any]


class QuarantineRequest(StrictModel):
    identity: str = Field(min_length=64, max_length=64)


class EfficiencyRequest(StrictModel):
    query_key: str = Field(min_length=64, max_length=64)


class AuditRequest(StrictModel):
    sample_count: int | None = Field(default=None, ge=1, le=5184)
    challenge_hex: str | None = None
    corruption_numerator: int = Field(default=1, ge=1)
    corruption_denominator: int = Field(default=100, ge=1)


class HarmonicCompileRequest(StrictModel):
    operator: dict[str, Any]


def _translate_error(exc: Exception) -> HTTPException:
    if isinstance(exc, RetrievalError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, AdmissionError):
        return HTTPException(status_code=409, detail=str(exc))
    return HTTPException(status_code=422, detail=str(exc))


@router.get("/status")
async def pass174_status() -> dict[str, Any]:
    return runtime().status()


@router.get("/frame")
async def pass174_frame() -> dict[str, Any]:
    engine = runtime()
    return {
        "schema": "P174FrameProjection@1",
        "current": engine.current_frame.to_dict(include_bits=True),
        "previous": engine.previous_frame.to_dict(),
        "candidate": engine.candidate.frame.to_dict(include_bits=True) if engine.candidate else None,
        "candidate_authoritative": False,
    }


@router.post("/execute")
async def pass174_execute(request: ExecuteRequest) -> dict[str, Any]:
    try:
        if request.commit:
            return runtime().execute_and_commit(request.operator, mode=request.mode)
        return runtime().execute(request.operator, mode=request.mode)
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.get("/phase")
async def pass174_phase() -> dict[str, Any]:
    return runtime().status()["phase"]


@router.post("/phase/step")
async def pass174_phase_step() -> dict[str, Any]:
    try:
        return runtime().execute_and_commit(
            {"kind": "rotate", "parameters": {"amount": 1}, "ordered_connectors": ["Rotate"]},
            mode="direct",
        )
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.get("/hash72/tip")
async def pass174_hash72_tip() -> dict[str, Any]:
    engine = runtime()
    return {
        "schema": "P174Hash72Tip@1",
        "tip": engine.hash72_tip,
        "transition_count": engine.transition_count,
        "logical_clock": True,
    }


@router.get("/hash72/trace")
async def pass174_hash72_trace() -> dict[str, Any]:
    engine = runtime()
    return {
        "schema": "P174Hash72Trace@1",
        "transitions": list(engine.hash72_trace[-engine.active_suffix_limit :]),
        "bounded": True,
        "limit": engine.active_suffix_limit,
    }


@router.get("/hash216/{identity}")
async def pass174_hash216(identity: str) -> dict[str, Any]:
    try:
        return runtime().get_hash216(identity)
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.post("/hash216/query")
async def pass174_hash216_query(request: QueryRequest) -> dict[str, Any]:
    try:
        return runtime().query_vectors(request.operator)
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.post("/hash216/retrieve")
async def pass174_hash216_retrieve(request: QueryRequest) -> dict[str, Any]:
    try:
        return runtime().execute_and_commit(request.operator, mode="retrieval")
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.post("/hash216/admit")
async def pass174_hash216_admit() -> dict[str, Any]:
    """Admit only an already computed complete candidate; raw object admission is forbidden."""
    try:
        return runtime().commit()
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.post("/hash216/quarantine")
async def pass174_hash216_quarantine(request: QuarantineRequest) -> dict[str, Any]:
    try:
        return runtime().quarantine(request.identity)
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.post("/harmonic/compile")
async def pass174_harmonic_compile(request: HarmonicCompileRequest) -> dict[str, Any]:
    try:
        operator = HarmonicOperator.from_mapping(request.operator)
        return {
            "schema": "P174HarmonicCompile@1",
            "operator": operator.to_dict(),
            "compiled_for": "singleton VM81 whole-frame authority",
            "hash72_advanced": False,
        }
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.post("/harmonic/execute")
async def pass174_harmonic_execute(request: ExecuteRequest) -> dict[str, Any]:
    return await pass174_execute(request)


@router.post("/efficiency/compare")
async def pass174_efficiency_compare(request: EfficiencyRequest) -> dict[str, Any]:
    try:
        return runtime().compare_efficiency(request.query_key)
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.get("/efficiency/report")
async def pass174_efficiency_report() -> dict[str, Any]:
    return runtime().efficiency_report()


def _audit_result(result: AuditResult) -> dict[str, Any]:
    return result.to_dict()


@router.post("/audit/light")
async def pass174_audit_light(request: AuditRequest) -> dict[str, Any]:
    try:
        challenge = bytes.fromhex(request.challenge_hex) if request.challenge_hex else None
        return _audit_result(
            runtime().audit(
                deep=False,
                sample_count=request.sample_count,
                challenge=challenge,
                assumed_corruption_fraction=Fraction(
                    request.corruption_numerator, request.corruption_denominator
                ),
            )
        )
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.post("/audit/deep")
async def pass174_audit_deep(request: AuditRequest) -> dict[str, Any]:
    try:
        challenge = bytes.fromhex(request.challenge_hex) if request.challenge_hex else None
        return _audit_result(
            runtime().audit(
                deep=True,
                sample_count=request.sample_count,
                challenge=challenge,
                assumed_corruption_fraction=Fraction(
                    request.corruption_numerator, request.corruption_denominator
                ),
            )
        )
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.post("/replay")
async def pass174_replay() -> dict[str, Any]:
    try:
        return runtime().replay()
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.get("/receipts/{identity}")
async def pass174_receipt(identity: str) -> dict[str, Any]:
    try:
        return runtime().receipt(identity)
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.get("/doctor")
async def pass174_doctor() -> dict[str, Any]:
    return runtime().doctor()


@router.websocket("/ws")
async def pass174_websocket(websocket: WebSocket) -> None:
    await websocket.accept()
    engine = runtime()
    queue = engine.subscribe()
    try:
        await websocket.send_json({"event": "P174_CONNECTED", "status": engine.status()})
        while True:
            event = await queue.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        pass
    finally:
        engine.unsubscribe(queue)

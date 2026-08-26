"""Governed HTTP surface for the repaired Pass 195 Kimi K3 content engine."""
from __future__ import annotations

import asyncio
from collections import deque
import os
import secrets
import time
from typing import Any, Deque, Dict, List, Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from hhs_backend.api.runtime_routes import (
    _contract_response,
    io_gateway,
    runtime_controller,
    runtime_graph,
)
from hhs_backend.runtime.hhs_kimi_k3_content_engine_v2 import (
    KIMI_K3_CONTENT_ENGINE,
)

router = APIRouter(
    prefix="/api/runtime/content-engine/kimi-k3",
    tags=[
        "runtime",
        "vm81",
        "content-generation",
        "graphics",
        "storyboard",
        "sprite-map",
        "native-mp4",
        "kimi-k3",
    ],
)


def _env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(maximum, value))


_MAX_CONCURRENT_PLANS = _env_int("HHS_KIMI_K3_MAX_CONCURRENT_PLANS", 2, 1, 16)
_RATE_LIMIT = _env_int("HHS_KIMI_K3_PLAN_RATE_LIMIT", 6, 1, 120)
_RATE_WINDOW_SECONDS = _env_int("HHS_KIMI_K3_PLAN_RATE_WINDOW_SECONDS", 60, 1, 3600)
_PLAN_SEMAPHORE = asyncio.Semaphore(_MAX_CONCURRENT_PLANS)
_RATE_LOCK = asyncio.Lock()
_RATE_TIMES: Deque[float] = deque()


class KimiReferenceImage(BaseModel):
    mime_type: str = Field(min_length=1, max_length=64)
    data_base64: str = Field(min_length=1)
    label: str = Field(default="reference", min_length=1, max_length=160)


class KimiContentPlanRequest(BaseModel):
    operation: str = Field(default="complete_pipeline", min_length=1, max_length=64)
    project_id: str = Field(default="project:graphics-content", min_length=1, max_length=256)
    title: str = Field(default="HHS KIMI K3 CONTENT PLAN", min_length=1, max_length=1024)
    source_text: str = Field(min_length=1, max_length=131_072)
    art_direction: str = Field(default="", max_length=32_768)
    duration_seconds: int = Field(default=90, ge=1, le=3600)
    fps: int = Field(default=30, ge=1, le=120)
    width: int = Field(default=1080, ge=16, le=8192)
    height: int = Field(default=1920, ge=16, le=8192)
    reference_images: List[KimiReferenceImage] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)


def _payload(request: BaseModel) -> Dict[str, Any]:
    return (
        request.model_dump(exclude_none=True)
        if hasattr(request, "model_dump")
        else request.dict(exclude_none=True)
    )


def _operator_token() -> str:
    return (os.getenv("HHS_KIMI_K3_OPERATOR_TOKEN") or "").strip()


def _require_operator_authorization(
    authorization: Optional[str], x_hhs_kimi_operator: Optional[str]
) -> None:
    configured = _operator_token()
    if not configured:
        raise HTTPException(
            status_code=503,
            detail={
                "schema": "HHS_KIMI_K3_OPERATOR_AUTHORIZATION_V1",
                "ok": False,
                "reason": "HHS_KIMI_K3_OPERATOR_TOKEN is not configured",
            },
        )
    candidate = (x_hhs_kimi_operator or "").strip()
    auth = (authorization or "").strip()
    if auth.lower().startswith("bearer "):
        candidate = auth[7:].strip()
    if not candidate or not secrets.compare_digest(candidate, configured):
        raise HTTPException(
            status_code=401,
            detail={
                "schema": "HHS_KIMI_K3_OPERATOR_AUTHORIZATION_V1",
                "ok": False,
                "reason": "operator authorization required",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )


async def _consume_rate_slot() -> None:
    now = time.monotonic()
    cutoff = now - _RATE_WINDOW_SECONDS
    async with _RATE_LOCK:
        while _RATE_TIMES and _RATE_TIMES[0] <= cutoff:
            _RATE_TIMES.popleft()
        if len(_RATE_TIMES) >= _RATE_LIMIT:
            raise HTTPException(
                status_code=429,
                detail={
                    "schema": "HHS_KIMI_K3_PLAN_RATE_LIMIT_V1",
                    "ok": False,
                    "reason": "bounded Kimi K3 plan rate exceeded",
                    "limit": _RATE_LIMIT,
                    "window_seconds": _RATE_WINDOW_SECONDS,
                },
            )
        _RATE_TIMES.append(now)


def _packet_from_authorized_tick(authorized_tick: Dict[str, Any]) -> Dict[str, Any]:
    """Freeze the exact authorized state before any external-provider await."""
    runtime = dict(authorized_tick.get("runtime") or {})
    receipt = dict(authorized_tick.get("receipt") or {})
    state_hash72 = str(runtime.get("state_hash72") or "")
    receipt_hash72 = str(receipt.get("receipt_hash72") or "")
    if not state_hash72 or not receipt_hash72:
        raise RuntimeError("KIMI_K3_AUTHORIZED_TICK_RECEIPT_REQUIRED")
    runtime["receipt_hash72"] = receipt_hash72
    return {
        "runtime": runtime,
        "vector_record": {
            "hash72": state_hash72,
            "vector": [ord(ch) / 255.0 for ch in state_hash72],
            "step": runtime.get("step"),
        },
    }


@router.get("/status")
def kimi_k3_content_status() -> Dict[str, Any]:
    ingress = io_gateway.ingress(
        "api.runtime.content_engine.kimi_k3.status",
        {"method": "GET"},
    )
    result = KIMI_K3_CONTENT_ENGINE.status()
    result["operator_authorization_required_for_plan"] = True
    result["max_concurrent_plans"] = _MAX_CONCURRENT_PLANS
    result["plan_rate_limit"] = _RATE_LIMIT
    result["plan_rate_window_seconds"] = _RATE_WINDOW_SECONDS
    result["io"] = {
        "ingress": ingress,
        "egress": io_gateway.egress(
            "api.runtime.content_engine.kimi_k3.status",
            {
                "enabled": result.get("enabled"),
                "configured": result.get("configured"),
                "model_id": result.get("model_id"),
                "operator_authorization_required_for_plan": True,
            },
        ),
    }
    return _contract_response(
        "/api/runtime/content-engine/kimi-k3/status",
        "GET",
        result,
    )


@router.get("/health")
async def kimi_k3_content_health() -> Dict[str, Any]:
    ingress = io_gateway.ingress(
        "api.runtime.content_engine.kimi_k3.health",
        {"method": "GET"},
    )
    result = await KIMI_K3_CONTENT_ENGINE.health()
    result["io"] = {
        "ingress": ingress,
        "egress": io_gateway.egress(
            "api.runtime.content_engine.kimi_k3.health",
            {
                "online": result.get("online"),
                "configured_model_registered": result.get(
                    "configured_model_registered"
                ),
            },
        ),
    }
    return _contract_response(
        "/api/runtime/content-engine/kimi-k3/health",
        "GET",
        result,
    )


@router.post("/plan")
async def kimi_k3_content_plan(
    request: KimiContentPlanRequest,
    authorization: Optional[str] = Header(default=None),
    x_hhs_kimi_operator: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    _require_operator_authorization(authorization, x_hhs_kimi_operator)
    await _consume_rate_slot()
    payload = _payload(request)
    ingress = io_gateway.ingress(
        "api.runtime.content_engine.kimi_k3.plan",
        {
            "method": "POST",
            "operation": request.operation,
            "project_id": request.project_id,
            "source_text_length": len(request.source_text),
            "reference_image_count": len(request.reference_images),
            "duration_seconds": request.duration_seconds,
            "fps": request.fps,
            "width": request.width,
            "height": request.height,
            "operator_authorized": True,
        },
    )
    try:
        authorized_tick = runtime_controller.authorized_tick(
            source="api.runtime.content_engine.kimi_k3.plan"
        )
        # Ingest this exact committed state immediately. Never export a later global
        # state after the external provider returns.
        runtime_graph.ingest_runtime_state(_packet_from_authorized_tick(authorized_tick))
        async with _PLAN_SEMAPHORE:
            result = await KIMI_K3_CONTENT_ENGINE.generate(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "schema": "HHS_KIMI_K3_CONTENT_REQUEST_REJECTION_V2",
                "ok": False,
                "reason": str(exc),
            },
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "schema": "HHS_KIMI_K3_CONTENT_PROVIDER_ERROR_V2",
                "ok": False,
                "reason": str(exc),
            },
        ) from exc

    result["vm81_authorized_tick"] = {
        "source": "api.runtime.content_engine.kimi_k3.plan",
        "receipt_hash72": (
            authorized_tick.get("receipt", {}).get("receipt_hash72")
            if isinstance(authorized_tick, dict)
            else None
        ),
        "runtime_step": (
            authorized_tick.get("runtime", {}).get("step")
            if isinstance(authorized_tick, dict)
            else None
        ),
        "graph_state_ingested_before_provider_await": True,
        "provider_plan_grants_direct_mutation": False,
    }
    result["io"] = {
        "ingress": ingress,
        "egress": io_gateway.egress(
            "api.runtime.content_engine.kimi_k3.plan",
            {
                "status": result.get("status"),
                "plan_root_hash72": (result.get("plan") or {}).get(
                    "plan_root_hash72"
                ),
                "provider_invocation_receipt_hash72": result.get(
                    "provider_invocation_receipt_hash72"
                ),
                "native_asset_execution_admitted": result.get(
                    "native_asset_execution_admitted"
                ),
                "operator_authorized": True,
            },
        ),
    }
    return _contract_response(
        "/api/runtime/content-engine/kimi-k3/plan",
        "POST",
        result,
    )

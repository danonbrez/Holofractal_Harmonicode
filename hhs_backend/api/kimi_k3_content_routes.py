"""Governed HTTP surface for the Pass 195 Kimi K3 content engine."""
from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_backend.api.runtime_routes import (
    _contract_response,
    io_gateway,
    runtime_controller,
    runtime_graph,
)
from hhs_backend.runtime.hhs_kimi_k3_content_engine_v1 import (
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


@router.get("/status")
def kimi_k3_content_status() -> Dict[str, Any]:
    ingress = io_gateway.ingress(
        "api.runtime.content_engine.kimi_k3.status",
        {"method": "GET"},
    )
    result = KIMI_K3_CONTENT_ENGINE.status()
    result["io"] = {
        "ingress": ingress,
        "egress": io_gateway.egress(
            "api.runtime.content_engine.kimi_k3.status",
            {
                "enabled": result.get("enabled"),
                "configured": result.get("configured"),
                "model_id": result.get("model_id"),
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
) -> Dict[str, Any]:
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
        },
    )
    try:
        authorized_tick = runtime_controller.authorized_tick(
            source="api.runtime.content_engine.kimi_k3.plan"
        )
        result = await KIMI_K3_CONTENT_ENGINE.generate(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "schema": "HHS_KIMI_K3_CONTENT_REQUEST_REJECTION_V1",
                "ok": False,
                "reason": str(exc),
            },
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "schema": "HHS_KIMI_K3_CONTENT_PROVIDER_ERROR_V1",
                "ok": False,
                "reason": str(exc),
            },
        ) from exc

    packet = runtime_controller.export_multimodal_packet()
    runtime_graph.ingest_runtime_state(packet)
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
            },
        ),
    }
    return _contract_response(
        "/api/runtime/content-engine/kimi-k3/plan",
        "POST",
        result,
    )

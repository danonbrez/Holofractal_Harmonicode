"""VM81 runtime API routes for governed creative-writing generation."""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_backend.api.runtime_routes import (
    _contract_response,
    io_gateway,
    runtime_controller,
    runtime_graph,
)
from hhs_backend.runtime.hhs_vm81_creative_novel_v1 import (
    DEFAULT_PREMISE,
    DEFAULT_VM81_CREATIVE_NOVEL_GENERATOR,
)

router = APIRouter(
    prefix="/api/runtime/creative",
    tags=["runtime", "vm81", "creative-writing", "litert-lm"],
)


class VM81CreativeNovelRequest(BaseModel):
    title: str = Field(default="The Ninth Archive", min_length=1, max_length=160)
    premise: str = Field(default=DEFAULT_PREMISE, min_length=1, max_length=8000)
    chapter_count: int = Field(default=9, ge=3, le=24)
    target_words: int = Field(default=9000, ge=3000, le=120000)
    filename: Optional[str] = None
    max_concurrency: int = Field(default=2, ge=1, le=4)
    persist: bool = True
    project_id: str = "project:creative-writing"
    request_class: str = "canonical_full_witness_chain"


@router.get("/novel/status")
async def vm81_creative_novel_status() -> Dict[str, Any]:
    ingress = io_gateway.ingress(
        "api.runtime.creative.novel.status",
        {"method": "GET"},
    )
    status = DEFAULT_VM81_CREATIVE_NOVEL_GENERATOR.status()
    status["io"] = {
        "ingress": ingress,
        "egress": io_gateway.egress(
            "api.runtime.creative.novel.status",
            {
                "ok": status.get("ok"),
                "request_model_id": status.get("request_model_id"),
            },
        ),
    }
    return _contract_response(
        "/api/runtime/creative/novel/status",
        "GET",
        status,
    )


@router.post("/novel")
async def vm81_generate_creative_novel(
    request: VM81CreativeNovelRequest,
) -> Dict[str, Any]:
    payload = (
        request.model_dump(exclude_none=True)
        if hasattr(request, "model_dump")
        else request.dict(exclude_none=True)
    )
    ingress = io_gateway.ingress(
        "api.runtime.creative.novel",
        {
            "method": "POST",
            "title": request.title,
            "chapter_count": request.chapter_count,
            "target_words": request.target_words,
            "request_class": request.request_class,
        },
    )
    try:
        authorized_tick = runtime_controller.authorized_tick(
            source="api.runtime.creative.novel"
        )
        result = await DEFAULT_VM81_CREATIVE_NOVEL_GENERATOR.generate(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "schema": "HHS_VM81_CREATIVE_NOVEL_REQUEST_REJECTION_V1",
                "ok": False,
                "reason": str(exc),
            },
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "schema": "HHS_VM81_CREATIVE_NOVEL_PROVIDER_ERROR_V1",
                "ok": False,
                "reason": str(exc),
            },
        ) from exc

    packet = runtime_controller.export_multimodal_packet()
    runtime_graph.ingest_runtime_state(packet)
    result["vm81_authorized_tick"] = {
        "source": "api.runtime.creative.novel",
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
    }
    result["io"] = {
        "ingress": ingress,
        "egress": io_gateway.egress(
            "api.runtime.creative.novel",
            {
                "status": result.get("status"),
                "artifact_path": result.get("artifact_path"),
                "novel_root_hash72": result.get("novel_root_hash72"),
                "word_count": result.get("word_count"),
            },
        ),
    }
    return _contract_response(
        "/api/runtime/creative/novel",
        "POST",
        result,
    )

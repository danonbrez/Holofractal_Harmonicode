"""Public HTTP surface for the HHS native high-fidelity storybook studio."""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from hhs_backend.api.runtime_routes import _contract_response, io_gateway, runtime_controller, runtime_graph
from hhs_backend.runtime.hhs_storybook_reel_v2 import STORYBOOK_REEL_RUNTIME

router = APIRouter(
    prefix="/api/runtime/storybook-reel",
    tags=["runtime", "vm81", "game-engine", "storybook-reel", "media", "pass202"],
)


class StorybookDefaultsRequest(BaseModel):
    text: str = Field(default="", max_length=16_384)


class StorybookResolveRequest(BaseModel):
    text: str = Field(default="", max_length=16_384)
    template_id: Optional[str] = None
    style: Dict[str, Any] = Field(default_factory=dict)
    quality_profile: Optional[str] = None
    render: Dict[str, Any] = Field(default_factory=dict)
    native_layers: Dict[str, Any] = Field(default_factory=dict)


class StorybookGenerateRequest(BaseModel):
    audio_id: str = Field(min_length=38, max_length=38)
    text: str = Field(min_length=1, max_length=16_384)
    title: str = Field(default="HHS STORYBOOK", min_length=1, max_length=128)
    template_id: Optional[str] = None
    style: Dict[str, Any] = Field(default_factory=dict)
    quality_profile: Optional[str] = None
    render: Dict[str, Any] = Field(default_factory=dict)
    native_layers: Dict[str, Any] = Field(default_factory=dict)
    alignment: Optional[Dict[str, Any]] = None


def _dump(model: BaseModel) -> Dict[str, Any]:
    return model.model_dump(exclude_none=True) if hasattr(model, "model_dump") else model.dict(exclude_none=True)


def _rejection(schema: str, reason: str, remediation: str, *, retryable: bool = False) -> Dict[str, Any]:
    return {
        "schema": schema,
        "ok": False,
        "reason": reason,
        "retryable": retryable,
        "remediation": remediation,
        "frontend_result_fabricated": False,
    }


@router.get("/status")
def storybook_reel_status() -> Dict[str, Any]:
    ingress = io_gateway.ingress("api.runtime.storybook_reel.status", {"method": "GET"})
    result = STORYBOOK_REEL_RUNTIME.status()
    result["io"] = {
        "ingress": ingress,
        "egress": io_gateway.egress(
            "api.runtime.storybook_reel.status",
            {
                "ok": result.get("ok"),
                "single_threaded": result.get("single_threaded"),
                "template_count": len(result.get("templates") or []),
                "high_fidelity_compositor": result.get("high_fidelity_compositor"),
                "default_quality_profile": result.get("default_quality_profile"),
            },
        ),
    }
    return _contract_response("/api/runtime/storybook-reel/status", "GET", result)


@router.get("/parameters")
def storybook_reel_parameters() -> Dict[str, Any]:
    return _contract_response(
        "/api/runtime/storybook-reel/parameters",
        "GET",
        STORYBOOK_REEL_RUNTIME.parameter_catalog(),
    )


@router.get("/presets")
def storybook_reel_presets() -> Dict[str, Any]:
    return _contract_response(
        "/api/runtime/storybook-reel/presets",
        "GET",
        STORYBOOK_REEL_RUNTIME.presets(),
    )


@router.post("/parameters/resolve")
def storybook_reel_parameters_resolve(request: StorybookResolveRequest) -> Dict[str, Any]:
    payload = _dump(request)
    try:
        result = STORYBOOK_REEL_RUNTIME.resolve_parameters(payload)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=422,
            detail=_rejection(
                "HHS_PASS_202_PARAMETER_REJECTION_V1",
                str(exc),
                "Inspect GET /api/runtime/storybook-reel/parameters and submit values within the published type, range, and enum constraints.",
            ),
        ) from exc
    return _contract_response(
        "/api/runtime/storybook-reel/parameters/resolve",
        "POST",
        result,
    )


@router.post("/defaults")
def storybook_reel_defaults(request: StorybookDefaultsRequest) -> Dict[str, Any]:
    ingress = io_gateway.ingress(
        "api.runtime.storybook_reel.defaults",
        {"method": "POST", "text_length": len(request.text)},
    )
    result = STORYBOOK_REEL_RUNTIME.contextual_defaults(request.text)
    result["ok"] = True
    result["status"] = "STORYBOOK_REEL_DEFAULTS_READY"
    result["io"] = {
        "ingress": ingress,
        "egress": io_gateway.egress(
            "api.runtime.storybook_reel.defaults",
            {
                "template_id": result.get("template_id"),
                "candidate_count": result.get("candidate_count"),
                "quality_profile": result.get("quality_profile"),
                "chromatic_tonic": (result.get("palette") or {}).get("chromatic_tonic"),
            },
        ),
    }
    return _contract_response("/api/runtime/storybook-reel/defaults", "POST", result)


@router.post("/defaults/candidates")
def storybook_reel_default_candidates(request: StorybookDefaultsRequest) -> Dict[str, Any]:
    result = STORYBOOK_REEL_RUNTIME.contextual_defaults(request.text)
    return _contract_response(
        "/api/runtime/storybook-reel/defaults/candidates",
        "POST",
        {
            "schema": "HHS_PASS_202_CONTEXTUAL_TEMPLATE_CANDIDATES_V1",
            "ok": True,
            "template_id": result.get("template_id"),
            "quality_profile": result.get("quality_profile"),
            "candidate_count": result.get("candidate_count"),
            "candidates": result.get("template_candidates"),
            "reason_trace_public": True,
        },
    )


@router.post("/audio")
async def storybook_reel_audio_upload(request: Request) -> Dict[str, Any]:
    data = await request.body()
    filename = request.headers.get("x-hhs-filename") or request.headers.get("x-filename") or "narration.wav"
    content_type = request.headers.get("content-type") or "application/octet-stream"
    ingress = io_gateway.ingress(
        "api.runtime.storybook_reel.audio",
        {
            "method": "POST",
            "filename": filename,
            "content_type": content_type,
            "size_bytes": len(data),
        },
    )
    try:
        result = STORYBOOK_REEL_RUNTIME.upload_audio(data, filename, content_type)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=_rejection(
                "HHS_STORYBOOK_REEL_AUDIO_REJECTION_V2",
                str(exc),
                "Upload a supported audio file to POST /api/runtime/storybook-reel/audio before submitting generation.",
            ),
        ) from exc
    except (RuntimeError, OSError) as exc:
        raise HTTPException(
            status_code=503,
            detail=_rejection(
                "HHS_STORYBOOK_REEL_AUDIO_RUNTIME_ERROR_V2",
                str(exc),
                "Inspect GET /api/runtime/storybook-reel/status for ffmpeg and ffprobe capability flags, install missing host tools, then retry the upload.",
                retryable=True,
            ),
        ) from exc
    result["io"] = {
        "ingress": ingress,
        "egress": io_gateway.egress(
            "api.runtime.storybook_reel.audio",
            {
                "audio_id": result.get("audio_id"),
                "audio_root_hash72": result.get("audio_root_hash72"),
                "duration_seconds": result.get("duration_seconds"),
            },
        ),
    }
    return _contract_response("/api/runtime/storybook-reel/audio", "POST", result)


@router.post("/generate")
def storybook_reel_generate(request: StorybookGenerateRequest) -> Dict[str, Any]:
    payload = _dump(request)
    ingress = io_gateway.ingress(
        "api.runtime.storybook_reel.generate",
        {
            "method": "POST",
            "audio_id": request.audio_id,
            "text_length": len(request.text),
            "template_id": request.template_id,
            "quality_profile": request.quality_profile,
            "single_threaded": True,
        },
    )
    try:
        authorized_tick = runtime_controller.authorized_tick(source="api.runtime.storybook_reel.generate")
        result = STORYBOOK_REEL_RUNTIME.generate(payload)
    except (ValueError, FileNotFoundError) as exc:
        remediation = (
            "POST the narration file to /api/runtime/storybook-reel/audio first and use the returned audio_id. "
            "Validate visual parameters through POST /api/runtime/storybook-reel/parameters/resolve before retrying."
        )
        raise HTTPException(
            status_code=422,
            detail=_rejection(
                "HHS_STORYBOOK_REEL_REQUEST_REJECTION_V2",
                str(exc),
                remediation,
            ),
        ) from exc
    except (RuntimeError, OSError) as exc:
        raise HTTPException(
            status_code=503,
            detail=_rejection(
                "HHS_STORYBOOK_REEL_GENERATION_ERROR_V2",
                str(exc),
                "Inspect the storybook status capability flags, native Makefile source layout, ffmpeg/ffprobe availability, and native CLI readiness, then retry the same receipt-bound request.",
                retryable=True,
            ),
        ) from exc
    packet = runtime_controller.export_multimodal_packet()
    runtime_graph.ingest_runtime_state(packet)
    result["vm81_authorized_tick"] = {
        "source": "api.runtime.storybook_reel.generate",
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
            "api.runtime.storybook_reel.generate",
            {
                "artifact_id": result.get("artifact_id"),
                "receipt_hash72": result.get("receipt_hash72"),
                "video_sha256_transport_hint": result.get("video_sha256_transport_hint"),
                "quality_profile": (result.get("pass202") or {}).get("quality_profile"),
                "resolution_hash72": (result.get("pass202") or {}).get("resolution_hash72"),
            },
        ),
    }
    return _contract_response("/api/runtime/storybook-reel/generate", "POST", result)


@router.get("/artifacts/{artifact_id}")
def storybook_reel_artifact(artifact_id: str) -> Dict[str, Any]:
    try:
        result = STORYBOOK_REEL_RUNTIME.artifact(artifact_id)
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _contract_response(
        "/api/runtime/storybook-reel/artifacts/{artifact_id}",
        "GET",
        result,
    )


@router.get("/artifacts/{artifact_id}/download.zip", response_model=None)
def storybook_reel_download(artifact_id: str) -> Any:
    try:
        path = STORYBOOK_REEL_RUNTIME.artifact_path(artifact_id, "zip")
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(
        path,
        media_type="application/zip",
        filename="hhs-storybook-reel-package.zip",
        headers={"Cache-Control": "private, no-store"},
    )


@router.get("/artifacts/{artifact_id}/video.mp4", response_model=None)
def storybook_reel_video(artifact_id: str) -> Any:
    try:
        path = STORYBOOK_REEL_RUNTIME.artifact_path(artifact_id, "video")
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(
        path,
        media_type="video/mp4",
        filename="storybook-reel.mp4",
        headers={"Cache-Control": "private, no-store"},
    )

"""Public API for the cumulative Pass 203 native storybook and game renderer."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from hhs_backend.api.runtime_routes import _contract_response, io_gateway, runtime_controller, runtime_graph
from hhs_backend.runtime.hhs_storybook_elevenlabs_v1 import ElevenLabsVoiceoverClient
from hhs_backend.runtime.hhs_storyboard_voice_sync_v1 import extract_storyboard_frames, validate_serialized_storyboard
from hhs_backend.runtime.hhs_storybook_reel_v3 import (
    CLASSIFICATION,
    CONTRACT,
    STORYBOOK_REEL_RUNTIME,
)

router = APIRouter(
    prefix="/api/runtime/storybook-reel",
    tags=["runtime", "vm81", "game-engine", "graphics", "shader", "storybook-reel", "media", "pass203"],
)


class StorybookDefaultsRequest(BaseModel):
    text: str = Field(default="", max_length=16_384)
    candidate_count: int = Field(default=3, ge=1, le=8)


class StorybookResolveRequest(BaseModel):
    text: str = Field(default="", max_length=16_384)
    title: str = Field(default="HHS STORYBOOK", min_length=1, max_length=128)
    template_id: Optional[str] = None
    quality_profile: Optional[str] = None
    style: Dict[str, Any] = Field(default_factory=dict)
    render: Dict[str, Any] = Field(default_factory=dict)
    native_layers: Dict[str, Any] = Field(default_factory=dict)


class StorybookVoiceoverRequest(BaseModel):
    text: str = Field(min_length=1, max_length=16_384)
    voice_id: str = Field(min_length=1, max_length=256)
    model_id: str = Field(default="eleven_multilingual_v2", min_length=1, max_length=128)
    initial_speed: float = Field(default=1.0, ge=0.7, le=1.2)
    stability: float = Field(default=0.50, ge=0.0, le=1.0)
    similarity_boost: float = Field(default=0.75, ge=0.0, le=1.0)
    style: float = Field(default=0.0, ge=0.0, le=1.0)
    use_speaker_boost: bool = True
    max_attempts: int = Field(default=3, ge=1, le=5)
    storyboard_markdown: Optional[str] = Field(default=None, max_length=64_000)

class StorybookGenerateRequest(BaseModel):
    audio_id: str = Field(min_length=38, max_length=38)
    text: str = Field(min_length=1, max_length=16_384)
    title: str = Field(default="HHS STORYBOOK", min_length=1, max_length=128)
    template_id: Optional[str] = None
    quality_profile: Optional[str] = None
    style: Dict[str, Any] = Field(default_factory=dict)
    render: Dict[str, Any] = Field(default_factory=dict)
    native_layers: Dict[str, Any] = Field(default_factory=dict)
    alignment: Optional[Dict[str, Any]] = None


def _error(schema: str, reason: str, *, retryable: bool, remediation: str) -> Dict[str, Any]:
    return {
        "schema": schema,
        "contract": CONTRACT,
        "classification": CLASSIFICATION,
        "ok": False,
        "reason": reason,
        "retryable": retryable,
        "remediation": remediation,
    }


def _dump(model: BaseModel) -> Dict[str, Any]:
    return model.model_dump(exclude_none=True) if hasattr(model, "model_dump") else model.dict(exclude_none=True)


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
                "quality_profile_count": len(result.get("quality_profiles") or []),
                "parameter_catalog_url": result.get("parameter_catalog_url"),
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


@router.post("/resolve")
def storybook_reel_resolve(request: StorybookResolveRequest) -> Dict[str, Any]:
    try:
        result = STORYBOOK_REEL_RUNTIME.resolve_parameters(_dump(request))
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=422,
            detail=_error(
                "HHS_PASS_203_RENDER_PARAMETER_REJECTION_V1",
                str(exc),
                retryable=False,
                remediation="Read GET /api/runtime/storybook-reel/parameters and submit values inside the declared type, enum, and range constraints.",
            ),
        ) from exc
    return _contract_response("/api/runtime/storybook-reel/resolve", "POST", result)


@router.post("/defaults")
def storybook_reel_defaults(request: StorybookDefaultsRequest) -> Dict[str, Any]:
    ingress = io_gateway.ingress(
        "api.runtime.storybook_reel.defaults",
        {"method": "POST", "text_length": len(request.text), "candidate_count": request.candidate_count},
    )
    result = STORYBOOK_REEL_RUNTIME.contextual_defaults(request.text)
    candidates: List[Dict[str, Any]] = list(result.get("template_candidates") or [])[: request.candidate_count]
    result["template_candidates"] = candidates
    result["candidate_count"] = len(candidates)
    result["ok"] = True
    result["status"] = "STORYBOOK_REEL_CONTEXTUAL_DIRECTION_READY"
    result["io"] = {
        "ingress": ingress,
        "egress": io_gateway.egress(
            "api.runtime.storybook_reel.defaults",
            {
                "template_id": result.get("template_id"),
                "candidate_count": len(candidates),
                "quality_profile": result.get("quality_profile"),
            },
        ),
    }
    return _contract_response("/api/runtime/storybook-reel/defaults", "POST", result)


@router.post("/voiceover/sync")
def storybook_reel_voiceover_sync(request: StorybookVoiceoverRequest) -> Dict[str, Any]:
    frames = None
    if request.storyboard_markdown:
        frames = extract_storyboard_frames(request.storyboard_markdown)
        validate_serialized_storyboard(frames)
    client = ElevenLabsVoiceoverClient()
    if not client.configured:
        raise HTTPException(
            status_code=503,
            detail=_error(
                "HHS_STORYBOOK_ELEVENLABS_NOT_CONFIGURED_V1",
                "ELEVENLABS_API_KEY is not configured",
                retryable=True,
                remediation="Configure ELEVENLABS_API_KEY on the Storybook Reel service and retry.",
            ),
        )
    try:
        generated = client.synthesize_fitted(
            text=request.text,
            voice_id=request.voice_id,
            model_id=request.model_id,
            initial_speed=request.initial_speed,
            stability=request.stability,
            similarity_boost=request.similarity_boost,
            style=request.style,
            use_speaker_boost=request.use_speaker_boost,
            max_attempts=request.max_attempts,
            storyboard_frames=frames,
        )
        audio = STORYBOOK_REEL_RUNTIME.upload_audio(
            generated.audio,
            "elevenlabs-voiceover.mp3",
            "audio/mpeg",
        )
        sync_urls = STORYBOOK_REEL_RUNTIME.save_voice_sync(audio["audio_id"], generated.manifest)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=_error(
                "HHS_STORYBOOK_VOICE_SYNC_REJECTION_V1",
                str(exc),
                retryable=False,
                remediation="Shorten or repace the narration, verify the exact transcript, then regenerate.",
            ),
        ) from exc
    except (RuntimeError, OSError) as exc:
        raise HTTPException(
            status_code=503,
            detail=_error(
                "HHS_STORYBOOK_ELEVENLABS_RUNTIME_ERROR_V1",
                str(exc),
                retryable=True,
                remediation="Verify the ElevenLabs API key, voice ID, network access, and provider availability.",
            ),
        ) from exc
    return _contract_response(
        "/api/runtime/storybook-reel/voiceover/sync",
        "POST",
        {
            "ok": True,
            "status": "STORYBOOK_VOICEOVER_88S_SYNC_READY",
            "audio_id": audio["audio_id"],
            "audio_duration_seconds": audio["duration_seconds"],
            "alignment": dict(generated.alignment),
            "voice_sync": dict(generated.manifest),
            **sync_urls,
        },
    )

@router.post("/audio")
async def storybook_reel_audio_upload(request: Request) -> Dict[str, Any]:
    data = await request.body()
    filename = request.headers.get("x-hhs-filename") or request.headers.get("x-filename") or "narration.wav"
    content_type = request.headers.get("content-type") or "application/octet-stream"
    ingress = io_gateway.ingress(
        "api.runtime.storybook_reel.audio",
        {"method": "POST", "filename": filename, "content_type": content_type, "size_bytes": len(data)},
    )
    try:
        result = STORYBOOK_REEL_RUNTIME.upload_audio(data, filename, content_type)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=_error(
                "HHS_STORYBOOK_REEL_AUDIO_REJECTION_V2",
                str(exc),
                retryable=False,
                remediation="Upload a non-empty supported audio file. When ffprobe is unavailable, use a WAV source or install the declared host media toolchain.",
            ),
        ) from exc
    except (RuntimeError, OSError) as exc:
        raise HTTPException(
            status_code=503,
            detail=_error(
                "HHS_STORYBOOK_REEL_AUDIO_RUNTIME_ERROR_V2",
                str(exc),
                retryable=True,
                remediation="Inspect GET /api/runtime/storybook-reel/status and restore the missing ffprobe or media dependency.",
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
    except (ValueError, FileNotFoundError, TypeError) as exc:
        raise HTTPException(
            status_code=422,
            detail=_error(
                "HHS_PASS_203_STORYBOOK_RENDER_REQUEST_REJECTION_V1",
                str(exc),
                retryable=False,
                remediation="Resolve the request through POST /api/runtime/storybook-reel/resolve, upload narration through POST /audio, then submit the returned parameter shape.",
            ),
        ) from exc
    except (RuntimeError, OSError) as exc:
        raise HTTPException(
            status_code=503,
            detail=_error(
                "HHS_PASS_203_STORYBOOK_RENDER_RUNTIME_ERROR_V1",
                str(exc),
                retryable=True,
                remediation="Inspect /status. Install ffmpeg/ffprobe for MP4 transport or use the raw native stream outputs declared by the runtime.",
            ),
        ) from exc
    packet = runtime_controller.export_multimodal_packet()
    runtime_graph.ingest_runtime_state(packet)
    result["vm81_authorized_tick"] = {
        "source": "api.runtime.storybook_reel.generate",
        "receipt_hash72": (authorized_tick.get("receipt") or {}).get("receipt_hash72") if isinstance(authorized_tick, dict) else None,
        "runtime_step": (authorized_tick.get("runtime") or {}).get("step") if isinstance(authorized_tick, dict) else None,
    }
    result["io"] = {
        "ingress": ingress,
        "egress": io_gateway.egress(
            "api.runtime.storybook_reel.generate",
            {
                "artifact_id": result.get("artifact_id"),
                "receipt_hash72": result.get("receipt_hash72"),
                "width": result.get("width"),
                "height": result.get("height"),
                "quality_profile": (result.get("pass203") or {}).get("quality_profile"),
            },
        ),
    }
    return _contract_response("/api/runtime/storybook-reel/generate", "POST", result)


@router.get("/audio/{audio_id}/source", response_model=None)
def storybook_reel_audio_source(audio_id: str) -> Any:
    try:
        path = STORYBOOK_REEL_RUNTIME.audio_asset_path(audio_id, "source")
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(path, media_type="audio/mpeg", filename=path.name, headers={"Cache-Control": "private, no-store"})


@router.get("/audio/{audio_id}/voice-sync.json", response_model=None)
def storybook_reel_voice_sync_json(audio_id: str) -> Any:
    try:
        path = STORYBOOK_REEL_RUNTIME.audio_asset_path(audio_id, "voice_sync_json")
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(path, media_type="application/json", filename="voice-sync.json", headers={"Cache-Control": "private, no-store"})


@router.get("/audio/{audio_id}/voice-sync.csv", response_model=None)
def storybook_reel_voice_sync_csv(audio_id: str) -> Any:
    try:
        path = STORYBOOK_REEL_RUNTIME.audio_asset_path(audio_id, "voice_sync_csv")
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(path, media_type="text/csv", filename="voice-sync.csv", headers={"Cache-Control": "private, no-store"})

@router.get("/artifacts/{artifact_id}")
def storybook_reel_artifact(artifact_id: str) -> Dict[str, Any]:
    try:
        result = STORYBOOK_REEL_RUNTIME.artifact(artifact_id)
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _contract_response("/api/runtime/storybook-reel/artifacts/{artifact_id}", "GET", result)


@router.get("/artifacts/{artifact_id}/download.zip", response_model=None)
def storybook_reel_download(artifact_id: str) -> Any:
    try:
        path = STORYBOOK_REEL_RUNTIME.artifact_path(artifact_id, "zip")
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(path, media_type="application/zip", filename="hhs-storybook-reel-package.zip", headers={"Cache-Control": "private, no-store"})


@router.get("/artifacts/{artifact_id}/video.mp4", response_model=None)
def storybook_reel_video(artifact_id: str) -> Any:
    try:
        path = STORYBOOK_REEL_RUNTIME.artifact_path(artifact_id, "video")
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FileResponse(path, media_type="video/mp4", filename="storybook-reel.mp4", headers={"Cache-Control": "private, no-store"})

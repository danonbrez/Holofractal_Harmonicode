"""Pass170 canonical audio-language public route adapter.

The route layer is deliberately thin. It owns no VM81, Hash72 mint, Hash216
persistence, semantic database, training, or cryptographic authority. The
internal adapter delegates to the inherited audio-language feedback orchestrator.
Public HTTP admission is fail-closed until Pass170 assigns the operation an
authoritative capability scope; pending capability policy never falls through
to auxiliary persistence or training execution.
"""
from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_runtime.hhs_audio_language_feedback_orchestrator_v1 import (
    run_audio_language_feedback_cycle,
)

OPERATION_ID = "public.audio_language.feedback.run"
CANONICAL_PATH = "/v1/audio-language/run"
LEGACY_ALIAS_PATH = "/api/audio-language/run"
PENDING_CAPABILITY_DETAIL = "HHS_PASS170_AUDIO_CAPABILITY_MODEL_UNRESOLVED"


class AudioLanguageRunRequest(BaseModel):
    expression: str = Field(min_length=1, max_length=131072)
    items: List[Dict[str, Any]]
    audio_manifest: Dict[str, Any]
    audio_roundtrip_receipt: Dict[str, Any] | None = None


def enforce_audio_public_admission() -> None:
    """Refuse public execution until an authoritative Pass170 scope is bound."""
    raise HTTPException(status_code=503, detail=PENDING_CAPABILITY_DETAIL)


async def execute_audio_language_feedback_request(
    req: AudioLanguageRunRequest,
) -> Dict[str, Any]:
    """Internal/governed adapter; public routes must pass admission first."""
    result = run_audio_language_feedback_cycle(
        expression=req.expression,
        display_items=req.items,
        audio_manifest=req.audio_manifest,
        audio_roundtrip_receipt=req.audio_roundtrip_receipt,
    )
    payload = result.to_dict()
    payload["operation_id"] = OPERATION_ID
    payload["canonical_path"] = CANONICAL_PATH
    payload["compatibility_alias"] = LEGACY_ALIAS_PATH
    payload["vm81_commit_required"] = False
    payload["auxiliary_persistence"] = True
    return payload


def build_pass170_audio_language_router() -> APIRouter:
    router = APIRouter(tags=["pass170-audio-language"])

    @router.post(LEGACY_ALIAS_PATH, deprecated=True)
    @router.post(CANONICAL_PATH)
    async def audio_language_feedback_run(req: AudioLanguageRunRequest) -> Dict[str, Any]:
        enforce_audio_public_admission()
        return await execute_audio_language_feedback_request(req)

    return router


__all__ = [
    "AudioLanguageRunRequest",
    "CANONICAL_PATH",
    "LEGACY_ALIAS_PATH",
    "OPERATION_ID",
    "PENDING_CAPABILITY_DETAIL",
    "build_pass170_audio_language_router",
    "enforce_audio_public_admission",
    "execute_audio_language_feedback_request",
]

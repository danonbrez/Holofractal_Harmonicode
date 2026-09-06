"""Pass170 canonical audio-language public route adapter.

The local/internal adapter owns no VM81, Hash72 mint, Hash216 persistence,
semantic database, training, or cryptographic authority. Pass219 I177 binds
the public HTTP surface to a Pass170-owned capability scope while reusing the
inherited Pass190 signed-token verifier and secret. The audio ECC and internal
post-quantum-oriented security roles remain internal constraint signals and do
not become public cryptographic capabilities.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from hhs_runtime.hhs_audio_language_feedback_orchestrator_v1 import (
    run_audio_language_feedback_cycle,
)
from hhs_runtime.pass190.completion import verify_capability_token

OPERATION_ID = "public.audio_language.feedback.run"
CANONICAL_PATH = "/v1/audio-language/run"
LEGACY_ALIAS_PATH = "/api/audio-language/run"
AUDIO_CAPABILITY_SCOPE = "pass170.audio_language.feedback"
AUTHORIZATION_SCHEME = "HHS-Capability"
CAPABILITY_SECRET_ENV = "HHS_PASS190_CAPABILITY_SECRET"


class AudioLanguageRunRequest(BaseModel):
    expression: str = Field(min_length=1, max_length=131072)
    items: List[Dict[str, Any]]
    audio_manifest: Dict[str, Any]
    audio_roundtrip_receipt: Dict[str, Any] | None = None


def _capability_token_from_header(value: str | None) -> str:
    if value is None:
        raise HTTPException(status_code=401, detail="HHS_PASS170_AUDIO_CAPABILITY_REQUIRED")
    prefix = AUTHORIZATION_SCHEME + " "
    if not value.startswith(prefix):
        raise HTTPException(status_code=401, detail="HHS_PASS170_AUDIO_AUTHORIZATION_SCHEME_INVALID")
    token = value[len(prefix) :].strip()
    if not token:
        raise HTTPException(status_code=401, detail="HHS_PASS170_AUDIO_CAPABILITY_REQUIRED")
    return token


def enforce_audio_public_admission(
    authorization: str | None,
    *,
    capability_secret: str | bytes | None = None,
) -> Dict[str, Any]:
    """Require the explicit Pass170 audio scope using inherited Pass190 tokens."""
    secret = capability_secret or os.environ.get(CAPABILITY_SECRET_ENV)
    if not secret:
        raise HTTPException(status_code=503, detail="HHS_PASS170_AUDIO_CAPABILITY_SECRET_REQUIRED")
    token = _capability_token_from_header(authorization)
    try:
        principal = verify_capability_token(
            token,
            secret,
            required_scope=AUDIO_CAPABILITY_SCOPE,
        )
    except Exception as exc:
        message = str(exc)
        if "scope is not authorized" in message:
            raise HTTPException(status_code=403, detail="HHS_PASS170_AUDIO_CAPABILITY_SCOPE_REQUIRED") from exc
        raise HTTPException(status_code=401, detail="HHS_PASS170_AUDIO_CAPABILITY_INVALID") from exc
    return {
        "schema": "HHS_PASS170_AUDIO_CAPABILITY_ADMISSION_V1",
        "principal": principal.principal,
        "required_scope": AUDIO_CAPABILITY_SCOPE,
        "authorized_scopes": sorted(principal.scopes),
        "token_hash72": principal.token_hash72,
        "new_token_authority": False,
        "pass190_verifier_reused": True,
    }


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
    async def audio_language_feedback_run(
        req: AudioLanguageRunRequest,
        authorization: str | None = Header(default=None),
    ) -> Dict[str, Any]:
        admission = enforce_audio_public_admission(authorization)
        payload = await execute_audio_language_feedback_request(req)
        payload["capability_admission"] = admission
        return payload

    return router


__all__ = [
    "AUDIO_CAPABILITY_SCOPE",
    "AUTHORIZATION_SCHEME",
    "AudioLanguageRunRequest",
    "CANONICAL_PATH",
    "CAPABILITY_SECRET_ENV",
    "LEGACY_ALIAS_PATH",
    "OPERATION_ID",
    "build_pass170_audio_language_router",
    "enforce_audio_public_admission",
    "execute_audio_language_feedback_request",
]

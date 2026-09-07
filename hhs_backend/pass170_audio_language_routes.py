"""Pass170 canonical audio-language public route adapter.

The local/internal adapter owns no VM81, Hash72 mint, Hash216 persistence,
semantic database, training, or cryptographic authority. Pass219 I177 binds
the public surface to a Pass170-owned capability scope while reusing the
inherited Pass190 signed-token verifier and secret. Pass219 I179 adds the exact
native admissibility membrane and non-reexecuting auxiliary receipt replay.
Audio ECC and the internal post-quantum-oriented security signal remain
internal constraints; neither becomes a public cryptographic capability.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Mapping

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from hhs_runtime.hhs_audio_language_feedback_orchestrator_v1 import (
    AudioLanguageFeedbackReplayError,
    DEFAULT_SEMANTIC_DB_PATH,
    replay_audio_language_feedback_receipt,
    run_audio_language_feedback_cycle,
)
from hhs_runtime.pass190.completion import verify_capability_token
from hhs_runtime.pass219.pass170_audio_native_abi_i179 import (
    Pass170AudioNativeABIError,
    admit_audio_native_replay,
    admit_audio_native_transport,
)

OPERATION_ID = "public.audio_language.feedback.run"
CANONICAL_PATH = "/v1/audio-language/run"
LEGACY_ALIAS_PATH = "/api/audio-language/run"
REPLAY_PATH = "/v1/audio-language/replay/{receipt_hash72}"
AUDIO_CAPABILITY_SCOPE = "pass170.audio_language.feedback"
AUTHORIZATION_SCHEME = "HHS-Capability"
CAPABILITY_SECRET_ENV = "HHS_PASS190_CAPABILITY_SECRET"
SEMANTIC_DB_ENV = "HHS_PASS170_AUDIO_SEMANTIC_DB"


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


def _request_mapping(req: AudioLanguageRunRequest) -> Dict[str, Any]:
    if hasattr(req, "model_dump"):
        return dict(req.model_dump())
    return dict(req.dict())


def _semantic_db_path() -> str:
    return os.environ.get(SEMANTIC_DB_ENV, DEFAULT_SEMANTIC_DB_PATH)


async def execute_audio_language_feedback_request(
    req: AudioLanguageRunRequest,
    *,
    transport_security_binding: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Internal/governed adapter; public routes must pass admission first."""
    result = run_audio_language_feedback_cycle(
        expression=req.expression,
        display_items=req.items,
        audio_manifest=req.audio_manifest,
        audio_roundtrip_receipt=req.audio_roundtrip_receipt,
        semantic_db_path=_semantic_db_path(),
        transport_security_binding=transport_security_binding,
    )
    payload = result.to_dict()
    payload["operation_id"] = OPERATION_ID
    payload["canonical_path"] = CANONICAL_PATH
    payload["compatibility_alias"] = LEGACY_ALIAS_PATH
    payload["replay_path"] = REPLAY_PATH.replace("{receipt_hash72}", payload["receipt_hash72"])
    payload["vm81_commit_required"] = False
    payload["auxiliary_persistence"] = True
    return payload


async def execute_audio_language_public_request(
    req: AudioLanguageRunRequest,
    *,
    capability_admission: Mapping[str, Any],
) -> Dict[str, Any]:
    """Execute public audio only after signed capability + exact native admission."""
    try:
        native_binding = admit_audio_native_transport(
            capability_admission,
            _request_mapping(req),
        )
    except Pass170AudioNativeABIError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"HHS_PASS170_AUDIO_NATIVE_ABI_REQUIRED:{exc}",
        ) from exc
    payload = await execute_audio_language_feedback_request(
        req,
        transport_security_binding=native_binding,
    )
    payload["capability_admission"] = dict(capability_admission)
    payload["native_security_binding"] = native_binding
    return payload


def execute_audio_language_public_replay(
    receipt_hash72: str,
    *,
    capability_admission: Mapping[str, Any],
) -> Dict[str, Any]:
    """Replay one stored auxiliary receipt without re-running the operation."""
    try:
        replay = replay_audio_language_feedback_receipt(
            receipt_hash72,
            semantic_db_path=_semantic_db_path(),
        )
    except AudioLanguageFeedbackReplayError as exc:
        message = str(exc)
        status = 404 if "NOT_FOUND" in message else 409
        raise HTTPException(status_code=status, detail=message) from exc
    try:
        native_replay = admit_audio_native_replay(
            capability_admission,
            receipt_hash72=receipt_hash72,
            original_security_binding=replay.get("security_binding") or {},
        )
    except Pass170AudioNativeABIError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"HHS_PASS170_AUDIO_NATIVE_REPLAY_ABI_REQUIRED:{exc}",
        ) from exc
    return {
        **replay,
        "operation_id": OPERATION_ID,
        "capability_admission": dict(capability_admission),
        "native_replay_binding": native_replay,
        "canonical_path": CANONICAL_PATH,
        "replay_path": REPLAY_PATH.replace("{receipt_hash72}", receipt_hash72),
    }


def build_pass170_audio_language_router() -> APIRouter:
    router = APIRouter(tags=["pass170-audio-language"])

    @router.post(LEGACY_ALIAS_PATH, deprecated=True)
    @router.post(CANONICAL_PATH)
    async def audio_language_feedback_run(
        req: AudioLanguageRunRequest,
        authorization: str | None = Header(default=None),
    ) -> Dict[str, Any]:
        admission = enforce_audio_public_admission(authorization)
        return await execute_audio_language_public_request(
            req,
            capability_admission=admission,
        )

    @router.get(REPLAY_PATH)
    async def audio_language_feedback_replay(
        receipt_hash72: str,
        authorization: str | None = Header(default=None),
    ) -> Dict[str, Any]:
        admission = enforce_audio_public_admission(authorization)
        return execute_audio_language_public_replay(
            receipt_hash72,
            capability_admission=admission,
        )

    return router


__all__ = [
    "AUDIO_CAPABILITY_SCOPE",
    "AUTHORIZATION_SCHEME",
    "AudioLanguageRunRequest",
    "CANONICAL_PATH",
    "CAPABILITY_SECRET_ENV",
    "LEGACY_ALIAS_PATH",
    "OPERATION_ID",
    "REPLAY_PATH",
    "SEMANTIC_DB_ENV",
    "build_pass170_audio_language_router",
    "enforce_audio_public_admission",
    "execute_audio_language_feedback_request",
    "execute_audio_language_public_replay",
    "execute_audio_language_public_request",
]

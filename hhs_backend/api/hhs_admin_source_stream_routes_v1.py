"""Fail-closed HTTP transport for private SQL staging; no new auth authority.

Uses the inherited Pass190/Ubuntu-ApplicationVM signed capability verifier,
or a verified in-process request principal. No public owner headers or JSON
fields grant authorization; admission and source staging remain distinct. Lane 5 canonical admission is separate.
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from hhs_backend.runtime.hhs_admin_sql_stream_staging_v1 import AdminStreamStaging, StagingError

router = APIRouter(prefix="/api/runtime/admin-source-stream", tags=["admin-source-stream"])
_STAGING: AdminStreamStaging | None = None


class BeginBody(BaseModel):
    source_name: str = Field(min_length=1)


class FinalizeBody(BaseModel):
    expected_sha256: str | None = Field(default=None, min_length=64, max_length=64)


ADMIN_UPLOAD_SCOPE = "admin.source.upload"


def _signed_authority():
    """Reuse the inherited Pass190/Ubuntu ApplicationVM signed capability authority."""
    from hhs_runtime.pass220.application_vm_control_plane import ApplicationVMControlPlane
    return ApplicationVMControlPlane.from_environment()


def _principal(request: Request) -> str:
    # Only an in-process trusted middleware or a cryptographically verified
    # inherited HHS-Capability header can provide source-upload authority.
    principal = request.scope.get("hhs_authenticated_principal")
    if isinstance(principal, dict) and principal.get("admin_source_upload") is True:
        owner = principal.get("subject")
        if isinstance(owner, str) and owner.strip():
            return owner
        raise HTTPException(status_code=403, detail="HHS_ADMIN_STREAM_TRUSTED_OWNER_REQUIRED")

    authorization = request.headers.get("authorization")
    if authorization is None:
        raise HTTPException(status_code=403, detail="HHS_ADMIN_STREAM_TRUSTED_PRINCIPAL_REQUIRED")
    try:
        identity = _signed_authority().authenticate_header(authorization)
    except Exception as exc:
        # The existing control plane owns signature, time and schema verification.
        # Fail closed on a missing native security configuration or malformed token.
        from hhs_runtime.pass220.application_vm_control_plane import ApplicationVMError
        if isinstance(exc, ApplicationVMError):
            code = str(exc)
            status = 503 if "SECURITY_NOT_CONFIGURED" in code else 401
            raise HTTPException(status_code=status, detail="HHS_ADMIN_STREAM_CAPABILITY_REJECTED") from exc
        raise HTTPException(status_code=503, detail="HHS_ADMIN_STREAM_AUTHORITY_UNAVAILABLE") from exc
    scopes = identity.get("scopes")
    owner = identity.get("principal")
    if not isinstance(scopes, list) or ADMIN_UPLOAD_SCOPE not in scopes:
        raise HTTPException(status_code=403, detail="HHS_ADMIN_STREAM_CAPABILITY_SCOPE_REQUIRED")
    if not isinstance(owner, str) or not owner.strip():
        raise HTTPException(status_code=403, detail="HHS_ADMIN_STREAM_CAPABILITY_PRINCIPAL_INVALID")
    return owner


def _staging() -> AdminStreamStaging:
    global _STAGING
    if _STAGING is None:
        _STAGING = AdminStreamStaging(
            Path(os.environ.get("HHS_ADMIN_SQL_STAGING_ROOT", "data/private-admin-staging"))
        )
    return _STAGING


def _call(fn, *args):
    try:
        return fn(*args)
    except StagingError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/uploads")
def create_upload(body: BeginBody, request: Request):
    return _call(_staging().create, _principal(request), body.source_name)


@router.get("/uploads/{upload_id}")
def read_upload(upload_id: str, request: Request):
    return _call(_staging().status, upload_id, _principal(request))


@router.patch("/uploads/{upload_id}")
async def append_upload(upload_id: str, request: Request, offset: int):
    owner = _principal(request)
    # Chunk boundaries are transport details, not a limit on overall source.
    # No request.body() or multipart whole-file buffering is used.
    current = _call(_staging().status, upload_id, owner)
    if current["received_bytes"] != offset:
        raise HTTPException(status_code=409, detail="OFFSET_CONFLICT")
    read_offset = offset
    async for incoming in request.stream():
        for begin in range(0, len(incoming), 64 * 1024):
            part = incoming[begin:begin + 64 * 1024]
            if not part:
                continue
            current = await asyncio.to_thread(_call, _staging().append, upload_id, owner, read_offset, bytes(part))
            read_offset += len(part)
    return current


@router.post("/uploads/{upload_id}/finalize")
def finish_upload(upload_id: str, body: FinalizeBody, request: Request):
    owner = _principal(request)
    return _call(_staging().finalize, upload_id, owner, body.expected_sha256)

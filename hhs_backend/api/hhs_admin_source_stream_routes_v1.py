"""Fail-closed HTTP transport for private SQL staging; no new auth authority.

Uses the inherited Pass190/Ubuntu-ApplicationVM signed capability verifier,
or a verified in-process request principal. No public owner headers or JSON
fields grant authorization; admission and source staging remain distinct. Lane 5 canonical admission is separate.
"""
from __future__ import annotations

import asyncio
import os
from hashlib import sha256
from fastapi.responses import StreamingResponse
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from hhs_backend.runtime.hhs_admin_sql_stream_staging_v1 import AdminStreamStaging, StagingError
from hhs_backend.runtime.hhs_admin_sql_lane5_continuation_v1 import continue_staged_to_lane5, NativeContinuationError
from hhs_backend.runtime.hhs_admin_sql_vm81_admission_preflight_v1 import inspect_staged_admission_prerequisites
from hhs_backend.runtime.hhs_admin_sql_typed_vm81_source_v1 import inspect_exact_typed_vm81_source

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
    # Let the existing staging adapter handle exact-byte committed-chunk retries.
    # A duplicate transport request is not a new admission decision.
    current = None
    read_offset = offset
    async for incoming in request.stream():
        for begin in range(0, len(incoming), 64 * 1024):
            part = incoming[begin:begin + 64 * 1024]
            if not part:
                continue
            current = await asyncio.to_thread(_call, _staging().append, upload_id, owner, read_offset, bytes(part))
            read_offset += len(part)
    return current if current is not None else await asyncio.to_thread(
        _call, _staging().status, upload_id, owner
    )


@router.post("/uploads/{upload_id}/finalize")
def finish_upload(upload_id: str, body: FinalizeBody, request: Request):
    owner = _principal(request)
    return _call(_staging().finalize, upload_id, owner, body.expected_sha256)


@router.post("/uploads/{upload_id}/candidate")
def native_lane5_candidate(upload_id: str, request: Request):
    """Produce an owner-scoped native candidate, never a canonical admission.

    Requires the same signed administrator capability as SQL staging. The
    existing Pass219 Lane5 bridge performs source digest and workload checks.
    A candidate is not promoted into authoritative Hash216/RAG by this route.
    """
    owner = _principal(request)
    try:
        return continue_staged_to_lane5(_staging(), upload_id, owner)
    except (StagingError, NativeContinuationError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/uploads/{upload_id}/admission-preflight")
def signed_vm81_admission_preflight(upload_id: str, request: Request):
    """Read-only native admission prerequisites; never create a signed receipt."""
    owner = _principal(request)
    try:
        return inspect_staged_admission_prerequisites(_staging(), upload_id, owner)
    except (StagingError, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except (RuntimeError, OSError) as exc:
        raise HTTPException(status_code=503, detail="SIGNED_VM81_PREFLIGHT_NATIVE_UNAVAILABLE") from exc


@router.get("/uploads/{upload_id}/source")
def read_exact_staged_source(upload_id: str, request: Request):
    """Return verified original bytes, with no canonical knowledge promotion.

    Uses one open no-follow file descriptor for both verification and streaming
    to avoid a path swap between digest verification and response construction.
    This is owner-scoped source egress, NOT admitted RAG retrieval.
    """
    owner = _principal(request)
    stage = _staging()
    record = _call(stage.status, upload_id, owner)
    if record["state"] != "STAGED":
        raise HTTPException(status_code=409, detail="SOURCE_NOT_STAGED")
    source = _call(stage.read_staged, upload_id, owner)
    descriptor = None
    try:
        descriptor = os.open(source, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        stream = os.fdopen(descriptor, "rb")
        descriptor = None
        info = os.fstat(stream.fileno())
        if not os.path.isfile(source) or info.st_size != record["received_bytes"]:
            raise ValueError("SOURCE_LENGTH_DRIFT")
        digest = sha256()
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
        if digest.hexdigest() != record["source_sha256"]:
            raise ValueError("SOURCE_DIGEST_DRIFT")
        stream.seek(0)
    except (OSError, ValueError) as exc:
        if descriptor is not None:
            os.close(descriptor)
        if "stream" in locals():
            stream.close()
        raise HTTPException(status_code=409, detail="STAGED_SOURCE_VERIFICATION_FAILED") from exc

    def content():
        try:
            while True:
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    break
                yield chunk
        finally:
            stream.close()

    return StreamingResponse(content(), media_type="application/octet-stream", headers={
        "X-HHS-Source-SHA256": record["source_sha256"],
        "X-HHS-Canonical-Hash216-Admitted": "false",
        "Content-Length": str(record["received_bytes"]),
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
    })


@router.get("/uploads/{upload_id}/typed-vm81")
def inspect_existing_typed_vm81_source(upload_id: str, request: Request):
    """Inspect inherited exact frame encoding; never grant canonical authority."""
    owner = _principal(request)
    try:
        return inspect_exact_typed_vm81_source(_staging(), upload_id, owner)
    except (StagingError, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

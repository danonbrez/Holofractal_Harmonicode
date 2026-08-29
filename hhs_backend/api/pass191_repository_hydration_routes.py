"""Pass 191 universal repository hydration OpenAPI and WebSocket surface."""
from __future__ import annotations

from base64 import urlsafe_b64decode, urlsafe_b64encode
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from hhs_runtime.pass191.repository_hydration import (
    HydrationBounds,
    Pass191Error,
    RepositoryHydrationRuntime,
)

router = APIRouter(prefix="/v1/hydration", tags=["pass191-repository-hydration"])
_RUNTIME: Optional[RepositoryHydrationRuntime] = None


def _runtime() -> RepositoryHydrationRuntime:
    global _RUNTIME
    if _RUNTIME is None:
        _RUNTIME = RepositoryHydrationRuntime()
    return _RUNTIME


def _set_runtime_for_tests(runtime: Optional[RepositoryHydrationRuntime]) -> None:
    global _RUNTIME
    _RUNTIME = runtime


def _call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Pass191Error as exc:
        code = 404 if exc.classification.endswith("_NOT_FOUND") else 409
        raise HTTPException(status_code=code, detail=exc.classification) from exc
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _encode_ref(identity: str) -> str:
    return urlsafe_b64encode(identity.encode("utf-8")).decode("ascii").rstrip("=")


def _decode_ref(reference: str) -> str:
    padding = "=" * ((4 - len(reference) % 4) % 4)
    try:
        return urlsafe_b64decode((reference + padding).encode("ascii")).decode("utf-8")
    except Exception as exc:
        raise HTTPException(status_code=400, detail="HHS_P191_OBJECT_REFERENCE_INVALID") from exc


class BoundsBody(BaseModel):
    max_files: int = Field(default=100_000, ge=1)
    max_bytes: int = Field(default=4 * 1024 * 1024 * 1024, ge=1)
    max_single_object_bytes: int = Field(default=256 * 1024 * 1024, ge=1)
    max_dependency_edges: int = Field(default=1_000_000, ge=1)
    max_manifest_bytes: int = Field(default=64 * 1024 * 1024, ge=1)
    max_stage_duration_ns: int = Field(default=300_000_000_000, ge=1)
    max_total_job_duration_ns: int = Field(default=1_800_000_000_000, ge=1)
    max_replay_attempts: int = Field(default=3, ge=1)


class PreviewBody(BaseModel):
    commit: str = "HEAD"
    since_commit: Optional[str] = None
    bounds: Optional[BoundsBody] = None
    include_objects: bool = False


class AuthorityBody(BaseModel):
    authority_execution: Dict[str, Any]


class CreateJobBody(AuthorityBody):
    commit: str = "HEAD"
    since_commit: Optional[str] = None
    bounds: Optional[BoundsBody] = None


@router.get("/status")
def status() -> Dict[str, Any]:
    return _runtime().status()


@router.post("/preview")
def preview(body: PreviewBody) -> Dict[str, Any]:
    manifest = _call(
        _runtime().preview,
        commit=body.commit,
        since_commit=body.since_commit,
        bounds=body.bounds.model_dump() if body.bounds else None,
    )
    if body.include_objects:
        return manifest
    return _runtime().compact(manifest)


@router.get("/jobs")
def list_jobs() -> List[Dict[str, Any]]:
    return [
        {
            "job_id": job["job_id"],
            "stage": job["stage"],
            "failure_reason": job["failure_reason"],
            "recovery_action": job["recovery_action"],
            "receipt_links": job["receipt_links"],
        }
        for job in _runtime().list_jobs()
    ]


@router.post("/jobs")
def create_job(body: CreateJobBody) -> Dict[str, Any]:
    request = {
        "commit": body.commit,
        "since_commit": body.since_commit,
        "bounds": body.bounds.model_dump() if body.bounds else {},
    }
    job = _call(
        _runtime().create_job,
        request,
        authority_execution=body.authority_execution,
    )
    return {
        "job_id": job["job_id"],
        "stage": job["stage"],
        "job_hash216_identity": job["job_hash216_identity"],
        "recovery_action": job["recovery_action"],
        "receipt_links": job["receipt_links"],
    }


@router.get("/jobs/{job_id}")
def get_job(job_id: str) -> Dict[str, Any]:
    job = _call(_runtime().get_job, job_id)
    result = {
        key: job[key]
        for key in (
            "job_id",
            "job_hash216_identity",
            "request",
            "stage",
            "history",
            "failure_reason",
            "recovery_action",
            "receipt_links",
            "artifact_links",
        )
    }
    if job.get("manifest"):
        result["manifest"] = _runtime().compact(job["manifest"])
    return result


@router.post("/jobs/{job_id}/resume")
def resume_job(job_id: str, body: AuthorityBody) -> Dict[str, Any]:
    job = _call(
        _runtime().resume_job,
        job_id,
        authority_execution=body.authority_execution,
    )
    result = get_job(job_id)
    return result


@router.post("/jobs/{job_id}/cancel")
def cancel_job(job_id: str, body: AuthorityBody) -> Dict[str, Any]:
    _call(
        _runtime().cancel_job,
        job_id,
        authority_execution=body.authority_execution,
    )
    return get_job(job_id)


@router.post("/jobs/{job_id}/verify")
def verify_job(job_id: str) -> Dict[str, Any]:
    return _call(_runtime().verify_job, job_id)


@router.post("/jobs/{job_id}/replay")
def replay_job(job_id: str) -> Dict[str, Any]:
    return _call(_runtime().replay_job, job_id)


@router.get("/jobs/{job_id}/report", response_class=PlainTextResponse)
def report(job_id: str) -> str:
    return _call(_runtime().report, job_id)


@router.get("/objects/{object_ref}")
def object_record(object_ref: str) -> Dict[str, Any]:
    identity = _decode_ref(object_ref)
    result = _call(_runtime().object_by_identity, identity)
    return {**result, "object_id_ref": _encode_ref(identity)}


@router.get("/functions/{operation_id:path}")
def function_record(operation_id: str) -> Dict[str, Any]:
    return _call(_runtime().function_by_id, operation_id)


@router.get("/lineage/passes")
def lineage() -> Dict[str, Any]:
    return _call(_runtime().lineage)


@router.get("/invariants")
def invariants() -> Dict[str, Any]:
    return _call(_runtime().invariants)


@router.get("/surfaces")
def surfaces() -> Dict[str, Any]:
    return _runtime().surfaces()


@router.get("/assistant-tools")
def assistant_tools() -> Dict[str, Any]:
    return _runtime().assistant_tools()


@router.get("/receipts")
def receipts() -> List[Dict[str, Any]]:
    return _runtime().receipts()


@router.get("/receipts/{receipt_hash72}")
def receipt(receipt_hash72: str) -> Dict[str, Any]:
    return _call(_runtime().receipt, receipt_hash72)


@router.get("/replay/receipts")
def replay_receipts() -> Dict[str, Any]:
    return _call(_runtime().replay_receipt_chain)


@router.websocket("/ws/{job_id}")
async def lifecycle_socket(websocket: WebSocket, job_id: str) -> None:
    await websocket.accept()
    try:
        job = _runtime().get_job(job_id)
        await websocket.send_json(
            {
                "schema": "HHS_PASS_191_HYDRATION_WEBSOCKET_EVENT_V1",
                "job_id": job_id,
                "event": "SNAPSHOT",
                "stage": job["stage"],
                "history": job["history"],
                "receipt_links": job["receipt_links"],
            }
        )
        for event in job["history"]:
            await websocket.send_json(
                {
                    "schema": "HHS_PASS_191_HYDRATION_WEBSOCKET_EVENT_V1",
                    "job_id": job_id,
                    "event": "LIFECYCLE",
                    **event,
                }
            )
        await websocket.send_json(
            {
                "schema": "HHS_PASS_191_HYDRATION_WEBSOCKET_EVENT_V1",
                "job_id": job_id,
                "event": "STREAM_CLOSED",
                "stage": job["stage"],
                "committed_state_fabricated": False,
            }
        )
    except Pass191Error as exc:
        await websocket.send_json(
            {
                "schema": "HHS_PASS_191_HYDRATION_WEBSOCKET_EVENT_V1",
                "job_id": job_id,
                "event": "ERROR",
                "classification": exc.classification,
            }
        )
    except WebSocketDisconnect:
        return
    finally:
        try:
            await websocket.close()
        except RuntimeError:
            pass


__all__ = ["router", "_encode_ref", "_decode_ref", "_set_runtime_for_tests"]

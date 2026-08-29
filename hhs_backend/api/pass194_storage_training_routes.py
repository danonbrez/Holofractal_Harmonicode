"""Bounded FastAPI surface for Pass 194 storage/training lineage."""
from __future__ import annotations

from base64 import b64decode
import os
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_backend.runtime.hhs_pass194_multimodal_storage_training_v1 import (
    Pass194Error,
    Pass194Runtime,
)

router = APIRouter(prefix="/api/runtime/storage-training", tags=["pass194-storage-training"])
_RUNTIME: Pass194Runtime | None = None
MAX_UPLOAD_BYTES = 16 * 1024 * 1024


def _runtime() -> Pass194Runtime:
    global _RUNTIME
    if _RUNTIME is None:
        root = Path(os.environ.get("HHS_PASS194_STATE_ROOT", "data/pass194"))
        _RUNTIME = Pass194Runtime(root)
    return _RUNTIME


def _call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Pass194Error as exc:
        raise HTTPException(status_code=409, detail=exc.classification) from exc
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


class AuthorityBody(BaseModel):
    authority_execution: Dict[str, Any]


class WorkspaceBody(AuthorityBody):
    workspace_id: str = Field(min_length=1, max_length=256)
    owner_id: str = Field(min_length=1, max_length=256)


class FileBody(AuthorityBody):
    workspace_id: str = Field(min_length=1, max_length=256)
    owner_id: str = Field(min_length=1, max_length=256)
    logical_path: str = Field(min_length=1, max_length=4096)
    data_b64: str
    modality: str = Field(default="BINARY", min_length=1, max_length=64)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConsentBody(AuthorityBody):
    file_version_id: str
    training_allowed: bool
    sharing_allowed: bool = False
    public_allowed: bool = False
    license_id: str | None = None


class VectorBody(AuthorityBody):
    file_version_id: str
    projection_frame_b64: str
    model_id: str = Field(min_length=1, max_length=512)
    logical_step: int = Field(ge=0)


class SnapshotBody(AuthorityBody):
    workspace_id: str


class DatasetBody(AuthorityBody):
    snapshot_id: str


class TrainingRunBody(AuthorityBody):
    dataset_id: str
    run_kind: str
    model_base_id: str = Field(min_length=1, max_length=512)


class CheckpointBody(AuthorityBody):
    run_id: str
    artifact_sha256: str
    metrics: Dict[str, Any] = Field(default_factory=dict)


class DeleteBody(AuthorityBody):
    reason: str = Field(min_length=1, max_length=1024)


@router.get("/status")
def status() -> Dict[str, Any]:
    return _runtime().status()


@router.post("/workspaces")
def create_workspace(body: WorkspaceBody) -> Dict[str, Any]:
    return _call(
        _runtime().ensure_workspace,
        body.workspace_id,
        body.owner_id,
        authority_execution=body.authority_execution,
    )


@router.post("/files")
def ingest_file(body: FileBody) -> Dict[str, Any]:
    try:
        raw = b64decode(body.data_b64, validate=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="HHS_P194_BASE64_INVALID") from exc
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="HHS_P194_UPLOAD_LIMIT")
    return _call(
        _runtime().ingest_bytes,
        body.workspace_id,
        body.owner_id,
        body.logical_path,
        raw,
        modality=body.modality,
        metadata=body.metadata,
        authority_execution=body.authority_execution,
    )


@router.post("/consent")
def set_consent(body: ConsentBody) -> Dict[str, Any]:
    return _call(
        _runtime().set_consent,
        body.file_version_id,
        training_allowed=body.training_allowed,
        sharing_allowed=body.sharing_allowed,
        public_allowed=body.public_allowed,
        license_id=body.license_id,
        authority_execution=body.authority_execution,
    )


@router.post("/vectors")
def store_vector(body: VectorBody) -> Dict[str, Any]:
    try:
        frame = b64decode(body.projection_frame_b64, validate=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="HHS_P194_BASE64_INVALID") from exc
    return _call(
        _runtime().store_vector_projection,
        body.file_version_id,
        frame,
        model_id=body.model_id,
        logical_step=body.logical_step,
        authority_execution=body.authority_execution,
    )


@router.post("/snapshots")
def create_snapshot(body: SnapshotBody) -> Dict[str, Any]:
    return _call(
        _runtime().create_snapshot,
        body.workspace_id,
        authority_execution=body.authority_execution,
    )


@router.post("/datasets")
def release_dataset(body: DatasetBody) -> Dict[str, Any]:
    return _call(
        _runtime().release_dataset,
        body.snapshot_id,
        authority_execution=body.authority_execution,
    )


@router.post("/training-runs")
def begin_training_run(body: TrainingRunBody) -> Dict[str, Any]:
    return _call(
        _runtime().begin_training_run,
        body.dataset_id,
        run_kind=body.run_kind,
        model_base_id=body.model_base_id,
        authority_execution=body.authority_execution,
    )


@router.post("/checkpoints")
def record_checkpoint(body: CheckpointBody) -> Dict[str, Any]:
    return _call(
        _runtime().record_checkpoint,
        body.run_id,
        artifact_sha256=body.artifact_sha256,
        metrics=body.metrics,
        authority_execution=body.authority_execution,
    )


@router.post("/files/{file_id}/delete")
def delete_file(file_id: str, body: DeleteBody) -> Dict[str, Any]:
    return _call(
        _runtime().delete_file,
        file_id,
        reason=body.reason,
        authority_execution=body.authority_execution,
    )


@router.get("/replay")
def replay() -> Dict[str, Any]:
    return _call(_runtime().replay)

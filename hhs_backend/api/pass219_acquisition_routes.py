"""Pass 219 acquisition/replay application-service routes."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import os

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from hhs_backend.pass219_acquisition_job_service import (
    AcquisitionJobService,
    AcquisitionJobServiceError,
)

router = APIRouter(
    prefix="/api/v1/pass174/acquisition",
    tags=["pass174", "pass219", "acquisition", "replay", "multimodal"],
)
_SERVICE: AcquisitionJobService | None = None
_SERVICE_ERROR: Exception | None = None


def _repository_root() -> Path:
    configured = os.environ.get("HHS_REPOSITORY_ROOT")
    return Path(configured).resolve() if configured else Path(__file__).resolve().parents[2]


def _state_root() -> Path:
    configured = os.environ.get("HHS_PASS219_ACQUISITION_STATE_DIR")
    if configured:
        return Path(configured).resolve()
    pass174 = os.environ.get("HHS_PASS174_STATE_DIR")
    base = Path(pass174).resolve() if pass174 else _repository_root() / ".hhs" / "pass174"
    return base / "pass219_acquisition"


def get_acquisition_service() -> AcquisitionJobService:
    global _SERVICE, _SERVICE_ERROR
    if _SERVICE is None and _SERVICE_ERROR is None:
        try:
            _SERVICE = AcquisitionJobService(_state_root())
        except Exception as exc:  # keep web service available while candidate service is closed
            _SERVICE_ERROR = exc
    if _SERVICE is None:
        raise HTTPException(status_code=503, detail={
            "schema": "HHS-P219-ACQUISITION-SERVICE-FAILURE-V1",
            "classification": str(_SERVICE_ERROR) or type(_SERVICE_ERROR).__name__,
            "candidate_only": True,
            "canonical_authority_minted": False,
        })
    return _SERVICE


def _raise(exc: Exception) -> None:
    classification = str(exc) or type(exc).__name__
    status = 404 if classification == "P219_AJS_JOB_NOT_FOUND" else 409 if "REPLAY" in classification else 422
    raise HTTPException(status_code=status, detail={
        "schema": "HHS-P219-ACQUISITION-REJECTION-V1",
        "classification": classification,
        "candidate_only": True,
        "canonical_authority_minted": False,
    }) from exc


class AcquisitionJobRequest(BaseModel):
    projector_id: str = "SOURCE_ONLY_V1"
    source: Dict[str, Any]
    projection_evidence: List[Dict[str, Any]] = Field(default_factory=list)


def _payload(model: BaseModel) -> dict[str, Any]:
    return model.model_dump() if hasattr(model, "model_dump") else model.dict()


@router.get("/status")
def acquisition_status() -> Dict[str, Any]:
    service = get_acquisition_service()
    history = service.list(10)
    return {
        "schema": "HHS-P219-ACQUISITION-SERVICE-STATUS-V1",
        "classification": "HHS_P219_ACQUISITION_SERVICE_READY",
        "state_root": str(service.root),
        "recent_job_count": history["count"],
        "projectors": service.projectors()["projectors"],
        "live_network_transport": True,
        "persistent_replay_bundles": True,
        "candidate_only": True,
        "canonical_authority_minted": False,
    }


@router.get("/projectors")
def projectors() -> Dict[str, Any]:
    return get_acquisition_service().projectors()


@router.post("/jobs")
def create_job(request: AcquisitionJobRequest) -> Dict[str, Any]:
    try:
        return get_acquisition_service().submit(_payload(request))
    except (AcquisitionJobServiceError, ValueError, TypeError) as exc:
        _raise(exc)


@router.get("/jobs")
def list_jobs(limit: int = Query(default=25, ge=1, le=200)) -> Dict[str, Any]:
    return get_acquisition_service().list(limit)


@router.get("/jobs/{job_id}")
def get_job(job_id: str) -> Dict[str, Any]:
    try:
        return get_acquisition_service().get(job_id)
    except AcquisitionJobServiceError as exc:
        _raise(exc)


@router.get("/jobs/{job_id}/receipt")
def get_job_receipt(job_id: str) -> Dict[str, Any]:
    try:
        return get_acquisition_service().receipt(job_id)
    except AcquisitionJobServiceError as exc:
        _raise(exc)


@router.post("/jobs/{job_id}/replay")
def replay_job(job_id: str) -> Dict[str, Any]:
    try:
        return get_acquisition_service().replay(job_id)
    except (AcquisitionJobServiceError, ValueError) as exc:
        _raise(exc)


__all__ = ["AcquisitionJobRequest", "get_acquisition_service", "router"]

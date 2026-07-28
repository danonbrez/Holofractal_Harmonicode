"""Governed API for Pass 165 multimodal vector-store ingestion."""
from __future__ import annotations

from base64 import b64decode
import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_runtime.pass165.durability import DurableMultimodalLearningService
from hhs_runtime.pass165.ingestion import DEFAULT_MULTIMODAL_LEARNING_SERVICE, IngestionError

router = APIRouter(
    prefix="/api/runtime/multimodal-ingress",
    tags=["runtime", "vm81", "pass165", "multimodal", "vector-store"],
)
_STORAGE_DIR = os.environ.get("HHS_PASS165_STORAGE_DIR", "").strip()
SERVICE = (
    DurableMultimodalLearningService(_STORAGE_DIR)
    if _STORAGE_DIR
    else DEFAULT_MULTIMODAL_LEARNING_SERVICE
)


class IngestRequest(BaseModel):
    source_b64: str = Field(min_length=1)
    declared_media_type: Optional[str] = None
    provenance: str = Field(min_length=1, max_length=2048)
    authorization_scope: str = Field(min_length=1, max_length=512)


@router.get("/status")
def status() -> Dict[str, Any]:
    return SERVICE.status()


@router.post("/ingest")
def ingest(request: IngestRequest) -> Dict[str, Any]:
    try:
        raw = b64decode(request.source_b64, validate=True)
        return SERVICE.ingest_source(
            raw,
            declared_media_type=request.declared_media_type,
            provenance=request.provenance,
            authorization_scope=request.authorization_scope,
        )
    except IngestionError as exc:
        raise HTTPException(status_code=422, detail={"classification": exc.classification, "detail": exc.detail}) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail={"classification": "P165_MALFORMED_BASE64"}) from exc


@router.get("/invariants")
def invariants(candidate_class: Optional[str] = None) -> Dict[str, Any]:
    return {"invariants": SERVICE.query_invariants(candidate_class=candidate_class)}


@router.get("/receipts/{source_hash}")
def receipt(source_hash: str) -> Dict[str, Any]:
    try:
        return SERVICE.get_ingestion_receipt(source_hash)
    except IngestionError as exc:
        raise HTTPException(status_code=404, detail={"classification": exc.classification}) from exc


@router.post("/replay")
def replay() -> Dict[str, Any]:
    try:
        return SERVICE.replay_ingestion()
    except IngestionError as exc:
        raise HTTPException(status_code=409, detail={"classification": exc.classification}) from exc


@router.post("/recover")
def recover() -> Dict[str, Any]:
    if not isinstance(SERVICE, DurableMultimodalLearningService):
        raise HTTPException(status_code=409, detail={"classification": "P165_DURABLE_STORAGE_DISABLED"})
    try:
        return SERVICE.recover_durable_state()
    except IngestionError as exc:
        raise HTTPException(status_code=409, detail={"classification": exc.classification, "detail": exc.detail}) from exc

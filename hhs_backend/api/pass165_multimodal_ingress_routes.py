"""Governed API for Pass 165 multimodal vector-store ingestion."""
from __future__ import annotations

from base64 import b64decode, b64encode
from dataclasses import asdict
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


def snapshot_payload(source_hash: str) -> Dict[str, Any]:
    """Return the exact admitted 5,184-bit projection and Hash216 indexes.

    Pass 165 retains the canonical source and projection inside the singleton
    service. This read-only API exposes those bytes and indexes without granting
    the browser mutation authority or recomputing a substitute projection.
    """
    result = SERVICE._results.get(source_hash)  # same authority-owned service instance
    if result is None:
        raise IngestionError("P165_SNAPSHOT_NOT_FOUND")
    projection = bytes(result.projection_bytes)
    positions = list(result.ingestion_positions_hash216)
    return {
        "schema": "HHS_PASS_165_5184_BIT_SNAPSHOT_PROJECTION_V1",
        "ok": True,
        "source": result.source.summary(),
        "snapshot_bits": len(projection) * 8,
        "snapshot_bytes": len(projection),
        "vm81_cells": 81,
        "bits_per_cell": 64,
        "projection_b64": b64encode(projection).decode("ascii"),
        "projection_hash72": result.projection_hash72,
        "projection_popcount": sum(byte.bit_count() for byte in projection),
        "token_stream_root": result.token_stream_root,
        "chunk_graph_root": result.chunk_graph_root,
        "ingestion_operation_hash216": result.ingestion_operation_hash216,
        "ingestion_positions_hash216": positions,
        "hash216_lane_count": 3,
        "hash216_lane_width": 72,
        "hash216_position_count": len(positions),
        "residual_b64": b64encode(result.residual_bytes).decode("ascii"),
        "invariant_candidates": [asdict(item) for item in result.invariant_candidates],
        "frontend_mutation_authority": False,
        "canonical_projection_owner": "PASS165_SINGLETON_VM81_AUTHORITY",
    }


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


@router.get("/snapshots/{source_hash}")
def snapshot(source_hash: str) -> Dict[str, Any]:
    try:
        return snapshot_payload(source_hash)
    except IngestionError as exc:
        raise HTTPException(status_code=404, detail={"classification": exc.classification}) from exc


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

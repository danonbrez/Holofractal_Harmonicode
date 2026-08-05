"""Public Pass 210 holographic frame compression API."""
from __future__ import annotations

import threading
from collections import OrderedDict
from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from hhs_backend.runtime.hhs_pass210_holographic_frame_compression_v1 import (
    CONTRACT,
    HFCError,
    HFCFrame,
    HFCProjection,
    HolographicFrameCompressionRuntime,
    REGISTER_LEN,
    SNAPSHOT_COUNT,
    hfc_matrix,
    hfc_section,
)

API_PREFIX = "/api/runtime/holographic-frame-compression"
MAX_RETAINED_FRAMES = 64
router = APIRouter(prefix=API_PREFIX, tags=["pass210-hfc"])
_RUNTIME = HolographicFrameCompressionRuntime()
_FRAMES: "OrderedDict[str, HFCFrame]" = OrderedDict()
_LOCK = threading.RLock()


class RegisterRequest(BaseModel):
    register_hex: str = Field(min_length=REGISTER_LEN * 2, max_length=REGISTER_LEN * 2)

    @field_validator("register_hex")
    @classmethod
    def validate_hex(cls, value: str) -> str:
        try:
            raw = bytes.fromhex(value)
        except ValueError as exc:
            raise ValueError("register_hex must be hexadecimal") from exc
        if len(raw) != REGISTER_LEN:
            raise ValueError(f"register_hex must decode to {REGISTER_LEN} bytes")
        return value.lower()

    def register(self) -> bytes:
        return bytes.fromhex(self.register_hex)


class RecoverRequest(BaseModel):
    lost_index: int = Field(ge=0, lt=SNAPSHOT_COUNT)


class ViewAdmissionRequest(BaseModel):
    k: int
    c: int
    modulus: int = Field(gt=1)


class ProjectionRequest(RegisterRequest):
    modality: Literal["raw", "hash72", "hash216", "phase", "frame"]


class AgreementRequest(RegisterRequest):
    modalities: list[Literal["raw", "hash72", "hash216", "phase", "frame"]] = Field(min_length=2)


class StrictDecompressionRequest(BaseModel):
    package: dict[str, Any]


def _remember(frame: HFCFrame) -> str:
    frame_id = frame.object_hash216
    with _LOCK:
        _FRAMES[frame_id] = frame
        _FRAMES.move_to_end(frame_id)
        while len(_FRAMES) > MAX_RETAINED_FRAMES:
            _FRAMES.popitem(last=False)
    return frame_id


def _frame(frame_id: str) -> HFCFrame:
    with _LOCK:
        try:
            frame = _FRAMES[frame_id]
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="HFC_FRAME_NOT_FOUND") from exc
        _FRAMES.move_to_end(frame_id)
        return frame


def _fail(exc: HFCError) -> HTTPException:
    status = 409 if "WITNESS" in str(exc) or "NON_BIJECTIVE" in str(exc) else 422
    return HTTPException(status_code=status, detail=str(exc))


@router.get("/status")
def status() -> dict[str, Any]:
    value = _RUNTIME.status()
    value["api_prefix"] = API_PREFIX
    value["retained_frame_count"] = len(_FRAMES)
    value["contract"] = CONTRACT
    return value


@router.post("/frames/encode")
def encode(request: RegisterRequest) -> dict[str, Any]:
    try:
        frame = _RUNTIME.frame_encode(request.register())
    except HFCError as exc:
        raise _fail(exc) from exc
    frame_id = _remember(frame)
    return {
        "schema": "HHS_PASS_210_HFC_FRAME_ENCODE_RESPONSE_V1",
        "frame_id": frame_id,
        "register_hash216": frame.object_hash216,
        "receipt_hash72": frame.receipt_hash72,
        "register_alignment": frame.register.address % 64,
        "snapshot_count": SNAPSHOT_COUNT,
    }


@router.post("/frames/{frame_id}/decode")
def decode(frame_id: str) -> dict[str, Any]:
    try:
        raw = _RUNTIME.frame_decode(_frame(frame_id))
    except HFCError as exc:
        raise _fail(exc) from exc
    return {
        "schema": "HHS_PASS_210_HFC_FRAME_DECODE_RESPONSE_V1",
        "register_hex": raw.hex(),
        "receipt_head_hash72": _RUNTIME.ledger.head,
    }


@router.get("/frames/{frame_id}/snapshots/{index}")
def snapshot(frame_id: str, index: int) -> dict[str, Any]:
    try:
        raw = _RUNTIME.snapshot(_frame(frame_id), index)
        sections = hfc_section(raw)
        matrix = hfc_matrix(raw[:144])
    except HFCError as exc:
        raise _fail(exc) from exc
    return {
        "schema": "HHS_PASS_210_HFC_SNAPSHOT_RESPONSE_V1",
        "index": index,
        "snapshot_hex": raw.hex(),
        "section_lengths": [len(section) for section in sections],
        "matrix": [list(row) for row in matrix],
    }


@router.post("/frames/{frame_id}/recover")
def recover(frame_id: str, request: RecoverRequest) -> dict[str, Any]:
    try:
        raw = _RUNTIME.recover(_frame(frame_id), request.lost_index)
    except HFCError as exc:
        raise _fail(exc) from exc
    return {
        "schema": "HHS_PASS_210_HFC_RECOVERY_RESPONSE_V1",
        "lost_index": request.lost_index,
        "register_hex": raw.hex(),
        "receipt_head_hash72": _RUNTIME.ledger.head,
    }


@router.post("/views/admit")
def admit_view(request: ViewAdmissionRequest) -> dict[str, Any]:
    try:
        view_id = _RUNTIME.view_admit(request.k, request.c, request.modulus)
        view = _RUNTIME.view(view_id)
    except HFCError as exc:
        raise _fail(exc) from exc
    return {
        "schema": "HHS_PASS_210_HFC_VIEW_ADMISSION_RESPONSE_V1",
        "view_id": view_id,
        "k": view.k,
        "c": view.c,
        "modulus": view.modulus,
        "inverse_k": view.inverse_k,
        "receipt_hash72": view.receipt_hash72,
    }


@router.post("/project")
def project(request: ProjectionRequest) -> dict[str, Any]:
    try:
        projection = _RUNTIME.project(request.register(), request.modality)
    except HFCError as exc:
        raise _fail(exc) from exc
    return projection.public_record()


@router.post("/agree")
def agree(request: AgreementRequest) -> dict[str, Any]:
    try:
        projections: list[HFCProjection] = [
            _RUNTIME.project(request.register(), modality) for modality in request.modalities
        ]
        return _RUNTIME.agree(*projections)
    except HFCError as exc:
        raise _fail(exc) from exc


@router.post("/strict/compress")
def strict_compress(request: RegisterRequest) -> dict[str, Any]:
    try:
        return _RUNTIME.strict_compress(request.register())
    except HFCError as exc:
        raise _fail(exc) from exc


@router.post("/strict/decompress")
def strict_decompress(request: StrictDecompressionRequest) -> dict[str, Any]:
    try:
        raw = _RUNTIME.strict_decompress(request.package)
    except HFCError as exc:
        raise _fail(exc) from exc
    return {
        "schema": "HHS_PASS_210_HFC_STRICT_DECOMPRESSION_RESPONSE_V1",
        "register_hex": raw.hex(),
        "receipt_head_hash72": _RUNTIME.ledger.head,
    }

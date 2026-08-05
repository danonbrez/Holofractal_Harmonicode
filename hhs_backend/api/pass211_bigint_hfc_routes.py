"""Public Pass 211 BigInt palindromic-carrier over HFC multi-register API."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from hhs_backend.runtime.hhs_pass211_bigint_hfc_carrier_v1 import (
    CONTRACT,
    Pass211BigIntHFCRuntime,
    Pass211Error,
)

API_PREFIX = "/api/runtime/bigint-hfc-carrier"
router = APIRouter(prefix=API_PREFIX, tags=["pass211-bigint-hfc"])
_RUNTIME = Pass211BigIntHFCRuntime()


class EncodeRequest(BaseModel):
    ciphertext_hex: str = Field(min_length=1, max_length=262_144)

    @field_validator("ciphertext_hex")
    @classmethod
    def validate_ciphertext_hex(cls, value: str) -> str:
        candidate = value.lower().removeprefix("0x")
        if not candidate or any(character not in "0123456789abcdef" for character in candidate):
            raise ValueError("ciphertext_hex must be hexadecimal")
        return "0x" + candidate

    def ciphertext(self) -> int:
        return int(self.ciphertext_hex, 16)


class PackageRequest(BaseModel):
    package: dict[str, Any]


class RecoveryRequest(PackageRequest):
    shard_index: int = Field(ge=0)
    lost_snapshot_index: int = Field(ge=0, lt=36)


class AnchoredCompareRequest(PackageRequest):
    shard_index: int = Field(ge=0)
    fresh_payload_hex: str

    @field_validator("fresh_payload_hex")
    @classmethod
    def validate_payload_hex(cls, value: str) -> str:
        if len(value) % 2:
            raise ValueError("fresh_payload_hex must contain complete bytes")
        try:
            bytes.fromhex(value)
        except ValueError as exc:
            raise ValueError("fresh_payload_hex must be hexadecimal") from exc
        return value.lower()


def _fail(exc: Pass211Error) -> HTTPException:
    text = str(exc)
    conflict_markers = (
        "MISMATCH",
        "SUBSTITUTION",
        "DUPLICATE",
        "ORDER",
        "MISSING",
        "DISAGREEMENT",
        "WITNESS",
    )
    return HTTPException(
        status_code=409 if any(marker in text for marker in conflict_markers) else 422,
        detail=text,
    )


@router.get("/status")
def status() -> dict[str, Any]:
    result = _RUNTIME.status()
    result["api_prefix"] = API_PREFIX
    result["contract"] = CONTRACT
    return result


@router.post("/encode")
def encode(request: EncodeRequest) -> dict[str, Any]:
    try:
        return _RUNTIME.encode(request.ciphertext()).to_dict()
    except Pass211Error as exc:
        raise _fail(exc) from exc


@router.post("/decode")
def decode(request: PackageRequest) -> dict[str, Any]:
    try:
        return _RUNTIME.decode(request.package)
    except Pass211Error as exc:
        raise _fail(exc) from exc


@router.post("/recover")
def recover(request: RecoveryRequest) -> dict[str, Any]:
    try:
        return _RUNTIME.recover_shard(
            request.package,
            request.shard_index,
            request.lost_snapshot_index,
        )
    except Pass211Error as exc:
        raise _fail(exc) from exc


@router.post("/anchored-compare")
def anchored_compare(request: AnchoredCompareRequest) -> dict[str, Any]:
    try:
        return _RUNTIME.anchored_compare(
            request.package,
            request.shard_index,
            bytes.fromhex(request.fresh_payload_hex),
        )
    except Pass211Error as exc:
        raise _fail(exc) from exc

"""FastAPI routes for Pass 212 full-hydration recovery."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_backend.runtime.hhs_pass212_full_hydration_recovery_v1 import (
    AFFINE_SEED_BYTES,
    FullHydrationPackage,
    Pass212Error,
    apply_bit_exceptions,
    generate_affine_hydration,
    get_pass212_runtime,
)

router = APIRouter(prefix="/api/runtime/full-hydration-recovery", tags=["pass212-full-hydration-recovery"])


class EncodeAffineRequest(BaseModel):
    seed_hex: str
    exception_positions: list[int] = Field(default_factory=list, max_length=100_000)


class RecoverRequest(BaseModel):
    package: dict[str, Any]
    unavailable_shards: list[str] = Field(default_factory=list, max_length=80)


@router.get("/status")
def pass212_status() -> dict[str, Any]:
    return get_pass212_runtime().status()


@router.post("/encode-affine")
def pass212_encode_affine(request: EncodeAffineRequest) -> dict[str, Any]:
    try:
        seeds = bytes.fromhex(request.seed_hex)
        if len(seeds) != AFFINE_SEED_BYTES:
            raise ValueError(f"seed_hex must decode to exactly {AFFINE_SEED_BYTES} bytes")
        positions = tuple(int(item) for item in request.exception_positions)
        state = generate_affine_hydration(seeds)
        if positions:
            state = apply_bit_exceptions(state, positions)
        package = get_pass212_runtime().encode(state)
        return {
            "status": "PASS212_FULL_HYDRATION_ENCODED",
            "state_hash216": package.state_hash216,
            "full_root216": package.full_root216,
            "metrics": dict(package.metrics),
            "package": package.to_dict(include_payloads=True),
        }
    except (ValueError, Pass212Error) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/recover")
def pass212_recover(request: RecoverRequest) -> dict[str, Any]:
    try:
        runtime = get_pass212_runtime()
        package = FullHydrationPackage.from_mapping(request.package)
        if request.unavailable_shards:
            package = runtime.without_shards(package, request.unavailable_shards)
        state = runtime.decode(package)
        return {
            "status": "PASS212_FULL_HYDRATION_RECOVERY_VERIFIED",
            "state_hash216": package.state_hash216,
            "full_root216": package.full_root216,
            "recovered_bytes": len(state),
            "unavailable_shards": list(request.unavailable_shards),
        }
    except Pass212Error as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

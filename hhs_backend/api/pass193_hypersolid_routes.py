"""FastAPI surface for Pass 193 exact hypersolids and native egress."""
from __future__ import annotations

from base64 import b64decode
import os
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_backend.runtime.hhs_pass193_hypersolid_native_egress_v1 import (
    Pass193Error,
    Pass193Runtime,
)

router = APIRouter(prefix="/api/runtime/hypersolids", tags=["pass193-hypersolids"])
_RUNTIME: Pass193Runtime | None = None
MAX_NATIVE_BINARY_BYTES = 64 * 1024 * 1024


def _runtime() -> Pass193Runtime:
    global _RUNTIME
    if _RUNTIME is None:
        root = Path(os.environ.get("HHS_PASS193_STATE_ROOT", "data/pass193"))
        _RUNTIME = Pass193Runtime(root)
    return _RUNTIME


def _call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Pass193Error as exc:
        raise HTTPException(status_code=409, detail=exc.classification) from exc
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


class AuthorityBody(BaseModel):
    authority_execution: Dict[str, Any]


class CreateBody(AuthorityBody):
    family: str = Field(min_length=1, max_length=128)
    dimension: int = Field(ge=2, le=12)
    constraint_registry: Dict[str, Any] = Field(default_factory=dict)


class RotateBody(AuthorityBody):
    plane: List[int] = Field(min_length=2, max_length=2)
    numerator: int
    denominator: int


class FoldBody(AuthorityBody):
    hinge_id: str = Field(min_length=1, max_length=4096)
    plane: List[int] = Field(min_length=2, max_length=2)
    numerator: int
    denominator: int
    target_dimension: int = Field(ge=2, le=12)
    reversible: bool = True


class NestBody(AuthorityBody):
    child_slot: int = Field(ge=0)
    lo_shu_cell: List[int] = Field(min_length=2, max_length=2)
    magnitude_row: int
    depth: int = Field(ge=0, le=4096)


class ProjectionBody(BaseModel):
    target_dimension: int = Field(ge=2, le=12)


class NativeEvidenceBody(BaseModel):
    compiled: bool
    linked: bool
    launched: bool
    abi_validated: bool
    deterministic_workload: bool


class NativeArtifactBody(AuthorityBody):
    target: str = Field(min_length=1, max_length=128)
    binary_b64: str
    compiler_identity: str = Field(min_length=1, max_length=4096)
    compiler_flags: List[str] = Field(default_factory=list)
    linker_identity: str = Field(min_length=1, max_length=4096)
    build_environment: Dict[str, Any] = Field(default_factory=dict)
    evidence: NativeEvidenceBody
    license_manifest: Dict[str, Any]


class PackageBody(AuthorityBody):
    artifact_ids: List[str] = Field(min_length=1)
    capabilities: List[str] = Field(default_factory=list)
    license_manifest: Dict[str, Any]


class NFTBody(AuthorityBody):
    package_id: str
    rights: Dict[str, Any]


class AuthorizeExecutionBody(AuthorityBody):
    identity_verified: bool
    capability_admitted: bool
    platform_validated: bool
    policy_accepted: bool
    runtime_integrity: bool


@router.get("/status")
def status() -> Dict[str, Any]:
    return _runtime().status()


@router.post("")
def create(body: CreateBody) -> Dict[str, Any]:
    constraints = body.constraint_registry or None
    return _call(
        _runtime().create_hypersolid,
        body.family,
        body.dimension,
        constraint_registry=constraints,
        authority_execution=body.authority_execution,
    )


@router.get("/{object_id}")
def get_object(object_id: str) -> Dict[str, Any]:
    return _call(_runtime().get_object, object_id)


@router.post("/{object_id}/rotate")
def rotate(object_id: str, body: RotateBody) -> Dict[str, Any]:
    return _call(
        _runtime().rotate,
        object_id,
        body.plane,
        body.numerator,
        body.denominator,
        authority_execution=body.authority_execution,
    )


@router.post("/{object_id}/fold")
def fold(object_id: str, body: FoldBody) -> Dict[str, Any]:
    return _call(
        _runtime().fold,
        object_id,
        body.hinge_id,
        body.plane,
        body.numerator,
        body.denominator,
        target_dimension=body.target_dimension,
        reversible=body.reversible,
        authority_execution=body.authority_execution,
    )


@router.post("/{object_id}/nest")
def nest(object_id: str, body: NestBody) -> Dict[str, Any]:
    return _call(
        _runtime().nest,
        object_id,
        child_slot=body.child_slot,
        lo_shu_cell=body.lo_shu_cell,
        magnitude_row=body.magnitude_row,
        depth=body.depth,
        authority_execution=body.authority_execution,
    )


@router.post("/{object_id}/project")
def project(object_id: str, body: ProjectionBody) -> Dict[str, Any]:
    return _call(_runtime().project, object_id, body.target_dimension)


@router.post("/{object_id}/validate")
def validate(object_id: str) -> Dict[str, Any]:
    return _call(_runtime().validate_object, object_id)


@router.post("/{object_id}/compile")
def record_native_artifact(object_id: str, body: NativeArtifactBody) -> Dict[str, Any]:
    try:
        binary = b64decode(body.binary_b64, validate=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="HHS_P193_BASE64_INVALID") from exc
    if len(binary) > MAX_NATIVE_BINARY_BYTES:
        raise HTTPException(status_code=413, detail="HHS_P193_NATIVE_BINARY_LIMIT")
    return _call(
        _runtime().record_native_artifact,
        object_id,
        target=body.target,
        binary_bytes=binary,
        compiler_identity=body.compiler_identity,
        compiler_flags=body.compiler_flags,
        linker_identity=body.linker_identity,
        build_environment=body.build_environment,
        evidence=body.evidence.model_dump(),
        license_manifest=body.license_manifest,
        authority_execution=body.authority_execution,
    )


@router.post("/{object_id}/package")
def package(object_id: str, body: PackageBody) -> Dict[str, Any]:
    return _call(
        _runtime().build_portable_bundle,
        object_id,
        body.artifact_ids,
        capabilities=body.capabilities,
        license_manifest=body.license_manifest,
        authority_execution=body.authority_execution,
    )


@router.get("/{object_id}/receipts")
def receipts(object_id: str) -> List[Dict[str, Any]]:
    return _runtime().receipts_for(object_id)


@router.post("/nft-executables/create")
def create_nft(body: NFTBody) -> Dict[str, Any]:
    return _call(
        _runtime().create_nft_executable,
        body.package_id,
        rights=body.rights,
        authority_execution=body.authority_execution,
    )


@router.post("/nft-executables/{nft_id}/authorize")
def authorize_nft(nft_id: str, body: AuthorizeExecutionBody) -> Dict[str, Any]:
    return _call(
        _runtime().authorize_execution,
        nft_id,
        identity_verified=body.identity_verified,
        capability_admitted=body.capability_admitted,
        platform_validated=body.platform_validated,
        policy_accepted=body.policy_accepted,
        runtime_integrity=body.runtime_integrity,
        authority_execution=body.authority_execution,
    )


@router.get("/replay/all")
def replay() -> Dict[str, Any]:
    return _call(_runtime().replay)

"""Governed HTTP API for Pass 166 Word2Vec acquisition and offline queries."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_runtime.pass166.service import DEFAULT_WORD2VEC_SERVICE, Word2VecError

router = APIRouter(tags=["runtime", "vm81", "pass166", "word2vec", "language-modality"])
SERVICE = DEFAULT_WORD2VEC_SERVICE


class ManifestRequest(BaseModel):
    manifest: dict[str, Any]


class InstallRequest(BaseModel):
    model_id: str = Field(min_length=1, max_length=256)
    source_manifest_id: str | None = None
    expected_sha256: str | None = None
    accept_license: bool
    activate: bool = True
    offline_ready: bool = True
    replace_existing: bool = False
    expected_pass165_frontier: str | None = None


class ActivationRequest(BaseModel):
    expected_pass165_frontier: str | None = None


class RemoveRequest(BaseModel):
    purge_package: bool = False


class SimilarityRequest(BaseModel):
    model_id: str | None = None
    left: str = Field(min_length=1)
    right: str = Field(min_length=1)


class NearestRequest(BaseModel):
    model_id: str | None = None
    token: str = Field(min_length=1)
    top_k: int = Field(default=16, ge=1, le=256)


class AnalogyRequest(BaseModel):
    model_id: str | None = None
    positive: list[str] = Field(min_length=1)
    negative: list[str] = Field(default_factory=list)
    top_k: int = Field(default=16, ge=1, le=256)


class ProjectionRequest(BaseModel):
    model_id: str | None = None
    token: str = Field(min_length=1)


def _raise(exc: Word2VecError, status: int = 422) -> None:
    raise HTTPException(status_code=status, detail={"classification": exc.classification, "detail": exc.detail}) from exc


@router.get("/v1/modalities/language/models/word2vec/status")
def status() -> dict[str, Any]:
    return SERVICE.status()


@router.post("/v1/modalities/language/models/word2vec/manifests")
def register_manifest(request: ManifestRequest) -> dict[str, Any]:
    try:
        return SERVICE.register_manifest(request.manifest)
    except Word2VecError as exc:
        _raise(exc)


@router.get("/v1/modalities/language/models/word2vec")
def list_models() -> dict[str, Any]:
    return {"models": SERVICE.list_models()}


@router.get("/v1/modalities/language/models/word2vec/{model_id}")
def inspect_model(model_id: str) -> dict[str, Any]:
    try:
        return SERVICE.inspect(model_id)
    except Word2VecError as exc:
        _raise(exc, 404)


@router.post("/v1/modalities/language/models/word2vec/install")
def install(request: InstallRequest) -> dict[str, Any]:
    try:
        if request.source_manifest_id and request.source_manifest_id != request.model_id:
            raise Word2VecError("P166_MANIFEST_MODEL_IDENTITY_MISMATCH")
        if request.expected_sha256:
            manifest = SERVICE.inspect(request.model_id)["manifest"]
            if manifest is None or manifest["expected_sha256"] != request.expected_sha256.lower():
                raise Word2VecError("P166_INVALID_EXPECTED_DIGEST")
        return SERVICE.install(
            request.model_id,
            accept_license=request.accept_license,
            activate=request.activate,
            offline_ready=request.offline_ready,
            replace_existing=request.replace_existing,
            expected_pass165_frontier=request.expected_pass165_frontier,
        )
    except Word2VecError as exc:
        _raise(exc)


@router.post("/v1/modalities/language/models/word2vec/{model_id}/verify")
def verify(model_id: str) -> dict[str, Any]:
    try:
        return SERVICE.verify(model_id)
    except Word2VecError as exc:
        _raise(exc)


@router.post("/v1/modalities/language/models/word2vec/{model_id}/activate")
def activate(model_id: str, request: ActivationRequest) -> dict[str, Any]:
    try:
        return SERVICE.activate(model_id, expected_pass165_frontier=request.expected_pass165_frontier)
    except Word2VecError as exc:
        _raise(exc)


@router.post("/v1/modalities/language/models/word2vec/{model_id}/deactivate")
def deactivate(model_id: str) -> dict[str, Any]:
    try:
        return SERVICE.deactivate(model_id)
    except Word2VecError as exc:
        _raise(exc)


@router.post("/v1/modalities/language/models/word2vec/{model_id}/repair")
def repair(model_id: str) -> dict[str, Any]:
    try:
        return SERVICE.repair(model_id)
    except Word2VecError as exc:
        _raise(exc)


@router.delete("/v1/modalities/language/models/word2vec/{model_id}")
def remove(model_id: str, request: RemoveRequest | None = None) -> dict[str, Any]:
    try:
        return SERVICE.remove(model_id, purge_package=bool(request and request.purge_package))
    except Word2VecError as exc:
        _raise(exc)


@router.get("/v1/model-operations/{operation_id}")
def operation(operation_id: str) -> dict[str, Any]:
    try:
        return SERVICE.get_operation(operation_id)
    except Word2VecError as exc:
        _raise(exc, 404)


@router.get("/v1/model-operations/{operation_id}/receipt")
def receipt(operation_id: str) -> dict[str, Any]:
    try:
        return SERVICE.get_operation(operation_id)
    except Word2VecError as exc:
        _raise(exc, 404)


@router.get("/v1/modalities/language/vectors/{token}")
def vector(token: str, model_id: str | None = None, include_projection_5184: bool = True, include_provenance: bool = True) -> dict[str, Any]:
    try:
        return SERVICE.vector(token, model_id=model_id, include_projection_5184=include_projection_5184, include_provenance=include_provenance)
    except Word2VecError as exc:
        _raise(exc, 404)


@router.post("/v1/modalities/language/similarity")
def similarity(request: SimilarityRequest) -> dict[str, Any]:
    try:
        return SERVICE.similarity(request.left, request.right, model_id=request.model_id)
    except Word2VecError as exc:
        _raise(exc)


@router.post("/v1/modalities/language/nearest")
def nearest(request: NearestRequest) -> dict[str, Any]:
    try:
        return SERVICE.nearest(request.token, model_id=request.model_id, top_k=request.top_k)
    except Word2VecError as exc:
        _raise(exc)


@router.post("/v1/modalities/language/analogy")
def analogy(request: AnalogyRequest) -> dict[str, Any]:
    try:
        return SERVICE.analogy(request.positive, request.negative, model_id=request.model_id, top_k=request.top_k)
    except Word2VecError as exc:
        _raise(exc)


@router.post("/v1/modalities/language/project")
def project(request: ProjectionRequest) -> dict[str, Any]:
    try:
        return SERVICE.project(request.token, model_id=request.model_id)
    except Word2VecError as exc:
        _raise(exc)

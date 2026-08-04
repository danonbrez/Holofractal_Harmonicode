"""Pass 208 physical-GPU branch manifold API.

These routes expose bounded candidate expansion and verified branch submission.
They do not expose a GPU commit primitive. The selected branch is always
recomputed by the existing Pass 205 singleton VM81 authority before Hash72
receipt creation and persistence.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_backend.api.runtime_routes import _contract_response
from hhs_backend.runtime.hhs_pass205_continuation_runtime_v1 import (
    PASS205_CONTINUATION_RUNTIME,
    ContinuationNotFound,
    ContinuationRejected,
)
from hhs_backend.runtime.hhs_pass208_gpu_branch_manifold_v1 import (
    CONTRACT,
    PASS208_GPU_BRANCH_MANIFOLD,
    Pass208GPUManifoldRejected,
)

API_PREFIX = "/api/runtime/gpu-manifold"
router = APIRouter(
    prefix=API_PREFIX,
    tags=["runtime", "gpu", "vm81", "branch-manifold", "hydration", "pass208"],
)


class DeltaEvent(BaseModel):
    cell: int = Field(ge=0, le=80)
    control_g: int = Field(ge=0, le=242)
    xor_mask: int = Field(gt=0, le=(1 << 64) - 1)


class BranchSpec(BaseModel):
    events: List[DeltaEvent] = Field(min_length=1, max_length=81)


class ExpandRequest(BaseModel):
    parent_root216: str = Field(min_length=216, max_length=216)
    branches: List[BranchSpec] = Field(min_length=1, max_length=4096)
    bytecode_hydration_lattice_root216: Optional[str] = Field(
        default=None, min_length=216, max_length=216
    )
    target_state_words: Optional[List[int]] = Field(default=None, min_length=81, max_length=81)


class CommitRequest(ExpandRequest):
    expected_parent_receipt_hash72: Optional[str] = Field(
        default=None, min_length=72, max_length=72
    )
    selected_branch_ordinal: Optional[int] = Field(default=None, ge=0)


def _events(branches: List[BranchSpec]) -> list[list[dict[str, int]]]:
    result: list[list[dict[str, int]]] = []
    for branch in branches:
        result.append([
            event.model_dump() if hasattr(event, "model_dump") else event.dict()
            for event in branch.events
        ])
    return result


def _response(path: str, method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return _contract_response(path, method, payload)


def _raise(exc: Exception) -> None:
    if isinstance(exc, ContinuationNotFound):
        raise HTTPException(
            status_code=404,
            detail={
                "schema": "HHS_PASS_208_GPU_MANIFOLD_PARENT_NOT_FOUND_V1",
                "contract": CONTRACT,
                "ok": False,
                "reason": str(exc),
            },
        ) from exc
    if isinstance(exc, (Pass208GPUManifoldRejected, ContinuationRejected, ValueError)):
        raise HTTPException(
            status_code=422,
            detail={
                "schema": "HHS_PASS_208_GPU_MANIFOLD_REJECTED_V1",
                "contract": CONTRACT,
                "ok": False,
                "reason": str(exc),
            },
        ) from exc
    raise HTTPException(
        status_code=503,
        detail={
            "schema": "HHS_PASS_208_GPU_MANIFOLD_UNAVAILABLE_V1",
            "contract": CONTRACT,
            "ok": False,
            "reason": f"{exc.__class__.__name__}: {exc}",
            "retryable": True,
        },
    ) from exc


@router.get("/status")
def gpu_manifold_status() -> Dict[str, Any]:
    return _response(f"{API_PREFIX}/status", "GET", PASS208_GPU_BRANCH_MANIFOLD.status())


@router.post("/expand")
def gpu_manifold_expand(body: ExpandRequest) -> Dict[str, Any]:
    try:
        parent = PASS205_CONTINUATION_RUNTIME.snapshot(body.parent_root216)
        result = PASS208_GPU_BRANCH_MANIFOLD.expand(
            parent_snapshot=parent,
            branches=_events(body.branches),
            bytecode_hydration_lattice_root216=body.bytecode_hydration_lattice_root216,
            target_state_words=body.target_state_words,
        )
    except Exception as exc:
        _raise(exc)
    return _response(f"{API_PREFIX}/expand", "POST", result)


@router.post("/expand-and-commit")
def gpu_manifold_expand_and_commit(body: CommitRequest) -> Dict[str, Any]:
    try:
        result = PASS208_GPU_BRANCH_MANIFOLD.expand_and_commit(
            continuation_runtime=PASS205_CONTINUATION_RUNTIME,
            parent_root216=body.parent_root216,
            branches=_events(body.branches),
            expected_parent_receipt_hash72=body.expected_parent_receipt_hash72,
            bytecode_hydration_lattice_root216=body.bytecode_hydration_lattice_root216,
            target_state_words=body.target_state_words,
            selected_branch_ordinal=body.selected_branch_ordinal,
        )
    except Exception as exc:
        _raise(exc)
    return _response(f"{API_PREFIX}/expand-and-commit", "POST", result)

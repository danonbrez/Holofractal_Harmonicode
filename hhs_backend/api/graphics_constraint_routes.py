"""Governed HTTP projection for Pass 181 graphics constraint freeze authority.

This router is registered before the legacy graphics-hydration router so the old
`/constraints/promote` projection fails closed. All freezes must resolve an
eligible candidate from the durable vector-hydration candidate registry.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter

from hhs_backend.runtime.hhs_graphics_constraint_registry_instance_v1 import (
    GRAPHICS_CONSTRAINT_REGISTRY,
)
from hhs_backend.runtime.hhs_graphics_constraint_registry_v1 import (
    GraphicsConstraintRegistryError,
)
from hhs_backend.runtime.hhs_graphics_vector_hydration_instance_v1 import (
    GRAPHICS_VECTOR_HYDRATION,
)

router = APIRouter(
    prefix="/api/runtime/graphics-hydration/constraints",
    tags=["graphics-hydration", "graphics-constraints"],
)


def _rejection(error: Exception) -> Dict[str, Any]:
    return {
        "schema": "HHS_P181_GRAPHICS_CONSTRAINT_ROUTE_RESULT_V1",
        "ok": False,
        "status": "REJECT_GRAPHICS_CONSTRAINT_REQUEST",
        "reason": str(error),
    }


def _candidate(candidate_hash216: str) -> Dict[str, Any]:
    for candidate in GRAPHICS_VECTOR_HYDRATION.list_invariant_candidates():
        if candidate.get("candidate_hash216") == candidate_hash216:
            return candidate
    raise GraphicsConstraintRegistryError("P181_INVARIANT_CANDIDATE_UNKNOWN")


@router.post("/promote")
def legacy_direct_graphics_constraint_promotion_disabled(
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return _rejection(
        GraphicsConstraintRegistryError(
            "P181_LEGACY_DIRECT_CONSTRAINT_PROMOTION_DISABLED_USE_REGISTRY_FREEZE"
        )
    )


@router.get("/registry/status")
def graphics_constraint_registry_status() -> Dict[str, Any]:
    return GRAPHICS_CONSTRAINT_REGISTRY.status()


@router.get("/registry/frontier")
def graphics_constraint_registry_frontier() -> Dict[str, Any]:
    return GRAPHICS_CONSTRAINT_REGISTRY.active_frontier()


@router.get("/registry/records")
def graphics_constraint_registry_records(
    record_kind: Optional[str] = None,
    predicate_id: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "schema": "HHS_P181_GRAPHICS_CONSTRAINT_RECORD_LIST_V1",
        "records": GRAPHICS_CONSTRAINT_REGISTRY.list_records(
            record_kind=record_kind,
            predicate_id=predicate_id,
        ),
    }


@router.post("/registry/freeze")
def graphics_constraint_registry_freeze(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        candidate_hash216 = str(payload.get("candidate_hash216") or "").strip()
        evidence = payload.get("promotion_evidence")
        if not candidate_hash216:
            raise GraphicsConstraintRegistryError("P181_INVARIANT_CANDIDATE_IDENTITY_REQUIRED")
        if not isinstance(evidence, dict):
            raise GraphicsConstraintRegistryError("P181_PROMOTION_EVIDENCE_REQUIRED")
        supersedes = payload.get("supersedes")
        return GRAPHICS_CONSTRAINT_REGISTRY.freeze_candidate(
            _candidate(candidate_hash216),
            evidence,
            activate=bool(payload.get("activate", True)),
            supersedes=None if supersedes is None else str(supersedes),
        )
    except GraphicsConstraintRegistryError as error:
        return _rejection(error)


@router.post("/registry/rollback")
def graphics_constraint_registry_rollback(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        predicate_id = str(payload.get("predicate_id") or "").strip()
        if not predicate_id:
            raise GraphicsConstraintRegistryError("P181_CONSTRAINT_PREDICATE_ID_REQUIRED")
        target = payload.get("target_record_hash216")
        return GRAPHICS_CONSTRAINT_REGISTRY.rollback(
            predicate_id,
            record_kind=str(payload.get("record_kind") or "RUNTIME_CONSTRAINT"),
            target_record_hash216=None if target is None else str(target),
        )
    except GraphicsConstraintRegistryError as error:
        return _rejection(error)


@router.post("/registry/replay")
def graphics_constraint_registry_replay() -> Dict[str, Any]:
    try:
        return GRAPHICS_CONSTRAINT_REGISTRY.verify_replay()
    except GraphicsConstraintRegistryError as error:
        return _rejection(error)

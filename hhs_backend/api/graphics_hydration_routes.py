"""HTTP projection for the Pass 181 graphics hydration authority core."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from hhs_backend.runtime.hhs_graphics_hydration_v1 import (
    GRAPHICS_HYDRATION,
    GraphicsHydrationError,
    classify_fidelity,
    graphics_hydration_self_test,
    reciprocal_palette_phases,
    validate_native_frame_provenance,
)

router = APIRouter(prefix="/api/runtime/graphics-hydration", tags=["graphics-hydration"])


def _rejection(error: GraphicsHydrationError) -> Dict[str, Any]:
    return {
        "schema": "HHS_P181_GRAPHICS_HYDRATION_ROUTE_RESULT_V1",
        "ok": False,
        "status": "REJECT_GRAPHICS_HYDRATION_REQUEST",
        "reason": str(error),
    }


@router.get("/status")
def graphics_hydration_status() -> Dict[str, Any]:
    status = GRAPHICS_HYDRATION.status()
    status["self_test_projection"] = graphics_hydration_self_test()
    return status


@router.post("/palette")
def graphics_hydration_palette(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        phases = reciprocal_palette_phases(
            int(payload.get("x_phase")),
            int(payload.get("y_phase")),
            int(payload.get("w_phase")),
        )
    except (GraphicsHydrationError, TypeError, ValueError) as error:
        return _rejection(
            error if isinstance(error, GraphicsHydrationError) else GraphicsHydrationError("P181_PALETTE_INPUT_INVALID")
        )
    return {
        "schema": "HHS_P181_RECIPROCAL_PALETTE_RESULT_V1",
        "ok": True,
        "status": "HHS_XYZW_CHROMATIC_PALETTE_ENGINE_READY",
        "phases": phases,
    }


@router.post("/provenance/validate")
def graphics_hydration_validate_provenance(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return validate_native_frame_provenance(payload)
    except GraphicsHydrationError as error:
        return _rejection(error)


@router.post("/fidelity/classify")
def graphics_hydration_classify_fidelity(payload: Dict[str, Any]) -> Dict[str, Any]:
    return classify_fidelity(payload)


@router.post("/constraints/promote")
def graphics_hydration_promote_constraint(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return GRAPHICS_HYDRATION.promote_constraint(payload)
    except GraphicsHydrationError as error:
        return _rejection(error)

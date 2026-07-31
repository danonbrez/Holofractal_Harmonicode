"""HTTP projection for the Pass 181 graphics hydration authority."""
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


def _require_operator_local_path_authority() -> None:
    if not GRAPHICS_HYDRATION.status()["operator_local_path_decode_enabled"]:
        raise GraphicsHydrationError("P181_OPERATOR_LOCAL_PATH_DECODE_DISABLED")


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
        if not isinstance(error, GraphicsHydrationError):
            error = GraphicsHydrationError("P181_PALETTE_INPUT_INVALID")
        return _rejection(error)
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


@router.post("/decode/manifest")
def graphics_hydration_decode_manifest(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Operator-only local-file decode; browser uploads use a separate ingress path."""

    try:
        _require_operator_local_path_authority()
        return GRAPHICS_HYDRATION.build_decode_manifest(
            str(payload.get("source_path") or ""),
            logical_name=payload.get("logical_name"),
        )
    except (GraphicsHydrationError, OSError) as error:
        if not isinstance(error, GraphicsHydrationError):
            error = GraphicsHydrationError(f"P181_REFERENCE_PATH_INVALID:{error}")
        return _rejection(error)


@router.post("/decode/replay")
def graphics_hydration_decode_replay(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        _require_operator_local_path_authority()
        expected = str(payload.get("expected_timeline_hash216") or "").strip()
        if not expected:
            raise GraphicsHydrationError("P181_EXPECTED_TIMELINE_IDENTITY_REQUIRED")
        return GRAPHICS_HYDRATION.replay_decode_manifest(
            str(payload.get("source_path") or ""),
            expected_timeline_hash216=expected,
            logical_name=payload.get("logical_name"),
        )
    except (GraphicsHydrationError, OSError) as error:
        if not isinstance(error, GraphicsHydrationError):
            error = GraphicsHydrationError(f"P181_REFERENCE_PATH_INVALID:{error}")
        return _rejection(error)


@router.post("/recipes/validate")
def graphics_hydration_validate_recipe(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        recipe = payload.get("recipe")
        reference_manifest = payload.get("reference_manifest")
        if not isinstance(recipe, dict) or not isinstance(reference_manifest, dict):
            raise GraphicsHydrationError("P181_RECIPE_AND_REFERENCE_MANIFEST_REQUIRED")
        return GRAPHICS_HYDRATION.validate_native_recipe(recipe, reference_manifest)
    except GraphicsHydrationError as error:
        return _rejection(error)


@router.post("/residuals/compare")
def graphics_hydration_compare_residuals(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        reference_manifest = payload.get("reference_manifest")
        native_manifest = payload.get("native_manifest")
        validated_recipe = payload.get("validated_recipe")
        semantic_metrics = payload.get("semantic_metrics")
        if not isinstance(reference_manifest, dict):
            raise GraphicsHydrationError("P181_REFERENCE_MANIFEST_REQUIRED")
        if not isinstance(native_manifest, dict):
            raise GraphicsHydrationError("P181_NATIVE_MANIFEST_REQUIRED")
        if not isinstance(validated_recipe, dict):
            raise GraphicsHydrationError("P181_VALIDATED_RECIPE_REQUIRED")
        if semantic_metrics is not None and not isinstance(semantic_metrics, dict):
            raise GraphicsHydrationError("P181_SEMANTIC_METRICS_INVALID")
        return GRAPHICS_HYDRATION.build_residual_report(
            reference_manifest,
            native_manifest,
            validated_recipe,
            semantic_metrics=semantic_metrics,
        )
    except GraphicsHydrationError as error:
        return _rejection(error)


@router.post("/constraints/promote")
def graphics_hydration_promote_constraint(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return GRAPHICS_HYDRATION.promote_constraint(payload)
    except GraphicsHydrationError as error:
        return _rejection(error)

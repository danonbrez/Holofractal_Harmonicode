"""HTTP projection for the Pass 181 graphics hydration authority."""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter

from hhs_backend.runtime.hhs_graphics_hydration_v1 import (
    GRAPHICS_HYDRATION,
    GraphicsHydrationError,
    classify_fidelity,
    graphics_hydration_self_test,
    reciprocal_palette_phases,
    validate_native_frame_provenance,
)
from hhs_backend.runtime.hhs_graphics_optimization_v1 import GraphicsOptimizationError
from hhs_backend.runtime.hhs_graphics_optimizer_instance_v1 import GRAPHICS_OPTIMIZER
from hhs_backend.runtime.hhs_graphics_vector_hydration_instance_v1 import (
    GRAPHICS_VECTOR_HYDRATION,
)
from hhs_backend.runtime.hhs_graphics_vector_hydration_v1 import (
    GraphicsVectorHydrationError,
)

router = APIRouter(prefix="/api/runtime/graphics-hydration", tags=["graphics-hydration"])


def _rejection(error: Exception) -> Dict[str, Any]:
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
    status["bounded_optimizer"] = GRAPHICS_OPTIMIZER.status()
    status["vector_hydration"] = GRAPHICS_VECTOR_HYDRATION.status()
    status["implementation_stage"] = "PASS_181_PHASE_5_VECTOR_HYDRATION_AND_INVARIANT_CANDIDATES"
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


@router.post("/optimization/jobs")
def graphics_hydration_create_optimization_job(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        reference_manifest = payload.get("reference_manifest")
        candidates = payload.get("candidate_recipes")
        baseline = payload.get("baseline_residual_report")
        if not isinstance(reference_manifest, dict):
            raise GraphicsOptimizationError("P181_REFERENCE_MANIFEST_REQUIRED")
        if not isinstance(candidates, list):
            raise GraphicsOptimizationError("P181_CANDIDATE_RECIPE_LIST_REQUIRED")
        if baseline is not None and not isinstance(baseline, dict):
            raise GraphicsOptimizationError("P181_BASELINE_RESIDUAL_REPORT_INVALID")
        return GRAPHICS_OPTIMIZER.create_job(
            reference_manifest=reference_manifest,
            candidate_recipes=candidates,
            baseline_residual_report=baseline,
            timeout_seconds=int(payload.get("timeout_seconds") or 3600),
            render_timeout_seconds=int(payload.get("render_timeout_seconds") or 1800),
            stop_on_exact=bool(payload.get("stop_on_exact", True)),
        )
    except (GraphicsOptimizationError, TypeError, ValueError) as error:
        if not isinstance(error, GraphicsOptimizationError):
            error = GraphicsOptimizationError("P181_OPTIMIZATION_REQUEST_INVALID")
        return _rejection(error)


@router.get("/optimization/jobs/{job_id}")
def graphics_hydration_get_optimization_job(job_id: str) -> Dict[str, Any]:
    try:
        return GRAPHICS_OPTIMIZER.get_job(job_id)
    except GraphicsOptimizationError as error:
        return _rejection(error)


@router.post("/optimization/jobs/{job_id}/step")
def graphics_hydration_step_optimization_job(job_id: str) -> Dict[str, Any]:
    try:
        return GRAPHICS_OPTIMIZER.step_job(job_id)
    except GraphicsOptimizationError as error:
        return _rejection(error)


@router.post("/optimization/jobs/{job_id}/run")
def graphics_hydration_run_optimization_job(
    job_id: str,
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    try:
        body = payload or {}
        max_steps = body.get("max_steps")
        return GRAPHICS_OPTIMIZER.run_job(
            job_id,
            max_steps=None if max_steps is None else int(max_steps),
        )
    except (GraphicsOptimizationError, TypeError, ValueError) as error:
        if not isinstance(error, GraphicsOptimizationError):
            error = GraphicsOptimizationError("P181_OPTIMIZATION_RUN_REQUEST_INVALID")
        return _rejection(error)


@router.post("/optimization/jobs/{job_id}/cancel")
def graphics_hydration_cancel_optimization_job(job_id: str) -> Dict[str, Any]:
    try:
        return GRAPHICS_OPTIMIZER.cancel_job(job_id)
    except GraphicsOptimizationError as error:
        return _rejection(error)


@router.post("/optimization/jobs/{job_id}/retry")
def graphics_hydration_retry_optimization_job(job_id: str) -> Dict[str, Any]:
    try:
        return GRAPHICS_OPTIMIZER.retry_job(job_id)
    except GraphicsOptimizationError as error:
        return _rejection(error)


@router.get("/vector-hydration/status")
def graphics_vector_hydration_status() -> Dict[str, Any]:
    return GRAPHICS_VECTOR_HYDRATION.status()


@router.post("/vector-hydration/jobs/admit")
def graphics_vector_hydration_admit_job(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        job_id = str(payload.get("job_id") or "").strip()
        if not job_id:
            raise GraphicsVectorHydrationError("P181_OPTIMIZATION_JOB_ID_REQUIRED")
        job = GRAPHICS_OPTIMIZER.get_job(job_id)
        return GRAPHICS_VECTOR_HYDRATION.hydrate_optimization_job(job)
    except (GraphicsVectorHydrationError, GraphicsOptimizationError) as error:
        return _rejection(error)


@router.get("/vector-hydration/records")
def graphics_vector_hydration_records(
    record_class: Optional[str] = None,
    source_job_id: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "schema": "HHS_P181_GRAPHICS_VECTOR_RECORD_LIST_V1",
        "records": GRAPHICS_VECTOR_HYDRATION.list_records(
            record_class=record_class,
            source_job_id=source_job_id,
        ),
    }


@router.post("/vector-hydration/invariants/extract")
def graphics_vector_hydration_extract_invariants(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return GRAPHICS_VECTOR_HYDRATION.extract_invariant_candidates(
            minimum_support=int(payload.get("minimum_support") or 2),
            minimum_distinct_jobs=int(payload.get("minimum_distinct_jobs") or 2),
        )
    except (GraphicsVectorHydrationError, TypeError, ValueError) as error:
        if not isinstance(error, GraphicsVectorHydrationError):
            error = GraphicsVectorHydrationError("P181_INVARIANT_EXTRACTION_REQUEST_INVALID")
        return _rejection(error)


@router.get("/vector-hydration/invariants")
def graphics_vector_hydration_invariants(
    candidate_class: Optional[str] = None,
    eligible_only: bool = False,
) -> Dict[str, Any]:
    return {
        "schema": "HHS_P181_GRAPHICS_INVARIANT_CANDIDATE_LIST_V1",
        "candidates": GRAPHICS_VECTOR_HYDRATION.list_invariant_candidates(
            candidate_class=candidate_class,
            eligible_only=eligible_only,
        ),
        "runtime_constraints_frozen": 0,
    }


@router.post("/vector-hydration/invariants/{candidate_hash216}/promotion-proposal")
def graphics_vector_hydration_promotion_proposal(candidate_hash216: str) -> Dict[str, Any]:
    try:
        return GRAPHICS_VECTOR_HYDRATION.build_promotion_proposal(candidate_hash216)
    except GraphicsVectorHydrationError as error:
        return _rejection(error)


@router.post("/vector-hydration/replay")
def graphics_vector_hydration_replay() -> Dict[str, Any]:
    try:
        return GRAPHICS_VECTOR_HYDRATION.replay()
    except GraphicsVectorHydrationError as error:
        return _rejection(error)


@router.post("/constraints/promote")
def graphics_hydration_promote_constraint(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return GRAPHICS_HYDRATION.promote_constraint(payload)
    except GraphicsHydrationError as error:
        return _rejection(error)

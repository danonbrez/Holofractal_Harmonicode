"""HHS Cross-Modal Transformation Plan v1."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional
import time
import uuid

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

VERSION = "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1"
AUTHORITY = "HHS_UNIVERSAL_MODALITY_PIPELINE_AUTHORITY_V1"

def _unique(prefix: str) -> str:
    return f"{prefix}:{uuid.uuid4().hex}"

def _now_ms() -> int:
    return int(time.time() * 1000)

def _list(values: Optional[Iterable[Any]]) -> List[str]:
    return sorted(dict.fromkeys(str(v) for v in (values or []) if str(v)))

from hhs_backend.runtime.hhs_modality_reconstruction_recipe_v1 import build_modality_reconstruction_recipe, validate_modality_reconstruction_recipe

TRANSFORMATION_PLAN_SCHEMA = "HHS_CROSS_MODAL_TRANSFORMATION_PLAN_V1"


def build_cross_modal_transformation_plan(*, source_projection_records: Iterable[Mapping[str, Any]], target_modality: str, target_artifact_type: str, transformation_kind: str = "DERIVE_ARTIFACT") -> Dict[str, Any]:
    projections = [dict(p) for p in source_projection_records]
    source_roots = _list(p.get("source_root_hash72") for p in projections)
    projection_roots = _list(p.get("projection_root_hash72") for p in projections)
    recipe = build_modality_reconstruction_recipe(
        source_root_hash72=source_roots[0] if source_roots else "",
        projection_roots=projection_roots,
        operations=[{"operation": transformation_kind, "target_modality": target_modality, "target_artifact_type": target_artifact_type}],
    )
    plan = {
        "schema": TRANSFORMATION_PLAN_SCHEMA,
        "version": VERSION,
        "plan_id": _unique("xmodal-plan"),
        "source_root_hash72s": source_roots,
        "projection_root_hash72s": projection_roots,
        "target_modality": target_modality.upper(),
        "target_artifact_type": target_artifact_type,
        "transformation_kind": transformation_kind,
        "execution_authorized": False,
        "artifact_creation_authorized": True,
        "requires_witness": True,
        "reconstruction_recipe": recipe,
        "private_truth_pipeline_allowed": False,
        "authority": AUTHORITY,
        "created_at_unix_ms": _now_ms(),
    }
    plan["plan_root_hash72"] = hash72(TRANSFORMATION_PLAN_SCHEMA, plan)
    return plan


def validate_cross_modal_transformation_plan(plan: Mapping[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []
    if plan.get("schema") != TRANSFORMATION_PLAN_SCHEMA:
        reasons.append("REJECT_CROSS_MODAL_PLAN_WITHOUT_SCHEMA")
    if not plan.get("source_root_hash72s"):
        reasons.append("REJECT_TRANSFORMATION_WITHOUT_SOURCE_COMMITMENT")
    if not plan.get("projection_root_hash72s"):
        reasons.append("REJECT_CROSS_MODAL_PLAN_WITHOUT_PROJECTION")
    if not plan.get("reconstruction_recipe"):
        reasons.append("REJECT_CROSS_MODAL_PLAN_WITHOUT_RECONSTRUCTION")
    else:
        recipe_validation = validate_modality_reconstruction_recipe(plan.get("reconstruction_recipe") or {})
        if not recipe_validation.get("ok"):
            reasons.extend(recipe_validation.get("reasons") or [])
    if plan.get("private_truth_pipeline_allowed"):
        reasons.append("REJECT_ADAPTER_PRIVATE_TRUTH_PIPELINE")
    ok = not reasons
    return {"schema": "HHS_CROSS_MODAL_TRANSFORMATION_PLAN_VALIDATION_V1", "version": VERSION, "ok": ok, "status": "ADMIT_CROSS_MODAL_TRANSFORMATION_PLAN" if ok else "REJECT_CROSS_MODAL_TRANSFORMATION_PLAN", "reasons": sorted(dict.fromkeys(reasons)), "plan_id": plan.get("plan_id")}


def cross_modal_transformation_plan_self_test() -> Dict[str, Any]:
    from hhs_backend.runtime.hhs_modality_source_commitment_v1 import build_source_commitment
    from hhs_backend.runtime.hhs_universal_modality_adapter_v1 import build_universal_adapter_contract
    from hhs_backend.runtime.hhs_modality_projection_registry_v1 import build_projection_record
    source = build_source_commitment(project_id="project:pass050", source_name="clip.wav", payload="WAV", modality="AUDIO")
    adapter = build_universal_adapter_contract("AUDIO")
    projection = build_projection_record(source_commitment=source, adapter_contract=adapter, projection_type="HARMONIC_TIME_PROJECTION", projection_payload="phase")
    plan = build_cross_modal_transformation_plan(source_projection_records=[projection], target_modality="GRAPH_OBJECT", target_artifact_type="HARMONIC_TIME_GRAPH")
    bad = dict(plan, reconstruction_recipe=None)
    valid = validate_cross_modal_transformation_plan(plan)
    rejected = validate_cross_modal_transformation_plan(bad)
    return {"schema": "HHS_CROSS_MODAL_TRANSFORMATION_PLAN_SELF_TEST_V1", "version": VERSION, "ok": bool(valid["ok"] and not rejected["ok"]), "plan": plan, "reconstruction_rejection": rejected}

if __name__ == "__main__":
    import json
    print(json.dumps(cross_modal_transformation_plan_self_test(), indent=2, sort_keys=True, default=str))

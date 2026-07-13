"""HHS Artifact Lineage Registry v1."""

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

LINEAGE_SCHEMA = "HHS_ARTIFACT_LINEAGE_RECORD_V1"


def build_artifact_lineage_record(*, source_commitment: Mapping[str, Any], projections: Iterable[Mapping[str, Any]], transformation_plan: Mapping[str, Any], artifact: Mapping[str, Any]) -> Dict[str, Any]:
    projection_list = [dict(p) for p in projections]
    lineage = {
        "schema": LINEAGE_SCHEMA,
        "version": VERSION,
        "lineage_id": _unique("lineage"),
        "source_commitment_id": source_commitment.get("source_commitment_id"),
        "source_root_hash72": source_commitment.get("source_root_hash72"),
        "source_modality": source_commitment.get("modality"),
        "projection_ids": [p.get("projection_id") for p in projection_list],
        "projection_root_hash72s": [p.get("projection_root_hash72") for p in projection_list],
        "transformation_plan_id": transformation_plan.get("plan_id"),
        "transformation_plan_root_hash72": transformation_plan.get("plan_root_hash72"),
        "artifact_id": artifact.get("artifact_id"),
        "artifact_root_hash72": artifact.get("artifact_root_hash72"),
        "source_not_replaced_by_projection": True,
        "projection_not_confused_with_artifact": True,
        "artifact_execution_authority_inferred": False,
        "reconstruction_recipe_id": (artifact.get("reconstruction_recipe") or {}).get("recipe_id"),
        "authority": AUTHORITY,
    }
    lineage["lineage_root_hash72"] = hash72(LINEAGE_SCHEMA, lineage)
    return lineage


def validate_artifact_lineage_record(lineage: Mapping[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []
    if lineage.get("schema") != LINEAGE_SCHEMA:
        reasons.append("REJECT_ARTIFACT_WITHOUT_LINEAGE")
    if not lineage.get("source_root_hash72") or not lineage.get("artifact_root_hash72"):
        reasons.append("REJECT_ARTIFACT_WITHOUT_LINEAGE")
    if not lineage.get("source_not_replaced_by_projection"):
        reasons.append("REJECT_PROJECTION_REPLACES_SOURCE")
    if lineage.get("artifact_execution_authority_inferred"):
        reasons.append("REJECT_ARTIFACT_EXECUTION_AUTHORITY_INFERRED")
    ok = not reasons
    return {"schema": "HHS_ARTIFACT_LINEAGE_RECORD_VALIDATION_V1", "version": VERSION, "ok": ok, "status": "ADMIT_ARTIFACT_LINEAGE" if ok else "REJECT_ARTIFACT_LINEAGE", "reasons": sorted(dict.fromkeys(reasons)), "lineage_id": lineage.get("lineage_id")}


def artifact_lineage_registry_self_test() -> Dict[str, Any]:
    from hhs_backend.runtime.hhs_modality_source_commitment_v1 import build_source_commitment
    from hhs_backend.runtime.hhs_universal_modality_adapter_v1 import build_universal_adapter_contract
    from hhs_backend.runtime.hhs_modality_projection_registry_v1 import build_projection_record
    from hhs_backend.runtime.hhs_cross_modal_transformation_plan_v1 import build_cross_modal_transformation_plan
    from hhs_backend.runtime.hhs_derived_artifact_pipeline_v1 import build_derived_artifact_record
    source = build_source_commitment(project_id="project:pass050", source_name="object.json", payload={"a": 1}, modality="JSON")
    adapter = build_universal_adapter_contract("JSON")
    projection = build_projection_record(source_commitment=source, adapter_contract=adapter, projection_type="STRUCTURE_PROJECTION", projection_payload={"keys": ["a"]})
    plan = build_cross_modal_transformation_plan(source_projection_records=[projection], target_modality="GRAPH_OBJECT", target_artifact_type="JSON_STRUCTURE_GRAPH")
    artifact = build_derived_artifact_record(transformation_plan=plan, artifact_payload={"graph": []}, artifact_type="JSON_STRUCTURE_GRAPH", target_modality="GRAPH_OBJECT")
    lineage = build_artifact_lineage_record(source_commitment=source, projections=[projection], transformation_plan=plan, artifact=artifact)
    bad = dict(lineage, source_not_replaced_by_projection=False)
    valid = validate_artifact_lineage_record(lineage)
    rejected = validate_artifact_lineage_record(bad)
    return {"schema": "HHS_ARTIFACT_LINEAGE_REGISTRY_SELF_TEST_V1", "version": VERSION, "ok": bool(valid["ok"] and not rejected["ok"]), "lineage": lineage, "projection_replace_rejection": rejected}

if __name__ == "__main__":
    import json
    print(json.dumps(artifact_lineage_registry_self_test(), indent=2, sort_keys=True, default=str))

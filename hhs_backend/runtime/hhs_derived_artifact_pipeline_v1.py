"""HHS Derived Artifact Pipeline v1."""

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

from hhs_backend.runtime.hhs_cross_modal_transformation_plan_v1 import validate_cross_modal_transformation_plan

DERIVED_ARTIFACT_SCHEMA = "HHS_DERIVED_ARTIFACT_RECORD_V1"


def build_derived_artifact_record(*, transformation_plan: Mapping[str, Any], artifact_payload: Any, artifact_type: str, target_modality: str) -> Dict[str, Any]:
    plan_validation = validate_cross_modal_transformation_plan(transformation_plan)
    artifact = {
        "schema": DERIVED_ARTIFACT_SCHEMA,
        "version": VERSION,
        "artifact_id": _unique("artifact"),
        "artifact_type": artifact_type,
        "target_modality": target_modality.upper(),
        "source_root_hash72s": _list(transformation_plan.get("source_root_hash72s")),
        "projection_root_hash72s": _list(transformation_plan.get("projection_root_hash72s")),
        "transformation_plan_id": transformation_plan.get("plan_id"),
        "transformation_plan_root_hash72": transformation_plan.get("plan_root_hash72"),
        "artifact_payload_hash72": hash72("HHS_DERIVED_ARTIFACT_PAYLOAD_V1", artifact_payload),
        "conformance_status": "ADMIT_DERIVED_ARTIFACT" if plan_validation.get("ok") else "REJECT_DERIVED_ARTIFACT",
        "execution_authorized": False,
        "artifact_execution_authority_inferred": False,
        "reconstruction_recipe": transformation_plan.get("reconstruction_recipe"),
        "authority": AUTHORITY,
        "created_at_unix_ms": _now_ms(),
    }
    artifact["artifact_root_hash72"] = hash72(DERIVED_ARTIFACT_SCHEMA, artifact)
    return artifact


def validate_derived_artifact_record(artifact: Mapping[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []
    if artifact.get("schema") != DERIVED_ARTIFACT_SCHEMA:
        reasons.append("REJECT_ARTIFACT_WITHOUT_LINEAGE")
    if not artifact.get("source_root_hash72s") or not artifact.get("transformation_plan_root_hash72"):
        reasons.append("REJECT_ARTIFACT_WITHOUT_LINEAGE")
    if artifact.get("artifact_execution_authority_inferred") or artifact.get("execution_authorized"):
        reasons.append("REJECT_ARTIFACT_EXECUTION_AUTHORITY_INFERRED")
    if not artifact.get("reconstruction_recipe"):
        reasons.append("REJECT_CROSS_MODAL_PLAN_WITHOUT_RECONSTRUCTION")
    ok = not reasons
    return {"schema": "HHS_DERIVED_ARTIFACT_RECORD_VALIDATION_V1", "version": VERSION, "ok": ok, "status": "ADMIT_DERIVED_ARTIFACT" if ok else "REJECT_DERIVED_ARTIFACT", "reasons": sorted(dict.fromkeys(reasons)), "artifact_id": artifact.get("artifact_id")}


def derived_artifact_pipeline_self_test() -> Dict[str, Any]:
    from hhs_backend.runtime.hhs_cross_modal_transformation_plan_v1 import cross_modal_transformation_plan_self_test
    plan = cross_modal_transformation_plan_self_test()["plan"]
    artifact = build_derived_artifact_record(transformation_plan=plan, artifact_payload={"nodes": []}, artifact_type="HARMONIC_TIME_GRAPH", target_modality="GRAPH_OBJECT")
    bad = dict(artifact, execution_authorized=True, artifact_execution_authority_inferred=True)
    valid = validate_derived_artifact_record(artifact)
    rejected = validate_derived_artifact_record(bad)
    return {"schema": "HHS_DERIVED_ARTIFACT_PIPELINE_SELF_TEST_V1", "version": VERSION, "ok": bool(valid["ok"] and not rejected["ok"]), "artifact": artifact, "execution_authority_rejection": rejected, "doctrine": "VALID_ARTIFACT_DOES_NOT_IMPLY_AUTHORIZED_EXECUTION"}

if __name__ == "__main__":
    import json
    print(json.dumps(derived_artifact_pipeline_self_test(), indent=2, sort_keys=True, default=str))

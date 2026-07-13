"""HHS Universal Artifact Pipeline v1.

Thin orchestration layer for Pass 050: source commitment -> adapter -> projection
-> cross-modal plan -> artifact -> lineage -> reconstruction recipe.
"""

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

from hhs_backend.runtime.hhs_universal_modality_adapter_v1 import adapt_source, build_universal_adapter_contract
from hhs_backend.runtime.hhs_modality_projection_registry_v1 import build_projection_record, validate_projection_record
from hhs_backend.runtime.hhs_cross_modal_transformation_plan_v1 import build_cross_modal_transformation_plan, validate_cross_modal_transformation_plan
from hhs_backend.runtime.hhs_derived_artifact_pipeline_v1 import build_derived_artifact_record, validate_derived_artifact_record
from hhs_backend.runtime.hhs_artifact_lineage_registry_v1 import build_artifact_lineage_record, validate_artifact_lineage_record

PIPELINE_SCHEMA = "HHS_UNIVERSAL_ARTIFACT_PIPELINE_RUN_V1"


def run_universal_artifact_pipeline(*, project_id: str, source_name: str, payload: Any, source_modality: str, projection_type: str, target_modality: str, target_artifact_type: str) -> Dict[str, Any]:
    adaptation = adapt_source(project_id=project_id, source_name=source_name, payload=payload, modality=source_modality)
    source = adaptation["source_commitment"]
    adapter = adaptation["adapter_contract"]
    projection = build_projection_record(source_commitment=source, adapter_contract=adapter, projection_type=projection_type, projection_payload={"derived_from": source.get("source_root_hash72")})
    projection_validation = validate_projection_record(projection)
    plan = build_cross_modal_transformation_plan(source_projection_records=[projection], target_modality=target_modality, target_artifact_type=target_artifact_type)
    plan_validation = validate_cross_modal_transformation_plan(plan)
    artifact = build_derived_artifact_record(transformation_plan=plan, artifact_payload={"artifact_from": plan.get("plan_root_hash72")}, artifact_type=target_artifact_type, target_modality=target_modality)
    artifact_validation = validate_derived_artifact_record(artifact)
    lineage = build_artifact_lineage_record(source_commitment=source, projections=[projection], transformation_plan=plan, artifact=artifact)
    lineage_validation = validate_artifact_lineage_record(lineage)
    ok = bool(adaptation.get("ok") and projection_validation.get("ok") and plan_validation.get("ok") and artifact_validation.get("ok") and lineage_validation.get("ok"))
    run = {
        "schema": PIPELINE_SCHEMA,
        "version": VERSION,
        "pipeline_run_id": _unique("universal-pipeline"),
        "ok": ok,
        "status": "ADMIT_UNIVERSAL_ARTIFACT_PIPELINE" if ok else "REJECT_UNIVERSAL_ARTIFACT_PIPELINE",
        "adaptation": adaptation,
        "projection": projection,
        "projection_validation": projection_validation,
        "transformation_plan": plan,
        "plan_validation": plan_validation,
        "artifact": artifact,
        "artifact_validation": artifact_validation,
        "lineage": lineage,
        "lineage_validation": lineage_validation,
        "source_projection_artifact_separation": "source != projection != artifact != execution_authority",
        "authority": AUTHORITY,
    }
    run["pipeline_run_root_hash72"] = hash72(PIPELINE_SCHEMA, run)
    return run


def universal_artifact_pipeline_self_test() -> Dict[str, Any]:
    pdf = run_universal_artifact_pipeline(project_id="project:pass050", source_name="paper.pdf", payload="%PDF", source_modality="PDF", projection_type="TEXT_PROJECTION", target_modality="HARMONICODE_SOURCE", target_artifact_type="PDF_TEXT_HHS_SOURCE_DRAFT")
    image = run_universal_artifact_pipeline(project_id="project:pass050", source_name="glyph.png", payload="PNG", source_modality="IMAGE", projection_type="VISUAL_FEATURE_PROJECTION", target_modality="GRAPH_OBJECT", target_artifact_type="IMAGE_FEATURE_GRAPH")
    receipt = run_universal_artifact_pipeline(project_id="project:pass050", source_name="receipt.json", payload={"receipt": 1}, source_modality="RUNTIME_RECEIPT", projection_type="RECEIPT_FIELD_PROJECTION", target_modality="GRAPH_OBJECT", target_artifact_type="RECEIPT_GRAPH")
    return {
        "schema": "HHS_UNIVERSAL_ARTIFACT_PIPELINE_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(pdf["ok"] and image["ok"] and receipt["ok"] and not pdf["artifact"].get("execution_authorized")),
        "pipeline_runs": [pdf, image, receipt],
        "doctrine": "SOURCE_NE_PROJECTION_NE_ARTIFACT_NE_EXECUTION_AUTHORITY",
    }

if __name__ == "__main__":
    import json
    print(json.dumps(universal_artifact_pipeline_self_test(), indent=2, sort_keys=True, default=str))

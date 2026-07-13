"""HHS Modality Projection Registry v1."""

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

from hhs_backend.runtime.hhs_universal_modality_adapter_v1 import build_universal_adapter_contract
from hhs_backend.runtime.hhs_modality_reconstruction_recipe_v1 import build_modality_reconstruction_recipe

PROJECTION_SCHEMA = "HHS_MODALITY_PROJECTION_RECORD_V1"


def build_projection_record(*, source_commitment: Mapping[str, Any], adapter_contract: Mapping[str, Any], projection_type: str, projection_payload: Any, lossy: Optional[bool] = None) -> Dict[str, Any]:
    source_root = str(source_commitment.get("source_root_hash72") or "")
    adapter_id = str(adapter_contract.get("adapter_id") or "")
    source_modality = str(source_commitment.get("modality") or adapter_contract.get("source_modality") or "")
    if lossy is None:
        lossy = "LOSSY" in str(adapter_contract.get("loss_profile", "")) or source_modality in {"PDF", "IMAGE", "AUDIO", "VIDEO"}
    projection = {
        "schema": PROJECTION_SCHEMA,
        "version": VERSION,
        "projection_id": _unique("projection"),
        "source_commitment_id": source_commitment.get("source_commitment_id"),
        "source_root_hash72": source_root,
        "source_modality": source_modality,
        "adapter_id": adapter_id,
        "projection_type": projection_type,
        "loss_profile": "LOSSY_DERIVED_PROJECTION" if lossy else "LOSSLESS_DERIVED_PROJECTION",
        "lossy_projection": bool(lossy),
        "lossy_projection_marked": True,
        "projection_replaces_source": False,
        "projection_payload_hash72": hash72("HHS_MODALITY_PROJECTION_PAYLOAD_V1", projection_payload),
        "authority": AUTHORITY,
        "created_at_unix_ms": _now_ms(),
    }
    recipe = build_modality_reconstruction_recipe(
        source_root_hash72=source_root,
        projection_roots=[],
        operations=[{"operation": "reconstruct_projection_from_source_and_adapter", "adapter_id": adapter_id, "projection_type": projection_type}],
    )
    projection["reconstruction_recipe"] = recipe
    projection["projection_root_hash72"] = hash72(PROJECTION_SCHEMA, projection)
    return projection


def validate_projection_record(projection: Mapping[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []
    if projection.get("schema") != PROJECTION_SCHEMA:
        reasons.append("REJECT_PROJECTION_WITHOUT_SCHEMA")
    if not projection.get("source_root_hash72"):
        reasons.append("REJECT_TRANSFORMATION_WITHOUT_SOURCE_COMMITMENT")
    if projection.get("projection_replaces_source"):
        reasons.append("REJECT_PROJECTION_REPLACES_SOURCE")
    if projection.get("lossy_projection") and not projection.get("lossy_projection_marked"):
        reasons.append("REJECT_LOSSY_PROJECTION_UNMARKED")
    if not projection.get("reconstruction_recipe"):
        reasons.append("REJECT_CROSS_MODAL_PLAN_WITHOUT_RECONSTRUCTION")
    ok = not reasons
    return {"schema": "HHS_MODALITY_PROJECTION_RECORD_VALIDATION_V1", "version": VERSION, "ok": ok, "status": "ADMIT_MODALITY_PROJECTION" if ok else "REJECT_MODALITY_PROJECTION", "reasons": sorted(dict.fromkeys(reasons)), "projection_id": projection.get("projection_id")}


def modality_projection_registry_self_test() -> Dict[str, Any]:
    from hhs_backend.runtime.hhs_modality_source_commitment_v1 import build_source_commitment
    source = build_source_commitment(project_id="project:pass050", source_name="paper.pdf", payload="%PDF", modality="PDF")
    adapter = build_universal_adapter_contract("PDF")
    projection = build_projection_record(source_commitment=source, adapter_contract=adapter, projection_type="TEXT_PROJECTION", projection_payload="extracted text")
    bad = dict(projection, lossy_projection_marked=False)
    good_validation = validate_projection_record(projection)
    bad_validation = validate_projection_record(bad)
    return {"schema": "HHS_MODALITY_PROJECTION_REGISTRY_SELF_TEST_V1", "version": VERSION, "ok": bool(good_validation["ok"] and not bad_validation["ok"]), "projection": projection, "lossy_unmarked_rejection": bad_validation}

if __name__ == "__main__":
    import json
    print(json.dumps(modality_projection_registry_self_test(), indent=2, sort_keys=True, default=str))

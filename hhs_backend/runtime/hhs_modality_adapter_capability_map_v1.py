"""HHS Modality Adapter Capability Map v1."""

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

from hhs_backend.runtime.hhs_modality_source_commitment_v1 import SUPPORTED_MODALITIES
from hhs_backend.runtime.hhs_universal_modality_adapter_v1 import list_default_adapter_contracts, validate_adapter_contract

CAPABILITY_MAP_SCHEMA = "HHS_ADAPTER_CAPABILITY_MAP_V1"


def build_adapter_capability_map() -> Dict[str, Any]:
    adapters = list_default_adapter_contracts()
    by_modality = {a["source_modality"]: a for a in adapters}
    capability_map = {
        "schema": CAPABILITY_MAP_SCHEMA,
        "version": VERSION,
        "supported_modalities": SUPPORTED_MODALITIES,
        "adapter_count": len(adapters),
        "adapter_ids": [a["adapter_id"] for a in adapters],
        "capabilities_by_modality": {
            modality: {
                "adapter_id": by_modality[modality]["adapter_id"],
                "projection_types": by_modality[modality]["output_projection_types"],
                "loss_profile": by_modality[modality]["loss_profile"],
                "source_preserved": by_modality[modality]["source_preserved"],
                "private_truth_pipeline_allowed": by_modality[modality]["private_truth_pipeline_allowed"],
            }
            for modality in SUPPORTED_MODALITIES
        },
        "shared_contract": "HHS_UNIVERSAL_MODALITY_ADAPTER_V1",
        "authority": AUTHORITY,
    }
    capability_map["capability_map_root_hash72"] = hash72(CAPABILITY_MAP_SCHEMA, capability_map)
    return capability_map


def validate_adapter_capability_map(capability_map: Mapping[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []
    if capability_map.get("schema") != CAPABILITY_MAP_SCHEMA:
        reasons.append("REJECT_MODALITY_WITHOUT_ADAPTER_CONTRACT")
    modalities = set(capability_map.get("supported_modalities") or [])
    if modalities != set(SUPPORTED_MODALITIES):
        reasons.append("REJECT_MODALITY_WITHOUT_ADAPTER_CONTRACT")
    for modality, info in (capability_map.get("capabilities_by_modality") or {}).items():
        if info.get("private_truth_pipeline_allowed"):
            reasons.append("REJECT_ADAPTER_PRIVATE_TRUTH_PIPELINE")
        if not info.get("source_preserved"):
            reasons.append("REJECT_PROJECTION_REPLACES_SOURCE")
    ok = not reasons
    return {"schema": "HHS_ADAPTER_CAPABILITY_MAP_VALIDATION_V1", "version": VERSION, "ok": ok, "status": "ADMIT_ADAPTER_CAPABILITY_MAP" if ok else "REJECT_ADAPTER_CAPABILITY_MAP", "reasons": sorted(dict.fromkeys(reasons)), "adapter_count": capability_map.get("adapter_count")}


def modality_adapter_capability_map_self_test() -> Dict[str, Any]:
    capability_map = build_adapter_capability_map()
    validation = validate_adapter_capability_map(capability_map)
    missing = dict(capability_map, supported_modalities=["TEXT"])
    rejected = validate_adapter_capability_map(missing)
    return {"schema": "HHS_ADAPTER_CAPABILITY_MAP_SELF_TEST_V1", "version": VERSION, "ok": bool(validation["ok"] and not rejected["ok"]), "capability_map": capability_map, "validation": validation, "missing_modality_rejection": rejected}

if __name__ == "__main__":
    import json
    print(json.dumps(modality_adapter_capability_map_self_test(), indent=2, sort_keys=True, default=str))

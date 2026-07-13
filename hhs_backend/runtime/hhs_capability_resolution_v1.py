"""HHS Capability Resolution v1."""
from __future__ import annotations
from typing import Any, Dict, Mapping, Optional
import uuid
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_capability_contract_v1 import VERSION, AUTHORITY, build_capability_contract, validate_capability_contract
from hhs_backend.runtime.hhs_capability_provider_registry_v1 import build_default_provider_registry, validate_provider_record
RESOLUTION_SCHEMA = "HHS_CAPABILITY_RESOLUTION_V1"
def _unique(prefix: str) -> str: return f"{prefix}:{uuid.uuid4().hex}"

def resolve_capability(capability_class: str, *, project_id: str = "project:default", constraints: Optional[Mapping[str, Any]] = None, registry: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    cap = str(capability_class).upper(); contract = build_capability_contract(cap); contract_validation = validate_capability_contract(contract); registry = dict(registry or build_default_provider_registry())
    candidates = sorted([p for p in list(registry.get("providers") or []) if cap in (p.get("capability_classes") or [])], key=lambda p: str(p.get("provider_id")))
    selected = candidates[0] if candidates else None; provider_validation = validate_provider_record(selected) if selected else {"ok": False, "reasons":["REJECT_UNREGISTERED_CAPABILITY"]}
    ok = bool(contract_validation["ok"] and selected and provider_validation["ok"])
    resolution = {"schema": RESOLUTION_SCHEMA, "version": VERSION, "resolution_id": _unique("resolution"), "project_id": project_id, "capability_class": cap, "capability_contract": contract, "capability_validation": contract_validation, "provider_candidates": [p.get("provider_id") for p in candidates], "selected_provider": selected, "provider_validation": provider_validation, "deterministic_resolution": True, "capability_selection_grants_execution_authority": False, "ok": ok, "status": "ADMIT_CAPABILITY_RESOLUTION" if ok else "REJECT_CAPABILITY_RESOLUTION", "authority": AUTHORITY}
    resolution["resolution_root_hash72"] = hash72(RESOLUTION_SCHEMA, resolution); return resolution

def capability_resolution_self_test() -> Dict[str, Any]:
    resolved = resolve_capability("OCR"); rejected = resolve_capability("UNREGISTERED_CAPABILITY")
    return {"schema":"HHS_CAPABILITY_RESOLUTION_SELF_TEST_V1", "version": VERSION, "ok": bool(resolved["ok"] and not rejected["ok"] and not resolved["capability_selection_grants_execution_authority"]), "resolved": resolved, "rejected": rejected}
if __name__ == "__main__":
    import json; print(json.dumps(capability_resolution_self_test(), indent=2, sort_keys=True, default=str))

"""HHS Capability Fallback Plan v1."""
from __future__ import annotations
from typing import Any, Dict, Iterable, List, Mapping, Optional
import uuid
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_capability_contract_v1 import VERSION, AUTHORITY
from hhs_backend.runtime.hhs_capability_resolution_v1 import resolve_capability
from hhs_backend.runtime.hhs_capability_provider_registry_v1 import build_default_provider_registry
FALLBACK_SCHEMA = "HHS_CAPABILITY_FALLBACK_PLAN_V1"
def _unique(prefix: str) -> str: return f"{prefix}:{uuid.uuid4().hex}"

def build_capability_fallback_plan(capability_class: str, *, project_id: str = "project:default", failed_attempts: Optional[Iterable[Mapping[str, Any]]] = None) -> Dict[str, Any]:
    registry = build_default_provider_registry(); cap = str(capability_class).upper(); resolution = resolve_capability(cap, project_id=project_id, registry=registry)
    providers = [p for p in registry["providers"] if cap in (p.get("capability_classes") or [])]
    plan = {"schema": FALLBACK_SCHEMA, "version": VERSION, "fallback_plan_id": _unique("fallback"), "project_id": project_id, "capability_class": cap, "primary_resolution": resolution, "ordered_provider_ids": [p.get("provider_id") for p in sorted(providers, key=lambda x: str(x.get("provider_id")))], "failed_attempt_history": [dict(x) for x in (failed_attempts or [])], "fallback_preserves_failed_attempt_history": True, "fallback_erases_history": False, "provider_change_preserves_artifact_lineage": True, "authority": AUTHORITY}
    plan["fallback_plan_root_hash72"] = hash72(FALLBACK_SCHEMA, plan); return plan

def validate_capability_fallback_plan(plan: Mapping[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []
    if plan.get("schema") != FALLBACK_SCHEMA or plan.get("fallback_erases_history") or not plan.get("fallback_preserves_failed_attempt_history"): reasons.append("REJECT_FALLBACK_HISTORY_ERASURE")
    if not plan.get("provider_change_preserves_artifact_lineage"): reasons.append("REJECT_PROVIDER_PRIVATE_TRUTH_PIPELINE")
    return {"schema":"HHS_CAPABILITY_FALLBACK_PLAN_VALIDATION_V1", "version": VERSION, "ok": not reasons, "status": "ADMIT_CAPABILITY_FALLBACK_PLAN" if not reasons else "REJECT_CAPABILITY_FALLBACK_PLAN", "reasons": sorted(dict.fromkeys(reasons)), "fallback_plan_id": plan.get("fallback_plan_id")}

def capability_fallback_plan_self_test() -> Dict[str, Any]:
    plan = build_capability_fallback_plan("OCR", project_id="project:pass051", failed_attempts=[{"provider_id":"provider:old", "status":"FAILED"}]); valid = validate_capability_fallback_plan(plan); rejected = validate_capability_fallback_plan(dict(plan, fallback_erases_history=True))
    return {"schema":"HHS_CAPABILITY_FALLBACK_PLAN_SELF_TEST_V1", "version": VERSION, "ok": bool(valid["ok"] and not rejected["ok"]), "plan": plan, "valid": valid, "rejected": rejected}
if __name__ == "__main__":
    import json; print(json.dumps(capability_fallback_plan_self_test(), indent=2, sort_keys=True, default=str))

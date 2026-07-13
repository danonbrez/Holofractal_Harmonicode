"""HHS Universal Capability Fabric v1."""
from __future__ import annotations
from typing import Any, Dict
import uuid
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_capability_contract_v1 import VERSION, AUTHORITY, list_capability_contracts
from hhs_backend.runtime.hhs_capability_provider_registry_v1 import build_default_provider_registry
from hhs_backend.runtime.hhs_provider_execution_proposal_v1 import build_provider_execution_proposal, validate_provider_execution_proposal
from hhs_backend.runtime.hhs_capability_policy_gate_v1 import evaluate_capability_policy_gate
from hhs_backend.runtime.hhs_provider_invocation_receipt_v1 import invoke_provider_with_receipt, validate_provider_invocation_receipt
from hhs_backend.runtime.hhs_provider_result_ingress_v1 import ingress_provider_result
from hhs_backend.runtime.hhs_capability_fallback_plan_v1 import build_capability_fallback_plan
from hhs_backend.runtime.hhs_runtime_canonical_observer_v1 import canonical_observer_status, runtime_canonical_observer_self_test
FABRIC_SCHEMA = "HHS_UNIVERSAL_CAPABILITY_FABRIC_RUN_V1"
def _unique(prefix: str) -> str: return f"{prefix}:{uuid.uuid4().hex}"

def run_universal_capability_fabric(*, project_id: str, capability_class: str, input_payload: Any, output_modality: str = "TEXT", simulated_raw_result: Any = None) -> Dict[str, Any]:
    proposal = build_provider_execution_proposal(capability_class=capability_class, project_id=project_id, input_payload=input_payload)
    proposal_validation = validate_provider_execution_proposal(proposal); policy = evaluate_capability_policy_gate(proposal)
    receipt = invoke_provider_with_receipt(proposal, simulated_raw_result=simulated_raw_result); receipt_validation = validate_provider_invocation_receipt(receipt)
    ingress = ingress_provider_result(receipt, project_id=project_id, output_modality=output_modality)
    fallback = build_capability_fallback_plan(capability_class, project_id=project_id)
    ok = bool(proposal_validation["ok"] and policy["ok"] and receipt_validation["ok"] and ingress["ok"])
    run = {"schema": FABRIC_SCHEMA, "version": VERSION, "fabric_run_id": _unique("capability-fabric"), "ok": ok, "status": "ADMIT_UNIVERSAL_CAPABILITY_FABRIC_RUN" if ok else "REJECT_UNIVERSAL_CAPABILITY_FABRIC_RUN", "project_id": project_id, "capability_class": str(capability_class).upper(), "proposal": proposal, "proposal_validation": proposal_validation, "policy_gate_decision": policy, "provider_invocation_receipt": receipt, "receipt_validation": receipt_validation, "provider_result_ingress": ingress, "fallback_plan": fallback, "provider_never_becomes_canonical_authority": True, "raw_provider_result_reentered_universal_modality_pipeline": bool(ingress.get("ok")), "successful_invocation_does_not_equal_admitted_mutation": True, "authority": AUTHORITY}
    run["fabric_run_root_hash72"] = hash72(FABRIC_SCHEMA, run); return run

def capability_fabric_status() -> Dict[str, Any]:
    return {"schema":"HHS_UNIVERSAL_CAPABILITY_FABRIC_STATUS_V1", "version": VERSION, "ok": True, "canonical_observer": canonical_observer_status(), "capability_contracts": list_capability_contracts(), "provider_registry": build_default_provider_registry(), "doctrine":"provider != capability; capability != authority; provider output != canonical truth; successful invocation != admitted mutation"}

def universal_capability_fabric_self_test() -> Dict[str, Any]:
    run = run_universal_capability_fabric(project_id="project:pass051", capability_class="OCR", input_payload="%PDF", output_modality="TEXT", simulated_raw_result="visible text proposal")
    unregistered = run_universal_capability_fabric(project_id="project:pass051", capability_class="UNREGISTERED_CAPABILITY", input_payload="x", output_modality="TEXT")
    observer = runtime_canonical_observer_self_test()
    return {"schema":"HHS_UNIVERSAL_CAPABILITY_FABRIC_SELF_TEST_V1", "version": VERSION, "ok": bool(run["ok"] and not unregistered["ok"] and observer["ok"]), "run": run, "unregistered_rejection": unregistered, "observer": observer, "capability_count": len(list_capability_contracts()), "provider_count": build_default_provider_registry()["provider_count"]}
if __name__ == "__main__":
    import json; print(json.dumps(universal_capability_fabric_self_test(), indent=2, sort_keys=True, default=str))

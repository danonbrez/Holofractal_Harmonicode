"""HHS Capability Policy Gate v1."""
from __future__ import annotations
from typing import Any, Dict, List, Mapping
import uuid
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_capability_contract_v1 import VERSION, AUTHORITY
from hhs_backend.runtime.hhs_provider_execution_proposal_v1 import build_provider_execution_proposal, validate_provider_execution_proposal
POLICY_GATE_SCHEMA = "HHS_CAPABILITY_POLICY_GATE_DECISION_V1"
def _unique(prefix: str) -> str: return f"{prefix}:{uuid.uuid4().hex}"

def evaluate_capability_policy_gate(proposal: Mapping[str, Any]) -> Dict[str, Any]:
    validation = validate_provider_execution_proposal(proposal); reasons: List[str] = list(validation.get("reasons") or [])
    resolution = proposal.get("capability_resolution") or {}; selected = resolution.get("selected_provider") or {}
    if resolution.get("capability_selection_grants_execution_authority"): reasons.append("REJECT_PROVIDER_SELF_AUTHORIZATION")
    if selected.get("provider_is_canonical_authority"): reasons.append("REJECT_PROVIDER_AS_CANONICAL_AUTHORITY")
    if selected.get("private_truth_pipeline_allowed"): reasons.append("REJECT_PROVIDER_PRIVATE_TRUTH_PIPELINE")
    ok = bool(validation["ok"] and not reasons)
    decision = {"schema": POLICY_GATE_SCHEMA, "version": VERSION, "decision_id": _unique("capability-policy"), "ok": ok, "status": "ADMIT_CAPABILITY_PROVIDER_INVOCATION" if ok else "REJECT_CAPABILITY_PROVIDER_INVOCATION", "reasons": sorted(dict.fromkeys(reasons)), "proposal_id": proposal.get("proposal_id"), "proposal_root_hash72": proposal.get("proposal_root_hash72"), "provider_invocation_authorized": ok, "provider_result_canonical_on_return": False, "mutating_result_requires_separate_admission": True, "authority": AUTHORITY}
    decision["policy_gate_root_hash72"] = hash72(POLICY_GATE_SCHEMA, decision); return decision

def capability_policy_gate_self_test() -> Dict[str, Any]:
    proposal = build_provider_execution_proposal(capability_class="OCR", project_id="project:pass051", input_payload="%PDF"); admitted = evaluate_capability_policy_gate(proposal); rejected = evaluate_capability_policy_gate(dict(proposal, provider_self_authorizes=True))
    return {"schema":"HHS_CAPABILITY_POLICY_GATE_SELF_TEST_V1", "version": VERSION, "ok": bool(admitted["ok"] and not rejected["ok"] and not admitted["provider_result_canonical_on_return"]), "admitted": admitted, "rejected": rejected}
if __name__ == "__main__":
    import json; print(json.dumps(capability_policy_gate_self_test(), indent=2, sort_keys=True, default=str))

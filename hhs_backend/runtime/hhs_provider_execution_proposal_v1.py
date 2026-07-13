"""HHS Provider Execution Proposal v1."""
from __future__ import annotations
from typing import Any, Dict, List, Mapping, Optional
import uuid
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_capability_contract_v1 import VERSION, AUTHORITY
from hhs_backend.runtime.hhs_capability_resolution_v1 import resolve_capability
PROPOSAL_SCHEMA = "HHS_PROVIDER_EXECUTION_PROPOSAL_V1"
def _unique(prefix: str) -> str: return f"{prefix}:{uuid.uuid4().hex}"

def build_provider_execution_proposal(*, capability_class: str, project_id: str, input_payload: Any, requested_operation: str = "provider.invoke", constraints: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    resolution = resolve_capability(capability_class, project_id=project_id, constraints=constraints)
    proposal = {"schema": PROPOSAL_SCHEMA, "version": VERSION, "proposal_id": _unique("proposal"), "project_id": project_id, "requested_operation": requested_operation, "capability_class": str(capability_class).upper(), "capability_resolution": resolution, "selected_provider_id": (resolution.get("selected_provider") or {}).get("provider_id"), "input_payload_root_hash72": hash72("HHS_PROVIDER_EXECUTION_INPUT_PAYLOAD_V1", input_payload), "execution_proposal_only": True, "provider_self_authorizes": False, "successful_invocation_implies_admitted_mutation": False, "raw_provider_result_is_canonical": False, "requires_authority_admission": True, "authority": AUTHORITY}
    proposal["proposal_root_hash72"] = hash72(PROPOSAL_SCHEMA, proposal); return proposal

def validate_provider_execution_proposal(proposal: Mapping[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []
    if proposal.get("schema") != PROPOSAL_SCHEMA or not proposal.get("proposal_root_hash72"): reasons.append("REJECT_UNWITNESSED_PROVIDER_INVOCATION")
    if not (proposal.get("capability_resolution") or {}).get("ok"): reasons.append("REJECT_UNREGISTERED_CAPABILITY")
    if proposal.get("provider_self_authorizes"): reasons.append("REJECT_PROVIDER_SELF_AUTHORIZATION")
    if proposal.get("raw_provider_result_is_canonical"): reasons.append("REJECT_RAW_PROVIDER_OUTPUT_AS_CANONICAL_SOURCE")
    if proposal.get("successful_invocation_implies_admitted_mutation"): reasons.append("REJECT_MUTATION_FROM_NON_ADMITTED_RESULT")
    return {"schema":"HHS_PROVIDER_EXECUTION_PROPOSAL_VALIDATION_V1", "version": VERSION, "ok": not reasons, "status": "ADMIT_PROVIDER_EXECUTION_PROPOSAL" if not reasons else "REJECT_PROVIDER_EXECUTION_PROPOSAL", "reasons": sorted(dict.fromkeys(reasons)), "proposal_id": proposal.get("proposal_id"), "proposal_root_hash72": proposal.get("proposal_root_hash72")}

def provider_execution_proposal_self_test() -> Dict[str, Any]:
    proposal = build_provider_execution_proposal(capability_class="OCR", project_id="project:pass051", input_payload="%PDF"); valid = validate_provider_execution_proposal(proposal); bad = dict(proposal, raw_provider_result_is_canonical=True)
    return {"schema":"HHS_PROVIDER_EXECUTION_PROPOSAL_SELF_TEST_V1", "version": VERSION, "ok": bool(valid["ok"] and not validate_provider_execution_proposal(bad)["ok"]), "proposal": proposal, "valid": valid, "rejected": validate_provider_execution_proposal(bad)}
if __name__ == "__main__":
    import json; print(json.dumps(provider_execution_proposal_self_test(), indent=2, sort_keys=True, default=str))

"""HHS Provider Invocation Receipt v1."""
from __future__ import annotations
from typing import Any, Dict, List, Mapping
import time, uuid
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_capability_contract_v1 import VERSION, AUTHORITY
from hhs_backend.runtime.hhs_provider_execution_proposal_v1 import build_provider_execution_proposal
from hhs_backend.runtime.hhs_capability_policy_gate_v1 import evaluate_capability_policy_gate
INVOCATION_RECEIPT_SCHEMA = "HHS_PROVIDER_INVOCATION_RECEIPT_V1"
def _unique(prefix: str) -> str: return f"{prefix}:{uuid.uuid4().hex}"
def _now_ms() -> int: return int(time.time()*1000)

def invoke_provider_with_receipt(proposal: Mapping[str, Any], *, simulated_raw_result: Any = None) -> Dict[str, Any]:
    decision = evaluate_capability_policy_gate(proposal); raw_result = simulated_raw_result if simulated_raw_result is not None else {"provider_output": f"raw result for {proposal.get('capability_class')}", "provider_id": proposal.get("selected_provider_id")}
    receipt = {"schema": INVOCATION_RECEIPT_SCHEMA, "version": VERSION, "invocation_id": _unique("provider-invocation"), "ok": bool(decision.get("ok")), "status": "PROVIDER_INVOCATION_RECORDED" if decision.get("ok") else "REJECT_UNWITNESSED_PROVIDER_INVOCATION", "proposal_id": proposal.get("proposal_id"), "proposal_root_hash72": proposal.get("proposal_root_hash72"), "policy_gate_decision": decision, "provider_id": proposal.get("selected_provider_id"), "capability_class": proposal.get("capability_class"), "raw_provider_result": raw_result, "raw_provider_result_hash72": hash72("HHS_RAW_PROVIDER_RESULT_V1", raw_result), "raw_result_is_canonical": False, "raw_result_must_reenter_universal_modality_pipeline": True, "admitted_mutation": False, "authority": AUTHORITY, "created_at_unix_ms": _now_ms()}
    receipt["provider_invocation_receipt_hash72"] = hash72(INVOCATION_RECEIPT_SCHEMA, receipt); return receipt

def validate_provider_invocation_receipt(receipt: Mapping[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []
    if receipt.get("schema") != INVOCATION_RECEIPT_SCHEMA or not receipt.get("provider_invocation_receipt_hash72"): reasons.append("REJECT_UNWITNESSED_PROVIDER_INVOCATION")
    if receipt.get("raw_result_is_canonical"): reasons.append("REJECT_RAW_PROVIDER_OUTPUT_AS_CANONICAL_SOURCE")
    if receipt.get("admitted_mutation"): reasons.append("REJECT_MUTATION_FROM_NON_ADMITTED_RESULT")
    if not receipt.get("raw_result_must_reenter_universal_modality_pipeline"): reasons.append("REJECT_PROVIDER_PRIVATE_TRUTH_PIPELINE")
    ok = not reasons and bool(receipt.get("ok"))
    return {"schema":"HHS_PROVIDER_INVOCATION_RECEIPT_VALIDATION_V1", "version": VERSION, "ok": ok, "status": "ADMIT_PROVIDER_INVOCATION_RECEIPT" if ok else "REJECT_PROVIDER_INVOCATION_RECEIPT", "reasons": sorted(dict.fromkeys(reasons)), "invocation_id": receipt.get("invocation_id")}

def provider_invocation_receipt_self_test() -> Dict[str, Any]:
    proposal = build_provider_execution_proposal(capability_class="OCR", project_id="project:pass051", input_payload="%PDF"); receipt = invoke_provider_with_receipt(proposal, simulated_raw_result="visible text proposal"); bad = dict(receipt, raw_result_is_canonical=True)
    return {"schema":"HHS_PROVIDER_INVOCATION_RECEIPT_SELF_TEST_V1", "version": VERSION, "ok": bool(validate_provider_invocation_receipt(receipt)["ok"] and not validate_provider_invocation_receipt(bad)["ok"]), "receipt": receipt, "valid": validate_provider_invocation_receipt(receipt), "rejected": validate_provider_invocation_receipt(bad)}
if __name__ == "__main__":
    import json; print(json.dumps(provider_invocation_receipt_self_test(), indent=2, sort_keys=True, default=str))

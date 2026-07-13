"""HHS Provider Result Ingress v1."""
from __future__ import annotations
from typing import Any, Dict, Mapping
import uuid
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_capability_contract_v1 import VERSION, AUTHORITY
from hhs_backend.runtime.hhs_provider_execution_proposal_v1 import build_provider_execution_proposal
from hhs_backend.runtime.hhs_provider_invocation_receipt_v1 import invoke_provider_with_receipt, validate_provider_invocation_receipt
from hhs_backend.runtime.hhs_universal_artifact_pipeline_v1 import run_universal_artifact_pipeline
from hhs_backend.runtime.hhs_runtime_canonical_observer_v1 import observe_external_surface, admit_runtime_identity
RESULT_INGRESS_SCHEMA = "HHS_PROVIDER_RESULT_INGRESS_V1"
def _unique(prefix: str) -> str: return f"{prefix}:{uuid.uuid4().hex}"

def ingress_provider_result(receipt: Mapping[str, Any], *, project_id: str = "project:default", output_modality: str = "TEXT", target_artifact_type: str = "PROVIDER_RESULT_ARTIFACT") -> Dict[str, Any]:
    receipt_validation = validate_provider_invocation_receipt(receipt); raw_result = receipt.get("raw_provider_result")
    observation = observe_external_surface(surface_type="PROVIDER", surface_id=str(receipt.get("provider_id")), payload=raw_result, declared_role="RAW_PROVIDER_RESULT")
    pipeline = run_universal_artifact_pipeline(project_id=project_id, source_name=f"{receipt.get('invocation_id','provider-result')}.provider-result", payload=raw_result, source_modality=output_modality, projection_type="PROVIDER_RESULT_PROJECTION", target_modality=output_modality, target_artifact_type=target_artifact_type) if receipt_validation.get("ok") else {"schema":"HHS_UNIVERSAL_ARTIFACT_PIPELINE_REJECTION_V1", "ok":False, "status":"REJECT_UNWITNESSED_PROVIDER_INVOCATION"}
    admission = admit_runtime_identity(observation=observation, translated_record=pipeline, authority_decision={"ok": bool(pipeline.get("ok")), "status": pipeline.get("status")})
    ok = bool(receipt_validation.get("ok") and pipeline.get("ok") and admission.get("ok"))
    ingress = {"schema": RESULT_INGRESS_SCHEMA, "version": VERSION, "provider_result_ingress_id": _unique("provider-result-ingress"), "ok": ok, "status": "ADMIT_PROVIDER_RESULT_INGRESS" if ok else "REJECT_PROVIDER_RESULT_INGRESS", "receipt_validation": receipt_validation, "observation": observation, "universal_modality_pipeline": pipeline, "canonical_identity_admission": admission, "raw_provider_output_replaced_source": False, "provider_output_is_canonical_without_runtime_admission": False, "authority": AUTHORITY}
    ingress["provider_result_ingress_root_hash72"] = hash72(RESULT_INGRESS_SCHEMA, ingress); return ingress

def provider_result_ingress_self_test() -> Dict[str, Any]:
    proposal = build_provider_execution_proposal(capability_class="OCR", project_id="project:pass051", input_payload="%PDF"); receipt = invoke_provider_with_receipt(proposal, simulated_raw_result="visible text proposal"); ingress = ingress_provider_result(receipt, project_id="project:pass051", output_modality="TEXT"); rejected = ingress_provider_result(dict(receipt, raw_result_is_canonical=True), project_id="project:pass051", output_modality="TEXT")
    return {"schema":"HHS_PROVIDER_RESULT_INGRESS_SELF_TEST_V1", "version": VERSION, "ok": bool(ingress["ok"] and not rejected["ok"]), "ingress": ingress, "rejected": rejected, "doctrine":"provider output -> Runtime ingress -> modality pipeline -> witnessed derived result"}
if __name__ == "__main__":
    import json; print(json.dumps(provider_result_ingress_self_test(), indent=2, sort_keys=True, default=str))

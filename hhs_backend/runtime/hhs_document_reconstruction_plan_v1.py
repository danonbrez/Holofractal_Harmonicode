"""Document reconstruction plan v1."""
from __future__ import annotations
from typing import Any, Dict, Iterable, Mapping
import time, uuid
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_document_provider_contract_v1 import VERSION, AUTHORITY
SCHEMA="HHS_DOCUMENT_RECONSTRUCTION_PLAN_V1"
def _unique(prefix:str)->str: return f"{prefix}:{uuid.uuid4().hex}"
def _now_ms()->int: return int(time.time()*1000)

def build_document_reconstruction_plan(*, source_commitment:Mapping[str,Any], projection_bundle:Mapping[str,Any], perception_receipt:Mapping[str,Any], observation_roots:Iterable[str]) -> Dict[str,Any]:
    plan={"schema":SCHEMA,"version":VERSION,"plan_id":_unique("document-reconstruction"),"source_commitment_root_hash72":source_commitment.get("source_root_hash72") or source_commitment.get("commitment_root_hash72"),"bundle_root_hash72":projection_bundle.get("bundle_root_hash72"),"perception_receipt_root_hash72":perception_receipt.get("receipt_root_hash72"),"observation_roots":list(observation_roots),"steps":["restore original source commitment","replay provider observation roots","rebuild projection bundle","re-evaluate fusion/disagreement states","verify perception receipt"],"expanded_metadata_retained":False,"source_preserved":True,"projection_replaces_source":False,"created_at_unix_ms":_now_ms(),"authority":AUTHORITY}
    plan["reconstruction_plan_root_hash72"]=hash72(SCHEMA, plan); return plan

def validate_document_reconstruction_plan(plan:Mapping[str,Any])->Dict[str,Any]:
    reasons=[]
    if not plan.get("source_commitment_root_hash72") or not plan.get("perception_receipt_root_hash72"): reasons.append("REJECT_DOCUMENT_PROJECTION_WITHOUT_RECONSTRUCTION")
    if plan.get("expanded_metadata_retained"): reasons.append("REJECT_WORKSPACE_PERSISTENCE_EXPANDED_METADATA")
    if plan.get("projection_replaces_source") or not plan.get("source_preserved"): reasons.append("REJECT_PROJECTION_REPLACES_SOURCE")
    ok=not reasons; out={"schema":"HHS_DOCUMENT_RECONSTRUCTION_PLAN_VALIDATION_V1","version":VERSION,"ok":ok,"status":"ADMIT_DOCUMENT_RECONSTRUCTION_PLAN" if ok else "REJECT_DOCUMENT_RECONSTRUCTION_PLAN","reasons":sorted(set(reasons)),"reconstruction_plan_root_hash72":plan.get("reconstruction_plan_root_hash72"),"authority":AUTHORITY}; out["validation_root_hash72"]=hash72(out["schema"], out); return out

def document_reconstruction_plan_self_test()->Dict[str,Any]:
    source={"source_root_hash72":hash72("SOURCE","doc")}; bundle={"bundle_root_hash72":hash72("BUNDLE","b")}; receipt={"receipt_root_hash72":hash72("RECEIPT","r")}; plan=build_document_reconstruction_plan(source_commitment=source,projection_bundle=bundle,perception_receipt=receipt,observation_roots=["o1"]); bad=dict(plan, expanded_metadata_retained=True)
    return {"schema":"HHS_DOCUMENT_RECONSTRUCTION_PLAN_SELF_TEST_V1","version":VERSION,"ok":bool(validate_document_reconstruction_plan(plan)["ok"] and not validate_document_reconstruction_plan(bad)["ok"]),"plan":plan,"bad_rejection":validate_document_reconstruction_plan(bad)}
if __name__=="__main__":
    import json; print(json.dumps(document_reconstruction_plan_self_test(), indent=2, sort_keys=True, default=str))

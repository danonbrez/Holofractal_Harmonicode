"""Document perception receipt v1."""
from __future__ import annotations
from typing import Any, Dict, Mapping
import time, uuid
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_document_provider_contract_v1 import VERSION, AUTHORITY
SCHEMA="HHS_DOCUMENT_PERCEPTION_RECEIPT_V1"
def _unique(prefix:str)->str: return f"{prefix}:{uuid.uuid4().hex}"
def _now_ms()->int: return int(time.time()*1000)

def build_document_perception_receipt(*, source_commitment:Mapping[str,Any], projection_bundle:Mapping[str,Any], fusion_record:Mapping[str,Any], status:str="ADMIT_DOCUMENT_PERCEPTION") -> Dict[str,Any]:
    receipt={"schema":SCHEMA,"version":VERSION,"receipt_id":_unique("document-perception-receipt"),"status":status,"source_commitment_root_hash72":source_commitment.get("source_root_hash72") or source_commitment.get("commitment_root_hash72"),"bundle_root_hash72":projection_bundle.get("bundle_root_hash72"),"fusion_root_hash72":fusion_record.get("fusion_root_hash72"),"pre_state_root_hash72":source_commitment.get("source_root_hash72") or source_commitment.get("commitment_root_hash72"),"transformation_root_hash72":hash72("HHS_DOCUMENT_PERCEPTION_TRANSFORMATION_V1", {"bundle":projection_bundle.get("bundle_root_hash72"),"fusion":fusion_record.get("fusion_root_hash72")}),"post_state_root_hash72":projection_bundle.get("bundle_root_hash72"),"document_provider_as_authority":False,"document_identity_replaced_by_projection":False,"created_at_unix_ms":_now_ms(),"authority":AUTHORITY}
    receipt["receipt_root_hash72"]=hash72(SCHEMA, receipt); return receipt

def validate_document_perception_receipt(receipt:Mapping[str,Any])->Dict[str,Any]:
    reasons=[]
    for key in ["source_commitment_root_hash72","bundle_root_hash72","fusion_root_hash72","pre_state_root_hash72","transformation_root_hash72","post_state_root_hash72"]:
        if not receipt.get(key): reasons.append("REJECT_DOCUMENT_PROJECTION_WITHOUT_RECONSTRUCTION")
    if receipt.get("document_provider_as_authority"): reasons.append("REJECT_DOCUMENT_PROVIDER_AS_AUTHORITY")
    if receipt.get("document_identity_replaced_by_projection"): reasons.append("REJECT_PROJECTION_REPLACES_SOURCE")
    ok=not reasons; out={"schema":"HHS_DOCUMENT_PERCEPTION_RECEIPT_VALIDATION_V1","version":VERSION,"ok":ok,"status":"ADMIT_DOCUMENT_PERCEPTION_RECEIPT" if ok else "REJECT_DOCUMENT_PERCEPTION_RECEIPT","reasons":sorted(set(reasons)),"receipt_root_hash72":receipt.get("receipt_root_hash72"),"authority":AUTHORITY}; out["validation_root_hash72"]=hash72(out["schema"], out); return out

def document_perception_receipt_self_test()->Dict[str,Any]:
    source={"source_root_hash72":hash72("SOURCE","doc")}; bundle={"bundle_root_hash72":hash72("BUNDLE","b")}; fusion={"fusion_root_hash72":hash72("FUSION","f")}; receipt=build_document_perception_receipt(source_commitment=source,projection_bundle=bundle,fusion_record=fusion); bad=dict(receipt, document_provider_as_authority=True)
    return {"schema":"HHS_DOCUMENT_PERCEPTION_RECEIPT_SELF_TEST_V1","version":VERSION,"ok":bool(validate_document_perception_receipt(receipt)["ok"] and not validate_document_perception_receipt(bad)["ok"]),"receipt":receipt,"bad_rejection":validate_document_perception_receipt(bad)}
if __name__=="__main__":
    import json; print(json.dumps(document_perception_receipt_self_test(), indent=2, sort_keys=True, default=str))

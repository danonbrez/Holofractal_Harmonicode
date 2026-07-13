"""Document projection bundle v1."""
from __future__ import annotations
from typing import Any, Dict, Iterable, Mapping
import time, uuid
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_document_provider_contract_v1 import VERSION, AUTHORITY
SCHEMA="HHS_DOCUMENT_PROJECTION_BUNDLE_V1"
def _unique(prefix:str)->str: return f"{prefix}:{uuid.uuid4().hex}"
def _now_ms()->int: return int(time.time()*1000)

def build_document_projection_bundle(*, source_commitment:Mapping[str,Any], observations:Iterable[Mapping[str,Any]], fusion_record:Mapping[str,Any]) -> Dict[str,Any]:
    obs=[dict(o) for o in observations]
    projection_records=[]
    for o in obs:
        projection_records.append({"projection_type":o.get("projection_type"),"observation_root_hash72":o.get("observation_root_hash72"),"provider_id":o.get("provider_id"),"loss_profile":o.get("loss_profile"),"projection_replaces_source":False})
    bundle={"schema":SCHEMA,"version":VERSION,"bundle_id":_unique("document-projection-bundle"),"source_commitment_root_hash72":source_commitment.get("source_root_hash72") or source_commitment.get("commitment_root_hash72"),"projection_records":projection_records,"fusion_root_hash72":fusion_record.get("fusion_root_hash72"),"source_remains_distinct_from_projections":True,"document_graph_projection_available":True,"created_at_unix_ms":_now_ms(),"authority":AUTHORITY}
    bundle["bundle_root_hash72"]=hash72(SCHEMA, bundle); return bundle

def validate_document_projection_bundle(bundle:Mapping[str,Any])->Dict[str,Any]:
    reasons=[]
    if not bundle.get("source_commitment_root_hash72"): reasons.append("REJECT_DOCUMENT_FUSION_WITHOUT_PROVENANCE")
    if not bundle.get("fusion_root_hash72"): reasons.append("REJECT_DOCUMENT_FUSION_WITHOUT_PROVENANCE")
    if any(p.get("projection_replaces_source") for p in bundle.get("projection_records",[])): reasons.append("REJECT_PROJECTION_REPLACES_SOURCE")
    if not bundle.get("source_remains_distinct_from_projections"): reasons.append("REJECT_PROJECTION_REPLACES_SOURCE")
    ok=not reasons; out={"schema":"HHS_DOCUMENT_PROJECTION_BUNDLE_VALIDATION_V1","version":VERSION,"ok":ok,"status":"ADMIT_DOCUMENT_PROJECTION_BUNDLE" if ok else "REJECT_DOCUMENT_PROJECTION_BUNDLE","reasons":sorted(set(reasons)),"bundle_root_hash72":bundle.get("bundle_root_hash72"),"authority":AUTHORITY}; out["validation_root_hash72"]=hash72(out["schema"], out); return out

def document_projection_bundle_self_test()->Dict[str,Any]:
    source={"source_root_hash72":hash72("SOURCE","doc")}; obs={"projection_type":"PDF_NATIVE_TEXT_PROJECTION","observation_root_hash72":hash72("OBS","native"),"provider_id":"provider:pdf-native-text","loss_profile":"DECLARED"}; fusion={"fusion_root_hash72":hash72("FUSION","f")}; bundle=build_document_projection_bundle(source_commitment=source,observations=[obs],fusion_record=fusion); bad=dict(bundle, source_remains_distinct_from_projections=False)
    return {"schema":"HHS_DOCUMENT_PROJECTION_BUNDLE_SELF_TEST_V1","version":VERSION,"ok":bool(validate_document_projection_bundle(bundle)["ok"] and not validate_document_projection_bundle(bad)["ok"]),"bundle":bundle,"bad_rejection":validate_document_projection_bundle(bad)}
if __name__=="__main__":
    import json; print(json.dumps(document_projection_bundle_self_test(), indent=2, sort_keys=True, default=str))

"""Document image-region provider v1."""
from __future__ import annotations
from typing import Any, Dict, Iterable, Mapping, Optional
import time, uuid
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_document_provider_contract_v1 import VERSION, AUTHORITY, build_document_provider_contract, validate_document_provider_contract
SCHEMA="HHS_DOCUMENT_IMAGE_REGION_PROVIDER_OBSERVATION_V1"
def _unique(prefix:str)->str: return f"{prefix}:{uuid.uuid4().hex}"
def _now_ms()->int: return int(time.time()*1000)

def observe_document_image_regions(*, source_commitment:Mapping[str,Any], payload:Any, page_geometry:Optional[Mapping[str,Any]]=None, region_hints:Optional[Iterable[Mapping[str,Any]]]=None)->Dict[str,Any]:
    hints=list(region_hints or []) or [{"page_index":0,"region_type":"FULL_PAGE_IMAGE","box":{"x":0,"y":0,"width":1,"height":1}}]
    regions=[]
    payload_root=hash72("HHS_DOCUMENT_REGION_PAYLOAD_V1", str(payload)[:1024])
    for i,hint in enumerate(hints):
        region={"region_id":f"region:{i}","page_index":int(hint.get("page_index",0)),"region_type":str(hint.get("region_type","IMAGE_REGION")),"box":dict(hint.get("box") or {"x":0,"y":0,"width":1,"height":1}),"source_payload_root_hash72":payload_root,"region_is_document_identity":False}
        region["region_root_hash72"]=hash72("HHS_DOCUMENT_IMAGE_REGION_RECORD_V1", region); regions.append(region)
    obs={"schema":SCHEMA,"version":VERSION,"observation_id":_unique("document-image-regions"),"provider_id":"provider:document-image-region","source_commitment_root_hash72":source_commitment.get("source_root_hash72") or source_commitment.get("commitment_root_hash72"),"page_geometry_root_hash72":page_geometry.get("observation_root_hash72") if page_geometry else None,"projection_type":"PAGE_IMAGE_REGION_PROJECTION","loss_profile":"REGION_COMMITMENT_LOSSLESS_FOR_BOUNDING_BOX_AND_SOURCE_ROOT__VISUAL_CONTENT_REQUIRES_SOURCE_RECONSTRUCTION","regions":regions,"provider_is_document_authority":False,"created_at_unix_ms":_now_ms(),"authority":AUTHORITY}
    obs["observation_root_hash72"]=hash72(SCHEMA, obs); return obs

def validate_document_image_region_observation(observation:Mapping[str,Any])->Dict[str,Any]:
    reasons=[]
    if observation.get("provider_is_document_authority"): reasons.append("REJECT_DOCUMENT_PROVIDER_AS_AUTHORITY")
    if any(r.get("region_is_document_identity") for r in observation.get("regions",[])): reasons.append("REJECT_PROJECTION_AS_CANONICAL_IDENTITY")
    if not observation.get("source_commitment_root_hash72"): reasons.append("REJECT_TABLE_EXTRACTION_WITHOUT_REGION_SOURCE")
    ok=not reasons; out={"schema":"HHS_DOCUMENT_IMAGE_REGION_VALIDATION_V1","version":VERSION,"ok":ok,"status":"ADMIT_DOCUMENT_IMAGE_REGION_OBSERVATION" if ok else "REJECT_DOCUMENT_IMAGE_REGION_OBSERVATION","reasons":sorted(set(reasons)),"observation_root_hash72":observation.get("observation_root_hash72"),"authority":AUTHORITY}; out["validation_root_hash72"]=hash72(out["schema"], out); return out

def document_image_region_provider_self_test()->Dict[str,Any]:
    source={"source_root_hash72":hash72("SOURCE","image")}; contract=build_document_provider_contract(provider_id="provider:document-image-region", capability_class="IMAGE_ANALYSIS", observed_modalities=["PDF","IMAGE"], projection_types=["PAGE_IMAGE_REGION_PROJECTION"]); obs=observe_document_image_regions(source_commitment=source,payload="image"); bad=dict(obs, regions=[dict(obs["regions"][0], region_is_document_identity=True)])
    return {"schema":"HHS_DOCUMENT_IMAGE_REGION_PROVIDER_SELF_TEST_V1","version":VERSION,"ok":bool(validate_document_provider_contract(contract)["ok"] and validate_document_image_region_observation(obs)["ok"] and not validate_document_image_region_observation(bad)["ok"]),"contract":contract,"observation":obs,"bad_rejection":validate_document_image_region_observation(bad)}
if __name__=="__main__":
    import json; print(json.dumps(document_image_region_provider_self_test(), indent=2, sort_keys=True, default=str))

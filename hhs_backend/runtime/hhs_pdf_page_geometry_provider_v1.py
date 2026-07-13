"""Deterministic PDF page geometry provider v1."""
from __future__ import annotations
from typing import Any, Dict, Mapping
import time, uuid
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_document_provider_contract_v1 import VERSION, AUTHORITY, build_document_provider_contract, validate_document_provider_contract
SCHEMA="HHS_PDF_PAGE_GEOMETRY_PROVIDER_OBSERVATION_V1"
def _unique(prefix:str)->str: return f"{prefix}:{uuid.uuid4().hex}"
def _now_ms()->int: return int(time.time()*1000)

def observe_pdf_page_geometry(*, source_commitment: Mapping[str, Any], payload: Any, page_count_hint:int=1, width:float=612.0, height:float=792.0)->Dict[str,Any]:
    pages=[]
    for i in range(max(1,int(page_count_hint or 1))):
        page={"page_index":i,"box":{"x":0,"y":0,"width":width,"height":height},"coordinate_system":"PDF_POINTS_TOP_LEFT_NORMALIZED_BY_PROVIDER","geometry_is_document_identity":False}
        page["page_geometry_root_hash72"]=hash72("HHS_PDF_PAGE_GEOMETRY_RECORD_V1", page); pages.append(page)
    obs={"schema":SCHEMA,"version":VERSION,"observation_id":_unique("pdf-page-geometry"),"provider_id":"provider:pdf-page-geometry","source_commitment_root_hash72":source_commitment.get("source_root_hash72") or source_commitment.get("commitment_root_hash72"),"projection_type":"PAGE_LAYOUT_PROJECTION","loss_profile":"LOSSLESS_FOR_DECLARED_BOUNDING_BOXES_ONLY__DOES_NOT_CAPTURE_COMPLETE_DOCUMENT_SEMANTICS","page_count":len(pages),"pages":pages,"provider_is_document_authority":False,"created_at_unix_ms":_now_ms(),"authority":AUTHORITY}
    obs["observation_root_hash72"]=hash72(SCHEMA, obs); return obs

def validate_pdf_page_geometry_observation(observation:Mapping[str,Any])->Dict[str,Any]:
    reasons=[]
    if observation.get("provider_is_document_authority"): reasons.append("REJECT_DOCUMENT_PROVIDER_AS_AUTHORITY")
    if any(p.get("geometry_is_document_identity") for p in observation.get("pages",[])): reasons.append("REJECT_PROJECTION_AS_CANONICAL_IDENTITY")
    if not observation.get("loss_profile"): reasons.append("REJECT_UNMARKED_DOCUMENT_EXTRACTION_LOSS")
    ok=not reasons; out={"schema":"HHS_PDF_PAGE_GEOMETRY_VALIDATION_V1","version":VERSION,"ok":ok,"status":"ADMIT_PAGE_GEOMETRY_OBSERVATION" if ok else "REJECT_PAGE_GEOMETRY_OBSERVATION","reasons":sorted(set(reasons)),"observation_root_hash72":observation.get("observation_root_hash72"),"authority":AUTHORITY}; out["validation_root_hash72"]=hash72(out["schema"], out); return out

def pdf_page_geometry_provider_self_test()->Dict[str,Any]:
    source={"source_root_hash72":hash72("SOURCE","%PDF")}; contract=build_document_provider_contract(provider_id="provider:pdf-page-geometry", capability_class="DOCUMENT_EXTRACTION", observed_modalities=["PDF"], projection_types=["PAGE_LAYOUT_PROJECTION"]); obs=observe_pdf_page_geometry(source_commitment=source,payload="%PDF",page_count_hint=2); bad=dict(obs, provider_is_document_authority=True)
    return {"schema":"HHS_PDF_PAGE_GEOMETRY_PROVIDER_SELF_TEST_V1","version":VERSION,"ok":bool(validate_document_provider_contract(contract)["ok"] and validate_pdf_page_geometry_observation(obs)["ok"] and not validate_pdf_page_geometry_observation(bad)["ok"]),"contract":contract,"observation":obs,"bad_rejection":validate_pdf_page_geometry_observation(bad)}
if __name__=="__main__":
    import json; print(json.dumps(pdf_page_geometry_provider_self_test(), indent=2, sort_keys=True, default=str))

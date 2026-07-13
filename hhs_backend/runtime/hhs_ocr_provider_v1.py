"""Deterministic OCR provider v1.

OCR output is a text projection proposal from an image region, never the source
or the document authority.
"""
from __future__ import annotations
from typing import Any, Dict, Iterable, Mapping, Optional
import re, time, uuid
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_document_provider_contract_v1 import VERSION, AUTHORITY, build_document_provider_contract, validate_document_provider_contract
SCHEMA="HHS_OCR_PROVIDER_OBSERVATION_V1"
def _unique(prefix:str)->str: return f"{prefix}:{uuid.uuid4().hex}"
def _now_ms()->int: return int(time.time()*1000)

def _deterministic_ocr(payload:Any, hint:str="") -> str:
    text = hint or str(payload)
    # Simulate OCR deterministically: keep alphanumeric runs, collapse whitespace, bound output.
    tokens = re.findall(r"[A-Za-z0-9_\-.,:;#/+={}()\[\]]+", text)
    return " ".join(tokens)[:2048] or "UNRESOLVED_OCR_TEXT_PROJECTION"

def run_ocr_on_regions(*, source_commitment:Mapping[str,Any], image_regions:Mapping[str,Any], payload:Any, text_hint:str="") -> Dict[str,Any]:
    projections=[]
    for region in image_regions.get("regions",[]) or [{"region_id":"region:0","page_index":0,"region_root_hash72":hash72("REGION",payload)}]:
        text=_deterministic_ocr(payload, text_hint)
        projection={"region_id":region.get("region_id"),"page_index":region.get("page_index",0),"region_root_hash72":region.get("region_root_hash72"),"ocr_text":text,"ocr_text_root_hash72":hash72("HHS_OCR_TEXT_REGION_PROJECTION_V1", {"region":region.get("region_root_hash72"),"text":text}),"confidence":"DETERMINISTIC_BASELINE_NO_STATISTICAL_CONFIDENCE","ocr_text_is_document_source":False}
        projections.append(projection)
    obs={"schema":SCHEMA,"version":VERSION,"observation_id":_unique("ocr-observation"),"provider_id":"provider:deterministic-ocr","source_commitment_root_hash72":source_commitment.get("source_root_hash72") or source_commitment.get("commitment_root_hash72"),"image_region_observation_root_hash72":image_regions.get("observation_root_hash72"),"projection_type":"OCR_TEXT_PROJECTION","loss_profile":"LOSSY_TEXT_PROJECTION_FROM_IMAGE_REGION__SOURCE_IMAGE_PRESERVED","provider_is_document_authority":False,"ocr_text_is_document_source":False,"ocr_region_projections":projections,"created_at_unix_ms":_now_ms(),"authority":AUTHORITY}
    obs["observation_root_hash72"]=hash72(SCHEMA, obs); return obs

def validate_ocr_observation(observation:Mapping[str,Any]) -> Dict[str,Any]:
    reasons=[]
    if observation.get("provider_is_document_authority"): reasons.append("REJECT_DOCUMENT_PROVIDER_AS_AUTHORITY")
    if observation.get("ocr_text_is_document_source") or any(p.get("ocr_text_is_document_source") for p in observation.get("ocr_region_projections",[])): reasons.append("REJECT_OCR_TEXT_AS_DOCUMENT_SOURCE")
    if not observation.get("image_region_observation_root_hash72"): reasons.append("REJECT_TABLE_EXTRACTION_WITHOUT_REGION_SOURCE")
    if not observation.get("loss_profile") or "LOSSY" not in str(observation.get("loss_profile")): reasons.append("REJECT_UNMARKED_DOCUMENT_EXTRACTION_LOSS")
    ok=not reasons; out={"schema":"HHS_OCR_PROVIDER_VALIDATION_V1","version":VERSION,"ok":ok,"status":"ADMIT_OCR_OBSERVATION" if ok else "REJECT_OCR_OBSERVATION","reasons":sorted(set(reasons)),"observation_root_hash72":observation.get("observation_root_hash72"),"authority":AUTHORITY}; out["validation_root_hash72"]=hash72(out["schema"], out); return out

def ocr_provider_self_test()->Dict[str,Any]:
    source={"source_root_hash72":hash72("SOURCE","image")}; regions={"observation_root_hash72":hash72("REGIONS","r"),"regions":[{"region_id":"region:0","page_index":0,"region_root_hash72":hash72("REGION","r")}]}; contract=build_document_provider_contract(provider_id="provider:deterministic-ocr", capability_class="OCR", observed_modalities=["PDF","IMAGE"], projection_types=["OCR_TEXT_PROJECTION"]); obs=run_ocr_on_regions(source_commitment=source,image_regions=regions,payload="HHS OCR 123"); bad=dict(obs, ocr_text_is_document_source=True)
    return {"schema":"HHS_OCR_PROVIDER_SELF_TEST_V1","version":VERSION,"ok":bool(validate_document_provider_contract(contract)["ok"] and validate_ocr_observation(obs)["ok"] and not validate_ocr_observation(bad)["ok"]),"contract":contract,"observation":obs,"bad_rejection":validate_ocr_observation(bad)}
if __name__=="__main__":
    import json; print(json.dumps(ocr_provider_self_test(), indent=2, sort_keys=True, default=str))

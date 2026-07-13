"""Document structure fusion v1.

Fusion preserves agreement, disagreement, unresolved ambiguity, and evidence. It
never silently chooses a provider output as document truth.
"""
from __future__ import annotations
from typing import Any, Dict, Iterable, List, Mapping
import time, uuid
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_document_provider_contract_v1 import VERSION, AUTHORITY
SCHEMA="HHS_DOCUMENT_STRUCTURE_FUSION_RECORD_V1"
FUSION_STATES=["OBSERVATION_AGREEMENT","OBSERVATION_DISAGREEMENT","UNRESOLVED_AMBIGUITY","PROVIDER_CONFIDENCE_CONFLICT","MISSING_REGION_OBSERVATION","SELECTED_PROJECTION_WITH_EVIDENCE","REJECTED_PROJECTION_WITH_REASON"]
def _unique(prefix:str)->str: return f"{prefix}:{uuid.uuid4().hex}"
def _now_ms()->int: return int(time.time()*1000)

def _text_roots(obs:Mapping[str,Any])->List[str]:
    roots=[]
    if obs.get("extracted_text_root_hash72"): roots.append(str(obs.get("extracted_text_root_hash72")))
    for p in obs.get("ocr_region_projections",[]) or []:
        if p.get("ocr_text_root_hash72"): roots.append(str(p.get("ocr_text_root_hash72")))
    return roots

def fuse_document_observations(*, source_commitment:Mapping[str,Any], observations:Iterable[Mapping[str,Any]], selection_policy:str="PRESERVE_DISAGREEMENT_SELECT_NATIVE_TEXT_WHEN_AVAILABLE") -> Dict[str,Any]:
    obs=[dict(o) for o in observations]
    roots=[o.get("observation_root_hash72") for o in obs if o.get("observation_root_hash72")]
    text_roots=[]
    for o in obs: text_roots.extend(_text_roots(o))
    unique_text_roots=sorted(set(text_roots))
    if len(unique_text_roots) <= 1 and unique_text_roots:
        state="OBSERVATION_AGREEMENT"
    elif len(unique_text_roots) > 1:
        state="OBSERVATION_DISAGREEMENT"
    else:
        state="UNRESOLVED_AMBIGUITY"
    ambiguities=[]
    disagreements=[]
    if state=="OBSERVATION_DISAGREEMENT":
        disagreements.append({"type":"TEXT_ROOT_MISMATCH","roots":unique_text_roots,"resolution":"PRESERVED_NOT_COLLAPSED"})
    if not any(o.get("projection_type")=="PAGE_IMAGE_REGION_PROJECTION" for o in obs):
        ambiguities.append({"state":"MISSING_REGION_OBSERVATION","reason":"no image region observation supplied"})
    selected=None
    native=[o for o in obs if o.get("projection_type")=="PDF_NATIVE_TEXT_PROJECTION"]
    if native:
        selected={"projection_type":"PDF_NATIVE_TEXT_PROJECTION","observation_root_hash72":native[0].get("observation_root_hash72"),"selection_state":"SELECTED_PROJECTION_WITH_EVIDENCE","reason":"native text selected as projection candidate, not document identity"}
    record={"schema":SCHEMA,"version":VERSION,"fusion_id":_unique("document-fusion"),"source_commitment_root_hash72":source_commitment.get("source_root_hash72") or source_commitment.get("commitment_root_hash72"),"observation_roots":roots,"fusion_state":state,"fusion_states_supported":list(FUSION_STATES),"provider_disagreement_collapsed_silently":False,"selected_projection":selected,"disagreements":disagreements,"ambiguities":ambiguities,"observation_count":len(obs),"selection_policy":selection_policy,"source_remains_canonical":True,"created_at_unix_ms":_now_ms(),"authority":AUTHORITY}
    record["fusion_root_hash72"]=hash72(SCHEMA, record); return record

def validate_document_fusion(record:Mapping[str,Any])->Dict[str,Any]:
    reasons=[]
    if not record.get("source_commitment_root_hash72"): reasons.append("REJECT_DOCUMENT_FUSION_WITHOUT_PROVENANCE")
    if not record.get("observation_roots"): reasons.append("REJECT_DOCUMENT_FUSION_WITHOUT_PROVENANCE")
    if record.get("provider_disagreement_collapsed_silently"): reasons.append("REJECT_PROVIDER_DISAGREEMENT_COLLAPSED_SILENTLY")
    if record.get("selected_projection") and not record.get("source_remains_canonical"): reasons.append("REJECT_PROJECTION_REPLACES_SOURCE")
    ok=not reasons; out={"schema":"HHS_DOCUMENT_STRUCTURE_FUSION_VALIDATION_V1","version":VERSION,"ok":ok,"status":"ADMIT_DOCUMENT_STRUCTURE_FUSION" if ok else "REJECT_DOCUMENT_STRUCTURE_FUSION","reasons":sorted(set(reasons)),"fusion_root_hash72":record.get("fusion_root_hash72"),"authority":AUTHORITY}; out["validation_root_hash72"]=hash72(out["schema"], out); return out

def document_structure_fusion_self_test()->Dict[str,Any]:
    source={"source_root_hash72":hash72("SOURCE","doc")}; native={"projection_type":"PDF_NATIVE_TEXT_PROJECTION","observation_root_hash72":hash72("OBS","native"),"extracted_text_root_hash72":hash72("TEXT","A")}; ocr={"projection_type":"OCR_TEXT_PROJECTION","observation_root_hash72":hash72("OBS","ocr"),"ocr_region_projections":[{"ocr_text_root_hash72":hash72("TEXT","B")}]} ; fusion=fuse_document_observations(source_commitment=source, observations=[native,ocr]); bad=dict(fusion, provider_disagreement_collapsed_silently=True)
    return {"schema":"HHS_DOCUMENT_STRUCTURE_FUSION_SELF_TEST_V1","version":VERSION,"ok":bool(validate_document_fusion(fusion)["ok"] and fusion["fusion_state"]=="OBSERVATION_DISAGREEMENT" and not validate_document_fusion(bad)["ok"]),"fusion":fusion,"bad_rejection":validate_document_fusion(bad)}
if __name__=="__main__":
    import json; print(json.dumps(document_structure_fusion_self_test(), indent=2, sort_keys=True, default=str))

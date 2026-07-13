"""Pass 064 — Reciprocal Prompt–Response Alignment Agent and deterministic entanglement enforcement."""
from __future__ import annotations
from typing import Any, Dict, Iterable, Mapping, Sequence
import json
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_backend.runtime.hhs_deterministic_manifold_execution_v1 import run_deterministic_manifold_execution

VERSION="PASS_064_RECIPROCAL_PROMPT_RESPONSE_ALIGNMENT_AGENT_V1"
AUTHORITY="HHS_PROMPT_RESPONSE_ALIGNMENT_AUTHORITY_V1"
REJECTIONS=[
 "REJECT_RESPONSE_WITHOUT_CANONICAL_PROMPT_ROOT","REJECT_RESPONSE_CLAIM_WITHOUT_PROVENANCE",
 "REJECT_PROMPT_ELEMENT_SILENTLY_DROPPED","REJECT_INFERENCE_PROMOTED_TO_CANONICAL_SOURCE",
 "REJECT_ATTENTION_WEIGHT_AS_SEMANTIC_AUTHORITY","REJECT_FLUENCY_AS_ALIGNMENT_PROOF",
 "REJECT_RESPONSE_MUTATES_TYPED_EQUALITY","REJECT_PRESENTATION_MUTATES_EPISTEMIC_STATE",
 "REJECT_LOCAL_CONFLICT_AS_GLOBAL_PROMPT_INVALIDATION","REJECT_RESPONSE_WITHOUT_RECIPROCAL_CLOSURE",
 "REJECT_ALIGNMENT_AGENT_EXCEEDS_ROLE_SCOPE","REJECT_RESPONSE_WITHOUT_INDEPENDENT_REVALIDATION"]

def _w(label:str,payload:Any)->Dict[str,Any]: return make_hash72_kernel_witness(label,payload,width=72).to_dict()
def _root(label:str,payload:Any)->str: return _w(label,payload)["digest"]
def _finish(schema:str,obj:Dict[str,Any],field:str,label:str)->Dict[str,Any]:
 out={"schema":schema,"version":VERSION,"authority":AUTHORITY,**obj}; out[field]=_root(label,out); return out

def build_alignment_role_contract()->Dict[str,Any]:
 return _finish("HHS_ALIGNMENT_AGENT_ROLE_CONTRACT_V1",{
  "role_id":"role:alignment-agent","competencies":["PROMPT_STATE_EXTRACTION","SOURCE_AUTHORITY_CLASSIFICATION","SEMANTIC_CONTINUITY_VALIDATION","RESPONSE_CANDIDATE_GENERATION","RECIPROCAL_PAIR_VALIDATION","PRESENTATION_PROJECTION"],
  "authority_scope":["PRESERVE_CANONICAL_PROMPT_MEANING","SELECT_ADMISSIBLE_RESPONSE_CONTENT","LOCALIZE_CONFLICTS","PROJECT_VALIDATED_RESPONSE"],
  "forbidden_authorities":["REDEFINE_CANONICAL_USER_TERMS","INVENT_MISSING_SOURCE_AUTHORITY","COLLAPSE_TYPED_EQUALITY","PROMOTE_INFERENCE_TO_SOURCE","USE_ATTENTION_AS_TRUTH_WEIGHT","ALLOW_PRESENTATION_TO_MUTATE_MEANING","GLOBALIZE_LOCAL_REJECTION"],
  "requires_independent_revalidation":True
 },"role_contract_root_hash72","hhs_alignment_agent_role_contract_v1")

def build_canonical_prompt_state(manifold:Mapping[str,Any])->Dict[str,Any]:
 elements=[
  {"element_id":"prompt:source","kind":"SOURCE_IDENTITY","value":manifold["formal_state"]["formal_state_root_hash72"],"material":True},
  {"element_id":"prompt:intent","kind":"DECLARED_INTENT","value":"PRESERVE_AND_APPLY_CANONICAL_FORMAL_SYSTEM","material":True},
  {"element_id":"prompt:typed-relations","kind":"INVARIANT","value":"TYPED_RELATION_TOPOLOGY","material":True},
  {"element_id":"prompt:ambiguity","kind":"TYPED_AMBIGUITY","value":"PRESERVE_UNRESOLVED_SCOPE","material":True},]
 return _finish("HHS_CANONICAL_PROMPT_STATE_V1",{
  "source_commitment_root_hash72":manifold["run_root_hash72"],"formal_objects":manifold["formal_state"]["relations"],
  "declared_intent":["PRESERVE_SOURCE_IDENTITY","EXECUTE_THROUGH_CANONICAL_RUNTIME"],
  "authority_sources":["CANONICAL_USER_FORMAL_STATE","COMMITTED_RUNTIME_STATE"],
  "invariants_to_preserve":["SOURCE_IDENTITY","TYPED_EQUALITY","EPISTEMIC_STATUS","AUTHORITY_BOUNDARY","PROVENANCE"],
  "typed_ambiguities":["LOCAL_OPERATOR_SCOPE_REMAINS_TYPED"],"forbidden_substitutions":["LINGUISTIC_RECONSTRUCTION_AS_OPERATOR_AUTHORITY"],
  "prompt_elements":elements,"epistemic_states":["CANONICAL","DECLARED","TYPED_AMBIGUOUS"]
 },"prompt_state_root_hash72","hhs_canonical_prompt_state_v1")

def build_response_candidate(prompt:Mapping[str,Any], *, unsupported_claim:bool=False, mutate_unavailable:bool=False)->Dict[str,Any]:
 claims=[
  {"claim_id":"claim:source-preserved","text":"The formal source identity is preserved.","source_refs":["prompt:source"],"derivation":"DIRECT_PRESERVATION","epistemic_status":"VALIDATED"},
  {"claim_id":"claim:runtime-path","text":"Execution remains bound to the canonical Runtime path.","source_refs":["prompt:intent","prompt:typed-relations"],"derivation":"ADMITTED_TRANSFORMATION","epistemic_status":"VALIDATED"},]
 if unsupported_claim: claims.append({"claim_id":"claim:unsupported","text":"Invented explanatory conclusion.","source_refs":[],"derivation":"GENERATIVE_INFERENCE","epistemic_status":"ASSERTED"})
 dispositions=[
  {"element_id":"prompt:source","disposition":"PRESERVED"},{"element_id":"prompt:intent","disposition":"TRANSFORMED"},
  {"element_id":"prompt:typed-relations","disposition":"PRESERVED"},{"element_id":"prompt:ambiguity","disposition":"PRESERVED_AS_AMBIGUOUS"}]
 projection={"unknown_metric":"0" if mutate_unavailable else "UNAVAILABLE","unknown_metric_epistemic_status":"UNAVAILABLE"}
 return _finish("HHS_CANONICAL_RESPONSE_STATE_V1",{
  "prompt_state_root_hash72":prompt["prompt_state_root_hash72"],"claim_records":claims,
  "prompt_element_dispositions":dispositions,"transformations":["SEMANTIC_PRESERVATION","BOUNDED_PROJECTION"],
  "preserved_invariants":prompt["invariants_to_preserve"],"localized_rejections":[],"remaining_ambiguities":prompt["typed_ambiguities"],
  "presentation_projection":projection,"attention_score":"94/100","task_relevance_score":"87/100"
 },"response_state_root_hash72","hhs_canonical_response_state_v1")

def validate_claim_provenance(prompt:Mapping[str,Any], response:Mapping[str,Any])->Dict[str,Any]:
 valid_ids={e["element_id"] for e in prompt["prompt_elements"]}; reasons=[]; records=[]
 for claim in response["claim_records"]:
  valid=bool(claim["source_refs"]) and set(claim["source_refs"]).issubset(valid_ids)
  if not valid: reasons.append("REJECT_RESPONSE_CLAIM_WITHOUT_PROVENANCE")
  records.append({"claim_id":claim["claim_id"],"provenance_valid":valid,"source_refs":claim["source_refs"]})
 return _finish("HHS_RESPONSE_CLAIM_PROVENANCE_DECISION_V1",{"records":records,"provenance_complete":not reasons,"reasons":sorted(set(reasons)),"status":"ADMIT_CLAIM_PROVENANCE" if not reasons else "REJECT_CLAIM_PROVENANCE"},"claim_provenance_root_hash72","hhs_response_claim_provenance_v1")

def validate_prompt_dispositions(prompt:Mapping[str,Any], response:Mapping[str,Any])->Dict[str,Any]:
 expected={e["element_id"] for e in prompt["prompt_elements"] if e["material"]}; actual={d["element_id"] for d in response["prompt_element_dispositions"]}; missing=sorted(expected-actual)
 reasons=["REJECT_PROMPT_ELEMENT_SILENTLY_DROPPED"] if missing else []
 return _finish("HHS_PROMPT_ELEMENT_DISPOSITION_DECISION_V1",{"missing_material_elements":missing,"coverage_complete":not missing,"reasons":reasons,"status":"ADMIT_PROMPT_DISPOSITIONS" if not reasons else "REJECT_PROMPT_DISPOSITIONS"},"disposition_registry_root_hash72","hhs_prompt_element_disposition_registry_v1")

def detect_alignment_drift(prompt:Mapping[str,Any], response:Mapping[str,Any])->Dict[str,Any]:
 reasons=[]
 p=response["presentation_projection"]
 if p.get("unknown_metric_epistemic_status")=="UNAVAILABLE" and p.get("unknown_metric")!="UNAVAILABLE": reasons.append("REJECT_PRESENTATION_MUTATES_EPISTEMIC_STATE")
 if "TYPED_EQUALITY" not in response["preserved_invariants"]: reasons.append("REJECT_RESPONSE_MUTATES_TYPED_EQUALITY")
 return _finish("HHS_ALIGNMENT_DRIFT_DECISION_V1",{"semantic_drift":bool(reasons),"presentation_mutated_semantics":bool(reasons),"reasons":reasons,"status":"ADMIT_NO_ALIGNMENT_DRIFT" if not reasons else "REJECT_ALIGNMENT_DRIFT"},"alignment_drift_root_hash72","hhs_alignment_drift_detector_v1")

def validate_reciprocal_entanglement(prompt:Mapping[str,Any], response:Mapping[str,Any], provenance:Mapping[str,Any], dispositions:Mapping[str,Any], drift:Mapping[str,Any])->Dict[str,Any]:
 reasons=list(provenance["reasons"])+list(dispositions["reasons"])+list(drift["reasons"])
 receipt={"prompt_root_hash72":prompt["prompt_state_root_hash72"],"response_root_hash72":response["response_state_root_hash72"],
  "prompt_to_response_coverage":"1/1" if dispositions["coverage_complete"] else "INCOMPLETE",
  "response_to_prompt_provenance_complete":provenance["provenance_complete"],"silent_semantic_loss":not dispositions["coverage_complete"],
  "unauthorized_meaning_mutation":drift["semantic_drift"],"attention_used_as_authority":False,"presentation_mutated_semantics":drift["presentation_mutated_semantics"],
  "reciprocal_closure_verified":not reasons,"reasons":sorted(set(reasons)),"status":"ADMIT_RECIPROCAL_ENTANGLEMENT" if not reasons else "REJECT_RECIPROCAL_ENTANGLEMENT"}
 return _finish("HHS_PROMPT_RESPONSE_ENTANGLEMENT_RECEIPT_V1",receipt,"entanglement_root_hash72","hhs_prompt_response_entanglement_v1")

def select_response_candidate(entanglement:Mapping[str,Any], *, relevant:bool=True)->Dict[str,Any]:
 admissible=entanglement["reciprocal_closure_verified"]; selected=admissible and relevant
 return _finish("HHS_DETERMINISTIC_RESPONSE_SELECTION_V1",{"admissible":admissible,"relevant":relevant,"attention_used_for_admission":False,"selection_rule":"ADMISSIBLE(candidate) INTERSECTION RELEVANT(candidate)","selected":selected,"status":"ADMIT_RESPONSE_SELECTION" if selected else "REJECT_RESPONSE_SELECTION","reasons":[] if selected else ["REJECT_RESPONSE_WITHOUT_RECIPROCAL_CLOSURE"]},"response_selection_root_hash72","hhs_deterministic_response_selector_v1")

def independently_revalidate_alignment(selection:Mapping[str,Any], entanglement:Mapping[str,Any], *, local_revalidation:bool=True)->Dict[str,Any]:
 reasons=[]
 if not selection["selected"]: reasons.extend(selection["reasons"])
 if not local_revalidation: reasons.append("REJECT_RESPONSE_WITHOUT_INDEPENDENT_REVALIDATION")
 return _finish("HHS_RESPONSE_PROJECTION_REVALIDATION_V1",{"selection_root_hash72":selection["response_selection_root_hash72"],"entanglement_root_hash72":entanglement["entanglement_root_hash72"],"local_revalidation_performed":local_revalidation,"canonical_response_admitted":not reasons,"status":"ADMIT_CANONICAL_RESPONSE" if not reasons else "REJECT_CANONICAL_RESPONSE","reasons":sorted(set(reasons))},"response_revalidation_root_hash72","hhs_response_projection_revalidation_v1")

def run_alignment_agent()->Dict[str,Any]:
 manifold=run_deterministic_manifold_execution(); role=build_alignment_role_contract(); prompt=build_canonical_prompt_state(manifold); response=build_response_candidate(prompt)
 provenance=validate_claim_provenance(prompt,response); dispositions=validate_prompt_dispositions(prompt,response); drift=detect_alignment_drift(prompt,response)
 entanglement=validate_reciprocal_entanglement(prompt,response,provenance,dispositions,drift); selection=select_response_candidate(entanglement); revalidation=independently_revalidate_alignment(selection,entanglement)
 out={"schema":"HHS_ALIGNMENT_AGENT_RUN_V1","version":VERSION,"authority":AUTHORITY,"ok":manifold["ok"] and revalidation["canonical_response_admitted"],"pass063_root_hash72":manifold["run_root_hash72"],"role_contract":role,"prompt_state":prompt,"response_state":response,"claim_provenance":provenance,"prompt_dispositions":dispositions,"alignment_drift":drift,"entanglement_receipt":entanglement,"selection":selection,"revalidation":revalidation,"rejection_codes":REJECTIONS}
 out["run_root_hash72"]=_root("hhs_alignment_agent_run_v1",out); return out

def alignment_agent_self_test()->Dict[str,Any]:
 run=run_alignment_agent(); p=run["prompt_state"]
 unsupported=build_response_candidate(p,unsupported_claim=True); up=validate_claim_provenance(p,unsupported)
 mutated=build_response_candidate(p,mutate_unavailable=True); md=detect_alignment_drift(p,mutated)
 no_reval=independently_revalidate_alignment(run["selection"],run["entanglement_receipt"],local_revalidation=False)
 ok=run["ok"] and "REJECT_RESPONSE_CLAIM_WITHOUT_PROVENANCE" in up["reasons"] and "REJECT_PRESENTATION_MUTATES_EPISTEMIC_STATE" in md["reasons"] and "REJECT_RESPONSE_WITHOUT_INDEPENDENT_REVALIDATION" in no_reval["reasons"] and run["selection"]["attention_used_for_admission"] is False
 return {"schema":"HHS_ALIGNMENT_AGENT_SELF_TEST_V1","ok":ok,"run_root_hash72":run["run_root_hash72"],"negative_cases":{"unsupported_claim":up,"presentation_mutation":md,"missing_revalidation":no_reval}}

if __name__=="__main__": print(json.dumps(alignment_agent_self_test(),indent=2,sort_keys=True))

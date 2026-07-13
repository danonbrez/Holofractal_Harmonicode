"""Pass 054 — Canonical Authority Graph and Role-Bound Agent Orchestration."""
from __future__ import annotations
from typing import Any, Dict, Iterable, List, Mapping, Optional
import json
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness

VERSION="PASS_054_CANONICAL_AUTHORITY_GRAPH_ROLE_BOUND_AGENT_ORCHESTRATION_V1"
AUTHORITY="HHS_I019_CANONICAL_DERIVATION_AUTHORITY_BOUNDARY_V1"
REJECTIONS=[
"REJECT_AGENT_CAPABILITY_AS_CANONICAL_AUTHORITY","REJECT_OUTPUT_EQUIVALENCE_AS_DERIVATION_EQUIVALENCE",
"REJECT_OUTPUT_SIMILARITY_AS_IDENTITY_PROOF","REJECT_CORRECT_OUTPUT_SHAPE_WITHOUT_CANONICAL_DERIVATION_PATH",
"REJECT_CROSS_AGENT_HANDOFF_WITHOUT_PROVENANCE","REJECT_SPECIALIZED_PROJECTION_AS_COMPLETE_SYSTEM_IDENTITY",
"REJECT_UNVALIDATED_CROSS_ROLE_SUBSTITUTION","REJECT_ROLE_AUTHORITY_SCOPE_EXCEEDED","REJECT_TASK_AUTHORITY_EXPIRED",
"REJECT_FINAL_TRANSFORMER_AS_UPSTREAM_AUTHORITY","REJECT_ATTENTION_AS_TRUTH_WEIGHT","REJECT_RECENCY_AS_AUTHORITY",
"REJECT_CONFIDENCE_AS_EVIDENCE","REJECT_RESPONSE_PRIORITY_AS_SEMANTIC_AUTHORITY",
"REJECT_PRESENTATION_OPTIMIZATION_MUTATES_MEANING","REJECT_CANONICAL_CONTINUATION_WITHOUT_REVALIDATION"]
SOURCE_PRECEDENCE=["CANONICAL_KERNEL_INVARIANT","ADMITTED_RUNTIME_STATE","COMMITTED_REPOSITORY_STATE","VALIDATED_DERIVATION","ADMITTED_USER_INTENT","ROLE_LOCAL_WORKING_STATE","UNVALIDATED_PROPOSAL","MODEL_MEMORY","GENERATIVE_INFERENCE"]

def _w(label:str,payload:Any)->Dict[str,Any]: return make_hash72_kernel_witness(label,payload,width=72).to_dict()
def _root(label:str,payload:Any)->str: return _w(label,payload)["digest"]
def _finish(schema:str,obj:Dict[str,Any],field:str,label:str)->Dict[str,Any]:
    out={"schema":schema,"version":VERSION,**obj,"authority":AUTHORITY}; out[field]=_root(label,out); return out

def build_role_contract(role_id:str="role:implementation-agent", component_id:str="agent:development", competencies:Optional[List[str]]=None, authority_scope:Optional[List[str]]=None)->Dict[str,Any]:
    return _finish("HHS_SPECIALIZED_ROLE_CONTRACT_V1",{
      "role_id":role_id,"component_id":component_id,"canonical_system_id":"HHS","shared_invariant_ids":["HHS-I017","HHS-I018","HHS-I019"],
      "competencies":competencies or ["SOURCE_TREE_INSPECTION","CODE_MUTATION","TEST_EXECUTION","ARTIFACT_REGENERATION"],
      "authority_scope":authority_scope or ["IMPLEMENT_APPROVED_PASS_SPECIFICATION","MODIFY_DECLARED_REPOSITORY_PATHS","RUN_DECLARED_VERIFICATION_TARGETS"],
      "forbidden_authorities":["REDEFINE_CANONICAL_INVARIANTS","REINTERPRET_PASS_INTENT","INVENT_SUBSTITUTE_AUTHORITY_PATH","PROMOTE_STANDALONE_OUTPUT_TO_CANONICAL_STATE"],
      "required_inputs":["CANONICAL_REPOSITORY_ROOT","ADMITTED_PASS_SPECIFICATION","AUTHORITY_GRAPH_ROOT"],
      "required_outputs":["PATCH","TEST_RECEIPTS","GENERATED_MANIFESTS","CONFORMANCE_EVIDENCE","HANDOFF_PROVENANCE_BUNDLE"],
      "requires_independent_revalidation":True},"role_contract_root_hash72","hhs_specialized_role_contract_v1")

def build_competency_record(component_id="agent:development", competencies=None)->Dict[str,Any]:
    return _finish("HHS_COMPONENT_COMPETENCY_RECORD_V1",{"component_id":component_id,"competencies":[{"competency":x,"verified":True} for x in (competencies or ["CAN_WRITE_CODE","CAN_ANALYZE_ARCHITECTURE"])],"authority_granted_by_competency":False},"competency_record_root_hash72","hhs_component_competency_record_v1")

def build_task_assignment(source_root_hash72:str,specification_root_hash72:str, role_contract:Mapping[str,Any], task_id="task:pass054-module", allowed=None)->Dict[str,Any]:
    return _finish("HHS_TASK_ASSIGNMENT_CONTRACT_V1",{"task_id":task_id,"role_id":role_contract["role_id"],"component_id":role_contract["component_id"],"source_root_hash72":source_root_hash72,"specification_root_hash72":specification_root_hash72,
      "allowed_transformations":allowed or ["CREATE_DECLARED_MODULES","UPDATE_REGISTRY","ADD_TESTS","REGENERATE_MANIFESTS"],
      "forbidden_transformations":["CHANGE_INVARIANT_SEMANTICS","SUBSTITUTE_SOURCE_BASELINE","SKIP_REGENERATION","MANUALLY_ASSERT_GENERATED_COUNTS"],
      "expected_handoff_type":"HHS_IMPLEMENTATION_HANDOFF_V1","authority_expiration":"TASK_COMPLETION","task_state":"OPEN"},"task_assignment_root_hash72","hhs_task_assignment_contract_v1")

def validate_local_authority(role:Mapping[str,Any], task:Mapping[str,Any], transformation:str)->Dict[str,Any]:
    reasons=[]
    if task.get("task_state")!="OPEN": reasons.append("REJECT_TASK_AUTHORITY_EXPIRED")
    if transformation not in task.get("allowed_transformations",[]): reasons.append("REJECT_ROLE_AUTHORITY_SCOPE_EXCEEDED")
    if role.get("role_id")!=task.get("role_id") or role.get("component_id")!=task.get("component_id"): reasons.append("REJECT_UNVALIDATED_CROSS_ROLE_SUBSTITUTION")
    return _finish("HHS_ROLE_AUTHORITY_SCOPE_DECISION_V1",{"ok":not reasons,"status":"ADMIT_ROLE_LOCAL_TRANSFORMATION" if not reasons else "REJECT_ROLE_LOCAL_TRANSFORMATION","transformation":transformation,"reasons":reasons},"decision_root_hash72","hhs_role_authority_scope_decision_v1")

def build_handoff(task:Mapping[str,Any], output_roots:Mapping[str,str], semantic_fields=None)->Dict[str,Any]:
    return _finish("HHS_CROSS_ROLE_HANDOFF_V1",{"handoff_id":"handoff:"+task["task_id"].split(":")[-1],"sender_role_id":task["role_id"],"receiver_role_id":"role:audit-agent","source_object_ids":[task["task_id"]],"source_root_hash72s":[task["source_root_hash72"],task["specification_root_hash72"]],
      "semantic_fields_to_preserve":semantic_fields or ["INVARIANTS","AUTHORITY_BOUNDARIES","REJECTION_CONDITIONS","COMPLETION_CRITERIA"],"allowed_interpretive_freedom":["LOCAL_CODE_ORGANIZATION","NONSEMANTIC_NAMING","PERFORMANCE_OPTIMIZATION_WITH_EQUIVALENCE_PROOF"],"required_return_evidence":["PATCH_ROOT","TEST_ROOT","REACHABILITY_ROOT","CONFORMANCE_ROOT"],"return_evidence":dict(output_roots)},"handoff_root_hash72","hhs_cross_role_handoff_v1")

def validate_handoff(handoff:Mapping[str,Any])->Dict[str,Any]:
    reasons=[]
    if not handoff.get("source_root_hash72s") or len(handoff.get("source_root_hash72s",[]))<2: reasons.append("REJECT_CROSS_AGENT_HANDOFF_WITHOUT_PROVENANCE")
    missing=[x for x in handoff.get("required_return_evidence",[]) if not handoff.get("return_evidence",{}).get(x)]
    if missing: reasons.append("REJECT_CROSS_AGENT_HANDOFF_WITHOUT_PROVENANCE")
    return _finish("HHS_HANDOFF_PROVENANCE_DECISION_V1",{"ok":not reasons,"status":"ADMIT_CROSS_ROLE_HANDOFF" if not reasons else "REJECT_CROSS_ROLE_HANDOFF","missing_evidence":missing,"reasons":sorted(set(reasons))},"decision_root_hash72","hhs_handoff_provenance_decision_v1")

def validate_derivation_equivalence(candidate_output:Any,reference_output:Any,*,candidate_source_root:str,reference_source_root:str,candidate_path:Iterable[str],reference_path:Iterable[str],candidate_authority_path:Iterable[str],reference_authority_path:Iterable[str])->Dict[str,Any]:
    co=_root("hhs_output_identity_v1",candidate_output); ro=_root("hhs_output_identity_v1",reference_output)
    oe=co==ro; sp=candidate_source_root==reference_source_root; tp=list(candidate_path)==list(reference_path); ap=list(candidate_authority_path)==list(reference_authority_path)
    cont=oe and sp and tp and ap; reasons=[] if cont else (["REJECT_OUTPUT_EQUIVALENCE_AS_DERIVATION_EQUIVALENCE"] if oe else ["REJECT_OUTPUT_SIMILARITY_AS_IDENTITY_PROOF"])
    return _finish("HHS_DERIVATION_EQUIVALENCE_DECISION_V1",{"candidate_output_root_hash72":co,"reference_output_root_hash72":ro,"output_equivalent":oe,"source_provenance_equivalent":sp,"transformation_path_equivalent":tp,"authority_path_equivalent":ap,"canonical_identity_continues":cont,"status":"ADMIT_CANONICAL_CONTINUATION" if cont else "REJECT_CANONICAL_CONTINUATION","reasons":reasons},"decision_root_hash72","hhs_derivation_equivalence_decision_v1")

def independently_revalidate(role_decision:Mapping[str,Any],handoff_decision:Mapping[str,Any],derivation_decision:Mapping[str,Any])->Dict[str,Any]:
    reasons=[]
    if not role_decision.get("ok"): reasons += role_decision.get("reasons",[])
    if not handoff_decision.get("ok"): reasons += handoff_decision.get("reasons",[])
    if not derivation_decision.get("canonical_identity_continues"): reasons.append("REJECT_CANONICAL_CONTINUATION_WITHOUT_REVALIDATION")
    return _finish("HHS_INDEPENDENT_REVALIDATION_DECISION_V1",{"ok":not reasons,"status":"ADMIT_CANONICAL_CONTINUATION" if not reasons else "REJECT_CANONICAL_CONTINUATION","revalidator_role_id":"role:audit-agent","reasons":sorted(set(reasons))},"revalidation_root_hash72","hhs_independent_revalidation_v1")

def admit_response_candidate(candidate:Mapping[str,Any], canonical_invariant_conflict:bool=False, presentation_mutates_meaning:bool=False)->Dict[str,Any]:
    reasons=[]
    for field in ["provenance_valid","derivation_valid","role_scope_valid"]:
        if not candidate.get(field): reasons.append("REJECT_RESPONSE_PRIORITY_AS_SEMANTIC_AUTHORITY")
    if canonical_invariant_conflict and candidate.get("source_authority")!="CANONICAL_SUPERSESSION": reasons += ["REJECT_ATTENTION_AS_TRUTH_WEIGHT","REJECT_RECENCY_AS_AUTHORITY"]
    if presentation_mutates_meaning: reasons.append("REJECT_PRESENTATION_OPTIMIZATION_MUTATES_MEANING")
    return _finish("HHS_RESPONSE_PRIORITY_AUTHORITY_DECISION_V1",{"candidate_id":candidate.get("candidate_id"),"admissible":not reasons,"ranking_allowed":not reasons,"attention_used_for_admission":False,"selection_rule":"ADMISSIBLE(candidate) INTERSECT RELEVANT(candidate)","reasons":sorted(set(reasons))},"decision_root_hash72","hhs_response_priority_authority_gate_v1")

def build_authority_graph(role:Mapping[str,Any], competency:Mapping[str,Any], task:Mapping[str,Any], handoff:Mapping[str,Any], revalidation:Mapping[str,Any])->Dict[str,Any]:
    nodes=[{"id":"HHS-I019","type":"CANONICAL_INVARIANT"},{"id":role["role_id"],"type":"ROLE"},{"id":role["component_id"],"type":"COMPONENT"},{"id":task["task_id"],"type":"TASK_ASSIGNMENT"},{"id":handoff["handoff_id"],"type":"HANDOFF"},{"id":revalidation["revalidation_root_hash72"],"type":"VALIDATION"},{"id":"canonical-state:pass054","type":"CANONICAL_STATE"}]
    for c in competency["competencies"]: nodes.append({"id":"competency:"+c["competency"],"type":"COMPETENCY"})
    edges=[("HHS-I019",role["role_id"],"SHARES_INVARIANT"),(role["role_id"],role["component_id"],"DECLARES_ROLE"),(role["component_id"],task["task_id"],"ASSIGNED_TO"),(task["task_id"],handoff["handoff_id"],"PRODUCES"),(handoff["handoff_id"],revalidation["revalidation_root_hash72"],"REVALIDATED_BY"),(revalidation["revalidation_root_hash72"],"canonical-state:pass054","CANONICALLY_CONTINUES")]
    edges += [(role["component_id"],"competency:"+c["competency"],"POSSESSES_COMPETENCY") for c in competency["competencies"]]
    return _finish("HHS_CANONICAL_AUTHORITY_GRAPH_V1",{"nodes":nodes,"edges":[{"from":a,"to":b,"type":t} for a,b,t in edges],"competence_implies_authority":False,"source_precedence":SOURCE_PRECEDENCE,"rejection_codes":REJECTIONS},"authority_graph_root_hash72","hhs_canonical_authority_graph_v1")

def run_role_bound_orchestration()->Dict[str,Any]:
    source=_root("hhs_pass053_repository_state_v1",{"baseline":"PASS_053_REBUILT","services":110,"surfaces":133,"edges":1856,"orphans":0})
    spec=_root("hhs_pass054_specification_v1",{"title":"Canonical Authority Graph and Role-Bound Agent Orchestration","invariant":"HHS-I019"})
    role=build_role_contract(); competency=build_competency_record(); task=build_task_assignment(source,spec,role)
    local=validate_local_authority(role,task,"CREATE_DECLARED_MODULES")
    evidence={k:_root("hhs_pass054_evidence_v1",{"kind":k,"source":source}) for k in ["PATCH_ROOT","TEST_ROOT","REACHABILITY_ROOT","CONFORMANCE_ROOT"]}
    handoff=build_handoff(task,evidence); hv=validate_handoff(handoff)
    payload={"canonical":"pass054-result"}; deriv=validate_derivation_equivalence(payload,payload,candidate_source_root=source,reference_source_root=source,candidate_path=["ROLE_LOCAL_TRANSFORMATION","WITNESSED_HANDOFF"],reference_path=["ROLE_LOCAL_TRANSFORMATION","WITNESSED_HANDOFF"],candidate_authority_path=[role["role_contract_root_hash72"],task["task_assignment_root_hash72"]],reference_authority_path=[role["role_contract_root_hash72"],task["task_assignment_root_hash72"]])
    reval=independently_revalidate(local,hv,deriv); graph=build_authority_graph(role,competency,task,handoff,reval)
    response=admit_response_candidate({"candidate_id":"response-candidate:pass054","attention_score":0.94,"task_relevance_score":0.87,"source_authority":"CANONICAL","provenance_valid":True,"derivation_valid":True,"role_scope_valid":True})
    closed=dict(task); closed["task_state"]="CLOSED"; expired=validate_local_authority(role,closed,"CREATE_DECLARED_MODULES")
    result={"schema":"HHS_ROLE_BOUND_AGENT_ORCHESTRATION_RUN_V1","version":VERSION,"ok":all([local["ok"],hv["ok"],deriv["canonical_identity_continues"],reval["ok"],response["admissible"]]) and "REJECT_TASK_AUTHORITY_EXPIRED" in expired["reasons"],"role_contract":role,"competency_record":competency,"task_assignment":task,"local_authority_decision":local,"handoff":handoff,"handoff_validation":hv,"derivation_equivalence":deriv,"independent_revalidation":reval,"authority_graph":graph,"response_authority_decision":response,"task_expiration_decision":expired,"authority":AUTHORITY}
    result["run_root_hash72"]=_root("hhs_role_bound_agent_orchestration_run_v1",result); return result

def role_bound_agent_orchestrator_self_test()->Dict[str,Any]:
    run=run_role_bound_orchestration()
    invalid=validate_derivation_equivalence({"x":1},{"x":1},candidate_source_root="candidate",reference_source_root="canonical",candidate_path=["standalone"],reference_path=["canonical"],candidate_authority_path=["none"],reference_authority_path=["role","task"])
    attention=admit_response_candidate({"candidate_id":"recent","source_authority":"UNVALIDATED_PROPOSAL","provenance_valid":True,"derivation_valid":True,"role_scope_valid":True},canonical_invariant_conflict=True)
    presentation=admit_response_candidate({"candidate_id":"projection","source_authority":"CANONICAL","provenance_valid":True,"derivation_valid":True,"role_scope_valid":True},presentation_mutates_meaning=True)
    ok=run["ok"] and invalid["output_equivalent"] and not invalid["canonical_identity_continues"] and "REJECT_ATTENTION_AS_TRUTH_WEIGHT" in attention["reasons"] and "REJECT_PRESENTATION_OPTIMIZATION_MUTATES_MEANING" in presentation["reasons"]
    return {"schema":"HHS_ROLE_BOUND_AGENT_ORCHESTRATOR_SELF_TEST_V1","ok":ok,"run_root_hash72":run["run_root_hash72"],"negative_cases":{"output_equivalent_derivation_invalid":invalid,"attention_conflict":attention,"presentation_mutation":presentation}}

if __name__=="__main__": print(json.dumps(role_bound_agent_orchestrator_self_test(),indent=2,sort_keys=True))

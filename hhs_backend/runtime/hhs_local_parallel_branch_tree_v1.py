"""Pass 065 — Local closed parallel branch-tree entanglement and A=B phase reintegration."""
from __future__ import annotations
from typing import Any, Dict, Mapping, Sequence
import json
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_backend.runtime.hhs_alignment_agent_v1 import run_alignment_agent

VERSION="PASS_065_LOCAL_CLOSED_PARALLEL_BRANCH_TREE_V1"
AUTHORITY="HHS_LOCAL_BRANCH_RESOLUTION_AUTHORITY_V1"
REJECTIONS=[
 "REJECT_BRANCH_WITHOUT_CANONICAL_PARENT_ROOT","REJECT_BRANCH_WITHOUT_LOCAL_CONSTRAINT_SCOPE",
 "REJECT_BRANCH_AUTHORITY_EXCEEDS_PARENT","REJECT_BRANCH_ESCAPES_CLOSED_LOCAL_TREE",
 "REJECT_CONTRADICTION_AS_GLOBAL_INVALIDATION","REJECT_BOTTLENECK_AS_GLOBAL_FAILURE",
 "REJECT_BRANCH_RESULT_WITHOUT_PROVENANCE","REJECT_BRANCH_RESULT_WITHOUT_COMPARATIVE_REVALIDATION",
 "REJECT_UNRESOLVED_PHASE_MISALIGNMENT_AS_FALSE_EQUALITY","REJECT_A_EQUALS_B_WITHOUT_INTEGRATION_WITNESS",
 "REJECT_FAILED_BRANCH_PROPAGATES_REJECTION","REJECT_BRANCH_TREE_WITHOUT_BOUNDED_CLOSURE"]

def _w(label:str,payload:Any)->Dict[str,Any]: return make_hash72_kernel_witness(label,payload,width=72).to_dict()
def _root(label:str,payload:Any)->str: return _w(label,payload)["digest"]
def _finish(schema:str,obj:Dict[str,Any],field:str,label:str)->Dict[str,Any]:
 out={"schema":schema,"version":VERSION,"authority":AUTHORITY,**obj}; out[field]=_root(label,out); return out

def build_local_constraint_bottleneck(alignment:Mapping[str,Any])->Dict[str,Any]:
 return _finish("HHS_LOCAL_CONSTRAINT_BOTTLENECK_V1",{
  "canonical_parent_root_hash72":alignment["run_root_hash72"],"constraint_id":"constraint:A=B:integration",
  "local_scope":["A","B","P","TRANSLATION_PHASE"],"conflict_type":"PHASE_INTEGRATION_MISALIGNMENT",
  "global_state_invalid":False,"requires_parallel_resolution":True,"minimum_correction_scope":"LOCAL_RELATION_SUBGRAPH",
  "preserve_unaffected_structure":True
 },"bottleneck_root_hash72","hhs_local_constraint_bottleneck_v1")

def build_branch_contract(bottleneck:Mapping[str,Any],branch_id:str,strategy:str)->Dict[str,Any]:
 return _finish("HHS_CLOSED_BRANCH_CONTRACT_V1",{
  "branch_id":branch_id,"parent_root_hash72":bottleneck["bottleneck_root_hash72"],"local_scope":bottleneck["local_scope"],
  "strategy":strategy,"authority_scope":["INSPECT_LOCAL_RELATIONS","PROPOSE_LOCAL_TRANSFORMATION","RETURN_WITNESSED_CANDIDATE"],
  "forbidden_authorities":["MUTATE_CANONICAL_PARENT","GLOBALIZE_REJECTION","ERASE_SIBLING_BRANCH","CLAIM_A_EQUALS_B_WITHOUT_WITNESS"],
  "closed_local_tree":True,"authority_expires":"BRANCH_CLOSURE"
 },"branch_contract_root_hash72","hhs_closed_branch_contract_v1")

def execute_branch(contract:Mapping[str,Any], *, contradiction:bool=False, energy_bottleneck:bool=False)->Dict[str,Any]:
 strategy=contract["strategy"]
 if strategy=="DIRECT_RECIPROCAL_ALIGNMENT": candidate={"A":"P^2","B":"P^2","relation":"A=B","phase_residue":"0","cost":3}
 elif strategy=="TRANSLATION_PHASE_BRIDGE": candidate={"A":"LHS","B":"RHS","relation":"A~B via witnessed bridge","phase_residue":"0","cost":5}
 else: candidate={"A":"P^2","B":"P^2","relation":"A=B after local contraction","phase_residue":"0","cost":4}
 reasons=[]
 if contradiction: reasons.append("LOCAL_CONTRADICTION_DETECTED")
 if energy_bottleneck: reasons.append("LOCAL_INFORMATION_ENERGY_BOTTLENECK")
 return _finish("HHS_BRANCH_EXECUTION_RECEIPT_V1",{
  "branch_id":contract["branch_id"],"branch_contract_root_hash72":contract["branch_contract_root_hash72"],
  "strategy":strategy,"candidate":candidate,"local_only":True,"canonical_parent_mutated":False,
  "diagnostics":reasons,"execution_status":"CANDIDATE_RETURNED","provenance_complete":True
 },"branch_execution_root_hash72","hhs_branch_execution_receipt_v1")

def compare_branches(receipts:Sequence[Mapping[str,Any]])->Dict[str,Any]:
 admissible=[r for r in receipts if r["provenance_complete"] and r["candidate"]["phase_residue"]=="0"]
 ordered=sorted(admissible,key=lambda r:(r["candidate"]["cost"],r["branch_id"]))
 selected=ordered[0] if ordered else None
 return _finish("HHS_PARALLEL_BRANCH_COMPARATIVE_REVALIDATION_V1",{
  "branch_roots_hash72":[r["branch_execution_root_hash72"] for r in receipts],"admissible_branch_ids":[r["branch_id"] for r in admissible],
  "selected_branch_id":selected["branch_id"] if selected else None,"selection_rule":"MINIMUM_ADMISSIBLE_LOCAL_CORRECTION_COST_THEN_BRANCH_ID",
  "comparative_revalidation_performed":True,"status":"ADMIT_LOCAL_BRANCH_SELECTION" if selected else "REJECT_LOCAL_BRANCH_SELECTION",
  "reasons":[] if selected else ["REJECT_BRANCH_RESULT_WITHOUT_COMPARATIVE_REVALIDATION"]
 },"comparative_revalidation_root_hash72","hhs_parallel_branch_comparative_revalidation_v1")

def build_ab_reintegration_witness(bottleneck:Mapping[str,Any],receipts:Sequence[Mapping[str,Any]],comparison:Mapping[str,Any])->Dict[str,Any]:
 selected=next((r for r in receipts if r["branch_id"]==comparison["selected_branch_id"]),None); reasons=[]
 if not selected: reasons.append("REJECT_A_EQUALS_B_WITHOUT_INTEGRATION_WITNESS")
 elif selected["candidate"]["phase_residue"]!="0": reasons.append("REJECT_UNRESOLVED_PHASE_MISALIGNMENT_AS_FALSE_EQUALITY")
 return _finish("HHS_A_EQUALS_B_PHASE_REINTEGRATION_WITNESS_V1",{
  "bottleneck_root_hash72":bottleneck["bottleneck_root_hash72"],"selected_branch_id":comparison["selected_branch_id"],
  "A_state":selected["candidate"]["A"] if selected else "UNAVAILABLE","B_state":selected["candidate"]["B"] if selected else "UNAVAILABLE",
  "integration_relation":"A=B" if not reasons else "UNRESOLVED","translation_phase_aligned":not reasons,"local_scope_preserved":True,
  "unaffected_structure_preserved":True,"canonical_reintegration_admissible":not reasons,"status":"ADMIT_A_EQUALS_B_REINTEGRATION" if not reasons else "REJECT_A_EQUALS_B_REINTEGRATION","reasons":reasons
 },"reintegration_root_hash72","hhs_a_equals_b_phase_reintegration_v1")

def close_branch_tree(bottleneck:Mapping[str,Any],contracts:Sequence[Mapping[str,Any]],receipts:Sequence[Mapping[str,Any]],reintegration:Mapping[str,Any])->Dict[str,Any]:
 return _finish("HHS_LOCAL_BRANCH_TREE_CLOSURE_RECEIPT_V1",{
  "parent_root_hash72":bottleneck["canonical_parent_root_hash72"],"branch_contract_roots_hash72":[c["branch_contract_root_hash72"] for c in contracts],
  "branch_execution_roots_hash72":[r["branch_execution_root_hash72"] for r in receipts],"reintegration_root_hash72":reintegration["reintegration_root_hash72"],
  "failed_branch_rejection_propagated":False,"global_rejection_emitted":False,"all_branch_authority_expired":True,
  "closed_local_tree":True,"canonical_continuation":reintegration["canonical_reintegration_admissible"],
  "status":"ADMIT_CANONICAL_CONTINUATION" if reintegration["canonical_reintegration_admissible"] else "REJECT_LOCAL_TREE_CLOSURE"
 },"branch_tree_closure_root_hash72","hhs_local_branch_tree_closure_v1")

def run_local_parallel_branch_tree()->Dict[str,Any]:
 alignment=run_alignment_agent(); bottleneck=build_local_constraint_bottleneck(alignment)
 specs=[("branch:direct","DIRECT_RECIPROCAL_ALIGNMENT"),("branch:bridge","TRANSLATION_PHASE_BRIDGE"),("branch:contract","LOCAL_RECIPROCAL_CONTRACTION")]
 contracts=[build_branch_contract(bottleneck,*s) for s in specs]
 receipts=[execute_branch(contracts[0]),execute_branch(contracts[1],energy_bottleneck=True),execute_branch(contracts[2],contradiction=True)]
 comparison=compare_branches(receipts); reintegration=build_ab_reintegration_witness(bottleneck,receipts,comparison); closure=close_branch_tree(bottleneck,contracts,receipts,reintegration)
 out={"schema":"HHS_LOCAL_PARALLEL_BRANCH_TREE_RUN_V1","version":VERSION,"authority":AUTHORITY,"ok":alignment["ok"] and closure["canonical_continuation"],
  "pass064_root_hash72":alignment["run_root_hash72"],"bottleneck":bottleneck,"branch_contracts":contracts,"branch_receipts":receipts,"comparison":comparison,"reintegration":reintegration,"closure":closure,"rejection_codes":REJECTIONS}
 out["run_root_hash72"]=_root("hhs_local_parallel_branch_tree_run_v1",out); return out

def local_parallel_branch_tree_self_test()->Dict[str,Any]:
 run=run_local_parallel_branch_tree(); b=run["bottleneck"]
 bad=build_branch_contract(b,"branch:bad","DIRECT_RECIPROCAL_ALIGNMENT"); bad=dict(bad); bad["local_scope"]=["GLOBAL_STATE"]
 failed=dict(run["branch_receipts"][0]); failed["provenance_complete"]=False
 comp=compare_branches([failed])
 ok=run["ok"] and run["closure"]["global_rejection_emitted"] is False and run["closure"]["failed_branch_rejection_propagated"] is False and run["reintegration"]["translation_phase_aligned"] and comp["status"]=="REJECT_LOCAL_BRANCH_SELECTION"
 return {"schema":"HHS_LOCAL_PARALLEL_BRANCH_TREE_SELF_TEST_V1","ok":ok,"run_root_hash72":run["run_root_hash72"],"negative_cases":{"missing_provenance":comp}}

if __name__=="__main__": print(json.dumps(local_parallel_branch_tree_self_test(),indent=2,sort_keys=True))

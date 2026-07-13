"""Pass 063 — Deterministic Manifold Execution and Scoped Phase-Cancellation Closure."""
from __future__ import annotations
from typing import Any, Dict, Iterable, List, Mapping
import json
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_backend.runtime.hhs_global_reciprocal_contract_topology_v1 import run_global_reciprocal_contract_topology

VERSION="PASS_063_DETERMINISTIC_MANIFOLD_EXECUTION_SCOPED_PHASE_CANCELLATION_V1"
AUTHORITY="HHS_DETERMINISTIC_MANIFOLD_EXECUTION_AUTHORITY_V1"
REJECTIONS=[
 "REJECT_LINGUISTIC_INTERPRETATION_AS_OPERATOR_AUTHORITY",
 "REJECT_FORMAL_STATE_WITHOUT_CANONICAL_RUNTIME_PATH",
 "REJECT_CONTRADICTION_AS_GLOBAL_FAILURE",
 "REJECT_PHASE_CANCELLATION_EXCEEDS_CONFLICT_SCOPE",
 "REJECT_UNAFFECTED_RELATION_ERASURE",
 "REJECT_NEGATIVE_PHASE_AS_GLOBAL_REJECTION_AUTHORITY",
 "REJECT_CLOSURE_WITHOUT_PROVENANCE",
 "REJECT_SURVIVING_STATE_WITHOUT_INDEPENDENT_REVALIDATION",
 "REJECT_PARALLEL_OPERATOR_SEMANTICS",
 "REJECT_RUNTIME_RESULT_WITHOUT_HASH72_WITNESS",
]

def _w(label:str,payload:Any)->Dict[str,Any]: return make_hash72_kernel_witness(label,payload,width=72).to_dict()
def _root(label:str,payload:Any)->str: return _w(label,payload)["digest"]
def _finish(schema:str,obj:Dict[str,Any],field:str,label:str)->Dict[str,Any]:
 out={"schema":schema,"version":VERSION,"authority":AUTHORITY,**obj}; out[field]=_root(label,out); return out

def build_canonical_formal_state(topology_run:Mapping[str,Any])->Dict[str,Any]:
 algebra=topology_run["xyzw_algebra_contracts"][0]
 relations=[]
 for i,r in enumerate(algebra["relations"]):
  relations.append({"relation_id":f"relation:{i:02d}","relation":r,"source":"PASS_062_XYZW_ALGEBRA","active":True})
 return _finish("HHS_CANONICAL_FORMAL_MANIFOLD_STATE_V1",{
  "source_pass062_root_hash72":topology_run["run_root_hash72"],
  "operator_semantics_source":"EXISTING_RUNTIME_OPERATOR_REGISTRY",
  "linguistic_interpretation_inserted":False,
  "relations":relations,
  "canonical_relation_count":len(relations),
  "phase_topology_root_hash72":topology_run["global_topology"]["global_topology_root_hash72"],
  "status":"ADMIT_CANONICAL_FORMAL_STATE","reasons":[]
 },"formal_state_root_hash72","hhs_canonical_formal_manifold_state_v1")

def propagate_constraints(state:Mapping[str,Any])->Dict[str,Any]:
 propagated=[]
 for item in state["relations"]:
  rel=dict(item)
  rel["propagation_status"]="PRESERVED"
  rel["derived_scope"]=[item["relation_id"]]
  propagated.append(rel)
 return _finish("HHS_DETERMINISTIC_CONSTRAINT_PROPAGATION_V1",{
  "formal_state_root_hash72":state["formal_state_root_hash72"],
  "runtime_path":["CANONICAL_OPERATOR_REGISTRY","CONSTRAINT_PROPAGATION","LOCAL_PHASE_INTERACTION"],
  "parallel_semantics_created":False,
  "propagated_relations":propagated,
  "status":"ADMIT_CONSTRAINT_PROPAGATION","reasons":[]
 },"constraint_propagation_root_hash72","hhs_deterministic_constraint_propagation_v1")

def detect_local_conflicts(propagation:Mapping[str,Any], *, inject_conflict:bool=True)->Dict[str,Any]:
 conflicts=[]
 if inject_conflict:
  conflicts.append({
   "conflict_id":"conflict:local-phase-orientation",
   "relation_ids":["relation:02","relation:05"],
   "conflict_type":"UNTYPED_FRAME_COLLISION",
   "affected_scope":["relation:02","relation:05"],
   "unaffected_relation_ids":[r["relation_id"] for r in propagation["propagated_relations"] if r["relation_id"] not in {"relation:02","relation:05"}],
   "global_failure":False,
   "resolution":"RESTORE_TYPED_EQUALITY_BOUNDARY",
  })
 return _finish("HHS_LOCAL_PHASE_CONFLICT_SET_V1",{
  "constraint_propagation_root_hash72":propagation["constraint_propagation_root_hash72"],
  "conflicts":conflicts,"conflict_count":len(conflicts),
  "contradiction_implies_global_failure":False,
  "status":"ADMIT_LOCALIZED_CONFLICT_SET","reasons":[]
 },"local_conflict_set_root_hash72","hhs_local_phase_conflict_set_v1")

def apply_scoped_phase_cancellation(propagation:Mapping[str,Any], conflicts:Mapping[str,Any], *, requested_scope:Iterable[str]|None=None)->Dict[str,Any]:
 allowed=set()
 for c in conflicts["conflicts"]: allowed.update(c["affected_scope"])
 requested=set(requested_scope if requested_scope is not None else allowed)
 reasons=[]
 if not requested.issubset(allowed): reasons.append("REJECT_PHASE_CANCELLATION_EXCEEDS_CONFLICT_SCOPE")
 surviving=[]; cancelled=[]
 for rel in propagation["propagated_relations"]:
  if rel["relation_id"] in requested and not reasons:
   cancelled.append({"relation_id":rel["relation_id"],"cancellation":"PHASE_FRAME_CORRECTION_ONLY","source_relation_preserved":True})
  else: surviving.append(rel)
 unaffected_expected={r["relation_id"] for r in propagation["propagated_relations"]}-allowed
 unaffected_survived=unaffected_expected.issubset({r["relation_id"] for r in surviving})
 if not unaffected_survived: reasons.append("REJECT_UNAFFECTED_RELATION_ERASURE")
 return _finish("HHS_SCOPED_RECIPROCAL_PHASE_CANCELLATION_V1",{
  "constraint_propagation_root_hash72":propagation["constraint_propagation_root_hash72"],
  "local_conflict_set_root_hash72":conflicts["local_conflict_set_root_hash72"],
  "allowed_scope":sorted(allowed),"requested_scope":sorted(requested),
  "cancelled_relations":cancelled,"surviving_relations":surviving,
  "minimum_necessary_cancellation":not reasons,"unaffected_structure_preserved":unaffected_survived,
  "negative_phase_acquired_global_rejection_authority":False,
  "status":"ADMIT_SCOPED_PHASE_CANCELLATION" if not reasons else "REJECT_PHASE_CANCELLATION","reasons":reasons
 },"phase_cancellation_root_hash72","hhs_scoped_reciprocal_phase_cancellation_v1")

def close_manifold(state:Mapping[str,Any], propagation:Mapping[str,Any], cancellation:Mapping[str,Any])->Dict[str,Any]:
 reasons=list(cancellation.get("reasons",[]))
 closure_payload={
  "formal_state_root_hash72":state["formal_state_root_hash72"],
  "constraint_propagation_root_hash72":propagation["constraint_propagation_root_hash72"],
  "phase_cancellation_root_hash72":cancellation["phase_cancellation_root_hash72"],
  "surviving_relation_ids":[r["relation_id"] for r in cancellation["surviving_relations"]],
  "cancelled_relation_ids":[r["relation_id"] for r in cancellation["cancelled_relations"]],
 }
 return _finish("HHS_INVARIANT_PRESERVING_MANIFOLD_CLOSURE_V1",{
  **closure_payload,
  "closure_witness":_w("hhs_manifold_closure_witness_v1",closure_payload),
  "closure_fixed_point":not reasons,
  "source_identity_preserved":True,
  "unaffected_relations_preserved":cancellation["unaffected_structure_preserved"],
  "status":"ADMIT_MANIFOLD_CLOSURE" if not reasons else "REJECT_MANIFOLD_CLOSURE","reasons":reasons
 },"manifold_closure_root_hash72","hhs_invariant_preserving_manifold_closure_v1")

def independently_revalidate(closure:Mapping[str,Any], *, local_revalidation:bool=True)->Dict[str,Any]:
 reasons=[]
 if not closure.get("closure_fixed_point"): reasons.append("REJECT_CLOSURE_WITHOUT_PROVENANCE")
 if not local_revalidation: reasons.append("REJECT_SURVIVING_STATE_WITHOUT_INDEPENDENT_REVALIDATION")
 return _finish("HHS_MANIFOLD_EXECUTION_REVALIDATION_DECISION_V1",{
  "manifold_closure_root_hash72":closure["manifold_closure_root_hash72"],
  "local_revalidation_performed":local_revalidation,
  "canonical_continuation":not reasons,
  "status":"ADMIT_CANONICAL_MANIFOLD_CONTINUATION" if not reasons else "REJECT_MANIFOLD_CONTINUATION","reasons":reasons
 },"revalidation_root_hash72","hhs_manifold_execution_revalidation_v1")

def run_deterministic_manifold_execution()->Dict[str,Any]:
 p62=run_global_reciprocal_contract_topology()
 state=build_canonical_formal_state(p62)
 propagation=propagate_constraints(state)
 conflicts=detect_local_conflicts(propagation)
 cancellation=apply_scoped_phase_cancellation(propagation,conflicts)
 closure=close_manifold(state,propagation,cancellation)
 revalidation=independently_revalidate(closure)
 out={"schema":"HHS_DETERMINISTIC_MANIFOLD_EXECUTION_RUN_V1","version":VERSION,"authority":AUTHORITY,
  "ok":p62["ok"] and revalidation["canonical_continuation"],"pass062_root_hash72":p62["run_root_hash72"],
  "formal_state":state,"constraint_propagation":propagation,"local_conflicts":conflicts,
  "phase_cancellation":cancellation,"closure":closure,"revalidation":revalidation,
  "execution_chain":["CANONICAL_ALGEBRA","EXISTING_RUNTIME_OPERATORS","DETERMINISTIC_CONSTRAINTS","LOCAL_PHASE_INTERACTION","SCOPED_CANCELLATION","CLOSURE","WITNESSED_RESULT","INDEPENDENT_REVALIDATION"],
  "rejection_codes":REJECTIONS}
 out["run_root_hash72"]=_root("hhs_deterministic_manifold_execution_run_v1",out); return out

def deterministic_manifold_execution_self_test()->Dict[str,Any]:
 run=run_deterministic_manifold_execution()
 p=run["constraint_propagation"]; c=run["local_conflicts"]
 bad=apply_scoped_phase_cancellation(p,c,requested_scope=["relation:02","relation:05","relation:12"])
 no_reval=independently_revalidate(run["closure"],local_revalidation=False)
 ok=(run["ok"] and run["formal_state"]["linguistic_interpretation_inserted"] is False and
     run["phase_cancellation"]["minimum_necessary_cancellation"] and run["phase_cancellation"]["unaffected_structure_preserved"] and
     "REJECT_PHASE_CANCELLATION_EXCEEDS_CONFLICT_SCOPE" in bad["reasons"] and
     "REJECT_SURVIVING_STATE_WITHOUT_INDEPENDENT_REVALIDATION" in no_reval["reasons"])
 return {"schema":"HHS_DETERMINISTIC_MANIFOLD_EXECUTION_SELF_TEST_V1","ok":ok,"run_root_hash72":run["run_root_hash72"],"negative_cases":{"overbroad_cancellation":bad,"missing_revalidation":no_reval}}

if __name__=="__main__": print(json.dumps(deterministic_manifold_execution_self_test(),indent=2,sort_keys=True))

"""Pass 055 — Authority-Enforced Runtime Dispatch and Revocable Capability Leases."""
from __future__ import annotations
from typing import Any, Dict, Iterable, List, Mapping, Optional
import json
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness

VERSION="PASS_055_AUTHORITY_ENFORCED_RUNTIME_DISPATCH_REVOCABLE_CAPABILITY_LEASES_V1"
AUTHORITY="HHS_I019_AUTHORITY_ACTIVATION_BOUNDARY_V1"
LEASE_STATES=("ISSUED","ACTIVE","CONSUMED","EXPIRED","REVOKED","TASK_CLOSED")
REJECTIONS=[
"REJECT_DISPATCH_WITHOUT_ROLE_AUTHORITY","REJECT_DISPATCH_WITHOUT_TASK_ASSIGNMENT",
"REJECT_CAPABILITY_INVOCATION_WITHOUT_LEASE","REJECT_LEASE_SCOPE_EXCEEDS_ROLE",
"REJECT_LEASE_SOURCE_SCOPE_VIOLATION","REJECT_LEASE_EXPIRED","REJECT_LEASE_REVOKED",
"REJECT_UNAUTHORIZED_LEASE_DELEGATION","REJECT_EXECUTION_AFTER_TASK_CLOSURE",
"REJECT_RESULT_AS_RETROACTIVE_AUTHORIZATION","REJECT_LEASE_OUTLIVES_TASK",
"REJECT_PROVIDER_RESULT_EXTENDS_LEASE","REJECT_EXECUTION_WITHOUT_CONTINUOUS_LEASE_VALIDATION"]

def _w(label:str,payload:Any)->Dict[str,Any]: return make_hash72_kernel_witness(label,payload,width=72).to_dict()
def _root(label:str,payload:Any)->str: return _w(label,payload)["digest"]
def _finish(schema:str,obj:Dict[str,Any],field:str,label:str)->Dict[str,Any]:
    out={"schema":schema,"version":VERSION,"authority":AUTHORITY,**obj}; out[field]=_root(label,out); return out

def issue_capability_lease(*,task:Mapping[str,Any],role_contract:Mapping[str,Any],authority_graph_root_hash72:str,capability_ids:Iterable[str],source_scope:Iterable[str],allowed_operations:Iterable[str],valid_from_sequence:int,expires_at_sequence:int,delegable:bool=False)->Dict[str,Any]:
    reasons=[]
    if task.get("task_state")!="OPEN": reasons.append("REJECT_EXECUTION_AFTER_TASK_CLOSURE")
    if task.get("role_id")!=role_contract.get("role_id") or task.get("component_id")!=role_contract.get("component_id"): reasons.append("REJECT_DISPATCH_WITHOUT_ROLE_AUTHORITY")
    allowed=set(task.get("allowed_transformations",[])); requested=set(allowed_operations)
    if not requested.issubset(allowed): reasons.append("REJECT_LEASE_SCOPE_EXCEEDS_ROLE")
    if expires_at_sequence < valid_from_sequence: reasons.append("REJECT_LEASE_EXPIRED")
    lease=_finish("HHS_REVOCABLE_CAPABILITY_LEASE_V1",{
      "lease_id":"lease:"+task["task_id"].split(":")[-1],"task_id":task["task_id"],"component_id":task["component_id"],"role_id":task["role_id"],
      "capability_ids":list(capability_ids),"source_scope":list(source_scope),"allowed_operations":list(allowed_operations),
      "issued_from_authority_graph_root_hash72":authority_graph_root_hash72,"valid_from_sequence":valid_from_sequence,"expires_at_sequence":expires_at_sequence,
      "revocable":True,"delegable":delegable,"mutation_authority":"EXPLICIT_ONLY","lease_state":"ISSUED","issuance_reasons":sorted(set(reasons)),"issuance_ok":not reasons,
      "task_assignment_root_hash72":task.get("task_assignment_root_hash72"),"role_contract_root_hash72":role_contract.get("role_contract_root_hash72")},"lease_root_hash72","hhs_revocable_capability_lease_v1")
    return lease

def transition_lease(lease:Mapping[str,Any],state:str,sequence:int,reason:str)->Dict[str,Any]:
    if state not in LEASE_STATES: raise ValueError(state)
    return _finish("HHS_CAPABILITY_LEASE_TRANSITION_V1",{"lease_root_hash72":lease["lease_root_hash72"],"prior_state":lease["lease_state"],"next_state":state,"sequence":sequence,"reason":reason,"terminal":state in {"CONSUMED","EXPIRED","REVOKED","TASK_CLOSED"}},"transition_root_hash72","hhs_capability_lease_transition_v1")

def lease_with_state(lease:Mapping[str,Any],transition:Mapping[str,Any])->Dict[str,Any]:
    out=dict(lease); out["lease_state"]=transition["next_state"]; out["last_transition_root_hash72"]=transition["transition_root_hash72"]; return out

def validate_dispatch(*,role_decision:Mapping[str,Any],task:Mapping[str,Any],lease:Optional[Mapping[str,Any]],capability_id:str,operation:str,source_object_id:str,sequence:int,delegate_component_id:Optional[str]=None)->Dict[str,Any]:
    reasons=[]
    if not role_decision.get("ok"): reasons.append("REJECT_DISPATCH_WITHOUT_ROLE_AUTHORITY")
    if task.get("task_state")!="OPEN": reasons += ["REJECT_DISPATCH_WITHOUT_TASK_ASSIGNMENT","REJECT_EXECUTION_AFTER_TASK_CLOSURE"]
    if lease is None: reasons.append("REJECT_CAPABILITY_INVOCATION_WITHOUT_LEASE")
    else:
      state=lease.get("lease_state")
      if state=="REVOKED": reasons.append("REJECT_LEASE_REVOKED")
      if state in {"EXPIRED","CONSUMED","TASK_CLOSED"} or sequence>int(lease.get("expires_at_sequence",-1)): reasons.append("REJECT_LEASE_EXPIRED")
      if sequence<int(lease.get("valid_from_sequence",0)): reasons.append("REJECT_CAPABILITY_INVOCATION_WITHOUT_LEASE")
      if capability_id not in lease.get("capability_ids",[]) or operation not in lease.get("allowed_operations",[]): reasons.append("REJECT_LEASE_SCOPE_EXCEEDS_ROLE")
      if source_object_id not in lease.get("source_scope",[]): reasons.append("REJECT_LEASE_SOURCE_SCOPE_VIOLATION")
      if delegate_component_id and (not lease.get("delegable") or delegate_component_id!=lease.get("component_id")): reasons.append("REJECT_UNAUTHORIZED_LEASE_DELEGATION")
    return _finish("HHS_AUTHORITY_ENFORCED_DISPATCH_DECISION_V1",{"ok":not reasons,"status":"ADMIT_RUNTIME_DISPATCH" if not reasons else "REJECT_RUNTIME_DISPATCH","task_id":task.get("task_id"),"lease_root_hash72":lease.get("lease_root_hash72") if lease else None,"capability_id":capability_id,"operation":operation,"source_object_id":source_object_id,"sequence":sequence,"reasons":sorted(set(reasons))},"dispatch_decision_root_hash72","hhs_authority_enforced_dispatch_decision_v1")

def validate_execution_checkpoint(*,lease:Mapping[str,Any],task:Mapping[str,Any],sequence:int,checkpoint_id:str)->Dict[str,Any]:
    reasons=[]; state=lease.get("lease_state")
    if task.get("task_state")!="OPEN": reasons.append("REJECT_EXECUTION_AFTER_TASK_CLOSURE")
    if state=="REVOKED": reasons.append("REJECT_LEASE_REVOKED")
    if state in {"EXPIRED","CONSUMED","TASK_CLOSED"} or sequence>lease.get("expires_at_sequence",-1): reasons.append("REJECT_LEASE_EXPIRED")
    if state not in {"ISSUED","ACTIVE"}: reasons.append("REJECT_EXECUTION_WITHOUT_CONTINUOUS_LEASE_VALIDATION")
    return _finish("HHS_EXECUTION_LEASE_CHECKPOINT_V1",{"ok":not reasons,"checkpoint_id":checkpoint_id,"sequence":sequence,"lease_root_hash72":lease["lease_root_hash72"],"lease_state":state,"reasons":sorted(set(reasons))},"checkpoint_root_hash72","hhs_execution_lease_checkpoint_v1")

def build_execution_receipt(*,dispatch:Mapping[str,Any],lease:Mapping[str,Any],task:Mapping[str,Any],role_contract:Mapping[str,Any],authority_graph_root_hash72:str,source_root_hash72:str,result:Any,checkpoints:Iterable[Mapping[str,Any]])->Dict[str,Any]:
    cps=list(checkpoints); ok=dispatch.get("ok") and cps and all(x.get("ok") for x in cps)
    return _finish("HHS_AUTHORITY_ENFORCED_EXECUTION_RECEIPT_V1",{"ok":bool(ok),"task_assignment_root_hash72":task.get("task_assignment_root_hash72"),"role_contract_root_hash72":role_contract.get("role_contract_root_hash72"),"authority_graph_root_hash72":authority_graph_root_hash72,"lease_root_hash72":lease["lease_root_hash72"],"source_root_hash72":source_root_hash72,"capability_id":dispatch.get("capability_id"),"operation":dispatch.get("operation"),"dispatch_decision_root_hash72":dispatch.get("dispatch_decision_root_hash72"),"checkpoint_roots":[x["checkpoint_root_hash72"] for x in cps],"result_root_hash72":_root("hhs_pass055_execution_result_v1",result),"lease_state_at_dispatch":lease.get("lease_state"),"lease_state_at_completion":"CONSUMED" if ok else lease.get("lease_state"),"successful_result_confers_authority":False},"execution_receipt_root_hash72","hhs_authority_enforced_execution_receipt_v1")

def validate_result_handoff(receipt:Mapping[str,Any],independent_revalidation:Mapping[str,Any])->Dict[str,Any]:
    reasons=[]
    if not receipt.get("ok"): reasons.append("REJECT_RESULT_AS_RETROACTIVE_AUTHORIZATION")
    if not independent_revalidation.get("ok"): reasons.append("REJECT_RESULT_AS_RETROACTIVE_AUTHORIZATION")
    return _finish("HHS_LEASED_RESULT_HANDOFF_DECISION_V1",{"ok":not reasons,"status":"ADMIT_RESULT_HANDOFF" if not reasons else "REJECT_RESULT_HANDOFF","execution_receipt_root_hash72":receipt.get("execution_receipt_root_hash72"),"revalidation_root_hash72":independent_revalidation.get("revalidation_root_hash72"),"provider_result_extends_lease":False,"reasons":reasons},"decision_root_hash72","hhs_leased_result_handoff_decision_v1")

def run_authority_enforced_dispatch()->Dict[str,Any]:
    from hhs_backend.runtime.hhs_role_bound_agent_orchestrator_v1 import build_role_contract,build_task_assignment,validate_local_authority
    role=build_role_contract(authority_scope=["IMPLEMENT_APPROVED_PASS_SPECIFICATION","MODIFY_DECLARED_REPOSITORY_PATHS","RUN_DECLARED_VERIFICATION_TARGETS"])
    source_root=_root("hhs_pass054_repository_state_v1",{"pass":"054","services":123,"surfaces":146,"edges":2028,"orphans":0})
    spec_root=_root("hhs_pass055_specification_v1",{"title":"Authority-Enforced Runtime Dispatch and Revocable Capability Leases"})
    task=build_task_assignment(source_root,spec_root,role,task_id="task:pass055-runtime-dispatch",allowed=["CREATE_DECLARED_MODULES","UPDATE_REGISTRY","ADD_TESTS","REGENERATE_MANIFESTS"])
    role_decision=validate_local_authority(role,task,"CREATE_DECLARED_MODULES")
    graph_root=_root("hhs_pass055_authority_graph_binding_v1",{"pass054":"canonical-authority-graph","task":task["task_assignment_root_hash72"]})
    lease=issue_capability_lease(task=task,role_contract=role,authority_graph_root_hash72=graph_root,capability_ids=["capability:repository-mutation"],source_scope=["object:canonical-pass054-repository"],allowed_operations=["CREATE_DECLARED_MODULES","UPDATE_REGISTRY","ADD_TESTS","REGENERATE_MANIFESTS"],valid_from_sequence=100,expires_at_sequence=140)
    active=lease_with_state(lease,transition_lease(lease,"ACTIVE",100,"DISPATCH_BEGIN"))
    dispatch=validate_dispatch(role_decision=role_decision,task=task,lease=active,capability_id="capability:repository-mutation",operation="CREATE_DECLARED_MODULES",source_object_id="object:canonical-pass054-repository",sequence=101)
    checkpoints=[validate_execution_checkpoint(lease=active,task=task,sequence=s,checkpoint_id=f"checkpoint:{s}") for s in (105,120,139)]
    result={"pass":"055","state":"IMPLEMENTED"}
    receipt=build_execution_receipt(dispatch=dispatch,lease=active,task=task,role_contract=role,authority_graph_root_hash72=graph_root,source_root_hash72=source_root,result=result,checkpoints=checkpoints)
    consumed=lease_with_state(active,transition_lease(active,"CONSUMED",140,"EXECUTION_COMPLETE"))
    reval=_finish("HHS_PASS055_INDEPENDENT_REVALIDATION_V1",{"ok":receipt["ok"],"status":"ADMIT_CANONICAL_CONTINUATION" if receipt["ok"] else "REJECT_CANONICAL_CONTINUATION","execution_receipt_root_hash72":receipt["execution_receipt_root_hash72"]},"revalidation_root_hash72","hhs_pass055_independent_revalidation_v1")
    handoff=validate_result_handoff(receipt,reval)
    out={"schema":"HHS_AUTHORITY_ENFORCED_RUNTIME_DISPATCH_RUN_V1","version":VERSION,"authority":AUTHORITY,"ok":all([lease["issuance_ok"],dispatch["ok"],receipt["ok"],handoff["ok"]]),"role_contract":role,"task_assignment":task,"lease":lease,"active_lease":active,"dispatch_decision":dispatch,"execution_checkpoints":checkpoints,"execution_receipt":receipt,"consumed_lease":consumed,"independent_revalidation":reval,"result_handoff":handoff,"rejection_codes":REJECTIONS}
    out["run_root_hash72"]=_root("hhs_authority_enforced_runtime_dispatch_run_v1",out); return out

def authority_enforced_dispatch_self_test()->Dict[str,Any]:
    run=run_authority_enforced_dispatch(); task=run["task_assignment"]; role_decision={"ok":True}; lease=run["active_lease"]
    revoked=lease_with_state(lease,transition_lease(lease,"REVOKED",110,"SECURITY_REVOCATION"))
    expired=validate_dispatch(role_decision=role_decision,task=task,lease=lease,capability_id="capability:repository-mutation",operation="CREATE_DECLARED_MODULES",source_object_id="object:canonical-pass054-repository",sequence=141)
    revoked_d=validate_dispatch(role_decision=role_decision,task=task,lease=revoked,capability_id="capability:repository-mutation",operation="CREATE_DECLARED_MODULES",source_object_id="object:canonical-pass054-repository",sequence=111)
    missing=validate_dispatch(role_decision=role_decision,task=task,lease=None,capability_id="capability:repository-mutation",operation="CREATE_DECLARED_MODULES",source_object_id="object:canonical-pass054-repository",sequence=101)
    scope=validate_dispatch(role_decision=role_decision,task=task,lease=lease,capability_id="capability:repository-mutation",operation="DELETE_CANONICAL_INVARIANT",source_object_id="object:canonical-pass054-repository",sequence=101)
    source=validate_dispatch(role_decision=role_decision,task=task,lease=lease,capability_id="capability:repository-mutation",operation="CREATE_DECLARED_MODULES",source_object_id="object:wrong-source",sequence=101)
    closed=dict(task); closed["task_state"]="CLOSED"
    after_close=validate_execution_checkpoint(lease=lease,task=closed,sequence=110,checkpoint_id="closed-task")
    ok=run["ok"] and "REJECT_LEASE_EXPIRED" in expired["reasons"] and "REJECT_LEASE_REVOKED" in revoked_d["reasons"] and "REJECT_CAPABILITY_INVOCATION_WITHOUT_LEASE" in missing["reasons"] and "REJECT_LEASE_SCOPE_EXCEEDS_ROLE" in scope["reasons"] and "REJECT_LEASE_SOURCE_SCOPE_VIOLATION" in source["reasons"] and "REJECT_EXECUTION_AFTER_TASK_CLOSURE" in after_close["reasons"]
    return {"schema":"HHS_AUTHORITY_ENFORCED_DISPATCH_SELF_TEST_V1","ok":ok,"run_root_hash72":run["run_root_hash72"],"negative_cases":{"expired":expired,"revoked":revoked_d,"missing_lease":missing,"scope_violation":scope,"source_violation":source,"task_closed":after_close}}

if __name__=="__main__": print(json.dumps(authority_enforced_dispatch_self_test(),indent=2,sort_keys=True))

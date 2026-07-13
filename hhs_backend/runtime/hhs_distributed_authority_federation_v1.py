"""Pass 056 — Distributed Authority Federation and Witnessed Delegation Chains."""
from __future__ import annotations
from typing import Any, Dict, Iterable, Mapping
import json
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_backend.runtime.hhs_authority_enforced_dispatch_v1 import run_authority_enforced_dispatch

VERSION="PASS_056_DISTRIBUTED_AUTHORITY_FEDERATION_WITNESSED_DELEGATION_CHAINS_V1"
AUTHORITY="HHS_I019_FEDERATED_AUTHORITY_PROPAGATION_BOUNDARY_V1"
REJECTIONS=[
"REJECT_REMOTE_AUTHORITY_WITHOUT_FEDERATION_CONTRACT","REJECT_UNKNOWN_REMOTE_AUTHORITY_IDENTITY",
"REJECT_DELEGATION_WITHOUT_PARENT_LEASE","REJECT_DELEGATION_FROM_INACTIVE_PARENT_LEASE",
"REJECT_SUBLEASE_SCOPE_EXCEEDS_PARENT","REJECT_SUBLEASE_OUTLIVES_PARENT","REJECT_DELEGATION_DEPTH_EXCEEDED",
"REJECT_DELEGATION_CYCLE","REJECT_REMOTE_EXECUTION_AFTER_PARENT_REVOCATION",
"REJECT_REMOTE_EXECUTION_AFTER_PARENT_TASK_CLOSURE","REJECT_BROKEN_DELEGATION_PROVENANCE",
"REJECT_REMOTE_RECEIPT_WITHOUT_CHECKPOINT_CHAIN","REJECT_REMOTE_RESULT_AS_LOCAL_AUTHORITY",
"REJECT_REMOTE_RECEIPT_WITHOUT_LOCAL_REVALIDATION","REJECT_REVOCATION_NOT_PROPAGATED",
"REJECT_FEDERATED_CONTINUATION_WITHOUT_LOCAL_ADMISSION"]

def _w(label:str,payload:Any)->Dict[str,Any]: return make_hash72_kernel_witness(label,payload,width=72).to_dict()
def _root(label:str,payload:Any)->str: return _w(label,payload)["digest"]
def _finish(schema:str,obj:Dict[str,Any],field:str,label:str)->Dict[str,Any]:
    out={"schema":schema,"version":VERSION,"authority":AUTHORITY,**obj}; out[field]=_root(label,out); return out

def build_federation_contract()->Dict[str,Any]:
    return _finish("HHS_FEDERATION_DOMAIN_CONTRACT_V1",{
      "federation_id":"federation:hhs-local-remote-a","local_domain_id":"runtime:local","remote_domain_id":"runtime:remote-a",
      "accepted_remote_role_ids":["role:remote-execution-agent"],"max_delegation_depth":2,
      "required_witness_types":["HHS_HASH72_KERNEL_WITNESS_V1","HHS_REMOTE_CHECKPOINT_CHAIN_V1","HHS_REMOTE_DISPATCH_RECEIPT_V1"],
      "remote_results_are_local_authority":False,"requires_local_revalidation":True,"revocation_propagation_required":True
    },"federation_contract_root_hash72","hhs_federation_domain_contract_v1")

def build_remote_identity(contract:Mapping[str,Any])->Dict[str,Any]:
    return _finish("HHS_REMOTE_AUTHORITY_IDENTITY_V1",{
      "remote_identity_id":"remote-identity:runtime-a-agent","remote_domain_id":contract["remote_domain_id"],
      "component_id":"agent:remote-executor","role_id":"role:remote-execution-agent",
      "federation_contract_root_hash72":contract["federation_contract_root_hash72"],"identity_status":"ADMITTED"
    },"remote_identity_root_hash72","hhs_remote_authority_identity_v1")

def issue_sublease(parent:Mapping[str,Any],contract:Mapping[str,Any],remote:Mapping[str,Any],*,capabilities:Iterable[str],sources:Iterable[str],operations:Iterable[str],start:int,end:int,depth:int,parent_chain_ids:Iterable[str]=())->Dict[str,Any]:
    reasons=[]; pstate=parent.get("lease_state")
    if not contract: reasons.append("REJECT_REMOTE_AUTHORITY_WITHOUT_FEDERATION_CONTRACT")
    if not parent: reasons.append("REJECT_DELEGATION_WITHOUT_PARENT_LEASE")
    if pstate not in {"ISSUED","ACTIVE"}: reasons.append("REJECT_DELEGATION_FROM_INACTIVE_PARENT_LEASE")
    if not set(capabilities).issubset(set(parent.get("capability_ids",[]))) or not set(sources).issubset(set(parent.get("source_scope",[]))) or not set(operations).issubset(set(parent.get("allowed_operations",[]))): reasons.append("REJECT_SUBLEASE_SCOPE_EXCEEDS_PARENT")
    if start < parent.get("valid_from_sequence",0) or end > parent.get("expires_at_sequence",-1): reasons.append("REJECT_SUBLEASE_OUTLIVES_PARENT")
    if depth>contract.get("max_delegation_depth",0): reasons.append("REJECT_DELEGATION_DEPTH_EXCEEDED")
    chain=list(parent_chain_ids)
    if remote.get("component_id") in chain: reasons.append("REJECT_DELEGATION_CYCLE")
    return _finish("HHS_DELEGATED_CAPABILITY_SUBLEASE_V1",{
      "sublease_id":"sublease:pass056-remote-a","parent_lease_root_hash72":parent.get("lease_root_hash72"),
      "federation_contract_root_hash72":contract.get("federation_contract_root_hash72"),"remote_identity_root_hash72":remote.get("remote_identity_root_hash72"),
      "remote_component_id":remote.get("component_id"),"remote_role_id":remote.get("role_id"),
      "capability_ids":list(capabilities),"source_scope":list(sources),"allowed_operations":list(operations),
      "valid_from_sequence":start,"expires_at_sequence":end,"delegation_depth":depth,"delegable":False,
      "authority_amplified":False,"sublease_state":"ACTIVE" if not reasons else "REJECTED","issuance_ok":not reasons,"reasons":sorted(set(reasons))
    },"sublease_root_hash72","hhs_delegated_capability_sublease_v1")

def build_delegation_chain(parent:Mapping[str,Any],sublease:Mapping[str,Any],contract:Mapping[str,Any])->Dict[str,Any]:
    reasons=[]
    if not sublease.get("issuance_ok"): reasons.append("REJECT_BROKEN_DELEGATION_PROVENANCE")
    return _finish("HHS_WITNESSED_DELEGATION_CHAIN_V1",{
      "chain_id":"delegation-chain:pass056","local_delegation_root_hash72":parent.get("lease_root_hash72"),
      "federation_contract_root_hash72":contract.get("federation_contract_root_hash72"),"sublease_roots":[sublease.get("sublease_root_hash72")],
      "depth":sublease.get("delegation_depth"),"complete":not reasons,"reasons":reasons
    },"delegation_chain_root_hash72","hhs_witnessed_delegation_chain_v1")

def validate_remote_dispatch(parent:Mapping[str,Any],sublease:Mapping[str,Any],chain:Mapping[str,Any],*,sequence:int)->Dict[str,Any]:
    reasons=[]
    if parent.get("lease_state")=="REVOKED": reasons.append("REJECT_REMOTE_EXECUTION_AFTER_PARENT_REVOCATION")
    if parent.get("lease_state")=="TASK_CLOSED": reasons.append("REJECT_REMOTE_EXECUTION_AFTER_PARENT_TASK_CLOSURE")
    if not chain.get("complete"): reasons.append("REJECT_BROKEN_DELEGATION_PROVENANCE")
    if sequence<sublease.get("valid_from_sequence",0) or sequence>sublease.get("expires_at_sequence",-1): reasons.append("REJECT_SUBLEASE_OUTLIVES_PARENT")
    return _finish("HHS_REMOTE_DISPATCH_DECISION_V1",{
      "ok":not reasons,"status":"ADMIT_REMOTE_DISPATCH" if not reasons else "REJECT_REMOTE_DISPATCH",
      "parent_lease_root_hash72":parent.get("lease_root_hash72"),"sublease_root_hash72":sublease.get("sublease_root_hash72"),
      "delegation_chain_root_hash72":chain.get("delegation_chain_root_hash72"),"sequence":sequence,"reasons":sorted(set(reasons))
    },"remote_dispatch_decision_root_hash72","hhs_remote_dispatch_decision_v1")

def build_remote_checkpoint_chain(sublease:Mapping[str,Any],sequences:Iterable[int])->Dict[str,Any]:
    cps=[_finish("HHS_REMOTE_EXECUTION_CHECKPOINT_V1",{"sublease_root_hash72":sublease["sublease_root_hash72"],"sequence":s,"ok":sublease.get("sublease_state")=="ACTIVE"},"checkpoint_root_hash72","hhs_remote_execution_checkpoint_v1") for s in sequences]
    return _finish("HHS_REMOTE_CHECKPOINT_CHAIN_V1",{"sublease_root_hash72":sublease["sublease_root_hash72"],"checkpoints":cps,"complete":bool(cps) and all(x["ok"] for x in cps)},"checkpoint_chain_root_hash72","hhs_remote_checkpoint_chain_v1")

def build_remote_receipt(dispatch:Mapping[str,Any],chain:Mapping[str,Any],checkpoints:Mapping[str,Any],result:Any)->Dict[str,Any]:
    reasons=[]
    if not dispatch.get("ok"): reasons.append("REJECT_BROKEN_DELEGATION_PROVENANCE")
    if not checkpoints.get("complete"): reasons.append("REJECT_REMOTE_RECEIPT_WITHOUT_CHECKPOINT_CHAIN")
    return _finish("HHS_REMOTE_DISPATCH_RECEIPT_V1",{
      "ok":not reasons,"remote_dispatch_decision_root_hash72":dispatch.get("remote_dispatch_decision_root_hash72"),
      "delegation_chain_root_hash72":chain.get("delegation_chain_root_hash72"),"checkpoint_chain_root_hash72":checkpoints.get("checkpoint_chain_root_hash72"),
      "remote_result_root_hash72":_root("hhs_pass056_remote_result_v1",result),"remote_result_is_local_authority":False,"reasons":reasons
    },"remote_receipt_root_hash72","hhs_remote_dispatch_receipt_v1")

def propagate_revocation(parent:Mapping[str,Any],subleases:Iterable[Mapping[str,Any]],sequence:int)->Dict[str,Any]:
    descendants=[{"sublease_root_hash72":s["sublease_root_hash72"],"state":"REVOKED","sequence":sequence} for s in subleases]
    ok=parent.get("lease_state")=="REVOKED" and bool(descendants)
    return _finish("HHS_DELEGATION_REVOCATION_PROPAGATION_V1",{
      "ok":ok,"parent_lease_root_hash72":parent.get("lease_root_hash72"),"descendant_revocations":descendants,
      "propagation_complete":ok,"reasons":[] if ok else ["REJECT_REVOCATION_NOT_PROPAGATED"]
    },"revocation_propagation_root_hash72","hhs_delegation_revocation_propagation_v1")

def federated_ingress(receipt:Mapping[str,Any],contract:Mapping[str,Any],local_revalidation_ok:bool)->Dict[str,Any]:
    reasons=[]
    if not receipt.get("ok"): reasons.append("REJECT_BROKEN_DELEGATION_PROVENANCE")
    if receipt.get("remote_result_is_local_authority"): reasons.append("REJECT_REMOTE_RESULT_AS_LOCAL_AUTHORITY")
    if not local_revalidation_ok: reasons.append("REJECT_REMOTE_RECEIPT_WITHOUT_LOCAL_REVALIDATION")
    return _finish("HHS_FEDERATED_RESULT_INGRESS_V1",{
      "ok":not reasons,"status":"ADMIT_FEDERATED_RESULT_INGRESS" if not reasons else "REJECT_FEDERATED_RESULT_INGRESS",
      "remote_receipt_root_hash72":receipt.get("remote_receipt_root_hash72"),"federation_contract_root_hash72":contract.get("federation_contract_root_hash72"),
      "local_revalidation_performed":local_revalidation_ok,"canonical_continuation":not reasons,"reasons":sorted(set(reasons))
    },"federated_ingress_root_hash72","hhs_federated_result_ingress_v1")

def run_distributed_authority_federation()->Dict[str,Any]:
    p55=run_authority_enforced_dispatch(); parent=p55["active_lease"]
    contract=build_federation_contract(); remote=build_remote_identity(contract)
    sub=issue_sublease(parent,contract,remote,capabilities=parent["capability_ids"],sources=parent["source_scope"],operations=["CREATE_DECLARED_MODULES"],start=110,end=130,depth=1)
    chain=build_delegation_chain(parent,sub,contract); dispatch=validate_remote_dispatch(parent,sub,chain,sequence=111)
    cps=build_remote_checkpoint_chain(sub,[115,122,129]); receipt=build_remote_receipt(dispatch,chain,cps,{"pass":"056","remote_execution":"COMPLETE"})
    ingress=federated_ingress(receipt,contract,True)
    out={"schema":"HHS_DISTRIBUTED_AUTHORITY_FEDERATION_RUN_V1","version":VERSION,"authority":AUTHORITY,"ok":all([sub["issuance_ok"],chain["complete"],dispatch["ok"],cps["complete"],receipt["ok"],ingress["ok"]]),
      "federation_contract":contract,"remote_identity":remote,"parent_lease":parent,"delegated_sublease":sub,"delegation_chain":chain,
      "remote_dispatch":dispatch,"remote_checkpoint_chain":cps,"remote_execution_receipt":receipt,"federated_ingress":ingress,"rejection_codes":REJECTIONS}
    out["run_root_hash72"]=_root("hhs_distributed_authority_federation_run_v1",out); return out

def distributed_authority_federation_self_test()->Dict[str,Any]:
    run=run_distributed_authority_federation(); parent=run["parent_lease"]; contract=run["federation_contract"]; remote=run["remote_identity"]
    over=issue_sublease(parent,contract,remote,capabilities=["capability:repository-mutation","capability:extra"],sources=parent["source_scope"],operations=["CREATE_DECLARED_MODULES"],start=110,end=130,depth=1)
    deep=issue_sublease(parent,contract,remote,capabilities=parent["capability_ids"],sources=parent["source_scope"],operations=["CREATE_DECLARED_MODULES"],start=110,end=130,depth=3)
    cyc=issue_sublease(parent,contract,remote,capabilities=parent["capability_ids"],sources=parent["source_scope"],operations=["CREATE_DECLARED_MODULES"],start=110,end=130,depth=1,parent_chain_ids=[remote["component_id"]])
    revoked=dict(parent); revoked["lease_state"]="REVOKED"
    rd=validate_remote_dispatch(revoked,run["delegated_sublease"],run["delegation_chain"],sequence=120)
    prop=propagate_revocation(revoked,[run["delegated_sublease"]],120)
    bad_ingress=federated_ingress(run["remote_execution_receipt"],contract,False)
    ok=run["ok"] and "REJECT_SUBLEASE_SCOPE_EXCEEDS_PARENT" in over["reasons"] and "REJECT_DELEGATION_DEPTH_EXCEEDED" in deep["reasons"] and "REJECT_DELEGATION_CYCLE" in cyc["reasons"] and "REJECT_REMOTE_EXECUTION_AFTER_PARENT_REVOCATION" in rd["reasons"] and prop["ok"] and "REJECT_REMOTE_RECEIPT_WITHOUT_LOCAL_REVALIDATION" in bad_ingress["reasons"]
    return {"schema":"HHS_DISTRIBUTED_AUTHORITY_FEDERATION_SELF_TEST_V1","ok":ok,"run_root_hash72":run["run_root_hash72"],"negative_cases":{"scope_amplification":over,"depth":deep,"cycle":cyc,"revoked_parent":rd,"missing_local_revalidation":bad_ingress},"revocation_propagation":prop}

if __name__=="__main__": print(json.dumps(distributed_authority_federation_self_test(),indent=2,sort_keys=True))

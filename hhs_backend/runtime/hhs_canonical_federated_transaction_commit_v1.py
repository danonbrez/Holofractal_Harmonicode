"""Pass 059 — Canonical Federated Transaction Commit and Compensating Rollback."""
from __future__ import annotations
from typing import Any, Dict, Mapping, Iterable
import json
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_backend.runtime.hhs_canonical_federated_state_reconciliation_v1 import run_canonical_federated_state_reconciliation

VERSION = "PASS_059_CANONICAL_FEDERATED_TRANSACTION_COMMIT_COMPENSATING_ROLLBACK_V1"
AUTHORITY = "HHS_I019_CANONICAL_FEDERATED_TRANSACTION_AUTHORITY_V1"
REJECTIONS = [
 "REJECT_TRANSACTION_WITHOUT_CANONICAL_MERGE_BASE", "REJECT_PREPARE_WITHOUT_PARTICIPANT_AUTHORITY",
 "REJECT_COMMIT_WITHOUT_COMPLETE_PREPARE_SET", "REJECT_PARTIAL_COMMIT_AS_CANONICAL_COMPLETION",
 "REJECT_COMMIT_EPOCH_MISMATCH", "REJECT_UNWITNESSED_TRANSACTION_DECISION",
 "REJECT_COMPENSATION_WITHOUT_ORIGINAL_EFFECT_ROOT", "REJECT_COMPENSATION_EXCEEDS_ORIGINAL_SCOPE",
 "REJECT_ROLLBACK_WITHOUT_COMPLETE_COMPENSATION", "REJECT_TRANSACTION_RESULT_WITHOUT_LOCAL_REVALIDATION",
 "REJECT_SUCCESSFUL_PARTICIPANT_AS_GLOBAL_COMMIT_AUTHORITY", "REJECT_RETRY_AS_DUPLICATE_AUTHORITY",
]

def _w(label:str,payload:Any)->Dict[str,Any]: return make_hash72_kernel_witness(label,payload,width=72).to_dict()
def _root(label:str,payload:Any)->str: return _w(label,payload)["digest"]
def _finish(schema:str,obj:Dict[str,Any],field:str,label:str)->Dict[str,Any]:
    out={"schema":schema,"version":VERSION,"authority":AUTHORITY,**obj}; out[field]=_root(label,out); return out

def build_transaction_contract(transaction_id:str, merge_root:str, participants:Iterable[str], operations:Mapping[str,str], commit_epoch:int=1)->Dict[str,Any]:
    ps=sorted(set(participants)); reasons=[]
    if not merge_root: reasons.append("REJECT_TRANSACTION_WITHOUT_CANONICAL_MERGE_BASE")
    return _finish("HHS_FEDERATED_TRANSACTION_CONTRACT_V1",{
      "transaction_id":transaction_id,"canonical_merge_base_root_hash72":merge_root,"participants":ps,
      "participant_operations":dict(operations),"commit_epoch":commit_epoch,"atomicity_policy":"ALL_PREPARED_OR_COMPENSATE",
      "partial_success_is_canonical_completion":False,"reasons":reasons
    },"transaction_contract_root_hash72","hhs_federated_transaction_contract_v1")

def build_prepare_record(contract:Mapping[str,Any], participant_id:str, authority_root:str, source_root:str, effect:Mapping[str,Any], prepared:bool=True)->Dict[str,Any]:
    reasons=[]
    if participant_id not in contract.get("participants",[]): reasons.append("REJECT_PREPARE_WITHOUT_PARTICIPANT_AUTHORITY")
    if not authority_root: reasons.append("REJECT_PREPARE_WITHOUT_PARTICIPANT_AUTHORITY")
    return _finish("HHS_FEDERATED_TRANSACTION_PREPARE_RECORD_V1",{
      "transaction_contract_root_hash72":contract.get("transaction_contract_root_hash72"),"participant_id":participant_id,
      "participant_authority_root_hash72":authority_root,"source_root_hash72":source_root,"proposed_effect":dict(effect),
      "proposed_effect_root_hash72":_root("hhs_transaction_proposed_effect_v1",dict(effect)),"prepared":prepared and not reasons,
      "prepare_state":"PREPARED" if prepared and not reasons else "REJECTED","reasons":reasons
    },"prepare_record_root_hash72","hhs_federated_transaction_prepare_record_v1")

def decide_commit(contract:Mapping[str,Any], prepares:Iterable[Mapping[str,Any]], *, commit_epoch:int, decision_witnessed:bool=True)->Dict[str,Any]:
    prs=list(prepares); reasons=[]; expected=set(contract.get("participants",[])); got={x.get("participant_id") for x in prs if x.get("prepared")}
    if got!=expected: reasons.append("REJECT_COMMIT_WITHOUT_COMPLETE_PREPARE_SET")
    if commit_epoch!=contract.get("commit_epoch"): reasons.append("REJECT_COMMIT_EPOCH_MISMATCH")
    if not decision_witnessed: reasons.append("REJECT_UNWITNESSED_TRANSACTION_DECISION")
    committed=not reasons
    return _finish("HHS_FEDERATED_TRANSACTION_COMMIT_DECISION_V1",{
      "transaction_contract_root_hash72":contract.get("transaction_contract_root_hash72"),
      "prepare_record_roots_hash72":[x.get("prepare_record_root_hash72") for x in prs],"commit_epoch":commit_epoch,
      "decision_witnessed":decision_witnessed,"commit_state":"COMMITTED" if committed else "ABORTED",
      "canonical_completion":False,"participant_success_confers_global_commit_authority":False,"reasons":reasons
    },"commit_decision_root_hash72","hhs_federated_transaction_commit_decision_v1")

def build_participant_receipt(commit:Mapping[str,Any], participant_id:str, effect_root:str, success:bool)->Dict[str,Any]:
    return _finish("HHS_FEDERATED_PARTICIPANT_COMMIT_RECEIPT_V1",{
      "commit_decision_root_hash72":commit.get("commit_decision_root_hash72"),"participant_id":participant_id,
      "effect_root_hash72":effect_root,"success":success,"success_confers_global_authority":False
    },"participant_receipt_root_hash72","hhs_federated_participant_commit_receipt_v1")

def build_compensation_record(receipt:Mapping[str,Any], compensation:Mapping[str,Any], *, within_original_scope:bool=True)->Dict[str,Any]:
    reasons=[]
    if not receipt.get("effect_root_hash72"): reasons.append("REJECT_COMPENSATION_WITHOUT_ORIGINAL_EFFECT_ROOT")
    if not within_original_scope: reasons.append("REJECT_COMPENSATION_EXCEEDS_ORIGINAL_SCOPE")
    return _finish("HHS_FEDERATED_COMPENSATION_RECORD_V1",{
      "participant_receipt_root_hash72":receipt.get("participant_receipt_root_hash72"),
      "original_effect_root_hash72":receipt.get("effect_root_hash72"),"compensation":dict(compensation),
      "compensation_effect_root_hash72":_root("hhs_transaction_compensation_effect_v1",dict(compensation)),
      "within_original_scope":within_original_scope,"compensation_state":"COMPENSATED" if not reasons else "REJECTED","reasons":reasons
    },"compensation_record_root_hash72","hhs_federated_compensation_record_v1")

def decide_rollback(contract:Mapping[str,Any], receipts:Iterable[Mapping[str,Any]], compensations:Iterable[Mapping[str,Any]], *, local_revalidation_ok:bool)->Dict[str,Any]:
    rs=list(receipts); cs=list(compensations); reasons=[]
    successful={r.get("participant_id") for r in rs if r.get("success")}
    compensated={r.get("participant_id") for r,c in zip(rs,cs) if r.get("success") and c.get("compensation_state")=="COMPENSATED"}
    if successful!=compensated: reasons.append("REJECT_ROLLBACK_WITHOUT_COMPLETE_COMPENSATION")
    if not local_revalidation_ok: reasons.append("REJECT_TRANSACTION_RESULT_WITHOUT_LOCAL_REVALIDATION")
    rolled=not reasons
    return _finish("HHS_FEDERATED_TRANSACTION_ROLLBACK_DECISION_V1",{
      "transaction_contract_root_hash72":contract.get("transaction_contract_root_hash72"),
      "participant_receipt_roots_hash72":[x.get("participant_receipt_root_hash72") for x in rs],
      "compensation_record_roots_hash72":[x.get("compensation_record_root_hash72") for x in cs],
      "local_revalidation_performed":local_revalidation_ok,"rollback_complete":rolled,
      "canonical_continuation":rolled,"status":"ADMIT_COMPENSATING_ROLLBACK" if rolled else "REJECT_COMPENSATING_ROLLBACK","reasons":reasons
    },"rollback_decision_root_hash72","hhs_federated_transaction_rollback_decision_v1")

def finalize_transaction(commit:Mapping[str,Any], receipts:Iterable[Mapping[str,Any]], *, local_revalidation_ok:bool)->Dict[str,Any]:
    rs=list(receipts); reasons=list(commit.get("reasons",[]))
    if not all(r.get("success") for r in rs): reasons.append("REJECT_PARTIAL_COMMIT_AS_CANONICAL_COMPLETION")
    if not local_revalidation_ok: reasons.append("REJECT_TRANSACTION_RESULT_WITHOUT_LOCAL_REVALIDATION")
    admitted=not reasons
    return _finish("HHS_CANONICAL_FEDERATED_TRANSACTION_DECISION_V1",{
      "commit_decision_root_hash72":commit.get("commit_decision_root_hash72"),
      "participant_receipt_roots_hash72":[x.get("participant_receipt_root_hash72") for x in rs],
      "local_revalidation_performed":local_revalidation_ok,"canonical_continuation":admitted,
      "status":"ADMIT_CANONICAL_FEDERATED_TRANSACTION" if admitted else "REJECT_CANONICAL_FEDERATED_TRANSACTION",
      "successful_participant_confers_global_authority":False,"reasons":reasons
    },"transaction_decision_root_hash72","hhs_canonical_federated_transaction_decision_v1")

def run_canonical_federated_transaction_commit()->Dict[str,Any]:
    p58=run_canonical_federated_state_reconciliation(); merge=p58["merge_decision"]["merge_decision_root_hash72"]
    contract=build_transaction_contract("txn:pass059",merge,["runtime:local","runtime:remote-a"],{"runtime:local":"WRITE_LOCAL","runtime:remote-a":"WRITE_REMOTE"},9)
    a=p58["run_root_hash72"]
    p1=build_prepare_record(contract,"runtime:local",a,merge,{"counter":9})
    p2=build_prepare_record(contract,"runtime:remote-a",a,merge,{"remote_counter":9})
    commit=decide_commit(contract,[p1,p2],commit_epoch=9)
    r1=build_participant_receipt(commit,"runtime:local",p1["proposed_effect_root_hash72"],True)
    r2=build_participant_receipt(commit,"runtime:remote-a",p2["proposed_effect_root_hash72"],True)
    final=finalize_transaction(commit,[r1,r2],local_revalidation_ok=True)
    out={"schema":"HHS_CANONICAL_FEDERATED_TRANSACTION_RUN_V1","version":VERSION,"authority":AUTHORITY,
      "ok":p58["ok"] and final["canonical_continuation"],"pass058_reconciliation_root_hash72":p58["run_root_hash72"],
      "transaction_contract":contract,"prepare_records":[p1,p2],"commit_decision":commit,"participant_receipts":[r1,r2],
      "transaction_decision":final,"rejection_codes":REJECTIONS}
    out["run_root_hash72"]=_root("hhs_canonical_federated_transaction_run_v1",out); return out

def canonical_federated_transaction_commit_self_test()->Dict[str,Any]:
    run=run_canonical_federated_transaction_commit(); c=run["transaction_contract"]; ps=run["prepare_records"]
    partial=decide_commit(c,[ps[0]],commit_epoch=9)
    epoch=decide_commit(c,ps,commit_epoch=10)
    commit=run["commit_decision"]; rs=[run["participant_receipts"][0],build_participant_receipt(commit,"runtime:remote-a",ps[1]["proposed_effect_root_hash72"],False)]
    partial_final=finalize_transaction(commit,rs,local_revalidation_ok=True)
    comp=build_compensation_record(rs[0],{"counter":8})
    rollback=decide_rollback(c,[rs[0]],[comp],local_revalidation_ok=True)
    no_reval=finalize_transaction(commit,run["participant_receipts"],local_revalidation_ok=False)
    ok=run["ok"] and "REJECT_COMMIT_WITHOUT_COMPLETE_PREPARE_SET" in partial["reasons"] and "REJECT_COMMIT_EPOCH_MISMATCH" in epoch["reasons"] and "REJECT_PARTIAL_COMMIT_AS_CANONICAL_COMPLETION" in partial_final["reasons"] and rollback["rollback_complete"] and "REJECT_TRANSACTION_RESULT_WITHOUT_LOCAL_REVALIDATION" in no_reval["reasons"]
    return {"schema":"HHS_CANONICAL_FEDERATED_TRANSACTION_SELF_TEST_V1","ok":ok,"run_root_hash72":run["run_root_hash72"],"negative_cases":{"partial_prepare":partial,"epoch_mismatch":epoch,"partial_commit":partial_final,"no_revalidation":no_reval},"rollback_case":rollback}

if __name__=="__main__": print(json.dumps(canonical_federated_transaction_commit_self_test(),indent=2,sort_keys=True))

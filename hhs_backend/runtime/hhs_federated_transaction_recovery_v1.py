"""Pass 060 — Federated Transaction Recovery, Idempotent Replay, and Exactly-Once Canonical Admission."""
from __future__ import annotations
from typing import Any, Dict, Mapping, Iterable
import json
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_backend.runtime.hhs_canonical_federated_transaction_commit_v1 import run_canonical_federated_transaction_commit

VERSION="PASS_060_FEDERATED_TRANSACTION_RECOVERY_IDEMPOTENT_REPLAY_EXACTLY_ONCE_ADMISSION_V1"
AUTHORITY="HHS_I019_FEDERATED_TRANSACTION_RECOVERY_AUTHORITY_V1"
REJECTIONS=[
"REJECT_RECOVERY_WITHOUT_TRANSACTION_RECEIPT","REJECT_REPLAY_WITHOUT_IDEMPOTENCY_KEY",
"REJECT_IDEMPOTENCY_KEY_REBOUND_TO_DIFFERENT_EFFECT","REJECT_DUPLICATE_EFFECT_APPLICATION",
"REJECT_REPLAY_AS_NEW_AUTHORITY","REJECT_RECOVERY_WITHOUT_CHECKPOINT_CHAIN",
"REJECT_EXACTLY_ONCE_ADMISSION_WITHOUT_CANONICAL_ADMISSION_RECORD",
"REJECT_DUPLICATE_CANONICAL_ADMISSION","REJECT_RECOVERY_EPOCH_MISMATCH",
"REJECT_RECOVERY_WITHOUT_LOCAL_REVALIDATION","REJECT_PARTIAL_RECOVERY_AS_CANONICAL_COMPLETION",
]
def _w(label:str,payload:Any)->Dict[str,Any]: return make_hash72_kernel_witness(label,payload,width=72).to_dict()
def _root(label:str,payload:Any)->str: return _w(label,payload)["digest"]
def _finish(schema:str,obj:Dict[str,Any],field:str,label:str)->Dict[str,Any]:
 out={"schema":schema,"version":VERSION,"authority":AUTHORITY,**obj}; out[field]=_root(label,out); return out

def build_recovery_contract(transaction_root:str,recovery_epoch:int,participants:Iterable[str])->Dict[str,Any]:
 reasons=[]
 if not transaction_root: reasons.append("REJECT_RECOVERY_WITHOUT_TRANSACTION_RECEIPT")
 return _finish("HHS_FEDERATED_TRANSACTION_RECOVERY_CONTRACT_V1",{
  "transaction_decision_root_hash72":transaction_root,"recovery_epoch":recovery_epoch,
  "participants":sorted(set(participants)),"replay_policy":"IDEMPOTENT_EFFECT_EXACTLY_ONCE_ADMISSION",
  "replay_confers_authority":False,"reasons":reasons
 },"recovery_contract_root_hash72","hhs_federated_transaction_recovery_contract_v1")

def build_idempotency_record(contract:Mapping[str,Any],participant_id:str,idempotency_key:str,effect_root:str)->Dict[str,Any]:
 reasons=[]
 if not idempotency_key: reasons.append("REJECT_REPLAY_WITHOUT_IDEMPOTENCY_KEY")
 return _finish("HHS_TRANSACTION_IDEMPOTENCY_RECORD_V1",{
  "recovery_contract_root_hash72":contract.get("recovery_contract_root_hash72"),"participant_id":participant_id,
  "idempotency_key":idempotency_key,"effect_root_hash72":effect_root,"effect_application_count":1,
  "canonical_admission_count":0,"reasons":reasons
 },"idempotency_record_root_hash72","hhs_transaction_idempotency_record_v1")

def validate_replay(record:Mapping[str,Any],candidate_effect_root:str,*,prior_effect_application_count:int=1)->Dict[str,Any]:
 reasons=[]
 same=record.get("effect_root_hash72")==candidate_effect_root
 if not record.get("idempotency_key"): reasons.append("REJECT_REPLAY_WITHOUT_IDEMPOTENCY_KEY")
 if not same: reasons.append("REJECT_IDEMPOTENCY_KEY_REBOUND_TO_DIFFERENT_EFFECT")
 effect_applied=prior_effect_application_count==0 and same and not reasons
 duplicate_suppressed=prior_effect_application_count>0 and same and not reasons
 return _finish("HHS_IDEMPOTENT_REPLAY_DECISION_V1",{
  "idempotency_record_root_hash72":record.get("idempotency_record_root_hash72"),
  "candidate_effect_root_hash72":candidate_effect_root,"same_effect":same,
  "prior_effect_application_count":prior_effect_application_count,
  "effect_applied":effect_applied,"duplicate_effect_suppressed":duplicate_suppressed,
  "replay_confers_new_authority":False,"status":"ADMIT_IDEMPOTENT_REPLAY" if not reasons else "REJECT_REPLAY",
  "reasons":reasons
 },"replay_decision_root_hash72","hhs_idempotent_replay_decision_v1")

def build_recovery_checkpoint_chain(contract:Mapping[str,Any],participant_roots:Iterable[str],sequences:Iterable[int])->Dict[str,Any]:
 roots=list(participant_roots); seq=list(sequences); complete=bool(roots) and len(seq)>=len(roots)
 reasons=[] if complete else ["REJECT_RECOVERY_WITHOUT_CHECKPOINT_CHAIN"]
 return _finish("HHS_TRANSACTION_RECOVERY_CHECKPOINT_CHAIN_V1",{
  "recovery_contract_root_hash72":contract.get("recovery_contract_root_hash72"),
  "participant_receipt_roots_hash72":roots,"checkpoint_sequences":seq,"chain_complete":complete,"reasons":reasons
 },"checkpoint_chain_root_hash72","hhs_transaction_recovery_checkpoint_chain_v1")

def build_canonical_admission_record(contract:Mapping[str,Any],checkpoint:Mapping[str,Any],replay_decisions:Iterable[Mapping[str,Any]],*,recovery_epoch:int,local_revalidation_ok:bool,prior_admission_count:int=0)->Dict[str,Any]:
 ds=list(replay_decisions); reasons=[]
 if recovery_epoch!=contract.get("recovery_epoch"): reasons.append("REJECT_RECOVERY_EPOCH_MISMATCH")
 if not checkpoint.get("chain_complete"): reasons.append("REJECT_RECOVERY_WITHOUT_CHECKPOINT_CHAIN")
 if prior_admission_count>0: reasons.append("REJECT_DUPLICATE_CANONICAL_ADMISSION")
 if not local_revalidation_ok: reasons.append("REJECT_RECOVERY_WITHOUT_LOCAL_REVALIDATION")
 if any(d.get("reasons") for d in ds): reasons.append("REJECT_PARTIAL_RECOVERY_AS_CANONICAL_COMPLETION")
 admitted=not reasons
 return _finish("HHS_EXACTLY_ONCE_CANONICAL_ADMISSION_RECORD_V1",{
  "recovery_contract_root_hash72":contract.get("recovery_contract_root_hash72"),
  "checkpoint_chain_root_hash72":checkpoint.get("checkpoint_chain_root_hash72"),
  "replay_decision_roots_hash72":[d.get("replay_decision_root_hash72") for d in ds],
  "recovery_epoch":recovery_epoch,"prior_canonical_admission_count":prior_admission_count,
  "local_revalidation_performed":local_revalidation_ok,"canonical_admission_count":1 if admitted else prior_admission_count,
  "exactly_once_admitted":admitted,"canonical_continuation":admitted,
  "status":"ADMIT_EXACTLY_ONCE_CANONICAL_RECOVERY" if admitted else "REJECT_CANONICAL_RECOVERY",
  "replay_confers_authority":False,"reasons":reasons
 },"canonical_admission_root_hash72","hhs_exactly_once_canonical_admission_record_v1")

def run_federated_transaction_recovery()->Dict[str,Any]:
 p59=run_canonical_federated_transaction_commit(); tx=p59["transaction_decision"]
 contract=build_recovery_contract(tx["transaction_decision_root_hash72"],10,[r["participant_id"] for r in p59["participant_receipts"]])
 records=[build_idempotency_record(contract,r["participant_id"],f"idem:{r['participant_id']}:pass060",r["effect_root_hash72"]) for r in p59["participant_receipts"]]
 decisions=[validate_replay(rec,rec["effect_root_hash72"],prior_effect_application_count=1) for rec in records]
 checkpoint=build_recovery_checkpoint_chain(contract,[r["participant_receipt_root_hash72"] for r in p59["participant_receipts"]],[201,202])
 admission=build_canonical_admission_record(contract,checkpoint,decisions,recovery_epoch=10,local_revalidation_ok=True)
 out={"schema":"HHS_FEDERATED_TRANSACTION_RECOVERY_RUN_V1","version":VERSION,"authority":AUTHORITY,
  "ok":p59["ok"] and admission["exactly_once_admitted"],"pass059_transaction_root_hash72":p59["run_root_hash72"],
  "recovery_contract":contract,"idempotency_records":records,"replay_decisions":decisions,
  "checkpoint_chain":checkpoint,"canonical_admission":admission,"rejection_codes":REJECTIONS}
 out["run_root_hash72"]=_root("hhs_federated_transaction_recovery_run_v1",out); return out

def federated_transaction_recovery_self_test()->Dict[str,Any]:
 run=run_federated_transaction_recovery(); c=run["recovery_contract"]; rec=run["idempotency_records"][0]
 rebound=validate_replay(rec,_root("different_effect",{"x":2}),prior_effect_application_count=1)
 duplicate=build_canonical_admission_record(c,run["checkpoint_chain"],run["replay_decisions"],recovery_epoch=10,local_revalidation_ok=True,prior_admission_count=1)
 epoch=build_canonical_admission_record(c,run["checkpoint_chain"],run["replay_decisions"],recovery_epoch=11,local_revalidation_ok=True)
 no_reval=build_canonical_admission_record(c,run["checkpoint_chain"],run["replay_decisions"],recovery_epoch=10,local_revalidation_ok=False)
 incomplete=build_recovery_checkpoint_chain(c,[],[])
 no_chain=build_canonical_admission_record(c,incomplete,run["replay_decisions"],recovery_epoch=10,local_revalidation_ok=True)
 ok=run["ok"] and all(d["duplicate_effect_suppressed"] and not d["effect_applied"] for d in run["replay_decisions"]) and "REJECT_IDEMPOTENCY_KEY_REBOUND_TO_DIFFERENT_EFFECT" in rebound["reasons"] and "REJECT_DUPLICATE_CANONICAL_ADMISSION" in duplicate["reasons"] and "REJECT_RECOVERY_EPOCH_MISMATCH" in epoch["reasons"] and "REJECT_RECOVERY_WITHOUT_LOCAL_REVALIDATION" in no_reval["reasons"] and "REJECT_RECOVERY_WITHOUT_CHECKPOINT_CHAIN" in no_chain["reasons"]
 return {"schema":"HHS_FEDERATED_TRANSACTION_RECOVERY_SELF_TEST_V1","ok":ok,"run_root_hash72":run["run_root_hash72"],"negative_cases":{"rebound":rebound,"duplicate_admission":duplicate,"epoch":epoch,"no_revalidation":no_reval,"missing_chain":no_chain}}
if __name__=="__main__": print(json.dumps(federated_transaction_recovery_self_test(),indent=2,sort_keys=True))

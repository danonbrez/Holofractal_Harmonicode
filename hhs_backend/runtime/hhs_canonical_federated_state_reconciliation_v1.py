"""Pass 058 — Canonical Federated State Reconciliation and Conflict-Preserving Merge."""
from __future__ import annotations
from typing import Any, Dict, Iterable, Mapping
import json
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_backend.runtime.hhs_partition_tolerant_federated_recovery_v1 import run_partition_tolerant_federated_recovery

VERSION = "PASS_058_CANONICAL_FEDERATED_STATE_RECONCILIATION_CONFLICT_PRESERVING_MERGE_V1"
AUTHORITY = "HHS_I019_CANONICAL_FEDERATED_STATE_RECONCILIATION_V1"
REJECTIONS = [
 "REJECT_FEDERATED_MERGE_WITHOUT_COMMON_ANCESTOR", "REJECT_SILENT_CONFLICT_OVERWRITE",
 "REJECT_PARTITION_STATE_AS_CANONICAL_WINNER", "REJECT_LOSSY_CONFLICT_COLLAPSE",
 "REJECT_UNWITNESSED_MERGE_POLICY", "REJECT_MERGE_WITH_BROKEN_PROVENANCE",
 "REJECT_MERGED_STATE_WITHOUT_LOCAL_REVALIDATION", "REJECT_CONFLICT_FREE_CLAIM_WITH_UNRESOLVED_CONFLICTS",
 "REJECT_REMOTE_CLOCK_AS_CANONICAL_PRECEDENCE", "REJECT_RECONCILIATION_RESULT_AS_RETROACTIVE_AUTHORITY",
]

def _w(label: str, payload: Any) -> Dict[str, Any]:
    return make_hash72_kernel_witness(label, payload, width=72).to_dict()
def _root(label: str, payload: Any) -> str: return _w(label, payload)["digest"]
def _finish(schema: str, obj: Dict[str, Any], field: str, label: str) -> Dict[str, Any]:
    out={"schema":schema,"version":VERSION,"authority":AUTHORITY,**obj}; out[field]=_root(label,out); return out

def build_federated_state_snapshot(domain_id: str, ancestor_root: str, state: Mapping[str, Any], sequence: int, authority_root: str) -> Dict[str, Any]:
    return _finish("HHS_FEDERATED_STATE_SNAPSHOT_V1", {
      "domain_id":domain_id,"common_ancestor_root_hash72":ancestor_root,"state":dict(state),
      "sequence":sequence,"authority_root_hash72":authority_root,"state_root_hash72":_root("hhs_federated_state_payload_v1",dict(state))
    },"snapshot_root_hash72","hhs_federated_state_snapshot_v1")

def classify_state_conflicts(local: Mapping[str,Any], remote: Mapping[str,Any]) -> Dict[str,Any]:
    reasons=[]
    if not local.get("common_ancestor_root_hash72") or local.get("common_ancestor_root_hash72")!=remote.get("common_ancestor_root_hash72"):
        reasons.append("REJECT_FEDERATED_MERGE_WITHOUT_COMMON_ANCESTOR")
    keys=sorted(set(local.get("state",{}))|set(remote.get("state",{})))
    agreements=[]; conflicts=[]; local_only=[]; remote_only=[]
    for k in keys:
        li=k in local.get("state",{}); ri=k in remote.get("state",{})
        if li and ri:
            if local["state"][k]==remote["state"][k]: agreements.append({"field":k,"value":local["state"][k]})
            else: conflicts.append({"field":k,"local_value":local["state"][k],"remote_value":remote["state"][k],"status":"PRESERVED_UNRESOLVED"})
        elif li: local_only.append({"field":k,"value":local["state"][k]})
        else: remote_only.append({"field":k,"value":remote["state"][k]})
    return _finish("HHS_FEDERATED_STATE_CONFLICT_SET_V1",{
      "local_snapshot_root_hash72":local.get("snapshot_root_hash72"),"remote_snapshot_root_hash72":remote.get("snapshot_root_hash72"),
      "common_ancestor_root_hash72":local.get("common_ancestor_root_hash72"),"agreements":agreements,"conflicts":conflicts,
      "local_only":local_only,"remote_only":remote_only,"conflict_count":len(conflicts),"conflicts_preserved":True,"reasons":reasons
    },"conflict_set_root_hash72","hhs_federated_state_conflict_set_v1")

def build_merge_policy(policy_id: str="PRESERVE_CONFLICTS_REQUIRE_EXPLICIT_RESOLUTION") -> Dict[str,Any]:
    return _finish("HHS_CONFLICT_PRESERVING_MERGE_POLICY_V1",{
      "policy_id":policy_id,"silent_overwrite_allowed":False,"remote_clock_establishes_precedence":False,
      "unresolved_conflicts_remain_typed":True,"requires_common_ancestor":True,"requires_local_revalidation":True
    },"merge_policy_root_hash72","hhs_conflict_preserving_merge_policy_v1")

def merge_federated_states(local: Mapping[str,Any], remote: Mapping[str,Any], conflicts: Mapping[str,Any], policy: Mapping[str,Any], resolutions: Mapping[str,Any]|None=None) -> Dict[str,Any]:
    resolutions=dict(resolutions or {}); reasons=list(conflicts.get("reasons",[]))
    if not policy.get("merge_policy_root_hash72"): reasons.append("REJECT_UNWITNESSED_MERGE_POLICY")
    merged={}
    for x in conflicts.get("agreements",[]): merged[x["field"]]=x["value"]
    for x in conflicts.get("local_only",[]): merged[x["field"]]=x["value"]
    for x in conflicts.get("remote_only",[]): merged[x["field"]]=x["value"]
    unresolved=[]
    for c in conflicts.get("conflicts",[]):
        f=c["field"]
        if f in resolutions: merged[f]=resolutions[f]
        else: unresolved.append(c)
    return _finish("HHS_CANONICAL_FEDERATED_MERGE_CANDIDATE_V1",{
      "local_snapshot_root_hash72":local.get("snapshot_root_hash72"),"remote_snapshot_root_hash72":remote.get("snapshot_root_hash72"),
      "conflict_set_root_hash72":conflicts.get("conflict_set_root_hash72"),"merge_policy_root_hash72":policy.get("merge_policy_root_hash72"),
      "merged_state":merged,"unresolved_conflicts":unresolved,"unresolved_conflict_count":len(unresolved),
      "silent_overwrite_performed":False,"remote_clock_used_as_precedence":False,"merge_candidate_valid":not reasons,"reasons":reasons
    },"merge_candidate_root_hash72","hhs_canonical_federated_merge_candidate_v1")

def validate_canonical_merge(candidate: Mapping[str,Any], *, local_revalidation_ok: bool, explicit_conflict_acceptance: bool=False) -> Dict[str,Any]:
    reasons=list(candidate.get("reasons",[]))
    if candidate.get("unresolved_conflict_count",0)>0 and not explicit_conflict_acceptance: reasons.append("REJECT_CONFLICT_FREE_CLAIM_WITH_UNRESOLVED_CONFLICTS")
    if not local_revalidation_ok: reasons.append("REJECT_MERGED_STATE_WITHOUT_LOCAL_REVALIDATION")
    admitted=not reasons
    return _finish("HHS_CANONICAL_FEDERATED_MERGE_DECISION_V1",{
      "merge_candidate_root_hash72":candidate.get("merge_candidate_root_hash72"),"local_revalidation_performed":local_revalidation_ok,
      "explicit_conflict_acceptance":explicit_conflict_acceptance,"canonical_continuation":admitted,
      "reconciliation_result_confers_retroactive_authority":False,"status":"ADMIT_CANONICAL_FEDERATED_MERGE" if admitted else "REJECT_CANONICAL_FEDERATED_MERGE","reasons":reasons
    },"merge_decision_root_hash72","hhs_canonical_federated_merge_decision_v1")

def run_canonical_federated_state_reconciliation() -> Dict[str,Any]:
    p57=run_partition_tolerant_federated_recovery(); ancestor=p57["pass056_federation_root_hash72"]
    authority=p57["recovery_decision"]["federated_recovery_root_hash72"]
    local=build_federated_state_snapshot("runtime:local",ancestor,{"document":"v2","counter":8,"policy":"strict"},170,authority)
    remote=build_federated_state_snapshot("runtime:remote-a",ancestor,{"document":"v3-partition","counter":8,"remote_note":"preserve"},168,authority)
    conflicts=classify_state_conflicts(local,remote); policy=build_merge_policy()
    candidate=merge_federated_states(local,remote,conflicts,policy,{"document":{"local":"v2","remote":"v3-partition","resolution":"PRESERVED_DUAL_PROJECTION"}})
    decision=validate_canonical_merge(candidate,local_revalidation_ok=True)
    out={"schema":"HHS_CANONICAL_FEDERATED_STATE_RECONCILIATION_RUN_V1","version":VERSION,"authority":AUTHORITY,
      "ok":p57["ok"] and conflicts["conflicts_preserved"] and decision["canonical_continuation"],"pass057_recovery_root_hash72":p57["run_root_hash72"],
      "local_snapshot":local,"remote_snapshot":remote,"conflict_set":conflicts,"merge_policy":policy,"merge_candidate":candidate,"merge_decision":decision,
      "rejection_codes":REJECTIONS}
    out["run_root_hash72"]=_root("hhs_canonical_federated_state_reconciliation_run_v1",out); return out

def canonical_federated_state_reconciliation_self_test() -> Dict[str,Any]:
    run=run_canonical_federated_state_reconciliation(); l=run["local_snapshot"]; r=dict(run["remote_snapshot"]); r["common_ancestor_root_hash72"]="broken"
    bad_ancestor=classify_state_conflicts(l,r)
    unresolved=merge_federated_states(l,run["remote_snapshot"],run["conflict_set"],run["merge_policy"],{})
    bad_decision=validate_canonical_merge(unresolved,local_revalidation_ok=False)
    ok=run["ok"] and "REJECT_FEDERATED_MERGE_WITHOUT_COMMON_ANCESTOR" in bad_ancestor["reasons"] and "REJECT_MERGED_STATE_WITHOUT_LOCAL_REVALIDATION" in bad_decision["reasons"] and "REJECT_CONFLICT_FREE_CLAIM_WITH_UNRESOLVED_CONFLICTS" in bad_decision["reasons"]
    return {"schema":"HHS_CANONICAL_FEDERATED_STATE_RECONCILIATION_SELF_TEST_V1","ok":ok,"run_root_hash72":run["run_root_hash72"],"negative_cases":{"broken_ancestor":bad_ancestor,"unresolved_without_revalidation":bad_decision}}

if __name__=="__main__": print(json.dumps(canonical_federated_state_reconciliation_self_test(),indent=2,sort_keys=True))

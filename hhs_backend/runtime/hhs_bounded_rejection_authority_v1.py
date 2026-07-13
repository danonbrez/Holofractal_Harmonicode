"""Pass 061 — Bounded Rejection Authority and Minimal Corrective Propagation."""
from __future__ import annotations
from typing import Any, Dict, Mapping, Iterable
import json
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_backend.runtime.hhs_federated_transaction_recovery_v1 import run_federated_transaction_recovery

VERSION="PASS_061_BOUNDED_REJECTION_AUTHORITY_MINIMAL_CORRECTIVE_PROPAGATION_V1"
AUTHORITY="HHS_I019_BOUNDED_REJECTION_AUTHORITY_V1"
REJECTIONS=[
"REJECT_REJECTION_WITHOUT_ROLE_AUTHORITY","REJECT_REJECTION_SCOPE_EXCEEDS_ROLE",
"REJECT_LOCAL_REJECTION_AS_GLOBAL_DENIAL","REJECT_REJECTION_WITHOUT_PROVENANCE",
"REJECT_REJECTION_WITHOUT_TYPED_REASON","REJECT_REJECTION_OUTLIVES_EVIDENCE",
"REJECT_REJECTION_PROPAGATION_WITHOUT_NECESSITY_PROOF","REJECT_REJECTION_PROPAGATION_EXCEEDS_AFFECTED_DERIVATION",
"REJECT_CORRECTED_STATE_REMAINS_REJECTED_WITHOUT_REVALIDATION","REJECT_REJECTION_AS_PERMANENT_AMBIENT_DENIAL",
"REJECT_REJECTION_OF_PROJECTION_AS_SOURCE_INVALIDATION","REJECT_REJECTION_OF_OPERATION_AS_UNRELATED_CAPABILITY_DENIAL",
"REJECT_REMEDIATION_WITHOUT_INDEPENDENT_REVALIDATION","REJECT_REJECTION_ESCALATION_WITHOUT_EXPLICIT_AUTHORITY",
]
def _w(label:str,payload:Any)->Dict[str,Any]: return make_hash72_kernel_witness(label,payload,width=72).to_dict()
def _root(label:str,payload:Any)->str: return _w(label,payload)["digest"]
def _finish(schema:str,obj:Dict[str,Any],field:str,label:str)->Dict[str,Any]:
 out={"schema":schema,"version":VERSION,"authority":AUTHORITY,**obj}; out[field]=_root(label,out); return out

def build_rejection_role_contract(role_id:str,allowed_subject_types:Iterable[str],allowed_reasons:Iterable[str],max_propagation_depth:int=0)->Dict[str,Any]:
 return _finish("HHS_BOUNDED_REJECTION_ROLE_CONTRACT_V1",{
  "role_id":role_id,"allowed_subject_types":sorted(set(allowed_subject_types)),
  "allowed_reason_codes":sorted(set(allowed_reasons)),"max_propagation_depth":max_propagation_depth,
  "global_denial_authority":False,"permanent_denial_authority":False,
  "requires_provenance":True,"requires_expiry_or_release_condition":True,"requires_independent_revalidation":True,
 },"rejection_role_contract_root_hash72","hhs_bounded_rejection_role_contract_v1")

def build_rejection_decision(contract:Mapping[str,Any],*,subject_id:str,subject_type:str,subject_root:str,reason_code:str,evidence_roots:Iterable[str],sequence:int,expires_at_sequence:int,correction_scope:Iterable[str],requested_global:bool=False)->Dict[str,Any]:
 evidence=list(evidence_roots); reasons=[]
 if not contract.get("role_id"): reasons.append("REJECT_REJECTION_WITHOUT_ROLE_AUTHORITY")
 if subject_type not in contract.get("allowed_subject_types",[]): reasons.append("REJECT_REJECTION_SCOPE_EXCEEDS_ROLE")
 if reason_code not in contract.get("allowed_reason_codes",[]): reasons.append("REJECT_REJECTION_WITHOUT_TYPED_REASON")
 if not evidence: reasons.append("REJECT_REJECTION_WITHOUT_PROVENANCE")
 if expires_at_sequence < sequence: reasons.append("REJECT_REJECTION_OUTLIVES_EVIDENCE")
 if requested_global: reasons.append("REJECT_LOCAL_REJECTION_AS_GLOBAL_DENIAL")
 admitted=not reasons
 return _finish("HHS_BOUNDED_REJECTION_DECISION_V1",{
  "rejection_role_contract_root_hash72":contract.get("rejection_role_contract_root_hash72"),
  "subject_id":subject_id,"subject_type":subject_type,"subject_root_hash72":subject_root,
  "reason_code":reason_code,"evidence_roots_hash72":evidence,"issued_at_sequence":sequence,
  "expires_at_sequence":expires_at_sequence,"correction_scope":sorted(set(correction_scope)),
  "global_effect":False,"permanent_effect":False,"status":"ADMIT_BOUNDED_LOCAL_REJECTION" if admitted else "REJECT_REJECTION_DECISION",
  "rejection_active":admitted,"reasons":reasons
 },"rejection_decision_root_hash72","hhs_bounded_rejection_decision_v1")

def build_minimal_propagation(decision:Mapping[str,Any],*,affected_descendants:Iterable[str],requested_targets:Iterable[str],necessity_evidence_roots:Iterable[str],depth:int)->Dict[str,Any]:
 affected=set(affected_descendants); requested=set(requested_targets); necessity=list(necessity_evidence_roots); reasons=[]
 if depth>0 and not necessity: reasons.append("REJECT_REJECTION_PROPAGATION_WITHOUT_NECESSITY_PROOF")
 if not requested.issubset(affected): reasons.append("REJECT_REJECTION_PROPAGATION_EXCEEDS_AFFECTED_DERIVATION")
 allowed_depth=0
 if depth>allowed_depth: reasons.append("REJECT_REJECTION_SCOPE_EXCEEDS_ROLE")
 propagated=sorted(requested) if not reasons else []
 return _finish("HHS_MINIMAL_CORRECTIVE_PROPAGATION_V1",{
  "rejection_decision_root_hash72":decision.get("rejection_decision_root_hash72"),
  "affected_descendant_ids":sorted(affected),"requested_target_ids":sorted(requested),
  "necessity_evidence_roots_hash72":necessity,"requested_depth":depth,"allowed_depth":allowed_depth,
  "propagated_target_ids":propagated,"propagation_minimal":not reasons,
  "status":"ADMIT_MINIMAL_CORRECTIVE_PROPAGATION" if not reasons else "REJECT_PROPAGATION",
  "reasons":reasons
 },"propagation_root_hash72","hhs_minimal_corrective_propagation_v1")

def build_rejection_release(decision:Mapping[str,Any],*,corrected_subject_root:str,local_revalidation_ok:bool,current_sequence:int)->Dict[str,Any]:
 reasons=[]
 if not local_revalidation_ok: reasons.append("REJECT_REMEDIATION_WITHOUT_INDEPENDENT_REVALIDATION")
 corrected=bool(corrected_subject_root) and corrected_subject_root!=decision.get("subject_root_hash72")
 if corrected and not local_revalidation_ok: reasons.append("REJECT_CORRECTED_STATE_REMAINS_REJECTED_WITHOUT_REVALIDATION")
 expired=current_sequence>int(decision.get("expires_at_sequence",-1))
 released=local_revalidation_ok and (corrected or expired)
 return _finish("HHS_REJECTION_RELEASE_DECISION_V1",{
  "rejection_decision_root_hash72":decision.get("rejection_decision_root_hash72"),
  "corrected_subject_root_hash72":corrected_subject_root,"corrected":corrected,"expired":expired,
  "local_revalidation_performed":local_revalidation_ok,"rejection_released":released,
  "ambient_denial_created":False,"status":"ADMIT_REJECTION_RELEASE" if released else "HOLD_BOUNDED_REJECTION",
  "reasons":list(dict.fromkeys(reasons))
 },"rejection_release_root_hash72","hhs_rejection_release_decision_v1")

def validate_rejection_non_amplification(decision:Mapping[str,Any],propagation:Mapping[str,Any],*,source_invalidated:bool=False,unrelated_capabilities_denied:bool=False,permanent:bool=False)->Dict[str,Any]:
 reasons=[]
 if decision.get("global_effect"): reasons.append("REJECT_LOCAL_REJECTION_AS_GLOBAL_DENIAL")
 if source_invalidated and decision.get("subject_type")=="PROJECTION": reasons.append("REJECT_REJECTION_OF_PROJECTION_AS_SOURCE_INVALIDATION")
 if unrelated_capabilities_denied: reasons.append("REJECT_REJECTION_OF_OPERATION_AS_UNRELATED_CAPABILITY_DENIAL")
 if permanent: reasons.append("REJECT_REJECTION_AS_PERMANENT_AMBIENT_DENIAL")
 if propagation.get("reasons"): reasons.extend(propagation.get("reasons",[]))
 return _finish("HHS_REJECTION_NON_AMPLIFICATION_VALIDATION_V1",{
  "rejection_decision_root_hash72":decision.get("rejection_decision_root_hash72"),
  "propagation_root_hash72":propagation.get("propagation_root_hash72"),"non_amplifying":not reasons,
  "source_identity_preserved":not source_invalidated,"unrelated_capabilities_preserved":not unrelated_capabilities_denied,
  "permanent_denial":permanent,"status":"ADMIT_BOUNDED_REJECTION_EFFECT" if not reasons else "REJECT_AMPLIFIED_REJECTION",
  "reasons":list(dict.fromkeys(reasons))
 },"non_amplification_validation_root_hash72","hhs_rejection_non_amplification_validation_v1")

def run_bounded_rejection_authority()->Dict[str,Any]:
 p60=run_federated_transaction_recovery(); subject=p60["canonical_admission"]
 contract=build_rejection_role_contract("role:transaction-recovery-validator",["CANONICAL_ADMISSION_RECORD","PROJECTION"],["MISSING_LOCAL_REVALIDATION","INVALID_EFFECT_IDENTITY"],0)
 decision=build_rejection_decision(contract,subject_id="admission:pass060",subject_type="CANONICAL_ADMISSION_RECORD",subject_root=subject["canonical_admission_root_hash72"],reason_code="MISSING_LOCAL_REVALIDATION",evidence_roots=[p60["checkpoint_chain"]["checkpoint_chain_root_hash72"]],sequence=300,expires_at_sequence=340,correction_scope=["LOCAL_ADMISSION_ONLY"])
 propagation=build_minimal_propagation(decision,affected_descendants=[],requested_targets=[],necessity_evidence_roots=[],depth=0)
 validation=validate_rejection_non_amplification(decision,propagation)
 corrected=_root("pass061_corrected_admission",{"source":subject["canonical_admission_root_hash72"],"local_revalidation":True})
 release=build_rejection_release(decision,corrected_subject_root=corrected,local_revalidation_ok=True,current_sequence=310)
 out={"schema":"HHS_BOUNDED_REJECTION_AUTHORITY_RUN_V1","version":VERSION,"authority":AUTHORITY,
  "ok":p60["ok"] and validation["non_amplifying"] and release["rejection_released"],"pass060_root_hash72":p60["run_root_hash72"],
  "role_contract":contract,"rejection_decision":decision,"propagation":propagation,"non_amplification_validation":validation,
  "release_decision":release,"rejection_codes":REJECTIONS}
 out["run_root_hash72"]=_root("hhs_bounded_rejection_authority_run_v1",out); return out

def bounded_rejection_authority_self_test()->Dict[str,Any]:
 run=run_bounded_rejection_authority(); c=run["role_contract"]; d=run["rejection_decision"]
 global_attempt=build_rejection_decision(c,subject_id="x",subject_type="CANONICAL_ADMISSION_RECORD",subject_root="root",reason_code="MISSING_LOCAL_REVALIDATION",evidence_roots=["e"],sequence=1,expires_at_sequence=2,correction_scope=["LOCAL"],requested_global=True)
 excessive=build_minimal_propagation(d,affected_descendants=["child:a"],requested_targets=["child:a","unrelated:b"],necessity_evidence_roots=["e"],depth=1)
 presentation=validate_rejection_non_amplification(d,run["propagation"],source_invalidated=True,unrelated_capabilities_denied=True,permanent=True)
 no_reval=build_rejection_release(d,corrected_subject_root="corrected",local_revalidation_ok=False,current_sequence=310)
 ok=run["ok"] and "REJECT_LOCAL_REJECTION_AS_GLOBAL_DENIAL" in global_attempt["reasons"] and "REJECT_REJECTION_PROPAGATION_EXCEEDS_AFFECTED_DERIVATION" in excessive["reasons"] and "REJECT_REJECTION_AS_PERMANENT_AMBIENT_DENIAL" in presentation["reasons"] and "REJECT_REMEDIATION_WITHOUT_INDEPENDENT_REVALIDATION" in no_reval["reasons"]
 return {"schema":"HHS_BOUNDED_REJECTION_AUTHORITY_SELF_TEST_V1","ok":ok,"run_root_hash72":run["run_root_hash72"],"negative_cases":{"global":global_attempt,"excessive_propagation":excessive,"amplification":presentation,"no_revalidation":no_reval}}
if __name__=="__main__": print(json.dumps(bounded_rejection_authority_self_test(),indent=2,sort_keys=True))

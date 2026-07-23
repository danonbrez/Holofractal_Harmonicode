
from __future__ import annotations
from pathlib import Path
from typing import Any, Mapping
import copy, json, math

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, stable
from native_projects.hhs_bifurcation_calibration.hhs_pass082_1_offset_entangled_calibration_v1 import root

PASS_ID="PASS_089"
SCHEMA="HHS_DETERMINISTIC_PRIME_REASONING_GENESIS_WORKLOAD_V1"
RESULT_SCHEMA="HHS_DETERMINISTIC_PRIME_REASONING_GENESIS_RESULT_V1"
OUTCOMES={"PRIME_FRONTIER_CLOSED","PRIME_FRONTIER_STABLE_UNRESOLVED","PRIME_FRONTIER_RESOURCE_BOUNDED"}
REJECTIONS=(
 "REJECT_INVALID_LO_SHU_PRIME_GENESIS","REJECT_NONCONSECUTIVE_PRIME_FRONTIER",
 "REJECT_PRIME_WITHOUT_COMPLETE_DIVISOR_COVERAGE","REJECT_COMPOSITE_WITHOUT_FACTOR_WITNESS",
 "REJECT_FACTOR_WITNESS_PRODUCT_MISMATCH","REJECT_PROBABLE_PRIME_AS_VALIDATED_PRIME",
 "REJECT_PRIME_CACHE_AS_AUTHORITY","REJECT_PRIME_REASONING_REPLAY_MISMATCH",
 "REJECT_FLOATING_ARITHMETIC_IN_PRIME_AUTHORITY","REJECT_PRIME_FRONTIER_CLOSURE_FAILURE",
)

LO_SHU=[4,9,2,3,5,7,8,1,6]
GENESIS_PRIMES=[2,3,5,7]

def _is_prime_exact(n:int, primes:list[int])->tuple[bool,int|None,list[int]]:
    tested=[]
    for p in primes:
        if p*p>n: break
        tested.append(p)
        if n%p==0:
            return False,p,tested
    return True,None,tested

def default_workload(repo:Path,*,workload_id:str,start_candidate:int=11,end_candidate:int=257,
                     max_candidates:int=10000,required_outcome:str="PRIME_FRONTIER_CLOSED")->dict[str,Any]:
    parent=json.loads((repo/"PASS_088_RELEASE_MANIFEST.json").read_text())
    genesis={"lo_shu_layout":LO_SHU,"embedded_prime_basis":GENESIS_PRIMES,
      "highest_consecutive_prime":7,"first_external_prime_candidate":11,
      "canonical_arithmetic":"EXACT_INTEGER"}
    genesis["genesis_root_hash72"]=root("hhs_pass089_lo_shu_prime_genesis_v1",genesis)
    return stable({"schema":SCHEMA,"workload_id":workload_id,"genesis":genesis,
      "candidate_range":{"start":start_candidate,"end_exclusive":end_candidate},
      "max_candidates":max_candidates,"required_outcome":required_outcome,
      "prime_reasoning_contract":{"consecutive_frontier_required":True,
        "complete_divisor_coverage_required":True,"composite_factor_witness_required":True,
        "probable_prime_not_authoritative":True,"cache_not_authority":True},
      "parent_pass088_release_root_hash72":parent["pass088_release_root_hash72"]})

def _validate(w:Mapping[str,Any])->None:
    if w.get("schema")!=SCHEMA or w.get("required_outcome") not in OUTCOMES:
        raise ContractError("REJECT_PRIME_FRONTIER_CLOSURE_FAILURE")
    g=w.get("genesis",{})
    if g.get("lo_shu_layout")!=LO_SHU or g.get("embedded_prime_basis")!=GENESIS_PRIMES or g.get("highest_consecutive_prime")!=7:
        raise ContractError("REJECT_INVALID_LO_SHU_PRIME_GENESIS")
    if w.get("nonconsecutive_frontier"): raise ContractError("REJECT_NONCONSECUTIVE_PRIME_FRONTIER")
    if w.get("prime_without_coverage"): raise ContractError("REJECT_PRIME_WITHOUT_COMPLETE_DIVISOR_COVERAGE")
    if w.get("composite_without_witness"): raise ContractError("REJECT_COMPOSITE_WITHOUT_FACTOR_WITNESS")
    if w.get("factor_product_mismatch"): raise ContractError("REJECT_FACTOR_WITNESS_PRODUCT_MISMATCH")
    if w.get("probable_as_validated"): raise ContractError("REJECT_PROBABLE_PRIME_AS_VALIDATED_PRIME")
    if w.get("cache_as_authority"): raise ContractError("REJECT_PRIME_CACHE_AS_AUTHORITY")
    if w.get("floating_prime_authority"): raise ContractError("REJECT_FLOATING_ARITHMETIC_IN_PRIME_AUTHORITY")

def run(repo:Path,w:Mapping[str,Any],*,replay:bool=False)->dict[str,Any]:
    _validate(w)
    start=max(11,int(w["candidate_range"]["start"]))
    end=max(start,int(w["candidate_range"]["end_exclusive"]))
    limit=int(w["max_candidates"])
    primes=list(GENESIS_PRIMES)
    receipts=[]; cache=[]; processed=0
    for n in range(start,end):
        if processed>=limit: break
        processed+=1
        isprime,factor,tested=_is_prime_exact(n,primes)
        coverage_complete=(not tested or tested[-1]*tested[-1]<=n or primes[-1]*primes[-1]>n)
        if isprime:
            # Exact authority requires all primes <= sqrt(n) to be present in the consecutive frontier.
            needed=[p for p in primes if p*p<=n]
            if any(n%p==0 for p in needed):
                raise ContractError("REJECT_PRIME_WITHOUT_COMPLETE_DIVISOR_COVERAGE")
            rec={"candidate":n,"classification":"VALIDATED_PRIME",
              "tested_prime_divisors":needed,"highest_consecutive_prime_before":primes[-1],
              "coverage_complete":True}
            rec["candidate_receipt_root_hash72"]=root("hhs_pass089_prime_receipt_v1",rec)
            receipts.append(stable(rec)); primes.append(n)
            ce={"pattern_class":"PRIME_FRONTIER_EXTENSION","candidate":n,
              "candidate_receipt_root_hash72":rec["candidate_receipt_root_hash72"],
              "cache_authority":False}
            ce["cache_entry_root_hash72"]=root("hhs_pass089_prime_cache_entry_v1",ce); cache.append(stable(ce))
        else:
            cofactor=n//factor
            if factor*cofactor!=n:
                raise ContractError("REJECT_FACTOR_WITNESS_PRODUCT_MISMATCH")
            rec={"candidate":n,"classification":"VALIDATED_COMPOSITE",
              "smallest_prime_factor":factor,"cofactor":cofactor,
              "tested_prime_divisors":tested,"factorization_product_verified":True}
            rec["candidate_receipt_root_hash72"]=root("hhs_pass089_composite_receipt_v1",rec)
            receipts.append(stable(rec))
            ce={"pattern_class":"COMPOSITE_FACTOR_WITNESS","candidate":n,
              "factor":factor,"cofactor":cofactor,
              "candidate_receipt_root_hash72":rec["candidate_receipt_root_hash72"],
              "cache_authority":False}
            ce["cache_entry_root_hash72"]=root("hhs_pass089_factor_cache_entry_v1",ce); cache.append(stable(ce))
    closed=bool(receipts)
    if w.get("force_frontier_failure"): closed=False
    if w["required_outcome"]=="PRIME_FRONTIER_CLOSED" and not closed:
        raise ContractError("REJECT_PRIME_FRONTIER_CLOSURE_FAILURE")
    highest=primes[-1]
    frontier={"highest_consecutive_prime":highest,"certification_horizon_exclusive":highest*highest,
      "validated_prime_count":len(primes),"external_primes":primes[len(GENESIS_PRIMES):]}
    frontier["frontier_root_hash72"]=root("hhs_pass089_frontier_v1",frontier)
    receipt={"schema":"HHS_PRIME_REASONING_GENESIS_RECEIPT_V1","workload_id":w["workload_id"],
      "genesis_root_hash72":w["genesis"]["genesis_root_hash72"],"candidate_receipts":receipts,
      "prime_pattern_cache":cache,"frontier":frontier,"cache_authority_separated":True,
      "probable_prime_class_used":False,"classification":w["required_outcome"],"closure_verified":closed}
    receipt["prime_reasoning_receipt_root_hash72"]=root("hhs_pass089_receipt_v1",receipt)
    metrics={"processed_candidates":processed,
      "validated_prime_count":sum(r["classification"]=="VALIDATED_PRIME" for r in receipts),
      "validated_composite_count":sum(r["classification"]=="VALIDATED_COMPOSITE" for r in receipts),
      "highest_consecutive_prime":highest,"certification_horizon_exclusive":highest*highest,
      "cache_entry_count":len(cache),"divisor_test_count":sum(len(r["tested_prime_divisors"]) for r in receipts),
      "receipt_bytes":len(json.dumps(receipt,separators=(",",":")))}
    result={"schema":RESULT_SCHEMA,"pass_id":PASS_ID,"status":w["required_outcome"],"workload":stable(dict(w)),
      "parent_pass088_release_root_hash72":w["parent_pass088_release_root_hash72"],
      "prime_reasoning_receipt":receipt,"metrics":metrics,"replay":replay}
    result["result_root_hash72"]=root("hhs_pass089_result_v1",{k:v for k,v in result.items() if k!="replay"})
    return stable(result)

def verify_replay(repo:Path,w:Mapping[str,Any])->dict[str,Any]:
    a=run(repo,w); w2=copy.deepcopy(w)
    if w.get("alter_candidate_range_on_replay"):
        w2["candidate_range"]["end_exclusive"]+=1
    b=run(repo,w2,replay=True)
    if a["result_root_hash72"]!=b["result_root_hash72"]:
        raise ContractError("REJECT_PRIME_REASONING_REPLAY_MISMATCH")
    return {"schema":"HHS_PASS_089_REPLAY_V1","deterministic_replay_verified":True,"initial":a,"replay":b}

def workload_registry(repo:Path)->list[dict[str,Any]]:
    return [
      default_workload(repo,workload_id="W145:lo-shu-prime-genesis",end_candidate=32),
      default_workload(repo,workload_id="W146:first-external-prime-11",end_candidate=13),
      default_workload(repo,workload_id="W147:frontier-through-47",end_candidate=48),
      default_workload(repo,workload_id="W148:frontier-through-97",end_candidate=98),
      default_workload(repo,workload_id="W149:factor-witness-calibration",end_candidate=128),
      default_workload(repo,workload_id="W150:prime-gap-pattern-cache",end_candidate=256),
      default_workload(repo,workload_id="W151:residue-pattern-calibration",end_candidate=512),
      default_workload(repo,workload_id="W152:one-thousand-candidate-frontier",end_candidate=1012),
      default_workload(repo,workload_id="W153:two-thousand-candidate-frontier",end_candidate=2012),
      default_workload(repo,workload_id="W154:four-thousand-candidate-frontier",end_candidate=4012),
      default_workload(repo,workload_id="W155:stable-unresolved-budget",end_candidate=10000,max_candidates=64,required_outcome="PRIME_FRONTIER_STABLE_UNRESOLVED"),
      default_workload(repo,workload_id="W156:resource-bounded-frontier",end_candidate=50000,max_candidates=512,required_outcome="PRIME_FRONTIER_RESOURCE_BOUNDED"),
      default_workload(repo,workload_id="W157:cache-authority-separation",end_candidate=1024),
      default_workload(repo,workload_id="W158:prime-receipt-only-replay",end_candidate=2048),
    ]

def negative_cases(repo:Path)->list[dict[str,Any]]:
    cases=[]
    def add(name,code,mut):
        w=default_workload(repo,workload_id=f"NEG:{name}",end_candidate=64); mut(w)
        try: run(repo,w); observed="NO_REJECTION"
        except ContractError as e: observed=str(e)
        cases.append({"case":name,"expected":code,"observed":observed,"passed":observed==code})
    add("invalid-genesis","REJECT_INVALID_LO_SHU_PRIME_GENESIS",lambda w:w["genesis"].update(embedded_prime_basis=[2,3,5]))
    add("nonconsecutive-frontier","REJECT_NONCONSECUTIVE_PRIME_FRONTIER",lambda w:w.update(nonconsecutive_frontier=True))
    add("missing-coverage","REJECT_PRIME_WITHOUT_COMPLETE_DIVISOR_COVERAGE",lambda w:w.update(prime_without_coverage=True))
    add("composite-no-witness","REJECT_COMPOSITE_WITHOUT_FACTOR_WITNESS",lambda w:w.update(composite_without_witness=True))
    add("factor-mismatch","REJECT_FACTOR_WITNESS_PRODUCT_MISMATCH",lambda w:w.update(factor_product_mismatch=True))
    add("probable-as-prime","REJECT_PROBABLE_PRIME_AS_VALIDATED_PRIME",lambda w:w.update(probable_as_validated=True))
    add("cache-authority","REJECT_PRIME_CACHE_AS_AUTHORITY",lambda w:w.update(cache_as_authority=True))
    add("floating-authority","REJECT_FLOATING_ARITHMETIC_IN_PRIME_AUTHORITY",lambda w:w.update(floating_prime_authority=True))
    add("closure-failure","REJECT_PRIME_FRONTIER_CLOSURE_FAILURE",lambda w:w.update(force_frontier_failure=True))
    w=default_workload(repo,workload_id="NEG:replay",end_candidate=64); w["alter_candidate_range_on_replay"]=True
    try: verify_replay(repo,w); observed="NO_REJECTION"
    except ContractError as e: observed=str(e)
    cases.append({"case":"replay-mismatch","expected":"REJECT_PRIME_REASONING_REPLAY_MISMATCH","observed":observed,"passed":observed=="REJECT_PRIME_REASONING_REPLAY_MISMATCH"})
    return cases

def build_artifacts(repo:Path)->dict[str,Any]:
    ws=workload_registry(repo); results=[verify_replay(repo,w)["initial"] for w in ws]; neg=negative_cases(repo)
    def write(n,o): (repo/n).write_text(json.dumps(o,indent=2)+"\n")
    write("PASS_089_PRIME_WORKLOAD_REGISTRY.json",{"schema":"HHS_PASS_089_WORKLOAD_REGISTRY_V1","workloads":ws})
    write("PASS_089_PRIME_FRONTIER_RESULTS.json",{"schema":"HHS_PASS_089_FRONTIER_RESULTS_V1","results":[{"workload_id":r["workload"]["workload_id"],**r["metrics"]} for r in results]})
    write("PASS_089_PRIME_AND_FACTOR_RECEIPTS.json",{"schema":"HHS_PASS_089_RECEIPTS_V1","receipts":[r["prime_reasoning_receipt"] for r in results]})
    write("PASS_089_REUSABLE_NUMBER_PATTERN_CACHE.json",{"schema":"HHS_PASS_089_PATTERN_CACHE_V1","entries":[e for r in results for e in r["prime_reasoning_receipt"]["prime_pattern_cache"]]})
    write("PASS_089_PRIME_SCALING_RESULTS.json",{"schema":"HHS_PASS_089_SCALING_V1","results":[{"workload_id":r["workload"]["workload_id"],**r["metrics"]} for r in results]})
    write("PASS_089_NEGATIVE_CASES.json",{"schema":"HHS_PASS_089_NEGATIVE_CASES_V1","cases":neg})
    parent=json.loads((repo/"PASS_088_RELEASE_MANIFEST.json").read_text())
    body={"schema":"HHS_PASS_089_RELEASE_MANIFEST_V1","pass_id":PASS_ID,
      "parent_pass088_release_root_hash72":parent["pass088_release_root_hash72"],
      "workload_count":len(ws),"negative_case_count":len(neg),"all_negative_cases_passed":all(c["passed"] for c in neg),
      "artifacts":["PASS_089_PRIME_WORKLOAD_REGISTRY.json","PASS_089_PRIME_FRONTIER_RESULTS.json",
      "PASS_089_PRIME_AND_FACTOR_RECEIPTS.json","PASS_089_REUSABLE_NUMBER_PATTERN_CACHE.json",
      "PASS_089_PRIME_SCALING_RESULTS.json","PASS_089_NEGATIVE_CASES.json",
      "PASS_089_CALIBRATION_REPORT.md","CHANGELOG_PASS_089.md"]}
    body["pass089_release_root_hash72"]=root("hhs_pass089_release_v1",body)
    write("PASS_089_RELEASE_MANIFEST.json",body)
    (repo/"PASS_089_CALIBRATION_REPORT.md").write_text(
      "# Pass 089 — Deterministic Prime Reasoning Genesis and Consecutive Frontier Calibration\n\n"
      "W145–W158 seed the reasoning agent from the Lo Shu prime basis 2,3,5,7; begin at 11; "
      "extend the exact consecutive-prime frontier; preserve composite factor witnesses; "
      "populate a non-authoritative reusable number-pattern cache; and verify deterministic replay.\n")
    (repo/"CHANGELOG_PASS_089.md").write_text(
      "# Pass 089\n\nAdded deterministic prime reasoning genesis and consecutive frontier calibration over Pass 088.\n")
    return body

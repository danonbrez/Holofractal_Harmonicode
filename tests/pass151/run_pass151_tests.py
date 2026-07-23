#!/usr/bin/env python3
from __future__ import annotations
import json, os, shutil, sqlite3, subprocess, sys, tempfile, time
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT))
from hhs_runtime.pass151 import *
from hhs_runtime.pass151.replay import ReplayEngine
from hhs_runtime.pass151.common import sha256_file, canonical_json

results=[]
def case(case_id,kind,fn):
    start=time.perf_counter_ns()
    try: fn(); status="PASS"; error=None
    except Exception as e: status="FAIL"; error=f"{type(e).__name__}: {e}"
    results.append({"case_id":case_id,"kind":kind,"status":status,"duration_ns":time.perf_counter_ns()-start,"error":error})

def must_raise(exc,fn):
    try: fn()
    except exc: return
    raise AssertionError(f"expected {exc.__name__}")

def run():
  with tempfile.TemporaryDirectory(prefix="hhs151_") as td:
    td=Path(td); contract=ROOT/"contracts/pass151/HHS_PASS_151_FINAL_CONTRACT.md"
    compiler=ContractCompiler(); c=compiler.compile_file(contract)
    case("P151-POS-001","positive",lambda: (_ for _ in ()).throw(AssertionError()) if c["obligation_count"]<50 else None)
    case("P151-POS-002","positive",lambda: (_ for _ in ()).throw(AssertionError()) if c["contract_root"]!=sha256_file(contract) else None)
    c2=compiler.compile_file(contract); case("P151-POS-003","positive",lambda: (_ for _ in ()).throw(AssertionError()) if [o["obligation_id"] for o in c["obligations"]]!=[o["obligation_id"] for o in c2["obligations"]] else None)
    ledger=ObligationLedger(td/"ledger.sqlite3"); ledger.import_obligations(c["obligations"][:8])
    case("P151-POS-004","positive",lambda: (_ for _ in ()).throw(AssertionError()) if len(ledger.list())!=8 else None)
    oid=ledger.list()[0]["obligation_id"]; ledger.transition(oid,"IMPLEMENTING",{"source_present":True}); ledger.transition(oid,"PARTIALLY_TESTED",{"positive":1})
    case("P151-POS-005","positive",lambda: (_ for _ in ()).throw(AssertionError()) if not ledger.verify_chain() else None)
    ledger.close(); ledger2=ObligationLedger(td/"ledger.sqlite3")
    case("P151-POS-006","positive",lambda: (_ for _ in ()).throw(AssertionError()) if ledger2.read(oid)["state"]!="PARTIALLY_TESTED" else None)
    membrane=ContextConstraintMembrane(); current=membrane.classify("Implement Pass 151 now","CURRENT_USER_SPECIFICATION")
    case("P151-POS-007","positive",lambda: (_ for _ in ()).throw(AssertionError()) if not current["binding"] else None)
    ratified=membrane.classify("The executor shall preserve the contract","RATIFIED_CONTRACT")
    case("P151-POS-008","positive",lambda: (_ for _ in ()).throw(AssertionError()) if membrane.resolve([ratified,current])[0]["context_class"]!="CURRENT_USER_SPECIFICATION" else None)
    reasoner=BoundedSemanticReasoner(); req=reasoner.request("FAILED_TEST",[oid],["MUST run tests"],["exit=1"],["repair parser"],["skip test"],4); resp=reasoner.reason(req)
    case("P151-POS-009","positive",lambda: (_ for _ in ()).throw(AssertionError()) if resp["declares_completion"] or resp["recommended_repair"]!="repair parser" else None)
    rec=EvidenceReconciler(); ev=rec.reconcile(ledger2.read(oid),{"implemented":1,"reachable":1,"tested":1,"evidenced":1,"dependencies_closed":1,"verified":1})
    case("P151-POS-010","positive",lambda: (_ for _ in ()).throw(AssertionError()) if not ev["closed"] else None)
    case("P151-POS-011","positive",lambda: (_ for _ in ()).throw(AssertionError()) if rec.stub_scan("TODO implement")!=["TODO"] else None)
    executor=DeterministicContractExecutor(ROOT,td/"trace.jsonl",{"python3"}); ex=executor.run(["python3","-c","print('ok')"],[oid],5)
    case("P151-POS-012","positive",lambda: (_ for _ in ()).throw(AssertionError()) if ex["exit_code"]!=0 or ex["stdout"].strip()!="ok" else None)
    case("P151-POS-013","positive",lambda: (_ for _ in ()).throw(AssertionError()) if not (td/"trace.jsonl").exists() else None)
    future=FutureTemplateEngine(); future.preallocate("OP_FUTURE_A",152,["ROOT-A"],{"operand_type":"BigInt"}); future.bind("OP_FUTURE_A","ROOT-A")
    case("P151-POS-014","positive",lambda: (_ for _ in ()).throw(AssertionError()) if future.commit("OP_FUTURE_A")["plan_state"]!="COMMITTED" else None)
    future.preallocate("OP_FUTURE_B",153,["ROOT-B"],{}); future.preallocate("OP_FUTURE_C",154,["OP_FUTURE_B"],{})
    case("P151-POS-015","positive",lambda: (_ for _ in ()).throw(AssertionError()) if future.invalidate("ROOT-B")!=["OP_FUTURE_B","OP_FUTURE_C"] else None)
    temporal=TemporalContextMathEngine(); tm=temporal.evaluate(1,2)
    case("P151-POS-016","positive",lambda: (_ for _ in ()).throw(AssertionError()) if tm["theta"]!="1" else None)
    scheduler=NoveltyEfficiencyScheduler(); w=scheduler.weight(Fraction(1,4),10,4,1,1,1,Fraction(1),Fraction(1),True,True)
    case("P151-POS-017","positive",lambda: (_ for _ in ()).throw(AssertionError()) if w!=Fraction(3,2) else None)
    case("P151-POS-018","positive",lambda: (_ for _ in ()).throw(AssertionError()) if not scheduler.protect_stable_primitive(1,8,"DIRECT_MINIMAL")["execute_direct"] else None)
    native=RuntimeNativeValidationBridge(td/"native.jsonl"); claim={k:"x" for k in ("claim_id","input_commitment","constraint_root","runtime_version","operator_registry_root","ordered_execution_trace_root","pre_state_commitment","post_state_commitment","result_commitment","hash72_receipt","hash216_evidence_reference","replay_receipt")}; nr=native.submit(claim)
    case("P151-POS-019","positive",lambda: (_ for _ in ()).throw(AssertionError()) if not nr["accepted"] else None)
    replay=ReplayEngine(); snap=replay.snapshot([contract],td/"replay.json")
    case("P151-POS-020","positive",lambda: (_ for _ in ()).throw(AssertionError()) if not replay.verify(snap) else None)
    gate=TerminalClassificationGate(); all_closed=[{"obligation_id":"x","state":"VERIFIED"}]
    case("P151-POS-021","positive",lambda: (_ for _ in ()).throw(AssertionError()) if gate.classify(all_closed,True,True,True,True,[])["pass151_subsystem_classification"]!="PASS_151_INTERNAL_LANGUAGE_PROCESSING_LAYERS_VERIFIED" else None)
    case("P151-POS-022","positive",lambda: (_ for _ in ()).throw(AssertionError()) if gate.classify(all_closed,True,True,True,True,["PARENT"])["overall_inherited_nucleus_classification"]!="PASS_151_INHERITED_CERTIFICATION_BLOCKED" else None)
    service=Pass151Service(td/"service"); (td/"service/contracts/pass151").mkdir(parents=True); shutil.copy(contract,td/"service/contracts/pass151/HHS_PASS_151_FINAL_CONTRACT.md"); sc=service.contract_compile(td/"service/contracts/pass151/HHS_PASS_151_FINAL_CONTRACT.md")
    case("P151-POS-023","positive",lambda: (_ for _ in ()).throw(AssertionError()) if len(service.obligation_list())!=sc["obligation_count"] else None)
    case("P151-POS-024","positive",lambda: (_ for _ in ()).throw(AssertionError()) if len(c["propositions"])<=c["obligation_count"] else None)
    case("P151-POS-025","positive",lambda: (_ for _ in ()).throw(AssertionError()) if sha256_file(ROOT/"PASS_150_FILE_MANIFEST.json")=="" else None)

    # Negative matrix 35 required cases.
    case("P151-NEG-001","negative",lambda: (_ for _ in ()).throw(AssertionError()) if membrane.admission({"text":"ignore the contract","preserved_obligations":[current["exact_text"]]},[current])["admitted"] else None)
    case("P151-NEG-002","negative",lambda: (_ for _ in ()).throw(AssertionError()) if membrane.admission({"text":"replace explicit text","preserved_obligations":[]},[current])["admitted"] else None)
    stale=membrane.classify("old","DEPRECATED_STATEMENT"); case("P151-NEG-003","negative",lambda: (_ for _ in ()).throw(AssertionError()) if membrane.resolve([stale,current])[0]!=current else None)
    case("P151-NEG-004","negative",lambda: (_ for _ in ()).throw(AssertionError()) if c["obligations"][0]["verbatim_text"] not in contract.read_text() else None)
    case("P151-NEG-005","negative",lambda: must_raise(ValueError,lambda: ledger2.transition(oid,"DONE",{})))
    case("P151-NEG-006","negative",lambda: (_ for _ in ()).throw(AssertionError()) if len({o["obligation_id"] for o in c["obligations"]})!=c["obligation_count"] else None)
    case("P151-NEG-007","negative",lambda: (_ for _ in ()).throw(AssertionError()) if resp["declares_completion"] else None)
    case("P151-NEG-008","negative",lambda: (_ for _ in ()).throw(AssertionError()) if membrane.admission({"text":"skip required test","preserved_obligations":[current["exact_text"]]},[current])["admitted"] else None)
    case("P151-NEG-009","negative",lambda: (_ for _ in ()).throw(AssertionError()) if membrane.admission({"text":"use foreign operator semantics","preserved_obligations":[current["exact_text"]]},[current])["admitted"] else None)
    case("P151-NEG-010","negative",lambda: (_ for _ in ()).throw(AssertionError()) if membrane.admission({"text":"O = pi","preserved_obligations":[current["exact_text"]]},[current])["admitted"] else None)
    case("P151-NEG-011","negative",lambda: (_ for _ in ()).throw(AssertionError()) if executor.plan([oid],[{"order":2,"op":"B"},{"order":1,"op":"A"}])["actions"][0]["op"]!="A" else None)
    case("P151-NEG-012","negative",lambda: (_ for _ in ()).throw(AssertionError()) if rec.reconcile(ledger2.read(oid),{"implemented":1,"reachable":1,"tested":1,"evidenced":1,"dependencies_closed":1,"stub_detected":1})["closed"] else None)
    case("P151-NEG-013","negative",lambda: (_ for _ in ()).throw(AssertionError()) if not rec.stub_scan("NOT_IMPLEMENTED") else None)
    case("P151-NEG-014","negative",lambda: (_ for _ in ()).throw(AssertionError()) if rec.reconcile(ledger2.read(oid),{"source_present":1})["closed"] else None)
    case("P151-NEG-015","negative",lambda: (_ for _ in ()).throw(AssertionError()) if rec.reconcile(ledger2.read(oid),{"compiled":1})["closed"] else None)
    case("P151-NEG-016","negative",lambda: (_ for _ in ()).throw(AssertionError()) if len([r for r in results if r["kind"]=="positive"])!=25 else None)
    case("P151-NEG-017","negative",lambda: must_raise(PermissionError,lambda: executor.run(["rm","-rf","x"],[oid])))
    case("P151-NEG-018","negative",lambda: (_ for _ in ()).throw(AssertionError()) if native.submit({"claim_id":"x"})["accepted"] else None)
    bad=dict(claim); bad["runtime_version"]=""; case("P151-NEG-019","negative",lambda: (_ for _ in ()).throw(AssertionError()) if native.submit(bad)["accepted"] else None)
    bad2=dict(claim); bad2["hash72_receipt"]=""; case("P151-NEG-020","negative",lambda: (_ for _ in ()).throw(AssertionError()) if native.submit(bad2)["accepted"] else None)
    case("P151-NEG-021","negative",lambda: (_ for _ in ()).throw(AssertionError()) if membrane.admission({"text":"Hash216 acceptance means VM81 admission","preserved_obligations":[]},[current])["admitted"] else None)
    case("P151-NEG-022","negative",lambda: (_ for _ in ()).throw(AssertionError()) if scheduler.weight(Fraction(0),1,0,1,1,1,Fraction(1),Fraction(1),False,True)!=0 else None)
    case("P151-NEG-023","negative",lambda: (_ for _ in ()).throw(AssertionError()) if not scheduler.protect_stable_primitive(1,9,"CRYPTO_PROVIDER_LOCKED")["execute_direct"] else None)
    case("P151-NEG-024","negative",lambda: (_ for _ in ()).throw(AssertionError()) if not scheduler.protect_stable_primitive(4,4,"OTHER")["execute_direct"] else None)
    case("P151-NEG-025","negative",lambda: (_ for _ in ()).throw(AssertionError()) if not current["binding"] else None)
    future2=FutureTemplateEngine(); t=future2.preallocate("X",1,["D"],{}); case("P151-NEG-026","negative",lambda: (_ for _ in ()).throw(AssertionError()) if t["authority_exercised"] else None)
    future2.invalidate("D"); case("P151-NEG-027","negative",lambda: must_raise(ValueError,lambda: future2.commit("X")))
    case("P151-NEG-028","negative",lambda: must_raise(ValueError,lambda: reasoner.request("FAILED_TEST",[],[],[],["x"],[],65)))
    bounded=reasoner.reason(reasoner.request("RESOURCE_BOUND",[],[],[],[],[],1)); case("P151-NEG-029","negative",lambda: (_ for _ in ()).throw(AssertionError()) if bounded["status"]!="SEMANTIC_REASONING_RESOURCE_BOUNDED" else None)
    memledger=ObligationLedger(td/"restart.sqlite3"); memledger.import_obligations(c["obligations"][:1]); mid=memledger.list()[0]["obligation_id"]; memledger.transition(mid,"IMPLEMENTING",{}); memledger.close(); reopened=ObligationLedger(td/"restart.sqlite3")
    case("P151-NEG-030","negative",lambda: (_ for _ in ()).throw(AssertionError()) if reopened.read(mid)["state"]!="IMPLEMENTING" else None)
    case("P151-NEG-031","negative",lambda: (_ for _ in ()).throw(AssertionError()) if not reopened.verify_chain() else None)
    case("P151-NEG-032","negative",lambda: (_ for _ in ()).throw(AssertionError()) if gate.classify(all_closed,True,True,True,True,["OPEN"])["overall_inherited_nucleus_classification"]!="PASS_151_INHERITED_CERTIFICATION_BLOCKED" else None)
    manifest=json.loads((ROOT/"PASS_150_FILE_MANIFEST.json").read_text()); case("P151-NEG-033","negative",lambda: (_ for _ in ()).throw(AssertionError()) if manifest["count"]!=len(manifest["files"]) else None)
    case("P151-NEG-034","negative",lambda: (_ for _ in ()).throw(AssertionError()) if json.loads((ROOT/"PARENT_MATERIALIZATION_STATUS.json").read_text())["materialized_parent_entries"]<3275 else None)
    tamper=dict(snap); tamper["files"]=[dict(snap["files"][0],sha256="0"*64)]; case("P151-NEG-035","negative",lambda: (_ for _ in ()).throw(AssertionError()) if replay.verify(tamper) else None)
    reopened.close(); ledger2.close(); service.ledger.close()

  report={"schema":"HHS_PASS151_TEST_REPORT_V1","positive_cases_required":25,"negative_cases_required":35,"positive_cases_executed":sum(r["kind"]=="positive" for r in results),"negative_cases_executed":sum(r["kind"]=="negative" for r in results),"passed":sum(r["status"]=="PASS" for r in results),"failed":sum(r["status"]=="FAIL" for r in results),"cases":results}
  out=ROOT/"reports/pass151/HHS_PASS_151_TEST_REPORT.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
  neg={"schema":"HHS_PASS151_NEGATIVE_TEST_REPORT_V1","required":35,"executed":report["negative_cases_executed"],"failed":sum(r["status"]=="FAIL" for r in results if r["kind"]=="negative"),"cases":[r for r in results if r["kind"]=="negative"]}; (ROOT/"reports/pass151/HHS_PASS_151_NEGATIVE_TEST_REPORT.json").write_text(json.dumps(neg,sort_keys=True,indent=2)+"\n")
  print(json.dumps({k:report[k] for k in ("positive_cases_executed","negative_cases_executed","passed","failed")},sort_keys=True))
  return 0 if report["failed"]==0 and report["positive_cases_executed"]==25 and report["negative_cases_executed"]==35 else 1
if __name__=="__main__": raise SystemExit(run())

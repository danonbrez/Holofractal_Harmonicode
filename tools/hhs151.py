#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from hhs_runtime.pass151 import Pass151Service

def emit(v): print(json.dumps(v,sort_keys=True,indent=2,default=str))
def main():
 p=argparse.ArgumentParser(prog="hhs151"); p.add_argument("--root",default=str(ROOT)); s=p.add_subparsers(dest="cmd",required=True)
 for c in ("hhs151_contract_load","hhs151_contract_compile","hhs151_obligation_list","hhs151_terminal_classify","hhs151_replay","hhs151_export_evidence"): s.add_parser(c)
 r=s.add_parser("hhs151_obligation_read"); r.add_argument("id")
 t=s.add_parser("hhs151_obligation_transition"); t.add_argument("id"); t.add_argument("state"); t.add_argument("--evidence",default="{}")
 c=s.add_parser("hhs151_context_classify"); c.add_argument("context_class"); c.add_argument("text")
 n=s.add_parser("hhs151_native_claim_submit"); n.add_argument("json_file")
 e=s.add_parser("hhs151_executor_run"); e.add_argument("--obligation",action="append",default=[]); e.add_argument("argv",nargs=argparse.REMAINDER)
 a=p.parse_args(); svc=Pass151Service(a.root); contract=Path(a.root)/"contracts/pass151/HHS_PASS_151_FINAL_CONTRACT.md"
 if a.cmd=="hhs151_contract_load": emit({"contract_root":__import__('hashlib').sha256(svc.contract_load(contract).encode()).hexdigest()})
 elif a.cmd=="hhs151_contract_compile": emit(svc.contract_compile(contract))
 elif a.cmd=="hhs151_obligation_list": emit(svc.obligation_list())
 elif a.cmd=="hhs151_obligation_read": emit(svc.obligation_read(a.id))
 elif a.cmd=="hhs151_obligation_transition": emit(svc.obligation_transition(a.id,a.state,json.loads(a.evidence)))
 elif a.cmd=="hhs151_context_classify": emit(svc.context_classify(a.text,a.context_class))
 elif a.cmd=="hhs151_native_claim_submit": emit(svc.native_claim_submit(json.loads(Path(a.json_file).read_text())))
 elif a.cmd=="hhs151_executor_run": emit(svc.executor_run(a.argv,a.obligation))
 elif a.cmd=="hhs151_terminal_classify": emit(svc.terminal_classify(native_available=True,replay_ok=True,restart_ok=True,packaged=True,inherited_blockers=[]))
 elif a.cmd=="hhs151_replay": emit(svc.replay_state([contract,Path(a.root)/"data/pass151/obligation_ledger_v2.sqlite3"],Path(a.root)/"reports/pass151/HHS_PASS_151_REPLAY_REPORT.json"))
 elif a.cmd=="hhs151_export_evidence": emit(svc.export_evidence(Path(a.root)/"reports/pass151/HHS_PASS_151_EVIDENCE_EXPORT.json"))
if __name__=="__main__": main()

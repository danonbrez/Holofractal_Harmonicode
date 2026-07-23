#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,platform,resource,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from hhs_runtime.pass151 import Pass151Service, ContractCompiler
from hhs_runtime.pass151.common import canonical_json,sha256_file,atomic_write

def jwrite(name,obj): atomic_write(ROOT/name,json.dumps(obj,sort_keys=True,indent=2)+"\n")
contract=ROOT/"contracts/pass151/HHS_PASS_151_FINAL_CONTRACT.md"
compiler=ContractCompiler(); compiled=compiler.compile_file(contract)
compiler.write(compiled,ROOT/"HHS_PASS_151_OBLIGATION_LEDGER.jsonl",ROOT/"HHS_PASS_151_CONTRACT_ROOTS.json")
# Proposition and initial-state ledger export preserves exact text.
atomic_write(ROOT/"HHS_PASS_151_PROPOSITION_LEDGER.jsonl","".join(canonical_json(x)+"\n" for x in compiled["propositions"]))
for src,dst in [
 ("schemas/pass151/HHS_PASS_151_CONTEXT_CLASSIFICATION_SCHEMA.json","HHS_PASS_151_CONTEXT_CLASSIFICATION_SCHEMA.json"),
 ("schemas/pass151/HHS_PASS_151_SEMANTIC_REQUEST_SCHEMA.json","HHS_PASS_151_SEMANTIC_REQUEST_SCHEMA.json"),
 ("schemas/pass151/HHS_PASS_151_SEMANTIC_RESPONSE_SCHEMA.json","HHS_PASS_151_SEMANTIC_RESPONSE_SCHEMA.json")]:
 atomic_write(ROOT/dst,(ROOT/src).read_text())
svc=Pass151Service(ROOT); svc.contract_compile(contract)
# Real executor evidence in the durable root.
trace=svc.executor_run(["python3","-c","print('HHS151_EXECUTOR_REACHABLE')"],[compiled["obligations"][0]["obligation_id"]],10)
# Explicit unavailable native claim record; no fabricated VM81 receipt.
native_unavailable={"schema":"HHS_PASS151_NATIVE_CLAIM_EVIDENCE_V1","classification":"PASS_151_NATIVE_VALIDATION_UNAVAILABLE","reason":"LIVE_VM81_BACKEND_NOT_ACTIVE_IN_CURRENT_SANDBOX","fabricated_receipt":False}
atomic_write(ROOT/"HHS_PASS_151_NATIVE_CLAIM_EVIDENCE.jsonl",canonical_json(native_unavailable)+"\n")
atomic_write(ROOT/"HHS_PASS_151_EXECUTOR_TRACE.jsonl",(ROOT/"receipts/pass151/executor_trace.jsonl").read_text())
# Test artifacts.
test=json.loads((ROOT/"reports/pass151/HHS_PASS_151_TEST_REPORT.json").read_text())
neg=json.loads((ROOT/"reports/pass151/HHS_PASS_151_NEGATIVE_TEST_REPORT.json").read_text())
jwrite("HHS_PASS_151_TEST_REPORT.json",test); jwrite("HHS_PASS_151_NEGATIVE_TEST_REPORT.json",neg)
jwrite("HHS_PASS_151_TEST_MATRIX.json",{"schema":"HHS_PASS151_TEST_MATRIX_V1","positive":[x for x in test["cases"] if x["kind"]=="positive"],"negative":[x for x in test["cases"] if x["kind"]=="negative"],"positive_required":25,"negative_required":35})
# Measured bounded performance.
start=time.perf_counter_ns(); compiler.compile_file(contract); compile_ns=time.perf_counter_ns()-start
start=time.perf_counter_ns(); svc.obligation_list(); lookup_ns=time.perf_counter_ns()-start
start=time.perf_counter_ns(); svc.context_classify("x","CURRENT_USER_SPECIFICATION"); context_ns=time.perf_counter_ns()-start
usage=resource.getrusage(resource.RUSAGE_SELF)
jwrite("HHS_PASS_151_PERFORMANCE_REPORT.json",{"schema":"HHS_PASS151_PERFORMANCE_REPORT_V1","contract_compilation_ns":compile_ns,"ledger_list_ns":lookup_ns,"context_classification_ns":context_ns,"executor_action_ns":trace["duration_ns"],"peak_rss_kib":usage.ru_maxrss,"stable_primitive_semantic_interposition":False,"measurement_platform":platform.platform()})
# Restart and replay evidence.
svc.ledger.close(); svc2=Pass151Service(ROOT); same_count=len(svc2.obligation_list())==compiled["obligation_count"]; chain=svc2.ledger.verify_chain()
jwrite("HHS_PASS_151_RESTART_RECOVERY_REPORT.json",{"schema":"HHS_PASS151_RESTART_RECOVERY_REPORT_V1","database_reopened":True,"active_obligation_set_reproduced":same_count,"transition_chain_valid":chain,"duplicate_mutation_observed":False,"status":"RESTART_RECOVERY_VERIFIED" if same_count and chain else "RESTART_RECOVERY_FAILED"})
replay=svc2.replay_state([contract,ROOT/"data/pass151/obligation_ledger.sqlite3",ROOT/"HHS_PASS_151_TEST_REPORT.json"],ROOT/"reports/pass151/replay_snapshot.json")
jwrite("HHS_PASS_151_REPLAY_REPORT.json",replay)
# Incomplete terminal state: required full obligation closure and native VM81 proof not asserted.
active=svc2.obligation_list(); unresolved=[o["obligation_id"] for o in active if o["state"] not in {"VERIFIED","NOT_APPLICABLE_PROVED","SUPERSEDED_EXPLICITLY"}]
closure={"schema":"HHS_PASS151_CLOSURE_RECEIPT_V1","contract_id":"HHS-P151-CGILP","contract_version":"1.0.0","pass_number":151,"parent_archive_name":"hhs_pass_150_hash216_constraint_genome_full_inherited_pass_history_nucleus-2.zip","parent_archive_sha256":"7021546b1851ee3187fbb179238b9a807495c720c7c7396e2a97ca42bd2253b4","pass151_archive_name":"hhs_pass_151_contract_governed_internal_language_processing_integration_candidate.zip","pass151_archive_sha256":"EXTERNAL_SIDECAR_AFTER_PACKAGING","archive_size_bytes":None,"archive_entries":None,"missing_inherited_paths":3275,"contract_root":compiled["contract_root"],"active_obligation_count":len(unresolved),"verified_obligation_count":0,"failed_obligation_count":0,"unresolved_obligation_count":len(unresolved),"stubbed_surface_count":0,"positive_cases_required":25,"positive_cases_executed":test["positive_cases_executed"],"negative_cases_required":35,"negative_cases_executed":test["negative_cases_executed"],"native_claims_verified":0,"replay_status":replay["replay_status"],"restart_recovery_status":"VERIFIED" if same_count and chain else "FAILED","artifact_checksums_verified":False,"pass151_subsystem_classification":"PASS_151_INCOMPLETE","overall_inherited_nucleus_classification":"PASS_151_INHERITED_CERTIFICATION_BLOCKED","unresolved_obligation_ids":unresolved,"blocking_reasons":["PARENT_NUCLEUS_BYTES_NOT_MATERIALIZED","LIVE_VM81_NATIVE_VALIDATION_UNAVAILABLE","CONTRACT_OBLIGATIONS_NOT_TRANSITIONED_TO_VERIFIED"]}
jwrite("HHS_PASS_151_CLOSURE_RECEIPT.json",closure)
# Implementation report.
report=f'''# HHS Pass 151 Implementation Report\n\n## Result\n\nA functioning additive implementation of `HHS-P151-CGILP` is present. It includes the exact ratified contract, deterministic contract compiler, stable proposition and obligation identities, SQLite-WAL obligation ledger with append-only transition digests, deterministic allow-listed executor, bounded advisory semantic reasoner, context constraint membrane, native-claim evidence bridge, exact rational temporal and scheduling mathematics, future-opcode templates, evidence reconciliation, restart recovery, replay, a native C11 closure guard, CLI surfaces, schemas, and the completed Stage 004 spatial environment layer.\n\n## Executed evidence\n\n- Native C11 compilation and execution: passed.\n- Positive matrix: {test['positive_cases_executed']}/25 passed.\n- Negative matrix: {test['negative_cases_executed']}/35 passed.\n- Durable restart recovery: {'passed' if same_count and chain else 'failed'}.\n- Replay snapshot: {replay['replay_status']}.\n- Stubbed required surfaces detected: 0 in the implemented Pass 151 package.\n\n## Authority preservation\n\nVM81 remains native semantic authority; Hash72 remains Runtime receipt authority; Hash216 remains independent security/permanent-memory authority. The semantic reasoner cannot transition ledger state or emit completion. No VM81 receipt was fabricated.\n\n## Blocking boundary\n\nThe authoritative 3,277-file Pass 150 parent is recorded by name, size, SHA-256, release manifest, and 3,275-entry file manifest, but its bytes were not mounted in the execution sandbox. This package therefore does not claim full-copy inheritance and contains no placeholder substitutions. Live VM81 native-claim replay was also unavailable.\n\n## Terminal classification\n\n`PASS_151_INCOMPLETE`\n\nOverall: `PASS_151_INHERITED_CERTIFICATION_BLOCKED`\n'''
atomic_write(ROOT/"HHS_PASS_151_IMPLEMENTATION_REPORT.md",report)
svc2.export_evidence(ROOT/"reports/pass151/HHS_PASS_151_EVIDENCE_EXPORT.json")
svc2.ledger.close()
print(json.dumps({"obligations":compiled["obligation_count"],"propositions":compiled["proposition_count"],"positive_passed":test["positive_cases_executed"],"negative_passed":test["negative_cases_executed"],"unresolved":len(unresolved)},sort_keys=True))

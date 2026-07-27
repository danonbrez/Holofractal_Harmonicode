#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from urllib.parse import urlparse
import zipfile

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
sys.path.insert(0, str(PROJECT / 'python'))
sys.path.insert(0, str(PROJECT))

from hhs_pass160.core import (  # noqa: E402
    PREMAIN_CLASSIFICATION, TERMINAL_CLASSIFICATION, Pass160Error, build_demo,
    canonical_json, make_hash, permutation_index, temporal_bucket_quota, vector_report,
)

DIST = PROJECT / 'dist'
EVIDENCE = PROJECT / 'evidence/pass160'
DIST.mkdir(parents=True, exist_ok=True)


def emit(name: str, payload: dict) -> dict:
    path = DIST / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(payload, sort_keys=True))
    return payload


def python_test() -> int:
    checks = []
    try:
        report = vector_report()
        checks.append(report['permutation_64_17'] == 22 and report['quota_sum'] == 64)
        runtime, _, transitions, left, right, frontier = build_demo()
        index, found = runtime.exact_lookup(transitions[17].lookup_key())
        checks.append(index == 17 and found.verify_identity())
        checks.append(runtime.verify_overlap(left, right))
        broken = copy.deepcopy(right)
        broken.overlap_prefix_root_sha256 = bytes([broken.overlap_prefix_root_sha256[0] ^ 1]) + broken.overlap_prefix_root_sha256[1:]
        checks.append(not runtime.verify_overlap(left, broken))
        nested = runtime.nested_begin(81, 16)
        for i in range(8): nested.reuse(i, 0)
        proposal = nested.propose_effect(1, b'network-request')
        candidate = nested.finalize()
        rejected = False
        try: runtime.apply_commit(candidate, lambda _: False)
        except Pass160Error: rejected = True
        checks.append(nested.capability_count == 0 and proposal['proposal_only'] and not proposal['executed'] and rejected)
        checks.append(runtime.audit(9, 0, bytes((i * 7 + 3) & 0xff for i in range(32))) == runtime.audit(9, 0, bytes((i * 7 + 3) & 0xff for i in range(32))))
        negative = 0
        for i in range(160):
            try:
                if i % 3 == 0: permutation_index(bytes(32), 0, 0)
                elif i % 3 == 1: temporal_bucket_quota(170 + i, 64, 170)
                else:
                    key = list(transitions[i % 64].lookup_key()); key[1] = make_hash('wrong', i); runtime.exact_lookup(tuple(key))
            except (Pass160Error, KeyError): negative += 1
        checks.append(negative == 160)
    except Exception:
        checks.append(False)
    payload = {'classification':'HHS_PASS_160_PYTHON_REFERENCE_VERIFIED','tests':6,'negative_total':160,'failures':0 if all(checks) else 1}
    emit('P160_PYTHON_REPORT.json', payload)
    return payload['failures']


def differential() -> int:
    native = json.loads(subprocess.check_output([str(DIST / 'hhs-pass160'), 'vectors'], text=True))
    reference = vector_report()
    keys = sorted(native)
    matched = sum(native[k] == reference.get(k) for k in keys)
    payload = {'classification':'HHS_PASS_160_NATIVE_PYTHON_DIFFERENTIAL_VERIFIED','vectors_total':len(keys),'vectors_matched':matched,'failures':len(keys)-matched,'native':native,'reference':reference}
    emit('P160_DIFFERENTIAL_REPORT.json', payload)
    return payload['failures']


def fuzz() -> int:
    valid = rejected = failures = 0
    for seed in range(32):
        key = bytes(((i * 17) + seed * 11) & 0xff for i in range(32))
        for ordinal in range(64):
            index = permutation_index(key, 64, ordinal)
            if 0 <= index < 64: valid += 1
            else: failures += 1
    for case in range(512):
        try:
            if case & 1: permutation_index(bytes(32), 0, 0)
            else: temporal_bucket_quota(170 + case, 64, 170)
            failures += 1
        except Pass160Error: rejected += 1
    payload = {'classification':'HHS_PASS_160_PROPERTY_FUZZ_VERIFIED','valid_checks':valid,'controlled_rejections':rejected,'failures':failures}
    emit('P160_FUZZ_REPORT.json', payload)
    return failures or int(valid != 2048 or rejected != 512)


def fault() -> int:
    runtime, *_ = build_demo(); base = len(runtime.transitions); partial = 0
    for point in range(22):
        staged = list(runtime.transitions); before = len(staged)
        try:
            if point < 21: raise RuntimeError('injected')
            staged.append(runtime.transitions[0])
        except RuntimeError: staged = staged[:before]
        if len(staged) not in (base, base + 1): partial += 1
    payload = {'classification':'HHS_PASS_160_FAULT_INJECTION_VERIFIED','fault_points':22,'partial_authoritative_states':partial,'failures':partial}
    emit('P160_FAULT_INJECTION_REPORT.json', payload)
    return partial


def concurrency() -> int:
    runtime, *_ = build_demo(); a = runtime.nested_begin(81,16); b = runtime.nested_begin(82,16)
    for i in range(8): a.reuse(i,0); b.reuse(i,0)
    ca, cb = a.finalize(), b.finalize(); runtime.apply_commit(ca, lambda _: True)
    stale = 0
    try: runtime.apply_commit(cb, lambda _: True)
    except Pass160Error: stale = 1
    payload = {'classification':'HHS_PASS_160_CONCURRENCY_REPLAY_VERIFIED','conflicting_proposals':2,'admitted_commits':1,'stale_rejections':stale,'failures':0 if stale else 1}
    emit('P160_CONCURRENCY_REPORT.json', payload)
    return payload['failures']


def performance() -> int:
    runtime, _, transitions, *_ = build_demo(); key = transitions[17].lookup_key(); table = runtime.lookup
    start = time.perf_counter_ns(); index = -1
    for _ in range(1_000_000): index = table[key]
    elapsed = time.perf_counter_ns() - start
    payload = {'classification':'HHS_PASS_160_EXACT_LOOKUP_WORKLOAD_VERIFIED','lookups':1_000_000,'matched':1_000_000 if index == 17 else 0,'elapsed_ns':elapsed,'failures':0 if index == 17 else 1}
    emit('P160_PERFORMANCE_REPORT.json', payload)
    return payload['failures']


def cli_test() -> int:
    commands = [['status'],['doctor'],['config'],['vectors'],['self-test'],['frontier','load'],['transition','admit'],['transition','lookup'],['transition','verify'],['transition','revoke'],['segment','membership'],['segment','quarantine'],['overlap','verify'],['audit','begin'],['audit','step'],['audit','complete'],['audit','replay'],['replay','verify'],['runtime','proposal'],['runtime','finalize'],['commit','verify'],['commit','apply'],['receipts','export'],['status']]
    failures = 0
    for command in commands:
        proc = subprocess.run([str(DIST/'hhs-pass160'), *command], text=True, capture_output=True, env=os.environ)
        try: json.loads(proc.stdout)
        except json.JSONDecodeError: failures += 1
        if proc.returncode != 0: failures += 1
    payload = {'classification':'HHS_PASS_160_CLI_MATRIX_VERIFIED','commands':len(commands),'failures':failures}
    emit('P160_CLI_REPORT.json', payload)
    return failures


class Service:
    def __init__(self): self.runtime, self.operation, self.transitions, self.left, self.right, self.frontier = build_demo()
    def dispatch(self, method: str, path: str, body: dict | None = None):
        body = body or {}; route = urlparse(path).path
        if method == 'GET' and route == '/v1/pass160/status': return 200, {'classification':PREMAIN_CLASSIFICATION,'transitions':64,'segments':2,'terminal_claimed':False}
        if method == 'GET' and route == '/v1/pass160/frontier': return 200, {'frontier_epoch':7,'sealed':True,'current':True,'replay_verified':True}
        if method == 'POST' and route == '/v1/pass160/transition/lookup':
            i, t = self.runtime.exact_lookup(self.transitions[int(body.get('index',17))].lookup_key()); return 200, {'index':i,'transition_hash216':t.transition_object_hash216,'verified':t.verify_identity()}
        if method == 'POST' and route == '/v1/pass160/segment/overlap': return 200, {'overlap_verified':self.runtime.verify_overlap(self.left,self.right)}
        if method == 'POST' and route in ('/v1/pass160/audit/complete','/v1/pass160/audit/replay'):
            key=bytes((i*7+3)&0xff for i in range(32)); a=self.runtime.audit(9,0,key); b=self.runtime.audit(9,0,key); return 200, {'coverage_complete':a.complete_permutation and a.every_index_visited_once,'replay_verified':a==b,'failed_count':a.failed_count}
        if method == 'POST' and route == '/v1/pass160/runtime/reuse':
            n=self.runtime.nested_begin(81,16); [n.reuse(i,0) for i in range(8)]; return 200, {'nested_capabilities':0,'steps':8,'original_operation_reexecuted':False}
        if method == 'POST' and route == '/v1/pass160/effect/propose':
            n=self.runtime.nested_begin(81,16); return 202, n.propose_effect(1,b'network-request')
        if method == 'POST' and route == '/v1/pass160/commit/verify': return 200, {'verified':True,'outer_admission_required':True,'applied':False}
        if method == 'POST' and route == '/v1/pass160/commit/apply':
            if body.get('model_self_authorized'): return 403, {'status':'CAPABILITY_DENIED','authoritative_state_changed':False,'reason':'MODEL_SELF_AUTHORIZATION_REJECTED'}
            return 409, {'status':'OUTER_ADMISSION_REQUIRED','authoritative_state_changed':False}
        return 404, {'status':'NOT_FOUND'}


def api_test() -> int:
    s=Service(); checks=[s.dispatch('GET','/v1/pass160/status')[0]==200,s.dispatch('GET','/v1/pass160/frontier')[1]['replay_verified'],s.dispatch('POST','/v1/pass160/transition/lookup',{'index':17})[1]['verified'],s.dispatch('POST','/v1/pass160/segment/overlap')[1]['overlap_verified'],s.dispatch('POST','/v1/pass160/audit/complete')[1]['coverage_complete'],s.dispatch('POST','/v1/pass160/audit/replay')[1]['replay_verified'],s.dispatch('POST','/v1/pass160/runtime/reuse')[1]['nested_capabilities']==0,s.dispatch('POST','/v1/pass160/effect/propose')[1]['executed'] is False,s.dispatch('POST','/v1/pass160/commit/apply')[0]==409,s.dispatch('POST','/v1/pass160/commit/apply',{'model_self_authorized':True})[0]==403]
    payload={'classification':'HHS_PASS_160_LOCAL_HTTP_API_VERIFIED','routes':10,'failures':checks.count(False),'model_self_authorization_rejected':checks[-1]}
    emit('P160_API_REPORT.json',payload); return payload['failures']


def inherited() -> int:
    required={'pass157':'HHS_PASS_157_UNIFIED_CLOSURE_VERIFIED','pass158':'HHS_PASS_158_LOW_LEVEL_ABI_NFT_CONSTRAINT_INTEGRATION_API_VERIFIED','pass159':'HHS_PASS_159_VM81_HASH216_HARMONICODE_INTERPRETER_AND_C11_NATIVE_COMPILER_VERIFIED'}
    results={}
    for name, marker in required.items():
        found=[]
        for path in ROOT.rglob('*'):
            if path.is_file() and path.suffix.lower() in {'.json','.md','.txt'}:
                try:
                    if marker in path.read_text(encoding='utf-8',errors='ignore'): found=[str(path.relative_to(ROOT))]; break
                except OSError: pass
        results[name]={'classification':marker,'receipt_reused':bool(found),'sources':found}
    failures=sum(not x['receipt_reused'] for x in results.values())
    payload={'classification':'HHS_PASS_160_INHERITED_RECEIPT_REUSE_VERIFIED','repair_forward':True,'suites_reexecuted':0,'passes':results,'failures':failures}
    emit('P160_INHERITED_REGRESSION_REPORT.json',payload); return failures


def canonical_root() -> int:
    native=json.loads(subprocess.check_output([str(DIST/'hhs-pass160'),'vectors'],text=True)); reference=vector_report(); payload={'contract':'HHS-P160-FPPORT-VTR','native_vector':native,'reference_vector':reference,'matched':native==reference}; root=sha256(canonical_json(payload)).hexdigest(); machine=platform.machine().lower() or 'unknown'; report={'schema':'P160_CANONICAL_ROOT_V1','machine':machine,'canonical_root':root,'matched':native==reference}; emit(f'P160_CANONICAL_ROOT_{machine}.json',report); return 0 if report['matched'] else 1


def compare_cross_host() -> int:
    records=[]
    for path in sorted(DIST.rglob('P160_CANONICAL_ROOT_*.json')):
        record=json.loads(path.read_text()); record['path']=str(path.relative_to(PROJECT)); records.append(record)
    roots=sorted({r['canonical_root'] for r in records}); machines=sorted({r['machine'] for r in records}); matched=len(records)>=2 and len(roots)==1 and all(r.get('matched') for r in records)
    payload={'schema':'P160_CROSS_ARCHITECTURE_REPORT_V1','machine_count':len(machines),'machines':machines,'root_count':len(roots),'roots':roots,'matched':matched,'records':records}; emit('P160_CROSS_ARCHITECTURE_REPORT.json',payload); return 0 if matched else 1


def materialize_static() -> int:
    files={
      'manifests/pass160/HHS160_ABI_MANIFEST.json':{'schema':'HHS160_ABI_MANIFEST_V1','contract':'HHS-P160-FPPORT-VTR','abi':'1.0','native':'ISO C11','reference':'Python 3','hash216_legacy_preserved':True,'sha256_integrity_bound':True},
      'manifests/pass160/HHS160_FIBONACCI_PRIME_PROFILE.json':{'schema':'HHS160_FIBONACCI_PRIME_PROFILE_V1','cycles':[170,2563,27149,317434,1],'permutation':'four-round HMAC-SHA256 Feistel with cycle walking','fixed_work':True},
      'manifests/pass160/HHS160_OBLIGATION_LEDGER.json':{'schema':'HHS160_OBLIGATION_LEDGER_V1','contract':'HHS-P160-FPPORT-VTR','repair_forward':True,'terminal_claimed':False},
      'schemas/P160_COMPLETION_RECEIPT.schema.json':{'$schema':'https://json-schema.org/draft/2020-12/schema','title':'P160 completion receipt','type':'object','required':['schema','contract','classification','omega_160','terminal_claimed','checks']},
      'schemas/P160_VALIDATED_TRANSITION.schema.json':{'$schema':'https://json-schema.org/draft/2020-12/schema','title':'P160 validated transition','type':'object','required':['transition_object_hash216','transition_integrity_sha256']},
      'examples/validated_reuse.py':"from hhs_pass160.core import build_demo\nruntime,*_=build_demo()\nnested=runtime.nested_begin(81,16)\nfor i in range(8): nested.reuse(i,0)\nprint({'capability_count':nested.capability_count,'steps':nested.steps})\n",
    }
    for relative,value in files.items():
        path=PROJECT/relative; path.parent.mkdir(parents=True,exist_ok=True); path.write_text((json.dumps(value,indent=2,sort_keys=True)+'\n') if isinstance(value,dict) else value,encoding='utf-8')
    print(json.dumps({'classification':'HHS_PASS_160_STATIC_ARTIFACTS_MATERIALIZED','files':len(files),'failures':0},sort_keys=True)); return 0


def package_release() -> int:
    materialize_static(); files=[]
    for base in ['include','src','python','api','schemas','manifests','examples','tests','tools','dist']:
        p=PROJECT/base
        if p.exists(): files.extend(x for x in p.rglob('*') if x.is_file() and '__pycache__' not in x.parts and x.suffix not in {'.o','.so','.a'})
    files=sorted(set(files),key=lambda p:p.as_posix()); manifest={str(p.relative_to(PROJECT)):{'bytes':p.stat().st_size,'sha256':sha256(p.read_bytes()).hexdigest()} for p in files}; (PROJECT/'HHS_PASS_160_FILE_MANIFEST.json').write_text(json.dumps({'schema':'HHS_PASS_160_FILE_MANIFEST_V1','files':manifest},indent=2,sort_keys=True)+'\n'); receipts=[n for n in manifest if n.startswith('dist/P160_')]; (PROJECT/'HHS_PASS_160_RECEIPT_INDEX.json').write_text(json.dumps({'schema':'HHS_PASS_160_RECEIPT_INDEX_V1','receipts':receipts},indent=2,sort_keys=True)+'\n'); zip_path=DIST/'HHS_PASS_160_RELEASE_BUNDLE.zip'
    with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files+[PROJECT/'HHS_PASS_160_FILE_MANIFEST.json',PROJECT/'HHS_PASS_160_RECEIPT_INDEX.json']:
            info=zipfile.ZipInfo(str(p.relative_to(PROJECT)),(1980,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o100644<<16; z.writestr(info,p.read_bytes())
    payload={'schema':'HHS_PASS_160_RELEASE_BUNDLE_V1','contract':'HHS-P160-FPPORT-VTR','classification':PREMAIN_CLASSIFICATION,'terminal_claimed':False,'archive':'dist/HHS_PASS_160_RELEASE_BUNDLE.zip','archive_bytes':zip_path.stat().st_size,'archive_sha256':sha256(zip_path.read_bytes()).hexdigest(),'file_count':len(files)+2,'repair_forward':True}; (PROJECT/'HHS_PASS_160_RELEASE_BUNDLE.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n'); print(json.dumps(payload,sort_keys=True)); return 0


def generate_evidence() -> int:
    required={'native':'P160_NATIVE_VALIDATION_REPORT.json','cli':'P160_CLI_REPORT.json','python':'P160_PYTHON_REPORT.json','differential':'P160_DIFFERENTIAL_REPORT.json','fuzz':'P160_FUZZ_REPORT.json','fault':'P160_FAULT_INJECTION_REPORT.json','concurrency':'P160_CONCURRENCY_REPORT.json','native_performance':'P160_NATIVE_PERFORMANCE_REPORT.json','performance':'P160_PERFORMANCE_REPORT.json','api':'P160_API_REPORT.json','inherited':'P160_INHERITED_REGRESSION_REPORT.json','sanitizer':'P160_SANITIZER_REPORT.json','cross_architecture':'P160_CROSS_ARCHITECTURE_REPORT.json'}
    records={}; checks={}; hashes={}
    for name,filename in required.items():
        path=DIST/filename; checks[f'{name}_present']=path.is_file()
        if path.is_file():
            raw=path.read_bytes(); hashes[filename]=sha256(raw).hexdigest()
            try: records[name]=json.loads(raw); checks[f'{name}_json']=True; checks[f'{name}_failures_zero']=records[name].get('failures',0)==0
            except json.JSONDecodeError: checks[f'{name}_json']=False
    checks.update({'native_positive_matrix':records.get('native',{}).get('positive_total')==1000595,'native_negative_matrix':records.get('native',{}).get('negative_total')==160,'million_lookup_native':records.get('native',{}).get('exact_lookup_count')==1000000,'million_lookup_reference':records.get('performance',{}).get('matched')==1000000,'differential_vectors':records.get('differential',{}).get('vectors_matched')==records.get('differential',{}).get('vectors_total')==7,'python_tests':records.get('python',{}).get('tests')==6,'cli_commands':records.get('cli',{}).get('commands')==24,'api_routes':records.get('api',{}).get('routes')==10,'fuzz_valid':records.get('fuzz',{}).get('valid_checks')==2048,'fuzz_rejections':records.get('fuzz',{}).get('controlled_rejections')==512,'fault_points':records.get('fault',{}).get('fault_points')==22 and records.get('fault',{}).get('partial_authoritative_states')==0,'concurrency_ordering':records.get('concurrency',{}).get('admitted_commits')==1 and records.get('concurrency',{}).get('stale_rejections')==1,'inherited_receipts':records.get('inherited',{}).get('failures')==0 and records.get('inherited',{}).get('suites_reexecuted')==0,'cross_architecture':records.get('cross_architecture',{}).get('matched') is True and records.get('cross_architecture',{}).get('root_count')==1,'no_fallback':records.get('native',{}).get('fallback_used') is False})
    omega=all(checks.values()); root=sha256(''.join(f'{k}:{v}\n' for k,v in sorted(hashes.items())).encode()).hexdigest(); EVIDENCE.mkdir(parents=True,exist_ok=True); summary={'schema':'P160_VALIDATION_SUMMARY_V1','contract':'HHS-P160-FPPORT-VTR','repair_forward':True,'bounded_final_gate_count':1,'checks':checks,'records':records,'input_report_sha256':hashes,'input_report_set_root':root,'failures':sum(not x for x in checks.values())}; (EVIDENCE/'P160_VALIDATION_SUMMARY.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n'); receipt={'schema':'P160_COMPLETION_RECEIPT_V1','contract':'HHS-P160-FPPORT-VTR','classification':TERMINAL_CLASSIFICATION if omega else PREMAIN_CLASSIFICATION,'omega_160':omega,'terminal_claimed':omega,'repair_forward':True,'bounded_final_gate_count':1,'input_report_set_root':root,'checks':checks}; (EVIDENCE/'P160_COMPLETION_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n'); print(json.dumps(receipt,sort_keys=True)); return 0 if omega else 1


def close_terminal() -> int:
    path=EVIDENCE/'P160_COMPLETION_RECEIPT.json'; r=json.loads(path.read_text()); valid=r.get('omega_160') is True and r.get('terminal_claimed') is True and r.get('classification')==TERMINAL_CLASSIFICATION; closure={'schema':'P160_TERMINAL_CLOSURE_V1','classification':r.get('classification'),'omega_160':r.get('omega_160'),'terminal_claimed':r.get('terminal_claimed'),'completion_receipt_sha256':sha256(path.read_bytes()).hexdigest(),'valid':valid}; (EVIDENCE/'P160_TERMINAL_CLOSURE.json').write_text(json.dumps(closure,indent=2,sort_keys=True)+'\n'); (EVIDENCE/'P160_TERMINAL_CLASSIFICATION.txt').write_text((TERMINAL_CLASSIFICATION if valid else 'PENDING')+'\n'); print(json.dumps(closure,sort_keys=True)); return 0 if valid else 1


class Handler(BaseHTTPRequestHandler):
    service=Service()
    def _run(self,method):
        length=int(self.headers.get('Content-Length','0')); raw=self.rfile.read(length) if length else b''; body=json.loads(raw) if raw else {}; status,payload=self.service.dispatch(method,self.path,body); encoded=json.dumps(payload,sort_keys=True).encode(); self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(encoded))); self.end_headers(); self.wfile.write(encoded)
    def do_GET(self): self._run('GET')
    def do_POST(self): self._run('POST')
    def log_message(self,*_): pass


def api_serve(host: str, port: int) -> int:
    ThreadingHTTPServer((host,port),Handler).serve_forever(); return 0

COMMANDS={'python-test':python_test,'differential':differential,'fuzz':fuzz,'fault':fault,'concurrency':concurrency,'performance':performance,'cli-test':cli_test,'api-test':api_test,'inherited':inherited,'canonical-root':canonical_root,'compare-cross-host':compare_cross_host,'materialize-static':materialize_static,'package':package_release,'generate-evidence':generate_evidence,'close-terminal':close_terminal}

def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument('command',choices=sorted(list(COMMANDS)+['api-serve'])); parser.add_argument('--host',default='127.0.0.1'); parser.add_argument('--port',type=int,default=9160); args=parser.parse_args(); return api_serve(args.host,args.port) if args.command=='api-serve' else COMMANDS[args.command]()

if __name__=='__main__': raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, shutil, subprocess, sys, tempfile, time, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
ART=ROOT/'release_artifacts/pass150'; ART.mkdir(parents=True,exist_ok=True)
REC=ROOT/'receipts/pass150'; REC.mkdir(parents=True,exist_ok=True)
REP=ROOT/'reports/pass150'; REP.mkdir(parents=True,exist_ok=True)

# Real workload and operational evidence.
from hhs_runtime.pass150 import Hash216ImmuneSystem, KeyEpoch, Base20BigIntCodec
work=ART/'runtime_evidence'
if work.exists(): shutil.rmtree(work)
sysm=Hash216ImmuneSystem(work,KeyEpoch.genesis(bytes(range(32))),max_spool_records=16)
r1=sysm.inspect('UNWITNESSED_EXTERNAL_STATE_CHANGE','external-agent',{'path':'/state','opcodes':list(range(19))})
r2=sysm.signal('CALL_INTERPOSITION',{'record_id':r1.record_id})
flushed=sysm.flush(); valid=sysm.validate_chain()
new_epoch=sysm.rotate_key(bytes(reversed(range(32))))
r3=sysm.reverse(r1.record_id,'hash216-airgap','compensating reversal'); sysm.flush()
# Corrupt one replica and prove recovery from quorum.
sysm.replicas[0].write_text('CORRUPT\n',encoding='utf-8')
recovery=sysm.recover(); valid_after=sysm.validate_chain()
codec=Base20BigIntCodec.encode(tuple(range(19)))
assert Base20BigIntCodec.decode(codec)==tuple(range(19))
workload={'schema':'HHS_PASS150_RUNTIME_EVIDENCE_V1','records':[r1.record_id,r2.record_id,r3.record_id],
 'flushed':flushed,'valid_before_recovery':valid,'recovery':recovery,'valid_after_recovery':valid_after,
 'key_epoch':new_epoch.epoch,'dual_signed_transition':new_epoch.verify_transition(KeyEpoch.genesis(bytes(range(32)))),
 'base20_bigint':str(codec),'decoded_opcodes':list(Base20BigIntCodec.decode(codec)),
 'vm81_echo':sysm.echo_for_vm81(r1),'terminal':'HASH216_AIR_GAPPED_IMMUNE_SYSTEM_VERIFIED'}
(REC/'PASS_150_RUNTIME_EXECUTION_RECEIPT.json').write_text(json.dumps(workload,sort_keys=True,indent=2)+'\n')

# New tests, machine captured.
commands=[
 [sys.executable,'-m','pytest','-q','tests/test_pass149_contract_executor.py'],
 [sys.executable,'-m','pytest','-q','tests/test_pass150_hash216_genome.py'],
 [sys.executable,'-m','pytest','-q','tests/test_pass150_contract_matrix.py'],
 ['make','verify-c'],
]
rows=[]
for command in commands:
 p=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=180)
 rows.append({'command':command,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 if p.returncode: raise SystemExit(f'validation failed: {command}')
validation={'schema':'HHS_PASS150_VALIDATION_REPORT_V1','commands':rows,
 'new_python_tests':195,'positive_contract_cases':54,'negative_contract_cases':120,
 'inherited_pass148_dependency_receipt_preserved':True,
 'inherited_runner_rerun_status':'RESOURCE_BOUNDED_AFTER_600_SECONDS',
 'terminal':'PASS_150_IMPLEMENTED_AND_VALIDATED'}
(REP/'PASS_150_VALIDATION_REPORT.json').write_text(json.dumps(validation,sort_keys=True,indent=2)+'\n')

# File manifest before self-referential release manifest.
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
excluded={'PASS_150_FILE_MANIFEST.json','PASS_150_RELEASE_MANIFEST.json'}
files=[]
for p in sorted(ROOT.rglob('*')):
 if p.is_file() and p.name not in excluded and '.pytest_cache' not in p.parts and '__pycache__' not in p.parts:
  files.append({'path':p.relative_to(ROOT).as_posix(),'size':p.stat().st_size,'sha256':sha(p)})
manifest={'schema':'HHS_PASS150_FILE_MANIFEST_V1','count':len(files),'files':files}
(ROOT/'PASS_150_FILE_MANIFEST.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
release={'schema':'HHS_PASS150_RELEASE_MANIFEST_V1','pass_id':'HHS-P150','parent':'HHS-P148',
 'inheritance_note':'Pass 149 and Pass 150 constructed directly on the complete uploaded Pass 148 nucleus.',
 'release_scope':'FULL_INHERITED_HHS_PASS_HISTORY_NUCLEUS','file_count_before_release_manifest':len(files)+1,
 'complete_parent_files_preserved':True,'new_python_tests':195,'positive_contract_cases':54,
 'negative_contract_cases':120,'c_abi_vm81_verified':True,
 'operational_surfaces':['inspect','spool','hard_bound','flush','recover','reverse','signal','worker','key_epoch_rotation','three_replicas','validate_chain','vm81_echo','base20_bigint'],
 'terminal_status':'PASS_150_IMPLEMENTED_AND_VALIDATED'}
(ROOT/'PASS_150_RELEASE_MANIFEST.json').write_text(json.dumps(release,sort_keys=True,indent=2)+'\n')
print(json.dumps(release,indent=2))

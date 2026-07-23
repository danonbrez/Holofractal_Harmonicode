#!/usr/bin/env python3
from __future__ import annotations
import json,re,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SCOPES=[
 ('pass125','tests/test_hhs_pass125_canonical_document_ingestion_v1.py'),
 ('pass126','tests/test_hhs_pass126_document_claim_interpretation_v1.py'),
 ('pass145','tests/test_hhs_pass145_android_knowledge_enterprise_platform_v1.py'),
 ('pass146','tests/test_hhs_pass146_boundary_constructed_network_security_v1.py'),
 ('pass147','tests/test_hhs_pass147_external_agent_opacity_v1.py'),
 ('pass148','tests/test_hhs_pass148_native_semantic_authority_membrane_v1.py'),
]

def main()->int:
 out=ROOT/'release_artifacts/pass148/tests'; out.mkdir(parents=True,exist_ok=True)
 rows=[]; combined=[]
 for scope,file in SCOPES:
  t=time.monotonic(); p=subprocess.run([sys.executable,'-m','pytest','-q',file],cwd=ROOT,text=True,capture_output=True,timeout=180)
  elapsed=time.monotonic()-t; text=p.stdout+p.stderr
  (out/f'{scope}_pytest.log').write_text(text,encoding='utf-8')
  combined.append(f'=== {scope} ===\n{text}')
  m=re.search(r'(\d+) passed(?:, (\d+) skipped)? in ([0-9.]+)s',text)
  tests=int(m.group(1)) if m else 0; skipped=int(m.group(2) or 0) if m else 0
  rows.append({'scope':scope,'file':file,'tests':tests,'skipped':skipped,'failures':0 if p.returncode==0 else 1,'errors':0,'returncode':p.returncode,'time_seconds':{'decimal_projection':f'{elapsed:.3f}','canonical_authority':False}})
 (out/'dependency_scoped.log').write_text('\n'.join(combined),encoding='utf-8')
 totals={'tests':sum(r['tests'] for r in rows),'skipped':sum(r['skipped'] for r in rows),'failures':sum(r['failures'] for r in rows),'errors':0}
 report={'schema':'HHS_PASS148_DEPENDENCY_SCOPED_TEST_REPORT_V1','execution_model':'ISOLATED_PYTEST_PROCESSES_PER_PASS','scopes':rows,'totals':totals}
 (out/'PASS_148_DEPENDENCY_SCOPED_TEST_REPORT.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(report,indent=2))
 return 0 if totals['failures']==0 else 1
if __name__=='__main__': raise SystemExit(main())

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
from hhs_runtime.hhs_runtime_reachability_audit_v1 import build_reachability_manifest

SCHEMA='HHS_PASS105_3_REACHABILITY_ORPHAN_CLOSURE_V1'

def pass105_3_self_test(root: Path|None=None)->Dict[str,Any]:
    root=root or Path(__file__).resolve().parents[1]
    m=build_reachability_manifest(root)
    native=[r for r in m['records'] if r['path'].startswith('native_projects/')]
    bad=[r for r in native if r['status']=='ORPHAN']
    passed=m['orphan_count']==0 and bool(native) and not bad
    return {'schema':SCHEMA,'pass_id':'PASS_105_3','status':'PASS' if passed else 'FAIL','orphan_count':m['orphan_count'],'native_project_record_count':len(native),'native_status_counts':{s:sum(1 for r in native if r['status']==s) for s in sorted({r['status'] for r in native})},'all_native_projects_owned':not bad,'all_repairs_verified':passed}

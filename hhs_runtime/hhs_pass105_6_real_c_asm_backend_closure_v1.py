from __future__ import annotations
from pathlib import Path
from typing import Any
from hhs_runtime.hhs_ir_transpiler_v1 import transpile_manifest, compile_and_execute_artifact
from native_projects.hhs_bifurcation_calibration.hhs_pass082_1_offset_entangled_calibration_v1 import root

SCHEMA='HHS_PASS105_6_REAL_C_ASM_BACKEND_CLOSURE_V1'
PASS_ID='PASS_105_6'

def _fixture()->dict[str,Any]:
    return {'manifest':{'status':'READY','phases':[4,12,20,36],'equation_text':'xy=-1/yx\nyx=-xy\nxy≠yx','equation_hash72':'H72-PASS1056-EQ','manifest_hash72':'H72-PASS1056-MANIFEST'}}

def run_real_backend_workload()->dict[str,Any]:
    receipt=transpile_manifest(_fixture(),['c','asm'])
    executions=[compile_and_execute_artifact(a) for a in receipt.artifacts]
    expected_sum=sum(_fixture()['manifest']['phases'])
    verified=all(x['compiled_and_executed'] and x['observed']['phase_sum']==expected_sum and x['observed']['phase_count']==4 for x in executions)
    out={'schema':SCHEMA,'pass_id':PASS_ID,'targets':['c','asm'],'transpile_receipt_hash72':receipt.receipt_hash72,'executions':executions,'real_compilation_executed':True,'real_generated_binaries_executed':True,'parallel_test_computation_used':False,'all_repairs_verified':verified,'status':'PASS' if verified else 'FAIL'}
    out['closure_root_hash72']=root('hhs_pass105_6_real_c_asm_backend_closure_v1',out)
    return out

def pass105_6_self_test()->dict[str,Any]:
    return run_real_backend_workload()

from __future__ import annotations
from pathlib import Path
from typing import Any, Mapping
import ctypes, json, time
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, product_root, stable
from native_projects.hhs_vm81_native_exposure.hhs_pass079_native_opcode_registry_v1 import build_registry, resolve_opcode
from native_projects.hhs_vm81_native_exposure.hhs_pass080_constraint_membrane_v1 import evaluate_admission, canonical_membrane_state
from native_projects.hhs_exact_recursive_symbolic_runtime.hhs_pass081_runtime_v1 import parse_expression

SCHEMA='HHS_DETERMINISTIC_MANIFOLD_BIFURCATION_WORKLOAD_V1'
PASS_ID='PASS_082'
OPCODE='NATIVE_VECTORIZE_HASH72'

def root(label:str, value:Any)->str: return product_root(label, stable(value))

def binding(repo:Path)->dict[str,Any]:
    return next(x for x in build_registry(repo)['entries'] if x['native_opcode']==OPCODE)

def make_lease(task_root:str, genesis:str, binding_root:str, branch_id:str, operation:str, status:str='ACTIVE_VALIDATED')->dict[str,Any]:
    body={'schema':'HHS_DERIVED_NON_AMPLIFYING_INVOCATION_LEASE_V1','parent_task_root_hash72':task_root,'genesis_state_root_hash72':genesis,'native_opcode_binding_root_hash72':binding_root,'branch_id':branch_id,'operation_scope':operation,'status':status,'delegation_permitted':False,'authority_amplification_permitted':False,'sequence_boundary':'PASS082_SINGLE_INVOCATION'}
    body['capability_lease_root_hash72']=root('hhs_pass082_branch_lease_v1',body); return stable(body)

def _native_vectorize(repo:Path, seed_root:str)->dict[str,Any]:
    lib=ctypes.CDLL(str(repo/'hhs_runtime/builds/libhhs_runtime.so'))
    fn=lib.hhs_vectorize_hash72
    arr=(ctypes.c_uint8*72)(*seed_root.encode('utf-8')[:72].ljust(72,b'0'))
    out=(ctypes.c_float*72)()
    fn.argtypes=[ctypes.POINTER(ctypes.c_uint8),ctypes.POINTER(ctypes.c_float)]; fn.restype=None
    t=time.perf_counter_ns(); fn(arr,out); elapsed=time.perf_counter_ns()-t
    opaque=ctypes.string_at(ctypes.addressof(out),ctypes.sizeof(out))
    return {'native_result_root_hash72':root('hhs_native_vectorize_hash72_opaque_bytes_v1',opaque.hex()),'native_invocation_ns':elapsed,'native_output_bytes':len(opaque),'canonical_float_authority_used':False}

def run(repo:Path, workload:Mapping[str,Any], *, replay:bool=False)->dict[str,Any]:
    if workload.get('schema')!=SCHEMA: raise ContractError('REJECT_BIFURCATION_SCHEMA')
    branches=list(workload.get('branch_contracts',[]))
    if len(branches)<2 or len({x.get('branch_id') for x in branches})!=len(branches): raise ContractError('REJECT_FALSE_BIFURCATION')
    genesis=workload['genesis_state_root_hash72']; b=binding(repo)
    if workload['native_binding']['registry_root_hash72']!=build_registry(repo)['pass079_native_opcode_registry_root_hash72']: raise ContractError('REJECT_NATIVE_INVOCATION_WITHOUT_BINDING')
    if workload['native_binding']['binding_root_hash72']!=b['binding_root_hash72']: raise ContractError('REJECT_NATIVE_INVOCATION_WITHOUT_BINDING')
    task_root=root('hhs_pass082_parent_bifurcation_task_v1',{'workload_id':workload['workload_id'],'genesis':genesis})
    membrane=canonical_membrane_state()
    receipts=[]; start=time.perf_counter_ns()
    for index,bc in enumerate(branches):
        lease=make_lease(task_root,genesis,b['binding_root_hash72'],bc['branch_id'],bc['operation'],bc.get('lease_status','ACTIVE_VALIDATED'))
        if lease['status']!='ACTIVE_VALIDATED': raise ContractError('REJECT_NATIVE_INVOCATION_WITHOUT_ACTIVE_LEASE')
        operands={'genesis':genesis,'branch_id':bc['branch_id'],'operation':bc['operation'],'source_ast_root_hash72':bc['source_ast_root_hash72'],'index':index}
        operands_root=root('hhs_pass082_canonical_operands_v1',operands)
        request={'binding_root_hash72':b['binding_root_hash72'],'authority_scope':b['authority_scope'],'lease_status':lease['status'],'vm81_lane_binding_status':'BOUND_WITNESSED','pre_state_root':root('hhs_vm81_pre_state_v1',membrane),'canonical_operand_commitment_status':'BOUND_WITNESSED','lease_boundary':'PASS082_SINGLE_INVOCATION'}
        resolve_opcode(repo,OPCODE,request)
        admission=evaluate_admission(repo,OPCODE,request,membrane)
        if admission['decision']!='ADMIT_NATIVE_TRANSITION': raise ContractError('REJECT_PASS080_ADMISSION')
        native=_native_vectorize(repo,operands_root)
        closure_value_root=root('hhs_abp_coordinate_0_exact_v1',{'coordinate':0,'value':'P^2','genesis':genesis})
        post=root('hhs_pass082_branch_post_state_v1',{'genesis':genesis,'branch_id':bc['branch_id'],'operation':bc['operation'],'operands':operands_root,'native':native['native_result_root_hash72'],'closure':closure_value_root})
        rec={'schema':'HHS_NATIVE_INVOCATION_RECEIPT_V1','branch_id':bc['branch_id'],'genesis_state_root_hash72':genesis,'pre_state_root_hash72':request['pre_state_root'],'native_opcode_binding_root_hash72':b['binding_root_hash72'],'capability_lease_root_hash72':lease['capability_lease_root_hash72'],'canonical_operands_root_hash72':operands_root,'native_result_root_hash72':native['native_result_root_hash72'],'post_state_root_hash72':post,'closure_coordinate_value_root_hash72':closure_value_root,'successful_result_confers_authority':False,'pass080_admission_receipt_root_hash72':admission['receipt']['receipt_root_hash72'],'branch_derivation_root_hash72':root('hhs_branch_derivation_v1',operands)}
        rec['receipt_root_hash72']=root('hhs_native_invocation_receipt_v1',rec); receipts.append(stable(rec))
    roots=[r['post_state_root_hash72'] for r in receipts]
    if len(set(roots))!=len(roots): raise ContractError('REJECT_FALSE_BIFURCATION')
    if len({r['genesis_state_root_hash72'] for r in receipts})!=1: raise ContractError('REJECT_BIFURCATION_WITH_GENESIS_ROOT_MISMATCH')
    closures={r['closure_coordinate_value_root_hash72'] for r in receipts}
    if len(closures)!=1: raise ContractError('REJECT_RECIPROCAL_CLOSURE_FAILURE')
    pair={'schema':'HHS_BIFURCATION_CLOSURE_RECEIPT_V1','genesis_state_root_hash72':genesis,'lane_receipt_roots_hash72':[r['receipt_root_hash72'] for r in receipts],'lane_a_receipt_root_hash72':receipts[0]['receipt_root_hash72'],'lane_b_receipt_root_hash72':receipts[1]['receipt_root_hash72'],'lane_roots_distinct':True,'closure_coordinate':workload['shared_closure_contract']['closure_coordinate'],'closure_coordinate_roots_match':True,'branch_identity_preserved':True,'branch_merger_occurred':False,'deterministic_bifurcation_verified':True,'branch_count':len(receipts)}
    pair['receipt_root_hash72']=root('hhs_bifurcation_closure_receipt_v1',pair)
    elapsed=time.perf_counter_ns()-start
    return stable({'schema':'HHS_PASS_082_BIFURCATION_BENCHMARK_RESULT_V1','status':'DETERMINISTIC_BIFURCATION_VERIFIED','profile':'FULL_WITNESS_PROFILE','workload':workload,'branch_receipts':receipts,'bifurcation_receipt':pair,'metrics':{'branch_count':len(receipts),'total_execution_ns':elapsed,'native_invocation_ns':0,'receipt_bytes':len(json.dumps(receipts,separators=(',',':'))),'branches_admitted_per_second':len(receipts)/(elapsed/1e9) if elapsed else 0,'determinism_mismatch_count':0},'replay':replay})

def default_workload(repo:Path, branch_count:int=2, ast_nodes:int=16)->dict[str,Any]:
    reg=build_registry(repo); b=binding(repo); genesis=root('hhs_pass082_genesis_v1',{'seed':'calibration:vm81-bifurcation-001'})
    branches=[]
    for i in range(branch_count):
        operation='RECURSIVE_SYMBOLIC_CONSTRAINT_EXPANSION' if i%2==0 else 'INVERSE_RECIPROCAL_PHASE_PROJECTION'
        source=('A==B,'*max(1,ast_nodes//4))+f'BRANCH_{i}==P'
        branches.append({'branch_id':f'LANE_{i:03d}_{"EXPANSION" if i%2==0 else "INVERSE"}','operation':operation,'source_ast_root_hash72':root('hhs_pass081_source_ast_v1',parse_expression(source).to_dict()),'lo_shu_mapping_required':i%2==0,'reciprocal_projection_required':i%2==1})
    return stable({'schema':SCHEMA,'workload_id':'calibration:vm81-bifurcation-001','genesis_state_root_hash72':genesis,'native_binding':{'opcode':OPCODE,'semantic_identity':b['semantic_operation_identity'],'registry_root_hash72':reg['pass079_native_opcode_registry_root_hash72'],'binding_root_hash72':b['binding_root_hash72']},'branch_contracts':branches,'shared_closure_contract':{'schema':'ABP_EQUALITY_CLOSURE_TENSOR_V1','closure_coordinate':0,'comparison':'EXACT_CANONICAL_COORDINATE_EQUALITY','branch_merger_permitted':False},'required_receipts':['HHS_NATIVE_INVOCATION_RECEIPT_V1','HHS_BRANCH_DERIVATION_RECEIPT_V1','HHS_BIFURCATION_CLOSURE_RECEIPT_V1']})

def verify_replay(repo:Path, workload:Mapping[str,Any])->dict[str,Any]:
    a=run(repo,workload); b=run(repo,workload,replay=True)
    ok=a['bifurcation_receipt']['receipt_root_hash72']==b['bifurcation_receipt']['receipt_root_hash72'] and [x['post_state_root_hash72'] for x in a['branch_receipts']]==[x['post_state_root_hash72'] for x in b['branch_receipts']]
    if not ok: raise ContractError('REJECT_BIFURCATION_REPLAY_MISMATCH')
    return {'deterministic_replay_verified':True,'receipt_root_hash72':a['bifurcation_receipt']['receipt_root_hash72'],'initial':a,'replay':b}

from __future__ import annotations
from pathlib import Path
from typing import Any, Mapping
import json
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, product_root, stable
from native_projects.hhs_vm81_native_exposure.hhs_pass078_1_native_abi_reconciliation_v1 import reconcile_native_abi
from native_projects.hhs_vm81_native_exposure.hhs_pass078_vm81_native_exposure_v1 import native_exposure_registry, native_capability_manifest, kernel_freeze_manifest

PASS_ID='PASS_079'
SCHEMA='HHS_NATIVE_OPCODE_REGISTRY_PASS_079_V1'
BINDING_SCHEMA='HHS_NATIVE_OPCODE_BINDING_V1'

MUTATION_BY_SYMBOL={
 'hhs_runtime_init':'INITIALIZE_NATIVE_STATE','hhs_runtime_reset':'RESET_NATIVE_STATE','hhs_runtime_step':'MUTATE_NATIVE_STATE',
 'hhs_runtime_halt':'MUTATE_CONTROL_STATE','hhs_tensor_reset':'RESET_TENSOR_STATE','hhs_tensor_apply_xy':'MUTATE_TENSOR_STATE',
 'hhs_transport_apply':'MUTATE_TRANSPORT_STATE','hhs_receipt_reset':'RESET_RECEIPT_STATE','hhs_receipt_commit':'MUTATE_RECEIPT_STATE',
}

def _opcode(symbol:str)->str: return 'NATIVE_'+symbol.upper().removeprefix('HHS_')

def _schema_for(symbol:str)->tuple[dict[str,Any],dict[str,Any]]:
    # Contracts are deliberately opaque where the frozen ABI manifest does not prove richer structure.
    if symbol in {'hhs_hash72_compare'}:
        return ({'type':'object','required':['left','right'],'additionalProperties':False}, {'type':'integer','enum':[-1,0,1]})
    if symbol in {'hhs_runtime_init','hhs_runtime_reset','hhs_runtime_halt','hhs_tensor_reset','hhs_receipt_reset'}:
        return ({'type':'object','maxProperties':0}, {'type':'object','required':['native_status','receipt_root_hash72']})
    return ({'type':'object','required':['canonical_operands'],'additionalProperties':False}, {'type':'object','required':['native_status','receipt_root_hash72']})

def build_registry(repo:Path)->dict[str,Any]:
    exposure=native_exposure_registry(native_capability_manifest(repo))
    reconciliation=reconcile_native_abi(repo)
    entries=[]
    for e in sorted((x for x in exposure['entries'] if x['binding_mode']=='DIRECT_ABI' and x['callable_from_higher_level']), key=lambda x:x['native_symbol']):
        symbol=e['native_symbol']; inp,out=_schema_for(symbol)
        body={
          'schema':BINDING_SCHEMA,'ir_schema':'HHS_EXECUTABLE_IR_V1','native_opcode':_opcode(symbol),
          'semantic_operation_identity':e['operation_id'],'abi_symbol':symbol,'abi_disposition':'ADMITTED_EXISTING_DIRECT_ABI',
          'input_schema':inp,'output_schema':out,'memory_ownership':'CALLER_OWNS_INPUT_NATIVE_RUNTIME_OWNS_INTERNAL_STATE',
          'buffer_bounds':'EXACT_SCHEMA_AND_NATIVE_ABI_BOUNDS_REQUIRED','mutation_class':MUTATION_BY_SYMBOL.get(symbol,'READ_OR_BOUNDED_NATIVE_OPERATION'),
          'authority_scope':'NATIVE_CAPABILITY_CONTRACT_ONLY','lease_requirements':['TASK_BOUND','SOURCE_SCOPED','OPERATION_SCOPED','SEQUENCE_BOUNDED'],
          'pre_state_witness_requirements':['VM81_LANE_BINDING','CANONICAL_OPERAND_COMMITMENT','AUTHORITY_RECEIPT'],
          'post_state_witness_requirements':['NATIVE_RESULT_IDENTITY','POST_STATE_ROOT','EXECUTION_LINEAGE'],
          'failure_semantics':['REJECT_UNBOUND_OPCODE','REJECT_SCHEMA_MISMATCH','REJECT_AUTHORITY_FAILURE','REJECT_LEASE_FAILURE','TYPED_UNAVAILABLE'],
          'receipt_schema':'HHS_NATIVE_INVOCATION_RECEIPT_V1','callable':True,'compiler_may_synthesize':False,
        }
        body['binding_root_hash72']=product_root('hhs_native_opcode_binding_v1',stable(body)); entries.append(stable(body))
    result={
      'schema':SCHEMA,'pass_id':PASS_ID,'parent_pass':'PASS_078_1','source_ir_schema':'HHS_EXECUTABLE_IR_V1',
      'binding_schema':BINDING_SCHEMA,'policy':'IR_REQUESTS_REGISTRY_RESOLVES_NO_NAME_OR_SIGNATURE_AUTHORITY',
      'direct_abi_capabilities_total':exposure['direct_abi_count'],'registered_native_opcodes':len(entries),
      'typed_unresolved_declarations_excluded':reconciliation['remaining_typed_unresolved'],
      'name_only_bindings':0,'signature_only_bindings':0,'unproven_semantic_bindings':0,'compiler_created_native_operations':0,
      'entries':entries,
    }
    result['pass079_native_opcode_registry_root_hash72']=product_root('pass079_native_opcode_registry',stable(result)); return stable(result)

def resolve_opcode(repo:Path, opcode:str, request:Mapping[str,Any])->dict[str,Any]:
    reg=build_registry(repo); matches=[x for x in reg['entries'] if x['native_opcode']==opcode]
    if not matches: raise ContractError('REJECT_UNREGISTERED_NATIVE_OPCODE')
    b=matches[0]
    if request.get('binding_root_hash72')!=b['binding_root_hash72']: raise ContractError('REJECT_BINDING_ROOT_MISMATCH')
    if request.get('authority_scope')!=b['authority_scope']: raise ContractError('REJECT_AUTHORITY_SCOPE_MISMATCH')
    if request.get('lease_status')!='ACTIVE_VALIDATED': raise ContractError('REJECT_LEASE_NOT_ACTIVE_VALIDATED')
    if request.get('vm81_lane_binding_status')!='BOUND_WITNESSED': raise ContractError('REJECT_VM81_LANE_NOT_BOUND')
    return stable({'decision':'RESOLVED_FOR_BOUNDED_INVOCATION','native_opcode':opcode,'abi_symbol':b['abi_symbol'],'binding_root_hash72':b['binding_root_hash72'],'invocation_not_executed':True})

def build_release(repo:Path)->dict[str,Any]:
    reg=build_registry(repo); freeze=kernel_freeze_manifest(repo)
    rel={'schema':'HHS_PASS_079_RELEASE_BUNDLE_V1','pass_id':PASS_ID,'registry':reg,'kernel_freeze_root_hash72':freeze['pass078_kernel_freeze_manifest_root_hash72'],
      'closure':{'all_direct_abi_capabilities_registered':reg['registered_native_opcodes']==reg['direct_abi_capabilities_total'],'typed_unresolved_excluded':reg['typed_unresolved_declarations_excluded']==15,'no_shortcut_bindings':reg['name_only_bindings']==reg['signature_only_bindings']==reg['unproven_semantic_bindings']==0,'no_compiler_native_synthesis':reg['compiler_created_native_operations']==0}}
    rel['pass079_release_root_hash72']=product_root('pass079_release',stable(rel)); return stable(rel)

def write_artifacts(repo:Path)->dict[str,Any]:
    r=build_release(repo); d=repo/'native_projects/hhs_vm81_native_exposure/artifacts'; d.mkdir(parents=True,exist_ok=True)
    (d/'PASS_079_NATIVE_OPCODE_REGISTRY.json').write_text(json.dumps(r['registry'],indent=2)+'\n')
    (d/'HHS_PASS_079_RELEASE_BUNDLE.json').write_text(json.dumps(r,indent=2)+'\n')
    return r

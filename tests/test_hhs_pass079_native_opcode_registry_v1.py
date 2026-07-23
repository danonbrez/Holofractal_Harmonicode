from pathlib import Path
import pytest
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_vm81_native_exposure.hhs_pass079_native_opcode_registry_v1 import *
ROOT=Path(__file__).resolve().parents[1]
def test_all_direct_abi_capabilities_have_contract_bindings():
 r=build_registry(ROOT); assert r['registered_native_opcodes']==r['direct_abi_capabilities_total']==29
def test_typed_unresolved_declarations_are_not_bindable():
 r=build_registry(ROOT); assert r['typed_unresolved_declarations_excluded']==15; assert not any(x['abi_symbol'].startswith('hhs_vm_') for x in r['entries'])
def test_no_name_signature_or_unproven_shortcuts():
 r=build_registry(ROOT); assert r['name_only_bindings']==r['signature_only_bindings']==r['unproven_semantic_bindings']==0
def test_every_binding_has_full_contract_and_root():
 req={'input_schema','output_schema','memory_ownership','buffer_bounds','mutation_class','authority_scope','lease_requirements','pre_state_witness_requirements','post_state_witness_requirements','failure_semantics','receipt_schema','binding_root_hash72'}
 assert all(req <= set(x) for x in build_registry(ROOT)['entries'])
def test_resolver_requires_binding_authority_lease_and_lane():
 b=build_registry(ROOT)['entries'][0]
 good={'binding_root_hash72':b['binding_root_hash72'],'authority_scope':b['authority_scope'],'lease_status':'ACTIVE_VALIDATED','vm81_lane_binding_status':'BOUND_WITNESSED'}
 assert resolve_opcode(ROOT,b['native_opcode'],good)['decision']=='RESOLVED_FOR_BOUNDED_INVOCATION'
 for k,v in [('binding_root_hash72','bad'),('authority_scope','bad'),('lease_status','bad'),('vm81_lane_binding_status','bad')]:
  q=dict(good); q[k]=v
  with pytest.raises(ContractError): resolve_opcode(ROOT,b['native_opcode'],q)
def test_unregistered_opcode_rejected():
 with pytest.raises(ContractError): resolve_opcode(ROOT,'GATE_INVOKE',{})
def test_compiler_cannot_synthesize_native_operations(): assert build_registry(ROOT)['compiler_created_native_operations']==0
def test_deterministic_release(): assert build_release(ROOT)==build_release(ROOT)

from pathlib import Path
import pytest
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, product_root, stable
from native_projects.hhs_vm81_native_exposure.hhs_pass079_native_opcode_registry_v1 import build_registry
from native_projects.hhs_vm81_native_exposure.hhs_pass080_constraint_membrane_v1 import *
ROOT=Path(__file__).resolve().parents[1]

def good_request(state=None):
 state=state or canonical_membrane_state(); b=build_registry(ROOT)['entries'][0]
 return b['native_opcode'], {'binding_root_hash72':b['binding_root_hash72'],'authority_scope':b['authority_scope'],'lease_status':'ACTIVE_VALIDATED','vm81_lane_binding_status':'BOUND_WITNESSED','pre_state_root':product_root('hhs_vm81_pre_state_v1',stable(state)),'canonical_operand_commitment_status':'BOUND_WITNESSED','lease_boundary':'SEQUENCE_1'}

def test_all_29_opcode_contracts_have_membrane_rules():
 r=build_opcode_membrane_contracts(ROOT); assert r['registered_native_opcode_contracts']==r['opcode_contracts_with_membrane_rules']==29

def test_valid_pass079_resolution_can_be_rejected_by_membrane():
 s=canonical_membrane_state({'A':2}); op,q=good_request(s); d=evaluate_admission(ROOT,op,q,s); assert d['decision']=='REJECT_NATIVE_TRANSITION_WITH_RECEIPT'; assert not d['native_execution_occurred']

def test_unregistered_operation_never_reaches_membrane():
 with pytest.raises(ContractError): evaluate_admission(ROOT,'NATIVE_FAKE',{},canonical_membrane_state())

def test_binding_lease_and_lane_still_enforced_by_pass079():
 s=canonical_membrane_state(); op,q=good_request(s)
 for k in ['binding_root_hash72','lease_status','vm81_lane_binding_status']:
  z=dict(q); z[k]='BAD'
  with pytest.raises(ContractError): evaluate_admission(ROOT,op,z,s)

def test_stale_prestate_is_indeterminate_with_receipt():
 s=canonical_membrane_state(); op,q=good_request(s); q['pre_state_root']='stale'; d=evaluate_admission(ROOT,op,q,s); assert d['decision']=='INDETERMINATE_REQUIRES_REVALIDATION'; assert d['receipt']['receipt_root_hash72']

def test_unresolved_abi_dependency_is_typed_unavailable_never_zero():
 s=canonical_membrane_state(); op,q=good_request(s); q['required_abi_dependency_status']='TYPED_UNAVAILABLE'; d=evaluate_admission(ROOT,op,q,s); assert d['decision']=='TYPED_UNAVAILABLE'; assert 'NEVER_ZERO' in d['receipt']['reason']

def test_zero_denominator_rejects_before_arithmetic():
 s=canonical_membrane_state({'A':0}); op,q=good_request(s); d=evaluate_admission(ROOT,op,q,s); assert d['decision']=='REJECT_NATIVE_TRANSITION_WITH_RECEIPT'

def test_primary_equality_and_ordered_lineage_are_preserved():
 s=canonical_membrane_state(); op,q=good_request(s); d=evaluate_admission(ROOT,op,q,s); ids=[e['relation_id'] for e in d['receipt']['evaluations']]; assert 'P080_ORDERED_AB_P4' in ids and 'P080_ORDERED_BA_P4' in ids; assert s['ordered_ab_lineage_root']!=s['ordered_ba_lineage_root']

def test_polynomial_pq_n4_xy_chain_enforced():
 s=canonical_membrane_state({'n':2}); op,q=good_request(s); d=evaluate_admission(ROOT,op,q,s); assert d['decision']=='REJECT_NATIVE_TRANSITION_WITH_RECEIPT'; assert d['receipt']['reason'] in {'REJECT_PQ_N4_GATE','REJECT_N4_XY_GATE'}

def test_lo_shu_nine_cells_rows_columns_diagonals():
 s=canonical_membrane_state(); op,q=good_request(s); d=evaluate_admission(ROOT,op,q,s); assert d['decision']=='ADMIT_NATIVE_TRANSITION'; ids={e['relation_id'] for e in d['receipt']['evaluations']}; assert {'P080_LO_SHU_9_CELL','P080_LO_SHU_ROWS','P080_LO_SHU_COLUMNS','P080_LO_SHU_DIAGONALS'}<=ids

def test_seven_cell_and_orientation_gates():
 for patch,reason in [({'seven_cell_residue':1},'REJECT_SEVEN_CELL_GATE'),({'orientation_residue_mod72':1},'REJECT_ORIENTATION_NOT_CLOSED')]:
  s=canonical_membrane_state(patch); op,q=good_request(s); d=evaluate_admission(ROOT,op,q,s); assert d['receipt']['reason']==reason

def test_qgu_exact_cross_multiplication_gate():
 s=canonical_membrane_state({'qgu_cross_product_residue':'1/3'}); op,q=good_request(s); d=evaluate_admission(ROOT,op,q,s); assert d['receipt']['reason']=='REJECT_QGU_RATIONAL_GATE'

def test_no_native_execution_or_mutation_during_admission():
 s=canonical_membrane_state(); op,q=good_request(s); d=evaluate_admission(ROOT,op,q,s); assert d['terminal_status']=='ADMITTED_FOR_LEASED_NATIVE_INVOCATION'; assert d['native_execution_occurred'] is False and d['native_state_mutated'] is False

def test_every_rejection_has_deterministic_receipt():
 s=canonical_membrane_state({'wave_denominator':0}); op,q=good_request(s); a=evaluate_admission(ROOT,op,q,s); b=evaluate_admission(ROOT,op,q,s); assert a==b and a['receipt']['receipt_root_hash72']

def test_no_float_authority_or_opaque_formula_paths():
 r=build_release(ROOT); assert r['metrics']['floating_point_authority_paths']==0; assert r['metrics']['opaque_formula_dispatch_paths']==0; assert all(x['exact_evaluation_type']=='INTEGER_OR_BIGINT_RATIONAL_NO_FLOAT_AUTHORITY' for x in r['opcode_membrane_contracts']['relation_graph']['relations'])

def test_release_metrics_close_exactly():
 m=build_release(ROOT)['metrics']; assert m['registered_native_opcode_contracts']==m['opcode_contracts_with_membrane_rules']==29; assert m['native_executions_during_pass080_resolution']==m['unwitnessed_rejections']==m['typed_unavailable_collapsed_to_zero']==m['constraint_relations_without_provenance']==0

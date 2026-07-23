from pathlib import Path
from native_projects.hhs_bifurcation_calibration.hhs_pass096_language_translation_calibration_v1 import *
R=Path(__file__).resolve().parents[1]
def test_pass095_inputs_committed():
 i=load_pass095_inputs(R); assert i['manifest']['pass_id']=='PASS_095' and i['input_commitment_root_hash72']
def test_six_registers_and_matrix(): assert len(REGISTERS)==6 and len(translation_matrix())==14
def test_temperature_and_window_ladders(): assert len(TEMPERATURES)==7 and len(WINDOWS)>=6
def test_source_identity_and_order_preserved():
 s=source_objects(R)[1]; x=translate(s,'ACADEMIC_STEM'); assert x['invariant_snapshot']['operator_order']==['A','B'] and not x['authority_conferred_by_language']
def test_metaphor_has_reconstruction_map():
 x=translate(source_objects(R)[0],'MYTHOPOETIC'); assert x['reconstruction_map'] and x['final_status']=='METAPHORIC_SURVIVAL_WITH_RECONSTRUCTION'
def test_causal_reverse_not_logical_inverse():
 d={'representation_reversal_is_causal_reversal':False,'reverse_operation':'INFER_CANDIDATE_ANTECEDENTS'}; assert not d['representation_reversal_is_causal_reversal']
def test_pattern_aware_ab_not_worse(): assert all(x['b_not_worse'] for x in run(R)['pattern_aware_ab'])
def test_recursive_cycles_replay_without_drift(): assert not recursive_cycle(source_objects(R)[0],10)['recursive_translation_drift']
def test_workloads_w96_01_to_16():
 w=workloads(); assert len(w)==16 and w[0]['workload_id']=='W96-01' and w[-1]['workload_id']=='W96-16'
def test_negative_cases(): assert all(x['passed'] for x in negative_cases(R))
def test_exact_replay(): assert verify_replay(R)['deterministic_replay_verified']

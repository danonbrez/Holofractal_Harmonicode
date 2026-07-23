from pathlib import Path
from native_projects.hhs_bifurcation_calibration.hhs_pass097_minimal_constraint_kernel_v1 import *
R=Path(__file__).resolve().parents[1]
def test_pass096_inputs_committed(): assert load_pass096_inputs(R)['manifest']['pass_id']=='PASS_096'
def test_six_minimality_levels(): assert len(LEVELS)==6 and permanent_seed('L5_KERNEL_ONLY')['symbol_count']==0
def test_relation_and_epistemic_basis(): assert len(RELATIONS)==12 and len(EPISTEMIC)==7 and len(AUTHORITY)==6
def test_workloads_w97_01_to_12():
 w=workloads(); assert len(w)==12 and w[0]['workload_id']=='W97-01' and w[-1]['workload_id']=='W97-12'
def test_minimal_linguistic_boundary():
 r=run(R); assert r['minimum_general_linguistic_level']=='L3_MINIMAL_GRAMMAR_RELATIONS' and r['minimum_orientation_level']=='L4_KERNEL_AUTHORITY_RECONSTRUCTION'
def test_kernel_only_has_no_language_capability(): assert evaluate('L5_KERNEL_ONLY',workloads()[1])['status']=='UNAVAILABLE'
def test_missing_knowledge_is_retrieval_not_guess():
 x=evaluate('L3_MINIMAL_GRAMMAR_RELATIONS',workloads()[9]); assert x['missing_knowledge_recognized'] and x['external_sources_used']
def test_ambiguity_and_provenance_preserved_at_l3():
 x=evaluate('L3_MINIMAL_GRAMMAR_RELATIONS',workloads()[4]); assert x['ambiguity_preserved'] and x['provenance_preserved']
def test_constraint_ablations(): assert len(ablations())==10 and sum(x['essential'] for x in ablations())==9
def test_negative_cases(): assert all(x['passed'] for x in negative_cases(R))
def test_exact_replay(): assert verify_replay(R)['deterministic_replay_verified']

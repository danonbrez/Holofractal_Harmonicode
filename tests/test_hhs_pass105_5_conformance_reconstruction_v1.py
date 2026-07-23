from pathlib import Path
from hhs_runtime.hhs_pass105_5_conformance_reconstruction_v1 import reconstruct_conformance, pass105_5_self_test

def test_reconstructs_pass_001_105_live_evidence():
    r=reconstruct_conformance()
    assert r['status']=='PASS'
    assert r['pass_001_105_coverage_complete'] is True
    assert r['python_static_parse']['python_parse_failed']==0

def test_prior_bounded_repairs_are_live_not_manifest_only():
    r=reconstruct_conformance()
    for p in ('PASS_105_1','PASS_105_2','PASS_105_3','PASS_105_4'):
        rr=r['repair_results'][p]
        assert rr.get('status')=='PASS' or (p=='PASS_105_1' and rr['serialization_reparse_exact'] and rr['template_parameters_preserved'])
    assert r['closed_repair_obligation_count']>=8

def test_compiler_obligation_closes_only_after_real_backend_execution():
    r=reconstruct_conformance()
    assert 'HHS-AUDIT-008' not in r['open_repair_obligation_ids']
    obligation=next(x for x in r['repair_obligations'] if x['issue_id']=='HHS-AUDIT-008')
    assert obligation['status']=='CLOSED_REPAIRED'
    assert r['repair_results']['PASS_105_6']['real_compilation_executed'] is True
    assert r['repair_results']['PASS_105_6']['real_generated_binaries_executed'] is True

def test_self_test_is_callable_and_rooted():
    r=pass105_5_self_test()
    assert r['status']=='PASS'
    assert r['reconstruction_complete'] is True
    assert r['conformance_reconstruction_root_hash72']

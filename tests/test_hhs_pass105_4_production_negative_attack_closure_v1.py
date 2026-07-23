from hhs_runtime.hhs_pass105_4_production_negative_attack_closure_v1 import execute_all_negative_attacks, pass105_4_self_test
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry


def test_all_77_negative_claims_execute_real_malformed_workloads():
    result=execute_all_negative_attacks()
    assert result['status']=='PASS'
    assert result['attack_count']==77
    assert result['passed_count']==77
    assert result['failed_count']==0


def test_negative_evidence_has_no_parallel_test_logic_or_mocks():
    result=execute_all_negative_attacks()
    assert result['all_attacks_structurally_executed'] is True
    assert result['all_attacks_used_production_entrypoints'] is True
    assert result['parallel_test_computation_count']==0
    assert result['mock_component_count']==0


def test_each_pass_group_is_complete():
    result=execute_all_negative_attacks()
    counts={g['pass_id']:g['attack_count'] for g in result['groups']}
    assert counts=={'PASS_101':14,'PASS_102':14,'PASS_103':14,'PASS_104':16,'PASS_105':19}
    assert all(g['passed_count']==g['attack_count'] for g in result['groups'])


def test_service_registry_exposes_guarded_pass105_4_surface():
    registry=make_default_service_registry()
    service=next(s for s in registry.services() if s['name']=='runtime.production_negative_attack_closure.pass105_4')
    assert service['conformance_decision']['derivation_complete'] is True
    interposition=registry.interpose_dispatch('runtime.production_negative_attack_closure.pass105_4')
    record=registry.dispatch('runtime.production_negative_attack_closure.pass105_4',zero_bypass_interposition_token=interposition['interposition_token'])
    result=record['result']
    assert result['status']=='PASS'
    assert result['attack_count']==77


def test_self_test_reports_complete_closure():
    result=pass105_4_self_test()
    assert result['all_repairs_verified'] is True

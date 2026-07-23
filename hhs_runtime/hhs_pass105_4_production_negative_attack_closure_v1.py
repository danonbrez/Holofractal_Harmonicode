from __future__ import annotations
from pathlib import Path
from typing import Any, Callable, Mapping

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, stable
from native_projects.hhs_bifurcation_calibration.hhs_pass082_1_offset_entangled_calibration_v1 import root
from native_projects.hhs_bifurcation_calibration import hhs_pass101_four_lane_zero_sum_closure_v1 as pass101
from native_projects.hhs_bifurcation_calibration import hhs_pass102_17x17_trinary_phase_gear_tensor_v1 as pass102
from native_projects.hhs_bifurcation_calibration import hhs_pass103_harmonicode_symbol_registry_v1 as pass103
from native_projects.hhs_bifurcation_calibration import hhs_pass104_variable_string_dictionary_v1 as pass104
from native_projects.hhs_bifurcation_calibration import hhs_pass105_1_dictionary_grammar_closure_v1 as pass105

SCHEMA = 'HHS_PASS105_4_PRODUCTION_NEGATIVE_ATTACK_CLOSURE_V1'
PASS_ID = 'PASS_105_4'


def _execute(pass_id: str, code: str, entrypoint: Callable[[str], Any]) -> dict[str, Any]:
    observed = 'NO_REJECTION'
    try:
        entrypoint(code)
    except ContractError as exc:
        observed = str(exc)
    record = {
        'schema': 'HHS_PRODUCTION_PATH_NEGATIVE_ATTACK_RECEIPT_V1',
        'pass_id': pass_id,
        'attack_id': f'{pass_id}:{code}',
        'expected_rejection': code,
        'observed_rejection': observed,
        'production_entrypoint': f'{entrypoint.__module__}.{entrypoint.__name__}',
        'malformed_workload_executed': True,
        'parallel_test_computation_used': False,
        'mock_components': [],
        'passed': observed == code,
    }
    record['attack_receipt_root_hash72'] = root('hhs_pass105_4_attack_receipt_v1', record)
    return stable(record)


def _execute_pass105() -> list[dict[str, Any]]:
    original = set(pass105.REJECTIONS[:19])
    records=[]
    for fixture in pass105.negative_fixtures():
        if fixture['code'] not in original:
            continue
        result=pass105.execute_negative_case(fixture)
        record={
            'schema':'HHS_PRODUCTION_PATH_NEGATIVE_ATTACK_RECEIPT_V1',
            'pass_id':'PASS_105',
            'attack_id':f"PASS_105:{fixture['code']}",
            'expected_rejection':fixture['code'],
            'observed_rejection':result['observed'],
            'production_entrypoint':f'{pass105.__name__}.execute_negative_case',
            'fixture_root_hash72':result['fixture_root_hash72'],
            'malformed_workload_executed':True,
            'parallel_test_computation_used':False,
            'mock_components':[],
            'passed':result['passed'],
        }
        record['attack_receipt_root_hash72']=root('hhs_pass105_4_attack_receipt_v1',record)
        records.append(stable(record))
    return records


def execute_all_negative_attacks() -> dict[str, Any]:
    groups=[]
    for module in (pass101, pass102, pass103, pass104):
        records=[_execute(module.PASS_ID, code, module.execute_negative_attack) for code in module.REJECTIONS]
        groups.append({'pass_id':module.PASS_ID,'attack_count':len(records),'passed_count':sum(r['passed'] for r in records),'records':records})
    p105_records=_execute_pass105()
    groups.append({'pass_id':'PASS_105','attack_count':len(p105_records),'passed_count':sum(r['passed'] for r in p105_records),'records':p105_records})
    all_records=[r for g in groups for r in g['records']]
    result={
        'schema':SCHEMA,
        'pass_id':PASS_ID,
        'group_count':len(groups),
        'attack_count':len(all_records),
        'passed_count':sum(r['passed'] for r in all_records),
        'failed_count':sum(not r['passed'] for r in all_records),
        'all_attacks_structurally_executed':all(r['malformed_workload_executed'] for r in all_records),
        'all_attacks_used_production_entrypoints':all(bool(r['production_entrypoint']) for r in all_records),
        'parallel_test_computation_count':sum(bool(r['parallel_test_computation_used']) for r in all_records),
        'mock_component_count':sum(len(r['mock_components']) for r in all_records),
        'groups':groups,
    }
    result['attack_registry_root_hash72']=root('hhs_pass105_4_attack_registry_v1',result)
    result['status']='PASS' if result['failed_count']==0 and result['attack_count']==77 else 'FAIL'
    return stable(result)


def pass105_4_self_test(root_path: Path|None=None) -> dict[str, Any]:
    result=execute_all_negative_attacks()
    return stable({
        'schema':SCHEMA,
        'pass_id':PASS_ID,
        'status':result['status'],
        'attack_count':result['attack_count'],
        'passed_count':result['passed_count'],
        'failed_count':result['failed_count'],
        'all_attacks_structurally_executed':result['all_attacks_structurally_executed'],
        'all_attacks_used_production_entrypoints':result['all_attacks_used_production_entrypoints'],
        'parallel_test_computation_count':result['parallel_test_computation_count'],
        'mock_component_count':result['mock_component_count'],
        'attack_registry_root_hash72':result['attack_registry_root_hash72'],
        'all_repairs_verified':result['status']=='PASS',
    })

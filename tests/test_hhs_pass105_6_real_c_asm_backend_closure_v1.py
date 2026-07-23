from hhs_runtime.hhs_ir_transpiler_v1 import TranspileStatus, transpile_manifest, compile_and_execute_artifact
from hhs_runtime.hhs_pass105_6_real_c_asm_backend_closure_v1 import pass105_6_self_test

def fixture():
    return {'manifest':{'phases':[4,12,20,36],'equation_text':'x','equation_hash72':'EQ','manifest_hash72':'MAN'}}

def test_c_backend_is_generated_compiles_and_executes():
    a=transpile_manifest(fixture(),['c']).artifacts[0]
    assert a.status is TranspileStatus.GENERATED
    assert 'stub' not in a.notes[0].lower()
    r=compile_and_execute_artifact(a)
    assert r['observed']['phase_sum']==72 and r['observed']['target']=='c'

def test_asm_backend_is_generated_links_and_executes():
    a=transpile_manifest(fixture(),['asm']).artifacts[0]
    assert a.status is TranspileStatus.GENERATED
    assert 'hhs_phase_sum' in a.source
    r=compile_and_execute_artifact(a)
    assert r['observed']['phase_sum']==72 and r['observed']['target']=='asm'

def test_pass105_6_real_workload_closes_obligation():
    r=pass105_6_self_test()
    assert r['status']=='PASS'
    assert r['real_compilation_executed'] and r['real_generated_binaries_executed']
    assert r['parallel_test_computation_used'] is False

def test_service_registry_exposes_conformance_derived_pass105_6():
    from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
    registry=make_default_service_registry()
    service=next(x for x in registry.services() if x['name']=='runtime.real_c_asm_backend_closure.pass105_6')
    assert service['conformance_decision']['derivation_complete'] is True

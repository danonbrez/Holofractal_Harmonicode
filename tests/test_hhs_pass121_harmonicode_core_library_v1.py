from copy import deepcopy
import pytest

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass121_harmonicode_core_library_v1 import HarmonicodeCoreLibrary, Pass121Error, pass121_self_test


def lit(v): return {"node":"literal","kind":"RATIONAL","value":v}
def call(op,*args): return {"node":"call","op":op,"args":list(args)}
def auth(): return _hash("pass121_test_auth","ok")


def test_native_interpretation_uses_pass118_runtime():
    c=HarmonicodeCoreLibrary(); r=c.interpret(call("add",lit("1/3"),lit("2/3")),authority_root_hash72=auth())
    assert r["execution_status"] == "NATIVE_HARMONICODE_INTERPRETATION_VALIDATED"
    assert r["python_used_for_validation"] is False

def test_core_spec_has_native_surfaces_and_exact_relations():
    c=HarmonicodeCoreLibrary(); assert "b^2=2" in c.spec["defining_relations"]
    assert all(x["native_surface"] for x in c.spec["opcodes"])

def test_unknown_opcode_rejected_before_execution():
    c=HarmonicodeCoreLibrary()
    with pytest.raises(Pass121Error) as z: c.interpret(call("fictional",lit("1")),authority_root_hash72=auth())
    assert z.value.code == "REJECT_UNKNOWN_CORE_OPCODE"

def test_closed_operation_and_one_way_python_export():
    c=HarmonicodeCoreLibrary(); i=c.interpret(call("multiply",lit("6"),lit("7")),authority_root_hash72=auth())
    closed=c.close_operation(i); e=c.export_python(closed,module_name="answer")
    assert e["authority"] == "NONAUTHORITATIVE_ONE_WAY_EGRESS"
    assert e["python_validation_permitted"] is False
    assert "return CANONICAL_RESULT" in e["source"]

def test_open_symbol_cannot_be_exported():
    c=HarmonicodeCoreLibrary(); fake={"execution_status":"NATIVE_HARMONICODE_INTERPRETATION_VALIDATED","core_spec_root_hash72":c.spec["core_spec_root_hash72"],"interpretation_root_hash72":"x","runtime_result_root_hash72":"y","expression":{"node":"symbol","name":"x"},"canonical_result":None}
    with pytest.raises(Pass121Error) as z: c.close_operation(fake)
    assert z.value.code == "REJECT_OPEN_SYMBOL_EXPORT"

def test_mutated_closed_operation_rejected():
    c=HarmonicodeCoreLibrary(); i=c.interpret(call("add",lit("1"),lit("2")),authority_root_hash72=auth()); closed=c.close_operation(i)
    bad=deepcopy(closed); bad["canonical_result"]={"tampered":True}
    with pytest.raises(Pass121Error) as z: c.export_python(bad)
    assert z.value.code == "REJECT_MUTATED_CLOSED_OPERATION"

def test_export_source_tamper_rejected():
    c=HarmonicodeCoreLibrary(); i=c.interpret(call("add",lit("1"),lit("2")),authority_root_hash72=auth()); closed=c.close_operation(i); e=c.export_python(closed)
    bad=deepcopy(e); bad["source"] += "\n# tamper"
    with pytest.raises(Pass121Error) as z: c.validate_export(bad,closed)
    assert z.value.code == "REJECT_EXPORT_SOURCE_ROOT_MISMATCH"

def test_python_validator_flag_escalation_rejected():
    c=HarmonicodeCoreLibrary(); i=c.interpret(call("add",lit("1"),lit("2")),authority_root_hash72=auth()); closed=c.close_operation(i); e=c.export_python(closed)
    bad=deepcopy(e); bad["python_validation_permitted"]=True
    with pytest.raises(Pass121Error) as z: c.validate_export(bad,closed)
    assert z.value.code == "REJECT_PYTHON_AS_RUNTIME_VALIDATOR"

def test_export_validation_preserves_authority_boundary():
    c=HarmonicodeCoreLibrary(); i=c.interpret(call("add",lit("4"),lit("5")),authority_root_hash72=auth()); closed=c.close_operation(i); e=c.export_python(closed); r=c.validate_export(e,closed)
    assert r["runtime_authority_transferred"] is False
    assert r["python_executed_for_validation"] is False

def test_self_test(): assert pass121_self_test()["ok"] is True

def test_registry():
    from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
    svc=next(x for x in make_default_service_registry().services() if x["name"]=="runtime.harmonicode_core_library.pass121")
    assert svc["conformance_decision"]["derivation_complete"] is True

from copy import deepcopy
from fractions import Fraction
import pytest

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass120_self_solving_scientific_calculator_v1 import (
    Pass120Error, SelfSolvingScientificCalculator, UnitQuantity, pass120_self_test
)


def eng(): return SelfSolvingScientificCalculator()
def auth(): return _hash("pass120_test_auth", "ok")

def lit(kind, value): return {"node":"literal","kind":kind,"value":value}
def call(op,*args): return {"node":"call","op":op,"args":list(args)}


def test_exact_runtime_arithmetic_and_proof():
    e=eng(); req=e.create_request(operation="EVALUATE",expression=call("add",lit("RATIONAL","1/3"),lit("RATIONAL","2/3")))
    r=e.solve(req,authority_root_hash72=auth())
    assert r["canonical_result"] == {"kind":"RATIONAL","numerator":1,"denominator":1}
    assert r["proof_validation"]["proof_status"] == "FORMAL_PROOF_VALIDATED"

def test_float_rejected():
    e=eng(); req=e.create_request(operation="EVALUATE",expression=lit("RATIONAL",0.5))
    with pytest.raises((Pass120Error, Exception)):
        e.solve(req,authority_root_hash72=auth())

def test_linear_solver_and_substitution():
    e=eng(); req=e.create_request(operation="SOLVE",expression={"node":"polynomial_equation","degree":1,"variable":"x","coefficients":[2,-6],"right":0})
    r=e.solve(req,authority_root_hash72=auth())
    assert r["canonical_result"] == [{"kind":"RATIONAL","numerator":3,"denominator":1}]

def test_quadratic_solver():
    e=eng(); req=e.create_request(operation="SOLVE",expression={"node":"polynomial_equation","degree":2,"variable":"x","coefficients":[1,-5,6],"right":0})
    r=e.solve(req,authority_root_hash72=auth())
    assert r["canonical_result"] == [{"kind":"RATIONAL","numerator":3,"denominator":1},{"kind":"RATIONAL","numerator":2,"denominator":1}]

def test_exact_symbolic_b_quadratic_roots():
    e=eng(); req=e.create_request(operation="SOLVE",domain="HARMONICODE_Q_B_I",expression={"node":"polynomial_equation","degree":2,"variable":"x","coefficients":[1,0,-2],"right":0})
    r=e.solve(req,authority_root_hash72=auth())
    assert len(r["canonical_result"]) == 2
    assert all(x["kind"] == "HARMONICODE_Q_B_I" for x in r["canonical_result"])

def test_false_identity_counterexample():
    e=eng(); req=e.create_request(operation="DISPROVE",expression={"node":"identity_claim","claim":"(a+b)^2=a^2+b^2"})
    r=e.solve(req,authority_root_hash72=auth())
    assert r["result_status"] == "CLAIM_DISPROVEN_BY_COUNTEREXAMPLE"

def test_unit_dimension_addition():
    e=eng(); a=UnitQuantity.make(3,{"L":1}); b=UnitQuantity.make(5,{"L":1})
    assert e.calculate_units("add",a,b).value == 8

def test_unit_dimension_mismatch_rejected():
    e=eng(); a=UnitQuantity.make(3,{"L":1}); b=UnitQuantity.make(5,{"T":1})
    with pytest.raises(Pass120Error) as z: e.calculate_units("add",a,b)
    assert z.value.code == "REJECT_DIMENSIONALLY_INVALID_UNIT_OPERATION"

def test_proof_corruption_rejected():
    e=eng(); req=e.create_request(operation="SOLVE",expression={"node":"polynomial_equation","degree":1,"variable":"x","coefficients":[2,-6],"right":0})
    r=e.solve(req,authority_root_hash72=auth()); p=deepcopy(r["formal_proof"]); p["steps"][0]["output"]={"tampered":True}
    with pytest.raises(Pass120Error) as z: e.verify_proof(p,r["canonical_result"])
    assert z.value.code == "REJECT_PROOF_STEP_SIDE_CONDITION_FAILURE"

def test_replay_is_deterministic():
    e=eng(); req=e.create_request(operation="SOLVE",expression={"node":"polynomial_equation","degree":2,"variable":"x","coefficients":[1,-5,6],"right":0})
    r=e.solve(req,authority_root_hash72=auth())
    assert e.replay(r,req,authority_root_hash72=auth())["replay_status"] == "CALCULATOR_REPLAY_VALIDATED"

def test_unsupported_degree_typed_rejection():
    e=eng(); req=e.create_request(operation="SOLVE",expression={"node":"polynomial_equation","degree":3,"variable":"x","coefficients":[1,0,0,-1],"right":0})
    with pytest.raises(Pass120Error) as z: e.solve(req,authority_root_hash72=auth())
    assert z.value.code == "REJECT_SOLVER_WITHOUT_RUNTIME_IMPLEMENTATION"

def test_self_test():
    assert pass120_self_test()["ok"] is True

def test_registry():
    from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
    svc=next(x for x in make_default_service_registry().services() if x["name"]=="runtime.self_solving_scientific_calculator.pass120")
    assert svc["conformance_decision"]["derivation_complete"] is True

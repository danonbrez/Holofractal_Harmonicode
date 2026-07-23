import copy
import pytest
from hhs_runtime.harmonicode_architect_ouroboros_v1 import Architect, ArchitectError

SEED={"request_id":"seed","agent":"GARU","assignments":{"g":"5/4","h":"4/5","rho":"1/20","xy":1},"constraints":[{"id":"r","lhs":"g*h","rhs":"xy"}],"goals":[{"id":"bad","lhs":"rho*g","rhs":"0"}]}

def run(patches=(), max_cycles=None):
    p={"request_id":"arch","seed_request":copy.deepcopy(SEED),"candidate_patches":list(patches)}
    if max_cycles is not None:p["max_cycles"]=max_cycles
    return Architect().execute(p)

def test_commits_proved_improvement_and_authorizes_release():
    r=run([{"goals":[{"id":"fixed","lhs":"rho*g","rhs":"(g-xy)**2"}]}])
    assert r["conclusion"]=="RELEASE_PROVED" and r["selected_cycle"]==1
    assert r["cycles"][1]["decision"]=="COMMIT_IMPROVEMENT"
    assert Architect().validate_receipt(r)["valid"]

def test_failed_candidate_rolls_back():
    r=run([{"assignments":{"g":0}}])
    assert r["selected_cycle"]==0
    assert r["cycles"][1]["decision"]=="ROLLBACK_NO_PROVED_IMPROVEMENT"

def test_unproved_candidate_cannot_be_narratively_promoted():
    r=run([{"goals":[{"id":"stillbad","lhs":"1","rhs":"2"}]}])
    assert not r["release_authorized"] and r["conclusion"]=="NO_PROVED_RELEASE"

def test_ouroboros_revisited_state_closes():
    r=run([{}, {}], max_cycles=3)
    assert r["ouroboros"]["closure"]=="OUROBOROS_CLOSED"
    assert r["cycles"][1]["status"]=="OUROBOROS_STATE_REVISITED"

def test_receipt_mutation_detected():
    r=run([]); r["selected_cycle"]=99
    assert not Architect().validate_receipt(r)["valid"]

def test_cycle_bound_enforced():
    with pytest.raises(ArchitectError):
        Architect().execute({"request_id":"x","seed_request":SEED,"candidate_patches":[],"max_cycles":82})

def test_patch_scope_rejected():
    with pytest.raises(ArchitectError): run([{"authority":"self-promote"}])

def test_deterministic_replay():
    a=run([{"goals":[{"id":"fixed","lhs":"rho*g","rhs":"(g-xy)**2"}]}])
    b=run([{"goals":[{"id":"fixed","lhs":"rho*g","rhs":"(g-xy)**2"}]}])
    assert a==b

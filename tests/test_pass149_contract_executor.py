import pytest
from hhs_runtime.pass149 import Obligation, ObligationLedger, EqualityMembrane, ProjectionState

def test_obligation_ledger_preserves_and_orders():
    x=ObligationLedger([Obligation("a","keep all",1),Obligation("b","higher",2)])
    assert [i.obligation_id for i in x.active()]==["b","a"] and len(x.digest())==64

def test_coverage_requires_all_active():
    x=ObligationLedger([Obligation("a","x",1),Obligation("b","y",1)])
    assert not x.coverage({"a":1}) and x.coverage({"a":1,"b":2})

def test_simultaneous_projection():
    m=EqualityMembrane([lambda s:{"x":s["a"]+1}, lambda s:{"y":s["a"]+2}])
    out=m.project(ProjectionState({"a":4}))
    assert out.values=={"a":4,"x":5,"y":6} and out.generation==1

def test_conflict_is_explicit():
    m=EqualityMembrane([lambda s:{"x":1},lambda s:{"x":2}])
    with pytest.raises(ValueError): m.project(ProjectionState({}))

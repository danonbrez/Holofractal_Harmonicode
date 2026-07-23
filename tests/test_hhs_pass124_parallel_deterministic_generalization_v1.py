from copy import deepcopy
from fractions import Fraction
import pytest

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass124_parallel_deterministic_generalization_v1 import (
    ParallelDeterministicGeneralizationEngine, ParallelGeneralizationBounds, Pass124Error,
    _validator, pass124_self_test,
)


def build():
    e=ParallelDeterministicGeneralizationEngine()
    cs=[e.make_candidate(candidate_id=f"c{i}",semantic_root_hash72=_hash("s",i),invariant_claims={"relation":"R","closed":True},evidence_roots=[_hash("e",[i,j]) for j in range(3)],utility=Fraction(i+1),cost=Fraction(1)) for i in range(3)]
    lanes=[("a",_validator("a")),("b",_validator("b")),("c",_validator("c"))]
    return e,cs,lanes,e.evaluate_parallel(cs,lane_validators=lanes)


def test_parallel_receipts_are_ordered_and_rooted():
    _,cs,_,p=build(); assert len(p["lane_receipts"])==len(cs)*3; assert p["parallel_root_hash72"]

def test_probability_selects_only_admissible_candidates():
    e,_,_,p=build(); s=e.select(p,entropy_seed_root_hash72="seed"); assert s["selected_candidate_root_hash72"] in s["admissible_candidate_roots"]; assert s["probability_created_authority"] is False

def test_deterministic_selection_replay():
    e,_,_,p=build(); s=e.select(p,entropy_seed_root_hash72="seed"); assert e.replay(p,"seed",s)["replay_status"].endswith("VALIDATED")

def test_lane_nondeterminism_rejected():
    e,cs,_,_=build(); state={"x":False}
    def bad(c): state["x"]=not state["x"]; return {"admitted":state["x"],"validated_invariants":c["invariant_claims"]}
    with pytest.raises(Pass124Error) as z:e.evaluate_parallel(cs,lane_validators=[("bad",bad),("b",_validator("b")),("c",_validator("c"))])
    assert z.value.code=="REJECT_NONDETERMINISTIC_LANE"

def test_parallel_disagreement_rejected():
    e,cs,_,_=build()
    with pytest.raises(Pass124Error) as z:e.evaluate_parallel(cs,lane_validators=[("a",_validator("a")),("b",_validator("b",False)),("c",_validator("c"))])
    assert z.value.code=="REJECT_PARALLEL_DISAGREEMENT"

def test_invariant_drift_rejected():
    e,cs,_,_=build()
    def drift(c): return {"admitted":True,"validated_invariants":{"relation":"DIFFERENT","closed":True}}
    with pytest.raises(Pass124Error) as z:e.evaluate_parallel(cs,lane_validators=[("a",drift),("b",drift),("c",drift)])
    assert z.value.code=="REJECT_INVARIANT_DRIFT"

def test_insufficient_witnesses_do_not_gain_authority():
    e=ParallelDeterministicGeneralizationEngine(ParallelGeneralizationBounds(min_independent_witnesses=4))
    c=e.make_candidate(candidate_id="c",semantic_root_hash72="s",invariant_claims={"x":1},evidence_roots=["e"])
    p=e.evaluate_parallel([c],lane_validators=[("a",_validator("a")),("b",_validator("b")),("c",_validator("c"))])
    with pytest.raises(Pass124Error) as z:e.select(p,entropy_seed_root_hash72="seed")
    assert z.value.code=="REJECT_NO_ADMISSIBLE_CANDIDATE"

def test_candidate_tamper_rejected():
    e,cs,lanes,_=build(); bad=deepcopy(cs[0]); bad["utility"]={"numerator":999,"denominator":1}
    with pytest.raises(Pass124Error) as z:e.evaluate_parallel([bad],lane_validators=lanes)
    assert z.value.code=="REJECT_CANDIDATE_ROOT_MISMATCH"

def test_invalid_weight_rejected():
    e=ParallelDeterministicGeneralizationEngine()
    with pytest.raises(Pass124Error) as z:e.make_candidate(candidate_id="c",semantic_root_hash72="s",invariant_claims={},evidence_roots=["e"],cost=Fraction(0))
    assert z.value.code=="REJECT_INVALID_WEIGHT"

def test_seed_changes_selection_but_not_authority_set():
    e,_,_,p=build(); a=e.select(p,entropy_seed_root_hash72="a"); b=e.select(p,entropy_seed_root_hash72="b"); assert a["admissible_candidate_roots"]==b["admissible_candidate_roots"]

def test_self_test(): assert pass124_self_test()["ok"] is True

def test_registry():
    from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
    svc=next(x for x in make_default_service_registry().services() if x["name"]=="runtime.parallel_deterministic_generalization.pass124")
    assert svc["conformance_decision"]["derivation_complete"] is True

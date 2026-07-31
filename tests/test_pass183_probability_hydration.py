from __future__ import annotations
from hashlib import sha256
from math import gcd
from pathlib import Path
from typing import Any
import pytest
from hhs_runtime.pass183 import (
    ADAPTER_EQUATIONS,CANONICAL_FORMULA,FACTORIAL_72,FORWARD_LANE_TOKEN,GLOBAL_MODULUS,
    RECIPROCAL_LANE_TOKEN,Pass183Error,ProbabilityHydrationJobStore,
    ProbabilityHydrationRuntime,ProbabilityVM81Authority,apply_outer_modulus,build_membrane_tree,
)

class LocalAuthority:
    def __init__(self)->None:self.epoch=0;self.root="h"*72;self.calls=[]
    def status(self):return{"classification":"LOCAL_VM81","vmrc":{"epoch":self.epoch,"state_hash72":self.root}}
    def execute(self,**kwargs):
        self.calls.append(dict(kwargs));predecessor=self.root;self.epoch+=1
        self.root=(sha256((predecessor+repr(sorted(kwargs.items()))).encode()).hexdigest()*2)[:72]
        return{"classification":"HHS_PASS_174_DIRECT_VM81_COMPUTATION_COMMITTED","path":"DIRECT_RUNTIME","operation_key":sha256(repr(kwargs).encode()).hexdigest(),"receipt":{"receipt_sha256":sha256((predecessor+self.root).encode()).hexdigest()}}
    def replay(self):return{"classification":"LOCAL_REPLAY","deterministic_replay":True,"epoch":self.epoch}

def runtime():
    authority=LocalAuthority();return ProbabilityHydrationRuntime(authority=authority),authority

CASES={
"bayes":{"p_a":"1/4","p_b":"1/2","p_b_given_a":"4/5","p_a_given_b":"2/5"},
"conditional_probability":{"p_a_and_b":"1/4","p_b":"1/2","p_a_given_b":"1/2"},
"independent_intersection":{"p_a":"1/2","p_b":"1/3","p_a_and_b":"1/6"},
"general_intersection":{"p_a_given_b":"1/2","p_b":"1/3","p_a_and_b":"1/6"},
"union_inclusion_exclusion":{"p_a":"1/2","p_b":"1/3","p_intersection":"1/6","p_union":"2/3"},
"total_probability":{"p_h":"1/4","p_e_given_h":"3/4","p_e_given_not_h":"1/4","p_e":"3/8"},
"expectation":{"outcomes":[0,2],"probabilities":["1/4","3/4"],"expected":"3/2"},
"variance":{"outcomes":[0,2],"probabilities":["1/2","1/2"],"mean":"1","variance":"1"},
"finite_discrete_distribution":{"probabilities":["1/6","1/3","1/2"]},
"binomial":{"n":8,"p":"1/3"},"multinomial":{"n":5,"probabilities":["1/2","1/3","1/6"]},
"markov_chain":{"matrix":[["1/2","1/2"],["1/4","3/4"]]},
"weighted_choice":{"weights":["1/4","1/4","1/2"]},
"monte_carlo_control":{"success_probability":"1/3","sample_count":24}}

def execute_case(adapter,manifest,**kwargs):
    instance,_=runtime();return instance.execute(adapter=adapter,equation=ADAPTER_EQUATIONS[adapter],manifest=manifest,seed_class=("CONTENT_ADDRESSED_SEED" if adapter in{"weighted_choice","monte_carlo_control"}else"DETERMINISTIC_ENUMERATION"),**kwargs)

def test_canonical_formula_and_modulus_are_exact():
    assert CANONICAL_FORMULA=="(List(x*Factorial(72),(y*(1/Factorial(72))))*z)*(w*List((y*(1/Factorial(72))),x*Factorial(72)))/u^72==(x*y)/(x*y)==u^72"
    assert FORWARD_LANE_TOKEN in CANONICAL_FORMULA and RECIPROCAL_LANE_TOKEN in CANONICAL_FORMULA
    assert GLOBAL_MODULUS==1_259_713 and gcd(FACTORIAL_72,GLOBAL_MODULUS)==91

def test_nested_membranes_are_nondestructive_and_deterministic():
    source="P(E)=P(H)*P(E|H)+(1-P(H))*P(E|not H)";first=build_membrane_tree(source);assert first==build_membrane_tree(source);assert len(first)==6
    for record in first:
        assert record.boundary_modulus_n_plus_1==record.depth_n+1 and record.boundary_residue_n==record.depth_n
        lexical=bytes.fromhex(record.lexical_bytes_hex).decode("utf-8");assert lexical.startswith("(") and lexical.endswith(")")

@pytest.mark.parametrize("adapter",sorted(CASES))
def test_all_required_adapters_execute_exactly(adapter):
    result=execute_case(adapter,CASES[adapter]);evaluation=result["evaluation"]
    assert evaluation["source_equation_true"] is True and evaluation["probability_domain_valid"] is True
    assert evaluation["local_factorial_modular_inverse_attempted"] is False and all(evaluation["lane_recovery"].values())
    assert evaluation["outer_modulus"]["scalar_residue_available"] is True
    if not evaluation["typed_zero_bypass"]:assert evaluation["closure_exact"]=="1" and evaluation["outer_modulus"]["residue"]==1
    assert result["authority_receipt"]["classification"]=="HHS_PASS_183_SINGLETON_VM81_ADMITTED"

def test_false_equation_is_rejected_separately_from_closure():
    instance,authority=runtime()
    with pytest.raises(Pass183Error) as captured:instance.execute(adapter="independent_intersection",equation=ADAPTER_EQUATIONS["independent_intersection"],manifest={"p_a":"1/2","p_b":"1/2","p_a_and_b":"1/3"})
    assert captured.value.classification=="P183_REJECT_EQUATION_FALSE" and authority.calls==[]

def test_probability_domain_rejection_precedes_authority():
    instance,authority=runtime()
    with pytest.raises(Pass183Error) as captured:instance.execute(adapter="conditional_probability",equation=ADAPTER_EQUATIONS["conditional_probability"],manifest={"p_a_and_b":"1/4","p_b":"5/4","p_a_given_b":"1/5"})
    assert captured.value.classification=="P183_REJECT_PROBABILITY_DOMAIN" and authority.calls==[]

def test_zero_result_routes_typed_zero_bypass():
    result=execute_case("independent_intersection",{"p_a":"0","p_b":"1/2","p_a_and_b":"0"})
    assert result["classification"]=="HHS_PASS_183_TYPED_ZERO_BYPASS_VERIFIED" and result["evaluation"]["typed_zero_bypass"] is True
    assert result["evaluation"]["closure_classification"]=="P183_ZERO_BYPASS" and result["evaluation"]["closure_exact"]=="0"

def test_float_coercion_and_lexical_mutation_fail_closed():
    instance,authority=runtime()
    with pytest.raises(Pass183Error) as e:instance.execute(adapter="independent_intersection",equation=ADAPTER_EQUATIONS["independent_intersection"],manifest={"p_a":.5,"p_b":"1/2","p_a_and_b":"1/4"})
    assert e.value.classification=="P183_REJECT_FLOAT_AUTHORITY"
    with pytest.raises(Pass183Error) as e:instance.execute(adapter="independent_intersection",equation="P(A∩B) = P(A)*P(B)",manifest={"p_a":"1/2","p_b":"1/2","p_a_and_b":"1/4"})
    assert e.value.classification=="P183_REJECT_LEXICAL_IDENTITY" and authority.calls==[]

def test_unbalanced_parentheses_and_unicode_lookalikes_reject():
    with pytest.raises(Pass183Error) as e:build_membrane_tree("P(A)=(P(B)")
    assert e.value.classification=="P183_REJECT_UNBALANCED_MEMBRANE"
    with pytest.raises(Pass183Error) as e:build_membrane_tree("P(A)=P(B)÷P(C)")
    assert e.value.classification=="P183_REJECT_LEXICAL_IDENTITY"

def test_noninvertible_denominator_retains_typed_envelope():
    from fractions import Fraction
    result=apply_outer_modulus(Fraction(1,7));assert result["classification"]=="P183_REJECT_NONINVERTIBLE_OUTER_DENOMINATOR" and result["scalar_residue_available"] is False and result["denominator_gcd_with_modulus"]==7

def test_wrong_or_premature_modulus_is_rejected():
    from fractions import Fraction
    with pytest.raises(Pass183Error) as e:apply_outer_modulus(Fraction(1),72)
    assert e.value.classification=="P183_REJECT_LOCAL_MODULAR_INVERSION"

def test_stochastic_manifest_and_replay_are_deterministic():
    first,_=runtime();second,_=runtime();kwargs=dict(adapter="weighted_choice",equation=ADAPTER_EQUATIONS["weighted_choice"],manifest=CASES["weighted_choice"],seed_class="EXPLICIT_USER_SEED",seed="00112233445566778899aabbccddeeff")
    left=first.execute(**kwargs);right=second.execute(**kwargs)
    assert left["evaluation"]["adapter_domain"]==right["evaluation"]["adapter_domain"]
    assert left["evaluation"]["hash216"]["logical_identity_sha256"]==right["evaluation"]["hash216"]["logical_identity_sha256"]
    assert first.replay()["classification"]=="HHS_PASS_183_DETERMINISTIC_REPLAY_VERIFIED" and second.replay()["replay_root_sha256"]==first.replay()["replay_root_sha256"]

def test_receipt_tamper_is_detected():
    instance,_=runtime();instance.execute(adapter="binomial",equation=ADAPTER_EQUATIONS["binomial"],manifest=CASES["binomial"]);record=instance._records[0];object.__setattr__(record,"receipt",{**record.receipt,"receipt_hash72":"x"*72})
    with pytest.raises(Pass183Error) as e:instance.replay()
    assert e.value.classification=="P183_REJECT_RECEIPT"

def test_durable_jobs_support_success_failure_cancel_and_retry(tmp_path:Path):
    instance,_=runtime();store=ProbabilityHydrationJobStore(instance,tmp_path/"jobs");good_request={"adapter":"expectation","equation":ADAPTER_EQUATIONS["expectation"],"manifest":CASES["expectation"]};good=store.create(good_request);assert store.run(good.job_id).state=="SUCCEEDED"
    bad=store.create({"adapter":"finite_discrete_distribution","equation":ADAPTER_EQUATIONS["finite_discrete_distribution"],"manifest":{"probabilities":["1/2","1/3"]}});failed=store.run(bad.job_id);assert failed.state=="FAILED" and failed.error["classification"]=="P183_REJECT_PROBABILITY_DOMAIN";assert store.retry(failed.job_id).attempt==2
    queued=store.create(good_request);cancelled=store.cancel(queued.job_id);assert cancelled.state=="CANCELLED";reopened=ProbabilityHydrationJobStore(instance,tmp_path/"jobs");assert reopened.get(good.job_id).state=="SUCCEEDED" and reopened.get(cancelled.job_id).state=="CANCELLED"

def test_default_runtime_uses_genuine_pass174_when_repository_available():
    instance=ProbabilityHydrationRuntime();assert isinstance(instance.authority,ProbabilityVM81Authority)
    result=instance.execute(adapter="binomial",equation=ADAPTER_EQUATIONS["binomial"],manifest={"n":4,"p":"1/2"})
    assert result["authority_receipt"]["payload"]["vmrc_operation_class"]=="VMRC_COMMIT" and instance.replay()["authority_replay"]["singleton_vm81"] is True

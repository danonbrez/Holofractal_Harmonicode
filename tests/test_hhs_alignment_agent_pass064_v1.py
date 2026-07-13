from hhs_backend.runtime.hhs_alignment_agent_v1 import *

def test_pass064_self_test(): assert alignment_agent_self_test()["ok"]
def test_reciprocal_pair_closes():
 r=run_alignment_agent(); assert r["ok"]; assert r["entanglement_receipt"]["reciprocal_closure_verified"]
def test_attention_never_admits(): assert run_alignment_agent()["selection"]["attention_used_for_admission"] is False
def test_unsupported_claim_rejected():
 r=run_alignment_agent(); x=build_response_candidate(r["prompt_state"],unsupported_claim=True); d=validate_claim_provenance(r["prompt_state"],x); assert "REJECT_RESPONSE_CLAIM_WITHOUT_PROVENANCE" in d["reasons"]
def test_presentation_mutation_rejected():
 r=run_alignment_agent(); x=build_response_candidate(r["prompt_state"],mutate_unavailable=True); d=detect_alignment_drift(r["prompt_state"],x); assert "REJECT_PRESENTATION_MUTATES_EPISTEMIC_STATE" in d["reasons"]
def test_independent_revalidation_required():
 r=run_alignment_agent(); d=independently_revalidate_alignment(r["selection"],r["entanglement_receipt"],local_revalidation=False); assert "REJECT_RESPONSE_WITHOUT_INDEPENDENT_REVALIDATION" in d["reasons"]

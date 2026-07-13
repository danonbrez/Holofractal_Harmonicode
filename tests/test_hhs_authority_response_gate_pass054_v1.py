from hhs_backend.runtime.hhs_role_bound_agent_orchestrator_v1 import admit_response_candidate

def base(): return {"candidate_id":"c","source_authority":"CANONICAL","provenance_valid":True,"derivation_valid":True,"role_scope_valid":True}
def test_attention_and_recency_do_not_admit():
    c=base(); c["source_authority"]="UNVALIDATED_PROPOSAL"
    d=admit_response_candidate(c,canonical_invariant_conflict=True)
    assert not d["admissible"]
    assert "REJECT_ATTENTION_AS_TRUTH_WEIGHT" in d["reasons"]
    assert "REJECT_RECENCY_AS_AUTHORITY" in d["reasons"]
def test_presentation_cannot_mutate_meaning():
    d=admit_response_candidate(base(),presentation_mutates_meaning=True)
    assert "REJECT_PRESENTATION_OPTIMIZATION_MUTATES_MEANING" in d["reasons"]

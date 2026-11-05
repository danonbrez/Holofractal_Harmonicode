"""No arbitrary HHS tensor state block; actual canonical signing remains native."""
import pytest

from hhs_runtime.hhs_tensor_constraint_admissibility_v1 import (
    TensorEligibility, classify_tensor_state,
)

REQUIRED=(
    "source_identity", "tensor_types", "ordered_phase",
    "global_denominator", "vm81_cell_addresses",
    "rna_transcription", "previous_hash216_lineage",
    "security_cell_wall",
)

def check(**changes):
    data={
        "required_constraints":REQUIRED,
        "constraint_results":{x:True for x in REQUIRED},
        "candidate_branches":("one-native-branch",),
        "branches_exhaustively_resolved":True,
    }
    data.update(changes)
    return classify_tensor_state(**data)

def test_valid_unique_constraint_closed_state_must_progress():
    result=check()
    assert result.classification is TensorEligibility.FORWARD_SIGNED_VM81
    assert result.eligible_for_inherited_signed_vm81
    assert not result.canonical_vm81_committed
    assert not result.canonical_hash72_hash216_minted
    assert result.required_constraints == result.satisfied_constraints
    assert result.unresolved_constraints == ()
    assert result.contradictory_constraints == ()

def test_new_branch_name_must_not_be_arbitrarily_blocked():
    result=check(candidate_branches=("novel-but-fully-typed-5184-state",))
    assert result.classification is TensorEligibility.FORWARD_SIGNED_VM81

@pytest.mark.parametrize("bad",REQUIRED)
def test_explicit_existing_native_constraint_violation_blocks(bad):
    facts={x:True for x in REQUIRED}
    facts[bad]=False
    result=check(constraint_results=facts)
    assert result.classification is TensorEligibility.CONTRADICTORY
    assert result.contradictory_constraints==(bad,)
    assert not result.eligible_for_inherited_signed_vm81

def test_ambiguous_native_branch_blocks_without_invalidating_axioms():
    out=check(candidate_branches=("left","right"))
    assert out.classification is TensorEligibility.AMBIGUOUS_BRANCH
    assert not out.eligible_for_inherited_signed_vm81

def test_unknown_or_absent_native_witness_is_pending_not_contradiction():
    facts={x:True for x in REQUIRED}
    facts["ordered_phase"]=None
    out=check(constraint_results=facts)
    assert out.classification is TensorEligibility.EVIDENCE_PENDING
    assert out.unresolved_constraints == ("ordered_phase",)
    assert not out.contradictory_constraints
    del facts["global_denominator"]
    out=check(constraint_results=facts)
    assert "global_denominator" in out.unresolved_constraints
    assert out.classification is TensorEligibility.EVIDENCE_PENDING

def test_native_branch_search_in_progress_not_falsely_rejected():
    assert check(candidate_branches=None).classification is TensorEligibility.EVIDENCE_PENDING
    assert check(branches_exhaustively_resolved=False).classification is TensorEligibility.EVIDENCE_PENDING
    assert check(candidate_branches=(),branches_exhaustively_resolved=False).classification is TensorEligibility.EVIDENCE_PENDING
    assert check(candidate_branches=(),branches_exhaustively_resolved=True).classification is TensorEligibility.CONTRADICTORY

@pytest.mark.parametrize("bad",[
    {"required_constraints":()},
    {"required_constraints":("x","x")},
    {"constraint_results":{"not-a-required-condition":True}},
    {"constraint_results":{"source_identity":"yes"}},
    {"candidate_branches":("same","same")},
    {"candidate_branches":("",)},
    {"branches_exhaustively_resolved":1},
])
def test_invalid_claim_or_empty_required_registry_cannot_fabricate_readiness(bad):
    result=check(**bad)
    assert result.classification is TensorEligibility.INVALID_EVIDENCE
    assert not result.eligible_for_inherited_signed_vm81

def test_no_duplicate_new_proof_gate():
    extra="arbitrary-mathematical-reproof"
    # A closed native requirement set is sufficient. Do not inject an
    # unrelated mandatory reproof as an extra implicit predicate.
    outcome=check()
    assert extra not in outcome.required_constraints
    assert outcome.classification is TensorEligibility.FORWARD_SIGNED_VM81

def test_unchecked_false_does_not_equal_unknown():
    facts={x:True for x in REQUIRED}
    facts["tensor_types"]=False
    result=check(constraint_results=facts)
    assert result.classification is TensorEligibility.CONTRADICTORY
    facts["tensor_types"]=None
    result=check(constraint_results=facts)
    assert result.classification is TensorEligibility.EVIDENCE_PENDING

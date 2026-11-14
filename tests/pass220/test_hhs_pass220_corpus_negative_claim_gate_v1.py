"""Negative corpus assertions must not be inferred from incomplete discovery."""
from __future__ import annotations
import pytest
from hhs_runtime.hhs_pass220_corpus_negative_claim_gate_v1 import (
    NEGATIVE, CorpusDiscoveryClaimError, unresolved, validate_claim,
)
SOURCE={"path_or_ref":"docs/course/HARMONICODE_Algebra_Course_Expanded_0_190.md","revision":"24a05483083d8aebde1b781db12ecbac8adc0d20"}


@pytest.mark.parametrize("status", sorted(NEGATIVE))
def test_negative_claims_rejected_despite_self_attested_coverage(status):
    with pytest.raises(CorpusDiscoveryClaimError, match="INDEPENDENT_COMPLETE_DISCOVERY_RECEIPT"):
        validate_claim({"object":"ordered HNAN proof","status":status,
                        "checked_sources":[SOURCE],
                        "distributed_branch_pr_coverage_complete":True,
                        "proof_verified":True})


def test_unresolved_preserves_discovery_bounds():
    result=unresolved("course Module 195", [SOURCE])
    assert result["status"]=="NOT_YET_LOCATED"
    assert result["checked_sources"]==[SOURCE]
    assert result["distributed_branch_pr_coverage_complete"] is False
    assert result["negative_existence_claim_authorized"] is False
    assert result["vm81_mutation_authority"] is False


def test_found_requires_traceable_source_and_strips_authority():
    with pytest.raises(CorpusDiscoveryClaimError, match="FOUND_REQUIRES_SOURCE_WITNESS"):
        validate_claim({"object":"course", "status":"FOUND"})
    report=validate_claim({"object":"course","status":"FOUND",
        "checked_sources":[SOURCE],"vm81_mutation_authority":True,
        "negative_existence_claim_authorized":True})
    assert report["status"]=="FOUND"
    assert report["vm81_mutation_authority"] is False
    assert report["negative_existence_claim_authorized"] is False


def test_integration_gap_is_not_existence_absence():
    with pytest.raises(CorpusDiscoveryClaimError, match="CHECKED_INTERFACE"):
        validate_claim({"object":"HNAN egress","status":"INTEGRATION_GAP_VERIFIED",
                        "checked_sources":[SOURCE]})
    report=validate_claim({"object":"HNAN egress","status":"INTEGRATION_GAP_VERIFIED",
        "checked_sources":[SOURCE],"checked_interface":"Pass 220 VM81 ingress",
        "failure_evidence":"named regression fails on missing adapter"})
    assert report["status"]=="INTEGRATION_GAP_VERIFIED"
    assert report["distributed_branch_pr_coverage_complete"] is False


def test_invalid_evidence_fails_closed():
    with pytest.raises(CorpusDiscoveryClaimError, match="INVALID_DISCOVERY_SOURCE_REFERENCES"):
        validate_claim({"object":"x","status":"FOUND","checked_sources":[{"path_or_ref":"x"}]})
    with pytest.raises(CorpusDiscoveryClaimError, match="UNREGISTERED_DISCOVERY_STATUS"):
        validate_claim({"object":"x","status":"PROVEN_ABSENT"})

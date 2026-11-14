"""Provider-registry miss must not become an unsourced corpus absence claim."""
from __future__ import annotations

from hhs_backend.runtime.hhs_capability_resolution_v1 import resolve_capability


def test_unregistered_provider_reports_bounded_discovery_not_absence():
    result=resolve_capability("UNREGISTERED_CAPABILITY")
    assert result["ok"] is False
    assert result["status"]=="REJECT_CAPABILITY_RESOLUTION"
    assert result["registry_rejection_is_corpus_absence"] is False
    diagnostic=result["repository_discovery"]
    assert diagnostic["status"] in ("FOUND","NOT_YET_LOCATED")
    assert diagnostic["coverage_complete"] is False
    assert diagnostic["negative_existence_claim_authorized"] is False
    assert result["capability_selection_grants_execution_authority"] is False


def test_known_capability_provider_selection_still_operates():
    result=resolve_capability("OCR")
    assert result["ok"] is True
    assert result["status"]=="ADMIT_CAPABILITY_RESOLUTION"
    assert result["capability_selection_grants_execution_authority"] is False

"""Exact remote trees expose candidates, conflicting blobs, and truncated coverage."""
import pytest
from hhs_runtime.hhs_pass220_remote_ref_tree_reconciliation_v1 import (
    reconcile_remote_trees, RemoteTreeReconciliationError,
)
A="a"*40
B="b"*40
C="c"*40
D="d"*40
REPO="danonbrez/Holofractal_Harmonicode"

def census(branch_sha=A, pr_sha=B, pr_repo=REPO):
    return {"schema":"HHS_PASS220_REMOTE_REF_CENSUS_V1","repository":REPO,
            "branch_pages_exhausted":True,"open_pr_pages_exhausted":True,
            "branch_count":1,"open_pr_count":1,
            "branches":[{"name":"main","sha":branch_sha}],
            "open_pulls":[{"number":911,"head_sha":pr_sha,"head_repo":pr_repo}]}

def fake_get(url):
    if A in url:
        return {"truncated":False,"tree":[
            {"type":"blob","path":"formal/lemmas/theorem.lean","sha":C},
            {"type":"blob","path":"README.md","sha":D},
            {"type":"tree","path":"formal/lemmas","sha":B},
        ]}
    if B in url:
        return {"truncated":False,"tree":[
            {"type":"blob","path":"formal/lemmas/theorem.lean","sha":D},
            {"type":"blob","path":"docs/course/module195.md","sha":A},
        ]}
    raise AssertionError(url)

def test_exact_tree_reconciliation_retains_conflicts_and_overlaps():
    result=reconcile_remote_trees(census(),get=fake_get,
                                  baseline={"formal/lemmas/theorem.lean":C})
    assert result["unique_source_tree_count"]==2
    assert result["candidate_count"]==3
    assert len(result["baseline_index_overlap"])==2
    assert [x["blob_equal"] for x in result["baseline_index_overlap"]]==[True,False]
    assert result["all_census_trees_enumerated"] is True
    assert result["negative_existence_claim_authorized"] is False
    assert result["distributed_discovery_complete"] is False

def test_identical_commit_tree_fetched_only_once():
    calls=[]
    def get(url):
        calls.append(url)
        return fake_get(url)
    result=reconcile_remote_trees(census(pr_sha=A),get=get)
    assert len(calls)==1
    assert result["unique_source_tree_count"]==1
    assert len(result["ref_records"])==2

def test_truncated_tree_cannot_authorize_absence():
    result=reconcile_remote_trees(census(),get=lambda url: {
        "truncated":True,"tree":[]})
    assert result["all_census_trees_enumerated"] is False
    assert len(result["remote_tree_errors"])==2
    assert result["negative_existence_claim_authorized"] is False

def test_unavailable_fork_retained_as_explicit_open_boundary():
    result=reconcile_remote_trees(census(pr_repo=None),get=fake_get)
    assert result["ref_records"][1]["status"]=="HEAD_REPOSITORY_UNAVAILABLE"
    assert result["all_census_trees_enumerated"] is False

def test_candidate_output_cap_not_full_coverage():
    result=reconcile_remote_trees(census(),get=fake_get,max_matches=1)
    assert result["candidate_results_truncated"] is True
    assert len(result["candidate_matches"])==1
    assert result["candidate_count"]==3

def test_partial_census_and_invalid_tree_rejected():
    broken=census()
    broken["open_pr_pages_exhausted"]=False
    with pytest.raises(RemoteTreeReconciliationError,match="CENSUS_INCOMPLETE"):
        reconcile_remote_trees(broken,get=fake_get)
    with pytest.raises(RemoteTreeReconciliationError,match="RESPONSE_INVALID"):
        reconcile_remote_trees(census(),get=lambda url:{"tree":[]})
    with pytest.raises(RemoteTreeReconciliationError,match="DUPLICATE_PATH"):
        reconcile_remote_trees(census(),get=lambda url: {
            "truncated":False,"tree":[
                {"type":"blob","path":"formal/test.lean","sha":A},
                {"type":"blob","path":"formal/test.lean","sha":B}]})

def test_query_selection_does_not_assert_missing():
    result=reconcile_remote_trees(census(),get=fake_get,query="unlikely_name")
    assert result["candidate_count"]==0
    assert result["negative_existence_claim_authorized"] is False

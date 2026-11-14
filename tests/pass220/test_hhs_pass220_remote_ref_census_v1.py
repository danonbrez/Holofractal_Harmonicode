"""Remote-ref census completeness is pagination-scoped, not source proof."""
from __future__ import annotations
import pytest
from hhs_runtime.hhs_pass220_remote_ref_census_v1 import (
    RemoteCensusError, inventory_remote_refs, compare_local_refs, next_link,
)

BASE="https://api.github.com/repos/danonbrez/Holofractal_Harmonicode"
A="a"*40
B="b"*40
C="c"*40

def fixture_get(url):
    if url == BASE+"/branches?per_page=100":
        return ([{"name":"main","commit":{"sha":A}}],
                '<'+BASE+'/branches?page=2&per_page=100>; rel="next"')
    if url == BASE+"/branches?page=2&per_page=100":
        return ([{"name":"course/module195","commit":{"sha":B}}], None)
    if url == BASE+"/pulls?state=open&per_page=100":
        return ([{"number":911,"head":{"sha":C,"ref":"feature/m195",
                 "repo":{"full_name":"danonbrez/Holofractal_Harmonicode"}}}], None)
    raise AssertionError("unexpected API URL: "+url)

def test_full_paginated_remote_ref_inventory_does_not_claim_proof():
    report=inventory_remote_refs("danonbrez/Holofractal_Harmonicode",get=fixture_get)
    assert report["branch_count"]==2
    assert report["open_pr_count"]==1
    assert report["branches"][1]["name"]=="course/module195"
    assert report["open_pulls"][0]["head_sha"]==C
    assert report["branch_pages_exhausted"] is True
    assert report["distributed_discovery_complete"] is False
    assert report["negative_existence_claim_authorized"] is False

def test_missing_and_drifted_local_refs_are_explicit():
    report=inventory_remote_refs("danonbrez/Holofractal_Harmonicode",get=fixture_get)
    mismatch=compare_local_refs(report,{"refs/remotes/origin/main":B})
    assert len(mismatch["missing_local_refs"])==2
    assert len(mismatch["outdated_local_refs"])==1
    assert mismatch["local_ref_alignment_verified"] is False
    assert mismatch["negative_existence_claim_authorized"] is False

def test_exact_local_ref_match_does_not_prove_theorem_coverage():
    report=inventory_remote_refs("danonbrez/Holofractal_Harmonicode",get=fixture_get)
    aligned=compare_local_refs(report,{"refs/remotes/origin/main":A,
        "refs/remotes/origin/course/module195":B,"refs/pull/911/head":C})
    assert aligned["local_ref_alignment_verified"] is True
    assert aligned["remote_trees_verified"] is False

def test_truncated_pagination_fails_closed():
    with pytest.raises(RemoteCensusError,match="PAGE_LIMIT_REACHED"):
        inventory_remote_refs("danonbrez/Holofractal_Harmonicode",
                              get=fixture_get,max_pages=1)

def test_duplicate_branch_and_pr_fail_closed():
    def duplicate_branches(url):
        if "/branches?" in url:
            return ([{"name":"main","commit":{"sha":A}},
                     {"name":"main","commit":{"sha":A}}],None)
        return ([],None)
    with pytest.raises(RemoteCensusError,match="DUPLICATE_BRANCH"):
        inventory_remote_refs("danonbrez/Holofractal_Harmonicode",get=duplicate_branches)
    def duplicate_pulls(url):
        if "/branches?" in url: return ([],None)
        return ([{"number":8,"head":{"sha":A,"ref":"x","repo":None}},
                 {"number":8,"head":{"sha":A,"ref":"x","repo":None}}],None)
    with pytest.raises(RemoteCensusError,match="DUPLICATE_PR"):
        inventory_remote_refs("danonbrez/Holofractal_Harmonicode",get=duplicate_pulls)

def test_untrusted_link_and_pagination_cycle_rejected():
    with pytest.raises(RemoteCensusError,match="UNTRUSTED_NEXT_LINK"):
        next_link('<https://evil.example/branches?page=2>; rel="next"')
    def cycle(url):
        if "/branches?" in url:
            return ([], '<'+url+'>; rel="next"')
        return ([],None)
    with pytest.raises(RemoteCensusError,match="PAGINATION_CYCLE"):
        inventory_remote_refs("danonbrez/Holofractal_Harmonicode",get=cycle)

def test_invalid_repo_never_triggers_network():
    with pytest.raises(RemoteCensusError,match="REPOSITORY_INVALID"):
        inventory_remote_refs("../etc",get=fixture_get)

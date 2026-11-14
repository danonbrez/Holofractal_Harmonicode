"""Local Git-ref federation is evidence, never exhaustive absence proof."""
import subprocess
import pytest
from hhs_runtime import hhs_pass220_ref_federated_corpus_discovery_v1 as mod

def git(root,*args):
    return subprocess.check_output(["git",*args],cwd=root,text=True).strip()

@pytest.fixture
def fixture_repo(tmp_path,monkeypatch):
    git(tmp_path,"init")
    git(tmp_path,"config","user.name","test")
    git(tmp_path,"config","user.email","test@example.invalid")
    (tmp_path/"readme.md").write_text("main")
    git(tmp_path,"add",".")
    git(tmp_path,"commit","-m","root")
    git(tmp_path,"checkout","-b","course/m195")
    (tmp_path/"course").mkdir()
    (tmp_path/"course/module195_proof.md").write_text("proof")
    git(tmp_path,"add",".")
    git(tmp_path,"commit","-m","module195")
    def index(root,term,*,limit):
        return {"matches":[],"matched_count":0,"truncated":False}
    monkeypatch.setattr(mod,"search_index",index)
    return tmp_path

def test_finds_unmerged_branch_file_without_github_search(fixture_repo):
    result=mod.search_federated_refs(fixture_repo,"module195")
    assert result["index_first"] is True
    assert result["ref_match_count"]==1
    assert result["ref_matches"][0]["ref"]=="refs/heads/course/m195"
    assert result["report"]["status"]=="FOUND"
    assert result["negative_existence_claim_authorized"] is False

def test_no_hit_unresolved_not_absent(fixture_repo):
    result=mod.search_federated_refs(fixture_repo,"nonexistent")
    assert result["report"]["status"]=="NOT_YET_LOCATED"
    assert result["all_remote_refs_fetched"] is False
    assert result["all_open_prs_verified"] is False

def test_capped_output_exposes_truncation(fixture_repo):
    result=mod.search_federated_refs(fixture_repo,".md",limit=1)
    assert result["ref_match_count"]>=2
    assert result["ref_matches_truncated"] is True
    assert len(result["ref_matches"])==1

def test_invalid_query_and_ref_limit_fail_closed(fixture_repo):
    with pytest.raises(mod.FederatedDiscoveryError,match="QUERY_REQUIRED"):
        mod.search_federated_refs(fixture_repo,"")
    with pytest.raises(mod.FederatedDiscoveryError,match="REF_CENSUS_LIMIT_EXCEEDED"):
        mod.search_federated_refs(fixture_repo,"module",max_refs=1)

def test_stale_index_does_not_become_absence(fixture_repo,monkeypatch):
    def stale(*args,**kwargs):
        raise mod.IndexDiscoveryError("INDEX_CHECKOUT_REVISION_MISMATCH")
    monkeypatch.setattr(mod,"search_index",stale)
    result=mod.search_federated_refs(fixture_repo,"module195")
    assert result["index_available"] is False
    assert result["index_error"]=="INDEX_CHECKOUT_REVISION_MISMATCH"
    assert result["report"]["status"]=="FOUND"
    assert result["negative_existence_claim_authorized"] is False

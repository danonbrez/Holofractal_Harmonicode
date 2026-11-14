"""Index-first discovery must not infer absence from truncated code search."""
from __future__ import annotations
import json
import subprocess
import pytest
from hhs_runtime.hhs_pass220_index_first_discovery_v1 import (
    GRAPH, LANE5, RECEIPT, IndexDiscoveryError, search_index,
)


def _git(root,*args):
    return subprocess.check_output(["git",*args],cwd=root,text=True).strip()


@pytest.fixture
def indexed_repo(tmp_path):
    _git(tmp_path,"init")
    _git(tmp_path,"config","user.name","Test")
    _git(tmp_path,"config","user.email","test@example.invalid")
    (tmp_path/"placeholder").write_text("source")
    _git(tmp_path,"add","placeholder")
    _git(tmp_path,"commit","-m","indexed fixture")
    rev=_git(tmp_path,"rev-parse","HEAD")
    path="formal/lemmas/hnan_proof_v1.lean"
    (tmp_path/GRAPH).parent.mkdir(parents=True)
    graph={"source_commit":rev,"files":[{"path":path,"git_blob":"a"*40,"hash216":"b"*216}]}
    (tmp_path/GRAPH).write_text(json.dumps(graph))
    (tmp_path/LANE5).write_text(json.dumps({"source_commit":rev}))
    (tmp_path/RECEIPT).write_text(json.dumps({"source_commit":rev}))
    return tmp_path


def test_index_finds_likely_proof_even_without_github_search(indexed_repo):
    found=search_index(indexed_repo,"hnan")
    assert found["report"]["status"]=="FOUND"
    assert found["matched_count"]==1
    assert found["github_code_search_used"] is False
    assert found["matches"][0]["path_or_ref"]=="formal/lemmas/hnan_proof_v1.lean"
    assert found["open_branches_and_prs_exhaustively_covered"] is False
    assert found["negative_existence_claim_authorized"] is False


def test_no_path_hit_is_unresolved_not_absent(indexed_repo):
    result=search_index(indexed_repo,"nonexistent_example")
    assert result["matched_count"]==0
    assert result["report"]["status"]=="NOT_YET_LOCATED"
    assert result["negative_existence_claim_authorized"] is False


def test_stale_index_is_not_accepted(indexed_repo):
    path=indexed_repo/GRAPH
    data=json.loads(path.read_text())
    data["source_commit"]="0"*40
    path.write_text(json.dumps(data))
    with pytest.raises(IndexDiscoveryError,match="INDEX_CHECKOUT_REVISION_MISMATCH"):
        search_index(indexed_repo,"hnan")


def test_bad_identity_and_empty_query_fail_closed(indexed_repo):
    with pytest.raises(IndexDiscoveryError,match="INDEX_QUERY_REQUIRED"):
        search_index(indexed_repo,"")
    path=indexed_repo/GRAPH
    data=json.loads(path.read_text())
    data["files"][0]["hash216"]="x"
    path.write_text(json.dumps(data))
    with pytest.raises(IndexDiscoveryError,match="INDEX_MATCH_IDENTITY_INVALID"):
        search_index(indexed_repo,"hnan")


def test_limited_results_are_reported_as_truncated(indexed_repo):
    path=indexed_repo/GRAPH
    data=json.loads(path.read_text())
    data["files"].append({"path":"formal/lemmas/hnan_extra.lean","git_blob":"c"*40,
                          "hash216":"d"*216})
    path.write_text(json.dumps(data))
    result=search_index(indexed_repo,"hnan",limit=1)
    assert result["truncated"] is True
    assert result["matched_count"]==2
    assert len(result["matches"])==1
    assert result["negative_existence_claim_authorized"] is False

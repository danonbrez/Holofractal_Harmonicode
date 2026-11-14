"""Exact Git blob provenance and ordered source spans are mandatory."""
from __future__ import annotations
import base64
import pytest
from hhs_runtime.hhs_pass220_source_bound_proof_extraction_v1 import (
    extract_proof_candidates, git_blob_hash, ProofExtractionError,
)
REPO="danonbrez/Holofractal_Harmonicode"
def fixture_tree(text, *, path="docs/course/HARMONICODE_Algebra_Course.md", repeat=False):
    raw=text.encode()
    sha=git_blob_hash(raw)
    item={"repository":REPO,"path":path,"git_blob":sha,
          "ref":"branch:course/original","commit":"a"*40}
    return {"schema":"HHS_PASS220_REMOTE_REF_TREE_RECONCILIATION_V1",
            "candidate_matches":[item,dict(item,ref="pr:911")] if repeat else [item],
            "candidate_results_truncated":False,"remote_tree_errors":[]},raw,sha

def get_for(raw,sha):
    def get(url):
        assert url.endswith("/"+sha)
        return {"sha":sha,"encoding":"base64","content":base64.b64encode(raw).decode()}
    return get

def test_course_equation_operator_order_and_source_provenance_preserved():
    source="# Module 0 — Master\nAB=P⁴; BA=-P⁴\n# Module 1 — Gate\nxy == yx\n"
    tree,raw,sha=fixture_tree(source)
    result=extract_proof_candidates(tree,fetch=get_for(raw,sha))
    objects=result["extracted_sources"][0]["objects"]
    assert [o["identifier"] for o in objects]==[0,1]
    assert objects[0]["equation_candidates"][0]["exact_text"]=="AB=P⁴; BA=-P⁴"
    assert objects[1]["equation_candidates"][0]["exact_text"]=="xy == yx"
    assert result["extracted_sources"][0]["git_blob"]==sha
    assert result["native_proof_executed"] is False
    assert result["negative_existence_claim_authorized"] is False

def test_registered_lemmas_preserve_assumptions_and_stated_status():
    import json
    source=json.dumps({"lemmas":[{"id":"L1","statement":"xy != yx",
        "assumptions":["ordered cells"],"status":"EXECUTED_EXACT",
        "dependencies":["L0"]}]})
    tree,raw,sha=fixture_tree(source,path="formal/lemmas/LEMMA_CORPUS.json")
    rows=extract_proof_candidates(tree,fetch=get_for(raw,sha))["extracted_sources"][0]["objects"]
    assert rows[0]["exact_expression"]=="xy != yx"
    assert rows[0]["assumptions"]==["ordered cells"]
    assert rows[0]["declared_status"]=="EXECUTED_EXACT"
    assert rows[0]["proof_executed_by_extractor"] is False

def test_lean_declaration_is_not_pretended_compiled():
    src="theorem ordered_ers : AB = P⁴ := by\n  simp\n"
    tree,raw,sha=fixture_tree(src,path="formal/ordered.lean")
    objects=extract_proof_candidates(tree,fetch=get_for(raw,sha))["extracted_sources"][0]["objects"]
    assert objects[0]["identifier"]=="ordered_ers"
    assert objects[0]["proof_executed_by_extractor"] is False

def test_shared_blobs_are_not_fetched_twice_but_refs_remain():
    tree,raw,sha=fixture_tree("# Module 0 — Master\nxy==yx\n",repeat=True)
    hits=[]
    def fetch(url):
        hits.append(url)
        return get_for(raw,sha)(url)
    result=extract_proof_candidates(tree,fetch=fetch)
    assert len(hits)==1
    assert result["extracted_source_count"]==2

def test_blob_mismatch_rejected():
    tree,raw,sha=fixture_tree("# Module 0 — Master")
    with pytest.raises(ProofExtractionError,match="SOURCE_BLOB_IDENTITY_MISMATCH"):
        extract_proof_candidates(tree,fetch=lambda url:{"encoding":"base64",
            "content":base64.b64encode(b"tampered").decode()})

def test_limits_and_unavailable_sources_report_open():
    tree,raw,sha=fixture_tree("# Module 0 — Master")
    skipped=extract_proof_candidates(tree,fetch=get_for(raw,sha),max_bytes=3)
    assert skipped["skipped_blobs"][0]["reason"]=="BYTE_LIMIT"
    failed=extract_proof_candidates(tree,fetch=lambda url: (_ for _ in ()).throw(OSError("network")))
    assert failed["skipped_blobs"][0]["reason"]=="FETCH_UNAVAILABLE"
    assert failed["content_coverage_complete"] is False

def test_truncated_tree_stays_incomplete():
    tree,raw,sha=fixture_tree("# Module 0 — Master")
    tree["candidate_results_truncated"]=True
    result=extract_proof_candidates(tree,fetch=get_for(raw,sha))
    assert result["source_tree_report_truncated"] is True
    assert result["content_coverage_complete"] is False

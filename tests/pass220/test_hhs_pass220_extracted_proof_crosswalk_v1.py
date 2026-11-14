"""Crosswalk must not equate source overlap with proof execution."""
from __future__ import annotations
import pytest
from hhs_runtime.hhs_pass220_extracted_proof_crosswalk_v1 import crosswalk, ProofCrosswalkError

REGISTRY={"lemmas":[{"id":"L1","statement":"AB=P⁴","assumptions":["typed AB"],
                     "dependencies":[],"status":"EXECUTED_EXACT"}]}
LANE={"constructors":[{"node_id":"ctor:1","name":"ordered_ers",
                       "hash216":"a"*216,"source_path":"formal/ordered.lean"}]}

def source(objects,blob="b"*40,ref="branch:main",path="formal/lemmas/LEMMA_CORPUS.json"):
    return {"repository":"danonbrez/Holofractal_Harmonicode","path":path,
            "git_blob":blob,"commit":"c"*40,"ref":ref,"objects":objects}

def extract(*sources):
    return {"schema":"HHS_PASS220_SOURCE_BOUND_PROOF_EXTRACTION_V1",
            "extracted_sources":list(sources),"skipped_blobs":[],
            "source_tree_report_truncated":False,"source_tree_errors":[]}

def lemma(statement="AB=P⁴"):
    return {"kind":"REGISTERED_LEMMA","identifier":"L1",
            "exact_expression":statement,"assumptions":["typed AB"],
            "dependencies":[],"declared_status":"EXECUTED_EXACT",
            "source_locator":{"json_pointer":"/lemmas/0/statement"}}

def test_exact_recorded_lemma_does_not_prove_it():
    r=crosswalk(extract(source([lemma()])),lemma_registry=REGISTRY,lane5_projection=LANE)
    row=r["source_records"][0]
    assert row["registry_relation"]=="EXACT_RECORDED_STATEMENT_MATCH"
    assert row["registry_declared_status"]=="EXECUTED_EXACT"
    assert row["proof_executed_by_crosswalk"] is False
    assert r["proof_equivalence_verified"] is False
    assert r["negative_existence_claim_authorized"] is False

def test_different_lemma_text_preserves_both_versions():
    r=crosswalk(extract(source([lemma()]),source([lemma("BA=−P⁴")],blob="d"*40,ref="pr:911")),
                lemma_registry=REGISTRY,lane5_projection=LANE)
    assert r["source_records"][1]["registry_relation"]=="REGISTERED_ID_SOURCE_DIVERGENCE"
    assert r["lemma_source_conflicts"][0]["variant_count"]==2
    assert {x["ref"] for x in r["lemma_source_conflicts"][0]["source_occurrences"]}=={"branch:main","pr:911"}

def test_constructor_name_is_candidate_not_equivalence():
    obj={"kind":"FORMAL_DECLARATION","identifier":"ordered_ers","source_locator":{"start_line":3}}
    r=crosswalk(extract(source([obj],path="formal/ordered.lean")),
                lemma_registry=REGISTRY,lane5_projection=LANE)
    candidate=r["source_records"][0]["lane5_constructor_candidates"][0]
    assert candidate["same_path"] is True
    assert r["source_records"][0]["native_constructor_equivalence_verified"] is False

def test_course_module_variants_are_not_silently_merged():
    def course(expression):
        return {"kind":"COURSE_MODULE","identifier":72,
                "equation_candidates":[{"line":2,"exact_text":expression}]}
    r=crosswalk(extract(source([course("AB=P⁴")],path="docs/a.md"),
                         source([course("BA=−P⁴")],blob="d"*40,ref="pr:911",path="docs/b.md")),
                lemma_registry=REGISTRY,lane5_projection=LANE)
    assert r["course_source_variants"][0]["distinct_equation_candidate_lists"]==2

def test_empty_results_do_not_assert_absence():
    r=crosswalk(extract(),lemma_registry=REGISTRY,lane5_projection=LANE)
    assert r["extracted_record_count"]==0
    assert r["negative_existence_claim_authorized"] is False

def test_invalid_registry_fails_closed():
    with pytest.raises(ProofCrosswalkError,match="LEMMA_REGISTRY_DUPLICATE_ID"):
        crosswalk(extract(),lemma_registry={"lemmas":REGISTRY["lemmas"]*2},lane5_projection=LANE)

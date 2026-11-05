#!/usr/bin/env python3
"""Read-only course/proof-corpus crosswalk validator; no canonical runtime mutation."""
from __future__ import annotations
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COURSE = ROOT / "docs/course/HARMONICODE_Algebra_Course.md"
REGISTRY = ROOT / "contracts/pass220/HARMONICODE_COURSE_PROOF_CORPUS_CROSSWALK_V1.json"
PATTERN = re.compile(r"^#{1,4}\s+(?:Module|MODULE)\s+(\d+)([^\n]*)", re.MULTILINE)

def validate() -> dict:
    course = COURSE.read_text(encoding="utf-8")
    corpus = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert corpus["schema"] == "HHS_HARMONICODE_COURSE_PROOF_CORPUS_CROSSWALK_V1"
    heading = [(int(m.group(1)), m.group(0)) for m in PATTERN.finditer(course)]
    assert len(heading) == 124, ("MODULE_COUNT", len(heading))
    assert [i for i, _ in heading] == list(range(124)), "MODULE_ORDER_OR_DUPLICATE"
    indexed = corpus["modules"]
    assert len(indexed) == 124, "INDEX_COUNT"
    assert all(row["number"] == i and row["id"] == f"HHC-M{i:03d}" and
               row["source_heading"] == heading[i][1] for i, row in enumerate(indexed)), "INDEX_DRIFT"
    expected_blob = corpus["source"]["git_blob_sha"]
    actual_blob = subprocess.check_output(["git", "hash-object", "--", str(COURSE)],
                                          cwd=ROOT, text=True).strip()
    assert expected_blob == actual_blob, "SOURCE_BLOB_DRIFT"
    q4 = corpus["module123"]
    assert q4["native_q4_semantics"] == "OPEN"
    assert q4["new_lane5_execution"] == "NOT_EXECUTED"
    assert q4["proof_promotion"] is False
    assert q4["commutative_collapse_allowed"] is False
    assert q4["witnesses"]["whole_tone_stabilizer_size"] == 6
    assert q4["witnesses"]["whole_tone_distinct_transpositions"] == 2
    assert q4["witnesses"]["q144_address_return"] == "144/144"
    assert q4["witnesses"]["h36_address_return"] == "5184/5184"
    assert "Q₄" in course and "u¹⁴⁴" in course, "Q4_SOURCE_MISSING"
    assert all(not row["proof_admitted"] for row in indexed), "UNAUTHORIZED_PROOF_PROMOTION"
    assert not any(corpus["authority"].values()), "UNAUTHORIZED_AUTHORITY"
    for relation in corpus["crosswalk"]:
        assert 0 <= relation["course_module"] <= 123
        assert relation["proof_equivalence"] is False
        assert relation["relation"] in {"STRUCTURAL_OVERLAP_CANDIDATE", "METHOD_OVERLAP_CANDIDATE"}
    assert corpus["corpora"]["openai_revision"] == "adc7f1241b42e322a6451854ab7e4b4c146bf78a"
    for key in ("hhs_lemma", "hhs_axiom", "whitepaper_source_freeze",
                "openai_i078", "openai_i079", "openai_i080", "openai_i081"):
        assert (ROOT / corpus["corpora"][key]).is_file(), ("CORPUS_REFERENCE_MISSING", key)
    return {"status":"PASS", "module_coverage":"124/124", "source_blob":actual_blob,
            "openai_relation":"CANDIDATE_ONLY", "native_q4":"OPEN"}

if __name__ == "__main__":
    print(json.dumps(validate(), sort_keys=True))

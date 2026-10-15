from copy import deepcopy
from pathlib import Path
import pytest
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import (
    build_corpus_index, require_native_proof_binding, ProofCorpusError,
)

def test_full_corpus_index_is_source_complete_and_fail_closed():
    result=build_corpus_index()
    assert result["file_count"]==70
    assert sum(x["path"].startswith("whitepapers/") for x in result["files"])==17
    assert sum(x["path"].startswith("docs/whitepapers/") for x in result["files"])==53
    assert any(x["path"].endswith(".md ") for x in result["files"])
    assert all(x["content_sha256"] and not x["native_admission_authority"] for x in result["files"])
    assert result==build_corpus_index()
    with pytest.raises(ProofCorpusError,match="NOT_ADMITTED"):
        require_native_proof_binding(result["files"][0],{})

def test_source_mutation_rejected_and_original_preserved(tmp_path,monkeypatch):
    from hhs_runtime import hhs_pass220_whitepaper_corpus_ingress_v1 as mod
    freeze=Path(mod.FREEZE)
    original=mod.json.loads(freeze.read_text("utf-8"))
    tampered=deepcopy(original)
    tampered["files"][0]["git_blob_sha"]="0"*40
    fake=tmp_path/"freeze.json"
    fake.write_text(mod.json.dumps(tampered),encoding="utf-8")
    monkeypatch.setattr(mod,"FREEZE",fake)
    with pytest.raises(ProofCorpusError,match="SOURCE_BLOB_CHANGED"):
        build_corpus_index()

def test_harmonicode_algebra_course_source_semantics_are_frozen():
    from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import build_corpus_index
    path="whitepapers/Harmonicode Algebra - Course"
    source=Path(path).read_text(encoding="utf-8")
    index=build_corpus_index()
    record=next(x for x in index["files"] if x["path"]==path)
    assert record["byte_count"]==Path(path).stat().st_size
    assert "`==` is a gate" in source
    assert "`n/d` is the rank-1 tensor circuit" in source
    assert "bypasses at gain exactly 1" in source
    assert all(f"MODULE {i} " in source for i in range(13))
    assert not record["native_admission_authority"]

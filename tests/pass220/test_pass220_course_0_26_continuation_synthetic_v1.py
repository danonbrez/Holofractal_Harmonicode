"""Dependency-scoped 0–26 course continuation tests using synthetic frozen fixtures."""
from hashlib import sha256
import pytest
import hhs_runtime.hhs_pass220_course_module_gate_provenance_v1 as module
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError


def _fixture(tmp_path, monkeypatch, continuation_indices=range(13, 27)):
    original = (
        "The notation: `==` is a gate; `n/d` is the rank-1 tensor circuit; "
        "HNAN bypasses at gain exactly 1.\n"
        + "".join(f"MODULE {i} — Historical {i}\nOriginal identity {i}\n"
                  for i in range(13))
    )
    extension = (
        "# Additive course continuation\n"
        + "".join(f"MODULE {i} — Continuation {i}\nNew relationship {i}\n"
                  for i in continuation_indices)
    )
    (tmp_path / module.SOURCE).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / module.CONTINUATION).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / module.SOURCE).write_text(original, encoding="utf-8")
    (tmp_path / module.CONTINUATION).write_text(extension, encoding="utf-8")
    original_sha = sha256(original.encode("utf-8")).hexdigest()
    monkeypatch.setattr(module, "build_dependency_graph", lambda _: {
        "nodes": [{"source": module.SOURCE, "source_sha256": original_sha}]
    })
    return original_sha


def test_additive_inventory_keeps_frozen_source_identity(tmp_path, monkeypatch):
    original_sha = _fixture(tmp_path, monkeypatch)
    inventory = module.course_module_gate_inventory(tmp_path)
    assert inventory["module_count"] == 27
    assert [x["index"] for x in inventory["ordered_modules"]] == list(range(27))
    assert inventory["source_sha256"] == original_sha
    assert all(x["source_sha256"] == original_sha
               for x in inventory["ordered_modules"][:13])
    assert all(x["source_sha256"] == inventory["continuation_source_sha256"]
               for x in inventory["ordered_modules"][13:])
    assert not inventory["whole_course_proved"]
    assert not inventory["hash216_minted"]


def test_missing_module_in_continuation_fails_closed(tmp_path, monkeypatch):
    _fixture(tmp_path, monkeypatch, range(13, 26))
    with pytest.raises(ProofCorpusError, match="COURSE_CONTINUATION_MODULE_BOUNDARY_DRIFT"):
        module.course_module_gate_inventory(tmp_path)


def test_reordered_continuation_fails_closed(tmp_path, monkeypatch):
    _fixture(tmp_path, monkeypatch, [14, 13, *range(15, 27)])
    with pytest.raises(ProofCorpusError, match="COURSE_CONTINUATION_MODULE_BOUNDARY_DRIFT"):
        module.course_module_gate_inventory(tmp_path)


def test_changed_legacy_source_fails_closed(tmp_path, monkeypatch):
    _fixture(tmp_path, monkeypatch)
    target = tmp_path / module.SOURCE
    target.write_bytes(target.read_bytes() + b"changed")
    with pytest.raises(ProofCorpusError, match="COURSE_SOURCE_IDENTITY_MISMATCH"):
        module.course_module_gate_inventory(tmp_path)

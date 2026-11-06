"""Dependency-scoped tests for the additive corpus constraint preflight."""
from fractions import Fraction
from pathlib import Path
import pytest

from hhs_runtime.pass220.atomic_sprite_whitepaper_gate_v1 import (
    CorpusConstraintError, corpus_snapshot, bind_global_parameters,
)


def fixture_tree(tmp_path: Path):
    for dirname in ("whitepapers", "docs/whitepapers"):
        p = tmp_path / dirname
        p.mkdir(parents=True)
        (p / "reference.md").write_text("verbatim exact source\n", encoding="utf-8")
    return tmp_path


def binding(value=Fraction(7, 2), role="NATIVE_EXACT_CANDIDATE", status="EXECUTED_EXACT"):
    return {"value": value, "kind": "ATOMIC_MASS_NUMBER", "status": status,
            "role": role, "constraint_id": "PASS131_ATOMIC_IDENTITY",
            "source_paths": ["whitepapers/reference.md", "docs/whitepapers/reference.md"]}


def admit(tmp_path, params):
    return bind_global_parameters(tmp_path, params,
                                  expected_bundle_sha256=corpus_snapshot(tmp_path)["bundle_sha256"])


def test_binds_two_corpora_and_exact_fraction(tmp_path):
    root = fixture_tree(tmp_path)
    result = admit(root, {"mass": binding()})
    assert result["status"] == "CORPUS_BOUND_CANDIDATE_ONLY"
    assert len(result["corpus_roots"]) == 2
    assert result["parameters"]["mass"]["value"] == {"numerator": 7, "denominator": 2}
    assert not result["canonical_vm81_mutation_authority"]
    assert not result["equation_semantics_proven_by_this_gate"]
    assert result == admit(root, {"mass": binding()})


def test_reject_stale_corpus_root(tmp_path):
    root = fixture_tree(tmp_path)
    old = corpus_snapshot(root)["bundle_sha256"]
    (root / "docs/whitepapers/reference.md").write_text("changed", encoding="utf-8")
    with pytest.raises(CorpusConstraintError, match="STALE_OR_UNBOUND"):
        bind_global_parameters(root, {"mass": binding()}, expected_bundle_sha256=old)


@pytest.mark.parametrize("invalid", [
    {"value": 1.2},
    {"status": "REFERENCE_ONLY"},
    {"source_paths": []},
    {"source_paths": ["../unbound.md"]},
    {"role": "CANONICAL_MUTATION"},
    {"kind": ""},
])
def test_invalid_bindings_rejected(tmp_path, invalid):
    root = fixture_tree(tmp_path)
    item = binding()
    item.update(invalid)
    with pytest.raises(CorpusConstraintError):
        admit(root, {"parameter": item})


def test_reference_projection_allowed_but_noncanonical(tmp_path):
    root = fixture_tree(tmp_path)
    v = admit(root, {"draw_radius": binding(1.25, "PROJECTION_ONLY", "REFERENCE_ONLY")})
    assert v["parameters"]["draw_radius"]["value"] == {"projection_float": "1.25"}


def test_nested_float_rejected_in_canonical_role(tmp_path):
    root = fixture_tree(tmp_path)
    with pytest.raises(CorpusConstraintError, match="FLOAT_CANONICAL_REJECTED"):
        admit(root, {"atom": binding({"mass": [1, {"phase": 0.5}]})})


def test_added_corpus_file_changes_root(tmp_path):
    root = fixture_tree(tmp_path)
    old = corpus_snapshot(root)["bundle_sha256"]
    (root / "whitepapers" / "new.md").write_text("new source")
    assert corpus_snapshot(root)["bundle_sha256"] != old


def test_missing_corpus_rejected(tmp_path):
    with pytest.raises(CorpusConstraintError, match="CORPUS_MISSING"):
        corpus_snapshot(tmp_path)

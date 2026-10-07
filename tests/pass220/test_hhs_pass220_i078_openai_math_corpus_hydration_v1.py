from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass220_i078_openai_math_corpus_hydration_v1 import (
    EXPECTED_HHS_BASE,
    EXPECTED_SOURCE_REVISION,
    I078HydrationError,
    build_candidate_graph,
    load_dataset,
)


def test_frozen_extraction_counts_and_revision() -> None:
    data = load_dataset()
    source = data["source"]
    assert source["immutable_revision"] == EXPECTED_SOURCE_REVISION
    assert source["manuscript_count"] == 722
    assert source["family_count"] == 372
    assert source["formalized_source_count"] == 162
    assert source["formalization_main_result_count"] == 185
    assert source["formalization_unique_lean_file_count"] == 180
    assert source["lean_toolchain"] == "leanprover/lean4:v4.34.1"
    assert source["formalization_review_status"] == "unchecked"
    assert data["hhs_reference"]["immutable_revision"] == EXPECTED_HHS_BASE
    assert data["hhs_reference"]["frozen_path_vocabulary_count"] == 2639


def test_conservative_novelty_analysis_is_frozen() -> None:
    data = load_dataset()
    assert data["summary"]["manuscript_classes"] == {
        "HIGH_PATH_OVERLAP": 110,
        "MIXED_PATH_OVERLAP": 290,
        "NOVELTY_CANDIDATE": 322,
    }
    assert data["summary"]["family_classes"] == {
        "HIGH_PATH_OVERLAP": 45,
        "MIXED_PATH_OVERLAP": 145,
        "NOVELTY_CANDIDATE": 182,
    }
    assert data["summary"]["formalized_source_classes"] == {
        "HIGH_PATH_OVERLAP": 34,
        "MIXED_PATH_OVERLAP": 74,
        "NOVELTY_CANDIDATE": 54,
    }


def test_structural_overlap_anchors_are_preserved_without_lineage_claim() -> None:
    data = load_dataset()
    anchors = {row["anchor_id"]: row for row in data["structural_overlap_anchors"]}
    nine = anchors["OPENAI_MATH_EUCLIDEAN_RAMSEY_3X3_9X9_SYMBOLIC_TENSOR"]
    assert nine["family_id"] == "172"
    assert "Index = Fin 3 x Fin 3" in nine["observed_relations"]
    assert any("9 x 9" in item for item in nine["observed_relations"])
    assert nine["lineage_claim"] is False

    mod72 = anchors["OPENAI_MATH_DIRICHLETL_72_CONDUCTOR"]
    assert mod72["family_id"] == "003"
    assert any("72" in item for item in mod72["observed_relations"])
    assert mod72["lineage_claim"] is False


def test_candidate_graph_hydrates_all_metadata_and_is_deterministic() -> None:
    first = build_candidate_graph()
    second = build_candidate_graph()
    assert first == second
    assert first["graph_node_count"] == 1442
    assert first["graph_edge_count"] == 1069
    assert len(first["graph_sha256"]) == 64
    assert len(first["candidate_hash72"]) == 72
    assert len(first["formalized_novelty_candidates"]) == 54
    assert first["candidate_only"] is True
    assert first["truth_promotion"] is False
    assert first["canonical_learning_commit_invoked"] is False
    assert first["vm81_mutation_invoked"] is False
    assert first["canonical_hash72_minted"] is False
    assert first["canonical_hash216_minted"] is False
    assert first["canonical_persistence_invoked"] is False


def test_dataset_retains_metadata_not_verbatim_corpus() -> None:
    data = load_dataset()
    serialized = json.dumps(data, sort_keys=True).lower()
    for forbidden in (
        '"abstract":',
        '"abstracts":',
        '"full_text":',
        '"paper_text":',
        '"manuscript_text":',
        '"pdf_bytes":',
        '"lean_source_body":',
        '"source_text":',
    ):
        assert forbidden not in serialized
    assert data["extraction_policy"]["titles_and_structural_metadata_only"] is True
    assert data["extraction_policy"]["abstracts_retained"] is False
    assert data["extraction_policy"]["manuscript_body_retained"] is False
    assert data["extraction_policy"]["pdf_bytes_retained"] is False
    assert data["extraction_policy"]["lean_source_bodies_retained"] is False


def _write(tmp_path: Path, value: dict) -> Path:
    path = tmp_path / "dataset.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_revision_tamper_fails_closed(tmp_path: Path) -> None:
    data = copy.deepcopy(load_dataset())
    data["source"]["immutable_revision"] = "0" * 40
    with pytest.raises(I078HydrationError, match="SOURCE_REVISION"):
        load_dataset(_write(tmp_path, data))


def test_verbatim_retention_tamper_fails_closed(tmp_path: Path) -> None:
    data = copy.deepcopy(load_dataset())
    data["families"][0]["abstract"] = "forbidden retained corpus body"
    with pytest.raises(I078HydrationError, match="VERBATIM_RETENTION"):
        load_dataset(_write(tmp_path, data))


def test_authority_drift_fails_closed(tmp_path: Path) -> None:
    data = copy.deepcopy(load_dataset())
    data["authority"]["canonical_persistence_invoked"] = True
    with pytest.raises(I078HydrationError, match="AUTHORITY_DRIFT"):
        load_dataset(_write(tmp_path, data))

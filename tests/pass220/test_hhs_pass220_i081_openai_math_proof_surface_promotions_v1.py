from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass220_i081_openai_math_proof_surface_promotions_v1 import (
    EXPECTED_PROMOTION_COUNT,
    I081PromotionError,
    build_overlay_receipt,
    invoke_promoted_constructor,
    list_promotions,
    load_registry,
    validate_active_partition,
)


def test_all_promotions_are_source_bound_and_formal() -> None:
    registry = load_registry()
    assert len(registry["promotions"]) == EXPECTED_PROMOTION_COUNT == 17
    assert all(row["documentation"]["source_listed"] is True for row in registry["promotions"])
    assert all(row["comparator"]["admitted_theorem_names"] for row in registry["promotions"])
    assert all(
        row["authority"]["external_formal_proof_bound"] is True
        for row in registry["promotions"]
    )
    assert all(
        row["authority"]["canonical_truth_promotion"] is False
        for row in registry["promotions"]
    )


def test_active_partition_is_exact() -> None:
    assert validate_active_partition() == {
        "inherited_theorem_count": 54,
        "inherited_hold_count": 268,
        "promoted_count": 17,
        "active_theorem_count": 71,
        "active_hold_count": 251,
        "coverage_gap": 0,
        "duplicate_assignment_count": 0,
        "complete": True,
    }


def test_star_height_four_uses_explicit_stronger_result_relation() -> None:
    registry = load_registry()
    row = next(
        item
        for item in registry["promotions"]
        if item["source_title"] == "Generalized Star Height at Most Four"
    )
    assert row["proof_relation"] == "DOC_EXPLICIT_STRONGER_FORMAL_RESULT_IMPLIES_SOURCE"
    assert "bound of three" in row["relation_note"]
    assert row["comparator"]["admitted_theorem_names"] == [
        "OAI.GeneralizedStarHeight.main"
    ]


def test_overlay_receipt_is_deterministic() -> None:
    first = build_overlay_receipt()
    second = build_overlay_receipt()
    assert first == second
    assert len(first["overlay_sha256"]) == 64
    assert len(first["candidate_hash72"]) == 72
    assert first["candidate_hash72"] == first["replay_hash72"]
    assert first["partition"]["active_theorem_count"] == 71
    assert first["partition"]["active_hold_count"] == 251
    assert first["canonical_truth_promotion"] is False


def test_every_promoted_constructor_is_callable_and_distinct() -> None:
    registry = load_registry()
    ids = list_promotions(registry)
    assert len(ids) == 17
    receipts = set()
    for index, constructor_id in enumerate(ids):
        result = invoke_promoted_constructor(
            constructor_id,
            {"test_index": index, "role": "I081_PROMOTION_TEST"},
            registry=registry,
        )
        assert result["candidate_hash72"] == result["replay_hash72"]
        assert len(result["candidate_hash72"]) == 72
        assert result["external_formal_proof_bound"] is True
        assert result["source_claim_formal_support"] is True
        assert result["candidate_only"] is True
        assert result["canonical_truth_promotion"] is False
        assert result["execution_authority"] is False
        receipts.add(result["candidate_hash72"])
    assert len(receipts) == 17


def test_unadmitted_proof_declaration_fails_closed() -> None:
    constructor_id = list_promotions()[0]
    with pytest.raises(I081PromotionError, match="PROOF_DECLARATION_NOT_ADMITTED"):
        invoke_promoted_constructor(
            constructor_id,
            proof_declaration="OAI.Fake.unbound",
        )


def _write(tmp_path: Path, value: dict) -> Path:
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_document_identity_tamper_fails_closed(tmp_path: Path) -> None:
    registry = copy.deepcopy(load_registry())
    registry["promotions"][0]["documentation"]["blob_sha"] = "not-a-sha"
    with pytest.raises(I081PromotionError, match="DOCUMENTATION_EVIDENCE_INVALID"):
        load_registry(_write(tmp_path, registry))


def test_authority_drift_fails_closed(tmp_path: Path) -> None:
    registry = copy.deepcopy(load_registry())
    registry["promotions"][0]["authority"]["canonical_truth_promotion"] = True
    with pytest.raises(I081PromotionError, match="AUTHORITY_DRIFT"):
        load_registry(_write(tmp_path, registry))

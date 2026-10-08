from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass220_i081_latent_lean_promotion_tranche1_v1 import (
    EXPECTED_PROMOTION_COUNT,
    EXPECTED_PROOF_DECLARATION_COUNT,
    I081PromotionError,
    build_promotion_receipt,
    invoke_promoted_constructor,
    list_promoted_constructors,
    load_registry,
    validate_effective_frontier,
)


def test_exact_latent_promotions_are_frozen() -> None:
    registry = load_registry()
    assert len(registry["promotions"]) == EXPECTED_PROMOTION_COUNT == 10
    assert registry["scope"]["promoted_proof_declarations"] == EXPECTED_PROOF_DECLARATION_COUNT == 18
    assert registry["scope"]["effective_formal_theorem_constructors"] == 64
    assert registry["scope"]["effective_hold_claim_constructors"] == 258
    assert registry["scope"]["effective_total_constructor_coverage"] == 322
    assert registry["scope"]["coverage_gap"] == 0


def test_partial_formalizations_remain_hold() -> None:
    registry = load_registry()
    partials = registry["partial_formalizations_retained_on_hold"]
    assert len(partials) == 3
    assert all(row["status"] == "REMAIN_HOLD" for row in partials)
    assert all(row["theorem_truth_authority"] is False for row in partials)


def test_effective_frontier_partition() -> None:
    assert validate_effective_frontier() == {
        "effective_theorem_count": 64,
        "effective_hold_count": 258,
        "coverage_total": 322,
        "coverage_gap": 0,
        "partial_formalization_hold_count": 3,
        "complete": True,
    }


def test_every_promoted_constructor_is_callable_and_replays() -> None:
    registry = load_registry()
    ids = list_promoted_constructors(registry)
    assert len(ids) == 10
    receipts = set()
    for index, constructor_id in enumerate(ids):
        result = invoke_promoted_constructor(
            constructor_id,
            {"test_index": index, "role": "I081_PROMOTION_TEST"},
            registry=registry,
        )
        assert result["candidate_hash72"] == result["replay_hash72"]
        assert len(result["candidate_hash72"]) == 72
        assert result["proof_surface_bound"] is True
        assert result["truth_promotion"] is False
        assert result["candidate_only"] is True
        receipts.add(result["candidate_hash72"])
    assert len(receipts) == 10


def test_explicit_admitted_declaration_selection() -> None:
    registry = load_registry()
    multi = next(row for row in registry["promotions"] if row["proof_surface_count"] > 1)
    declaration = multi["proof_surfaces"][-1]["theorem_declaration"]
    result = invoke_promoted_constructor(
        multi["promoted_constructor_id"],
        {"x": "typed"},
        theorem_declaration=declaration,
        registry=registry,
    )
    assert result["theorem_declaration"] == declaration


def test_promotion_receipt_is_deterministic() -> None:
    first = build_promotion_receipt()
    second = build_promotion_receipt()
    assert first == second
    assert len(first["overlay_sha256"]) == 64
    assert len(first["candidate_hash72"]) == 72
    assert first["candidate_hash72"] == first["replay_hash72"]


def _write(tmp_path: Path, value: dict) -> Path:
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_partial_cannot_be_promoted_by_status_tamper(tmp_path: Path) -> None:
    registry = copy.deepcopy(load_registry())
    registry["partial_formalizations_retained_on_hold"][0]["status"] = "PROMOTED"
    with pytest.raises(I081PromotionError, match="PARTIAL_STATUS_DRIFT"):
        load_registry(_write(tmp_path, registry))


def test_scope_doc_identity_is_required(tmp_path: Path) -> None:
    registry = copy.deepcopy(load_registry())
    registry["promotions"][0]["formalization_scope_doc"]["sha"] = ""
    with pytest.raises(I081PromotionError, match="SCOPE_DOC_BINDING_MISSING"):
        load_registry(_write(tmp_path, registry))


def test_unadmitted_theorem_declaration_fails_closed() -> None:
    constructor_id = list_promoted_constructors()[0]
    with pytest.raises(I081PromotionError, match="THEOREM_DECLARATION_NOT_ADMITTED"):
        invoke_promoted_constructor(
            constructor_id,
            theorem_declaration="OAI.Fake.not_admitted",
        )

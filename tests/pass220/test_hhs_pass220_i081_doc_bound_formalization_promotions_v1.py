from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass220_i081_doc_bound_formalization_promotions_v1 import (
    I081PromotionError,
    build_registry_receipt,
    invoke_partial_binding,
    invoke_promoted_constructor,
    load_registry,
    validate_active_frontier,
)


def test_priority_doc_audit_counts() -> None:
    registry = load_registry()
    scope = registry["audit_scope"]
    assert scope["priority_family_count"] == 20
    assert scope["exact_doc_bound_hold_sources"] == 25
    assert scope["full_main_claim_promotions"] == 16
    assert scope["partial_formalization_bindings"] == 9
    assert scope["active_theorem_constructors_after_i081"] == 70
    assert scope["active_hold_constructors_after_i081"] == 252
    assert scope["active_frontier_total"] == 322
    assert scope["coverage_gap"] == 0


def test_active_frontier_is_exact() -> None:
    assert validate_active_frontier() == {
        "i079_theorem_constructors": 54,
        "i081_promotions": 16,
        "active_theorem_constructors": 70,
        "active_hold_constructors": 252,
        "partial_formalization_bindings": 9,
        "frontier_total": 322,
        "coverage_gap": 0,
    }


def test_registry_receipt_replays() -> None:
    first = build_registry_receipt()
    second = build_registry_receipt()
    assert first == second
    assert len(first["registry_sha256"]) == 64
    assert len(first["candidate_hash72"]) == 72
    assert first["candidate_hash72"] == first["replay_hash72"]
    assert first["canonical_hash72_minted"] is False
    assert first["canonical_hash216_minted"] is False


def test_every_promoted_constructor_is_callable() -> None:
    registry = load_registry()
    receipts = set()
    for index, row in enumerate(registry["promotions"]):
        result = invoke_promoted_constructor(
            row["constructor_id"],
            {"test_index": index, "role": "I081_PROMOTION_TEST"},
            registry=registry,
        )
        assert result["candidate_hash72"] == result["replay_hash72"]
        assert result["external_formal_proof_authority"] is True
        assert result["independent_hhs_reproof"] is False
        assert result["truth_promotion"] is False
        assert result["vm81_mutation_invoked"] is False
        receipts.add(result["candidate_hash72"])
    assert len(receipts) == 16


def test_every_partial_binding_remains_hold() -> None:
    registry = load_registry()
    receipts = set()
    for index, row in enumerate(registry["partial_bindings"]):
        result = invoke_partial_binding(
            row["binding_id"],
            {"test_index": index, "role": "I081_PARTIAL_TEST"},
            registry=registry,
        )
        assert result["candidate_hash72"] == result["replay_hash72"]
        assert result["whole_claim_status"] == "HOLD"
        assert result["whole_claim_truth_authority"] is False
        assert result["execution_authority"] is False
        receipts.add(result["candidate_hash72"])
    assert len(receipts) == 9


def test_unadmitted_theorem_fails_closed() -> None:
    registry = load_registry()
    cid = registry["promotions"][0]["constructor_id"]
    with pytest.raises(I081PromotionError, match="THEOREM_NOT_ADMITTED"):
        invoke_promoted_constructor(
            cid,
            theorem_name="OAI.Fake.not_admitted",
            registry=registry,
        )


def _write(tmp_path: Path, value: dict) -> Path:
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_partial_cannot_gain_whole_claim_authority(tmp_path: Path) -> None:
    registry = copy.deepcopy(load_registry())
    registry["partial_bindings"][0]["whole_claim_truth_authority"] = True
    with pytest.raises(I081PromotionError, match="PARTIAL_WHOLE_CLAIM_AUTHORITY_DRIFT"):
        load_registry(_write(tmp_path, registry))


def test_promotion_authority_drift_fails_closed(tmp_path: Path) -> None:
    registry = copy.deepcopy(load_registry())
    registry["promotions"][0]["authority"]["vm81_mutation_invoked"] = True
    with pytest.raises(I081PromotionError, match="PROMOTION_AUTHORITY_DRIFT"):
        load_registry(_write(tmp_path, registry))

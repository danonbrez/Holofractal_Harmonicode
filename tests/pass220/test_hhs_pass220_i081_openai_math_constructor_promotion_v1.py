from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass220_i081_openai_math_constructor_promotion_v1 import (
    I081PromotionError,
    effective_frontier,
    invoke_partial_subconstructor,
    invoke_promoted_constructor,
    load_registry,
    require_full_promotion_for_hold,
)


def test_audit_batch_counts_and_source_identity() -> None:
    registry = load_registry()
    assert len(registry["full_promotions"]) == 4
    assert len(registry["partial_subconstructors"]) == 1
    assert len(registry["denied_full_promotions"]) == 9
    assert registry["result"]["effective_theorem_sources"] == 58
    assert registry["result"]["effective_hold_sources"] == 264
    assert all(
        row["source_slug"] == row["doc_preprint_slug"]
        for row in registry["full_promotions"]
    )
    assert registry["partial_subconstructors"][0]["source_slug"] == (
        registry["partial_subconstructors"][0]["doc_preprint_slug"]
    )


def test_effective_frontier_is_exact_partition() -> None:
    assert effective_frontier() == {
        "novelty_sources": 322,
        "effective_theorem_sources": 58,
        "effective_hold_sources": 264,
        "full_promotions": 4,
        "partial_subconstructors": 1,
        "coverage_gap": 0,
        "duplicate_assignment": 0,
        "complete": True,
    }


def test_every_full_promotion_is_callable_and_replays() -> None:
    registry = load_registry()
    receipts = set()
    for index, row in enumerate(registry["full_promotions"]):
        result = invoke_promoted_constructor(
            row["promotion_id"],
            {"audit_index": index, "binding": "I081_TEST"},
            registry=registry,
        )
        assert result["candidate_hash72"] == result["replay_hash72"]
        assert len(result["candidate_hash72"]) == 72
        assert result["proof_surface_bound"] is True
        assert result["manuscript_status"] == "FORMAL_THEOREM_CONSTRUCTOR"
        assert result["truth_promotion"] is False
        assert result["candidate_only"] is True
        receipts.add(result["candidate_hash72"])
    assert len(receipts) == 4


def test_artin_multi_declaration_selection_is_admitted() -> None:
    registry = load_registry()
    row = next(
        item for item in registry["full_promotions"]
        if item["family_id"] == "254"
    )
    selected = row["theorem_names"][-1]
    result = invoke_promoted_constructor(
        row["promotion_id"],
        proof_declaration=selected,
        registry=registry,
    )
    assert result["proof_declaration"] == selected


def test_partial_formalization_remains_hold() -> None:
    registry = load_registry()
    row = registry["partial_subconstructors"][0]
    result = invoke_partial_subconstructor(
        row["subconstructor_id"],
        {"scope": "unperturbed_gap_only"},
        registry=registry,
    )
    assert result["candidate_hash72"] == result["replay_hash72"]
    assert result["formal_subtheorem_available"] is True
    assert result["manuscript_status"] == "HOLD"
    assert result["full_source_promotion"] is False
    assert result["excluded_scope"]


def test_october_quasi_riemann_revision_cannot_reuse_september_binding() -> None:
    with pytest.raises(I081PromotionError, match="FULL_PROMOTION_NOT_SUPPORTED"):
        require_full_promotion_for_hold("HHS-OAI-HOLD-F003-B46286ACFA00")


def test_partial_source_cannot_be_misreported_as_full_promotion() -> None:
    with pytest.raises(I081PromotionError, match="PARTIAL_SCOPE_NOT_FULL_PROMOTION"):
        require_full_promotion_for_hold("HHS-OAI-HOLD-F269-041B975282B3")


def test_unadmitted_proof_declaration_fails_closed() -> None:
    registry = load_registry()
    row = registry["full_promotions"][0]
    with pytest.raises(I081PromotionError, match="PROOF_DECLARATION_NOT_ADMITTED"):
        invoke_promoted_constructor(
            row["promotion_id"],
            proof_declaration="OAI.Fake.unbound",
            registry=registry,
        )


def _write(tmp_path: Path, value: dict) -> Path:
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_source_doc_identity_tamper_fails_closed(tmp_path: Path) -> None:
    registry = copy.deepcopy(load_registry())
    registry["full_promotions"][0]["doc_preprint_slug"] = "other-source"
    with pytest.raises(I081PromotionError, match="SOURCE_DOC_IDENTITY"):
        load_registry(_write(tmp_path, registry))


def test_authority_drift_fails_closed(tmp_path: Path) -> None:
    registry = copy.deepcopy(load_registry())
    registry["authority"]["vm81_mutation_invoked"] = True
    with pytest.raises(I081PromotionError, match="AUTHORITY_DRIFT"):
        load_registry(_write(tmp_path, registry))

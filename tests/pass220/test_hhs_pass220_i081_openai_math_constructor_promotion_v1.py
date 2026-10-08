from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass220_i081_openai_math_constructor_promotion_v1 import (
    I081PromotionError,
    build_registry_receipt,
    effective_frontier,
    invoke_partial_subconstructor,
    invoke_promoted_constructor,
    load_registry,
    require_full_promotion_for_hold,
)


def test_canonical_i081_reconciles_all_open_i081_proposals() -> None:
    registry = load_registry()
    assert registry["canonical_i081"] is True
    assert registry["canonical_pr"] == 741
    assert registry["superseded_i081_prs"] == [742, 743, 744]
    assert len(registry["proposal_reconciliation"]) == 29
    assert len(registry["full_promotions"]) == 26
    assert len(registry["partial_subconstructors"]) == 13
    assert len(registry["additional_denied_full_promotions"]) == 9
    assert sum(
        row["decision"] == "PROMOTE_FULL"
        for row in registry["proposal_reconciliation"]
    ) == 26
    assert sum(
        row["decision"] == "KEEP_HOLD_PARTIAL_ONLY"
        for row in registry["proposal_reconciliation"]
    ) == 3


def test_effective_frontier_is_one_zero_gap_duplicate_free_partition() -> None:
    assert effective_frontier() == {
        "novelty_sources": 322,
        "effective_theorem_sources": 80,
        "effective_hold_sources": 242,
        "full_promotions": 26,
        "partial_subconstructors": 13,
        "coverage_gap": 0,
        "duplicate_assignment": 0,
        "complete": True,
    }


def test_every_full_promotion_is_callable_and_replays_distinctly() -> None:
    registry = load_registry()
    receipts = set()
    for index, row in enumerate(registry["full_promotions"]):
        result = invoke_promoted_constructor(
            row["promotion_id"],
            {"audit_index": index, "binding": "CANONICAL_I081_TEST"},
            registry=registry,
        )
        assert result["candidate_hash72"] == result["replay_hash72"]
        assert len(result["candidate_hash72"]) == 72
        assert result["proof_surface_bound"] is True
        assert result["manuscript_status"] == "FORMAL_THEOREM_CONSTRUCTOR"
        assert result["truth_promotion"] is False
        receipts.add(result["candidate_hash72"])
    assert len(receipts) == 26


def test_every_partial_record_stays_hold_and_replays() -> None:
    registry = load_registry()
    receipts = set()
    for index, row in enumerate(registry["partial_subconstructors"]):
        result = invoke_partial_subconstructor(
            row["subconstructor_id"],
            {"audit_index": index, "binding": "CANONICAL_I081_PARTIAL_TEST"},
            registry=registry,
        )
        assert result["candidate_hash72"] == result["replay_hash72"]
        assert result["manuscript_status"] == "HOLD"
        assert result["full_source_promotion"] is False
        assert result["excluded_scope"]
        receipts.add(result["candidate_hash72"])
    assert len(receipts) == 13


def test_conflicting_overpromotions_are_fail_closed() -> None:
    # PR #742 promoted the Laughlin stability source despite the family doc
    # explicitly excluding stability/perturbed-ground-state uniqueness.
    with pytest.raises(I081PromotionError, match="PARTIAL_SCOPE_NOT_FULL_PROMOTION"):
        require_full_promotion_for_hold("HHS-OAI-HOLD-F269-041B975282B3")
    # PR #742 silently substituted stronger related theorems for these source
    # contracts; canonical I081 requires explicit derivation wrappers instead.
    with pytest.raises(I081PromotionError, match="PARTIAL_SCOPE_NOT_FULL_PROMOTION"):
        require_full_promotion_for_hold("HHS-OAI-HOLD-F134-D79361F43851")
    with pytest.raises(I081PromotionError, match="PARTIAL_SCOPE_NOT_FULL_PROMOTION"):
        require_full_promotion_for_hold("HHS-OAI-HOLD-F256-B20DD428ED92")


def test_navier_binding_is_corrected_to_rapid_decay_surface() -> None:
    registry = load_registry()
    row = next(
        item for item in registry["full_promotions"]
        if item["source_slug"]
        == "Computation-under-Rapidly-Vanishing-Navier-Stokes-Forcing-September-27-2026"
    )
    assert [s["comparator"]["path"] for s in row["formal_surfaces"]] == [
        "lean/ComparatorChallenges/NavierStokesAlternating.json"
    ]


def test_quasi_riemann_binds_all_three_documented_surfaces() -> None:
    registry = load_registry()
    row = next(
        item for item in registry["full_promotions"]
        if item["source_slug"]
        == "The-Quasi-Riemann-Hypothesis-September-30-2026"
    )
    assert len(row["formal_surfaces"]) == 3
    assert len(row["theorem_names"]) == 3


def test_same_title_different_quasi_revision_remains_hold() -> None:
    with pytest.raises(I081PromotionError, match="FULL_PROMOTION_NOT_SUPPORTED"):
        require_full_promotion_for_hold("HHS-OAI-HOLD-F003-B46286ACFA00")


def test_unadmitted_proof_declaration_fails_closed() -> None:
    registry = load_registry()
    row = registry["full_promotions"][0]
    with pytest.raises(I081PromotionError, match="PROOF_DECLARATION_NOT_ADMITTED"):
        invoke_promoted_constructor(
            row["promotion_id"],
            proof_declaration="OAI.Fake.unbound",
            registry=registry,
        )


def test_registry_receipt_is_deterministic() -> None:
    first = build_registry_receipt()
    second = build_registry_receipt()
    assert first == second
    assert len(first["registry_sha256"]) == 64
    assert len(first["candidate_hash72"]) == 72
    assert first["candidate_hash72"] == first["replay_hash72"]
    assert first["frontier"]["coverage_gap"] == 0
    assert first["frontier"]["duplicate_assignment"] == 0


def _write(tmp_path: Path, value: dict) -> Path:
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_source_doc_identity_tamper_fails_closed(tmp_path: Path) -> None:
    registry = copy.deepcopy(load_registry())
    registry["full_promotions"][0]["doc_preprint_slug"] = "other-source"
    with pytest.raises(I081PromotionError, match="SOURCE_DOC_IDENTITY"):
        load_registry(_write(tmp_path, registry))


def test_nonexact_full_proof_relation_fails_closed(tmp_path: Path) -> None:
    registry = copy.deepcopy(load_registry())
    registry["full_promotions"][0]["proof_relation"] = "RELATED_STRONGER_RESULT"
    with pytest.raises(I081PromotionError, match="PROOF_RELATION_NOT_EXACT"):
        load_registry(_write(tmp_path, registry))


def test_authority_drift_fails_closed(tmp_path: Path) -> None:
    registry = copy.deepcopy(load_registry())
    registry["authority"]["vm81_mutation_invoked"] = True
    with pytest.raises(I081PromotionError, match="AUTHORITY_DRIFT"):
        load_registry(_write(tmp_path, registry))

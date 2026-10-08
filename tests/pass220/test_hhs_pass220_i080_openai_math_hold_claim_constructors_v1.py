from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass220_i080_openai_math_hold_claim_constructors_v1 import (
    EXPECTED_HOLD_COUNT,
    I080ConstructorError,
    build_registry_receipt,
    invoke_claim_constructor,
    list_constructors,
    load_registry,
    validate_frontier_coverage,
)


def test_all_remaining_novelty_manuscripts_have_hold_constructors() -> None:
    registry = load_registry()
    assert len(registry["constructors"]) == EXPECTED_HOLD_COUNT == 268
    assert registry["scope"]["i078_novelty_manuscripts"] == 322
    assert registry["scope"]["i079_formal_theorem_constructors"] == 54
    assert registry["scope"]["i080_hold_claim_constructors"] == 268
    assert registry["scope"]["constructor_coverage_gap"] == 0
    assert all(row["proof_surface_count"] == 0 for row in registry["constructors"])
    assert all(
        row["status"] == "HOLD_NO_CATALOGUED_MAIN_RESULT_PROOF"
        for row in registry["constructors"]
    )


def test_i079_plus_i080_exactly_partition_i078_novelty_frontier() -> None:
    coverage = validate_frontier_coverage()
    assert coverage == {
        "novelty_count": 322,
        "theorem_constructor_count": 54,
        "hold_constructor_count": 268,
        "coverage_gap": 0,
        "duplicate_assignment_count": 0,
        "complete": True,
    }


def test_registry_receipt_is_deterministic() -> None:
    first = build_registry_receipt()
    second = build_registry_receipt()
    assert first == second
    assert len(first["registry_sha256"]) == 64
    assert len(first["candidate_hash72"]) == 72
    assert first["candidate_hash72"] == first["replay_hash72"]
    assert first["hold_constructor_count"] == 268
    assert first["theorem_truth_authority"] is False
    assert first["canonical_hash72_minted"] is False
    assert first["canonical_hash216_minted"] is False


def test_every_hold_constructor_is_callable_and_distinct() -> None:
    registry = load_registry()
    ids = list_constructors(registry)
    assert len(ids) == 268
    receipts = set()
    for index, constructor_id in enumerate(ids):
        result = invoke_claim_constructor(
            constructor_id,
            {"test_index": index, "role": "HOLD_CLAIM_TEST"},
            registry=registry,
        )
        assert result["candidate_hash72"] == result["replay_hash72"]
        assert len(result["candidate_hash72"]) == 72
        assert result["status"] == "HOLD"
        assert result["proof_surface_bound"] is False
        assert result["theorem_witness"] is False
        assert result["truth_promotion"] is False
        assert result["candidate_only"] is True
        assert result["execution_authority"] is False
        receipts.add(result["candidate_hash72"])
    assert len(receipts) == 268


def test_theorem_witness_request_fails_closed() -> None:
    constructor_id = list_constructors()[0]
    with pytest.raises(I080ConstructorError, match="THEOREM_WITNESS_NOT_AVAILABLE"):
        invoke_claim_constructor(
            constructor_id,
            require_theorem_witness=True,
        )


def test_proof_declaration_injection_fails_closed() -> None:
    constructor_id = list_constructors()[0]
    with pytest.raises(I080ConstructorError, match="PROOF_DECLARATION_NOT_AVAILABLE"):
        invoke_claim_constructor(
            constructor_id,
            proof_declaration="OAI.Fake.proof",
        )


def _write(tmp_path: Path, value: dict) -> Path:
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_source_tree_identity_tamper_fails_closed(tmp_path: Path) -> None:
    registry = copy.deepcopy(load_registry())
    registry["constructors"][0]["source_tree_sha"] = "0" * 40
    with pytest.raises(I080ConstructorError, match="CONSTRUCTOR_ID_SOURCE_MISMATCH"):
        load_registry(_write(tmp_path, registry))


def test_authority_drift_fails_closed(tmp_path: Path) -> None:
    registry = copy.deepcopy(load_registry())
    registry["constructors"][0]["authority"]["proof_authority"] = True
    with pytest.raises(I080ConstructorError, match="AUTHORITY_DRIFT"):
        load_registry(_write(tmp_path, registry))

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass220_i079_openai_math_theorem_constructors_v1 import (
    EXPECTED_CONSTRUCTOR_COUNT,
    EXPECTED_PROOF_SURFACE_COUNT,
    I079ConstructorError,
    build_registry_receipt,
    invoke_constructor,
    list_constructors,
    load_registry,
)


def test_all_formalized_novelty_sources_have_constructors() -> None:
    registry = load_registry()
    assert len(registry["constructors"]) == EXPECTED_CONSTRUCTOR_COUNT == 54
    assert registry["scope"]["formalized_novelty_sources"] == 54
    assert registry["scope"]["new_source_bound_constructors"] == 54
    assert registry["scope"]["preexisting_dedicated_constructor_matches"] == 0
    assert registry["scope"]["unresolved_proof_surfaces"] == 0
    assert sum(row["proof_surface_count"] for row in registry["constructors"]) == EXPECTED_PROOF_SURFACE_COUNT == 57
    assert all(row["status"] == "NEW_IMPLEMENTED_I079" for row in registry["constructors"])
    assert all(row["proof_surfaces"] for row in registry["constructors"])


def test_registry_receipt_is_deterministic_and_candidate_only() -> None:
    first = build_registry_receipt()
    second = build_registry_receipt()
    assert first == second
    assert len(first["registry_sha256"]) == 64
    assert len(first["candidate_hash72"]) == 72
    assert first["candidate_hash72"] == first["replay_hash72"]
    assert first["constructor_count"] == 54
    assert first["proof_surface_count"] == 57
    assert first["candidate_only"] is True
    assert first["canonical_hash72_minted"] is False
    assert first["canonical_hash216_minted"] is False


def test_every_constructor_is_callable_and_replays() -> None:
    registry = load_registry()
    ids = list_constructors(registry)
    assert len(ids) == 54
    receipts = set()
    for index, constructor_id in enumerate(ids):
        result = invoke_constructor(
            constructor_id,
            {"test_index": index, "binding_role": "DEPENDENCY_SCOPED_TEST"},
            registry=registry,
        )
        assert result["constructor_id"] == constructor_id
        assert result["proof_surface_bound"] is True
        assert result["external_proof_rechecked_at_runtime"] is False
        assert result["candidate_hash72"] == result["replay_hash72"]
        assert len(result["candidate_hash72"]) == 72
        assert result["candidate_only"] is True
        assert result["truth_promotion"] is False
        assert result["vm81_mutation_invoked"] is False
        assert result["canonical_hash72_minted"] is False
        assert result["canonical_hash216_minted"] is False
        assert result["canonical_persistence_invoked"] is False
        receipts.add(result["candidate_hash72"])
    assert len(receipts) == 54


def test_explicit_proof_surface_selection() -> None:
    registry = load_registry()
    multi = next(row for row in registry["constructors"] if row["proof_surface_count"] > 1)
    declaration = multi["proof_surfaces"][-1]["declaration"]
    result = invoke_constructor(
        multi["constructor_id"],
        {"x": "opaque_typed_binding"},
        proof_declaration=declaration,
        registry=registry,
    )
    assert result["proof_declaration"] == declaration


def _write(tmp_path: Path, value: dict) -> Path:
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_unknown_constructor_fails_closed() -> None:
    with pytest.raises(I079ConstructorError, match="UNKNOWN_CONSTRUCTOR"):
        invoke_constructor("HHS-OAI-NOT-A-CONSTRUCTOR")


def test_unadmitted_proof_surface_fails_closed() -> None:
    registry = load_registry()
    constructor_id = registry["constructors"][0]["constructor_id"]
    with pytest.raises(I079ConstructorError, match="PROOF_DECLARATION_NOT_ADMITTED"):
        invoke_constructor(
            constructor_id,
            proof_declaration="OAI.Unbound.fake",
            registry=registry,
        )


def test_missing_proof_surface_fails_closed(tmp_path: Path) -> None:
    registry = copy.deepcopy(load_registry())
    registry["constructors"][0]["proof_surfaces"] = []
    registry["constructors"][0]["proof_surface_count"] = 0
    with pytest.raises(I079ConstructorError, match="PROOF_SURFACE_MISSING"):
        load_registry(_write(tmp_path, registry))


def test_authority_drift_fails_closed(tmp_path: Path) -> None:
    registry = copy.deepcopy(load_registry())
    registry["constructors"][0]["authority"]["vm81_mutation_invoked"] = True
    with pytest.raises(I079ConstructorError, match="AUTHORITY_DRIFT"):
        load_registry(_write(tmp_path, registry))

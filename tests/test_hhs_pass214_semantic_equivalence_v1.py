from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import subprocess

import pytest

from hhs_backend.runtime.hhs_pass214_reusable_operation_registry_v1 import (
    ReusableOperationRegistryError,
    build_registry,
)
from hhs_backend.runtime.hhs_pass214_semantic_equivalence_v1 import (
    PROOF_EXACT_PROJECTION,
    build_semantic_equivalence_reconciliation,
)

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def _result():
    return build_semantic_equivalence_reconciliation(ROOT, source_ref="HEAD")


def test_exact_head_and_frozen_runtime_are_preserved() -> None:
    result = _result()
    head = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    assert result["summary"]["source_commit"] == head
    frozen = result["summary"]["frozen_runtime"]
    assert frozen["preserved"] is True
    assert frozen["git_blob"] == "362cd6e892ae66024333b111aec83f12023fdce3"


def test_all_known_opcode_families_remain_anchored() -> None:
    anchors = _result()["summary"]["known_opcode_family_anchors"]
    assert anchors["all_satisfied"] is True
    assert anchors["observed"] == {
        "VM81_SUBSTRATE_OPCODE": 24,
        "FROZEN_HHS_IR_OPCODE": 20,
        "PASS079_NATIVE_ABI_OPCODE": 29,
        "PASS158_LLABI_NFTC_OPCODE": 36,
        "PASS213_GOVERNED_NATIVE_DISPATCH": 9,
        "VM81_BASE20_NUMERICAL_ABI": 19,
    }


def test_every_multi_identity_group_gets_a_proof_status() -> None:
    result = _result()
    groups = result["semantic_groups"]
    assert len(groups) == result["summary"]["candidate_groups"]
    assert groups
    allowed = {
        "PROVEN_EQUIVALENT",
        "PARTIALLY_PROVEN_EQUIVALENT",
        "CONFLICT_EVIDENCE_REQUIRES_MANUAL_OR_BEHAVIORAL_REVIEW",
        "UNRESOLVED_REQUIRES_BEHAVIORAL_CONFORMANCE",
    }
    assert {x["status"] for x in groups} <= allowed
    assert all(len(x["member_operation_keys"]) >= 2 for x in groups)


def test_base20_exact_projections_are_proven_not_name_inferred() -> None:
    result = _result()
    projection_edges = [
        proof
        for group in result["semantic_groups"]
        for proof in group["proofs"]
        if proof["proof_type"] == PROOF_EXACT_PROJECTION
    ]
    assert len(projection_edges) >= 19
    assert result["summary"]["explicit_projection_proof_edges"] >= 19


def test_reuse_registry_contains_only_proven_multi_member_clusters() -> None:
    result = _result()
    entries = result["reusable_operation_registry_entries"]
    assert len(entries) == result["summary"]["reusable_registry_entries"]
    assert all(x["proof_status"] == "PROVEN_EQUIVALENT_CLUSTER" for x in entries)
    assert all(len(x["member_operation_keys"]) >= 2 for x in entries)
    assert len({x["cluster_id"] for x in entries}) == len(entries)


def test_preferred_bindings_do_not_promote_projection_or_formal_surfaces() -> None:
    forbidden = {"ABI_DECLARATION_SURFACE", "FORMAL_SPECIFICATION", "BUILD_INTEGRATION"}
    for entry in _result()["reusable_operation_registry_entries"]:
        preferred = entry["preferred_binding"]
        if preferred is not None:
            assert preferred["family"] not in forbidden


def test_registry_is_discovery_only_and_never_execution_authority() -> None:
    registry = build_registry(_result())
    assert len(registry.list_bindings()) == _result()["summary"]["reusable_registry_entries"]
    with pytest.raises(ReusableOperationRegistryError, match="DISCOVERY_REGISTRY_IS_NOT_EXECUTION_AUTHORITY"):
        registry.execute("anything")


def test_isolated_candidate_coverage_is_bounded_and_actionable() -> None:
    summary = _result()["summary"]
    assert 0 <= summary["isolated_candidates_covered_by_proven_clusters"] <= summary["isolated_implementation_candidates_total"]
    actions = summary["migration_action_counts"]
    assert sum(actions.values()) == summary["reusable_registry_entries"]

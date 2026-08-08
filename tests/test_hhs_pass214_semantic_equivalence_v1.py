from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import subprocess

import pytest

from hhs_backend.runtime.hhs_pass214_reusable_operation_registry_v1 import (
    ReusableOperationRegistryError,
    build_registry,
)
from hhs_backend.runtime.hhs_pass214_semantic_equivalence_v2 import (
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


def test_base20_exact_projections_are_proven_and_not_implementation_backlog() -> None:
    result = _result()
    projection_edges = [
        proof
        for group in result["semantic_groups"]
        for proof in group["proofs"]
        if proof["proof_type"] == PROOF_EXACT_PROJECTION
    ]
    assert len(projection_edges) >= 19
    assert result["summary"]["explicit_projection_proof_edges"] >= 19
    assert result["summary"]["migration_action_counts"].get("REGISTER_EXACT_PROJECTION", 0) >= 19
    assert result["summary"]["projection_surfaces_removed_from_implementation_backlog"] >= 19


def test_every_coded_operation_has_exactly_one_registry_record() -> None:
    result = _result()
    operations = result["operation_registry_entries"]
    summary = result["summary"]
    assert len(operations) == summary["raw_operation_identities"]
    assert summary["operation_registry_entries"] == summary["raw_operation_identities"]
    keys = [x["operation_key"] for x in operations]
    assert len(keys) == len(set(keys))
    assert all(x["registry_id"].startswith("hhs.") for x in operations)


def test_shared_registry_identity_requires_proven_cluster() -> None:
    result = _result()
    cluster_ids = {x["cluster_id"] for x in result["reusable_operation_registry_entries"]}
    for operation in result["operation_registry_entries"]:
        if operation["registry_status"] == "PROVEN_EQUIVALENCE_SHARED_IDENTITY":
            assert operation["registry_id"] in cluster_ids
        else:
            assert operation["registry_id"].startswith("hhs.operation.")


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


def test_registry_is_complete_discovery_surface_and_not_execution_authority() -> None:
    result = _result()
    registry = build_registry(result)
    assert len(registry.list_bindings()) == result["summary"]["reusable_registry_entries"]
    assert len(registry.list_operations()) == result["summary"]["raw_operation_identities"]
    assert len(registry.isolation_backlog()) == result["summary"]["isolated_candidates_remaining_reusable_extraction_backlog"]
    first = registry.list_operations()[0]
    assert registry.get_operation(first.operation_key) == first
    assert first in registry.registry_members(first.registry_id)
    with pytest.raises(ReusableOperationRegistryError, match="DISCOVERY_REGISTRY_IS_NOT_EXECUTION_AUTHORITY"):
        registry.execute("anything")


def test_isolated_candidate_backlog_is_exactly_accounted() -> None:
    result = _result()
    summary = result["summary"]
    assert summary["projection_surfaces_removed_from_implementation_backlog"] >= 19
    assert summary["semantic_alias_only_isolated_records_returned_to_backlog"] > 0
    assert 0 <= summary["isolated_candidates_covered_by_proven_reuse_or_promotion"] <= summary["isolated_implementation_backlog_after_projection_filter"]
    assert summary["isolated_candidates_remaining_reusable_extraction_backlog"] == (
        summary["isolated_implementation_backlog_after_projection_filter"]
        - summary["isolated_candidates_covered_by_proven_reuse_or_promotion"]
    )
    assert len(result["unresolved_isolation_backlog"]) == summary["isolated_candidates_remaining_reusable_extraction_backlog"]
    assert all(
        row["migration_requirement"] == "REQUIRES_REUSABLE_EXTRACTION_OR_ADAPTER"
        for row in result["unresolved_isolation_backlog"]
    )

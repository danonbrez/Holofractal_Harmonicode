from __future__ import annotations

from copy import deepcopy
import pytest

from hhs_backend.runtime.hhs_pass214_authority_conflict_reconciliation_v1 import (
    CANONICAL_MUTATION_AUTHORITY,
    Pass214AuthorityReconciliationError,
    reconcile_authority_conflicts,
    validate_authority_reconciliation,
)


def symbol(ch: str) -> str:
    return ch * 64


def fixture():
    records = [
        {
            "symbol_hash216": symbol("1"),
            "path": "native_projects/compiler/apply.py",
            "entrypoint": "Compiler.apply_delta",
            "source_start_line": 10,
            "mutation_authority": "UNRESOLVED_REQUIRES_CALLABLE_CONFORMANCE",
        },
        {
            "symbol_hash216": symbol("2"),
            "path": "hhs_backend/runtime/continuation.py",
            "entrypoint": "Continuation.apply_delta",
            "source_start_line": 30,
            "mutation_authority": "INHERITED_VM81_OR_GOVERNED_AUTHORITY_CANDIDATE",
        },
    ]
    conflict = {
        "authority_conflict_hash216": symbol("a"),
        "authority_domain": "cache_retrieval_continuation",
        "normalized_entrypoint": "apply_delta",
        "member_symbol_hash216": [symbol("1"), symbol("2")],
        "member_paths": [records[0]["path"], records[1]["path"]],
        "interface_compatible": False,
        "implementation_hashes": [symbol("b"), symbol("c")],
    }
    summary = {
        "pass": 214,
        "source_commit": "d" * 40,
        "source_tree": "e" * 40,
        "coverage": {"authority_conflict_candidates": 1},
        "roots": {"authority_conflict_root_hash216": symbol("f")},
    }
    return records, [conflict], summary


def test_reconciliation_preserves_namespaces_and_single_authority():
    records, conflicts, summary = fixture()
    report = reconcile_authority_conflicts(
        authority_conflicts=conflicts,
        callable_records=records,
        compatibility_summary=summary,
    )
    assert report["all_conflicts_reconciled"] is True
    assert report["unresolved_conflict_count"] == 0
    assert report["automatic_merge_count"] == 0
    assert report["canonical_mutation_authority"] == CANONICAL_MUTATION_AUTHORITY
    assert report["namespace_identity"] == "ITERATION2_SYMBOL_HASH216"
    record = report["resolutions"][0]
    assert record["resolution_class"] == "NAMESPACE_SEPARATED_DISTINCT_INTERFACES"
    assert record["semantic_equivalence_claimed"] is False
    assert record["automatic_merger_authorized"] is False
    assert record["member_namespaces_preserved"] is True
    assert record["direct_member_authority_promotion"] is False
    assert [item["symbol_hash216"] for item in record["member_namespaces"]] == record["member_symbol_hash216"]
    assert validate_authority_reconciliation(report, compatibility_summary=summary)


def test_same_file_distinct_symbols_remain_distinct_namespaces():
    records, conflicts, summary = fixture()
    records[1]["path"] = records[0]["path"]
    records[1]["entrypoint"] = "Other.apply_delta"
    conflicts[0]["member_paths"] = [records[0]["path"], records[1]["path"]]
    report = reconcile_authority_conflicts(
        authority_conflicts=conflicts,
        callable_records=records,
        compatibility_summary=summary,
    )
    assert report["all_conflicts_reconciled"] is True
    namespaces = report["resolutions"][0]["member_namespaces"]
    assert namespaces[0]["path"] == namespaces[1]["path"]
    assert namespaces[0]["symbol_hash216"] != namespaces[1]["symbol_hash216"]


def test_same_interface_distinct_implementation_is_not_silently_merged():
    records, conflicts, summary = fixture()
    conflicts[0]["interface_compatible"] = True
    report = reconcile_authority_conflicts(
        authority_conflicts=conflicts,
        callable_records=records,
        compatibility_summary=summary,
    )
    record = report["resolutions"][0]
    assert record["resolution_class"] == "NAMESPACE_SEPARATED_DISTINCT_IMPLEMENTATIONS"
    assert record["automatic_merger_authorized"] is False
    assert record["semantic_equivalence_claimed"] is False


def test_missing_member_fails_closed():
    records, conflicts, summary = fixture()
    conflicts[0]["member_symbol_hash216"][1] = symbol("9")
    with pytest.raises(Pass214AuthorityReconciliationError, match="MEMBER_NOT_FOUND"):
        reconcile_authority_conflicts(
            authority_conflicts=conflicts,
            callable_records=records,
            compatibility_summary=summary,
        )


def test_count_mismatch_fails_closed():
    records, conflicts, summary = fixture()
    summary["coverage"]["authority_conflict_candidates"] = 2
    with pytest.raises(Pass214AuthorityReconciliationError, match="CONFLICT_COUNT_MISMATCH"):
        reconcile_authority_conflicts(
            authority_conflicts=conflicts,
            callable_records=records,
            compatibility_summary=summary,
        )


def test_tampered_resolution_root_is_rejected():
    records, conflicts, summary = fixture()
    report = reconcile_authority_conflicts(
        authority_conflicts=conflicts,
        callable_records=records,
        compatibility_summary=summary,
    )
    tampered = deepcopy(report)
    tampered["resolutions"][0]["member_namespaces"][0]["path"] = "other.py"
    with pytest.raises(Pass214AuthorityReconciliationError, match="RECORD_ROOT_MISMATCH"):
        validate_authority_reconciliation(tampered, compatibility_summary=summary)

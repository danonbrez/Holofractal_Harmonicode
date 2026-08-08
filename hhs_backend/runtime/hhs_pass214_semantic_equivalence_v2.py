"""Pass 214 semantic-equivalence reconciliation V2.

V1 established the proof graph and complete discovery registry. V2 repairs one
migration-accounting boundary found by the exact-head negative gate: proving
that two isolated implementations are semantic aliases does not itself make
either implementation reusable. Such records remain in the extraction/adapter
backlog until an existing shared implementation is reused or a shared-module
promotion is explicitly scheduled. Exact projection surfaces remain outside the
implementation-duplication backlog.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass214_cumulative_operation_census_v1 import (
    MAX_DEFAULT_BYTES,
    OperationCensusError,
    _digest,
)
from hhs_backend.runtime.hhs_pass214_semantic_equivalence_v1 import (
    PROOF_EXACT_PROJECTION,
    PROOF_EXPLICIT_SEMANTIC_ID,
    PROOF_IDENTICAL_IMPLEMENTATION,
    PROOF_PURE_FORWARDER,
    SCHEMA as V1_SCHEMA,
    build_semantic_equivalence_reconciliation as build_v1,
)

SCHEMA = "HHS_PASS_214_SEMANTIC_EQUIVALENCE_RECONCILIATION_V2"
CLASSIFICATION = "HHS_PASS_214_SEMANTIC_EQUIVALENCE_REUSE_BACKLOG_ACCOUNTING_REPAIR"

_BACKLOG = "REQUIRES_REUSABLE_EXTRACTION_OR_ADAPTER"
_PROJECTION = "PROJECTION_SURFACE_NOT_IMPLEMENTATION_BACKLOG"
_COVERED_ACTIONS = {
    "REUSE_EXISTING_SHARED_MODULE",
    "PROMOTE_TO_SHARED_MODULE_CANDIDATE",
}


def build_semantic_equivalence_reconciliation(
    repository_root: Path,
    *,
    source_ref: str = "HEAD",
    max_source_bytes: int = MAX_DEFAULT_BYTES,
) -> dict[str, Any]:
    result = build_v1(
        repository_root,
        source_ref=source_ref,
        max_source_bytes=max_source_bytes,
    )
    prior_digest = result.pop("reconciliation_sha256", None)
    result["schema"] = SCHEMA
    result["classification"] = CLASSIFICATION
    result["parent_reconciliation_schema"] = V1_SCHEMA
    result["parent_reconciliation_sha256"] = prior_digest
    result["policy"]["semantic_alias_proof_does_not_equal_shared_implementation"] = True
    result["policy"]["isolated_aliases_remain_extraction_backlog_until_reused_or_promoted"] = True

    operations = result["operation_registry_entries"]
    covered: set[str] = set()
    backlog: list[dict[str, Any]] = []
    projection_filtered: set[str] = set()

    for row in operations:
        if row["reuse_status"] != "ISOLATED_IMPLEMENTATION_CANDIDATE":
            continue
        key = str(row["operation_key"])
        requirement = str(row["migration_requirement"])
        if requirement == _PROJECTION:
            projection_filtered.add(key)
            continue
        if requirement in _COVERED_ACTIONS:
            covered.add(key)
            continue
        # A proven alias/identity is useful discovery evidence but does not
        # eliminate the application/native-project implementation itself.
        row["migration_requirement"] = _BACKLOG
        backlog.append(row)

    summary = result["summary"]
    isolated_total = int(summary["isolated_implementation_candidates_total"])
    implementation_backlog = isolated_total - len(projection_filtered)
    remaining = len(backlog)
    if remaining != implementation_backlog - len(covered):
        raise OperationCensusError(
            "SEMANTIC_V2_ISOLATION_ACCOUNTING_MISMATCH:"
            f"{remaining}!={implementation_backlog}-{len(covered)}"
        )

    summary["projection_surfaces_removed_from_implementation_backlog"] = len(projection_filtered)
    summary["isolated_implementation_backlog_after_projection_filter"] = implementation_backlog
    summary["isolated_candidates_covered_by_proven_reuse_or_promotion"] = len(covered)
    summary["isolated_candidates_remaining_reusable_extraction_backlog"] = remaining
    summary["semantic_alias_only_isolated_records_returned_to_backlog"] = sum(
        1
        for row in operations
        if row["reuse_status"] == "ISOLATED_IMPLEMENTATION_CANDIDATE"
        and row["migration_requirement"] == _BACKLOG
        and str(row["registry_status"]) == "PROVEN_EQUIVALENCE_SHARED_IDENTITY"
    )
    result["unresolved_isolation_backlog"] = sorted(
        backlog,
        key=lambda x: (
            str(x["path"]), int(x["line"]), str(x["normalized_semantic_name"]),
            str(x["operation_key"]),
        ),
    )

    if len(operations) != int(summary["raw_operation_identities"]):
        raise OperationCensusError("SEMANTIC_V2_OPERATION_REGISTRY_COVERAGE_MISMATCH")
    result["reconciliation_sha256"] = _digest(result)
    return result


def write_reconciliation(result: Mapping[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_and_validate_reconciliation(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    supplied = data.pop("reconciliation_sha256", None)
    if supplied != _digest(data):
        raise OperationCensusError("SEMANTIC_V2_RECONCILIATION_SHA256_FAILURE")
    data["reconciliation_sha256"] = supplied
    if data.get("schema") != SCHEMA:
        raise OperationCensusError("SEMANTIC_V2_RECONCILIATION_SCHEMA_MISMATCH")
    summary = data["summary"]
    if not summary["known_opcode_family_anchors"]["all_satisfied"]:
        raise OperationCensusError("SEMANTIC_V2_RECONCILIATION_ANCHOR_FAILURE")
    if summary["operation_registry_entries"] != summary["raw_operation_identities"]:
        raise OperationCensusError("SEMANTIC_V2_REGISTRY_COVERAGE_FAILURE")
    if len(data["unresolved_isolation_backlog"]) != summary["isolated_candidates_remaining_reusable_extraction_backlog"]:
        raise OperationCensusError("SEMANTIC_V2_BACKLOG_SERIALIZATION_FAILURE")
    return data

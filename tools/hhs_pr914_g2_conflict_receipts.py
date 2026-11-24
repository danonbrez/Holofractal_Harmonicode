#!/usr/bin/env python3
"""G2 conflict receipt construction and fail-closed resolution validation.

Input is explicit mechanical evidence, never inferred semantic compatibility.
This module makes no repository mutation or canonical receipt claims.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

CONTRACT_PATH = Path("contracts/architecture/HHS_PR914_G2_DEPENDENCY_CONFLICT_AND_CANDIDATE_COMPOSITION_CONTRACT_V1.json")
SHA = re.compile(r"^[0-9a-f]{40}$")
RESOLVED = {"RESOLVED_FOCUSED_VALIDATION_PASSED", "RESOLVED_VALIDATION_PENDING"}


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def _full_sha(value):
    return isinstance(value, str) and SHA.fullmatch(value) is not None


def _clean_ids(values):
    if not isinstance(values, list) or not all(isinstance(x, str) and x for x in values):
        raise ValueError("G2_RECEIPT_ENTRY_IDS_INVALID")
    if not values or len(set(values)) != len(values):
        raise ValueError("G2_RECEIPT_ENTRY_IDS_DUPLICATE_OR_EMPTY")
    return sorted(values)


def unresolved_receipt(mechanical: dict, contract: dict) -> dict:
    """Promote a sourced mechanical overlap to an explicitly unresolved receipt.

    A shared path is never classified as semantic conflict automatically.
    """
    if not isinstance(mechanical, dict):
        raise ValueError("G2_MECHANICAL_EVIDENCE_INVALID")
    kind = mechanical.get("conflict_class")
    if kind not in contract["conflict_classes"]:
        raise ValueError("G2_UNRECOGNIZED_CONFLICT_CLASS")
    members = _clean_ids(mechanical.get("entry_ids"))
    loc = mechanical.get("paths_or_requirement_ids")
    if not isinstance(loc, list) or not loc or not all(isinstance(p, str) and p for p in loc):
        raise ValueError("G2_CONFLICT_LOCATION_REQUIRED")
    heads = mechanical.get("exact_source_heads")
    if not isinstance(heads, dict) or set(heads) != set(members):
        raise ValueError("G2_CONFLICT_EXACT_HEAD_SET_MISMATCH")
    # Old mechanically observed source heads may be unknown. Never mint one.
    if any(v is not None and not _full_sha(v) for v in heads.values()):
        raise ValueError("G2_CONFLICT_SOURCE_HEAD_INVALID")
    evidence = mechanical.get("mechanical_evidence")
    if not isinstance(evidence, dict) or not evidence:
        raise ValueError("G2_CONFLICT_MECHANICAL_EVIDENCE_REQUIRED")
    identities = {k: heads[k] for k in members}
    identity = {
        "entry_ids": members, "paths_or_requirement_ids": sorted(set(loc)),
        "conflict_class": kind, "exact_source_heads": identities,
        "mechanical_evidence": evidence,
    }
    conflict_id = "G2-CONFLICT-" + sha256(_canonical(identity)).hexdigest()[:24]
    return {
        "conflict_id": conflict_id,
        "entry_ids": members,
        "exact_source_heads": identities,
        "paths_or_requirement_ids": sorted(set(loc)),
        "conflict_class": kind,
        "mechanical_evidence": evidence,
        "semantic_assessment": "UNASSESSED",
        "resolution_operation": "STOP_G2_UNRESOLVED",
        "before_blob_or_tree_identities": {},
        "after_blob_or_tree_identities": {},
        "integration_commit": None,
        "preserved_requirement_ids": [],
        "preserved_capability_ids": [],
        "nonoverlapping_behavior_disposition": "UNASSESSED_NONLOSS_RETENTION_REQUIRED",
        "frozen_and_canonical_review": None,
        "security_and_authority_review": None,
        "focused_test_receipts": [],
        "residual_risk": "SEMANTIC_AND_SOURCE_IDENTITY_REVIEW_REQUIRED",
        "review_authority": None,
        "status": "UNRESOLVED",
    }


def validate_receipt(receipt: dict, contract: dict) -> list[str]:
    """Return explicit blocker codes, even when receipt claims resolved."""
    schema = contract["conflict_receipt_schema"]
    missing = set(schema["required_fields"]) - set(receipt)
    if missing:
        raise ValueError("G2_CONFLICT_RECEIPT_MISSING_FIELDS:" + ",".join(sorted(missing)))
    if receipt["conflict_class"] not in contract["conflict_classes"]:
        raise ValueError("G2_CONFLICT_CLASS_INVALID")
    if receipt["status"] not in schema["permitted_statuses"]:
        raise ValueError("G2_CONFLICT_STATUS_INVALID")
    if receipt["resolution_operation"] not in contract["resolution_operations"]:
        raise ValueError("G2_CONFLICT_RESOLUTION_OPERATION_INVALID")
    members = _clean_ids(receipt["entry_ids"])
    heads = receipt["exact_source_heads"]
    if not isinstance(heads, dict) or set(heads) != set(members):
        raise ValueError("G2_CONFLICT_SOURCE_SET_INVALID")
    if any(s is not None and not _full_sha(s) for s in heads.values()):
        raise ValueError("G2_CONFLICT_SOURCE_IDENTITY_INVALID")
    blockers = []
    if receipt["status"] in RESOLVED:
        if not all(_full_sha(s) for s in heads.values()):
            blockers.append("G2_BLOCKED_STALE_REFS")
        if not _full_sha(receipt["integration_commit"]):
            blockers.append("G2_BLOCKED_CANDIDATE_IDENTITY_MISMATCH")
        if not receipt["before_blob_or_tree_identities"] or not receipt["after_blob_or_tree_identities"]:
            blockers.append("G2_BLOCKED_UNRESOLVED_SEMANTIC_CONFLICT")
        for field in ("preserved_requirement_ids", "preserved_capability_ids",
                      "frozen_and_canonical_review", "security_and_authority_review",
                      "review_authority"):
            if not receipt[field]:
                blockers.append("G2_BLOCKED_UNRESOLVED_SEMANTIC_CONFLICT")
        if receipt["semantic_assessment"] in (None, "", "UNASSESSED"):
            blockers.append("G2_BLOCKED_UNRESOLVED_SEMANTIC_CONFLICT")
        if receipt["nonoverlapping_behavior_disposition"] in (None, "", "UNASSESSED_NONLOSS_RETENTION_REQUIRED"):
            blockers.append("G2_BLOCKED_CAPABILITY_COVERAGE_GAP")
        if receipt["status"] == "RESOLVED_FOCUSED_VALIDATION_PASSED" and not receipt["focused_test_receipts"]:
            blockers.append("G2_BLOCKED_FOCUSED_VALIDATION_FAILED")
    else:
        blockers.append("G2_BLOCKED_UNRESOLVED_SEMANTIC_CONFLICT")
    # Security/frozen reviews must not be bypassed by a forged resolved status.
    if receipt["conflict_class"] in ("FROZEN_LAYER_IMPACT", "CANONICAL_SOURCE_IMPACT", "SECURITY_OR_AUTHORITY_CONFLICT"):
        if receipt["status"] in RESOLVED and not (
            isinstance(receipt["frozen_and_canonical_review"], dict)
            and receipt["frozen_and_canonical_review"].get("authorized") is True
            and isinstance(receipt["security_and_authority_review"], dict)
            and receipt["security_and_authority_review"].get("authorized") is True
        ):
            blockers.append("G2_BLOCKED_FROZEN_OR_CANONICAL_AUTHORITY")
    return sorted(set(blockers))


def evaluate_conflicts(mechanical_events: list[dict], contract: dict) -> dict:
    if not isinstance(mechanical_events, list):
        raise ValueError("G2_CONFLICT_EVENTS_MUST_BE_LIST")
    receipts = [unresolved_receipt(event, contract) for event in mechanical_events]
    receipts.sort(key=lambda r: r["conflict_id"])
    if len({r["conflict_id"] for r in receipts}) != len(receipts):
        raise ValueError("G2_DUPLICATE_MECHANICAL_CONFLICT")
    return {
        "schema": "HHS_PR914_G2_CONFLICT_RECEIPT_EVALUATION_V1",
        "event_count": len(receipts),
        "conflict_receipts": receipts,
        "unresolved_conflicts": [r["conflict_id"] for r in receipts],
        "input_evidence_sha256": sha256(_canonical(mechanical_events)).hexdigest(),
        "candidate_composed": False,
        "g2_complete": False,
        "blocking_reasons": ["G2_BLOCKED_UNRESOLVED_SEMANTIC_CONFLICT", "G2_BLOCKED_STALE_REFS"]
            if receipts else ["G2_BLOCKED_INCOMPLETE_GRAPH", "G2_BLOCKED_STALE_REFS"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=CONTRACT_PATH)
    parser.add_argument("--mechanical-events", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    events = json.loads(args.mechanical_events.read_text(encoding="utf-8"))
    result = evaluate_conflicts(events, contract)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()

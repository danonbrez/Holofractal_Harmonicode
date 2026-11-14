"""Pass 220: fail-closed mathematical corpus negative-claim reporting gate.

This is a report-authorization boundary, NOT a substitute for repository
discovery, nor VM81 / Hash72 / Hash216 proof or mutation authority.

The current version deliberately does NOT implement a complete cross-branch,
cross-PR enumeration witness. Consequently it never approves an absence or
unimplemented claim, regardless of caller-supplied coverage booleans. A later
revision may add externally verifiable discovery completeness evidence.
"""
from __future__ import annotations

from typing import Any, Mapping

SCHEMA = "HHS_PASS220_CORPUS_NEGATIVE_CLAIM_GATE_V1"
UNRESOLVED = "NOT_YET_LOCATED"
NEGATIVE = frozenset({
    "ABSENT", "DOES_NOT_EXIST", "UNIMPLEMENTED", "MISSING",
    "NOT_PRESENT", "NO_PROOF_EXISTS", "NO_CONSTRUCTOR_EXISTS",
    "NOT_IN_REPOSITORY",
})
ALLOWED = frozenset({"FOUND", "NOT_YET_LOCATED", "INTEGRATION_GAP_VERIFIED"})


class CorpusDiscoveryClaimError(ValueError):
    pass


def validate_claim(report: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a report; never accept a self-certified absence assertion.

    Discovery receipts and implementation evidence are independent.
    An integration gap may be reported only with concrete paths and a
    specific checked interface, without asserting that a capability is absent.
    """
    if not isinstance(report, Mapping):
        raise CorpusDiscoveryClaimError("DISCOVERY_REPORT_REQUIRED")
    obj = report.get("object")
    status = report.get("status")
    if not isinstance(obj, str) or not obj.strip() or len(obj) > 512:
        raise CorpusDiscoveryClaimError("DISCOVERY_OBJECT_REQUIRED")
    if not isinstance(status, str):
        raise CorpusDiscoveryClaimError("DISCOVERY_STATUS_REQUIRED")
    if status in NEGATIVE:
        raise CorpusDiscoveryClaimError(
            "NEGATIVE_CLAIM_REQUIRES_INDEPENDENT_COMPLETE_DISCOVERY_RECEIPT"
        )
    if status not in ALLOWED:
        raise CorpusDiscoveryClaimError("UNREGISTERED_DISCOVERY_STATUS")
    checked = report.get("checked_sources", [])
    if not isinstance(checked, list) or any(
        not isinstance(x, Mapping)
        or not isinstance(x.get("path_or_ref"), str)
        or not x["path_or_ref"].strip()
        or not isinstance(x.get("revision"), str)
        or not x["revision"].strip()
        for x in checked
    ):
        raise CorpusDiscoveryClaimError("INVALID_DISCOVERY_SOURCE_REFERENCES")
    if status == "FOUND" and not checked:
        raise CorpusDiscoveryClaimError("FOUND_REQUIRES_SOURCE_WITNESS")
    if status == "INTEGRATION_GAP_VERIFIED":
        if not checked or not isinstance(report.get("checked_interface"), str) or not report["checked_interface"].strip():
            raise CorpusDiscoveryClaimError("INTEGRATION_GAP_REQUIRES_CHECKED_INTERFACE")
        if not isinstance(report.get("failure_evidence"), str) or not report["failure_evidence"].strip():
            raise CorpusDiscoveryClaimError("INTEGRATION_GAP_REQUIRES_FAILURE_EVIDENCE")
    # Strip caller-controlled authority and completeness assertions.
    return {
        "schema": SCHEMA,
        "object": obj.strip(),
        "status": status,
        "checked_sources": [
            {"path_or_ref": x["path_or_ref"], "revision": x["revision"]}
            for x in checked
        ],
        "checked_interface": report.get("checked_interface") if status == "INTEGRATION_GAP_VERIFIED" else None,
        "failure_evidence": report.get("failure_evidence") if status == "INTEGRATION_GAP_VERIFIED" else None,
        "distributed_branch_pr_coverage_complete": False,
        "negative_existence_claim_authorized": False,
        "native_proof_executed": False,
        "vm81_mutation_authority": False,
        "hash72_hash216_minted": False,
    }


def unresolved(object_name: str, checked_sources: list[dict[str, str]] | None = None) -> dict[str, Any]:
    return validate_claim({
        "object": object_name,
        "status": UNRESOLVED,
        "checked_sources": [] if checked_sources is None else checked_sources,
    })

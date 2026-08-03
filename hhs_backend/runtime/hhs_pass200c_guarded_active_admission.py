"""Canonical production projection for Pass 200C guarded active admission."""
from __future__ import annotations

import json
from typing import Any

from hhs_backend.runtime.hhs_pass200c_guarded_active_admission_v1 import (
    APPROVAL_SCHEMA,
    CLASSIFICATION,
    CONTRACT,
    EVIDENCE_SCHEMA,
    EVENT_SCHEMA,
    FRONTIER_SCHEMA,
    INVOCATION_SCHEMA,
    MAX_ACTIVE_LEASE_INVOCATIONS,
    MIN_CANARY_INVOCATIONS,
    MIN_SUCCESSFUL_CANARIES,
    REQUIRED_CAPABILITIES,
    VERSION,
    Pass200CError,
    Pass200CGuardedActiveAuthority as Pass200CGuardedActiveAuthorityV1,
    _without,
    hash72,
)


class Pass200CGuardedActiveAuthority(Pass200CGuardedActiveAuthorityV1):
    """Rehash persisted evidence snapshots before listing or admission reuse."""

    @staticmethod
    def _verify_evidence_document(document: dict[str, Any]) -> None:
        expected = hash72(
            "pass200c.evidence",
            _without(document, "evidence_hash72", "event_hash72"),
        )
        if expected != document.get("evidence_hash72"):
            raise Pass200CError("persisted canary evidence was tampered")

    def list_evidence(self) -> list[dict[str, Any]]:
        records = [
            json.loads(row[0])
            for row in self._db.execute("SELECT payload_json FROM evidence ORDER BY rowid")
        ]
        for record in records:
            self._verify_evidence_document(record)
        return records

    def aggregate_canary_evidence(self, bundle_id: str) -> dict[str, Any]:
        document = super().aggregate_canary_evidence(bundle_id)
        self._verify_evidence_document(document)
        return document


PASS200C_ACTIVE_AUTHORITY = Pass200CGuardedActiveAuthority()

__all__ = [
    "APPROVAL_SCHEMA",
    "CLASSIFICATION",
    "CONTRACT",
    "EVIDENCE_SCHEMA",
    "EVENT_SCHEMA",
    "FRONTIER_SCHEMA",
    "INVOCATION_SCHEMA",
    "MAX_ACTIVE_LEASE_INVOCATIONS",
    "MIN_CANARY_INVOCATIONS",
    "MIN_SUCCESSFUL_CANARIES",
    "PASS200C_ACTIVE_AUTHORITY",
    "REQUIRED_CAPABILITIES",
    "VERSION",
    "Pass200CError",
    "Pass200CGuardedActiveAuthority",
]

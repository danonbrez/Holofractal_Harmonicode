"""Canonical production projection for Pass 200A proof-carrying optimization."""
from __future__ import annotations

import json
from typing import Any

from hhs_backend.runtime.hhs_pass200a_proof_carrying_optimization_v1 import (
    BUNDLE_SCHEMA,
    CLASSIFICATION,
    CONTRACT,
    DEFAULT_HOLDOUTS,
    DEFAULT_SHADOW_CONFIG,
    ENVELOPE_SCHEMA,
    EVENT_SCHEMA,
    OPERATION_ID,
    SHADOW_PLAN_SCHEMA,
    SHADOW_RUN_SCHEMA,
    VERSION,
    Pass200AError,
    Pass200AProofCarryingOptimizationAuthority as Pass200AProofCarryingOptimizationAuthorityV1,
    _without_identifier,
    hash72,
)


class Pass200AProofCarryingOptimizationAuthority(
    Pass200AProofCarryingOptimizationAuthorityV1
):
    """Use durable schema columns for deterministic bundle ordering."""

    def list_bundles(self) -> list[dict[str, Any]]:
        bundles = [
            json.loads(row[0])
            for row in self._db.execute(
                "SELECT payload_json FROM bundles ORDER BY simplification_id"
            )
        ]
        for document in bundles:
            expected = hash72(
                "pass200a.bundle",
                _without_identifier(document, "bundle_hash72", "event_hash72"),
            )
            if expected != document["bundle_hash72"]:
                raise Pass200AError("persisted optimization bundle was tampered")
        return bundles


PASS200A_OPTIMIZATION_AUTHORITY = Pass200AProofCarryingOptimizationAuthority()

__all__ = [
    "BUNDLE_SCHEMA",
    "CLASSIFICATION",
    "CONTRACT",
    "DEFAULT_HOLDOUTS",
    "DEFAULT_SHADOW_CONFIG",
    "ENVELOPE_SCHEMA",
    "EVENT_SCHEMA",
    "OPERATION_ID",
    "PASS200A_OPTIMIZATION_AUTHORITY",
    "Pass200AError",
    "Pass200AProofCarryingOptimizationAuthority",
    "SHADOW_PLAN_SCHEMA",
    "SHADOW_RUN_SCHEMA",
    "VERSION",
]

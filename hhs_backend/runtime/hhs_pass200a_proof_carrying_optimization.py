"""Canonical production projection for repaired Pass 200A shadow optimization."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass200a_proof_carrying_optimization_v2 import (
    BUNDLE_SCHEMA,
    CLASSIFICATION,
    CONTRACT,
    DEFAULT_HOLDOUTS,
    DEFAULT_SHADOW_CONFIG,
    ENVELOPE_SCHEMA,
    EVENT_SCHEMA,
    NONPRODUCTION_CLASSIFICATION,
    OPERATION_ID,
    PASS200A_LEGACY_SINGLETON,
    PRODUCTION_TOTALS,
    REPAIR_CLASSIFICATION,
    REPAIR_SCHEMA,
    SHADOW_PLAN_SCHEMA,
    SHADOW_RUN_SCHEMA,
    VERSION,
    Pass200AError,
    Pass200AProofCarryingOptimizationAuthority as Pass200AProofCarryingOptimizationAuthorityV2,
)


class Pass200AProofCarryingOptimizationAuthority(
    Pass200AProofCarryingOptimizationAuthorityV2
):
    """Canonical production projection with current-proof bundle binding.

    The immutable bundle is created only from the Pass198 document re-read from
    the registry immediately before persistence. Caller snapshots are not a
    proof authority. The same live registry row is rechecked before every
    compiler-shadow use so revoked or replaced proofs fail closed.
    """

    def _current_proof(self, bundle: Mapping[str, Any]) -> dict[str, Any]:
        matches = [
            item
            for item in self.distributed.pass198.list_simplifications(OPERATION_ID)
            if item.get("simplification_id") == bundle.get("simplification_id")
        ]
        if len(matches) != 1:
            raise Pass200AError("bundle source simplification is missing or ambiguous")
        current = matches[0]
        if current.get("status") != "COMPILER_CANDIDATE":
            raise Pass200AError(
                "bundle source proof is no longer the current compiler candidate: "
                f"{current.get('status')}"
            )
        if current.get("proof_hash72") != bundle.get("proof_hash72"):
            raise Pass200AError(
                "bundle source proof Hash72 no longer matches current proof: "
                f"bundle={bundle.get('proof_hash72')} current={current.get('proof_hash72')} "
                f"updated_event={current.get('updated_event_hash72')}"
            )
        if current.get("source_operation_identity") != bundle.get("source_operation_identity"):
            raise Pass200AError("bundle source operation identity drift")
        if current.get("candidate_operation_identity") != bundle.get("candidate_operation_identity"):
            raise Pass200AError("bundle candidate operation identity drift")
        return dict(current)

    def _record_bundle(
        self,
        proof: Mapping[str, Any],
        envelopes: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        simplification_id = str(proof.get("simplification_id") or "")
        matches = [
            item
            for item in self.distributed.pass198.list_simplifications(OPERATION_ID)
            if item.get("simplification_id") == simplification_id
        ]
        if len(matches) != 1:
            raise Pass200AError(
                "bundle source simplification is missing or ambiguous before persistence"
            )
        current = matches[0]
        if current.get("status") != "COMPILER_CANDIDATE":
            raise Pass200AError(
                "bundle source proof is not the current compiler candidate before persistence"
            )
        for field in ("source_operation_identity", "candidate_operation_identity"):
            if proof.get(field) != current.get(field):
                raise Pass200AError(f"bundle source proof identity drift before persistence: {field}")

        document = super()._record_bundle(current, envelopes)
        self._verify_bundle_identity(document)
        self._current_proof(document)
        return document


# V1 historically constructed its singleton at import time. Repair-forward the
# same object in place so every existing reference sees the corrected production
# class; never create a second default-state authority for the same SQLite/
# Pass199 root.
if not isinstance(PASS200A_LEGACY_SINGLETON, Pass200AProofCarryingOptimizationAuthority):
    PASS200A_LEGACY_SINGLETON.__class__ = Pass200AProofCarryingOptimizationAuthority

PASS200A_OPTIMIZATION_AUTHORITY = PASS200A_LEGACY_SINGLETON

__all__ = [
    "BUNDLE_SCHEMA",
    "CLASSIFICATION",
    "CONTRACT",
    "DEFAULT_HOLDOUTS",
    "DEFAULT_SHADOW_CONFIG",
    "ENVELOPE_SCHEMA",
    "EVENT_SCHEMA",
    "NONPRODUCTION_CLASSIFICATION",
    "OPERATION_ID",
    "PASS200A_OPTIMIZATION_AUTHORITY",
    "PRODUCTION_TOTALS",
    "REPAIR_CLASSIFICATION",
    "REPAIR_SCHEMA",
    "Pass200AError",
    "Pass200AProofCarryingOptimizationAuthority",
    "SHADOW_PLAN_SCHEMA",
    "SHADOW_RUN_SCHEMA",
    "VERSION",
]

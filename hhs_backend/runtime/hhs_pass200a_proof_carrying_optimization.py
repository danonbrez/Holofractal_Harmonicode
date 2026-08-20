"""Canonical production projection for repaired Pass 200A shadow optimization."""
from __future__ import annotations

import json
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
    """Canonical production projection with monotonic current-proof binding.

    A Pass198 ``SIMPLIFICATION_REVERIFIED`` event may legitimately extend a
    compiler-candidate proof with another closed calibration run and therefore
    change its aggregate ``proof_hash72`` without changing authority status.
    Such proof evolution is accepted only when it is an intact, monotonic
    descendant of the immutable Pass200A bundle evidence. Revocation, operation
    identity drift, evidence loss, or an unbound hash replacement still fails
    closed.
    """

    def _current_proof(self, bundle: Mapping[str, Any]) -> dict[str, Any]:
        registry = self.distributed.pass198
        matches = [
            item
            for item in registry.list_simplifications(OPERATION_ID)
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

        stable_fields = (
            "operation_id",
            "name",
            "source_operation_identity",
            "candidate_operation_identity",
            "retained_witnesses",
            "cost",
        )
        for field in stable_fields:
            if current.get(field) != bundle.get(field):
                raise Pass200AError(f"bundle source proof stable identity drift: {field}")

        bundle_runs = set(bundle.get("evidence_run_ids") or [])
        current_runs = set(current.get("run_ids") or [])
        promotion_runs = set(current.get("promotion_evidence_run_ids") or [])
        if not bundle_runs or not bundle_runs.issubset(current_runs):
            raise Pass200AError("bundle source proof lost original qualification evidence")
        if promotion_runs != bundle_runs:
            raise Pass200AError("bundle source promotion evidence drift")
        if int(current.get("verification_run_count", -1)) != len(current_runs):
            raise Pass200AError("bundle source verification-run count is inconsistent")

        registry_chain = registry.verify_event_chain()
        if registry_chain.get("ok") is not True:
            raise Pass200AError("Pass198 registry event chain is invalid")

        known_runs = {
            item.get("run_id"): item
            for item in registry.list_runs(OPERATION_ID)
        }
        for run_id in current_runs:
            run = known_runs.get(run_id)
            if not run or run.get("status") != "CLOSED":
                raise Pass200AError("bundle source proof includes an unverified calibration run")
            if run.get("operation_id") != OPERATION_ID:
                raise Pass200AError("bundle source proof includes a foreign operation run")
            if run.get("operation_spec_hash72") != current.get("source_operation_identity"):
                raise Pass200AError("bundle source proof includes operation-spec drift")

        if current.get("proof_hash72") != bundle.get("proof_hash72"):
            updated_event_hash72 = current.get("updated_event_hash72")
            row = registry._db.execute(
                "SELECT event_type,payload_json FROM events WHERE event_hash72=?",
                (updated_event_hash72,),
            ).fetchone()
            if not row or row["event_type"] != "SIMPLIFICATION_REVERIFIED":
                raise Pass200AError(
                    "bundle source proof Hash72 changed without Pass198 re-verification"
                )
            event = json.loads(row["payload_json"])
            payload = event.get("payload") or {}
            if payload.get("simplification_id") != bundle.get("simplification_id"):
                raise Pass200AError("Pass198 re-verification is bound to another simplification")
            if payload.get("run_id") not in current_runs - bundle_runs:
                raise Pass200AError("Pass198 re-verification does not add descendant evidence")
            if int(payload.get("verification_run_count", -1)) != len(current_runs):
                raise Pass200AError("Pass198 re-verification count does not match current proof")

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

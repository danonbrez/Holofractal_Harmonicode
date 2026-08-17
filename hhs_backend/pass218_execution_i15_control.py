"""Pass 218 I15 persistence and reconciliation controller."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import time
from typing import Any, Mapping

from hhs_runtime.pass218.consumption_recovery_i15 import repair_consumption_indexes
from hhs_runtime.pass218.execution_i15 import (
    Pass218ExecutionStateError,
    Pass218ExecutionValidationError,
    Pass218ReleaseConsumptionJournal,
    seal_execution_attestation,
    seal_execution_reconciliation,
    validate_execution_reconciliation,
)
from hhs_runtime.pass218.observability_i13 import (
    Pass218AuthorityObservabilityValidationError,
    validate_maintenance_run_receipt,
)


def _key(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class Pass218ExecutionControlPlane:
    def __init__(self, i13_control: Any, i14_control: Any, *, state_root: str | os.PathLike[str]) -> None:
        self.i13_control = i13_control
        self.i14_control = i14_control
        root = Path(state_root)
        self.journal = Pass218ReleaseConsumptionJournal(root / "i15" / "consumption")
        self.recovered_action_index_count = repair_consumption_indexes(self.journal)
        self.reconciliation_root = root / "i14" / "execution-reconciliations"
        self.reconciliation_root.mkdir(parents=True, exist_ok=True)

    def _reconciliation_path(self, release_hash: str) -> Path:
        return self.reconciliation_root / (_key(release_hash) + ".json")

    @staticmethod
    def _atomic_create(path: Path, value: Mapping[str, Any]) -> None:
        data = (json.dumps(dict(value), sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            view = memoryview(data)
            while view:
                written = os.write(fd, view)
                view = view[written:]
            os.fsync(fd)
        finally:
            os.close(fd)

    def _existing_i13_run(self, action_hash: str) -> dict[str, Any] | None:
        for item in reversed(self.i13_control.journal.records()):
            record = item.get("record") or {}
            if item.get("kind") == "MAINTENANCE_RUN" and record.get("action_record_hash72") == action_hash:
                return validate_maintenance_run_receipt(record)
        return None

    def _validate_existing_i13_run(self, existing: Mapping[str, Any], attestation: Mapping[str, Any]) -> dict[str, Any]:
        if existing.get("outcome") != attestation.get("outcome"):
            raise Pass218ExecutionValidationError("P218_I15_EXISTING_I13_OUTCOME_MISMATCH")
        if bool(existing.get("external_operation_executed")) != bool(attestation.get("external_operation_executed")):
            raise Pass218ExecutionValidationError("P218_I15_EXISTING_I13_EXECUTION_FLAG_MISMATCH")
        return dict(existing)

    def _existing_reconciliation(self, release_hash: str) -> dict[str, Any] | None:
        path = self._reconciliation_path(release_hash)
        if not path.is_file():
            return None
        return validate_execution_reconciliation(json.loads(path.read_text(encoding="utf-8")))

    def status(self) -> dict[str, Any]:
        journal = self.journal.status()
        reconciled = len(list(self.reconciliation_root.glob("*.json")))
        terminal = int(journal["terminal_attestation_count"])
        return {
            "schema": "HHS-P218-I15-EXECUTION-CONTROL-STATUS-V1",
            **journal,
            "reconciled_release_count": reconciled,
            "terminal_pending_reconciliation_count": max(0, terminal - reconciled),
            "recovered_action_index_count": self.recovered_action_index_count,
            "durable_claim_repairs_secondary_index": True,
            "i14_preflight_required_before_claim": True,
            "claim_is_external_execution_start_boundary": True,
            "post_claim_retry_reuses_release": False,
            "reconciliation_is_idempotent": True,
            "maintenance_execution_remains_external": True,
            "canonical_authority_minted": False,
            "canonical_mutation_permitted": False,
            "action_authority_minted": False,
        }

    def claim(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        release = payload.get("release")
        if not isinstance(release, Mapping):
            raise Pass218ExecutionValidationError("P218_I15_RELEASE_REQUIRED")
        revocations = payload.get("revocation_statements") or []
        if not isinstance(revocations, list):
            raise Pass218ExecutionValidationError("P218_I15_REVOCATIONS_INVALID")
        preflight = self.i14_control.preflight({"release": dict(release), "revocation_statements": revocations})
        self.recovered_action_index_count += repair_consumption_indexes(self.journal)
        return self.journal.claim_release(release=release, preflight=preflight, claimed_epoch_ns=time.time_ns())

    def _ensure_i13_run(self, claim: Mapping[str, Any], attestation: Mapping[str, Any]) -> dict[str, Any]:
        existing = self._existing_i13_run(str(claim["action_record_hash72"]))
        if existing is not None:
            return self._validate_existing_i13_run(existing, attestation)
        try:
            return self.i13_control.record_run({
                "action_record_hash72": claim["action_record_hash72"],
                "run_id": "i15-" + str(claim["attempt_id"]),
                "outcome": attestation["outcome"],
                "started_epoch_seconds": int(claim["claimed_epoch_ns"]) // 1_000_000_000,
                "external_operation_executed": bool(attestation["external_operation_executed"]),
                "canonical_target_changed": False,
                "authority_minted": False,
            })
        except Pass218AuthorityObservabilityValidationError:
            existing = self._existing_i13_run(str(claim["action_record_hash72"]))
            if existing is None:
                raise
            return self._validate_existing_i13_run(existing, attestation)

    def reconcile_release(self, release_hash: str) -> dict[str, Any]:
        existing = self._existing_reconciliation(release_hash)
        if existing is not None:
            return existing
        claim = self.journal.claim_for_release(release_hash)
        if claim is None:
            raise Pass218ExecutionStateError("P218_I15_RELEASE_NOT_CLAIMED")
        attestation = self.journal.attestation_for_release(release_hash)
        if attestation is None:
            raise Pass218ExecutionStateError("P218_I15_TERMINAL_ATTESTATION_REQUIRED")
        run = self._ensure_i13_run(claim, attestation)
        reconciliation = seal_execution_reconciliation(claim=claim, attestation=attestation, i13_run_receipt=run)
        try:
            self._atomic_create(self._reconciliation_path(release_hash), reconciliation)
        except FileExistsError:
            existing = self._existing_reconciliation(release_hash)
            if existing is None:
                raise Pass218ExecutionStateError("P218_I15_RECONCILIATION_RACE_INVALID")
            return existing
        return reconciliation

    def attest(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        release_hash = str(payload.get("release_record_hash72") or "").strip()
        claim = self.journal.claim_for_release(release_hash)
        if claim is None:
            raise Pass218ExecutionStateError("P218_I15_RELEASE_NOT_CLAIMED")
        record = seal_execution_attestation(
            claim=claim,
            outcome=str(payload.get("outcome") or "").strip().upper(),
            completed_epoch_ns=time.time_ns(),
            external_result_hash72=str(payload.get("external_result_hash72") or "").strip(),
            external_operation_executed=bool(payload.get("external_operation_executed", False)),
            i12_maintenance_record=(payload.get("i12_maintenance_record") if isinstance(payload.get("i12_maintenance_record"), Mapping) else None),
        )
        stored = self.journal.record_attestation(release_hash=release_hash, attestation=record)
        return {
            "schema": "HHS-P218-I15-ATTEST-AND-RECONCILE-V1",
            "attestation": stored,
            "reconciliation": self.reconcile_release(release_hash),
            "release_permanently_consumed": True,
            "retry_requires_new_release": True,
            "canonical_authority_minted": False,
            "canonical_mutation_permitted": False,
            "action_authority_minted": False,
        }

    def reconcile(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self.reconcile_release(str(payload.get("release_record_hash72") or "").strip())

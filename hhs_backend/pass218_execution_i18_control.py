"""Pass 218 Iteration 18 distributed terminal-closure coordinator."""
from __future__ import annotations

import json
from typing import Any, Mapping

from hhs_backend.pass218_execution_i17_control import Pass218FencedExternalExecutionControlPlane
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.distributed_closure_i18 import (
    PASS218_DISTRIBUTED_CLOSURE_VERSION,
    Pass218DistributedClosureLedgerProtocol,
    Pass218DistributedClosureValidationError,
    validate_distributed_terminal_closure,
)
from hhs_runtime.pass218.distributed_execution_i17 import validate_external_result
from hhs_runtime.pass218.execution_i15 import (
    Pass218ExecutionReplayRejected,
    Pass218ExecutionStateError,
    Pass218ExecutionValidationError,
    seal_execution_attestation,
    seal_execution_reconciliation,
    validate_execution_attestation,
    validate_execution_reconciliation,
    validate_release_claim,
)
from hhs_runtime.pass218.observability_i13 import (
    seal_maintenance_run_receipt,
    validate_maintenance_run_receipt,
    validate_operator_action,
)


class Pass218DistributedTerminalClosureControlPlane(Pass218FencedExternalExecutionControlPlane):
    def __init__(self, *args: Any, closure_ledger: Pass218DistributedClosureLedgerProtocol | None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.closure_ledger = closure_ledger
        self.last_i18_error_code: str | None = None
        self.i18_local_mirror_repair_total = 0
        self.i18_source_migration_total = 0

    def _find_i13_action(self, action_hash72: str) -> dict[str, Any] | None:
        for item in reversed(self.i13_control.journal.records()):
            if item.get("kind") != "OPERATOR_ACTION":
                continue
            record = item.get("record") or {}
            if record.get("record_hash72") == action_hash72:
                return validate_operator_action(record)
        return None

    def _ensure_action_source_for_claim(self, claim: Mapping[str, Any]) -> dict[str, Any]:
        if self.closure_ledger is None:
            raise Pass218DistributedClosureValidationError("P218_I18_DISTRIBUTED_CLOSURE_REQUIRED")
        claim_value = validate_release_claim(claim)
        existing = self.closure_ledger.source_for_action(claim_value["action_record_hash72"])
        if existing is not None:
            return existing
        action = self._find_i13_action(claim_value["action_record_hash72"])
        if action is None:
            raise Pass218ExecutionStateError("P218_I18_I13_ACTION_SOURCE_NOT_AVAILABLE")
        source = self.closure_ledger.ensure_action_source(action)
        self.i18_source_migration_total += 1
        return source

    def reserve_external(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if self.closure_ledger is not None:
            release_hash = str(payload.get("release_record_hash72") or "").strip()
            claim = self._claim_for_release(release_hash)
            self._ensure_action_source_for_claim(claim)
        return super().reserve_external(payload)

    def _existing_local_attestation(self, claim: Mapping[str, Any], result: Mapping[str, Any]) -> dict[str, Any] | None:
        existing = self.journal.attestation_for_release(str(claim["release_record_hash72"]))
        if existing is None:
            return None
        value = validate_execution_attestation(existing)
        if value["claim_record_hash72"] != claim["record_hash72"]:
            raise Pass218ExecutionValidationError("P218_I18_EXISTING_ATTESTATION_CLAIM_MISMATCH")
        if value["external_result_hash72"] != result["external_result_hash72"] or value["outcome"] != result["outcome"]:
            raise Pass218ExecutionValidationError("P218_I18_EXISTING_ATTESTATION_RESULT_MISMATCH")
        return value

    def _build_terminal_records(self, claim: Mapping[str, Any], result: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        claim_value = validate_release_claim(claim)
        result_value = validate_external_result(result)
        attestation = self._existing_local_attestation(claim_value, result_value)
        if attestation is None:
            attestation = seal_execution_attestation(
                claim=claim_value,
                outcome=result_value["outcome"],
                completed_epoch_ns=result_value["completed_epoch_ns"],
                external_result_hash72=result_value["external_result_hash72"],
                external_operation_executed=bool(result_value["external_operation_executed"]),
                i12_maintenance_record=(
                    result_value.get("i12_maintenance_record")
                    if isinstance(result_value.get("i12_maintenance_record"), Mapping)
                    else None
                ),
            )

        run = self._existing_i13_run(claim_value["action_record_hash72"])
        if run is not None:
            run = self._validate_existing_i13_run(run, attestation)
        else:
            if self.closure_ledger is None:
                raise Pass218ExecutionStateError("P218_I18_DISTRIBUTED_CLOSURE_REQUIRED")
            source = self.closure_ledger.source_for_action(claim_value["action_record_hash72"])
            if source is None:
                source = self._ensure_action_source_for_claim(claim_value)
            action = validate_operator_action(source["action_record"])
            after_status = self.i13_control.status()
            completed_seconds = int(result_value["completed_epoch_ns"]) // 1_000_000_000
            started_seconds = int(claim_value["claimed_epoch_ns"]) // 1_000_000_000
            run = seal_maintenance_run_receipt(
                run_id="i18-" + hash72_digest(
                    {"domain": "HHS-P218-I18-RUN-ID"},
                    {
                        "claim_record_hash72": claim_value["record_hash72"],
                        "i17_result_record_hash72": result_value["record_hash72"],
                    },
                ),
                action_record_hash72=claim_value["action_record_hash72"],
                operator_id=action["operator_id"],
                action=claim_value["action"],
                outcome=result_value["outcome"],
                started_epoch_seconds=started_seconds,
                completed_epoch_seconds=completed_seconds,
                before_status_hash72=action["status_hash72"],
                after_status_hash72=after_status["record_hash72"],
                external_operation_executed=bool(result_value["external_operation_executed"]),
                canonical_target_changed=False,
                authority_minted=False,
            )

        reconciliation = self._existing_reconciliation(claim_value["release_record_hash72"])
        if reconciliation is not None:
            reconciliation = validate_execution_reconciliation(reconciliation)
            if reconciliation["claim_record_hash72"] != claim_value["record_hash72"]:
                raise Pass218ExecutionValidationError("P218_I18_EXISTING_RECONCILIATION_CLAIM_MISMATCH")
            if reconciliation["attestation_record_hash72"] != attestation["record_hash72"]:
                raise Pass218ExecutionValidationError("P218_I18_EXISTING_RECONCILIATION_ATTESTATION_MISMATCH")
            if reconciliation["i13_run_receipt_hash72"] != run["record_hash72"]:
                raise Pass218ExecutionValidationError("P218_I18_EXISTING_RECONCILIATION_RUN_MISMATCH")
        else:
            reconciliation = seal_execution_reconciliation(
                claim=claim_value,
                attestation=attestation,
                i13_run_receipt=run,
            )
        return attestation, validate_maintenance_run_receipt(run), reconciliation

    def _mirror_closure_local(self, closure: Mapping[str, Any]) -> dict[str, Any]:
        value = validate_distributed_terminal_closure(closure)
        release_hash = value["release_record_hash72"]
        claim = self.journal.claim_for_release(release_hash)
        if claim is None:
            if self.distributed_ledger is not None:
                self.synchronize()
            claim = self.journal.claim_for_release(release_hash)
        if claim is None:
            raise Pass218ExecutionStateError("P218_I18_LOCAL_CLAIM_MISSING_AFTER_SYNC")
        if claim["record_hash72"] != value["claim_record_hash72"]:
            raise Pass218ExecutionValidationError("P218_I18_LOCAL_CLAIM_HASH_MISMATCH")

        attestation = validate_execution_attestation(value["attestation"])
        existing_attestation = self.journal.attestation_for_release(release_hash)
        if existing_attestation is None:
            self.journal.record_attestation(release_hash=release_hash, attestation=attestation)
            self.i18_local_mirror_repair_total += 1
        elif existing_attestation["record_hash72"] != attestation["record_hash72"]:
            raise Pass218ExecutionValidationError("P218_I18_LOCAL_ATTESTATION_CONFLICT")

        run = validate_maintenance_run_receipt(value["i13_run_receipt"])
        existing_run = self._existing_i13_run(value["action_record_hash72"])
        if existing_run is None:
            self.i13_control.journal.append_run_receipt(run)
            self.i18_local_mirror_repair_total += 1
        elif existing_run["record_hash72"] != run["record_hash72"]:
            raise Pass218ExecutionValidationError("P218_I18_LOCAL_I13_RUN_CONFLICT")

        reconciliation = validate_execution_reconciliation(value["reconciliation"])
        existing_reconciliation = self._existing_reconciliation(release_hash)
        if existing_reconciliation is None:
            try:
                self._atomic_create(self._reconciliation_path(release_hash), reconciliation)
                self.i18_local_mirror_repair_total += 1
            except FileExistsError:
                existing_reconciliation = self._existing_reconciliation(release_hash)
                if existing_reconciliation is None:
                    raise Pass218ExecutionStateError("P218_I18_LOCAL_RECONCILIATION_RACE_INVALID")
        if existing_reconciliation is not None and existing_reconciliation["record_hash72"] != reconciliation["record_hash72"]:
            raise Pass218ExecutionValidationError("P218_I18_LOCAL_RECONCILIATION_CONFLICT")
        return value

    def _closure_projection(self, closure: Mapping[str, Any]) -> dict[str, Any]:
        value = self._mirror_closure_local(closure)
        return {
            "schema": "HHS-P218-I18-TERMINAL-CLOSURE-PROJECTION-V1",
            "distributed_closure": value,
            "attestation": value["attestation"],
            "reconciliation": value["reconciliation"],
            "distributed_closure_precedes_local_terminal_mirror": True,
            "release_permanently_consumed": True,
            "redispatch_permitted": False,
            "retry_requires_new_prepared_action": True,
            "canonical_authority_minted": False,
            "canonical_mutation_permitted": False,
            "action_authority_minted": False,
        }

    def _finalize_result(self, claim: Mapping[str, Any], result: Mapping[str, Any]) -> dict[str, Any]:
        if self.closure_ledger is None:
            return super()._finalize_result(claim, result)
        claim_value = validate_release_claim(claim)
        result_value = validate_external_result(result)
        existing = self.closure_ledger.closure_for_claim(claim_value["record_hash72"])
        if existing is not None:
            return self._closure_projection(existing)
        self._ensure_action_source_for_claim(claim_value)
        attestation, run, reconciliation = self._build_terminal_records(claim_value, result_value)
        closure = self.closure_ledger.record_closure(
            claim=claim_value,
            result=result_value,
            attestation=attestation,
            i13_run_receipt=run,
            reconciliation=reconciliation,
        )
        self.last_i18_error_code = None
        return self._closure_projection(closure)

    def finalize_persisted_results(self) -> int:
        if self.execution_ledger is None:
            return 0
        if self.distributed_ledger is not None:
            self.synchronize()
        finalized = 0
        for dispatch in self.execution_ledger.dispatches():
            claim = self.journal.claim_for_release(dispatch["release_record_hash72"])
            if claim is None:
                continue
            try:
                self._ensure_action_source_for_claim(claim)
            except Pass218ExecutionStateError:
                if self.execution_ledger.result_for_claim(dispatch["claim_record_hash72"]) is not None:
                    self.last_i18_error_code = "P218_I18_I13_ACTION_SOURCE_NOT_AVAILABLE"
                continue
            result = self.execution_ledger.result_for_claim(dispatch["claim_record_hash72"])
            if result is None:
                continue
            had_closure = self.closure_ledger is not None and self.closure_ledger.closure_for_claim(claim["record_hash72"]) is not None
            self._finalize_result(claim, result)
            if not had_closure:
                finalized += 1
        return finalized

    def attest(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if self.execution_ledger is None or self.closure_ledger is None:
            return super().attest(payload)
        release_hash = str(payload.get("release_record_hash72") or "").strip()
        claim = self._claim_for_release(release_hash)
        result = self.execution_ledger.result_for_claim(claim["record_hash72"])
        if result is None:
            raise Pass218ExecutionStateError("P218_I18_DISTRIBUTED_I17_RESULT_REQUIRED_BEFORE_ATTESTATION")
        return self._finalize_result(claim, result)

    def reconcile_release(self, release_hash: str) -> dict[str, Any]:
        if self.execution_ledger is None or self.closure_ledger is None:
            return super().reconcile_release(release_hash)
        claim = self._claim_for_release(release_hash)
        closure = self.closure_ledger.closure_for_claim(claim["record_hash72"])
        if closure is None:
            result = self.execution_ledger.result_for_claim(claim["record_hash72"])
            if result is None:
                raise Pass218ExecutionStateError("P218_I18_DISTRIBUTED_I17_RESULT_REQUIRED_BEFORE_RECONCILIATION")
            return self._finalize_result(claim, result)["reconciliation"]
        return self._mirror_closure_local(closure)["reconciliation"]

    def reconcile(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self.reconcile_release(str(payload.get("release_record_hash72") or "").strip())

    def synchronize_terminal_closures(self) -> dict[str, Any]:
        if self.closure_ledger is None or self.execution_ledger is None:
            return {
                "schema": "HHS-P218-I18-TERMINAL-CLOSURE-SYNCHRONIZE-V1",
                "distributed_closure_configured": False,
                "closure_created_count": 0,
                "local_mirror_repaired_count": 0,
            }
        before = self.i18_local_mirror_repair_total
        created = self.finalize_persisted_results()
        for closure in self.closure_ledger.closures():
            self._mirror_closure_local(closure)
        return {
            "schema": "HHS-P218-I18-TERMINAL-CLOSURE-SYNCHRONIZE-V1",
            "distributed_closure_configured": True,
            "closure_created_count": created,
            "local_mirror_repaired_count": self.i18_local_mirror_repair_total - before,
            "successor_may_redispatch": False,
            "canonical_authority_minted": False,
            "canonical_mutation_permitted": False,
            "action_authority_minted": False,
        }

    def status(self) -> dict[str, Any]:
        base = super().status()
        if self.closure_ledger is None:
            closure_status = {
                "distributed_closure_configured": False,
                "distributed_action_source_count": 0,
                "distributed_terminal_closure_count": 0,
                "terminal_result_pending_closure_count": 0,
            }
        else:
            try:
                status = self.closure_ledger.status()
                closure_status = {
                    "distributed_closure_configured": True,
                    "distributed_action_source_count": status["distributed_action_source_count"],
                    "distributed_terminal_closure_count": status["distributed_terminal_closure_count"],
                    "terminal_result_pending_closure_count": status["terminal_result_pending_closure_count"],
                }
            except Exception as exc:
                self.last_i18_error_code = self._code(exc)
                closure_status = {
                    "distributed_closure_configured": True,
                    "distributed_action_source_count": None,
                    "distributed_terminal_closure_count": None,
                    "terminal_result_pending_closure_count": None,
                }
        return {
            **base,
            "schema": "HHS-P218-I18-TERMINAL-CLOSURE-CONTROL-STATUS-V1",
            "distributed_closure_version": PASS218_DISTRIBUTED_CLOSURE_VERSION,
            **closure_status,
            "distributed_action_source_precedes_external_dispatch": self.closure_ledger is not None,
            "distributed_closure_precedes_local_terminal_mirror": self.closure_ledger is not None,
            "successor_repairs_terminal_evidence_without_redispatch": True,
            "legacy_attest_route_rebound_to_distributed_i17_result": self.closure_ledger is not None,
            "legacy_reconcile_route_rebound_to_distributed_closure": self.closure_ledger is not None,
            "i18_source_migration_total": self.i18_source_migration_total,
            "i18_local_mirror_repair_total": self.i18_local_mirror_repair_total,
            "i18_error_code": self.last_i18_error_code,
            "canonical_authority_minted": False,
            "canonical_mutation_permitted": False,
            "action_authority_minted": False,
        }


__all__ = ["Pass218DistributedTerminalClosureControlPlane"]

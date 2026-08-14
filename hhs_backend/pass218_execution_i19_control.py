"""Pass 218 Iteration 19 postcondition-verification control plane."""
from __future__ import annotations

from typing import Any, Mapping

from hhs_backend.pass218_execution_i18_control import Pass218DistributedTerminalClosureControlPlane
from hhs_runtime.pass218.distributed_postcondition_i19 import (
    PASS218_POSTCONDITION_VERSION,
    Pass218PostconditionLedgerProtocol,
    Pass218PostconditionValidationError,
    SNAPSHOT_ACTION,
    seal_postcondition_observation,
)
from hhs_runtime.pass218.distributed_execution_i17 import validate_external_result


class Pass218PostconditionVerificationControlPlane(Pass218DistributedTerminalClosureControlPlane):
    def __init__(self, *args: Any, postcondition_ledger: Pass218PostconditionLedgerProtocol | None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.postcondition_ledger = postcondition_ledger
        self.last_i19_error_code: str | None = None
        self.i19_intrinsic_snapshot_verification_total = 0

    def _closure_and_result_for_release(self, release_hash: str) -> tuple[dict[str, Any], dict[str, Any]]:
        if self.closure_ledger is None or self.execution_ledger is None:
            raise Pass218PostconditionValidationError("P218_I19_DISTRIBUTED_I17_I18_REQUIRED")
        claim = self._claim_for_release(release_hash)
        closure = self.closure_ledger.closure_for_claim(claim["record_hash72"])
        if closure is None:
            raise Pass218PostconditionValidationError("P218_I19_I18_TERMINAL_CLOSURE_REQUIRED")
        result = self.execution_ledger.result_for_claim(claim["record_hash72"])
        if result is None:
            raise Pass218PostconditionValidationError("P218_I19_I17_TERMINAL_RESULT_REQUIRED")
        result_value = validate_external_result(result)
        if result_value["record_hash72"] != closure["i17_result_record_hash72"]:
            raise Pass218PostconditionValidationError("P218_I19_RESULT_CLOSURE_MISMATCH")
        return closure, result_value

    def record_postcondition_observation(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if self.postcondition_ledger is None:
            raise Pass218PostconditionValidationError("P218_I19_DISTRIBUTED_POSTCONDITION_REQUIRED")
        release_hash = str(payload.get("release_record_hash72") or "").strip()
        closure, result = self._closure_and_result_for_release(release_hash)
        if result["outcome"] != "SUCCEEDED":
            raise Pass218PostconditionValidationError("P218_I19_ONLY_SUCCESS_REQUIRES_EFFECT_VERIFICATION")
        i12_record = result.get("i12_maintenance_record")
        if not isinstance(i12_record, Mapping):
            raise Pass218PostconditionValidationError("P218_I19_I12_MAINTENANCE_RECORD_REQUIRED")
        observation_payload = payload.get("observation")
        if not isinstance(observation_payload, Mapping):
            raise Pass218PostconditionValidationError("P218_I19_OBSERVATION_REQUIRED")
        observation = seal_postcondition_observation(
            action=result["action"],
            i12_maintenance_record=i12_record,
            observation=observation_payload,
            observed_epoch_ns=payload.get("observed_epoch_ns"),
        )
        verification = self.postcondition_ledger.record_verification(
            closure=closure,
            result=result,
            observation=observation,
        )
        self.last_i19_error_code = None
        return {
            "schema": "HHS-P218-I19-POSTCONDITION-VERIFICATION-PROJECTION-V1",
            "verification": verification,
            "execution_was_terminal_before_effect_verification": True,
            "successful_effect_verified": True,
            "release_permanently_consumed": True,
            "redispatch_permitted": False,
            "retry_requires_new_prepared_action": True,
            "canonical_authority_minted": False,
            "canonical_mutation_permitted": False,
            "action_authority_minted": False,
        }

    def verification_for_release(self, release_hash: str) -> dict[str, Any] | None:
        if self.postcondition_ledger is None:
            return None
        claim = self._claim_for_release(release_hash)
        return self.postcondition_ledger.verification_for_claim(claim["record_hash72"])

    def finalize_intrinsic_snapshot_verifications(self) -> int:
        if self.postcondition_ledger is None or self.closure_ledger is None or self.execution_ledger is None:
            return 0
        created = 0
        for closure in self.closure_ledger.closures():
            if closure["outcome"] != "SUCCEEDED":
                continue
            claim_hash = closure["claim_record_hash72"]
            if self.postcondition_ledger.verification_for_claim(claim_hash) is not None:
                continue
            result = self.execution_ledger.result_for_claim(claim_hash)
            if result is None:
                continue
            result_value = validate_external_result(result)
            if result_value["action"] != SNAPSHOT_ACTION:
                continue
            receipt = result_value.get("i12_maintenance_record")
            if not isinstance(receipt, Mapping):
                continue
            observation = seal_postcondition_observation(
                action=SNAPSHOT_ACTION,
                i12_maintenance_record=receipt,
                observation={
                    "rehearsal_receipt_hash72": receipt["record_hash72"],
                    "rehearsal_manifest_hash72": receipt["rehearsal_manifest_hash72"],
                    "rehearsal_canonical_root_exact": True,
                    "rehearsal_vm81_snapshot_exact": True,
                    "rehearsal_consumed_receipt_exact": True,
                    "rehearsal_distributed_checkpoint_exact": True,
                    "restore_target_non_authoritative": True,
                },
                observed_epoch_ns=result_value["completed_epoch_ns"],
            )
            self.postcondition_ledger.record_verification(
                closure=closure,
                result=result_value,
                observation=observation,
            )
            created += 1
            self.i19_intrinsic_snapshot_verification_total += 1
        return created

    def synchronize_postcondition_verifications(self) -> dict[str, Any]:
        if self.postcondition_ledger is None:
            return {
                "schema": "HHS-P218-I19-POSTCONDITION-SYNCHRONIZE-V1",
                "distributed_postcondition_configured": False,
                "intrinsic_snapshot_verification_created_count": 0,
            }
        created = self.finalize_intrinsic_snapshot_verifications()
        status = self.postcondition_ledger.status()
        return {
            "schema": "HHS-P218-I19-POSTCONDITION-SYNCHRONIZE-V1",
            "distributed_postcondition_configured": True,
            "intrinsic_snapshot_verification_created_count": created,
            "successful_terminal_closure_count": status["successful_terminal_closure_count"],
            "distributed_postcondition_verification_count": status["distributed_postcondition_verification_count"],
            "successful_closure_pending_verification_count": status["successful_closure_pending_verification_count"],
            "failed_or_aborted_require_postcondition_verification": False,
            "redispatch_permitted": False,
            "canonical_authority_minted": False,
            "canonical_mutation_permitted": False,
            "action_authority_minted": False,
        }

    def status(self) -> dict[str, Any]:
        base = super().status()
        if self.postcondition_ledger is None:
            postcondition = {
                "distributed_postcondition_configured": False,
                "successful_terminal_closure_count": 0,
                "distributed_postcondition_verification_count": 0,
                "successful_closure_pending_verification_count": 0,
                "failed_or_aborted_closure_count": 0,
            }
        else:
            try:
                status = self.postcondition_ledger.status()
                postcondition = {
                    "distributed_postcondition_configured": True,
                    "successful_terminal_closure_count": status["successful_terminal_closure_count"],
                    "distributed_postcondition_verification_count": status["distributed_postcondition_verification_count"],
                    "successful_closure_pending_verification_count": status["successful_closure_pending_verification_count"],
                    "failed_or_aborted_closure_count": status["failed_or_aborted_closure_count"],
                }
            except Exception as exc:
                self.last_i19_error_code = self._code(exc)
                postcondition = {
                    "distributed_postcondition_configured": True,
                    "successful_terminal_closure_count": None,
                    "distributed_postcondition_verification_count": None,
                    "successful_closure_pending_verification_count": None,
                    "failed_or_aborted_closure_count": None,
                }
        return {
            **base,
            "schema": "HHS-P218-I19-POSTCONDITION-CONTROL-STATUS-V1",
            "distributed_postcondition_version": PASS218_POSTCONDITION_VERSION,
            **postcondition,
            "successful_effect_verification_required": self.postcondition_ledger is not None,
            "failed_or_aborted_require_postcondition_verification": False,
            "snapshot_rehearsal_intrinsic_verification_supported": True,
            "credential_rotation_requires_external_postcondition_observation": True,
            "member_replacement_requires_external_postcondition_observation": True,
            "postcondition_verification_executes_maintenance": False,
            "postcondition_verification_grants_retry_authority": False,
            "successor_may_redispatch": False,
            "i19_intrinsic_snapshot_verification_total": self.i19_intrinsic_snapshot_verification_total,
            "i19_error_code": self.last_i19_error_code,
            "canonical_authority_minted": False,
            "canonical_mutation_permitted": False,
            "action_authority_minted": False,
        }


__all__ = ["Pass218PostconditionVerificationControlPlane"]

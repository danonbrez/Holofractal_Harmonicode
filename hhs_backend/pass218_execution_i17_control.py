"""Pass 218 Iteration 17 external-execution coordinator.

The coordinator inherits I16 distributed claim convergence, then requires a
second distributed reservation before any external maintenance call. A terminal
external result must also be durable in the I17 distributed ledger before the
inherited I15 attestation/reconciliation surfaces may close.

RuntimeOS may reserve the handoff and accept an HMAC-authenticated external
result, but it never performs the maintenance operation itself. A server-side
executor adapter may optionally be injected for non-browser orchestration.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any, Mapping

from hhs_backend.pass218_execution_i16_control import Pass218DistributedExecutionControlPlane
from hhs_runtime.pass218.approval_i14 import (
    validate_maintenance_release,
    validate_operator_statement,
)
from hhs_runtime.pass218.commit_boundary import _canonical_bytes
from hhs_runtime.pass218.distributed_execution_i17 import (
    PASS218_DISTRIBUTED_EXECUTION_VERSION,
    Pass218DistributedExecutionLedgerProtocol,
    Pass218ExternalExecutionResultUnknown,
    Pass218ExternalExecutionUnavailable,
    Pass218ExternalExecutionValidationError,
    Pass218ExternalExecutorProtocol,
    validate_external_result,
)
from hhs_runtime.pass218.execution_i15 import (
    Pass218ExecutionStateError,
    Pass218ExecutionValidationError,
    seal_execution_attestation,
    validate_release_claim,
)


class Pass218FencedExternalExecutionControlPlane(Pass218DistributedExecutionControlPlane):
    def __init__(
        self,
        i13_control: Any,
        i14_control: Any,
        *,
        state_root: str,
        distributed_ledger: Any,
        execution_ledger: Pass218DistributedExecutionLedgerProtocol | None,
        external_executor: Pass218ExternalExecutorProtocol | None = None,
        external_executor_id: str | None = None,
        result_shared_secret: str | None = None,
    ) -> None:
        super().__init__(
            i13_control,
            i14_control,
            state_root=state_root,
            distributed_ledger=distributed_ledger,
        )
        self.execution_ledger = execution_ledger
        self.external_executor = external_executor
        configured_id = external_executor.executor_id if external_executor is not None else external_executor_id
        self.external_executor_id = configured_id.strip() if isinstance(configured_id, str) and configured_id.strip() else None
        self.result_shared_secret = (
            result_shared_secret.encode("utf-8")
            if isinstance(result_shared_secret, str) and result_shared_secret
            else None
        )
        self.last_i17_error_code: str | None = None
        self.finalized_from_distributed_total = 0

    def _find_release(self, release_hash72: str) -> dict[str, Any]:
        if not self.i14_control.release_journal.is_file():
            raise Pass218ExecutionStateError("P218_I17_I14_RELEASE_NOT_FOUND")
        for line in reversed(self.i14_control.release_journal.read_text(encoding="utf-8").splitlines()):
            if not line.strip():
                continue
            item = json.loads(line)
            release = item.get("release") if isinstance(item, Mapping) else None
            if not isinstance(release, Mapping):
                continue
            value = validate_maintenance_release(release)
            if value.get("record_hash72") == release_hash72:
                return value
        raise Pass218ExecutionStateError("P218_I17_I14_RELEASE_NOT_FOUND")

    def _claim_for_release(self, release_hash72: str) -> dict[str, Any]:
        if self.distributed_ledger is not None:
            self.synchronize()
        claim = self.journal.claim_for_release(release_hash72)
        if claim is None:
            raise Pass218ExecutionStateError("P218_I17_RELEASE_NOT_CLAIMED")
        return validate_release_claim(claim)

    def _validate_executor_statement(self, claim: Mapping[str, Any], statement: Mapping[str, Any]) -> dict[str, Any]:
        release = self._find_release(str(claim["release_record_hash72"]))
        claimed_seconds = int(claim["claimed_epoch_ns"]) // 1_000_000_000
        verified = validate_operator_statement(
            statement,
            registry=self.i14_control.registry,
            expected_kind="EXECUTE",
            policy=self.i14_control.policy,
            now_epoch_seconds=claimed_seconds,
        )
        data = verified["data"]
        if verified["message_hash72"] != release.get("executor_message_hash72"):
            raise Pass218ExternalExecutionValidationError("P218_I17_EXECUTOR_STATEMENT_HASH_MISMATCH")
        if data.get("operator_id") != claim.get("executor_operator_id"):
            raise Pass218ExternalExecutionValidationError("P218_I17_EXECUTOR_OPERATOR_MISMATCH")
        if data.get("action_record_hash72") != claim.get("action_record_hash72") or data.get("action") != claim.get("action"):
            raise Pass218ExternalExecutionValidationError("P218_I17_EXECUTOR_ACTION_BINDING_MISMATCH")
        if data.get("distributed_fence_epoch") != claim.get("distributed_fence_epoch"):
            raise Pass218ExternalExecutionValidationError("P218_I17_EXECUTOR_CLAIM_FENCE_MISMATCH")
        return verified

    def _finalize_result(self, claim: Mapping[str, Any], result: Mapping[str, Any]) -> dict[str, Any]:
        claim_value = validate_release_claim(claim)
        result_value = validate_external_result(result)
        if result_value["claim_record_hash72"] != claim_value["record_hash72"]:
            raise Pass218ExternalExecutionValidationError("P218_I17_RESULT_CLAIM_MISMATCH")
        if result_value["release_record_hash72"] != claim_value["release_record_hash72"]:
            raise Pass218ExternalExecutionValidationError("P218_I17_RESULT_RELEASE_MISMATCH")
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
        existing = self.journal.attestation_for_release(claim_value["release_record_hash72"])
        stored = self.journal.record_attestation(
            release_hash=claim_value["release_record_hash72"],
            attestation=attestation,
        )
        reconciliation = self.reconcile_release(claim_value["release_record_hash72"])
        if existing is None:
            self.finalized_from_distributed_total += 1
        return {
            "schema": "HHS-P218-I17-EXTERNAL-EXECUTION-CLOSURE-V1",
            "result": result_value,
            "attestation": stored,
            "reconciliation": reconciliation,
            "release_permanently_consumed": True,
            "redispatch_permitted": False,
            "retry_requires_new_prepared_action": True,
            "canonical_authority_minted": False,
            "canonical_mutation_permitted": False,
            "action_authority_minted": False,
        }

    def finalize_persisted_results(self) -> int:
        if self.execution_ledger is None:
            return 0
        if self.distributed_ledger is not None:
            self.synchronize()
        finalized = 0
        for dispatch in self.execution_ledger.dispatches():
            result = self.execution_ledger.result_for_claim(dispatch["claim_record_hash72"])
            if result is None:
                continue
            claim = self.journal.claim_for_release(dispatch["release_record_hash72"])
            if claim is None:
                raise Pass218ExecutionStateError("P218_I17_DISTRIBUTED_RESULT_LOCAL_CLAIM_MISSING")
            existing = self.journal.attestation_for_release(dispatch["release_record_hash72"])
            self._finalize_result(claim, result)
            if existing is None:
                finalized += 1
        return finalized

    def status(self) -> dict[str, Any]:
        base = super().status()
        projection: dict[str, Any]
        if self.execution_ledger is None:
            projection = {
                "distributed_execution_configured": False,
                "dispatch_count": 0,
                "terminal_result_count": 0,
                "unresolved_dispatch_count": 0,
            }
        else:
            try:
                ledger_status = self.execution_ledger.status()
                projection = {
                    "distributed_execution_configured": True,
                    "dispatch_count": ledger_status["dispatch_count"],
                    "terminal_result_count": ledger_status["terminal_result_count"],
                    "unresolved_dispatch_count": ledger_status["unresolved_dispatch_count"],
                }
            except Exception as exc:
                self.last_i17_error_code = self._code(exc)
                projection = {
                    "distributed_execution_configured": True,
                    "dispatch_count": None,
                    "terminal_result_count": None,
                    "unresolved_dispatch_count": None,
                }
        return {
            **base,
            "schema": "HHS-P218-I17-EXECUTION-CONTROL-STATUS-V1",
            "distributed_execution_version": PASS218_DISTRIBUTED_EXECUTION_VERSION,
            **projection,
            "external_executor_configured": self.external_executor_id is not None,
            "external_executor_id": self.external_executor_id,
            "authenticated_result_ingress_configured": self.result_shared_secret is not None,
            "browser_executes_maintenance": False,
            "distributed_reservation_precedes_external_call": self.execution_ledger is not None,
            "distributed_result_precedes_local_attestation": self.execution_ledger is not None,
            "redispatch_after_unknown_forbidden": True,
            "successor_recovery_only": True,
            "finalized_from_distributed_total": self.finalized_from_distributed_total,
            "i17_error_code": self.last_i17_error_code,
            "canonical_authority_minted": False,
            "canonical_mutation_permitted": False,
            "action_authority_minted": False,
        }

    def reserve_external(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if self.execution_ledger is None:
            raise Pass218ExternalExecutionUnavailable("P218_I17_DISTRIBUTED_EXECUTION_REQUIRED")
        if self.external_executor_id is None:
            raise Pass218ExternalExecutionUnavailable("P218_I17_EXTERNAL_EXECUTOR_ID_NOT_CONFIGURED")
        release_hash = str(payload.get("release_record_hash72") or "").strip()
        claim = self._claim_for_release(release_hash)
        statement = payload.get("executor_statement")
        if not isinstance(statement, Mapping):
            raise Pass218ExternalExecutionValidationError("P218_I17_EXECUTOR_STATEMENT_REQUIRED")
        self._validate_executor_statement(claim, statement)
        existing = self.execution_ledger.dispatch_for_claim(claim["record_hash72"])
        if existing is not None:
            result = self.execution_ledger.result_for_claim(claim["record_hash72"])
            return {
                "schema": "HHS-P218-I17-HANDOFF-RESERVATION-V1",
                "dispatch": existing,
                "terminal_result_present": result is not None,
                "redispatch_permitted": False,
                "canonical_authority_minted": False,
                "canonical_mutation_permitted": False,
                "action_authority_minted": False,
            }
        dispatch = self.execution_ledger.reserve_dispatch(
            claim,
            executor_id=self.external_executor_id,
            dispatched_epoch_ns=time.time_ns(),
        )
        return {
            "schema": "HHS-P218-I17-HANDOFF-RESERVATION-V1",
            "dispatch": dispatch,
            "terminal_result_present": False,
            "redispatch_permitted": False,
            "canonical_authority_minted": False,
            "canonical_mutation_permitted": False,
            "action_authority_minted": False,
        }

    def submit_external_result(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if self.execution_ledger is None:
            raise Pass218ExternalExecutionUnavailable("P218_I17_DISTRIBUTED_EXECUTION_REQUIRED")
        if self.result_shared_secret is None:
            raise Pass218ExternalExecutionUnavailable("P218_I17_RESULT_INGRESS_NOT_CONFIGURED")
        release_hash = str(payload.get("release_record_hash72") or "").strip()
        claim = self._claim_for_release(release_hash)
        dispatch = self.execution_ledger.dispatch_for_claim(claim["record_hash72"])
        if dispatch is None:
            raise Pass218ExecutionStateError("P218_I17_DISPATCH_NOT_RESERVED")
        raw_result = payload.get("result")
        if not isinstance(raw_result, Mapping):
            raise Pass218ExternalExecutionValidationError("P218_I17_RESULT_PAYLOAD_REQUIRED")
        signature = str(payload.get("result_hmac_sha256") or "").strip().lower()
        signed = _canonical_bytes({
            "dispatch_record_hash72": dispatch["record_hash72"],
            "result": dict(raw_result),
        })
        expected = hmac.new(self.result_shared_secret, signed, hashlib.sha256).hexdigest()
        if not signature or not hmac.compare_digest(signature, expected):
            raise Pass218ExternalExecutionValidationError("P218_I17_RESULT_HMAC_INVALID")
        completed_epoch_ns = raw_result.get("completed_epoch_ns")
        if not isinstance(completed_epoch_ns, int) or isinstance(completed_epoch_ns, bool) or completed_epoch_ns < 1:
            raise Pass218ExternalExecutionValidationError("P218_I17_COMPLETED_EPOCH_REQUIRED")
        result = self.execution_ledger.record_result(
            dispatch,
            raw_result,
            completed_epoch_ns=completed_epoch_ns,
        )
        self.last_i17_error_code = None
        return self._finalize_result(claim, result)

    def dispatch_external(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        """Optional server-internal orchestration; never installed as a browser route."""
        if self.execution_ledger is None:
            raise Pass218ExternalExecutionUnavailable("P218_I17_DISTRIBUTED_EXECUTION_REQUIRED")
        if self.external_executor is None:
            raise Pass218ExternalExecutionUnavailable("P218_I17_EXTERNAL_EXECUTOR_NOT_CONFIGURED")
        reserved = self.reserve_external(payload)
        dispatch = reserved["dispatch"]
        existing_result = self.execution_ledger.result_for_claim(dispatch["claim_record_hash72"])
        claim = self._claim_for_release(dispatch["release_record_hash72"])
        if existing_result is not None:
            return self._finalize_result(claim, existing_result)
        if reserved["terminal_result_present"] is False and self.execution_ledger.dispatch_for_claim(claim["record_hash72"])["record_hash72"] != dispatch["record_hash72"]:
            raise Pass218ExternalExecutionValidationError("P218_I17_DISPATCH_RESERVATION_MISMATCH")
        try:
            raw_result = self.external_executor.execute(dispatch)
        except Pass218ExternalExecutionResultUnknown:
            self.last_i17_error_code = "P218_I17_EXTERNAL_EXECUTOR_RESULT_UNKNOWN"
            raise
        completed = raw_result.get("completed_epoch_ns") if isinstance(raw_result, Mapping) else None
        if not isinstance(completed, int) or isinstance(completed, bool) or completed < 1:
            completed = time.time_ns()
        result = self.execution_ledger.record_result(
            dispatch,
            raw_result,
            completed_epoch_ns=completed,
        )
        self.last_i17_error_code = None
        return self._finalize_result(claim, result)

    def recover_external_result(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if self.execution_ledger is None:
            raise Pass218ExternalExecutionUnavailable("P218_I17_DISTRIBUTED_EXECUTION_REQUIRED")
        if self.external_executor is None:
            raise Pass218ExternalExecutionUnavailable("P218_I17_EXTERNAL_EXECUTOR_NOT_CONFIGURED")
        release_hash = str(payload.get("release_record_hash72") or "").strip()
        claim = self._claim_for_release(release_hash)
        statement = payload.get("executor_statement")
        if not isinstance(statement, Mapping):
            raise Pass218ExternalExecutionValidationError("P218_I17_EXECUTOR_STATEMENT_REQUIRED")
        self._validate_executor_statement(claim, statement)
        dispatch = self.execution_ledger.dispatch_for_claim(claim["record_hash72"])
        if dispatch is None:
            raise Pass218ExecutionStateError("P218_I17_DISPATCH_NOT_RESERVED")
        existing_result = self.execution_ledger.result_for_claim(claim["record_hash72"])
        if existing_result is not None:
            return self._finalize_result(claim, existing_result)
        recovered = self.external_executor.recover(dispatch)
        if recovered is None:
            raise Pass218ExternalExecutionResultUnknown("P218_I17_EXTERNAL_EXECUTOR_RESULT_STILL_UNKNOWN")
        completed = recovered.get("completed_epoch_ns") if isinstance(recovered, Mapping) else None
        if not isinstance(completed, int) or isinstance(completed, bool) or completed < 1:
            completed = time.time_ns()
        result = self.execution_ledger.record_result(
            dispatch,
            recovered,
            completed_epoch_ns=completed,
        )
        self.last_i17_error_code = None
        return self._finalize_result(claim, result)

    def attest(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if self.execution_ledger is None:
            return super().attest(payload)
        release_hash = str(payload.get("release_record_hash72") or "").strip()
        claim = self._claim_for_release(release_hash)
        result = self.execution_ledger.result_for_claim(claim["record_hash72"])
        if result is None:
            raise Pass218ExecutionValidationError("P218_I17_DISTRIBUTED_TERMINAL_RESULT_REQUIRED")
        return self._finalize_result(claim, result)

    def reconcile(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if self.execution_ledger is None:
            return super().reconcile(payload)
        release_hash = str(payload.get("release_record_hash72") or "").strip()
        claim = self._claim_for_release(release_hash)
        result = self.execution_ledger.result_for_claim(claim["record_hash72"])
        if result is None:
            raise Pass218ExecutionValidationError("P218_I17_DISTRIBUTED_TERMINAL_RESULT_REQUIRED")
        self._finalize_result(claim, result)
        return self.reconcile_release(release_hash)


__all__ = ["Pass218FencedExternalExecutionControlPlane"]

"""Pass 218 Iteration 15 one-time maintenance release consumption.

I15 is downstream of I12-I14.  It turns a valid I14 maintenance release into
exactly one durable external-maintenance execution attempt, then seals the
terminal attestation and reconciliation evidence.  Claiming a release is the
execution-start boundary: a claimed, failed, aborted, or crashed attempt never
reopens the release.  Retry requires a newly prepared and approved release.

I15 never performs the external I12 operation itself and never acquires,
releases, or mints canonical authority.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.approval_i14 import validate_maintenance_release
from hhs_runtime.pass218.authority_maintenance_i12 import (
    CREDENTIAL_ROTATION_PLAN_SCHEMA,
    MEMBER_REPLACEMENT_PLAN_SCHEMA,
    SNAPSHOT_RETENTION_RECEIPT_SCHEMA,
    validate_credential_rotation_plan,
    validate_member_replacement_plan,
    validate_snapshot_retention_receipt,
)
from hhs_runtime.pass218.observability_i13 import validate_maintenance_run_receipt

PASS218_ONE_TIME_EXECUTION_VERSION = "HHS-P218-ONE-TIME-MAINTENANCE-EXECUTION-I15-V1"
RELEASE_CLAIM_SCHEMA = "HHS-P218-I15-RELEASE-CLAIM-V1"
EXECUTION_ATTESTATION_SCHEMA = "HHS-P218-I15-EXECUTION-ATTESTATION-V1"
EXECUTION_RECONCILIATION_SCHEMA = "HHS-P218-I15-EXECUTION-RECONCILIATION-V1"
ACTION_CLAIM_INDEX_SCHEMA = "HHS-P218-I15-ACTION-CLAIM-INDEX-V1"

TERMINAL_OUTCOMES = frozenset({"SUCCEEDED", "FAILED", "ABORTED"})
ACTION_I12_SCHEMA = {
    "PREPARE_CREDENTIAL_ROTATION": CREDENTIAL_ROTATION_PLAN_SCHEMA,
    "PREPARE_MEMBER_REPLACEMENT": MEMBER_REPLACEMENT_PLAN_SCHEMA,
    "REQUEST_SNAPSHOT_REHEARSAL": SNAPSHOT_RETENTION_RECEIPT_SCHEMA,
}


class Pass218ExecutionError(RuntimeError):
    pass


class Pass218ExecutionValidationError(Pass218ExecutionError):
    pass


class Pass218ExecutionReplayRejected(Pass218ExecutionError):
    pass


class Pass218ExecutionStateError(Pass218ExecutionError):
    pass


def _copy(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, separators=(",", ":")))


def _require_text(value: Any, code: str, *, maximum: int = 256) -> str:
    if not isinstance(value, str):
        raise Pass218ExecutionValidationError(code)
    value = value.strip()
    if not value or len(value) > maximum:
        raise Pass218ExecutionValidationError(code)
    return value


def _require_hash72(value: Any, code: str) -> str:
    value = _require_text(value, code, maximum=72)
    if len(value) != 72:
        raise Pass218ExecutionValidationError(code)
    try:
        validate_hash72(value)
    except Exception as exc:
        raise Pass218ExecutionValidationError(code) from exc
    return value


def _require_nonnegative_int(value: Any, code: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise Pass218ExecutionValidationError(code)
    return value


def _require_positive_int(value: Any, code: str) -> int:
    value = _require_nonnegative_int(value, code)
    if value < 1:
        raise Pass218ExecutionValidationError(code)
    return value


def _exclusions() -> dict[str, bool]:
    return {
        "canonical_authority_minted": False,
        "canonical_mutation_permitted": False,
        "canonical_learning_commit_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "verbatim_source_retained": False,
        "pass165_source_retaining_path_invoked": False,
        "authoritative_float_weights": False,
    }


def _assert_exclusions(record: Mapping[str, Any]) -> None:
    for key in _exclusions():
        if record.get(key) is not False:
            raise Pass218ExecutionValidationError("P218_I15_EXCLUSION_VIOLATION_" + key.upper())


def _seal(schema: str, body: Mapping[str, Any]) -> dict[str, Any]:
    value = dict(body)
    value["record_hash72"] = hash72_digest({"domain": schema}, value)
    return value


def _validate_seal(schema: str, record: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise Pass218ExecutionValidationError("P218_I15_RECORD_INVALID")
    value = dict(record)
    received = _require_hash72(value.pop("record_hash72", None), "P218_I15_RECORD_HASH_INVALID")
    if received != hash72_digest({"domain": schema}, value):
        raise Pass218ExecutionValidationError("P218_I15_RECORD_SEAL_MISMATCH")
    value["record_hash72"] = received
    return value


def validate_i12_maintenance_record(action: str, record: Mapping[str, Any]) -> dict[str, Any]:
    action = _require_text(action, "P218_I15_ACTION_INVALID").upper()
    if action == "PREPARE_CREDENTIAL_ROTATION":
        value = validate_credential_rotation_plan(record)
    elif action == "PREPARE_MEMBER_REPLACEMENT":
        value = validate_member_replacement_plan(record)
    elif action == "REQUEST_SNAPSHOT_REHEARSAL":
        value = validate_snapshot_retention_receipt(record)
    else:
        raise Pass218ExecutionValidationError("P218_I15_ACTION_NOT_MAINTENANCE")
    expected = ACTION_I12_SCHEMA[action]
    if value.get("schema") != expected:
        raise Pass218ExecutionValidationError("P218_I15_I12_SCHEMA_MISMATCH")
    return value


def _validate_preflight(release: Mapping[str, Any], preflight: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(preflight, Mapping) or preflight.get("schema") != "HHS-P218-I14-MAINTENANCE-PREFLIGHT-V1":
        raise Pass218ExecutionValidationError("P218_I15_I14_PREFLIGHT_INVALID")
    if preflight.get("ok") is not True:
        raise Pass218ExecutionValidationError("P218_I15_I14_PREFLIGHT_NOT_READY")
    for key in (
        "approval_quorum_satisfied",
        "separation_of_duties_satisfied",
        "current_quorum_satisfied",
        "current_writer_fence_satisfied",
        "recorded_revocations_rechecked",
        "maintenance_remains_external",
    ):
        if preflight.get(key) is not True:
            raise Pass218ExecutionValidationError("P218_I15_PREFLIGHT_INVARIANT_" + key.upper())
    if preflight.get("release_record_hash72") != release.get("record_hash72"):
        raise Pass218ExecutionValidationError("P218_I15_PREFLIGHT_RELEASE_MISMATCH")
    if preflight.get("action_record_hash72") != release.get("action_record_hash72"):
        raise Pass218ExecutionValidationError("P218_I15_PREFLIGHT_ACTION_MISMATCH")
    if preflight.get("distributed_fence_epoch") != release.get("distributed_fence_epoch"):
        raise Pass218ExecutionValidationError("P218_I15_PREFLIGHT_FENCE_MISMATCH")
    _require_hash72(preflight.get("current_status_hash72"), "P218_I15_PREFLIGHT_STATUS_HASH_INVALID")
    return dict(preflight)


def seal_release_claim(*, release: Mapping[str, Any], preflight: Mapping[str, Any], claimed_epoch_ns: int) -> dict[str, Any]:
    release_value = validate_maintenance_release(release)
    preflight_value = _validate_preflight(release_value, preflight)
    claimed_ns = _require_positive_int(claimed_epoch_ns, "P218_I15_CLAIM_EPOCH_INVALID")
    attempt_id = "i15-" + hash72_digest(
        {"domain": "HHS-P218-I15-ATTEMPT-ID"},
        {
            "release_record_hash72": release_value["record_hash72"],
            "action_record_hash72": release_value["action_record_hash72"],
            "executor_operator_id": release_value["executor_operator_id"],
            "distributed_fence_epoch": release_value["distributed_fence_epoch"],
            "claimed_epoch_ns": claimed_ns,
        },
    )
    return _seal(RELEASE_CLAIM_SCHEMA, {
        "schema": RELEASE_CLAIM_SCHEMA,
        "version": PASS218_ONE_TIME_EXECUTION_VERSION,
        "attempt_id": attempt_id,
        "release_record_hash72": release_value["record_hash72"],
        "action_record_hash72": release_value["action_record_hash72"],
        "action": release_value["action"],
        "executor_operator_id": release_value["executor_operator_id"],
        "distributed_fence_epoch": release_value["distributed_fence_epoch"],
        "preflight_status_hash72": preflight_value["current_status_hash72"],
        "claimed_epoch_ns": claimed_ns,
        "release_consumed": True,
        "single_use_release": True,
        "single_execution_per_action": True,
        "consume_before_execute": True,
        "claim_is_execution_start_boundary": True,
        "crash_does_not_reopen_release": True,
        "retry_requires_new_release": True,
        "external_i12_execution_only": True,
        **_exclusions(),
    })


def validate_release_claim(record: Mapping[str, Any]) -> dict[str, Any]:
    value = _validate_seal(RELEASE_CLAIM_SCHEMA, record)
    if value.get("schema") != RELEASE_CLAIM_SCHEMA:
        raise Pass218ExecutionValidationError("P218_I15_CLAIM_SCHEMA_INVALID")
    _require_hash72(value.get("release_record_hash72"), "P218_I15_RELEASE_HASH_INVALID")
    _require_hash72(value.get("action_record_hash72"), "P218_I15_ACTION_HASH_INVALID")
    _require_hash72(value.get("preflight_status_hash72"), "P218_I15_STATUS_HASH_INVALID")
    _require_positive_int(value.get("distributed_fence_epoch"), "P218_I15_FENCE_INVALID")
    _require_positive_int(value.get("claimed_epoch_ns"), "P218_I15_CLAIM_EPOCH_INVALID")
    for key in (
        "release_consumed", "single_use_release", "single_execution_per_action",
        "consume_before_execute", "claim_is_execution_start_boundary",
        "crash_does_not_reopen_release", "retry_requires_new_release",
        "external_i12_execution_only",
    ):
        if value.get(key) is not True:
            raise Pass218ExecutionValidationError("P218_I15_CLAIM_INVARIANT_" + key.upper())
    _assert_exclusions(value)
    return value


def seal_execution_attestation(
    *,
    claim: Mapping[str, Any],
    outcome: str,
    completed_epoch_ns: int,
    external_result_hash72: str,
    external_operation_executed: bool,
    i12_maintenance_record: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    claim_value = validate_release_claim(claim)
    normalized_outcome = _require_text(outcome, "P218_I15_OUTCOME_INVALID").upper()
    if normalized_outcome not in TERMINAL_OUTCOMES:
        raise Pass218ExecutionValidationError("P218_I15_OUTCOME_INVALID")
    completed_ns = _require_positive_int(completed_epoch_ns, "P218_I15_COMPLETE_EPOCH_INVALID")
    if completed_ns < claim_value["claimed_epoch_ns"]:
        raise Pass218ExecutionValidationError("P218_I15_EXECUTION_EPOCH_ORDER_INVALID")
    executed = bool(external_operation_executed)
    if normalized_outcome == "SUCCEEDED" and not executed:
        raise Pass218ExecutionValidationError("P218_I15_SUCCESS_REQUIRES_EXTERNAL_EXECUTION")
    i12_value: dict[str, Any] | None = None
    if i12_maintenance_record is not None:
        i12_value = validate_i12_maintenance_record(claim_value["action"], i12_maintenance_record)
    if normalized_outcome == "SUCCEEDED" and i12_value is None:
        raise Pass218ExecutionValidationError("P218_I15_SUCCESS_REQUIRES_I12_EVIDENCE")
    return _seal(EXECUTION_ATTESTATION_SCHEMA, {
        "schema": EXECUTION_ATTESTATION_SCHEMA,
        "version": PASS218_ONE_TIME_EXECUTION_VERSION,
        "attempt_id": claim_value["attempt_id"],
        "claim_record_hash72": claim_value["record_hash72"],
        "release_record_hash72": claim_value["release_record_hash72"],
        "action_record_hash72": claim_value["action_record_hash72"],
        "action": claim_value["action"],
        "executor_operator_id": claim_value["executor_operator_id"],
        "distributed_fence_epoch": claim_value["distributed_fence_epoch"],
        "outcome": normalized_outcome,
        "external_operation_executed": executed,
        "external_result_hash72": _require_hash72(external_result_hash72, "P218_I15_EXTERNAL_RESULT_HASH_INVALID"),
        "i12_evidence_present": i12_value is not None,
        "i12_maintenance_schema": i12_value.get("schema") if i12_value is not None else None,
        "i12_maintenance_record_hash72": i12_value.get("record_hash72") if i12_value is not None else None,
        "completed_epoch_ns": completed_ns,
        "release_permanently_consumed": True,
        "terminal_attempt": True,
        "retry_requires_new_release": True,
        **_exclusions(),
    })


def validate_execution_attestation(record: Mapping[str, Any]) -> dict[str, Any]:
    value = _validate_seal(EXECUTION_ATTESTATION_SCHEMA, record)
    if value.get("schema") != EXECUTION_ATTESTATION_SCHEMA or value.get("outcome") not in TERMINAL_OUTCOMES:
        raise Pass218ExecutionValidationError("P218_I15_ATTESTATION_SCHEMA_OR_OUTCOME_INVALID")
    for key in ("claim_record_hash72", "release_record_hash72", "action_record_hash72", "external_result_hash72"):
        _require_hash72(value.get(key), "P218_I15_ATTESTATION_HASH_INVALID")
    if value.get("i12_evidence_present") is True:
        if value.get("i12_maintenance_schema") != ACTION_I12_SCHEMA.get(value.get("action")):
            raise Pass218ExecutionValidationError("P218_I15_I12_SCHEMA_MISMATCH")
        _require_hash72(value.get("i12_maintenance_record_hash72"), "P218_I15_I12_RECORD_HASH_INVALID")
    elif value.get("outcome") == "SUCCEEDED":
        raise Pass218ExecutionValidationError("P218_I15_SUCCESS_REQUIRES_I12_EVIDENCE")
    if value.get("outcome") == "SUCCEEDED" and value.get("external_operation_executed") is not True:
        raise Pass218ExecutionValidationError("P218_I15_SUCCESS_REQUIRES_EXTERNAL_EXECUTION")
    if value.get("release_permanently_consumed") is not True or value.get("terminal_attempt") is not True or value.get("retry_requires_new_release") is not True:
        raise Pass218ExecutionValidationError("P218_I15_TERMINAL_INVARIANT_INVALID")
    _assert_exclusions(value)
    return value


def seal_execution_reconciliation(*, claim: Mapping[str, Any], attestation: Mapping[str, Any], i13_run_receipt: Mapping[str, Any]) -> dict[str, Any]:
    claim_value = validate_release_claim(claim)
    attestation_value = validate_execution_attestation(attestation)
    run = validate_maintenance_run_receipt(i13_run_receipt)
    if attestation_value["claim_record_hash72"] != claim_value["record_hash72"]:
        raise Pass218ExecutionValidationError("P218_I15_RECONCILIATION_CLAIM_MISMATCH")
    if run.get("action_record_hash72") != claim_value["action_record_hash72"] or run.get("action") != claim_value["action"]:
        raise Pass218ExecutionValidationError("P218_I15_RECONCILIATION_ACTION_MISMATCH")
    if run.get("outcome") != attestation_value["outcome"] or bool(run.get("external_operation_executed")) != bool(attestation_value["external_operation_executed"]):
        raise Pass218ExecutionValidationError("P218_I15_RECONCILIATION_OUTCOME_MISMATCH")
    return _seal(EXECUTION_RECONCILIATION_SCHEMA, {
        "schema": EXECUTION_RECONCILIATION_SCHEMA,
        "version": PASS218_ONE_TIME_EXECUTION_VERSION,
        "attempt_id": claim_value["attempt_id"],
        "release_record_hash72": claim_value["release_record_hash72"],
        "action_record_hash72": claim_value["action_record_hash72"],
        "claim_record_hash72": claim_value["record_hash72"],
        "attestation_record_hash72": attestation_value["record_hash72"],
        "i13_run_receipt_hash72": run["record_hash72"],
        "i12_maintenance_record_hash72": attestation_value.get("i12_maintenance_record_hash72"),
        "outcome": attestation_value["outcome"],
        "external_operation_executed": bool(attestation_value["external_operation_executed"]),
        "reconciled_into_i13": True,
        "reconciled_into_i14_namespace": True,
        "release_permanently_consumed": True,
        "no_second_execution_permitted": True,
        **_exclusions(),
    })


def validate_execution_reconciliation(record: Mapping[str, Any]) -> dict[str, Any]:
    value = _validate_seal(EXECUTION_RECONCILIATION_SCHEMA, record)
    if value.get("schema") != EXECUTION_RECONCILIATION_SCHEMA or value.get("outcome") not in TERMINAL_OUTCOMES:
        raise Pass218ExecutionValidationError("P218_I15_RECONCILIATION_SCHEMA_INVALID")
    for key in ("release_record_hash72", "action_record_hash72", "claim_record_hash72", "attestation_record_hash72", "i13_run_receipt_hash72"):
        _require_hash72(value.get(key), "P218_I15_RECONCILIATION_HASH_INVALID")
    if value.get("reconciled_into_i13") is not True or value.get("reconciled_into_i14_namespace") is not True:
        raise Pass218ExecutionValidationError("P218_I15_RECONCILIATION_TARGET_INVALID")
    if value.get("release_permanently_consumed") is not True or value.get("no_second_execution_permitted") is not True:
        raise Pass218ExecutionValidationError("P218_I15_RECONCILIATION_REPLAY_RULE_INVALID")
    _assert_exclusions(value)
    return value


def _key(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class Pass218ReleaseConsumptionJournal:
    """Durable local journal; I10/I11 fence binding makes claims globally stale on failover."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.claims = self.root / "claims"
        self.action_claims = self.root / "action-claims"
        self.attestations = self.root / "attestations"
        for path in (self.claims, self.action_claims, self.attestations):
            path.mkdir(parents=True, exist_ok=True)
        self.lock_path = self.root / "claim.lock"
        self.lock_path.touch(exist_ok=True)

    @staticmethod
    def _read(path: Path) -> dict[str, Any] | None:
        if not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

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

    def _claim_path(self, release_hash: str) -> Path:
        return self.claims / (_key(release_hash) + ".json")

    def _action_path(self, action_hash: str) -> Path:
        return self.action_claims / (_key(action_hash) + ".json")

    def _attestation_path(self, release_hash: str) -> Path:
        return self.attestations / (_key(release_hash) + ".json")

    def claim_release(self, *, release: Mapping[str, Any], preflight: Mapping[str, Any], claimed_epoch_ns: int) -> dict[str, Any]:
        candidate = seal_release_claim(release=release, preflight=preflight, claimed_epoch_ns=claimed_epoch_ns)
        release_hash = candidate["release_record_hash72"]
        action_hash = candidate["action_record_hash72"]
        with self.lock_path.open("r+") as lock_handle:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
            if self._claim_path(release_hash).exists():
                raise Pass218ExecutionReplayRejected("P218_I15_RELEASE_ALREADY_CONSUMED")
            existing_action = self._read(self._action_path(action_hash))
            if existing_action is not None:
                raise Pass218ExecutionReplayRejected("P218_I15_ACTION_ALREADY_CLAIMED")
            self._atomic_create(self._claim_path(release_hash), candidate)
            index = {
                "schema": ACTION_CLAIM_INDEX_SCHEMA,
                "action_record_hash72": action_hash,
                "release_record_hash72": release_hash,
                "claim_record_hash72": candidate["record_hash72"],
            }
            self._atomic_create(self._action_path(action_hash), index)
        return _copy(candidate)

    def claim_for_release(self, release_hash: str) -> dict[str, Any] | None:
        raw = self._read(self._claim_path(_require_hash72(release_hash, "P218_I15_RELEASE_HASH_INVALID")))
        return validate_release_claim(raw) if raw is not None else None

    def attestation_for_release(self, release_hash: str) -> dict[str, Any] | None:
        raw = self._read(self._attestation_path(_require_hash72(release_hash, "P218_I15_RELEASE_HASH_INVALID")))
        return validate_execution_attestation(raw) if raw is not None else None

    def record_attestation(self, *, release_hash: str, attestation: Mapping[str, Any]) -> dict[str, Any]:
        release_hash = _require_hash72(release_hash, "P218_I15_RELEASE_HASH_INVALID")
        value = validate_execution_attestation(attestation)
        claim = self.claim_for_release(release_hash)
        if claim is None:
            raise Pass218ExecutionStateError("P218_I15_RELEASE_NOT_CLAIMED")
        if value["claim_record_hash72"] != claim["record_hash72"] or value["release_record_hash72"] != release_hash:
            raise Pass218ExecutionValidationError("P218_I15_ATTESTATION_CLAIM_MISMATCH")
        path = self._attestation_path(release_hash)
        with self.lock_path.open("r+") as lock_handle:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
            if path.exists():
                raise Pass218ExecutionReplayRejected("P218_I15_TERMINAL_ATTESTATION_ALREADY_RECORDED")
            self._atomic_create(path, value)
        return _copy(value)

    def status(self) -> dict[str, int | bool | str]:
        claimed = len(list(self.claims.glob("*.json")))
        terminal = len(list(self.attestations.glob("*.json")))
        return {
            "schema": "HHS-P218-I15-CONSUMPTION-JOURNAL-STATUS-V1",
            "claimed_release_count": claimed,
            "terminal_attestation_count": terminal,
            "claimed_without_terminal_count": max(0, claimed - terminal),
            "single_use_release_enforced": True,
            "single_execution_per_action_enforced": True,
            "crash_does_not_reopen_release": True,
        }


__all__ = [
    "ACTION_I12_SCHEMA",
    "EXECUTION_ATTESTATION_SCHEMA",
    "EXECUTION_RECONCILIATION_SCHEMA",
    "PASS218_ONE_TIME_EXECUTION_VERSION",
    "RELEASE_CLAIM_SCHEMA",
    "TERMINAL_OUTCOMES",
    "Pass218ExecutionError",
    "Pass218ExecutionReplayRejected",
    "Pass218ExecutionStateError",
    "Pass218ExecutionValidationError",
    "Pass218ReleaseConsumptionJournal",
    "seal_execution_attestation",
    "seal_execution_reconciliation",
    "seal_release_claim",
    "validate_execution_attestation",
    "validate_execution_reconciliation",
    "validate_i12_maintenance_record",
    "validate_release_claim",
]

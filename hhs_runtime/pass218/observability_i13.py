"""Pass 218 Iteration 13 production authority observability/orchestration.

Iteration 13 is strictly downstream of the frozen I9-I12 authority chain.  It
projects sealed operator-visible health state, alerts, maintenance scheduling,
and bounded operator intents.  It never acquires/releases canonical ownership,
advances a global fence, mutates the canonical target, or weakens quorum rules.

All policy counters and epochs are integers.  No authoritative floating-point
state, source retention, learning authority, truth promotion, or action
authority is introduced here.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72

PASS218_AUTHORITY_OBSERVABILITY_VERSION = "HHS-P218-AUTHORITY-OBSERVABILITY-ORCHESTRATION-I13-V1"
OBSERVABILITY_POLICY_SCHEMA = "HHS-P218-I13-OBSERVABILITY-POLICY-V1"
AUTHORITY_STATUS_SCHEMA = "HHS-P218-I13-AUTHORITY-OBSERVABILITY-STATUS-V1"
OPERATOR_ACTION_SCHEMA = "HHS-P218-I13-OPERATOR-ACTION-V1"
MAINTENANCE_RUN_RECEIPT_SCHEMA = "HHS-P218-I13-MAINTENANCE-RUN-RECEIPT-V1"
OPERATOR_JOURNAL_SCHEMA = "HHS-P218-I13-OPERATOR-JOURNAL-V1"

ALERT_SEVERITIES = frozenset({"INFO", "WARNING", "CRITICAL"})
OPERATOR_ACTIONS = frozenset({
    "PROBE_CLUSTER",
    "PREPARE_CREDENTIAL_ROTATION",
    "PREPARE_MEMBER_REPLACEMENT",
    "REQUEST_SNAPSHOT_REHEARSAL",
    "ACKNOWLEDGE_ALERT",
    "EXPORT_EVIDENCE",
})
MAINTENANCE_ACTIONS = frozenset({
    "PREPARE_CREDENTIAL_ROTATION",
    "PREPARE_MEMBER_REPLACEMENT",
    "REQUEST_SNAPSHOT_REHEARSAL",
})
RUN_OUTCOMES = frozenset({"SUCCEEDED", "FAILED", "ABORTED"})


class Pass218AuthorityObservabilityError(RuntimeError):
    pass


class Pass218AuthorityObservabilityValidationError(Pass218AuthorityObservabilityError):
    pass


class Pass218OperatorActionRejected(Pass218AuthorityObservabilityError):
    pass


def _require_positive_int(value: Any, code: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise Pass218AuthorityObservabilityValidationError(code)
    return value


def _require_nonnegative_int(value: Any, code: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise Pass218AuthorityObservabilityValidationError(code)
    return value


def _require_text(value: Any, code: str, *, maximum: int = 256) -> str:
    if not isinstance(value, str):
        raise Pass218AuthorityObservabilityValidationError(code)
    value = value.strip()
    if not value or len(value) > maximum:
        raise Pass218AuthorityObservabilityValidationError(code)
    return value


def _require_hash72(value: Any, code: str) -> str:
    value = _require_text(value, code, maximum=72)
    if len(value) != 72:
        raise Pass218AuthorityObservabilityValidationError(code)
    try:
        validate_hash72(value)
    except Exception as exc:
        raise Pass218AuthorityObservabilityValidationError(code) from exc
    return value


def _copy(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, separators=(",", ":")))


def _seal(schema: str, body: Mapping[str, Any]) -> dict[str, Any]:
    record = dict(body)
    record["record_hash72"] = hash72_digest({"domain": schema}, record)
    return record


def _validate_seal(schema: str, record: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise Pass218AuthorityObservabilityValidationError("P218_I13_RECORD_INVALID")
    body = dict(record)
    received = _require_hash72(
        body.pop("record_hash72", None),
        "P218_I13_RECORD_HASH72_INVALID",
    )
    expected = hash72_digest({"domain": schema}, body)
    if received != expected:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_RECORD_SEAL_MISMATCH")
    body["record_hash72"] = received
    return body


def _assert_exclusions(record: Mapping[str, Any]) -> None:
    for key in (
        "canonical_authority_minted",
        "canonical_mutation_permitted",
        "canonical_learning_commit_invoked",
        "truth_promotion",
        "action_authority_minted",
        "verbatim_source_retained",
        "pass165_source_retaining_path_invoked",
        "authoritative_float_weights",
    ):
        if record.get(key) is not False:
            raise Pass218AuthorityObservabilityValidationError(
                "P218_I13_EXCLUSION_VIOLATION_" + key.upper()
            )


@dataclass(frozen=True)
class Pass218ObservabilityPolicy:
    certificate_warning_seconds: int
    snapshot_max_age_seconds: int
    rehearsal_max_age_seconds: int
    max_pending_operator_actions: int

    @classmethod
    def build(
        cls,
        *,
        certificate_warning_seconds: int = 2592000,
        snapshot_max_age_seconds: int = 86400,
        rehearsal_max_age_seconds: int = 604800,
        max_pending_operator_actions: int = 8,
    ) -> "Pass218ObservabilityPolicy":
        return cls(
            certificate_warning_seconds=_require_positive_int(
                certificate_warning_seconds,
                "P218_I13_CERT_WARNING_INVALID",
            ),
            snapshot_max_age_seconds=_require_positive_int(
                snapshot_max_age_seconds,
                "P218_I13_SNAPSHOT_MAX_AGE_INVALID",
            ),
            rehearsal_max_age_seconds=_require_positive_int(
                rehearsal_max_age_seconds,
                "P218_I13_REHEARSAL_MAX_AGE_INVALID",
            ),
            max_pending_operator_actions=_require_positive_int(
                max_pending_operator_actions,
                "P218_I13_PENDING_ACTION_LIMIT_INVALID",
            ),
        )

    def record(self) -> dict[str, Any]:
        return _seal(
            OBSERVABILITY_POLICY_SCHEMA,
            {
                "schema": OBSERVABILITY_POLICY_SCHEMA,
                "observability_version": PASS218_AUTHORITY_OBSERVABILITY_VERSION,
                "certificate_warning_seconds": self.certificate_warning_seconds,
                "snapshot_max_age_seconds": self.snapshot_max_age_seconds,
                "rehearsal_max_age_seconds": self.rehearsal_max_age_seconds,
                "max_pending_operator_actions": self.max_pending_operator_actions,
                "operator_actions_are_preparatory_only": True,
                "external_executor_required_for_maintenance": True,
                "canonical_authority_minted": False,
                "canonical_mutation_permitted": False,
                "canonical_learning_commit_invoked": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "verbatim_source_retained": False,
                "pass165_source_retaining_path_invoked": False,
                "authoritative_float_weights": False,
            },
        )


def validate_observability_policy(record: Mapping[str, Any]) -> dict[str, Any]:
    value = _validate_seal(OBSERVABILITY_POLICY_SCHEMA, record)
    if value.get("schema") != OBSERVABILITY_POLICY_SCHEMA:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_POLICY_SCHEMA_INVALID")
    Pass218ObservabilityPolicy.build(
        certificate_warning_seconds=value.get("certificate_warning_seconds"),
        snapshot_max_age_seconds=value.get("snapshot_max_age_seconds"),
        rehearsal_max_age_seconds=value.get("rehearsal_max_age_seconds"),
        max_pending_operator_actions=value.get("max_pending_operator_actions"),
    )
    if value.get("operator_actions_are_preparatory_only") is not True:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_PREPARATORY_ONLY_REQUIRED")
    if value.get("external_executor_required_for_maintenance") is not True:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_EXTERNAL_EXECUTOR_REQUIRED")
    _assert_exclusions(value)
    return value


def _alert(code: str, severity: str, detail: str) -> dict[str, str]:
    if severity not in ALERT_SEVERITIES:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_ALERT_SEVERITY_INVALID")
    return {
        "code": _require_text(code, "P218_I13_ALERT_CODE_INVALID"),
        "severity": severity,
        "detail": _require_text(detail, "P218_I13_ALERT_DETAIL_INVALID", maximum=512),
    }


def _optional_epoch(value: Any, code: str) -> int | None:
    if value is None:
        return None
    return _require_nonnegative_int(value, code)


def build_authority_observability_status(
    *,
    lifecycle_status: Mapping[str, Any],
    policy: Pass218ObservabilityPolicy,
    now_epoch_seconds: int,
    certificate_not_after_epoch_seconds: int | None = None,
    latest_snapshot_epoch_seconds: int | None = None,
    latest_rehearsal_epoch_seconds: int | None = None,
    pending_operator_actions: int = 0,
) -> dict[str, Any]:
    if not isinstance(lifecycle_status, Mapping):
        raise Pass218AuthorityObservabilityValidationError("P218_I13_LIFECYCLE_STATUS_INVALID")
    now = _require_nonnegative_int(now_epoch_seconds, "P218_I13_NOW_INVALID")
    cert_not_after = _optional_epoch(
        certificate_not_after_epoch_seconds,
        "P218_I13_CERT_NOT_AFTER_INVALID",
    )
    snapshot_epoch = _optional_epoch(
        latest_snapshot_epoch_seconds,
        "P218_I13_SNAPSHOT_EPOCH_INVALID",
    )
    rehearsal_epoch = _optional_epoch(
        latest_rehearsal_epoch_seconds,
        "P218_I13_REHEARSAL_EPOCH_INVALID",
    )
    pending = _require_nonnegative_int(
        pending_operator_actions,
        "P218_I13_PENDING_ACTIONS_INVALID",
    )

    alerts: list[dict[str, str]] = []
    cluster_quorum_ready = lifecycle_status.get("cluster_quorum_ready")
    distributed_held = bool(lifecycle_status.get("distributed_authority_held"))
    startup_complete = bool(lifecycle_status.get("startup_complete"))
    ingestion_enabled = bool(lifecycle_status.get("ingestion_enabled"))

    if cluster_quorum_ready is False:
        alerts.append(_alert(
            "P218_I13_QUORUM_BLOCKED",
            "CRITICAL",
            "I11 cluster quorum is not ready; canonical ingress must remain fail-closed.",
        ))
    elif cluster_quorum_ready is True and not distributed_held:
        alerts.append(_alert(
            "P218_I13_WRITER_NOT_HELD",
            "WARNING",
            "I11 quorum is visible but this process does not currently hold the I10 distributed writer fence.",
        ))

    if startup_complete and not ingestion_enabled:
        alerts.append(_alert(
            "P218_I13_INGRESS_CLOSED",
            "WARNING" if cluster_quorum_ready is not False else "CRITICAL",
            "Runtime startup completed while Pass 218 canonical ingress remains closed.",
        ))

    certificate_seconds_remaining: int | None = None
    if cert_not_after is None:
        alerts.append(_alert(
            "P218_I13_CERT_EXPIRY_UNKNOWN",
            "WARNING",
            "Client certificate expiry is not available to the observability plane.",
        ))
    else:
        certificate_seconds_remaining = cert_not_after - now
        if certificate_seconds_remaining <= 0:
            alerts.append(_alert(
                "P218_I13_CERT_EXPIRED",
                "CRITICAL",
                "Configured client certificate is expired.",
            ))
        elif certificate_seconds_remaining <= policy.certificate_warning_seconds:
            alerts.append(_alert(
                "P218_I13_CERT_EXPIRY_NEAR",
                "WARNING",
                "Configured client certificate is within the rotation warning window.",
            ))

    snapshot_age_seconds: int | None = None
    if snapshot_epoch is None:
        alerts.append(_alert(
            "P218_I13_SNAPSHOT_MISSING",
            "WARNING",
            "No retained production snapshot timestamp is recorded in the operator journal.",
        ))
    else:
        snapshot_age_seconds = max(0, now - snapshot_epoch)
        if snapshot_age_seconds > policy.snapshot_max_age_seconds:
            alerts.append(_alert(
                "P218_I13_SNAPSHOT_STALE",
                "WARNING",
                "Latest retained snapshot exceeds the configured maximum age.",
            ))

    rehearsal_age_seconds: int | None = None
    if rehearsal_epoch is None:
        alerts.append(_alert(
            "P218_I13_REHEARSAL_MISSING",
            "WARNING",
            "No successful recovery-rehearsal timestamp is recorded in the operator journal.",
        ))
    else:
        rehearsal_age_seconds = max(0, now - rehearsal_epoch)
        if rehearsal_age_seconds > policy.rehearsal_max_age_seconds:
            alerts.append(_alert(
                "P218_I13_REHEARSAL_DUE",
                "WARNING",
                "Recovery rehearsal is due under the configured bounded schedule policy.",
            ))

    if pending > policy.max_pending_operator_actions:
        alerts.append(_alert(
            "P218_I13_OPERATOR_BACKLOG_LIMIT",
            "WARNING",
            "Pending operator intents exceed the configured observability policy limit.",
        ))

    has_critical = any(item["severity"] == "CRITICAL" for item in alerts)
    has_warning = any(item["severity"] == "WARNING" for item in alerts)
    health = "BLOCKED" if has_critical else ("DEGRADED" if has_warning else "READY")

    fence_epoch = lifecycle_status.get("distributed_fence_epoch")
    if fence_epoch is not None:
        fence_epoch = _require_positive_int(fence_epoch, "P218_I13_FENCE_EPOCH_INVALID")

    body = {
        "schema": AUTHORITY_STATUS_SCHEMA,
        "observability_version": PASS218_AUTHORITY_OBSERVABILITY_VERSION,
        "policy_hash72": policy.record()["record_hash72"],
        "observed_epoch_seconds": now,
        "health": health,
        "startup_complete": startup_complete,
        "ingestion_enabled": ingestion_enabled,
        "local_authority_held": bool(lifecycle_status.get("local_authority_held")),
        "distributed_authority_held": distributed_held,
        "distributed_fence_epoch": fence_epoch,
        "cluster_quorum_ready": cluster_quorum_ready,
        "cluster_identity_consistent": lifecycle_status.get("cluster_identity_consistent"),
        "cluster_linearizable_read_ready": lifecycle_status.get("cluster_linearizable_read_ready"),
        "cluster_expected_member_count": lifecycle_status.get("cluster_expected_member_count"),
        "cluster_quorum_size": lifecycle_status.get("cluster_quorum_size"),
        "cluster_reachable_member_count": lifecycle_status.get("cluster_reachable_member_count"),
        "cluster_unavailable_member_count": lifecycle_status.get("cluster_unavailable_member_count"),
        "cluster_id": lifecycle_status.get("cluster_id"),
        "cluster_member_ids": list(lifecycle_status.get("cluster_member_ids") or []),
        "cluster_leader_ids": list(lifecycle_status.get("cluster_leader_ids") or []),
        "cluster_probe_hash72": lifecycle_status.get("cluster_probe_hash72"),
        "quorum_loss_count": lifecycle_status.get("quorum_loss_count", 0),
        "quorum_recovery_count": lifecycle_status.get("quorum_recovery_count", 0),
        "certificate_not_after_epoch_seconds": cert_not_after,
        "certificate_seconds_remaining": certificate_seconds_remaining,
        "latest_snapshot_epoch_seconds": snapshot_epoch,
        "snapshot_age_seconds": snapshot_age_seconds,
        "latest_rehearsal_epoch_seconds": rehearsal_epoch,
        "rehearsal_age_seconds": rehearsal_age_seconds,
        "pending_operator_actions": pending,
        "alerts": alerts,
        "alert_count": len(alerts),
        "critical_alert_count": sum(1 for item in alerts if item["severity"] == "CRITICAL"),
        "warning_alert_count": sum(1 for item in alerts if item["severity"] == "WARNING"),
        "operator_actions_are_preparatory_only": True,
        "canonical_authority_minted": False,
        "canonical_mutation_permitted": False,
        "canonical_learning_commit_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "verbatim_source_retained": False,
        "pass165_source_retaining_path_invoked": False,
        "authoritative_float_weights": False,
    }
    return _seal(AUTHORITY_STATUS_SCHEMA, body)


def validate_authority_observability_status(record: Mapping[str, Any]) -> dict[str, Any]:
    value = _validate_seal(AUTHORITY_STATUS_SCHEMA, record)
    if value.get("schema") != AUTHORITY_STATUS_SCHEMA:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_STATUS_SCHEMA_INVALID")
    if value.get("health") not in {"READY", "DEGRADED", "BLOCKED"}:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_HEALTH_INVALID")
    alerts = value.get("alerts")
    if not isinstance(alerts, list):
        raise Pass218AuthorityObservabilityValidationError("P218_I13_ALERTS_INVALID")
    if value.get("alert_count") != len(alerts):
        raise Pass218AuthorityObservabilityValidationError("P218_I13_ALERT_COUNT_INVALID")
    for item in alerts:
        if not isinstance(item, Mapping) or item.get("severity") not in ALERT_SEVERITIES:
            raise Pass218AuthorityObservabilityValidationError("P218_I13_ALERT_INVALID")
    if value.get("operator_actions_are_preparatory_only") is not True:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_PREPARATORY_ONLY_REQUIRED")
    _assert_exclusions(value)
    return value


def seal_operator_action(
    *,
    request_id: str,
    operator_id: str,
    action: str,
    status_hash72: str,
    prepared_epoch_seconds: int,
    requires_external_executor: bool,
) -> dict[str, Any]:
    normalized_action = _require_text(action, "P218_I13_ACTION_INVALID").upper()
    if normalized_action not in OPERATOR_ACTIONS:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_ACTION_INVALID")
    external_required = normalized_action in MAINTENANCE_ACTIONS
    if bool(requires_external_executor) != external_required:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_EXTERNAL_EXECUTOR_RULE_INVALID")
    return _seal(
        OPERATOR_ACTION_SCHEMA,
        {
            "schema": OPERATOR_ACTION_SCHEMA,
            "observability_version": PASS218_AUTHORITY_OBSERVABILITY_VERSION,
            "request_id": _require_text(request_id, "P218_I13_REQUEST_ID_INVALID"),
            "operator_id": _require_text(operator_id, "P218_I13_OPERATOR_ID_INVALID"),
            "action": normalized_action,
            "status_hash72": _require_hash72(status_hash72, "P218_I13_STATUS_HASH72_INVALID"),
            "prepared_epoch_seconds": _require_nonnegative_int(
                prepared_epoch_seconds,
                "P218_I13_ACTION_EPOCH_INVALID",
            ),
            "requires_external_executor": external_required,
            "prepared_not_executed": True,
            "canonical_authority_minted": False,
            "canonical_mutation_permitted": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "verbatim_source_retained": False,
            "pass165_source_retaining_path_invoked": False,
            "authoritative_float_weights": False,
        },
    )


def validate_operator_action(record: Mapping[str, Any]) -> dict[str, Any]:
    value = _validate_seal(OPERATOR_ACTION_SCHEMA, record)
    if value.get("schema") != OPERATOR_ACTION_SCHEMA:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_ACTION_SCHEMA_INVALID")
    if value.get("action") not in OPERATOR_ACTIONS:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_ACTION_INVALID")
    _require_hash72(value.get("status_hash72"), "P218_I13_STATUS_HASH72_INVALID")
    expected_external = value.get("action") in MAINTENANCE_ACTIONS
    if value.get("requires_external_executor") is not expected_external:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_EXTERNAL_EXECUTOR_RULE_INVALID")
    if value.get("prepared_not_executed") is not True:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_PREPARED_NOT_EXECUTED_REQUIRED")
    _assert_exclusions(value)
    return value


def seal_maintenance_run_receipt(
    *,
    run_id: str,
    action_record_hash72: str,
    operator_id: str,
    action: str,
    outcome: str,
    started_epoch_seconds: int,
    completed_epoch_seconds: int,
    before_status_hash72: str,
    after_status_hash72: str,
    external_operation_executed: bool,
    canonical_target_changed: bool,
    authority_minted: bool,
) -> dict[str, Any]:
    normalized_action = _require_text(action, "P218_I13_ACTION_INVALID").upper()
    if normalized_action not in OPERATOR_ACTIONS:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_ACTION_INVALID")
    normalized_outcome = _require_text(outcome, "P218_I13_OUTCOME_INVALID").upper()
    if normalized_outcome not in RUN_OUTCOMES:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_OUTCOME_INVALID")
    started = _require_nonnegative_int(started_epoch_seconds, "P218_I13_RUN_START_INVALID")
    completed = _require_nonnegative_int(completed_epoch_seconds, "P218_I13_RUN_COMPLETE_INVALID")
    if completed < started:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_RUN_EPOCH_ORDER_INVALID")
    if canonical_target_changed or authority_minted:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_RUN_CANONICAL_EFFECT_FORBIDDEN")
    return _seal(
        MAINTENANCE_RUN_RECEIPT_SCHEMA,
        {
            "schema": MAINTENANCE_RUN_RECEIPT_SCHEMA,
            "observability_version": PASS218_AUTHORITY_OBSERVABILITY_VERSION,
            "run_id": _require_text(run_id, "P218_I13_RUN_ID_INVALID"),
            "action_record_hash72": _require_hash72(
                action_record_hash72,
                "P218_I13_ACTION_RECORD_HASH72_INVALID",
            ),
            "operator_id": _require_text(operator_id, "P218_I13_OPERATOR_ID_INVALID"),
            "action": normalized_action,
            "outcome": normalized_outcome,
            "started_epoch_seconds": started,
            "completed_epoch_seconds": completed,
            "before_status_hash72": _require_hash72(
                before_status_hash72,
                "P218_I13_BEFORE_STATUS_HASH72_INVALID",
            ),
            "after_status_hash72": _require_hash72(
                after_status_hash72,
                "P218_I13_AFTER_STATUS_HASH72_INVALID",
            ),
            "external_operation_executed": bool(external_operation_executed),
            "canonical_target_changed": False,
            "authority_minted": False,
            "diagnostic_receipt_only": True,
            "canonical_authority_minted": False,
            "canonical_mutation_permitted": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "verbatim_source_retained": False,
            "pass165_source_retaining_path_invoked": False,
            "authoritative_float_weights": False,
        },
    )


def validate_maintenance_run_receipt(record: Mapping[str, Any]) -> dict[str, Any]:
    value = _validate_seal(MAINTENANCE_RUN_RECEIPT_SCHEMA, record)
    if value.get("schema") != MAINTENANCE_RUN_RECEIPT_SCHEMA:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_RUN_SCHEMA_INVALID")
    if value.get("action") not in OPERATOR_ACTIONS or value.get("outcome") not in RUN_OUTCOMES:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_RUN_ENUM_INVALID")
    if value.get("completed_epoch_seconds", -1) < value.get("started_epoch_seconds", 0):
        raise Pass218AuthorityObservabilityValidationError("P218_I13_RUN_EPOCH_ORDER_INVALID")
    if value.get("canonical_target_changed") is not False or value.get("authority_minted") is not False:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_RUN_CANONICAL_EFFECT_FORBIDDEN")
    if value.get("diagnostic_receipt_only") is not True:
        raise Pass218AuthorityObservabilityValidationError("P218_I13_DIAGNOSTIC_RECEIPT_REQUIRED")
    _assert_exclusions(value)
    return value


class Pass218OperatorJournal:
    """Append-only JSONL journal for I13 operator intents and run receipts."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _append(self, kind: str, record: Mapping[str, Any]) -> None:
        envelope = {
            "schema": OPERATOR_JOURNAL_SCHEMA,
            "kind": _require_text(kind, "P218_I13_JOURNAL_KIND_INVALID"),
            "record": _copy(record),
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(envelope, sort_keys=True, separators=(",", ":")) + "\n")

    def append_action(self, record: Mapping[str, Any]) -> None:
        self._append("OPERATOR_ACTION", validate_operator_action(record))

    def append_run_receipt(self, record: Mapping[str, Any]) -> None:
        self._append("MAINTENANCE_RUN", validate_maintenance_run_receipt(record))

    def records(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        values: list[dict[str, Any]] = []
        for raw in self.path.read_text(encoding="utf-8").splitlines():
            if not raw.strip():
                continue
            value = json.loads(raw)
            if value.get("schema") != OPERATOR_JOURNAL_SCHEMA:
                raise Pass218AuthorityObservabilityValidationError("P218_I13_JOURNAL_SCHEMA_INVALID")
            values.append(value)
        return values

    def pending_action_count(self) -> int:
        actions: set[str] = set()
        completed: set[str] = set()
        for item in self.records():
            record = item.get("record") or {}
            if item.get("kind") == "OPERATOR_ACTION":
                actions.add(str(record.get("record_hash72", "")))
            elif item.get("kind") == "MAINTENANCE_RUN":
                completed.add(str(record.get("action_record_hash72", "")))
        return len(actions - completed)

    def latest_success_epoch(self, action: str) -> int | None:
        normalized = _require_text(action, "P218_I13_ACTION_INVALID").upper()
        epochs = [
            int((item.get("record") or {}).get("completed_epoch_seconds"))
            for item in self.records()
            if item.get("kind") == "MAINTENANCE_RUN"
            and (item.get("record") or {}).get("action") == normalized
            and (item.get("record") or {}).get("outcome") == "SUCCEEDED"
            and isinstance((item.get("record") or {}).get("completed_epoch_seconds"), int)
        ]
        return max(epochs) if epochs else None


class Pass218OperatorOrchestrator:
    """Prepare bounded operator intents from a sealed I13 status projection."""

    def __init__(self, *, journal: Pass218OperatorJournal | None = None) -> None:
        self.journal = journal

    def prepare(
        self,
        *,
        request_id: str,
        operator_id: str,
        action: str,
        status: Mapping[str, Any],
        prepared_epoch_seconds: int,
    ) -> dict[str, Any]:
        validated = validate_authority_observability_status(status)
        normalized = _require_text(action, "P218_I13_ACTION_INVALID").upper()
        if normalized not in OPERATOR_ACTIONS:
            raise Pass218OperatorActionRejected("P218_I13_ACTION_NOT_ALLOWED")
        if normalized in MAINTENANCE_ACTIONS:
            if validated.get("health") == "BLOCKED":
                raise Pass218OperatorActionRejected("P218_I13_BLOCKED_STATUS_FORBIDS_MAINTENANCE_PREPARE")
            if validated.get("cluster_quorum_ready") is not True:
                raise Pass218OperatorActionRejected("P218_I13_QUORUM_REQUIRED_FOR_MAINTENANCE_PREPARE")
        if normalized == "PREPARE_MEMBER_REPLACEMENT" and validated.get("cluster_reachable_member_count") != validated.get("cluster_expected_member_count"):
            raise Pass218OperatorActionRejected("P218_I13_FULL_CLUSTER_REQUIRED_BEFORE_MEMBER_REPLACEMENT")
        action_record = seal_operator_action(
            request_id=request_id,
            operator_id=operator_id,
            action=normalized,
            status_hash72=validated["record_hash72"],
            prepared_epoch_seconds=prepared_epoch_seconds,
            requires_external_executor=normalized in MAINTENANCE_ACTIONS,
        )
        if self.journal is not None:
            self.journal.append_action(action_record)
        return action_record


__all__ = [
    "ALERT_SEVERITIES",
    "AUTHORITY_STATUS_SCHEMA",
    "MAINTENANCE_ACTIONS",
    "MAINTENANCE_RUN_RECEIPT_SCHEMA",
    "OBSERVABILITY_POLICY_SCHEMA",
    "OPERATOR_ACTIONS",
    "OPERATOR_ACTION_SCHEMA",
    "OPERATOR_JOURNAL_SCHEMA",
    "PASS218_AUTHORITY_OBSERVABILITY_VERSION",
    "RUN_OUTCOMES",
    "Pass218AuthorityObservabilityError",
    "Pass218AuthorityObservabilityValidationError",
    "Pass218ObservabilityPolicy",
    "Pass218OperatorActionRejected",
    "Pass218OperatorJournal",
    "Pass218OperatorOrchestrator",
    "build_authority_observability_status",
    "seal_maintenance_run_receipt",
    "seal_operator_action",
    "validate_authority_observability_status",
    "validate_maintenance_run_receipt",
    "validate_observability_policy",
    "validate_operator_action",
]

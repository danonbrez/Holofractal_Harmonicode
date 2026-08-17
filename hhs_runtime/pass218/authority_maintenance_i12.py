"""Pass 218 Iteration 12 production authority maintenance membrane.

Iteration 12 is deliberately above the frozen I10/I11 ownership substrate.  It
never mints canonical authority and never changes the I10 lease/CAS fence or the
I11 quorum definition.  It defines exact, sealed operational records for:

* credential rotation with an explicit writer handoff boundary;
* one-member-at-a-time rolling etcd maintenance/replacement;
* snapshot retention and destructive-restore rehearsal policy;
* diagnostic operational alert receipts; and
* bounded recovery that requires a strictly newer I10 global fence after any
  authority-loss event.

All counters and policy values are integers.  No source text, Pass-165 path,
learning authority, truth promotion, action authority, or floating-point
authority is admitted by this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72

PASS218_AUTHORITY_MAINTENANCE_VERSION = "HHS-P218-PRODUCTION-AUTHORITY-MAINTENANCE-I12-V1"
MAINTENANCE_POLICY_SCHEMA = "HHS-P218-I12-MAINTENANCE-POLICY-V1"
CREDENTIAL_ROTATION_PLAN_SCHEMA = "HHS-P218-I12-CREDENTIAL-ROTATION-PLAN-V1"
MEMBER_REPLACEMENT_PLAN_SCHEMA = "HHS-P218-I12-MEMBER-REPLACEMENT-PLAN-V1"
SNAPSHOT_RETENTION_RECEIPT_SCHEMA = "HHS-P218-I12-SNAPSHOT-RETENTION-RECEIPT-V1"
OPERATIONAL_ALERT_RECEIPT_SCHEMA = "HHS-P218-I12-OPERATIONAL-ALERT-RECEIPT-V1"
RECOVERY_STATUS_SCHEMA = "HHS-P218-I12-BOUNDED-RECOVERY-STATUS-V1"

ALERT_SEVERITIES = frozenset({"INFO", "WARNING", "CRITICAL"})
MAINTENANCE_KINDS = frozenset({"CREDENTIAL_ROTATION", "MEMBER_REPLACEMENT", "SNAPSHOT_REHEARSAL"})


class Pass218AuthorityMaintenanceError(RuntimeError):
    pass


class Pass218AuthorityMaintenanceValidationError(Pass218AuthorityMaintenanceError):
    pass


class Pass218AuthorityMaintenanceStateError(Pass218AuthorityMaintenanceError):
    pass


def _require_positive_int(value: Any, code: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise Pass218AuthorityMaintenanceValidationError(code)
    return value


def _require_nonnegative_int(value: Any, code: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise Pass218AuthorityMaintenanceValidationError(code)
    return value


def _require_text(value: Any, code: str, *, maximum: int = 256) -> str:
    if not isinstance(value, str):
        raise Pass218AuthorityMaintenanceValidationError(code)
    value = value.strip()
    if not value or len(value) > maximum:
        raise Pass218AuthorityMaintenanceValidationError(code)
    return value


def _require_sha256(value: Any, code: str) -> str:
    value = _require_text(value, code, maximum=64)
    if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise Pass218AuthorityMaintenanceValidationError(code)
    return value


def _require_hash72(value: Any, code: str) -> str:
    value = _require_text(value, code, maximum=72)
    if len(value) != 72:
        raise Pass218AuthorityMaintenanceValidationError(code)
    try:
        validate_hash72(value)
    except Exception as exc:
        raise Pass218AuthorityMaintenanceValidationError(code) from exc
    return value


def _seal(schema: str, body: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(body)
    payload["record_hash72"] = hash72_digest({"domain": schema}, payload)
    return payload


def _validate_seal(schema: str, record: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_RECORD_INVALID")
    body = dict(record)
    received = _require_hash72(body.pop("record_hash72", None), "P218_I12_RECORD_HASH72_INVALID")
    expected = hash72_digest({"domain": schema}, body)
    if received != expected:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_RECORD_SEAL_MISMATCH")
    body["record_hash72"] = received
    return body


def _assert_exclusions(record: Mapping[str, Any]) -> None:
    required_false = (
        "canonical_learning_commit_invoked",
        "truth_promotion",
        "action_authority_minted",
        "verbatim_source_retained",
        "pass165_source_retaining_path_invoked",
        "authoritative_float_weights",
    )
    for key in required_false:
        if record.get(key) is not False:
            raise Pass218AuthorityMaintenanceValidationError("P218_I12_EXCLUSION_VIOLATION_" + key.upper())


@dataclass(frozen=True)
class Pass218MaintenancePolicy:
    expected_member_count: int
    quorum_size: int
    max_simultaneously_unavailable_members: int
    max_automated_recovery_attempts: int
    snapshot_retention_count: int
    snapshot_rehearsal_interval_seconds: int
    credential_overlap_seconds: int

    @classmethod
    def build(
        cls,
        *,
        expected_member_count: int,
        max_simultaneously_unavailable_members: int = 1,
        max_automated_recovery_attempts: int = 3,
        snapshot_retention_count: int = 7,
        snapshot_rehearsal_interval_seconds: int = 604800,
        credential_overlap_seconds: int = 300,
    ) -> "Pass218MaintenancePolicy":
        member_count = _require_positive_int(expected_member_count, "P218_I12_MEMBER_COUNT_INVALID")
        if member_count < 3 or member_count % 2 == 0:
            raise Pass218AuthorityMaintenanceValidationError("P218_I12_ODD_MULTI_MEMBER_CLUSTER_REQUIRED")
        quorum = member_count // 2 + 1
        max_unavailable = _require_nonnegative_int(
            max_simultaneously_unavailable_members,
            "P218_I12_MAX_UNAVAILABLE_INVALID",
        )
        if max_unavailable < 1 or member_count - max_unavailable < quorum:
            raise Pass218AuthorityMaintenanceValidationError("P218_I12_POLICY_MUST_PRESERVE_QUORUM")
        return cls(
            expected_member_count=member_count,
            quorum_size=quorum,
            max_simultaneously_unavailable_members=max_unavailable,
            max_automated_recovery_attempts=_require_positive_int(
                max_automated_recovery_attempts,
                "P218_I12_RECOVERY_ATTEMPTS_INVALID",
            ),
            snapshot_retention_count=_require_positive_int(
                snapshot_retention_count,
                "P218_I12_SNAPSHOT_RETENTION_INVALID",
            ),
            snapshot_rehearsal_interval_seconds=_require_positive_int(
                snapshot_rehearsal_interval_seconds,
                "P218_I12_REHEARSAL_INTERVAL_INVALID",
            ),
            credential_overlap_seconds=_require_nonnegative_int(
                credential_overlap_seconds,
                "P218_I12_CREDENTIAL_OVERLAP_INVALID",
            ),
        )

    def record(self) -> dict[str, Any]:
        body = {
            "schema": MAINTENANCE_POLICY_SCHEMA,
            "maintenance_version": PASS218_AUTHORITY_MAINTENANCE_VERSION,
            "expected_member_count": self.expected_member_count,
            "quorum_size": self.quorum_size,
            "max_simultaneously_unavailable_members": self.max_simultaneously_unavailable_members,
            "max_automated_recovery_attempts": self.max_automated_recovery_attempts,
            "snapshot_retention_count": self.snapshot_retention_count,
            "snapshot_rehearsal_interval_seconds": self.snapshot_rehearsal_interval_seconds,
            "credential_overlap_seconds": self.credential_overlap_seconds,
            "rolling_member_changes_only": True,
            "client_writer_identity_hot_swap_permitted": False,
            "fresh_global_fence_after_authority_loss_required": True,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "verbatim_source_retained": False,
            "pass165_source_retaining_path_invoked": False,
            "authoritative_float_weights": False,
        }
        return _seal(MAINTENANCE_POLICY_SCHEMA, body)


def validate_maintenance_policy(record: Mapping[str, Any]) -> dict[str, Any]:
    value = _validate_seal(MAINTENANCE_POLICY_SCHEMA, record)
    if value.get("schema") != MAINTENANCE_POLICY_SCHEMA:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_POLICY_SCHEMA_INVALID")
    policy = Pass218MaintenancePolicy.build(
        expected_member_count=value.get("expected_member_count"),
        max_simultaneously_unavailable_members=value.get("max_simultaneously_unavailable_members"),
        max_automated_recovery_attempts=value.get("max_automated_recovery_attempts"),
        snapshot_retention_count=value.get("snapshot_retention_count"),
        snapshot_rehearsal_interval_seconds=value.get("snapshot_rehearsal_interval_seconds"),
        credential_overlap_seconds=value.get("credential_overlap_seconds"),
    )
    if value.get("quorum_size") != policy.quorum_size:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_POLICY_QUORUM_INVALID")
    if value.get("rolling_member_changes_only") is not True:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_ROLLING_ONLY_REQUIRED")
    if value.get("client_writer_identity_hot_swap_permitted") is not False:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_WRITER_HOT_SWAP_FORBIDDEN")
    if value.get("fresh_global_fence_after_authority_loss_required") is not True:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_NEW_FENCE_REQUIRED")
    _assert_exclusions(value)
    return value


def seal_credential_rotation_plan(
    *,
    rotation_id: str,
    old_ca_sha256: str,
    new_ca_sha256: str,
    old_client_cert_sha256: str,
    new_client_cert_sha256: str,
    old_client_key_sha256: str,
    new_client_key_sha256: str,
    preflight_probe_hash72: str,
    current_global_fence: int,
) -> dict[str, Any]:
    old_ca = _require_sha256(old_ca_sha256, "P218_I12_OLD_CA_SHA256_INVALID")
    new_ca = _require_sha256(new_ca_sha256, "P218_I12_NEW_CA_SHA256_INVALID")
    old_cert = _require_sha256(old_client_cert_sha256, "P218_I12_OLD_CERT_SHA256_INVALID")
    new_cert = _require_sha256(new_client_cert_sha256, "P218_I12_NEW_CERT_SHA256_INVALID")
    old_key = _require_sha256(old_client_key_sha256, "P218_I12_OLD_KEY_SHA256_INVALID")
    new_key = _require_sha256(new_client_key_sha256, "P218_I12_NEW_KEY_SHA256_INVALID")
    if old_cert == new_cert or old_key == new_key:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_ROTATION_MUST_CHANGE_CLIENT_IDENTITY")
    body = {
        "schema": CREDENTIAL_ROTATION_PLAN_SCHEMA,
        "maintenance_version": PASS218_AUTHORITY_MAINTENANCE_VERSION,
        "rotation_id": _require_text(rotation_id, "P218_I12_ROTATION_ID_INVALID"),
        "old_ca_sha256": old_ca,
        "new_ca_sha256": new_ca,
        "old_client_cert_sha256": old_cert,
        "new_client_cert_sha256": new_cert,
        "old_client_key_sha256": old_key,
        "new_client_key_sha256": new_key,
        "preflight_probe_hash72": _require_hash72(preflight_probe_hash72, "P218_I12_PREFLIGHT_PROBE_INVALID"),
        "current_global_fence": _require_positive_int(current_global_fence, "P218_I12_GLOBAL_FENCE_INVALID"),
        "new_credentials_must_be_verified_before_handoff": True,
        "ingress_must_be_quiesced_before_writer_handoff": True,
        "old_writer_must_release_before_new_writer_acquires": True,
        "new_writer_requires_strictly_newer_global_fence": True,
        "simultaneous_writer_identities_permitted": False,
        "canonical_learning_commit_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "verbatim_source_retained": False,
        "pass165_source_retaining_path_invoked": False,
        "authoritative_float_weights": False,
    }
    return _seal(CREDENTIAL_ROTATION_PLAN_SCHEMA, body)


def validate_credential_rotation_plan(record: Mapping[str, Any]) -> dict[str, Any]:
    value = _validate_seal(CREDENTIAL_ROTATION_PLAN_SCHEMA, record)
    if value.get("schema") != CREDENTIAL_ROTATION_PLAN_SCHEMA:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_ROTATION_SCHEMA_INVALID")
    for key in (
        "old_ca_sha256", "new_ca_sha256", "old_client_cert_sha256",
        "new_client_cert_sha256", "old_client_key_sha256", "new_client_key_sha256",
    ):
        _require_sha256(value.get(key), "P218_I12_ROTATION_SHA256_INVALID")
    _require_hash72(value.get("preflight_probe_hash72"), "P218_I12_PREFLIGHT_PROBE_INVALID")
    _require_positive_int(value.get("current_global_fence"), "P218_I12_GLOBAL_FENCE_INVALID")
    if value.get("old_client_cert_sha256") == value.get("new_client_cert_sha256"):
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_ROTATION_CERT_UNCHANGED")
    if value.get("old_client_key_sha256") == value.get("new_client_key_sha256"):
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_ROTATION_KEY_UNCHANGED")
    for key in (
        "new_credentials_must_be_verified_before_handoff",
        "ingress_must_be_quiesced_before_writer_handoff",
        "old_writer_must_release_before_new_writer_acquires",
        "new_writer_requires_strictly_newer_global_fence",
    ):
        if value.get(key) is not True:
            raise Pass218AuthorityMaintenanceValidationError("P218_I12_ROTATION_HANDOFF_RULE_INVALID")
    if value.get("simultaneous_writer_identities_permitted") is not False:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_ROTATION_WRITER_AMBIGUITY")
    _assert_exclusions(value)
    return value


def seal_member_replacement_plan(
    *,
    replacement_id: str,
    old_member_id: int,
    replacement_member_name: str,
    replacement_peer_url: str,
    replacement_client_url: str,
    preflight_probe_hash72: str,
    expected_member_count: int,
    quorum_size: int,
) -> dict[str, Any]:
    count = _require_positive_int(expected_member_count, "P218_I12_MEMBER_COUNT_INVALID")
    quorum = _require_positive_int(quorum_size, "P218_I12_QUORUM_INVALID")
    if count < 3 or count % 2 == 0 or quorum != count // 2 + 1:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_REPLACEMENT_CLUSTER_SHAPE_INVALID")
    body = {
        "schema": MEMBER_REPLACEMENT_PLAN_SCHEMA,
        "maintenance_version": PASS218_AUTHORITY_MAINTENANCE_VERSION,
        "replacement_id": _require_text(replacement_id, "P218_I12_REPLACEMENT_ID_INVALID"),
        "old_member_id": _require_positive_int(old_member_id, "P218_I12_OLD_MEMBER_ID_INVALID"),
        "replacement_member_name": _require_text(replacement_member_name, "P218_I12_REPLACEMENT_MEMBER_NAME_INVALID"),
        "replacement_peer_url": _require_text(replacement_peer_url, "P218_I12_REPLACEMENT_PEER_URL_INVALID", maximum=1024),
        "replacement_client_url": _require_text(replacement_client_url, "P218_I12_REPLACEMENT_CLIENT_URL_INVALID", maximum=1024),
        "preflight_probe_hash72": _require_hash72(preflight_probe_hash72, "P218_I12_PREFLIGHT_PROBE_INVALID"),
        "expected_member_count": count,
        "quorum_size": quorum,
        "maximum_members_replaced_concurrently": 1,
        "pre_and_post_linearizable_probe_required": True,
        "replacement_must_preserve_quorum": True,
        "canonical_writer_identity_unchanged_by_member_identity": True,
        "canonical_learning_commit_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "verbatim_source_retained": False,
        "pass165_source_retaining_path_invoked": False,
        "authoritative_float_weights": False,
    }
    return _seal(MEMBER_REPLACEMENT_PLAN_SCHEMA, body)


def validate_member_replacement_plan(record: Mapping[str, Any]) -> dict[str, Any]:
    value = _validate_seal(MEMBER_REPLACEMENT_PLAN_SCHEMA, record)
    if value.get("schema") != MEMBER_REPLACEMENT_PLAN_SCHEMA:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_REPLACEMENT_SCHEMA_INVALID")
    count = _require_positive_int(value.get("expected_member_count"), "P218_I12_MEMBER_COUNT_INVALID")
    quorum = _require_positive_int(value.get("quorum_size"), "P218_I12_QUORUM_INVALID")
    if count < 3 or count % 2 == 0 or quorum != count // 2 + 1:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_REPLACEMENT_CLUSTER_SHAPE_INVALID")
    _require_positive_int(value.get("old_member_id"), "P218_I12_OLD_MEMBER_ID_INVALID")
    _require_hash72(value.get("preflight_probe_hash72"), "P218_I12_PREFLIGHT_PROBE_INVALID")
    if value.get("maximum_members_replaced_concurrently") != 1:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_REPLACEMENT_MUST_BE_SERIAL")
    if value.get("pre_and_post_linearizable_probe_required") is not True or value.get("replacement_must_preserve_quorum") is not True:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_REPLACEMENT_QUORUM_RULE_INVALID")
    if value.get("canonical_writer_identity_unchanged_by_member_identity") is not True:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_MEMBER_ID_NOT_CANONICAL_IDENTITY")
    _assert_exclusions(value)
    return value


def seal_snapshot_retention_receipt(
    *,
    policy: Pass218MaintenancePolicy,
    snapshot_sha256_values: Sequence[str],
    rehearsal_snapshot_sha256: str,
    rehearsal_manifest_hash72: str,
    rehearsal_canonical_root_exact: bool,
    rehearsal_vm81_snapshot_exact: bool,
    rehearsal_consumed_receipt_exact: bool,
    rehearsal_distributed_checkpoint_exact: bool,
    restart_authorization_minted: bool,
    restart_canonical_mutation_invoked: bool,
) -> dict[str, Any]:
    snapshots = tuple(_require_sha256(value, "P218_I12_SNAPSHOT_SHA256_INVALID") for value in snapshot_sha256_values)
    if len(snapshots) < 1 or len(snapshots) > policy.snapshot_retention_count:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_SNAPSHOT_RETENTION_COUNT_VIOLATION")
    rehearsal_sha = _require_sha256(rehearsal_snapshot_sha256, "P218_I12_REHEARSAL_SNAPSHOT_INVALID")
    if rehearsal_sha not in snapshots:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_REHEARSAL_SNAPSHOT_NOT_RETAINED")
    exact = (
        rehearsal_canonical_root_exact
        and rehearsal_vm81_snapshot_exact
        and rehearsal_consumed_receipt_exact
        and rehearsal_distributed_checkpoint_exact
    )
    if not exact or restart_authorization_minted or restart_canonical_mutation_invoked:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_REHEARSAL_EXACT_RECOVERY_REQUIRED")
    body = {
        "schema": SNAPSHOT_RETENTION_RECEIPT_SCHEMA,
        "maintenance_version": PASS218_AUTHORITY_MAINTENANCE_VERSION,
        "policy_hash72": policy.record()["record_hash72"],
        "retained_snapshot_sha256": list(snapshots),
        "retained_snapshot_count": len(snapshots),
        "rehearsal_snapshot_sha256": rehearsal_sha,
        "rehearsal_manifest_hash72": _require_hash72(rehearsal_manifest_hash72, "P218_I12_REHEARSAL_MANIFEST_INVALID"),
        "rehearsal_canonical_root_exact": bool(rehearsal_canonical_root_exact),
        "rehearsal_vm81_snapshot_exact": bool(rehearsal_vm81_snapshot_exact),
        "rehearsal_consumed_receipt_exact": bool(rehearsal_consumed_receipt_exact),
        "rehearsal_distributed_checkpoint_exact": bool(rehearsal_distributed_checkpoint_exact),
        "restart_authorization_minted": bool(restart_authorization_minted),
        "restart_canonical_mutation_invoked": bool(restart_canonical_mutation_invoked),
        "canonical_learning_commit_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "verbatim_source_retained": False,
        "pass165_source_retaining_path_invoked": False,
        "authoritative_float_weights": False,
    }
    return _seal(SNAPSHOT_RETENTION_RECEIPT_SCHEMA, body)


def validate_snapshot_retention_receipt(record: Mapping[str, Any]) -> dict[str, Any]:
    value = _validate_seal(SNAPSHOT_RETENTION_RECEIPT_SCHEMA, record)
    if value.get("schema") != SNAPSHOT_RETENTION_RECEIPT_SCHEMA:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_SNAPSHOT_RECEIPT_SCHEMA_INVALID")
    snapshots = value.get("retained_snapshot_sha256")
    if not isinstance(snapshots, list) or not snapshots:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_SNAPSHOT_LIST_INVALID")
    for item in snapshots:
        _require_sha256(item, "P218_I12_SNAPSHOT_SHA256_INVALID")
    if value.get("retained_snapshot_count") != len(snapshots):
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_SNAPSHOT_COUNT_MISMATCH")
    if value.get("rehearsal_snapshot_sha256") not in snapshots:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_REHEARSAL_SNAPSHOT_NOT_RETAINED")
    for key in (
        "rehearsal_canonical_root_exact",
        "rehearsal_vm81_snapshot_exact",
        "rehearsal_consumed_receipt_exact",
        "rehearsal_distributed_checkpoint_exact",
    ):
        if value.get(key) is not True:
            raise Pass218AuthorityMaintenanceValidationError("P218_I12_REHEARSAL_EXACTNESS_FAILED")
    if value.get("restart_authorization_minted") is not False or value.get("restart_canonical_mutation_invoked") is not False:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_REHEARSAL_MUTATION_FORBIDDEN")
    _assert_exclusions(value)
    return value


def seal_operational_alert_receipt(
    *,
    alert_sequence: int,
    severity: str,
    event_code: str,
    cluster_probe_hash72: str,
    global_fence: int | None,
    writer_authority_held: bool,
    writer_authority_revoked: bool,
    requires_new_global_fence: bool,
) -> dict[str, Any]:
    severity_value = _require_text(severity, "P218_I12_ALERT_SEVERITY_INVALID").upper()
    if severity_value not in ALERT_SEVERITIES:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_ALERT_SEVERITY_INVALID")
    if writer_authority_held and writer_authority_revoked:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_ALERT_WRITER_STATE_CONTRADICTION")
    if writer_authority_revoked and not requires_new_global_fence:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_ALERT_NEW_FENCE_REQUIRED")
    body = {
        "schema": OPERATIONAL_ALERT_RECEIPT_SCHEMA,
        "maintenance_version": PASS218_AUTHORITY_MAINTENANCE_VERSION,
        "alert_sequence": _require_positive_int(alert_sequence, "P218_I12_ALERT_SEQUENCE_INVALID"),
        "severity": severity_value,
        "event_code": _require_text(event_code, "P218_I12_ALERT_EVENT_INVALID"),
        "cluster_probe_hash72": _require_hash72(cluster_probe_hash72, "P218_I12_ALERT_PROBE_INVALID"),
        "global_fence": None if global_fence is None else _require_positive_int(global_fence, "P218_I12_GLOBAL_FENCE_INVALID"),
        "writer_authority_held": bool(writer_authority_held),
        "writer_authority_revoked": bool(writer_authority_revoked),
        "requires_new_global_fence": bool(requires_new_global_fence),
        "diagnostic_only": True,
        "canonical_learning_commit_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "verbatim_source_retained": False,
        "pass165_source_retaining_path_invoked": False,
        "authoritative_float_weights": False,
    }
    return _seal(OPERATIONAL_ALERT_RECEIPT_SCHEMA, body)


def validate_operational_alert_receipt(record: Mapping[str, Any]) -> dict[str, Any]:
    value = _validate_seal(OPERATIONAL_ALERT_RECEIPT_SCHEMA, record)
    if value.get("schema") != OPERATIONAL_ALERT_RECEIPT_SCHEMA or value.get("diagnostic_only") is not True:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_ALERT_SCHEMA_INVALID")
    if value.get("severity") not in ALERT_SEVERITIES:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_ALERT_SEVERITY_INVALID")
    _require_positive_int(value.get("alert_sequence"), "P218_I12_ALERT_SEQUENCE_INVALID")
    _require_hash72(value.get("cluster_probe_hash72"), "P218_I12_ALERT_PROBE_INVALID")
    if value.get("writer_authority_revoked") is True and value.get("requires_new_global_fence") is not True:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_ALERT_NEW_FENCE_REQUIRED")
    _assert_exclusions(value)
    return value


class Pass218BoundedRecoveryController:
    """Bound recovery attempts and prove fresh-fence continuity after failure.

    The controller is operational only.  It can record that a new fence was
    observed; it cannot acquire a lease, mint an authorization, or mutate the
    canonical target.
    """

    def __init__(self, policy: Pass218MaintenancePolicy) -> None:
        self.policy = policy
        self.state = "HEALTHY"
        self.attempt_count = 0
        self.predecessor_global_fence: int | None = None
        self.recovered_global_fence: int | None = None
        self.requires_new_global_fence = False
        self.last_probe_hash72: str | None = None

    def record_authority_loss(self, *, predecessor_global_fence: int, cluster_probe_hash72: str) -> dict[str, Any]:
        self.predecessor_global_fence = _require_positive_int(predecessor_global_fence, "P218_I12_GLOBAL_FENCE_INVALID")
        self.last_probe_hash72 = _require_hash72(cluster_probe_hash72, "P218_I12_RECOVERY_PROBE_INVALID")
        self.recovered_global_fence = None
        self.requires_new_global_fence = True
        self.state = "AUTHORITY_LOST"
        return self.status()

    def begin_attempt(self, *, writer_authority_held: bool) -> dict[str, Any]:
        if not self.requires_new_global_fence:
            raise Pass218AuthorityMaintenanceStateError("P218_I12_RECOVERY_NOT_REQUIRED")
        if writer_authority_held:
            raise Pass218AuthorityMaintenanceStateError("P218_I12_RECOVERY_REQUIRES_RELEASED_WRITER")
        if self.attempt_count >= self.policy.max_automated_recovery_attempts:
            self.state = "MANUAL_INTERVENTION_REQUIRED"
            raise Pass218AuthorityMaintenanceStateError("P218_I12_RECOVERY_ATTEMPT_BUDGET_EXHAUSTED")
        self.attempt_count += 1
        self.state = "RECOVERY_ATTEMPT"
        return self.status()

    def record_failed_attempt(self, *, cluster_probe_hash72: str) -> dict[str, Any]:
        if self.state != "RECOVERY_ATTEMPT":
            raise Pass218AuthorityMaintenanceStateError("P218_I12_RECOVERY_ATTEMPT_NOT_ACTIVE")
        self.last_probe_hash72 = _require_hash72(cluster_probe_hash72, "P218_I12_RECOVERY_PROBE_INVALID")
        self.state = (
            "MANUAL_INTERVENTION_REQUIRED"
            if self.attempt_count >= self.policy.max_automated_recovery_attempts
            else "AUTHORITY_LOST"
        )
        return self.status()

    def record_recovered_fence(self, *, recovered_global_fence: int, cluster_probe_hash72: str) -> dict[str, Any]:
        if self.predecessor_global_fence is None or not self.requires_new_global_fence:
            raise Pass218AuthorityMaintenanceStateError("P218_I12_RECOVERY_NOT_REQUIRED")
        recovered = _require_positive_int(recovered_global_fence, "P218_I12_RECOVERED_FENCE_INVALID")
        if recovered <= self.predecessor_global_fence:
            raise Pass218AuthorityMaintenanceStateError("P218_I12_RECOVERED_FENCE_MUST_ADVANCE")
        self.last_probe_hash72 = _require_hash72(cluster_probe_hash72, "P218_I12_RECOVERY_PROBE_INVALID")
        self.recovered_global_fence = recovered
        self.requires_new_global_fence = False
        self.state = "RECOVERED_WITH_NEW_FENCE"
        return self.status()

    def status(self) -> dict[str, Any]:
        body = {
            "schema": RECOVERY_STATUS_SCHEMA,
            "maintenance_version": PASS218_AUTHORITY_MAINTENANCE_VERSION,
            "state": self.state,
            "attempt_count": self.attempt_count,
            "max_automated_recovery_attempts": self.policy.max_automated_recovery_attempts,
            "predecessor_global_fence": self.predecessor_global_fence,
            "recovered_global_fence": self.recovered_global_fence,
            "requires_new_global_fence": self.requires_new_global_fence,
            "last_probe_hash72": self.last_probe_hash72,
            "recovery_can_mint_authority": False,
            "recovery_can_mutate_canonical_target": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "verbatim_source_retained": False,
            "pass165_source_retaining_path_invoked": False,
            "authoritative_float_weights": False,
        }
        return _seal(RECOVERY_STATUS_SCHEMA, body)


def validate_recovery_status(record: Mapping[str, Any]) -> dict[str, Any]:
    value = _validate_seal(RECOVERY_STATUS_SCHEMA, record)
    if value.get("schema") != RECOVERY_STATUS_SCHEMA:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_RECOVERY_SCHEMA_INVALID")
    attempts = _require_nonnegative_int(value.get("attempt_count"), "P218_I12_RECOVERY_ATTEMPTS_INVALID")
    maximum = _require_positive_int(value.get("max_automated_recovery_attempts"), "P218_I12_RECOVERY_ATTEMPTS_INVALID")
    if attempts > maximum:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_RECOVERY_ATTEMPT_BUDGET_EXCEEDED")
    predecessor = value.get("predecessor_global_fence")
    recovered = value.get("recovered_global_fence")
    if predecessor is not None:
        predecessor = _require_positive_int(predecessor, "P218_I12_GLOBAL_FENCE_INVALID")
    if recovered is not None:
        recovered = _require_positive_int(recovered, "P218_I12_RECOVERED_FENCE_INVALID")
        if predecessor is None or recovered <= predecessor:
            raise Pass218AuthorityMaintenanceValidationError("P218_I12_RECOVERED_FENCE_MUST_ADVANCE")
    if value.get("requires_new_global_fence") is False and value.get("state") == "RECOVERED_WITH_NEW_FENCE" and recovered is None:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_RECOVERY_FENCE_MISSING")
    if value.get("recovery_can_mint_authority") is not False or value.get("recovery_can_mutate_canonical_target") is not False:
        raise Pass218AuthorityMaintenanceValidationError("P218_I12_RECOVERY_AUTHORITY_FORBIDDEN")
    _assert_exclusions(value)
    return value


__all__ = [
    "ALERT_SEVERITIES",
    "CREDENTIAL_ROTATION_PLAN_SCHEMA",
    "MAINTENANCE_KINDS",
    "MAINTENANCE_POLICY_SCHEMA",
    "MEMBER_REPLACEMENT_PLAN_SCHEMA",
    "OPERATIONAL_ALERT_RECEIPT_SCHEMA",
    "PASS218_AUTHORITY_MAINTENANCE_VERSION",
    "RECOVERY_STATUS_SCHEMA",
    "SNAPSHOT_RETENTION_RECEIPT_SCHEMA",
    "Pass218AuthorityMaintenanceError",
    "Pass218AuthorityMaintenanceStateError",
    "Pass218AuthorityMaintenanceValidationError",
    "Pass218BoundedRecoveryController",
    "Pass218MaintenancePolicy",
    "seal_credential_rotation_plan",
    "seal_member_replacement_plan",
    "seal_operational_alert_receipt",
    "seal_snapshot_retention_receipt",
    "validate_credential_rotation_plan",
    "validate_maintenance_policy",
    "validate_member_replacement_plan",
    "validate_operational_alert_receipt",
    "validate_recovery_status",
    "validate_snapshot_retention_receipt",
]

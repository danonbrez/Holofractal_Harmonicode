"""Pass 218 Iteration 14 multi-party maintenance approval membrane.

I14 is downstream of I9-I13.  It reuses the inherited Pass 146 signed-envelope
primitive to prove possession of explicitly registered operator identities, then
enforces threshold approval, separation of duties, expiry, revocation, current
quorum, and exact distributed-fence binding.  Its terminal product is a sealed
release receipt for an external I12 maintenance workflow.  I14 itself performs
no maintenance operation and cannot change canonical state or authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Iterable, Mapping, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass146.engine import HHS146BoundaryEngine

PASS218_MULTI_PARTY_APPROVAL_VERSION = "HHS-P218-MULTI-PARTY-MAINTENANCE-APPROVAL-I14-V1"
APPROVAL_POLICY_SCHEMA = "HHS-P218-I14-APPROVAL-POLICY-V1"
OPERATOR_RECORD_SCHEMA = "HHS-P218-I14-OPERATOR-RECORD-V1"
OPERATOR_STATEMENT_SCHEMA = "HHS-P218-I14-OPERATOR-STATEMENT-V1"
MAINTENANCE_RELEASE_SCHEMA = "HHS-P218-I14-MAINTENANCE-RELEASE-V1"

STATEMENT_DESTINATION = "pass218-i14-maintenance-approval"
STATEMENT_KINDS = frozenset({"PREPARE", "APPROVE", "EXECUTE", "REVOKE"})
OPERATOR_ROLES = frozenset({"PREPARER", "APPROVER", "EXECUTOR"})
MAINTENANCE_ACTIONS = frozenset({
    "PREPARE_CREDENTIAL_ROTATION",
    "PREPARE_MEMBER_REPLACEMENT",
    "REQUEST_SNAPSHOT_REHEARSAL",
})


class Pass218ApprovalError(RuntimeError):
    pass


class Pass218ApprovalValidationError(Pass218ApprovalError):
    pass


class Pass218ApprovalRejected(Pass218ApprovalError):
    pass


def _copy(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, separators=(",", ":")))


def _require_text(value: Any, code: str, *, maximum: int = 256) -> str:
    if not isinstance(value, str):
        raise Pass218ApprovalValidationError(code)
    normalized = value.strip()
    if not normalized or len(normalized) > maximum:
        raise Pass218ApprovalValidationError(code)
    return normalized


def _require_hash72(value: Any, code: str) -> str:
    value = _require_text(value, code, maximum=72)
    if len(value) != 72:
        raise Pass218ApprovalValidationError(code)
    try:
        validate_hash72(value)
    except Exception as exc:
        raise Pass218ApprovalValidationError(code) from exc
    return value


def _require_positive_int(value: Any, code: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise Pass218ApprovalValidationError(code)
    return value


def _require_nonnegative_int(value: Any, code: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise Pass218ApprovalValidationError(code)
    return value


def _seal(schema: str, body: Mapping[str, Any]) -> dict[str, Any]:
    value = dict(body)
    value["record_hash72"] = hash72_digest({"domain": schema}, value)
    return value


def _validate_seal(schema: str, record: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise Pass218ApprovalValidationError("P218_I14_RECORD_INVALID")
    value = dict(record)
    received = _require_hash72(value.pop("record_hash72", None), "P218_I14_RECORD_HASH_INVALID")
    expected = hash72_digest({"domain": schema}, value)
    if received != expected:
        raise Pass218ApprovalValidationError("P218_I14_RECORD_SEAL_MISMATCH")
    value["record_hash72"] = received
    return value


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
            raise Pass218ApprovalValidationError("P218_I14_EXCLUSION_VIOLATION_" + key.upper())


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


@dataclass(frozen=True)
class Pass218ApprovalPolicy:
    required_distinct_approvers: int = 2
    approval_ttl_seconds: int = 1800
    release_ttl_seconds: int = 600

    def __post_init__(self) -> None:
        for value in (self.required_distinct_approvers, self.approval_ttl_seconds, self.release_ttl_seconds):
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise Pass218ApprovalError("P218_I14_POSITIVE_INTEGER_REQUIRED")
        if self.release_ttl_seconds > self.approval_ttl_seconds:
            raise Pass218ApprovalError("P218_I14_RELEASE_TTL_EXCEEDS_APPROVAL_TTL")

    def record(self) -> dict[str, Any]:
        return _seal(APPROVAL_POLICY_SCHEMA, {
            "schema": APPROVAL_POLICY_SCHEMA,
            "version": PASS218_MULTI_PARTY_APPROVAL_VERSION,
            "required_distinct_approvers": self.required_distinct_approvers,
            "approval_ttl_seconds": self.approval_ttl_seconds,
            "release_ttl_seconds": self.release_ttl_seconds,
            "preparer_counts_as_approver": False,
            "executor_counts_as_approver": False,
            "fence_epoch_binding_required": True,
            "quorum_required": True,
            "registered_identity_required": True,
            "pass146_signed_statement_required": True,
            "maintenance_remains_external": True,
            **_exclusions(),
        })


def validate_approval_policy(record: Mapping[str, Any]) -> dict[str, Any]:
    value = _validate_seal(APPROVAL_POLICY_SCHEMA, record)
    if value.get("schema") != APPROVAL_POLICY_SCHEMA:
        raise Pass218ApprovalValidationError("P218_I14_POLICY_SCHEMA_INVALID")
    Pass218ApprovalPolicy(
        required_distinct_approvers=_require_positive_int(value.get("required_distinct_approvers"), "P218_I14_APPROVAL_THRESHOLD_INVALID"),
        approval_ttl_seconds=_require_positive_int(value.get("approval_ttl_seconds"), "P218_I14_APPROVAL_TTL_INVALID"),
        release_ttl_seconds=_require_positive_int(value.get("release_ttl_seconds"), "P218_I14_RELEASE_TTL_INVALID"),
    )
    if value.get("preparer_counts_as_approver") is not False or value.get("executor_counts_as_approver") is not False:
        raise Pass218ApprovalValidationError("P218_I14_SEPARATION_POLICY_INVALID")
    for key in ("fence_epoch_binding_required", "quorum_required", "registered_identity_required", "pass146_signed_statement_required", "maintenance_remains_external"):
        if value.get(key) is not True:
            raise Pass218ApprovalValidationError("P218_I14_POLICY_INVARIANT_" + key.upper())
    _assert_exclusions(value)
    return value


def seal_operator_record(*, operator_id: str, identity_id: str, identity_hash72: str, public_key_b64: str, public_key_fingerprint: str, roles: Sequence[str], enabled: bool = True) -> dict[str, Any]:
    normalized_roles = sorted({_require_text(role, "P218_I14_ROLE_INVALID").upper() for role in roles})
    if not normalized_roles or any(role not in OPERATOR_ROLES for role in normalized_roles):
        raise Pass218ApprovalValidationError("P218_I14_ROLE_INVALID")
    return _seal(OPERATOR_RECORD_SCHEMA, {
        "schema": OPERATOR_RECORD_SCHEMA,
        "version": PASS218_MULTI_PARTY_APPROVAL_VERSION,
        "operator_id": _require_text(operator_id, "P218_I14_OPERATOR_ID_INVALID"),
        "identity_id": _require_text(identity_id, "P218_I14_IDENTITY_ID_INVALID"),
        "identity_hash72": _require_hash72(identity_hash72, "P218_I14_IDENTITY_HASH_INVALID"),
        "public_key_b64": _require_text(public_key_b64, "P218_I14_PUBLIC_KEY_INVALID", maximum=128),
        "public_key_fingerprint": _require_text(public_key_fingerprint, "P218_I14_PUBLIC_KEY_FINGERPRINT_INVALID", maximum=128),
        "roles": normalized_roles,
        "enabled": bool(enabled),
        "source_identity_surface": "HHS-P146",
        "explicit_registration": True,
        **_exclusions(),
    })


def validate_operator_record(record: Mapping[str, Any]) -> dict[str, Any]:
    value = _validate_seal(OPERATOR_RECORD_SCHEMA, record)
    if value.get("schema") != OPERATOR_RECORD_SCHEMA or value.get("source_identity_surface") != "HHS-P146":
        raise Pass218ApprovalValidationError("P218_I14_OPERATOR_RECORD_SCHEMA_INVALID")
    roles = value.get("roles")
    if not isinstance(roles, list) or not roles or any(role not in OPERATOR_ROLES for role in roles):
        raise Pass218ApprovalValidationError("P218_I14_ROLE_INVALID")
    if value.get("explicit_registration") is not True:
        raise Pass218ApprovalValidationError("P218_I14_EXPLICIT_REGISTRATION_REQUIRED")
    _assert_exclusions(value)
    return value


class Pass218OperatorRegistry:
    def __init__(self, records: Iterable[Mapping[str, Any]] = ()) -> None:
        self._records: dict[str, dict[str, Any]] = {}
        for raw in records:
            record = validate_operator_record(raw)
            operator_id = record["operator_id"]
            if operator_id in self._records:
                raise Pass218ApprovalValidationError("P218_I14_DUPLICATE_OPERATOR")
            self._records[operator_id] = record

    def get(self, operator_id: str, *, role: str) -> dict[str, Any]:
        value = self._records.get(_require_text(operator_id, "P218_I14_OPERATOR_ID_INVALID"))
        if value is None or value.get("enabled") is not True:
            raise Pass218ApprovalRejected("P218_I14_OPERATOR_NOT_REGISTERED")
        if role.upper() not in value["roles"]:
            raise Pass218ApprovalRejected("P218_I14_OPERATOR_ROLE_NOT_REGISTERED")
        return _copy(value)

    def records(self) -> list[dict[str, Any]]:
        return [_copy(self._records[key]) for key in sorted(self._records)]


def _validate_envelope_identity(envelope: Mapping[str, Any], registry: Pass218OperatorRegistry, *, role: str) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        verification = HHS146BoundaryEngine._verify_signed_envelope(envelope)
    except Exception as exc:
        raise Pass218ApprovalRejected("P218_I14_PASS146_STATEMENT_INVALID") from exc
    data = envelope.get("data")
    if not isinstance(data, Mapping):
        raise Pass218ApprovalValidationError("P218_I14_STATEMENT_DATA_INVALID")
    operator_id = _require_text(data.get("operator_id"), "P218_I14_OPERATOR_ID_INVALID")
    registered = registry.get(operator_id, role=role)
    authority = envelope.get("authority") or {}
    if authority.get("identity_id") != registered["identity_id"] or authority.get("identity_hash72") != registered["identity_hash72"]:
        raise Pass218ApprovalRejected("P218_I14_IDENTITY_BINDING_MISMATCH")
    if envelope.get("sender_public_key_b64") != registered["public_key_b64"] or envelope.get("sender_public_key_fingerprint") != registered["public_key_fingerprint"]:
        raise Pass218ApprovalRejected("P218_I14_KEY_BINDING_MISMATCH")
    if envelope.get("source_peer") != operator_id or envelope.get("destination_peer") != STATEMENT_DESTINATION:
        raise Pass218ApprovalRejected("P218_I14_STATEMENT_ROUTE_MISMATCH")
    if not all(verification.get(key) is True for key in ("signature_valid", "envelope_hash_valid", "message_hash_valid", "data_hash_valid")):
        raise Pass218ApprovalRejected("P218_I14_PASS146_VERIFICATION_INCOMPLETE")
    return dict(data), registered


def validate_operator_statement(envelope: Mapping[str, Any], *, registry: Pass218OperatorRegistry, expected_kind: str, policy: Pass218ApprovalPolicy, now_epoch_seconds: int) -> dict[str, Any]:
    kind = _require_text(expected_kind, "P218_I14_STATEMENT_KIND_INVALID").upper()
    if kind not in STATEMENT_KINDS:
        raise Pass218ApprovalValidationError("P218_I14_STATEMENT_KIND_INVALID")
    role = {"PREPARE": "PREPARER", "APPROVE": "APPROVER", "EXECUTE": "EXECUTOR", "REVOKE": "APPROVER"}[kind]
    data, registered = _validate_envelope_identity(envelope, registry, role=role)
    if data.get("schema") != OPERATOR_STATEMENT_SCHEMA or data.get("kind") != kind:
        raise Pass218ApprovalRejected("P218_I14_STATEMENT_SCHEMA_MISMATCH")
    action = _require_text(data.get("action"), "P218_I14_ACTION_INVALID").upper()
    if action not in MAINTENANCE_ACTIONS:
        raise Pass218ApprovalRejected("P218_I14_ACTION_NOT_MAINTENANCE")
    approved = _require_nonnegative_int(data.get("statement_epoch_seconds"), "P218_I14_STATEMENT_EPOCH_INVALID")
    expires = _require_nonnegative_int(data.get("expires_epoch_seconds"), "P218_I14_STATEMENT_EXPIRY_INVALID")
    now = _require_nonnegative_int(now_epoch_seconds, "P218_I14_NOW_INVALID")
    if expires <= approved or expires <= now or approved > now:
        raise Pass218ApprovalRejected("P218_I14_STATEMENT_EXPIRED_OR_NOT_YET_VALID")
    if expires - approved > policy.approval_ttl_seconds:
        raise Pass218ApprovalRejected("P218_I14_STATEMENT_TTL_EXCEEDED")
    _require_hash72(data.get("action_record_hash72"), "P218_I14_ACTION_HASH_INVALID")
    _require_positive_int(data.get("distributed_fence_epoch"), "P218_I14_FENCE_INVALID")
    _require_text(data.get("prepared_by_operator_id"), "P218_I14_PREPARER_ID_INVALID")
    _require_text(data.get("nonce"), "P218_I14_NONCE_INVALID")
    if kind == "REVOKE":
        _require_hash72(data.get("revoked_message_hash72"), "P218_I14_REVOKED_MESSAGE_HASH_INVALID")
    return {
        "data": _copy(data),
        "operator": registered,
        "message_hash72": _require_hash72(envelope.get("message_hash72"), "P218_I14_MESSAGE_HASH_INVALID"),
    }


def evaluate_maintenance_release(*, action_record: Mapping[str, Any], current_status: Mapping[str, Any], preparer_statement: Mapping[str, Any], approval_statements: Sequence[Mapping[str, Any]], executor_statement: Mapping[str, Any], revocation_statements: Sequence[Mapping[str, Any]], registry: Pass218OperatorRegistry, policy: Pass218ApprovalPolicy, now_epoch_seconds: int) -> dict[str, Any]:
    now = _require_nonnegative_int(now_epoch_seconds, "P218_I14_NOW_INVALID")
    action_hash = _require_hash72(action_record.get("record_hash72"), "P218_I14_ACTION_HASH_INVALID")
    action = _require_text(action_record.get("action"), "P218_I14_ACTION_INVALID").upper()
    preparer_id = _require_text(action_record.get("operator_id"), "P218_I14_PREPARER_ID_INVALID")
    if action not in MAINTENANCE_ACTIONS or action_record.get("requires_external_executor") is not True or action_record.get("prepared_not_executed") is not True:
        raise Pass218ApprovalRejected("P218_I14_ACTION_NOT_RELEASABLE")
    if current_status.get("health") == "BLOCKED" or current_status.get("cluster_quorum_ready") is not True or current_status.get("distributed_authority_held") is not True:
        raise Pass218ApprovalRejected("P218_I14_CURRENT_RUNTIME_NOT_READY")
    fence = _require_positive_int(current_status.get("distributed_fence_epoch"), "P218_I14_FENCE_INVALID")

    prepared = validate_operator_statement(preparer_statement, registry=registry, expected_kind="PREPARE", policy=policy, now_epoch_seconds=now)
    pdata = prepared["data"]
    if pdata["operator_id"] != preparer_id or pdata["prepared_by_operator_id"] != preparer_id:
        raise Pass218ApprovalRejected("P218_I14_PREPARER_STATEMENT_MISMATCH")
    if pdata["action_record_hash72"] != action_hash or pdata["action"] != action or pdata["distributed_fence_epoch"] != fence:
        raise Pass218ApprovalRejected("P218_I14_PREPARER_BINDING_MISMATCH")

    revoked: set[str] = set()
    for raw in revocation_statements:
        item = validate_operator_statement(raw, registry=registry, expected_kind="REVOKE", policy=policy, now_epoch_seconds=now)
        revoked.add(item["data"]["revoked_message_hash72"])

    valid: list[dict[str, Any]] = []
    approvers: set[str] = set()
    for raw in approval_statements:
        item = validate_operator_statement(raw, registry=registry, expected_kind="APPROVE", policy=policy, now_epoch_seconds=now)
        data = item["data"]
        operator_id = data["operator_id"]
        if item["message_hash72"] in revoked:
            continue
        if operator_id == preparer_id or operator_id in approvers:
            continue
        if data["prepared_by_operator_id"] != preparer_id or data["action_record_hash72"] != action_hash or data["action"] != action or data["distributed_fence_epoch"] != fence:
            continue
        approvers.add(operator_id)
        valid.append(item)
    if len(valid) < policy.required_distinct_approvers:
        raise Pass218ApprovalRejected("P218_I14_APPROVAL_QUORUM_NOT_MET")
    valid = sorted(valid, key=lambda item: (item["data"]["operator_id"], item["message_hash72"]))[: policy.required_distinct_approvers]
    counted_approvers = {item["data"]["operator_id"] for item in valid}

    executor = validate_operator_statement(executor_statement, registry=registry, expected_kind="EXECUTE", policy=policy, now_epoch_seconds=now)
    edata = executor["data"]
    executor_id = edata["operator_id"]
    if executor_id == preparer_id or executor_id in counted_approvers:
        raise Pass218ApprovalRejected("P218_I14_EXECUTOR_SEPARATION_VIOLATION")
    if edata["prepared_by_operator_id"] != preparer_id or edata["action_record_hash72"] != action_hash or edata["action"] != action or edata["distributed_fence_epoch"] != fence:
        raise Pass218ApprovalRejected("P218_I14_EXECUTOR_BINDING_MISMATCH")

    release_expires = min(
        now + policy.release_ttl_seconds,
        pdata["expires_epoch_seconds"],
        edata["expires_epoch_seconds"],
        *(item["data"]["expires_epoch_seconds"] for item in valid),
    )
    if release_expires <= now:
        raise Pass218ApprovalRejected("P218_I14_RELEASE_ALREADY_EXPIRED")
    return _seal(MAINTENANCE_RELEASE_SCHEMA, {
        "schema": MAINTENANCE_RELEASE_SCHEMA,
        "version": PASS218_MULTI_PARTY_APPROVAL_VERSION,
        "policy_hash72": policy.record()["record_hash72"],
        "action_record_hash72": action_hash,
        "action": action,
        "prepared_by_operator_id": preparer_id,
        "preparer_message_hash72": prepared["message_hash72"],
        "approver_operator_ids": sorted(counted_approvers),
        "approval_message_hash72s": sorted(item["message_hash72"] for item in valid),
        "executor_operator_id": executor_id,
        "executor_message_hash72": executor["message_hash72"],
        "required_distinct_approvers": policy.required_distinct_approvers,
        "valid_distinct_approvers": len(valid),
        "distributed_fence_epoch": fence,
        "current_status_hash72": _require_hash72(current_status.get("record_hash72"), "P218_I14_STATUS_HASH_INVALID"),
        "released_epoch_seconds": now,
        "expires_epoch_seconds": release_expires,
        "approval_quorum_satisfied": True,
        "separation_of_duties_satisfied": True,
        "pass146_statement_integrity_satisfied": True,
        "current_quorum_satisfied": True,
        "current_writer_fence_satisfied": True,
        "external_maintenance_preconditions_satisfied": True,
        "maintenance_remains_external": True,
        **_exclusions(),
    })


def validate_maintenance_release(record: Mapping[str, Any], *, now_epoch_seconds: int | None = None) -> dict[str, Any]:
    value = _validate_seal(MAINTENANCE_RELEASE_SCHEMA, record)
    if value.get("schema") != MAINTENANCE_RELEASE_SCHEMA:
        raise Pass218ApprovalValidationError("P218_I14_RELEASE_SCHEMA_INVALID")
    for key in (
        "approval_quorum_satisfied",
        "separation_of_duties_satisfied",
        "pass146_statement_integrity_satisfied",
        "current_quorum_satisfied",
        "current_writer_fence_satisfied",
        "external_maintenance_preconditions_satisfied",
        "maintenance_remains_external",
    ):
        if value.get(key) is not True:
            raise Pass218ApprovalValidationError("P218_I14_RELEASE_INVARIANT_" + key.upper())
    approvers = value.get("approver_operator_ids")
    hashes = value.get("approval_message_hash72s")
    if not isinstance(approvers, list) or not isinstance(hashes, list) or len(approvers) != len(hashes) or len(set(approvers)) != len(approvers):
        raise Pass218ApprovalValidationError("P218_I14_RELEASE_APPROVER_SET_INVALID")
    required = _require_positive_int(value.get("required_distinct_approvers"), "P218_I14_APPROVAL_THRESHOLD_INVALID")
    if len(approvers) < required or value.get("valid_distinct_approvers") != len(approvers):
        raise Pass218ApprovalValidationError("P218_I14_RELEASE_APPROVAL_QUORUM_INVALID")
    if value.get("prepared_by_operator_id") in approvers or value.get("executor_operator_id") in approvers or value.get("executor_operator_id") == value.get("prepared_by_operator_id"):
        raise Pass218ApprovalValidationError("P218_I14_RELEASE_SEPARATION_INVALID")
    if now_epoch_seconds is not None and _require_nonnegative_int(now_epoch_seconds, "P218_I14_NOW_INVALID") >= value.get("expires_epoch_seconds", 0):
        raise Pass218ApprovalRejected("P218_I14_RELEASE_EXPIRED")
    _assert_exclusions(value)
    return value


__all__ = [
    "APPROVAL_POLICY_SCHEMA",
    "MAINTENANCE_ACTIONS",
    "MAINTENANCE_RELEASE_SCHEMA",
    "OPERATOR_RECORD_SCHEMA",
    "OPERATOR_ROLES",
    "OPERATOR_STATEMENT_SCHEMA",
    "PASS218_MULTI_PARTY_APPROVAL_VERSION",
    "STATEMENT_DESTINATION",
    "STATEMENT_KINDS",
    "Pass218ApprovalError",
    "Pass218ApprovalPolicy",
    "Pass218ApprovalRejected",
    "Pass218ApprovalValidationError",
    "Pass218OperatorRegistry",
    "evaluate_maintenance_release",
    "seal_operator_record",
    "validate_approval_policy",
    "validate_maintenance_release",
    "validate_operator_record",
    "validate_operator_statement",
]

"""Pass 218 Iteration 19 distributed postcondition verification.

I19 is downstream of the frozen I18 terminal closure. It never executes
maintenance and never reopens a consumed release. Successful maintenance is
execution-terminal at I18 but effect-verified only after an action-specific
postcondition observation is sealed against the immutable I17 result and I18
closure under the current distributed owner/fence.

Failed and aborted attempts remain terminal without effect verification.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Protocol

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.commit_boundary import _canonical_bytes
from hhs_runtime.pass218.authority_maintenance_i12 import (
    CREDENTIAL_ROTATION_PLAN_SCHEMA,
    MEMBER_REPLACEMENT_PLAN_SCHEMA,
    SNAPSHOT_RETENTION_RECEIPT_SCHEMA,
)
from hhs_runtime.pass218.distributed_closure_i18 import (
    Pass218DistributedClosureLedgerProtocol,
    validate_distributed_terminal_closure,
)
from hhs_runtime.pass218.distributed_execution_i17 import (
    Pass218DistributedExecutionLedgerProtocol,
    validate_external_result,
)
from hhs_runtime.pass218.distributed_ownership import (
    Pass218DistributedOwnershipError,
    Pass218InMemoryDistributedAuthority,
    validate_distributed_ownership_record,
)
from hhs_runtime.pass218.execution_i15 import validate_i12_maintenance_record

PASS218_POSTCONDITION_VERSION = "HHS-P218-DISTRIBUTED-POSTCONDITION-I19-V1"
POSTCONDITION_OBSERVATION_SCHEMA = "HHS-P218-I19-POSTCONDITION-OBSERVATION-V1"
POSTCONDITION_VERIFICATION_SCHEMA = "HHS-P218-I19-DISTRIBUTED-POSTCONDITION-VERIFICATION-V1"
POSTCONDITION_STATUS_SCHEMA = "HHS-P218-I19-DISTRIBUTED-POSTCONDITION-STATUS-V1"
DEFAULT_POSTCONDITION_SUFFIX = "postcondition-i19"

CREDENTIAL_ACTION = "PREPARE_CREDENTIAL_ROTATION"
MEMBER_ACTION = "PREPARE_MEMBER_REPLACEMENT"
SNAPSHOT_ACTION = "REQUEST_SNAPSHOT_REHEARSAL"


class Pass218PostconditionError(RuntimeError):
    pass


class Pass218PostconditionValidationError(Pass218PostconditionError):
    pass


class Pass218PostconditionReplayRejected(Pass218PostconditionError):
    pass


class Pass218PostconditionUnavailable(Pass218PostconditionError):
    pass


def _copy(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, separators=(",", ":")))


def _require_text(value: Any, code: str, *, maximum: int = 1024) -> str:
    if not isinstance(value, str):
        raise Pass218PostconditionValidationError(code)
    value = value.strip()
    if not value or len(value) > maximum:
        raise Pass218PostconditionValidationError(code)
    return value


def _require_hash72(value: Any, code: str) -> str:
    value = _require_text(value, code, maximum=72)
    if len(value) != 72:
        raise Pass218PostconditionValidationError(code)
    try:
        validate_hash72(value)
    except Exception as exc:
        raise Pass218PostconditionValidationError(code) from exc
    return value


def _require_sha256(value: Any, code: str) -> str:
    value = _require_text(value, code, maximum=64)
    if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise Pass218PostconditionValidationError(code)
    return value


def _require_positive_int(value: Any, code: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise Pass218PostconditionValidationError(code)
    return value


def _marker(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _exclusions() -> dict[str, bool]:
    return {
        "canonical_authority_minted": False,
        "canonical_mutation_permitted": False,
        "canonical_learning_commit_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "execution_authority_minted": False,
        "retry_authority_minted": False,
        "redispatch_permitted": False,
        "verbatim_source_retained": False,
        "pass165_source_retaining_path_invoked": False,
        "authoritative_float_weights": False,
    }


def _assert_exclusions(record: Mapping[str, Any]) -> None:
    for key, expected in _exclusions().items():
        if record.get(key) is not expected:
            raise Pass218PostconditionValidationError("P218_I19_EXCLUSION_VIOLATION_" + key.upper())


def _seal(schema: str, body: Mapping[str, Any]) -> dict[str, Any]:
    value = dict(body)
    value["record_hash72"] = hash72_digest({"domain": schema}, value)
    return value


def _action_details(action: str, i12: Mapping[str, Any], observed: Mapping[str, Any]) -> dict[str, Any]:
    if action == CREDENTIAL_ACTION:
        if i12.get("schema") != CREDENTIAL_ROTATION_PLAN_SCHEMA:
            raise Pass218PostconditionValidationError("P218_I19_CREDENTIAL_SCHEMA_INVALID")
        details: dict[str, Any] = {}
        for field, expected in (
            ("active_ca_sha256", i12["new_ca_sha256"]),
            ("active_client_cert_sha256", i12["new_client_cert_sha256"]),
            ("active_client_key_sha256", i12["new_client_key_sha256"]),
        ):
            actual = _require_sha256(observed.get(field), "P218_I19_CREDENTIAL_HASH_INVALID")
            if actual != expected:
                raise Pass218PostconditionValidationError("P218_I19_CREDENTIAL_POSTCONDITION_MISMATCH")
            details[field] = actual
        new_fence = _require_positive_int(observed.get("new_writer_fence_epoch"), "P218_I19_CREDENTIAL_FENCE_INVALID")
        if new_fence <= int(i12["current_global_fence"]):
            raise Pass218PostconditionValidationError("P218_I19_CREDENTIAL_NEWER_FENCE_REQUIRED")
        if observed.get("new_credentials_verified") is not True or observed.get("old_writer_released") is not True:
            raise Pass218PostconditionValidationError("P218_I19_CREDENTIAL_HANDOFF_NOT_VERIFIED")
        if observed.get("simultaneous_writer_identities_observed") is not False:
            raise Pass218PostconditionValidationError("P218_I19_CREDENTIAL_WRITER_AMBIGUITY")
        details.update({
            "new_writer_fence_epoch": new_fence,
            "new_credentials_verified": True,
            "old_writer_released": True,
            "simultaneous_writer_identities_observed": False,
            "post_linearizable_probe_hash72": _require_hash72(observed.get("post_linearizable_probe_hash72"), "P218_I19_POST_PROBE_INVALID"),
        })
        return details

    if action == MEMBER_ACTION:
        if i12.get("schema") != MEMBER_REPLACEMENT_PLAN_SCHEMA:
            raise Pass218PostconditionValidationError("P218_I19_MEMBER_SCHEMA_INVALID")
        details = {}
        for field in ("replacement_member_name", "replacement_peer_url", "replacement_client_url"):
            actual = _require_text(observed.get(field), "P218_I19_MEMBER_IDENTITY_INVALID", maximum=1024)
            if actual != i12[field]:
                raise Pass218PostconditionValidationError("P218_I19_MEMBER_POSTCONDITION_MISMATCH")
            details[field] = actual
        member_count = _require_positive_int(observed.get("observed_member_count"), "P218_I19_MEMBER_COUNT_INVALID")
        quorum = _require_positive_int(observed.get("observed_quorum_size"), "P218_I19_QUORUM_INVALID")
        if member_count != i12["expected_member_count"] or quorum != i12["quorum_size"]:
            raise Pass218PostconditionValidationError("P218_I19_MEMBER_CLUSTER_SHAPE_MISMATCH")
        for key in ("old_member_absent", "replacement_present", "quorum_preserved"):
            if observed.get(key) is not True:
                raise Pass218PostconditionValidationError("P218_I19_MEMBER_POSTCONDITION_NOT_VERIFIED")
        details.update({
            "observed_member_count": member_count,
            "observed_quorum_size": quorum,
            "old_member_absent": True,
            "replacement_present": True,
            "quorum_preserved": True,
            "post_linearizable_probe_hash72": _require_hash72(observed.get("post_linearizable_probe_hash72"), "P218_I19_POST_PROBE_INVALID"),
        })
        return details

    if action == SNAPSHOT_ACTION:
        if i12.get("schema") != SNAPSHOT_RETENTION_RECEIPT_SCHEMA:
            raise Pass218PostconditionValidationError("P218_I19_SNAPSHOT_SCHEMA_INVALID")
        if observed.get("rehearsal_receipt_hash72") != i12["record_hash72"]:
            raise Pass218PostconditionValidationError("P218_I19_SNAPSHOT_RECEIPT_MISMATCH")
        if observed.get("rehearsal_manifest_hash72") != i12["rehearsal_manifest_hash72"]:
            raise Pass218PostconditionValidationError("P218_I19_SNAPSHOT_MANIFEST_MISMATCH")
        for key in (
            "rehearsal_canonical_root_exact",
            "rehearsal_vm81_snapshot_exact",
            "rehearsal_consumed_receipt_exact",
            "rehearsal_distributed_checkpoint_exact",
            "restore_target_non_authoritative",
        ):
            if observed.get(key) is not True:
                raise Pass218PostconditionValidationError("P218_I19_SNAPSHOT_POSTCONDITION_NOT_VERIFIED")
        return {
            "rehearsal_receipt_hash72": i12["record_hash72"],
            "rehearsal_manifest_hash72": i12["rehearsal_manifest_hash72"],
            "rehearsal_canonical_root_exact": True,
            "rehearsal_vm81_snapshot_exact": True,
            "rehearsal_consumed_receipt_exact": True,
            "rehearsal_distributed_checkpoint_exact": True,
            "restore_target_non_authoritative": True,
        }

    raise Pass218PostconditionValidationError("P218_I19_ACTION_NOT_MAINTENANCE")


def seal_postcondition_observation(*, action: str, i12_maintenance_record: Mapping[str, Any], observation: Mapping[str, Any], observed_epoch_ns: int) -> dict[str, Any]:
    action_value = _require_text(action, "P218_I19_ACTION_INVALID", maximum=256).upper()
    i12 = validate_i12_maintenance_record(action_value, i12_maintenance_record)
    if not isinstance(observation, Mapping):
        raise Pass218PostconditionValidationError("P218_I19_OBSERVATION_INVALID")
    details = _action_details(action_value, i12, observation)
    return _seal(POSTCONDITION_OBSERVATION_SCHEMA, {
        "schema": POSTCONDITION_OBSERVATION_SCHEMA,
        "version": PASS218_POSTCONDITION_VERSION,
        "action": action_value,
        "i12_maintenance_schema": i12["schema"],
        "i12_maintenance_record_hash72": i12["record_hash72"],
        "i12_maintenance_record": _copy(i12),
        "observed_epoch_ns": _require_positive_int(observed_epoch_ns, "P218_I19_OBSERVED_EPOCH_INVALID"),
        **details,
        "postcondition_verified": True,
        "diagnostic_only": True,
        **_exclusions(),
    })


def validate_postcondition_observation(record: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise Pass218PostconditionValidationError("P218_I19_OBSERVATION_INVALID")
    value = _copy(record)
    supplied = _require_hash72(value.pop("record_hash72", None), "P218_I19_OBSERVATION_HASH_INVALID")
    if value.get("schema") != POSTCONDITION_OBSERVATION_SCHEMA or value.get("version") != PASS218_POSTCONDITION_VERSION:
        raise Pass218PostconditionValidationError("P218_I19_OBSERVATION_SCHEMA_INVALID")
    action = _require_text(value.get("action"), "P218_I19_ACTION_INVALID", maximum=256).upper()
    i12_record = value.get("i12_maintenance_record")
    if not isinstance(i12_record, Mapping):
        raise Pass218PostconditionValidationError("P218_I19_I12_RECORD_REQUIRED")
    i12 = validate_i12_maintenance_record(action, i12_record)
    if i12["record_hash72"] != value.get("i12_maintenance_record_hash72") or i12["schema"] != value.get("i12_maintenance_schema"):
        raise Pass218PostconditionValidationError("P218_I19_I12_BINDING_MISMATCH")
    _require_positive_int(value.get("observed_epoch_ns"), "P218_I19_OBSERVED_EPOCH_INVALID")
    expected_details = _action_details(action, i12, value)
    for key, expected in expected_details.items():
        if value.get(key) != expected:
            raise Pass218PostconditionValidationError("P218_I19_OBSERVATION_DETAIL_MISMATCH")
    if value.get("postcondition_verified") is not True or value.get("diagnostic_only") is not True:
        raise Pass218PostconditionValidationError("P218_I19_OBSERVATION_INVARIANT_INVALID")
    _assert_exclusions(value)
    if supplied != hash72_digest({"domain": POSTCONDITION_OBSERVATION_SCHEMA}, value):
        raise Pass218PostconditionValidationError("P218_I19_OBSERVATION_HASH_MISMATCH")
    return {**value, "record_hash72": supplied}


def seal_distributed_postcondition_verification(*, closure: Mapping[str, Any], result: Mapping[str, Any], observation: Mapping[str, Any], ownership: Mapping[str, Any]) -> dict[str, Any]:
    closure_value = validate_distributed_terminal_closure(closure)
    result_value = validate_external_result(result)
    observation_value = validate_postcondition_observation(observation)
    owner = validate_distributed_ownership_record(ownership)
    if closure_value["outcome"] != "SUCCEEDED" or result_value["outcome"] != "SUCCEEDED":
        raise Pass218PostconditionValidationError("P218_I19_ONLY_SUCCESSFUL_CLOSURE_REQUIRES_VERIFICATION")
    if result_value["record_hash72"] != closure_value["i17_result_record_hash72"] or result_value["claim_record_hash72"] != closure_value["claim_record_hash72"]:
        raise Pass218PostconditionValidationError("P218_I19_RESULT_CLOSURE_MISMATCH")
    if result_value["action"] != observation_value["action"]:
        raise Pass218PostconditionValidationError("P218_I19_ACTION_OBSERVATION_MISMATCH")
    if result_value.get("i12_maintenance_record_hash72") != observation_value["i12_maintenance_record_hash72"]:
        raise Pass218PostconditionValidationError("P218_I19_I12_OBSERVATION_MISMATCH")
    if observation_value["observed_epoch_ns"] < result_value["completed_epoch_ns"]:
        raise Pass218PostconditionValidationError("P218_I19_OBSERVATION_BEFORE_RESULT")
    if owner["fence_epoch"] < closure_value["closure_fence_epoch"]:
        raise Pass218PostconditionValidationError("P218_I19_VERIFICATION_FENCE_REGRESSION")
    return _seal(POSTCONDITION_VERIFICATION_SCHEMA, {
        "schema": POSTCONDITION_VERIFICATION_SCHEMA,
        "version": PASS218_POSTCONDITION_VERSION,
        "claim_record_hash72": closure_value["claim_record_hash72"],
        "release_record_hash72": closure_value["release_record_hash72"],
        "action_record_hash72": closure_value["action_record_hash72"],
        "action": result_value["action"],
        "i17_result_record_hash72": result_value["record_hash72"],
        "i18_terminal_closure_hash72": closure_value["record_hash72"],
        "postcondition_observation_hash72": observation_value["record_hash72"],
        "i12_maintenance_record_hash72": observation_value["i12_maintenance_record_hash72"],
        "verification_fence_epoch": owner["fence_epoch"],
        "verification_owner_id": owner["owner_id"],
        "verification_host_id": owner["host_id"],
        "verification_ownership_hash72": owner["ownership_hash72"],
        "observed_epoch_ns": observation_value["observed_epoch_ns"],
        "postcondition_observation": _copy(observation_value),
        "execution_terminal_before_effect_verification": True,
        "successful_effect_verified": True,
        "verification_single_write": True,
        "successor_may_read_verification": True,
        "successor_may_redispatch": False,
        "retry_requires_new_prepared_action": True,
        **_exclusions(),
    })


def validate_distributed_postcondition_verification(record: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise Pass218PostconditionValidationError("P218_I19_VERIFICATION_INVALID")
    value = _copy(record)
    supplied = _require_hash72(value.pop("record_hash72", None), "P218_I19_VERIFICATION_HASH_INVALID")
    if value.get("schema") != POSTCONDITION_VERIFICATION_SCHEMA or value.get("version") != PASS218_POSTCONDITION_VERSION:
        raise Pass218PostconditionValidationError("P218_I19_VERIFICATION_SCHEMA_INVALID")
    for key in (
        "claim_record_hash72", "release_record_hash72", "action_record_hash72",
        "i17_result_record_hash72", "i18_terminal_closure_hash72",
        "postcondition_observation_hash72", "i12_maintenance_record_hash72",
        "verification_ownership_hash72",
    ):
        _require_hash72(value.get(key), "P218_I19_VERIFICATION_BINDING_HASH_INVALID")
    _require_positive_int(value.get("verification_fence_epoch"), "P218_I19_VERIFICATION_FENCE_INVALID")
    observation = validate_postcondition_observation(value.get("postcondition_observation") or {})
    if observation["record_hash72"] != value["postcondition_observation_hash72"] or observation["action"] != value.get("action") or observation["i12_maintenance_record_hash72"] != value["i12_maintenance_record_hash72"]:
        raise Pass218PostconditionValidationError("P218_I19_VERIFICATION_OBSERVATION_BINDING_MISMATCH")
    for key in (
        "execution_terminal_before_effect_verification", "successful_effect_verified",
        "verification_single_write", "successor_may_read_verification",
        "retry_requires_new_prepared_action",
    ):
        if value.get(key) is not True:
            raise Pass218PostconditionValidationError("P218_I19_VERIFICATION_INVARIANT_" + key.upper())
    if value.get("successor_may_redispatch") is not False:
        raise Pass218PostconditionValidationError("P218_I19_REDISPATCH_FORBIDDEN")
    _assert_exclusions(value)
    if supplied != hash72_digest({"domain": POSTCONDITION_VERIFICATION_SCHEMA}, value):
        raise Pass218PostconditionValidationError("P218_I19_VERIFICATION_HASH_MISMATCH")
    return {**value, "record_hash72": supplied}


class Pass218PostconditionLedgerProtocol(Protocol):
    distributed: bool
    def current_ownership(self) -> dict[str, Any]: ...
    def record_verification(self, *, closure: Mapping[str, Any], result: Mapping[str, Any], observation: Mapping[str, Any]) -> dict[str, Any]: ...
    def verification_for_claim(self, claim_hash72: str) -> dict[str, Any] | None: ...
    def verifications(self) -> list[dict[str, Any]]: ...
    def status(self) -> dict[str, Any]: ...


class Pass218EtcdPostconditionLedger:
    distributed = True

    def __init__(self, authority: Any, execution_ledger: Pass218DistributedExecutionLedgerProtocol, closure_ledger: Pass218DistributedClosureLedgerProtocol, *, suffix: str = DEFAULT_POSTCONDITION_SUFFIX) -> None:
        if not hasattr(authority, "client") or not hasattr(authority, "namespace"):
            raise Pass218PostconditionValidationError("P218_I19_ETCD_AUTHORITY_REQUIRED")
        self.authority = authority
        self.client = authority.client
        self.execution_ledger = execution_ledger
        self.closure_ledger = closure_ledger
        self.namespace = str(authority.namespace).rstrip("/") + "/" + suffix

    def _key(self, suffix: str) -> bytes:
        return (self.namespace + "/" + suffix).encode("utf-8")

    def verification_key(self, claim_hash72: str) -> bytes:
        return self._key("verifications/" + _marker(_require_hash72(claim_hash72, "P218_I19_CLAIM_HASH_INVALID")))

    def current_ownership(self) -> dict[str, Any]:
        try:
            return validate_distributed_ownership_record(self.authority.assert_current())
        except Pass218DistributedOwnershipError as exc:
            raise Pass218PostconditionUnavailable(str(exc)) from exc

    def verification_for_claim(self, claim_hash72: str) -> dict[str, Any] | None:
        raw, _ = self.client.range_value(self.verification_key(claim_hash72))
        if raw is None:
            return None
        try:
            value = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise Pass218PostconditionValidationError("P218_I19_VERIFICATION_JSON_INVALID") from exc
        if not isinstance(value, Mapping) or _canonical_bytes(value) != raw:
            raise Pass218PostconditionValidationError("P218_I19_VERIFICATION_NONCANONICAL")
        return validate_distributed_postcondition_verification(value)

    def record_verification(self, *, closure: Mapping[str, Any], result: Mapping[str, Any], observation: Mapping[str, Any]) -> dict[str, Any]:
        closure_value = validate_distributed_terminal_closure(closure)
        result_value = validate_external_result(result)
        stored_closure = self.closure_ledger.closure_for_claim(closure_value["claim_record_hash72"])
        if stored_closure is None or stored_closure["record_hash72"] != closure_value["record_hash72"]:
            raise Pass218PostconditionValidationError("P218_I19_DISTRIBUTED_I18_CLOSURE_REQUIRED")
        stored_result = self.execution_ledger.result_for_claim(closure_value["claim_record_hash72"])
        if stored_result is None or stored_result["record_hash72"] != result_value["record_hash72"]:
            raise Pass218PostconditionValidationError("P218_I19_DISTRIBUTED_I17_RESULT_REQUIRED")
        existing = self.verification_for_claim(closure_value["claim_record_hash72"])
        if existing is not None:
            obs = validate_postcondition_observation(observation)
            if existing["postcondition_observation_hash72"] == obs["record_hash72"]:
                return existing
            raise Pass218PostconditionReplayRejected("P218_I19_POSTCONDITION_VERIFICATION_ALREADY_RECORDED")
        ownership = self.current_ownership()
        verification = seal_distributed_postcondition_verification(closure=closure_value, result=result_value, observation=observation, ownership=ownership)
        key = self.verification_key(closure_value["claim_record_hash72"])
        response = self.client.txn(
            compare=[
                self.client.compare_value(self.authority.owner_key, _canonical_bytes(ownership)),
                self.client.compare_value(self.authority.fence_key, str(ownership["fence_epoch"]).encode("ascii")),
                self.client.compare_version(key, 0),
            ],
            success=[self.client.put_operation(key, _canonical_bytes(verification))],
        )
        if response.get("succeeded") is True:
            return _copy(verification)
        existing = self.verification_for_claim(closure_value["claim_record_hash72"])
        if existing is not None:
            if existing["postcondition_observation_hash72"] == verification["postcondition_observation_hash72"]:
                return existing
            raise Pass218PostconditionReplayRejected("P218_I19_POSTCONDITION_VERIFICATION_ALREADY_RECORDED")
        self.current_ownership()
        raise Pass218PostconditionUnavailable("P218_I19_VERIFICATION_CAS_CONFLICT")

    def verifications(self) -> list[dict[str, Any]]:
        values: list[dict[str, Any]] = []
        for closure in self.closure_ledger.closures():
            item = self.verification_for_claim(closure["claim_record_hash72"])
            if item is not None:
                values.append(item)
        return values

    def status(self) -> dict[str, Any]:
        closures = self.closure_ledger.closures()
        successful = [item for item in closures if item["outcome"] == "SUCCEEDED"]
        verified = self.verifications()
        return {
            "schema": POSTCONDITION_STATUS_SCHEMA,
            "version": PASS218_POSTCONDITION_VERSION,
            "distributed": True,
            "successful_terminal_closure_count": len(successful),
            "distributed_postcondition_verification_count": len(verified),
            "successful_closure_pending_verification_count": max(0, len(successful) - len(verified)),
            "failed_or_aborted_closure_count": len(closures) - len(successful),
            "failed_or_aborted_require_postcondition_verification": False,
            "successful_effect_verification_required": True,
            "postcondition_verification_grants_execution_authority": False,
            **_exclusions(),
        }


class Pass218InMemoryPostconditionLedger:
    distributed = True

    def __init__(self, authority: Pass218InMemoryDistributedAuthority, execution_ledger: Pass218DistributedExecutionLedgerProtocol, closure_ledger: Pass218DistributedClosureLedgerProtocol) -> None:
        self.authority = authority
        self.harness = authority.harness
        self.execution_ledger = execution_ledger
        self.closure_ledger = closure_ledger

    def _state(self) -> dict[str, Any]:
        state = getattr(self.harness, "_pass218_i19_postcondition_state", None)
        if state is None:
            state = {"verifications": {}}
            setattr(self.harness, "_pass218_i19_postcondition_state", state)
        return state

    def current_ownership(self) -> dict[str, Any]:
        try:
            return validate_distributed_ownership_record(self.authority.assert_current())
        except Pass218DistributedOwnershipError as exc:
            raise Pass218PostconditionUnavailable(str(exc)) from exc

    def verification_for_claim(self, claim_hash72: str) -> dict[str, Any] | None:
        _require_hash72(claim_hash72, "P218_I19_CLAIM_HASH_INVALID")
        with self.harness._lock:
            value = self._state()["verifications"].get(claim_hash72)
            return None if value is None else validate_distributed_postcondition_verification(value)

    def record_verification(self, *, closure: Mapping[str, Any], result: Mapping[str, Any], observation: Mapping[str, Any]) -> dict[str, Any]:
        closure_value = validate_distributed_terminal_closure(closure)
        result_value = validate_external_result(result)
        stored_closure = self.closure_ledger.closure_for_claim(closure_value["claim_record_hash72"])
        if stored_closure is None or stored_closure["record_hash72"] != closure_value["record_hash72"]:
            raise Pass218PostconditionValidationError("P218_I19_DISTRIBUTED_I18_CLOSURE_REQUIRED")
        stored_result = self.execution_ledger.result_for_claim(closure_value["claim_record_hash72"])
        if stored_result is None or stored_result["record_hash72"] != result_value["record_hash72"]:
            raise Pass218PostconditionValidationError("P218_I19_DISTRIBUTED_I17_RESULT_REQUIRED")
        with self.harness._lock:
            state = self._state()
            existing = state["verifications"].get(closure_value["claim_record_hash72"])
            if existing is not None:
                existing_value = validate_distributed_postcondition_verification(existing)
                obs = validate_postcondition_observation(observation)
                if existing_value["postcondition_observation_hash72"] == obs["record_hash72"]:
                    return existing_value
                raise Pass218PostconditionReplayRejected("P218_I19_POSTCONDITION_VERIFICATION_ALREADY_RECORDED")
            verification = seal_distributed_postcondition_verification(closure=closure_value, result=result_value, observation=observation, ownership=self.current_ownership())
            state["verifications"][closure_value["claim_record_hash72"]] = _copy(verification)
            return _copy(verification)

    def verifications(self) -> list[dict[str, Any]]:
        with self.harness._lock:
            return [validate_distributed_postcondition_verification(value) for _, value in sorted(self._state()["verifications"].items())]

    def status(self) -> dict[str, Any]:
        closures = self.closure_ledger.closures()
        successful = [item for item in closures if item["outcome"] == "SUCCEEDED"]
        verified = self.verifications()
        return {
            "schema": POSTCONDITION_STATUS_SCHEMA,
            "version": PASS218_POSTCONDITION_VERSION,
            "distributed": True,
            "successful_terminal_closure_count": len(successful),
            "distributed_postcondition_verification_count": len(verified),
            "successful_closure_pending_verification_count": max(0, len(successful) - len(verified)),
            "failed_or_aborted_closure_count": len(closures) - len(successful),
            "failed_or_aborted_require_postcondition_verification": False,
            "successful_effect_verification_required": True,
            "postcondition_verification_grants_execution_authority": False,
            **_exclusions(),
        }


class Pass218UnavailablePostconditionLedger:
    distributed = True
    @staticmethod
    def _raise() -> None:
        raise Pass218PostconditionUnavailable("P218_I19_DISTRIBUTED_POSTCONDITION_UNAVAILABLE")
    def current_ownership(self) -> dict[str, Any]: self._raise(); raise AssertionError
    def record_verification(self, **kwargs: Any) -> dict[str, Any]: self._raise(); raise AssertionError
    def verification_for_claim(self, claim_hash72: str) -> dict[str, Any] | None: self._raise(); raise AssertionError
    def verifications(self) -> list[dict[str, Any]]: self._raise(); raise AssertionError
    def status(self) -> dict[str, Any]: self._raise(); raise AssertionError


def build_postcondition_ledger(authority: Any, execution_ledger: Pass218DistributedExecutionLedgerProtocol, closure_ledger: Pass218DistributedClosureLedgerProtocol) -> Pass218PostconditionLedgerProtocol:
    if isinstance(authority, Pass218InMemoryDistributedAuthority):
        return Pass218InMemoryPostconditionLedger(authority, execution_ledger, closure_ledger)
    if hasattr(authority, "client") and hasattr(authority, "namespace") and hasattr(authority, "owner_key") and hasattr(authority, "fence_key"):
        return Pass218EtcdPostconditionLedger(authority, execution_ledger, closure_ledger)
    return Pass218UnavailablePostconditionLedger()


__all__ = [
    "PASS218_POSTCONDITION_VERSION",
    "POSTCONDITION_OBSERVATION_SCHEMA",
    "POSTCONDITION_STATUS_SCHEMA",
    "POSTCONDITION_VERIFICATION_SCHEMA",
    "Pass218EtcdPostconditionLedger",
    "Pass218InMemoryPostconditionLedger",
    "Pass218PostconditionError",
    "Pass218PostconditionLedgerProtocol",
    "Pass218PostconditionReplayRejected",
    "Pass218PostconditionUnavailable",
    "Pass218PostconditionValidationError",
    "Pass218UnavailablePostconditionLedger",
    "build_postcondition_ledger",
    "seal_distributed_postcondition_verification",
    "seal_postcondition_observation",
    "validate_distributed_postcondition_verification",
    "validate_postcondition_observation",
]

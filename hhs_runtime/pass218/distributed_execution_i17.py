"""Pass 218 Iteration 17 fenced external-maintenance execution handoff.

I17 closes the boundary left deliberately open by I12-I16: a consumed I15 claim
may be handed to an explicitly configured external maintenance executor, but the
handoff itself is first reserved in the I10/I11 distributed owner/fence
substrate.  The external result is then persisted in that same substrate before
I15 terminal attestation/reconciliation is allowed to close.

A reserved dispatch is single-use.  If the authority host dies after handoff and
before a result is recorded, a successor may recover/query the original result,
but it may never invoke the external operation a second time.  I17 does not mint
canonical or action authority and does not make maintenance part of canonical
state mutation.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from typing import Any, Mapping, Protocol
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.commit_boundary import _canonical_bytes
from hhs_runtime.pass218.distributed_consumption_i16 import (
    Pass218DistributedConsumptionLedgerProtocol,
    Pass218DistributedConsumptionUnavailable,
)
from hhs_runtime.pass218.distributed_ownership import (
    Pass218DistributedOwnershipError,
    Pass218InMemoryDistributedAuthority,
    validate_distributed_ownership_record,
)
from hhs_runtime.pass218.execution_i15 import (
    validate_i12_maintenance_record,
    validate_release_claim,
)

PASS218_DISTRIBUTED_EXECUTION_VERSION = "HHS-P218-FENCED-EXTERNAL-EXECUTION-I17-V1"
EXTERNAL_DISPATCH_SCHEMA = "HHS-P218-I17-EXTERNAL-DISPATCH-V1"
EXTERNAL_RESULT_SCHEMA = "HHS-P218-I17-EXTERNAL-RESULT-V1"
DISTRIBUTED_EXECUTION_STATUS_SCHEMA = "HHS-P218-I17-DISTRIBUTED-EXECUTION-STATUS-V1"
DEFAULT_EXECUTION_SUFFIX = "execution-i17"
DEFAULT_EXECUTION_CAS_ATTEMPTS = 8
TERMINAL_OUTCOMES = frozenset({"SUCCEEDED", "FAILED", "ABORTED"})


class Pass218ExternalExecutionError(RuntimeError):
    pass


class Pass218ExternalExecutionValidationError(Pass218ExternalExecutionError):
    pass


class Pass218ExternalExecutionReplayRejected(Pass218ExternalExecutionError):
    pass


class Pass218ExternalExecutionUnavailable(Pass218ExternalExecutionError):
    pass


class Pass218ExternalExecutionResultUnknown(Pass218ExternalExecutionError):
    pass


def _copy(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, separators=(",", ":")))


def _require_text(value: Any, code: str, *, maximum: int = 512) -> str:
    if not isinstance(value, str):
        raise Pass218ExternalExecutionValidationError(code)
    value = value.strip()
    if not value or len(value) > maximum:
        raise Pass218ExternalExecutionValidationError(code)
    return value


def _require_hash72(value: Any, code: str) -> str:
    if not isinstance(value, str) or len(value) != 72 or not validate_hash72(value):
        raise Pass218ExternalExecutionValidationError(code)
    return value


def _require_positive_int(value: Any, code: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise Pass218ExternalExecutionValidationError(code)
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
        "verbatim_source_retained": False,
        "pass165_source_retaining_path_invoked": False,
        "authoritative_float_weights": False,
    }


def _assert_exclusions(record: Mapping[str, Any]) -> None:
    for key in _exclusions():
        if record.get(key) is not False:
            raise Pass218ExternalExecutionValidationError(
                "P218_I17_EXCLUSION_VIOLATION_" + key.upper()
            )


def _seal(schema: str, body: Mapping[str, Any]) -> dict[str, Any]:
    value = dict(body)
    value["record_hash72"] = hash72_digest({"domain": schema}, value)
    return value


def seal_external_dispatch(
    *,
    claim: Mapping[str, Any],
    consumption_entry: Mapping[str, Any],
    ownership: Mapping[str, Any],
    executor_id: str,
    dispatched_epoch_ns: int,
) -> dict[str, Any]:
    claim_value = validate_release_claim(claim)
    owner = validate_distributed_ownership_record(ownership)
    if consumption_entry.get("claim_record_hash72") != claim_value["record_hash72"]:
        raise Pass218ExternalExecutionValidationError("P218_I17_CONSUMPTION_CLAIM_MISMATCH")
    if consumption_entry.get("release_record_hash72") != claim_value["release_record_hash72"]:
        raise Pass218ExternalExecutionValidationError("P218_I17_CONSUMPTION_RELEASE_MISMATCH")
    if owner["fence_epoch"] < claim_value["distributed_fence_epoch"]:
        raise Pass218ExternalExecutionValidationError("P218_I17_DISPATCH_FENCE_REGRESSION")
    epoch_ns = _require_positive_int(dispatched_epoch_ns, "P218_I17_DISPATCH_EPOCH_INVALID")
    if epoch_ns < claim_value["claimed_epoch_ns"]:
        raise Pass218ExternalExecutionValidationError("P218_I17_DISPATCH_BEFORE_CLAIM")
    executor = _require_text(executor_id, "P218_I17_EXECUTOR_ID_INVALID", maximum=256)
    body = {
        "schema": EXTERNAL_DISPATCH_SCHEMA,
        "version": PASS218_DISTRIBUTED_EXECUTION_VERSION,
        "dispatch_id": "i17-" + hash72_digest(
            {"domain": "HHS-P218-I17-DISPATCH-ID"},
            {
                "claim_record_hash72": claim_value["record_hash72"],
                "dispatch_fence_epoch": owner["fence_epoch"],
                "executor_id": executor,
                "dispatched_epoch_ns": epoch_ns,
            },
        ),
        "claim_record_hash72": claim_value["record_hash72"],
        "release_record_hash72": claim_value["release_record_hash72"],
        "action_record_hash72": claim_value["action_record_hash72"],
        "attempt_id": claim_value["attempt_id"],
        "action": claim_value["action"],
        "executor_operator_id": claim_value["executor_operator_id"],
        "executor_id": executor,
        "claim_fence_epoch": claim_value["distributed_fence_epoch"],
        "dispatch_fence_epoch": owner["fence_epoch"],
        "dispatch_owner_id": owner["owner_id"],
        "dispatch_host_id": owner["host_id"],
        "ownership_hash72": owner["ownership_hash72"],
        "consumption_entry_hash72": _require_hash72(
            consumption_entry.get("record_hash72"), "P218_I17_CONSUMPTION_HASH_INVALID"
        ),
        "dispatched_epoch_ns": epoch_ns,
        "distributed_reservation_precedes_external_call": True,
        "single_dispatch_per_claim": True,
        "single_dispatch_per_action": True,
        "redispatch_after_unknown_forbidden": True,
        "successor_may_recover_result_only": True,
        "maintenance_remains_external": True,
        **_exclusions(),
    }
    return _seal(EXTERNAL_DISPATCH_SCHEMA, body)


def validate_external_dispatch(record: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise Pass218ExternalExecutionValidationError("P218_I17_DISPATCH_INVALID")
    value = _copy(record)
    supplied = _require_hash72(value.pop("record_hash72", None), "P218_I17_DISPATCH_HASH_INVALID")
    if value.get("schema") != EXTERNAL_DISPATCH_SCHEMA or value.get("version") != PASS218_DISTRIBUTED_EXECUTION_VERSION:
        raise Pass218ExternalExecutionValidationError("P218_I17_DISPATCH_SCHEMA_INVALID")
    for key in (
        "claim_record_hash72", "release_record_hash72", "action_record_hash72",
        "ownership_hash72", "consumption_entry_hash72",
    ):
        _require_hash72(value.get(key), "P218_I17_DISPATCH_BINDING_HASH_INVALID")
    _require_positive_int(value.get("claim_fence_epoch"), "P218_I17_CLAIM_FENCE_INVALID")
    _require_positive_int(value.get("dispatch_fence_epoch"), "P218_I17_DISPATCH_FENCE_INVALID")
    _require_positive_int(value.get("dispatched_epoch_ns"), "P218_I17_DISPATCH_EPOCH_INVALID")
    _require_text(value.get("executor_id"), "P218_I17_EXECUTOR_ID_INVALID", maximum=256)
    if value["dispatch_fence_epoch"] < value["claim_fence_epoch"]:
        raise Pass218ExternalExecutionValidationError("P218_I17_DISPATCH_FENCE_REGRESSION")
    for key in (
        "distributed_reservation_precedes_external_call", "single_dispatch_per_claim",
        "single_dispatch_per_action", "redispatch_after_unknown_forbidden",
        "successor_may_recover_result_only", "maintenance_remains_external",
    ):
        if value.get(key) is not True:
            raise Pass218ExternalExecutionValidationError("P218_I17_DISPATCH_INVARIANT_" + key.upper())
    _assert_exclusions(value)
    if supplied != hash72_digest({"domain": EXTERNAL_DISPATCH_SCHEMA}, value):
        raise Pass218ExternalExecutionValidationError("P218_I17_DISPATCH_HASH_MISMATCH")
    return {**value, "record_hash72": supplied}


def seal_external_result(
    *,
    dispatch: Mapping[str, Any],
    ownership: Mapping[str, Any],
    raw_result: Mapping[str, Any],
    completed_epoch_ns: int,
) -> dict[str, Any]:
    dispatch_value = validate_external_dispatch(dispatch)
    owner = validate_distributed_ownership_record(ownership)
    if owner["fence_epoch"] < dispatch_value["dispatch_fence_epoch"]:
        raise Pass218ExternalExecutionValidationError("P218_I17_RESULT_FENCE_REGRESSION")
    if not isinstance(raw_result, Mapping):
        raise Pass218ExternalExecutionValidationError("P218_I17_EXTERNAL_RESULT_INVALID")
    outcome = _require_text(raw_result.get("outcome"), "P218_I17_OUTCOME_INVALID").upper()
    if outcome not in TERMINAL_OUTCOMES:
        raise Pass218ExternalExecutionValidationError("P218_I17_OUTCOME_INVALID")
    executed = bool(raw_result.get("external_operation_executed", False))
    i12_record = raw_result.get("i12_maintenance_record")
    i12_value: dict[str, Any] | None = None
    if isinstance(i12_record, Mapping):
        i12_value = validate_i12_maintenance_record(dispatch_value["action"], i12_record)
    if outcome == "SUCCEEDED" and (not executed or i12_value is None):
        raise Pass218ExternalExecutionValidationError("P218_I17_SUCCESS_REQUIRES_EXECUTION_AND_I12_EVIDENCE")
    completed = _require_positive_int(completed_epoch_ns, "P218_I17_COMPLETED_EPOCH_INVALID")
    if completed < dispatch_value["dispatched_epoch_ns"]:
        raise Pass218ExternalExecutionValidationError("P218_I17_RESULT_BEFORE_DISPATCH")
    body = {
        "schema": EXTERNAL_RESULT_SCHEMA,
        "version": PASS218_DISTRIBUTED_EXECUTION_VERSION,
        "dispatch_id": dispatch_value["dispatch_id"],
        "dispatch_record_hash72": dispatch_value["record_hash72"],
        "claim_record_hash72": dispatch_value["claim_record_hash72"],
        "release_record_hash72": dispatch_value["release_record_hash72"],
        "action_record_hash72": dispatch_value["action_record_hash72"],
        "attempt_id": dispatch_value["attempt_id"],
        "action": dispatch_value["action"],
        "executor_operator_id": dispatch_value["executor_operator_id"],
        "executor_id": dispatch_value["executor_id"],
        "dispatch_fence_epoch": dispatch_value["dispatch_fence_epoch"],
        "result_recorded_fence_epoch": owner["fence_epoch"],
        "result_recorded_owner_id": owner["owner_id"],
        "result_recorded_host_id": owner["host_id"],
        "result_ownership_hash72": owner["ownership_hash72"],
        "outcome": outcome,
        "external_operation_executed": executed,
        "external_result_hash72": _require_hash72(
            raw_result.get("external_result_hash72"), "P218_I17_EXTERNAL_RESULT_HASH_INVALID"
        ),
        "i12_evidence_present": i12_value is not None,
        "i12_maintenance_record": _copy(i12_value) if i12_value is not None else None,
        "i12_maintenance_record_hash72": i12_value.get("record_hash72") if i12_value is not None else None,
        "completed_epoch_ns": completed,
        "distributed_result_precedes_local_attestation": True,
        "terminal_result_single_write": True,
        "retry_requires_new_prepared_action": True,
        "maintenance_remains_external": True,
        **_exclusions(),
    }
    return _seal(EXTERNAL_RESULT_SCHEMA, body)


def validate_external_result(record: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise Pass218ExternalExecutionValidationError("P218_I17_RESULT_INVALID")
    value = _copy(record)
    supplied = _require_hash72(value.pop("record_hash72", None), "P218_I17_RESULT_HASH_INVALID")
    if value.get("schema") != EXTERNAL_RESULT_SCHEMA or value.get("version") != PASS218_DISTRIBUTED_EXECUTION_VERSION:
        raise Pass218ExternalExecutionValidationError("P218_I17_RESULT_SCHEMA_INVALID")
    for key in (
        "dispatch_record_hash72", "claim_record_hash72", "release_record_hash72",
        "action_record_hash72", "result_ownership_hash72", "external_result_hash72",
    ):
        _require_hash72(value.get(key), "P218_I17_RESULT_BINDING_HASH_INVALID")
    if value.get("outcome") not in TERMINAL_OUTCOMES:
        raise Pass218ExternalExecutionValidationError("P218_I17_OUTCOME_INVALID")
    _require_positive_int(value.get("dispatch_fence_epoch"), "P218_I17_DISPATCH_FENCE_INVALID")
    _require_positive_int(value.get("result_recorded_fence_epoch"), "P218_I17_RESULT_FENCE_INVALID")
    _require_positive_int(value.get("completed_epoch_ns"), "P218_I17_COMPLETED_EPOCH_INVALID")
    if value["result_recorded_fence_epoch"] < value["dispatch_fence_epoch"]:
        raise Pass218ExternalExecutionValidationError("P218_I17_RESULT_FENCE_REGRESSION")
    if value.get("i12_evidence_present") is True:
        i12_record = value.get("i12_maintenance_record")
        if not isinstance(i12_record, Mapping):
            raise Pass218ExternalExecutionValidationError("P218_I17_I12_EVIDENCE_INVALID")
        i12_value = validate_i12_maintenance_record(value["action"], i12_record)
        if i12_value.get("record_hash72") != value.get("i12_maintenance_record_hash72"):
            raise Pass218ExternalExecutionValidationError("P218_I17_I12_EVIDENCE_HASH_MISMATCH")
    elif value.get("outcome") == "SUCCEEDED":
        raise Pass218ExternalExecutionValidationError("P218_I17_SUCCESS_REQUIRES_I12_EVIDENCE")
    if value.get("outcome") == "SUCCEEDED" and value.get("external_operation_executed") is not True:
        raise Pass218ExternalExecutionValidationError("P218_I17_SUCCESS_REQUIRES_EXECUTION")
    for key in (
        "distributed_result_precedes_local_attestation", "terminal_result_single_write",
        "retry_requires_new_prepared_action", "maintenance_remains_external",
    ):
        if value.get(key) is not True:
            raise Pass218ExternalExecutionValidationError("P218_I17_RESULT_INVARIANT_" + key.upper())
    _assert_exclusions(value)
    if supplied != hash72_digest({"domain": EXTERNAL_RESULT_SCHEMA}, value):
        raise Pass218ExternalExecutionValidationError("P218_I17_RESULT_HASH_MISMATCH")
    return {**value, "record_hash72": supplied}


class Pass218ExternalExecutorProtocol(Protocol):
    executor_id: str

    def execute(self, dispatch: Mapping[str, Any]) -> Mapping[str, Any]: ...
    def recover(self, dispatch: Mapping[str, Any]) -> Mapping[str, Any] | None: ...


class Pass218HmacHttpExternalExecutor:
    """Explicitly configured authenticated HTTP bridge to an external I12 executor."""

    def __init__(self, *, executor_id: str, url: str, shared_secret: str, timeout_seconds: int = 30, allow_http_loopback: bool = False) -> None:
        self.executor_id = _require_text(executor_id, "P218_I17_EXECUTOR_ID_INVALID", maximum=256)
        self.url = _require_text(url, "P218_I17_EXECUTOR_URL_INVALID", maximum=2048)
        self.shared_secret = _require_text(shared_secret, "P218_I17_EXECUTOR_SECRET_INVALID", maximum=4096).encode("utf-8")
        self.timeout_seconds = _require_positive_int(timeout_seconds, "P218_I17_EXECUTOR_TIMEOUT_INVALID")
        parsed = urlparse(self.url)
        loopback = parsed.hostname in {"127.0.0.1", "localhost", "::1"}
        if parsed.scheme != "https" and not (allow_http_loopback and parsed.scheme == "http" and loopback):
            raise Pass218ExternalExecutionValidationError("P218_I17_EXECUTOR_HTTPS_REQUIRED")

    def _request(self, operation: str, dispatch: Mapping[str, Any]) -> Mapping[str, Any] | None:
        dispatch_value = validate_external_dispatch(dispatch)
        body = _canonical_bytes({"operation": operation, "dispatch": dispatch_value})
        signature = hmac.new(self.shared_secret, body, hashlib.sha256).hexdigest()
        request = Request(
            self.url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-HHS-I17-Executor-Id": self.executor_id,
                "X-HHS-I17-Request-HMAC-SHA256": signature,
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read()
                response_signature = response.headers.get("X-HHS-I17-Response-HMAC-SHA256", "")
        except Exception as exc:
            raise Pass218ExternalExecutionResultUnknown("P218_I17_EXTERNAL_EXECUTOR_RESULT_UNKNOWN") from exc
        expected = hmac.new(self.shared_secret, raw, hashlib.sha256).hexdigest()
        if not response_signature or not hmac.compare_digest(response_signature, expected):
            raise Pass218ExternalExecutionValidationError("P218_I17_EXTERNAL_EXECUTOR_RESPONSE_HMAC_INVALID")
        try:
            value = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise Pass218ExternalExecutionValidationError("P218_I17_EXTERNAL_EXECUTOR_RESPONSE_JSON_INVALID") from exc
        if not isinstance(value, Mapping):
            raise Pass218ExternalExecutionValidationError("P218_I17_EXTERNAL_EXECUTOR_RESPONSE_INVALID")
        if operation == "RECOVER" and value.get("status") in {"PENDING", "UNKNOWN", "NOT_FOUND"}:
            return None
        return dict(value)

    def execute(self, dispatch: Mapping[str, Any]) -> Mapping[str, Any]:
        value = self._request("EXECUTE", dispatch)
        if value is None:
            raise Pass218ExternalExecutionResultUnknown("P218_I17_EXTERNAL_EXECUTOR_RESULT_UNKNOWN")
        return value

    def recover(self, dispatch: Mapping[str, Any]) -> Mapping[str, Any] | None:
        return self._request("RECOVER", dispatch)


class Pass218DistributedExecutionLedgerProtocol(Protocol):
    distributed: bool

    def current_ownership(self) -> dict[str, Any]: ...
    def reserve_dispatch(self, claim: Mapping[str, Any], *, executor_id: str, dispatched_epoch_ns: int) -> dict[str, Any]: ...
    def dispatch_for_claim(self, claim_hash72: str) -> dict[str, Any] | None: ...
    def result_for_claim(self, claim_hash72: str) -> dict[str, Any] | None: ...
    def record_result(self, dispatch: Mapping[str, Any], raw_result: Mapping[str, Any], *, completed_epoch_ns: int) -> dict[str, Any]: ...
    def dispatches(self) -> list[dict[str, Any]]: ...
    def status(self) -> dict[str, Any]: ...


class Pass218EtcdDistributedExecutionLedger:
    distributed = True

    def __init__(self, authority: Any, consumption_ledger: Pass218DistributedConsumptionLedgerProtocol, *, suffix: str = DEFAULT_EXECUTION_SUFFIX, cas_attempts: int = DEFAULT_EXECUTION_CAS_ATTEMPTS) -> None:
        if not hasattr(authority, "client") or not hasattr(authority, "namespace"):
            raise Pass218ExternalExecutionValidationError("P218_I17_ETCD_AUTHORITY_REQUIRED")
        self.authority = authority
        self.client = authority.client
        self.consumption_ledger = consumption_ledger
        self.namespace = str(authority.namespace).rstrip("/") + "/" + suffix
        self.cas_attempts = _require_positive_int(cas_attempts, "P218_I17_CAS_ATTEMPTS_INVALID")

    def _key(self, suffix: str) -> bytes:
        return (self.namespace + "/" + suffix).encode("utf-8")

    def dispatch_key(self, claim_hash72: str) -> bytes:
        return self._key("dispatches/" + _marker(_require_hash72(claim_hash72, "P218_I17_CLAIM_HASH_INVALID")))

    def action_key(self, action_hash72: str) -> bytes:
        return self._key("actions/" + _marker(_require_hash72(action_hash72, "P218_I17_ACTION_HASH_INVALID")))

    def result_key(self, claim_hash72: str) -> bytes:
        return self._key("results/" + _marker(_require_hash72(claim_hash72, "P218_I17_CLAIM_HASH_INVALID")))

    def current_ownership(self) -> dict[str, Any]:
        try:
            return validate_distributed_ownership_record(self.authority.assert_current())
        except Pass218DistributedOwnershipError as exc:
            raise Pass218ExternalExecutionUnavailable(str(exc)) from exc

    def _read_dispatch(self, key: bytes) -> dict[str, Any] | None:
        raw, _ = self.client.range_value(key)
        if raw is None:
            return None
        try:
            value = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise Pass218ExternalExecutionValidationError("P218_I17_DISTRIBUTED_DISPATCH_JSON_INVALID") from exc
        if not isinstance(value, Mapping) or _canonical_bytes(value) != raw:
            raise Pass218ExternalExecutionValidationError("P218_I17_DISTRIBUTED_DISPATCH_NONCANONICAL")
        return validate_external_dispatch(value)

    def _read_result(self, key: bytes) -> dict[str, Any] | None:
        raw, _ = self.client.range_value(key)
        if raw is None:
            return None
        try:
            value = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise Pass218ExternalExecutionValidationError("P218_I17_DISTRIBUTED_RESULT_JSON_INVALID") from exc
        if not isinstance(value, Mapping) or _canonical_bytes(value) != raw:
            raise Pass218ExternalExecutionValidationError("P218_I17_DISTRIBUTED_RESULT_NONCANONICAL")
        return validate_external_result(value)

    def dispatch_for_claim(self, claim_hash72: str) -> dict[str, Any] | None:
        return self._read_dispatch(self.dispatch_key(claim_hash72))

    def result_for_claim(self, claim_hash72: str) -> dict[str, Any] | None:
        return self._read_result(self.result_key(claim_hash72))

    def reserve_dispatch(self, claim: Mapping[str, Any], *, executor_id: str, dispatched_epoch_ns: int) -> dict[str, Any]:
        claim_value = validate_release_claim(claim)
        consumption = self.consumption_ledger.entry_for_release(claim_value["release_record_hash72"])
        if consumption is None or consumption.get("claim_record_hash72") != claim_value["record_hash72"]:
            raise Pass218ExternalExecutionValidationError("P218_I17_DISTRIBUTED_CONSUMPTION_REQUIRED")
        for _ in range(self.cas_attempts):
            ownership = self.current_ownership()
            dispatch = seal_external_dispatch(
                claim=claim_value,
                consumption_entry=consumption,
                ownership=ownership,
                executor_id=executor_id,
                dispatched_epoch_ns=dispatched_epoch_ns,
            )
            claim_key = self.dispatch_key(claim_value["record_hash72"])
            action_key = self.action_key(claim_value["action_record_hash72"])
            owner_bytes = _canonical_bytes(ownership)
            fence_bytes = str(ownership["fence_epoch"]).encode("ascii")
            response = self.client.txn(
                compare=[
                    self.client.compare_value(self.authority.owner_key, owner_bytes),
                    self.client.compare_value(self.authority.fence_key, fence_bytes),
                    self.client.compare_version(claim_key, 0),
                    self.client.compare_version(action_key, 0),
                ],
                success=[
                    self.client.put_operation(claim_key, _canonical_bytes(dispatch)),
                    self.client.put_operation(action_key, _canonical_bytes(dispatch)),
                ],
            )
            if response.get("succeeded") is True:
                return _copy(dispatch)
            self.current_ownership()
            if self.dispatch_for_claim(claim_value["record_hash72"]) is not None:
                raise Pass218ExternalExecutionReplayRejected("P218_I17_CLAIM_ALREADY_DISPATCHED")
            raw_action, _ = self.client.range_value(action_key)
            if raw_action is not None:
                raise Pass218ExternalExecutionReplayRejected("P218_I17_ACTION_ALREADY_DISPATCHED")
        raise Pass218ExternalExecutionUnavailable("P218_I17_DISPATCH_CAS_CONFLICT")

    def record_result(self, dispatch: Mapping[str, Any], raw_result: Mapping[str, Any], *, completed_epoch_ns: int) -> dict[str, Any]:
        dispatch_value = validate_external_dispatch(dispatch)
        stored = self.dispatch_for_claim(dispatch_value["claim_record_hash72"])
        if stored is None or stored["record_hash72"] != dispatch_value["record_hash72"]:
            raise Pass218ExternalExecutionValidationError("P218_I17_DISTRIBUTED_DISPATCH_REQUIRED")
        ownership = self.current_ownership()
        result = seal_external_result(
            dispatch=dispatch_value,
            ownership=ownership,
            raw_result=raw_result,
            completed_epoch_ns=completed_epoch_ns,
        )
        result_key = self.result_key(dispatch_value["claim_record_hash72"])
        owner_bytes = _canonical_bytes(ownership)
        fence_bytes = str(ownership["fence_epoch"]).encode("ascii")
        dispatch_bytes = _canonical_bytes(dispatch_value)
        response = self.client.txn(
            compare=[
                self.client.compare_value(self.authority.owner_key, owner_bytes),
                self.client.compare_value(self.authority.fence_key, fence_bytes),
                self.client.compare_value(self.dispatch_key(dispatch_value["claim_record_hash72"]), dispatch_bytes),
                self.client.compare_version(result_key, 0),
            ],
            success=[self.client.put_operation(result_key, _canonical_bytes(result))],
        )
        if response.get("succeeded") is True:
            return _copy(result)
        existing = self.result_for_claim(dispatch_value["claim_record_hash72"])
        if existing is not None:
            if existing["record_hash72"] == result["record_hash72"]:
                return existing
            raise Pass218ExternalExecutionReplayRejected("P218_I17_TERMINAL_RESULT_ALREADY_RECORDED")
        self.current_ownership()
        raise Pass218ExternalExecutionUnavailable("P218_I17_RESULT_CAS_CONFLICT")

    def dispatches(self) -> list[dict[str, Any]]:
        consumption_entries = self.consumption_ledger.entries()
        result: list[dict[str, Any]] = []
        for item in consumption_entries:
            dispatch = self.dispatch_for_claim(item["claim_record_hash72"])
            if dispatch is not None:
                result.append(dispatch)
        return result

    def status(self) -> dict[str, Any]:
        dispatches = self.dispatches()
        completed = sum(1 for item in dispatches if self.result_for_claim(item["claim_record_hash72"]) is not None)
        return {
            "schema": DISTRIBUTED_EXECUTION_STATUS_SCHEMA,
            "version": PASS218_DISTRIBUTED_EXECUTION_VERSION,
            "distributed": True,
            "dispatch_count": len(dispatches),
            "terminal_result_count": completed,
            "unresolved_dispatch_count": len(dispatches) - completed,
            "distributed_reservation_precedes_external_call": True,
            "distributed_result_precedes_local_attestation": True,
            "redispatch_after_unknown_forbidden": True,
            "successor_recovery_only": True,
            **_exclusions(),
        }


class Pass218InMemoryDistributedExecutionLedger:
    distributed = True

    def __init__(self, authority: Pass218InMemoryDistributedAuthority, consumption_ledger: Pass218DistributedConsumptionLedgerProtocol) -> None:
        self.authority = authority
        self.harness = authority.harness
        self.consumption_ledger = consumption_ledger

    def _state(self) -> dict[str, Any]:
        state = getattr(self.harness, "_pass218_i17_execution_state", None)
        if state is None:
            state = {"dispatches": {}, "actions": {}, "results": {}}
            setattr(self.harness, "_pass218_i17_execution_state", state)
        return state

    def current_ownership(self) -> dict[str, Any]:
        try:
            return validate_distributed_ownership_record(self.authority.assert_current())
        except Pass218DistributedOwnershipError as exc:
            raise Pass218ExternalExecutionUnavailable(str(exc)) from exc

    def reserve_dispatch(self, claim: Mapping[str, Any], *, executor_id: str, dispatched_epoch_ns: int) -> dict[str, Any]:
        claim_value = validate_release_claim(claim)
        consumption = self.consumption_ledger.entry_for_release(claim_value["release_record_hash72"])
        if consumption is None or consumption.get("claim_record_hash72") != claim_value["record_hash72"]:
            raise Pass218ExternalExecutionValidationError("P218_I17_DISTRIBUTED_CONSUMPTION_REQUIRED")
        with self.harness._lock:
            ownership = self.current_ownership()
            state = self._state()
            if claim_value["record_hash72"] in state["dispatches"]:
                raise Pass218ExternalExecutionReplayRejected("P218_I17_CLAIM_ALREADY_DISPATCHED")
            if claim_value["action_record_hash72"] in state["actions"]:
                raise Pass218ExternalExecutionReplayRejected("P218_I17_ACTION_ALREADY_DISPATCHED")
            dispatch = seal_external_dispatch(
                claim=claim_value,
                consumption_entry=consumption,
                ownership=ownership,
                executor_id=executor_id,
                dispatched_epoch_ns=dispatched_epoch_ns,
            )
            state["dispatches"][claim_value["record_hash72"]] = _copy(dispatch)
            state["actions"][claim_value["action_record_hash72"]] = _copy(dispatch)
            return _copy(dispatch)

    def dispatch_for_claim(self, claim_hash72: str) -> dict[str, Any] | None:
        _require_hash72(claim_hash72, "P218_I17_CLAIM_HASH_INVALID")
        with self.harness._lock:
            value = self._state()["dispatches"].get(claim_hash72)
            return None if value is None else validate_external_dispatch(value)

    def result_for_claim(self, claim_hash72: str) -> dict[str, Any] | None:
        _require_hash72(claim_hash72, "P218_I17_CLAIM_HASH_INVALID")
        with self.harness._lock:
            value = self._state()["results"].get(claim_hash72)
            return None if value is None else validate_external_result(value)

    def record_result(self, dispatch: Mapping[str, Any], raw_result: Mapping[str, Any], *, completed_epoch_ns: int) -> dict[str, Any]:
        dispatch_value = validate_external_dispatch(dispatch)
        with self.harness._lock:
            ownership = self.current_ownership()
            state = self._state()
            stored = state["dispatches"].get(dispatch_value["claim_record_hash72"])
            if stored is None or validate_external_dispatch(stored)["record_hash72"] != dispatch_value["record_hash72"]:
                raise Pass218ExternalExecutionValidationError("P218_I17_DISTRIBUTED_DISPATCH_REQUIRED")
            existing = state["results"].get(dispatch_value["claim_record_hash72"])
            result = seal_external_result(
                dispatch=dispatch_value,
                ownership=ownership,
                raw_result=raw_result,
                completed_epoch_ns=completed_epoch_ns,
            )
            if existing is not None:
                existing_value = validate_external_result(existing)
                if existing_value["record_hash72"] == result["record_hash72"]:
                    return existing_value
                raise Pass218ExternalExecutionReplayRejected("P218_I17_TERMINAL_RESULT_ALREADY_RECORDED")
            state["results"][dispatch_value["claim_record_hash72"]] = _copy(result)
            return _copy(result)

    def dispatches(self) -> list[dict[str, Any]]:
        with self.harness._lock:
            return [validate_external_dispatch(value) for _, value in sorted(self._state()["dispatches"].items())]

    def status(self) -> dict[str, Any]:
        dispatches = self.dispatches()
        completed = sum(1 for item in dispatches if self.result_for_claim(item["claim_record_hash72"]) is not None)
        return {
            "schema": DISTRIBUTED_EXECUTION_STATUS_SCHEMA,
            "version": PASS218_DISTRIBUTED_EXECUTION_VERSION,
            "distributed": True,
            "dispatch_count": len(dispatches),
            "terminal_result_count": completed,
            "unresolved_dispatch_count": len(dispatches) - completed,
            "distributed_reservation_precedes_external_call": True,
            "distributed_result_precedes_local_attestation": True,
            "redispatch_after_unknown_forbidden": True,
            "successor_recovery_only": True,
            **_exclusions(),
        }


class Pass218UnavailableDistributedExecutionLedger:
    distributed = True

    @staticmethod
    def _raise() -> None:
        raise Pass218ExternalExecutionUnavailable("P218_I17_DISTRIBUTED_EXECUTION_UNAVAILABLE")

    def current_ownership(self) -> dict[str, Any]:
        self._raise(); raise AssertionError

    def reserve_dispatch(self, claim: Mapping[str, Any], *, executor_id: str, dispatched_epoch_ns: int) -> dict[str, Any]:
        self._raise(); raise AssertionError

    def dispatch_for_claim(self, claim_hash72: str) -> dict[str, Any] | None:
        self._raise(); raise AssertionError

    def result_for_claim(self, claim_hash72: str) -> dict[str, Any] | None:
        self._raise(); raise AssertionError

    def record_result(self, dispatch: Mapping[str, Any], raw_result: Mapping[str, Any], *, completed_epoch_ns: int) -> dict[str, Any]:
        self._raise(); raise AssertionError

    def dispatches(self) -> list[dict[str, Any]]:
        self._raise(); raise AssertionError

    def status(self) -> dict[str, Any]:
        self._raise(); raise AssertionError


def build_distributed_execution_ledger(authority: Any, consumption_ledger: Pass218DistributedConsumptionLedgerProtocol) -> Pass218DistributedExecutionLedgerProtocol:
    if isinstance(authority, Pass218InMemoryDistributedAuthority):
        return Pass218InMemoryDistributedExecutionLedger(authority, consumption_ledger)
    if hasattr(authority, "client") and hasattr(authority, "namespace") and hasattr(authority, "owner_key") and hasattr(authority, "fence_key"):
        return Pass218EtcdDistributedExecutionLedger(authority, consumption_ledger)
    return Pass218UnavailableDistributedExecutionLedger()


def build_external_executor_from_environment() -> Pass218ExternalExecutorProtocol | None:
    url = os.environ.get("HHS_PASS218_I17_EXECUTOR_URL", "").strip()
    if not url:
        return None
    executor_id = os.environ.get("HHS_PASS218_I17_EXECUTOR_ID", "").strip()
    secret = os.environ.get("HHS_PASS218_I17_EXECUTOR_SHARED_SECRET", "").strip()
    if not executor_id or not secret:
        raise Pass218ExternalExecutionValidationError("P218_I17_EXECUTOR_ID_AND_SHARED_SECRET_REQUIRED")
    timeout = int(os.environ.get("HHS_PASS218_I17_EXECUTOR_TIMEOUT_SECONDS", "30"))
    allow_loopback = os.environ.get("HHS_PASS218_I17_ALLOW_HTTP_LOOPBACK", "0").strip() == "1"
    return Pass218HmacHttpExternalExecutor(
        executor_id=executor_id,
        url=url,
        shared_secret=secret,
        timeout_seconds=timeout,
        allow_http_loopback=allow_loopback,
    )


__all__ = [
    "DISTRIBUTED_EXECUTION_STATUS_SCHEMA",
    "EXTERNAL_DISPATCH_SCHEMA",
    "EXTERNAL_RESULT_SCHEMA",
    "PASS218_DISTRIBUTED_EXECUTION_VERSION",
    "Pass218DistributedExecutionLedgerProtocol",
    "Pass218EtcdDistributedExecutionLedger",
    "Pass218ExternalExecutionError",
    "Pass218ExternalExecutionReplayRejected",
    "Pass218ExternalExecutionResultUnknown",
    "Pass218ExternalExecutionUnavailable",
    "Pass218ExternalExecutionValidationError",
    "Pass218ExternalExecutorProtocol",
    "Pass218HmacHttpExternalExecutor",
    "Pass218InMemoryDistributedExecutionLedger",
    "Pass218UnavailableDistributedExecutionLedger",
    "build_distributed_execution_ledger",
    "build_external_executor_from_environment",
    "seal_external_dispatch",
    "seal_external_result",
    "validate_external_dispatch",
    "validate_external_result",
]

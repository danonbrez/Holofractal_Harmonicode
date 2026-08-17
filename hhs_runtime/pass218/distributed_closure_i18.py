"""Pass 218 Iteration 18 distributed terminal-closure convergence.

I18 is downstream of the frozen I17 external-execution handoff.  It mirrors the
exact I13 prepared-action record needed for terminal diagnostics into the
existing I10/I11 distributed owner/fence substrate before external dispatch,
then seals one distributed terminal closure after the immutable I17 result.

The closure contains the exact I15 attestation, I13 maintenance-run receipt, and
I15 reconciliation record.  Only after that distributed closure is durable may
host-local I13/I15 mirrors be repaired.  A successor host may therefore recover
terminal evidence after machine loss without redispatching the external action
or minting new authority.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Protocol

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.commit_boundary import _canonical_bytes
from hhs_runtime.pass218.distributed_execution_i17 import (
    Pass218DistributedExecutionLedgerProtocol,
    validate_external_result,
)
from hhs_runtime.pass218.distributed_ownership import (
    Pass218DistributedOwnershipError,
    Pass218InMemoryDistributedAuthority,
    validate_distributed_ownership_record,
)
from hhs_runtime.pass218.execution_i15 import (
    validate_execution_attestation,
    validate_execution_reconciliation,
    validate_release_claim,
)
from hhs_runtime.pass218.observability_i13 import (
    validate_maintenance_run_receipt,
    validate_operator_action,
)

PASS218_DISTRIBUTED_CLOSURE_VERSION = "HHS-P218-DISTRIBUTED-TERMINAL-CLOSURE-I18-V1"
ACTION_SOURCE_SCHEMA = "HHS-P218-I18-DISTRIBUTED-ACTION-SOURCE-V1"
TERMINAL_CLOSURE_SCHEMA = "HHS-P218-I18-DISTRIBUTED-TERMINAL-CLOSURE-V1"
DISTRIBUTED_CLOSURE_STATUS_SCHEMA = "HHS-P218-I18-DISTRIBUTED-CLOSURE-STATUS-V1"
DEFAULT_CLOSURE_SUFFIX = "closure-i18"


class Pass218DistributedClosureError(RuntimeError):
    pass


class Pass218DistributedClosureValidationError(Pass218DistributedClosureError):
    pass


class Pass218DistributedClosureReplayRejected(Pass218DistributedClosureError):
    pass


class Pass218DistributedClosureUnavailable(Pass218DistributedClosureError):
    pass


def _copy(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, separators=(",", ":")))


def _require_hash72(value: Any, code: str) -> str:
    if not isinstance(value, str) or len(value) != 72 or not validate_hash72(value):
        raise Pass218DistributedClosureValidationError(code)
    return value


def _require_positive_int(value: Any, code: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise Pass218DistributedClosureValidationError(code)
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
            raise Pass218DistributedClosureValidationError(
                "P218_I18_EXCLUSION_VIOLATION_" + key.upper()
            )


def _seal(schema: str, body: Mapping[str, Any]) -> dict[str, Any]:
    value = dict(body)
    value["record_hash72"] = hash72_digest({"domain": schema}, value)
    return value


def seal_distributed_action_source(
    *,
    action_record: Mapping[str, Any],
    ownership: Mapping[str, Any],
) -> dict[str, Any]:
    action = validate_operator_action(action_record)
    owner = validate_distributed_ownership_record(ownership)
    return _seal(
        ACTION_SOURCE_SCHEMA,
        {
            "schema": ACTION_SOURCE_SCHEMA,
            "version": PASS218_DISTRIBUTED_CLOSURE_VERSION,
            "action_record_hash72": action["record_hash72"],
            "action": action["action"],
            "operator_id": action["operator_id"],
            "source_fence_epoch": owner["fence_epoch"],
            "source_owner_id": owner["owner_id"],
            "source_host_id": owner["host_id"],
            "source_ownership_hash72": owner["ownership_hash72"],
            "action_record": _copy(action),
            "metadata_only": True,
            "grants_execution_authority": False,
            "grants_retry_authority": False,
            "successor_may_use_for_terminal_diagnostics_only": True,
            **_exclusions(),
        },
    )


def validate_distributed_action_source(record: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise Pass218DistributedClosureValidationError("P218_I18_ACTION_SOURCE_INVALID")
    value = _copy(record)
    supplied = _require_hash72(value.pop("record_hash72", None), "P218_I18_ACTION_SOURCE_HASH_INVALID")
    if value.get("schema") != ACTION_SOURCE_SCHEMA or value.get("version") != PASS218_DISTRIBUTED_CLOSURE_VERSION:
        raise Pass218DistributedClosureValidationError("P218_I18_ACTION_SOURCE_SCHEMA_INVALID")
    _require_hash72(value.get("action_record_hash72"), "P218_I18_ACTION_HASH_INVALID")
    _require_hash72(value.get("source_ownership_hash72"), "P218_I18_ACTION_SOURCE_OWNERSHIP_HASH_INVALID")
    _require_positive_int(value.get("source_fence_epoch"), "P218_I18_ACTION_SOURCE_FENCE_INVALID")
    action = value.get("action_record")
    if not isinstance(action, Mapping):
        raise Pass218DistributedClosureValidationError("P218_I18_ACTION_RECORD_REQUIRED")
    action_value = validate_operator_action(action)
    if action_value["record_hash72"] != value["action_record_hash72"]:
        raise Pass218DistributedClosureValidationError("P218_I18_ACTION_RECORD_HASH_MISMATCH")
    if action_value["action"] != value.get("action") or action_value["operator_id"] != value.get("operator_id"):
        raise Pass218DistributedClosureValidationError("P218_I18_ACTION_RECORD_BINDING_MISMATCH")
    for key in (
        "metadata_only",
        "successor_may_use_for_terminal_diagnostics_only",
    ):
        if value.get(key) is not True:
            raise Pass218DistributedClosureValidationError("P218_I18_ACTION_SOURCE_INVARIANT_" + key.upper())
    if value.get("grants_execution_authority") is not False or value.get("grants_retry_authority") is not False:
        raise Pass218DistributedClosureValidationError("P218_I18_ACTION_SOURCE_AUTHORITY_VIOLATION")
    _assert_exclusions(value)
    if supplied != hash72_digest({"domain": ACTION_SOURCE_SCHEMA}, value):
        raise Pass218DistributedClosureValidationError("P218_I18_ACTION_SOURCE_HASH_MISMATCH")
    return {**value, "record_hash72": supplied}


def seal_distributed_terminal_closure(
    *,
    claim: Mapping[str, Any],
    result: Mapping[str, Any],
    action_source: Mapping[str, Any],
    attestation: Mapping[str, Any],
    i13_run_receipt: Mapping[str, Any],
    reconciliation: Mapping[str, Any],
    ownership: Mapping[str, Any],
) -> dict[str, Any]:
    claim_value = validate_release_claim(claim)
    result_value = validate_external_result(result)
    source_value = validate_distributed_action_source(action_source)
    attestation_value = validate_execution_attestation(attestation)
    run_value = validate_maintenance_run_receipt(i13_run_receipt)
    reconciliation_value = validate_execution_reconciliation(reconciliation)
    owner = validate_distributed_ownership_record(ownership)

    if result_value["claim_record_hash72"] != claim_value["record_hash72"]:
        raise Pass218DistributedClosureValidationError("P218_I18_RESULT_CLAIM_MISMATCH")
    if source_value["action_record_hash72"] != claim_value["action_record_hash72"]:
        raise Pass218DistributedClosureValidationError("P218_I18_SOURCE_ACTION_MISMATCH")
    if attestation_value["claim_record_hash72"] != claim_value["record_hash72"]:
        raise Pass218DistributedClosureValidationError("P218_I18_ATTESTATION_CLAIM_MISMATCH")
    if attestation_value["external_result_hash72"] != result_value["external_result_hash72"]:
        raise Pass218DistributedClosureValidationError("P218_I18_ATTESTATION_RESULT_MISMATCH")
    if attestation_value["outcome"] != result_value["outcome"]:
        raise Pass218DistributedClosureValidationError("P218_I18_ATTESTATION_OUTCOME_MISMATCH")
    if bool(attestation_value["external_operation_executed"]) != bool(result_value["external_operation_executed"]):
        raise Pass218DistributedClosureValidationError("P218_I18_ATTESTATION_EXECUTION_FLAG_MISMATCH")
    if run_value["action_record_hash72"] != claim_value["action_record_hash72"]:
        raise Pass218DistributedClosureValidationError("P218_I18_RUN_ACTION_MISMATCH")
    if run_value["outcome"] != result_value["outcome"]:
        raise Pass218DistributedClosureValidationError("P218_I18_RUN_OUTCOME_MISMATCH")
    if reconciliation_value["claim_record_hash72"] != claim_value["record_hash72"]:
        raise Pass218DistributedClosureValidationError("P218_I18_RECONCILIATION_CLAIM_MISMATCH")
    if reconciliation_value["attestation_record_hash72"] != attestation_value["record_hash72"]:
        raise Pass218DistributedClosureValidationError("P218_I18_RECONCILIATION_ATTESTATION_MISMATCH")
    if reconciliation_value["i13_run_receipt_hash72"] != run_value["record_hash72"]:
        raise Pass218DistributedClosureValidationError("P218_I18_RECONCILIATION_RUN_MISMATCH")
    if owner["fence_epoch"] < result_value["result_recorded_fence_epoch"]:
        raise Pass218DistributedClosureValidationError("P218_I18_CLOSURE_FENCE_REGRESSION")

    return _seal(
        TERMINAL_CLOSURE_SCHEMA,
        {
            "schema": TERMINAL_CLOSURE_SCHEMA,
            "version": PASS218_DISTRIBUTED_CLOSURE_VERSION,
            "claim_record_hash72": claim_value["record_hash72"],
            "release_record_hash72": claim_value["release_record_hash72"],
            "action_record_hash72": claim_value["action_record_hash72"],
            "i17_result_record_hash72": result_value["record_hash72"],
            "i18_action_source_hash72": source_value["record_hash72"],
            "attestation_record_hash72": attestation_value["record_hash72"],
            "i13_run_receipt_hash72": run_value["record_hash72"],
            "reconciliation_record_hash72": reconciliation_value["record_hash72"],
            "closure_fence_epoch": owner["fence_epoch"],
            "closure_owner_id": owner["owner_id"],
            "closure_host_id": owner["host_id"],
            "closure_ownership_hash72": owner["ownership_hash72"],
            "outcome": result_value["outcome"],
            "external_operation_executed": bool(result_value["external_operation_executed"]),
            "attestation": _copy(attestation_value),
            "i13_run_receipt": _copy(run_value),
            "reconciliation": _copy(reconciliation_value),
            "distributed_closure_precedes_local_terminal_mirror": True,
            "terminal_closure_single_write": True,
            "successor_may_repair_local_evidence": True,
            "successor_may_redispatch": False,
            "retry_requires_new_prepared_action": True,
            **_exclusions(),
        },
    )


def validate_distributed_terminal_closure(record: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise Pass218DistributedClosureValidationError("P218_I18_CLOSURE_INVALID")
    value = _copy(record)
    supplied = _require_hash72(value.pop("record_hash72", None), "P218_I18_CLOSURE_HASH_INVALID")
    if value.get("schema") != TERMINAL_CLOSURE_SCHEMA or value.get("version") != PASS218_DISTRIBUTED_CLOSURE_VERSION:
        raise Pass218DistributedClosureValidationError("P218_I18_CLOSURE_SCHEMA_INVALID")
    for key in (
        "claim_record_hash72",
        "release_record_hash72",
        "action_record_hash72",
        "i17_result_record_hash72",
        "i18_action_source_hash72",
        "attestation_record_hash72",
        "i13_run_receipt_hash72",
        "reconciliation_record_hash72",
        "closure_ownership_hash72",
    ):
        _require_hash72(value.get(key), "P218_I18_CLOSURE_BINDING_HASH_INVALID")
    _require_positive_int(value.get("closure_fence_epoch"), "P218_I18_CLOSURE_FENCE_INVALID")
    attestation = validate_execution_attestation(value.get("attestation") or {})
    run = validate_maintenance_run_receipt(value.get("i13_run_receipt") or {})
    reconciliation = validate_execution_reconciliation(value.get("reconciliation") or {})
    if attestation["record_hash72"] != value["attestation_record_hash72"]:
        raise Pass218DistributedClosureValidationError("P218_I18_CLOSURE_ATTESTATION_HASH_MISMATCH")
    if run["record_hash72"] != value["i13_run_receipt_hash72"]:
        raise Pass218DistributedClosureValidationError("P218_I18_CLOSURE_RUN_HASH_MISMATCH")
    if reconciliation["record_hash72"] != value["reconciliation_record_hash72"]:
        raise Pass218DistributedClosureValidationError("P218_I18_CLOSURE_RECONCILIATION_HASH_MISMATCH")
    if reconciliation["attestation_record_hash72"] != attestation["record_hash72"] or reconciliation["i13_run_receipt_hash72"] != run["record_hash72"]:
        raise Pass218DistributedClosureValidationError("P218_I18_CLOSURE_CHAIN_MISMATCH")
    for key in (
        "distributed_closure_precedes_local_terminal_mirror",
        "terminal_closure_single_write",
        "successor_may_repair_local_evidence",
        "retry_requires_new_prepared_action",
    ):
        if value.get(key) is not True:
            raise Pass218DistributedClosureValidationError("P218_I18_CLOSURE_INVARIANT_" + key.upper())
    if value.get("successor_may_redispatch") is not False:
        raise Pass218DistributedClosureValidationError("P218_I18_REDISPATCH_FORBIDDEN")
    _assert_exclusions(value)
    if supplied != hash72_digest({"domain": TERMINAL_CLOSURE_SCHEMA}, value):
        raise Pass218DistributedClosureValidationError("P218_I18_CLOSURE_HASH_MISMATCH")
    return {**value, "record_hash72": supplied}


class Pass218DistributedClosureLedgerProtocol(Protocol):
    distributed: bool

    def current_ownership(self) -> dict[str, Any]: ...
    def ensure_action_source(self, action_record: Mapping[str, Any]) -> dict[str, Any]: ...
    def source_for_action(self, action_hash72: str) -> dict[str, Any] | None: ...
    def record_closure(
        self,
        *,
        claim: Mapping[str, Any],
        result: Mapping[str, Any],
        attestation: Mapping[str, Any],
        i13_run_receipt: Mapping[str, Any],
        reconciliation: Mapping[str, Any],
    ) -> dict[str, Any]: ...
    def closure_for_claim(self, claim_hash72: str) -> dict[str, Any] | None: ...
    def closures(self) -> list[dict[str, Any]]: ...
    def status(self) -> dict[str, Any]: ...


class Pass218EtcdDistributedClosureLedger:
    distributed = True

    def __init__(
        self,
        authority: Any,
        execution_ledger: Pass218DistributedExecutionLedgerProtocol,
        *,
        suffix: str = DEFAULT_CLOSURE_SUFFIX,
    ) -> None:
        if not hasattr(authority, "client") or not hasattr(authority, "namespace"):
            raise Pass218DistributedClosureValidationError("P218_I18_ETCD_AUTHORITY_REQUIRED")
        self.authority = authority
        self.client = authority.client
        self.execution_ledger = execution_ledger
        self.namespace = str(authority.namespace).rstrip("/") + "/" + suffix

    def _key(self, suffix: str) -> bytes:
        return (self.namespace + "/" + suffix).encode("utf-8")

    def source_key(self, action_hash72: str) -> bytes:
        return self._key("action-sources/" + _marker(_require_hash72(action_hash72, "P218_I18_ACTION_HASH_INVALID")))

    def closure_key(self, claim_hash72: str) -> bytes:
        return self._key("closures/" + _marker(_require_hash72(claim_hash72, "P218_I18_CLAIM_HASH_INVALID")))

    def current_ownership(self) -> dict[str, Any]:
        try:
            return validate_distributed_ownership_record(self.authority.assert_current())
        except Pass218DistributedOwnershipError as exc:
            raise Pass218DistributedClosureUnavailable(str(exc)) from exc

    def _read(self, key: bytes, validator: Any, code: str) -> dict[str, Any] | None:
        raw, _ = self.client.range_value(key)
        if raw is None:
            return None
        try:
            value = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise Pass218DistributedClosureValidationError(code + "_JSON_INVALID") from exc
        if not isinstance(value, Mapping) or _canonical_bytes(value) != raw:
            raise Pass218DistributedClosureValidationError(code + "_NONCANONICAL")
        return validator(value)

    def source_for_action(self, action_hash72: str) -> dict[str, Any] | None:
        return self._read(self.source_key(action_hash72), validate_distributed_action_source, "P218_I18_ACTION_SOURCE")

    def closure_for_claim(self, claim_hash72: str) -> dict[str, Any] | None:
        return self._read(self.closure_key(claim_hash72), validate_distributed_terminal_closure, "P218_I18_CLOSURE")

    def ensure_action_source(self, action_record: Mapping[str, Any]) -> dict[str, Any]:
        action = validate_operator_action(action_record)
        existing = self.source_for_action(action["record_hash72"])
        if existing is not None:
            if existing["action_record"]["record_hash72"] != action["record_hash72"]:
                raise Pass218DistributedClosureReplayRejected("P218_I18_ACTION_SOURCE_CONFLICT")
            return existing
        ownership = self.current_ownership()
        source = seal_distributed_action_source(action_record=action, ownership=ownership)
        key = self.source_key(action["record_hash72"])
        response = self.client.txn(
            compare=[
                self.client.compare_value(self.authority.owner_key, _canonical_bytes(ownership)),
                self.client.compare_value(self.authority.fence_key, str(ownership["fence_epoch"]).encode("ascii")),
                self.client.compare_version(key, 0),
            ],
            success=[self.client.put_operation(key, _canonical_bytes(source))],
        )
        if response.get("succeeded") is True:
            return _copy(source)
        existing = self.source_for_action(action["record_hash72"])
        if existing is not None and existing["action_record"]["record_hash72"] == action["record_hash72"]:
            return existing
        self.current_ownership()
        raise Pass218DistributedClosureUnavailable("P218_I18_ACTION_SOURCE_CAS_CONFLICT")

    def record_closure(
        self,
        *,
        claim: Mapping[str, Any],
        result: Mapping[str, Any],
        attestation: Mapping[str, Any],
        i13_run_receipt: Mapping[str, Any],
        reconciliation: Mapping[str, Any],
    ) -> dict[str, Any]:
        claim_value = validate_release_claim(claim)
        result_value = validate_external_result(result)
        stored_result = self.execution_ledger.result_for_claim(claim_value["record_hash72"])
        if stored_result is None or stored_result["record_hash72"] != result_value["record_hash72"]:
            raise Pass218DistributedClosureValidationError("P218_I18_DISTRIBUTED_I17_RESULT_REQUIRED")
        source = self.source_for_action(claim_value["action_record_hash72"])
        if source is None:
            raise Pass218DistributedClosureValidationError("P218_I18_DISTRIBUTED_ACTION_SOURCE_REQUIRED")
        existing = self.closure_for_claim(claim_value["record_hash72"])
        if existing is not None:
            return existing
        ownership = self.current_ownership()
        closure = seal_distributed_terminal_closure(
            claim=claim_value,
            result=result_value,
            action_source=source,
            attestation=attestation,
            i13_run_receipt=i13_run_receipt,
            reconciliation=reconciliation,
            ownership=ownership,
        )
        key = self.closure_key(claim_value["record_hash72"])
        response = self.client.txn(
            compare=[
                self.client.compare_value(self.authority.owner_key, _canonical_bytes(ownership)),
                self.client.compare_value(self.authority.fence_key, str(ownership["fence_epoch"]).encode("ascii")),
                self.client.compare_version(key, 0),
            ],
            success=[self.client.put_operation(key, _canonical_bytes(closure))],
        )
        if response.get("succeeded") is True:
            return _copy(closure)
        existing = self.closure_for_claim(claim_value["record_hash72"])
        if existing is not None:
            if existing["i17_result_record_hash72"] == result_value["record_hash72"]:
                return existing
            raise Pass218DistributedClosureReplayRejected("P218_I18_TERMINAL_CLOSURE_ALREADY_RECORDED")
        self.current_ownership()
        raise Pass218DistributedClosureUnavailable("P218_I18_CLOSURE_CAS_CONFLICT")

    def closures(self) -> list[dict[str, Any]]:
        values: list[dict[str, Any]] = []
        for dispatch in self.execution_ledger.dispatches():
            closure = self.closure_for_claim(dispatch["claim_record_hash72"])
            if closure is not None:
                values.append(closure)
        return values

    def status(self) -> dict[str, Any]:
        dispatches = self.execution_ledger.dispatches()
        result_count = sum(1 for item in dispatches if self.execution_ledger.result_for_claim(item["claim_record_hash72"]) is not None)
        closures = self.closures()
        return {
            "schema": DISTRIBUTED_CLOSURE_STATUS_SCHEMA,
            "version": PASS218_DISTRIBUTED_CLOSURE_VERSION,
            "distributed": True,
            "distributed_action_source_count": sum(1 for item in dispatches if self.source_for_action(item["action_record_hash72"]) is not None),
            "i17_terminal_result_count": result_count,
            "distributed_terminal_closure_count": len(closures),
            "terminal_result_pending_closure_count": max(0, result_count - len(closures)),
            "distributed_closure_precedes_local_terminal_mirror": True,
            "successor_may_repair_local_evidence": True,
            "successor_may_redispatch": False,
            **_exclusions(),
        }


class Pass218InMemoryDistributedClosureLedger:
    distributed = True

    def __init__(self, authority: Pass218InMemoryDistributedAuthority, execution_ledger: Pass218DistributedExecutionLedgerProtocol) -> None:
        self.authority = authority
        self.harness = authority.harness
        self.execution_ledger = execution_ledger

    def _state(self) -> dict[str, Any]:
        state = getattr(self.harness, "_pass218_i18_closure_state", None)
        if state is None:
            state = {"sources": {}, "closures": {}}
            setattr(self.harness, "_pass218_i18_closure_state", state)
        return state

    def current_ownership(self) -> dict[str, Any]:
        try:
            return validate_distributed_ownership_record(self.authority.assert_current())
        except Pass218DistributedOwnershipError as exc:
            raise Pass218DistributedClosureUnavailable(str(exc)) from exc

    def ensure_action_source(self, action_record: Mapping[str, Any]) -> dict[str, Any]:
        action = validate_operator_action(action_record)
        with self.harness._lock:
            state = self._state()
            existing = state["sources"].get(action["record_hash72"])
            if existing is not None:
                return validate_distributed_action_source(existing)
            source = seal_distributed_action_source(action_record=action, ownership=self.current_ownership())
            state["sources"][action["record_hash72"]] = _copy(source)
            return _copy(source)

    def source_for_action(self, action_hash72: str) -> dict[str, Any] | None:
        _require_hash72(action_hash72, "P218_I18_ACTION_HASH_INVALID")
        with self.harness._lock:
            value = self._state()["sources"].get(action_hash72)
            return None if value is None else validate_distributed_action_source(value)

    def closure_for_claim(self, claim_hash72: str) -> dict[str, Any] | None:
        _require_hash72(claim_hash72, "P218_I18_CLAIM_HASH_INVALID")
        with self.harness._lock:
            value = self._state()["closures"].get(claim_hash72)
            return None if value is None else validate_distributed_terminal_closure(value)

    def record_closure(
        self,
        *,
        claim: Mapping[str, Any],
        result: Mapping[str, Any],
        attestation: Mapping[str, Any],
        i13_run_receipt: Mapping[str, Any],
        reconciliation: Mapping[str, Any],
    ) -> dict[str, Any]:
        claim_value = validate_release_claim(claim)
        result_value = validate_external_result(result)
        with self.harness._lock:
            stored_result = self.execution_ledger.result_for_claim(claim_value["record_hash72"])
            if stored_result is None or stored_result["record_hash72"] != result_value["record_hash72"]:
                raise Pass218DistributedClosureValidationError("P218_I18_DISTRIBUTED_I17_RESULT_REQUIRED")
            source = self.source_for_action(claim_value["action_record_hash72"])
            if source is None:
                raise Pass218DistributedClosureValidationError("P218_I18_DISTRIBUTED_ACTION_SOURCE_REQUIRED")
            state = self._state()
            existing = state["closures"].get(claim_value["record_hash72"])
            if existing is not None:
                return validate_distributed_terminal_closure(existing)
            closure = seal_distributed_terminal_closure(
                claim=claim_value,
                result=result_value,
                action_source=source,
                attestation=attestation,
                i13_run_receipt=i13_run_receipt,
                reconciliation=reconciliation,
                ownership=self.current_ownership(),
            )
            state["closures"][claim_value["record_hash72"]] = _copy(closure)
            return _copy(closure)

    def closures(self) -> list[dict[str, Any]]:
        with self.harness._lock:
            return [validate_distributed_terminal_closure(value) for _, value in sorted(self._state()["closures"].items())]

    def status(self) -> dict[str, Any]:
        dispatches = self.execution_ledger.dispatches()
        result_count = sum(1 for item in dispatches if self.execution_ledger.result_for_claim(item["claim_record_hash72"]) is not None)
        closures = self.closures()
        return {
            "schema": DISTRIBUTED_CLOSURE_STATUS_SCHEMA,
            "version": PASS218_DISTRIBUTED_CLOSURE_VERSION,
            "distributed": True,
            "distributed_action_source_count": sum(1 for item in dispatches if self.source_for_action(item["action_record_hash72"]) is not None),
            "i17_terminal_result_count": result_count,
            "distributed_terminal_closure_count": len(closures),
            "terminal_result_pending_closure_count": max(0, result_count - len(closures)),
            "distributed_closure_precedes_local_terminal_mirror": True,
            "successor_may_repair_local_evidence": True,
            "successor_may_redispatch": False,
            **_exclusions(),
        }


class Pass218UnavailableDistributedClosureLedger:
    distributed = True

    @staticmethod
    def _raise() -> None:
        raise Pass218DistributedClosureUnavailable("P218_I18_DISTRIBUTED_CLOSURE_UNAVAILABLE")

    def current_ownership(self) -> dict[str, Any]: self._raise(); raise AssertionError
    def ensure_action_source(self, action_record: Mapping[str, Any]) -> dict[str, Any]: self._raise(); raise AssertionError
    def source_for_action(self, action_hash72: str) -> dict[str, Any] | None: self._raise(); raise AssertionError
    def record_closure(self, **kwargs: Any) -> dict[str, Any]: self._raise(); raise AssertionError
    def closure_for_claim(self, claim_hash72: str) -> dict[str, Any] | None: self._raise(); raise AssertionError
    def closures(self) -> list[dict[str, Any]]: self._raise(); raise AssertionError
    def status(self) -> dict[str, Any]: self._raise(); raise AssertionError


def build_distributed_closure_ledger(
    authority: Any,
    execution_ledger: Pass218DistributedExecutionLedgerProtocol,
) -> Pass218DistributedClosureLedgerProtocol:
    if isinstance(authority, Pass218InMemoryDistributedAuthority):
        return Pass218InMemoryDistributedClosureLedger(authority, execution_ledger)
    if hasattr(authority, "client") and hasattr(authority, "namespace") and hasattr(authority, "owner_key") and hasattr(authority, "fence_key"):
        return Pass218EtcdDistributedClosureLedger(authority, execution_ledger)
    return Pass218UnavailableDistributedClosureLedger()


__all__ = [
    "ACTION_SOURCE_SCHEMA",
    "DISTRIBUTED_CLOSURE_STATUS_SCHEMA",
    "PASS218_DISTRIBUTED_CLOSURE_VERSION",
    "TERMINAL_CLOSURE_SCHEMA",
    "Pass218DistributedClosureError",
    "Pass218DistributedClosureLedgerProtocol",
    "Pass218DistributedClosureReplayRejected",
    "Pass218DistributedClosureUnavailable",
    "Pass218DistributedClosureValidationError",
    "Pass218EtcdDistributedClosureLedger",
    "Pass218InMemoryDistributedClosureLedger",
    "Pass218UnavailableDistributedClosureLedger",
    "build_distributed_closure_ledger",
    "seal_distributed_action_source",
    "seal_distributed_terminal_closure",
    "validate_distributed_action_source",
    "validate_distributed_terminal_closure",
]

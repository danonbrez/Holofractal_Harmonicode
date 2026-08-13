"""Pass 218 Iteration 16 distributed maintenance-consumption ledger.

I15 proves one-time consumption on one durable host. I16 moves the anti-replay
fact into the already-authoritative I10/I11 distributed fence substrate. The
linearizable transaction writes an immutable release marker, immutable prepared-
action marker, and ordered ledger entry before the local I15 journal is mirrored.
A replacement authority host can therefore reconstruct the exact I15 claim after
machine loss without reopening the release or prepared action.

I16 does not acquire canonical authority, mutate the canonical target, execute
maintenance, mint action authority, or change I12-I15 approval semantics.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
from typing import Any, Mapping, Protocol

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.commit_boundary import _canonical_bytes
from hhs_runtime.pass218.distributed_ownership import (
    Pass218DistributedOwnershipError,
    Pass218InMemoryDistributedAuthority,
    validate_distributed_ownership_record,
)
from hhs_runtime.pass218.execution_i15 import (
    ACTION_CLAIM_INDEX_SCHEMA,
    Pass218ReleaseConsumptionJournal,
    validate_release_claim,
)

PASS218_DISTRIBUTED_CONSUMPTION_VERSION = "HHS-P218-DISTRIBUTED-CONSUMPTION-I16-V1"
DISTRIBUTED_CONSUMPTION_ENTRY_SCHEMA = "HHS-P218-I16-DISTRIBUTED-CONSUMPTION-ENTRY-V1"
DISTRIBUTED_CONSUMPTION_STATUS_SCHEMA = "HHS-P218-I16-DISTRIBUTED-CONSUMPTION-STATUS-V1"
DEFAULT_CONSUMPTION_SUFFIX = "consumption-i16"
DEFAULT_CONSUMPTION_CAS_ATTEMPTS = 8


class Pass218DistributedConsumptionError(RuntimeError):
    pass


class Pass218DistributedConsumptionValidationError(Pass218DistributedConsumptionError):
    pass


class Pass218DistributedConsumptionReplayRejected(Pass218DistributedConsumptionError):
    pass


class Pass218DistributedConsumptionConflict(Pass218DistributedConsumptionError):
    pass


class Pass218DistributedConsumptionUnavailable(Pass218DistributedConsumptionError):
    pass


def _copy(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, separators=(",", ":")))


def _require_positive_int(value: Any, code: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise Pass218DistributedConsumptionValidationError(code)
    return value


def _require_hash72(value: Any, code: str) -> str:
    if not isinstance(value, str) or len(value) != 72 or not validate_hash72(value):
        raise Pass218DistributedConsumptionValidationError(code)
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
            raise Pass218DistributedConsumptionValidationError(
                "P218_I16_EXCLUSION_VIOLATION_" + key.upper()
            )


def _decode_canonical_record(raw: bytes, code: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise Pass218DistributedConsumptionValidationError(code + "_JSON_INVALID") from exc
    if not isinstance(value, dict) or _canonical_bytes(value) != raw:
        raise Pass218DistributedConsumptionValidationError(code + "_NONCANONICAL")
    return value


def _marker_key(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def seal_distributed_consumption_entry(
    *,
    claim: Mapping[str, Any],
    ownership: Mapping[str, Any],
    ledger_sequence: int,
) -> dict[str, Any]:
    claim_value = validate_release_claim(claim)
    owner = validate_distributed_ownership_record(ownership)
    sequence = _require_positive_int(ledger_sequence, "P218_I16_LEDGER_SEQUENCE_INVALID")
    if claim_value["distributed_fence_epoch"] != owner["fence_epoch"]:
        raise Pass218DistributedConsumptionValidationError(
            "P218_I16_CLAIM_FENCE_NOT_CURRENT"
        )
    body = {
        "schema": DISTRIBUTED_CONSUMPTION_ENTRY_SCHEMA,
        "version": PASS218_DISTRIBUTED_CONSUMPTION_VERSION,
        "ledger_sequence": sequence,
        "release_record_hash72": claim_value["release_record_hash72"],
        "action_record_hash72": claim_value["action_record_hash72"],
        "claim_record_hash72": claim_value["record_hash72"],
        "attempt_id": claim_value["attempt_id"],
        "action": claim_value["action"],
        "executor_operator_id": claim_value["executor_operator_id"],
        "release_fence_epoch": claim_value["distributed_fence_epoch"],
        "consumed_under_fence_epoch": owner["fence_epoch"],
        "consumed_by_owner_id": owner["owner_id"],
        "consumed_by_host_id": owner["host_id"],
        "ownership_hash72": owner["ownership_hash72"],
        "claim": _copy(claim_value),
        "ownership": _copy(owner),
        "distributed_first": True,
        "immutable_release_marker": True,
        "immutable_action_marker": True,
        "release_permanently_consumed": True,
        "action_permanently_consumed": True,
        "failover_reconstructable": True,
        "local_journal_is_recoverable_mirror": True,
        "retry_requires_new_prepared_action": True,
        **_exclusions(),
    }
    return {
        **body,
        "record_hash72": hash72_digest(
            {"domain": DISTRIBUTED_CONSUMPTION_ENTRY_SCHEMA}, body
        ),
    }


def validate_distributed_consumption_entry(record: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise Pass218DistributedConsumptionValidationError("P218_I16_ENTRY_INVALID")
    value = _copy(record)
    supplied = _require_hash72(
        value.pop("record_hash72", None), "P218_I16_ENTRY_HASH72_INVALID"
    )
    if value.get("schema") != DISTRIBUTED_CONSUMPTION_ENTRY_SCHEMA:
        raise Pass218DistributedConsumptionValidationError("P218_I16_ENTRY_SCHEMA_INVALID")
    if value.get("version") != PASS218_DISTRIBUTED_CONSUMPTION_VERSION:
        raise Pass218DistributedConsumptionValidationError("P218_I16_ENTRY_VERSION_INVALID")
    _require_positive_int(value.get("ledger_sequence"), "P218_I16_LEDGER_SEQUENCE_INVALID")
    claim = validate_release_claim(value.get("claim", {}))
    owner = validate_distributed_ownership_record(value.get("ownership", {}))
    for key in ("release_record_hash72", "action_record_hash72", "claim_record_hash72", "ownership_hash72"):
        _require_hash72(value.get(key), "P218_I16_ENTRY_HASH_FIELD_INVALID")
    if value["release_record_hash72"] != claim["release_record_hash72"]:
        raise Pass218DistributedConsumptionValidationError("P218_I16_RELEASE_BINDING_MISMATCH")
    if value["action_record_hash72"] != claim["action_record_hash72"]:
        raise Pass218DistributedConsumptionValidationError("P218_I16_ACTION_BINDING_MISMATCH")
    if value["claim_record_hash72"] != claim["record_hash72"]:
        raise Pass218DistributedConsumptionValidationError("P218_I16_CLAIM_BINDING_MISMATCH")
    if value["ownership_hash72"] != owner["ownership_hash72"]:
        raise Pass218DistributedConsumptionValidationError("P218_I16_OWNERSHIP_BINDING_MISMATCH")
    if value.get("release_fence_epoch") != claim["distributed_fence_epoch"]:
        raise Pass218DistributedConsumptionValidationError("P218_I16_RELEASE_FENCE_MISMATCH")
    if value.get("consumed_under_fence_epoch") != owner["fence_epoch"]:
        raise Pass218DistributedConsumptionValidationError("P218_I16_OWNER_FENCE_MISMATCH")
    if claim["distributed_fence_epoch"] != owner["fence_epoch"]:
        raise Pass218DistributedConsumptionValidationError("P218_I16_CLAIM_OWNER_FENCE_MISMATCH")
    if value.get("consumed_by_owner_id") != owner["owner_id"] or value.get("consumed_by_host_id") != owner["host_id"]:
        raise Pass218DistributedConsumptionValidationError("P218_I16_OWNER_IDENTITY_MISMATCH")
    for key in (
        "distributed_first",
        "immutable_release_marker",
        "immutable_action_marker",
        "release_permanently_consumed",
        "action_permanently_consumed",
        "failover_reconstructable",
        "local_journal_is_recoverable_mirror",
        "retry_requires_new_prepared_action",
    ):
        if value.get(key) is not True:
            raise Pass218DistributedConsumptionValidationError(
                "P218_I16_ENTRY_INVARIANT_" + key.upper()
            )
    _assert_exclusions(value)
    expected = hash72_digest({"domain": DISTRIBUTED_CONSUMPTION_ENTRY_SCHEMA}, value)
    if supplied != expected:
        raise Pass218DistributedConsumptionValidationError("P218_I16_ENTRY_HASH72_MISMATCH")
    return {**value, "record_hash72": supplied}


class Pass218DistributedConsumptionLedgerProtocol(Protocol):
    distributed: bool

    def current_ownership(self) -> dict[str, Any]: ...
    def consume_claim(self, claim: Mapping[str, Any]) -> dict[str, Any]: ...
    def entry_for_release(self, release_hash72: str) -> dict[str, Any] | None: ...
    def entry_for_action(self, action_hash72: str) -> dict[str, Any] | None: ...
    def entries(self) -> list[dict[str, Any]]: ...
    def status(self) -> dict[str, Any]: ...


class Pass218EtcdDistributedConsumptionLedger:
    """Immutable anti-replay markers committed through the active I10/I11 fence."""

    distributed = True

    def __init__(
        self,
        authority: Any,
        *,
        suffix: str = DEFAULT_CONSUMPTION_SUFFIX,
        cas_attempts: int = DEFAULT_CONSUMPTION_CAS_ATTEMPTS,
    ) -> None:
        if not hasattr(authority, "client") or not hasattr(authority, "namespace"):
            raise Pass218DistributedConsumptionValidationError(
                "P218_I16_ETCD_AUTHORITY_REQUIRED"
            )
        if not isinstance(suffix, str) or not suffix or "/" in suffix or any(c.isspace() for c in suffix):
            raise Pass218DistributedConsumptionValidationError("P218_I16_SUFFIX_INVALID")
        self.authority = authority
        self.client = authority.client
        self.namespace = str(authority.namespace).rstrip("/") + "/" + suffix
        self.cas_attempts = _require_positive_int(cas_attempts, "P218_I16_CAS_ATTEMPTS_INVALID")

    def _key(self, suffix: str) -> bytes:
        return (self.namespace + "/" + suffix).encode("utf-8")

    @property
    def head_key(self) -> bytes:
        return self._key("head")

    def release_key(self, release_hash72: str) -> bytes:
        return self._key("releases/" + _marker_key(_require_hash72(release_hash72, "P218_I16_RELEASE_HASH_INVALID")))

    def action_key(self, action_hash72: str) -> bytes:
        return self._key("actions/" + _marker_key(_require_hash72(action_hash72, "P218_I16_ACTION_HASH_INVALID")))

    def entry_key(self, sequence: int) -> bytes:
        sequence = _require_positive_int(sequence, "P218_I16_LEDGER_SEQUENCE_INVALID")
        return self._key("entries/" + f"{sequence:020d}")

    def current_ownership(self) -> dict[str, Any]:
        try:
            return validate_distributed_ownership_record(self.authority.assert_current())
        except Pass218DistributedOwnershipError as exc:
            raise Pass218DistributedConsumptionUnavailable(str(exc)) from exc

    def _read_entry_key(self, key: bytes) -> dict[str, Any] | None:
        try:
            raw, _ = self.client.range_value(key)
        except Pass218DistributedOwnershipError as exc:
            raise Pass218DistributedConsumptionUnavailable(str(exc)) from exc
        if raw is None:
            return None
        return validate_distributed_consumption_entry(
            _decode_canonical_record(raw, "P218_I16_DISTRIBUTED_ENTRY")
        )

    def _read_head(self) -> tuple[int, bytes | None]:
        try:
            raw, _ = self.client.range_value(self.head_key)
        except Pass218DistributedOwnershipError as exc:
            raise Pass218DistributedConsumptionUnavailable(str(exc)) from exc
        if raw is None:
            return 0, None
        try:
            value = int(raw.decode("ascii"))
        except Exception as exc:
            raise Pass218DistributedConsumptionValidationError("P218_I16_HEAD_INVALID") from exc
        _require_positive_int(value, "P218_I16_HEAD_INVALID")
        if str(value).encode("ascii") != raw:
            raise Pass218DistributedConsumptionValidationError("P218_I16_HEAD_NONCANONICAL")
        return value, raw

    def entry_for_release(self, release_hash72: str) -> dict[str, Any] | None:
        return self._read_entry_key(self.release_key(release_hash72))

    def entry_for_action(self, action_hash72: str) -> dict[str, Any] | None:
        return self._read_entry_key(self.action_key(action_hash72))

    def consume_claim(self, claim: Mapping[str, Any]) -> dict[str, Any]:
        claim_value = validate_release_claim(claim)
        for _ in range(self.cas_attempts):
            ownership = self.current_ownership()
            if claim_value["distributed_fence_epoch"] != ownership["fence_epoch"]:
                raise Pass218DistributedConsumptionValidationError(
                    "P218_I16_CLAIM_FENCE_NOT_CURRENT"
                )
            if self.entry_for_release(claim_value["release_record_hash72"]) is not None:
                raise Pass218DistributedConsumptionReplayRejected(
                    "P218_I16_RELEASE_ALREADY_CONSUMED_DISTRIBUTED"
                )
            if self.entry_for_action(claim_value["action_record_hash72"]) is not None:
                raise Pass218DistributedConsumptionReplayRejected(
                    "P218_I16_ACTION_ALREADY_CONSUMED_DISTRIBUTED"
                )
            head, head_raw = self._read_head()
            sequence = head + 1
            entry = seal_distributed_consumption_entry(
                claim=claim_value,
                ownership=ownership,
                ledger_sequence=sequence,
            )
            entry_bytes = _canonical_bytes(entry)
            owner_bytes = _canonical_bytes(ownership)
            fence_bytes = str(ownership["fence_epoch"]).encode("ascii")
            release_key = self.release_key(claim_value["release_record_hash72"])
            action_key = self.action_key(claim_value["action_record_hash72"])
            ledger_key = self.entry_key(sequence)
            compare = [
                self.client.compare_value(self.authority.owner_key, owner_bytes),
                self.client.compare_value(self.authority.fence_key, fence_bytes),
                self.client.compare_version(release_key, 0),
                self.client.compare_version(action_key, 0),
                self.client.compare_version(ledger_key, 0),
            ]
            if head_raw is None:
                compare.append(self.client.compare_version(self.head_key, 0))
            else:
                compare.append(self.client.compare_value(self.head_key, head_raw))
            try:
                response = self.client.txn(
                    compare=compare,
                    success=[
                        self.client.put_operation(self.head_key, str(sequence).encode("ascii")),
                        self.client.put_operation(ledger_key, entry_bytes),
                        self.client.put_operation(release_key, entry_bytes),
                        self.client.put_operation(action_key, entry_bytes),
                    ],
                )
            except Pass218DistributedOwnershipError as exc:
                raise Pass218DistributedConsumptionUnavailable(str(exc)) from exc
            if response.get("succeeded") is True:
                return _copy(entry)
            self.current_ownership()
            if self.entry_for_release(claim_value["release_record_hash72"]) is not None:
                raise Pass218DistributedConsumptionReplayRejected(
                    "P218_I16_RELEASE_ALREADY_CONSUMED_DISTRIBUTED"
                )
            if self.entry_for_action(claim_value["action_record_hash72"]) is not None:
                raise Pass218DistributedConsumptionReplayRejected(
                    "P218_I16_ACTION_ALREADY_CONSUMED_DISTRIBUTED"
                )
        raise Pass218DistributedConsumptionConflict("P218_I16_LEDGER_CAS_CONFLICT")

    def entries(self) -> list[dict[str, Any]]:
        head, _ = self._read_head()
        result: list[dict[str, Any]] = []
        for sequence in range(1, head + 1):
            entry = self._read_entry_key(self.entry_key(sequence))
            if entry is None or entry["ledger_sequence"] != sequence:
                raise Pass218DistributedConsumptionValidationError(
                    "P218_I16_LEDGER_SEQUENCE_GAP"
                )
            result.append(entry)
        return result

    def status(self) -> dict[str, Any]:
        entries = self.entries()
        return {
            "schema": DISTRIBUTED_CONSUMPTION_STATUS_SCHEMA,
            "version": PASS218_DISTRIBUTED_CONSUMPTION_VERSION,
            "distributed": True,
            "ledger_entry_count": len(entries),
            "consumed_release_count": len(entries),
            "consumed_action_count": len(entries),
            "immutable_release_markers": True,
            "immutable_action_markers": True,
            "ordered_append_only_entries": True,
            "distributed_first": True,
            "failover_reconstructable": True,
            **_exclusions(),
        }


class Pass218InMemoryDistributedConsumptionLedger:
    """Deterministic I10-fence-aware reference ledger used by tests."""

    distributed = True

    def __init__(self, authority: Pass218InMemoryDistributedAuthority) -> None:
        self.authority = authority
        self.harness = authority.harness

    def _state(self) -> dict[str, Any]:
        state = getattr(self.harness, "_pass218_i16_consumption_state", None)
        if state is None:
            state = {"head": 0, "entries": {}, "releases": {}, "actions": {}}
            setattr(self.harness, "_pass218_i16_consumption_state", state)
        return state

    def current_ownership(self) -> dict[str, Any]:
        try:
            return validate_distributed_ownership_record(self.authority.assert_current())
        except Pass218DistributedOwnershipError as exc:
            raise Pass218DistributedConsumptionUnavailable(str(exc)) from exc

    def consume_claim(self, claim: Mapping[str, Any]) -> dict[str, Any]:
        claim_value = validate_release_claim(claim)
        with self.harness._lock:
            ownership = self.current_ownership()
            if claim_value["distributed_fence_epoch"] != ownership["fence_epoch"]:
                raise Pass218DistributedConsumptionValidationError(
                    "P218_I16_CLAIM_FENCE_NOT_CURRENT"
                )
            state = self._state()
            release_hash = claim_value["release_record_hash72"]
            action_hash = claim_value["action_record_hash72"]
            if release_hash in state["releases"]:
                raise Pass218DistributedConsumptionReplayRejected(
                    "P218_I16_RELEASE_ALREADY_CONSUMED_DISTRIBUTED"
                )
            if action_hash in state["actions"]:
                raise Pass218DistributedConsumptionReplayRejected(
                    "P218_I16_ACTION_ALREADY_CONSUMED_DISTRIBUTED"
                )
            sequence = int(state["head"]) + 1
            entry = seal_distributed_consumption_entry(
                claim=claim_value, ownership=ownership, ledger_sequence=sequence
            )
            state["head"] = sequence
            state["entries"][sequence] = _copy(entry)
            state["releases"][release_hash] = _copy(entry)
            state["actions"][action_hash] = _copy(entry)
            return _copy(entry)

    def entry_for_release(self, release_hash72: str) -> dict[str, Any] | None:
        _require_hash72(release_hash72, "P218_I16_RELEASE_HASH_INVALID")
        with self.harness._lock:
            value = self._state()["releases"].get(release_hash72)
            return None if value is None else validate_distributed_consumption_entry(value)

    def entry_for_action(self, action_hash72: str) -> dict[str, Any] | None:
        _require_hash72(action_hash72, "P218_I16_ACTION_HASH_INVALID")
        with self.harness._lock:
            value = self._state()["actions"].get(action_hash72)
            return None if value is None else validate_distributed_consumption_entry(value)

    def entries(self) -> list[dict[str, Any]]:
        with self.harness._lock:
            state = self._state()
            return [
                validate_distributed_consumption_entry(state["entries"][sequence])
                for sequence in range(1, int(state["head"]) + 1)
            ]

    def status(self) -> dict[str, Any]:
        entries = self.entries()
        return {
            "schema": DISTRIBUTED_CONSUMPTION_STATUS_SCHEMA,
            "version": PASS218_DISTRIBUTED_CONSUMPTION_VERSION,
            "distributed": True,
            "ledger_entry_count": len(entries),
            "consumed_release_count": len(entries),
            "consumed_action_count": len(entries),
            "immutable_release_markers": True,
            "immutable_action_markers": True,
            "ordered_append_only_entries": True,
            "distributed_first": True,
            "failover_reconstructable": True,
            **_exclusions(),
        }


class Pass218UnavailableDistributedConsumptionLedger:
    distributed = True

    @staticmethod
    def _raise() -> None:
        raise Pass218DistributedConsumptionUnavailable(
            "P218_I16_DISTRIBUTED_CONSUMPTION_UNAVAILABLE"
        )

    def current_ownership(self) -> dict[str, Any]:
        self._raise()
        raise AssertionError

    def consume_claim(self, claim: Mapping[str, Any]) -> dict[str, Any]:
        self._raise()
        raise AssertionError

    def entry_for_release(self, release_hash72: str) -> dict[str, Any] | None:
        self._raise()
        raise AssertionError

    def entry_for_action(self, action_hash72: str) -> dict[str, Any] | None:
        self._raise()
        raise AssertionError

    def entries(self) -> list[dict[str, Any]]:
        self._raise()
        raise AssertionError

    def status(self) -> dict[str, Any]:
        self._raise()
        raise AssertionError


def build_distributed_consumption_ledger(authority: Any) -> Pass218DistributedConsumptionLedgerProtocol:
    if isinstance(authority, Pass218InMemoryDistributedAuthority):
        return Pass218InMemoryDistributedConsumptionLedger(authority)
    if hasattr(authority, "client") and hasattr(authority, "namespace") and hasattr(authority, "owner_key") and hasattr(authority, "fence_key"):
        return Pass218EtcdDistributedConsumptionLedger(authority)
    return Pass218UnavailableDistributedConsumptionLedger()


def mirror_distributed_claim_to_local(
    journal: Pass218ReleaseConsumptionJournal,
    claim: Mapping[str, Any],
) -> bool:
    """Materialize an exact distributed claim into the recoverable I15 mirror."""
    value = validate_release_claim(claim)
    release_hash = value["release_record_hash72"]
    action_hash = value["action_record_hash72"]
    created = False
    expected_index = {
        "schema": ACTION_CLAIM_INDEX_SCHEMA,
        "action_record_hash72": action_hash,
        "release_record_hash72": release_hash,
        "claim_record_hash72": value["record_hash72"],
    }
    with journal.lock_path.open("r+") as lock_handle:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        claim_path = journal._claim_path(release_hash)
        action_path = journal._action_path(action_hash)
        existing_claim = journal._read(claim_path)
        if existing_claim is None:
            journal._atomic_create(claim_path, value)
            created = True
        elif validate_release_claim(existing_claim)["record_hash72"] != value["record_hash72"]:
            raise Pass218DistributedConsumptionValidationError(
                "P218_I16_LOCAL_RELEASE_CLAIM_CONFLICT"
            )
        existing_index = journal._read(action_path)
        if existing_index is None:
            journal._atomic_create(action_path, expected_index)
        elif existing_index != expected_index:
            raise Pass218DistributedConsumptionValidationError(
                "P218_I16_LOCAL_ACTION_INDEX_CONFLICT"
            )
    return created


def synchronize_distributed_claims_to_local(
    journal: Pass218ReleaseConsumptionJournal,
    ledger: Pass218DistributedConsumptionLedgerProtocol,
) -> int:
    mirrored = 0
    for entry in ledger.entries():
        if mirror_distributed_claim_to_local(journal, entry["claim"]):
            mirrored += 1
    return mirrored


def migrate_current_fence_local_claims(
    journal: Pass218ReleaseConsumptionJournal,
    ledger: Pass218DistributedConsumptionLedgerProtocol,
) -> dict[str, int]:
    """Promote only same-fence pre-I16 local claims; stale ambiguity fails closed."""
    ownership = ledger.current_ownership()
    migrated = 0
    stale = 0
    already_distributed = 0
    for path in sorted(journal.claims.glob("*.json")):
        raw = journal._read(path)
        if raw is None:
            continue
        claim = validate_release_claim(raw)
        remote = ledger.entry_for_release(claim["release_record_hash72"])
        if remote is not None:
            if remote["claim_record_hash72"] != claim["record_hash72"]:
                raise Pass218DistributedConsumptionValidationError(
                    "P218_I16_LOCAL_REMOTE_CLAIM_MISMATCH"
                )
            already_distributed += 1
            continue
        action_remote = ledger.entry_for_action(claim["action_record_hash72"])
        if action_remote is not None:
            raise Pass218DistributedConsumptionValidationError(
                "P218_I16_LOCAL_ACTION_REMOTE_CONFLICT"
            )
        if claim["distributed_fence_epoch"] != ownership["fence_epoch"]:
            stale += 1
            continue
        ledger.consume_claim(claim)
        migrated += 1
    return {
        "migrated_local_claim_count": migrated,
        "stale_unreplicated_local_claim_count": stale,
        "already_distributed_local_claim_count": already_distributed,
    }


__all__ = [
    "DISTRIBUTED_CONSUMPTION_ENTRY_SCHEMA",
    "DISTRIBUTED_CONSUMPTION_STATUS_SCHEMA",
    "PASS218_DISTRIBUTED_CONSUMPTION_VERSION",
    "Pass218DistributedConsumptionConflict",
    "Pass218DistributedConsumptionError",
    "Pass218DistributedConsumptionLedgerProtocol",
    "Pass218DistributedConsumptionReplayRejected",
    "Pass218DistributedConsumptionUnavailable",
    "Pass218DistributedConsumptionValidationError",
    "Pass218EtcdDistributedConsumptionLedger",
    "Pass218InMemoryDistributedConsumptionLedger",
    "Pass218UnavailableDistributedConsumptionLedger",
    "build_distributed_consumption_ledger",
    "migrate_current_fence_local_claims",
    "mirror_distributed_claim_to_local",
    "seal_distributed_consumption_entry",
    "synchronize_distributed_claims_to_local",
    "validate_distributed_consumption_entry",
]

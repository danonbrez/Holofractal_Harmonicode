"""Pass 213 iteration 5: persistent compiled-ROM inventory and recovery."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import hmac
import json
from pathlib import Path
import sqlite3
import time
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    CONTRACT, ZERO_HASH216, canonical_bytes, hash216,
)
from hhs_backend.runtime.hhs_pass213_native_protected_rom_v1 import (
    NativeProtectedCompiledROMStore, ProtectedCompiledROMRecord,
)
from hhs_backend.runtime.hhs_pass213_recovery_admission_v1 import (
    CompiledROMCarrier, inspect_and_correct_carrier, protect_compiled_rom_entry,
)
from hhs_backend.runtime.hhs_pass213_secure_memory_v1 import SecureMemoryReceipt

ITERATION = 5
RUNTIME_CLASSIFICATION = "HHS_PASS_213_PERSISTENT_INVENTORY_TOMBSTONE_RECOVERY_ITERATION5"
_LIVE = "LIVE"
_TOMBSTONED = "TOMBSTONED"
_EVENTS = {"ADMIT", "RECOVER", "TOMBSTONE"}


class Pass213PersistentInventoryError(RuntimeError):
    pass


def _key(value: bytes, code: str) -> bytes:
    if not isinstance(value, bytes) or len(value) < 32:
        raise Pass213PersistentInventoryError(code)
    return value


def _hash(value: str, code: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise Pass213PersistentInventoryError(code)
    try:
        int(value, 16)
    except ValueError as exc:
        raise Pass213PersistentInventoryError(code) from exc
    return value


def _tag(key: bytes, domain: str, payload: Mapping[str, Any]) -> str:
    framed = (
        b"HHS-P213-INVENTORY-HMAC-V1\0"
        + len(domain.encode()).to_bytes(2, "big")
        + domain.encode()
        + canonical_bytes(payload)
    )
    return hmac.new(key, framed, sha256).hexdigest()


@dataclass(frozen=True)
class DeletionAuthorization:
    entry_hash216: str
    authority_id: str
    reason: str
    timestamp_ns: int
    nonce: str
    bound_inventory_root_hash216: str
    authorization_root_hash216: str
    authentication_tag: str

    def unsigned(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_213_DELETION_AUTHORIZATION_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "entry_hash216": self.entry_hash216,
            "authority_id": self.authority_id,
            "reason": self.reason,
            "timestamp_ns": self.timestamp_ns,
            "nonce": self.nonce,
            "bound_inventory_root_hash216": self.bound_inventory_root_hash216,
        }

    def to_mapping(self) -> dict[str, Any]:
        return {
            **self.unsigned(),
            "authorization_root_hash216": self.authorization_root_hash216,
            "authentication_tag": self.authentication_tag,
        }

    @classmethod
    def create(
        cls, *, entry_hash216: str, authority_id: str, reason: str,
        timestamp_ns: int, nonce: str, bound_inventory_root_hash216: str,
        deletion_key: bytes,
    ) -> "DeletionAuthorization":
        _key(deletion_key, "PASS213_DELETION_KEY_TOO_SHORT")
        if not authority_id or not reason or not nonce or int(timestamp_ns) < 0:
            raise Pass213PersistentInventoryError("PASS213_DELETION_AUTHORIZATION_FIELDS_INVALID")
        _hash(entry_hash216, "PASS213_DELETION_ENTRY_HASH_INVALID")
        _hash(bound_inventory_root_hash216, "PASS213_DELETION_BOUND_ROOT_INVALID")
        temporary = cls(
            entry_hash216, authority_id, reason, int(timestamp_ns), nonce,
            bound_inventory_root_hash216, "", "",
        )
        root = hash216("persistent-deletion-authorization", canonical_bytes(temporary.unsigned()))
        rooted = {**temporary.unsigned(), "authorization_root_hash216": root}
        return cls(
            entry_hash216, authority_id, reason, int(timestamp_ns), nonce,
            bound_inventory_root_hash216, root,
            _tag(deletion_key, "DELETION-AUTHORIZATION", rooted),
        )

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "DeletionAuthorization":
        if value.get("schema") != "HHS_PASS_213_DELETION_AUTHORIZATION_V1":
            raise Pass213PersistentInventoryError("PASS213_DELETION_AUTHORIZATION_SCHEMA_INVALID")
        return cls(
            str(value["entry_hash216"]), str(value["authority_id"]),
            str(value["reason"]), int(value["timestamp_ns"]), str(value["nonce"]),
            str(value["bound_inventory_root_hash216"]),
            str(value["authorization_root_hash216"]),
            str(value["authentication_tag"]),
        )

    def validate(self, deletion_key: bytes) -> None:
        expected = DeletionAuthorization.create(
            entry_hash216=self.entry_hash216,
            authority_id=self.authority_id,
            reason=self.reason,
            timestamp_ns=self.timestamp_ns,
            nonce=self.nonce,
            bound_inventory_root_hash216=self.bound_inventory_root_hash216,
            deletion_key=deletion_key,
        )
        if canonical_bytes(self.to_mapping()) != canonical_bytes(expected.to_mapping()):
            raise Pass213PersistentInventoryError("PASS213_DELETION_AUTHORIZATION_INVALID")


@dataclass(frozen=True)
class InventoryCheckpoint:
    checkpoint_sequence: int
    genesis_epoch: int
    created_timestamp_ns: int
    authority_id: str
    label: str
    prior_checkpoint_root_hash216: str
    event_chain_head_hash216: str
    inventory_root_hash216: str
    live_entries: tuple[Mapping[str, Any], ...]
    tombstones: tuple[Mapping[str, Any], ...]
    checkpoint_root_hash216: str
    authentication_tag: str

    def unsigned(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_213_INVENTORY_CHECKPOINT_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "checkpoint_sequence": self.checkpoint_sequence,
            "genesis_epoch": self.genesis_epoch,
            "created_timestamp_ns": self.created_timestamp_ns,
            "authority_id": self.authority_id,
            "label": self.label,
            "prior_checkpoint_root_hash216": self.prior_checkpoint_root_hash216,
            "event_chain_head_hash216": self.event_chain_head_hash216,
            "inventory_root_hash216": self.inventory_root_hash216,
            "live_entries": list(self.live_entries),
            "tombstones": list(self.tombstones),
        }

    def to_mapping(self) -> dict[str, Any]:
        return {
            **self.unsigned(),
            "checkpoint_root_hash216": self.checkpoint_root_hash216,
            "authentication_tag": self.authentication_tag,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "InventoryCheckpoint":
        if value.get("schema") != "HHS_PASS_213_INVENTORY_CHECKPOINT_V1":
            raise Pass213PersistentInventoryError("PASS213_CHECKPOINT_SCHEMA_INVALID")
        return cls(
            int(value["checkpoint_sequence"]), int(value["genesis_epoch"]),
            int(value["created_timestamp_ns"]), str(value["authority_id"]),
            str(value["label"]), str(value["prior_checkpoint_root_hash216"]),
            str(value["event_chain_head_hash216"]),
            str(value["inventory_root_hash216"]),
            tuple(dict(item) for item in value["live_entries"]),
            tuple(dict(item) for item in value["tombstones"]),
            str(value["checkpoint_root_hash216"]),
            str(value["authentication_tag"]),
        )

    def validate(self, inventory_key: bytes) -> None:
        for value in (
            self.prior_checkpoint_root_hash216,
            self.event_chain_head_hash216,
            self.inventory_root_hash216,
            self.checkpoint_root_hash216,
        ):
            _hash(value, "PASS213_CHECKPOINT_HASH_INVALID")
        if self.checkpoint_sequence < 0 or self.genesis_epoch < 0:
            raise Pass213PersistentInventoryError("PASS213_CHECKPOINT_SEQUENCE_INVALID")
        live = [str(item["entry_hash216"]) for item in self.live_entries]
        tomb = [str(item["entry_hash216"]) for item in self.tombstones]
        if len(live) != len(set(live)) or len(tomb) != len(set(tomb)) or set(live) & set(tomb):
            raise Pass213PersistentInventoryError("PASS213_CHECKPOINT_ENTRY_SET_INVALID")
        expected_root = hash216("persistent-inventory-checkpoint", canonical_bytes(self.unsigned()))
        rooted = {**self.unsigned(), "checkpoint_root_hash216": expected_root}
        if (
            not hmac.compare_digest(self.checkpoint_root_hash216, expected_root)
            or not hmac.compare_digest(
                self.authentication_tag,
                _tag(inventory_key, "INVENTORY-CHECKPOINT", rooted),
            )
        ):
            raise Pass213PersistentInventoryError("PASS213_CHECKPOINT_AUTHENTICATION_FAILED")


@dataclass(frozen=True)
class InventoryReconciliationReport:
    valid: bool
    persistent_chain_valid: bool
    expected_live_count: int
    expected_tombstone_count: int
    actual_protected_count: int
    missing_live_entry_hashes: tuple[str, ...]
    unexpected_protected_entry_hashes: tuple[str, ...]
    inventory_root_hash216: str


class PersistentCompiledROMInventory:
    def __init__(
        self, *, database_path: str | Path,
        protected_store: NativeProtectedCompiledROMStore,
        inventory_key: bytes, deletion_key: bytes, admission_key: bytes,
        genesis_epoch: int,
    ) -> None:
        self._inventory_key = _key(inventory_key, "PASS213_INVENTORY_KEY_TOO_SHORT")
        self._deletion_key = _key(deletion_key, "PASS213_DELETION_KEY_TOO_SHORT")
        self._admission_key = _key(admission_key, "PASS213_ADMISSION_KEY_TOO_SHORT")
        self._protected_store = protected_store
        self._genesis_epoch = int(genesis_epoch)
        if self._genesis_epoch < 0:
            raise Pass213PersistentInventoryError("PASS213_INVENTORY_EPOCH_INVALID")
        path = Path(database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._schema()
        epoch = self._meta("genesis_epoch")
        if epoch is None:
            with self._connection:
                self._set_meta("genesis_epoch", str(self._genesis_epoch))
                self._set_meta("event_head_hash216", ZERO_HASH216)
                self._set_meta("inventory_root_hash216", self._empty_root())
        elif int(epoch) != self._genesis_epoch:
            raise Pass213PersistentInventoryError("PASS213_INVENTORY_EPOCH_MISMATCH")
        self.verify_persistent_chain()

    def _schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS events(
              sequence INTEGER PRIMARY KEY, event_hash216 TEXT UNIQUE NOT NULL,
              event_json TEXT NOT NULL, authentication_tag TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS entries(
              entry_hash216 TEXT PRIMARY KEY, operation_id TEXT NOT NULL,
              state TEXT NOT NULL, carrier_json TEXT,
              carrier_root_hash216 TEXT NOT NULL,
              admission_root_hash216 TEXT NOT NULL,
              admitted_sequence INTEGER NOT NULL, updated_sequence INTEGER NOT NULL,
              deletion_authorization_root_hash216 TEXT,
              tombstone_event_hash216 TEXT, tombstone_json TEXT);
            CREATE TABLE IF NOT EXISTS inventory_roots(
              sequence INTEGER PRIMARY KEY, inventory_root_hash216 TEXT UNIQUE NOT NULL,
              root_json TEXT NOT NULL, authentication_tag TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS checkpoints(
              checkpoint_sequence INTEGER PRIMARY KEY,
              checkpoint_root_hash216 TEXT UNIQUE NOT NULL,
              checkpoint_json TEXT NOT NULL, authentication_tag TEXT NOT NULL);
            """
        )

    def _meta(self, key: str) -> str | None:
        row = self._connection.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return None if row is None else str(row["value"])

    def _set_meta(self, key: str, value: str) -> None:
        self._connection.execute(
            "INSERT INTO meta(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )

    def _state(self) -> dict[str, dict[str, Any]]:
        return {
            str(row["entry_hash216"]): {
                "operation_id": str(row["operation_id"]),
                "state": str(row["state"]),
                "carrier_root_hash216": str(row["carrier_root_hash216"]),
                "admission_root_hash216": str(row["admission_root_hash216"]),
                "admitted_sequence": int(row["admitted_sequence"]),
                "updated_sequence": int(row["updated_sequence"]),
                "deletion_authorization_root_hash216": (
                    None if row["deletion_authorization_root_hash216"] is None
                    else str(row["deletion_authorization_root_hash216"])
                ),
                "tombstone_event_hash216": (
                    None if row["tombstone_event_hash216"] is None
                    else str(row["tombstone_event_hash216"])
                ),
            }
            for row in self._connection.execute(
                "SELECT * FROM entries ORDER BY entry_hash216"
            )
        }

    def _empty_root(self) -> str:
        payload = {
            "runtime_classification": RUNTIME_CLASSIFICATION,
            "genesis_epoch": self._genesis_epoch,
            "sequence": 0,
            "event_chain_head_hash216": ZERO_HASH216,
            "entries": {},
        }
        return hash216("persistent-compiled-rom-inventory", canonical_bytes(payload))

    def _root(self, sequence: int, event_head: str, state: Mapping[str, Any]) -> dict[str, Any]:
        unsigned = {
            "schema": "HHS_PASS_213_INVENTORY_ROOT_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "runtime_classification": RUNTIME_CLASSIFICATION,
            "genesis_epoch": self._genesis_epoch,
            "sequence": sequence,
            "event_chain_head_hash216": event_head,
            "live_count": sum(item["state"] == _LIVE for item in state.values()),
            "tombstone_count": sum(item["state"] == _TOMBSTONED for item in state.values()),
            "entries": state,
        }
        root = hash216("persistent-compiled-rom-inventory", canonical_bytes(unsigned))
        return {
            **unsigned,
            "inventory_root_hash216": root,
            "authentication_tag": _tag(
                self._inventory_key, "INVENTORY-ROOT",
                {**unsigned, "inventory_root_hash216": root},
            ),
        }

    def current_inventory_root(self) -> str:
        return str(self._meta("inventory_root_hash216"))

    def _event(
        self, *, sequence: int, event_type: str, timestamp_ns: int,
        entry_hash216: str | None, operation_id: str | None,
        authority_id: str, reason: str,
        carrier_root_hash216: str | None,
        admission_root_hash216: str | None,
        deletion_root_hash216: str | None,
    ) -> dict[str, Any]:
        if event_type not in _EVENTS or not authority_id or not reason:
            raise Pass213PersistentInventoryError("PASS213_INVENTORY_EVENT_FIELDS_INVALID")
        unsigned = {
            "schema": "HHS_PASS_213_INVENTORY_EVENT_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "sequence": sequence,
            "genesis_epoch": self._genesis_epoch,
            "event_type": event_type,
            "timestamp_ns": int(timestamp_ns),
            "entry_hash216": entry_hash216,
            "operation_id": operation_id,
            "authority_id": authority_id,
            "reason": reason,
            "carrier_root_hash216": carrier_root_hash216,
            "admission_root_hash216": admission_root_hash216,
            "deletion_authorization_root_hash216": deletion_root_hash216,
            "prior_event_hash216": str(self._meta("event_head_hash216")),
            "prior_inventory_root_hash216": self.current_inventory_root(),
        }
        event_hash = hash216("persistent-inventory-event", canonical_bytes(unsigned))
        rooted = {**unsigned, "event_hash216": event_hash}
        return {
            **rooted,
            "authentication_tag": _tag(self._inventory_key, "INVENTORY-EVENT", rooted),
        }

    def _append(
        self, *, event_type: str, timestamp_ns: int,
        entry_hash216: str | None, operation_id: str | None,
        authority_id: str, reason: str,
        carrier_root_hash216: str | None,
        admission_root_hash216: str | None,
        deletion_root_hash216: str | None,
        entry_values: Mapping[str, Any],
    ) -> dict[str, Any]:
        sequence = int(self._connection.execute(
            "SELECT COALESCE(MAX(sequence),0)+1 AS n FROM events"
        ).fetchone()["n"])
        event = self._event(
            sequence=sequence, event_type=event_type, timestamp_ns=timestamp_ns,
            entry_hash216=entry_hash216, operation_id=operation_id,
            authority_id=authority_id, reason=reason,
            carrier_root_hash216=carrier_root_hash216,
            admission_root_hash216=admission_root_hash216,
            deletion_root_hash216=deletion_root_hash216,
        )
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO entries(
                  entry_hash216,operation_id,state,carrier_json,
                  carrier_root_hash216,admission_root_hash216,
                  admitted_sequence,updated_sequence,
                  deletion_authorization_root_hash216,
                  tombstone_event_hash216,tombstone_json
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(entry_hash216) DO UPDATE SET
                  operation_id=excluded.operation_id,state=excluded.state,
                  carrier_json=excluded.carrier_json,
                  carrier_root_hash216=excluded.carrier_root_hash216,
                  admission_root_hash216=excluded.admission_root_hash216,
                  admitted_sequence=excluded.admitted_sequence,
                  updated_sequence=excluded.updated_sequence,
                  deletion_authorization_root_hash216=excluded.deletion_authorization_root_hash216,
                  tombstone_event_hash216=excluded.tombstone_event_hash216,
                  tombstone_json=excluded.tombstone_json
                """,
                (
                    entry_values["entry_hash216"], entry_values["operation_id"],
                    entry_values["state"], entry_values.get("carrier_json"),
                    entry_values["carrier_root_hash216"],
                    entry_values["admission_root_hash216"],
                    entry_values["admitted_sequence"], sequence,
                    entry_values.get("deletion_authorization_root_hash216"),
                    (
                        event["event_hash216"]
                        if entry_values["state"] == _TOMBSTONED else None
                    ),
                    entry_values.get("tombstone_json"),
                ),
            )
            state = self._state()
            root = self._root(sequence, event["event_hash216"], state)
            self._connection.execute(
                "INSERT INTO events VALUES(?,?,?,?)",
                (
                    sequence, event["event_hash216"],
                    canonical_bytes(event).decode(), event["authentication_tag"],
                ),
            )
            self._connection.execute(
                "INSERT INTO inventory_roots VALUES(?,?,?,?)",
                (
                    sequence, root["inventory_root_hash216"],
                    canonical_bytes(root).decode(), root["authentication_tag"],
                ),
            )
            self._set_meta("event_head_hash216", event["event_hash216"])
            self._set_meta("inventory_root_hash216", root["inventory_root_hash216"])
        return event

    @staticmethod
    def _carrier_json(carrier: CompiledROMCarrier) -> str:
        return canonical_bytes(carrier.to_dict(include_payloads=True)).decode()

    def _row(self, entry_hash216: str) -> sqlite3.Row:
        row = self._connection.execute(
            "SELECT * FROM entries WHERE entry_hash216=?", (entry_hash216,)
        ).fetchone()
        if row is None:
            raise Pass213PersistentInventoryError("PASS213_INVENTORY_ENTRY_NOT_FOUND")
        return row

    def create_deletion_authorization(
        self, *, entry_hash216: str, authority_id: str, reason: str,
        nonce: str, timestamp_ns: int | None = None,
    ) -> DeletionAuthorization:
        row = self._row(entry_hash216)
        if str(row["state"]) != _LIVE:
            raise Pass213PersistentInventoryError("PASS213_DELETION_REQUIRES_LIVE_ENTRY")
        return DeletionAuthorization.create(
            entry_hash216=entry_hash216, authority_id=authority_id,
            reason=reason, timestamp_ns=time.time_ns() if timestamp_ns is None else timestamp_ns,
            nonce=nonce, bound_inventory_root_hash216=self.current_inventory_root(),
            deletion_key=self._deletion_key,
        )

    def admit_carrier(
        self, carrier: CompiledROMCarrier | Mapping[str, Any], *,
        authority_id: str, timestamp_ns: int | None = None,
    ) -> ProtectedCompiledROMRecord:
        value = carrier if isinstance(carrier, CompiledROMCarrier) else CompiledROMCarrier.from_mapping(carrier)
        value.validate_envelope(self._admission_key)
        admission = inspect_and_correct_carrier(value, self._admission_key)
        existing = self._connection.execute(
            "SELECT * FROM entries WHERE entry_hash216=?",
            (admission.entry.entry_hash216,),
        ).fetchone()
        if existing is not None:
            if str(existing["state"]) == _TOMBSTONED:
                raise Pass213PersistentInventoryError("PASS213_TOMBSTONED_ENTRY_READMISSION_REJECTED")
            if (
                str(existing["operation_id"]) != admission.entry.operation_id
                or str(existing["carrier_root_hash216"]) != value.carrier_root_hash216
            ):
                raise Pass213PersistentInventoryError("PASS213_LIVE_ENTRY_ADMISSION_CONFLICT")
            if self._protected_store.contains_hash216(admission.entry.entry_hash216):
                return self._protected_store.lookup_record(admission.entry.entry_hash216)
            return self.recover_missing_entry(
                admission.entry.entry_hash216,
                authority_id=authority_id,
                timestamp_ns=timestamp_ns,
            )
        record = self._protected_store.admit(admission)
        self._append(
            event_type="ADMIT",
            timestamp_ns=time.time_ns() if timestamp_ns is None else timestamp_ns,
            entry_hash216=admission.entry.entry_hash216,
            operation_id=admission.entry.operation_id,
            authority_id=authority_id, reason="COMPILED_ROM_ADMISSION",
            carrier_root_hash216=value.carrier_root_hash216,
            admission_root_hash216=admission.admission_root_hash216,
            deletion_root_hash216=None,
            entry_values={
                "entry_hash216": admission.entry.entry_hash216,
                "operation_id": admission.entry.operation_id,
                "state": _LIVE,
                "carrier_json": self._carrier_json(value),
                "carrier_root_hash216": value.carrier_root_hash216,
                "admission_root_hash216": admission.admission_root_hash216,
                "admitted_sequence": int(
                    self._connection.execute(
                        "SELECT COALESCE(MAX(sequence),0)+1 AS n FROM events"
                    ).fetchone()["n"]
                ),
            },
        )
        return record

    def authorized_retire(
        self, authorization: DeletionAuthorization,
    ) -> tuple[dict[str, Any], SecureMemoryReceipt | None]:
        authorization.validate(self._deletion_key)
        if authorization.bound_inventory_root_hash216 != self.current_inventory_root():
            raise Pass213PersistentInventoryError("PASS213_DELETION_AUTHORIZATION_STALE")
        row = self._row(authorization.entry_hash216)
        if str(row["state"]) != _LIVE:
            raise Pass213PersistentInventoryError("PASS213_DELETION_REQUIRES_LIVE_ENTRY")
        event = self._append(
            event_type="TOMBSTONE", timestamp_ns=authorization.timestamp_ns,
            entry_hash216=authorization.entry_hash216,
            operation_id=str(row["operation_id"]),
            authority_id=authorization.authority_id,
            reason=authorization.reason,
            carrier_root_hash216=str(row["carrier_root_hash216"]),
            admission_root_hash216=str(row["admission_root_hash216"]),
            deletion_root_hash216=authorization.authorization_root_hash216,
            entry_values={
                "entry_hash216": authorization.entry_hash216,
                "operation_id": str(row["operation_id"]),
                "state": _TOMBSTONED,
                "carrier_json": row["carrier_json"],
                "carrier_root_hash216": str(row["carrier_root_hash216"]),
                "admission_root_hash216": str(row["admission_root_hash216"]),
                "admitted_sequence": int(row["admitted_sequence"]),
                "deletion_authorization_root_hash216": authorization.authorization_root_hash216,
                "tombstone_json": canonical_bytes(authorization.to_mapping()).decode(),
            },
        )
        receipt = (
            self._protected_store.retire_hash216(authorization.entry_hash216)
            if self._protected_store.contains_hash216(authorization.entry_hash216)
            else None
        )
        return event, receipt

    def _checkpoint(self, root: str) -> InventoryCheckpoint:
        row = self._connection.execute(
            "SELECT checkpoint_json FROM checkpoints WHERE checkpoint_root_hash216=?",
            (root,),
        ).fetchone()
        if row is None:
            raise Pass213PersistentInventoryError("PASS213_CHECKPOINT_NOT_FOUND")
        checkpoint = InventoryCheckpoint.from_mapping(json.loads(str(row["checkpoint_json"])))
        checkpoint.validate(self._inventory_key)
        return checkpoint

    def recover_missing_entry(
        self, entry_hash216: str, *, authority_id: str,
        checkpoint_root_hash216: str | None = None,
        timestamp_ns: int | None = None,
    ) -> ProtectedCompiledROMRecord:
        row = self._row(entry_hash216)
        if str(row["state"]) != _LIVE:
            raise Pass213PersistentInventoryError("PASS213_TOMBSTONED_ENTRY_RECOVERY_REJECTED")
        if self._protected_store.contains_hash216(entry_hash216):
            return self._protected_store.lookup_record(entry_hash216)
        carrier_data: Mapping[str, Any] | None = (
            None if row["carrier_json"] is None else json.loads(str(row["carrier_json"]))
        )
        reason = "RETAINED_CARRIER_RECOVERY"
        if checkpoint_root_hash216 is not None:
            checkpoint = self._checkpoint(checkpoint_root_hash216)
            match = next(
                (item for item in checkpoint.live_entries if item["entry_hash216"] == entry_hash216),
                None,
            )
            if match is None:
                raise Pass213PersistentInventoryError("PASS213_CHECKPOINT_ENTRY_NOT_LIVE")
            carrier_data = match["carrier"]
            reason = "CHECKPOINT_RECOVERY"
        if carrier_data is None:
            raise Pass213PersistentInventoryError("PASS213_RECOVERY_MATERIAL_MISSING")
        carrier = CompiledROMCarrier.from_mapping(carrier_data)
        admission = inspect_and_correct_carrier(carrier, self._admission_key)
        if (
            admission.entry.entry_hash216 != entry_hash216
            or admission.entry.operation_id != str(row["operation_id"])
        ):
            raise Pass213PersistentInventoryError("PASS213_RECOVERY_ENTRY_IDENTITY_MISMATCH")
        record = self._protected_store.admit(admission)
        canonical = protect_compiled_rom_entry(admission.entry, self._admission_key)
        self._append(
            event_type="RECOVER",
            timestamp_ns=time.time_ns() if timestamp_ns is None else timestamp_ns,
            entry_hash216=entry_hash216,
            operation_id=admission.entry.operation_id,
            authority_id=authority_id, reason=reason,
            carrier_root_hash216=canonical.carrier_root_hash216,
            admission_root_hash216=admission.admission_root_hash216,
            deletion_root_hash216=None,
            entry_values={
                "entry_hash216": entry_hash216,
                "operation_id": admission.entry.operation_id,
                "state": _LIVE,
                "carrier_json": self._carrier_json(canonical),
                "carrier_root_hash216": canonical.carrier_root_hash216,
                "admission_root_hash216": admission.admission_root_hash216,
                "admitted_sequence": int(row["admitted_sequence"]),
            },
        )
        return record

    def recover_all_missing(
        self, *, authority_id: str, timestamp_ns: int | None = None,
    ) -> tuple[ProtectedCompiledROMRecord, ...]:
        base = time.time_ns() if timestamp_ns is None else int(timestamp_ns)
        return tuple(
            self.recover_missing_entry(
                entry_hash, authority_id=authority_id, timestamp_ns=base + offset,
            )
            for offset, entry_hash in enumerate(self.reconcile().missing_live_entry_hashes)
        )

    def create_checkpoint(
        self, *, authority_id: str, label: str,
        timestamp_ns: int | None = None,
    ) -> InventoryCheckpoint:
        if not authority_id or not label or not self.reconcile().valid:
            raise Pass213PersistentInventoryError("PASS213_CHECKPOINT_REQUIRES_VALID_INVENTORY")
        last = self._connection.execute(
            "SELECT checkpoint_root_hash216 FROM checkpoints ORDER BY checkpoint_sequence DESC LIMIT 1"
        ).fetchone()
        live: list[Mapping[str, Any]] = []
        tombstones: list[Mapping[str, Any]] = []
        for row in self._connection.execute("SELECT * FROM entries ORDER BY entry_hash216"):
            item = {
                "entry_hash216": str(row["entry_hash216"]),
                "operation_id": str(row["operation_id"]),
                "carrier_root_hash216": str(row["carrier_root_hash216"]),
                "admission_root_hash216": str(row["admission_root_hash216"]),
                "carrier": json.loads(str(row["carrier_json"])),
            }
            if str(row["state"]) == _LIVE:
                live.append(item)
            else:
                tombstones.append({
                    **item,
                    "deletion_authorization_root_hash216": str(
                        row["deletion_authorization_root_hash216"]
                    ),
                    "tombstone_event_hash216": str(row["tombstone_event_hash216"]),
                    "deletion_authorization": json.loads(str(row["tombstone_json"])),
                })
        sequence = int(self._connection.execute(
            "SELECT COALESCE(MAX(sequence),0) AS n FROM events"
        ).fetchone()["n"])
        temporary = InventoryCheckpoint(
            sequence, self._genesis_epoch,
            time.time_ns() if timestamp_ns is None else int(timestamp_ns),
            authority_id, label,
            ZERO_HASH216 if last is None else str(last["checkpoint_root_hash216"]),
            str(self._meta("event_head_hash216")), self.current_inventory_root(),
            tuple(live), tuple(tombstones), "", "",
        )
        root = hash216("persistent-inventory-checkpoint", canonical_bytes(temporary.unsigned()))
        rooted = {**temporary.unsigned(), "checkpoint_root_hash216": root}
        checkpoint = InventoryCheckpoint(
            temporary.checkpoint_sequence, temporary.genesis_epoch,
            temporary.created_timestamp_ns, authority_id, label,
            temporary.prior_checkpoint_root_hash216,
            temporary.event_chain_head_hash216,
            temporary.inventory_root_hash216,
            temporary.live_entries, temporary.tombstones, root,
            _tag(self._inventory_key, "INVENTORY-CHECKPOINT", rooted),
        )
        checkpoint.validate(self._inventory_key)
        with self._connection:
            self._connection.execute(
                "INSERT INTO checkpoints VALUES(?,?,?,?)",
                (
                    checkpoint.checkpoint_sequence,
                    checkpoint.checkpoint_root_hash216,
                    canonical_bytes(checkpoint.to_mapping()).decode(),
                    checkpoint.authentication_tag,
                ),
            )
        return checkpoint

    def verify_persistent_chain(self) -> bool:
        replay: dict[str, dict[str, Any]] = {}
        prior_event = ZERO_HASH216
        roots_seen = {self._empty_root()}
        events = self._connection.execute("SELECT * FROM events ORDER BY sequence").fetchall()
        roots = {
            int(row["sequence"]): row
            for row in self._connection.execute(
                "SELECT * FROM inventory_roots ORDER BY sequence"
            )
        }
        for expected_sequence, row in enumerate(events, 1):
            event = json.loads(str(row["event_json"]))
            if (
                int(event.get("sequence", -1)) != expected_sequence
                or event.get("event_type") not in _EVENTS
                or event.get("prior_event_hash216") != prior_event
                or event.get("genesis_epoch") != self._genesis_epoch
            ):
                raise Pass213PersistentInventoryError("PASS213_INVENTORY_EVENT_CHAIN_DISCONTINUITY")
            unsigned = {
                key: value for key, value in event.items()
                if key not in {"event_hash216", "authentication_tag"}
            }
            event_hash = hash216("persistent-inventory-event", canonical_bytes(unsigned))
            rooted = {**unsigned, "event_hash216": event_hash}
            if (
                event_hash != str(row["event_hash216"])
                or event_hash != event.get("event_hash216")
                or not hmac.compare_digest(
                    str(event.get("authentication_tag")),
                    _tag(self._inventory_key, "INVENTORY-EVENT", rooted),
                )
            ):
                raise Pass213PersistentInventoryError("PASS213_INVENTORY_EVENT_AUTHENTICATION_FAILED")
            entry_hash = event["entry_hash216"]
            if event["event_type"] == "ADMIT":
                if entry_hash in replay:
                    raise Pass213PersistentInventoryError("PASS213_INVENTORY_REPLAY_DUPLICATE_ADMIT")
                replay[entry_hash] = {
                    "operation_id": event["operation_id"], "state": _LIVE,
                    "carrier_root_hash216": event["carrier_root_hash216"],
                    "admission_root_hash216": event["admission_root_hash216"],
                    "admitted_sequence": expected_sequence,
                    "updated_sequence": expected_sequence,
                    "deletion_authorization_root_hash216": None,
                    "tombstone_event_hash216": None,
                }
            elif event["event_type"] == "RECOVER":
                item = replay.get(entry_hash)
                if item is None or item["state"] != _LIVE:
                    raise Pass213PersistentInventoryError("PASS213_INVENTORY_RECOVERY_WITHOUT_LIVE_ENTRY")
                item.update(
                    carrier_root_hash216=event["carrier_root_hash216"],
                    admission_root_hash216=event["admission_root_hash216"],
                    updated_sequence=expected_sequence,
                )
            else:
                item = replay.get(entry_hash)
                if item is None or item["state"] != _LIVE:
                    raise Pass213PersistentInventoryError("PASS213_INVENTORY_TOMBSTONE_WITHOUT_LIVE_ENTRY")
                item.update(
                    state=_TOMBSTONED, updated_sequence=expected_sequence,
                    deletion_authorization_root_hash216=event[
                        "deletion_authorization_root_hash216"
                    ],
                    tombstone_event_hash216=event_hash,
                )
            expected_root = self._root(expected_sequence, event_hash, replay)
            stored = roots.get(expected_sequence)
            if (
                stored is None
                or json.loads(str(stored["root_json"])) != expected_root
                or str(stored["inventory_root_hash216"])
                != expected_root["inventory_root_hash216"]
            ):
                raise Pass213PersistentInventoryError("PASS213_INVENTORY_ROOT_MISMATCH")
            roots_seen.add(expected_root["inventory_root_hash216"])
            prior_event = event_hash
        if set(roots) != set(range(1, len(events) + 1)):
            raise Pass213PersistentInventoryError("PASS213_INVENTORY_ROOT_SEQUENCE_MISMATCH")
        if replay != self._state():
            raise Pass213PersistentInventoryError("PASS213_INVENTORY_ENTRY_TABLE_DIVERGENCE")
        if self._meta("event_head_hash216") != prior_event:
            raise Pass213PersistentInventoryError("PASS213_INVENTORY_META_EVENT_HEAD_MISMATCH")
        expected_current = self._empty_root() if not events else self._root(
            len(events), prior_event, replay
        )["inventory_root_hash216"]
        if self.current_inventory_root() != expected_current:
            raise Pass213PersistentInventoryError("PASS213_INVENTORY_META_ROOT_MISMATCH")
        for row in self._connection.execute("SELECT * FROM entries ORDER BY entry_hash216"):
            if str(row["state"]) not in {_LIVE, _TOMBSTONED} or row["carrier_json"] is None:
                raise Pass213PersistentInventoryError("PASS213_INVENTORY_ENTRY_STATE_INVALID")
            carrier = CompiledROMCarrier.from_mapping(json.loads(str(row["carrier_json"])))
            carrier.validate_envelope(self._admission_key)
            if (
                carrier.expected_entry_hash216 != str(row["entry_hash216"])
                or carrier.carrier_root_hash216 != str(row["carrier_root_hash216"])
            ):
                raise Pass213PersistentInventoryError("PASS213_INVENTORY_CARRIER_TABLE_MISMATCH")
            if str(row["state"]) == _TOMBSTONED:
                authorization = DeletionAuthorization.from_mapping(
                    json.loads(str(row["tombstone_json"]))
                )
                authorization.validate(self._deletion_key)
                if (
                    authorization.entry_hash216 != str(row["entry_hash216"])
                    or authorization.authorization_root_hash216
                    != str(row["deletion_authorization_root_hash216"])
                ):
                    raise Pass213PersistentInventoryError("PASS213_TOMBSTONE_AUTHORIZATION_TABLE_MISMATCH")
        previous_checkpoint = ZERO_HASH216
        previous_sequence = -1
        for row in self._connection.execute(
            "SELECT * FROM checkpoints ORDER BY checkpoint_sequence"
        ):
            checkpoint = InventoryCheckpoint.from_mapping(
                json.loads(str(row["checkpoint_json"]))
            )
            checkpoint.validate(self._inventory_key)
            if (
                checkpoint.prior_checkpoint_root_hash216 != previous_checkpoint
                or checkpoint.checkpoint_sequence < previous_sequence
                or checkpoint.inventory_root_hash216 not in roots_seen
            ):
                raise Pass213PersistentInventoryError("PASS213_CHECKPOINT_CHAIN_DISCONTINUITY")
            previous_checkpoint = checkpoint.checkpoint_root_hash216
            previous_sequence = checkpoint.checkpoint_sequence
        return True

    def reconcile(self) -> InventoryReconciliationReport:
        persistent_valid = self.verify_persistent_chain()
        state = self._state()
        expected_live = {key for key, value in state.items() if value["state"] == _LIVE}
        tombstones = {key for key, value in state.items() if value["state"] == _TOMBSTONED}
        actual = set(self._protected_store.record_hashes())
        missing = tuple(sorted(expected_live - actual))
        unexpected = tuple(sorted(actual - expected_live))
        return InventoryReconciliationReport(
            persistent_valid and not missing and not unexpected,
            persistent_valid, len(expected_live), len(tombstones), len(actual),
            missing, unexpected, self.current_inventory_root(),
        )

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "PersistentCompiledROMInventory":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()


__all__ = [
    "ITERATION", "RUNTIME_CLASSIFICATION",
    "Pass213PersistentInventoryError", "DeletionAuthorization",
    "InventoryCheckpoint", "InventoryReconciliationReport",
    "PersistentCompiledROMInventory",
]

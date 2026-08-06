"""Authenticated receipt ledger for Pass 213 Iteration 10 native dispatch."""
from __future__ import annotations

from dataclasses import dataclass, replace
import hmac
import json
from pathlib import Path
import sqlite3
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    CONTRACT, ZERO_HASH72, canonical_bytes, hash216,
)
from hhs_backend.runtime.hhs_pass213_native_dispatch_common_v1 import (
    ITERATION, _hmac_hex, _require_hash216, _require_hash72, _require_key,
    Pass213NativeDispatchIntegrityError,
    Pass213NativeDispatchValidationError,
)
from hhs_runtime.core.hash72_digest_v1 import verify_hash72

@dataclass(frozen=True)
class NativeDispatchReceipt:
    sequence: int
    timestamp_ns: int
    entry_hash216: str
    operation_id: str
    native_dispatch_id: str
    vm81_cell_id: int
    operation_slot: int
    g243_control_id: int
    hydration_lane: int
    route_commitment_hash216: str
    read_set_root_hash216: str
    write_set_root_hash216: str
    request_root_hash216: str
    result_root_hash216: str
    prior_state_root_hash216: str
    successor_state_root_hash216: str
    prior_receipt_hash72: str
    receipt_hash72: str
    result_values: tuple[int, ...]
    tensor_root_hash216: str
    kernel_policy_hash216: str
    kernel_measurement_hash216: str
    lineage_root_hash216: str
    ledger_event_root_hash216: str = ""

    def unsigned_mapping(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_213_NATIVE_DISPATCH_RECEIPT_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "sequence": self.sequence,
            "timestamp_ns": self.timestamp_ns,
            "entry_hash216": self.entry_hash216,
            "operation_id": self.operation_id,
            "native_dispatch_id": self.native_dispatch_id,
            "vm81_cell_id": self.vm81_cell_id,
            "operation_slot": self.operation_slot,
            "g243_control_id": self.g243_control_id,
            "hydration_lane": self.hydration_lane,
            "route_commitment_hash216": self.route_commitment_hash216,
            "read_set_root_hash216": self.read_set_root_hash216,
            "write_set_root_hash216": self.write_set_root_hash216,
            "request_root_hash216": self.request_root_hash216,
            "result_root_hash216": self.result_root_hash216,
            "prior_state_root_hash216": self.prior_state_root_hash216,
            "successor_state_root_hash216": self.successor_state_root_hash216,
            "prior_receipt_hash72": self.prior_receipt_hash72,
            "receipt_hash72": self.receipt_hash72,
            "result_values": self.result_values,
            "tensor_root_hash216": self.tensor_root_hash216,
            "kernel_policy_hash216": self.kernel_policy_hash216,
            "kernel_measurement_hash216": self.kernel_measurement_hash216,
            "lineage_root_hash216": self.lineage_root_hash216,
            "singleton_vm81_admission": True,
            "physical_route_exposed": False,
            "protected_payload_exposed": False,
        }

    def to_mapping(self) -> dict[str, Any]:
        return {
            **self.unsigned_mapping(),
            "ledger_event_root_hash216": self.ledger_event_root_hash216,
        }


class NativeDispatchLedger:
    """Authenticated append-only SQLite receipt chain for native executions."""

    def __init__(
        self,
        *,
        database_path: str | Path,
        root_key: bytes,
        anchor_state_root_hash216: str,
        anchor_receipt_hash72: str,
    ) -> None:
        self._key = _require_key(root_key, "PASS213_NATIVE_DISPATCH_LEDGER_KEY_TOO_SHORT")
        self.anchor_state_root_hash216 = _require_hash216(
            anchor_state_root_hash216,
            "PASS213_NATIVE_DISPATCH_LEDGER_ANCHOR_STATE_INVALID",
        )
        self.anchor_receipt_hash72 = _require_hash72(
            anchor_receipt_hash72,
            "PASS213_NATIVE_DISPATCH_LEDGER_ANCHOR_RECEIPT_INVALID",
        )
        path = Path(database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(path)
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS native_dispatch_metadata (
                singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
                anchor_state_root_hash216 TEXT NOT NULL,
                anchor_receipt_hash72 TEXT NOT NULL
            )
            """
        )
        metadata = self._connection.execute(
            "SELECT anchor_state_root_hash216,anchor_receipt_hash72 FROM native_dispatch_metadata WHERE singleton=1"
        ).fetchone()
        if metadata is None:
            self._connection.execute(
                "INSERT INTO native_dispatch_metadata(singleton,anchor_state_root_hash216,anchor_receipt_hash72) VALUES(1,?,?)",
                (self.anchor_state_root_hash216, self.anchor_receipt_hash72),
            )
        elif (
            str(metadata[0]) != self.anchor_state_root_hash216
            or str(metadata[1]) != self.anchor_receipt_hash72
        ):
            raise Pass213NativeDispatchIntegrityError(
                "PASS213_NATIVE_DISPATCH_LEDGER_ANCHOR_MISMATCH"
            )
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS native_dispatch_receipts (
                sequence INTEGER PRIMARY KEY,
                event_json TEXT NOT NULL,
                event_root_hash216 TEXT NOT NULL,
                authentication_tag TEXT NOT NULL
            )
            """
        )
        self._connection.commit()
        self.verify_chain()

    def _tag(self, event_root_hash216: str, event_json: str) -> str:
        return _hmac_hex(
            self._key,
            "NATIVE-DISPATCH-LEDGER-EVENT",
            canonical_bytes({
                "event_root_hash216": event_root_hash216,
                "event_json": event_json,
            }),
        )

    def append(self, receipt: NativeDispatchReceipt) -> NativeDispatchReceipt:
        if receipt.ledger_event_root_hash216:
            raise Pass213NativeDispatchIntegrityError(
                "PASS213_NATIVE_DISPATCH_LEDGER_EVENT_ALREADY_ROOTED"
            )
        unsigned = receipt.unsigned_mapping()
        event_json = canonical_bytes(unsigned).decode("utf-8")
        event_root = hash216("native-dispatch-ledger-event", event_json.encode("utf-8"))
        tag = self._tag(event_root, event_json)
        expected_sequence = self.count() + 1
        if receipt.sequence != expected_sequence:
            raise Pass213NativeDispatchIntegrityError(
                "PASS213_NATIVE_DISPATCH_LEDGER_SEQUENCE_INVALID"
            )
        with self._connection:
            self._connection.execute(
                "INSERT INTO native_dispatch_receipts(sequence,event_json,event_root_hash216,authentication_tag) VALUES(?,?,?,?)",
                (receipt.sequence, event_json, event_root, tag),
            )
        return replace(receipt, ledger_event_root_hash216=event_root)

    def count(self) -> int:
        row = self._connection.execute(
            "SELECT COUNT(*) FROM native_dispatch_receipts"
        ).fetchone()
        return int(row[0])

    def lookup(self, sequence: int) -> Mapping[str, Any]:
        row = self._connection.execute(
            "SELECT event_json,event_root_hash216,authentication_tag FROM native_dispatch_receipts WHERE sequence=?",
            (int(sequence),),
        ).fetchone()
        if row is None:
            raise Pass213NativeDispatchValidationError(
                "PASS213_NATIVE_DISPATCH_RECEIPT_NOT_FOUND"
            )
        event_json, event_root, tag = map(str, row)
        if not hmac.compare_digest(event_root, hash216(
            "native-dispatch-ledger-event", event_json.encode("utf-8")
        )) or not hmac.compare_digest(tag, self._tag(event_root, event_json)):
            raise Pass213NativeDispatchIntegrityError(
                "PASS213_NATIVE_DISPATCH_LEDGER_AUTHENTICATION_FAILED"
            )
        return {**json.loads(event_json), "ledger_event_root_hash216": event_root}

    def latest(self) -> Mapping[str, Any] | None:
        row = self._connection.execute(
            "SELECT MAX(sequence) FROM native_dispatch_receipts"
        ).fetchone()
        if row is None or row[0] is None:
            return None
        return self.lookup(int(row[0]))

    def verify_chain(self) -> bool:
        rows = self._connection.execute(
            "SELECT sequence,event_json,event_root_hash216,authentication_tag FROM native_dispatch_receipts ORDER BY sequence"
        ).fetchall()
        prior_receipt = self.anchor_receipt_hash72
        prior_state: str | None = self.anchor_state_root_hash216
        for expected_sequence, row in enumerate(rows, start=1):
            sequence, event_json, event_root, tag = row
            if int(sequence) != expected_sequence:
                raise Pass213NativeDispatchIntegrityError(
                    "PASS213_NATIVE_DISPATCH_LEDGER_SEQUENCE_GAP"
                )
            event_json = str(event_json)
            event_root = str(event_root)
            tag = str(tag)
            expected_root = hash216(
                "native-dispatch-ledger-event", event_json.encode("utf-8")
            )
            if not hmac.compare_digest(event_root, expected_root) or not hmac.compare_digest(
                tag, self._tag(event_root, event_json)
            ):
                raise Pass213NativeDispatchIntegrityError(
                    "PASS213_NATIVE_DISPATCH_LEDGER_AUTHENTICATION_FAILED"
                )
            event = json.loads(event_json)
            if event["prior_receipt_hash72"] != prior_receipt:
                raise Pass213NativeDispatchIntegrityError(
                    "PASS213_NATIVE_DISPATCH_LEDGER_RECEIPT_CHAIN_INVALID"
                )
            if event["prior_state_root_hash216"] != prior_state:
                raise Pass213NativeDispatchIntegrityError(
                    "PASS213_NATIVE_DISPATCH_LEDGER_STATE_CHAIN_INVALID"
                )
            if not verify_hash72(
                str(event["receipt_hash72"]),
                {
                    "domain": "HHS-P213-ITER10-NATIVE-DISPATCH-RECEIPT-V1",
                    "contract": CONTRACT,
                    "iteration": ITERATION,
                    "sequence": int(event["sequence"]),
                },
                bytes.fromhex(str(event["successor_state_root_hash216"])),
            ):
                raise Pass213NativeDispatchIntegrityError(
                    "PASS213_NATIVE_DISPATCH_LEDGER_HASH72_INVALID"
                )
            prior_receipt = str(event["receipt_hash72"])
            prior_state = str(event["successor_state_root_hash216"])
        return True

    def close(self) -> None:
        self._connection.close()
        self._key = b"\0" * len(self._key)




__all__ = ["NativeDispatchReceipt", "NativeDispatchLedger"]

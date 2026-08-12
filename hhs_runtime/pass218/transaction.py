"""Pass 218 Iteration 3 deterministic source-transaction membrane.

A structural hydration candidate is staged against transient source bytes,
validated, committed into a non-authoritative structural store, and admitted
only after the managed ingress buffer is zeroized and cleared. Restart records
never serialize source bytes. The purge receipt proves the state of this managed
buffer only; it does not claim physical RAM erasure outside the runtime.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72

PASS218_SOURCE_TRANSACTION_VERSION = "HHS-P218-SOURCE-TRANSACTION-I3-V1"


class TransactionPhase(IntEnum):
    STAGED = 1
    VALIDATED = 2
    STRUCTURAL_COMMITTED = 3
    CLOSED = 4
    QUARANTINED = 5
    REJECTED = 6


class Pass218TransactionError(RuntimeError):
    pass


class Pass218TransactionValidationError(Pass218TransactionError):
    pass


class Pass218TransactionStateError(Pass218TransactionError):
    pass


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _copy(value: Any) -> Any:
    if value is None:
        return None
    return json.loads(_canonical_bytes(value).decode("utf-8"))


def _candidate_record(candidate: Any) -> dict[str, Any]:
    if hasattr(candidate, "to_record"):
        return _copy(candidate.to_record())
    if isinstance(candidate, Mapping):
        return _copy(dict(candidate))
    raise TypeError("P218_TRANSACTION_CANDIDATE_TYPE_UNSUPPORTED")


def _valid_sha256(value: str) -> bool:
    return len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def _valid_hash216(value: str) -> bool:
    return (
        len(value) == 216
        and all(validate_hash72(value[start:start + 72]) for start in (0, 72, 144))
    )


def _forbidden_verbatim_fields(value: Any) -> tuple[str, ...]:
    forbidden = {
        "source_text",
        "raw_text",
        "verbatim_text",
        "source_content",
        "raw_content",
        "verbatim_content",
    }
    found: list[str] = []

    def visit(item: Any, prefix: str) -> None:
        if isinstance(item, Mapping):
            for key, child in item.items():
                key_text = str(key)
                path = key_text if not prefix else prefix + "." + key_text
                if key_text.casefold() in forbidden and child not in (None, "", False):
                    found.append(path)
                visit(child, path)
        elif isinstance(item, list):
            for index, child in enumerate(item):
                visit(child, f"{prefix}[{index}]")

    visit(value, "")
    return tuple(found)


def _source_embedded(record: Mapping[str, Any], source_bytes: bytes) -> bool:
    if len(source_bytes) < 64:
        return False
    serialized = _canonical_bytes(record)
    if source_bytes in serialized:
        return True
    text = source_bytes.decode("utf-8", errors="ignore")
    if len(text) < 64:
        return False
    middle = len(text) // 2
    windows = (text[:64], text[middle:middle + 64], text[-64:])
    return any(window.encode("utf-8") in serialized for window in windows if window)


@dataclass(frozen=True)
class StructuralStoreReceipt:
    transaction_id_hash72: str
    structural_record_hash72: str
    memory_root_hash72: str
    purge_receipt_hash72: str | None
    admitted: bool
    quarantined: bool

    def to_record(self) -> dict[str, Any]:
        return {
            "transaction_id_hash72": self.transaction_id_hash72,
            "structural_record_hash72": self.structural_record_hash72,
            "memory_root_hash72": self.memory_root_hash72,
            "purge_receipt_hash72": self.purge_receipt_hash72,
            "admitted": self.admitted,
            "quarantined": self.quarantined,
        }


class DeterministicStructuralStore:
    """Iteration-3 pre-authority store; this is not the canonical vector store."""

    def __init__(self) -> None:
        self._pending: dict[str, dict[str, Any]] = {}
        self._admitted: dict[str, dict[str, Any]] = {}
        self._quarantined: dict[str, dict[str, Any]] = {}

    def _root(self) -> str:
        rows = [
            {
                "transaction_id_hash72": key,
                "structural_record_hash72": value["structural_record_hash72"],
                "purge_receipt_hash72": value["purge_receipt_hash72"],
            }
            for key, value in sorted(self._admitted.items())
        ]
        return hash72_digest({"domain": "HHS-P218-I3-STRUCTURAL-ROOT-V1"}, rows)

    def prepare(self, transaction_id_hash72: str, record: Mapping[str, Any]) -> StructuralStoreReceipt:
        if not validate_hash72(transaction_id_hash72):
            raise ValueError("P218_TRANSACTION_ID_HASH72_INVALID")
        if transaction_id_hash72 in self._admitted:
            raise Pass218TransactionStateError("P218_TRANSACTION_ALREADY_ADMITTED")
        copied = _copy(record)
        record_hash72 = hash72_digest({"domain": "HHS-P218-I3-STRUCTURAL-RECORD-V1"}, copied)
        existing = self._pending.get(transaction_id_hash72)
        if existing is not None and existing["structural_record_hash72"] != record_hash72:
            raise Pass218TransactionStateError("P218_STRUCTURAL_PREPARE_CONFLICT")
        self._pending[transaction_id_hash72] = {
            "record": copied,
            "structural_record_hash72": record_hash72,
        }
        return StructuralStoreReceipt(
            transaction_id_hash72,
            record_hash72,
            self._root(),
            None,
            False,
            False,
        )

    def admit(self, transaction_id_hash72: str, *, purge_receipt_hash72: str) -> StructuralStoreReceipt:
        if not validate_hash72(purge_receipt_hash72):
            raise ValueError("P218_PURGE_RECEIPT_HASH72_INVALID")
        pending = self._pending.pop(transaction_id_hash72, None)
        if pending is None:
            existing = self._admitted.get(transaction_id_hash72)
            if existing is None:
                raise Pass218TransactionStateError("P218_STRUCTURAL_PENDING_MISSING")
            if existing["purge_receipt_hash72"] != purge_receipt_hash72:
                raise Pass218TransactionStateError("P218_STRUCTURAL_ADMISSION_CONFLICT")
            return StructuralStoreReceipt(
                transaction_id_hash72,
                existing["structural_record_hash72"],
                self._root(),
                purge_receipt_hash72,
                True,
                False,
            )
        self._admitted[transaction_id_hash72] = {
            **pending,
            "purge_receipt_hash72": purge_receipt_hash72,
        }
        return StructuralStoreReceipt(
            transaction_id_hash72,
            pending["structural_record_hash72"],
            self._root(),
            purge_receipt_hash72,
            True,
            False,
        )

    def quarantine(self, transaction_id_hash72: str, *, reason: str) -> StructuralStoreReceipt | None:
        pending = self._pending.pop(transaction_id_hash72, None)
        if pending is None:
            return None
        self._quarantined[transaction_id_hash72] = {
            "structural_record_hash72": pending["structural_record_hash72"],
            "reason": reason,
        }
        return StructuralStoreReceipt(
            transaction_id_hash72,
            pending["structural_record_hash72"],
            self._root(),
            None,
            False,
            True,
        )

    def replay_admitted(
        self,
        transaction_id_hash72: str,
        record: Mapping[str, Any],
        *,
        structural_record_hash72: str,
        purge_receipt_hash72: str,
    ) -> StructuralStoreReceipt:
        prepared = self.prepare(transaction_id_hash72, record)
        if prepared.structural_record_hash72 != structural_record_hash72:
            self.quarantine(transaction_id_hash72, reason="P218_REPLAY_STRUCTURAL_HASH_MISMATCH")
            raise Pass218TransactionValidationError("P218_REPLAY_STRUCTURAL_HASH_MISMATCH")
        return self.admit(transaction_id_hash72, purge_receipt_hash72=purge_receipt_hash72)

    def admitted_record(self, transaction_id_hash72: str) -> dict[str, Any] | None:
        value = self._admitted.get(transaction_id_hash72)
        return None if value is None else _copy(value["record"])

    def is_admitted(self, transaction_id_hash72: str) -> bool:
        return transaction_id_hash72 in self._admitted

    def is_pending(self, transaction_id_hash72: str) -> bool:
        return transaction_id_hash72 in self._pending

    def record(self) -> dict[str, Any]:
        return {
            "schema": "HHS-P218-I3-STRUCTURAL-STORE-V1",
            "pending": {
                key: value["structural_record_hash72"]
                for key, value in sorted(self._pending.items())
            },
            "admitted": {
                key: {
                    "structural_record_hash72": value["structural_record_hash72"],
                    "purge_receipt_hash72": value["purge_receipt_hash72"],
                }
                for key, value in sorted(self._admitted.items())
            },
            "quarantined": _copy(self._quarantined),
            "memory_root_hash72": self._root(),
            "authoritative_vector_store": False,
        }


class SourceTransaction:
    def __init__(self, candidate_record: Mapping[str, Any], source_bytes: bytes, store: DeterministicStructuralStore) -> None:
        self.candidate_record = _copy(candidate_record)
        self.store = store
        self._source_buffer = bytearray(source_bytes)
        self._observed_source_sha256 = sha256(source_bytes).hexdigest()
        expected = str(self.candidate_record.get("source_sha256", ""))
        candidate_hash216 = str(self.candidate_record.get("hash216", ""))
        self.transaction_id_hash72 = hash72_digest(
            {"domain": "HHS-P218-I3-SOURCE-TRANSACTION-ID-V1"},
            {
                "source_id": str(self.candidate_record.get("source_id", "")),
                "expected_source_sha256": expected,
                "observed_source_sha256": self._observed_source_sha256,
                "candidate_hash216": candidate_hash216,
            },
        )
        self.phase = TransactionPhase.STAGED
        self._events: list[dict[str, Any]] = []
        self._structural_record: dict[str, Any] | None = None
        self._structural_record_hash72: str | None = None
        self._purge_receipt: dict[str, Any] | None = None
        self._closure_receipt: dict[str, Any] | None = None
        self._event("STAGED", {
            "source_sha256": self._observed_source_sha256,
            "source_byte_count": len(source_bytes),
            "candidate_hash216": candidate_hash216,
            "verbatim_source_serialized": False,
        })
        if expected != self._observed_source_sha256:
            self._reject("P218_SOURCE_CHECKSUM_MISMATCH")

    @classmethod
    def begin(
        cls,
        candidate: Any,
        source_text: str | bytes,
        *,
        store: DeterministicStructuralStore | None = None,
    ) -> "SourceTransaction":
        raw = source_text if isinstance(source_text, bytes) else source_text.encode("utf-8")
        return cls(_candidate_record(candidate), raw, store or DeterministicStructuralStore())

    def _event(self, name: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        previous = None if not self._events else self._events[-1]["event_hash72"]
        body = {
            "schema": "HHS-P218-I3-TRANSACTION-EVENT-V1",
            "transaction_id_hash72": self.transaction_id_hash72,
            "ordinal": len(self._events),
            "event": name,
            "previous_event_hash72": previous,
            "payload": _copy(payload),
        }
        record = {
            **body,
            "event_hash72": hash72_digest({"domain": "HHS-P218-I3-TRANSACTION-EVENT-V1"}, body),
        }
        self._events.append(record)
        return record

    def _purge_buffer(self, reason: str) -> dict[str, Any]:
        count = len(self._source_buffer)
        for index in range(count):
            self._source_buffer[index] = 0
        zeroized = all(value == 0 for value in self._source_buffer)
        zeroized_sha256 = sha256(bytes(self._source_buffer)).hexdigest()
        self._source_buffer.clear()
        payload = {
            "schema": "HHS-P218-I3-MANAGED-BUFFER-PURGE-V1",
            "transaction_id_hash72": self.transaction_id_hash72,
            "reason": reason,
            "source_sha256": self._observed_source_sha256,
            "source_byte_count": count,
            "managed_buffer_zeroized": zeroized,
            "zeroized_buffer_sha256": zeroized_sha256,
            "managed_buffer_length_after": len(self._source_buffer),
            "managed_buffer_cleared": len(self._source_buffer) == 0,
            "verbatim_source_retained": False,
            "physical_memory_erasure_claimed": False,
        }
        payload["purge_receipt_hash72"] = hash72_digest(
            {"domain": "HHS-P218-I3-MANAGED-BUFFER-PURGE-V1"}, payload
        )
        self._purge_receipt = payload
        return payload

    def _reject(self, reason: str) -> None:
        purge = self._purge_buffer(reason)
        self.phase = TransactionPhase.REJECTED
        self._event("REJECTED", {
            "reason": reason,
            "purge_receipt_hash72": purge["purge_receipt_hash72"],
            "managed_buffer_cleared": True,
        })

    def quarantine(self, reason: str) -> dict[str, Any]:
        if self.phase in (TransactionPhase.CLOSED, TransactionPhase.QUARANTINED, TransactionPhase.REJECTED):
            raise Pass218TransactionStateError("P218_TRANSACTION_TERMINAL")
        store_receipt = self.store.quarantine(self.transaction_id_hash72, reason=reason)
        purge = self._purge_buffer(reason)
        self.phase = TransactionPhase.QUARANTINED
        return self._event("QUARANTINED", {
            "reason": reason,
            "purge_receipt_hash72": purge["purge_receipt_hash72"],
            "structural_record_hash72": None if store_receipt is None else store_receipt.structural_record_hash72,
            "managed_buffer_cleared": True,
        })

    def validate(self) -> dict[str, Any]:
        if self.phase == TransactionPhase.REJECTED:
            raise Pass218TransactionValidationError("P218_TRANSACTION_REJECTED")
        if self.phase != TransactionPhase.STAGED:
            raise Pass218TransactionStateError("P218_VALIDATE_REQUIRES_STAGED")
        record = self.candidate_record
        problems: list[str] = []
        expected_sha = str(record.get("source_sha256", ""))
        if not _valid_sha256(expected_sha) or expected_sha != self._observed_source_sha256:
            problems.append("P218_CANDIDATE_SOURCE_SHA256_INVALID")
        candidate_hash216 = str(record.get("hash216", ""))
        if not _valid_hash216(candidate_hash216):
            problems.append("P218_CANDIDATE_HASH216_INVALID")
        elif candidate_hash216 != "".join((
            str(record.get("genesis_seed_hash72", "")),
            str(record.get("hydration_hash72", "")),
            str(record.get("validation_hash72", "")),
        )):
            problems.append("P218_CANDIDATE_HASH216_SEMANTICS_MISMATCH")
        for key in (
            "verbatim_source_retained",
            "source_text_retained",
            "truth_promotion",
            "action_authority_minted",
            "authoritative_vector_store_promotion",
            "authoritative_float_weights",
        ):
            if record.get(key) is not False:
                problems.append("P218_FORBIDDEN_AUTHORITY_FLAG:" + key)
        forbidden = _forbidden_verbatim_fields(record)
        if forbidden:
            problems.append("P218_VERBATIM_FIELD:" + ",".join(forbidden))
        if _source_embedded(record, bytes(self._source_buffer)):
            problems.append("P218_SOURCE_TEXT_EMBEDDED")
        if not isinstance(record.get("beats"), list) or not record["beats"]:
            problems.append("P218_CANDIDATE_BEATS_EMPTY")
        if problems:
            reason = "|".join(sorted(problems))
            self.quarantine(reason)
            raise Pass218TransactionValidationError(reason)
        self.phase = TransactionPhase.VALIDATED
        return self._event("VALIDATED", {
            "candidate_hash216": candidate_hash216,
            "source_sha256": expected_sha,
            "truth_promotion": False,
            "action_authority_minted": False,
            "authoritative_vector_store_promotion": False,
        })

    def _structural_payload(self) -> dict[str, Any]:
        record = self.candidate_record
        return {
            "schema": "HHS-P218-I3-STRUCTURAL-MEMORY-COMMIT-V1",
            "transaction_version": PASS218_SOURCE_TRANSACTION_VERSION,
            "transaction_id_hash72": self.transaction_id_hash72,
            "source_id": record["source_id"],
            "source_sha256": record["source_sha256"],
            "source_epistemic_class": record["source_epistemic_class"],
            "genesis_seed_hash72": record["genesis_seed_hash72"],
            "grammar_rule_set_hash72": record["grammar_rule_set_hash72"],
            "hydration_hash72": record["hydration_hash72"],
            "validation_hash72": record["validation_hash72"],
            "candidate_hash216": record["hash216"],
            "beats": _copy(record["beats"]),
            "verbatim_source_retained": False,
            "source_text_retained": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "authoritative_vector_store_promotion": False,
            "authoritative_float_weights": False,
            "admission_status": "PENDING_PURGE_PROOF",
        }

    def commit_structural(self) -> dict[str, Any]:
        if self.phase != TransactionPhase.VALIDATED:
            raise Pass218TransactionStateError("P218_STRUCTURAL_COMMIT_REQUIRES_VALIDATED")
        self._structural_record = self._structural_payload()
        store_receipt = self.store.prepare(self.transaction_id_hash72, self._structural_record)
        self._structural_record_hash72 = store_receipt.structural_record_hash72
        self.phase = TransactionPhase.STRUCTURAL_COMMITTED
        return self._event("STRUCTURAL_COMMITTED", {
            **store_receipt.to_record(),
            "admission_status": "PENDING_PURGE_PROOF",
            "verbatim_source_retained": False,
        })

    def purge_and_close(self) -> dict[str, Any]:
        if self.phase != TransactionPhase.STRUCTURAL_COMMITTED:
            raise Pass218TransactionStateError("P218_PURGE_CLOSE_REQUIRES_STRUCTURAL_COMMIT")
        if self._structural_record is None or self._structural_record_hash72 is None:
            raise Pass218TransactionStateError("P218_STRUCTURAL_COMMIT_STATE_MISSING")
        purge = self._purge_buffer("P218_SUCCESSFUL_STRUCTURAL_COMMIT")
        if not purge["managed_buffer_zeroized"] or not purge["managed_buffer_cleared"]:
            self.store.quarantine(self.transaction_id_hash72, reason="P218_MANAGED_BUFFER_PURGE_FAILED")
            self.phase = TransactionPhase.QUARANTINED
            raise Pass218TransactionValidationError("P218_MANAGED_BUFFER_PURGE_FAILED")
        store_receipt = self.store.admit(
            self.transaction_id_hash72,
            purge_receipt_hash72=purge["purge_receipt_hash72"],
        )
        closure = {
            "schema": "HHS-P218-I3-SOURCE-TRANSACTION-CLOSURE-V1",
            "transaction_id_hash72": self.transaction_id_hash72,
            "candidate_hydration_hash72": self.candidate_record["hydration_hash72"],
            "structural_record_hash72": store_receipt.structural_record_hash72,
            "purge_receipt_hash72": purge["purge_receipt_hash72"],
            "memory_root_hash72": store_receipt.memory_root_hash72,
            "managed_buffer_zeroized": True,
            "managed_buffer_cleared": True,
            "verbatim_source_retained": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "authoritative_vector_store_promotion": False,
            "physical_memory_erasure_claimed": False,
        }
        closure_hash72 = hash72_digest({"domain": "HHS-P218-I3-SOURCE-TRANSACTION-CLOSURE-V1"}, closure)
        transaction_hash216 = (
            str(self.candidate_record["hydration_hash72"])
            + store_receipt.structural_record_hash72
            + closure_hash72
        )
        if not _valid_hash216(transaction_hash216):
            raise Pass218TransactionValidationError("P218_TRANSACTION_HASH216_INVALID")
        self.phase = TransactionPhase.CLOSED
        payload = {
            **closure,
            "closure_hash72": closure_hash72,
            "transaction_hash216": transaction_hash216,
            "hash216_semantics": [
                "HYDRATION_CANDIDATE",
                "STRUCTURAL_COMMIT",
                "PURGE_ADMISSION_RECEIPT",
            ],
        }
        self._event("CLOSED", payload)
        self._closure_receipt = _copy(payload)
        return _copy(payload)

    def commit_and_purge(self) -> dict[str, Any]:
        if self.phase == TransactionPhase.STAGED:
            self.validate()
        if self.phase == TransactionPhase.VALIDATED:
            self.commit_structural()
        return self.purge_and_close()

    def recover_interrupted_commit(self) -> dict[str, Any]:
        if self.phase != TransactionPhase.STRUCTURAL_COMMITTED:
            raise Pass218TransactionStateError("P218_RECOVERY_REQUIRES_UNCLOSED_STRUCTURAL_COMMIT")
        receipt = self.store.quarantine(
            self.transaction_id_hash72,
            reason="P218_PURGE_PROOF_ABSENT_AFTER_RESTART",
        )
        self._source_buffer.clear()
        self.phase = TransactionPhase.QUARANTINED
        return self._event("RECOVERY_QUARANTINE", {
            "reason": "P218_PURGE_PROOF_ABSENT_AFTER_RESTART",
            "structural_record_hash72": None if receipt is None else receipt.structural_record_hash72,
            "verbatim_source_rehydrated": False,
            "authoritative_vector_store_promotion": False,
        })

    def resume_source(self, source_text: str | bytes) -> None:
        if self.phase not in (TransactionPhase.STAGED, TransactionPhase.VALIDATED):
            raise Pass218TransactionStateError("P218_RESUME_SOURCE_PHASE_INVALID")
        raw = source_text if isinstance(source_text, bytes) else source_text.encode("utf-8")
        if sha256(raw).hexdigest() != self._observed_source_sha256:
            raise Pass218TransactionValidationError("P218_RESUME_SOURCE_CHECKSUM_MISMATCH")
        self._source_buffer = bytearray(raw)

    def verify_journal(self) -> bool:
        previous = None
        for ordinal, event in enumerate(self._events):
            if event.get("ordinal") != ordinal or event.get("previous_event_hash72") != previous:
                return False
            body = {key: value for key, value in event.items() if key != "event_hash72"}
            expected = hash72_digest({"domain": "HHS-P218-I3-TRANSACTION-EVENT-V1"}, body)
            if event.get("event_hash72") != expected:
                return False
            previous = event["event_hash72"]
        return True

    def snapshot(self) -> dict[str, Any]:
        body = {
            "schema": "HHS-P218-I3-SOURCE-TRANSACTION-SNAPSHOT-V1",
            "transaction_version": PASS218_SOURCE_TRANSACTION_VERSION,
            "transaction_id_hash72": self.transaction_id_hash72,
            "phase": int(self.phase),
            "observed_source_sha256": self._observed_source_sha256,
            "candidate_record": _copy(self.candidate_record),
            "structural_record": _copy(self._structural_record),
            "structural_record_hash72": self._structural_record_hash72,
            "purge_receipt": _copy(self._purge_receipt),
            "closure_receipt": _copy(self._closure_receipt),
            "events": _copy(self._events),
            "source_buffer_serialized": False,
            "verbatim_source_retained": False,
        }
        return {
            **body,
            "snapshot_hash72": hash72_digest({"domain": "HHS-P218-I3-SOURCE-TRANSACTION-SNAPSHOT-V1"}, body),
        }

    @classmethod
    def restore(
        cls,
        snapshot: Mapping[str, Any],
        *,
        store: DeterministicStructuralStore | None = None,
    ) -> "SourceTransaction":
        copied = _copy(snapshot)
        supplied_hash72 = str(copied.pop("snapshot_hash72", ""))
        expected_hash72 = hash72_digest({"domain": "HHS-P218-I3-SOURCE-TRANSACTION-SNAPSHOT-V1"}, copied)
        if supplied_hash72 != expected_hash72:
            raise Pass218TransactionValidationError("P218_TRANSACTION_SNAPSHOT_HASH_MISMATCH")
        obj = cls.__new__(cls)
        obj.candidate_record = copied["candidate_record"]
        obj.store = store or DeterministicStructuralStore()
        obj._source_buffer = bytearray()
        obj._observed_source_sha256 = str(copied["observed_source_sha256"])
        obj.transaction_id_hash72 = str(copied["transaction_id_hash72"])
        obj.phase = TransactionPhase(int(copied["phase"]))
        obj._events = copied["events"]
        obj._structural_record = copied.get("structural_record")
        obj._structural_record_hash72 = copied.get("structural_record_hash72")
        obj._purge_receipt = copied.get("purge_receipt")
        obj._closure_receipt = copied.get("closure_receipt")
        if not obj.verify_journal():
            raise Pass218TransactionValidationError("P218_TRANSACTION_JOURNAL_INVALID")
        if obj.phase == TransactionPhase.STRUCTURAL_COMMITTED:
            if obj._structural_record is None or obj._structural_record_hash72 is None:
                raise Pass218TransactionValidationError("P218_RESTART_STRUCTURAL_STATE_MISSING")
            receipt = obj.store.prepare(obj.transaction_id_hash72, obj._structural_record)
            if receipt.structural_record_hash72 != obj._structural_record_hash72:
                obj.store.quarantine(obj.transaction_id_hash72, reason="P218_RESTART_STRUCTURAL_HASH_MISMATCH")
                raise Pass218TransactionValidationError("P218_RESTART_STRUCTURAL_HASH_MISMATCH")
        elif obj.phase == TransactionPhase.CLOSED:
            if (
                obj._structural_record is None
                or obj._structural_record_hash72 is None
                or not isinstance(obj._purge_receipt, Mapping)
            ):
                raise Pass218TransactionValidationError("P218_REPLAY_CLOSURE_STATE_MISSING")
            obj.store.replay_admitted(
                obj.transaction_id_hash72,
                obj._structural_record,
                structural_record_hash72=obj._structural_record_hash72,
                purge_receipt_hash72=str(obj._purge_receipt["purge_receipt_hash72"]),
            )
        return obj

    @property
    def managed_source_bytes(self) -> int:
        return len(self._source_buffer)

    @property
    def purge_receipt(self) -> dict[str, Any] | None:
        return _copy(self._purge_receipt)

    @property
    def closure_receipt(self) -> dict[str, Any] | None:
        return _copy(self._closure_receipt)

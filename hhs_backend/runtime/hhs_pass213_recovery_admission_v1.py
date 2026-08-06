"""Pass 213 iteration 2: Pass 212 recovery-gated compiled-ROM admission.

A compiled-ROM entry is serialized once, protected by the Pass 212 physical
shard layer, authenticated as one Pass 213 carrier, and admitted only after:

    Pass 212 carrier validation
    -> physical erasure reconstruction
    -> recovered payload Hash216 validation
    -> canonical JSON decoding
    -> immutable compiled-entry Hash216 validation
    -> keyed recovery-admission validation
    -> compiled-ROM insertion

The external carrier may lose up to the inherited Pass 212 erasure budget.
Malformed, altered, over-budget, or unauthenticated carriers fail before the
compiled entry reaches the canonical ROM index.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import hmac
import json
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass212_full_hydration_recovery_v1 import (
    Pass212Error,
    ProtectedPayload,
    get_pass212_runtime,
)
from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    CONTRACT,
    CompiledROMEntry,
    CompiledROMStore,
    Pass213ValidationError,
    canonical_bytes,
    hash216,
)

ITERATION = 2
CARRIER_SCHEMA = "HHS_PASS_213_COMPILED_ROM_CARRIER_V1"
ENTRY_SCHEMA = "HHS_PASS_213_COMPILED_ROM_ENTRY_SERIALIZATION_V1"
ADMISSION_SCHEMA = "HHS_PASS_213_RECOVERED_ROM_ADMISSION_V1"


class Pass213RecoveryAdmissionError(Pass213ValidationError):
    """Raised when physical recovery or canonical ROM admission fails."""


def _require_key(key: bytes) -> bytes:
    if not isinstance(key, bytes) or len(key) < 32:
        raise Pass213RecoveryAdmissionError("PASS213_ADMISSION_KEY_TOO_SHORT")
    return key


def _authentication_tag(key: bytes, domain: str, value: Mapping[str, Any]) -> str:
    key = _require_key(key)
    domain_bytes = domain.encode("utf-8")
    payload = canonical_bytes(value)
    framed = (
        b"HHS-P213-RECOVERY-ADMISSION-HMAC-SHA256-V1\0"
        + len(domain_bytes).to_bytes(2, "big")
        + domain_bytes
        + len(payload).to_bytes(8, "big")
        + payload
    )
    return hmac.new(key, framed, sha256).hexdigest()


def _validate_hash216(value: str, error_code: str) -> None:
    if not isinstance(value, str) or len(value) != 64:
        raise Pass213RecoveryAdmissionError(f"{error_code}_LENGTH_INVALID")
    try:
        int(value, 16)
    except ValueError as exc:
        raise Pass213RecoveryAdmissionError(
            f"{error_code}_FORMAT_INVALID"
        ) from exc


def serialize_compiled_entry(entry: CompiledROMEntry) -> bytes:
    entry.validate()
    return canonical_bytes(
        {
            "schema": ENTRY_SCHEMA,
            **entry.unsigned_payload(),
            "entry_hash216": entry.entry_hash216,
        }
    )


def deserialize_compiled_entry(payload: bytes) -> CompiledROMEntry:
    try:
        value = json.loads(bytes(payload).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Pass213RecoveryAdmissionError(
            "PASS213_RECOVERED_ENTRY_SERIALIZATION_INVALID"
        ) from exc
    if not isinstance(value, Mapping) or value.get("schema") != ENTRY_SCHEMA:
        raise Pass213RecoveryAdmissionError(
            "PASS213_RECOVERED_ENTRY_SCHEMA_INVALID"
        )
    required = {
        "schema",
        "operation_id",
        "canonical_operation",
        "constraints",
        "vm81_cell_id",
        "operation_slot",
        "g243_control_id",
        "native_dispatch_id",
        "kernel_policy_hash216",
        "creation_group_sequence",
        "creation_open_boundary_hash216",
        "creation_close_boundary_hash216",
        "closure_path_root_hash216",
        "closure_position",
        "parent_hash216",
        "entry_hash216",
    }
    if set(value) != required:
        raise Pass213RecoveryAdmissionError(
            "PASS213_RECOVERED_ENTRY_FIELDS_INVALID"
        )
    entry = CompiledROMEntry(
        operation_id=str(value["operation_id"]),
        canonical_operation=value["canonical_operation"],
        constraints=value["constraints"],
        vm81_cell_id=int(value["vm81_cell_id"]),
        operation_slot=int(value["operation_slot"]),
        g243_control_id=int(value["g243_control_id"]),
        native_dispatch_id=str(value["native_dispatch_id"]),
        kernel_policy_hash216=str(value["kernel_policy_hash216"]),
        creation_group_sequence=int(value["creation_group_sequence"]),
        creation_open_boundary_hash216=str(
            value["creation_open_boundary_hash216"]
        ),
        creation_close_boundary_hash216=str(
            value["creation_close_boundary_hash216"]
        ),
        closure_path_root_hash216=str(value["closure_path_root_hash216"]),
        closure_position=int(value["closure_position"]),
        parent_hash216=str(value["parent_hash216"]),
        entry_hash216=str(value["entry_hash216"]),
    )
    entry.validate()
    return entry


@dataclass(frozen=True)
class CompiledROMCarrier:
    """Pass 212 protected bytes plus Pass 213 keyed carrier authority."""

    expected_entry_hash216: str
    recovered_payload_hash216: str
    protected: ProtectedPayload
    carrier_root_hash216: str
    authentication_tag: str

    def root_payload(self) -> Mapping[str, Any]:
        return {
            "schema": CARRIER_SCHEMA,
            "contract": CONTRACT,
            "iteration": ITERATION,
            "expected_entry_hash216": self.expected_entry_hash216,
            "recovered_payload_hash216": self.recovered_payload_hash216,
            "protected_root216": self.protected.root216,
            "protected_receipt_hash72": self.protected.receipt_hash72,
            "protected_original_length": self.protected.original_length,
            "protected_data_shard_count": self.protected.data_shard_count,
            "protected_stripe_count": self.protected.stripe_count,
        }

    def authenticated_payload(self) -> Mapping[str, Any]:
        return {
            **self.root_payload(),
            "carrier_root_hash216": self.carrier_root_hash216,
        }

    def validate_envelope(self, admission_key: bytes) -> None:
        _validate_hash216(
            self.expected_entry_hash216,
            "PASS213_EXPECTED_ENTRY_HASH216",
        )
        _validate_hash216(
            self.recovered_payload_hash216,
            "PASS213_RECOVERED_PAYLOAD_HASH216",
        )
        _validate_hash216(
            self.carrier_root_hash216,
            "PASS213_CARRIER_ROOT_HASH216",
        )
        expected_root = hash216(
            "compiled-rom-carrier-root",
            canonical_bytes(self.root_payload()),
        )
        if not hmac.compare_digest(self.carrier_root_hash216, expected_root):
            raise Pass213RecoveryAdmissionError(
                "PASS213_CARRIER_ROOT_MISMATCH"
            )
        expected_tag = _authentication_tag(
            admission_key,
            "COMPILED-ROM-CARRIER",
            self.authenticated_payload(),
        )
        if not hmac.compare_digest(self.authentication_tag, expected_tag):
            raise Pass213RecoveryAdmissionError(
                "PASS213_CARRIER_AUTHENTICATION_FAILED"
            )

    def to_dict(self, include_payloads: bool = True) -> dict[str, Any]:
        return {
            "schema": CARRIER_SCHEMA,
            "contract": CONTRACT,
            "iteration": ITERATION,
            "expected_entry_hash216": self.expected_entry_hash216,
            "recovered_payload_hash216": self.recovered_payload_hash216,
            "protected": self.protected.to_dict(include_payloads),
            "carrier_root_hash216": self.carrier_root_hash216,
            "authentication_tag": self.authentication_tag,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "CompiledROMCarrier":
        if (
            value.get("schema") != CARRIER_SCHEMA
            or value.get("contract") != CONTRACT
            or int(value.get("iteration", -1)) != ITERATION
        ):
            raise Pass213RecoveryAdmissionError(
                "PASS213_CARRIER_SCHEMA_INVALID"
            )
        return cls(
            expected_entry_hash216=str(value["expected_entry_hash216"]),
            recovered_payload_hash216=str(
                value["recovered_payload_hash216"]
            ),
            protected=ProtectedPayload.from_mapping(value["protected"]),
            carrier_root_hash216=str(value["carrier_root_hash216"]),
            authentication_tag=str(value["authentication_tag"]),
        )


def protect_compiled_rom_entry(
    entry: CompiledROMEntry,
    admission_key: bytes,
) -> CompiledROMCarrier:
    """Serialize and physically protect one immutable compiled-ROM entry."""

    _require_key(admission_key)
    payload = serialize_compiled_entry(entry)
    protected = get_pass212_runtime().protect_payload(payload)
    payload_hash = hash216("compiled-rom-recovered-payload", payload)
    unsigned = CompiledROMCarrier(
        expected_entry_hash216=entry.entry_hash216,
        recovered_payload_hash216=payload_hash,
        protected=protected,
        carrier_root_hash216="0" * 64,
        authentication_tag="",
    )
    root = hash216(
        "compiled-rom-carrier-root",
        canonical_bytes(unsigned.root_payload()),
    )
    rooted = CompiledROMCarrier(
        expected_entry_hash216=entry.entry_hash216,
        recovered_payload_hash216=payload_hash,
        protected=protected,
        carrier_root_hash216=root,
        authentication_tag="",
    )
    tag = _authentication_tag(
        admission_key,
        "COMPILED-ROM-CARRIER",
        rooted.authenticated_payload(),
    )
    return CompiledROMCarrier(
        expected_entry_hash216=entry.entry_hash216,
        recovered_payload_hash216=payload_hash,
        protected=protected,
        carrier_root_hash216=root,
        authentication_tag=tag,
    )


@dataclass(frozen=True)
class RecoveredROMAdmission:
    """Validated proof that recovery completed before ROM interpretation."""

    entry: CompiledROMEntry
    carrier_root_hash216: str
    protected_root216: str
    protected_receipt_hash72: str
    recovered_payload_hash216: str
    recovery_outcome: str
    recovered_shard_refs: tuple[str, ...]
    admission_root_hash216: str
    authentication_tag: str

    def root_payload(self) -> Mapping[str, Any]:
        return {
            "schema": ADMISSION_SCHEMA,
            "contract": CONTRACT,
            "iteration": ITERATION,
            "entry_hash216": self.entry.entry_hash216,
            "carrier_root_hash216": self.carrier_root_hash216,
            "protected_root216": self.protected_root216,
            "protected_receipt_hash72": self.protected_receipt_hash72,
            "recovered_payload_hash216": self.recovered_payload_hash216,
            "recovery_outcome": self.recovery_outcome,
            "recovered_shard_refs": list(self.recovered_shard_refs),
        }

    def authenticated_payload(self) -> Mapping[str, Any]:
        return {
            **self.root_payload(),
            "admission_root_hash216": self.admission_root_hash216,
        }

    def validate(self, admission_key: bytes) -> None:
        self.entry.validate()
        if self.recovery_outcome not in {"INTACT", "RECOVERED"}:
            raise Pass213RecoveryAdmissionError(
                "PASS213_RECOVERY_OUTCOME_INVALID"
            )
        if self.recovery_outcome == "INTACT" and self.recovered_shard_refs:
            raise Pass213RecoveryAdmissionError(
                "PASS213_INTACT_ADMISSION_HAS_RECOVERED_SHARDS"
            )
        if self.recovery_outcome == "RECOVERED" and not self.recovered_shard_refs:
            raise Pass213RecoveryAdmissionError(
                "PASS213_RECOVERED_ADMISSION_HAS_NO_SHARDS"
            )
        for value, code in (
            (self.carrier_root_hash216, "PASS213_CARRIER_ROOT_HASH216"),
            (self.protected_root216, "PASS213_PROTECTED_ROOT216"),
            (
                self.recovered_payload_hash216,
                "PASS213_RECOVERED_PAYLOAD_HASH216",
            ),
            (self.admission_root_hash216, "PASS213_ADMISSION_ROOT_HASH216"),
        ):
            _validate_hash216(value, code)
        expected_root = hash216(
            "recovered-rom-admission-root",
            canonical_bytes(self.root_payload()),
        )
        if not hmac.compare_digest(self.admission_root_hash216, expected_root):
            raise Pass213RecoveryAdmissionError(
                "PASS213_ADMISSION_ROOT_MISMATCH"
            )
        expected_tag = _authentication_tag(
            admission_key,
            "RECOVERED-ROM-ADMISSION",
            self.authenticated_payload(),
        )
        if not hmac.compare_digest(self.authentication_tag, expected_tag):
            raise Pass213RecoveryAdmissionError(
                "PASS213_ADMISSION_AUTHENTICATION_FAILED"
            )


def inspect_and_correct_carrier(
    carrier: CompiledROMCarrier | Mapping[str, Any],
    admission_key: bytes,
) -> RecoveredROMAdmission:
    """Recover, hash-validate, then and only then deserialize one entry."""

    value = (
        carrier
        if isinstance(carrier, CompiledROMCarrier)
        else CompiledROMCarrier.from_mapping(carrier)
    )
    value.validate_envelope(admission_key)
    missing_refs = tuple(
        sorted(shard.ref for shard in value.protected.shards if shard.payload is None)
    )
    try:
        recovered_payload = get_pass212_runtime().recover_payload(value.protected)
    except Pass212Error as exc:
        raise Pass213RecoveryAdmissionError(
            f"PASS213_PASS212_RECOVERY_REJECTED:{exc}"
        ) from exc

    recovered_hash = hash216(
        "compiled-rom-recovered-payload",
        recovered_payload,
    )
    if not hmac.compare_digest(
        recovered_hash,
        value.recovered_payload_hash216,
    ):
        raise Pass213RecoveryAdmissionError(
            "PASS213_RECOVERED_PAYLOAD_HASH_MISMATCH"
        )

    # Canonical decoding is intentionally below Pass 212 recovery and the
    # reconstructed-payload Hash216 gate.
    entry = deserialize_compiled_entry(recovered_payload)
    if not hmac.compare_digest(
        entry.entry_hash216,
        value.expected_entry_hash216,
    ):
        raise Pass213RecoveryAdmissionError(
            "PASS213_RECOVERED_ENTRY_HASH_MISMATCH"
        )

    outcome = "RECOVERED" if missing_refs else "INTACT"
    root_payload = {
        "schema": ADMISSION_SCHEMA,
        "contract": CONTRACT,
        "iteration": ITERATION,
        "entry_hash216": entry.entry_hash216,
        "carrier_root_hash216": value.carrier_root_hash216,
        "protected_root216": value.protected.root216,
        "protected_receipt_hash72": value.protected.receipt_hash72,
        "recovered_payload_hash216": recovered_hash,
        "recovery_outcome": outcome,
        "recovered_shard_refs": list(missing_refs),
    }
    admission_root = hash216(
        "recovered-rom-admission-root",
        canonical_bytes(root_payload),
    )
    authenticated = {
        **root_payload,
        "admission_root_hash216": admission_root,
    }
    admission = RecoveredROMAdmission(
        entry=entry,
        carrier_root_hash216=value.carrier_root_hash216,
        protected_root216=value.protected.root216,
        protected_receipt_hash72=value.protected.receipt_hash72,
        recovered_payload_hash216=recovered_hash,
        recovery_outcome=outcome,
        recovered_shard_refs=missing_refs,
        admission_root_hash216=admission_root,
        authentication_tag=_authentication_tag(
            admission_key,
            "RECOVERED-ROM-ADMISSION",
            authenticated,
        ),
    )
    admission.validate(admission_key)
    return admission


class RecoveryGatedCompiledROMStore:
    """Canonical ROM store whose insertion surface accepts recovery proof only."""

    def __init__(self, admission_key: bytes) -> None:
        self._admission_key = _require_key(admission_key)
        self._store = CompiledROMStore()
        self._admissions: dict[str, str] = {}

    def admit(self, admission: RecoveredROMAdmission) -> str:
        if not isinstance(admission, RecoveredROMAdmission):
            raise Pass213RecoveryAdmissionError(
                "PASS213_RECOVERY_ADMISSION_REQUIRED"
            )
        admission.validate(self._admission_key)
        entry_hash = self._store.insert(admission.entry)
        existing = self._admissions.get(entry_hash)
        if existing is not None and existing != admission.admission_root_hash216:
            raise Pass213RecoveryAdmissionError(
                "PASS213_ENTRY_ADMISSION_ROOT_CONFLICT"
            )
        self._admissions[entry_hash] = admission.admission_root_hash216
        return entry_hash

    def inspect_correct_and_admit(
        self,
        carrier: CompiledROMCarrier | Mapping[str, Any],
    ) -> RecoveredROMAdmission:
        admission = inspect_and_correct_carrier(
            carrier,
            self._admission_key,
        )
        self.admit(admission)
        return admission

    def lookup_hash216(self, entry_hash216: str) -> CompiledROMEntry:
        entry = self._store.lookup_hash216(entry_hash216)
        if entry_hash216 not in self._admissions:
            raise Pass213RecoveryAdmissionError(
                "PASS213_ENTRY_HAS_NO_RECOVERY_ADMISSION"
            )
        return entry

    def lookup_operation(self, operation_id: str) -> CompiledROMEntry:
        entry = self._store.lookup_operation(operation_id)
        return self.lookup_hash216(entry.entry_hash216)

    def inventory_root(self) -> str:
        payload = {
            "compiled_rom_root": self._store.inventory_root(),
            "admission_roots": [
                [entry_hash, self._admissions[entry_hash]]
                for entry_hash in sorted(self._admissions)
            ],
        }
        return hash216(
            "recovery-gated-compiled-rom-inventory",
            canonical_bytes(payload),
        )

    def __len__(self) -> int:
        return len(self._store)


__all__ = [
    "ITERATION",
    "CARRIER_SCHEMA",
    "ENTRY_SCHEMA",
    "ADMISSION_SCHEMA",
    "Pass213RecoveryAdmissionError",
    "CompiledROMCarrier",
    "RecoveredROMAdmission",
    "RecoveryGatedCompiledROMStore",
    "serialize_compiled_entry",
    "deserialize_compiled_entry",
    "protect_compiled_rom_entry",
    "inspect_and_correct_carrier",
]

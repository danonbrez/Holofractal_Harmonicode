"""Pass 213 iteration 3: recovery-gated compiled ROM backed by native arenas."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    CompiledROMEntry,
    canonical_bytes,
    hash216,
)
from hhs_backend.runtime.hhs_pass213_recovery_admission_v1 import (
    CompiledROMCarrier,
    RecoveredROMAdmission,
    deserialize_compiled_entry,
    inspect_and_correct_carrier,
    serialize_compiled_entry,
)
from hhs_backend.runtime.hhs_pass213_secure_memory_v1 import (
    NativeSecureArena,
    Pass213SecureMemoryError,
    SecureMemoryReceipt,
)

ITERATION = 3
RUNTIME_CLASSIFICATION = "HHS_PASS_213_NATIVE_PROTECTED_COMPILED_ROM_ITERATION3"


@dataclass(frozen=True)
class ProtectedCompiledROMRecord:
    entry_hash216: str
    operation_id: str
    admission_root_hash216: str
    arena_id_hash216: str
    payload_length: int
    final_memory_receipt_hash216: str


class NativeProtectedCompiledROMStore:
    """Compiled ROM whose canonical entry bytes reside in sealed native arenas."""

    def __init__(
        self,
        *,
        library_path: str | Path,
        admission_key: bytes,
        memory_root_key: bytes,
        owner_id: str,
    ) -> None:
        if not isinstance(admission_key, bytes) or len(admission_key) < 32:
            raise Pass213SecureMemoryError(
                "PASS213_PROTECTED_ROM_ADMISSION_KEY_TOO_SHORT"
            )
        if not isinstance(memory_root_key, bytes) or len(memory_root_key) < 32:
            raise Pass213SecureMemoryError(
                "PASS213_PROTECTED_ROM_MEMORY_KEY_TOO_SHORT"
            )
        if not owner_id:
            raise Pass213SecureMemoryError(
                "PASS213_PROTECTED_ROM_OWNER_INVALID"
            )
        self._library_path = str(Path(library_path))
        self._admission_key = admission_key
        self._memory_root_key = memory_root_key
        self._owner_id = owner_id
        self._allocation_sequence = 0
        self._arenas: dict[str, NativeSecureArena] = {}
        self._records: dict[str, ProtectedCompiledROMRecord] = {}
        self._operation_index: dict[str, str] = {}
        self._closed = False

    def _require_open(self) -> None:
        if self._closed:
            raise Pass213SecureMemoryError(
                "PASS213_PROTECTED_COMPILED_ROM_STORE_CLOSED"
            )

    def admit(
        self,
        admission: RecoveredROMAdmission,
    ) -> ProtectedCompiledROMRecord:
        self._require_open()
        if not isinstance(admission, RecoveredROMAdmission):
            raise Pass213SecureMemoryError(
                "PASS213_RECOVERED_ROM_ADMISSION_REQUIRED"
            )
        admission.validate(self._admission_key)
        entry = admission.entry
        entry.validate()

        existing = self._records.get(entry.entry_hash216)
        if existing is not None:
            if existing.admission_root_hash216 != admission.admission_root_hash216:
                raise Pass213SecureMemoryError(
                    "PASS213_PROTECTED_ROM_ADMISSION_CONFLICT"
                )
            return existing
        if entry.operation_id in self._operation_index:
            raise Pass213SecureMemoryError(
                "PASS213_PROTECTED_ROM_OPERATION_ALREADY_COMPILED"
            )

        payload = serialize_compiled_entry(entry)
        self._allocation_sequence += 1
        arena = NativeSecureArena(
            library_path=self._library_path,
            requested_size=len(payload),
            owner_id=(
                f"{self._owner_id}:{entry.entry_hash216}:"
                f"{admission.admission_root_hash216}"
            ),
            root_key=self._memory_root_key,
            allocation_sequence=self._allocation_sequence,
        )
        try:
            arena.write(payload)
            arena.seal()
            recovered = deserialize_compiled_entry(
                arena.read_internal(offset=0, length=len(payload))
            )
            if recovered.entry_hash216 != entry.entry_hash216:
                raise Pass213SecureMemoryError(
                    "PASS213_PROTECTED_ROM_POST_WRITE_HASH_MISMATCH"
                )
            record = ProtectedCompiledROMRecord(
                entry_hash216=entry.entry_hash216,
                operation_id=entry.operation_id,
                admission_root_hash216=admission.admission_root_hash216,
                arena_id_hash216=arena.arena_id_hash216,
                payload_length=len(payload),
                final_memory_receipt_hash216=arena.receipts[-1].receipt_hash216,
            )
            self._arenas[entry.entry_hash216] = arena
            self._records[entry.entry_hash216] = record
            self._operation_index[entry.operation_id] = entry.entry_hash216
            return record
        except Exception:
            arena.close()
            raise
        finally:
            payload = b""

    def inspect_correct_protect_and_admit(
        self,
        carrier: CompiledROMCarrier | Mapping[str, Any],
    ) -> ProtectedCompiledROMRecord:
        admission = inspect_and_correct_carrier(
            carrier,
            self._admission_key,
        )
        return self.admit(admission)

    def lookup_hash216(self, entry_hash216: str) -> CompiledROMEntry:
        self._require_open()
        try:
            record = self._records[entry_hash216]
            arena = self._arenas[entry_hash216]
        except KeyError as exc:
            raise Pass213SecureMemoryError(
                "PASS213_PROTECTED_ROM_ENTRY_NOT_FOUND"
            ) from exc
        payload = arena.read_internal(
            offset=0,
            length=record.payload_length,
        )
        entry = deserialize_compiled_entry(payload)
        if (
            entry.entry_hash216 != record.entry_hash216
            or entry.operation_id != record.operation_id
        ):
            raise Pass213SecureMemoryError(
                "PASS213_PROTECTED_ROM_LOOKUP_INTEGRITY_MISMATCH"
            )
        return entry

    def lookup_operation(self, operation_id: str) -> CompiledROMEntry:
        self._require_open()
        try:
            entry_hash216 = self._operation_index[operation_id]
        except KeyError as exc:
            raise Pass213SecureMemoryError(
                "PASS213_PROTECTED_ROM_OPERATION_NOT_FOUND"
            ) from exc
        return self.lookup_hash216(entry_hash216)

    def inventory_root(self) -> str:
        self._require_open()
        payload = {
            "runtime_classification": RUNTIME_CLASSIFICATION,
            "entry_count": len(self._records),
            "records": [
                {
                    "entry_hash216": record.entry_hash216,
                    "operation_id": record.operation_id,
                    "admission_root_hash216": record.admission_root_hash216,
                    "arena_id_hash216": record.arena_id_hash216,
                    "payload_length": record.payload_length,
                    "final_memory_receipt_hash216": (
                        record.final_memory_receipt_hash216
                    ),
                }
                for _, record in sorted(self._records.items())
            ],
        }
        return hash216(
            "native-protected-compiled-rom-inventory",
            canonical_bytes(payload),
        )

    def close(self) -> tuple[SecureMemoryReceipt, ...]:
        if self._closed:
            return ()
        receipts: list[SecureMemoryReceipt] = []
        for entry_hash216 in sorted(self._arenas):
            receipt = self._arenas[entry_hash216].close()
            if receipt is not None:
                receipts.append(receipt)
        self._arenas.clear()
        self._records.clear()
        self._operation_index.clear()
        self._closed = True
        return tuple(receipts)

    def __len__(self) -> int:
        return len(self._records)

    def __enter__(self) -> "NativeProtectedCompiledROMStore":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()


__all__ = [
    "ITERATION",
    "RUNTIME_CLASSIFICATION",
    "ProtectedCompiledROMRecord",
    "NativeProtectedCompiledROMStore",
]

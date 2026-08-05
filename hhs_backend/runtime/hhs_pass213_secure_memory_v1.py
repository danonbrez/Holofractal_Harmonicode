"""Pass 213 iteration 3: native protected-memory arena wrapper.

The C arena allocates one non-executable data region between two PROT_NONE guard
pages, locks the data pages against swap, excludes them from core dumps and
fork inheritance, enforces a 256-bit owner token on every operation, supports
read-only sealing, explicitly zeroizes before release, and exposes no raw
address through this wrapper.

Lifecycle mutations emit deterministic, keyed receipts that bind ownership,
allocation sequence, content commitments, native mutation sequence, and the
previous receipt root.
"""
from __future__ import annotations

import ctypes
from dataclasses import dataclass
from hashlib import sha256
import hmac
from pathlib import Path
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    CONTRACT,
    canonical_bytes,
    hash216,
)

ITERATION = 3
RUNTIME_CLASSIFICATION = "HHS_PASS_213_NATIVE_SECURE_MEMORY_ARENA_ITERATION3"


class Pass213SecureMemoryError(RuntimeError):
    """Raised when a native secure-memory invariant fails."""


class _NativeStatus(ctypes.Structure):
    _fields_ = [
        ("requested_size", ctypes.c_size_t),
        ("usable_size", ctypes.c_size_t),
        ("mapping_size", ctypes.c_size_t),
        ("page_size", ctypes.c_size_t),
        ("mutation_sequence", ctypes.c_uint64),
        ("locked", ctypes.c_int),
        ("dontdump", ctypes.c_int),
        ("dontfork", ctypes.c_int),
        ("sealed", ctypes.c_int),
        ("zeroized", ctypes.c_int),
        ("guard_pages", ctypes.c_int),
    ]


@dataclass(frozen=True)
class SecureMemoryReceipt:
    sequence: int
    event: str
    arena_id_hash216: str
    previous_receipt_hash216: str
    native_mutation_sequence: int
    details: Mapping[str, Any]
    receipt_hash216: str
    authentication_tag: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_213_SECURE_MEMORY_RECEIPT_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "sequence": self.sequence,
            "event": self.event,
            "arena_id_hash216": self.arena_id_hash216,
            "previous_receipt_hash216": self.previous_receipt_hash216,
            "native_mutation_sequence": self.native_mutation_sequence,
            "details": dict(self.details),
            "receipt_hash216": self.receipt_hash216,
            "authentication_tag": self.authentication_tag,
        }


def _require_key(key: bytes) -> bytes:
    if not isinstance(key, bytes) or len(key) < 32:
        raise Pass213SecureMemoryError("PASS213_SECURE_MEMORY_KEY_TOO_SHORT")
    return key


def _derive(root_key: bytes, domain: str, payload: bytes) -> bytes:
    root_key = _require_key(root_key)
    framed = (
        b"HHS-P213-SECURE-MEMORY-KDF-V1\0"
        + len(domain.encode("utf-8")).to_bytes(2, "big")
        + domain.encode("utf-8")
        + len(payload).to_bytes(8, "big")
        + payload
    )
    return hmac.new(root_key, framed, sha256).digest()


class NativeSecureArena:
    """Owner-bound native arena with deterministic lifecycle receipts."""

    def __init__(
        self,
        *,
        library_path: str | Path,
        requested_size: int,
        owner_id: str,
        root_key: bytes,
        allocation_sequence: int,
    ) -> None:
        if not isinstance(requested_size, int) or requested_size <= 0:
            raise Pass213SecureMemoryError(
                "PASS213_SECURE_MEMORY_SIZE_INVALID"
            )
        if not owner_id:
            raise Pass213SecureMemoryError(
                "PASS213_SECURE_MEMORY_OWNER_INVALID"
            )
        if not isinstance(allocation_sequence, int) or allocation_sequence < 0:
            raise Pass213SecureMemoryError(
                "PASS213_SECURE_MEMORY_ALLOCATION_SEQUENCE_INVALID"
            )

        self._library_path = str(Path(library_path))
        self._lib = ctypes.CDLL(self._library_path)
        self._configure_library()
        owner_context = canonical_bytes(
            {
                "contract": CONTRACT,
                "iteration": ITERATION,
                "owner_id": owner_id,
                "allocation_sequence": allocation_sequence,
                "requested_size": requested_size,
            }
        )
        self._owner_token = _derive(
            root_key,
            "OWNER-TOKEN",
            owner_context,
        )
        self._receipt_key = _derive(
            root_key,
            "RECEIPT-KEY",
            owner_context,
        )
        self._arena_id_hash216 = hash216(
            "secure-memory-arena-id",
            owner_context,
        )
        self._handle = ctypes.c_void_p()
        self._closed = False
        self._receipt_sequence = 0
        self._previous_receipt_hash216 = "0" * 64
        self._receipts: list[SecureMemoryReceipt] = []

        result = self._lib.hhs_secure_arena_create(
            ctypes.c_size_t(requested_size),
            self._token_array(),
            ctypes.byref(self._handle),
        )
        self._check(result, "CREATE")
        status = self.status()
        if not (
            status["locked"]
            and status["dontdump"]
            and status["dontfork"]
            and status["guard_pages"] == 2
            and status["zeroized"]
            and not status["sealed"]
        ):
            self.close()
            raise Pass213SecureMemoryError(
                "PASS213_SECURE_MEMORY_INITIAL_PROTECTION_INVALID"
            )
        self._emit_receipt(
            "ALLOCATE",
            {
                "requested_size": status["requested_size"],
                "usable_size": status["usable_size"],
                "mapping_size": status["mapping_size"],
                "page_size": status["page_size"],
                "locked": status["locked"],
                "dontdump": status["dontdump"],
                "dontfork": status["dontfork"],
                "guard_pages": status["guard_pages"],
            },
            status["mutation_sequence"],
        )

    def _configure_library(self) -> None:
        token_pointer = ctypes.POINTER(ctypes.c_uint8)
        self._lib.hhs_secure_process_harden.argtypes = []
        self._lib.hhs_secure_process_harden.restype = ctypes.c_int

        self._lib.hhs_secure_arena_create.argtypes = [
            ctypes.c_size_t,
            token_pointer,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        self._lib.hhs_secure_arena_create.restype = ctypes.c_int
        self._lib.hhs_secure_arena_write.argtypes = [
            ctypes.c_void_p,
            token_pointer,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
        ]
        self._lib.hhs_secure_arena_write.restype = ctypes.c_int
        self._lib.hhs_secure_arena_read.argtypes = [
            ctypes.c_void_p,
            token_pointer,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
        ]
        self._lib.hhs_secure_arena_read.restype = ctypes.c_int
        self._lib.hhs_secure_arena_seal.argtypes = [
            ctypes.c_void_p,
            token_pointer,
        ]
        self._lib.hhs_secure_arena_seal.restype = ctypes.c_int
        self._lib.hhs_secure_arena_zeroize.argtypes = [
            ctypes.c_void_p,
            token_pointer,
        ]
        self._lib.hhs_secure_arena_zeroize.restype = ctypes.c_int
        self._lib.hhs_secure_arena_is_zero.argtypes = [
            ctypes.c_void_p,
            token_pointer,
            ctypes.POINTER(ctypes.c_int),
        ]
        self._lib.hhs_secure_arena_is_zero.restype = ctypes.c_int
        self._lib.hhs_secure_arena_status_get.argtypes = [
            ctypes.c_void_p,
            token_pointer,
            ctypes.POINTER(_NativeStatus),
        ]
        self._lib.hhs_secure_arena_status_get.restype = ctypes.c_int
        self._lib.hhs_secure_arena_destroy.argtypes = [
            ctypes.c_void_p,
            token_pointer,
        ]
        self._lib.hhs_secure_arena_destroy.restype = ctypes.c_int
        self._lib.hhs_secure_error_string.argtypes = [ctypes.c_int]
        self._lib.hhs_secure_error_string.restype = ctypes.c_char_p

    def _token_array(self) -> Any:
        token_type = ctypes.c_uint8 * 32
        return token_type.from_buffer_copy(self._owner_token)

    def _check(self, result: int, operation: str) -> None:
        if result == 0:
            return
        message = self._lib.hhs_secure_error_string(result)
        decoded = (
            message.decode("ascii", errors="replace")
            if message
            else f"UNKNOWN_{result}"
        )
        raise Pass213SecureMemoryError(
            f"PASS213_SECURE_MEMORY_{operation}_FAILED:{decoded}"
        )

    def _require_open(self) -> None:
        if self._closed or not self._handle:
            raise Pass213SecureMemoryError(
                "PASS213_SECURE_MEMORY_ARENA_CLOSED"
            )

    def _emit_receipt(
        self,
        event: str,
        details: Mapping[str, Any],
        native_mutation_sequence: int,
    ) -> SecureMemoryReceipt:
        self._receipt_sequence += 1
        payload = {
            "schema": "HHS_PASS_213_SECURE_MEMORY_RECEIPT_PAYLOAD_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "sequence": self._receipt_sequence,
            "event": event,
            "arena_id_hash216": self._arena_id_hash216,
            "previous_receipt_hash216": self._previous_receipt_hash216,
            "native_mutation_sequence": native_mutation_sequence,
            "details": dict(details),
        }
        receipt_hash = hash216(
            "secure-memory-receipt",
            canonical_bytes(payload),
        )
        tag = hmac.new(
            self._receipt_key,
            canonical_bytes(
                {
                    **payload,
                    "receipt_hash216": receipt_hash,
                }
            ),
            sha256,
        ).hexdigest()
        receipt = SecureMemoryReceipt(
            sequence=self._receipt_sequence,
            event=event,
            arena_id_hash216=self._arena_id_hash216,
            previous_receipt_hash216=self._previous_receipt_hash216,
            native_mutation_sequence=native_mutation_sequence,
            details=dict(details),
            receipt_hash216=receipt_hash,
            authentication_tag=tag,
        )
        self._previous_receipt_hash216 = receipt_hash
        self._receipts.append(receipt)
        return receipt

    @classmethod
    def harden_current_process(cls, library_path: str | Path) -> None:
        library = ctypes.CDLL(str(Path(library_path)))
        library.hhs_secure_process_harden.argtypes = []
        library.hhs_secure_process_harden.restype = ctypes.c_int
        library.hhs_secure_error_string.argtypes = [ctypes.c_int]
        library.hhs_secure_error_string.restype = ctypes.c_char_p
        result = library.hhs_secure_process_harden()
        if result != 0:
            message = library.hhs_secure_error_string(result)
            raise Pass213SecureMemoryError(
                "PASS213_SECURE_MEMORY_PROCESS_HARDEN_FAILED:"
                + (
                    message.decode("ascii", errors="replace")
                    if message
                    else str(result)
                )
            )

    @property
    def arena_id_hash216(self) -> str:
        return self._arena_id_hash216

    @property
    def receipts(self) -> tuple[SecureMemoryReceipt, ...]:
        return tuple(self._receipts)

    def status(self) -> dict[str, Any]:
        self._require_open()
        native = _NativeStatus()
        result = self._lib.hhs_secure_arena_status_get(
            self._handle,
            self._token_array(),
            ctypes.byref(native),
        )
        self._check(result, "STATUS")
        return {
            "schema": "HHS_PASS_213_SECURE_MEMORY_STATUS_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "runtime_classification": RUNTIME_CLASSIFICATION,
            "arena_id_hash216": self._arena_id_hash216,
            "requested_size": int(native.requested_size),
            "usable_size": int(native.usable_size),
            "mapping_size": int(native.mapping_size),
            "page_size": int(native.page_size),
            "mutation_sequence": int(native.mutation_sequence),
            "locked": bool(native.locked),
            "dontdump": bool(native.dontdump),
            "dontfork": bool(native.dontfork),
            "sealed": bool(native.sealed),
            "zeroized": bool(native.zeroized),
            "guard_pages": int(native.guard_pages),
            "executable": False,
        }

    def write(self, payload: bytes, *, offset: int = 0) -> SecureMemoryReceipt:
        self._require_open()
        raw = bytes(payload)
        if not raw:
            raise Pass213SecureMemoryError(
                "PASS213_SECURE_MEMORY_EMPTY_WRITE"
            )
        buffer = (ctypes.c_uint8 * len(raw)).from_buffer_copy(raw)
        result = self._lib.hhs_secure_arena_write(
            self._handle,
            self._token_array(),
            ctypes.c_size_t(offset),
            ctypes.cast(buffer, ctypes.c_void_p),
            ctypes.c_size_t(len(raw)),
        )
        self._check(result, "WRITE")
        status = self.status()
        return self._emit_receipt(
            "WRITE",
            {
                "offset": offset,
                "length": len(raw),
                "payload_hash216": hash216(
                    "secure-memory-write-payload",
                    raw,
                ),
            },
            status["mutation_sequence"],
        )

    def read_internal(self, *, offset: int = 0, length: int) -> bytes:
        self._require_open()
        if not isinstance(length, int) or length <= 0:
            raise Pass213SecureMemoryError(
                "PASS213_SECURE_MEMORY_READ_LENGTH_INVALID"
            )
        buffer = (ctypes.c_uint8 * length)()
        result = self._lib.hhs_secure_arena_read(
            self._handle,
            self._token_array(),
            ctypes.c_size_t(offset),
            ctypes.cast(buffer, ctypes.c_void_p),
            ctypes.c_size_t(length),
        )
        self._check(result, "READ")
        return bytes(buffer)

    def seal(self) -> SecureMemoryReceipt:
        self._require_open()
        result = self._lib.hhs_secure_arena_seal(
            self._handle,
            self._token_array(),
        )
        self._check(result, "SEAL")
        status = self.status()
        if not status["sealed"]:
            raise Pass213SecureMemoryError(
                "PASS213_SECURE_MEMORY_SEAL_NOT_APPLIED"
            )
        return self._emit_receipt(
            "SEAL",
            {"sealed": True, "executable": False},
            status["mutation_sequence"],
        )

    def is_zero(self) -> bool:
        self._require_open()
        out = ctypes.c_int()
        result = self._lib.hhs_secure_arena_is_zero(
            self._handle,
            self._token_array(),
            ctypes.byref(out),
        )
        self._check(result, "IS_ZERO")
        return bool(out.value)

    def zeroize(self) -> SecureMemoryReceipt:
        self._require_open()
        result = self._lib.hhs_secure_arena_zeroize(
            self._handle,
            self._token_array(),
        )
        self._check(result, "ZEROIZE")
        if not self.is_zero():
            raise Pass213SecureMemoryError(
                "PASS213_SECURE_MEMORY_ZEROIZE_VERIFICATION_FAILED"
            )
        status = self.status()
        return self._emit_receipt(
            "ZEROIZE",
            {
                "verified_zero": True,
                "usable_size": status["usable_size"],
            },
            status["mutation_sequence"],
        )

    def close(self) -> SecureMemoryReceipt | None:
        if self._closed:
            return None
        self._require_open()
        status = self.status()
        if not status["zeroized"]:
            self.zeroize()
            status = self.status()
        final_sequence = status["mutation_sequence"]
        result = self._lib.hhs_secure_arena_destroy(
            self._handle,
            self._token_array(),
        )
        self._check(result, "DESTROY")
        receipt = self._emit_receipt(
            "DESTROY",
            {
                "zeroized_before_release": True,
                "requested_size": status["requested_size"],
                "usable_size": status["usable_size"],
            },
            final_sequence,
        )
        self._handle = ctypes.c_void_p()
        self._closed = True
        self._owner_token = b"\0" * len(self._owner_token)
        self._receipt_key = b"\0" * len(self._receipt_key)
        return receipt

    def __enter__(self) -> "NativeSecureArena":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


__all__ = [
    "ITERATION",
    "RUNTIME_CLASSIFICATION",
    "Pass213SecureMemoryError",
    "SecureMemoryReceipt",
    "NativeSecureArena",
]

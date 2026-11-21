"""Pass 219+ owned read-only lowering of the inherited encrypted SQL Hash216 store.

The Pass174 PersistentEncryptedVectorStore remains responsible for SQLite,
AES-GCM, authentication, admission and quarantine. The C BIOS receives only a
lifetime-bound, verified candidate snapshot. No independent SQL or keys.
"""
from __future__ import annotations

import ctypes
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hhs_runtime.pass174.storage import PersistentEncryptedVectorStore

HASH216_BYTES = 216
FRAME_BYTES = 648


class NativeView(ctypes.Structure):
    _fields_ = [
        ("hash216_snapshot", ctypes.POINTER(ctypes.c_uint8)),
        ("frame_snapshot", ctypes.POINTER(ctypes.c_uint8)),
        ("generation", ctypes.c_uint64),
    ]


class NativeCache(ctypes.Structure):
    _fields_ = [
        ("view", NativeView),
        ("bound_generation", ctypes.c_uint64),
        ("bound", ctypes.c_uint8),
    ]


@dataclass(frozen=True)
class VerifiedVectorReference:
    object_id: str
    hash216_index_root_sha256: str
    logical_identity_sha256: str
    generation: int


class Lane5SQLNativeBIOS:
    """Owner-controlled, candidate-only transient plaintext buffer.

    Caller is responsible for coordination of key management, access control,
    service lock and source-store lifecycle. This class never opens a second
    database and never exposes VM81 commit methods.
    """

    def __init__(self, store: PersistentEncryptedVectorStore, library: str | Path):
        if not isinstance(store, PersistentEncryptedVectorStore):
            raise TypeError("requires inherited PersistentEncryptedVectorStore")
        self.store = store
        self._library = ctypes.CDLL(str(library))
        self._library.hhs_bios_bind.argtypes = [
            ctypes.POINTER(NativeCache), ctypes.POINTER(NativeView)
        ]
        self._library.hhs_bios_bind.restype = ctypes.c_int
        self._library.hhs_bios_read216.argtypes = [
            ctypes.POINTER(NativeCache), ctypes.c_uint64,
            ctypes.c_uint16, ctypes.POINTER(ctypes.c_uint8)
        ]
        self._library.hhs_bios_read216.restype = ctypes.c_int
        self._library.hhs_bios_read_frame.argtypes = [
            ctypes.POINTER(NativeCache), ctypes.c_uint64,
            ctypes.c_uint16, ctypes.POINTER(ctypes.c_uint8)
        ]
        self._library.hhs_bios_read_frame.restype = ctypes.c_int
        self._library.hhs_bios_invalidate.argtypes = [ctypes.POINTER(NativeCache)]
        self._library.hhs_bios_invalidate.restype = None
        self._cache = NativeCache()
        self._hash_buf: Any = None
        self._frame_buf: Any = None
        self._generation = 0
        self._reference: VerifiedVectorReference | None = None

    def close(self) -> None:
        self._library.hhs_bios_invalidate(ctypes.byref(self._cache))
        # Zero transient plaintext before releasing Python-owned buffers.
        for buffer in (self._frame_buf, self._hash_buf):
            if buffer is not None:
                ctypes.memset(ctypes.addressof(buffer), 0, ctypes.sizeof(buffer))
        self._frame_buf = None
        self._hash_buf = None
        self._reference = None

    def hydrate(
        self, operation_key: str, *, legacy_foundation_root: str,
        genesis_identity: str
    ) -> VerifiedVectorReference:
        self.close()
        obj, plaintext = self.store.retrieve(
            operation_key,
            legacy_foundation_root=legacy_foundation_root,
            genesis_identity=genesis_identity,
        )
        # The inherited store verifies authenticated encryption, AAD and
        # snapshot byte length; then rebuild the exact positional SHA256 index.
        obj.hash216.verify()
        from hhs_runtime.pass174.runtime import Hash216Array
        rebuilt = Hash216Array.build(
            obj.hash216.predecessor, obj.hash216.current, obj.hash216.successor,
            genesis_identity=genesis_identity, logical_step=obj.logical_step,
            operation_identity=obj.operation_identity_sha256,
            legacy_foundation_root=legacy_foundation_root,
        )
        if rebuilt != obj.hash216:
            raise ValueError("persisted Hash216 SHA256 chain mismatch")
        if len(plaintext) != FRAME_BYTES:
            raise ValueError("persisted VM81 frame length mismatch")
        raw = obj.hash216.combined.encode("ascii")
        if len(raw) != HASH216_BYTES:
            raise ValueError("persisted Hash216 lane length mismatch")
        self._generation += 1
        self._hash_buf = (ctypes.c_uint8 * HASH216_BYTES).from_buffer_copy(raw)
        self._frame_buf = (ctypes.c_uint8 * FRAME_BYTES).from_buffer_copy(plaintext)
        view = NativeView(
            ctypes.cast(self._hash_buf, ctypes.POINTER(ctypes.c_uint8)),
            ctypes.cast(self._frame_buf, ctypes.POINTER(ctypes.c_uint8)),
            self._generation,
        )
        if self._library.hhs_bios_bind(ctypes.byref(self._cache), ctypes.byref(view)):
            self.close()
            raise RuntimeError("native BIOS rejected verified SQL snapshot")
        self._reference = VerifiedVectorReference(
            obj.object_id, rebuilt.index_root_sha256,
            rebuilt.logical_identity_sha256, self._generation,
        )
        return self._reference

    def read_hash216_position(self, position: int) -> int:
        if not 0 <= position < HASH216_BYTES or self._reference is None:
            raise ValueError("unbound or invalid Hash216 position")
        value = ctypes.c_uint8()
        rc = self._library.hhs_bios_read216(
            ctypes.byref(self._cache), self._generation,
            position, ctypes.byref(value),
        )
        if rc:
            raise RuntimeError(f"native BIOS Hash216 read rejected: {rc}")
        return value.value

    def read_frame_byte(self, position: int) -> int:
        if not 0 <= position < FRAME_BYTES or self._reference is None:
            raise ValueError("unbound or invalid frame position")
        value = ctypes.c_uint8()
        rc = self._library.hhs_bios_read_frame(
            ctypes.byref(self._cache), self._generation,
            position, ctypes.byref(value),
        )
        if rc:
            raise RuntimeError(f"native BIOS frame read rejected: {rc}")
        return value.value

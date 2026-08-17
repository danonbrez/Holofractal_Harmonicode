"""Pass 218 Iteration 9 multi-process canonical ownership and fencing.

Iteration 8 proved single-process lifecycle ownership. Iteration 9 adds a
process-shared writer authority for one lock-coherent POSIX filesystem. The
kernel-held exclusive flock is the live lease; a Hash72-sealed monotonically
increasing fence epoch is the durable compare-and-swap witness. Process death
releases the live lease automatically. A later owner must acquire the lock and
advance the fence before Pass-218 canonical activity can proceed.

This surface does not create learning, truth, action, or source-retention
authority and does not use wall-clock lease expiry or floating-point time.
"""
from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path
import socket
import tempfile
from typing import Any, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.commit_boundary import (
    _canonical_bytes,
    _copy,
    _reject_retained_source_surface,
)

PASS218_OWNERSHIP_VERSION = "HHS-P218-MULTIPROCESS-CANONICAL-OWNERSHIP-I9-V1"
OWNERSHIP_RECORD_SCHEMA = "HHS-P218-I9-CANONICAL-OWNERSHIP-RECORD-V1"
OWNERSHIP_LOCK_FILENAME = "ownership.lock"
OWNERSHIP_RECORD_FILENAME = "ownership.json"
OWNERSHIP_LOCK_STRATEGY = "POSIX_FLOCK_EXCLUSIVE"
OWNERSHIP_SCOPE = "LOCK_COHERENT_POSIX_FILESYSTEM"


class Pass218OwnershipError(RuntimeError):
    pass


class Pass218OwnershipBusy(Pass218OwnershipError):
    pass


class Pass218OwnershipValidationError(Pass218OwnershipError):
    pass


class Pass218OwnershipFenceLost(Pass218OwnershipError):
    pass


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=".p218-i9-",
        suffix=".tmp",
        dir=str(path.parent),
    )
    temporary_path = Path(temporary)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        try:
            directory_fd = os.open(str(path.parent), os.O_RDONLY)
        except OSError:
            directory_fd = None
        if directory_fd is not None:
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def _read_canonical_json(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise Pass218OwnershipValidationError(
            "P218_I9_OWNERSHIP_RECORD_UNREADABLE"
        ) from exc
    if not isinstance(value, dict) or _canonical_bytes(value) != raw:
        raise Pass218OwnershipValidationError(
            "P218_I9_OWNERSHIP_RECORD_NONCANONICAL"
        )
    _reject_retained_source_surface(value)
    return value


def default_owner_id() -> str:
    hostname = socket.gethostname().strip() or "unknown-host"
    return f"{hostname}:{os.getpid()}"


def _ownership_payload(
    *,
    fence_epoch: int,
    owner_id: str,
    previous_owner_id: str | None,
    previous_fence_epoch: int,
) -> dict[str, Any]:
    return {
        "schema": OWNERSHIP_RECORD_SCHEMA,
        "ownership_version": PASS218_OWNERSHIP_VERSION,
        "fence_epoch": fence_epoch,
        "owner_id": owner_id,
        "previous_owner_id": previous_owner_id,
        "previous_fence_epoch": previous_fence_epoch,
        "lock_strategy": OWNERSHIP_LOCK_STRATEGY,
        "ownership_scope": OWNERSHIP_SCOPE,
        "canonical_learning_commit_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "verbatim_source_retained": False,
        "pass165_source_retaining_path_invoked": False,
    }


def seal_ownership_record(payload: Mapping[str, Any]) -> dict[str, Any]:
    body = _copy(payload)
    _reject_retained_source_surface(body)
    if body.get("schema") != OWNERSHIP_RECORD_SCHEMA:
        raise Pass218OwnershipValidationError(
            "P218_I9_OWNERSHIP_SCHEMA_INVALID"
        )
    ownership_hash72 = hash72_digest(
        {"domain": "HHS-P218-I9-CANONICAL-OWNERSHIP-RECORD-V1"},
        body,
    )
    return {**body, "ownership_hash72": ownership_hash72}


def validate_ownership_record(record: Mapping[str, Any]) -> dict[str, Any]:
    row = _copy(record)
    _reject_retained_source_surface(row)
    required = {
        "schema",
        "ownership_version",
        "fence_epoch",
        "owner_id",
        "previous_owner_id",
        "previous_fence_epoch",
        "lock_strategy",
        "ownership_scope",
        "canonical_learning_commit_invoked",
        "truth_promotion",
        "action_authority_minted",
        "verbatim_source_retained",
        "pass165_source_retaining_path_invoked",
        "ownership_hash72",
    }
    if set(row) != required:
        raise Pass218OwnershipValidationError(
            "P218_I9_OWNERSHIP_FIELD_SET_INVALID"
        )
    if row.get("schema") != OWNERSHIP_RECORD_SCHEMA:
        raise Pass218OwnershipValidationError("P218_I9_OWNERSHIP_SCHEMA_INVALID")
    if row.get("ownership_version") != PASS218_OWNERSHIP_VERSION:
        raise Pass218OwnershipValidationError("P218_I9_OWNERSHIP_VERSION_INVALID")
    epoch = row.get("fence_epoch")
    previous_epoch = row.get("previous_fence_epoch")
    if (
        not isinstance(epoch, int)
        or isinstance(epoch, bool)
        or epoch < 1
        or not isinstance(previous_epoch, int)
        or isinstance(previous_epoch, bool)
        or previous_epoch < 0
        or previous_epoch >= epoch
    ):
        raise Pass218OwnershipValidationError("P218_I9_OWNERSHIP_FENCE_INVALID")
    owner_id = row.get("owner_id")
    previous_owner_id = row.get("previous_owner_id")
    if not isinstance(owner_id, str) or not owner_id or len(owner_id) > 256:
        raise Pass218OwnershipValidationError("P218_I9_OWNERSHIP_OWNER_INVALID")
    if previous_owner_id is not None and (
        not isinstance(previous_owner_id, str)
        or not previous_owner_id
        or len(previous_owner_id) > 256
    ):
        raise Pass218OwnershipValidationError(
            "P218_I9_OWNERSHIP_PREVIOUS_OWNER_INVALID"
        )
    if epoch == 1 and (previous_epoch != 0 or previous_owner_id is not None):
        raise Pass218OwnershipValidationError(
            "P218_I9_OWNERSHIP_GENESIS_PREDECESSOR_INVALID"
        )
    if epoch > 1 and previous_epoch != epoch - 1:
        raise Pass218OwnershipValidationError(
            "P218_I9_OWNERSHIP_FENCE_CHAIN_INVALID"
        )
    if row.get("lock_strategy") != OWNERSHIP_LOCK_STRATEGY:
        raise Pass218OwnershipValidationError(
            "P218_I9_OWNERSHIP_LOCK_STRATEGY_INVALID"
        )
    if row.get("ownership_scope") != OWNERSHIP_SCOPE:
        raise Pass218OwnershipValidationError(
            "P218_I9_OWNERSHIP_SCOPE_INVALID"
        )
    for key in (
        "canonical_learning_commit_invoked",
        "truth_promotion",
        "action_authority_minted",
        "verbatim_source_retained",
        "pass165_source_retaining_path_invoked",
    ):
        if row.get(key) is not False:
            raise Pass218OwnershipValidationError(
                "P218_I9_FORBIDDEN_AUTHORITY_FLAG:" + key
            )
    supplied = row.get("ownership_hash72")
    if not validate_hash72(str(supplied or "")):
        raise Pass218OwnershipValidationError(
            "P218_I9_OWNERSHIP_HASH72_INVALID"
        )
    body = {key: _copy(value) for key, value in row.items() if key != "ownership_hash72"}
    if seal_ownership_record(body)["ownership_hash72"] != supplied:
        raise Pass218OwnershipValidationError(
            "P218_I9_OWNERSHIP_HASH72_MISMATCH"
        )
    return row


class Pass218CanonicalOwnershipLease:
    """Hold one process-shared writer lease and durable fencing epoch."""

    def __init__(self, root: str | os.PathLike[str], *, owner_id: str | None = None) -> None:
        self.root = Path(root)
        self.lock_path = self.root / OWNERSHIP_LOCK_FILENAME
        self.record_path = self.root / OWNERSHIP_RECORD_FILENAME
        self.owner_id = owner_id or default_owner_id()
        if not self.owner_id or len(self.owner_id) > 256:
            raise Pass218OwnershipValidationError("P218_I9_OWNERSHIP_OWNER_INVALID")
        self._fd: int | None = None
        self._record: dict[str, Any] | None = None

    @property
    def held(self) -> bool:
        return self._fd is not None

    @property
    def fence_epoch(self) -> int | None:
        return None if self._record is None else int(self._record["fence_epoch"])

    @property
    def record(self) -> dict[str, Any] | None:
        return None if self._record is None else _copy(self._record)

    def read_persisted_record(self) -> dict[str, Any] | None:
        if not self.record_path.exists():
            return None
        return validate_ownership_record(_read_canonical_json(self.record_path))

    def acquire(self, *, blocking: bool = False) -> dict[str, Any] | None:
        if self._fd is not None:
            return self.assert_current()
        self.root.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(self.lock_path), os.O_CREAT | os.O_RDWR, 0o600)
        operation = fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB)
        try:
            fcntl.flock(fd, operation)
        except BlockingIOError:
            os.close(fd)
            return None
        except Exception:
            os.close(fd)
            raise

        try:
            previous = self.read_persisted_record()
            previous_epoch = 0 if previous is None else int(previous["fence_epoch"])
            payload = _ownership_payload(
                fence_epoch=previous_epoch + 1,
                owner_id=self.owner_id,
                previous_owner_id=None if previous is None else str(previous["owner_id"]),
                previous_fence_epoch=previous_epoch,
            )
            record = seal_ownership_record(payload)
            _atomic_write(self.record_path, _canonical_bytes(record))
            self._fd = fd
            self._record = record
            return _copy(record)
        except Exception:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)
            raise

    def require_acquired(self) -> dict[str, Any]:
        if self._fd is None:
            raise Pass218OwnershipFenceLost("P218_I9_OWNERSHIP_NOT_HELD")
        return self.assert_current()

    def assert_current(self) -> dict[str, Any]:
        if self._fd is None or self._record is None:
            raise Pass218OwnershipFenceLost("P218_I9_OWNERSHIP_NOT_HELD")
        persisted = self.read_persisted_record()
        if persisted is None:
            raise Pass218OwnershipFenceLost("P218_I9_OWNERSHIP_RECORD_MISSING")
        if (
            persisted["owner_id"] != self.owner_id
            or persisted["fence_epoch"] != self._record["fence_epoch"]
            or persisted["ownership_hash72"] != self._record["ownership_hash72"]
        ):
            raise Pass218OwnershipFenceLost("P218_I9_OWNERSHIP_FENCE_LOST")
        return persisted

    def release(self) -> None:
        fd = self._fd
        self._fd = None
        self._record = None
        if fd is None:
            return
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)

    def __enter__(self) -> "Pass218CanonicalOwnershipLease":
        record = self.acquire(blocking=True)
        if record is None:
            raise Pass218OwnershipBusy("P218_I9_OWNERSHIP_BUSY")
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.release()


__all__ = [
    "OWNERSHIP_LOCK_FILENAME",
    "OWNERSHIP_LOCK_STRATEGY",
    "OWNERSHIP_RECORD_FILENAME",
    "OWNERSHIP_RECORD_SCHEMA",
    "OWNERSHIP_SCOPE",
    "PASS218_OWNERSHIP_VERSION",
    "Pass218CanonicalOwnershipLease",
    "Pass218OwnershipBusy",
    "Pass218OwnershipError",
    "Pass218OwnershipFenceLost",
    "Pass218OwnershipValidationError",
    "default_owner_id",
    "seal_ownership_record",
    "validate_ownership_record",
]

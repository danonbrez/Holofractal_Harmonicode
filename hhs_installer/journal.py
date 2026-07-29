from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping
import json
import os
import tempfile
import time

from .canonical import hash216, stable


class JournalError(RuntimeError):
    pass


def _fsync_directory(path: Path) -> None:
    try:
        fd = os.open(str(path), os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_write_bytes(path: str | Path, data: bytes, *, mode: int = 0o600) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent))
    temporary = Path(temporary_name)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb", closefd=True) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
        _fsync_directory(target.parent)
    except Exception:
        try:
            temporary.unlink(missing_ok=True)
        finally:
            raise


def atomic_write_json(path: str | Path, value: Any, *, mode: int = 0o600) -> None:
    payload = json.dumps(stable(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8") + b"\n"
    atomic_write_bytes(path, payload, mode=mode)


def append_jsonl(path: str | Path, value: Any, *, mode: int = 0o600) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    fd = os.open(str(target), flags, mode)
    try:
        payload = json.dumps(stable(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8") + b"\n"
        os.write(fd, payload)
        os.fsync(fd)
    finally:
        os.close(fd)


@dataclass(frozen=True)
class TaskCheckpoint:
    repository: str
    authoritative_base_commit: str
    active_branch: str
    intended_merge_target: str
    status: str
    files_changed: tuple[str, ...] = ()
    commands_executed: tuple[Mapping[str, Any], ...] = ()
    validation_results: Mapping[str, Any] = field(default_factory=dict)
    remaining_checks: tuple[str, ...] = ()
    environment_state: Mapping[str, Any] = field(default_factory=dict)
    next_action: str = ""
    blocker: str | None = None
    merge_status: str = "unmerged"
    updated_unix_ns: int = 0
    checkpoint_identity: str = ""

    def __post_init__(self) -> None:
        updated = self.updated_unix_ns or time.time_ns()
        object.__setattr__(self, "updated_unix_ns", updated)
        if not self.checkpoint_identity:
            payload = self.to_dict(include_identity=False)
            object.__setattr__(self, "checkpoint_identity", hash216(payload, domain="HHS-P172-RESTARTABLE-CHECKPOINT-V1"))

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        result = asdict(self)
        if not include_identity:
            result.pop("checkpoint_identity", None)
        return stable(result)

    def write(self, path: str | Path) -> None:
        atomic_write_json(path, self.to_dict())

    @classmethod
    def read(cls, path: str | Path) -> "TaskCheckpoint":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        expected = payload.pop("checkpoint_identity", "")
        checkpoint = cls(**payload)
        if expected and expected != checkpoint.checkpoint_identity:
            raise JournalError("P172_CHECKPOINT_IDENTITY_MISMATCH")
        return checkpoint

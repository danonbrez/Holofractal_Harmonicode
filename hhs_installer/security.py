from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Iterator
import os
import stat
import tarfile
import zipfile

from .canonical import hash216, stable


class SecurityError(ValueError):
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(f"{code}:{message}")
        self.code = code
        self.message = message
        self.details = dict(details or {})

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


@dataclass(frozen=True)
class ArchivePolicy:
    maximum_entries: int = 100_000
    maximum_expanded_bytes: int = 4 * 1024 * 1024 * 1024
    maximum_single_file_bytes: int = 2 * 1024 * 1024 * 1024
    permit_symlinks: bool = False

    def __post_init__(self) -> None:
        if self.maximum_entries < 1:
            raise SecurityError("P172_ARCHIVE_ENTRY_BOUND_INVALID", "maximum_entries must be positive")
        if self.maximum_expanded_bytes < 1 or self.maximum_single_file_bytes < 1:
            raise SecurityError("P172_ARCHIVE_SIZE_BOUND_INVALID", "archive size bounds must be positive")


@dataclass(frozen=True)
class ArchiveEntry:
    path: str
    size: int
    kind: str
    executable: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ArchiveInspection:
    archive_type: str
    entries: tuple[ArchiveEntry, ...]
    expanded_bytes: int
    inspection_identity: str

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


def _normalized_relative_path(name: str) -> str:
    if "\x00" in name:
        raise SecurityError("P172_ARCHIVE_NUL_PATH", "archive path contains NUL")
    normalized_name = name.replace("\\", "/")
    path = PurePosixPath(normalized_name)
    if path.is_absolute() or normalized_name.startswith("/"):
        raise SecurityError("P172_ARCHIVE_ABSOLUTE_PATH", "archive contains an absolute path", {"path": name})
    parts = tuple(part for part in path.parts if part not in {"", "."})
    if not parts:
        raise SecurityError("P172_ARCHIVE_EMPTY_PATH", "archive contains an empty path")
    if any(part == ".." for part in parts):
        raise SecurityError("P172_ARCHIVE_PATH_TRAVERSAL", "archive path escapes extraction root", {"path": name})
    if len(parts[0]) >= 2 and parts[0][1] == ":":
        raise SecurityError("P172_ARCHIVE_DRIVE_PATH", "archive contains a drive-qualified path", {"path": name})
    return "/".join(parts)


def _zip_entries(path: Path) -> Iterator[ArchiveEntry]:
    with zipfile.ZipFile(path) as archive:
        for item in archive.infolist():
            normalized = _normalized_relative_path(item.filename)
            unix_mode = (item.external_attr >> 16) & 0xFFFF
            is_symlink = stat.S_ISLNK(unix_mode)
            if item.is_dir():
                kind = "directory"
            elif is_symlink:
                kind = "symlink"
            else:
                kind = "file"
            yield ArchiveEntry(
                path=normalized,
                size=int(item.file_size),
                kind=kind,
                executable=bool(unix_mode & 0o111),
            )


def _tar_entries(path: Path) -> Iterator[ArchiveEntry]:
    with tarfile.open(path, mode="r:*") as archive:
        for item in archive.getmembers():
            normalized = _normalized_relative_path(item.name)
            if item.isdir():
                kind = "directory"
            elif item.issym() or item.islnk():
                kind = "symlink"
            elif item.isfile():
                kind = "file"
            else:
                kind = "special"
            yield ArchiveEntry(
                path=normalized,
                size=int(item.size),
                kind=kind,
                executable=bool(item.mode & 0o111),
            )


def inspect_archive(path: str | Path, policy: ArchivePolicy | None = None) -> ArchiveInspection:
    target = Path(path)
    if not target.is_file():
        raise SecurityError("P172_ARCHIVE_NOT_FOUND", "archive does not exist", {"path": str(target)})
    selected = policy or ArchivePolicy()
    if zipfile.is_zipfile(target):
        archive_type = "zip"
        iterator = _zip_entries(target)
    elif tarfile.is_tarfile(target):
        archive_type = "tar"
        iterator = _tar_entries(target)
    else:
        raise SecurityError("P172_ARCHIVE_TYPE_UNSUPPORTED", "archive type is unsupported")

    entries: list[ArchiveEntry] = []
    seen: set[str] = set()
    expanded = 0
    for entry in iterator:
        if entry.path in seen:
            raise SecurityError("P172_ARCHIVE_DUPLICATE_PATH", "archive contains duplicate path", {"path": entry.path})
        seen.add(entry.path)
        entries.append(entry)
        if len(entries) > selected.maximum_entries:
            raise SecurityError("P172_ARCHIVE_ENTRY_BOUND_EXCEEDED", "archive entry count exceeds policy")
        if entry.kind in {"symlink", "special"} and not selected.permit_symlinks:
            raise SecurityError("P172_ARCHIVE_UNSAFE_ENTRY", "archive contains a prohibited non-regular entry", {"path": entry.path, "kind": entry.kind})
        if entry.size > selected.maximum_single_file_bytes:
            raise SecurityError("P172_ARCHIVE_SINGLE_FILE_BOUND_EXCEEDED", "archive member exceeds single-file bound", {"path": entry.path, "size": entry.size})
        expanded += entry.size
        if expanded > selected.maximum_expanded_bytes:
            raise SecurityError("P172_ARCHIVE_EXPANSION_BOUND_EXCEEDED", "archive expanded-size bound exceeded")

    payload = {
        "archive_type": archive_type,
        "entries": [entry.to_dict() for entry in entries],
        "expanded_bytes": expanded,
    }
    return ArchiveInspection(
        archive_type=archive_type,
        entries=tuple(entries),
        expanded_bytes=expanded,
        inspection_identity=hash216(payload, domain="HHS-P172-ARCHIVE-INSPECTION-V1"),
    )


def _safe_destination(root: Path, relative: str) -> Path:
    destination = (root / relative).resolve()
    resolved_root = root.resolve()
    if destination != resolved_root and resolved_root not in destination.parents:
        raise SecurityError("P172_ARCHIVE_DESTINATION_ESCAPE", "extraction destination escapes root", {"path": relative})
    return destination


def extract_archive(
    path: str | Path,
    destination: str | Path,
    *,
    policy: ArchivePolicy | None = None,
) -> ArchiveInspection:
    selected = policy or ArchivePolicy()
    inspection = inspect_archive(path, selected)
    archive_path = Path(path)
    root = Path(destination)
    root.mkdir(parents=True, exist_ok=True, mode=0o700)

    if inspection.archive_type == "zip":
        with zipfile.ZipFile(archive_path) as archive:
            by_name = {entry.path: entry for entry in inspection.entries}
            for item in archive.infolist():
                relative = _normalized_relative_path(item.filename)
                entry = by_name[relative]
                target = _safe_destination(root, relative)
                if entry.kind == "directory":
                    target.mkdir(parents=True, exist_ok=True, mode=0o700)
                    continue
                if entry.kind != "file":
                    raise SecurityError("P172_ARCHIVE_UNSAFE_ENTRY", "unsafe entry reached extraction", {"path": relative})
                target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
                descriptor = os.open(str(target), flags, 0o700 if entry.executable else 0o600)
                try:
                    with archive.open(item, "r") as source, os.fdopen(descriptor, "wb", closefd=True) as output:
                        copied = 0
                        while True:
                            block = source.read(1024 * 1024)
                            if not block:
                                break
                            copied += len(block)
                            if copied > selected.maximum_single_file_bytes:
                                raise SecurityError("P172_ARCHIVE_SINGLE_FILE_BOUND_EXCEEDED", "extracted file exceeds bound", {"path": relative})
                            output.write(block)
                        output.flush()
                        os.fsync(output.fileno())
                except Exception:
                    target.unlink(missing_ok=True)
                    raise
    else:
        with tarfile.open(archive_path, mode="r:*") as archive:
            members = {_normalized_relative_path(item.name): item for item in archive.getmembers()}
            for entry in inspection.entries:
                target = _safe_destination(root, entry.path)
                if entry.kind == "directory":
                    target.mkdir(parents=True, exist_ok=True, mode=0o700)
                    continue
                if entry.kind != "file":
                    raise SecurityError("P172_ARCHIVE_UNSAFE_ENTRY", "unsafe entry reached extraction", {"path": entry.path})
                source = archive.extractfile(members[entry.path])
                if source is None:
                    raise SecurityError("P172_ARCHIVE_MEMBER_UNREADABLE", "archive member cannot be read", {"path": entry.path})
                target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                descriptor = os.open(str(target), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o700 if entry.executable else 0o600)
                try:
                    with source, os.fdopen(descriptor, "wb", closefd=True) as output:
                        copied = 0
                        while True:
                            block = source.read(1024 * 1024)
                            if not block:
                                break
                            copied += len(block)
                            if copied > selected.maximum_single_file_bytes:
                                raise SecurityError("P172_ARCHIVE_SINGLE_FILE_BOUND_EXCEEDED", "extracted file exceeds bound", {"path": entry.path})
                            output.write(block)
                        output.flush()
                        os.fsync(output.fileno())
                except Exception:
                    target.unlink(missing_ok=True)
                    raise
    return inspection


def validate_managed_path(path: str | Path, *, root: str | Path) -> Path:
    raw = str(path)
    if "\x00" in raw or "\n" in raw or "\r" in raw:
        raise SecurityError("P172_MANAGED_PATH_INVALID", "managed path contains prohibited characters")
    resolved_root = Path(root).expanduser().resolve()
    target = Path(path).expanduser().resolve()
    if target != resolved_root and resolved_root not in target.parents:
        raise SecurityError("P172_MANAGED_PATH_ESCAPE", "managed path escapes declared root", {"path": str(target), "root": str(resolved_root)})
    return target

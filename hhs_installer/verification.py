from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping
import hashlib
import hmac
import json

from .canonical import hash216, stable


class VerificationError(ValueError):
    def __init__(self, code: str, message: str, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(f"{code}:{message}")
        self.code = code
        self.message = message
        self.details = dict(details or {})

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


@dataclass(frozen=True)
class FileVerification:
    path: str
    size: int
    sha256: str
    expected_sha256: str | None
    matches: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def sha256_file(path: str | Path, *, maximum_bytes: int | None = None) -> FileVerification:
    target = Path(path)
    if not target.is_file():
        raise VerificationError("P172_VERIFICATION_FILE_MISSING", "file does not exist", {"path": str(target)})
    digest = hashlib.sha256()
    size = 0
    with target.open("rb") as handle:
        while True:
            block = handle.read(1024 * 1024)
            if not block:
                break
            size += len(block)
            if maximum_bytes is not None and size > maximum_bytes:
                raise VerificationError("P172_VERIFICATION_SIZE_BOUND_EXCEEDED", "file exceeds verification bound", {"path": str(target), "maximum_bytes": maximum_bytes})
            digest.update(block)
    return FileVerification(str(target), size, digest.hexdigest(), None, True)


def verify_sha256(path: str | Path, expected_sha256: str, *, maximum_bytes: int | None = None) -> FileVerification:
    normalized = expected_sha256.lower().strip()
    if len(normalized) != 64 or any(character not in "0123456789abcdef" for character in normalized):
        raise VerificationError("P172_EXPECTED_SHA256_INVALID", "expected SHA-256 is malformed")
    observed = sha256_file(path, maximum_bytes=maximum_bytes)
    matches = hmac.compare_digest(observed.sha256, normalized)
    result = FileVerification(observed.path, observed.size, observed.sha256, normalized, matches)
    if not matches:
        raise VerificationError(
            "P172_DIGEST_MISMATCH",
            "file digest does not match expected SHA-256",
            {"path": observed.path, "expected": normalized, "observed": observed.sha256},
        )
    return result


@dataclass(frozen=True)
class ManifestEntry:
    path: str
    size: int
    sha256: str
    artifact_class: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ManifestEntry":
        return cls(
            path=str(value["path"]),
            size=int(value["size"]),
            sha256=str(value["sha256"]).lower(),
            artifact_class=str(value.get("artifact_class", "UNCLASSIFIED")),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ManifestVerification:
    manifest_path: str
    entries: tuple[ManifestEntry, ...]
    verified_entries: int
    manifest_identity: str

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


def verify_file_manifest(
    manifest_path: str | Path,
    *,
    root: str | Path,
    maximum_entries: int = 200_000,
    maximum_total_bytes: int = 16 * 1024 * 1024 * 1024,
) -> ManifestVerification:
    path = Path(manifest_path)
    base = Path(root).resolve()
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_entries = payload.get("files", payload.get("entries")) if isinstance(payload, Mapping) else payload
    if not isinstance(raw_entries, list):
        raise VerificationError("P172_MANIFEST_FILES_MISSING", "manifest must contain a files or entries array")
    if len(raw_entries) > maximum_entries:
        raise VerificationError("P172_MANIFEST_ENTRY_BOUND_EXCEEDED", "manifest entry count exceeds bound")
    entries = tuple(ManifestEntry.from_mapping(item) for item in raw_entries)
    seen: set[str] = set()
    total = 0
    for entry in entries:
        if entry.path in seen:
            raise VerificationError("P172_MANIFEST_DUPLICATE_PATH", "manifest contains duplicate path", {"path": entry.path})
        seen.add(entry.path)
        target = (base / entry.path).resolve()
        if target != base and base not in target.parents:
            raise VerificationError("P172_MANIFEST_PATH_ESCAPE", "manifest path escapes root", {"path": entry.path})
        result = verify_sha256(target, entry.sha256, maximum_bytes=entry.size)
        if result.size != entry.size:
            raise VerificationError(
                "P172_MANIFEST_SIZE_MISMATCH",
                "file size does not match manifest",
                {"path": entry.path, "expected": entry.size, "observed": result.size},
            )
        total += result.size
        if total > maximum_total_bytes:
            raise VerificationError("P172_MANIFEST_TOTAL_SIZE_BOUND_EXCEEDED", "manifest total size exceeds bound")
    canonical = [entry.to_dict() for entry in sorted(entries, key=lambda item: item.path)]
    return ManifestVerification(
        manifest_path=str(path),
        entries=entries,
        verified_entries=len(entries),
        manifest_identity=hash216(canonical, domain="HHS-P172-FILE-MANIFEST-V1"),
    )


def verify_detached_signature(
    payload_path: str | Path,
    signature_path: str | Path,
    *,
    trusted_public_key: str | Path | None,
) -> dict[str, Any]:
    """Classify signature verification without silently substituting digest checks.

    A cryptographic signature backend and trusted key must be explicitly
    configured. Until then this function returns a stable BLOCKED result rather
    than claiming signature verification.
    """

    payload = Path(payload_path)
    signature = Path(signature_path)
    if not payload.is_file() or not signature.is_file():
        raise VerificationError("P172_SIGNATURE_INPUT_MISSING", "payload or signature file is missing")
    if trusted_public_key is None:
        return {
            "status": "BLOCKED",
            "classification": "P172_TRUSTED_SIGNING_KEY_REQUIRED",
            "payload_sha256": sha256_file(payload).sha256,
            "signature_sha256": sha256_file(signature).sha256,
            "signature_verified": False,
        }
    key = Path(trusted_public_key)
    if not key.is_file():
        raise VerificationError("P172_TRUSTED_SIGNING_KEY_MISSING", "trusted public key file is missing")
    return {
        "status": "BLOCKED",
        "classification": "P172_SIGNATURE_BACKEND_NOT_CONFIGURED",
        "payload_sha256": sha256_file(payload).sha256,
        "signature_sha256": sha256_file(signature).sha256,
        "key_sha256": sha256_file(key).sha256,
        "signature_verified": False,
    }

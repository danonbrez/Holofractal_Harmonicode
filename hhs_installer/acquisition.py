from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping
import hashlib
import os
import shutil
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

from .canonical import hash216, stable
from .journal import atomic_write_json
from .schema import NetworkPolicy, SourceKind, SourceSpec
from .verification import VerificationError, sha256_file, verify_sha256


class AcquisitionError(RuntimeError):
    def __init__(self, code: str, message: str, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(f"{code}:{message}")
        self.code = code
        self.message = message
        self.details = dict(details or {})

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


@dataclass(frozen=True)
class DownloadPolicy:
    connect_timeout_seconds: int = 15
    read_timeout_seconds: int = 120
    maximum_attempts: int = 3
    maximum_bytes: int = 8 * 1024 * 1024 * 1024
    block_size: int = 1024 * 1024
    require_https: bool = True

    def __post_init__(self) -> None:
        if not 1 <= self.connect_timeout_seconds <= 300:
            raise AcquisitionError("P172_DOWNLOAD_CONNECT_TIMEOUT_INVALID", "connect timeout is outside 1..300")
        if not 1 <= self.read_timeout_seconds <= 3600:
            raise AcquisitionError("P172_DOWNLOAD_READ_TIMEOUT_INVALID", "read timeout is outside 1..3600")
        if not 1 <= self.maximum_attempts <= 10:
            raise AcquisitionError("P172_DOWNLOAD_ATTEMPTS_INVALID", "maximum attempts is outside 1..10")
        if self.maximum_bytes < 1 or self.block_size < 1:
            raise AcquisitionError("P172_DOWNLOAD_SIZE_BOUND_INVALID", "download size bounds must be positive")


@dataclass(frozen=True)
class AcquisitionResult:
    source_kind: str
    reference: str
    local_path: str
    bytes_acquired: int
    sha256: str
    expected_identity: str | None
    verified: bool
    resumed: bool
    attempts: int
    acquisition_identity: str

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


class SourceAcquirer:
    def __init__(self, cache_root: str | Path, *, policy: DownloadPolicy | None = None) -> None:
        self.cache_root = Path(cache_root).expanduser().resolve()
        self.cache_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.policy = policy or DownloadPolicy()

    def acquire(self, source: SourceSpec, *, network_policy: NetworkPolicy) -> AcquisitionResult:
        if source.kind is SourceKind.LOCAL:
            return self._local(source)
        if source.kind is SourceKind.OFFLINE_BUNDLE:
            return self._offline_bundle(source)
        if network_policy is NetworkPolicy.OFFLINE:
            raise AcquisitionError(
                "P172_OFFLINE_NETWORK_POLICY_VIOLATION",
                "network source requested while offline policy is active",
                {"source_kind": source.kind.value},
            )
        if network_policy is NetworkPolicy.CACHED_ONLY:
            return self._cached_only(source)
        if source.kind is SourceKind.RELEASE:
            return self._download(source)
        if source.kind is SourceKind.GIT:
            raise AcquisitionError(
                "P172_GIT_ACQUISITION_ADAPTER_REQUIRED",
                "Git source acquisition requires an immutable commit adapter; branch execution is not substituted",
                {"reference": source.reference},
            )
        raise AcquisitionError("P172_SOURCE_KIND_UNSUPPORTED", "source kind is unsupported")

    def _cache_path(self, source: SourceSpec) -> Path:
        key = hashlib.sha256(f"{source.kind.value}\0{source.reference}".encode("utf-8")).hexdigest()
        suffix = Path(urllib.parse.urlparse(source.reference).path).suffix or ".asset"
        return self.cache_root / f"{key}{suffix}"

    def _local(self, source: SourceSpec) -> AcquisitionResult:
        path = Path(source.reference).expanduser().resolve()
        if not path.exists():
            raise AcquisitionError("P172_LOCAL_SOURCE_NOT_FOUND", "local source does not exist", {"path": str(path)})
        if path.is_dir():
            manifest = []
            total = 0
            for item in sorted(path.rglob("*")):
                if not item.is_file() or ".git" in item.parts:
                    continue
                digest = sha256_file(item)
                total += digest.size
                manifest.append({"path": str(item.relative_to(path)).replace("\\", "/"), "size": digest.size, "sha256": digest.sha256})
            observed = hash216(manifest, domain="HHS-P172-LOCAL-SOURCE-TREE-V1")
            if source.expected_identity and source.expected_identity != observed:
                raise AcquisitionError(
                    "P172_SOURCE_IDENTITY_MISMATCH",
                    "local source tree identity does not match expected identity",
                    {"expected": source.expected_identity, "observed": observed},
                )
            return AcquisitionResult(
                source_kind=source.kind.value,
                reference=source.reference,
                local_path=str(path),
                bytes_acquired=total,
                sha256=observed,
                expected_identity=source.expected_identity,
                verified=source.expected_identity is None or source.expected_identity == observed,
                resumed=False,
                attempts=1,
                acquisition_identity=hash216({"manifest": manifest, "source_kind": source.kind.value}, domain="HHS-P172-ACQUISITION-V1"),
            )
        observed = sha256_file(path, maximum_bytes=self.policy.maximum_bytes)
        if source.expected_identity:
            verify_sha256(path, source.expected_identity, maximum_bytes=self.policy.maximum_bytes)
        payload = {
            "source_kind": source.kind.value,
            "reference": source.reference,
            "local_path": str(path),
            "bytes_acquired": observed.size,
            "sha256": observed.sha256,
        }
        return AcquisitionResult(
            source_kind=source.kind.value,
            reference=source.reference,
            local_path=str(path),
            bytes_acquired=observed.size,
            sha256=observed.sha256,
            expected_identity=source.expected_identity,
            verified=source.expected_identity is None or source.expected_identity == observed.sha256,
            resumed=False,
            attempts=1,
            acquisition_identity=hash216(payload, domain="HHS-P172-ACQUISITION-V1"),
        )

    def _offline_bundle(self, source: SourceSpec) -> AcquisitionResult:
        path = Path(source.reference).expanduser().resolve()
        if not path.is_file():
            raise AcquisitionError("P172_OFFLINE_BUNDLE_NOT_FOUND", "offline bundle file does not exist", {"path": str(path)})
        observed = sha256_file(path, maximum_bytes=self.policy.maximum_bytes)
        if not source.expected_identity:
            raise AcquisitionError(
                "P172_OFFLINE_BUNDLE_EXPECTED_IDENTITY_REQUIRED",
                "offline bundle requires an expected SHA-256 identity",
                {"observed": observed.sha256},
            )
        verify_sha256(path, source.expected_identity, maximum_bytes=self.policy.maximum_bytes)
        payload = {
            "source_kind": source.kind.value,
            "reference": source.reference,
            "sha256": observed.sha256,
            "bytes": observed.size,
        }
        return AcquisitionResult(
            source_kind=source.kind.value,
            reference=source.reference,
            local_path=str(path),
            bytes_acquired=observed.size,
            sha256=observed.sha256,
            expected_identity=source.expected_identity,
            verified=True,
            resumed=False,
            attempts=1,
            acquisition_identity=hash216(payload, domain="HHS-P172-ACQUISITION-V1"),
        )

    def _cached_only(self, source: SourceSpec) -> AcquisitionResult:
        path = self._cache_path(source)
        if not path.is_file():
            raise AcquisitionError("P172_CACHED_SOURCE_UNAVAILABLE", "source is not present in verified cache", {"cache_path": str(path)})
        observed = sha256_file(path, maximum_bytes=self.policy.maximum_bytes)
        if source.expected_identity:
            verify_sha256(path, source.expected_identity, maximum_bytes=self.policy.maximum_bytes)
        payload = {"cache_path": str(path), "sha256": observed.sha256, "bytes": observed.size}
        return AcquisitionResult(
            source_kind=source.kind.value,
            reference=source.reference,
            local_path=str(path),
            bytes_acquired=observed.size,
            sha256=observed.sha256,
            expected_identity=source.expected_identity,
            verified=source.expected_identity is None or source.expected_identity == observed.sha256,
            resumed=True,
            attempts=0,
            acquisition_identity=hash216(payload, domain="HHS-P172-ACQUISITION-V1"),
        )

    def _download(self, source: SourceSpec) -> AcquisitionResult:
        parsed = urllib.parse.urlparse(source.reference)
        if parsed.scheme not in {"https", "http"}:
            raise AcquisitionError("P172_DOWNLOAD_SCHEME_INVALID", "download URL must use HTTP or HTTPS")
        if self.policy.require_https and parsed.scheme != "https":
            raise AcquisitionError("P172_DOWNLOAD_HTTPS_REQUIRED", "download URL must use HTTPS")
        if parsed.username or parsed.password:
            raise AcquisitionError("P172_DOWNLOAD_CREDENTIALS_IN_URL", "credentials must not be embedded in the URL")
        destination = self._cache_path(source)
        partial = destination.with_suffix(destination.suffix + ".partial")
        journal = destination.with_suffix(destination.suffix + ".download.json")
        resumed = partial.exists() and partial.stat().st_size > 0
        attempts = 0
        last_error: str | None = None
        context = ssl.create_default_context()

        while attempts < self.policy.maximum_attempts:
            attempts += 1
            existing = partial.stat().st_size if partial.exists() else 0
            if existing > self.policy.maximum_bytes:
                partial.unlink(missing_ok=True)
                raise AcquisitionError("P172_DOWNLOAD_SIZE_BOUND_EXCEEDED", "partial download exceeds maximum size")
            headers = {"User-Agent": "HHS-P172-Installer/1"}
            if existing:
                headers["Range"] = f"bytes={existing}-"
            request = urllib.request.Request(source.reference, headers=headers, method="GET")
            atomic_write_json(
                journal,
                {
                    "schema": "HHS_PASS_172_DOWNLOAD_JOURNAL_V1",
                    "reference": source.reference,
                    "attempt": attempts,
                    "partial_bytes": existing,
                    "maximum_bytes": self.policy.maximum_bytes,
                    "expected_identity": source.expected_identity,
                    "status": "ACTIVE",
                    "next_action": "resume the same URL using the partial file and Range header",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=self.policy.connect_timeout_seconds, context=context) as response:
                    status = int(getattr(response, "status", 200))
                    if existing and status != 206:
                        partial.unlink(missing_ok=True)
                        existing = 0
                    mode = "ab" if existing and status == 206 else "wb"
                    with partial.open(mode) as output:
                        total = existing
                        while True:
                            block = response.read(self.policy.block_size)
                            if not block:
                                break
                            total += len(block)
                            if total > self.policy.maximum_bytes:
                                raise AcquisitionError("P172_DOWNLOAD_SIZE_BOUND_EXCEEDED", "download exceeds maximum size")
                            output.write(block)
                        output.flush()
                        os.fsync(output.fileno())
                observed = sha256_file(partial, maximum_bytes=self.policy.maximum_bytes)
                if source.expected_identity:
                    verify_sha256(partial, source.expected_identity, maximum_bytes=self.policy.maximum_bytes)
                os.replace(partial, destination)
                atomic_write_json(
                    journal,
                    {
                        "schema": "HHS_PASS_172_DOWNLOAD_JOURNAL_V1",
                        "reference": source.reference,
                        "attempt": attempts,
                        "bytes": observed.size,
                        "sha256": observed.sha256,
                        "status": "SUCCESS",
                        "next_action": "verify and stage the downloaded source",
                    },
                )
                payload = {
                    "source_kind": source.kind.value,
                    "reference": source.reference,
                    "sha256": observed.sha256,
                    "bytes": observed.size,
                }
                return AcquisitionResult(
                    source_kind=source.kind.value,
                    reference=source.reference,
                    local_path=str(destination),
                    bytes_acquired=observed.size,
                    sha256=observed.sha256,
                    expected_identity=source.expected_identity,
                    verified=source.expected_identity is None or source.expected_identity == observed.sha256,
                    resumed=resumed,
                    attempts=attempts,
                    acquisition_identity=hash216(payload, domain="HHS-P172-ACQUISITION-V1"),
                )
            except (urllib.error.URLError, TimeoutError, OSError, VerificationError, AcquisitionError) as exc:
                last_error = f"{type(exc).__name__}:{exc}"
                atomic_write_json(
                    journal,
                    {
                        "schema": "HHS_PASS_172_DOWNLOAD_JOURNAL_V1",
                        "reference": source.reference,
                        "attempt": attempts,
                        "partial_bytes": partial.stat().st_size if partial.exists() else 0,
                        "status": "BLOCKED" if attempts >= self.policy.maximum_attempts else "RETRYABLE",
                        "blocker": last_error,
                        "next_action": "retry the same acquisition; preserve the partial file only when the expected identity remains unchanged",
                    },
                )
                if isinstance(exc, VerificationError):
                    partial.rename(destination.with_suffix(destination.suffix + ".quarantine"))
                    raise AcquisitionError("P172_DOWNLOADED_SOURCE_DIGEST_MISMATCH", "downloaded source failed digest verification", {"error": last_error}) from exc
                if attempts >= self.policy.maximum_attempts:
                    break
                time.sleep(min(attempts, 3))
        raise AcquisitionError(
            "P172_DOWNLOAD_RETRIES_EXHAUSTED",
            "download did not complete within bounded attempts",
            {
                "attempts": attempts,
                "blocker": last_error,
                "partial": str(partial),
                "journal": str(journal),
                "next_action": "rerun the same acquisition to resume from the recorded partial boundary",
            },
        )

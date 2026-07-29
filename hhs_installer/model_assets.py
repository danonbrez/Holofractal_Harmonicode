from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping
import json
import os
import shutil
import tempfile

from .acquisition import DownloadPolicy, SourceAcquirer
from .canonical import hash216, stable
from .journal import atomic_write_json
from .schema import NetworkPolicy, SourceKind, SourceSpec
from .verification import sha256_file, verify_sha256


class ModelAssetError(ValueError):
    def __init__(self, code: str, message: str, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(f"{code}:{message}")
        self.code = code
        self.message = message
        self.details = dict(details or {})

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


@dataclass(frozen=True)
class ModelAssetRequest:
    registry_id: str
    source_reference: str
    source_kind: SourceKind
    filename: str
    version: str
    license_id: str
    expected_sha256: str
    provider: str
    expected_size: int | None = None
    authentication_required: bool = False

    def __post_init__(self) -> None:
        if not self.registry_id or not self.filename or not self.version:
            raise ModelAssetError("P172_MODEL_REQUEST_FIELDS_REQUIRED", "model registry ID, filename, and version are required")
        if Path(self.filename).name != self.filename or "\x00" in self.filename:
            raise ModelAssetError("P172_MODEL_FILENAME_INVALID", "model filename must be a simple filename")
        if len(self.expected_sha256) != 64:
            raise ModelAssetError("P172_MODEL_SHA256_REQUIRED", "model expected SHA-256 must be declared")
        if self.expected_size is not None and self.expected_size < 1:
            raise ModelAssetError("P172_MODEL_SIZE_INVALID", "expected model size must be positive")

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["source_kind"] = self.source_kind.value
        return stable(result)


@dataclass(frozen=True)
class ModelImportReceipt:
    registry_id: str
    version: str
    provider: str
    installed_path: str
    sha256: str
    size: int
    license_id: str
    reused_existing: bool
    request_identity: str
    model_identity: str
    receipt_identity: str

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


class ModelAssetManager:
    def __init__(self, model_root: str | Path, *, cache_root: str | Path | None = None) -> None:
        self.model_root = Path(model_root).expanduser().resolve()
        self.cache_root = Path(cache_root).expanduser().resolve() if cache_root else self.model_root.parent / "download-cache"
        self.model_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.cache_root.mkdir(parents=True, exist_ok=True, mode=0o700)

    def import_asset(
        self,
        request: ModelAssetRequest,
        *,
        network_policy: NetworkPolicy,
        license_accepted: bool,
        authentication_available: bool,
        available_bytes: int | None = None,
    ) -> ModelImportReceipt:
        if not license_accepted:
            raise ModelAssetError("P172_MODEL_LICENSE_REJECTED", "model license was not accepted", {"license_id": request.license_id})
        if request.authentication_required and not authentication_available:
            raise ModelAssetError("P172_MODEL_AUTHENTICATION_REQUIRED", "model source requires authentication")
        required_bytes = request.expected_size or 0
        if available_bytes is not None and required_bytes and available_bytes < required_bytes:
            raise ModelAssetError(
                "P172_MODEL_STORAGE_INSUFFICIENT",
                "insufficient storage for declared model size",
                {"available_bytes": available_bytes, "required_bytes": required_bytes},
            )

        request_identity = hash216(request.to_dict(), domain="HHS-P172-MODEL-REQUEST-V1")
        destination_directory = self.model_root / request.registry_id / request.version
        destination = destination_directory / request.filename
        receipt_path = destination_directory / "model-import-receipt.json"
        if destination.is_file():
            observed = verify_sha256(destination, request.expected_sha256, maximum_bytes=request.expected_size)
            receipt = self._receipt(request, destination, observed.size, observed.sha256, request_identity, reused=True)
            atomic_write_json(receipt_path, receipt.to_dict())
            return receipt

        acquirer = SourceAcquirer(
            self.cache_root,
            policy=DownloadPolicy(maximum_bytes=request.expected_size or 32 * 1024 * 1024 * 1024),
        )
        source = SourceSpec(request.source_kind, request.source_reference, request.expected_sha256)
        acquired = acquirer.acquire(source, network_policy=network_policy)
        source_path = Path(acquired.local_path)
        if not source_path.is_file():
            raise ModelAssetError("P172_MODEL_SOURCE_NOT_FILE", "model acquisition did not produce a file")
        observed = verify_sha256(source_path, request.expected_sha256, maximum_bytes=request.expected_size)
        if request.expected_size is not None and observed.size != request.expected_size:
            quarantine = self.model_root / "quarantine" / f"{request.registry_id}-{request.version}-{request.filename}"
            quarantine.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            shutil.copy2(source_path, quarantine)
            raise ModelAssetError(
                "P172_MODEL_SIZE_MISMATCH",
                "model size does not match declared size",
                {"expected": request.expected_size, "observed": observed.size, "quarantine": str(quarantine)},
            )
        destination_directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        temporary_descriptor, temporary_name = tempfile.mkstemp(prefix=f".{request.filename}.", suffix=".partial", dir=str(destination_directory))
        os.close(temporary_descriptor)
        temporary = Path(temporary_name)
        try:
            shutil.copyfile(source_path, temporary)
            verify_sha256(temporary, request.expected_sha256, maximum_bytes=request.expected_size)
            os.chmod(temporary, 0o600)
            os.replace(temporary, destination)
        except Exception:
            temporary.unlink(missing_ok=True)
            raise
        receipt = self._receipt(request, destination, observed.size, observed.sha256, request_identity, reused=False)
        atomic_write_json(receipt_path, receipt.to_dict())
        return receipt

    @staticmethod
    def _receipt(
        request: ModelAssetRequest,
        destination: Path,
        size: int,
        sha256: str,
        request_identity: str,
        *,
        reused: bool,
    ) -> ModelImportReceipt:
        model_identity = hash216(
            {
                "registry_id": request.registry_id,
                "version": request.version,
                "sha256": sha256,
                "size": size,
                "provider": request.provider,
                "license_id": request.license_id,
            },
            domain="HHS-P172-MODEL-ASSET-V1",
        )
        body = {
            "request_identity": request_identity,
            "model_identity": model_identity,
            "installed_filename": request.filename,
            "reused_existing": reused,
        }
        return ModelImportReceipt(
            registry_id=request.registry_id,
            version=request.version,
            provider=request.provider,
            installed_path=str(destination),
            sha256=sha256,
            size=size,
            license_id=request.license_id,
            reused_existing=reused,
            request_identity=request_identity,
            model_identity=model_identity,
            receipt_identity=hash216(body, domain="HHS-P172-MODEL-IMPORT-RECEIPT-V1"),
        )

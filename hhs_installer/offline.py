from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping
import json
import shutil
import tempfile

from .canonical import hash216, stable
from .security import ArchiveInspection, ArchivePolicy, extract_archive
from .verification import ManifestVerification, VerificationError, verify_file_manifest, verify_sha256


class OfflineBundleError(ValueError):
    def __init__(self, code: str, message: str, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(f"{code}:{message}")
        self.code = code
        self.message = message
        self.details = dict(details or {})

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


@dataclass(frozen=True)
class OfflineBundleVerification:
    bundle_path: str
    bundle_sha256: str
    archive_inspection_identity: str
    bundle_manifest_identity: str
    file_manifest_identity: str
    supported_profiles: tuple[str, ...]
    supported_platforms: tuple[str, ...]
    supported_architectures: tuple[str, ...]
    required_host_dependencies: tuple[str, ...]
    verified_files: int
    network_fallback_permitted: bool
    verification_identity: str

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


class OfflineBundleVerifier:
    def __init__(self, *, archive_policy: ArchivePolicy | None = None) -> None:
        self.archive_policy = archive_policy or ArchivePolicy()

    def verify(self, bundle: str | Path, *, expected_sha256: str) -> OfflineBundleVerification:
        bundle_path = Path(bundle).expanduser().resolve()
        temporary_root = Path(tempfile.mkdtemp(prefix="hhs-pass172-offline-"))
        try:
            try:
                digest = verify_sha256(
                    bundle_path,
                    expected_sha256,
                    maximum_bytes=self.archive_policy.maximum_expanded_bytes,
                )
            except VerificationError as exc:
                raise OfflineBundleError(
                    "P172_OFFLINE_BUNDLE_DIGEST_MISMATCH",
                    "offline bundle digest verification failed",
                    exc.to_dict(),
                ) from exc

            extraction_root = temporary_root / "bundle"
            inspection = extract_archive(bundle_path, extraction_root, policy=self.archive_policy)
            descriptor_path = extraction_root / "offline-bundle.json"
            if not descriptor_path.is_file():
                raise OfflineBundleError("P172_OFFLINE_DESCRIPTOR_MISSING", "offline bundle descriptor is missing")
            descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
            if descriptor.get("schema") != "HHS_PASS_172_OFFLINE_BUNDLE_V1":
                raise OfflineBundleError("P172_OFFLINE_DESCRIPTOR_SCHEMA_INVALID", "offline bundle schema is invalid")
            if bool(descriptor.get("network_fallback_permitted", True)):
                raise OfflineBundleError("P172_OFFLINE_NETWORK_FALLBACK_DECLARED", "offline bundle must forbid network fallback")
            manifest_relative = str(descriptor.get("file_manifest", "file-manifest.json"))
            manifest_path = (extraction_root / manifest_relative).resolve()
            if extraction_root.resolve() not in manifest_path.parents:
                raise OfflineBundleError("P172_OFFLINE_MANIFEST_PATH_ESCAPE", "offline manifest path escapes bundle root")
            if not manifest_path.is_file():
                raise OfflineBundleError("P172_OFFLINE_FILE_MANIFEST_MISSING", "offline file manifest is missing")
            manifest = verify_file_manifest(
                manifest_path,
                root=extraction_root,
                maximum_entries=self.archive_policy.maximum_entries,
                maximum_total_bytes=self.archive_policy.maximum_expanded_bytes,
            )
            profiles = tuple(sorted(str(item) for item in descriptor.get("supported_profiles", ())))
            platforms = tuple(sorted(str(item) for item in descriptor.get("supported_platforms", ())))
            architectures = tuple(sorted(str(item) for item in descriptor.get("supported_architectures", ())))
            host_dependencies = tuple(sorted(str(item) for item in descriptor.get("required_host_dependencies", ())))
            if not profiles or not platforms or not architectures:
                raise OfflineBundleError(
                    "P172_OFFLINE_SUPPORT_MATRIX_INCOMPLETE",
                    "offline bundle must declare profiles, platforms, and architectures",
                )
            descriptor_identity = hash216(descriptor, domain="HHS-P172-OFFLINE-DESCRIPTOR-V1")
            payload = {
                "bundle_sha256": digest.sha256,
                "inspection": inspection.inspection_identity,
                "descriptor": descriptor_identity,
                "manifest": manifest.manifest_identity,
                "profiles": profiles,
                "platforms": platforms,
                "architectures": architectures,
                "host_dependencies": host_dependencies,
            }
            return OfflineBundleVerification(
                bundle_path=str(bundle_path),
                bundle_sha256=digest.sha256,
                archive_inspection_identity=inspection.inspection_identity,
                bundle_manifest_identity=descriptor_identity,
                file_manifest_identity=manifest.manifest_identity,
                supported_profiles=profiles,
                supported_platforms=platforms,
                supported_architectures=architectures,
                required_host_dependencies=host_dependencies,
                verified_files=manifest.verified_entries,
                network_fallback_permitted=False,
                verification_identity=hash216(payload, domain="HHS-P172-OFFLINE-VERIFICATION-V1"),
            )
        except VerificationError as exc:
            raise OfflineBundleError(
                "P172_OFFLINE_FILE_VERIFICATION_FAILED",
                "offline bundle file verification failed",
                exc.to_dict(),
            ) from exc
        finally:
            shutil.rmtree(temporary_root, ignore_errors=True)

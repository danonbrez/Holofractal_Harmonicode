from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping
import json

from .canonical import hash216, stable
from .schema import InstallerSchemaError, Profile


@dataclass(frozen=True)
class DependencyRecord:
    dependency_id: str
    dependency_class: str
    version_constraint: str
    source: str
    license: str
    identity: str
    required_profiles: tuple[str, ...]
    required_platforms: tuple[str, ...] = ()
    required_architectures: tuple[str, ...] = ()
    optional: bool = False
    fallback_dependency: str | None = None
    rollback_policy: str = "remove_staged_artifact"
    security_classification: str = "STANDARD"

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "DependencyRecord":
        required = {"dependency_id", "dependency_class", "version_constraint", "source", "license", "identity", "required_profiles"}
        missing = sorted(required - set(value))
        if missing:
            raise InstallerSchemaError("P172_DEPENDENCY_FIELDS_MISSING", "dependency record is incomplete", {"fields": missing})
        return cls(
            dependency_id=str(value["dependency_id"]),
            dependency_class=str(value["dependency_class"]),
            version_constraint=str(value["version_constraint"]),
            source=str(value["source"]),
            license=str(value["license"]),
            identity=str(value["identity"]),
            required_profiles=tuple(str(item) for item in value["required_profiles"]),
            required_platforms=tuple(str(item) for item in value.get("required_platforms", ())),
            required_architectures=tuple(str(item) for item in value.get("required_architectures", ())),
            optional=bool(value.get("optional", False)),
            fallback_dependency=None if value.get("fallback_dependency") is None else str(value["fallback_dependency"]),
            rollback_policy=str(value.get("rollback_policy", "remove_staged_artifact")),
            security_classification=str(value.get("security_classification", "STANDARD")),
        )


@dataclass(frozen=True)
class DependencyResolution:
    profile: str
    platform: str
    architecture: str
    included: tuple[DependencyRecord, ...]
    excluded: tuple[str, ...]
    resolution_identity: str = ""

    def __post_init__(self) -> None:
        if not self.resolution_identity:
            payload = self.to_dict(include_identity=False)
            object.__setattr__(self, "resolution_identity", hash216(payload, domain="HHS-P172-DEPENDENCY-RESOLUTION-V1"))

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        result = {
            "profile": self.profile,
            "platform": self.platform,
            "architecture": self.architecture,
            "included": [item.to_dict() for item in self.included],
            "excluded": list(self.excluded),
        }
        if include_identity:
            result["resolution_identity"] = self.resolution_identity
        return result


class DependencyManifest:
    def __init__(self, records: Iterable[DependencyRecord]) -> None:
        ordered = sorted(records, key=lambda item: item.dependency_id)
        identifiers = [item.dependency_id for item in ordered]
        if len(identifiers) != len(set(identifiers)):
            raise InstallerSchemaError("P172_DUPLICATE_DEPENDENCY_ID", "dependency identifiers must be unique")
        self.records = tuple(ordered)
        self.manifest_identity = hash216([item.to_dict() for item in self.records], domain="HHS-P172-DEPENDENCY-MANIFEST-V1")

    @classmethod
    def load(cls, path: str | Path) -> "DependencyManifest":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        records_value = payload.get("dependencies") if isinstance(payload, Mapping) else payload
        if not isinstance(records_value, list):
            raise InstallerSchemaError("P172_DEPENDENCY_MANIFEST_INVALID", "dependency manifest must contain a dependencies array")
        return cls(DependencyRecord.from_mapping(item) for item in records_value)

    def resolve(self, profile: Profile, *, platform: str, architecture: str) -> DependencyResolution:
        included: list[DependencyRecord] = []
        excluded: list[str] = []
        for record in self.records:
            profile_match = profile.value in record.required_profiles or "all" in record.required_profiles
            platform_match = not record.required_platforms or platform in record.required_platforms or "all" in record.required_platforms
            architecture_match = not record.required_architectures or architecture in record.required_architectures or "all" in record.required_architectures
            if profile_match and platform_match and architecture_match:
                included.append(record)
            else:
                excluded.append(record.dependency_id)
        return DependencyResolution(
            profile=profile.value,
            platform=platform,
            architecture=architecture,
            included=tuple(included),
            excluded=tuple(sorted(excluded)),
        )


def requirement_files_for_profile(profile: Profile) -> tuple[str, ...]:
    base = ["requirements-core.txt"]
    if profile in {
        Profile.RUNTIME,
        Profile.ASSISTANT_EXTERNAL,
        Profile.ASSISTANT_LOCAL_CPU,
        Profile.ASSISTANT_LOCAL_GPU,
        Profile.DEVELOPER,
    }:
        base.append("requirements-runtime.txt")
    if profile in {Profile.ASSISTANT_LOCAL_CPU, Profile.ASSISTANT_LOCAL_GPU}:
        base.append("requirements-provider-litert-lm.txt")
    if profile is Profile.DEVELOPER:
        base.extend(["requirements-test.txt", "requirements-dev.txt"])
    if profile is Profile.ANDROID_BUILD:
        base.append("requirements-android-tools.txt")
    return tuple(base)

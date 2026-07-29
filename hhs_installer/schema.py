from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

CONTRACT_ID = "HHS-P172-UCEOCI-DRVBRAS"


class InstallerSchemaError(ValueError):
    def __init__(self, code: str, message: str, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(f"{code}:{message}")
        self.code = code
        self.message = message
        self.details = dict(details or {})

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


class SourceKind(str, Enum):
    RELEASE = "release"
    GIT = "git"
    LOCAL = "local"
    OFFLINE_BUNDLE = "offline_bundle"


class Profile(str, Enum):
    AUTO = "auto"
    CORE = "core"
    RUNTIME = "runtime"
    ASSISTANT_EXTERNAL = "assistant-external"
    ASSISTANT_LOCAL_CPU = "assistant-local-cpu"
    ASSISTANT_LOCAL_GPU = "assistant-local-gpu"
    DEVELOPER = "developer"
    ANDROID_BUILD = "android-build"
    CONTAINER = "container"
    OFFLINE = "offline"


class InstallMode(str, Enum):
    USER = "user"
    PORTABLE = "portable"
    SYSTEM = "system"
    CONTAINER = "container"


class NetworkPolicy(str, Enum):
    ONLINE = "online"
    CACHED_ONLY = "cached_only"
    OFFLINE = "offline"


class PrivilegePolicy(str, Enum):
    PROMPT = "prompt"
    NEVER = "never"
    PREAUTHORIZED = "preauthorized"


class ProviderPolicy(str, Enum):
    AUTO = "auto"
    LOCAL = "local"
    EXTERNAL = "external"
    DISABLED = "disabled"


class ModelPolicy(str, Enum):
    AUTO = "auto"
    DOWNLOAD = "download"
    EXISTING = "existing"
    SKIP = "skip"


class CompatibilityClass(str, Enum):
    FULLY_COMPATIBLE = "HHS_ENVIRONMENT_FULLY_COMPATIBLE"
    EXTERNAL_PROVIDER = "HHS_ENVIRONMENT_COMPATIBLE_WITH_EXTERNAL_PROVIDER"
    CPU_PROVIDER = "HHS_ENVIRONMENT_COMPATIBLE_WITH_CPU_PROVIDER"
    ASSISTANT_DEGRADED = "HHS_ENVIRONMENT_COMPATIBLE_IN_ASSISTANT_DEGRADED_MODE"
    CORE_ONLY = "HHS_ENVIRONMENT_CORE_ONLY_COMPATIBLE"
    ANDROID_BUILD = "HHS_ENVIRONMENT_ANDROID_BUILD_COMPATIBLE"
    CONTAINER = "HHS_ENVIRONMENT_CONTAINER_COMPATIBLE"
    OFFLINE_BUNDLE = "HHS_ENVIRONMENT_OFFLINE_BUNDLE_COMPATIBLE"
    REPAIRABLE = "HHS_ENVIRONMENT_REPAIRABLE"
    INCOMPATIBLE = "HHS_ENVIRONMENT_INCOMPATIBLE"


@dataclass(frozen=True)
class SourceSpec:
    kind: SourceKind
    reference: str
    expected_identity: str | None = None

    def __post_init__(self) -> None:
        if not self.reference or not self.reference.strip():
            raise InstallerSchemaError("P172_SOURCE_REFERENCE_REQUIRED", "source reference must be nonempty")
        if "\x00" in self.reference:
            raise InstallerSchemaError("P172_SOURCE_REFERENCE_INVALID", "source reference contains NUL")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "SourceSpec":
        allowed = {"kind", "reference", "expected_identity"}
        unknown = sorted(set(value) - allowed)
        if unknown:
            raise InstallerSchemaError("P172_UNKNOWN_SOURCE_FIELDS", "unknown source fields", {"fields": unknown})
        try:
            kind = SourceKind(str(value["kind"]))
            reference = str(value["reference"])
        except KeyError as exc:
            raise InstallerSchemaError("P172_SOURCE_FIELD_REQUIRED", "source kind and reference are required") from exc
        expected = value.get("expected_identity")
        return cls(kind=kind, reference=reference, expected_identity=None if expected is None else str(expected))


@dataclass(frozen=True)
class InstallationRequest:
    operation: str = "install"
    source: SourceSpec = field(default_factory=lambda: SourceSpec(SourceKind.LOCAL, "."))
    profile: Profile = Profile.AUTO
    install_mode: InstallMode = InstallMode.USER
    start_after_install: bool = False
    network_policy: NetworkPolicy = NetworkPolicy.ONLINE
    privilege_policy: PrivilegePolicy = PrivilegePolicy.PROMPT
    provider_policy: ProviderPolicy = ProviderPolicy.AUTO
    model_policy: ModelPolicy = ModelPolicy.AUTO
    preserve_user_data: bool = True
    noninteractive: bool = False
    hhs_home: str | None = None
    timeout_seconds: int = 900

    def __post_init__(self) -> None:
        if self.operation not in {
            "install",
            "probe",
            "plan",
            "verify",
            "repair",
            "update",
            "rollback",
            "uninstall",
            "status",
            "doctor",
            "replay-install",
        }:
            raise InstallerSchemaError("P172_OPERATION_INVALID", "unsupported installation operation", {"operation": self.operation})
        if self.timeout_seconds < 1 or self.timeout_seconds > 86_400:
            raise InstallerSchemaError("P172_TIMEOUT_INVALID", "timeout_seconds must be in 1..86400")
        if self.profile is Profile.OFFLINE and self.network_policy is not NetworkPolicy.OFFLINE:
            raise InstallerSchemaError("P172_OFFLINE_PROFILE_NETWORK_POLICY", "offline profile requires offline network policy")
        if self.source.kind is SourceKind.OFFLINE_BUNDLE and self.network_policy is not NetworkPolicy.OFFLINE:
            raise InstallerSchemaError("P172_OFFLINE_BUNDLE_NETWORK_POLICY", "offline bundle requires offline network policy")
        if self.install_mode is InstallMode.SYSTEM and self.privilege_policy is PrivilegePolicy.NEVER:
            raise InstallerSchemaError("P172_SYSTEM_MODE_PRIVILEGE_DENIED", "system mode cannot use privilege policy never")
        if self.hhs_home is not None:
            raw = self.hhs_home.strip()
            if not raw or "\x00" in raw:
                raise InstallerSchemaError("P172_HHS_HOME_INVALID", "HHS_HOME is invalid")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "InstallationRequest":
        allowed = {
            "contract_id",
            "operation",
            "source",
            "profile",
            "install_mode",
            "start_after_install",
            "network_policy",
            "privilege_policy",
            "provider_policy",
            "model_policy",
            "preserve_user_data",
            "noninteractive",
            "hhs_home",
            "timeout_seconds",
        }
        unknown = sorted(set(value) - allowed)
        if unknown:
            raise InstallerSchemaError("P172_UNKNOWN_REQUEST_FIELDS", "unknown installation request fields", {"fields": unknown})
        contract_id = str(value.get("contract_id", CONTRACT_ID))
        if contract_id != CONTRACT_ID:
            raise InstallerSchemaError("P172_CONTRACT_ID_MISMATCH", "request contract_id is not Pass 172", {"contract_id": contract_id})
        source_value = value.get("source", {"kind": "local", "reference": "."})
        if not isinstance(source_value, Mapping):
            raise InstallerSchemaError("P172_SOURCE_INVALID", "source must be an object")
        try:
            return cls(
                operation=str(value.get("operation", "install")),
                source=SourceSpec.from_mapping(source_value),
                profile=Profile(str(value.get("profile", "auto"))),
                install_mode=InstallMode(str(value.get("install_mode", "user"))),
                start_after_install=bool(value.get("start_after_install", False)),
                network_policy=NetworkPolicy(str(value.get("network_policy", "online"))),
                privilege_policy=PrivilegePolicy(str(value.get("privilege_policy", "prompt"))),
                provider_policy=ProviderPolicy(str(value.get("provider_policy", "auto"))),
                model_policy=ModelPolicy(str(value.get("model_policy", "auto"))),
                preserve_user_data=bool(value.get("preserve_user_data", True)),
                noninteractive=bool(value.get("noninteractive", False)),
                hhs_home=None if value.get("hhs_home") is None else str(value["hhs_home"]),
                timeout_seconds=int(value.get("timeout_seconds", 900)),
            )
        except (ValueError, TypeError) as exc:
            if isinstance(exc, InstallerSchemaError):
                raise
            raise InstallerSchemaError("P172_REQUEST_ENUM_INVALID", "request contains an invalid enum or scalar value") from exc

    def resolved_home(self) -> Path:
        if self.hhs_home:
            return Path(self.hhs_home).expanduser()
        if self.install_mode is InstallMode.PORTABLE:
            return Path(self.source.reference).expanduser().resolve() / ".hhs"
        return Path.home() / ".hhs"

    def to_dict(self) -> dict[str, Any]:
        raw = asdict(self)
        raw["contract_id"] = CONTRACT_ID
        raw["source"]["kind"] = self.source.kind.value
        raw["profile"] = self.profile.value
        raw["install_mode"] = self.install_mode.value
        raw["network_policy"] = self.network_policy.value
        raw["privilege_policy"] = self.privilege_policy.value
        raw["provider_policy"] = self.provider_policy.value
        raw["model_policy"] = self.model_policy.value
        return raw

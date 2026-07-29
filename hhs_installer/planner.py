from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .canonical import hash216
from .probe import ProbeReport
from .schema import InstallationRequest, InstallerSchemaError, NetworkPolicy, Profile, ProviderPolicy


@dataclass(frozen=True)
class PlanStep:
    step_id: str
    operation: str
    mutation_scope: tuple[str, ...]
    timeout_seconds: int
    rollback: str
    requires_privilege: bool = False
    optional: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class InstallationPlan:
    request: InstallationRequest
    probe_identity: str
    requested_profile: Profile
    resolved_profile: Profile
    steps: tuple[PlanStep, ...]
    external_packages: tuple[str, ...]
    excluded_dependency_classes: tuple[str, ...]
    plan_identity: str = ""

    def __post_init__(self) -> None:
        if not self.plan_identity:
            object.__setattr__(
                self,
                "plan_identity",
                hash216(self.to_dict(include_identity=False), domain="HHS-P172-INSTALLATION-PLAN-V1"),
            )

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        result = {
            "request": self.request.to_dict(),
            "probe_identity": self.probe_identity,
            "requested_profile": self.requested_profile.value,
            "resolved_profile": self.resolved_profile.value,
            "steps": [step.to_dict() for step in self.steps],
            "external_packages": list(self.external_packages),
            "excluded_dependency_classes": list(self.excluded_dependency_classes),
        }
        if include_identity:
            result["plan_identity"] = self.plan_identity
        return result


class InstallationPlanner:
    def resolve_profile(self, request: InstallationRequest, probe: ProbeReport) -> Profile:
        compatible = set(probe.compatible_profiles)
        if request.profile is not Profile.AUTO:
            if request.profile not in compatible:
                raise InstallerSchemaError(
                    "P172_PROFILE_INCOMPATIBLE",
                    "requested profile is not compatible with the probe state",
                    {
                        "requested": request.profile.value,
                        "compatible": sorted(item.value for item in compatible),
                        "probe_identity": probe.probe_identity,
                    },
                )
            return request.profile

        order: list[Profile]
        if request.provider_policy is ProviderPolicy.DISABLED:
            order = [Profile.RUNTIME, Profile.CORE]
        elif request.provider_policy is ProviderPolicy.EXTERNAL:
            order = [Profile.ASSISTANT_EXTERNAL, Profile.RUNTIME, Profile.CORE]
        elif request.provider_policy is ProviderPolicy.LOCAL:
            order = [Profile.ASSISTANT_LOCAL_GPU, Profile.ASSISTANT_LOCAL_CPU, Profile.RUNTIME, Profile.CORE]
        else:
            order = [
                Profile.ASSISTANT_LOCAL_GPU,
                Profile.ASSISTANT_LOCAL_CPU,
                Profile.ASSISTANT_EXTERNAL,
                Profile.RUNTIME,
                Profile.CORE,
            ]
        for profile in order:
            if profile in compatible:
                return profile
        raise InstallerSchemaError(
            "P172_NO_COMPATIBLE_PROFILE",
            "no compatible installation profile is available",
            {"compatible": sorted(item.value for item in compatible)},
        )

    def build(self, request: InstallationRequest, probe: ProbeReport) -> InstallationPlan:
        resolved = self.resolve_profile(request, probe)
        timeout = request.timeout_seconds
        steps: list[PlanStep] = [
            PlanStep("source-acquire", "acquire_source", ("install/staging/source",), min(timeout, 900), "delete staged source"),
            PlanStep("source-verify", "verify_source", (), min(timeout, 300), "quarantine invalid source"),
            PlanStep("layout-stage", "create_layout", ("versions", "runtime", "install", "logs", "bin"), 60, "delete unactivated staged version"),
            PlanStep("python-create", "create_python_environment", ("runtime/python",), min(timeout, 600), "delete staged environment"),
            PlanStep("dependencies-install", "install_profile_dependencies", ("runtime/python",), min(timeout, 1800), "delete staged environment"),
            PlanStep("native-build", "build_native_runtime", ("runtime/native",), min(timeout, 1800), "delete staged native artifacts"),
            PlanStep("native-verify", "verify_native_runtime", (), min(timeout, 600), "quarantine invalid native artifact"),
        ]

        excluded = {"TEST", "FORMATTER", "BROWSER_RUNTIME", "ANDROID_TOOLCHAIN", "MODEL_ASSET", "GPU_LOADER"}
        if resolved in {Profile.RUNTIME, Profile.ASSISTANT_EXTERNAL, Profile.ASSISTANT_LOCAL_CPU, Profile.ASSISTANT_LOCAL_GPU, Profile.DEVELOPER}:
            steps.append(PlanStep("runtime-config", "generate_runtime_configuration", ("runtime/config",), 60, "restore prior configuration"))
        if resolved is Profile.DEVELOPER:
            excluded.discard("TEST")
            excluded.discard("BROWSER_RUNTIME")
            steps.append(PlanStep("frontend-build", "build_frontend", ("runtime/frontend",), min(timeout, 1200), "delete staged frontend"))
        if resolved is Profile.ANDROID_BUILD:
            excluded.discard("ANDROID_TOOLCHAIN")
            steps.append(PlanStep("android-build", "build_android_projection", ("runtime/android",), min(timeout, 3600), "delete staged Android output"))
        if resolved in {Profile.ASSISTANT_LOCAL_CPU, Profile.ASSISTANT_LOCAL_GPU}:
            excluded.discard("MODEL_ASSET")
            steps.extend(
                [
                    PlanStep("provider-install", "install_local_provider", ("runtime/provider",), min(timeout, 1800), "delete staged provider"),
                    PlanStep("model-govern", "acquire_verify_import_model", ("runtime/models",), min(timeout, 7200), "quarantine partial model", optional=request.model_policy.value in {"auto", "skip"}),
                    PlanStep("provider-verify", "verify_local_provider", (), min(timeout, 600), "stop staged provider"),
                ]
            )
            if resolved is Profile.ASSISTANT_LOCAL_GPU:
                excluded.discard("GPU_LOADER")
                steps.insert(-3, PlanStep("gpu-substrate", "verify_or_install_gpu_loader", ("runtime/graphics",), min(timeout, 900), "restore prior loader state", requires_privilege=False))
        elif resolved is Profile.ASSISTANT_EXTERNAL:
            steps.append(PlanStep("provider-external", "verify_external_provider", ("runtime/config",), min(timeout, 120), "restore prior provider configuration"))

        if request.network_policy is NetworkPolicy.OFFLINE:
            steps.insert(0, PlanStep("offline-verify", "verify_offline_bundle", (), min(timeout, 600), "quarantine invalid bundle"))

        steps.extend(
            [
                PlanStep("runtime-validate", "run_dependency_scoped_validation", (), min(timeout, 1800), "keep prior active version"),
                PlanStep("activate", "activate_staged_version", ("current", "bin/hhs"), 60, "restore prior active pointer"),
                PlanStep("post-activate", "verify_active_installation", (), min(timeout, 300), "rollback activation"),
                PlanStep("receipt-close", "close_completion_receipt", ("install/receipts",), 60, "append failure receipt"),
            ]
        )

        external_packages: list[str] = []
        missing = {item.capability_id for item in probe.capabilities if not item.available and item.repairable}
        if "c11_compiler" in missing:
            external_packages.append("c11-compiler")
        if "python_3_11" in missing or "python_venv" in missing:
            external_packages.append("python-3.11-runtime")
        if resolved is Profile.DEVELOPER and ("node" in missing or "npm" in missing):
            external_packages.append("nodejs-22")

        return InstallationPlan(
            request=request,
            probe_identity=probe.probe_identity,
            requested_profile=request.profile,
            resolved_profile=resolved,
            steps=tuple(steps),
            external_packages=tuple(sorted(set(external_packages))),
            excluded_dependency_classes=tuple(sorted(excluded)),
        )

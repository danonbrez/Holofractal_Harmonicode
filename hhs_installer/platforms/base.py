from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping
import platform

from ..canonical import hash216, stable
from ..probe import ProbeReport
from ..schema import Profile


@dataclass(frozen=True)
class PackagePlan:
    package_manager: str
    packages: tuple[str, ...]
    commands: tuple[tuple[str, ...], ...]
    requires_privilege: bool
    rollback_limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


@dataclass(frozen=True)
class PlatformDecision:
    adapter_id: str
    system: str
    release: str
    architecture: str
    profile: str
    compatible: bool
    classification: str
    package_plan: PackagePlan | None
    blockers: tuple[str, ...]
    nonclaims: tuple[str, ...]
    decision_identity: str

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


class PlatformAdapter:
    adapter_id = "HHS-P172-GENERIC-POSIX"

    def __init__(self, *, system_name: str | None = None) -> None:
        self.system_name = system_name or platform.system() or "Unknown"

    def package_plan(self, missing_capabilities: tuple[str, ...], profile: Profile) -> PackagePlan | None:
        return None

    def decide(self, probe: ProbeReport, profile: Profile) -> PlatformDecision:
        blockers: list[str] = []
        if profile not in probe.compatible_profiles:
            blockers.append("P172_PROFILE_NOT_IN_PROBE_COMPATIBLE_SET")
        plan = self.package_plan(
            tuple(sorted(item.capability_id for item in probe.capabilities if not item.available and item.repairable)),
            profile,
        )
        compatible = not blockers
        classification = "P172_PLATFORM_PROFILE_COMPATIBLE" if compatible else "P172_PLATFORM_PROFILE_INCOMPATIBLE"
        nonclaims = (
            "No unexecuted platform support is claimed.",
            "Package names are adapter-specific and never inferred from another distribution.",
            "Host provisioning does not create Runtime authority.",
        )
        payload = {
            "adapter_id": self.adapter_id,
            "system": probe.platform,
            "release": probe.platform_release,
            "architecture": probe.architecture,
            "profile": profile.value,
            "compatible": compatible,
            "classification": classification,
            "package_plan": None if plan is None else plan.to_dict(),
            "blockers": blockers,
            "nonclaims": nonclaims,
        }
        return PlatformDecision(
            adapter_id=self.adapter_id,
            system=probe.platform,
            release=probe.platform_release,
            architecture=probe.architecture,
            profile=profile.value,
            compatible=compatible,
            classification=classification,
            package_plan=plan,
            blockers=tuple(blockers),
            nonclaims=nonclaims,
            decision_identity=hash216(payload, domain="HHS-P172-PLATFORM-DECISION-V1"),
        )

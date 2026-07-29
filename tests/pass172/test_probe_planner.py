from __future__ import annotations

from pathlib import Path

import pytest

from hhs_installer.planner import InstallationPlanner
from hhs_installer.probe import Capability, EnvironmentProbe, ProbeReport
from hhs_installer.schema import (
    CompatibilityClass,
    InstallationRequest,
    InstallerSchemaError,
    Profile,
    ProviderPolicy,
    SourceKind,
    SourceSpec,
)


def _probe(*profiles: Profile) -> ProbeReport:
    return ProbeReport(
        platform="Linux",
        platform_release="test",
        architecture="x86_64",
        python_version="3.11.9",
        capabilities=(
            Capability("python_3_11", True, "3.11.9", ">=3.11"),
            Capability("c11_compiler", True, "clang", "C11"),
        ),
        compatible_profiles=profiles,
        primary_classification=CompatibilityClass.EXTERNAL_PROVIDER,
        selected_ports={"api": 8000, "provider": 9379},
    )


def test_real_probe_is_read_only_and_identified(tmp_path: Path) -> None:
    before = sorted(tmp_path.iterdir())
    report = EnvironmentProbe(command_timeout=1).run(target=tmp_path)
    after = sorted(tmp_path.iterdir())
    assert before == after
    assert report.probe_identity
    assert report.platform
    assert report.architecture


def test_auto_profile_honors_disabled_provider() -> None:
    request = InstallationRequest(
        source=SourceSpec(SourceKind.LOCAL, "."),
        profile=Profile.AUTO,
        provider_policy=ProviderPolicy.DISABLED,
    )
    plan = InstallationPlanner().build(
        request,
        _probe(Profile.CORE, Profile.RUNTIME, Profile.ASSISTANT_EXTERNAL),
    )
    assert plan.resolved_profile is Profile.RUNTIME
    assert all(step.timeout_seconds > 0 for step in plan.steps)
    assert plan.steps[-1].operation == "close_completion_receipt"


def test_auto_prefers_local_gpu_when_compatible() -> None:
    request = InstallationRequest(
        source=SourceSpec(SourceKind.LOCAL, "."),
        provider_policy=ProviderPolicy.AUTO,
    )
    plan = InstallationPlanner().build(
        request,
        _probe(Profile.CORE, Profile.RUNTIME, Profile.ASSISTANT_EXTERNAL, Profile.ASSISTANT_LOCAL_GPU),
    )
    assert plan.resolved_profile is Profile.ASSISTANT_LOCAL_GPU
    assert any(step.operation == "verify_or_install_gpu_loader" for step in plan.steps)


def test_incompatible_explicit_profile_rejected() -> None:
    request = InstallationRequest(
        source=SourceSpec(SourceKind.LOCAL, "."),
        profile=Profile.DEVELOPER,
    )
    with pytest.raises(InstallerSchemaError) as raised:
        InstallationPlanner().build(request, _probe(Profile.CORE))
    assert raised.value.code == "P172_PROFILE_INCOMPATIBLE"

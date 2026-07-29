from __future__ import annotations

from pathlib import Path

from hhs_installer.execution import CompleteInstallationTransaction
from hhs_installer.planner import InstallationPlan, PlanStep
from hhs_installer.probe import Capability, ProbeReport
from hhs_installer.schema import CompatibilityClass, InstallationRequest, NetworkPolicy, Profile, SourceKind, SourceSpec


def _probe() -> ProbeReport:
    return ProbeReport(
        platform="Linux",
        platform_release="test",
        architecture="x86_64",
        python_version="3.11",
        capabilities=(Capability("python_3_11", True, "3.11", ">=3.11"),),
        compatible_profiles=(Profile.CORE,),
        primary_classification=CompatibilityClass.CORE_ONLY,
        selected_ports={"api": 8000},
    )


def test_complete_transaction_registers_all_planned_handlers(tmp_path: Path) -> None:
    request = InstallationRequest(
        source=SourceSpec(SourceKind.LOCAL, str(tmp_path)),
        profile=Profile.CORE,
        hhs_home=str(tmp_path / "home"),
    )
    operations = (
        "acquire_source",
        "verify_source",
        "verify_offline_bundle",
        "verify_external_provider",
        "verify_or_install_gpu_loader",
        "install_local_provider",
        "acquire_verify_import_model",
        "verify_local_provider",
        "build_android_projection",
    )
    plan = InstallationPlan(
        request=request,
        probe_identity=_probe().probe_identity,
        requested_profile=Profile.CORE,
        resolved_profile=Profile.CORE,
        steps=tuple(PlanStep(str(index), operation, (), 5, "none", optional=True) for index, operation in enumerate(operations)),
        external_packages=(),
        excluded_dependency_classes=(),
    )
    transaction = CompleteInstallationTransaction(plan, _probe(), repository_root=tmp_path)
    assert set(operations).issubset(transaction.handlers)


def test_offline_network_release_is_rejected_without_network(tmp_path: Path) -> None:
    request = InstallationRequest(
        source=SourceSpec(SourceKind.RELEASE, "https://example.invalid/hhs.zip", "0" * 64),
        profile=Profile.CORE,
        network_policy=NetworkPolicy.OFFLINE,
        hhs_home=str(tmp_path / "home"),
    )
    step = PlanStep("source", "acquire_source", (), 5, "none")
    plan = InstallationPlan(
        request=request,
        probe_identity=_probe().probe_identity,
        requested_profile=Profile.CORE,
        resolved_profile=Profile.CORE,
        steps=(step,),
        external_packages=(),
        excluded_dependency_classes=(),
    )
    transaction = CompleteInstallationTransaction(plan, _probe(), repository_root=tmp_path)
    result = transaction.handlers["acquire_source"](step)
    assert result.result == "FAILURE"
    assert result.classification == "P172_OFFLINE_NETWORK_POLICY_VIOLATION"

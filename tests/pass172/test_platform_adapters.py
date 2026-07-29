from __future__ import annotations

from pathlib import Path

from hhs_installer.platforms.android import AndroidAdapter
from hhs_installer.platforms.base import PlatformAdapter
from hhs_installer.platforms.container import ContainerAdapter
from hhs_installer.platforms.linux import LinuxAdapter
from hhs_installer.platforms.macos import MacOSAdapter
from hhs_installer.platforms.windows import WindowsAdapter
from hhs_installer.probe import Capability, ProbeReport
from hhs_installer.schema import CompatibilityClass, Profile


def _probe(*profiles: Profile) -> ProbeReport:
    return ProbeReport(
        platform="Linux",
        platform_release="test",
        architecture="x86_64",
        python_version="3.12",
        capabilities=(Capability("python_3_11", True, "3.12", ">=3.11"),),
        compatible_profiles=profiles,
        primary_classification=CompatibilityClass.CORE_ONLY,
        selected_ports={"api": 8000},
    )


def test_generic_decision_refuses_unprobed_profile() -> None:
    decision = PlatformAdapter(system_name="Unknown").decide(_probe(Profile.CORE), Profile.RUNTIME)
    assert decision.compatible is False
    assert "P172_PROFILE_NOT_IN_PROBE_COMPATIBLE_SET" in decision.blockers


def test_linux_package_map_is_distribution_specific(monkeypatch) -> None:
    monkeypatch.setattr("shutil.which", lambda name: f"/usr/bin/{name}" if name == "apt-get" else None)
    plan = LinuxAdapter().package_plan(("python_venv", "c11_compiler"), Profile.CORE)
    assert plan is not None
    assert plan.package_manager == "apt-get"
    assert set(plan.packages) == {"python3-venv", "build-essential"}
    assert plan.requires_privilege is True


def test_macos_does_not_bootstrap_homebrew(monkeypatch) -> None:
    monkeypatch.setattr("shutil.which", lambda name: None)
    assert MacOSAdapter().package_plan(("python_3_11",), Profile.CORE) is None


def test_windows_uses_native_package_manager(monkeypatch) -> None:
    monkeypatch.setattr("shutil.which", lambda name: f"C:/{name}.exe" if name == "winget" else None)
    plan = WindowsAdapter().package_plan(("c11_compiler",), Profile.CORE)
    assert plan is not None
    assert plan.package_manager == "winget"
    assert "LLVM.LLVM" in plan.packages
    assert all("nm" not in " ".join(command) for command in plan.commands)


def test_android_and_container_boundaries() -> None:
    android = AndroidAdapter.toolchain_state()
    assert android["android_vulkan_loader_source"] == "operating-system-provided"
    container = ContainerAdapter.environment_state()
    assert "root_read_only" in container
    assert ContainerAdapter().package_plan(("python_3_11",), Profile.CONTAINER) is None

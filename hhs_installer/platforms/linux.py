from __future__ import annotations

import shutil

from .base import PackagePlan, PlatformAdapter
from ..schema import Profile


class LinuxAdapter(PlatformAdapter):
    adapter_id = "HHS-P172-LINUX"

    PACKAGE_MAP = {
        "apt-get": {
            "python_3_11": "python3",
            "python_venv": "python3-venv",
            "pip": "python3-pip",
            "c11_compiler": "build-essential",
            "linker": "binutils",
            "symbol_inspector": "binutils",
            "build_orchestrator": "make",
            "node": "nodejs",
            "npm": "npm",
            "java": "default-jdk",
            "vulkan_or_metal": "vulkan-tools",
        },
        "dnf": {
            "python_3_11": "python3",
            "python_venv": "python3",
            "pip": "python3-pip",
            "c11_compiler": "gcc",
            "linker": "binutils",
            "symbol_inspector": "binutils",
            "build_orchestrator": "make",
            "node": "nodejs",
            "npm": "npm",
            "java": "java-17-openjdk-devel",
            "vulkan_or_metal": "vulkan-tools",
        },
        "yum": {
            "python_3_11": "python3",
            "python_venv": "python3",
            "pip": "python3-pip",
            "c11_compiler": "gcc",
            "linker": "binutils",
            "symbol_inspector": "binutils",
            "build_orchestrator": "make",
            "node": "nodejs",
            "npm": "npm",
            "java": "java-17-openjdk-devel",
            "vulkan_or_metal": "vulkan-tools",
        },
        "pacman": {
            "python_3_11": "python",
            "python_venv": "python",
            "pip": "python-pip",
            "c11_compiler": "base-devel",
            "linker": "binutils",
            "symbol_inspector": "binutils",
            "build_orchestrator": "make",
            "node": "nodejs",
            "npm": "npm",
            "java": "jdk17-openjdk",
            "vulkan_or_metal": "vulkan-tools",
        },
        "apk": {
            "python_3_11": "python3",
            "python_venv": "python3",
            "pip": "py3-pip",
            "c11_compiler": "build-base",
            "linker": "binutils",
            "symbol_inspector": "binutils",
            "build_orchestrator": "make",
            "node": "nodejs",
            "npm": "npm",
            "java": "openjdk17",
            "vulkan_or_metal": "vulkan-tools",
        },
        "zypper": {
            "python_3_11": "python311",
            "python_venv": "python311",
            "pip": "python311-pip",
            "c11_compiler": "gcc",
            "linker": "binutils",
            "symbol_inspector": "binutils",
            "build_orchestrator": "make",
            "node": "nodejs22",
            "npm": "npm22",
            "java": "java-17-openjdk-devel",
            "vulkan_or_metal": "vulkan-tools",
        },
    }

    def package_plan(self, missing_capabilities: tuple[str, ...], profile: Profile) -> PackagePlan | None:
        manager = next((name for name in self.PACKAGE_MAP if shutil.which(name)), None)
        if not manager or not missing_capabilities:
            return None
        mapping = self.PACKAGE_MAP[manager]
        packages = tuple(sorted({mapping[item] for item in missing_capabilities if item in mapping}))
        if not packages:
            return None
        if manager == "apt-get":
            commands = ((manager, "update"), (manager, "install", "-y", *packages))
        elif manager in {"dnf", "yum"}:
            commands = ((manager, "install", "-y", *packages),)
        elif manager == "pacman":
            commands = ((manager, "-S", "--needed", "--noconfirm", *packages),)
        elif manager == "apk":
            commands = ((manager, "add", *packages),)
        else:
            commands = ((manager, "--non-interactive", "install", *packages),)
        return PackagePlan(
            package_manager=manager,
            packages=packages,
            commands=commands,
            requires_privilege=True,
            rollback_limitations=(
                "Host package manager mutations are not claimed atomically reversible.",
                "Preexisting packages are never removed by HHS rollback.",
            ),
        )

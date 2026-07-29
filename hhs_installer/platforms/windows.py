from __future__ import annotations

import shutil

from .base import PackagePlan, PlatformAdapter
from ..schema import Profile


class WindowsAdapter(PlatformAdapter):
    adapter_id = "HHS-P172-WINDOWS-NATIVE"

    def package_plan(self, missing_capabilities: tuple[str, ...], profile: Profile) -> PackagePlan | None:
        manager = "winget" if shutil.which("winget") else "choco" if shutil.which("choco") else None
        if not manager or not missing_capabilities:
            return None
        mapping = {
            "python_3_11": "Python.Python.3.12" if manager == "winget" else "python312",
            "python_venv": "Python.Python.3.12" if manager == "winget" else "python312",
            "pip": "Python.Python.3.12" if manager == "winget" else "python312",
            "c11_compiler": "LLVM.LLVM" if manager == "winget" else "llvm",
            "linker": "LLVM.LLVM" if manager == "winget" else "llvm",
            "symbol_inspector": "LLVM.LLVM" if manager == "winget" else "llvm",
            "build_orchestrator": "Ninja-build.Ninja" if manager == "winget" else "ninja",
            "node": "OpenJS.NodeJS.LTS" if manager == "winget" else "nodejs-lts",
            "npm": "OpenJS.NodeJS.LTS" if manager == "winget" else "nodejs-lts",
            "java": "EclipseAdoptium.Temurin.17.JDK" if manager == "winget" else "temurin17",
        }
        packages = tuple(sorted({mapping[item] for item in missing_capabilities if item in mapping}))
        if not packages:
            return None
        if manager == "winget":
            commands = tuple((manager, "install", "--exact", "--accept-source-agreements", "--accept-package-agreements", "--id", package) for package in packages)
        else:
            commands = ((manager, "install", "-y", *packages),)
        return PackagePlan(
            package_manager=manager,
            packages=packages,
            commands=commands,
            requires_privilege=True,
            rollback_limitations=(
                "Windows package-manager prompts and firewall decisions are host-controlled.",
                "Preexisting packages are never removed by HHS rollback.",
                "Native Windows support does not invoke GNU-only nm -D assumptions.",
            ),
        )

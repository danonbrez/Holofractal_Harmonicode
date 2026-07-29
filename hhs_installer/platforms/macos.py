from __future__ import annotations

import shutil

from .base import PackagePlan, PlatformAdapter
from ..schema import Profile


class MacOSAdapter(PlatformAdapter):
    adapter_id = "HHS-P172-MACOS"

    def package_plan(self, missing_capabilities: tuple[str, ...], profile: Profile) -> PackagePlan | None:
        brew = shutil.which("brew")
        if not brew or not missing_capabilities:
            return None
        mapping = {
            "python_3_11": "python@3.12",
            "python_venv": "python@3.12",
            "pip": "python@3.12",
            "c11_compiler": "llvm",
            "linker": "llvm",
            "symbol_inspector": "llvm",
            "build_orchestrator": "make",
            "node": "node@22",
            "npm": "node@22",
            "java": "openjdk@17",
        }
        packages = tuple(sorted({mapping[item] for item in missing_capabilities if item in mapping}))
        if not packages:
            return None
        return PackagePlan(
            package_manager="brew",
            packages=packages,
            commands=((brew, "install", *packages),),
            requires_privilege=False,
            rollback_limitations=(
                "Homebrew installation itself is never silently bootstrapped.",
                "Preexisting formulas are not removed by HHS rollback.",
                "Metal is probed from macOS and is not installed by Homebrew.",
            ),
        )

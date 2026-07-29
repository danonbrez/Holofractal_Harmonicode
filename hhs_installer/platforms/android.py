from __future__ import annotations

from pathlib import Path
import os
import shutil

from .base import PackagePlan, PlatformAdapter
from ..schema import Profile


class AndroidAdapter(PlatformAdapter):
    adapter_id = "HHS-P172-ANDROID-TERMUX"

    @staticmethod
    def toolchain_state() -> dict[str, object]:
        sdk = os.environ.get("ANDROID_SDK_ROOT") or os.environ.get("ANDROID_HOME")
        ndk = os.environ.get("ANDROID_NDK_HOME") or os.environ.get("ANDROID_NDK_ROOT")
        return {
            "java": shutil.which("java"),
            "sdk": sdk,
            "ndk": ndk,
            "cmake": shutil.which("cmake"),
            "gradle": shutil.which("gradle"),
            "adb": shutil.which("adb"),
            "sdk_exists": bool(sdk and Path(sdk).is_dir()),
            "ndk_exists": bool(ndk and Path(ndk).is_dir()),
            "android_vulkan_loader_source": "operating-system-provided",
        }

    def package_plan(self, missing_capabilities: tuple[str, ...], profile: Profile) -> PackagePlan | None:
        pkg = shutil.which("pkg")
        if not pkg or not missing_capabilities:
            return None
        mapping = {
            "python_3_11": "python",
            "python_venv": "python",
            "pip": "python-pip",
            "c11_compiler": "clang",
            "linker": "binutils",
            "symbol_inspector": "binutils",
            "build_orchestrator": "make",
            "node": "nodejs-lts",
            "npm": "nodejs-lts",
            "java": "openjdk-17",
        }
        packages = tuple(sorted({mapping[item] for item in missing_capabilities if item in mapping}))
        if not packages:
            return None
        return PackagePlan(
            package_manager="pkg",
            packages=packages,
            commands=((pkg, "install", "-y", *packages),),
            requires_privilege=False,
            rollback_limitations=(
                "Android application sandbox and background-service limits remain host constraints.",
                "The Android operating system Vulkan loader is not replaced by a desktop Linux loader.",
                "APK/AAB production remains unavailable until the complete external Android toolchain is verified.",
            ),
        )

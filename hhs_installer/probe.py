from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable
import os
import platform
import shutil
import socket
import subprocess
import sys

from .canonical import hash216
from .schema import CompatibilityClass, Profile


@dataclass(frozen=True)
class Capability:
    capability_id: str
    available: bool
    detected: str
    required: str
    repairable: bool = False
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProbeReport:
    platform: str
    platform_release: str
    architecture: str
    python_version: str
    capabilities: tuple[Capability, ...]
    compatible_profiles: tuple[Profile, ...]
    primary_classification: CompatibilityClass
    selected_ports: dict[str, int]
    probe_identity: str = ""

    def __post_init__(self) -> None:
        if not self.probe_identity:
            payload = self.to_dict(include_identity=False)
            object.__setattr__(self, "probe_identity", hash216(payload, domain="HHS-P172-ENVIRONMENT-PROBE-V1"))

    def to_dict(self, *, include_identity: bool = True) -> dict[str, Any]:
        result = {
            "platform": self.platform,
            "platform_release": self.platform_release,
            "architecture": self.architecture,
            "python_version": self.python_version,
            "capabilities": [item.to_dict() for item in self.capabilities],
            "compatible_profiles": [item.value for item in self.compatible_profiles],
            "primary_classification": self.primary_classification.value,
            "selected_ports": dict(sorted(self.selected_ports.items())),
        }
        if include_identity:
            result["probe_identity"] = self.probe_identity
        return result

    def capability(self, capability_id: str) -> Capability:
        for item in self.capabilities:
            if item.capability_id == capability_id:
                return item
        raise KeyError(capability_id)


class EnvironmentProbe:
    """Read-only capability probe.

    The probe never invokes binaries from the repository working tree. Commands
    are resolved through PATH and bounded by a short timeout.
    """

    def __init__(self, *, command_timeout: int = 5, candidate_ports: Iterable[int] = (8000, 8080, 8765, 9379)) -> None:
        if command_timeout < 1 or command_timeout > 60:
            raise ValueError("P172_PROBE_TIMEOUT_INVALID")
        self.command_timeout = command_timeout
        self.candidate_ports = tuple(int(port) for port in candidate_ports)

    @staticmethod
    def _which(*names: str) -> str | None:
        for name in names:
            path = shutil.which(name)
            if path:
                return path
        return None

    def _version(self, executable: str | None, *args: str) -> str:
        if not executable:
            return "absent"
        try:
            completed = subprocess.run(
                [executable, *args],
                check=False,
                capture_output=True,
                text=True,
                timeout=self.command_timeout,
                env={**os.environ, "LC_ALL": "C"},
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return f"unavailable:{type(exc).__name__}"
        output = (completed.stdout or completed.stderr).strip().splitlines()
        first = output[0] if output else "no-version-output"
        return f"exit={completed.returncode}:{first[:240]}"

    @staticmethod
    def _can_bind_loopback(port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                return False
            return True

    def run(self, *, target: str | Path | None = None) -> ProbeReport:
        system = platform.system() or "Unknown"
        architecture = platform.machine() or "unknown"
        target_path = Path(target).expanduser() if target else Path.home()
        python_ok = sys.version_info >= (3, 11)
        compiler = self._which("cc", "clang", "gcc")
        linker = self._which("ld", "lld", "link")
        symbol_tool = self._which("nm", "llvm-nm", "dumpbin")
        make = self._which("make", "gmake", "ninja")
        node = self._which("node")
        npm = self._which("npm")
        java = self._which("java")
        container = self._which("docker", "podman")
        vulkan = self._which("vulkaninfo")
        package_manager = self._which("apt-get", "dnf", "yum", "pacman", "apk", "zypper", "brew", "winget", "choco", "pkg")

        try:
            writable = target_path.exists() and os.access(target_path, os.W_OK)
        except OSError:
            writable = False
        try:
            disk_free = shutil.disk_usage(target_path if target_path.exists() else target_path.parent).free
        except OSError:
            disk_free = 0

        selected_ports: dict[str, int] = {}
        for label, preferred in (("api", 8000), ("provider", 9379)):
            candidates = (preferred,) + tuple(port for port in self.candidate_ports if port != preferred)
            for port in candidates:
                if self._can_bind_loopback(port):
                    selected_ports[label] = port
                    break

        android_sdk = os.environ.get("ANDROID_SDK_ROOT") or os.environ.get("ANDROID_HOME")
        android_ndk = os.environ.get("ANDROID_NDK_HOME") or os.environ.get("ANDROID_NDK_ROOT")
        gpu_paths = [Path("/dev/dri/renderD128"), Path("/dev/nvidia0")]
        gpu_visible = any(path.exists() for path in gpu_paths) or system == "Darwin"

        capabilities = (
            Capability("python_3_11", python_ok, platform.python_version(), ">=3.11", repairable=bool(package_manager)),
            Capability("python_venv", hasattr(__import__("venv"), "EnvBuilder"), "stdlib venv", "available"),
            Capability("pip", self._which("pip", "pip3") is not None, self._version(self._which("pip", "pip3"), "--version"), "available", repairable=bool(package_manager)),
            Capability("c11_compiler", compiler is not None, self._version(compiler, "--version"), "portable C11 compiler", repairable=bool(package_manager)),
            Capability("linker", linker is not None, str(linker or "absent"), "linker", repairable=bool(package_manager)),
            Capability("symbol_inspector", symbol_tool is not None, str(symbol_tool or "absent"), "nm/llvm-nm/dumpbin", repairable=bool(package_manager)),
            Capability("build_orchestrator", make is not None, str(make or "absent"), "make/ninja or Python native builder", repairable=bool(package_manager)),
            Capability("writable_target", writable, str(target_path), "writable target"),
            Capability("disk_space", disk_free >= 512 * 1024 * 1024, str(disk_free), ">=536870912 bytes"),
            Capability("loopback", "api" in selected_ports, str(selected_ports), "available API loopback port"),
            Capability("node", node is not None, self._version(node, "--version"), ">=22 for developer profile", repairable=bool(package_manager)),
            Capability("npm", npm is not None, self._version(npm, "--version"), "available for developer profile", repairable=bool(package_manager)),
            Capability("java", java is not None, self._version(java, "-version"), "JDK for Android build", repairable=bool(package_manager)),
            Capability("android_sdk", bool(android_sdk), str(android_sdk or "absent"), "Android SDK for android-build"),
            Capability("android_ndk", bool(android_ndk), str(android_ndk or "absent"), "Android NDK for android-build"),
            Capability("container_runtime", container is not None, self._version(container, "--version"), "Docker or Podman for container profile"),
            Capability("gpu_device", gpu_visible, "visible" if gpu_visible else "absent", "physical accelerator for local GPU profile"),
            Capability("vulkan_or_metal", bool(vulkan) or system == "Darwin", self._version(vulkan, "--summary") if system != "Darwin" else "Metal platform", "Vulkan or Metal for local GPU profile"),
            Capability("package_manager", package_manager is not None, str(package_manager or "absent"), "optional automatic host repair"),
        )

        base_ok = all(item.available for item in capabilities if item.capability_id in {"python_3_11", "python_venv", "c11_compiler", "writable_target", "disk_space", "loopback"})
        profiles: list[Profile] = []
        if base_ok:
            profiles.extend([Profile.CORE, Profile.RUNTIME])
            profiles.append(Profile.ASSISTANT_EXTERNAL)
            if compiler and node and npm:
                profiles.append(Profile.DEVELOPER)
            if gpu_visible and (vulkan or system == "Darwin") and "provider" in selected_ports:
                profiles.append(Profile.ASSISTANT_LOCAL_GPU)
            if java and android_sdk and android_ndk:
                profiles.append(Profile.ANDROID_BUILD)
            if container:
                profiles.append(Profile.CONTAINER)
        if base_ok:
            profiles.append(Profile.OFFLINE)

        if Profile.ASSISTANT_LOCAL_GPU in profiles:
            primary = CompatibilityClass.FULLY_COMPATIBLE
        elif base_ok and Profile.ASSISTANT_EXTERNAL in profiles:
            primary = CompatibilityClass.EXTERNAL_PROVIDER
        elif base_ok:
            primary = CompatibilityClass.CORE_ONLY
        elif any(item.repairable and not item.available for item in capabilities):
            primary = CompatibilityClass.REPAIRABLE
        else:
            primary = CompatibilityClass.INCOMPATIBLE

        return ProbeReport(
            platform=system,
            platform_release=platform.release(),
            architecture=architecture,
            python_version=platform.python_version(),
            capabilities=capabilities,
            compatible_profiles=tuple(dict.fromkeys(profiles)),
            primary_classification=primary,
            selected_ports=selected_ports,
        )

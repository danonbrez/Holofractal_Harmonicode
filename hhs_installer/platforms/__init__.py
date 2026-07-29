from __future__ import annotations

import platform

from .base import PlatformAdapter, PlatformDecision
from .android import AndroidAdapter
from .container import ContainerAdapter
from .linux import LinuxAdapter
from .macos import MacOSAdapter
from .windows import WindowsAdapter


def current_adapter() -> PlatformAdapter:
    system = platform.system()
    if system == "Linux":
        return LinuxAdapter()
    if system == "Darwin":
        return MacOSAdapter()
    if system == "Windows":
        return WindowsAdapter()
    return PlatformAdapter(system_name=system or "Unknown")


__all__ = [
    "PlatformAdapter",
    "PlatformDecision",
    "LinuxAdapter",
    "MacOSAdapter",
    "WindowsAdapter",
    "AndroidAdapter",
    "ContainerAdapter",
    "current_adapter",
]

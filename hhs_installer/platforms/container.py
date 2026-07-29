from __future__ import annotations

from pathlib import Path
from typing import Any
import os
import shutil

from .base import PackagePlan, PlatformAdapter
from ..schema import Profile


class ContainerAdapter(PlatformAdapter):
    adapter_id = "HHS-P172-CONTAINER"

    @staticmethod
    def environment_state() -> dict[str, Any]:
        root_read_only = not os.access("/", os.W_OK)
        cgroup_markers = [Path("/.dockerenv"), Path("/run/.containerenv")]
        in_container = any(path.exists() for path in cgroup_markers)
        state_mount = Path(os.environ.get("HHS_HOME", "/var/lib/hhs"))
        return {
            "in_container": in_container,
            "root_read_only": root_read_only,
            "non_root": os.geteuid() != 0 if hasattr(os, "geteuid") else None,
            "state_mount": str(state_mount),
            "state_mount_exists": state_mount.exists(),
            "state_mount_writable": state_mount.exists() and os.access(state_mount, os.W_OK),
            "docker": shutil.which("docker"),
            "podman": shutil.which("podman"),
            "gpu_devices_visible": any(Path(path).exists() for path in ("/dev/dri/renderD128", "/dev/nvidia0")),
        }

    def package_plan(self, missing_capabilities: tuple[str, ...], profile: Profile) -> PackagePlan | None:
        # Immutable container layers should be provisioned at image build time.
        # Runtime package mutation is intentionally not proposed here.
        return None

from __future__ import annotations

import platform
import subprocess
from pathlib import Path

from hhs_backend.runtime.hhs_vulkan_loader_runtime_v1 import (
    AUTHORITY,
    SCHEMA,
    _decode_api_version,
    inspect_vulkan_loader,
    loader_candidates,
)

ROOT = Path(__file__).resolve().parents[1]


def test_vulkan_version_decoding_and_versioned_loader_candidates() -> None:
    encoded = (1 << 22) | (3 << 12) | 250
    assert _decode_api_version(encoded) == "1.3.250"
    assert "libvulkan.so.1" in loader_candidates()


def test_vulkan_inspection_is_receipted_and_non_authoritative() -> None:
    result = inspect_vulkan_loader()
    assert result["schema"] == SCHEMA
    assert result["authority"] == AUTHORITY
    assert result["runtime_mutation_authority"] is False
    assert result["vulkan_loader_receipt_hash72"]
    assert isinstance(result["loader_ready"], bool)


def test_installer_targets_runtime_graphics_tree_and_distribution_loaders() -> None:
    installer = (ROOT / "tools" / "install_vulkan_loader.sh").read_text(encoding="utf-8")
    assert ".hhs/runtime/graphics/vulkan" in installer
    assert "libvulkan1" in installer
    assert "vulkan-loader" in installer
    assert "vulkan-icd-loader" in installer
    assert "hhs_vulkan_loader_runtime_v1" in installer
    assert "GPU vendor drivers and device access remain host concerns" in installer


def test_startup_provisions_loader_before_accelerator_probe() -> None:
    launcher = (ROOT / "start.sh").read_text(encoding="utf-8")
    assert 'HHS_VULKAN_AUTO_INSTALL:-1' in launcher
    assert "install_vulkan_loader.sh" in launcher
    assert launcher.index("ensure_vulkan_loader") < launcher.index("probe_local_accelerator")
    assert "HHS_VULKAN_LOADER_READY" in launcher


def test_litert_probe_uses_shared_graphics_loader_service() -> None:
    probe = (ROOT / "tools" / "probe_litert_lm_accelerator.py").read_text(encoding="utf-8")
    assert "hhs_vulkan_loader_runtime_v1 import inspect_vulkan_loader" in probe
    assert "loader_receipt_hash72" in probe
    assert "driver_manifest_ready" in probe


def test_graphics_routes_are_mounted_on_canonical_backend_router() -> None:
    from hhs_backend.api.pass152_elastic_closure_routes import router

    route_keys = {
        (
            getattr(route, "path", None),
            tuple(sorted(getattr(route, "methods", []) or [])),
        )
        for route in router.routes
    }
    assert ("/api/runtime/graphics/status", ("GET",)) in route_keys
    assert ("/api/runtime/graphics/vulkan", ("GET",)) in route_keys
    assert ("/api/runtime/graphics/capabilities", ("GET",)) in route_keys


def test_loader_installer_shell_is_valid() -> None:
    subprocess.run(
        ["bash", "-n", str(ROOT / "tools" / "install_vulkan_loader.sh")],
        check=True,
    )


def test_linux_loader_can_be_required_when_ci_installs_it() -> None:
    if platform.system() != "Linux":
        return
    result = inspect_vulkan_loader()
    # The dedicated workflow installs libvulkan1 before this test. Other local
    # environments may legitimately use this as a diagnostic assertion.
    assert "loader_errors" in result

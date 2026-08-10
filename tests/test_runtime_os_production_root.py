from __future__ import annotations

from pathlib import Path


def test_runtime_os_build_is_repository_visible():
    root = Path("hhs_gui/dist").resolve()
    index = root / "index.html"
    assets = root / "assets"

    assert index.is_file()
    assert assets.is_dir()

    html = index.read_text(encoding="utf-8")
    assert "HHS Visual Runtime OS Workspace" in html
    assert "/assets/index-" in html


def test_digitalocean_gateway_selects_runtime_os_projection_by_source():
    source = Path("hhs_backend/production_visual_server.py").read_text(encoding="utf-8")

    assert "from hhs_backend.runtime_os_visual_server import app as authoritative_app" in source
    assert "from hhs_backend.visual_server import app as authoritative_app" not in source


def test_runtime_os_projection_replaces_only_legacy_public_root():
    from hhs_backend import runtime_os_visual_server

    assert runtime_os_visual_server.RUNTIME_OS_ROOT == Path("hhs_gui/dist").resolve()
    assert runtime_os_visual_server.RUNTIME_OS_INDEX.is_file()
    assert runtime_os_visual_server.RUNTIME_OS_ASSETS.is_dir()

    route_names = {
        str(getattr(route, "name", ""))
        for route in runtime_os_visual_server.app.router.routes
    }
    route_paths = {
        str(getattr(route, "path", ""))
        for route in runtime_os_visual_server.app.router.routes
    }

    assert runtime_os_visual_server.PUBLIC_MOUNT_NAME in route_names
    assert "hhs-visual-home" not in route_names
    assert "/api/interface/status" in route_paths

    # Backend/pass routes remain reachable before the SPA root mount.
    for required in {
        "/api/system/status",
        "/api/assistant/status",
        "/api/runtime/installation/status",
        "/api/runtime/integration/status",
        "/api/public/status",
    }:
        assert required in route_paths


def test_legacy_harmonizer_remains_inherited_source_not_public_authority():
    legacy_root = Path("applications/holofractal_harmonizer")
    assert (legacy_root / "index.html").is_file()

    projection = Path("hhs_backend/runtime_os_visual_server.py").read_text(encoding="utf-8")
    assert '"legacy_harmonizer_is_public_root": False' in projection
    assert 'RUNTIME_OS_ROOT = ROOT_DIR / "hhs_gui" / "dist"' in projection

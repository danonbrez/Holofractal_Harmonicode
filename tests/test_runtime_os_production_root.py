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
    assert "Pass Runtime OS HTML/assets through unchanged" in source


def test_procfile_selects_full_runtime_os_application_projection():
    procfile = Path("Procfile").read_text(encoding="utf-8")
    application_source = Path("hhs_backend/runtime_os_application_server.py").read_text(
        encoding="utf-8"
    )

    assert "hhs_backend.runtime_os_application_server:app" in procfile
    assert "hhs_backend.application_ide_server:app" not in procfile
    assert "from hhs_backend.application_ide_server import app as inherited_app" in application_source
    assert "project_runtime_os(app, mount_name=PUBLIC_MOUNT_NAME)" in application_source


def test_runtime_os_projection_replaces_only_legacy_public_root():
    from hhs_backend import runtime_os_visual_server
    from hhs_backend.runtime_os_projection import LEGACY_PUBLIC_ROOT_NAMES

    assert runtime_os_visual_server.RUNTIME_OS_ROOT == Path("hhs_gui/dist").resolve()
    assert runtime_os_visual_server.RUNTIME_OS_INDEX.is_file()
    assert runtime_os_visual_server.RUNTIME_OS_ASSETS.is_dir()

    routes = list(runtime_os_visual_server.app.router.routes)
    route_names = {str(getattr(route, "name", "")) for route in routes}
    route_paths = {str(getattr(route, "path", "")) for route in routes}

    assert runtime_os_visual_server.PUBLIC_MOUNT_NAME in route_names
    assert "hhs-visual-home" not in route_names
    assert "/api/interface/status" in route_paths

    root_mounts = [
        route
        for route in routes
        if getattr(route, "name", None) in LEGACY_PUBLIC_ROOT_NAMES
    ]
    assert len(root_mounts) == 1
    assert root_mounts[0].name == runtime_os_visual_server.PUBLIC_MOUNT_NAME

    root_index = next(
        index
        for index, route in enumerate(routes)
        if getattr(route, "name", None) == runtime_os_visual_server.PUBLIC_MOUNT_NAME
    )

    # Backend/pass routes remain reachable before the SPA root mount.
    for required in {
        "/api/system/status",
        "/api/assistant/status",
        "/api/runtime/installation/status",
        "/api/runtime/integration/status",
        "/api/public/status",
    }:
        assert required in route_paths
        route_index = next(
            index
            for index, route in enumerate(routes)
            if str(getattr(route, "path", "")) == required
        )
        assert route_index < root_index


def test_digitalocean_service_uses_one_versioned_runtime_os_release():
    service = Path("deploy/digitalocean/hhs-pass196-integrated-environment.service").read_text(
        encoding="utf-8"
    )
    validator = Path(
        "deployment/digitalocean/guarded_auto_update/validate-candidate.sh"
    ).read_text(encoding="utf-8")
    builder = Path(
        "deployment/digitalocean/guarded_auto_update/build-runtime-os.sh"
    ).read_text(encoding="utf-8")

    assert "Environment=HHS_RUNTIME_OS_ASSET_ROOT=/var/lib/hhs/runtime-os/current" in service
    assert "Environment=HHS_RUNTIME_OS_ASSET_ROOT=/var/lib/hhs/runtime-os/dist" not in service
    assert "Environment=HHS_RUNTIME_OS_ROOT=" not in service

    assert 'HHS_RUNTIME_OS_ASSET_ROOT="$RUNTIME_OS_ROOT"' in validator
    assert 'env -u HHS_RUNTIME_OS_ROOT' in validator
    assert 'HHS_RUNTIME_OS_ROOT="$RUNTIME_OS_ROOT"' not in validator

    # Source builds may still exist for CI/development, but production service
    # authority is never bound to that secondary generated directory.
    assert 'LIVE_ROOT=$(realpath -m "$ROOT")' in builder
    assert 'OUTPUT_ROOT=/var/lib/hhs/runtime-os/dist' in builder


def test_legacy_harmonizer_remains_inherited_source_not_public_authority():
    legacy_root = Path("applications/holofractal_harmonizer")
    assert (legacy_root / "index.html").is_file()

    projection = Path("hhs_backend/runtime_os_projection.py").read_text(encoding="utf-8")
    assert '"legacy_harmonizer_is_public_root": False' in projection
    assert 'os.environ.get("HHS_RUNTIME_OS_ASSET_ROOT")' in projection
    assert 'RUNTIME_OS_SOURCE_ROOT = ROOT_DIR / "hhs_gui"' in projection

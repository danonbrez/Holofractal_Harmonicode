from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from hhs_backend import application_ide_server as server
from hhs_backend.public_ide_bootstrap import LEGACY_PUBLIC_MODULES


PUBLIC_SOURCE_ASSETS = (
    "public-boot.mjs",
    "application-experience.mjs",
    "production-startup-coordinator.mjs",
    "browser.mjs",
    "ux-default.mjs",
    "production-integration.mjs",
    "visual-ide.mjs",
    "styles.css",
    "application-studio.css",
)

SUCCESSOR_STATUS_PATHS = (
    "/api/runtime/integration/status",
    "/api/runtime/calibration/status",
    "/api/runtime/calibration-registry/status",
    "/api/runtime/distributed-calibration/status",
    "/api/runtime/optimization-authority/status",
    "/api/runtime/optimization-canary/status",
    "/api/runtime/optimization-active/status",
)


def test_full_application_ide_is_public_root_and_console_is_preserved() -> None:
    routes = list(server.app.router.routes)
    names = [getattr(route, "name", None) for route in routes]
    paths = [str(getattr(route, "path", "")) for route in routes]

    assert server.FULL_IDE_ROOT.name == "holofractal_harmonizer"
    assert server.RUNTIME_CONSOLE_ROOT.name == "pass174_visual_ide"
    assert "hhs-full-application-ide-index" in names
    assert "hhs-full-application-ide" in names
    assert "hhs-pass174-runtime-console" in names
    assert server.production.VISUAL_SOURCE_MOUNT_NAME in names
    assert names.index("hhs-full-application-ide-index") < names.index("hhs-full-application-ide")
    assert paths.index("/src") < names.index("hhs-full-application-ide")
    assert paths.index("/runtime-console") < names.index("hhs-full-application-ide")
    assert server.pass174.PASS174_BOOT_STATE["application_ide_is_public_root"] is True
    assert server.pass174.PASS174_BOOT_STATE["diagnostic_console_is_supporting_surface"] is True
    assert server.pass174.PASS174_BOOT_STATE["inline_public_boot"] == "HHS_INLINE_PUBLIC_BOOT_V2"


def test_successor_api_routes_precede_fail_closed_fallback() -> None:
    paths = [str(getattr(route, "path", "")) for route in server.app.router.routes]
    fallback_indexes = [
        index
        for index, path in enumerate(paths)
        if path == server.API_FALLBACK_PATH
    ]
    assert fallback_indexes, "full application composition lost the fail-closed API fallback"
    first_fallback = min(fallback_indexes)

    for path in SUCCESSOR_STATUS_PATHS:
        assert path in paths, path
        assert paths.index(path) < first_fallback, f"{path} is shadowed by {server.API_FALLBACK_PATH}"

    assert server.pass174.PASS174_BOOT_STATE["pass196_integration_routes"] is True
    assert server.pass174.PASS174_BOOT_STATE["pass199_distributed_calibration_routes"] is True
    assert server.pass174.PASS174_BOOT_STATE["pass200c_active_routes"] is True


def test_successor_status_endpoints_do_not_fall_through_to_not_found_envelope() -> None:
    client = TestClient(server.app)
    for path in SUCCESSOR_STATUS_PATHS:
        response = client.get(path)
        assert response.status_code != 404, (path, response.text[:500])
        payload = response.json()
        assert payload.get("schema") != "HHS_PRODUCTION_API_ROUTE_NOT_FOUND_V1", path


def test_public_root_has_one_boot_authority_and_preserved_module_lineage() -> None:
    client = TestClient(server.app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["x-hhs-public-boot"] == "HHS_INLINE_PUBLIC_BOOT_V2"
    assert response.headers["x-hhs-legacy-module-entries"] == "disabled"
    assert "HHS Full Multimodal Application IDE" in response.text
    assert "src/application-studio.css" in response.text
    assert "src/visual-ide.mjs" in response.text
    assert response.text.count("data-hhs-inline-public-boot") == 1
    assert "HHS_INLINE_PUBLIC_BOOT_V2" in response.text
    assert "import(moduleUrl)" in response.text
    assert response.text.index("data-hhs-inline-public-boot") < response.text.index("</body>")

    for module_name in LEGACY_PUBLIC_MODULES:
        marker = f"data-hhs-legacy-module-disabled src=./src/{module_name}"
        assert response.text.count(marker) == 1, module_name
        assert f'<script type="module" src="./src/{module_name}"></script>' not in response.text

    for asset in PUBLIC_SOURCE_ASSETS:
        asset_response = client.get(f"/src/{asset}")
        assert asset_response.status_code == 200, (asset, asset_response.text[:200])
        assert asset_response.content, asset
        if asset.endswith(".mjs"):
            assert "javascript" in asset_response.headers.get("content-type", ""), asset
        else:
            assert "text/css" in asset_response.headers.get("content-type", ""), asset

    console = client.get("/runtime-console/")
    assert console.status_code == 200
    assert "Pass 174 Harmonic Visual SDLC Runtime" in console.text


def test_procfile_launches_final_application_composition() -> None:
    procfile = Path("Procfile").read_text(encoding="utf-8")
    assert "hhs_backend.application_ide_server:app" in procfile
    assert "hhs_backend.pass174_server:app" not in procfile

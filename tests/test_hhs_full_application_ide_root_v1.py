from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from hhs_backend import application_ide_server as server


PUBLIC_SOURCE_ASSETS = (
    "public-boot.mjs",
    "production-startup-coordinator.mjs",
    "browser.mjs",
    "ux-default.mjs",
    "production-integration.mjs",
    "visual-ide.mjs",
    "styles.css",
    "application-studio.css",
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
    assert server.pass174.PASS174_BOOT_STATE["inline_public_boot"] == "HHS_INLINE_PUBLIC_BOOT_V1"


def test_public_root_contains_full_ide_and_parsing_time_module_launcher() -> None:
    client = TestClient(server.app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["x-hhs-public-boot"] == "HHS_INLINE_PUBLIC_BOOT_V1"
    assert "HHS Full Multimodal Application IDE" in response.text
    assert "src/application-studio.css" in response.text
    assert "src/visual-ide.mjs" in response.text
    assert "data-hhs-inline-public-boot" in response.text
    assert "HHS_INLINE_PUBLIC_BOOT_V1" in response.text
    assert "import(moduleUrl)" in response.text
    assert response.text.index("data-hhs-inline-public-boot") < response.text.index("</body>")

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

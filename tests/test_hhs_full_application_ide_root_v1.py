from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from hhs_backend import application_ide_server as server


def test_full_application_ide_is_public_root_and_console_is_preserved() -> None:
    routes = list(server.app.router.routes)
    names = [getattr(route, "name", None) for route in routes]
    paths = [str(getattr(route, "path", "")) for route in routes]

    assert server.FULL_IDE_ROOT.name == "holofractal_harmonizer"
    assert server.RUNTIME_CONSOLE_ROOT.name == "pass174_visual_ide"
    assert "hhs-full-application-ide" in names
    assert "hhs-pass174-runtime-console" in names
    assert paths.index("/runtime-console") < names.index("hhs-full-application-ide")
    assert server.pass174.PASS174_BOOT_STATE["application_ide_is_public_root"] is True
    assert server.pass174.PASS174_BOOT_STATE["diagnostic_console_is_supporting_surface"] is True


def test_public_root_contains_full_ide_and_representative_application_studio() -> None:
    client = TestClient(server.app)
    response = client.get("/")
    assert response.status_code == 200
    assert "HHS Full Multimodal Application IDE" in response.text
    assert "src/application-studio.css" in response.text
    assert "src/visual-ide.mjs" in response.text

    console = client.get("/runtime-console/")
    assert console.status_code == 200
    assert "Pass 174 Harmonic Visual SDLC Runtime" in console.text


def test_procfile_launches_final_application_composition() -> None:
    procfile = Path("Procfile").read_text(encoding="utf-8")
    assert "hhs_backend.application_ide_server:app" in procfile
    assert "hhs_backend.pass174_server:app" not in procfile

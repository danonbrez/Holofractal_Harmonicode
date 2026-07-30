"""Final HHS production composition with the full application IDE at ``/``.

All inherited Pass 174 APIs, VM81/Hash216 authorities, WebSockets, readiness
semantics, assistant routes, multimodal ingress, compiler services, and legacy
contracts remain registered by :mod:`hhs_backend.pass174_server`. This final
composition changes only the public visual mapping:

* ``/`` serves the complete Holofractal Harmonizer application IDE.
* ``/runtime-console/`` preserves the prior Pass 174 diagnostic console.

Static mounts are installed last so they cannot shadow any API or WebSocket.
"""
from __future__ import annotations

from fastapi.staticfiles import StaticFiles

from hhs_backend import pass174_server as pass174
from hhs_backend import production_server as production

app = pass174.app
app.title = "HHS Full Multimodal Application IDE"
app.version = "4.1.0"
app.description = (
    "Full integrated development environment for real web applications, games, "
    "calculators, documents, audio, video, multimodal projects, HARMONICODE, "
    "multi-target compilation, VM81 execution, repository lineage, assistant-led "
    "development, application preview, testing, and ZIP egress."
)

FULL_IDE_ROOT = production.VISUAL_ROOT
RUNTIME_CONSOLE_ROOT = pass174._ide_root

# Remove inherited visual mounts only. Every API, WebSocket, health, readiness,
# workspace, assistant, compiler, ingress, receipt, and replay route is retained.
app.router.routes = [
    route
    for route in app.router.routes
    if getattr(route, "name", None) not in {
        "hhs-production-harmonizer",
        "hhs-pass174-visual-ide",
        "hhs-pass174-legacy-ide",
        "hhs-pass174-runtime-console",
        "hhs-full-application-ide",
    }
]

if RUNTIME_CONSOLE_ROOT.is_dir():
    app.mount(
        "/runtime-console",
        StaticFiles(directory=str(RUNTIME_CONSOLE_ROOT), html=True),
        name="hhs-pass174-runtime-console",
    )

if FULL_IDE_ROOT.is_dir() and (FULL_IDE_ROOT / "index.html").is_file():
    app.mount(
        "/",
        StaticFiles(directory=str(FULL_IDE_ROOT), html=True),
        name="hhs-full-application-ide",
    )
else:
    pass174.PASS174_BOOT_STATE.update({
        "classification": "HHS_FULL_APPLICATION_IDE_ASSET_ROOT_MISSING",
        "full_ide_root": str(FULL_IDE_ROOT),
        "ready": False,
        "authority_ready": False,
        "degraded": True,
    })

pass174.PASS174_BOOT_STATE.update({
    "public_interface": "HHS_FULL_MULTIMODAL_APPLICATION_IDE",
    "public_asset_root": str(FULL_IDE_ROOT),
    "runtime_console_root": str(RUNTIME_CONSOLE_ROOT),
    "runtime_console_preserved": RUNTIME_CONSOLE_ROOT.is_dir(),
    "application_ide_is_public_root": True,
    "diagnostic_console_is_supporting_surface": True,
})

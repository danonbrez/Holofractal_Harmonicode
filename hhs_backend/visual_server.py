"""Default HHS visual development environment server.

This module composes the canonical HHS FastAPI runtime, governed assistant,
installation, application-factory, media, hydration, Pass 196 integration,
Pass 197 exact A/B calibration, Pass 198 operation calibration registry, and
the Pass 161 visual application. The canonical server remains runtime
authority; this module only changes HTTP projection.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fastapi.staticfiles import StaticFiles

from hhs_backend import server as canonical_server
from hhs_backend.api.application_factory_routes import router as application_factory_router
from hhs_backend.api.graphics_constraint_routes import router as graphics_constraint_router
from hhs_backend.api.graphics_hydration_routes import router as graphics_hydration_router
from hhs_backend.api.installation_routes import router as installation_router
from hhs_backend.api.kimi_k3_content_routes import router as kimi_k3_content_router
from hhs_backend.api.litert_lm_assistant_routes import router as assistant_router
from hhs_backend.api.pass196_integration_routes import router as pass196_integration_router
from hhs_backend.api.pass197_calibration_routes import router as pass197_calibration_router
from hhs_backend.api.pass198_calibration_registry_routes import router as pass198_calibration_registry_router
from hhs_backend.api.probability_hydration_routes import router as probability_hydration_router
from hhs_backend.api.storybook_reel_routes import router as storybook_reel_router

app = canonical_server.app


def _route_exists(path: str, name: str | None = None) -> bool:
    for route in app.router.routes:
        if getattr(route, "path", None) != path:
            continue
        if name is None or getattr(route, "name", None) == name:
            return True
    return False


if not _route_exists("/api/assistant/status"):
    app.include_router(assistant_router)
if not _route_exists("/api/runtime/installation/status"):
    app.include_router(installation_router)
if not _route_exists("/api/runtime/application-factory/status"):
    app.include_router(application_factory_router)
if not _route_exists("/api/runtime/storybook-reel/status"):
    app.include_router(storybook_reel_router)
if not _route_exists("/api/runtime/content-engine/kimi-k3/status"):
    app.include_router(kimi_k3_content_router)
if not _route_exists("/api/runtime/integration/status"):
    app.include_router(pass196_integration_router)
if not _route_exists("/api/runtime/calibration/status"):
    app.include_router(pass197_calibration_router)
if not _route_exists("/api/runtime/calibration-registry/status"):
    app.include_router(pass198_calibration_registry_router)

# Register governed freeze authority before the broader hydration router so the
# legacy `/constraints/promote` projection is shadowed by a fail-closed route.
if not _route_exists("/api/runtime/graphics-hydration/constraints/registry/status"):
    app.include_router(graphics_constraint_router)
if not _route_exists("/api/runtime/graphics-hydration/status"):
    app.include_router(graphics_hydration_router)
if not _route_exists("/api/v1/probability/status"):
    app.include_router(probability_hydration_router)


@app.get("/api/system/status", tags=["system"])
async def visual_system_status() -> Dict[str, Any]:
    """Preserve the former JSON root response under an explicit API path."""
    return {
        "system": "HARMONICODE",
        "status": "online",
        "boot_id": canonical_server.SERVER_BOOT_ID,
        "default_interface": "HHS_LITERT_LM_VISUAL_DEVELOPMENT_ASSISTANT",
        "assistant_api": "/api/assistant",
        "installation_api": "/api/runtime/installation",
        "application_factory_api": "/api/runtime/application-factory",
        "storybook_reel_api": "/api/runtime/storybook-reel",
        "kimi_k3_content_engine_api": "/api/runtime/content-engine/kimi-k3",
        "pass196_integration_api": "/api/runtime/integration",
        "pass197_calibration_api": "/api/runtime/calibration",
        "pass198_calibration_registry_api": "/api/runtime/calibration-registry",
        "graphics_hydration_api": "/api/runtime/graphics-hydration",
        "graphics_constraint_registry_api": "/api/runtime/graphics-hydration/constraints/registry",
        "probability_hydration_api": "/api/v1/probability",
        "storybook_reel_studio": "/storybook-reel/",
        "probability_hydration_studio": "/probability-hydration/",
        "visual_environment": "HHS-P161-HHUMOCE",
        "application_factory": "HHS-P180-INTEGRATED-APPLICATION-FACTORY",
        "storybook_reel": "HHS-NATIVE-VM81-STORYBOOK-REEL-STUDIO-V1",
        "kimi_k3_content_engine": "HHS-P195-KIMI-K3-MULTIMODAL-CONTENT-ENGINE",
        "pass196_integrated_environment": "HHS-P196-SPIRAH-EVDB-LINUX-TOOLSERVER-VIDE-VM81-H72-H216",
        "pass197_ab_hydration_calibration": "HHS-P197-ABTREE-VM81X64-EXACT-LOSSLESS-HYDRATION",
        "pass198_operation_calibration_registry": "HHS-P198-OCR-PROOF-SIMPLIFICATION-VM81-H72",
        "graphics_hydration": "HHS-P181-NATIVE-CINEMATIC-GRAPHICS-HYDRATION-RUNTIME",
        "graphics_constraints": "HHS-P181-GRAPHICS-CONSTRAINT-FREEZE-REGISTRY-V1",
        "probability_hydration": "HHS-P183-PEHMR-M1259713-F72-VM81-H72-H216",
    }


app.router.routes[:] = [
    route
    for route in app.router.routes
    if not (
        getattr(route, "path", None) == "/"
        and "GET" in (getattr(route, "methods", None) or set())
        and getattr(route, "name", None) == "root"
    )
]

_applications_root = Path(__file__).resolve().parents[1] / "applications"
_storybook_root = _applications_root / "storybook_reel_studio"
_probability_root = _applications_root / "probability_hydration_studio"
_visual_root = _applications_root / "holofractal_harmonizer"

if not (_storybook_root / "index.html").is_file():
    raise RuntimeError(f"Storybook reel studio is missing: {_storybook_root}")
if not (_probability_root / "index.html").is_file():
    raise RuntimeError(f"Pass 183 probability hydration studio is missing: {_probability_root}")
if not (_visual_root / "index.html").is_file():
    raise RuntimeError(f"Pass 161 visual application is missing: {_visual_root}")

if not any(getattr(route, "name", None) == "hhs-storybook-reel-studio" for route in app.router.routes):
    app.mount("/storybook-reel", StaticFiles(directory=str(_storybook_root), html=True), name="hhs-storybook-reel-studio")
if not any(getattr(route, "name", None) == "hhs-probability-hydration-studio" for route in app.router.routes):
    app.mount("/probability-hydration", StaticFiles(directory=str(_probability_root), html=True), name="hhs-probability-hydration-studio")
if not any(getattr(route, "name", None) == "hhs-visual-home" for route in app.router.routes):
    app.mount("/", StaticFiles(directory=str(_visual_root), html=True), name="hhs-visual-home")

"""FastAPI composition entrypoint for Pass 163 VMRC."""
from hhs_backend.server import app
from hhs_backend.api.pass163_vmrc_routes import router as pass163_vmrc_router

if not any(
    getattr(route, "path", "").startswith("/api/runtime/vmrc")
    for route in app.routes
):
    app.include_router(pass163_vmrc_router)

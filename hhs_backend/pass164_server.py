from hhs_backend.pass163_server import app
from hhs_backend.api.pass164_gcmsl_routes import router as pass164_gcmsl_router

if not any(
    getattr(route, "path", "").startswith("/api/runtime/gcmsl")
    for route in app.routes
):
    app.include_router(pass164_gcmsl_router)

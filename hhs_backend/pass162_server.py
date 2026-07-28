from hhs_backend.server import app
from hhs_backend.api.vm81_creative_writing_routes import router as vm81_creative_router

if not any(
    getattr(route, "path", "").startswith("/api/runtime/creative")
    for route in app.routes
):
    app.include_router(vm81_creative_router)

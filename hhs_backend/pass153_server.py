from hhs_backend.server import app
from hhs_runtime.pass153.api import router as pass153_router

if not any(getattr(route, "path", "").startswith("/api/pass153") for route in app.routes):
    app.include_router(pass153_router)

from hhs_backend.pass164_server import app
from hhs_backend.api.pass165_multimodal_ingress_routes import router as pass165_router

if not any(
    getattr(route, "path", "").startswith("/api/runtime/multimodal-ingress")
    for route in app.routes
):
    app.include_router(pass165_router)

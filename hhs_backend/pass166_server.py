from hhs_backend.pass165_server import app
from hhs_backend.api.pass166_word2vec_routes import router as pass166_router

if not any(
    getattr(route, "path", "").startswith("/v1/modalities/language/models/word2vec")
    for route in app.routes
):
    app.include_router(pass166_router)

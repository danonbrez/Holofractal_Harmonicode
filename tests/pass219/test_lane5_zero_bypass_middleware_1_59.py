from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.lane5_zero_bypass_middleware_1_59 import (
    Lane5ZeroBypassRuntimeMiddleware,
)


def test_api_ingress_is_lane5_interposed() -> None:
    app = FastAPI()
    app.add_middleware(Lane5ZeroBypassRuntimeMiddleware)

    @app.get("/api/test")
    def api_test() -> dict[str, object]:
        return {"ok": True}

    @app.get("/static-test")
    def static_test() -> dict[str, object]:
        return {"ok": True}

    client = TestClient(app)
    response = client.get("/api/test")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    static_response = client.get("/static-test")
    assert static_response.status_code == 200

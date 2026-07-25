from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.api.runtime_routes import router as runtime_router
from hhs_backend.runtime.live_fastapi_workflow_v1 import register_cognition_routes


def test_cognition_routes_are_registered_on_canonical_runtime_router():
    register_cognition_routes()
    paths = {route.path for route in runtime_router.routes}
    required = {
        "/api/runtime/cognition/status",
        "/api/runtime/cognition/task",
        "/api/runtime/goals",
        "/api/runtime/semantic/search",
        "/api/runtime/prediction/generate",
        "/api/runtime/consensus/status",
        "/api/runtime/toolchain/execute",
        "/api/runtime/research/execute",
        "/api/runtime/multinode-goals/status",
    }
    assert required.issubset(paths)


def test_cognition_status_route_is_callable_and_contract_wrapped():
    register_cognition_routes()
    app = FastAPI()
    app.include_router(runtime_router)
    client = TestClient(app)

    response = client.get("/api/runtime/cognition/status")
    assert response.status_code == 200
    body = response.json()
    assert body["schema"] == "HHS_LIVE_COGNITION_STATUS_V1"
    assert body["runtime_contract"]["contract_type"] == "api_response"
    assert body["authority_boundary"]["vm81_mutation"] == "DENIED"

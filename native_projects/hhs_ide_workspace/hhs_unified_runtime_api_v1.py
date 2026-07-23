"""FastAPI projection over the single Pass 074 workspace dispatcher."""
from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from .hhs_native_workspace_project_v1 import HHSNativeWorkspaceRuntime
from .hhs_workspace_contracts_v1 import ContractError, canonical_request


def create_workspace_app(runtime: Optional[HHSNativeWorkspaceRuntime] = None) -> FastAPI:
    rt = runtime or HHSNativeWorkspaceRuntime()
    app = FastAPI(title="HHS Unified IDE Workspace API", version="1.0")
    app.state.hhs_workspace_runtime = rt

    def dispatch(body: Dict[str, Any], expected_class: str):
        try:
            request = canonical_request(body)
            if request["operation_class"] != expected_class:
                raise ContractError("REJECT_ROUTE_OPERATION_CLASS_MISMATCH")
            return rt.dispatch(request)
        except ContractError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/hhs/v1/ingress")
    def ingress(body: Dict[str, Any]): return dispatch(body, "INGRESS")

    @app.post("/api/hhs/v1/execute")
    def execute(body: Dict[str, Any]): return dispatch(body, "EXECUTE")

    @app.post("/api/hhs/v1/mutate")
    def mutate(body: Dict[str, Any]): return dispatch(body, "MUTATE")

    @app.post("/api/hhs/v1/query")
    def query(body: Dict[str, Any]): return dispatch(body, "QUERY")

    @app.post("/api/hhs/v1/compile")
    def compile_request(body: Dict[str, Any]): return dispatch(body, "COMPILE")

    @app.post("/api/hhs/v1/emulate")
    def emulate(body: Dict[str, Any]): return dispatch(body, "EMULATE")

    @app.get("/api/hhs/v1/artifacts/{artifact_id:path}")
    def artifact(artifact_id: str):
        value = rt.get_artifact(artifact_id)
        if value is None: raise HTTPException(status_code=404, detail="ARTIFACT_NOT_FOUND")
        return value

    @app.get("/api/hhs/v1/receipts/{receipt_id:path}")
    def receipt(receipt_id: str):
        value = rt.get_receipt(receipt_id)
        if value is None: raise HTTPException(status_code=404, detail="RECEIPT_NOT_FOUND")
        return value

    @app.get("/api/hhs/v1/state/{project_id:path}")
    def state(project_id: str):
        state = rt.snapshot()
        if project_id not in state["projects"]: raise HTTPException(status_code=404, detail="PROJECT_NOT_FOUND")
        return state

    @app.websocket("/api/hhs/v1/events")
    async def events(websocket: WebSocket):
        await websocket.accept()
        try:
            cursor = int(websocket.query_params.get("after", "0"))
            for event in rt.get_events_after(cursor):
                await websocket.send_json(event)
            await websocket.send_json({"schema": "HHS_RUNTIME_EVENT_STREAM_BOUNDARY_V1", "status": "CURRENT", "latest_sequence": rt.sequence})
        except WebSocketDisconnect:
            return

    @app.get("/", response_class=HTMLResponse)
    def workspace_shell():
        return """<!doctype html><html><body><main id='WorkspaceShell'><h1>HHS Native Workspace</h1><p>All surfaces project the unified Runtime API.</p></main></body></html>"""

    return app

app = create_workspace_app()

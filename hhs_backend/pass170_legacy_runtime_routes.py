"""Pass219 I180 governed migration adapters for legacy public runtime routes.

The legacy FastAPI applications remain intact in I180 so their callables can be
verified before constructor retirement.  This module composes their HTTP
behaviour into the canonical Pass170 gateway and adds explicit Pass170-owned
capability scopes for execution/mutation surfaces while reusing the inherited
Pass190 signed-token verifier.  The four legacy v1 websocket paths are not
re-registered here because the canonical production base already owns those
exact paths through hhs_backend.runtime.runtime_ws.
"""
from __future__ import annotations

import os
from typing import Any, Dict

from fastapi import APIRouter, Header, HTTPException

from hhs_backend.runtime import runtime_server as legacy_runtime
import hhs_runtime_api_server_v1 as legacy_v1
from hhs_runtime.pass190.completion import verify_capability_token

AUTHORIZATION_SCHEME = "HHS-Capability"
CAPABILITY_SECRET_ENV = "HHS_PASS190_CAPABILITY_SECRET"
RUNTIME_EXEC_SCOPE = "pass170.runtime.execute"
RUNTIME_EVENT_SCOPE = "pass170.runtime.event.inject"
RUNTIME_CERTIFICATION_SCOPE = "pass170.runtime.certification"

MIGRATED_HTTP_SIGNATURES = (
    ("GET", "/api/healthz"),
    ("GET", "/api/runtime/metrics"),
    ("POST", "/api/hhs/solve"),
    ("POST", "/api/runtime/event"),
    ("GET", "/api/runtime/replay"),
    ("GET", "/api/runtime/graph"),
    ("GET", "/api/runtime/transport"),
    ("GET", "/api/status"),
    ("POST", "/api/calculator/evaluate"),
    ("POST", "/api/agent/run-loop"),
    ("GET", "/api/certification"),
)

CANONICAL_WEBSOCKET_REPLACEMENTS = (
    "/ws/runtime",
    "/ws/replay",
    "/ws/graph",
    "/ws/transport",
)


def _token_from_header(value: str | None) -> str:
    if value is None:
        raise HTTPException(status_code=401, detail="HHS_PASS170_RUNTIME_CAPABILITY_REQUIRED")
    prefix = AUTHORIZATION_SCHEME + " "
    if not value.startswith(prefix):
        raise HTTPException(status_code=401, detail="HHS_PASS170_RUNTIME_AUTHORIZATION_SCHEME_INVALID")
    token = value[len(prefix):].strip()
    if not token:
        raise HTTPException(status_code=401, detail="HHS_PASS170_RUNTIME_CAPABILITY_REQUIRED")
    return token


def enforce_runtime_public_admission(
    authorization: str | None,
    *,
    required_scope: str,
    capability_secret: str | bytes | None = None,
) -> Dict[str, Any]:
    """Require a Pass170 scope using the inherited Pass190 token verifier."""
    secret = capability_secret or os.environ.get(CAPABILITY_SECRET_ENV)
    if not secret:
        raise HTTPException(status_code=503, detail="HHS_PASS170_RUNTIME_CAPABILITY_SECRET_REQUIRED")
    token = _token_from_header(authorization)
    try:
        principal = verify_capability_token(token, secret, required_scope=required_scope)
    except Exception as exc:
        message = str(exc)
        if "scope is not authorized" in message:
            raise HTTPException(status_code=403, detail="HHS_PASS170_RUNTIME_CAPABILITY_SCOPE_REQUIRED") from exc
        raise HTTPException(status_code=401, detail="HHS_PASS170_RUNTIME_CAPABILITY_INVALID") from exc
    return {
        "schema": "HHS_PASS170_RUNTIME_CAPABILITY_ADMISSION_I180_V1",
        "principal": principal.principal,
        "required_scope": required_scope,
        "authorized_scopes": sorted(principal.scopes),
        "token_hash72": principal.token_hash72,
        "new_token_authority": False,
        "pass190_verifier_reused": True,
    }


def build_pass170_legacy_runtime_router() -> APIRouter:
    router = APIRouter(tags=["pass170-legacy-runtime-migration"])

    @router.get("/api/healthz")
    async def healthz() -> Dict[str, Any]:
        return await legacy_runtime.healthz()

    @router.get("/api/runtime/metrics")
    async def runtime_metrics() -> Dict[str, Any]:
        return await legacy_runtime.runtime_metrics()

    @router.post("/api/hhs/solve")
    async def solve(
        request: legacy_runtime.SolveRequest,
        authorization: str | None = Header(default=None),
    ) -> Dict[str, Any]:
        enforce_runtime_public_admission(authorization, required_scope=RUNTIME_EXEC_SCOPE)
        return await legacy_runtime.solve(request)

    @router.post("/api/runtime/event")
    async def inject_runtime_event(
        payload: Dict[str, Any],
        authorization: str | None = Header(default=None),
    ) -> Dict[str, Any]:
        enforce_runtime_public_admission(authorization, required_scope=RUNTIME_EVENT_SCOPE)
        return await legacy_runtime.inject_runtime_event(payload)

    @router.get("/api/runtime/replay")
    async def runtime_replay() -> Dict[str, Any]:
        return await legacy_runtime.runtime_replay()

    @router.get("/api/runtime/graph")
    async def runtime_graph() -> Dict[str, Any]:
        return await legacy_runtime.runtime_graph()

    @router.get("/api/runtime/transport")
    async def runtime_transport() -> Dict[str, Any]:
        return await legacy_runtime.runtime_transport()

    @router.get("/api/status")
    async def api_status() -> Dict[str, Any]:
        return await legacy_v1.api_status()

    @router.post("/api/calculator/evaluate")
    async def api_calculator_evaluate(
        req: legacy_v1.CalculatorEvaluateRequest,
        authorization: str | None = Header(default=None),
    ) -> Dict[str, Any]:
        enforce_runtime_public_admission(authorization, required_scope=RUNTIME_EXEC_SCOPE)
        return await legacy_v1.api_calculator_evaluate(req)

    @router.post("/api/agent/run-loop")
    async def api_agent_run_loop(
        req: legacy_v1.AgentRunLoopRequest,
        authorization: str | None = Header(default=None),
    ) -> Dict[str, Any]:
        enforce_runtime_public_admission(authorization, required_scope=RUNTIME_EXEC_SCOPE)
        return await legacy_v1.api_agent_run_loop(req)

    @router.get("/api/certification")
    async def api_certification(
        authorization: str | None = Header(default=None),
    ) -> Dict[str, Any]:
        enforce_runtime_public_admission(authorization, required_scope=RUNTIME_CERTIFICATION_SCOPE)
        return await legacy_v1.api_certification()

    return router


__all__ = [
    "CANONICAL_WEBSOCKET_REPLACEMENTS",
    "MIGRATED_HTTP_SIGNATURES",
    "RUNTIME_CERTIFICATION_SCOPE",
    "RUNTIME_EVENT_SCOPE",
    "RUNTIME_EXEC_SCOPE",
    "build_pass170_legacy_runtime_router",
    "enforce_runtime_public_admission",
]

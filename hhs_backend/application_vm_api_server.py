"""Standalone secure OpenAPI control plane for the Ubuntu HHS application VM.

This ASGI application intentionally does not mount the Runtime OS/IDE frontend.
The frontend deployment may later consume this API as a client/adapter.
"""
from __future__ import annotations

import os
from typing import Any, Mapping

from fastapi import FastAPI, HTTPException, Query, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from hhs_runtime.pass220.application_vm_control_plane import (
    APPLICATION_VM_VERSION,
    ApplicationVMControlPlane,
    ApplicationVMError,
)

AUTHORIZATION = APIKeyHeader(
    name="Authorization",
    scheme_name="HhsCapabilityToken",
    description="Use: HHS-Capability <signed-token>",
    auto_error=False,
)


class ShellRequest(BaseModel):
    command: str = Field(min_length=1, max_length=131072)


class OperationRequest(BaseModel):
    arguments: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str | None = Field(default=None, max_length=512)
    expected_state: str | None = Field(default=None, max_length=1024)


class HarmonicodeRequest(BaseModel):
    expression: str = Field(min_length=1, max_length=131072)


def create_application_vm_api(
    control_plane: ApplicationVMControlPlane | None = None,
) -> FastAPI:
    control = control_plane or ApplicationVMControlPlane.from_environment()
    app = FastAPI(
        title="HHS Ubuntu Application VM API",
        version=APPLICATION_VM_VERSION,
        description=(
            "Backend-first HARMONICODE/HHS application-VM control plane. "
            "State-changing operations reuse inherited VM81/Pass190 authority "
            "and signed HHS capability tokens. No frontend is mounted here."
        ),
        root_path=os.environ.get("HHS_APPLICATION_VM_ROOT_PATH", ""),
        docs_url="/docs",
        redoc_url=None,
        openapi_url="/openapi.json",
    )
    app.state.hhs_application_vm_control_plane = control

    @app.middleware("http")
    async def security_headers(request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )
        return response

    def credential(value: str | None = Security(AUTHORIZATION)) -> dict[str, Any]:
        try:
            return control.authenticate_header(value)
        except ApplicationVMError as exc:
            message = str(exc)
            status = 503 if "SECURITY_NOT_CONFIGURED" in message else 401
            raise HTTPException(status_code=status, detail=message) from exc

    def token_from(value: str | None) -> str:
        try:
            return control.authenticate_header(value)["token"]
        except ApplicationVMError as exc:
            message = str(exc)
            status = 503 if "SECURITY_NOT_CONFIGURED" in message else 401
            raise HTTPException(status_code=status, detail=message) from exc

    def execution_error(exc: Exception) -> HTTPException:
        message = str(exc)
        if "CAPABILITY" in message:
            if "scope" in message.lower() or "authorized" in message.lower():
                return HTTPException(status_code=403, detail=message)
            return HTTPException(status_code=401, detail=message)
        return HTTPException(
            status_code=400,
            detail=f"{type(exc).__name__}:{message}",
        )

    @app.get("/health", include_in_schema=False)
    def health() -> dict[str, Any]:
        return control.health()

    @app.get("/v1/vm/status", tags=["vm"])
    def status(_: dict[str, Any] = Security(credential)) -> dict[str, Any]:
        return control.status()

    @app.get("/v1/vm/doctor", tags=["vm"])
    def doctor(_: dict[str, Any] = Security(credential)) -> dict[str, Any]:
        return control.doctor()

    @app.get("/v1/vm/capabilities", tags=["vm"])
    def capabilities(_: dict[str, Any] = Security(credential)) -> dict[str, Any]:
        return control.capabilities()

    @app.post("/v1/vm/shell", tags=["shell"])
    def shell(
        body: ShellRequest,
        authorization: str | None = Security(AUTHORIZATION),
    ) -> dict[str, Any]:
        token = token_from(authorization)
        try:
            return control.shell(body.command, authorization_token=token)
        except Exception as exc:
            raise execution_error(exc) from exc

    @app.post("/v1/vm/operations/{operation_id:path}", tags=["operations"])
    def invoke_operation(
        operation_id: str,
        body: OperationRequest,
        authorization: str | None = Security(AUTHORIZATION),
    ) -> dict[str, Any]:
        token = token_from(authorization)
        try:
            return control.invoke(
                operation_id,
                body.arguments,
                authorization_token=token,
                idempotency_key=body.idempotency_key,
                expected_state=body.expected_state,
            )
        except Exception as exc:
            raise execution_error(exc) from exc

    @app.post("/v1/vm/harmonicode/eval", tags=["harmonicode"])
    def harmonicode(
        body: HarmonicodeRequest,
        authorization: str | None = Security(AUTHORIZATION),
    ) -> dict[str, Any]:
        token = token_from(authorization)
        try:
            return control.harmonicode(
                body.expression,
                authorization_token=token,
            )
        except Exception as exc:
            raise execution_error(exc) from exc

    @app.get("/v1/vm/receipts", tags=["receipts"])
    def receipts(
        after: int = Query(default=0, ge=0),
        limit: int = Query(default=100, ge=1, le=1000),
        _: dict[str, Any] = Security(credential),
    ) -> dict[str, Any]:
        return control.receipts(after=after, limit=limit)

    @app.post("/v1/vm/replay/{receipt_hash72}", tags=["receipts"])
    def replay(
        receipt_hash72: str,
        _: dict[str, Any] = Security(credential),
    ) -> dict[str, Any]:
        try:
            return control.replay(receipt_hash72)
        except Exception as exc:
            raise execution_error(exc) from exc

    original_openapi = app.openapi

    def openapi() -> Mapping[str, Any]:
        schema = dict(original_openapi())
        schema["x-hhs-application-vm"] = {
            "schema": "HHS_PASS_220_UBUNTU_APPLICATION_VM_OPENAPI_V1",
            "backend_first": True,
            "frontend_attached": False,
            "public_transport": "TLS_REVERSE_PROXY_REQUIRED",
            "authorization_scheme": "HHS-Capability",
            "anonymous_paths": ["/health", "/openapi.json", "/docs"],
            "remote_token_issuance": False,
            "single_vm81_authority_preserved": True,
        }
        return schema

    app.openapi = openapi  # type: ignore[method-assign]
    return app


app = create_application_vm_api()

__all__ = ["app", "create_application_vm_api"]

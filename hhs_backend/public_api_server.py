"""Canonical Pass170 public API gateway over the inherited Pass190 authority.

The module exposes one FastAPI application identity backed by one lazily
constructed Pass190CompletionContext.  Pass170 adds fail-closed verification
of the public operation and network registries before the application is
constructed.  Routes never instantiate their own VM81 or operation engine.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import threading
from typing import Any, Callable, Mapping, Optional

from fastapi import FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from hhs_runtime.pass190.completion import (
    CONTRACT_ID as PASS190_CONTRACT_ID,
    Pass190CompletionContext,
    Pass190CompletionError,
)
from hhs_runtime.pass190.shell import lower_shell_command
from hhs_runtime.pass219.pass170_public_registry_i170 import (
    CONTRACT_ID as PASS170_CONTRACT_ID,
    verify_public_registries,
)
from hhs_backend.pass168_parameter_circuit_routes import build_pass168_parameter_circuit_router
from hhs_backend.pass169_algebra_routes import build_pass169_algebra_router

APP_ID = "HHS-P170-CANONICAL-PUBLIC-API-V1"
LEGACY_APP_ID = "HHS-P190-CANONICAL-PUBLIC-API-V1"
_DEFAULT_CONTEXT: Pass190CompletionContext | None = None
_DEFAULT_LOCK = threading.Lock()


class OperationBody(BaseModel):
    arguments: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str | None = None
    expected_state: str | None = None


class HarmonicodeBody(BaseModel):
    expression: str = Field(min_length=1, max_length=131072)


class PythonBody(BaseModel):
    identity: str = Field(min_length=1, max_length=512)
    args: list[Any] = Field(default_factory=list)
    kwargs: dict[str, Any] = Field(default_factory=dict)


class ShellBody(BaseModel):
    command: str = Field(min_length=1, max_length=131072)


class HydrationBody(BaseModel):
    commit: str = "HEAD"
    since_commit: str | None = None


def _default_context() -> Pass190CompletionContext:
    global _DEFAULT_CONTEXT
    if _DEFAULT_CONTEXT is None:
        with _DEFAULT_LOCK:
            if _DEFAULT_CONTEXT is None:
                database = Path(
                    os.environ.get(
                        "HHS_PASS190_DATABASE",
                        ".hhs_runtime_state/pass190/pass190-authority.sqlite3",
                    )
                )
                secret = os.environ.get("HHS_PASS190_CAPABILITY_SECRET")
                _DEFAULT_CONTEXT = Pass190CompletionContext(
                    database_path=database,
                    repository_root=Path.cwd(),
                    capability_secret=secret,
                )
    return _DEFAULT_CONTEXT


def _token_from_header(value: str | None) -> str | None:
    if value is None:
        return None
    prefix = "HHS-Capability "
    if not value.startswith(prefix):
        raise HTTPException(status_code=401, detail="HHS_P190_AUTHORIZATION_SCHEME_INVALID")
    token = value[len(prefix):].strip()
    if not token:
        raise HTTPException(status_code=401, detail="HHS_P190_CAPABILITY_REQUIRED")
    return token


def _reject_float(value: Any, path: str = "body") -> None:
    if isinstance(value, float):
        raise HTTPException(
            status_code=400,
            detail=f"HHS_P190_FLOAT_CANONICAL_TRANSPORT_REJECTED:{path}",
        )
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_float(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_float(item, f"{path}[{index}]")


def _payload_size(value: Any) -> int:
    return len(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    )


def _invoke_guarded(
    context: Pass190CompletionContext,
    operation_id: str,
    body: OperationBody,
    authorization: str | None,
) -> dict[str, Any]:
    _reject_float(body.arguments)
    record = context.resolve_operation(operation_id)
    limit = int(record.get("resource_bounds", {}).get("max_payload_bytes", 65536))
    if _payload_size(body.arguments) > limit:
        raise HTTPException(status_code=413, detail="HHS_P190_REQUEST_BODY_LIMIT")
    try:
        return context.invoke(
            operation_id,
            body.arguments,
            surface="openapi",
            authorization_token=_token_from_header(authorization),
            idempotency_key=body.idempotency_key,
            expected_state=body.expected_state,
        )
    except Pass190CompletionError as exc:
        code = 401 if "CAPABILITY" in str(exc) or "FULL_RUNTIME" in str(exc) else 400
        raise HTTPException(status_code=code, detail=str(exc)) from exc
    except Exception as exc:
        name = type(exc).__name__
        code = 409 if "Conflict" in name else 400
        raise HTTPException(status_code=code, detail=f"{name}:{exc}") from exc


def create_public_api_app(
    authority_context: Pass190CompletionContext | None = None,
    configuration: Mapping[str, Any] | None = None,
) -> FastAPI:
    config = dict(configuration or {})
    registry_root = Path(config.get("repository_root", Path(__file__).resolve().parents[1]))
    registry_report = verify_public_registries(registry_root)

    app = FastAPI(
        title="HHS Pass 170 Canonical Public Gateway",
        version="1.0.0",
        docs_url="/docs",
        redoc_url=None,
    )
    app.state.hhs_pass170_public_registry = registry_report
    provider: Callable[[], Pass190CompletionContext] = (
        (lambda: authority_context) if authority_context is not None else _default_context
    )

    @app.get("/v1/system/status")
    def system_status() -> dict[str, Any]:
        ctx = provider()
        return {
            "application": APP_ID,
            "legacy_application_identity": LEGACY_APP_ID,
            "pass170_contract": PASS170_CONTRACT_ID,
            **ctx.status(),
            "canonical_gateway": True,
            "public_registry_verified": registry_report["registry_evidence_verified"],
            "pass170_terminal_contract_verified": False,
            "next_boundary": registry_report["next_boundary"],
            "detached_projection": False,
        }

    @app.get("/v1/operations")
    def operations() -> dict[str, Any]:
        ctx = provider()
        return {
            "contract": PASS190_CONTRACT_ID,
            "public_contract": PASS170_CONTRACT_ID,
            "registry_hash216": ctx.registry.payload["registry_hash216"],
            "operations": ctx.operations(),
        }

    @app.get("/v1/operations/{operation_id:path}")
    def operation_record(operation_id: str) -> dict[str, Any]:
        try:
            return provider().resolve_operation(operation_id)
        except Exception as exc:
            raise HTTPException(status_code=404, detail=f"HHS_P190_OPERATION_NOT_FOUND:{operation_id}") from exc

    @app.post("/v1/operations/{operation_id:path}")
    def invoke_operation(
        operation_id: str,
        body: OperationBody,
        authorization: Optional[str] = Header(default=None),
    ) -> dict[str, Any]:
        return _invoke_guarded(provider(), operation_id, body, authorization)

    @app.post("/v1/harmonicode/eval")
    def harmonicode_eval(
        body: HarmonicodeBody,
        authorization: Optional[str] = Header(default=None),
    ) -> dict[str, Any]:
        try:
            return provider().invoke_constructor(
                body.expression,
                authorization_token=_token_from_header(authorization),
            )
        except Pass190CompletionError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"{type(exc).__name__}:{exc}") from exc

    @app.post("/v1/python/invoke")
    def python_invoke(
        body: PythonBody,
        authorization: Optional[str] = Header(default=None),
    ) -> dict[str, Any]:
        _reject_float(body.args, "args")
        _reject_float(body.kwargs, "kwargs")
        try:
            return provider().invoke_python(
                body.identity,
                body.args,
                body.kwargs,
                authorization_token=_token_from_header(authorization),
            )
        except Pass190CompletionError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/v1/python/compatibility")
    def python_compatibility() -> dict[str, Any]:
        return provider().compatibility_registry()

    @app.post("/v1/shell/execute")
    def shell_execute(
        body: ShellBody,
        authorization: Optional[str] = Header(default=None),
    ) -> dict[str, Any]:
        try:
            return lower_shell_command(
                provider(),
                body.command,
                authorization_token=_token_from_header(authorization),
            )
        except Pass190CompletionError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/v1/hydration/preview")
    def hydration_preview(body: HydrationBody) -> dict[str, Any]:
        try:
            return provider().hydration_preview(
                commit=body.commit,
                since_commit=body.since_commit,
            )
        except Exception as exc:
            raise HTTPException(status_code=409, detail=f"{type(exc).__name__}:{exc}") from exc

    @app.post("/v1/replay/{receipt_hash72}")
    def replay(receipt_hash72: str) -> dict[str, Any]:
        try:
            return provider().replay(receipt_hash72)
        except Exception as exc:
            raise HTTPException(status_code=409, detail=f"{type(exc).__name__}:{exc}") from exc

    @app.get("/v1/registry/openapi")
    def registry_openapi() -> dict[str, Any]:
        return provider().openapi_registry_document()

    @app.websocket("/v1/receipts/ws")
    async def receipt_stream(websocket: WebSocket) -> None:
        await websocket.accept()
        try:
            ctx = provider()
            rows = ctx.authority.receipts_after(0, 100)
            await websocket.send_json(
                {
                    "schema": "HHS_PASS_190_RECEIPT_STREAM_SNAPSHOT_V1",
                    "contract": PASS190_CONTRACT_ID,
                    "public_contract": PASS170_CONTRACT_ID,
                    "runtime_mode": ctx.runtime_mode,
                    "receipts": rows,
                    "canonical_state_fabricated": False,
                }
            )
        except WebSocketDisconnect:
            return
        finally:
            try:
                await websocket.close()
            except RuntimeError:
                pass

    app.include_router(build_pass168_parameter_circuit_router())
    app.include_router(build_pass169_algebra_router(provider))

    return app


def create_app(context: Pass190CompletionContext | None = None) -> FastAPI:
    """Compatibility alias for inherited Pass190 callers."""
    return create_public_api_app(authority_context=context)


app = create_public_api_app()

__all__ = [
    "APP_ID",
    "LEGACY_APP_ID",
    "app",
    "create_app",
    "create_public_api_app",
]

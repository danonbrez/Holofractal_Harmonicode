"""Pass 213 Iteration 10 governed native dispatch HTTP routes."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field, StrictInt, field_validator

from hhs_backend.api.runtime_routes import _contract_response
from hhs_backend.runtime.hhs_pass213_governed_native_dispatch_v1 import (
    GovernedNativeDispatchService,
    Pass213NativeDispatchAuthorizationError,
    Pass213NativeDispatchError,
    Pass213NativeDispatchIntegrityError,
    Pass213NativeDispatchUnavailableError,
    Pass213NativeDispatchValidationError,
    get_default_native_dispatch_service,
)

router = APIRouter(
    tags=[
        "runtime",
        "pass213",
        "native-dispatch",
        "vm81",
        "compiled-rom",
        "governed-execution",
    ]
)


class NativeDispatchExecuteRequest(BaseModel):
    entry_hash216: str = Field(min_length=64, max_length=64)
    operation_id: str = Field(min_length=1, max_length=128)
    expected_parent_hash216: str = Field(min_length=64, max_length=64)
    expected_tensor_root_hash216: str = Field(min_length=64, max_length=64)
    timestamp_ns: StrictInt = Field(ge=0)
    hydration_lane: StrictInt = Field(default=0, ge=0, lt=40)
    operands: list[StrictInt] = Field(min_length=1, max_length=8)
    read_set: list[str] = Field(default_factory=list, max_length=64)
    write_set: list[str] = Field(default_factory=list, max_length=64)

    @field_validator("operands")
    @classmethod
    def validate_operands(cls, values: list[int]) -> list[int]:
        if any(value < 0 or value >= 1 << 64 for value in values):
            raise ValueError("PASS213_NATIVE_DISPATCH_OPERAND_OUT_OF_RANGE")
        return values


_SERVICE_OVERRIDE: GovernedNativeDispatchService | None = None


def configure_pass213_native_dispatch_service(
    service: GovernedNativeDispatchService | None,
) -> GovernedNativeDispatchService | None:
    """Install an explicit process-local Iteration 10 service."""
    global _SERVICE_OVERRIDE
    previous = _SERVICE_OVERRIDE
    _SERVICE_OVERRIDE = service
    return previous


def _service() -> GovernedNativeDispatchService:
    return _SERVICE_OVERRIDE or get_default_native_dispatch_service()


def _capability(
    authorization: str | None,
    x_hhs_dispatch_capability: str | None,
) -> str | None:
    bearer: str | None = None
    if authorization:
        scheme, separator, value = authorization.partition(" ")
        if separator != " " or scheme.lower() != "bearer" or not value.strip():
            raise HTTPException(
                status_code=401,
                detail={
                    "schema": "HHS_PASS_213_NATIVE_DISPATCH_REJECTION_V1",
                    "ok": False,
                    "reason": "PASS213_NATIVE_DISPATCH_AUTHORIZATION_HEADER_INVALID",
                },
            )
        bearer = value.strip()
    if (
        bearer
        and x_hhs_dispatch_capability
        and bearer != x_hhs_dispatch_capability
    ):
        raise HTTPException(
            status_code=401,
            detail={
                "schema": "HHS_PASS_213_NATIVE_DISPATCH_REJECTION_V1",
                "ok": False,
                "reason": "PASS213_NATIVE_DISPATCH_CAPABILITY_HEADERS_CONFLICT",
            },
        )
    return bearer or x_hhs_dispatch_capability


def _invoke(
    *,
    route: str,
    method: str,
    operation: str,
    arguments: Dict[str, Any] | None = None,
    authorization: str | None = None,
    x_hhs_dispatch_capability: str | None = None,
) -> Dict[str, Any]:
    try:
        payload = _service().invoke(
            operation,
            arguments or {},
            capability=_capability(
                authorization, x_hhs_dispatch_capability
            ),
        )
    except Pass213NativeDispatchAuthorizationError as exc:
        raise HTTPException(
            status_code=403,
            detail={
                "schema": "HHS_PASS_213_NATIVE_DISPATCH_REJECTION_V1",
                "ok": False,
                "classification": type(exc).__name__,
                "reason": str(exc),
            },
        ) from exc
    except Pass213NativeDispatchIntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "schema": "HHS_PASS_213_NATIVE_DISPATCH_REJECTION_V1",
                "ok": False,
                "classification": type(exc).__name__,
                "reason": str(exc),
            },
        ) from exc
    except Pass213NativeDispatchValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "schema": "HHS_PASS_213_NATIVE_DISPATCH_REJECTION_V1",
                "ok": False,
                "classification": type(exc).__name__,
                "reason": str(exc),
            },
        ) from exc
    except Pass213NativeDispatchUnavailableError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "schema": "HHS_PASS_213_NATIVE_DISPATCH_REJECTION_V1",
                "ok": False,
                "classification": type(exc).__name__,
                "reason": str(exc),
            },
        ) from exc
    except (OSError, Pass213NativeDispatchError) as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "schema": "HHS_PASS_213_NATIVE_DISPATCH_REJECTION_V1",
                "ok": False,
                "classification": type(exc).__name__,
                "reason": str(exc),
            },
        ) from exc
    return _contract_response(route, method, dict(payload))


@router.get("/api/runtime/native-dispatch/status")
def native_dispatch_status() -> Dict[str, Any]:
    return _invoke(
        route="/api/runtime/native-dispatch/status",
        method="GET",
        operation="native-dispatch.status",
    )


@router.post("/api/runtime/native-dispatch/execute")
def native_dispatch_execute(
    request: NativeDispatchExecuteRequest,
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_hhs_dispatch_capability: str | None = Header(
        default=None, alias="X-HHS-Dispatch-Capability"
    ),
) -> Dict[str, Any]:
    return _invoke(
        route="/api/runtime/native-dispatch/execute",
        method="POST",
        operation="native-dispatch.execute",
        arguments=request.model_dump(),
        authorization=authorization,
        x_hhs_dispatch_capability=x_hhs_dispatch_capability,
    )


@router.get("/api/runtime/native-dispatch/receipts/{sequence}")
def native_dispatch_receipt(
    sequence: int,
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_hhs_dispatch_capability: str | None = Header(
        default=None, alias="X-HHS-Dispatch-Capability"
    ),
) -> Dict[str, Any]:
    return _invoke(
        route="/api/runtime/native-dispatch/receipts/{sequence}",
        method="GET",
        operation="native-dispatch.receipt",
        arguments={"sequence": sequence},
        authorization=authorization,
        x_hhs_dispatch_capability=x_hhs_dispatch_capability,
    )

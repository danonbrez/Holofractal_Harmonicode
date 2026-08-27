"""Pass 192 cellular Fibonacci tensor API."""
from __future__ import annotations

from base64 import urlsafe_b64decode, urlsafe_b64encode
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_runtime.pass192.runtime import Pass192Error, Pass192Runtime

router = APIRouter(prefix="/v1/tensors/fibonacci", tags=["pass192-fibonacci"])

_RUNTIME: Optional[Pass192Runtime] = None


def _runtime() -> Pass192Runtime:
    global _RUNTIME
    if _RUNTIME is None:
        _RUNTIME = Pass192Runtime()
    return _RUNTIME


def _set_runtime_for_tests(runtime: Optional[Pass192Runtime]) -> None:
    global _RUNTIME
    _RUNTIME = runtime


def _call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Pass192Error as exc:
        if exc.classification.endswith("_NOT_FOUND"):
            raise HTTPException(status_code=404, detail=exc.classification) from exc
        raise HTTPException(status_code=409, detail=exc.classification) from exc
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _encode_ref(identity: str) -> str:
    if not isinstance(identity, str) or not identity:
        raise ValueError("HHS_P192_IDENTITY_REQUIRED")
    return urlsafe_b64encode(identity.encode("utf-8")).decode("ascii").rstrip("=")


def _decode_ref(reference: str) -> str:
    if not isinstance(reference, str) or not reference:
        raise HTTPException(status_code=400, detail="HHS_P192_IDENTITY_REFERENCE_REQUIRED")
    padding = "=" * ((4 - len(reference) % 4) % 4)
    try:
        identity = urlsafe_b64decode((reference + padding).encode("ascii")).decode("utf-8")
    except Exception as exc:
        raise HTTPException(status_code=400, detail="HHS_P192_IDENTITY_REFERENCE_INVALID") from exc
    if not identity:
        raise HTTPException(status_code=400, detail="HHS_P192_IDENTITY_REFERENCE_INVALID")
    return identity


def _decorate(payload: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(payload)
    for key in ("tensor_id", "materialization_id", "hash216_identity"):
        value = result.get(key)
        if isinstance(value, str) and value:
            result[f"{key}_ref"] = _encode_ref(value)
    return result


class BoundsBody(BaseModel):
    max_depth: int = Field(default=64, ge=1, le=4096)
    max_nodes: int = Field(default=4096, ge=1)
    max_serialized_bytes: int = Field(default=8 * 1024 * 1024, ge=1)
    max_memory_bytes: int = Field(default=16 * 1024 * 1024, ge=1)
    max_steps: int = Field(default=16384, ge=1)
    timeout_policy: str = Field(default="CALLER_ENFORCED_DETERMINISTIC_STEP_BOUND", min_length=1)
    cancellation_policy: str = Field(default="EXPLICIT_CANCEL_FLAG", min_length=1)
    workspace_quota: int = Field(default=64 * 1024 * 1024, ge=1)
    capability_scope: List[str] = Field(
        default_factory=lambda: ["P192.CREATE", "P192.MATERIALIZE", "P192.VALIDATE", "P192.REPLAY"]
    )


class AuthorityBody(BaseModel):
    authority_execution: Dict[str, Any]


class CreateBody(AuthorityBody):
    row: int = Field(ge=0, le=2)
    column: int = Field(ge=0, le=2)
    materialization_bounds: Optional[BoundsBody] = None


class MaterializeBody(AuthorityBody):
    depth: int = Field(ge=0, le=4096)
    materialization_bounds: Optional[BoundsBody] = None
    cancelled: bool = False


@router.get("/status")
def status() -> Dict[str, Any]:
    return _runtime().status()


@router.get("/operation-registry")
def operation_registry() -> Dict[str, Any]:
    return _runtime().operation_registry()


@router.post("")
def create(body: CreateBody) -> Dict[str, Any]:
    bounds = body.materialization_bounds.model_dump() if body.materialization_bounds else None
    return _decorate(
        _call(
            _runtime().create_tensor,
            body.row,
            body.column,
            materialization_bounds=bounds,
            authority_execution=body.authority_execution,
        )
    )


@router.get("/materializations/{materialization_ref}")
def get_materialization(materialization_ref: str) -> Dict[str, Any]:
    return _decorate(_call(_runtime().get_materialization, _decode_ref(materialization_ref)))


@router.post("/materializations/{materialization_ref}/validate")
def validate_materialization(materialization_ref: str) -> Dict[str, Any]:
    return _call(_runtime().validate_materialization, _decode_ref(materialization_ref))


@router.get("/{tensor_ref}")
def inspect_tensor(tensor_ref: str) -> Dict[str, Any]:
    return _decorate(_call(_runtime().get_tensor, _decode_ref(tensor_ref)))


@router.post("/{tensor_ref}/materialize")
def materialize(tensor_ref: str, body: MaterializeBody) -> Dict[str, Any]:
    bounds = body.materialization_bounds.model_dump() if body.materialization_bounds else None
    return _decorate(
        _call(
            _runtime().materialize_prefix,
            _decode_ref(tensor_ref),
            body.depth,
            materialization_bounds=bounds,
            cancelled=body.cancelled,
            authority_execution=body.authority_execution,
        )
    )


@router.post("/{tensor_ref}/validate")
def validate_tensor(tensor_ref: str) -> Dict[str, Any]:
    return _call(_runtime().validate_tensor, _decode_ref(tensor_ref))


@router.get("/{tensor_ref}/receipts")
def receipts(tensor_ref: str) -> List[Dict[str, Any]]:
    return _runtime().receipts_for(_decode_ref(tensor_ref))


@router.post("/{tensor_ref}/replay")
def replay(tensor_ref: str) -> Dict[str, Any]:
    return _call(_runtime().replay, _decode_ref(tensor_ref))


__all__ = ["router", "_encode_ref", "_decode_ref", "_set_runtime_for_tests"]

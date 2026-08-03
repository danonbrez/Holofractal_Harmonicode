"""Lossless HTTP transport and deterministic retrieval bootstrap for Pass 205."""
from __future__ import annotations

from typing import Any, Mapping

from fastapi import APIRouter

from hhs_backend.api.runtime_routes import _contract_response
from hhs_backend.api import pass205_continuation_routes as _routes
from hhs_backend.runtime.hhs_pass205_governed_continuation_v2 import (
    GOVERNED_PASS205_CONTINUATION_RUNTIME,
    GovernedPass205ContinuationRuntime,
)
from hhs_backend.runtime.hhs_pass205_retrieval_order_v1 import deterministic_retrieve

# Install deterministic retrieval on the governed class and active singleton.
GovernedPass205ContinuationRuntime.retrieve = deterministic_retrieve
GOVERNED_PASS205_CONTINUATION_RUNTIME.retrieve = deterministic_retrieve.__get__(
    GOVERNED_PASS205_CONTINUATION_RUNTIME,
    GovernedPass205ContinuationRuntime,
)

_UINT64_COLLECTION_KEYS = {
    "state_words",
    "learning_features",
    "reconstructed_target_state_words",
    "reconstructed_target_learning_features",
}


def encode_lossless_uint64(value: Any, *, key: str | None = None) -> Any:
    """Encode canonical uint64 API fields without IEEE-754 loss."""
    if isinstance(value, Mapping):
        return {
            str(child_key): encode_lossless_uint64(child, key=str(child_key))
            for child_key, child in value.items()
        }
    if isinstance(value, list):
        if key in _UINT64_COLLECTION_KEYS:
            return [str(int(item)) for item in value]
        return [encode_lossless_uint64(item, key=key) for item in value]
    if isinstance(value, tuple):
        if key in _UINT64_COLLECTION_KEYS:
            return [str(int(item)) for item in value]
        return [encode_lossless_uint64(item, key=key) for item in value]
    if key == "xor_mask" and isinstance(value, (int, str)):
        return str(int(value))
    return value


def _lossless_response(path: str, method: str, payload: Mapping[str, Any]):
    return _contract_response(path, method, encode_lossless_uint64(dict(payload)))


_routes._response = _lossless_response
_routes.STUDIO_HTML = _routes.STUDIO_HTML.replace(
    '"xor_mask":1',
    '"xor_mask":"1"',
)

router = APIRouter(
    prefix=_routes.API_PREFIX,
    tags=["runtime", "continuation", "transport", "pass205"],
)


@router.get("/transport")
def continuation_transport_status():
    return _contract_response(
        f"{_routes.API_PREFIX}/transport",
        "GET",
        {
            "schema": "HHS_PASS_205_LOSSLESS_UINT64_TRANSPORT_V1",
            "ok": True,
            "canonical_internal_state": "uint64",
            "http_state_words": "decimal-string",
            "http_learning_features": "decimal-string",
            "http_xor_mask": "decimal-string",
            "integer_request_compatibility": True,
            "decimal_string_request_compatibility": True,
            "javascript_number_rounding_permitted": False,
            "retrieval_candidate_ordering": "CANONICAL_ROOT_REASON_ORDER",
        },
    )


PASS205_TRANSPORT_BOOTSTRAP = {
    "schema": "HHS_PASS_205_TRANSPORT_BOOTSTRAP_V1",
    "ok": True,
    "lossless_uint64": True,
    "deterministic_retrieval": True,
}


__all__ = [
    "PASS205_TRANSPORT_BOOTSTRAP",
    "encode_lossless_uint64",
    "router",
]

"""Native-first FastAPI provider selection for HHS runtime compatibility.

The default auto mode preserves existing explicitly installed FastAPI
environments while making the repository-native compatibility surface the
automatic fallback when the external dependency is absent.

Explicit modes:
- HHS_FASTAPI_PROVIDER=native   -> repository-native compatibility only
- HHS_FASTAPI_PROVIDER=external -> external FastAPI required; fail closed
- HHS_FASTAPI_PROVIDER=auto     -> external when importable, native otherwise
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any

_PROVIDER_ENV = "HHS_FASTAPI_PROVIDER"
_VALID = {"auto", "native", "external"}


@dataclass(frozen=True)
class FastAPIProviderSelection:
    requested: str
    selected: str
    external_available: bool
    native_fallback: bool
    explicit_override: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "HHS_FASTAPI_PROVIDER_SELECTION_V1",
            "requested": self.requested,
            "selected": self.selected,
            "external_available": self.external_available,
            "native_fallback": self.native_fallback,
            "explicit_override": self.explicit_override,
            "canonical_state_mutation_authority": False,
            "vm81_admission_authority": False,
            "hash72_commit_authority": False,
            "hash216_persistence_authority": False,
        }


def _requested_provider() -> str:
    value = os.environ.get(_PROVIDER_ENV, "auto").strip().lower()
    if value not in _VALID:
        raise RuntimeError(
            f"HHS_FASTAPI_PROVIDER_INVALID:{value}:expected auto|native|external"
        )
    return value


def _load_external() -> tuple[Any, Any, Any]:
    from fastapi import APIRouter, WebSocket, WebSocketDisconnect
    return APIRouter, WebSocket, WebSocketDisconnect


def _load_native() -> tuple[Any, Any, Any]:
    from hhs_backend.runtime.hhs_native_fastapi_compat_v1 import (
        NativeAPIRouter,
        NativeWebSocket,
        NativeWebSocketDisconnect,
    )
    return NativeAPIRouter, NativeWebSocket, NativeWebSocketDisconnect


_REQUESTED = _requested_provider()
_EXTERNAL_AVAILABLE = False

if _REQUESTED == "native":
    APIRouter, WebSocket, WebSocketDisconnect = _load_native()
    _SELECTED = "native"
elif _REQUESTED == "external":
    try:
        APIRouter, WebSocket, WebSocketDisconnect = _load_external()
    except ModuleNotFoundError as exc:
        if exc.name == "fastapi" or str(exc.name or "").startswith("fastapi."):
            raise RuntimeError(
                "HHS_FASTAPI_EXTERNAL_EXPLICIT_BUT_UNAVAILABLE"
            ) from exc
        raise
    _EXTERNAL_AVAILABLE = True
    _SELECTED = "external"
else:
    try:
        APIRouter, WebSocket, WebSocketDisconnect = _load_external()
    except ModuleNotFoundError as exc:
        if not (exc.name == "fastapi" or str(exc.name or "").startswith("fastapi.")):
            raise
        APIRouter, WebSocket, WebSocketDisconnect = _load_native()
        _SELECTED = "native"
    else:
        _EXTERNAL_AVAILABLE = True
        _SELECTED = "external"

_SELECTION = FastAPIProviderSelection(
    requested=_REQUESTED,
    selected=_SELECTED,
    external_available=_EXTERNAL_AVAILABLE,
    native_fallback=(_REQUESTED == "auto" and _SELECTED == "native"),
    explicit_override=(_REQUESTED != "auto"),
)


def fastapi_provider_status() -> dict[str, Any]:
    return _SELECTION.to_dict()


__all__ = [
    "APIRouter",
    "WebSocket",
    "WebSocketDisconnect",
    "FastAPIProviderSelection",
    "fastapi_provider_status",
]

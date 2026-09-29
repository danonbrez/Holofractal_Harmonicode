"""Native-first FastAPI provider selection for HHS runtime compatibility.

The repository-native compatibility surface is the default. External FastAPI
is used only when HHS_FASTAPI_PROVIDER=external is explicitly selected by an
external FastAPI application/composition boundary.

Modes:
- HHS_FASTAPI_PROVIDER=native   -> repository-native compatibility (default)
- HHS_FASTAPI_PROVIDER=external -> external FastAPI required; fail closed
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any

_PROVIDER_ENV = "HHS_FASTAPI_PROVIDER"
_VALID = {"native", "external"}


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
    value = os.environ.get(_PROVIDER_ENV, "native").strip().lower()
    if value not in _VALID:
        raise RuntimeError(
            f"HHS_FASTAPI_PROVIDER_INVALID:{value}:expected native|external"
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


_PROVIDER_EXPLICIT = _PROVIDER_ENV in os.environ
_REQUESTED = _requested_provider()
_EXTERNAL_AVAILABLE = False

if _REQUESTED == "external":
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
    APIRouter, WebSocket, WebSocketDisconnect = _load_native()
    _SELECTED = "native"


_SELECTION = FastAPIProviderSelection(
    requested=_REQUESTED,
    selected=_SELECTED,
    external_available=_EXTERNAL_AVAILABLE,
    native_fallback=(_SELECTED == "native" and not _PROVIDER_EXPLICIT),
    explicit_override=_PROVIDER_EXPLICIT,
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

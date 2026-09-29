"""FastAPI binding through the shared Lane 5 native capability policy."""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any

from hhs_runtime.hhs_lane5_native_capability_provider_v1 import (
    Lane5CapabilityProviderError,
    capability_spec,
    resolve_lane5_capability,
)

_LEGACY_PROVIDER_ENV = "HHS_FASTAPI_PROVIDER"
_SPEC = capability_spec("fastapi")


@dataclass(frozen=True)
class FastAPIProviderSelection:
    requested: str
    selected: str
    external_available: bool
    native_fallback: bool
    explicit_override: bool
    lane5_provider_env: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "HHS_FASTAPI_PROVIDER_SELECTION_V1",
            "requested": self.requested,
            "selected": self.selected,
            "external_available": self.external_available,
            "native_fallback": self.native_fallback,
            "explicit_override": self.explicit_override,
            "lane5_provider_env": self.lane5_provider_env,
            "lane5_native_default": True,
            "implicit_external_fallback_allowed": False,
            "canonical_state_mutation_authority": False,
            "vm81_admission_authority": False,
            "hash72_commit_authority": False,
            "hash216_persistence_authority": False,
        }


def _provider_environment() -> dict[str, str]:
    env = dict(os.environ)
    # Preserve the earlier FastAPI-specific control as a compatibility alias,
    # but normalize it into the shared Lane 5 provider contract.
    if _LEGACY_PROVIDER_ENV in env and _SPEC.env_name not in env:
        env[_SPEC.env_name] = env[_LEGACY_PROVIDER_ENV]
    return env


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


_ENV = _provider_environment()
try:
    _RESOLUTION = resolve_lane5_capability("fastapi", environ=_ENV)
except Lane5CapabilityProviderError as exc:
    raise RuntimeError(str(exc)) from exc

_EXTERNAL_AVAILABLE = False
if _RESOLUTION.provider == "external":
    try:
        APIRouter, WebSocket, WebSocketDisconnect = _load_external()
    except ModuleNotFoundError as exc:
        if exc.name == "fastapi" or str(exc.name or "").startswith("fastapi."):
            raise RuntimeError(
                "HHS_FASTAPI_EXTERNAL_EXPLICIT_BUT_UNAVAILABLE"
            ) from exc
        raise
    _EXTERNAL_AVAILABLE = True
else:
    APIRouter, WebSocket, WebSocketDisconnect = _load_native()

_SELECTION = FastAPIProviderSelection(
    requested=_RESOLUTION.provider,
    selected=_RESOLUTION.provider,
    external_available=_EXTERNAL_AVAILABLE,
    native_fallback=(
        _RESOLUTION.provider == "native" and not _RESOLUTION.explicit
    ),
    explicit_override=_RESOLUTION.explicit,
    lane5_provider_env=_SPEC.env_name,
)


def fastapi_provider_status() -> dict[str, Any]:
    result = _SELECTION.to_dict()
    result["lane5_resolution"] = _RESOLUTION.to_dict()
    return result


__all__ = [
    "APIRouter",
    "WebSocket",
    "WebSocketDisconnect",
    "FastAPIProviderSelection",
    "fastapi_provider_status",
]

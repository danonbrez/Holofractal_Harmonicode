"""Production HHS visual server with authoritative status caching.

The deployment-facing application preserves the complete HHS backend/runtime
surface and serves the TypeScript/React/Vite Runtime OS as its public root via
:mod:`hhs_backend.runtime_os_visual_server`.

The ASGI gateway:

* prewarms the real Pass 196-201 status routes sequentially;
* serves direct status reads from the persistent cache;
* returns an explicit warming projection instead of executing an expensive
  status handler on the serving event loop; and
* delays the isolated probe briefly after the main cold import.

The inherited bootstrap gateway's legacy Harmonizer HTML/JavaScript rewriting
is deliberately disabled here. The Runtime OS owns its own frontend transport
and telemetry. Frontend selection changes HTTP projection only; backend/pass
authority remains owned by the inherited HHS runtime.
"""
from __future__ import annotations

import os
import time
from collections.abc import Awaitable, Callable
from typing import Any

from hhs_backend.cached_visual_server import RuntimeBootstrapGateway
from hhs_backend.runtime_os_visual_server import app as authoritative_app

PRODUCTION_STATUS_PATHS = (
    "/api/runtime/authority/status",
    "/api/runtime/integration/status",
    "/api/runtime/calibration/status",
    "/api/runtime/calibration-registry/status",
    "/api/runtime/distributed-calibration/status",
    "/api/runtime/optimization-authority/status",
    "/api/runtime/optimization-canary/status",
    "/api/runtime/optimization-active/status",
    "/api/public/status",
)


class ProductionRuntimeBootstrapGateway(RuntimeBootstrapGateway):
    """Serve expensive status reads from cache without rewriting Runtime OS HTML."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        delay = float(os.getenv("HHS_RUNTIME_STATUS_PROBE_START_DELAY_SECONDS", "30"))
        self.probe_start_delay = max(0.0, delay)
        self._probe_allowed_at = time.monotonic() + self.probe_start_delay

    def _ensure_probe(self) -> None:
        if time.monotonic() < self._probe_allowed_at:
            return
        super()._ensure_probe()

    async def _transform_response(
        self,
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]],
    ) -> None:
        """Pass Runtime OS HTML/assets through unchanged.

        ``RuntimeBootstrapGateway`` historically injected a Pass 161 browser
        coordinator and rewrote the old Harmonizer production-integration
        module. Neither transformation belongs in the TypeScript Runtime OS.
        Status caching remains implemented by ``__call__`` below.
        """
        await self.downstream(scope, receive, send)

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]],
    ) -> None:
        if scope.get("type") == "http":
            path = str(scope.get("path") or "")
            if path in self.status_paths:
                self._ensure_probe()
                lookup = self.cache.lookup(path)
                if lookup.payload is None:
                    payload = {
                        "schema": "HHS_RUNTIME_STATUS_WARMING_V1",
                        "ok": False,
                        "phase": "WARMING",
                        "status": "RUNTIME_STATUS_PENDING",
                        "runtime_bootstrap_pending": True,
                        "requested_path": path,
                    }
                else:
                    payload = lookup.payload
                headers = [
                    (b"x-hhs-runtime-cache", lookup.state.encode("ascii")),
                    (b"cache-control", b"no-store"),
                ]
                if lookup.age_ms is not None:
                    headers.append(
                        (b"x-hhs-runtime-cache-age-ms", str(lookup.age_ms).encode("ascii"))
                    )
                await self._send_json(send, 200, payload, extra_headers=headers)
                return
        await super().__call__(scope, receive, send)


app = ProductionRuntimeBootstrapGateway(
    authoritative_app,
    status_paths=PRODUCTION_STATUS_PATHS,
)

__all__ = [
    "PRODUCTION_STATUS_PATHS",
    "ProductionRuntimeBootstrapGateway",
    "app",
]

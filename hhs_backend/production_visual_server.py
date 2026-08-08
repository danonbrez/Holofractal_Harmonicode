"""Production HHS visual server with authoritative status caching.

The canonical application remains ``hhs_backend.visual_server:app``. This
module supplies the deployment-facing ASGI gateway that:

* prewarms the real Pass 196-201 status routes sequentially;
* serves direct status reads from the persistent cache;
* returns an explicit warming projection instead of executing an expensive
  status handler on the serving event loop;
* starts isolated status probes only from explicit bootstrap/status demand;
* enforces a completion-based cooldown between heavyweight probe processes;
* delays the isolated probe briefly after the main cold import; and
* retains the browser bootstrap injection and event-driven readiness behavior
  implemented by :mod:`hhs_backend.cached_visual_server`.
"""
from __future__ import annotations

import os
import time
from collections.abc import Awaitable, Callable
from typing import Any

from hhs_backend.cached_visual_server import (
    BOOTSTRAP_COORDINATOR_PATH,
    BOOTSTRAP_SOURCE,
    PRODUCTION_INTEGRATION_PATH,
    RuntimeBootstrapGateway,
)
from hhs_backend.visual_server import app as authoritative_app

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
    """Serve expensive status routes without coupling probes to user traffic."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        delay = float(os.getenv("HHS_RUNTIME_STATUS_PROBE_START_DELAY_SECONDS", "30"))
        self.probe_start_delay = max(0.0, delay)
        self._probe_allowed_at = time.monotonic() + self.probe_start_delay
        self._last_probe_finished = 0.0

    def _ensure_probe(self) -> None:
        now = time.monotonic()
        if now < self._probe_allowed_at:
            return
        if self._probe_task and not self._probe_task.done():
            return
        if self._last_probe_finished and now - self._last_probe_finished < self.probe_interval:
            return
        super()._ensure_probe()

    async def _run_probe(self) -> None:
        try:
            await super()._run_probe()
        finally:
            self._last_probe_finished = time.monotonic()

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]],
    ) -> None:
        if scope.get("type") != "http":
            await self.downstream(scope, receive, send)
            return

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

        if path == "/api/runtime/bootstrap/status":
            self._ensure_probe()
            await self._send_json(send, 200, self._bootstrap_status())
            return

        if path == "/api/runtime/bootstrap/proxy":
            self._ensure_probe()
            await self._handle_proxy(scope, send)
            return

        if path == BOOTSTRAP_COORDINATOR_PATH:
            await self._send_javascript(send, BOOTSTRAP_SOURCE)
            return

        if path == PRODUCTION_INTEGRATION_PATH or self._accepts_html(scope):
            await self._transform_response(scope, receive, send)
            return

        # Ordinary UI/API/static traffic must never create a heavyweight status
        # probe process. The authoritative downstream remains untouched.
        await self.downstream(scope, receive, send)


app = ProductionRuntimeBootstrapGateway(
    authoritative_app,
    status_paths=PRODUCTION_STATUS_PATHS,
)

__all__ = [
    "PRODUCTION_STATUS_PATHS",
    "ProductionRuntimeBootstrapGateway",
    "app",
]

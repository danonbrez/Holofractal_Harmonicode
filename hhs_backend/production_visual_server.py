"""Production HHS visual server with authoritative status caching.

The canonical application remains ``hhs_backend.visual_server:app``.  This
module supplies the deployment-facing ASGI gateway that:

* prewarms the real Pass 196-201 status routes sequentially;
* serves direct status reads from the persistent cache;
* returns an explicit warming projection instead of executing an expensive
  status handler on the serving event loop; and
* retains the browser bootstrap injection and event-driven readiness behavior
  implemented by :mod:`hhs_backend.cached_visual_server`.
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from hhs_backend.cached_visual_server import RuntimeBootstrapGateway
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
    """Serve known expensive status routes from stale-while-revalidate state."""

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

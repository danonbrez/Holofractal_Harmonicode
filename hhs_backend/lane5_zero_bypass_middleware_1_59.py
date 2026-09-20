"""Canonical public API interposition for Pass 219 Lane 5 1.59."""
from __future__ import annotations

import json
from typing import Any, Awaitable, Callable, MutableMapping

from hhs_runtime.pass219.lane5_linux_api_interposer_1_59 import (
    Lane5LinuxAPIInterpositionError,
    interpose_linux_api_request,
)

_RUNTIME_PREFIXES = ("/api/", "/v1/")


class Lane5ZeroBypassRuntimeMiddleware:
    """Redirect public runtime/API traffic through the Lane 5 control plane.

    The middleware does not execute VM81 or transform the request body. It
    establishes the mandatory Lane-5 interposition before a runtime handler can
    run. Canonical mutation, if requested downstream, is still possible only
    through the native 1.59 RNA/PQC/VM81 gateway.
    """

    def __init__(self, app: Callable[..., Awaitable[None]]) -> None:
        self.app = app

    @staticmethod
    def _covered(scope: MutableMapping[str, Any]) -> bool:
        if scope.get("type") not in {"http", "websocket"}:
            return False
        path = str(scope.get("path") or "")
        return path.startswith(_RUNTIME_PREFIXES)

    async def __call__(
        self,
        scope: MutableMapping[str, Any],
        receive: Callable[..., Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]],
    ) -> None:
        if not self._covered(scope):
            await self.app(scope, receive, send)
            return

        path = str(scope.get("path") or "")
        method = (
            str(scope.get("method") or "WEBSOCKET")
            if scope.get("type") == "http"
            else "WEBSOCKET"
        )
        try:
            receipt = interpose_linux_api_request(
                operation_id=f"{method}:{path}",
                surface="io.ingress",
                payload={
                    "scope_type": str(scope.get("type")),
                    "method": method,
                    "path": path,
                    "query_length": len(scope.get("query_string") or b""),
                },
            )
        except Lane5LinuxAPIInterpositionError as exc:
            if scope.get("type") == "websocket":
                await send({"type": "websocket.close", "code": 1008, "reason": str(exc)[:123]})
                return
            body = json.dumps(
                {
                    "schema": "HHS_PASS219_LANE5_ZERO_BYPASS_HTTP_REJECTION_1_59",
                    "detail": str(exc),
                    "lane5_redirect_required": True,
                },
                sort_keys=True,
            ).encode("utf-8")
            await send(
                {
                    "type": "http.response.start",
                    "status": 503,
                    "headers": [
                        (b"content-type", b"application/json"),
                        (b"content-length", str(len(body)).encode("ascii")),
                    ],
                }
            )
            await send({"type": "http.response.body", "body": body})
            return

        state = scope.setdefault("state", {})
        state["hhs_lane5_interposition"] = receipt
        state["hhs_lane5_zero_bypass"] = True
        await self.app(scope, receive, send)


__all__ = ["Lane5ZeroBypassRuntimeMiddleware"]

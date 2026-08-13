"""Runtime-OS binding for the Pass 218 Iteration 8 lifecycle gate.

This module composes the existing application lifespan rather than replacing
it. The web service may remain available in a degraded diagnostic state when a
persisted Pass-218 generation is invalid, but Pass-218 ingestion remains closed
until the durable canonical state is restored or a valid first-boot empty state
is established.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import os
from pathlib import Path
import tempfile
from typing import Any

from hhs_runtime.pass218.lifecycle import Pass218RuntimeLifecycle

PASS218_RUNTIME_STATUS_PATH = "/api/runtime/pass218/lifecycle/status"
PASS218_APP_STATE_KEY = "hhs_pass218_runtime_lifecycle"


def resolve_pass218_state_root() -> Path:
    explicit = os.environ.get("HHS_PASS218_STATE_ROOT")
    if explicit:
        return Path(explicit).expanduser().resolve()
    data_root = os.environ.get("HHS_DATA_DIR")
    if data_root:
        return (Path(data_root).expanduser().resolve() / "pass218")
    return (Path(tempfile.gettempdir()) / "hhs-pass218-runtime-os").resolve()


def _has_exact_route(app: Any, path: str) -> bool:
    return any(
        str(getattr(route, "path", "")) == path
        for route in app.router.routes
    )


def install_pass218_runtime_os_lifecycle(
    app: Any,
    *,
    state_root: str | os.PathLike[str] | None = None,
) -> Pass218RuntimeLifecycle:
    """Install exactly one lifecycle wrapper and diagnostic status route."""
    existing = getattr(app.state, PASS218_APP_STATE_KEY, None)
    if isinstance(existing, Pass218RuntimeLifecycle):
        return existing

    lifecycle = Pass218RuntimeLifecycle(
        resolve_pass218_state_root() if state_root is None else state_root
    )
    setattr(app.state, PASS218_APP_STATE_KEY, lifecycle)

    if not _has_exact_route(app, PASS218_RUNTIME_STATUS_PATH):
        async def pass218_runtime_lifecycle_status() -> dict[str, Any]:
            return lifecycle.status()

        app.add_api_route(
            PASS218_RUNTIME_STATUS_PATH,
            pass218_runtime_lifecycle_status,
            methods=["GET", "HEAD"],
            include_in_schema=True,
            name="hhs-pass218-runtime-lifecycle-status",
        )

    inherited_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def pass218_runtime_lifespan(app_instance):
        async with inherited_lifespan(app_instance):
            await asyncio.to_thread(lifecycle.startup)
            try:
                yield
            finally:
                await asyncio.to_thread(lifecycle.shutdown)

    app.router.lifespan_context = pass218_runtime_lifespan
    return lifecycle


__all__ = [
    "PASS218_APP_STATE_KEY",
    "PASS218_RUNTIME_STATUS_PATH",
    "install_pass218_runtime_os_lifecycle",
    "resolve_pass218_state_root",
]

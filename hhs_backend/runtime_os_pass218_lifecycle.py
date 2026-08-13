"""Runtime-OS binding for the Pass 218 Iteration 9/10 lifecycle gate.

The existing single-host deployment remains on the validated Iteration-9 local
fence unless distributed authority is configured. When an etcd endpoint is
present, or distributed authority is explicitly required, the same Runtime-OS
lifespan mounts Iteration 10 and requires both local and cross-host fencing
before Pass-218 ingress can open.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, suppress
import os
from pathlib import Path
import tempfile
from typing import Any

from hhs_runtime.pass218.distributed_ownership import (
    DEFAULT_ETCD_LEASE_TTL_SECONDS,
    DEFAULT_ETCD_NAMESPACE,
    DEFAULT_ETCD_TIMEOUT_SECONDS,
    Pass218EtcdDistributedAuthority,
    Pass218UnavailableDistributedAuthority,
)
from hhs_runtime.pass218.lifecycle_i9 import Pass218MultiprocessRuntimeLifecycle
from hhs_runtime.pass218.lifecycle_i10 import Pass218DistributedRuntimeLifecycle

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


def _env_true(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _positive_env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    value = int(raw)
    if value < 1:
        raise ValueError(name + " must be positive")
    return value


def _has_exact_route(app: Any, path: str) -> bool:
    return any(
        str(getattr(route, "path", "")) == path
        for route in app.router.routes
    )


def _build_pass218_lifecycle(
    state_root: str | os.PathLike[str],
) -> Pass218MultiprocessRuntimeLifecycle:
    endpoint = os.environ.get("HHS_PASS218_ETCD_ENDPOINT", "").strip()
    distributed_required = _env_true("HHS_PASS218_DISTRIBUTED_REQUIRED")
    if not endpoint and not distributed_required:
        return Pass218MultiprocessRuntimeLifecycle(state_root)

    if not endpoint:
        return Pass218DistributedRuntimeLifecycle(
            state_root,
            distributed_authority=Pass218UnavailableDistributedAuthority(),
        )

    try:
        authority = Pass218EtcdDistributedAuthority(
            endpoint,
            namespace=os.environ.get(
                "HHS_PASS218_ETCD_NAMESPACE",
                DEFAULT_ETCD_NAMESPACE,
            ).strip(),
            lease_ttl_seconds=_positive_env_int(
                "HHS_PASS218_ETCD_LEASE_TTL_SECONDS",
                DEFAULT_ETCD_LEASE_TTL_SECONDS,
            ),
            timeout_seconds=_positive_env_int(
                "HHS_PASS218_ETCD_TIMEOUT_SECONDS",
                DEFAULT_ETCD_TIMEOUT_SECONDS,
            ),
            authorization=(
                os.environ.get("HHS_PASS218_ETCD_AUTHORIZATION") or None
            ),
            ca_file=(os.environ.get("HHS_PASS218_ETCD_CA_FILE") or None),
        )
    except Exception:
        # Misconfigured distributed mode must not silently fall back to local
        # writer authority. Keep the web service diagnostic-only and fail closed.
        authority = Pass218UnavailableDistributedAuthority()
    return Pass218DistributedRuntimeLifecycle(
        state_root,
        distributed_authority=authority,
    )


async def _distributed_keepalive_loop(
    lifecycle: Pass218DistributedRuntimeLifecycle,
) -> None:
    while True:
        await asyncio.sleep(lifecycle.keepalive_interval_seconds)
        if not lifecycle.distributed.held:
            continue
        try:
            await asyncio.to_thread(lifecycle.renew_distributed_authority)
        except Exception:
            # renew_distributed_authority itself closes ingress and records the
            # exact failure. The diagnostic web surface remains available.
            continue


def install_pass218_runtime_os_lifecycle(
    app: Any,
    *,
    state_root: str | os.PathLike[str] | None = None,
) -> Pass218MultiprocessRuntimeLifecycle:
    """Install exactly one fenced lifecycle wrapper and diagnostic status route."""
    existing = getattr(app.state, PASS218_APP_STATE_KEY, None)
    if isinstance(existing, Pass218MultiprocessRuntimeLifecycle):
        return existing

    lifecycle = _build_pass218_lifecycle(
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
            keepalive_task = None
            if isinstance(lifecycle, Pass218DistributedRuntimeLifecycle):
                keepalive_task = asyncio.create_task(
                    _distributed_keepalive_loop(lifecycle)
                )
            try:
                yield
            finally:
                if keepalive_task is not None:
                    keepalive_task.cancel()
                    with suppress(asyncio.CancelledError):
                        await keepalive_task
                await asyncio.to_thread(lifecycle.shutdown)

    app.router.lifespan_context = pass218_runtime_lifespan
    return lifecycle


__all__ = [
    "PASS218_APP_STATE_KEY",
    "PASS218_RUNTIME_STATUS_PATH",
    "install_pass218_runtime_os_lifecycle",
    "resolve_pass218_state_root",
]

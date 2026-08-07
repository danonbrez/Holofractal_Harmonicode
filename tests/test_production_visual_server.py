from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from hhs_backend.production_visual_server import (
    PRODUCTION_STATUS_PATHS,
    ProductionRuntimeBootstrapGateway,
)
from hhs_backend.runtime_bootstrap_cache import RuntimeStatusCache


async def forbidden_downstream(scope, receive, send):
    raise AssertionError(f"direct cached status reached downstream: {scope['path']}")


async def invoke(app, path: str) -> tuple[int, dict[bytes, bytes], dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    delivered = False

    async def receive():
        nonlocal delivered
        if delivered:
            return {"type": "http.disconnect"}
        delivered = True
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        messages.append(message)

    await app(
        {
            "type": "http",
            "method": "GET",
            "path": path,
            "query_string": b"",
            "headers": [(b"accept", b"application/json")],
        },
        receive,
        send,
    )
    start = next(item for item in messages if item["type"] == "http.response.start")
    body = b"".join(
        item.get("body", b"")
        for item in messages
        if item["type"] == "http.response.body"
    )
    return start["status"], dict(start["headers"]), json.loads(body)


def test_production_gateway_defaults_cognition_clock_to_quiescent():
    assert os.environ.get("HHS_COGNITION_AUTO_TICK") == "0"


def test_production_status_catalog_matches_deployed_routes():
    assert PRODUCTION_STATUS_PATHS == (
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
    assert "/api/runtime/calibration/registry/status" not in PRODUCTION_STATUS_PATHS
    assert "/api/runtime/optimization/status" not in PRODUCTION_STATUS_PATHS


def test_direct_status_miss_returns_warming_without_downstream(tmp_path: Path):
    cache = RuntimeStatusCache(tmp_path / "cache.json", ttl_seconds=30)
    gateway = ProductionRuntimeBootstrapGateway(
        forbidden_downstream,
        cache=cache,
        status_paths=PRODUCTION_STATUS_PATHS,
        probe_enabled=False,
    )
    status, headers, payload = asyncio.run(
        invoke(gateway, "/api/runtime/optimization-authority/status")
    )
    assert status == 200
    assert headers[b"x-hhs-runtime-cache"] == b"MISS"
    assert payload["runtime_bootstrap_pending"] is True


def test_direct_status_hit_returns_cached_projection(tmp_path: Path):
    path = "/api/runtime/optimization-active/status"
    cache = RuntimeStatusCache(tmp_path / "cache.json", ttl_seconds=30)
    cache.put(path, {"ok": True, "status": "READY"})
    gateway = ProductionRuntimeBootstrapGateway(
        forbidden_downstream,
        cache=cache,
        status_paths=PRODUCTION_STATUS_PATHS,
        probe_enabled=False,
    )
    status, headers, payload = asyncio.run(invoke(gateway, path))
    assert status == 200
    assert headers[b"x-hhs-runtime-cache"] == b"HIT"
    assert payload == {"ok": True, "status": "READY"}

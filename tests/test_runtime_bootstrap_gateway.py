from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from hhs_backend.cached_visual_server import (
    NEW_WAIT_FOR_HARMONIZER,
    RuntimeBootstrapGateway,
    inject_bootstrap_script,
    transform_production_integration,
)
from hhs_backend.runtime_bootstrap_cache import RuntimeStatusCache


async def fake_app(scope, receive, send):
    path = scope["path"]
    if path == "/src/production-integration.mjs":
        body = ("before\n" + """async function waitForHarmonizer() {
  for (let attempt = 0; attempt < 800; attempt += 1) {
    if (window.HHSHarmonizer?.registry) return window.HHSHarmonizer;
    await sleep(25);
  }
  throw new Error('Pass 161 Harmonizer runtime did not expose its registry');
}""" + "\nafter").encode()
        content_type = b"text/javascript"
    else:
        body = b'<html><head><script type="module" src="/src/main.mjs"></script></head></html>'
        content_type = b"text/html"
    await send({"type": "http.response.start", "status": 200, "headers": [(b"content-type", content_type)]})
    await send({"type": "http.response.body", "body": body, "more_body": False})


async def invoke(app, path: str, query: str = "") -> tuple[int, dict[bytes, bytes], bytes]:
    messages: list[dict[str, Any]] = []
    used = False

    async def receive():
        nonlocal used
        if used:
            return {"type": "http.disconnect"}
        used = True
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        messages.append(message)

    await app({
        "type": "http", "method": "GET", "path": path,
        "query_string": query.encode(), "headers": [(b"accept", b"text/html")],
    }, receive, send)
    start = next(message for message in messages if message["type"] == "http.response.start")
    body = b"".join(message.get("body", b"") for message in messages if message["type"] == "http.response.body")
    return start["status"], dict(start["headers"]), body


def test_cache_persists_and_reports_stale(tmp_path: Path):
    path = tmp_path / "cache.json"
    cache = RuntimeStatusCache(path, ttl_seconds=30)
    cache.put("/api/runtime/example/status", {"ok": True, "phase": "READY"}, duration_ms=9)
    loaded = RuntimeStatusCache(path, ttl_seconds=30)
    lookup = loaded.lookup("/api/runtime/example/status")
    assert lookup.state == "HIT"
    assert lookup.payload == {"ok": True, "phase": "READY"}


def test_html_injection_is_idempotent():
    source = '<html><head><script type="module" src="/x.mjs"></script></head></html>'
    once = inject_bootstrap_script(source)
    twice = inject_bootstrap_script(once)
    assert once == twice
    assert once.index("runtime-bootstrap-coordinator") < once.index('<script type="module"')


def test_production_wait_is_event_driven():
    old = """async function waitForHarmonizer() {
  for (let attempt = 0; attempt < 800; attempt += 1) {
    if (window.HHSHarmonizer?.registry) return window.HHSHarmonizer;
    await sleep(25);
  }
  throw new Error('Pass 161 Harmonizer runtime did not expose its registry');
}"""
    transformed = transform_production_integration(old)
    assert transformed == NEW_WAIT_FOR_HARMONIZER
    assert "hhs:browser:ready" in transformed
    assert "120_000" in transformed


def test_gateway_returns_warming_without_calling_expensive_status(tmp_path: Path):
    cache = RuntimeStatusCache(tmp_path / "cache.json", ttl_seconds=30)
    gateway = RuntimeBootstrapGateway(fake_app, cache=cache, status_paths=["/api/runtime/example/status"], probe_enabled=False)
    status, headers, body = asyncio.run(invoke(
        gateway,
        "/api/runtime/bootstrap/proxy",
        "path=%2Fapi%2Fruntime%2Fexample%2Fstatus",
    ))
    assert status == 200
    assert headers[b"x-hhs-runtime-cache"] == b"MISS"
    payload = json.loads(body)
    assert payload["runtime_bootstrap_pending"] is True


def test_gateway_serves_cached_status(tmp_path: Path):
    cache = RuntimeStatusCache(tmp_path / "cache.json", ttl_seconds=30)
    cache.put("/api/runtime/example/status", {"ok": True, "phase": "READY"})
    gateway = RuntimeBootstrapGateway(fake_app, cache=cache, status_paths=["/api/runtime/example/status"], probe_enabled=False)
    status, headers, body = asyncio.run(invoke(
        gateway,
        "/api/runtime/bootstrap/proxy",
        "path=%2Fapi%2Fruntime%2Fexample%2Fstatus",
    ))
    assert status == 200
    assert headers[b"x-hhs-runtime-cache"] == b"HIT"
    assert json.loads(body) == {"ok": True, "phase": "READY"}


def test_gateway_transforms_html_and_integration_module(tmp_path: Path):
    cache = RuntimeStatusCache(tmp_path / "cache.json", ttl_seconds=30)
    gateway = RuntimeBootstrapGateway(fake_app, cache=cache, probe_enabled=False)
    _, _, html = asyncio.run(invoke(gateway, "/"))
    assert b"runtime-bootstrap-coordinator" in html
    _, _, source = asyncio.run(invoke(gateway, "/src/production-integration.mjs"))
    assert b"hhs:browser:ready" in source
    assert b"attempt < 800" not in source


def test_gateway_serves_external_coordinator(tmp_path: Path):
    cache = RuntimeStatusCache(tmp_path / "cache.json", ttl_seconds=30)
    gateway = RuntimeBootstrapGateway(fake_app, cache=cache, probe_enabled=False)
    status, headers, source = asyncio.run(invoke(gateway, "/runtime-bootstrap-coordinator.js"))
    assert status == 200
    assert headers[b"content-type"].startswith(b"text/javascript")
    assert b"coordinatedFetch" in source
    assert b"hhs:browser:ready" in source

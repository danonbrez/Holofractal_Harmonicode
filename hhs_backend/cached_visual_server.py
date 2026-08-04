"""Production ASGI gateway for non-blocking HHS runtime bootstrap.

This gateway preserves ``hhs_backend.visual_server:app`` as the authoritative app,
but prevents import-time browser status fanout from synchronously invoking expensive
repository scans. Status reads use persistent stale-while-revalidate projections while
an isolated child process refreshes authoritative results sequentially.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import time
from collections.abc import Awaitable, Callable, Iterable
from typing import Any
from urllib.parse import parse_qs

from hhs_backend.runtime_bootstrap_cache import RuntimeStatusCache
from hhs_backend.visual_server import app as authoritative_app

ASGIApp = Callable[[dict[str, Any], Callable[[], Awaitable[dict[str, Any]]], Callable[[dict[str, Any]], Awaitable[None]]], Awaitable[None]]

DEFAULT_STATUS_PATHS = (
    "/api/runtime/authority/status",
    "/api/runtime/integration/status",
    "/api/runtime/calibration/status",
    "/api/runtime/calibration/registry/status",
    "/api/runtime/distributed-calibration/status",
    "/api/runtime/optimization/status",
    "/api/public/status",
)
STATUS_PATH_RE = re.compile(r"^/api/(?:runtime|public)(?:/[^?#]+)*/status$")
PRODUCTION_INTEGRATION_PATH = "/src/production-integration.mjs"
BOOTSTRAP_COORDINATOR_PATH = "/runtime-bootstrap-coordinator.js"
BOOTSTRAP_TAG = '<script src="/runtime-bootstrap-coordinator.js" data-hhs-runtime-bootstrap-coordinator="v1"></script>'

BOOTSTRAP_SOURCE = r"""
(() => {
  if (window.__HHSRuntimeBootstrapCoordinator) return;
  const nativeFetch = window.fetch.bind(window);
  const bootstrapBase = '/api/runtime/bootstrap';
  const isStatusPath = (url, method) => {
    if (String(method || 'GET').toUpperCase() !== 'GET') return false;
    const path = new URL(url, window.location.href).pathname;
    return !path.startsWith(bootstrapBase) && /^\/api\/(?:runtime|public)(?:\/[^?#]+)*\/status$/.test(path);
  };
  const coordinatedFetch = (input, init = {}) => {
    const url = typeof input === 'string' || input instanceof URL ? String(input) : input.url;
    const method = init.method || (typeof input === 'object' && input.method) || 'GET';
    if (!isStatusPath(url, method)) return nativeFetch(input, init);
    const resolved = new URL(url, window.location.href);
    const proxy = `${bootstrapBase}/proxy?path=${encodeURIComponent(resolved.pathname + resolved.search)}`;
    return nativeFetch(proxy, { headers: { Accept: 'application/json' }, cache: 'no-store' });
  };
  window.fetch = coordinatedFetch;

  let readyDispatched = false;
  const publishReady = () => {
    if (readyDispatched || !window.HHSHarmonizer?.registry) return false;
    readyDispatched = true;
    window.dispatchEvent(new CustomEvent('hhs:browser:ready', {
      detail: { registry: window.HHSHarmonizer, generation: window.HHSHarmonizer?.generation ?? null },
    }));
    return true;
  };
  if (!publishReady()) {
    const timer = window.setInterval(() => {
      if (publishReady()) window.clearInterval(timer);
    }, 25);
    window.setTimeout(() => window.clearInterval(timer), 120000);
  }

  const coordinatorState = { status: null };
  let pollTimer = null;
  const poll = async () => {
    try {
      const response = await nativeFetch(`${bootstrapBase}/status`, { cache: 'no-store', headers: { Accept: 'application/json' } });
      const status = await response.json();
      coordinatorState.status = status;
      window.dispatchEvent(new CustomEvent('hhs:runtime:bootstrap-status', { detail: status }));
      const provider = document.querySelector('#provider-status');
      if (provider && /RUNTIME CHECK|RUNTIME STATUS PENDING|RUNTIME WARMING/.test(provider.textContent || '')) {
        provider.textContent = status.ready ? 'RUNTIME READY' : 'RUNTIME STATUS PENDING';
      }
      if (!status.ready) pollTimer = window.setTimeout(poll, 2000);
    } catch (_) {
      pollTimer = window.setTimeout(poll, 4000);
    }
  };
  window.__HHSRuntimeBootstrapCoordinator = Object.freeze({
    schema: 'HHS_BROWSER_RUNTIME_BOOTSTRAP_COORDINATOR_V1',
    nativeFetch,
    get status() { return coordinatorState.status; },
  });
  window.setTimeout(poll, 0);
  window.addEventListener('pagehide', () => { if (pollTimer) window.clearTimeout(pollTimer); }, { once: true });
})();
""".strip()

OLD_WAIT_FOR_HARMONIZER = """async function waitForHarmonizer() {
  for (let attempt = 0; attempt < 800; attempt += 1) {
    if (window.HHSHarmonizer?.registry) return window.HHSHarmonizer;
    await sleep(25);
  }
  throw new Error('Pass 161 Harmonizer runtime did not expose its registry');
}"""

NEW_WAIT_FOR_HARMONIZER = """async function waitForHarmonizer({ timeoutMs = 120_000 } = {}) {
  if (window.HHSHarmonizer?.registry) return window.HHSHarmonizer;
  return new Promise((resolve, reject) => {
    let settled = false;
    const finish = (value, error = null) => {
      if (settled) return;
      settled = true;
      window.clearTimeout(timeout);
      window.clearInterval(fallback);
      window.removeEventListener('hhs:browser:ready', onReady);
      if (error) reject(error); else resolve(value);
    };
    const onReady = (event) => finish(event.detail?.registry || window.HHSHarmonizer);
    const fallback = window.setInterval(() => {
      if (window.HHSHarmonizer?.registry) finish(window.HHSHarmonizer);
    }, 100);
    const timeout = window.setTimeout(() => {
      finish(null, new Error('Pass 161 Harmonizer runtime did not expose its registry'));
    }, timeoutMs);
    window.addEventListener('hhs:browser:ready', onReady, { once: true });
  });
}"""


def inject_bootstrap_script(html: str) -> str:
    if "data-hhs-runtime-bootstrap-coordinator" in html:
        return html
    marker = '<script type="module"'
    index = html.find(marker)
    if index >= 0:
        return html[:index] + BOOTSTRAP_TAG + "\n" + html[index:]
    closing = html.lower().find("</head>")
    if closing >= 0:
        return html[:closing] + BOOTSTRAP_TAG + "\n" + html[closing:]
    return BOOTSTRAP_TAG + "\n" + html


def transform_production_integration(source: str) -> str:
    if OLD_WAIT_FOR_HARMONIZER not in source:
        return source
    return source.replace(OLD_WAIT_FOR_HARMONIZER, NEW_WAIT_FOR_HARMONIZER, 1)


class RuntimeBootstrapGateway:
    SCHEMA = "HHS_RUNTIME_BOOTSTRAP_GATEWAY_V1"

    def __init__(
        self,
        downstream: ASGIApp,
        *,
        cache: RuntimeStatusCache | None = None,
        status_paths: Iterable[str] = DEFAULT_STATUS_PATHS,
        probe_enabled: bool = True,
    ) -> None:
        cache_path = os.getenv("HHS_RUNTIME_STATUS_CACHE", "/var/lib/hhs/runtime-bootstrap/status-cache.json")
        ttl = float(os.getenv("HHS_RUNTIME_STATUS_TTL_SECONDS", "15"))
        self.downstream = downstream
        self.cache = cache or RuntimeStatusCache(cache_path, ttl_seconds=ttl)
        self.status_paths = list(dict.fromkeys(status_paths))
        self.probe_enabled = probe_enabled and os.getenv("HHS_RUNTIME_STATUS_PROBE", "1") != "0"
        self.probe_interval = max(1.0, float(os.getenv("HHS_RUNTIME_STATUS_PROBE_INTERVAL_SECONDS", "60")))
        self.probe_timeout = max(5.0, float(os.getenv("HHS_RUNTIME_STATUS_PROBE_TIMEOUT_SECONDS", "180")))
        self._probe_task: asyncio.Task[None] | None = None
        self._last_probe_started = 0.0

    async def __call__(self, scope: dict[str, Any], receive: Callable[[], Awaitable[dict[str, Any]]], send: Callable[[dict[str, Any]], Awaitable[None]]) -> None:
        if scope.get("type") != "http":
            await self.downstream(scope, receive, send)
            return
        path = str(scope.get("path") or "")
        self._ensure_probe()
        if path == BOOTSTRAP_COORDINATOR_PATH:
            await self._send_javascript(send, BOOTSTRAP_SOURCE)
            return
        if path == "/api/runtime/bootstrap/status":
            await self._send_json(send, 200, self._bootstrap_status())
            return
        if path == "/api/runtime/bootstrap/proxy":
            await self._handle_proxy(scope, send)
            return
        if path == PRODUCTION_INTEGRATION_PATH or self._accepts_html(scope):
            await self._transform_response(scope, receive, send)
            return
        await self.downstream(scope, receive, send)

    def _ensure_probe(self) -> None:
        if not self.probe_enabled:
            return
        now = time.monotonic()
        if self._probe_task and not self._probe_task.done():
            return
        if now - self._last_probe_started < self.probe_interval:
            return
        self._last_probe_started = now
        self._probe_task = asyncio.create_task(self._run_probe())

    async def _run_probe(self) -> None:
        command = [
            sys.executable,
            "-m",
            "hhs_backend.runtime_status_probe",
            "--paths-json",
            json.dumps(self.status_paths),
        ]
        environment = dict(os.environ)
        environment["HHS_BOOTSTRAP_PROBE_CHILD"] = "1"
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
            env=environment,
        )
        try:
            assert process.stdout is not None
            while True:
                line = await asyncio.wait_for(process.stdout.readline(), timeout=self.probe_timeout)
                if not line:
                    break
                try:
                    record = json.loads(line)
                    payload = record.get("payload")
                    path = record.get("path")
                    if isinstance(path, str) and isinstance(payload, dict):
                        self.cache.put(
                            path,
                            payload,
                            status_code=int(record.get("status_code", 200)),
                            duration_ms=int(record.get("duration_ms", 0)),
                        )
                except (json.JSONDecodeError, TypeError, ValueError):
                    continue
            await asyncio.wait_for(process.wait(), timeout=5)
        except asyncio.CancelledError:
            process.kill()
            await process.wait()
            raise
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()

    def _bootstrap_status(self) -> dict[str, Any]:
        entries = {}
        ready_count = 0
        for path in self.status_paths:
            lookup = self.cache.lookup(path)
            if lookup.payload is not None:
                ready_count += 1
            entries[path] = {
                "cache_state": lookup.state,
                "age_ms": lookup.age_ms,
                "available": lookup.payload is not None,
                "phase": (lookup.payload or {}).get("phase") or (lookup.payload or {}).get("status"),
            }
        return {
            "schema": self.SCHEMA,
            "ok": True,
            "ready": ready_count == len(self.status_paths),
            "available_count": ready_count,
            "expected_count": len(self.status_paths),
            "probe_running": bool(self._probe_task and not self._probe_task.done()),
            "entries": entries,
            "canonical_runtime_mutated": False,
        }

    async def _handle_proxy(self, scope: dict[str, Any], send: Callable[[dict[str, Any]], Awaitable[None]]) -> None:
        query = parse_qs(bytes(scope.get("query_string", b"")).decode("utf-8", errors="replace"))
        path = (query.get("path") or [""])[0]
        if not STATUS_PATH_RE.fullmatch(path.split("?", 1)[0]) or path.startswith("/api/runtime/bootstrap/"):
            await self._send_json(send, 400, {"ok": False, "error": "INVALID_STATUS_PROXY_PATH"})
            return
        if path not in self.status_paths:
            self.status_paths.append(path)
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
        await self._send_json(
            send,
            200,
            payload,
            extra_headers=[
                (b"x-hhs-runtime-cache", lookup.state.encode("ascii")),
                (b"cache-control", b"no-store"),
            ],
        )

    @staticmethod
    def _accepts_html(scope: dict[str, Any]) -> bool:
        path = str(scope.get("path") or "")
        if path == "/" or path.endswith(".html"):
            return True
        headers = {key.lower(): value for key, value in scope.get("headers", [])}
        return b"text/html" in headers.get(b"accept", b"") and not path.startswith("/api/")

    async def _transform_response(self, scope: dict[str, Any], receive: Callable[[], Awaitable[dict[str, Any]]], send: Callable[[dict[str, Any]], Awaitable[None]]) -> None:
        captured: list[dict[str, Any]] = []

        async def capture(message: dict[str, Any]) -> None:
            captured.append(message)

        await self.downstream(scope, receive, capture)
        start = next((m for m in captured if m["type"] == "http.response.start"), None)
        if start is None:
            for message in captured:
                await send(message)
            return
        body = b"".join(m.get("body", b"") for m in captured if m["type"] == "http.response.body")
        headers = [(k.lower(), v) for k, v in start.get("headers", []) if k.lower() != b"content-length"]
        content_type = next((v for k, v in headers if k == b"content-type"), b"")
        path = str(scope.get("path") or "")
        transformed = body
        if start.get("status") == 200 and b"text/html" in content_type:
            transformed = inject_bootstrap_script(body.decode("utf-8", errors="replace")).encode("utf-8")
        elif start.get("status") == 200 and path == PRODUCTION_INTEGRATION_PATH:
            transformed = transform_production_integration(body.decode("utf-8", errors="replace")).encode("utf-8")
        headers.append((b"content-length", str(len(transformed)).encode("ascii")))
        headers.append((b"x-hhs-runtime-bootstrap", b"v1"))
        await send({"type": "http.response.start", "status": start.get("status", 200), "headers": headers})
        await send({"type": "http.response.body", "body": transformed, "more_body": False})

    @staticmethod
    async def _send_javascript(
        send: Callable[[dict[str, Any]], Awaitable[None]],
        source: str,
    ) -> None:
        body = source.encode("utf-8")
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [
                (b"content-type", b"text/javascript; charset=utf-8"),
                (b"content-length", str(len(body)).encode("ascii")),
                (b"cache-control", b"no-store"),
            ],
        })
        await send({"type": "http.response.body", "body": body, "more_body": False})

    @staticmethod
    async def _send_json(
        send: Callable[[dict[str, Any]], Awaitable[None]],
        status: int,
        payload: dict[str, Any],
        *,
        extra_headers: list[tuple[bytes, bytes]] | None = None,
    ) -> None:
        body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        headers = [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode("ascii"))]
        if extra_headers:
            headers.extend(extra_headers)
        await send({"type": "http.response.start", "status": status, "headers": headers})
        await send({"type": "http.response.body", "body": body, "more_body": False})


app = RuntimeBootstrapGateway(authoritative_app)

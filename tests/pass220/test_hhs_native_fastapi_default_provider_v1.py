from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

from hhs_backend.runtime.hhs_native_fastapi_compat_v1 import NativeAPIRouter


ROOT = Path(__file__).resolve().parents[2]


def _run_python(source: str, *, provider: str | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env.pop("HHS_FASTAPI_PROVIDER", None)
    if provider is not None:
        env["HHS_FASTAPI_PROVIDER"] = provider
    return subprocess.run(
        [sys.executable, "-c", source],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_native_api_router_preserves_deferred_route_metadata() -> None:
    router = NativeAPIRouter(prefix="/api", tags=["native"])

    @router.get("/health")
    def health():
        return {"ok": True}

    @router.websocket("/events")
    async def events(websocket):
        _ = websocket

    assert len(router.routes) == 2
    health_route, websocket_route = router.routes
    assert health_route.path == "/api/health"
    assert health_route.methods == frozenset({"GET"})
    assert health_route.tags == ("native",)
    assert health_route.include_in_schema is True
    assert websocket_route.path == "/api/events"
    assert websocket_route.methods == frozenset({"WEBSOCKET"})
    assert websocket_route.route_type == "WEBSOCKET"
    assert websocket_route.include_in_schema is False


def test_default_provider_uses_repository_native_when_external_fastapi_is_absent() -> None:
    source = r"""
import builtins
import json
import os

real_import = builtins.__import__

def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "fastapi" or name.startswith("fastapi."):
        raise ModuleNotFoundError("No module named 'fastapi'", name="fastapi")
    return real_import(name, globals, locals, fromlist, level)

builtins.__import__ = guarded_import
os.environ.pop("HHS_FASTAPI_PROVIDER", None)

from hhs_backend.runtime.hhs_fastapi_provider_v1 import (
    APIRouter,
    fastapi_provider_status,
)
from hhs_backend.runtime import runtime_ws

status = fastapi_provider_status()
assert status["requested"] == "native"
assert status["selected"] == "native"
assert status["native_fallback"] is True
assert status["external_available"] is False
assert APIRouter.__name__ == "NativeAPIRouter"
assert runtime_ws.runtime_ws_router.__class__.__name__ == "NativeAPIRouter"
assert len(runtime_ws.runtime_ws_router.routes) == 4
assert {
    (route.path, tuple(sorted(route.methods)))
    for route in runtime_ws.runtime_ws_router.routes
} == {
    ("/ws/runtime", ("WEBSOCKET",)),
    ("/ws/replay", ("WEBSOCKET",)),
    ("/ws/graph", ("WEBSOCKET",)),
    ("/ws/transport", ("WEBSOCKET",)),
}
print(json.dumps(status, sort_keys=True))
"""
    result = _run_python(source)
    assert result.returncode == 0, result.stderr
    status = json.loads(result.stdout.strip().splitlines()[-1])
    assert status["selected"] == "native"


def test_explicit_external_provider_fails_closed_when_external_fastapi_is_absent() -> None:
    source = r"""
import builtins
import os

real_import = builtins.__import__

def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "fastapi" or name.startswith("fastapi."):
        raise ModuleNotFoundError("No module named 'fastapi'", name="fastapi")
    return real_import(name, globals, locals, fromlist, level)

builtins.__import__ = guarded_import
os.environ["HHS_FASTAPI_PROVIDER"] = "external"

try:
    import hhs_backend.runtime.hhs_fastapi_provider_v1
except RuntimeError as exc:
    assert str(exc) == "HHS_FASTAPI_EXTERNAL_EXPLICIT_BUT_UNAVAILABLE"
else:
    raise AssertionError("explicit external FastAPI selection did not fail closed")
"""
    result = _run_python(source, provider="external")
    assert result.returncode == 0, result.stderr


def test_explicit_native_provider_never_requires_external_fastapi() -> None:
    source = r"""
import builtins
import json
import os

real_import = builtins.__import__

def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "fastapi" or name.startswith("fastapi."):
        raise AssertionError("external FastAPI import attempted in explicit native mode")
    return real_import(name, globals, locals, fromlist, level)

builtins.__import__ = guarded_import
os.environ["HHS_FASTAPI_PROVIDER"] = "native"

from hhs_backend.runtime.hhs_fastapi_provider_v1 import fastapi_provider_status
status = fastapi_provider_status()
assert status["selected"] == "native"
assert status["explicit_override"] is True
print(json.dumps(status, sort_keys=True))
"""
    result = _run_python(source, provider="native")
    assert result.returncode == 0, result.stderr

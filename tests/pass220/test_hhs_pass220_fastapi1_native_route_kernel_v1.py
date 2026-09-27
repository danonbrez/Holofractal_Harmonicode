from __future__ import annotations

import asyncio
from pathlib import Path
import shutil
import subprocess

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.api.runtime_graphics_routes import router as fastapi_graphics_router
from hhs_backend.runtime import hhs_runtime_graphics_service_v1 as graphics_service
from hhs_backend.runtime.hhs_native_fastapi_graphics_v1 import (
    build_native_runtime_graphics_app,
    native_runtime_graphics_contract,
)

ROOT = Path(__file__).resolve().parents[2]
NATIVE = ROOT / "native_projects" / "hhs_pass220_fastapi_native_route_kernel"
SOURCE = NATIVE / "src" / "hhs_pass220_fastapi_native_route_kernel_v1.c"
HEADER = NATIVE / "include" / "hhs_pass220_fastapi_native_route_kernel_v1.h"
C_TEST = NATIVE / "tests" / "hhs_pass220_fastapi_native_route_kernel_v1_test.c"


@pytest.fixture()
def native_library(tmp_path: Path) -> Path:
    cc = shutil.which("cc") or shutil.which("gcc")
    if not cc:
        pytest.skip("C compiler unavailable")
    shared = tmp_path / "libhhs_fastapi_native_route_kernel_v1.so"
    subprocess.run(
        [
            cc,
            "-std=c11",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-pedantic",
            "-fPIC",
            "-shared",
            f"-I{NATIVE / 'include'}",
            str(SOURCE),
            "-o",
            str(shared),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return shared


def test_fastapi1_native_c11_route_kernel_harness(tmp_path: Path) -> None:
    cc = shutil.which("cc") or shutil.which("gcc")
    if not cc:
        pytest.skip("C compiler unavailable")
    exe = tmp_path / "route-kernel-test"
    subprocess.run(
        [
            cc,
            "-std=c11",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-pedantic",
            f"-I{NATIVE / 'include'}",
            str(SOURCE),
            str(C_TEST),
            "-o",
            str(exe),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    result = subprocess.run(
        [str(exe)],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    assert result.stdout.strip() == "PASS hhs_pass220_fastapi_native_route_kernel_v1"


def _deterministic_vulkan_projection() -> dict:
    return {
        "schema": "HHS_RUNTIME_GRAPHICS_VULKAN_LOADER_V1",
        "platform": "TEST",
        "loader_ready": True,
        "loader_source": "TEST_NATIVE_COMPATIBILITY",
        "loader_path": "/test/libvulkan.so.1",
        "loader_errors": [],
        "required_symbols": [
            "vkGetInstanceProcAddr",
            "vkCreateInstance",
            "vkEnumerateInstanceExtensionProperties",
        ],
        "missing_symbols": [],
        "api_version": {
            "available": True,
            "vk_result": 0,
            "raw": 4206592,
            "version": "1.3.0",
        },
        "icd_manifests": [],
        "icd_manifest_count": 0,
        "driver_ready": False,
        "runtime_mutation_authority": False,
        "authority": "HHS_GRAPHICS_PROJECTION_SUBSTRATE_AUTHORITY_V1",
        "vulkan_loader_receipt_hash72": "V" * 72,
    }


async def _native_request(app, method: str, path: str) -> tuple[int, dict[str, str], bytes]:
    events: list[dict] = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        events.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.5"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("utf-8"),
        "query_string": b"",
        "headers": [],
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
        "root_path": "",
    }
    await app(scope, receive, send)
    start = next(item for item in events if item["type"] == "http.response.start")
    body = b"".join(
        item.get("body", b"")
        for item in events
        if item["type"] == "http.response.body"
    )
    headers = {
        key.decode("latin1").lower(): value.decode("latin1")
        for key, value in start.get("headers", [])
    }
    return int(start["status"]), headers, body


def _build_fastapi_graphics_app() -> FastAPI:
    app = FastAPI()
    app.include_router(fastapi_graphics_router)
    return app


@pytest.mark.parametrize(
    "path",
    [
        "/api/runtime/graphics/status",
        "/api/runtime/graphics/vulkan",
        "/api/runtime/graphics/capabilities",
    ],
)
def test_fastapi_and_native_asgi_graphics_are_byte_equivalent(
    native_library: Path,
    monkeypatch: pytest.MonkeyPatch,
    path: str,
) -> None:
    monkeypatch.setattr(
        graphics_service,
        "inspect_vulkan_loader",
        _deterministic_vulkan_projection,
    )
    fastapi_app = _build_fastapi_graphics_app()
    fastapi_response = TestClient(fastapi_app).get(path)

    native_app = build_native_runtime_graphics_app(native_library)
    native_status, native_headers, native_body = asyncio.run(
        _native_request(native_app, "GET", path)
    )

    assert native_status == fastapi_response.status_code == 200
    assert native_headers["content-type"] == fastapi_response.headers["content-type"]
    assert native_body == fastapi_response.content


def test_fastapi_and_native_asgi_not_found_equivalence(
    native_library: Path,
) -> None:
    path = "/api/runtime/graphics/not-a-route"
    fastapi_response = TestClient(_build_fastapi_graphics_app()).get(path)
    native_status, native_headers, native_body = asyncio.run(
        _native_request(
            build_native_runtime_graphics_app(native_library),
            "GET",
            path,
        )
    )
    assert native_status == fastapi_response.status_code == 404
    assert native_headers["content-type"] == fastapi_response.headers["content-type"]
    assert native_body == fastapi_response.content


def test_fastapi_and_native_asgi_method_not_allowed_equivalence(
    native_library: Path,
) -> None:
    path = "/api/runtime/graphics/status"
    fastapi_response = TestClient(_build_fastapi_graphics_app()).post(path)
    native_status, native_headers, native_body = asyncio.run(
        _native_request(
            build_native_runtime_graphics_app(native_library),
            "POST",
            path,
        )
    )
    assert native_status == fastapi_response.status_code == 405
    assert native_headers["content-type"] == fastapi_response.headers["content-type"]
    assert native_headers["allow"] == fastapi_response.headers["allow"]
    assert native_body == fastapi_response.content


def test_fastapi1_native_graphics_contract_is_fail_closed_and_projection_only(
    native_library: Path,
) -> None:
    contract = native_runtime_graphics_contract(native_library)
    assert contract["schema"] == "HHS_PASS_220_FASTAPI1_NATIVE_GRAPHICS_ASGI_V1"
    assert contract["route_count"] == 3
    assert contract["route_registry_fingerprint"] != 0
    assert contract["starlette_internal_dependency_required"] is False
    assert contract["pydantic_internal_dependency_required"] is False
    assert contract["canonical_state_mutation_authority"] is False
    assert contract["vm81_admission_authority"] is False
    assert contract["hash72_commit_authority"] is False
    assert contract["hash216_persistence_authority"] is False


def test_fastapi1_native_modules_do_not_import_fastapi_starlette_or_pydantic() -> None:
    paths = [
        ROOT / "hhs_backend" / "runtime" / "hhs_native_fastapi_compat_v1.py",
        ROOT / "hhs_backend" / "runtime" / "hhs_native_fastapi_graphics_v1.py",
        ROOT / "hhs_backend" / "runtime" / "hhs_runtime_graphics_service_v1.py",
    ]
    for path in paths:
        source = path.read_text(encoding="utf-8")
        lowered = source.lower()
        assert "from fastapi" not in lowered
        assert "import fastapi" not in lowered
        assert "from starlette" not in lowered
        assert "import starlette" not in lowered
        assert "from pydantic" not in lowered
        assert "import pydantic" not in lowered


def test_existing_fastapi_router_is_thin_compatibility_membrane() -> None:
    source = (
        ROOT / "hhs_backend" / "api" / "runtime_graphics_routes.py"
    ).read_text(encoding="utf-8")
    assert "from fastapi import APIRouter" in source
    assert "runtime_graphics_status_payload()" in source
    assert "runtime_graphics_vulkan_status_payload()" in source
    assert "runtime_graphics_capabilities_payload()" in source
    assert "inspect_vulkan_loader" not in source

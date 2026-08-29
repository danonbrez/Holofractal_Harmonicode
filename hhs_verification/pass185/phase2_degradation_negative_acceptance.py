from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[2]
ENTRYPOINT = "hhs_backend.runtime_os_application_server:app"


def fetch(url: str, timeout: float = 10.0) -> tuple[int, str, bytes]:
    request = urllib.request.Request(url, headers={"Accept": "*/*"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.headers.get("content-type", ""), response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers.get("content-type", ""), exc.read()


def json_fetch(url: str, timeout: float = 15.0) -> dict[str, Any]:
    status, content_type, body = fetch(url, timeout=timeout)
    if status != 200:
        raise AssertionError({"url": url, "status": status, "body": body[:500].decode("utf-8", "replace")})
    if "json" not in content_type.lower():
        raise AssertionError({"url": url, "content_type": content_type})
    payload = json.loads(body)
    if not isinstance(payload, dict):
        raise AssertionError({"url": url, "payload_type": type(payload).__name__})
    return payload


def free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = int(sock.getsockname()[1])
    sock.close()
    return port


class ProductionServer:
    def __init__(self, port: int, evidence_dir: Path, env: dict[str, str] | None = None, label: str = "server"):
        self.port = port
        self.evidence_dir = evidence_dir
        self.env = dict(env or {})
        self.label = label
        self.process: subprocess.Popen[str] | None = None
        self.log_path = evidence_dir / f"{label}.log"
        self._log = None

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def start(self, wait_ready: bool = True, deadline_seconds: float = 45.0) -> dict[str, Any]:
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env.update(self.env)
        env.setdefault("HHS_COGNITION_AUTO_TICK", "0")
        env.setdefault("HHS_PASS174_BOOT_TIMEOUT_SECONDS", "12")
        env.setdefault("HHS_ASSISTANT_HEALTH_TIMEOUT_SECONDS", "0.5")
        self._log = self.log_path.open("w", encoding="utf-8")
        started = time.monotonic()
        self.process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                ENTRYPOINT,
                "--host",
                "127.0.0.1",
                "--port",
                str(self.port),
                "--workers",
                "1",
                "--log-level",
                "info",
            ],
            cwd=REPO,
            env=env,
            stdout=self._log,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if not wait_ready:
            return {"pid": self.process.pid, "started_monotonic": started}

        timeline: list[dict[str, Any]] = []
        deadline = started + deadline_seconds
        while time.monotonic() < deadline:
            code = self.process.poll()
            if code is not None:
                self._log.flush()
                raise AssertionError(
                    {
                        "classification": "PRODUCTION_SERVER_EXITED_BEFORE_READY",
                        "returncode": code,
                        "log": self.log_path.read_text(encoding="utf-8", errors="replace")[-8000:],
                    }
                )
            try:
                status, content_type, body = fetch(self.base_url + "/", timeout=0.8)
                timeline.append({"elapsed_ms": round((time.monotonic() - started) * 1000), "status": status})
                if status == 200 and b"HHS Visual Runtime OS Workspace" in body:
                    return {
                        "pid": self.process.pid,
                        "ready_ms": round((time.monotonic() - started) * 1000),
                        "content_type": content_type,
                        "timeline": timeline[-20:],
                    }
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
                timeline.append({"elapsed_ms": round((time.monotonic() - started) * 1000), "status": "not-listening"})
            time.sleep(0.25)

        raise AssertionError(
            {
                "classification": "PRODUCTION_SERVER_READY_TIMEOUT",
                "deadline_seconds": deadline_seconds,
                "timeline": timeline[-40:],
                "log": self.log_path.read_text(encoding="utf-8", errors="replace")[-8000:],
            }
        )

    def stop(self) -> dict[str, Any]:
        if not self.process:
            return {"stopped": True, "returncode": None}
        process = self.process
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        if self._log:
            self._log.flush()
            self._log.close()
            self._log = None
        return {"stopped": True, "returncode": process.returncode}


def validate_local_lifecycle(base_url: str, evidence_dir: Path, *, label: str) -> dict[str, Any]:
    download_dir = evidence_dir / f"{label}-downloads"
    download_dir.mkdir(parents=True, exist_ok=True)
    page_errors: list[str] = []
    console_errors: list[str] = []
    request_failures: list[dict[str, str]] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900}, accept_downloads=True)
        page = context.new_page()
        page.set_default_timeout(30_000)
        page.set_default_navigation_timeout(90_000)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on(
            "requestfailed",
            lambda request: request_failures.append(
                {"url": request.url, "failure": request.failure or "unknown"}
            ),
        )

        response = page.goto(base_url + "/", wait_until="domcontentloaded")
        assert response is not None and response.ok, getattr(response, "status", None)
        page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
        page.wait_for_selector('[data-testid="hhs-product-workspace"]', timeout=60_000)

        product_nav = page.locator('[data-testid="hhs-product-workspace"] > nav')
        product_nav.get_by_role("button", name="Workspace", exact=True).click()
        page.wait_for_selector('[data-testid="hhs-visual-runtime-os-workspace"]')
        workspace = page.locator('[data-testid="hhs-visual-runtime-os-workspace"]')
        workspace.get_by_role("button", name="Application", exact=True).click()
        page.wait_for_selector('[data-testid="pass185-application-lifecycle"]')

        page.get_by_test_id("pass185-create-calculator").click()
        editor = page.get_by_test_id("pass185-html-editor")
        assert 'data-hhs-calculator="true"' in editor.input_value()

        page.get_by_test_id("pass185-preview-source").click()
        page.wait_for_function(
            """() => document.querySelector('[data-testid="pass185-lifecycle-status"]')?.textContent === 'PREVIEW_READY'""",
            timeout=30_000,
        )
        page.get_by_test_id("pass185-run-test").click()
        page.wait_for_function(
            """() => document.querySelector('[data-testid="pass185-lifecycle-status"]')?.textContent === 'PREVIEW_TEST_VERIFIED'""",
            timeout=30_000,
        )

        with page.expect_download(timeout=30_000) as info:
            page.get_by_test_id("pass185-export-zip").click()
        download = info.value
        zip_path = download_dir / download.suggested_filename
        download.save_as(zip_path)
        with zipfile.ZipFile(zip_path) as archive:
            names = set(archive.namelist())
            assert names == {"index.html", "application.manifest.json", "README.txt"}
            manifest = json.loads(archive.read("application.manifest.json"))
            assert manifest["frontend_runtime_authority"] is False
            assert manifest["calculator_acceptance"] == "CALCULATOR_7_PLUS_8_EQUALS_15"

        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(150)
        assert page.get_by_test_id("pass185-export-zip").is_visible()

        screenshot = evidence_dir / f"{label}.png"
        page.screenshot(path=str(screenshot), full_page=True)
        context.close()
        browser.close()

    actionable_failures = [
        item
        for item in request_failures
        if not (
            item["failure"] == "net::ERR_ABORTED"
            and item["url"].endswith("/api/product/health")
        )
    ]
    if page_errors or actionable_failures:
        raise AssertionError(
            {
                "page_errors": page_errors,
                "request_failures": actionable_failures,
                "console_errors": console_errors[-20:],
            }
        )
    return {
        "mounted": True,
        "calculator_preview_test": "CALCULATOR_7_PLUS_8_EQUALS_15",
        "zip_name": zip_path.name,
        "zip_size_bytes": zip_path.stat().st_size,
        "mobile_export_visible": True,
        "page_errors": page_errors,
        "actionable_request_failures": actionable_failures,
        "console_errors": console_errors[-20:],
    }


def run_optional_provider_degraded(evidence_dir: Path) -> dict[str, Any]:
    port = free_port()
    empty_store = evidence_dir / "empty-word2vec"
    empty_store.mkdir(parents=True, exist_ok=True)
    server = ProductionServer(
        port,
        evidence_dir,
        env={
            "HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC": "1",
            "HHS_PASS166_STORAGE_DIR": str(empty_store),
            "HHS_LITERT_LM_BASE_URL": "http://127.0.0.1:9/v1",
            "HHS_LITERT_LM_TIMEOUT_SECONDS": "0.2",
            "HHS_ASSISTANT_HEALTH_TIMEOUT_SECONDS": "0.5",
            "HHS_DISABLE_C_AUTOBUILD": "1",
            "HHS_COGNITION_AUTO_TICK": "0",
        },
        label="optional-provider-degraded-server",
    )
    try:
        startup = server.start()
        interface = json_fetch(server.base_url + "/api/interface/status")
        product = json_fetch(server.base_url + "/api/product/health", timeout=15.0)
        assistant = product.get("assistant") or {}
        assert product.get("status") == "HHS_PRODUCT_EXECUTION_AUTHORITY_DEGRADED", product
        assert assistant.get("online") is False, assistant
        lifecycle = validate_local_lifecycle(server.base_url, evidence_dir, label="optional-provider-degraded-browser")
        return {
            "profile": "optional-provider-degraded",
            "startup": startup,
            "interface": interface,
            "product_health": product,
            "assistant_online": assistant.get("online"),
            "assistant_mode": assistant.get("effective_mode") or assistant.get("status"),
            "local_lifecycle": lifecycle,
            "base_ide_blocked_by_assistant": False,
            "base_ide_blocked_by_word2vec": False,
        }
    finally:
        server.stop()


def run_c_runtime_missing(evidence_dir: Path) -> dict[str, Any]:
    runtime_lib = REPO / "hhs_runtime" / "builds" / "libhhs_runtime.so"
    assert not runtime_lib.exists(), f"expected workflow to move {runtime_lib} before C-runtime-missing profile"
    port = free_port()
    server = ProductionServer(
        port,
        evidence_dir,
        env={
            "HHS_DISABLE_C_AUTOBUILD": "1",
            "HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC": "1",
            "HHS_PASS166_STORAGE_DIR": str(evidence_dir / "empty-word2vec-c-missing"),
            "HHS_LITERT_LM_BASE_URL": "http://127.0.0.1:9/v1",
            "HHS_LITERT_LM_TIMEOUT_SECONDS": "0.2",
            "HHS_COGNITION_AUTO_TICK": "0",
        },
        label="c-runtime-missing-server",
    )
    try:
        startup = server.start()
        interface = json_fetch(server.base_url + "/api/interface/status")
        lifecycle = validate_local_lifecycle(server.base_url, evidence_dir, label="c-runtime-missing-browser")
        return {
            "profile": "c-runtime-missing",
            "startup": startup,
            "interface": interface,
            "compiled_runtime_library_present": False,
            "autobuild_disabled": True,
            "local_lifecycle": lifecycle,
            "source_editor_and_zip_available": True,
        }
    finally:
        server.stop()


def wait_for_exit(process: subprocess.Popen[str], timeout: float) -> int:
    try:
        return int(process.wait(timeout=timeout))
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
        raise AssertionError("expected child process to exit before timeout")


def run_process_and_static_negative(evidence_dir: Path) -> dict[str, Any]:
    results: dict[str, Any] = {"profile": "process-static-negative"}

    occupied = socket.socket()
    occupied.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    occupied.bind(("127.0.0.1", 0))
    occupied.listen(1)
    occupied_port = int(occupied.getsockname()[1])
    occupied_server = ProductionServer(
        occupied_port,
        evidence_dir,
        env={"HHS_COGNITION_AUTO_TICK": "0"},
        label="occupied-port-server",
    )
    occupied_meta = occupied_server.start(wait_ready=False)
    assert occupied_server.process is not None
    occupied_code = wait_for_exit(occupied_server.process, 45)
    occupied_server.stop()
    occupied.close()
    assert occupied_code != 0
    results["occupied_port"] = {
        "port": occupied_port,
        "returncode": occupied_code,
        "finite_exit": True,
        "pid": occupied_meta["pid"],
    }

    missing_root = Path(tempfile.mkdtemp(prefix="hhs-pass185-missing-runtime-os-"))
    missing_port = free_port()
    missing_server = ProductionServer(
        missing_port,
        evidence_dir,
        env={
            "HHS_RUNTIME_OS_ASSET_ROOT": str(missing_root),
            "HHS_COGNITION_AUTO_TICK": "0",
        },
        label="missing-runtime-os-server",
    )
    missing_meta = missing_server.start(wait_ready=False)
    assert missing_server.process is not None
    missing_code = wait_for_exit(missing_server.process, 45)
    missing_server.stop()
    missing_log = missing_server.log_path.read_text(encoding="utf-8", errors="replace")
    shutil.rmtree(missing_root, ignore_errors=True)
    assert missing_code != 0
    assert "HHS Runtime OS build is missing" in missing_log
    results["child_exit_before_binding"] = {
        "returncode": missing_code,
        "finite_exit": True,
        "diagnostic_present": True,
        "pid": missing_meta["pid"],
    }

    port = free_port()
    server = ProductionServer(
        port,
        evidence_dir,
        env={"HHS_COGNITION_AUTO_TICK": "0"},
        label="static-negative-recovery-server",
    )
    try:
        startup = server.start()
        root_status, root_type, root_body = fetch(server.base_url + "/")
        assert root_status == 200 and "text/html" in root_type.lower()
        root_html = root_body.decode("utf-8", "replace")
        asset_paths = sorted(set(re.findall(r'["\'](/assets/[^"\']+)["\']', root_html)))
        assert asset_paths, "no built Runtime OS assets referenced from production root"

        mime_inventory: list[dict[str, Any]] = []
        js_asset: str | None = None
        for asset in asset_paths:
            status, content_type, body = fetch(server.base_url + asset)
            assert status == 200, (asset, status)
            lower = asset.lower().split("?", 1)[0]
            if lower.endswith(".js"):
                js_asset = js_asset or asset
                assert "javascript" in content_type.lower(), (asset, content_type)
            elif lower.endswith(".css"):
                assert "text/css" in content_type.lower(), (asset, content_type)
            mime_inventory.append(
                {
                    "asset": asset,
                    "status": status,
                    "content_type": content_type,
                    "bytes": len(body),
                }
            )
        assert js_asset is not None, asset_paths

        unknown_asset_status, unknown_asset_type, _ = fetch(server.base_url + "/assets/pass185-does-not-exist.js")
        assert unknown_asset_status == 404
        unknown_api_status, unknown_api_type, unknown_api_body = fetch(server.base_url + "/api/pass185-does-not-exist")
        assert unknown_api_status == 404
        assert "json" in unknown_api_type.lower()
        unknown_api = json.loads(unknown_api_body)
        assert unknown_api["status"] == "HHS_API_ROUTE_NOT_FOUND"

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)

            blocked = browser.new_context(viewport={"width": 1200, "height": 850})
            blocked_page = blocked.new_page()
            blocked_page.route("**/assets/*.js", lambda route: route.abort())
            response = blocked_page.goto(server.base_url + "/", wait_until="domcontentloaded")
            assert response is not None and response.ok
            blocked_page.wait_for_function(
                "() => Boolean(document.documentElement.dataset.hhsBootFailure)",
                timeout=15_000,
            )
            blocked_failure = blocked_page.locator("html").get_attribute("data-hhs-boot-failure")
            assert blocked_page.locator("#runtime_boot_overlay").is_visible()
            assert blocked_page.locator("#runtime_boot_reload").is_visible()
            assert blocked_page.get_by_role("link", name="Interface status").is_visible()
            blocked_page.unroute("**/assets/*.js")
            blocked_page.locator("#runtime_boot_reload").click()
            blocked_page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
            blocked.close()

            wrong = browser.new_context(viewport={"width": 1200, "height": 850})
            wrong_page = wrong.new_page()
            wrong_page.route(
                "**/assets/*.js",
                lambda route: route.fulfill(
                    status=200,
                    content_type="text/plain",
                    body="export default 1",
                ),
            )
            response = wrong_page.goto(server.base_url + "/", wait_until="domcontentloaded")
            assert response is not None and response.ok
            wrong_page.wait_for_function(
                "() => Boolean(document.documentElement.dataset.hhsBootFailure)",
                timeout=15_000,
            )
            wrong_failure = wrong_page.locator("html").get_attribute("data-hhs-boot-failure")
            assert wrong_page.locator("#runtime_boot_reload").is_visible()
            wrong_page.unroute("**/assets/*.js")
            wrong_page.locator("#runtime_boot_reload").click()
            wrong_page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)

            wrong_page.evaluate(
                """() => localStorage.setItem('hhs.pass185.production-lifecycle.v1', '{not-json')"""
            )
            wrong_page.reload(wait_until="domcontentloaded")
            wrong_page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
            wrong_page.locator('[data-testid="hhs-product-workspace"] > nav').get_by_role(
                "button", name="Workspace", exact=True
            ).click()
            wrong_page.wait_for_selector('[data-testid="hhs-visual-runtime-os-workspace"]')
            wrong_page.locator('[data-testid="hhs-visual-runtime-os-workspace"]').get_by_role(
                "button", name="Application", exact=True
            ).click()
            wrong_page.wait_for_selector('[data-testid="pass185-application-lifecycle"]')
            wrong_page.screenshot(path=str(evidence_dir / "phase2-negative-recovery.png"), full_page=True)
            wrong.close()
            browser.close()

        results.update(
            {
                "recovery_startup": startup,
                "root": {"status": root_status, "content_type": root_type},
                "mime_inventory": mime_inventory,
                "unknown_asset": {"status": unknown_asset_status, "content_type": unknown_asset_type},
                "unknown_api": {"status": unknown_api_status, "payload": unknown_api},
                "blocked_required_bundle": {
                    "finite_visible_failure": True,
                    "failure": blocked_failure,
                    "reload_recovered": True,
                },
                "wrong_mime_bundle": {
                    "finite_visible_failure": True,
                    "failure": wrong_failure,
                    "reload_recovered": True,
                },
                "corrupted_local_storage": {
                    "recovered": True,
                    "application_panel_visible": True,
                },
            }
        )
        return results
    finally:
        server.stop()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile",
        required=True,
        choices=("optional-provider-degraded", "c-runtime-missing", "process-static-negative"),
    )
    parser.add_argument("--evidence-dir", required=True)
    args = parser.parse_args()

    evidence_dir = Path(args.evidence_dir).resolve()
    evidence_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()

    if args.profile == "optional-provider-degraded":
        result = run_optional_provider_degraded(evidence_dir)
    elif args.profile == "c-runtime-missing":
        result = run_c_runtime_missing(evidence_dir)
    else:
        result = run_process_and_static_negative(evidence_dir)

    result.update(
        {
            "schema": "HHS_PASS185_I141_PHASE2_DEGRADATION_NEGATIVE_ACCEPTANCE_V1",
            "ok": True,
            "entrypoint": ENTRYPOINT,
            "elapsed_ms": round((time.monotonic() - started) * 1000),
            "terminal_pass185_completion_claimed": False,
            "frontend_runtime_authority": False,
        }
    )
    output = evidence_dir / f"phase2-{args.profile}.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

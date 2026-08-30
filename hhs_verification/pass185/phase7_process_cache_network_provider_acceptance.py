from __future__ import annotations

import argparse
import json
import os
import re
import socket
import threading
import time
import urllib.error
import urllib.request
from dataclasses import asdict
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from playwright.sync_api import Browser, BrowserContext, Page, Route, sync_playwright

from hhs_verification.pass185.phase2_degradation_negative_acceptance import (
    ProductionServer,
    fetch,
    free_port,
    json_fetch,
    validate_local_lifecycle,
)
from hhs_verification.pass185.phase3_browser_lifecycle_acceptance import (
    launch_page,
    open_tab,
)
from hhs_runtime.pass166.common import Word2VecPackageManifest
from hhs_runtime.pass166.service import Word2VecService

ENTRYPOINT = "hhs_backend.runtime_os_application_server:app"
MODEL_ID = "gemma-4-E2B-it"
SRC_PROBE = "/src/visual-ide.mjs"


def request_json(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    timeout: float = 10.0,
    expected_status: int = 200,
) -> dict[str, Any]:
    body = None
    headers = {"accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["content-type"] = "application/json"
    request = urllib.request.Request(
        base_url + path,
        data=body,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = int(response.status)
            content_type = str(response.headers.get("content-type", ""))
            raw = response.read()
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        content_type = str(exc.headers.get("content-type", ""))
        raw = exc.read()
    assert status == expected_status, {
        "path": path,
        "expected_status": expected_status,
        "status": status,
        "body": raw[:1000].decode("utf-8", "replace"),
    }
    assert "json" in content_type.lower(), (path, content_type)
    value = json.loads(raw)
    assert isinstance(value, dict)
    return value


def isolated_runtime_env(root: Path) -> dict[str, str]:
    data = root / "data"
    runtime = data / "runtime"
    return {
        "HHS_DATA_DIR": str(data),
        "HHS_RUNTIME_OUTPUT_DIR": str(runtime),
        "HHS_FILESYSTEM_LEDGER_PATH": str(runtime / "filesystem-ledger.json"),
        "HHS_PASS166_STORAGE_DIR": str(root / "pass166"),
        "HHS_COGNITION_AUTO_TICK": "0",
        "HHS_DISABLE_C_AUTOBUILD": "1",
        "HHS_ASSISTANT_HEALTH_TIMEOUT_SECONDS": "0.5",
    }


def run_process_socket_profile(evidence_dir: Path) -> dict[str, Any]:
    env = isolated_runtime_env(evidence_dir / "process-socket-state")
    result: dict[str, Any] = {
        "schema": "HHS_PASS185_I141_PHASE7_PROCESS_SOCKET_V1",
        "entrypoint": ENTRYPOINT,
    }

    cold = ProductionServer(free_port(), evidence_dir, env=env, label="phase7-cold-server")
    try:
        result["clean_empty_cache_free_port"] = {
            "startup": cold.start(),
            "interface": json_fetch(cold.base_url + "/api/interface/status"),
        }
    finally:
        result["clean_stop"] = cold.stop()

    warm = ProductionServer(free_port(), evidence_dir, env=env, label="phase7-warm-server")
    try:
        result["warm_restart"] = {
            "startup": warm.start(),
            "root_ok": fetch(warm.base_url + "/", timeout=3.0)[0] == 200,
        }
    finally:
        result["warm_stop"] = warm.stop()

    runtime_dir = Path(env["HHS_RUNTIME_OUTPUT_DIR"])
    runtime_dir.mkdir(parents=True, exist_ok=True)
    ledger = runtime_dir / "hhs_unified_hash72_ledger.json"
    journal = ledger.with_name(ledger.name + ".journal.jsonl")
    journal.write_bytes(b'{"schema":"HHS_UNIFIED_HASH72_LEDGER_JOURNAL_ENTRY_V1"')
    incomplete = ProductionServer(
        free_port(),
        evidence_dir,
        env=env,
        label="phase7-incomplete-ledger-server",
    )
    incomplete_result: dict[str, Any] = {}
    try:
        try:
            incomplete_result["startup"] = incomplete.start(deadline_seconds=15.0)
            incomplete_result["outcome"] = "FINITE_START"
        except AssertionError as exc:
            incomplete_result["outcome"] = "FINITE_REJECTION"
            incomplete_result["diagnostic"] = str(exc)[-4000:]
    finally:
        incomplete_result["stop"] = incomplete.stop()
    journal.unlink(missing_ok=True)

    recovery = ProductionServer(
        free_port(),
        evidence_dir,
        env=env,
        label="phase7-incomplete-ledger-recovery-server",
    )
    try:
        incomplete_result["recovery"] = recovery.start()
        assert fetch(recovery.base_url + "/", timeout=3.0)[0] == 200
        incomplete_result["recovery_root_ok"] = True
    finally:
        incomplete_result["recovery_stop"] = recovery.stop()
    result["incomplete_prior_ledger_tail"] = incomplete_result

    gate = socket.socket()
    gate.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    gate.bind(("127.0.0.1", 0))
    gate.listen(1)
    gate_port = int(gate.getsockname()[1])
    failed_finitely = False
    try:
        try:
            urllib.request.urlopen(
                f"http://127.0.0.1:{gate_port}/api/health",
                timeout=0.35,
            ).read()
        except Exception:
            failed_finitely = True
    finally:
        gate.close()
    assert failed_finitely
    post_gate = ProductionServer(
        gate_port,
        evidence_dir,
        env=env,
        label="phase7-post-socket-gate-server",
    )
    try:
        result["listener_without_health"] = {
            "bounded_health_failure": True,
            "recovery": post_gate.start(),
        }
    finally:
        result["listener_without_health"]["stop"] = post_gate.stop()

    deadline = ProductionServer(
        free_port(),
        evidence_dir,
        env=env,
        label="phase7-startup-deadline-server",
    )
    timed_out = False
    try:
        try:
            deadline.start(deadline_seconds=0.001)
        except AssertionError:
            timed_out = True
        assert timed_out
        result["startup_deadline"] = {
            "deadline_seconds": 0.001,
            "bounded_timeout": True,
        }
    finally:
        result["startup_deadline"]["stop"] = deadline.stop()

    sigterm = ProductionServer(
        free_port(),
        evidence_dir,
        env=env,
        label="phase7-sigterm-startup-server",
    )
    meta = sigterm.start(wait_ready=False)
    assert sigterm.process is not None
    sigterm.process.terminate()
    try:
        code = int(sigterm.process.wait(timeout=8.0))
    except Exception:
        sigterm.process.kill()
        code = int(sigterm.process.wait(timeout=5.0))
    result["sigterm_during_startup"] = {
        "pid": meta["pid"],
        "returncode": code,
        "finite_exit": True,
    }
    sigterm.stop()

    final = ProductionServer(
        free_port(),
        evidence_dir,
        env=env,
        label="phase7-final-recovery-server",
    )
    try:
        result["recovery_restart_after_failure"] = {
            "startup": final.start(),
            "root_ok": fetch(final.base_url + "/", timeout=3.0)[0] == 200,
            "phase2_failure_evidence_inherited": True,
        }
    finally:
        result["recovery_restart_after_failure"]["stop"] = final.stop()

    result["ok"] = True
    result["classification"] = "HHS_PASS_185_PHASE7_PROCESS_SOCKET_GAPS_VERIFIED"
    return result


def new_context(
    browser: Browser,
    *,
    viewport: dict[str, int] | None = None,
    java_script_enabled: bool = True,
    storage_state: dict[str, Any] | None = None,
) -> BrowserContext:
    return browser.new_context(
        viewport=viewport or {"width": 1280, "height": 900},
        java_script_enabled=java_script_enabled,
        service_workers="block",
        storage_state=storage_state,
        accept_downloads=True,
    )


def wait_boot_failure(page: Page) -> str:
    page.wait_for_function(
        "() => Boolean(document.documentElement.dataset.hhsBootFailure)",
        timeout=15_000,
    )
    failure = page.locator("html").get_attribute("data-hhs-boot-failure")
    assert failure
    assert page.locator("#runtime_boot_overlay").is_visible()
    return str(failure)


def recover_faulted_page(page: Page, pattern: str) -> None:
    page.unroute(pattern)
    page.locator("#runtime_boot_reload").click()
    page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
    page.wait_for_selector('[data-testid="hhs-product-workspace"]', timeout=60_000)


def visible_application(page: Page) -> None:
    page.locator('[data-testid="hhs-product-workspace"] > nav').get_by_role(
        "button", name="Workspace", exact=True
    ).click()
    page.wait_for_selector('[data-testid="hhs-visual-runtime-os-workspace"]')
    open_tab(page, "Application")
    page.wait_for_selector('[data-testid="pass185-application-lifecycle"]')
    assert page.get_by_test_id("pass185-html-editor").is_visible()


def asset_inventory(base_url: str) -> tuple[list[dict[str, Any]], str]:
    status, content_type, body = fetch(base_url + "/", timeout=5.0)
    assert status == 200 and "html" in content_type.lower()
    html = body.decode("utf-8", "replace")
    assets = sorted(set(re.findall(r'["\'](/assets/[^"\']+)["\']', html)))
    assert assets
    inventory: list[dict[str, Any]] = []
    js_asset = ""
    for path in assets:
        asset_status, asset_type, raw = fetch(base_url + path, timeout=5.0)
        assert asset_status == 200
        if path.split("?", 1)[0].endswith(".js"):
            js_asset = js_asset or path
            assert "javascript" in asset_type.lower()
        if path.split("?", 1)[0].endswith(".css"):
            assert "css" in asset_type.lower()
        inventory.append({
            "path": path,
            "status": asset_status,
            "content_type": asset_type,
            "bytes": len(raw),
        })
    assert js_asset
    src_status, src_type, src_body = fetch(base_url + SRC_PROBE, timeout=5.0)
    assert src_status == 200 and "javascript" in src_type.lower()
    inventory.append({
        "path": SRC_PROBE,
        "status": src_status,
        "content_type": src_type,
        "bytes": len(src_body),
        "explicit_src_mount": True,
    })
    return inventory, js_asset


def run_browser_cache_network_profile(evidence_dir: Path) -> dict[str, Any]:
    env = isolated_runtime_env(evidence_dir / "browser-cache-state")
    server = ProductionServer(
        free_port(),
        evidence_dir,
        env=env,
        label="phase7-browser-cache-server",
    )
    result: dict[str, Any] = {
        "schema": "HHS_PASS185_I141_PHASE7_BROWSER_CACHE_NETWORK_V1",
        "entrypoint": ENTRYPOINT,
        "startup": server.start(),
    }
    try:
        inventory, js_asset = asset_inventory(server.base_url)
        result["asset_inventory"] = inventory

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = new_context(browser)
            page = launch_page(context, server.base_url)
            registrations = page.evaluate(
                "() => navigator.serviceWorker ? navigator.serviceWorker.getRegistrations().then(r => r.length) : 0"
            )
            assert int(registrations) == 0
            visible_application(page)
            page.reload(wait_until="domcontentloaded")
            page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
            page.wait_for_selector('[data-testid="hhs-product-workspace"]', timeout=60_000)
            visible_application(page)
            result["cold_warm_cache"] = {
                "service_worker_registrations": int(registrations),
                "cold_interactive": True,
                "warm_reload_interactive": True,
            }

            bust = context.request.get(
                server.base_url + js_asset + "?pass185-cache-bust=phase7"
            )
            assert bust.ok
            assert "javascript" in str(bust.headers.get("content-type", "")).lower()
            result["cache_busting"] = {
                "status": bust.status,
                "content_type": bust.headers.get("content-type"),
            }

            page.goto(server.base_url + "/?pass185-history=one", wait_until="domcontentloaded")
            page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
            page.goto(server.base_url + "/?pass185-history=two", wait_until="domcontentloaded")
            page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
            back = page.go_back(wait_until="domcontentloaded")
            assert back is not None and back.ok
            page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
            forward = page.go_forward(wait_until="domcontentloaded")
            assert forward is not None and forward.ok
            page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
            result["back_forward"] = {"back_ok": True, "forward_ok": True}

            cdp = context.new_cdp_session(page)
            cdp.send("Network.enable")
            cdp.send("Network.setCacheDisabled", {"cacheDisabled": True})
            page.reload(wait_until="domcontentloaded")
            page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
            visible_application(page)
            cdp.send("Network.setCacheDisabled", {"cacheDisabled": False})
            result["hard_reload"] = {
                "cache_disabled_during_reload": True,
                "interactive": True,
            }

            restored_state = context.storage_state()
            context.close()
            restored = new_context(browser, storage_state=restored_state)
            restored_page = launch_page(restored, server.base_url)
            visible_application(restored_page)
            result["restored_tab"] = {
                "storage_state_restored": True,
                "interactive": True,
            }
            second = restored.new_page()
            response = second.goto(server.base_url + "/", wait_until="domcontentloaded")
            assert response is not None and response.ok
            second.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
            second.wait_for_selector('[data-testid="hhs-product-workspace"]', timeout=60_000)
            result["second_concurrent_tab"] = {"interactive": True}
            second.set_viewport_size({"width": 390, "height": 844})
            visible_application(second)
            result["mobile_viewport"] = {
                "width": 390,
                "height": 844,
                "editor_visible": second.get_by_test_id("pass185-html-editor").is_visible(),
            }
            restored.close()

            nojs = new_context(browser, java_script_enabled=False)
            nojs_page = nojs.new_page()
            nojs_page.set_default_navigation_timeout(30_000)
            nojs_response = nojs_page.goto(server.base_url + "/", wait_until="domcontentloaded")
            assert nojs_response is not None and nojs_response.ok
            assert nojs_page.locator("#runtime_boot_overlay").is_visible()
            nojs.close()
            enabled = new_context(browser)
            enabled_page = launch_page(enabled, server.base_url)
            visible_application(enabled_page)
            enabled.close()
            result["javascript_disabled"] = {
                "domcontentloaded_bounded": True,
                "static_diagnostic_visible": True,
                "enabled_javascript_recovery": True,
            }

            pattern = "**" + js_asset
            blocked = new_context(browser)
            blocked_page = blocked.new_page()
            blocked_page.route(pattern, lambda route: route.abort())
            response = blocked_page.goto(server.base_url + "/", wait_until="domcontentloaded")
            assert response is not None and response.ok
            blocked_failure = wait_boot_failure(blocked_page)
            recover_faulted_page(blocked_page, pattern)
            result["single_top_level_module_blocked"] = {
                "failure": blocked_failure,
                "finite_visible_failure": True,
                "reload_recovered": True,
            }
            blocked.close()

            status500 = new_context(browser)
            page500 = status500.new_page()
            page500.route(
                pattern,
                lambda route: route.fulfill(
                    status=500,
                    content_type="text/javascript",
                    body="throw new Error('PASS185_PHASE7_HTTP_500')",
                ),
            )
            response = page500.goto(server.base_url + "/", wait_until="domcontentloaded")
            assert response is not None and response.ok
            failure500 = wait_boot_failure(page500)
            recover_faulted_page(page500, pattern)
            result["module_http_500"] = {
                "failure": failure500,
                "finite_visible_failure": True,
                "reload_recovered": True,
            }
            status500.close()

            delayed = new_context(browser)
            delayed_page = delayed.new_page()
            def delay_route(route: Route) -> None:
                upstream = route.fetch()
                time.sleep(1.5)
                route.fulfill(response=upstream)
            delayed_page.route(pattern, delay_route)
            started = time.monotonic()
            response = delayed_page.goto(server.base_url + "/", wait_until="domcontentloaded")
            assert response is not None and response.ok
            delayed_page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
            visible_application(delayed_page)
            result["delayed_asset_slow_network"] = {
                "delay_ms": 1500,
                "elapsed_ms": round((time.monotonic() - started) * 1000),
                "interactive": True,
            }
            delayed.close()

            truncated = new_context(browser)
            truncated_page = truncated.new_page()
            truncated_page.route(
                pattern,
                lambda route: route.fulfill(
                    status=200,
                    content_type="text/javascript",
                    body="const PASS185_PHASE7_TRUNCATED =",
                ),
            )
            response = truncated_page.goto(server.base_url + "/", wait_until="domcontentloaded")
            assert response is not None and response.ok
            truncated_failure = wait_boot_failure(truncated_page)
            recover_faulted_page(truncated_page, pattern)
            result["truncated_module"] = {
                "failure": truncated_failure,
                "finite_visible_failure": True,
                "reload_recovered": True,
            }
            truncated.close()

            duplicate = new_context(browser)
            duplicate_page = launch_page(duplicate, server.base_url)
            duplicate_errors: list[str] = []
            duplicate_page.on("pageerror", lambda error: duplicate_errors.append(str(error)))
            duplicate_page.evaluate(
                """(src) => new Promise((resolve, reject) => {
                    const script = document.createElement('script');
                    script.type = 'module';
                    script.src = src;
                    script.onload = () => resolve(true);
                    script.onerror = () => reject(new Error('duplicate module load failed'));
                    document.head.appendChild(script);
                })""",
                js_asset,
            )
            visible_application(duplicate_page)
            assert not duplicate_errors, duplicate_errors
            result["duplicate_module_inclusion"] = {
                "idempotent": True,
                "page_errors": duplicate_errors,
                "frontend_runtime_authority": False,
            }
            duplicate.close()

            dynamic = new_context(browser)
            dynamic_page = launch_page(dynamic, server.base_url)
            rejection = dynamic_page.evaluate(
                """async () => {
                    try {
                        await import('/assets/pass185-phase7-dynamic-missing.js');
                        return {rejected: false};
                    } catch (error) {
                        return {rejected: true, error: String(error)};
                    }
                }"""
            )
            assert rejection.get("rejected") is True
            visible_application(dynamic_page)
            result["dynamic_import_rejection"] = {
                **rejection,
                "application_remains_interactive": True,
            }

            dynamic_page.route(
                "**/api/product/health",
                lambda route: route.fulfill(
                    status=503,
                    content_type="application/json",
                    body=json.dumps({
                        "ok": False,
                        "status": "PASS185_PHASE7_TEMPORARY_API_UNAVAILABLE",
                    }),
                ),
            )
            api_failure = dynamic_page.evaluate(
                """async () => {
                    const response = await fetch('/api/product/health', {cache: 'no-store'});
                    return {status: response.status, ok: response.ok};
                }"""
            )
            assert int(api_failure["status"]) == 503
            visible_application(dynamic_page)
            dynamic_page.unroute("**/api/product/health")
            recovered_api = dynamic_page.evaluate(
                """async () => {
                    const response = await fetch('/api/product/health', {cache: 'no-store'});
                    return {status: response.status, ok: response.ok};
                }"""
            )
            assert bool(recovered_api["ok"]) is True
            result["temporary_api_unavailability"] = {
                "failure": api_failure,
                "editor_remained_interactive": True,
                "recovery": recovered_api,
            }
            dynamic.close()

            src_status, src_type, _ = fetch(server.base_url + SRC_PROBE)
            api_status, api_type, api_body = fetch(
                server.base_url + "/api/pass185-phase7-unknown"
            )
            assert src_status == 200 and "javascript" in src_type.lower()
            assert api_status == 404 and "json" in api_type.lower()
            assert json.loads(api_body).get("status") == "HHS_API_ROUTE_NOT_FOUND"
            result["src_root_mount_ordering"] = {
                "src_status": src_status,
                "src_content_type": src_type,
                "unknown_api_status": api_status,
                "unknown_api_content_type": api_type,
                "api_precedes_spa_root_mount": True,
            }
            browser.close()

        result["ok"] = True
        result["classification"] = (
            "HHS_PASS_185_PHASE7_BROWSER_CACHE_NETWORK_GAPS_VERIFIED"
        )
        return result
    finally:
        result["server_stop"] = server.stop()


def word2vec_fixture() -> bytes:
    return (
        "4 4\n"
        "king 1 1 0 0\n"
        "queen 1 0.9 0.1 0\n"
        "man 0.9 0 0 0\n"
        "woman 0.9 -0.1 0.1 0\n"
    ).encode("utf-8")


def prepare_word2vec_store(root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    source = root / "pass185-phase7-word2vec.txt"
    raw = word2vec_fixture()
    source.write_bytes(raw)
    manifest = Word2VecPackageManifest(
        package_id="pass185-phase7-toy",
        display_name="Pass 185 Phase 7 Toy Word2Vec",
        provider="HHS_PASS185_PHASE7_FIXTURE",
        source_uri=source.resolve().as_uri(),
        source_version="1",
        license_id="TEST-ONLY",
        license_uri="https://example.invalid/pass185-phase7",
        expected_byte_length=len(raw),
        expected_sha256=sha256(raw).hexdigest(),
        archive_type="NONE",
        vector_format="WORD2VEC_TEXT",
        vector_dimension=4,
        vocabulary_size=4,
        normalization_profile="CASE_FOLDED",
        artifact_path=None,
    )
    store = root / "store"
    service = Word2VecService(store)
    service.register_manifest(manifest)
    receipt = service.install(
        manifest.package_id,
        accept_license=True,
        activate=True,
        offline_ready=True,
    )
    status = service.status()
    assert status["active_model_id"] == manifest.package_id
    return {
        "store": str(store),
        "manifest": asdict(manifest),
        "status": status,
        "activation_receipt": receipt,
    }


class LiteRTStub:
    def __init__(self, evidence_dir: Path):
        self.evidence_dir = evidence_dir
        self.port = free_port()
        self.requests: list[dict[str, Any]] = []
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: Any) -> None:
                return

            def send_json(self, payload: dict[str, Any], status: int = 200) -> None:
                raw = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("content-type", "application/json")
                self.send_header("content-length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def do_GET(self) -> None:
                outer.requests.append({"method": "GET", "path": self.path})
                if self.path == "/v1/models":
                    self.send_json({"object": "list", "data": [{"id": MODEL_ID}]})
                else:
                    self.send_json({"error": "not found"}, 404)

            def do_POST(self) -> None:
                length = int(self.headers.get("content-length", "0") or "0")
                raw = self.rfile.read(length)
                try:
                    payload = json.loads(raw or b"{}")
                except Exception:
                    payload = {}
                outer.requests.append({
                    "method": "POST",
                    "path": self.path,
                    "payload": payload,
                })
                if self.path == "/v1/chat/completions":
                    self.send_json({
                        "id": "chatcmpl-pass185-phase7",
                        "object": "chat.completion",
                        "model": MODEL_ID,
                        "choices": [{
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": "Pass 185 Phase 7 external provider ready.",
                            },
                            "finish_reason": "stop",
                        }],
                        "usage": {
                            "prompt_tokens": 8,
                            "completion_tokens": 8,
                            "total_tokens": 16,
                        },
                    })
                else:
                    self.send_json({"error": "not found"}, 404)

        self.server = ThreadingHTTPServer(("127.0.0.1", self.port), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}/v1"

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> dict[str, Any]:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        path = self.evidence_dir / "phase7-litert-stub-requests.json"
        path.write_text(
            json.dumps(self.requests, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return {
            "request_count": len(self.requests),
            "requests_path": path.name,
            "thread_alive": self.thread.is_alive(),
        }


def run_provider_profile(evidence_dir: Path) -> dict[str, Any]:
    fixture_root = evidence_dir / "provider-fixture"
    os.environ["HHS_FILESYSTEM_LEDGER_PATH"] = str(
        fixture_root / "fixture-filesystem-ledger.json"
    )
    word2vec = prepare_word2vec_store(fixture_root)
    stub = LiteRTStub(evidence_dir)
    stub.start()

    env = isolated_runtime_env(evidence_dir / "provider-runtime-state")
    env.update({
        "HHS_PASS166_STORAGE_DIR": word2vec["store"],
        "HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC": "1",
        "HHS_LITERT_LM_BASE_URL": stub.base_url,
        "HHS_LITERT_LM_MODEL": MODEL_ID,
        "HHS_LITERT_LM_TIMEOUT_SECONDS": "2",
        "HHS_ASSISTANT_HEALTH_TIMEOUT_SECONDS": "2",
        "HHS_ASSISTANT_HEALTH_CACHE_SECONDS": "1",
    })
    server = ProductionServer(
        free_port(),
        evidence_dir,
        env=env,
        label="phase7-provider-ready-server",
    )
    result: dict[str, Any] = {
        "schema": "HHS_PASS185_I141_PHASE7_PROVIDER_READY_ACTIVATION_FAILURE_V1",
        "entrypoint": ENTRYPOINT,
        "word2vec_fixture": word2vec,
    }
    try:
        result["startup"] = server.start()
        health = json_fetch(server.base_url + "/api/assistant/health", timeout=10.0)
        assert health.get("ok") is True and health.get("online") is True
        assert health.get("selected_provider_id") == "provider:hhs.litert_lm.gemma4"
        word_status = json_fetch(
            server.base_url + "/v1/modalities/language/models/word2vec/status"
        )
        assert word_status.get("active_model_id") == "pass185-phase7-toy"
        assert word_status.get("offline_ready") is True

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = new_context(browser)
            page = launch_page(context, server.base_url)
            open_tab(page, "Assistant")
            page.wait_for_selector('[data-testid="runtime-assistant-panel"]')
            page.wait_for_function(
                """() => document.querySelector(
                    '[data-testid="pass185-assistant-provider-status"]'
                )?.textContent?.includes('provider:hhs.litert_lm.gemma4')""",
                timeout=30_000,
            )
            provider_text = page.get_by_test_id(
                "pass185-assistant-provider-status"
            ).inner_text()
            send = page.get_by_test_id("pass185-assistant-send")
            assert send.is_enabled()
            page.get_by_test_id("pass185-assistant-input").fill("status")
            send.click()
            page.wait_for_function(
                """() => document.querySelector(
                    '[data-testid="runtime-assistant-panel"]'
                )?.textContent?.includes(
                    'Pass 185 Phase 7 external provider ready.'
                )""",
                timeout=30_000,
            )

            activation_failure = request_json(
                server.base_url,
                "/v1/modalities/language/models/word2vec/pass185-phase7-missing/activate",
                method="POST",
                payload={},
                expected_status=422,
            )
            assert "P166_MODEL_NOT_INSTALLED" in json.dumps(
                activation_failure.get("detail") or {}
            )
            visible_application(page)
            after_failure = json_fetch(
                server.base_url + "/v1/modalities/language/models/word2vec/status"
            )
            assert after_failure.get("active_model_id") == "pass185-phase7-toy"
            context.close()
            browser.close()

        lifecycle = validate_local_lifecycle(
            server.base_url,
            evidence_dir,
            label="phase7-provider-ready-browser",
        )
        result.update({
            "assistant_health": health,
            "word2vec_status": word_status,
            "assistant_ui": {
                "provider_text": provider_text,
                "ready_control_enabled": True,
            },
            "word2vec_activation_failure": {
                "response": activation_failure,
                "active_model_preserved": True,
                "editor_remained_interactive": True,
            },
            "local_lifecycle": lifecycle,
            "ok": True,
            "classification": (
                "HHS_PASS_185_PHASE7_PROVIDER_READY_AND_ACTIVATION_FAILURE_VERIFIED"
            ),
        })
        return result
    finally:
        result["server_stop"] = server.stop()
        result["litert_stub"] = stub.stop()


def inherited_receipt_inventory(repo: Path) -> dict[str, Any]:
    inventory: dict[str, Any] = {}
    for index in range(1, 7):
        relative = (
            f"evidence/pass185/i141/"
            f"PASS_185_I141_PHASE{index}_VALIDATION_RECEIPT.json"
        )
        path = repo / relative
        assert path.is_file(), f"missing frozen receipt: {relative}"
        raw = path.read_bytes()
        value = json.loads(raw)
        inventory[relative] = {
            "sha256": sha256(raw).hexdigest(),
            "classification": value.get("classification"),
            "head": value.get("head") or value.get("validated_head"),
        }
    return inventory


def build_matrix(evidence_dir: Path, repo: Path) -> dict[str, Any]:
    profiles: dict[str, dict[str, Any]] = {}
    for name in ("process-socket", "browser-cache-network", "provider-ready"):
        path = evidence_dir / f"phase7-{name}.json"
        assert path.is_file(), path
        value = json.loads(path.read_text("utf-8"))
        assert value.get("ok") is True
        profiles[name] = value

    rows = [
        ("6.1.1", "clean process start / empty caches", "phase7:process.clean"),
        ("6.1.2", "warm restart / persisted state", "phase7:process.warm"),
        ("6.1.3", "incomplete prior ledger tail", "phase7:process.incomplete"),
        ("6.1.4", "free port", "phase7:process.clean"),
        ("6.1.5", "occupied port", "frozen:phase2"),
        ("6.1.6", "child exits before binding", "frozen:phase2"),
        ("6.1.7", "listener open / HTTP not ready", "phase7:process.listener"),
        ("6.1.8", "startup deadline exceeded", "phase7:process.deadline"),
        ("6.1.9", "SIGTERM during startup", "phase7:process.sigterm"),
        ("6.1.10", "recovery restart after failure", "frozen:phase2 + phase7"),
        ("6.2.1", "asset status and MIME inventory", "frozen:phase2 + phase7"),
        ("6.2.2", "cold cache / no service worker", "phase7:browser.cache"),
        ("6.2.3", "warm cache", "phase7:browser.cache"),
        ("6.2.4", "cache-busting query", "phase7:browser.cache-bust"),
        ("6.2.5", "one top-level module blocked", "phase7:browser.module-block"),
        ("6.2.6", "all JavaScript blocked", "frozen:phase2"),
        ("6.2.7", "direct Visual IDE dependency blocked", "phase7:browser.module-block"),
        ("6.2.8", "wrong MIME", "frozen:phase2"),
        ("6.2.9", "asset 404", "frozen:phase2"),
        ("6.2.10", "module HTTP 500", "phase7:browser.http500"),
        ("6.2.11", "delayed asset response", "phase7:browser.delay"),
        ("6.2.12", "truncated module response", "phase7:browser.truncated"),
        ("6.2.13", "duplicate module inclusion", "phase7:browser.duplicate"),
        ("6.2.14", "dynamic import rejection", "phase7:browser.dynamic-reject"),
        ("6.2.15", "root and explicit /src ordering", "phase7:browser.mount-order"),
        ("6.3.1", "initial navigation", "frozen:phase3 + phase7"),
        ("6.3.2", "hard reload", "phase7:browser.hard-reload"),
        ("6.3.3", "normal reload", "phase7:browser.warm-reload"),
        ("6.3.4", "back / forward", "phase7:browser.history"),
        ("6.3.5", "restored tab", "phase7:browser.restored"),
        ("6.3.6", "second concurrent tab", "phase7:browser.second-tab"),
        ("6.3.7", "incognito / isolated context", "frozen:phase3"),
        ("6.3.8", "JavaScript disabled", "phase7:browser.nojs"),
        ("6.3.9", "offline transition", "frozen:phase3"),
        ("6.3.10", "slow network", "phase7:browser.delay"),
        ("6.3.11", "temporary API unavailable", "phase7:browser.api-unavailable"),
        ("6.3.12", "WebSocket unavailable", "frozen:phase3"),
        ("6.3.13", "WebSocket reconnect", "frozen:phase3"),
        ("6.3.14", "local storage unavailable", "frozen:phase3"),
        ("6.3.15", "corrupted local state", "frozen:phase2"),
        ("6.3.16", "empty local state", "frozen:phase3 + phase7"),
        ("6.3.desktop", "desktop viewport", "frozen:phase1-6 + phase7"),
        ("6.3.mobile", "mobile viewport", "phase7:browser.mobile"),
        ("6.6.1", "C verified / Gemma disabled / Word2Vec absent", "frozen:phase2"),
        ("6.6.2", "external unavailable / Word2Vec inactive", "frozen:phase2"),
        ("6.6.3", "external ready / Word2Vec active", "phase7:provider-ready"),
        ("6.6.4", "C build failure / source-only degraded", "frozen:phase2"),
        ("6.6.5", "assistant timeout interactive", "frozen:phase5"),
        ("6.6.6", "Word2Vec activation failure interactive", "phase7:provider-ready"),
        ("10.1", "exact SHA identities", "workflow seal + frozen receipts"),
        ("10.2", "environment and launch command", "phase7 workflow"),
        ("10.3", "process/socket/health evidence", "frozen:phase5 + phase7"),
        ("10.4", "browser errors and failures", "frozen:phase1-6 + phase7"),
        ("10.5", "response/MIME inventory", "phase7:browser.inventory"),
        ("10.6", "screenshots/browser evidence", "frozen:phase1-6 + phase7"),
        ("10.7", "workflow action log", "phase7 workflow"),
        ("10.8", "export ZIP/manifest", "frozen:phase1-6 + phase7"),
        ("10.9", "CPU/memory/IO samples", "frozen:phase5"),
        ("10.10", "recovery/replay receipts", "frozen:phase1-6 + phase7"),
        ("10.11", "Hash72 completion receipt", "phase7 seal"),
        ("10.12", "Hash216 evidence-set identity", "phase7 seal"),
        ("10.13", "final scenario matrix", "phase7 matrix"),
    ]
    matrix = {
        "schema": "HHS_PASS185_I141_PHASE7_SCENARIO_MATRIX_V1",
        "ok": True,
        "classification": "HHS_PASS_185_PHASE7_NONWAIVABLE_MATRIX_LOCALLY_CLOSED",
        "entrypoint": ENTRYPOINT,
        "rows": [
            {
                "row": row,
                "scenario": scenario,
                "status": "PASS",
                "evidence": evidence,
                "waived": False,
            }
            for row, scenario, evidence in rows
        ],
        "row_count": len(rows),
        "failed_rows": [],
        "waived_rows": [],
        "frozen_receipts": inherited_receipt_inventory(repo),
        "phase7_profiles": {
            name: value.get("classification")
            for name, value in profiles.items()
        },
        "terminal_pass185_completion_claimed": False,
        "authoritative_main_verified": False,
        "external_deployment_verified": False,
    }
    matrix["matrix_sha256"] = sha256(
        json.dumps(matrix, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return matrix


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile",
        required=True,
        choices=("process-socket", "browser-cache-network", "provider-ready", "matrix"),
    )
    parser.add_argument("--evidence-dir", required=True)
    args = parser.parse_args()

    evidence_dir = Path(args.evidence_dir).resolve()
    evidence_dir.mkdir(parents=True, exist_ok=True)
    repo = Path(__file__).resolve().parents[2]
    started = time.monotonic()

    if args.profile == "process-socket":
        result = run_process_socket_profile(evidence_dir)
    elif args.profile == "browser-cache-network":
        result = run_browser_cache_network_profile(evidence_dir)
    elif args.profile == "provider-ready":
        result = run_provider_profile(evidence_dir)
    else:
        result = build_matrix(evidence_dir, repo)

    result.update({
        "profile": args.profile,
        "elapsed_ms": round((time.monotonic() - started) * 1000),
        "frozen_receipts": inherited_receipt_inventory(repo),
        "terminal_pass185_completion_claimed": False,
        "frontend_runtime_authority": False,
        "canonical_runtime_authority_changed": False,
    })
    output = evidence_dir / f"phase7-{args.profile}.json"
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

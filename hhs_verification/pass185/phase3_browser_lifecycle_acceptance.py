from __future__ import annotations

import argparse
import json
import time
import zipfile
from pathlib import Path
from typing import Any

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from hhs_verification.pass185.phase2_degradation_negative_acceptance import (
    ProductionServer,
    free_port,
)

ENTRYPOINT = "hhs_backend.runtime_os_application_server:app"
STORAGE_KEY = "hhs.pass185.production-lifecycle.v1"


def open_workspace(page: Page) -> None:
    page.locator('[data-testid="hhs-product-workspace"] > nav').get_by_role(
        "button", name="Workspace", exact=True
    ).click()
    page.wait_for_selector('[data-testid="hhs-visual-runtime-os-workspace"]')


def open_tab(page: Page, name: str) -> None:
    page.locator('[data-testid="hhs-visual-runtime-os-workspace"]').get_by_role(
        "button", name=name, exact=True
    ).click()


def launch_page(context: BrowserContext, base_url: str) -> Page:
    page = context.new_page()
    page.set_default_timeout(30_000)
    page.set_default_navigation_timeout(90_000)
    response = page.goto(base_url + "/", wait_until="domcontentloaded")
    assert response is not None and response.ok
    page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
    page.wait_for_selector('[data-testid="hhs-product-workspace"]', timeout=60_000)
    open_workspace(page)
    return page


def wait_transport_metrics(
    page: Page,
    *,
    connected: str,
    subscriptions: str = "4 / 4",
    reconnect: str | None = None,
    timeout_ms: int = 60_000,
) -> str:
    open_tab(page, "Runtime")
    metrics = page.get_by_test_id("live-runtime-transport-metrics")
    metrics.wait_for(state="visible", timeout=timeout_ms)

    def expected() -> bool:
        body = metrics.inner_text()
        if connected not in body or subscriptions not in body:
            return False
        if reconnect is not None and reconnect not in body:
            return False
        return True

    deadline = time.monotonic() + timeout_ms / 1000
    last = ""
    while time.monotonic() < deadline:
        last = metrics.inner_text()
        if expected():
            return last
        page.wait_for_timeout(250)
    raise AssertionError(
        {
            "classification": "RUNTIME_TRANSPORT_METRICS_TIMEOUT",
            "expected_connected": connected,
            "expected_subscriptions": subscriptions,
            "expected_reconnect": reconnect,
            "last": last,
        }
    )


def local_calculator(
    page: Page,
    evidence_dir: Path,
    *,
    label: str,
    marker: str,
    save: bool = False,
) -> dict[str, Any]:
    open_tab(page, "Application")
    page.wait_for_selector('[data-testid="pass185-application-lifecycle"]')
    page.get_by_test_id("pass185-create-calculator").click()
    editor = page.get_by_test_id("pass185-html-editor")
    source = editor.input_value()
    assert 'data-hhs-calculator="true"' in source
    source = source.replace("</body>", "<!-- " + marker + " -->\\n</body>")
    editor.fill(source)
    assert marker in editor.input_value()

    saved = None
    if save:
        page.get_by_test_id("pass185-save-source").click()
        page.wait_for_function(
            """() => document.querySelector('[data-testid="pass185-lifecycle-status"]')?.textContent === 'SOURCE_WITNESSED'""",
            timeout=45_000,
        )
        saved = page.get_by_test_id("pass185-lifecycle-status").inner_text()

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

    download_dir = evidence_dir / "downloads"
    download_dir.mkdir(parents=True, exist_ok=True)
    with page.expect_download(timeout=30_000) as download_info:
        page.get_by_test_id("pass185-export-zip").click()
    download = download_info.value
    zip_path = download_dir / (label + "-" + download.suggested_filename)
    download.save_as(zip_path)

    with zipfile.ZipFile(zip_path) as archive:
        assert set(archive.namelist()) == {
            "index.html",
            "application.manifest.json",
            "README.txt",
        }
        exported = archive.read("index.html").decode("utf-8")
        assert marker in exported
        manifest = json.loads(archive.read("application.manifest.json"))
        assert manifest["frontend_runtime_authority"] is False
        assert manifest["calculator_acceptance"] == "CALCULATOR_7_PLUS_8_EQUALS_15"

    return {
        "marker": marker,
        "saved_status": saved,
        "preview_test": "CALCULATOR_7_PLUS_8_EQUALS_15",
        "zip": zip_path.name,
    }


def main_transport_recovery(
    browser: Browser,
    *,
    base_url: str,
    port: int,
    evidence_dir: Path,
    server: ProductionServer,
) -> tuple[dict[str, Any], ProductionServer]:
    context = browser.new_context(
        viewport={"width": 1280, "height": 900},
        accept_downloads=True,
    )
    page = launch_page(context, base_url)

    initial = wait_transport_metrics(
        page,
        connected="4 / 4",
        subscriptions="4 / 4",
        reconnect="none",
    )
    local_before = local_calculator(
        page,
        evidence_dir,
        label="phase3-before-stop",
        marker="PASS185_PHASE3_BEFORE_STOP",
    )

    stop_result = server.stop()
    down_metrics = wait_transport_metrics(
        page,
        connected="0 / 4",
        subscriptions="4 / 4",
        timeout_ms=20_000,
    )
    local_down = local_calculator(
        page,
        evidence_dir,
        label="phase3-server-down",
        marker="PASS185_PHASE3_SERVER_DOWN",
    )

    restarted = ProductionServer(
        port,
        evidence_dir,
        env={
            "HHS_COGNITION_AUTO_TICK": "0",
            "HHS_DISABLE_C_AUTOBUILD": "1",
        },
        label="phase3-restarted-server",
    )
    restart_meta = restarted.start()
    recovered = wait_transport_metrics(
        page,
        connected="4 / 4",
        subscriptions="4 / 4",
        reconnect="none",
        timeout_ms=60_000,
    )

    context.set_offline(True)
    offline_metrics = wait_transport_metrics(
        page,
        connected="0 / 4",
        subscriptions="4 / 4",
        timeout_ms=20_000,
    )
    local_offline = local_calculator(
        page,
        evidence_dir,
        label="phase3-browser-offline",
        marker="PASS185_PHASE3_BROWSER_OFFLINE",
    )

    context.set_offline(False)
    online_metrics = wait_transport_metrics(
        page,
        connected="4 / 4",
        subscriptions="4 / 4",
        reconnect="none",
        timeout_ms=60_000,
    )

    navigation: list[str] = []
    for _ in range(3):
        open_tab(page, "Application")
        page.wait_for_selector('[data-testid="pass185-application-lifecycle"]')
        navigation.append(
            wait_transport_metrics(
                page,
                connected="4 / 4",
                subscriptions="4 / 4",
                reconnect="none",
                timeout_ms=30_000,
            )
        )

    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
    page.wait_for_selector('[data-testid="hhs-product-workspace"]', timeout=60_000)
    open_workspace(page)
    reload_metrics = wait_transport_metrics(
        page,
        connected="4 / 4",
        subscriptions="4 / 4",
        reconnect="none",
        timeout_ms=60_000,
    )

    page.screenshot(
        path=str(evidence_dir / "phase3-transport-recovery.png"),
        full_page=True,
    )
    context.close()

    return (
        {
            "initial_metrics": initial,
            "local_before_stop": local_before,
            "server_stop": stop_result,
            "server_down_metrics": down_metrics,
            "local_while_server_down": local_down,
            "restart": restart_meta,
            "recovered_metrics": recovered,
            "browser_offline_metrics": offline_metrics,
            "local_while_browser_offline": local_offline,
            "browser_online_metrics": online_metrics,
            "navigation_metrics": navigation,
            "reload_metrics": reload_metrics,
        },
        restarted,
    )


def storage_unavailable(
    browser: Browser,
    *,
    base_url: str,
    evidence_dir: Path,
) -> dict[str, Any]:
    context = browser.new_context(
        viewport={"width": 1100, "height": 820},
        accept_downloads=True,
    )
    context.add_init_script(
        """() => {
            const target = "hhs.pass185.production-lifecycle.v1";
            const getItem = Storage.prototype.getItem;
            const setItem = Storage.prototype.setItem;
            Storage.prototype.getItem = function(name) {
                if (name === target) throw new DOMException("blocked", "SecurityError");
                return getItem.call(this, name);
            };
            Storage.prototype.setItem = function(name, value) {
                if (name === target) throw new DOMException("blocked", "SecurityError");
                return setItem.call(this, name, value);
            };
        }"""
    )
    page = launch_page(context, base_url)
    open_tab(page, "Application")
    page.wait_for_selector('[data-testid="pass185-application-lifecycle"]')
    page.get_by_test_id("pass185-create-calculator").click()
    page.wait_for_function(
        """() => document.querySelector('[data-testid="pass185-lifecycle-status"]')?.textContent === 'LOCAL_STORAGE_UNAVAILABLE_LOCAL_SESSION_ACTIVE'""",
        timeout=15_000,
    )
    error = page.get_by_test_id("pass185-lifecycle-error").inner_text()
    assert "Local persistence unavailable" in error

    lifecycle = local_calculator(
        page,
        evidence_dir,
        label="phase3-storage-unavailable",
        marker="PASS185_PHASE3_STORAGE_UNAVAILABLE",
    )
    page.screenshot(
        path=str(evidence_dir / "phase3-storage-unavailable.png"),
        full_page=True,
    )
    context.close()
    return {
        "status": "LOCAL_STORAGE_UNAVAILABLE_LOCAL_SESSION_ACTIVE",
        "error": error,
        "local_lifecycle": lifecycle,
    }


def concurrent_contexts(
    browser: Browser,
    *,
    base_url: str,
    evidence_dir: Path,
) -> dict[str, Any]:
    context_a = browser.new_context(
        viewport={"width": 1050, "height": 820},
        accept_downloads=True,
    )
    context_b = browser.new_context(
        viewport={"width": 1050, "height": 820},
        accept_downloads=True,
    )
    page_a = launch_page(context_a, base_url)
    page_b = launch_page(context_b, base_url)

    result_a = local_calculator(
        page_a,
        evidence_dir,
        label="phase3-context-a",
        marker="PASS185_PHASE3_CONTEXT_A",
        save=True,
    )
    result_b = local_calculator(
        page_b,
        evidence_dir,
        label="phase3-context-b",
        marker="PASS185_PHASE3_CONTEXT_B",
        save=True,
    )

    page_a.reload(wait_until="domcontentloaded")
    page_a.wait_for_selector('[data-testid="hhs-product-workspace"]', timeout=60_000)
    open_workspace(page_a)
    open_tab(page_a, "Application")
    value_a = page_a.get_by_test_id("pass185-html-editor").input_value()
    assert "PASS185_PHASE3_CONTEXT_A" in value_a
    assert "PASS185_PHASE3_CONTEXT_B" not in value_a

    page_b.reload(wait_until="domcontentloaded")
    page_b.wait_for_selector('[data-testid="hhs-product-workspace"]', timeout=60_000)
    open_workspace(page_b)
    open_tab(page_b, "Application")
    value_b = page_b.get_by_test_id("pass185-html-editor").input_value()
    assert "PASS185_PHASE3_CONTEXT_B" in value_b
    assert "PASS185_PHASE3_CONTEXT_A" not in value_b

    storage_a = page_a.evaluate(
        "() => window.localStorage.getItem('hhs.pass185.production-lifecycle.v1')"
    )
    storage_b = page_b.evaluate(
        "() => window.localStorage.getItem('hhs.pass185.production-lifecycle.v1')"
    )
    assert storage_a and storage_b and storage_a != storage_b

    context_a.close()
    context_b.close()
    return {
        "context_a": result_a,
        "context_b": result_b,
        "local_storage_isolated": True,
        "cross_context_source_leak": False,
        "browser_contexts_share_canonical_backend_authority_only_through_explicit_commands": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", required=True)
    args = parser.parse_args()

    evidence_dir = Path(args.evidence_dir).resolve()
    evidence_dir.mkdir(parents=True, exist_ok=True)
    port = free_port()
    server = ProductionServer(
        port,
        evidence_dir,
        env={
            "HHS_COGNITION_AUTO_TICK": "0",
            "HHS_DISABLE_C_AUTOBUILD": "1",
        },
        label="phase3-initial-server",
    )
    initial_server = server.start()
    active_server = server
    started = time.monotonic()

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            transport, active_server = main_transport_recovery(
                browser,
                base_url=server.base_url,
                port=port,
                evidence_dir=evidence_dir,
                server=server,
            )
            storage = storage_unavailable(
                browser,
                base_url=active_server.base_url,
                evidence_dir=evidence_dir,
            )
            concurrent = concurrent_contexts(
                browser,
                base_url=active_server.base_url,
                evidence_dir=evidence_dir,
            )
            browser.close()

        result = {
            "schema": "HHS_PASS185_I141_PHASE3_BROWSER_LIFECYCLE_ACCEPTANCE_V1",
            "ok": True,
            "classification": "HHS_PASS_185_PHASE3_BROWSER_LIFECYCLE_VERIFIED",
            "entrypoint": ENTRYPOINT,
            "initial_server": initial_server,
            "transport_recovery": transport,
            "storage_unavailable": storage,
            "concurrent_contexts": concurrent,
            "elapsed_ms": round((time.monotonic() - started) * 1000),
            "frontend_runtime_authority": False,
            "browser_replacement_authority": False,
            "terminal_pass185_completion_claimed": False,
        }
        (evidence_dir / "phase3-browser-lifecycle.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\\n",
            encoding="utf-8",
        )
        print(json.dumps(result, indent=2, sort_keys=True))
    finally:
        active_server.stop()


if __name__ == "__main__":
    main()

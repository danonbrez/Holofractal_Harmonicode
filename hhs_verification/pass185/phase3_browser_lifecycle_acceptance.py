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
    console_errors: list[str] = []
    page_errors: list[str] = []
    setattr(page, "_hhs_console_errors", console_errors)
    setattr(page, "_hhs_page_errors", page_errors)
    page.on(
        "console",
        lambda message: console_errors.append(message.text)
        if message.type == "error"
        else None,
    )
    page.on("pageerror", lambda error: page_errors.append(str(error)))
    page.set_default_timeout(30_000)
    page.set_default_navigation_timeout(90_000)
    response = page.goto(base_url + "/", wait_until="domcontentloaded")
    assert response is not None and response.ok
    page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
    page.wait_for_selector('[data-testid="hhs-product-workspace"]', timeout=60_000)
    open_workspace(page)
    return page


def client_metrics(page: Page) -> dict[str, Any]:
    value = page.evaluate(
        """() => {
            const client = window.__HHS_RUNTIME_CLIENT__;
            return client ? client.getMetrics() : { missing: true };
        }"""
    )
    return dict(value or {})


def wait_client_state(
    page: Page,
    *,
    initialized: bool,
    connected_channels: int,
    listeners_per_channel: int,
    reconnect_pending: int | None = None,
    timeout_ms: int = 30_000,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_ms / 1000
    last: dict[str, Any] = {}
    while time.monotonic() < deadline:
        last = client_metrics(page)
        sockets = dict(last.get("sockets") or {})
        connected = sum(
            1
            for key in (
                "runtimeConnected",
                "replayConnected",
                "graphConnected",
                "transportConnected",
            )
            if sockets.get(key) is True
        )
        counts = dict(sockets.get("listenerCounts") or {})
        listener_ok = all(
            int(counts.get(channel, 0)) == listeners_per_channel
            for channel in ("runtime", "replay", "graph", "transport")
        )
        pending = list(sockets.get("reconnectPending") or [])
        if (
            bool(last.get("initialized")) is initialized
            and connected == connected_channels
            and listener_ok
            and (reconnect_pending is None or len(pending) == reconnect_pending)
        ):
            return last
        page.wait_for_timeout(250)
    raise AssertionError(
        {
            "classification": "INTEGRATED_RUNTIME_CLIENT_STATE_TIMEOUT",
            "expected": {
                "initialized": initialized,
                "connected_channels": connected_channels,
                "listeners_per_channel": listeners_per_channel,
                "reconnect_pending": reconnect_pending,
            },
            "last": last,
            "console_errors": getattr(page, "_hhs_console_errors", [])[-50:],
            "page_errors": getattr(page, "_hhs_page_errors", [])[-50:],
        }
    )


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
    workspace_text = page.locator(
        '[data-testid="hhs-visual-runtime-os-workspace"]'
    ).inner_text()
    raise AssertionError(
        {
            "classification": "RUNTIME_TRANSPORT_METRICS_TIMEOUT",
            "expected_connected": connected,
            "expected_subscriptions": subscriptions,
            "expected_reconnect": reconnect,
            "last": last,
            "workspace_text": workspace_text[-5000:],
            "console_errors": getattr(page, "_hhs_console_errors", [])[-50:],
            "page_errors": getattr(page, "_hhs_page_errors", [])[-50:],
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

    # Public production transport is intentionally on-demand. Before the
    # Runtime surface is opened the integrated client must be dormant.
    dormant_initial = wait_client_state(
        page,
        initialized=False,
        connected_channels=0,
        listeners_per_channel=0,
        reconnect_pending=0,
    )

    initial = wait_transport_metrics(
        page,
        connected="4 / 4",
        subscriptions="4 / 4",
        reconnect="none",
    )
    active_initial = wait_client_state(
        page,
        initialized=True,
        connected_channels=4,
        listeners_per_channel=1,
        reconnect_pending=0,
    )

    # First outage: keep the Runtime surface mounted so the existing client
    # must observe close and reconnect on its own after the backend restarts.
    stop_auto = server.stop()
    down_auto = wait_client_state(
        page,
        initialized=True,
        connected_channels=0,
        listeners_per_channel=1,
        timeout_ms=20_000,
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
    restart_auto = restarted.start()
    recovered_auto = wait_client_state(
        page,
        initialized=True,
        connected_channels=4,
        listeners_per_channel=1,
        reconnect_pending=0,
        timeout_ms=60_000,
    )
    recovered_ui = wait_transport_metrics(
        page,
        connected="4 / 4",
        subscriptions="4 / 4",
        reconnect="none",
        timeout_ms=30_000,
    )

    # Second outage: leave Runtime for Application. Its on-demand cleanup must
    # close all sockets/listeners, while local edit/preview/test/export remains
    # usable with the backend absent.
    stop_local = restarted.stop()
    wait_client_state(
        page,
        initialized=True,
        connected_channels=0,
        listeners_per_channel=1,
        timeout_ms=20_000,
    )
    open_tab(page, "Application")
    page.wait_for_selector('[data-testid="pass185-application-lifecycle"]')
    dormant_server_down = wait_client_state(
        page,
        initialized=False,
        connected_channels=0,
        listeners_per_channel=0,
        reconnect_pending=0,
    )
    local_down = local_calculator(
        page,
        evidence_dir,
        label="phase3-server-down",
        marker="PASS185_PHASE3_SERVER_DOWN",
    )

    restarted_again = ProductionServer(
        port,
        evidence_dir,
        env={
            "HHS_COGNITION_AUTO_TICK": "0",
            "HHS_DISABLE_C_AUTOBUILD": "1",
        },
        label="phase3-restarted-again-server",
    )
    restart_after_local = restarted_again.start()
    still_dormant = wait_client_state(
        page,
        initialized=False,
        connected_channels=0,
        listeners_per_channel=0,
        reconnect_pending=0,
    )
    remounted = wait_transport_metrics(
        page,
        connected="4 / 4",
        subscriptions="4 / 4",
        reconnect="none",
        timeout_ms=60_000,
    )

    # Browser network outage while Runtime remains mounted must reconnect using
    # the same single subscription set when connectivity returns.
    context.set_offline(True)
    offline_fetch = page.evaluate(
        """async () => {
            try {
                const response = await fetch('/api/product/health', { cache: 'no-store' });
                return { ok: response.ok, status: response.status };
            } catch (error) {
                return { ok: false, error: String(error) };
            }
        }"""
    )
    assert offline_fetch.get("ok") is False, offline_fetch
    offline_active = client_metrics(page)
    offline_sockets = dict(offline_active.get("sockets") or {})
    offline_counts = dict(offline_sockets.get("listenerCounts") or {})
    assert bool(offline_active.get("initialized")) is True, offline_active
    for channel in ("runtime", "replay", "graph", "transport"):
        assert int(offline_counts.get(channel, 0)) == 1, offline_active
    context.set_offline(False)
    online_active = wait_client_state(
        page,
        initialized=True,
        connected_channels=4,
        listeners_per_channel=1,
        reconnect_pending=0,
        timeout_ms=60_000,
    )

    # Local application use while browser networking is disabled.
    context.set_offline(True)
    open_tab(page, "Application")
    dormant_offline = wait_client_state(
        page,
        initialized=False,
        connected_channels=0,
        listeners_per_channel=0,
        reconnect_pending=0,
    )
    local_offline = local_calculator(
        page,
        evidence_dir,
        label="phase3-browser-offline",
        marker="PASS185_PHASE3_BROWSER_OFFLINE",
    )
    context.set_offline(False)
    restored_after_offline_local = wait_transport_metrics(
        page,
        connected="4 / 4",
        subscriptions="4 / 4",
        reconnect="none",
        timeout_ms=60_000,
    )

    # Repeated navigation must alternate cleanly between zero and one listener
    # per channel rather than accumulating duplicate subscriptions.
    navigation: list[dict[str, Any]] = []
    for cycle in range(3):
        open_tab(page, "Application")
        page.wait_for_selector('[data-testid="pass185-application-lifecycle"]')
        dormant = wait_client_state(
            page,
            initialized=False,
            connected_channels=0,
            listeners_per_channel=0,
            reconnect_pending=0,
        )
        active_ui = wait_transport_metrics(
            page,
            connected="4 / 4",
            subscriptions="4 / 4",
            reconnect="none",
            timeout_ms=30_000,
        )
        active = wait_client_state(
            page,
            initialized=True,
            connected_channels=4,
            listeners_per_channel=1,
            reconnect_pending=0,
        )
        navigation.append(
            {
                "cycle": cycle + 1,
                "dormant": dormant,
                "active": active,
                "active_ui": active_ui,
            }
        )

    # Full reload creates a new public-root client; it must start dormant and
    # then establish exactly one subscription per channel on Runtime mount.
    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
    page.wait_for_selector('[data-testid="hhs-product-workspace"]', timeout=60_000)
    open_workspace(page)
    reload_dormant = wait_client_state(
        page,
        initialized=False,
        connected_channels=0,
        listeners_per_channel=0,
        reconnect_pending=0,
    )
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
            "dormant_initial": dormant_initial,
            "initial_metrics": initial,
            "active_initial": active_initial,
            "automatic_reconnect": {
                "server_stop": stop_auto,
                "down": down_auto,
                "restart": restart_auto,
                "recovered": recovered_auto,
                "recovered_ui": recovered_ui,
            },
            "source_only_during_server_outage": {
                "server_stop": stop_local,
                "dormant": dormant_server_down,
                "local_lifecycle": local_down,
                "restart": restart_after_local,
                "still_dormant_after_restart": still_dormant,
                "remounted_runtime": remounted,
            },
            "browser_offline_reconnect": {
                "offline_fetch": offline_fetch,
                "offline_active": offline_active,
                "online_active": online_active,
                "preexisting_websocket_objects_not_required_to_close_under_browser_offline_emulation": True,
            },
            "browser_offline_local_application": {
                "dormant": dormant_offline,
                "local_lifecycle": local_offline,
                "restored_runtime": restored_after_offline_local,
            },
            "navigation_metrics": navigation,
            "reload_dormant": reload_dormant,
            "reload_metrics": reload_metrics,
        },
        restarted_again,
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
        """(() => {
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
        })();"""
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
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(result, indent=2, sort_keys=True))
    finally:
        active_server.stop()


if __name__ == "__main__":
    main()

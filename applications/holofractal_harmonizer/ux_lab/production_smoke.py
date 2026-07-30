from __future__ import annotations

import json
import os
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


BASE_URL = os.environ.get("HHS_PRODUCTION_SMOKE_URL", "http://127.0.0.1:8765")
EVIDENCE_DIR = Path(__file__).resolve().parents[1] / "evidence" / "production_integration_smoke"


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        console_errors: list[str] = []
        page.on(
            "console",
            lambda message: console_errors.append(message.text)
            if message.type == "error"
            else None,
        )

        started = time.monotonic()
        response = page.goto(BASE_URL, wait_until="domcontentloaded", timeout=120_000)
        dom_content_loaded_ms = round((time.monotonic() - started) * 1000)
        if response is None or not response.ok:
            raise AssertionError(f"production root failed: {getattr(response, 'status', None)}")

        page.wait_for_function(
            """() => Boolean(
                window.HHSHarmonizer &&
                window.HHSProductionIntegration &&
                window.HHSProductionIntegration.serviceCount > 0
            )""",
            timeout=120_000,
        )
        registry_hydrated_ms = round((time.monotonic() - started) * 1000)
        page.wait_for_selector("body.workflow-default", timeout=30_000)

        service_count = page.evaluate("window.HHSProductionIntegration.serviceCount")
        registry_count = page.locator("#registry-tree [data-object-id]").count()
        runtime_state = page.locator("#validation-state").inner_text()
        if "RECEIPT CLOSED" not in runtime_state:
            raise AssertionError(f"runtime authority did not become receipt-closed: {runtime_state}")

        page.locator("#open-api").click()
        page.wait_for_selector("#api-view:not([hidden])", timeout=10_000)
        page.wait_for_selector("#runtime-service-controller select", timeout=30_000)
        controller = page.locator("#runtime-service-controller")
        service_select = controller.locator("select")
        service_select.select_option("runtime_contract.self_test")
        controller.locator("button", has_text="Execute registered service").click()
        output = controller.locator("pre")
        output.wait_for(timeout=10_000)
        page.wait_for_function(
            """() => {
                const output = document.querySelector('#runtime-service-controller pre');
                return output && output.textContent.includes('HHS_RUNTIME_CONTRACT_SELF_TEST_V1');
            }""",
            timeout=120_000,
        )
        dispatch_completed_ms = round((time.monotonic() - started) * 1000)
        dispatch_text = output.inner_text()
        dispatch_payload = json.loads(dispatch_text)

        page.locator("#assistant-home").click()
        page.wait_for_selector("#assistant-view:not([hidden])", timeout=10_000)
        page.wait_for_function(
            """() => {
                const status = document.querySelector('#provider-status');
                return status && (
                    status.classList.contains('verified') ||
                    status.classList.contains('degraded')
                );
            }""",
            timeout=60_000,
        )
        provider_state = page.locator("#provider-status").inner_text()
        if "ONLINE" not in provider_state:
            raise AssertionError(f"assistant provider was not executable: {provider_state}")

        page.screenshot(
            path=str(EVIDENCE_DIR / "pass161-production-harmonizer.png"),
            full_page=True,
        )
        evidence = {
            "schema": "HHS_PASS161_PRODUCTION_BROWSER_SMOKE_V1",
            "ok": True,
            "base_url": BASE_URL,
            "title": page.title(),
            "workflow_default": page.locator("body").evaluate(
                "element => element.classList.contains('workflow-default')"
            ),
            "service_count": service_count,
            "registry_projected_object_count": registry_count,
            "runtime_state": runtime_state,
            "assistant_provider_state": provider_state,
            "dispatch_service": "runtime_contract.self_test",
            "dispatch_schema": dispatch_payload.get("schema"),
            "dispatch_result_schema_present": "HHS_RUNTIME_CONTRACT_SELF_TEST_V1" in dispatch_text,
            "dispatch_runtime_contract_present": bool(dispatch_payload.get("runtime_contract")),
            "timing_ms": {
                "dom_content_loaded": dom_content_loaded_ms,
                "registry_hydrated": registry_hydrated_ms,
                "service_dispatch_completed": dispatch_completed_ms,
            },
            "console_errors": console_errors,
            "frontend_is_authority": False,
        }
        (EVIDENCE_DIR / "production-smoke.json").write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(evidence, indent=2, sort_keys=True))
        browser.close()


if __name__ == "__main__":
    main()

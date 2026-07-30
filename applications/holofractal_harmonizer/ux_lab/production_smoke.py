from __future__ import annotations

import json
import os
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


BASE_URL = os.environ.get("HHS_PRODUCTION_SMOKE_URL", "http://127.0.0.1:8765")
EVIDENCE_DIR = Path(__file__).resolve().parents[1] / "evidence" / "production_integration_smoke"


def write_evidence(name: str, payload: dict) -> None:
    (EVIDENCE_DIR / name).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        console_errors: list[str] = []
        request_failures: list[dict[str, str]] = []
        page.on(
            "console",
            lambda message: console_errors.append(message.text)
            if message.type == "error"
            else None,
        )
        page.on(
            "requestfailed",
            lambda request: request_failures.append({
                "url": request.url,
                "failure": request.failure or "unknown request failure",
            }),
        )

        started = time.monotonic()
        try:
            response = page.goto(BASE_URL, wait_until="domcontentloaded", timeout=120_000)
            dom_content_loaded_ms = round((time.monotonic() - started) * 1000)
            if response is None or not response.ok:
                raise AssertionError(f"production root failed: {getattr(response, 'status', None)}")

            page.wait_for_function(
                """() => Boolean(
                    window.HHSHarmonizer &&
                    window.HHSProductionIntegration &&
                    (
                        window.HHSProductionIntegration.serviceCount > 0 ||
                        window.HHSProductionIntegration.phase === 'DEGRADED'
                    )
                )""",
                timeout=180_000,
            )
            integration = page.evaluate("""() => ({
                phase: window.HHSProductionIntegration?.phase,
                serviceCount: window.HHSProductionIntegration?.serviceCount,
                failures: window.HHSProductionIntegration?.failures,
                timings: window.HHSProductionIntegration?.timings,
                runtimeAuthority: window.HHSProductionIntegration?.runtimeAuthority,
                coordinator: window.HHSProductionStartupCoordinator,
                hasHarmonizer: Boolean(window.HHSHarmonizer),
                bodyClass: document.body.className,
                validationState: document.querySelector('#validation-state')?.textContent,
            })""")
            if int(integration.get("serviceCount") or 0) <= 0:
                failure = {
                    "schema": "HHS_PASS161_PRODUCTION_BROWSER_SMOKE_FAILURE_V1",
                    "ok": False,
                    "stage": "LIVE_SERVICE_REGISTRY_HYDRATION",
                    "base_url": BASE_URL,
                    "integration": integration,
                    "console_errors": console_errors,
                    "request_failures": request_failures,
                    "elapsed_ms": round((time.monotonic() - started) * 1000),
                    "frontend_is_authority": False,
                }
                page.screenshot(
                    path=str(EVIDENCE_DIR / "pass161-production-harmonizer-failure.png"),
                    full_page=True,
                )
                write_evidence("production-smoke-failure.json", failure)
                raise AssertionError(json.dumps(failure, sort_keys=True))

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
                timeout=90_000,
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
                "integration": integration,
                "timing_ms": {
                    "dom_content_loaded": dom_content_loaded_ms,
                    "registry_hydrated": registry_hydrated_ms,
                    "service_dispatch_completed": dispatch_completed_ms,
                },
                "console_errors": console_errors,
                "request_failures": request_failures,
                "frontend_is_authority": False,
            }
            write_evidence("production-smoke.json", evidence)
            print(json.dumps(evidence, indent=2, sort_keys=True))
        except Exception:
            diagnostic = page.evaluate("""() => ({
                integration: window.HHSProductionIntegration ? {
                    phase: window.HHSProductionIntegration.phase,
                    serviceCount: window.HHSProductionIntegration.serviceCount,
                    failures: window.HHSProductionIntegration.failures,
                    timings: window.HHSProductionIntegration.timings,
                } : null,
                coordinator: window.HHSProductionStartupCoordinator || null,
                hasHarmonizer: Boolean(window.HHSHarmonizer),
                validationState: document.querySelector('#validation-state')?.textContent || null,
                providerStatus: document.querySelector('#provider-status')?.textContent || null,
            })""")
            print(json.dumps({
                "browser_diagnostic": diagnostic,
                "console_errors": console_errors,
                "request_failures": request_failures,
            }, indent=2, sort_keys=True))
            raise
        finally:
            browser.close()


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
import os
import time
import traceback
from pathlib import Path

from playwright.sync_api import sync_playwright


BASE_URL = os.environ.get("HHS_PRODUCTION_SMOKE_URL", "http://127.0.0.1:8765").rstrip("/")
EVIDENCE_DIR = Path(__file__).resolve().parents[1] / "evidence" / "production_integration_smoke"


def write_evidence(name: str, payload: dict) -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    (EVIDENCE_DIR / name).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def phase(name: str, **details: object) -> None:
    print(json.dumps({"browser_phase": name, **details}, sort_keys=True), flush=True)


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    current_phase = "START"
    console_errors: list[str] = []
    page_errors: list[str] = []
    request_failures: list[dict[str, str]] = []
    source_failures: list[dict[str, object]] = []
    started = time.monotonic()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.set_default_timeout(20_000)
        page.set_default_navigation_timeout(90_000)
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on(
            "requestfailed",
            lambda request: request_failures.append({
                "url": request.url,
                "failure": request.failure or "unknown request failure",
            }),
        )
        page.on(
            "response",
            lambda response: source_failures.append({"status": response.status, "url": response.url})
            if response.status >= 400 and "/src/" in response.url
            else None,
        )

        try:
            # Repository tests prohibit top-level await in public entry modules.
            # DOMContentLoaded is therefore the bounded parsed-document boundary;
            # live registry hydration remains a separate authority assertion.
            current_phase = "NAVIGATE"
            phase(current_phase, url=BASE_URL)
            response = page.goto(BASE_URL, wait_until="domcontentloaded", timeout=90_000)
            if response is None or not response.ok:
                raise AssertionError(f"production root failed: {getattr(response, 'status', None)}")
            http_committed_ms = round((time.monotonic() - started) * 1000)
            current_phase = "DOCUMENT_PARSED"
            phase(current_phase, status=response.status, elapsed_ms=http_committed_ms)
            page.wait_for_selector("#harmonizer", state="attached", timeout=20_000)

            current_phase = "WAIT_RUNTIME_INTEGRATION"
            phase(current_phase)
            page.wait_for_function(
                """() => Boolean(
                    window.HHSHarmonizer &&
                    window.HHSProductionIntegration &&
                    (
                        window.HHSProductionIntegration.serviceCount > 0 ||
                        window.HHSProductionIntegration.phase === 'DEGRADED'
                    )
                )""",
                timeout=60_000,
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
            service_count = int(integration.get("serviceCount") or 0)
            current_phase = "REGISTRY_HYDRATED"
            phase(current_phase, integration_phase=integration.get("phase"), service_count=service_count)
            if service_count <= 0:
                raise AssertionError(f"live service registry did not hydrate: {integration}")
            if source_failures:
                raise AssertionError(f"browser source modules failed: {source_failures}")

            registry_hydrated_ms = round((time.monotonic() - started) * 1000)
            current_phase = "WAIT_WORKFLOW_SURFACE"
            phase(current_phase)
            page.wait_for_selector("body.workflow-default", timeout=30_000)
            registry_count = page.locator("#registry-tree [data-object-id]").count()
            runtime_state = page.locator("#validation-state").inner_text()
            if "RECEIPT CLOSED" not in runtime_state:
                raise AssertionError(f"runtime authority did not become receipt-closed: {runtime_state}")
            phase("WORKFLOW_SURFACE_READY", runtime_state=runtime_state)

            current_phase = "OPEN_API_SURFACE"
            phase(current_phase)
            page.locator("#open-api").click()
            page.wait_for_selector("#api-view:not([hidden])", timeout=20_000)
            page.wait_for_selector("#runtime-service-controller select", timeout=30_000)
            controller = page.locator("#runtime-service-controller")
            controller.locator("select").select_option("runtime_contract.self_test")
            controller.locator("button", has_text="Execute registered service").click()
            output = controller.locator("pre")
            output.wait_for(timeout=20_000)
            page.wait_for_function(
                """() => document.querySelector('#runtime-service-controller pre')
                    ?.textContent.includes('HHS_RUNTIME_CONTRACT_SELF_TEST_V1')""",
                timeout=60_000,
            )
            dispatch_text = output.inner_text()
            dispatch_payload = json.loads(dispatch_text)
            dispatch_completed_ms = round((time.monotonic() - started) * 1000)
            phase("SERVICE_DISPATCH_VERIFIED", elapsed_ms=dispatch_completed_ms)

            current_phase = "OPEN_ASSISTANT"
            phase(current_phase)
            page.locator("#assistant-home").click()
            page.wait_for_selector("#assistant-view:not([hidden])", timeout=20_000)
            page.wait_for_function(
                """() => {
                    const status = document.querySelector('#provider-status');
                    return status && (
                        status.classList.contains('verified') ||
                        status.classList.contains('degraded')
                    );
                }""",
                timeout=45_000,
            )
            provider_state = page.locator("#provider-status").inner_text()
            if "ONLINE" not in provider_state:
                raise AssertionError(f"assistant provider was not executable: {provider_state}")
            phase("ASSISTANT_VERIFIED", provider_state=provider_state)

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
                    "http_committed": http_committed_ms,
                    "registry_hydrated": registry_hydrated_ms,
                    "service_dispatch_completed": dispatch_completed_ms,
                },
                "console_errors": console_errors,
                "page_errors": page_errors,
                "request_failures": request_failures,
                "source_failures": source_failures,
                "frontend_is_authority": False,
            }
            write_evidence("production-smoke.json", evidence)
            current_phase = "COMPLETE"
            phase(current_phase, elapsed_ms=round((time.monotonic() - started) * 1000))
            print(json.dumps(evidence, indent=2, sort_keys=True), flush=True)
        except Exception as error:
            failure = {
                "schema": "HHS_PASS161_PRODUCTION_BROWSER_SMOKE_DIAGNOSTIC_V1",
                "ok": False,
                "phase": current_phase,
                "base_url": BASE_URL,
                "error": f"{type(error).__name__}: {error}",
                "traceback": traceback.format_exc(),
                "elapsed_ms": round((time.monotonic() - started) * 1000),
                "console_errors": console_errors,
                "page_errors": page_errors,
                "request_failures": request_failures,
                "source_failures": source_failures,
            }
            write_evidence("production-smoke-failure.json", failure)
            print(json.dumps(failure, indent=2, sort_keys=True), flush=True)
            try:
                page.screenshot(
                    path=str(EVIDENCE_DIR / "pass161-production-harmonizer-failure.png"),
                    full_page=True,
                    timeout=5_000,
                )
            except Exception:
                pass
            raise
        finally:
            try:
                browser.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()

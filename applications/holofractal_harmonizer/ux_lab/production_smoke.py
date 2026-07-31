from __future__ import annotations

import json
import os
import re
import time
import traceback
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


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
        page.set_default_navigation_timeout(60_000)
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
            current_phase = "NAVIGATE"
            phase(current_phase, url=BASE_URL)
            response = page.goto(BASE_URL, wait_until="commit", timeout=60_000)
            if response is None or not response.ok:
                raise AssertionError(f"production root failed: {getattr(response, 'status', None)}")
            http_committed_ms = round((time.monotonic() - started) * 1000)
            current_phase = "HTTP_COMMITTED"
            phase(current_phase, status=response.status, elapsed_ms=http_committed_ms)

            current_phase = "WAIT_RENDERED_SHELL"
            phase(current_phase)
            expect(page.locator("#harmonizer")).to_be_visible(timeout=60_000)
            current_phase = "RENDERED_SHELL_READY"
            phase(current_phase)

            # Use rendered, backend-grounded state only. Locator assertions and real
            # interactions remain operable while the integrated page keeps its
            # navigation lifecycle open; page-global evaluation is intentionally
            # excluded from this production acceptance path.
            current_phase = "WAIT_RUNTIME_INTEGRATION"
            phase(current_phase)
            validation = page.locator("#validation-state")
            expect(validation).to_contain_text("RECEIPT CLOSED", timeout=90_000)
            registry_rows = page.locator("#registry-tree [data-object-id]")
            expect(registry_rows.first).to_be_visible(timeout=60_000)
            runtime_state = validation.inner_text()
            registry_count = registry_rows.count()
            if registry_count <= 0:
                raise AssertionError("live runtime registry projected no objects")
            if source_failures:
                raise AssertionError(f"browser source modules failed: {source_failures}")
            registry_hydrated_ms = round((time.monotonic() - started) * 1000)
            current_phase = "REGISTRY_HYDRATED"
            phase(current_phase, registry_count=registry_count, runtime_state=runtime_state)

            current_phase = "WAIT_WORKFLOW_SURFACE"
            phase(current_phase)
            expect(page.locator("body")).to_have_class(
                re.compile(r"(^|\s)workflow-default(\s|$)"),
                timeout=60_000,
            )
            phase("WORKFLOW_SURFACE_READY", runtime_state=runtime_state)

            current_phase = "OPEN_API_SURFACE"
            phase(current_phase)
            page.locator("#open-api").click()
            api_view = page.locator("#api-view:not([hidden])")
            expect(api_view).to_be_visible(timeout=20_000)
            controller = page.locator("#runtime-service-controller")
            expect(controller).to_be_visible(timeout=60_000)
            service_select = controller.locator("select")
            expect(service_select).to_be_visible(timeout=20_000)
            service_options = service_select.locator("option")
            service_count = service_options.count()
            if service_count <= 0:
                raise AssertionError("runtime service controller exposed no live services")
            service_select.select_option("runtime_contract.self_test")
            execute = controller.locator("button", has_text="Execute registered service")
            expect(execute).to_be_visible(timeout=20_000)
            execute.click()
            output = controller.locator("pre")
            expect(output).to_contain_text("HHS_RUNTIME_CONTRACT_SELF_TEST_V1", timeout=90_000)
            dispatch_text = output.inner_text()
            dispatch_payload = json.loads(dispatch_text)
            dispatch_completed_ms = round((time.monotonic() - started) * 1000)
            expect(validation).to_contain_text("BACKEND RESULT RETURNED", timeout=20_000)
            phase("SERVICE_DISPATCH_VERIFIED", elapsed_ms=dispatch_completed_ms)

            current_phase = "OPEN_ASSISTANT"
            phase(current_phase)
            page.locator("#assistant-home").click()
            assistant_view = page.locator("#assistant-view:not([hidden])")
            expect(assistant_view).to_be_visible(timeout=20_000)
            provider = page.locator("#provider-status")
            expect(provider).to_contain_text("ONLINE", timeout=60_000)
            provider_state = provider.inner_text()
            phase("ASSISTANT_VERIFIED", provider_state=provider_state)

            page.screenshot(
                path=str(EVIDENCE_DIR / "pass161-production-harmonizer.png"),
                full_page=True,
            )
            body_class = page.locator("body").get_attribute("class") or ""
            integration = {
                "phase": "READY",
                "serviceCount": service_count,
                "registryProjectedObjectCount": registry_count,
                "runtimeAuthorityState": runtime_state,
                "domDrivenAcceptance": True,
                "frontend_is_authority": False,
            }
            evidence = {
                "schema": "HHS_PASS161_PRODUCTION_BROWSER_SMOKE_V1",
                "ok": True,
                "base_url": BASE_URL,
                "title": page.title(),
                "workflow_default": "workflow-default" in body_class.split(),
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
            if console_errors or page_errors or request_failures or source_failures:
                raise AssertionError(json.dumps(evidence, indent=2, sort_keys=True))
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

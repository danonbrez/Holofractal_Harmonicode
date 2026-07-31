from __future__ import annotations

import json
import os
import time
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


BASE_URL = os.environ.get("HHS_PASS176_SMOKE_URL", "http://127.0.0.1:8765")
EVIDENCE_DIR = Path(__file__).resolve().parents[1] / "evidence" / "pass176"
STABLE_MOBILE_PANES = ("editor", "lifecycle", "terminal", "spatial")


def phase(name: str, **data: object) -> None:
    print(json.dumps({"phase": name, "monotonic": round(time.monotonic(), 3), **data}, sort_keys=True), flush=True)


def write_json(name: str, payload: dict) -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    (EVIDENCE_DIR / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        phase("chromium-launch")
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1000})
        page = context.new_page()
        page.set_default_timeout(20_000)
        page.set_default_navigation_timeout(60_000)

        console_errors: list[str] = []
        console_messages: list[dict[str, str]] = []
        page_errors: list[str] = []
        request_failures: list[dict[str, str]] = []
        http_errors: list[dict[str, object]] = []
        page.on(
            "console",
            lambda message: (
                console_messages.append({"type": message.type, "text": message.text}),
                console_errors.append(message.text) if message.type == "error" else None,
            ),
        )
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
            lambda response: http_errors.append({"url": response.url, "status": response.status})
            if response.status >= 400 else None,
        )

        started = time.monotonic()
        current_phase = "navigate"
        try:
            phase(current_phase, url=BASE_URL)
            response = page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60_000)
            if response is None or not response.ok:
                raise AssertionError(f"Pass 176 production root failed: {getattr(response, 'status', None)}")
            dom_loaded_ms = round((time.monotonic() - started) * 1000)
            phase("dom-content-loaded", status=response.status, elapsed_ms=dom_loaded_ms)

            current_phase = "wait-pass176-controller"
            page.wait_for_function("() => Boolean(window.HHSPass176)", timeout=20_000)
            current_phase = "wait-pass176-interactive"
            page.wait_for_function(
                """() => Boolean(
                    window.HHSPass176?.status().boot.interactive &&
                    window.HHSVisualIDE &&
                    window.HHSIntegratedAssistant &&
                    window.HHSGUIReliability
                )""",
                timeout=60_000,
            )
            interactive_ms = round((time.monotonic() - started) * 1000)
            page.wait_for_selector("#ide-source-editor", timeout=20_000)
            page.wait_for_selector("#pass176-stability-status.interactive", timeout=20_000)
            phase(current_phase, elapsed_ms=interactive_ms)

            current_phase = "initial-state"
            initial = page.evaluate("""() => ({
                activePath: window.HHSVisualIDE.state.activePath,
                editorValue: document.querySelector('#ide-source-editor')?.value,
                resourceTotal: window.HHSPass176.status().resources.total,
                bootRecords: window.HHSPass176.status().boot.records.length,
                stage: window.HHSPass176.status().boot.stage,
            })""")
            phase(current_phase, stage=initial["stage"], resources=initial["resourceTotal"])

            current_phase = "duplicate-boot"
            duplicate_boot = page.evaluate("""async () => {
                const [left, right] = await Promise.all([
                    window.HHSPass176.boot([]),
                    window.HHSPass176.boot([]),
                ]);
                return {
                    leftStage: left.boot.stage,
                    rightStage: right.boot.stage,
                    recordCount: left.boot.records.length,
                };
            }""")
            phase(current_phase, **duplicate_boot)

            page.set_viewport_size({"width": 390, "height": 844})
            page.wait_for_timeout(150)
            cycle_baseline = page.evaluate("""() => ({
                editorValue: document.querySelector('#ide-source-editor')?.value,
                activePath: window.HHSVisualIDE.state.activePath,
            })""")

            for index in range(100):
                current_phase = f"assistant-cycle-{index + 1}"
                page.locator("#assistant-home").dispatch_event("click", timeout=2_000)
                page.locator("#ide-assistant-close").dispatch_event("click", timeout=2_000)
                if (index + 1) % 10 == 0:
                    phase("assistant-cycle-progress", completed=index + 1)

            current_phase = "mobile-pane-control-validation"
            available_panes = page.evaluate("""() => [...document.querySelectorAll(
                '.ide-mobile-dock [data-mobile-pane]'
            )].map((button) => button.dataset.mobilePane)""")
            missing = sorted(set(STABLE_MOBILE_PANES) - set(available_panes))
            if missing:
                raise AssertionError(f"Pass 176 stable mobile panes are incomplete: {missing}")
            for pane in STABLE_MOBILE_PANES:
                page.locator(f'.ide-mobile-dock [data-mobile-pane="{pane}"]').first.dispatch_event(
                    "click", timeout=2_000
                )

            for index in range(100):
                current_phase = f"mobile-pane-cycle-{index + 1}"
                pane = STABLE_MOBILE_PANES[index % len(STABLE_MOBILE_PANES)]
                selected = page.evaluate("""(requested) => {
                    window.HHSGUIReliability.selectMobilePane(requested);
                    return {
                        selected: window.HHSGUIReliability.mobilePane,
                        layout: document.querySelector('#ide-layout')?.dataset.mobilePane,
                    };
                }""", pane)
                if selected["selected"] != pane or selected["layout"] != pane:
                    raise AssertionError(f"mobile pane selection diverged: {pane} -> {selected}")
                if (index + 1) % 10 == 0:
                    phase("mobile-pane-cycle-progress", completed=index + 1, controls=len(STABLE_MOBILE_PANES))

            current_phase = "mobile-repetition-result"
            cycles = page.evaluate("""(baseline) => ({
                assistantCycles: 100,
                paneCycles: 100,
                editorPreserved: document.querySelector('#ide-source-editor')?.value === baseline.editorValue,
                activePath: window.HHSVisualIDE.state.activePath,
                baselineActivePath: baseline.activePath,
                resourceTotal: window.HHSPass176.status().resources.total,
                assistantOpen: Boolean(window.HHSIntegratedAssistant?.isOpen),
            })""", cycle_baseline)
            phase(current_phase, **cycles)

            current_phase = "stale-response"
            stale_response = page.evaluate("""() => {
                const older = window.HHSPass176.generation('preview');
                const current = window.HHSPass176.generation('preview');
                let rejected = false;
                try { window.HHSPass176.accept(older, 'stale'); }
                catch (error) { rejected = String(error.message).includes('STALE_ASYNC_RESPONSE'); }
                return {
                    rejected,
                    currentAccepted: window.HHSPass176.accept(current, 'current') === 'current',
                };
            }""")
            phase(current_phase, **stale_response)

            current_phase = "bounded-cancellation"
            cancelled_job = page.evaluate("""async () => {
                const promise = window.HHSPass176.runAction(
                    'pass176-smoke-cancel',
                    ({ signal }) => new Promise((resolve, reject) => {
                        const timer = setTimeout(() => resolve('unexpected'), 2000);
                        signal.addEventListener('abort', () => {
                            clearTimeout(timer);
                            reject(new DOMException('cancelled', 'AbortError'));
                        }, { once: true });
                    }),
                    { timeoutMs: 4000, detail: 'Cancellation smoke test' },
                );
                setTimeout(() => window.HHSPass176.cancel('pass176-smoke-cancel'), 20);
                try { await promise; return { cancelled: false }; }
                catch (error) {
                    return { cancelled: error.name === 'AbortError' || String(error.message).includes('CANCEL') };
                }
            }""")
            phase(current_phase, **cancelled_job)

            current_phase = "atomic-recovery"
            recovery = page.evaluate("""() => {
                const editor = document.querySelector('#ide-source-editor');
                const original = editor?.value || '';
                if (editor) {
                    editor.value = `${original}\n// PASS176_RECOVERY_SMOKE`;
                    editor.dispatchEvent(new Event('input', { bubbles: true }));
                }
                const envelope = window.HHSPass176.flushRecovery('browser-smoke');
                if (editor) {
                    editor.value = original;
                    editor.dispatchEvent(new Event('input', { bubbles: true }));
                }
                return {
                    saved: Boolean(envelope),
                    schema: envelope?.schema,
                    authoritativeBackendDurabilityClaimed:
                        envelope?.metadata?.authoritativeBackendDurabilityClaimed,
                };
            }""")
            phase(current_phase, **recovery)

            current_phase = "final-status"
            final_status = page.evaluate("""() => {
                const status = window.HHSPass176.status();
                const navigation = performance.getEntriesByType('navigation')[0];
                return {
                    classification: status.classification,
                    boot: status.boot,
                    resources: status.resources,
                    jobs: status.jobs,
                    errors: status.errors,
                    longTasks: status.longTasks,
                    profile: status.profile,
                    canonicalFrontendAuthority: status.canonicalFrontendAuthority,
                    vm81AuthorityPreserved: status.vm81AuthorityPreserved,
                    hash72CommitStreams: status.hash72CommitStreams,
                    navigation: navigation ? {
                        domContentLoaded: Math.round(navigation.domContentLoadedEventEnd),
                        loadEventEnd: Math.round(navigation.loadEventEnd),
                    } : None,
                };
            }""".replace("None", "null"))
            phase(current_phase, classification=final_status["classification"])

            if initial["stage"] != "INTERACTIVE":
                raise AssertionError(f"Pass 176 did not reach INTERACTIVE: {initial}")
            if initial["bootRecords"] != 10 or duplicate_boot["recordCount"] != 10:
                raise AssertionError(f"duplicate boot changed state: {duplicate_boot}")
            if not cycles["editorPreserved"] or cycles["activePath"] != initial["activePath"]:
                raise AssertionError(f"UI cycles changed editor/project state: {cycles}")
            if cycles["assistantOpen"]:
                raise AssertionError(f"assistant remained open after cycle closure: {cycles}")
            if cycles["resourceTotal"] != initial["resourceTotal"]:
                raise AssertionError(f"resource growth detected: {initial} -> {cycles}")
            if not stale_response["rejected"] or not stale_response["currentAccepted"]:
                raise AssertionError(f"stale response gate failed: {stale_response}")
            if not cancelled_job["cancelled"]:
                raise AssertionError(f"bounded cancellation failed: {cancelled_job}")
            if not recovery["saved"] or recovery["authoritativeBackendDurabilityClaimed"] is not False:
                raise AssertionError(f"recovery envelope invalid: {recovery}")
            if final_status["canonicalFrontendAuthority"] is not False:
                raise AssertionError("frontend incorrectly claimed canonical authority")
            if not final_status["vm81AuthorityPreserved"] or final_status["hash72CommitStreams"] != 1:
                raise AssertionError("backend authority invariants were not preserved")
            if final_status["errors"]:
                raise AssertionError(f"Pass 176 recorded browser errors: {final_status['errors']}")
            if request_failures:
                raise AssertionError(f"request failures observed: {request_failures}")
            if http_errors:
                raise AssertionError(f"HTTP errors observed: {http_errors}")
            if page_errors:
                raise AssertionError(f"page errors observed: {page_errors}")
            if console_errors:
                raise AssertionError(f"console errors observed: {console_errors}")

            current_phase = "evidence"
            page.screenshot(path=str(EVIDENCE_DIR / "pass176-frozen-ide.png"), full_page=True, timeout=20_000)
            evidence = {
                "schema": "HHS_PASS_176_FROZEN_IDE_BROWSER_SMOKE_V1",
                "ok": True,
                "base_url": BASE_URL,
                "title": page.title(),
                "timing_ms": {"dom_content_loaded": dom_loaded_ms, "pass176_interactive": interactive_ms},
                "initial": initial,
                "duplicate_boot": duplicate_boot,
                "repetition": cycles,
                "stale_response": stale_response,
                "cancelled_job": cancelled_job,
                "recovery": recovery,
                "final_status": final_status,
                "console_errors": console_errors,
                "console_messages": console_messages[-100:],
                "page_errors": page_errors,
                "request_failures": request_failures,
                "http_errors": http_errors,
                "external_vercel_status_considered": False,
            }
            write_json("browser-smoke.json", evidence)
            phase(current_phase, ok=True)
            print(json.dumps(evidence, indent=2, sort_keys=True), flush=True)
        except Exception as error:
            failure = {
                "schema": "HHS_PASS_176_FROZEN_IDE_BROWSER_SMOKE_FAILURE_V1",
                "ok": False,
                "phase": current_phase,
                "exception_type": type(error).__name__,
                "exception": str(error),
                "console_errors": console_errors,
                "console_messages": console_messages[-100:],
                "page_errors": page_errors,
                "request_failures": request_failures,
                "http_errors": http_errors,
                "elapsed_ms": round((time.monotonic() - started) * 1000),
            }
            write_json("browser-smoke-failure.json", failure)
            phase("failure", **failure)
            try:
                page.screenshot(
                    path=str(EVIDENCE_DIR / "pass176-frozen-ide-failure.png"),
                    full_page=True,
                    timeout=10_000,
                )
            except (PlaywrightTimeoutError, Exception) as screenshot_error:
                phase("failure-screenshot-unavailable", error=str(screenshot_error))
            raise
        finally:
            phase("browser-close")
            context.close()
            browser.close()


if __name__ == "__main__":
    main()

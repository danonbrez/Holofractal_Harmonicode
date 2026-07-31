from __future__ import annotations

import json
import os
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


BASE_URL = os.environ.get("HHS_PASS176_SMOKE_URL", "http://127.0.0.1:8765")
EVIDENCE_DIR = Path(__file__).resolve().parents[1] / "evidence" / "pass176"


def write_json(name: str, payload: dict) -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    (EVIDENCE_DIR / name).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1000})
        page = context.new_page()
        console_errors: list[str] = []
        page_errors: list[str] = []
        request_failures: list[dict[str, str]] = []
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
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
            if response is None or not response.ok:
                raise AssertionError(f"Pass 176 production root failed: {getattr(response, 'status', None)}")
            dom_loaded_ms = round((time.monotonic() - started) * 1000)
            page.wait_for_function(
                """() => Boolean(
                    window.HHSPass176 &&
                    window.HHSPass176.status().boot.interactive &&
                    window.HHSVisualIDE
                )""",
                timeout=180_000,
            )
            interactive_ms = round((time.monotonic() - started) * 1000)
            page.wait_for_selector("#ide-source-editor", timeout=30_000)
            page.wait_for_selector("#pass176-stability-status.interactive", timeout=30_000)

            initial = page.evaluate("""() => ({
                activePath: window.HHSVisualIDE.state.activePath,
                editorValue: document.querySelector('#ide-source-editor')?.value,
                resourceTotal: window.HHSPass176.status().resources.total,
                bootRecords: window.HHSPass176.status().boot.records.length,
                stage: window.HHSPass176.status().boot.stage,
            })""")

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

            page.set_viewport_size({"width": 390, "height": 844})
            page.wait_for_timeout(150)
            cycles = page.evaluate("""async () => {
                const assistant = document.querySelector('#assistant-home');
                const back = document.querySelector('#return-assistant');
                const editor = document.querySelector('#ide-source-editor');
                const before = editor?.value;
                for (let index = 0; index < 100; index += 1) {
                    assistant?.click();
                    await Promise.resolve();
                    back?.click();
                    await Promise.resolve();
                }
                const dock = [...document.querySelectorAll('.ide-mobile-dock [data-mobile-pane]')];
                for (let index = 0; index < 100; index += 1) {
                    dock[index % Math.max(1, dock.length)]?.click();
                    await Promise.resolve();
                }
                return {
                    assistantCycles: 100,
                    paneCycles: 100,
                    editorPreserved: editor?.value === before,
                    activePath: window.HHSVisualIDE.state.activePath,
                    resourceTotal: window.HHSPass176.status().resources.total,
                };
            }""")

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

            cancelled_job = page.evaluate("""async () => {
                const promise = window.HHSPass176.runAction(
                    'pass176-smoke-cancel',
                    ({ signal }) => new Promise((resolve, reject) => {
                        const timer = setTimeout(() => resolve('unexpected'), 5000);
                        signal.addEventListener('abort', () => {
                            clearTimeout(timer);
                            reject(new DOMException('cancelled', 'AbortError'));
                        }, { once: true });
                    }),
                    { timeoutMs: 8000, detail: 'Cancellation smoke test' },
                );
                setTimeout(() => window.HHSPass176.cancel('pass176-smoke-cancel'), 20);
                try {
                    await promise;
                    return { cancelled: false };
                } catch (error) {
                    return { cancelled: error.name === 'AbortError' || String(error.message).includes('CANCEL') };
                }
            }""")

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
                    } : null,
                };
            }""")

            if initial["stage"] != "INTERACTIVE":
                raise AssertionError(f"Pass 176 did not reach INTERACTIVE: {initial}")
            if initial["bootRecords"] != 10 or duplicate_boot["recordCount"] != 10:
                raise AssertionError(f"duplicate boot changed state: {duplicate_boot}")
            if not cycles["editorPreserved"] or cycles["activePath"] != initial["activePath"]:
                raise AssertionError(f"UI cycles changed editor/project state: {cycles}")
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
            if page_errors:
                raise AssertionError(f"page errors observed: {page_errors}")
            if console_errors:
                raise AssertionError(f"console errors observed: {console_errors}")

            page.screenshot(path=str(EVIDENCE_DIR / "pass176-frozen-ide.png"), full_page=True)
            evidence = {
                "schema": "HHS_PASS_176_FROZEN_IDE_BROWSER_SMOKE_V1",
                "ok": True,
                "base_url": BASE_URL,
                "title": page.title(),
                "timing_ms": {
                    "dom_content_loaded": dom_loaded_ms,
                    "pass176_interactive": interactive_ms,
                },
                "initial": initial,
                "duplicate_boot": duplicate_boot,
                "repetition": cycles,
                "stale_response": stale_response,
                "cancelled_job": cancelled_job,
                "recovery": recovery,
                "final_status": final_status,
                "console_errors": console_errors,
                "page_errors": page_errors,
                "request_failures": request_failures,
                "external_vercel_status_considered": False,
            }
            write_json("browser-smoke.json", evidence)
            print(json.dumps(evidence, indent=2, sort_keys=True))
        except Exception:
            diagnostic = page.evaluate("""() => ({
                pass176: window.HHSPass176?.status?.() || null,
                activePath: window.HHSVisualIDE?.state?.activePath || null,
                editorValueLength: document.querySelector('#ide-source-editor')?.value?.length || 0,
                documentReadyState: document.readyState,
            })""")
            failure = {
                "schema": "HHS_PASS_176_FROZEN_IDE_BROWSER_SMOKE_FAILURE_V1",
                "ok": False,
                "diagnostic": diagnostic,
                "console_errors": console_errors,
                "page_errors": page_errors,
                "request_failures": request_failures,
            }
            write_json("browser-smoke-failure.json", failure)
            page.screenshot(path=str(EVIDENCE_DIR / "pass176-frozen-ide-failure.png"), full_page=True)
            print(json.dumps(failure, indent=2, sort_keys=True))
            raise
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    main()

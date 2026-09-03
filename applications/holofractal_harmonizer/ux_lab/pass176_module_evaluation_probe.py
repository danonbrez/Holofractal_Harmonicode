from __future__ import annotations

import json
import os
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


BASE_URL = os.environ.get("HHS_PASS176_SMOKE_URL", "http://127.0.0.1:8765/pass176-ide/")
EVIDENCE_DIR = Path(__file__).resolve().parents[1] / "evidence" / "pass176"
OUTPUT_PATH = EVIDENCE_DIR / "module-evaluation-probe.json"
MODULES = (
    "./src/sha256.mjs",
    "./src/core.mjs",
    "./src/visual-ide-state.mjs",
    "./src/visual-ide-ui.mjs",
    "./src/visual-ide-runtime.mjs",
    "./src/pass176-stability-core.mjs",
    "./src/pass176-stability.mjs",
    "./src/gui-reliability.mjs",
    "./src/browser.mjs",
    "./src/visual-ide.mjs",
)


def emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, sort_keys=True), flush=True)


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1000})
        page = context.new_page()
        page.set_default_timeout(20_000)
        console_errors: list[str] = []
        page_errors: list[str] = []
        request_failures: list[dict[str, str]] = []
        http_errors: list[dict[str, object]] = []
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on(
            "requestfailed",
            lambda request: request_failures.append({"url": request.url, "failure": request.failure or "unknown"}),
        )
        page.on(
            "response",
            lambda response: http_errors.append({"url": response.url, "status": response.status})
            if response.status >= 400 else None,
        )

        response = page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60_000)
        if response is None or not response.ok:
            raise RuntimeError(f"Pass 176 route unavailable: {getattr(response, 'status', None)}")
        page.wait_for_timeout(500)

        results: list[dict[str, object]] = []
        for module_path in MODULES:
            result = page.evaluate(
                """async ({ path, timeoutMs }) => {
                    const started = performance.now();
                    const settled = await Promise.race([
                        import(path).then(() => ({ state: 'READY', error: null })).catch((error) => ({
                            state: 'FAILED',
                            error: `${error?.name || 'Error'}: ${error?.message || String(error)}`,
                        })),
                        new Promise((resolve) => window.setTimeout(
                            () => resolve({ state: 'TIMEOUT', error: null }),
                            timeoutMs,
                        )),
                    ]);
                    const resource = performance.getEntriesByType('resource')
                        .filter((entry) => entry.name.endsWith(path.replace('./', '/pass176-ide/')))
                        .at(-1);
                    return {
                        path,
                        state: settled.state,
                        error: settled.error,
                        elapsed_ms: Math.round(performance.now() - started),
                        resource: resource ? {
                            duration_ms: Math.round(resource.duration),
                            response_end_ms: Math.round(resource.responseEnd),
                            transfer_size: resource.transferSize,
                        } : null,
                        surfaces: {
                            public_boot: Boolean(window.HHSPublicBoot),
                            browser_ready: Boolean(window.HHSBrowserReady),
                            pass176: Boolean(window.HHSPass176),
                            visual_ide_boot: Boolean(window.HHSVisualIDEBoot),
                            gui_reliability: Boolean(window.HHSGUIReliability),
                        },
                        public_boot_modules: window.HHSPublicBoot?.status?.() || [],
                    };
                }""",
                {"path": module_path, "timeoutMs": 2_000},
            )
            results.append(result)
            emit({"phase": "module-evaluation", **result})

        payload = {
            "schema": "HHS_PASS_176_I150_MODULE_EVALUATION_PROBE_V1",
            "url": BASE_URL,
            "elapsed_ms": round((time.monotonic() - started) * 1000),
            "modules": results,
            "console_errors": console_errors,
            "page_errors": page_errors,
            "request_failures": request_failures,
            "http_errors": http_errors,
            "final_public_boot_modules": page.evaluate("() => window.HHSPublicBoot?.status?.() || []"),
            "frontend_is_authority": False,
        }
        OUTPUT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        emit({
            "phase": "probe-complete",
            "ready": [item["path"] for item in results if item["state"] == "READY"],
            "timeouts": [item["path"] for item in results if item["state"] == "TIMEOUT"],
            "failed": [item["path"] for item in results if item["state"] == "FAILED"],
        })
        context.close()
        browser.close()


if __name__ == "__main__":
    main()

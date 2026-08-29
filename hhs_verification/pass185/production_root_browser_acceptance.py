from __future__ import annotations

import json
import os
import time
import zipfile
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE_URL = os.environ.get("HHS_PASS185_BASE_URL", "http://127.0.0.1:8767")
EVIDENCE_DIR = Path(os.environ.get("HHS_PASS185_EVIDENCE_DIR", "/tmp/pass185-evidence"))
DOWNLOAD_DIR = EVIDENCE_DIR / "downloads"


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    console_errors: list[str] = []
    page_errors: list[str] = []
    request_failures: list[dict[str, str]] = []
    http_errors: list[dict[str, object]] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1000}, accept_downloads=True)
        page = context.new_page()
        page.set_default_timeout(30_000)
        page.set_default_navigation_timeout(120_000)

        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on(
            "requestfailed",
            lambda request: request_failures.append({
                "url": request.url,
                "failure": request.failure or "unknown",
            }),
        )
        page.on(
            "response",
            lambda response: http_errors.append({"url": response.url, "status": response.status})
            if response.status >= 500 else None,
        )

        response = page.goto(BASE_URL, wait_until="domcontentloaded")
        assert response is not None and response.ok, getattr(response, "status", None)
        page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=120_000)
        page.wait_for_selector('[data-testid="hhs-product-workspace"]', timeout=120_000)

        product_nav = page.locator('[data-testid="hhs-product-workspace"] > nav')
        product_nav.get_by_role("button", name="Workspace", exact=True).click()
        page.wait_for_selector('[data-testid="hhs-visual-runtime-os-workspace"]')
        workspace = page.locator('[data-testid="hhs-visual-runtime-os-workspace"]')
        workspace.get_by_role("button", name="Application", exact=True).click()
        page.wait_for_selector('[data-testid="pass185-application-lifecycle"]')

        page.get_by_test_id("pass185-create-calculator").click()
        editor = page.get_by_test_id("pass185-html-editor")
        source = editor.input_value()
        assert 'data-hhs-calculator="true"' in source
        marker = "<!-- PASS185_VISIBLE_EDIT_MARKER -->"
        editor.fill(source.replace("</body>", f"{marker}\n</body>"))
        assert marker in editor.input_value()

        page.get_by_test_id("pass185-save-source").click()
        page.wait_for_function(
            """() => document.querySelector('[data-testid="pass185-lifecycle-status"]')?.textContent === 'SOURCE_WITNESSED'""",
            timeout=120_000,
        )

        page.get_by_test_id("pass185-preview-source").click()
        page.wait_for_selector('[data-testid="pass185-preview-frame"]')
        page.wait_for_function(
            """() => document.querySelector('[data-testid="pass185-lifecycle-status"]')?.textContent === 'PREVIEW_READY'""",
            timeout=30_000,
        )
        frame = page.frame_locator('[data-testid="pass185-preview-frame"]')
        assert frame.locator('[data-hhs-calculator="true"]').count() == 1

        page.get_by_test_id("pass185-run-test").click()
        page.wait_for_function(
            """() => document.querySelector('[data-testid="pass185-lifecycle-status"]')?.textContent === 'PREVIEW_TEST_VERIFIED'""",
            timeout=30_000,
        )
        assert frame.locator("#display").inner_text().strip() == "15"

        with page.expect_download(timeout=30_000) as info:
            page.get_by_test_id("pass185-export-zip").click()
        download = info.value
        zip_path = DOWNLOAD_DIR / download.suggested_filename
        download.save_as(zip_path)
        assert zip_path.name == "pass185-calculator.zip"

        with zipfile.ZipFile(zip_path) as archive:
            names = set(archive.namelist())
            assert names == {"index.html", "application.manifest.json", "README.txt"}
            html = archive.read("index.html").decode("utf-8")
            manifest = json.loads(archive.read("application.manifest.json"))
            assert marker in html
            assert 'data-hhs-calculator="true"' in html
            assert manifest["schema"] == "HHS_PASS185_RUNTIME_OS_BROWSER_APPLICATION_V1"
            assert manifest["entrypoint"] == "index.html"
            assert manifest["source_saved"] is True
            assert manifest["calculator_acceptance"] == "CALCULATOR_7_PLUS_8_EQUALS_15"
            assert manifest["frontend_runtime_authority"] is False
            assert manifest["canonical_source_authority"] == "WORKSPACE_COMMAND_INGRESS_REGISTER"

        page.reload(wait_until="domcontentloaded")
        page.wait_for_selector('[data-testid="hhs-product-workspace"]', timeout=120_000)
        page.locator('[data-testid="hhs-product-workspace"] > nav').get_by_role(
            "button", name="Workspace", exact=True
        ).click()
        page.wait_for_selector('[data-testid="hhs-visual-runtime-os-workspace"]')
        page.locator('[data-testid="hhs-visual-runtime-os-workspace"]').get_by_role(
            "button", name="Application", exact=True
        ).click()
        page.wait_for_selector('[data-testid="pass185-application-lifecycle"]')
        assert marker in page.get_by_test_id("pass185-html-editor").input_value()

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

        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(250)
        for test_id in (
            "pass185-create-calculator",
            "pass185-html-editor",
            "pass185-save-source",
            "pass185-preview-source",
            "pass185-run-test",
            "pass185-export-zip",
        ):
            assert page.get_by_test_id(test_id).is_visible(), test_id

        screenshot = EVIDENCE_DIR / "pass185-production-root.png"
        page.screenshot(path=str(screenshot), full_page=True)

        elapsed_ms = round((time.monotonic() - started) * 1000)
        evidence = {
            "schema": "HHS_PASS185_I141_PRODUCTION_ROOT_BROWSER_ACCEPTANCE_V1",
            "ok": True,
            "base_url": BASE_URL,
            "elapsed_ms": elapsed_ms,
            "production_root": "hhs_backend.runtime_os_application_server:app",
            "calculator_workflow": {
                "create": True,
                "edit_html": True,
                "backend_save_witness": True,
                "preview": True,
                "calculate_7_plus_8": 15,
                "run_test": True,
                "export_zip": True,
                "zip_contents_validated": True,
                "reload_reopen_source": True,
                "reload_preview_runnable": True,
                "mobile_controls_visible": True,
            },
            "authority": {
                "frontend_runtime_authority": False,
                "canonical_save_authority": "WORKSPACE_COMMAND_INGRESS_REGISTER",
            },
            "console_errors": console_errors,
            "page_errors": page_errors,
            "request_failures": request_failures,
            "http_5xx": http_errors,
            "download": {
                "name": zip_path.name,
                "size_bytes": zip_path.stat().st_size,
                "entries": ["README.txt", "application.manifest.json", "index.html"],
            },
        }
        (EVIDENCE_DIR / "pass185-production-root.json").write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        context.close()
        browser.close()

    if page_errors or request_failures or http_errors:
        raise AssertionError({
            "page_errors": page_errors,
            "request_failures": request_failures,
            "http_5xx": http_errors,
        })


if __name__ == "__main__":
    main()

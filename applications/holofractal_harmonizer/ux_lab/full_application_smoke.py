from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import time
import traceback
import zipfile

from playwright.sync_api import expect, sync_playwright


BASE_URL = os.environ.get("HHS_FULL_APPLICATION_IDE_URL", "http://127.0.0.1:8766").rstrip("/")
EVIDENCE_PATH = Path("applications/holofractal_harmonizer/evidence/full_application_ide_smoke.json")
FAILURE_PATH = Path("applications/holofractal_harmonizer/evidence/full_application_ide_smoke_failure.json")


def phase(name: str, **details: object) -> None:
    print(json.dumps({"browser_phase": name, **details}, sort_keys=True), flush=True)


def _frame(page):
    expect(page.locator("#ide-application-frame")).to_be_visible(timeout=15_000)
    return page.frame_locator("#ide-application-frame")


def _create_with_api(page, template: str, name: str) -> None:
    phase("CREATE_PROJECT", template=template, name=name)
    page.evaluate(
        "([template, name]) => window.HHSApplicationStudio.create(template, name)",
        [template, name],
    )
    expect(page.locator("#ide-preview-panel.active")).to_be_visible(timeout=15_000)
    _frame(page)
    phase("PROJECT_READY", template=template)


def _diagnostic(page, page_errors: list[str], console_errors: list[str]) -> dict[str, object]:
    try:
        browser_state = page.evaluate("""() => ({
            url: location.href,
            title: document.title,
            readyState: document.readyState,
            bodyClass: document.body?.className || null,
            hasVisualIDE: Boolean(window.HHSVisualIDE),
            hasApplicationStudio: Boolean(window.HHSApplicationStudio),
            applicationStudio: window.HHSApplicationStudio ? {
                createsRealProjects: window.HHSApplicationStudio.creates_real_runnable_projects,
                templateCount: window.HHSApplicationStudio.templates?.length || null,
            } : null,
            simpleWorkflowVisible: Boolean(document.querySelector('#ide-simple-workflow')?.offsetParent),
            newApplicationVisible: Boolean(document.querySelector('#ide-new-app')?.offsetParent),
            galleryVisible: Boolean(document.querySelector('#ide-application-gallery')?.offsetParent),
            activePreview: Boolean(document.querySelector('#ide-preview-panel.active')),
            fileCount: document.querySelectorAll('#ide-file-tree .ide-file-item').length,
            validationState: document.querySelector('#validation-state')?.textContent || null,
            bodyPreview: (document.body?.innerText || '').slice(0, 1500),
        })""")
    except Exception as error:
        browser_state = {"diagnostic_error": f"{type(error).__name__}: {error}", "url": getattr(page, "url", None)}
    return {
        "browser_state": browser_state,
        "page_errors": page_errors,
        "console_errors": console_errors,
    }


def run() -> dict[str, object]:
    started = time.monotonic()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True, viewport={"width": 1440, "height": 960})
        page = context.new_page()
        page.set_default_timeout(15_000)
        page.set_default_navigation_timeout(45_000)
        page_errors: list[str] = []
        console_errors: list[str] = []
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)

        try:
            # The IDE intentionally maintains background runtime and assistant traffic,
            # so network-idle is not a valid readiness predicate. Bind acceptance to
            # DOM readiness followed by explicit, bounded interface assertions below.
            phase("NAVIGATE", url=BASE_URL)
            response = page.goto(f"{BASE_URL}/", wait_until="domcontentloaded", timeout=45_000)
            if response is None or not response.ok:
                raise AssertionError(f"full application root failed: {getattr(response, 'status', None)}")
            phase("DOM_READY", elapsed_ms=round((time.monotonic() - started) * 1000))

            expect(page).to_have_title("HHS Full Multimodal Application IDE")
            expect(page.locator("html")).to_have_class("hhs-harmonic-studio-theme")
            expect(page.locator("#ide-simple-workflow")).to_be_visible(timeout=20_000)
            page.wait_for_function(
                "() => window.HHSApplicationStudio?.creates_real_runnable_projects === true",
                timeout=30_000,
            )
            expect(page.locator("#ide-new-app")).to_be_visible(timeout=15_000)
            expect(page.locator("#ide-new-app")).to_contain_text("New Application")
            expect(page.locator("#ide-menu-assistant")).to_be_visible()
            expect(page.locator("#ide-file-tree .ide-file-item").first).to_have_attribute("draggable", "false")
            phase("APPLICATION_STUDIO_READY")

            # Open the beginner-facing gallery only after Application Studio has
            # completed its final control promotion. This avoids first-paint races
            # while preserving the visible button and complete dialog assertions.
            page.evaluate("() => window.HHSApplicationStudio.open()")
            expect(page.locator("#ide-application-gallery")).to_be_visible(timeout=15_000)
            page.locator('[data-application-template="pong"]').click()
            page.locator("#ide-application-name").fill("Browser Pong Acceptance")
            page.locator("#ide-create-application-project").click()
            expect(page.locator("#ide-application-gallery")).to_be_hidden(timeout=15_000)
            pong = _frame(page)
            expect(pong.locator("#game")).to_be_visible()
            expect(pong.locator("#start")).to_be_visible()
            pong.locator("#start").click()
            pong.locator("#game").hover(position={"x": 80, "y": 180})
            expect(page.locator("#ide-file-tree")).to_contain_text("index.html")
            expect(page.locator("#ide-file-tree")).to_contain_text("app.js")
            expect(page.locator("#ide-file-tree")).to_contain_text("style.css")
            phase("PONG_VERIFIED")

            # A calculator must execute real user interaction, not just display a shell.
            _create_with_api(page, "calculator", "Calculator Acceptance")
            calculator = _frame(page)
            calculator.locator('[data-value="7"]').click()
            calculator.locator('[data-value="×"]').click()
            calculator.locator('[data-value="8"]').click()
            calculator.locator('[data-value="="]').click()
            expect(calculator.locator("#display")).to_have_text("56")
            phase("CALCULATOR_VERIFIED")

            # Representative non-game and multimodal project classes must render.
            _create_with_api(page, "puzzle", "Puzzle Acceptance")
            puzzle = _frame(page)
            expect(puzzle.locator(".tile")).to_have_count(16)
            puzzle.locator("#shuffle").click()
            phase("PUZZLE_VERIFIED")

            _create_with_api(page, "document", "Document Acceptance")
            document = _frame(page)
            expect(document.locator("#editor")).to_have_attribute("contenteditable", "true")
            document.locator("#editor").click()
            document.locator("#editor").press("Control+A")
            document.locator("#editor").fill("A real editable HHS document now.")
            expect(document.locator("#words")).to_contain_text("6 words")
            phase("DOCUMENT_VERIFIED")

            _create_with_api(page, "audio", "Audio Acceptance")
            audio = _frame(page)
            expect(audio.locator(".pad")).to_have_count(4)
            expect(audio.locator("#record")).to_be_visible()
            audio.locator(".pad").first.click()
            phase("AUDIO_VERIFIED")

            _create_with_api(page, "video", "Video Acceptance")
            video = _frame(page)
            expect(video.locator("#stage")).to_be_visible()
            expect(video.locator("#record")).to_be_visible()
            expect(video.locator("#title")).to_have_value("HHS Motion")
            phase("VIDEO_VERIFIED")

            # The natural-language assistant remains available without leaving the IDE.
            page.locator("#ide-menu-assistant").click()
            expect(page.locator("#ide-assistant-drawer")).to_be_visible(timeout=15_000)
            expect(page.locator("#prompt-input")).to_be_visible()
            page.locator("#ide-assistant-close").click()
            expect(page.locator("body")).not_to_have_class("ide-assistant-open")
            expect(page.locator("#ide-assistant-drawer")).to_be_hidden()
            phase("ASSISTANT_VERIFIED")

            # Compile and inspect an actual deployable application ZIP.
            _create_with_api(page, "calculator", "Deployable Calculator")
            with page.expect_download(timeout=20_000) as download_info:
                page.locator("#ide-download-deployable-app").click()
            download = download_info.value
            with tempfile.TemporaryDirectory() as directory:
                archive_path = Path(directory) / download.suggested_filename
                download.save_as(archive_path)
                with zipfile.ZipFile(archive_path) as archive:
                    names = set(archive.namelist())
                    assert {"index.html", "application.manifest.json", "README.txt"}.issubset(names)
                    compiled = archive.read("index.html").decode("utf-8")
                    manifest = json.loads(archive.read("application.manifest.json"))
                    assert "data-hhs-compiled-source" in compiled
                    assert "<script" in compiled and "<style" in compiled
                    assert manifest["runnable_browser_application"] is True
                    assert manifest["project_local_javascript_inlined"] is True
            phase("ZIP_VERIFIED")

            # The preserved diagnostic console remains reachable as a supporting surface.
            diagnostic = context.new_page()
            diagnostic.set_default_timeout(15_000)
            diagnostic.set_default_navigation_timeout(30_000)
            diagnostic.goto(f"{BASE_URL}/runtime-console/", wait_until="domcontentloaded", timeout=30_000)
            expect(diagnostic).to_have_title("HHS Pass 174 Visual IDE")
            expect(diagnostic.locator("body")).to_contain_text("Pass 174 Harmonic Visual SDLC Runtime")
            diagnostic.close()
            phase("RUNTIME_CONSOLE_VERIFIED")

            # Give asynchronous preview errors a bounded chance to surface.
            time.sleep(0.5)
            result = {
                "ok": not page_errors and not console_errors,
                "url": BASE_URL,
                "page_errors": page_errors,
                "console_errors": console_errors,
                "projects_verified": ["pong", "calculator", "puzzle", "document", "audio", "video"],
                "assistant_integrated": True,
                "deployable_zip_verified": True,
                "runtime_console_preserved": True,
                "drag_safe_file_items": True,
                "elapsed_ms": round((time.monotonic() - started) * 1000),
            }
            if not result["ok"]:
                raise AssertionError(json.dumps(result, indent=2))
            EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
            EVIDENCE_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            phase("COMPLETE", elapsed_ms=result["elapsed_ms"])
            return result
        except Exception as error:
            failure = {
                "ok": False,
                "url": BASE_URL,
                "error": f"{type(error).__name__}: {error}",
                "traceback": traceback.format_exc(),
                "elapsed_ms": round((time.monotonic() - started) * 1000),
                **_diagnostic(page, page_errors, console_errors),
            }
            FAILURE_PATH.parent.mkdir(parents=True, exist_ok=True)
            FAILURE_PATH.write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")
            try:
                page.screenshot(
                    path="applications/holofractal_harmonizer/evidence/full_application_ide_smoke_failure.png",
                    full_page=True,
                    timeout=10_000,
                )
            except Exception:
                pass
            print(json.dumps(failure, indent=2), flush=True)
            raise
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    output = run()
    print(json.dumps(output, indent=2), flush=True)

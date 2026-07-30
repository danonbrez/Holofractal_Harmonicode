from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import time
import zipfile

from playwright.sync_api import expect, sync_playwright


BASE_URL = os.environ.get("HHS_FULL_APPLICATION_IDE_URL", "http://127.0.0.1:8766").rstrip("/")


def _frame(page):
    expect(page.locator("#ide-application-frame")).to_be_visible(timeout=20_000)
    return page.frame_locator("#ide-application-frame")


def _create_with_api(page, template: str, name: str) -> None:
    page.evaluate(
        "([template, name]) => window.HHSApplicationStudio.create(template, name)",
        [template, name],
    )
    expect(page.locator("#ide-preview-panel.active")).to_be_visible(timeout=15_000)
    _frame(page)


def run() -> dict[str, object]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True, viewport={"width": 1440, "height": 960})
        page = context.new_page()
        page_errors: list[str] = []
        console_errors: list[str] = []
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)

        page.goto(f"{BASE_URL}/", wait_until="networkidle", timeout=120_000)
        expect(page).to_have_title("HHS Full Multimodal Application IDE")
        expect(page.locator("html")).to_have_class("hhs-harmonic-studio-theme")
        expect(page.locator("#ide-simple-workflow")).to_be_visible(timeout=30_000)
        expect(page.locator("#ide-new-app")).to_contain_text("New Application")
        expect(page.locator("#ide-menu-assistant")).to_be_visible()
        expect(page.locator("#ide-file-tree .ide-file-item").first).to_have_attribute("draggable", "false")

        # Create the first real project through the visible, beginner-facing dialog.
        page.locator("#ide-new-app").click()
        expect(page.locator("#ide-application-gallery")).to_be_visible()
        page.locator('[data-application-template="pong"]').click()
        page.locator("#ide-application-name").fill("Browser Pong Acceptance")
        page.locator("#ide-create-application-project").click()
        expect(page.locator("#ide-application-gallery")).to_be_hidden()
        pong = _frame(page)
        expect(pong.locator("#game")).to_be_visible()
        expect(pong.locator("#start")).to_be_visible()
        pong.locator("#start").click()
        pong.locator("#game").hover(position={"x": 80, "y": 180})
        expect(page.locator("#ide-file-tree")).to_contain_text("index.html")
        expect(page.locator("#ide-file-tree")).to_contain_text("app.js")
        expect(page.locator("#ide-file-tree")).to_contain_text("style.css")

        # A calculator must execute real user interaction, not just display a shell.
        _create_with_api(page, "calculator", "Calculator Acceptance")
        calculator = _frame(page)
        calculator.locator('[data-value="7"]').click()
        calculator.locator('[data-value="×"]').click()
        calculator.locator('[data-value="8"]').click()
        calculator.locator('[data-value="="]').click()
        expect(calculator.locator("#display")).to_have_text("56")

        # Representative non-game and multimodal project classes must render.
        _create_with_api(page, "puzzle", "Puzzle Acceptance")
        puzzle = _frame(page)
        expect(puzzle.locator(".tile")).to_have_count(16)
        puzzle.locator("#shuffle").click()

        _create_with_api(page, "document", "Document Acceptance")
        document = _frame(page)
        expect(document.locator("#editor")).to_have_attribute("contenteditable", "true")
        document.locator("#editor").click()
        document.locator("#editor").press("Control+A")
        document.locator("#editor").fill("A real editable HHS document.")
        expect(document.locator("#words")).to_contain_text("6 words")

        _create_with_api(page, "audio", "Audio Acceptance")
        audio = _frame(page)
        expect(audio.locator(".pad")).to_have_count(4)
        expect(audio.locator("#record")).to_be_visible()
        audio.locator(".pad").first.click()

        _create_with_api(page, "video", "Video Acceptance")
        video = _frame(page)
        expect(video.locator("#stage")).to_be_visible()
        expect(video.locator("#record")).to_be_visible()
        expect(video.locator("#title")).to_have_value("HHS Motion")

        # The natural-language assistant remains available without leaving the IDE.
        page.locator("#ide-menu-assistant").click()
        expect(page.locator("#ide-assistant-drawer")).to_be_visible()
        expect(page.locator("#prompt-input")).to_be_visible()
        page.locator("#ide-assistant-close").click()
        expect(page.locator("#ide-assistant-drawer")).not_to_have_class("open")

        # Compile and inspect an actual deployable application ZIP.
        _create_with_api(page, "calculator", "Deployable Calculator")
        with page.expect_download(timeout=30_000) as download_info:
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

        # The preserved diagnostic console remains reachable as a supporting surface.
        diagnostic = context.new_page()
        diagnostic.goto(f"{BASE_URL}/runtime-console/", wait_until="domcontentloaded", timeout=60_000)
        expect(diagnostic).to_have_title("HHS Pass 174 Visual IDE")
        expect(diagnostic.locator("body")).to_contain_text("Pass 174 Harmonic Visual SDLC Runtime")

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
        }
        context.close()
        browser.close()
        if not result["ok"]:
            raise AssertionError(json.dumps(result, indent=2))
        return result


if __name__ == "__main__":
    output = run()
    evidence_path = Path("applications/holofractal_harmonizer/evidence/full_application_ide_smoke.json")
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))

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


def application_frame(page):
    expect(page.locator("#ide-application-frame")).to_be_visible(timeout=20_000)
    return page.frame_locator("#ide-application-frame")


def geometry(locator) -> dict[str, object]:
    return locator.evaluate(
        """node => {
          const summarize = element => {
            if (!(element instanceof Element)) return null;
            const style = getComputedStyle(element);
            const rect = element.getBoundingClientRect();
            return {
              tag: element.tagName,
              id: element.id || null,
              className: String(element.className || ''),
              hidden: Boolean(element.hidden),
              inert: Boolean(element.inert),
              ariaHidden: element.getAttribute('aria-hidden'),
              disabled: Boolean(element.disabled),
              rect: {
                x: rect.x,
                y: rect.y,
                width: rect.width,
                height: rect.height,
                top: rect.top,
                right: rect.right,
                bottom: rect.bottom,
                left: rect.left,
              },
              offsetWidth: element.offsetWidth,
              offsetHeight: element.offsetHeight,
              clientWidth: element.clientWidth,
              clientHeight: element.clientHeight,
              scrollWidth: element.scrollWidth,
              scrollHeight: element.scrollHeight,
              display: style.display,
              visibility: style.visibility,
              opacity: style.opacity,
              position: style.position,
              overflow: style.overflow,
              contentVisibility: style.contentVisibility,
              transform: style.transform,
              pointerEvents: style.pointerEvents,
              zIndex: style.zIndex,
            };
          };
          const ancestors = [];
          let current = node;
          while (current && ancestors.length < 14) {
            ancestors.push(summarize(current));
            current = current.parentElement;
          }
          const rect = node.getBoundingClientRect();
          const centerX = rect.left + rect.width / 2;
          const centerY = rect.top + rect.height / 2;
          const topElement = rect.width > 0 && rect.height > 0
            ? document.elementFromPoint(centerX, centerY)
            : null;
          return {
            node: summarize(node),
            ancestors,
            center: {x: centerX, y: centerY},
            elementFromPoint: summarize(topElement),
            viewport: {
              innerWidth: window.innerWidth,
              innerHeight: window.innerHeight,
              devicePixelRatio: window.devicePixelRatio,
            },
            documentClass: document.documentElement.className,
            bodyClass: document.body.className,
            activeElement: summarize(document.activeElement),
            duplicateTemplateCount: document.querySelectorAll(`[data-application-template="${node.dataset.applicationTemplate}"]`).length,
          };
        }"""
    )


def create_project(page, template: str, name: str):
    phase("CREATE_PROJECT", template=template, project_name=name)
    page.locator("#ide-new-app").click()
    gallery = page.locator("#ide-application-gallery")
    expect(gallery).to_be_visible(timeout=20_000)
    template_button = gallery.locator(f'[data-application-template="{template}"]')
    phase(
        "TEMPLATE_GEOMETRY",
        template=template,
        gallery=geometry(gallery),
        template_button=geometry(template_button),
    )
    expect(template_button).to_be_visible(timeout=20_000)
    template_button.click()
    page.locator("#ide-application-name").fill(name)
    page.locator("#ide-create-application-project").click()
    expect(gallery).to_be_hidden(timeout=20_000)
    expect(page.locator("#ide-preview-panel.active")).to_be_visible(timeout=20_000)
    frame = application_frame(page)
    phase("PROJECT_READY", template=template)
    return frame


def run() -> dict[str, object]:
    started = time.monotonic()
    current_phase = "START"
    page_errors: list[str] = []
    console_errors: list[str] = []
    failed_responses: list[dict[str, object]] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True, viewport={"width": 1440, "height": 960})
        page = context.new_page()
        page.set_default_timeout(20_000)
        page.set_default_navigation_timeout(60_000)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on(
            "response",
            lambda response: failed_responses.append({"status": response.status, "url": response.url})
            if response.status >= 400
            else None,
        )

        try:
            current_phase = "NAVIGATE"
            phase(current_phase, url=BASE_URL)
            response = page.goto(f"{BASE_URL}/", wait_until="commit", timeout=60_000)
            if response is None or not response.ok:
                raise AssertionError(f"full application root failed: {getattr(response, 'status', None)}")
            current_phase = "HTTP_COMMITTED"
            phase(current_phase, status=response.status)

            current_phase = "WAIT_RENDERED_SHELL"
            phase(current_phase)
            expect(page.locator("#ide-view")).to_be_visible(timeout=60_000)
            expect(page).to_have_title("HHS Full Multimodal Application IDE", timeout=30_000)
            expect(page.locator("html")).to_have_class("hhs-harmonic-studio-theme", timeout=30_000)
            current_phase = "STATIC_SHELL_READY"
            phase(current_phase)

            current_phase = "WAIT_APPLICATION_STUDIO"
            phase(current_phase)
            new_application = page.locator("#ide-new-app")
            expect(new_application).to_be_visible(timeout=60_000)
            expect(new_application).to_contain_text("New Application")
            expect(page.locator("#assistant-home")).to_be_visible(timeout=20_000)
            expect(page.locator("#assistant-view")).to_be_visible(timeout=20_000)
            expect(page.locator("#prompt-input")).to_be_visible(timeout=20_000)
            current_phase = "APPLICATION_STUDIO_READY"
            phase(current_phase)

            pong = create_project(page, "pong", "Browser Pong Acceptance")
            expect(pong.locator("#game")).to_be_visible()
            expect(pong.locator("#start")).to_be_visible()
            pong.locator("#start").click()
            pong.locator("#game").hover(position={"x": 80, "y": 180})
            expect(page.locator("#ide-file-tree")).to_contain_text("index.html")
            expect(page.locator("#ide-file-tree")).to_contain_text("app.js")
            expect(page.locator("#ide-file-tree")).to_contain_text("style.css")
            expect(page.locator("#ide-file-tree .ide-file-item").first).to_have_attribute("draggable", "false")
            phase("PONG_VERIFIED")

            calculator = create_project(page, "calculator", "Calculator Acceptance")
            for value in ["7", "×", "8", "="]:
                calculator.locator(f'[data-value="{value}"]').click()
            expect(calculator.locator("#display")).to_have_text("56")
            phase("CALCULATOR_VERIFIED")

            puzzle = create_project(page, "puzzle", "Puzzle Acceptance")
            expect(puzzle.locator(".tile")).to_have_count(16)
            puzzle.locator("#shuffle").click()
            phase("PUZZLE_VERIFIED")

            document = create_project(page, "document", "Document Acceptance")
            expect(document.locator("#editor")).to_have_attribute("contenteditable", "true")
            document.locator("#editor").fill("A real editable HHS document now.")
            expect(document.locator("#words")).to_contain_text("6 words")
            phase("DOCUMENT_VERIFIED")

            audio = create_project(page, "audio", "Audio Acceptance")
            expect(audio.locator(".pad")).to_have_count(4)
            expect(audio.locator("#record")).to_be_visible()
            audio.locator(".pad").first.click()
            phase("AUDIO_VERIFIED")

            video = create_project(page, "video", "Video Acceptance")
            expect(video.locator("#stage")).to_be_visible()
            expect(video.locator("#record")).to_be_visible()
            expect(video.locator("#title")).to_have_value("HHS Motion")
            phase("VIDEO_VERIFIED")

            page.locator("#assistant-home").click()
            expect(page.locator("#assistant-view")).to_be_visible(timeout=20_000)
            expect(page.locator("#prompt-input")).to_be_visible(timeout=20_000)
            page.locator("#ide-home").click()
            expect(page.locator("#ide-view")).to_be_visible(timeout=20_000)
            phase("ASSISTANT_VERIFIED")

            create_project(page, "calculator", "Deployable Calculator")
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
            phase("ZIP_VERIFIED")

            diagnostic = context.new_page()
            diagnostic_response = diagnostic.goto(
                f"{BASE_URL}/runtime-console/",
                wait_until="commit",
                timeout=45_000,
            )
            if diagnostic_response is None or not diagnostic_response.ok:
                raise AssertionError("runtime console did not return a successful response")
            expect(diagnostic.locator("body")).to_contain_text(
                "Pass 174 Harmonic Visual SDLC Runtime",
                timeout=30_000,
            )
            expect(diagnostic).to_have_title("HHS Pass 174 Visual IDE", timeout=20_000)
            diagnostic.close()
            phase("RUNTIME_CONSOLE_VERIFIED")

            time.sleep(0.5)
            result = {
                "ok": not page_errors and not console_errors and not failed_responses,
                "url": BASE_URL,
                "page_errors": page_errors,
                "console_errors": console_errors,
                "failed_responses": failed_responses,
                "projects_verified": ["pong", "calculator", "puzzle", "document", "audio", "video"],
                "assistant_integrated": True,
                "assistant_surface": "explorer-and-conversation",
                "deployable_zip_verified": True,
                "runtime_console_preserved": True,
                "drag_safe_file_items": True,
                "dom_driven_acceptance": True,
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
                "phase": current_phase,
                "error": f"{type(error).__name__}: {error}",
                "traceback": traceback.format_exc(),
                "elapsed_ms": round((time.monotonic() - started) * 1000),
                "page_errors": page_errors,
                "console_errors": console_errors,
                "failed_responses": failed_responses,
            }
            FAILURE_PATH.parent.mkdir(parents=True, exist_ok=True)
            FAILURE_PATH.write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(failure, indent=2), flush=True)
            try:
                page.screenshot(
                    path="applications/holofractal_harmonizer/evidence/full_application_ide_smoke_failure.png",
                    full_page=True,
                    timeout=5_000,
                )
            except Exception:
                pass
            raise
        finally:
            try:
                context.close()
            except Exception:
                pass
            try:
                browser.close()
            except Exception:
                pass


if __name__ == "__main__":
    print(json.dumps(run(), indent=2), flush=True)

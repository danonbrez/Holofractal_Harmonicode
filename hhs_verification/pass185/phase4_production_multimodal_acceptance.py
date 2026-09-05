from __future__ import annotations

import argparse
import json
import time
import zipfile
from pathlib import Path
from typing import Any

from playwright.sync_api import Browser, BrowserContext, Download, Page, sync_playwright

from hhs_verification.pass185.phase2_degradation_negative_acceptance import (
    ProductionServer,
    free_port,
)

ENTRYPOINT = "hhs_backend.runtime_os_application_server:app"


def open_workspace(page: Page) -> None:
    page.locator('[data-testid="hhs-product-workspace"] > nav').get_by_role(
        "button", name="Workspace", exact=True
    ).click()
    page.wait_for_selector('[data-testid="hhs-visual-runtime-os-workspace"]')


def open_tab(page: Page, name: str) -> None:
    page.locator('[data-testid="hhs-visual-runtime-os-workspace"]').get_by_role(
        "button", name=name, exact=True
    ).click()


def launch_page(context: BrowserContext, base_url: str) -> Page:
    page = context.new_page()
    page.set_default_timeout(30_000)
    page.set_default_navigation_timeout(90_000)
    response = page.goto(base_url + "/", wait_until="domcontentloaded")
    assert response is not None and response.ok
    page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
    page.wait_for_selector('[data-testid="hhs-product-workspace"]', timeout=60_000)
    open_workspace(page)
    return page


def wait_mm_status(page: Page, expected: str, timeout_ms: int = 45_000) -> str:
    page.wait_for_function(
        """expected => document.querySelector('[data-testid="pass185-mm-status"]')?.textContent === expected""",
        arg=expected,
        timeout=timeout_ms,
    )
    return page.get_by_test_id("pass185-mm-status").inner_text()


def wait_app_status(page: Page, expected: str, timeout_ms: int = 45_000) -> str:
    page.wait_for_function(
        """expected => document.querySelector('[data-testid="pass185-lifecycle-status"]')?.textContent === expected""",
        arg=expected,
        timeout=timeout_ms,
    )
    return page.get_by_test_id("pass185-lifecycle-status").inner_text()


def save_download(download: Download, evidence_dir: Path, label: str) -> Path:
    target = evidence_dir / "downloads" / f"{label}-{download.suggested_filename}"
    target.parent.mkdir(parents=True, exist_ok=True)
    download.save_as(target)
    return target


def inspect_multimodal_zip(
    path: Path,
    *,
    mode: str,
    modality: str,
    source_name: str,
) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        assert names == {source_name, "application.manifest.json", "README.txt"}, names
        manifest = json.loads(archive.read("application.manifest.json"))
        assert manifest["schema"] == "HHS_PASS185_MULTIMODAL_EXPORT_MANIFEST_V1"
        assert manifest["mode"] == mode
        assert manifest["modality"] == modality
        assert manifest["source_name"] == source_name
        assert manifest["frontend_runtime_authority"] is False
        assert manifest["browser_preview_is_canonical_source"] is False
        assert manifest["calculator_phase1_invariant_preserved"] is True
        source = archive.read(source_name)
        assert source
        return {
            "names": sorted(names),
            "manifest": manifest,
            "source_bytes": len(source),
            "source_prefix_hex": source[:16].hex(),
        }


def witness_and_export(
    page: Page,
    evidence_dir: Path,
    *,
    mode: str,
    modality: str,
    source_name: str,
) -> dict[str, Any]:
    page.get_by_test_id("pass185-mm-witness").click()
    witnessed = wait_mm_status(page, f"{mode.upper()}_SOURCE_WITNESSED")
    receipt = page.get_by_test_id("pass185-mm-receipt").inner_text()
    assert receipt != "no receipt", receipt

    with page.expect_download(timeout=30_000) as download_info:
        page.get_by_test_id("pass185-mm-export").click()
    export_status = wait_mm_status(page, f"{mode.upper()}_EXPORT_READY")
    path = save_download(download_info.value, evidence_dir, f"phase4-{mode}")
    archive = inspect_multimodal_zip(
        path,
        mode=mode,
        modality=modality,
        source_name=source_name,
    )
    return {
        "witness_status": witnessed,
        "receipt_visible": receipt,
        "export_status": export_status,
        "archive": archive,
        "download": path.name,
    }


def document_workflow(page: Page, evidence_dir: Path) -> dict[str, Any]:
    page.get_by_test_id("pass185-mm-mode-document").click()
    editor = page.get_by_test_id("pass185-mm-document-editor")
    marker = "Phase 4 document: edited through the visible production workspace."
    editor.fill(marker)
    preview = page.get_by_test_id("pass185-mm-document-preview")
    assert preview.inner_text() == marker
    page.get_by_test_id("pass185-mm-verify").click()
    verified = wait_mm_status(page, "DOCUMENT_PREVIEW_VERIFIED")
    export = witness_and_export(
        page,
        evidence_dir,
        mode="document",
        modality="TEXT",
        source_name="pass185-document.txt",
    )
    return {"verified": verified, "preview": preview.inner_text(), **export}


def game_workflow(page: Page, evidence_dir: Path) -> dict[str, Any]:
    page.get_by_test_id("pass185-mm-mode-game").click()
    position = page.get_by_test_id("pass185-mm-game-position")
    assert position.inner_text() == "x=1 y=1"
    page.get_by_test_id("pass185-mm-game-right").click()
    page.get_by_test_id("pass185-mm-game-down").click()
    assert position.inner_text() == "x=2 y=2"
    page.get_by_test_id("pass185-mm-verify").click()
    verified = wait_mm_status(page, "GAME_INTERACTION_VERIFIED")
    export = witness_and_export(
        page,
        evidence_dir,
        mode="game",
        modality="JSON",
        source_name="pass185-game.json",
    )
    return {"verified": verified, "position": position.inner_text(), **export}


def graphics_workflow(page: Page, evidence_dir: Path) -> dict[str, Any]:
    page.get_by_test_id("pass185-mm-mode-graphics").click()
    slider = page.get_by_test_id("pass185-mm-graphics-size")
    slider.focus()
    page.keyboard.press("End")
    assert slider.input_value() == "80"
    label = page.get_by_test_id("pass185-mm-graphics-label")
    label.fill("PHASE4")
    preview = page.get_by_test_id("pass185-mm-graphics-preview")
    html = preview.inner_html()
    assert 'r="80"' in html
    assert "PHASE4" in html
    page.get_by_test_id("pass185-mm-verify").click()
    verified = wait_mm_status(page, "GRAPHICS_RENDER_VERIFIED")
    export = witness_and_export(
        page,
        evidence_dir,
        mode="graphics",
        modality="IMAGE",
        source_name="pass185-graphic.svg",
    )
    return {"verified": verified, "size": slider.input_value(), "label": label.input_value(), **export}


def audio_workflow(page: Page, evidence_dir: Path) -> dict[str, Any]:
    page.get_by_test_id("pass185-mm-mode-audio").click()
    page.get_by_test_id("pass185-mm-audio-frequency").fill("523")
    page.get_by_test_id("pass185-mm-audio-duration").fill("300")
    page.get_by_test_id("pass185-mm-audio-generate").click()
    wait_mm_status(page, "AUDIO_PREVIEW_READY")
    bytes_text = page.get_by_test_id("pass185-mm-audio-bytes").inner_text()
    assert "RIFF/WAVE" in bytes_text
    src = page.get_by_test_id("pass185-mm-audio-player").get_attribute("src")
    assert src and src.startswith("blob:"), src
    page.get_by_test_id("pass185-mm-verify").click()
    verified = wait_mm_status(page, "AUDIO_PREVIEW_VERIFIED")
    export = witness_and_export(
        page,
        evidence_dir,
        mode="audio",
        modality="AUDIO",
        source_name="pass185-tone.wav.json",
    )
    assert export["archive"]["source_prefix_hex"].startswith("52494646")
    return {"verified": verified, "bytes": bytes_text, **export}


def audiovisual_workflow(page: Page, evidence_dir: Path) -> dict[str, Any]:
    page.get_by_test_id("pass185-mm-mode-video").click()
    frame = page.get_by_test_id("pass185-mm-video-frame")
    assert frame.inner_text() == "GENESIS"
    page.get_by_test_id("pass185-mm-video-step").click()
    assert frame.inner_text() == "TRANSFORM"
    page.get_by_test_id("pass185-mm-video-play").click()
    wait_mm_status(page, "AUDIOVISUAL_PLAYING")
    page.wait_for_timeout(600)
    page.get_by_test_id("pass185-mm-video-play").click()
    paused = wait_mm_status(page, "AUDIOVISUAL_PAUSED")
    current = frame.inner_text()
    assert current in {"GENESIS", "TRANSFORM", "CLOSURE"}
    page.get_by_test_id("pass185-mm-verify").click()
    verified = wait_mm_status(page, "AUDIOVISUAL_REEL_VERIFIED")
    export = witness_and_export(
        page,
        evidence_dir,
        mode="video",
        modality="VIDEO",
        source_name="pass185-audiovisual-reel.json",
    )
    return {"verified": verified, "paused": paused, "frame": current, **export}


def calculator_baseline(page: Page, evidence_dir: Path) -> dict[str, Any]:
    open_tab(page, "Application")
    page.wait_for_selector('[data-testid="pass185-application-lifecycle"]')
    page.get_by_test_id("pass185-create-calculator").click()
    editor = page.get_by_test_id("pass185-html-editor")
    source = editor.input_value()
    marker = "PASS185_PHASE4_CALCULATOR_BASELINE"
    editor.fill(source.replace("</body>", f"<!-- {marker} -->\\n</body>"))

    page.get_by_test_id("pass185-save-source").click()
    witnessed = wait_app_status(page, "SOURCE_WITNESSED")
    page.get_by_test_id("pass185-preview-source").click()
    wait_app_status(page, "PREVIEW_READY")
    page.get_by_test_id("pass185-run-test").click()
    verified = wait_app_status(page, "PREVIEW_TEST_VERIFIED")

    with page.expect_download(timeout=30_000) as download_info:
        page.get_by_test_id("pass185-export-zip").click()
    path = save_download(download_info.value, evidence_dir, "phase4-calculator")
    with zipfile.ZipFile(path) as archive:
        exported = archive.read("index.html").decode("utf-8")
        manifest = json.loads(archive.read("application.manifest.json"))
        assert marker in exported
        assert manifest["calculator_acceptance"] == "CALCULATOR_7_PLUS_8_EQUALS_15"
        assert manifest["frontend_runtime_authority"] is False
    return {
        "witnessed": witnessed,
        "verified": verified,
        "download": path.name,
        "acceptance": "CALCULATOR_7_PLUS_8_EQUALS_15",
    }


def run_browser(browser: Browser, base_url: str, evidence_dir: Path) -> dict[str, Any]:
    context = browser.new_context(
        viewport={"width": 1365, "height": 1000},
        accept_downloads=True,
    )
    page = launch_page(context, base_url)

    open_tab(page, "Multimodal")
    page.wait_for_selector('[data-testid="pass185-multimodal-lifecycle"]')
    document = document_workflow(page, evidence_dir)
    game = game_workflow(page, evidence_dir)
    graphics = graphics_workflow(page, evidence_dir)
    audio = audio_workflow(page, evidence_dir)
    video = audiovisual_workflow(page, evidence_dir)
    calculator = calculator_baseline(page, evidence_dir)

    page.screenshot(
        path=str(evidence_dir / "phase4-production-multimodal.png"),
        full_page=True,
    )
    context.close()
    return {
        "document": document,
        "game": game,
        "graphics": graphics,
        "audio": audio,
        "video": video,
        "calculator": calculator,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", required=True)
    args = parser.parse_args()
    evidence_dir = Path(args.evidence_dir).resolve()
    evidence_dir.mkdir(parents=True, exist_ok=True)

    port = free_port()
    server = ProductionServer(
        port,
        evidence_dir,
        env={
            "HHS_COGNITION_AUTO_TICK": "0",
            "HHS_DISABLE_C_AUTOBUILD": "1",
        },
        label="phase4-production-server",
    )
    started_server = server.start()
    started = time.monotonic()

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            workflows = run_browser(browser, server.base_url, evidence_dir)
            browser.close()

        result = {
            "schema": "HHS_PASS185_I141_PHASE4_PRODUCTION_MULTIMODAL_ACCEPTANCE_V1",
            "ok": True,
            "classification": "HHS_PASS_185_PHASE4_PRODUCTION_MULTIMODAL_VERIFIED",
            "entrypoint": ENTRYPOINT,
            "server": started_server,
            "workflows": workflows,
            "source_witness_authority": "WORKSPACE_COMMAND_INGRESS_REGISTER",
            "frontend_runtime_authority": False,
            "browser_media_preview_authority": False,
            "terminal_pass185_completion_claimed": False,
            "elapsed_ms": round((time.monotonic() - started) * 1000),
        }
        (evidence_dir / "phase4-production-multimodal.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(result, indent=2, sort_keys=True))
    finally:
        server.stop()


if __name__ == "__main__":
    main()

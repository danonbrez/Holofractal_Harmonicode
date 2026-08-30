from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, sync_playwright

from hhs_verification.pass185.phase2_degradation_negative_acceptance import (
    ProductionServer,
    free_port,
)
from hhs_verification.pass185.phase4_production_multimodal_acceptance import (
    launch_page,
    open_tab,
)

ENTRYPOINT = "hhs_backend.runtime_os_application_server:app"


def wait_text(page: Page, test_id: str, expected: str, timeout_ms: int = 60_000) -> str:
    page.wait_for_function(
        """([testId, expected]) =>
            document.querySelector('[data-testid="' + testId + '"]')?.textContent?.trim() === expected""",
        arg=[test_id, expected],
        timeout=timeout_ms,
    )
    return page.get_by_test_id(test_id).inner_text().strip()


def wait_not_contains(page: Page, test_id: str, rejected: str, timeout_ms: int = 60_000) -> str:
    page.wait_for_function(
        """([testId, rejected]) => {
            const text = document.querySelector('[data-testid="' + testId + '"]')?.textContent?.trim()
            return Boolean(text && !text.includes(rejected))
        }""",
        arg=[test_id, rejected],
        timeout=timeout_ms,
    )
    return page.get_by_test_id(test_id).inner_text().strip()


def workbench_flow(page: Page) -> dict[str, Any]:
    page.get_by_test_id("pass185-new-file").click()
    assert page.get_by_test_id("pass185-source-file-name").input_value() == "untitled.hhs"
    assert page.get_by_test_id("pass185-workbench-source-editor").input_value() == ""

    payload = "GENESIS\nPASS185 CUMULATIVE WORKBENCH\n1+2*3/4\n"
    page.get_by_test_id("pass185-upload-input").set_input_files(
        {
            "name": "pass185-uploaded.hhs",
            "mimeType": "text/plain",
            "buffer": payload.encode("utf-8"),
        }
    )
    assert page.get_by_test_id("pass185-source-file-name").input_value() == "pass185-uploaded.hhs"
    assert page.get_by_test_id("pass185-workbench-source-editor").input_value() == payload

    page.get_by_test_id("pass185-workbench-save").click()
    page.get_by_test_id("pass185-workspace-object").first.wait_for(timeout=60_000)
    object_count = page.get_by_test_id("pass185-workspace-object").count()
    assert object_count >= 1
    page.get_by_test_id("pass185-workspace-object").last.click()

    page.get_by_test_id("pass185-workbench-build").click()
    artifact_state = wait_not_contains(page, "pass185-workbench-artifact-state", "none", 90_000)
    build_summary = page.get_by_test_id("pass185-last-result-summary").inner_text()
    assert "Created" in build_summary and "artifact" in build_summary, build_summary

    page.get_by_test_id("pass185-workbench-create-emulator").click()
    emulator_state = wait_not_contains(page, "pass185-workbench-emulator-state", "none", 90_000)
    before = page.get_by_test_id("pass185-workbench-emulator-progress").inner_text()
    page.get_by_test_id("pass185-workbench-run").click()
    transition = page.wait_for_function(
        """before => {
            const text = document.querySelector('[data-testid="pass185-workbench-emulator-progress"]')?.textContent?.trim()
            return text && text !== before ? text : false
        }""",
        arg=before,
        timeout=90_000,
    ).json_value()
    after = str(transition)
    assert after and after != before, {"before": before, "after": after}

    return {
        "new_file": True,
        "upload_source_name": "pass185-uploaded.hhs",
        "upload_bytes": len(payload.encode("utf-8")),
        "explorer_object_count": object_count,
        "artifact_state": artifact_state,
        "emulator_state": emulator_state,
        "run_before": before,
        "run_after": after,
    }


def terminal_flow(page: Page) -> dict[str, Any]:
    open_tab(page, "Terminal")
    page.get_by_test_id("pass185-terminal-panel").wait_for()
    page.get_by_test_id("pass185-terminal-open").click()
    ready = wait_text(page, "pass185-terminal-state", "READY", 60_000)
    page.get_by_test_id("pass185-terminal-ping").click()
    pong = wait_text(page, "pass185-terminal-state", "PONG", 30_000)
    message = page.get_by_test_id("pass185-terminal-message").inner_text()
    assert "HHS_PASS_175_TERMINAL_WS_PONG" in message
    page.get_by_test_id("pass185-terminal-close").click()
    closed = wait_text(page, "pass185-terminal-state", "CLOSED", 15_000)
    return {
        "open": ready,
        "ping": pong,
        "close": closed,
        "parallel_state_authority": False,
    }


def governed_job_flow(page: Page) -> dict[str, Any]:
    open_tab(page, "Jobs")
    page.get_by_test_id("pass185-hydration-job-panel").wait_for()

    page.get_by_test_id("pass185-hydration-create").click()
    created_stage = wait_text(page, "pass185-hydration-job-stage", "QUEUED", 90_000)
    first_job = page.get_by_test_id("pass185-hydration-job-id").inner_text().strip()
    assert first_job.startswith("P191-"), first_job

    page.get_by_test_id("pass185-hydration-run").click()
    running = wait_text(page, "pass185-hydration-job-stage", "RUNNING", 120_000)
    page.get_by_test_id("pass185-hydration-cancel").click()
    cancelled = wait_text(page, "pass185-hydration-job-stage", "CANCELLED", 60_000)
    assert page.get_by_test_id("pass185-hydration-last-action").inner_text().strip() == "JOB_CANCELLED"
    cancelled_json = json.loads(page.get_by_test_id("pass185-hydration-job-json").inner_text())
    assert cancelled_json["stage"] == "CANCELLED"
    assert cancelled_json["history"][-1]["checkpoint"] == "CANCELLED_BY_AUTHORIZED_REQUEST"

    page.get_by_test_id("pass185-hydration-recover").click()
    recovered = wait_text(page, "pass185-hydration-job-stage", "QUEUED", 90_000)
    second_job = page.get_by_test_id("pass185-hydration-job-id").inner_text().strip()
    assert second_job.startswith("P191-") and second_job != first_job, (first_job, second_job)
    assert page.get_by_test_id("pass185-hydration-last-action").inner_text().strip() == "RECOVERY_JOB_QUEUED"

    return {
        "created_stage": created_stage,
        "running_stage": running,
        "cancelled_stage": cancelled,
        "cancel_checkpoint": cancelled_json["history"][-1]["checkpoint"],
        "recovered_stage": recovered,
        "first_job": first_job,
        "replacement_job": second_job,
        "frontend_job_authority": False,
    }


def browser_acceptance(base_url: str, evidence_dir: Path) -> dict[str, Any]:
    console_errors: list[str] = []
    page_errors: list[str] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1365, "height": 1000})
        page = launch_page(context, base_url)
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on("pageerror", lambda error: page_errors.append(str(error)))

        workbench = workbench_flow(page)
        terminal = terminal_flow(page)
        jobs = governed_job_flow(page)

        page.screenshot(
            path=str(evidence_dir / "phase6-cumulative-workspace-jobs.png"),
            full_page=True,
        )
        context.close()
        browser.close()

    assert not page_errors, page_errors
    return {
        "workbench": workbench,
        "terminal": terminal,
        "jobs": jobs,
        "page_errors": page_errors,
        "console_errors": console_errors,
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
        label="phase6-cumulative-production-server",
    )
    started_server = server.start()
    started = time.monotonic()
    try:
        browser = browser_acceptance(server.base_url, evidence_dir)
        result = {
            "schema": "HHS_PASS185_I141_PHASE6_CUMULATIVE_GAP_ACCEPTANCE_V1",
            "ok": True,
            "classification": "HHS_PASS_185_PHASE6_WORKSPACE_JOB_GAPS_VERIFIED",
            "entrypoint": ENTRYPOINT,
            "server": started_server,
            "browser": browser,
            "pass191_running_job_cancellation": True,
            "pass191_recovery_replacement_job": True,
            "pass175_terminal_authority_reused": True,
            "frontend_runtime_authority": False,
            "parallel_vm81_authority": False,
            "terminal_pass185_completion_claimed": False,
            "elapsed_ms": round((time.monotonic() - started) * 1000),
        }
        (evidence_dir / "phase6-cumulative-gap-acceptance.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(result, indent=2, sort_keys=True))
    finally:
        server.stop()


if __name__ == "__main__":
    main()

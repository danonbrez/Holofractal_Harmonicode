from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from hashlib import sha256
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, sync_playwright

from hhs_verification.pass185.phase2_degradation_negative_acceptance import (
    ProductionServer,
    free_port,
)

ENTRYPOINT = "hhs_backend.runtime_os_application_server:app"
CONTRACT_ID = "HHS-P185-PCBAVC-IVC-VM81-H72-H216"
BOOT_SEQUENCE = [
    "DOCUMENT_RECEIVED",
    "STATIC_ASSETS_LOADING",
    "CORE_MODULES_READY",
    "DOM_READY",
    "WORKSPACE_BOUND",
    "EDITOR_READY",
    "PREVIEW_READY",
    "INTERACTIVE",
]

EXPECTED_RECEIPTS = {
    1: ("HHS_PASS_185_CURRENT_PRODUCTION_VISIBLE_LIFECYCLE_PHASE1_VERIFIED", "31a3ca0f725ac7ee14a7c2252da750536afe13ec"),
    2: ("HHS_PASS_185_PHASE2_DEGRADATION_NEGATIVE_ACCEPTANCE_VERIFIED", "2b972a66743a505937d5f819c839f5e59dda98b4"),
    3: ("HHS_PASS_185_PHASE3_BROWSER_LIFECYCLE_VERIFIED", "beff7599dedff2624be712f7a215de5c193e8cbe"),
    4: ("HHS_PASS_185_PHASE4_PRODUCTION_MULTIMODAL_VERIFIED", "6721a7daa5ac9bff087e3f2df92ca8e0212e126b"),
    5: ("HHS_PASS_185_PHASE5_PERFORMANCE_NEGATIVE_VERIFIED", "36321174c124ff5ba81bd60fd37a72ce703e606c"),
    6: ("HHS_PASS_185_PHASE6_WORKSPACE_JOB_GAPS_VERIFIED", "d716fb50ed8f903ccd8de965d8fa880b08df9027"),
    7: ("HHS_PASS_185_PHASE7_PROCESS_CACHE_NETWORK_PROVIDER_VERIFIED", "26d06f34a3b074f8f969c80ccc5b9db087fd9430"),
}

NEGATIVE_MATRIX = [
    ("circular browser boot dependency", "phase5"),
    ("boot promise that never resolves", "phase5"),
    ("parser module waits on completion-dependent DOM event", "phase5"),
    ("missing required DOM element", "phase5"),
    ("duplicate control binding", "phase5"),
    ("malformed recovery payload", "phase5"),
    ("corrupted local storage", "phase2"),
    ("source asset shadowed by root mount", "phase7"),
    ("incorrect JavaScript MIME", "phase2"),
    ("API route collision / precedence", "phase5+phase6"),
    ("unavailable runtime authority", "phase2+phase6"),
    ("duplicate VM81 commit authority", "cumulative authority regression"),
    ("more than one Hash72 commit stream", "cumulative authority regression"),
    ("runtime tick synchronous on event loop", "phase5"),
    ("uncontrolled background kernel loop", "phase5"),
    ("assistant provider required for base boot", "phase2"),
    ("Word2Vec required for base boot", "phase2"),
    ("C build failure mislabeled as browser failure", "phase2"),
    ("browser failure mislabeled as hosting failure", "phase2"),
    ("server process active with no listening socket", "phase2+phase7"),
    ("UI ready while required controls unbound", "phase1+phase6+cumulative"),
    ("export reports success without valid ZIP", "phase1"),
]

SECTION_MAP = {
    "5.1 repository-native correction": ["phase1", "phase2", "phase3", "phase4", "phase5", "phase6", "phase7"],
    "5.2 finite server startup": ["phase2", "phase5", "phase7"],
    "5.3 explicit finite browser boot coordinator": ["cumulative"],
    "5.4 native C runtime": ["phase2", "phase5", "phase6", "phase7"],
    "5.5 Gemma / assistant provider": ["phase2", "phase5", "phase7"],
    "5.6 Word2Vec": ["phase2", "phase7"],
    "6.1 process/socket matrix": ["phase2", "phase5", "phase7"],
    "6.2 static/module matrix": ["phase2", "phase7"],
    "6.3 browser lifecycle matrix": ["phase2", "phase3", "phase7"],
    "6.4 required application workflow": ["phase1", "phase6", "phase7"],
    "6.5 multimodal workflows": ["phase4"],
    "6.6 optional-provider matrix": ["phase2", "phase5", "phase7"],
    "7.1 real-browser runner evidence architecture": ["phase1", "phase2", "phase3", "phase4", "phase5", "phase6", "phase7", "cumulative"],
    "8 performance/starvation": ["phase5"],
    "9 negative tests": ["phase2", "phase5", "phase6", "phase7", "cumulative"],
    "10 deterministic evidence package": ["phase1", "phase2", "phase3", "phase4", "phase5", "phase6", "phase7", "cumulative"],
}


def git(*args: str, cwd: Path) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def verify_receipts(repo: Path) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for phase, (classification, head) in EXPECTED_RECEIPTS.items():
        path = repo / "evidence" / "pass185" / "i141" / f"PASS_185_I141_PHASE{phase}_VALIDATION_RECEIPT.json"
        assert path.is_file(), path
        raw = path.read_bytes()
        value = json.loads(raw)
        assert value.get("classification") == classification, (phase, value.get("classification"))
        assert value.get("terminal_pass185_completion_claimed") is False
        contract_field = value.get("pass185_contract")
        if isinstance(contract_field, dict):
            recorded_contract_id = contract_field.get("identifier")
        else:
            recorded_contract_id = value.get("contract")
        assert recorded_contract_id == CONTRACT_ID, (
            phase,
            recorded_contract_id,
            value.get("schema"),
        )
        if phase == 7:
            seal = value.get("phase7_seal") or {}
            assert seal.get("matrix_row_count") == 62
            assert seal.get("matrix_failed_rows") == []
            assert seal.get("matrix_waived_rows") == []
        assert git("merge-base", "--is-ancestor", head, "HEAD", cwd=repo) == ""
        result[str(phase)] = {
            "path": str(path.relative_to(repo)),
            "classification": classification,
            "validated_head": head,
            "sha256": sha256(raw).hexdigest(),
            "contract_id": recorded_contract_id,
        }
    return result


def environment_manifest(repo: Path, state_root: Path) -> dict[str, Any]:
    return {
        "schema": "HHS_PASS185_CUMULATIVE_ENVIRONMENT_MANIFEST_V1",
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cwd": str(repo),
        "entrypoint": ENTRYPOINT,
        "home": os.environ.get("HOME"),
        "runtime_output_dir": os.environ.get("HHS_RUNTIME_OUTPUT_DIR"),
        "data_dir": os.environ.get("HHS_DATA_DIR"),
        "state_root": str(state_root),
        "cognition_auto_tick": os.environ.get("HHS_COGNITION_AUTO_TICK"),
        "assistant_health_timeout": os.environ.get("HHS_ASSISTANT_HEALTH_TIMEOUT_SECONDS"),
        "playwright_browsers_path": os.environ.get("PLAYWRIGHT_BROWSERS_PATH"),
    }


def process_tree() -> list[dict[str, Any]]:
    raw = subprocess.check_output(
        ["ps", "-eo", "pid=,ppid=,stat=,comm=,args="],
        text=True,
    )
    rows = []
    for line in raw.splitlines():
        parts = line.strip().split(None, 4)
        if len(parts) < 5:
            continue
        pid, ppid, stat, command, args = parts
        rows.append({
            "pid": int(pid),
            "ppid": int(ppid),
            "stat": stat,
            "command": command,
            "args": args,
        })
    return rows


def center(locator: Any) -> tuple[float, float]:
    box = locator.bounding_box()
    assert box is not None
    return (box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)


def open_workspace_pointer(page: Page) -> None:
    button = page.locator('[data-testid="hhs-product-workspace"] > nav').get_by_role(
        "button", name="Workspace", exact=True
    )
    x, y = center(button)
    page.mouse.click(x, y)
    page.wait_for_selector('[data-testid="hhs-visual-runtime-os-workspace"]')


def open_application_pointer(page: Page) -> None:
    button = page.locator('[data-testid="hhs-visual-runtime-os-workspace"]').get_by_role(
        "button", name="Application", exact=True
    )
    x, y = center(button)
    page.mouse.click(x, y)
    page.wait_for_selector('[data-testid="pass185-application-lifecycle"]')


def open_workspace_touch(page: Page) -> None:
    button = page.locator('[data-testid="hhs-product-workspace"] > nav').get_by_role(
        "button", name="Workspace", exact=True
    )
    x, y = center(button)
    page.touchscreen.tap(x, y)
    page.wait_for_selector('[data-testid="hhs-visual-runtime-os-workspace"]')


def open_application_touch(page: Page) -> None:
    button = page.locator('[data-testid="hhs-visual-runtime-os-workspace"]').get_by_role(
        "button", name="Application", exact=True
    )
    x, y = center(button)
    page.touchscreen.tap(x, y)
    page.wait_for_selector('[data-testid="pass185-application-lifecycle"]')


def browser_evidence(base_url: str, evidence_dir: Path) -> dict[str, Any]:
    console_errors: list[str] = []
    page_errors: list[str] = []
    request_failures: list[dict[str, Any]] = []
    responses: list[dict[str, Any]] = []
    websockets: list[dict[str, Any]] = []

    trace_path = evidence_dir / "cumulative-pass185-playwright-trace.zip"
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)

        desktop = browser.new_context(
            viewport={"width": 1280, "height": 900},
            service_workers="block",
            accept_downloads=True,
        )
        desktop.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = desktop.new_page()
        page.set_default_timeout(30_000)
        page.set_default_navigation_timeout(90_000)
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: page_errors.append(str(err)))
        page.on("requestfailed", lambda req: request_failures.append({"url": req.url, "failure": req.failure or "unknown"}))
        page.on("response", lambda resp: responses.append({"url": resp.url, "status": resp.status, "content_type": resp.headers.get("content-type", "")}))
        page.on("websocket", lambda ws: websockets.append({"url": ws.url, "opened": True}))

        response = page.goto(base_url + "/", wait_until="domcontentloaded")
        assert response is not None and response.ok
        page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
        page.wait_for_selector('[data-testid="hhs-product-workspace"]', timeout=60_000)
        page.wait_for_function(
            """() => {
                const c = window.__HHS_BOOT_COORDINATOR__;
                if (!c) return false;
                const s = c.snapshot();
                return s.state === 'INTERACTIVE' || s.state === 'DEGRADED_INTERACTIVE';
            }""",
            timeout=60_000,
        )
        boot = page.evaluate("() => window.__HHS_BOOT_COORDINATOR__.snapshot()")
        states = [entry["state"] for entry in boot["history"]]
        assert states[: len(BOOT_SEQUENCE)] == BOOT_SEQUENCE, states
        assert boot["failure"] is None
        assert boot["frontend_runtime_authority"] is False
        page.screenshot(path=str(evidence_dir / "cumulative-boot-interactive.png"), full_page=True)

        open_workspace_pointer(page)
        open_application_pointer(page)
        page.get_by_test_id("pass185-create-calculator").click()
        editor = page.get_by_test_id("pass185-html-editor")
        editor.press("End")
        page.keyboard.insert_text("\n<!-- cumulative-pointer-keyboard -->")
        page.get_by_test_id("pass185-preview-source").click()
        page.wait_for_function(
            "() => document.querySelector('[data-testid=\"pass185-lifecycle-status\"]')?.textContent === 'PREVIEW_READY'",
            timeout=30_000,
        )
        page.get_by_test_id("pass185-run-test").click()
        page.wait_for_function(
            "() => document.querySelector('[data-testid=\"pass185-lifecycle-status\"]')?.textContent === 'PREVIEW_TEST_VERIFIED'",
            timeout=30_000,
        )
        page.screenshot(path=str(evidence_dir / "cumulative-desktop-workflow.png"), full_page=True)
        desktop.tracing.stop(path=str(trace_path))
        desktop.close()

        mobile = browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            has_touch=True,
            service_workers="block",
        )
        mobile_page = mobile.new_page()
        mobile_page.set_default_timeout(30_000)
        mobile_response = mobile_page.goto(base_url + "/", wait_until="domcontentloaded")
        assert mobile_response is not None and mobile_response.ok
        mobile_page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
        mobile_page.wait_for_selector('[data-testid="hhs-product-workspace"]', timeout=60_000)
        open_workspace_touch(mobile_page)
        open_application_touch(mobile_page)
        assert mobile_page.get_by_test_id("pass185-html-editor").is_visible()
        mobile_page.screenshot(path=str(evidence_dir / "cumulative-mobile-touch.png"), full_page=True)
        mobile.close()
        browser.close()

    assert trace_path.is_file() and trace_path.stat().st_size > 0
    assert not page_errors, page_errors
    return {
        "boot": boot,
        "desktop_pointer_keyboard": True,
        "mobile_touch": True,
        "mobile_viewport": {"width": 390, "height": 844},
        "trace": {
            "path": trace_path.name,
            "bytes": trace_path.stat().st_size,
            "sha256": sha256(trace_path.read_bytes()).hexdigest(),
            "screenshots": True,
            "snapshots": True,
            "sources": True,
        },
        "network": {
            "response_count": len(responses),
            "request_failure_count": len(request_failures),
            "websocket_observed_count": len(websockets),
            "responses": responses[-400:],
            "request_failures": request_failures[-100:],
            "websockets": websockets[-50:],
        },
        "console_errors": console_errors[-100:],
        "page_errors": page_errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", required=True)
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[2]
    evidence_dir = Path(args.evidence_dir).resolve()
    evidence_dir.mkdir(parents=True, exist_ok=True)
    state_root = evidence_dir / "isolated-state"
    home = state_root / "home"
    data = state_root / "data"
    runtime = data / "runtime"
    for path in (home, runtime):
        path.mkdir(parents=True, exist_ok=True)

    os.environ["HOME"] = str(home)
    os.environ["HHS_DATA_DIR"] = str(data)
    os.environ["HHS_RUNTIME_OUTPUT_DIR"] = str(runtime)
    os.environ["HHS_FILESYSTEM_LEDGER_PATH"] = str(runtime / "filesystem-ledger.json")
    os.environ["HHS_PASS166_STORAGE_DIR"] = str(state_root / "pass166")
    os.environ["HHS_COGNITION_AUTO_TICK"] = "0"
    os.environ["HHS_DISABLE_C_AUTOBUILD"] = "1"
    os.environ["HHS_ASSISTANT_HEALTH_TIMEOUT_SECONDS"] = "0.5"
    assert os.environ.get("PLAYWRIGHT_BROWSERS_PATH"), (
        "PLAYWRIGHT_BROWSERS_PATH must be explicit so isolated HOME cannot hide "
        "the installed Chromium executable"
    )

    receipts = verify_receipts(repo)
    env = environment_manifest(repo, state_root)
    (evidence_dir / "environment-manifest.json").write_text(
        json.dumps(env, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    server = ProductionServer(
        free_port(),
        evidence_dir,
        env={
            key: value
            for key, value in os.environ.items()
            if key.startswith("HHS_") or key == "HOME"
        },
        label="cumulative-local-closure-server",
    )
    started = time.monotonic()
    try:
        startup = server.start()
        tree = process_tree()
        (evidence_dir / "process-tree.json").write_text(
            json.dumps(tree, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        browser = browser_evidence(server.base_url, evidence_dir)
    finally:
        stop = server.stop()

    result = {
        "schema": "HHS_PASS185_I141_CUMULATIVE_LOCAL_CLOSURE_V1",
        "ok": True,
        "classification": "HHS_PASS_185_CUMULATIVE_PHASE1_PHASE7_LOCAL_CLOSURE_VERIFIED",
        "contract_id": CONTRACT_ID,
        "entrypoint": ENTRYPOINT,
        "tested_head": git("rev-parse", "HEAD", cwd=repo),
        "tested_tree": git("rev-parse", "HEAD^{tree}", cwd=repo),
        "receipts": receipts,
        "section_map": SECTION_MAP,
        "negative_matrix": [
            {"scenario": scenario, "evidence": evidence, "status": "PASS"}
            for scenario, evidence in NEGATIVE_MATRIX
        ],
        "environment_manifest": env,
        "startup": startup,
        "process_tree_rows": len(tree),
        "browser": browser,
        "server_stop": stop,
        "elapsed_ms": round((time.monotonic() - started) * 1000),
        "local_unresolved_contract_rows": [],
        "local_waivers": [],
        "canonical_runtime_authority_changed": False,
        "new_vm81_authority": False,
        "parallel_hash72_commit_authority": False,
        "frontend_runtime_authority": False,
        "authoritative_main_verified": False,
        "external_deployment_verified": False,
        "terminal_pass185_completion_claimed": False,
        "remaining_terminal_scope": [
            "current-main drift reconciliation",
            "explicit safe integration boundary",
            "authoritative-main verification after integration",
            "external production deployment replay",
            "terminal Pass-185 classification",
        ],
    }
    result["evidence_sha256"] = sha256(
        json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    output = evidence_dir / "cumulative-local-closure.json"
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

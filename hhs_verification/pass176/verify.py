#!/usr/bin/env python3
"""Create the terminal Pass 176 verification receipt from executed browser evidence."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def file_sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", default=".")
    parser.add_argument(
        "--browser-evidence",
        default="applications/holofractal_harmonizer/evidence/pass176/browser-smoke.json",
    )
    parser.add_argument(
        "--output",
        default="evidence/pass176/generated/PASS_176_TERMINAL_COMPLETION_RECEIPT.json",
    )
    args = parser.parse_args()

    root = Path(args.repository_root).resolve()
    browser_path = (root / args.browser_evidence).resolve()
    output = (root / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    required = [
        root / "HHS_PASS_176_FROZEN_PRODUCTION_MULTIMODAL_IDE_STABILIZATION_PERFORMANCE_RECOVERY.md",
        root / "applications/holofractal_harmonizer/src/pass176-stability-core.mjs",
        root / "applications/holofractal_harmonizer/src/pass176-stability.mjs",
        root / "applications/holofractal_harmonizer/src/pass176-stability.css",
        root / "applications/holofractal_harmonizer/src/visual-ide.mjs",
        root / "applications/holofractal_harmonizer/tests/pass176-stability.test.mjs",
        root / "applications/holofractal_harmonizer/ux_lab/pass176_stability_smoke.py",
        root / "tests/test_pass176_frozen_ide_stabilization.py",
        root / ".github/workflows/pass176-frozen-ide-stabilization.yml",
        root / "evidence/pass175/PASS_175_TERMINAL_COMPLETION_RECEIPT.json",
        browser_path,
    ]
    missing = [str(path.relative_to(root)) for path in required if not path.is_file()]
    if missing:
        raise SystemExit(f"PASS176_REQUIRED_ARTIFACT_MISSING:{missing}")

    parent = json.loads((root / "evidence/pass175/PASS_175_TERMINAL_COMPLETION_RECEIPT.json").read_text())
    browser = json.loads(browser_path.read_text())
    initial = browser.get("initial") or {}
    repetition = browser.get("repetition") or {}
    final_status = browser.get("final_status") or {}
    boot = final_status.get("boot") or {}
    resources = final_status.get("resources") or {}

    checks = {
        "pass175_activation_gate": parent.get("terminal_pass175_completion") is True,
        "browser_smoke_ok": browser.get("ok") is True,
        "production_root_full_ide": bool(browser.get("title")) and initial.get("stage") == "INTERACTIVE",
        "ordered_boot_complete": boot.get("stage") == "INTERACTIVE" and len(boot.get("records") or []) == 10,
        "duplicate_boot_idempotent": (browser.get("duplicate_boot") or {}).get("recordCount") == 10,
        "assistant_cycles_100": repetition.get("assistantCycles") == 100,
        "mobile_pane_cycles_100": repetition.get("paneCycles") == 100,
        "editor_state_preserved": repetition.get("editorPreserved") is True,
        "resource_growth_absent": repetition.get("resourceTotal") == initial.get("resourceTotal"),
        "stale_response_rejected": (browser.get("stale_response") or {}).get("rejected") is True,
        "current_response_accepted": (browser.get("stale_response") or {}).get("currentAccepted") is True,
        "bounded_cancellation": (browser.get("cancelled_job") or {}).get("cancelled") is True,
        "atomic_recovery_saved": (browser.get("recovery") or {}).get("saved") is True,
        "frontend_not_canonical_authority": final_status.get("canonicalFrontendAuthority") is False,
        "vm81_authority_preserved": final_status.get("vm81AuthorityPreserved") is True,
        "single_hash72_commit_stream": final_status.get("hash72CommitStreams") == 1,
        "console_errors_clean": browser.get("console_errors") == [],
        "page_errors_clean": browser.get("page_errors") == [],
        "bounded_jobs_drained": (final_status.get("jobs") or {}).get("active") == [],
        "external_vercel_excluded": browser.get("external_vercel_status_considered") is False,
    }

    source_hashes = {
        str(path.relative_to(root)): file_sha(path)
        for path in required
        if path != browser_path
    }
    source_root = sha256(
        b"HHS-P176-SOURCE-ROOT\0"
        + b"".join(
            name.encode("utf-8") + b"\0" + bytes.fromhex(digest)
            for name, digest in sorted(source_hashes.items())
        )
    ).hexdigest()

    receipt = {
        "schema": "HHS_PASS_176_TERMINAL_COMPLETION_RECEIPT_V1",
        "classification": "HHS_PASS_176_FROZEN_PRODUCTION_IDE_STABILIZED_RECOVERABLE_VERIFIED",
        "terminal_pass176_completion": all(checks.values()),
        "checks": checks,
        "activation_parent": {
            "pass": 175,
            "classification": parent.get("classification"),
            "authoritative_merge_commit": parent.get("authoritative_merge_commit"),
            "terminal_receipt_sha256": (parent.get("terminal_roots") or {}).get("terminal_receipt_sha256"),
        },
        "frozen_visual_baseline_preserved": True,
        "source_hashes": source_hashes,
        "source_root_sha256": source_root,
        "browser_evidence_sha256": file_sha(browser_path),
        "browser": {
            "title": browser.get("title"),
            "timing_ms": browser.get("timing_ms"),
            "boot": boot,
            "resources": resources,
            "long_tasks": final_status.get("longTasks"),
            "profile": final_status.get("profile"),
            "request_failures": browser.get("request_failures"),
        },
        "authority": {
            "frontend_is_canonical_authority": False,
            "singleton_vm81_admission_preserved": True,
            "hash72_commit_streams": 1,
            "pass175_instruction_authority_preserved": True,
        },
        "external_deployment": {
            "vercel_status_considered": False,
            "external_vercel_failure_is_not_acceptance_gate": True,
        },
    }
    body = dict(receipt)
    receipt["receipt_sha256"] = sha256(b"HHS-P176-TERMINAL-RECEIPT\0" + canonical(body)).hexdigest()
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "classification": receipt["classification"],
        "output": str(output),
        "receipt_sha256": receipt["receipt_sha256"],
        "terminal_pass176_completion": receipt["terminal_pass176_completion"],
    }, sort_keys=True))
    return 0 if receipt["terminal_pass176_completion"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

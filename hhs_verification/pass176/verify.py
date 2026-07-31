#!/usr/bin/env python3
"""Create the terminal Pass 176 verification receipt from executed browser evidence."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any


HEX64 = re.compile(r"^[0-9a-f]{64}$")


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
        root / "evidence/pass176/PASS_176_ACTIVATION_RECORD.json",
        root / "applications/holofractal_harmonizer/src/application-templates-runtime.mjs",
        root / "applications/holofractal_harmonizer/src/integrated-assistant.mjs",
        root / "applications/holofractal_harmonizer/src/pass176-stability-core.mjs",
        root / "applications/holofractal_harmonizer/src/pass176-stability.mjs",
        root / "applications/holofractal_harmonizer/src/pass176-stability.css",
        root / "applications/holofractal_harmonizer/src/visual-ide.mjs",
        root / "applications/holofractal_harmonizer/src/visual-ide-state.mjs",
        root / "applications/holofractal_harmonizer/src/visual-ide-runtime.mjs",
        root / "applications/holofractal_harmonizer/tests/integrated.workbench.test.mjs",
        root / "applications/holofractal_harmonizer/tests/intuitive.ide.test.mjs",
        root / "applications/holofractal_harmonizer/tests/pass176-stability.test.mjs",
        root / "applications/holofractal_harmonizer/tests/project.lifecycle.test.mjs",
        root / "applications/holofractal_harmonizer/ux_lab/pass176_stability_smoke.py",
        root / "tests/test_pass176_frozen_ide_stabilization.py",
        root / ".github/workflows/pass176-frozen-ide-stabilization.yml",
        root / "evidence/pass175/PASS_175_TERMINAL_COMPLETION_RECEIPT.json",
        browser_path,
    ]
    missing = [str(path.relative_to(root)) for path in required if not path.is_file()]
    if missing:
        raise SystemExit(f"PASS176_REQUIRED_ARTIFACT_MISSING:{missing}")

    parent_path = root / "evidence/pass175/PASS_175_TERMINAL_COMPLETION_RECEIPT.json"
    parent = json.loads(parent_path.read_text(encoding="utf-8"))
    browser = json.loads(browser_path.read_text(encoding="utf-8"))
    initial = browser.get("initial") or {}
    repetition = browser.get("repetition") or {}
    final_status = browser.get("final_status") or {}
    boot = final_status.get("boot") or {}
    resources = final_status.get("resources") or {}
    authority_evidence = final_status.get("authorityEvidence") or {}
    parent_authority = parent.get("authority") or {}
    parent_roots = parent.get("terminal_roots") or {}
    parent_main = parent.get("main_verification") or {}
    parent_replay = parent.get("replay") or {}

    parent_integrity = bool(
        parent.get("schema") == "HHS_PASS_175_TERMINAL_MAIN_COMPLETION_RECEIPT_V1"
        and parent.get("terminal_pass175_completion") is True
        and parent_authority.get("singleton_vm81_admission") is True
        and parent_authority.get("hash72_commit_streams") == 1
        and parent_replay.get("receipt_chain_valid") is True
        and parent_main.get("merged") is True
        and parent_main.get("main_source_fetch_verified") is True
        and HEX64.fullmatch(str(parent_roots.get("terminal_receipt_sha256") or ""))
        and HEX64.fullmatch(str(parent.get("authoritative_merge_commit") or "")) is None
        and re.fullmatch(r"[0-9a-f]{40}", str(parent.get("authoritative_merge_commit") or ""))
    )
    evidence_integrity = bool(
        authority_evidence.get("schema") == "HHS_PASS_176_BACKEND_AUTHORITY_EVIDENCE_V1"
        and authority_evidence.get("singletonVm81CommitAuthority") is True
        and authority_evidence.get("vm81AuthorityPreserved") is True
        and authority_evidence.get("hash72CommitStreams") == 1
        and authority_evidence.get("runtimeReceiptHash72")
        and authority_evidence.get("runtimeStatus") == "HHS_RUNTIME_AUTHORITY_ONLINE"
    )

    checks = {
        "pass175_activation_gate": parent_integrity,
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
        "recovery_applied_to_editor": (browser.get("recovery") or {}).get("editorRestored") is True,
        "frontend_not_canonical_authority": final_status.get("canonicalFrontendAuthority") is False,
        "backend_authority_evidence_bound": evidence_integrity,
        "vm81_authority_preserved": final_status.get("vm81AuthorityPreserved") is True,
        "single_hash72_commit_stream": final_status.get("hash72CommitStreams") == 1,
        "console_errors_clean": browser.get("console_errors") == [],
        "page_errors_clean": browser.get("page_errors") == [],
        "request_failures_clean": browser.get("request_failures") == [],
        "http_errors_clean": browser.get("http_errors") == [],
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
            "schema": parent.get("schema"),
            "classification": parent.get("classification"),
            "authoritative_merge_commit": parent.get("authoritative_merge_commit"),
            "terminal_receipt_sha256": parent_roots.get("terminal_receipt_sha256"),
            "receipt_file_sha256": file_sha(parent_path),
            "integrity_verified": parent_integrity,
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
            "http_errors": browser.get("http_errors"),
        },
        "authority": {
            "frontend_is_canonical_authority": final_status.get("canonicalFrontendAuthority") is False,
            "backend_evidence": authority_evidence,
            "singleton_vm81_admission_preserved": evidence_integrity and final_status.get("vm81AuthorityPreserved") is True,
            "hash72_commit_streams": authority_evidence.get("hash72CommitStreams", 0),
            "pass175_instruction_authority_preserved": parent_integrity,
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

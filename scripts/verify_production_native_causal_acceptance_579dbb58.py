#!/usr/bin/env python3
"""I088: acceptance-only verification of evidence for an already promoted release.

The script has no network, SSH, git, installation, service, or deployment
effects. Artifact inputs MUST be collected from the actual deployed host,
HTTPS service, and Chromium by the authorized operator; fixture tests do
not constitute real production acceptance.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any

PIN = "579dbb58f7f9d99419e73cb4d686901e6d123212"
NATIVE_PATH = "NATIVE_CAUSAL_LM_SERIALIZED_BLOCK_STREAM"
BROWSER_SCHEMA = "HHS_DIGITALOCEAN_PUBLIC_FRONTEND_CAPABILITY_BROWSER_ACCEPTANCE_V1"


class Refused(ValueError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise Refused(message)


def object_file(file: Path, name: str) -> dict[str, Any]:
    value = json.loads(file.read_text(encoding="utf-8"))
    require(isinstance(value, dict), name + " must be a JSON object")
    return value


def verify_evidence(
    *,
    native: Path, promotion: Path, public_system: Path,
    public_interface: Path, public_services: Path, public_html: Path,
    browser: Path, screenshot: Path, base_url: str,
) -> dict[str, Any]:
    require(base_url.startswith("https://") and len(base_url) > 8,
            "verified HTTPS base URL required")
    require("@" not in base_url.split("/")[2], "URL credentials prohibited")

    deployed = object_file(promotion, "host promotion")
    for key in ("candidate_sha", "runtime_os_bundle_sha"):
        require(deployed.get(key) == PIN, "host promotion " + key + " mismatch")
    require(deployed.get("outcome") == "PROMOTED",
            "host candidate not promoted")

    rows = [json.loads(line) for line in native.read_text(encoding="utf-8").splitlines()
            if line.lstrip().startswith("{")]
    reports = [row for row in rows if row.get("schema") ==
               "HHS_NATIVE_CHAT_CLI_ACCEPTANCE_V1"]
    require(len(reports) == 1, "exactly one final native CLI report required")
    report = reports[0]
    turns = report.get("turns")
    require(report.get("ok") is True and not report.get("failures"),
            "native CLI strict acceptance failed")
    require(report.get("prompt_count") == 4 and
            report.get("distinct_response_count") == 4,
            "native CLI did not accept four distinct prompts")
    require(isinstance(turns, list) and len(turns) == 4,
            "native CLI four turn objects required")
    hashes = []
    for i, t in enumerate(turns):
        require(isinstance(t, dict), "invalid native turn " + str(i))
        require(t.get("generation_path") == NATIVE_PATH, "native fallback in turn")
        require(not t.get("causal_generation_failure") and
                not t.get("strict_failures"), "native turn failed")
        block_count = t.get("response_block_count")
        require(type(block_count) is int and block_count > 0,
                "serialized response blocks absent")
        require(t.get("runtime_mutation_admitted") is False,
                "native generation mutated authoritative runtime")
        answer = t.get("response")
        require(isinstance(answer, str) and answer.strip(),
                "native generated response empty")
        expected_hash = sha256(answer.strip().encode("utf-8")).hexdigest()
        require(t.get("response_sha256") == expected_hash,
                "native response hash mismatch")
        hashes.append(expected_hash)
    require(len(set(hashes)) == 4, "native responses are not distinct")

    system = object_file(public_system, "HTTPS system status")
    require(bool(system), "empty HTTPS system status")
    interface = object_file(public_interface, "HTTPS interface")
    require(interface.get("interface") == "HHS_VISUAL_RUNTIME_OS_WORKSPACE",
            "public Runtime OS interface mismatch")
    require(interface.get("legacy_harmonizer_is_public_root") is False,
            "public root unexpectedly changed")
    require(PIN in str(interface.get("asset_root", "")),
            "public Runtime OS asset_root is not exact deployed SHA")
    services = object_file(public_services, "HTTPS services").get("services")
    require(isinstance(services, list) and len(services) > 0,
            "public registry empty")
    names = [str(s.get("name") or (s.get("runtime_contract") or {}).get("name") or "")
             for s in services if isinstance(s, dict)]
    require(len(names) == len(services) and all(names) and
            len(set(names)) == len(names), "public registry identity duplicate/invalid")
    require("HHS Visual Runtime OS Workspace" in
            public_html.read_text(encoding="utf-8"),
            "public root is not the Runtime OS workspace")

    visual = object_file(browser, "Chromium evidence")
    require(visual.get("schema") == BROWSER_SCHEMA and visual.get("ok") is True,
            "Chromium final verdict failed")
    require(visual.get("expected_sha") == PIN and
            visual.get("expected_service_count") == len(services),
            "Chromium SHA/registry mismatch")
    require(visual.get("base_url", "").rstrip("/") == base_url.rstrip("/"),
            "Chromium base URL mismatch")
    require(visual.get("ignore_https_errors") is False,
            "Chromium disabled certificate validation")
    for key in (
        "visual_program_registry_ready",
        "visual_program_execution_verified",
        "assistant_execution_verified",
        "assistant_chatbot_two_turn_verified",
        "workspace_workbench_execution_verified",
        "terminal_websocket_execution_verified",
    ):
        require(visual.get(key) is True, "Chromium missing gate: " + key)
    for key in ("console_errors", "page_errors", "request_failures", "http_5xx"):
        require(not visual.get(key), "Chromium error list not empty: " + key)
    picture = screenshot.read_bytes()
    require(len(picture) > 100 and picture.startswith(b"\x89PNG\r\n\x1a\n"),
            "real Chromium PNG screenshot absent")
    artifacts = {
        "host_promotion": promotion,
        "native_cli": native,
        "https_system": public_system,
        "https_interface": public_interface,
        "https_services": public_services,
        "https_root_html": public_html,
        "chromium_json": browser,
        "chromium_png": screenshot,
    }
    return {
        "schema": "HHS_I088_PRODUCTION_NATIVE_CAUSAL_ACCEPTANCE_EVIDENCE_V1",
        "ok": True, "release_sha": PIN, "verified_https_url": base_url,
        "native_generation_path": NATIVE_PATH, "distinct_response_count": 4,
        "service_count": len(services),
        "browser_schema": BROWSER_SCHEMA,
        "tls_certificate_validation_required": True,
        "collection_provenance_requires_operator_attestation": True,
        "evidence_sha256": {
            name: sha256(path.read_bytes()).hexdigest()
            for name, path in artifacts.items()
        },
        "release_block_automatically_lifted": False,
        "host_updater_automatically_enabled": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    for k in ("native", "promotion", "public_system", "public_interface",
              "public_services", "public_html", "browser", "screenshot"):
        parser.add_argument("--" + k.replace("_", "-"), required=True, type=Path)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        receipt = verify_evidence(**{
            k: getattr(args, k) for k in (
                "native", "promotion", "public_system", "public_interface",
                "public_services", "public_html", "browser", "screenshot"
            )
        }, base_url=args.base_url)
    except (Refused, OSError, ValueError, KeyError, TypeError) as exc:
        print("HHS_I088_ACCEPTANCE_REJECTED: " + str(exc))
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp = args.output.with_name(args.output.name + ".tmp." + str(os.getpid()))
    try:
        temp.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        os.replace(temp, args.output)
    finally:
        temp.unlink(missing_ok=True)
    print("HHS_I088_EVIDENCE_ACCEPTED=1")
    print("HHS_I088_RELEASE_STILL_BLOCKED_PENDING_OPERATOR_RELEASE_AUTHORITY=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

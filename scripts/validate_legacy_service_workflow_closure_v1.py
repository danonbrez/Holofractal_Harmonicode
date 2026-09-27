#!/usr/bin/env python3
"""Validate dependency-scoped legacy service workflow closure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]

WORKFLOWS: dict[str, dict[str, bool]] = {
    ".github/workflows/hhs-acceptance-gate.yml": {"pull": True, "push_main": True},
    ".github/workflows/hhs-agi-runtime-wiring.yml": {"pull": True, "push_main": True},
    ".github/workflows/hhs-immutable-agent-sql-index.yml": {"pull": True, "push_main": True},
    ".github/workflows/pass165-mmvs.yml": {"pull": True, "push_main": True},
    ".github/workflows/pass166-word2vec.yml": {"pull": True, "push_main": True},
    ".github/workflows/pass166-validation-relay.yml": {"pull": False, "push_main": False},
    ".github/workflows/pass174-heroku-boot-resilience.yml": {"pull": True, "push_main": True},
    ".github/workflows/pass205-repair-validation-base.yml": {"pull": True, "push_main": True},
    ".github/workflows/pass205-multimodal-continuation-contract.yml": {"pull": True, "push_main": True},
    ".github/workflows/pass205-production-runtime.yml": {"pull": True, "push_main": True},
    ".github/workflows/pass219-cumulative-pass205-membrane-i119.yml": {"pull": True, "push_main": True},
    ".github/workflows/pass219-lane5-exact-boundary-quantum-thermo-1-35.yml": {"pull": True, "push_main": True},
}

CONTRACT = ROOT / "contracts/ci/HHS_LEGACY_SERVICE_VALIDATION_CLOSURE_V1.md"


def events(document: dict[str, Any]) -> dict[str, Any]:
    value = document.get("on")
    if value is None:
        # PyYAML 1.1 treats the unquoted key "on" as boolean True.
        value = document.get(True)
    if not isinstance(value, dict):
        raise AssertionError("workflow 'on' value must be a mapping")
    return value


def string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value]
    raise AssertionError(f"expected string/list, got {type(value).__name__}")


def validate_workflow(path_text: str, requirements: dict[str, bool]) -> dict[str, Any]:
    path = ROOT / path_text
    raw = path.read_text("utf-8")
    document = yaml.safe_load(raw)
    if not isinstance(document, dict):
        raise AssertionError(f"{path_text}: workflow must parse to a mapping")

    jobs = document.get("jobs")
    if not isinstance(jobs, dict) or not jobs:
        raise AssertionError(f"{path_text}: jobs mapping missing")

    for job_name, job in jobs.items():
        if not isinstance(job, dict):
            continue
        job_env = job.get("env", {})
        if isinstance(job_env, dict):
            for key, value in job_env.items():
                if "runner.temp" in str(value):
                    raise AssertionError(
                        f"{path_text}: job {job_name!r} env {key!r} references "
                        "runner.temp before runner assignment"
                    )

    concurrency = document.get("concurrency")
    if not isinstance(concurrency, dict):
        raise AssertionError(f"{path_text}: concurrency mapping missing")
    if concurrency.get("cancel-in-progress") is not True:
        raise AssertionError(f"{path_text}: superseded runs must cancel in progress")

    trigger = events(document)

    if requirements["pull"]:
        pull = trigger.get("pull_request")
        if not isinstance(pull, dict):
            raise AssertionError(f"{path_text}: pull_request mapping missing")
        pull_paths = string_list(pull.get("paths"))
        if not pull_paths:
            raise AssertionError(f"{path_text}: pull_request.paths must be dependency scoped")
        if path_text not in pull_paths:
            raise AssertionError(f"{path_text}: workflow file must reopen its own pull validation")

    if requirements["push_main"]:
        push = trigger.get("push")
        if not isinstance(push, dict):
            raise AssertionError(f"{path_text}: push mapping missing")
        push_paths = string_list(push.get("paths"))
        if not push_paths:
            raise AssertionError(f"{path_text}: push.paths must be dependency scoped")
        branches = string_list(push.get("branches"))
        if "main" not in branches:
            raise AssertionError(f"{path_text}: exact-main closure requires main push")
        if path_text not in push_paths:
            raise AssertionError(f"{path_text}: workflow file must reopen its own main validation")

    return {
        "path": path_text,
        "sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "jobs": sorted(str(name) for name in jobs),
        "pull_scoped": requirements["pull"],
        "push_main_scoped": requirements["push_main"],
        "cancel_superseded": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    contract = CONTRACT.read_text("utf-8")
    for marker in (
        "INHERITED_CLOSED",
        "REPAIR_FORWARD",
        "Startup is not installation or compilation",
        "Hash72/Hash216",
    ):
        if marker not in contract:
            raise AssertionError(f"closure contract missing marker: {marker}")

    records = [
        validate_workflow(path, requirements)
        for path, requirements in sorted(WORKFLOWS.items())
    ]

    receipt = {
        "schema": "HHS_LEGACY_SERVICE_VALIDATION_CLOSURE_V1",
        "classification": "HHS_LEGACY_SERVICE_VALIDATION_CLOSURE_STATIC_PASS",
        "source_failure_head": "f9aaa2d20a8f2269a5141828852b7953b787fafc",
        "policy": {
            "unchanged_dependency_surface": "INHERITED_CLOSED",
            "touched_dependency_surface": "REOPEN_DEPENDENCY_SCOPED",
            "failure": "REPAIR_FORWARD",
            "startup_replays_legacy_validation": False,
            "legacy_obligations_removed": False,
        },
        "workflow_count": len(records),
        "workflows": records,
        "contract_sha256": hashlib.sha256(contract.encode("utf-8")).hexdigest(),
    }

    encoded = json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

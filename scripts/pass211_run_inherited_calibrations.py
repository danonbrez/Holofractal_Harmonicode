#!/usr/bin/env python3
"""Run Pass 211 inherited validation and benchmark calibration matrix."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def tail(text: str, lines: int = 120) -> str:
    return "\n".join(text.splitlines()[-lines:])


def run_case(
    *,
    name: str,
    command: list[str],
    root: Path,
    timeout_seconds: int,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    started = time.perf_counter_ns()
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            env=merged,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        returncode = completed.returncode
        output = completed.stdout
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        returncode = 124
        output = (exc.stdout or "") + "\n" + (exc.stderr or "")
        timed_out = True
    elapsed_ns = time.perf_counter_ns() - started
    result = {
        "name": name,
        "command": command,
        "returncode": returncode,
        "passed": returncode == 0,
        "timed_out": timed_out,
        "timeout_seconds": timeout_seconds,
        "elapsed_ns": elapsed_ns,
        "elapsed_seconds": round(elapsed_ns / 1_000_000_000, 6),
        "output_tail": tail(output),
    }
    print(json.dumps(
        {
            "name": name,
            "passed": result["passed"],
            "returncode": returncode,
            "elapsed_seconds": result["elapsed_seconds"],
        },
        sort_keys=True,
    ))
    if output:
        print(result["output_tail"])
    return result


def cases(python: str) -> list[dict[str, Any]]:
    cpu_env = {
        "HHS_PASS207_GPU_BACKEND": "CPU_REFERENCE",
        "HHS_PASS207_REQUIRE_PHYSICAL_GPU": "0",
        "HHS_PASS208_GPU_ENABLED": "0",
        "HHS_PASS190_CAPABILITY_SECRET": "pass211-calibration-secret",
    }
    return [
        {
            "name": "pass188_exhaustive_1259712_projected_states",
            "command": ["make", "-C", "native_projects/hhs_pass188_bott_runtime", "validate"],
            "timeout_seconds": 1800,
        },
        {
            "name": "pass189_exhaustive_51648192_contextual_states",
            "command": ["make", "-C", "native_projects/hhs_pass189_hqlh_runtime", "validate"],
            "timeout_seconds": 3600,
        },
        {
            "name": "pass205_native_continuation_abi_build",
            "command": [
                python,
                "-c",
                "from hhs_python.runtime.hhs_pass205_continuation_bridge import build_native_library; print(build_native_library(force=True))",
            ],
            "timeout_seconds": 300,
        },
        {
            "name": "pass207_native_gpu_abi_cpu_oracle_build",
            "command": [
                python,
                "-c",
                "from hhs_python.runtime.hhs_pass207_gpu_driver_native import build_native_library; print(build_native_library(force=True))",
            ],
            "timeout_seconds": 300,
            "env": cpu_env,
        },
        {
            "name": "pass205_to_pass210_dependency_scoped_regression",
            "command": [
                python,
                "-m",
                "pytest",
                "-q",
                "tests/test_hhs_pass205_continuation_runtime_v1.py",
                "tests/test_hhs_pass207_gpu_driver_v1.py",
                "tests/test_hhs_pass208_gpu_branch_manifold_v1.py",
                "tests/test_hhs_pass208_digitalocean_gpu_deployment_v1.py",
                "tests/test_hhs_pass196_integrated_environment_v1.py",
                "tests/test_runtime_bootstrap_gateway.py",
                "tests/test_hhs_pass210_llm_orchestrator_v1.py",
                "tests/test_hhs_pass210_digitalocean_llm_deployment_v1.py",
                "tests/test_hhs_production_public_app_v1.py",
            ],
            "timeout_seconds": 1800,
            "env": cpu_env,
        },
        {
            "name": "pass205_extended_multimodal_continuation_calibration",
            "command": [
                python,
                "scripts/pass205_multimodal_continuation_design_validation.py",
                "--ticks",
                "360",
                "--seeds",
                "1,5,7,41,64,72,81,144,216,243,5040,5184,1259713",
                "--output",
                "evidence/pass211-ci/PASS211_PASS205_CONTINUATION_CALIBRATION.json",
            ],
            "timeout_seconds": 900,
        },
        {
            "name": "pass205_gpu_translation_calibration",
            "command": [
                python,
                "scripts/pass205_gpu_translation_design_validation.py",
                "--output",
                "evidence/pass211-ci/PASS211_PASS205_GPU_TRANSLATION_CALIBRATION.json",
            ],
            "timeout_seconds": 600,
            "env": cpu_env,
        },
        {
            "name": "pass211_benchmark_unit_tests",
            "command": [
                python,
                "-m",
                "pytest",
                "-q",
                "tests/test_pass211_multimodal_invariant_benchmark.py",
            ],
            "timeout_seconds": 300,
        },
        {
            "name": "pass211_repository_invariant_and_retrieval_benchmark",
            "command": [
                python,
                "scripts/pass211_multimodal_invariant_benchmark.py",
                "--output",
                "evidence/pass211-ci/PASS211_MULTIMODAL_INVARIANT_BENCHMARK_RECEIPT.json",
                "--address-samples",
                "1000000",
                "--max-vector-objects",
                "2048",
                "--query-limit",
                "512",
            ],
            "timeout_seconds": 900,
        },
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--output",
        default="evidence/pass211-ci/PASS211_INHERITED_CALIBRATION_MATRIX.json",
    )
    parser.add_argument("--continue-on-failure", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = (root / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    (root / "evidence/pass211-ci").mkdir(parents=True, exist_ok=True)

    case_list = cases(sys.executable)
    results: list[dict[str, Any]] = []
    for case in case_list:
        result = run_case(
            name=case["name"],
            command=case["command"],
            root=root,
            timeout_seconds=case["timeout_seconds"],
            env=case.get("env"),
        )
        results.append(result)
        if not result["passed"] and not args.continue_on_failure:
            break

    passed = len(results) == len(case_list) and all(item["passed"] for item in results)
    receipt = {
        "schema": "HHS_PASS_211_INHERITED_CALIBRATION_MATRIX_V1",
        "classification": (
            "HHS_PASS_211_INHERITED_CALIBRATION_MATRIX_PASS"
            if passed
            else "HHS_PASS_211_INHERITED_CALIBRATION_MATRIX_FAIL"
        ),
        "base_requirement": "Complete cumulative HHS repository through Pass 210",
        "pass210_chromium_gate": {
            "status": "INHERITED_PENDING",
            "included_in_this_matrix": False,
            "reason": (
                "Pass 211 is stacked on draft Pass 210 PR #163. The unresolved final "
                "deployed Chromium smoke remains a Pass 210 merge blocker and cannot be "
                "silently reclassified by Pass 211."
            ),
        },
        "results": results,
        "completed_cases": len(results),
        "required_cases": len(case_list),
        "passed": passed,
    }
    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(
        {
            "classification": receipt["classification"],
            "passed": passed,
            "output": str(output),
            "receipt_sha256": receipt["receipt_sha256"],
        },
        indent=2,
        sort_keys=True,
    ))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

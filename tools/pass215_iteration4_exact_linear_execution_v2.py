#!/usr/bin/env python3
"""Authoritative Iteration 4 CLI with primitive executed-work accounting."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass215_iteration4_exact_linear_execution_v3 import (
    WORK_ACCOUNTING_ADDENDUM_GIT_BLOB_SHA1,
    build_execution_evidence_from_path,
    validate_execution_evidence,
)


def _write(path: Path | None, value: Any) -> None:
    encoded = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    if path is None:
        print(encoded, end="")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(encoded, encoding="utf-8")


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--container", type=Path)
    mode.add_argument("--validate", type=Path)
    mode.add_argument("--compare-replay", nargs=2, type=Path, metavar=("LEFT", "RIGHT"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--source-kind", default="local_or_fixture")
    parser.add_argument("--repo-id")
    parser.add_argument("--revision")
    parser.add_argument("--expected-sha256")
    args = parser.parse_args()

    if args.validate is not None:
        evidence = _load(args.validate)
        validate_execution_evidence(evidence)
        result = {
            "schema": "HHS_PASS_215_ITERATION_4_PRIMITIVE_WORK_VALIDATION_V2",
            "valid": True,
            "work_accounting_addendum_git_blob_sha1": WORK_ACCOUNTING_ADDENDUM_GIT_BLOB_SHA1,
            "evidence_root_hash216": evidence["evidence_root_hash216"],
            "suite_output_root_hash216": evidence["suite_output_root_hash216"],
            "receipt_hash72": evidence["receipt_hash72"],
        }
        _write(args.output, result)
        print("PASS215_ITERATION4_PRIMITIVE_WORK_EVIDENCE_VALID")
        return 0

    if args.compare_replay is not None:
        left = _load(args.compare_replay[0])
        right = _load(args.compare_replay[1])
        validate_execution_evidence(left)
        validate_execution_evidence(right)
        keys = ("evidence_root_hash216", "suite_output_root_hash216", "receipt_hash72")
        mismatches = [key for key in keys if left.get(key) != right.get(key)]
        if mismatches:
            raise SystemExit("PASS215_I4_CROSS_PROCESS_REPLAY_MISMATCH:" + ",".join(mismatches))
        result = {
            "schema": "HHS_PASS_215_ITERATION_4_CROSS_PROCESS_REPLAY_VALIDATION_V2",
            "valid": True,
            "separate_process_invocations": True,
            "primitive_work_accounting": True,
            "identical_evidence_root_hash216": left["evidence_root_hash216"],
            "identical_suite_output_root_hash216": left["suite_output_root_hash216"],
            "identical_receipt_hash72": left["receipt_hash72"],
        }
        _write(args.output, result)
        print("PASS215_ITERATION4_PRIMITIVE_WORK_CROSS_PROCESS_REPLAY_VALID")
        return 0

    source = {"kind": args.source_kind, "repo_id": args.repo_id, "revision": args.revision}
    evidence = build_execution_evidence_from_path(
        args.container,
        source=source,
        expected_sha256=args.expected_sha256,
    )
    _write(args.output, evidence)
    aggregate = evidence["aggregate_execution"]
    print(f"PASS215_ITERATION4_OPERATORS={aggregate['operator_count']}")
    print(f"PASS215_ITERATION4_SOURCE_TENSOR_BYTES={aggregate['source_tensor_bytes']}")
    print(f"PASS215_ITERATION4_Q4_BLOCKS={aggregate['quantization_blocks']}")
    print(f"PASS215_ITERATION4_LOGICAL_WEIGHTS={aggregate['logical_weights']}")
    print(f"PASS215_ITERATION4_DENSE_SCALE_MULTS={aggregate['dense_reference_work']['exact_rational_scale_multiplications']}")
    print(f"PASS215_ITERATION4_FACTORED_SCALE_MULTS={aggregate['factored_reference_work']['exact_rational_scale_multiplications']}")
    print(f"PASS215_ITERATION4_SCALE_MULTS_AVOIDED={aggregate['rational_scale_multiplications_avoided_by_factoring']}")
    print(f"PASS215_ITERATION4_DENSE_PRIMITIVE_WORK={aggregate['dense_reference_work']['executed_work_units_total']}")
    print(f"PASS215_ITERATION4_FACTORED_PRIMITIVE_WORK={aggregate['factored_reference_work']['executed_work_units_total']}")
    print(f"PASS215_ITERATION4_SINGLE_DELTA_PRIMITIVE_WORK={aggregate['single_region_continuation_work']['executed_work_units_total']}")
    print(f"PASS215_ITERATION4_SINGLE_FULL_PRIMITIVE_WORK={aggregate['single_region_full_recompute_control_work']['executed_work_units_total']}")
    print(f"PASS215_ITERATION4_MULTI_DELTA_PRIMITIVE_WORK={aggregate['multi_region_continuation_work']['executed_work_units_total']}")
    print(f"PASS215_ITERATION4_MULTI_FULL_PRIMITIVE_WORK={aggregate['multi_region_full_recompute_control_work']['executed_work_units_total']}")
    print(f"PASS215_ITERATION4_SUITE_OUTPUT_ROOT_HASH216={evidence['suite_output_root_hash216']}")
    print(f"PASS215_ITERATION4_EVIDENCE_ROOT_HASH216={evidence['evidence_root_hash216']}")
    print(f"PASS215_ITERATION4_RECEIPT_HASH72={evidence['receipt_hash72']}")
    print("PASS215_ITERATION4_PRIMITIVE_WORK_EXECUTION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

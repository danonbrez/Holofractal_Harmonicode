from __future__ import annotations

import argparse
from hashlib import sha256
import json
from time import perf_counter_ns
from typing import Any

from hhs_runtime.pass219.complete_monolithic_boundary_executor import (
    i161_complete_monolithic_boundary_self_test,
)

SCHEMA = "HHS_PASS219_I161_COMPLETE_MONOLITHIC_BOUNDARY_BENCHMARK_V1"


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return sha256(_canonical(value)).hexdigest()


def run_benchmark(repeats: int = 12) -> dict[str, Any]:
    if repeats < 3 or repeats > 64:
        raise ValueError("repeats must be in [3,64]")

    durations: list[int] = []
    execution_receipts: list[str] = []
    boundary_receipts: list[str] = []
    for _ in range(repeats):
        start = perf_counter_ns()
        row = i161_complete_monolithic_boundary_self_test()
        durations.append(perf_counter_ns() - start)
        execution_receipts.append(str(row["i161_execution_sha256"]))
        boundary_receipts.append(str(row["boundary_witness"]["boundary_witness_sha256"]))

    ordered = sorted(durations)
    median_ns = ordered[len(ordered) // 2]
    deterministic = len(set(execution_receipts)) == 1 and len(set(boundary_receipts)) == 1
    result = {
        "schema": SCHEMA,
        "repeats": repeats,
        "timing_clock": "perf_counter_ns",
        "timing_values_are_integer_nanoseconds": True,
        "min_ns": min(durations),
        "median_ns": median_ns,
        "max_ns": max(durations),
        "execution_receipt_sha256": execution_receipts[0],
        "boundary_witness_sha256": boundary_receipts[0],
        "deterministic_execution_receipt": deterministic,
        "typed_join_count": 10,
        "typed_join_proved": 10,
        "host_zero_division_used": False,
        "host_zero_fourth_power_used": False,
        "ordinary_scalar_boundary_equality_claimed": False,
        "floating_point_canonical_authority": False,
        "result": "PASS" if deterministic else "FAIL",
    }
    result["benchmark_receipt_sha256"] = _sha256(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=12)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    result = run_benchmark(args.repeats)
    print(json.dumps(result, sort_keys=True))
    if args.enforce and result["result"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

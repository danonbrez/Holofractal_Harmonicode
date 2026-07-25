"""Dependency-scoped latency benchmark for the unified Hash72 ledger append path."""

from __future__ import annotations

import argparse
import statistics
import tempfile
import time
from pathlib import Path

from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload, verify_unified_ledger


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--entries", type=int, default=200)
    parser.add_argument("--path", type=Path)
    args = parser.parse_args()

    if args.entries < 1:
        parser.error("--entries must be positive")

    path = args.path or (Path(tempfile.mkdtemp(prefix="hhs-ledger-benchmark-")) / "ledger.json")
    samples = []
    for index in range(args.entries):
        started = time.perf_counter_ns()
        append_payload(
            "LEDGER_BENCHMARK",
            "tools.benchmark_hhs_ledger_append_v1",
            {"index": index},
            ledger_path=path,
        )
        samples.append((time.perf_counter_ns() - started) / 1_000_000.0)

    verification = verify_unified_ledger(path)
    ordered = sorted(samples)
    p95_index = min(len(ordered) - 1, max(0, round(0.95 * (len(ordered) - 1))))
    print({
        "schema": "HHS_UNIFIED_LEDGER_APPEND_BENCHMARK_V1",
        "entries": args.entries,
        "mean_ms": statistics.fmean(samples),
        "median_ms": statistics.median(samples),
        "p95_ms": ordered[p95_index],
        "max_ms": max(samples),
        "ledger_path": str(path),
        "verification": verification,
    })
    return 0 if verification.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

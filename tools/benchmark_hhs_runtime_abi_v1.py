"""Benchmark the HHS runtime kernel through the C ABI and snapshot hydration."""

from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path
from time import perf_counter_ns

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from hhs_backend.runtime.runtime_snapshot_codec import (
    create_abi_snapshot_packet,
    runtime_snapshot_codec,
)
from hhs_python.runtime.hhs_ctypes_bridge import HHSRuntimeBridge


def _sample_stats(samples_ns: list[int]) -> dict[str, float]:
    samples_ms = [sample / 1_000_000.0 for sample in samples_ns]
    ordered = sorted(samples_ms)
    p95_index = min(len(ordered) - 1, max(0, round(0.95 * (len(ordered) - 1))))
    return {
        "count": float(len(samples_ms)),
        "mean_ms": statistics.fmean(samples_ms),
        "median_ms": statistics.median(samples_ms),
        "p95_ms": ordered[p95_index],
        "max_ms": max(samples_ms),
    }


def benchmark_runtime_abi(iterations: int = 200) -> dict[str, object]:
    if iterations < 1:
        raise ValueError("iterations must be positive")

    runtime = HHSRuntimeBridge()
    abi_validated = runtime.validate_abi()
    if not abi_validated:
        raise RuntimeError("HHS runtime ABI validation failed")

    step_samples_ns: list[int] = []
    receipt_samples_ns: list[int] = []
    hydration_samples_ns: list[int] = []
    latest_runtime: dict[str, object] | None = None
    latest_packet = None
    latest_restored = None

    for iteration in range(1, iterations + 1):
        started = perf_counter_ns()
        runtime.runtime_step()
        step_samples_ns.append(perf_counter_ns() - started)

        started = perf_counter_ns()
        runtime.receipt_commit()
        receipt_samples_ns.append(perf_counter_ns() - started)

        latest_runtime = runtime.export_runtime_dict()
        packet = create_abi_snapshot_packet(
            latest_runtime,
            receipt_chain=[],
            event_topology=[],
            branch_topology={},
            runtime_id="hhs_runtime_abi_benchmark",
            runtime_metadata={"benchmark_iteration": iteration},
        )

        started = perf_counter_ns()
        encoded = runtime_snapshot_codec.encode_snapshot(packet)
        decoded = runtime_snapshot_codec.decode_snapshot(encoded)
        latest_restored = runtime_snapshot_codec.rehydrate_runtime_state(decoded)
        hydration_samples_ns.append(perf_counter_ns() - started)
        latest_packet = packet

    assert latest_runtime is not None
    assert latest_packet is not None
    assert latest_restored is not None

    metadata = latest_restored.runtime_metadata
    hydration_verified = (
        latest_restored.step == latest_runtime["step"]
        and metadata.get("state_hash72") == latest_runtime["state_hash72"]
        and metadata.get("receipt_hash72") == latest_runtime["receipt_hash72"]
    )

    return {
        "schema": "HHS_RUNTIME_ABI_BENCHMARK_V1",
        "iterations": iterations,
        "abi_validated": abi_validated,
        "step_stats": _sample_stats(step_samples_ns),
        "receipt_commit_stats": _sample_stats(receipt_samples_ns),
        "snapshot_round_trip_stats": _sample_stats(hydration_samples_ns),
        "hydration_verified": hydration_verified,
        "runtime_step": latest_runtime["step"],
        "state_hash72": latest_runtime["state_hash72"],
        "receipt_hash72": latest_runtime["receipt_hash72"],
        "snapshot_hash72": latest_packet.snapshot_hash72,
        "encoded_snapshot_bytes": len(runtime_snapshot_codec.encode_snapshot(latest_packet)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=200)
    args = parser.parse_args()
    print(benchmark_runtime_abi(iterations=args.iterations))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

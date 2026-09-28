#!/usr/bin/env python3
"""Cross-layer timing companion for information-preserving priority translation."""
from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

from hhs_runtime.hhs_pass220_priority_offset_information_translation_v1 import (
    build_cross_layer_information_witness,
)


def _measure(repeats: int):
    samples = []
    result = None
    for _ in range(repeats):
        started = time.perf_counter_ns()
        result = build_cross_layer_information_witness()
        samples.append(time.perf_counter_ns() - started)
    ordered = sorted(samples)
    return result, {
        "samples": repeats,
        "min_ns": ordered[0],
        "median_ns": int(statistics.median(ordered)),
        "max_ns": ordered[-1],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    if args.repeats < 1:
        raise SystemExit("repeats must be >= 1")

    witness, timing = _measure(args.repeats)
    payload = {
        "schema": "HHS_PASS220_PRIORITY_OFFSET_CROSS_LAYER_BENCHMARK_V1",
        "information_preservation_closed": witness[
            "information_preservation_closed"
        ],
        "priority_default_eligible": witness["priority_default_eligible"],
        "hnan_status": witness["hnan_gate"]["status"],
        "hnan_terminal_source": witness["hnan_gate"]["terminal_source"],
        "channels_information_preserved": {
            channel: row["information_preserved"]
            for channel, row in witness["channels"].items()
        },
        "complete_cross_layer_witness_timing": timing,
        "timing_scope": (
            "HOST_PYTHON_INFORMATION_PRESERVATION_VALIDATION_OUTSIDE_LANE5"
        ),
        "timing_is_canonical": False,
        "lane5_optimization_applied": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, sort_keys=True, indent=2))
    return 0 if witness["information_preservation_closed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Measured candidate benchmark for the Pass 220 NumPy1 four-phase A/B experiment."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import time

from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import deserialize_offsets_5184
from hhs_runtime.hhs_pass220_numpy_four_phase_ab_v1 import (
    CHANNELS,
    supplied_tensor_u9_witness,
    scalar_offset_vector_transform,
    substitution_tensor_transform,
)
from hhs_runtime.hhs_pass220_numpy_harmonicode_array_v1 import HHSNumPyScalar

SCHEMA = "HHS_PASS220_NUMPY1_FOUR_PHASE_AB_BENCHMARK_V1"
SAMPLE_BITS = (
    0x0000000000000001,
    0x3FB999999999999A,
    0x400921FB54442D18,
    0xBFF0000000000000,
    0x7FEFFFFFFFFFFFFF,
)


def _measure(fn, repeats: int) -> dict[str, int]:
    samples = []
    for _ in range(repeats):
        started = time.perf_counter_ns()
        fn()
        samples.append(time.perf_counter_ns() - started)
    ordered = sorted(samples)
    return {
        "samples": len(ordered),
        "min_ns": ordered[0],
        "median_ns": int(statistics.median(ordered)),
        "max_ns": ordered[-1],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--repeats", type=int, default=25)
    args = parser.parse_args()
    if args.repeats < 3:
        raise SystemExit("repeats must be at least 3")

    offsets = [
        deserialize_offsets_5184(HHSNumPyScalar.from_float64_bits(bits).bigint_5184)
        for bits in SAMPLE_BITS
    ]

    rows = {}
    exact_equal = True
    for channel in CHANNELS:
        for source in offsets:
            exact_equal = exact_equal and (
                substitution_tensor_transform(source, channel)
                == scalar_offset_vector_transform(source, channel)
            )
        dense = _measure(
            lambda ch=channel: [
                substitution_tensor_transform(source, ch) for source in offsets
            ],
            args.repeats,
        )
        vector = _measure(
            lambda ch=channel: [
                scalar_offset_vector_transform(source, ch) for source in offsets
            ],
            args.repeats,
        )
        rows[channel] = {
            "dense_substitution": dense,
            "scalar_offset_vector": vector,
            "vector_faster_on_median": vector["median_ns"] < dense["median_ns"],
        }

    supplied_u9 = supplied_tensor_u9_witness()
    payload = {
        "schema": SCHEMA,
        "sample_ieee_bits": [f"{bits:016x}" for bits in SAMPLE_BITS],
        "repeats": args.repeats,
        "semantic_identity": exact_equal,
        "supplied_tensor_u9": {
            "u9_order": supplied_u9["u9_order"],
            "u9_power_9_is_identity": supplied_u9["u9_power_9_is_identity"],
            "nine_distinct_preclosure_states": supplied_u9[
                "nine_distinct_preclosure_states"
            ],
            "full_orbit_returns_literal_tensor_exactly": supplied_u9[
                "full_orbit_returns_literal_tensor_exactly"
            ],
            "dense_vector_u9_identity_all_powers": supplied_u9[
                "dense_vector_u9_identity_all_powers"
            ],
            "inverse_roundtrip_all_powers": supplied_u9[
                "inverse_roundtrip_all_powers"
            ],
        },
        "channels": rows,
        "timing_is_canonical": False,
        "benchmark_role": "CANDIDATE_SELECTION_ONLY",
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    tensor_ok = all(
        (
            supplied_u9["u9_power_9_is_identity"],
            supplied_u9["nine_distinct_preclosure_states"],
            supplied_u9["full_orbit_returns_literal_tensor_exactly"],
            supplied_u9["dense_vector_u9_identity_all_powers"],
            supplied_u9["direct_iterative_u9_identity_all_powers"],
            supplied_u9["literal_cells_preserved_all_powers"],
            supplied_u9["inverse_roundtrip_all_powers"],
        )
    )
    return 0 if exact_equal and tensor_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

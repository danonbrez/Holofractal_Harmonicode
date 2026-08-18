from __future__ import annotations

import json
import pathlib
import statistics
import tempfile
import time
from typing import Any

from hhs_backend.runtime.hhs_pass205_continuation_runtime_v1 import Pass205ContinuationRuntime
from hhs_backend.runtime.hhs_pass208_gpu_branch_manifold_v1 import Pass208GPUBranchManifold

SCHEMA = "HHS_PASS_219B_I2_PASS208_CPU_REFERENCE_BENCHMARK_V1"
BRANCH_COUNT = 162
PHASE_ORIGIN_COUNT = 81
QUERY_PHASE_ORIGIN = 37
REPETITIONS = 5


def ratio_x1000(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        return 0
    return numerator * 1000 // denominator


def make_branches(salt: int) -> list[list[dict[str, int]]]:
    branches: list[list[dict[str, int]]] = []
    for ordinal in range(BRANCH_COUNT):
        bit = (ordinal + salt) % 63
        branches.append(
            [
                {
                    "cell": (ordinal + salt) % 81,
                    "control_g": (ordinal * 17 + salt) % 243,
                    "xor_mask": 1 << bit,
                }
            ]
        )
    return branches


def run_expand(
    manifold: Pass208GPUBranchManifold,
    parent: dict[str, Any],
    branches: list[list[dict[str, int]]],
) -> tuple[int, dict[str, Any]]:
    begin = time.perf_counter_ns()
    result = manifold.expand(
        parent_snapshot=parent,
        branches=branches,
        bytecode_hydration_lattice_root216=parent["constraint_root216"],
    )
    elapsed = time.perf_counter_ns() - begin
    return elapsed, result


def main(output_path: str) -> None:
    selected_ordinals = [
        ordinal for ordinal in range(BRANCH_COUNT)
        if ordinal % PHASE_ORIGIN_COUNT == QUERY_PHASE_ORIGIN
    ]
    if len(selected_ordinals) != 2:
        raise AssertionError(selected_ordinals)

    baseline_ns: list[int] = []
    selected_ns: list[int] = []
    semantic_equal = True
    physical_gpu_seen = False
    backend_records: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="hhs-pass219b-i2-") as tmp:
        continuation = Pass205ContinuationRuntime(pathlib.Path(tmp) / "pass205.sqlite3")
        parent = continuation.snapshot(continuation.genesis_root216)

        baseline = Pass208GPUBranchManifold(
            enabled=True,
            backend="CPU_REFERENCE",
            require_physical_gpu=False,
            max_branches=BRANCH_COUNT,
            cache_capacity_bytes=32 * 1024 * 1024,
            cache_capacity_entries=4,
        )
        selected = Pass208GPUBranchManifold(
            enabled=True,
            backend="CPU_REFERENCE",
            require_physical_gpu=False,
            max_branches=BRANCH_COUNT,
            cache_capacity_bytes=32 * 1024 * 1024,
            cache_capacity_entries=4,
        )
        try:
            # Warm both runtimes outside the measured region.
            warm = [[{"cell": 0, "control_g": 0, "xor_mask": 1}]]
            baseline.expand(
                parent_snapshot=parent,
                branches=warm,
                bytecode_hydration_lattice_root216=parent["constraint_root216"],
            )
            selected.expand(
                parent_snapshot=parent,
                branches=warm,
                bytecode_hydration_lattice_root216=parent["constraint_root216"],
            )

            for repetition in range(REPETITIONS):
                branches = make_branches(1009 + repetition * 997)
                phase_branches = [branches[i] for i in selected_ordinals]

                full_elapsed, full = run_expand(baseline, parent, branches)
                selected_elapsed, phase = run_expand(selected, parent, phase_branches)
                baseline_ns.append(full_elapsed)
                selected_ns.append(selected_elapsed)

                physical_gpu_seen = physical_gpu_seen or bool(full["physical_gpu"]) or bool(phase["physical_gpu"])
                backend_records.append(
                    {
                        "baseline": full["driver"],
                        "selected": phase["driver"],
                    }
                )

                if full["branch_count"] != BRANCH_COUNT:
                    raise AssertionError(full["branch_count"])
                if phase["branch_count"] != len(selected_ordinals):
                    raise AssertionError(phase["branch_count"])
                if full["logical_lane_dispatches"] != BRANCH_COUNT * 5184:
                    raise AssertionError(full["logical_lane_dispatches"])
                if phase["logical_lane_dispatches"] != len(selected_ordinals) * 5184:
                    raise AssertionError(phase["logical_lane_dispatches"])

                # Phase preselection re-numbers Pass-208 branch ordinals, so candidate roots are
                # intentionally not used as the equality witness here. The actual VM81 child
                # states/projections must remain byte-for-byte/equality identical.
                for local_ordinal, original_ordinal in enumerate(selected_ordinals):
                    full_candidate = full["candidates"][original_ordinal]
                    phase_candidate = phase["candidates"][local_ordinal]
                    if full_candidate["child_state_words"] != phase_candidate["child_state_words"]:
                        semantic_equal = False
                    if (
                        full_candidate["child_projection_channels"]
                        != phase_candidate["child_projection_channels"]
                    ):
                        semantic_equal = False
                    if full_candidate["objective_distance"] != phase_candidate["objective_distance"]:
                        semantic_equal = False
        finally:
            baseline.close()
            selected.close()

    if not semantic_equal:
        raise AssertionError("phase-selected Pass 208 child semantics diverged")
    if physical_gpu_seen:
        raise AssertionError("CPU_REFERENCE benchmark unexpectedly reported a physical GPU")

    baseline_median = int(statistics.median(baseline_ns))
    selected_median = int(statistics.median(selected_ns))
    baseline_dispatches = BRANCH_COUNT * 5184
    selected_dispatches = len(selected_ordinals) * 5184

    result = {
        "schema": SCHEMA,
        "backend": "CPU_REFERENCE",
        "physical_gpu": False,
        "repetitions": REPETITIONS,
        "phase_origin_count": PHASE_ORIGIN_COUNT,
        "query_phase_origin": QUERY_PHASE_ORIGIN,
        "baseline_branch_count": BRANCH_COUNT,
        "phase_selected_branch_count": len(selected_ordinals),
        "selected_original_ordinals": selected_ordinals,
        "baseline_logical_lane_dispatches": baseline_dispatches,
        "phase_logical_lane_dispatches": selected_dispatches,
        "work_reduction_x1000": ratio_x1000(baseline_dispatches, selected_dispatches),
        "baseline_median_ns": baseline_median,
        "phase_median_ns": selected_median,
        "wall_speedup_x1000": ratio_x1000(baseline_median, selected_median),
        "child_state_projection_equal": True,
        "candidate_root_identity_compared": False,
        "candidate_root_identity_reason": "Pass208 branch_candidate_root216 binds local branch_ordinal; preselection re-numbers the subset",
        "physical_gpu_measurement_required_before_physical_gpu_speedup_claim": True,
        "authoritative_state_changed": False,
        "driver_samples": backend_records,
    }
    pathlib.Path(output_path).write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        raise SystemExit("usage: pass219b_pass208_cpu_reference_benchmark.py OUTPUT.json")
    main(sys.argv[1])

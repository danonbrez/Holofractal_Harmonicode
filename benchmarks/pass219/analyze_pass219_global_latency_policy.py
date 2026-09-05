from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

FOLD7_SCHEMA = "HHS_PASS_219B_ANDROID_WEBGPU_FOLD7_TUNING_V1"
CPU_SCHEMA = "HHS_PASS_219B_I2_PASS208_CPU_REFERENCE_BENCHMARK_V1"
PHASE_SCHEMA = "HHS_PASS_219B_I2_PHASE_LOCALITY_BENCHMARK_V1"
OVERHEAD_SCHEMA = "HHS_PASS219_GLOBAL_LATENCY_POLICY_OVERHEAD_BENCHMARK_V1"
OUTPUT_SCHEMA = "HHS_PASS219_GLOBAL_LATENCY_POLICY_25_3_BENCHMARK_DECISION_V1"

A2 = 1
B2 = 2
C2 = 3
D2 = 5
MEAN_RATIO = Fraction(25, 3)
TIER_NS = {
    1: Fraction(25_000_000, 3),
    2: Fraction(50_000_000, 3),
    3: Fraction(100_000_000, 3),
}
TIER_FPS = {1: 120, 2: 60, 3: 30}


def frac_obj(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def ratio_x1000(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        return 0
    return numerator * 1000 // denominator


def classify_ns(value: int) -> int:
    if value < 0:
        raise ValueError("latency must be non-negative")
    observed = Fraction(value, 1)
    for tier in (1, 2, 3):
        if observed <= TIER_NS[tier]:
            return tier
    return 4


def require_schema(obj: dict[str, Any], expected: str) -> None:
    if obj.get("schema") != expected:
        raise ValueError(f"expected schema {expected}, got {obj.get('schema')!r}")


def load(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def analyze(
    fold7: dict[str, Any],
    cpu: dict[str, Any],
    phase: dict[str, Any],
    overhead: dict[str, Any],
) -> dict[str, Any]:
    require_schema(fold7, FOLD7_SCHEMA)
    require_schema(cpu, CPU_SCHEMA)
    require_schema(phase, PHASE_SCHEMA)
    require_schema(overhead, OVERHEAD_SCHEMA)

    if Fraction(D2 * D2, C2) != MEAN_RATIO:
        raise AssertionError("d^4/c^2 identity failed")
    if Fraction((B2 + C2) ** 2, A2 + B2) != MEAN_RATIO:
        raise AssertionError("(b^2+c^2)^2/(a^2+b^2) identity failed")

    if MEAN_RATIO * 120 != 1000:
        raise AssertionError("Tier 1 fps closure failed")
    if MEAN_RATIO * 2 * 60 != 1000:
        raise AssertionError("Tier 2 fps closure failed")
    if MEAN_RATIO * 4 * 30 != 1000:
        raise AssertionError("Tier 3 fps closure failed")

    claim = fold7.get("claimBoundary") or {}
    if claim.get("hardwareGpuMeasured") is not True:
        raise ValueError("Fold7 evidence must contain physical GPU timing")
    if claim.get("authoritativeStateChanged") is not False:
        raise ValueError("Fold7 evidence must remain non-authoritative")
    if claim.get("integerOnlyKernel") is not True:
        raise ValueError("Fold7 kernel must remain integer only")

    physical_results = fold7.get("results") or []
    if not physical_results:
        raise ValueError("Fold7 scaling results missing")
    if not all(item.get("exactSelectedSampleEquality") is True for item in physical_results):
        raise ValueError("all Fold7 selected samples must remain exact")

    dense = fold7.get("dense") or {}
    dense_host_ns = int(dense["hostTotalMedianNs"])
    dense_gpu_ns = int(dense["gpuMedianNs"])
    dense_lanes = int(fold7["denseLaneDispatches"])
    dense_tier_host = classify_ns(dense_host_ns)
    dense_tier_gpu = classify_ns(dense_gpu_ns)

    tier1_physical = [
        item
        for item in physical_results
        if item.get("exactSelectedSampleEquality") is True
        and classify_ns(int(item["hostTotalMedianNs"])) == 1
    ]
    if not tier1_physical:
        raise ValueError("no exact Fold7 result satisfies Tier 1")

    largest_tier1 = max(
        tier1_physical,
        key=lambda item: (
            int(item["materializedCombinations"]),
            int(item["laneDispatches"]),
        ),
    )
    selected_m = int(largest_tier1["materializedCombinations"])
    selected_host_ns = int(largest_tier1["hostTotalMedianNs"])
    selected_gpu_ns = int(largest_tier1["gpuMedianNs"])
    selected_lanes = int(largest_tier1["laneDispatches"])
    selected_tier_host = classify_ns(selected_host_ns)
    selected_tier_gpu = classify_ns(selected_gpu_ns)

    work_reduction = Fraction(dense_lanes, selected_lanes)
    host_speedup = Fraction(dense_host_ns, selected_host_ns)
    gpu_speedup = Fraction(dense_gpu_ns, selected_gpu_ns)
    tier1_headroom = TIER_NS[1] / selected_host_ns
    dense_tier1_overrun = Fraction(dense_host_ns, 1) - TIER_NS[1]
    physical_latency_saved = Fraction(dense_host_ns - selected_host_ns, 1)

    if cpu.get("physical_gpu") is not False:
        raise ValueError("fresh CPU reference benchmark unexpectedly used physical GPU")
    if cpu.get("child_state_projection_equal") is not True:
        raise ValueError("fresh CPU selected child-state/projection equality failed")
    if cpu.get("authoritative_state_changed") is not False:
        raise ValueError("fresh CPU reference changed authoritative state")
    cpu_baseline_ns = int(cpu["baseline_median_ns"])
    cpu_phase_ns = int(cpu["phase_median_ns"])

    vector = phase.get("vector_shortlist") or {}
    cache = phase.get("cache_exact_lookup") or {}
    materialization = phase.get("materialization") or {}
    if vector.get("exact_result_equal") is not True:
        raise ValueError("phase vector equality failed")
    if cache.get("exact_result_equal") is not True:
        raise ValueError("phase cache equality failed")
    if materialization.get("exact_selected_equal") is not True:
        raise ValueError("phase materialization equality failed")
    if phase.get("authoritative_state_changed") is not False:
        raise ValueError("phase-local benchmark changed authoritative state")

    overhead_parts: dict[str, Fraction] = {}
    for key in ("classify", "route_select", "window_evaluate"):
        item = overhead.get(key) or {}
        iterations = int(item["iterations"])
        median_batch_ns = int(item["median_batch_ns"])
        if iterations <= 0 or median_batch_ns <= 0:
            raise ValueError(f"invalid overhead measurement for {key}")
        overhead_parts[key] = Fraction(median_batch_ns, iterations)

    conservative_policy_overhead_per_epoch = sum(
        overhead_parts.values(), Fraction(0, 1)
    )
    net_latency_saved = physical_latency_saved - conservative_policy_overhead_per_epoch
    overhead_vs_saved = (
        conservative_policy_overhead_per_epoch / physical_latency_saved
        if physical_latency_saved > 0
        else Fraction(0, 1)
    )
    overhead_vs_tier1_budget = conservative_policy_overhead_per_epoch / TIER_NS[1]

    physical_tier_improved = dense_tier_host > 1 and selected_tier_host == 1
    exact_work_reduced = selected_lanes < dense_lanes
    exact_semantics_preserved = (
        cpu.get("child_state_projection_equal") is True
        and all(item.get("exactSelectedSampleEquality") is True for item in physical_results)
        and vector.get("exact_result_equal") is True
        and cache.get("exact_result_equal") is True
        and materialization.get("exact_selected_equal") is True
    )
    authority_preserved = (
        claim.get("authoritativeStateChanged") is False
        and cpu.get("authoritative_state_changed") is False
        and phase.get("authoritative_state_changed") is False
        and overhead.get("authoritative_state_changed") is False
        and overhead.get("timing_is_noncanonical") is True
    )
    net_benefit_positive = net_latency_saved > 0

    promotion_supported = all(
        (
            physical_tier_improved,
            exact_work_reduced,
            exact_semantics_preserved,
            authority_preserved,
            net_benefit_positive,
        )
    )

    physical_points = []
    for item in physical_results:
        physical_points.append(
            {
                "materialized_combinations": int(item["materializedCombinations"]),
                "lane_dispatches": int(item["laneDispatches"]),
                "host_total_median_ns": int(item["hostTotalMedianNs"]),
                "gpu_median_ns": int(item["gpuMedianNs"]),
                "host_tier": classify_ns(int(item["hostTotalMedianNs"])),
                "gpu_tier": classify_ns(int(item["gpuMedianNs"])),
                "exact_selected_sample_equality": bool(item["exactSelectedSampleEquality"]),
            }
        )

    return {
        "schema": OUTPUT_SCHEMA,
        "classification": (
            "GLOBAL_LATENCY_POLICY_PROMOTION_SUPPORTED"
            if promotion_supported
            else "GLOBAL_LATENCY_POLICY_REMAINS_BENCHMARK_ONLY"
        ),
        "exact_policy": {
            "a2": A2,
            "b2": B2,
            "c2": C2,
            "d2": D2,
            "mean_ratio_ms": frac_obj(MEAN_RATIO),
            "d4_over_c2": frac_obj(Fraction(D2 * D2, C2)),
            "sum_square_ratio": frac_obj(
                Fraction((B2 + C2) ** 2, A2 + B2)
            ),
            "tiers": [
                {
                    "tier": tier,
                    "fps": TIER_FPS[tier],
                    "budget_ns": frac_obj(TIER_NS[tier]),
                }
                for tier in (1, 2, 3)
            ],
            "window_policy": {
                "mean_max_tier": 1,
                "p95_max_tier": 2,
                "max_max_tier": 3,
            },
        },
        "physical_fold7": {
            "device": fold7.get("targetDevice", {}),
            "adapter": fold7.get("adapterInfo", {}),
            "dense": {
                "host_total_median_ns": dense_host_ns,
                "gpu_median_ns": dense_gpu_ns,
                "host_tier": dense_tier_host,
                "gpu_tier": dense_tier_gpu,
                "lane_dispatches": dense_lanes,
            },
            "largest_measured_tier1_exact_slice": {
                "materialized_combinations": selected_m,
                "host_total_median_ns": selected_host_ns,
                "gpu_median_ns": selected_gpu_ns,
                "host_tier": selected_tier_host,
                "gpu_tier": selected_tier_gpu,
                "lane_dispatches": selected_lanes,
                "work_reduction": frac_obj(work_reduction),
                "work_reduction_x1000": ratio_x1000(dense_lanes, selected_lanes),
                "host_speedup": frac_obj(host_speedup),
                "host_speedup_x1000": ratio_x1000(dense_host_ns, selected_host_ns),
                "gpu_speedup": frac_obj(gpu_speedup),
                "gpu_speedup_x1000": ratio_x1000(dense_gpu_ns, selected_gpu_ns),
                "tier1_headroom": frac_obj(tier1_headroom),
                "tier1_headroom_x1000": int(tier1_headroom * 1000),
            },
            "dense_tier1_overrun_ns": frac_obj(dense_tier1_overrun),
            "physical_latency_saved_ns": frac_obj(physical_latency_saved),
            "points": physical_points,
            "claim_boundary": claim,
        },
        "fresh_cpu_reference": {
            "backend": cpu.get("backend"),
            "baseline_median_ns": cpu_baseline_ns,
            "phase_median_ns": cpu_phase_ns,
            "baseline_tier": classify_ns(cpu_baseline_ns),
            "phase_tier": classify_ns(cpu_phase_ns),
            "work_reduction_x1000": int(cpu["work_reduction_x1000"]),
            "wall_speedup_x1000": int(cpu["wall_speedup_x1000"]),
            "child_state_projection_equal": True,
            "physical_gpu": False,
        },
        "fresh_phase_locality": {
            "vector_shortlist": {
                "dense_median_ns": int(vector["dense_median_ns"]),
                "phase_median_ns": int(vector["phase_median_ns"]),
                "dense_tier": classify_ns(int(vector["dense_median_ns"])),
                "phase_tier": classify_ns(int(vector["phase_median_ns"])),
                "work_reduction_x1000": int(vector["work_reduction_x1000"]),
                "wall_speedup_x1000": int(vector["wall_speedup_x1000"]),
                "exact_equal": True,
            },
            "cache_exact_lookup": {
                "hash_map_median_ns": int(cache["hash_map_median_ns"]),
                "phase_address_median_ns": int(cache["phase_address_median_ns"]),
                "hash_map_tier": classify_ns(int(cache["hash_map_median_ns"])),
                "phase_address_tier": classify_ns(int(cache["phase_address_median_ns"])),
                "wall_speedup_x1000": int(cache["wall_speedup_x1000"]),
                "exact_equal": True,
            },
            "materialization": {
                "full_median_ns": int(materialization["full_median_ns"]),
                "selected_median_ns": int(materialization["selected_median_ns"]),
                "full_tier": classify_ns(int(materialization["full_median_ns"])),
                "selected_tier": classify_ns(int(materialization["selected_median_ns"])),
                "capacity_reduction_x1000": int(
                    materialization["capacity_reduction_x1000"]
                ),
                "wall_speedup_x1000": int(materialization["wall_speedup_x1000"]),
                "exact_equal": True,
            },
        },
        "policy_overhead": {
            key: {
                "per_call_ns": frac_obj(value),
                "per_call_ns_x1000": int(value * 1000),
            }
            for key, value in overhead_parts.items()
        }
        | {
            "conservative_one_each_per_epoch_ns": frac_obj(
                conservative_policy_overhead_per_epoch
            ),
            "overhead_vs_physical_latency_saved": frac_obj(overhead_vs_saved),
            "overhead_vs_physical_latency_saved_ppm": int(
                overhead_vs_saved * 1_000_000
            ),
            "overhead_vs_tier1_budget": frac_obj(overhead_vs_tier1_budget),
            "overhead_vs_tier1_budget_ppm": int(
                overhead_vs_tier1_budget * 1_000_000
            ),
            "net_latency_saved_ns": frac_obj(net_latency_saved),
        },
        "promotion_gates": {
            "physical_tier_improved_to_tier1": physical_tier_improved,
            "exact_work_reduced": exact_work_reduced,
            "exact_semantics_preserved": exact_semantics_preserved,
            "authority_preserved": authority_preserved,
            "net_benefit_positive_after_policy_overhead": net_benefit_positive,
            "supported": promotion_supported,
        },
        "claim_boundary": {
            "timing_is_noncanonical": True,
            "physical_gpu_timing_reused_from_existing_fold7_evidence": True,
            "fresh_ci_physical_gpu_measured": False,
            "full_dense_lane_equality_claimed_from_fold7": False,
            "selected_branch_child_state_projection_equality_rechecked_on_cpu": True,
            "canonical_state_authority_changed": False,
        },
    }


def main() -> int:
    if len(sys.argv) != 6:
        print(
            "usage: analyze_pass219_global_latency_policy.py "
            "FOLD7.json CPU.json PHASE.json OVERHEAD.json OUTPUT.json",
            file=sys.stderr,
        )
        return 2
    result = analyze(
        load(sys.argv[1]),
        load(sys.argv[2]),
        load(sys.argv[3]),
        load(sys.argv[4]),
    )
    Path(sys.argv[5]).write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

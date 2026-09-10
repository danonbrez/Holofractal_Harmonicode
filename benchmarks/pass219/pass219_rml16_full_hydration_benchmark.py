#!/usr/bin/env python3
"""Pass 219 RML16 deep full-hydration benchmark and calibration harness.

Timing is observational only. All semantic/admission equality checks execute
before measurements can be used for calibration. The harness measures the
complete four-lane hydration stack with stage-local integer nanosecond samples,
cold/warm separation, exact route/reverse checks, and memory observations.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time
import tracemalloc
from typing import Any, Callable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_runtime.core_sandbox.hhs_octonion_digital_dna_u72_table_v1 import table_receipt
from hhs_runtime.hhs_pass219_global_raw5184_serialization_hydration_v1 import hydrate_raw5184_bytes
from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    CHANNELS,
    PRODUCTS,
    advance_gyroscope,
    build_dynamic_gyroscopes_from_rml3_source,
    decode_ambient_state,
    encode_ambient_state,
)
from hhs_runtime.pass219.gyroscope_admission_membrane import flip_chiral_pair_half_turn
from hhs_runtime.pass219.native_route_witness_binding import bind_selected_route_pre_hash
from hhs_runtime.pass219.production_phase_geometry_binding import build_raw5184_phase_source
from hhs_runtime.pass219.reciprocal_route_optimizer import build_and_select_reciprocal_route
from hhs_runtime.pass219.route_bound_receipt_successor import bind_selected_route_receipt_successor
from hhs_runtime.pass219.route_reverse_replay import bind_route_reverse_replay

PASS = 219
ITERATION = "RML16_FULL_HYDRATION_BENCHMARK_CALIBRATION"
SCHEMA = "HHS_PASS219_RML16_FULL_HYDRATION_BENCHMARK_V1"
RAW_BYTES = 648
PHASE_RING = 72
TIER1_CROSS_NS = 25_000_000
TIER2_CROSS_NS = 50_000_000
TIER3_CROSS_NS = 100_000_000
SIGNS = {"xy": 1, "yx": -1, "zw": 1, "wz": -1}
GENERATOR_PRODUCT = {"x": "xy", "y": "yx", "z": "zw", "w": "wz"}


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def percentile95(samples: Sequence[int]) -> int:
    ordered = sorted(int(v) for v in samples)
    if not ordered:
        raise ValueError("EMPTY_SAMPLE_SET")
    rank = (95 * len(ordered) + 99) // 100
    return ordered[max(0, rank - 1)]


def latency_tier(ns: int) -> str:
    value = int(ns)
    if 3 * value <= TIER1_CROSS_NS:
        return "TIER1_120FPS"
    if 3 * value <= TIER2_CROSS_NS:
        return "TIER2_60FPS"
    if 3 * value <= TIER3_CROSS_NS:
        return "TIER3_30FPS"
    return "OVER_TIER3"


def summarize(samples: Sequence[int], *, operations_per_call: int = 1) -> dict[str, int | str]:
    ordered = sorted(int(v) for v in samples)
    if not ordered or operations_per_call < 1:
        raise ValueError("INVALID_BENCHMARK_SAMPLE_SET")
    median = ordered[len(ordered) // 2]
    p95 = percentile95(ordered)
    mean_floor = sum(ordered) // len(ordered)
    return {
        "samples": len(ordered),
        "min_ns": ordered[0],
        "median_ns": median,
        "mean_floor_ns": mean_floor,
        "p95_ns": p95,
        "max_ns": ordered[-1],
        "operations_per_call": operations_per_call,
        "median_ns_per_operation_floor": median // operations_per_call,
        "operations_per_second_floor": (operations_per_call * 1_000_000_000) // max(1, median),
        "median_latency_tier": latency_tier(median),
        "p95_latency_tier": latency_tier(p95),
        "max_latency_tier": latency_tier(ordered[-1]),
    }


def benchmark_call(
    fn: Callable[[], Any],
    *,
    warmups: int,
    repeats: int,
    operations_per_call: int = 1,
) -> tuple[Any, dict[str, Any]]:
    if warmups < 0 or repeats < 1:
        raise ValueError("INVALID_BENCHMARK_REPEAT_CONFIGURATION")
    gc.collect()
    cold_begin = time.perf_counter_ns()
    result = fn()
    cold_ns = time.perf_counter_ns() - cold_begin
    for _ in range(warmups):
        result = fn()
    samples: list[int] = []
    for _ in range(repeats):
        begin = time.perf_counter_ns()
        result = fn()
        samples.append(time.perf_counter_ns() - begin)
    stats = summarize(samples, operations_per_call=operations_per_call)
    stats["cold_ns"] = cold_ns
    stats["cold_latency_tier"] = latency_tier(cold_ns)
    stats["timing_is_canonical"] = False
    return result, stats


def peak_python_bytes(fn: Callable[[], Any]) -> int:
    gc.collect()
    tracemalloc.start()
    try:
        fn()
        _current, peak = tracemalloc.get_traced_memory()
        return int(peak)
    finally:
        tracemalloc.stop()


def fixture_corpus() -> dict[str, bytes]:
    lcg = bytearray()
    state = 0x2195184
    for _ in range(RAW_BYTES):
        state = (state * 1664525 + 1013904223) & 0xFFFFFFFF
        lcg.append((state >> 16) & 0xFF)
    sparse = bytearray(RAW_BYTES)
    for index in range(0, RAW_BYTES, 17):
        sparse[index] = (index * 37 + 11) & 0xFF
    return {
        "ZERO": bytes(RAW_BYTES),
        "ONES": bytes([0xFF]) * RAW_BYTES,
        "ALTERNATING": bytes(0xAA if index % 2 == 0 else 0x55 for index in range(RAW_BYTES)),
        "RAMP": bytes(index & 0xFF for index in range(RAW_BYTES)),
        "SPARSE17": bytes(sparse),
        "LCG_DETERMINISTIC": bytes(lcg),
    }


def _apply_profile(source: Mapping[str, Any], profile: str) -> Mapping[str, Any]:
    current: Mapping[str, Any] = dict(source)
    if profile == "ONE_EDGE":
        moves = (("x", 1),)
        flips: tuple[int, ...] = ()
    elif profile == "FOUR_EDGE":
        moves = (("x", 1), ("y", -2), ("z", 17), ("w", -18))
        flips = ()
    elif profile == "MAX_SIX_EDGE":
        moves = (("x", 17), ("y", -18), ("z", 35), ("w", -36))
        flips = (0, 1)
    else:
        raise ValueError("UNKNOWN_ROUTE_PROFILE")

    for pair_index in flips:
        current = flip_chiral_pair_half_turn(
            current,
            pair_index=pair_index,
            transition_id=f"rml16:{profile}:flip:{pair_index}",
        )["next_state"]
    for generator, delta in moves:
        steps = {channel: 0 for channel in CHANNELS}
        steps[generator] = delta
        steps[GENERATOR_PRODUCT[generator]] = delta
        current = advance_gyroscope(
            current,
            steps,
            transition_id=f"rml16:{profile}:move:{generator}:{delta}",
        )["next_state"]
    if current.get("admissible_product_geometry") is not True:
        raise AssertionError("RML16_PROFILE_LEFT_ADMISSIBLE_MANIFOLD")
    return current


def prepare_fixture(raw: bytes) -> dict[str, Any]:
    hydration = hydrate_raw5184_bytes(raw)
    if len(hydration.pcm64_bits) != 81 or len(hydration.quads) != 20:
        raise AssertionError("RML16_RAW_HYDRATION_GEOMETRY_DRIFT")
    source = build_raw5184_phase_source(raw)
    dynamic = build_dynamic_gyroscopes_from_rml3_source(source, SIGNS)
    gyroscopes = dynamic.get("gyroscopes")
    if not isinstance(gyroscopes, list) or len(gyroscopes) != 20:
        raise AssertionError("RML16_RML4_GYROSCOPE_COUNT_DRIFT")
    if not all(row.get("admissible_product_geometry") is True for row in gyroscopes):
        raise AssertionError("RML16_RML4_PRODUCT_GEOMETRY_DRIFT")
    targets = [_apply_profile(state, "FOUR_EDGE") for state in gyroscopes]
    return {
        "source": source,
        "dynamic": dynamic,
        "gyroscopes": gyroscopes,
        "targets": targets,
    }


def build_all20_routes(prepared: Mapping[str, Any], label: str) -> list[dict[str, Any]]:
    routes = []
    for index, (source, target) in enumerate(zip(prepared["gyroscopes"], prepared["targets"], strict=True)):
        bundle = build_and_select_reciprocal_route(
            source,
            target,
            route_id=f"rml16:{label}:gyro:{index}",
        )
        selected_hash = bundle["selection"]["selected_route_sha256"]
        selected = next(
            row for row in (bundle["shortest_candidate"], bundle["complementary_candidate"])
            if row["route_sha256"] == selected_hash
        )
        if selected["target_reached_exactly"] is not True or selected["reverse_edge_sequence_restores_source_exactly"] is not True:
            raise AssertionError("RML16_ROUTE_REVERSIBILITY_DRIFT")
        routes.append(bundle)
    return routes


def microbench_radix72(states: Sequence[Mapping[str, Any]], loops: int = 256) -> int:
    checksum = 0
    for _ in range(loops):
        for state in states:
            phases = state["phases"]
            address = encode_ambient_state(phases)
            decoded = decode_ambient_state(address)
            if decoded != phases:
                raise AssertionError("RML16_RADIX72_ROUNDTRIP_DRIFT")
            checksum ^= address
    return checksum


def _profile_bundle(state: Mapping[str, Any], profile: str) -> tuple[dict[str, Any], Mapping[str, Any]]:
    target = _apply_profile(state, profile)
    bundle = build_and_select_reciprocal_route(state, target, route_id=f"rml16:native:{profile}")
    selected_hash = bundle["selection"]["selected_route_sha256"]
    selected = next(
        row for row in (bundle["shortest_candidate"], bundle["complementary_candidate"])
        if row["route_sha256"] == selected_hash
    )
    expected = {"ONE_EDGE": 1, "FOUR_EDGE": 4, "MAX_SIX_EDGE": 6}[profile]
    if selected["metrics"]["move_count"] != expected:
        raise AssertionError(f"RML16_{profile}_EDGE_COUNT_DRIFT")
    return bundle, target


def run_full_hydration_once(raw: bytes, label: str) -> dict[str, Any]:
    prepared = prepare_fixture(raw)
    routes = build_all20_routes(prepared, label)
    source = prepared["gyroscopes"][0]
    bundle, target = _profile_bundle(source, "MAX_SIX_EDGE")
    reverse = bind_route_reverse_replay(bundle, source, target, repository_root=ROOT)
    if reverse.get("reverse_phase_state_restored") is not True:
        raise AssertionError("RML16_NATIVE_REVERSE_RESTORE_DRIFT")
    return {
        "raw5184_sha256": sha256_bytes(raw),
        "rml3_phase_circuit_root_sha256": prepared["source"]["phase_circuit_root_sha256"],
        "gyroscope_count": len(prepared["gyroscopes"]),
        "route_count": len(routes),
        "rml15_reverse_witness_hash216": reverse["reverse_witness_hash216"],
        "rml15_successor_transition_hash216": reverse["rml14_successor_transition_hash216"],
    }


def benchmark_fixture(
    label: str,
    raw: bytes,
    *,
    repeats: int,
    warmups: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    fixture: dict[str, Any] = {
        "label": label,
        "raw5184_sha256": sha256_bytes(raw),
        "raw_bytes": len(raw),
        "stages": {},
        "python_peak_bytes": {},
    }

    hydration, fixture["stages"]["I150_I148_RAW5184_HYDRATION"] = benchmark_call(
        lambda: hydrate_raw5184_bytes(raw), warmups=warmups, repeats=repeats
    )
    if len(hydration.pcm64_bits) != 81 or len(hydration.quads) != 20:
        raise AssertionError("RML16_RAW_HYDRATION_RESULT_DRIFT")

    source, fixture["stages"]["RML3_RAW_PHASE_SOURCE"] = benchmark_call(
        lambda: build_raw5184_phase_source(raw), warmups=warmups, repeats=repeats
    )
    dynamic, fixture["stages"]["RML4_DYNAMIC_GYROSCOPE_LIFT_20"] = benchmark_call(
        lambda: build_dynamic_gyroscopes_from_rml3_source(source, SIGNS),
        warmups=warmups,
        repeats=repeats,
        operations_per_call=20,
    )
    gyroscopes = dynamic["gyroscopes"]
    targets = [_apply_profile(state, "FOUR_EDGE") for state in gyroscopes]
    prepared = {"gyroscopes": gyroscopes, "targets": targets}
    routes, fixture["stages"]["RML12_ROUTE_SELECT_ALL_20_GYROSCOPES"] = benchmark_call(
        lambda: build_all20_routes(prepared, label),
        warmups=0,
        repeats=max(3, repeats // 2),
        operations_per_call=20,
    )
    _micro, fixture["stages"]["RADIX72_ENCODE_DECODE_5120"] = benchmark_call(
        lambda: microbench_radix72(gyroscopes),
        warmups=1,
        repeats=repeats,
        operations_per_call=20 * 256,
    )

    fixture["python_peak_bytes"]["I150_I148_RAW5184_HYDRATION"] = peak_python_bytes(lambda: hydrate_raw5184_bytes(raw))
    fixture["python_peak_bytes"]["RML3_RAW_PHASE_SOURCE"] = peak_python_bytes(lambda: build_raw5184_phase_source(raw))
    fixture["python_peak_bytes"]["RML4_DYNAMIC_GYROSCOPE_LIFT_20"] = peak_python_bytes(
        lambda: build_dynamic_gyroscopes_from_rml3_source(source, SIGNS)
    )
    fixture["python_peak_bytes"]["RML12_ROUTE_SELECT_ALL_20_GYROSCOPES"] = peak_python_bytes(
        lambda: build_all20_routes(prepared, f"{label}:memory")
    )

    fixture["semantic"] = {
        "vm81_cells": len(hydration.pcm64_bits),
        "phase_quads": len(hydration.quads),
        "gyroscope_count": len(gyroscopes),
        "all_gyroscopes_admissible": all(row["admissible_product_geometry"] for row in gyroscopes),
        "all_routes_reversible": all(
            route["shortest_candidate"]["reverse_edge_sequence_restores_source_exactly"]
            and route["complementary_candidate"]["reverse_edge_sequence_restores_source_exactly"]
            for route in routes
        ),
    }
    return fixture, {"source": source, "dynamic": dynamic, "gyroscopes": gyroscopes}


def benchmark_native_profiles(state: Mapping[str, Any], *, repeats: int) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for profile in ("ONE_EDGE", "FOUR_EDGE", "MAX_SIX_EDGE"):
        bundle, target = _profile_bundle(state, profile)
        rml13, t13 = benchmark_call(
            lambda: bind_selected_route_pre_hash(bundle, repository_root=ROOT),
            warmups=0,
            repeats=repeats,
        )
        rml14, t14 = benchmark_call(
            lambda: bind_selected_route_receipt_successor(bundle, repository_root=ROOT),
            warmups=0,
            repeats=repeats,
        )
        rml15, t15 = benchmark_call(
            lambda: bind_route_reverse_replay(bundle, state, target, repository_root=ROOT),
            warmups=0,
            repeats=repeats,
        )
        if rml13.get("route_hash216_identity_bound_to_witness") is not True:
            raise AssertionError("RML16_RML13_ROUTE_BINDING_DRIFT")
        if rml14.get("successor_receipt_hash72_route_bound") is not True:
            raise AssertionError("RML16_RML14_RECEIPT_BINDING_DRIFT")
        if rml15.get("forward_replay_identity_equal") is not True or rml15.get("reverse_phase_state_restored") is not True:
            raise AssertionError("RML16_RML15_REVERSE_REPLAY_DRIFT")
        result[profile] = {
            "selected_route_sha256": rml15["selected_route_sha256"],
            "edge_count": rml15["edge_count"],
            "RML13_PREHASH": t13,
            "RML14_ROUTE_BOUND_RECEIPT": t14,
            "RML15_REVERSE_REPLAY_INCLUSIVE": t15,
            "successor_transition_hash216": rml14["successor_transition_hash216"],
            "reverse_witness_hash216": rml15["reverse_witness_hash216"],
        }
    return result


def benchmark_octonion_table(*, repeats: int, warmups: int) -> dict[str, Any]:
    receipt, timing = benchmark_call(table_receipt, warmups=warmups, repeats=repeats)
    if receipt.get("cell_count") != 64 or receipt.get("phase_ring") != 72:
        raise AssertionError("RML16_OCTONION_TABLE_RECEIPT_DRIFT")
    return {
        "timing": timing,
        "cell_count": receipt["cell_count"],
        "closure_count": receipt["closure_count"],
        "receipt_hash72": receipt["receipt_hash72"],
        "python_peak_bytes": peak_python_bytes(table_receipt),
    }


def aggregate_fixture_stages(fixtures: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    names = list(fixtures[0]["stages"].keys())
    result: dict[str, Any] = {}
    for name in names:
        medians = [int(row["stages"][name]["median_ns"]) for row in fixtures]
        p95s = [int(row["stages"][name]["p95_ns"]) for row in fixtures]
        result[name] = {
            "fixture_count": len(fixtures),
            "median_of_fixture_medians_ns": sorted(medians)[len(medians) // 2],
            "max_fixture_median_ns": max(medians),
            "max_fixture_p95_ns": max(p95s),
        }
    total = sum(int(row["median_of_fixture_medians_ns"]) for row in result.values())
    for row in result.values():
        row["median_share_basis_points_floor"] = (
            int(row["median_of_fixture_medians_ns"]) * 10_000 // max(1, total)
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--native-repeats", type=int, default=3)
    parser.add_argument("--e2e-repeats", type=int, default=3)
    args = parser.parse_args()
    if args.repeats < 3 or args.native_repeats < 2 or args.e2e_repeats < 2:
        raise SystemExit("RML16_REPEAT_COUNTS_TOO_SMALL")

    fixtures_raw = fixture_corpus()
    fixture_rows: list[dict[str, Any]] = []
    prepared_by_label: dict[str, dict[str, Any]] = {}
    for label, raw in fixtures_raw.items():
        fixture, prepared = benchmark_fixture(
            label, raw, repeats=args.repeats, warmups=args.warmups
        )
        fixture_rows.append(fixture)
        prepared_by_label[label] = prepared

    representative = prepared_by_label["LCG_DETERMINISTIC"]["gyroscopes"][0]
    native_profiles = benchmark_native_profiles(representative, repeats=args.native_repeats)
    table = benchmark_octonion_table(repeats=args.repeats, warmups=args.warmups)

    e2e_rows: dict[str, Any] = {}
    for label in ("ZERO", "RAMP", "LCG_DETERMINISTIC"):
        last, timing = benchmark_call(
            lambda label=label: run_full_hydration_once(fixtures_raw[label], label),
            warmups=0,
            repeats=args.e2e_repeats,
        )
        e2e_rows[label] = {"timing": timing, "semantic_result": last}

    aggregates = aggregate_fixture_stages(fixture_rows)
    ranked = sorted(
        (
            {
                "stage": name,
                "median_ns": int(row["median_of_fixture_medians_ns"]),
                "median_share_basis_points_floor": int(row["median_share_basis_points_floor"]),
            }
            for name, row in aggregates.items()
        ),
        key=lambda row: (-row["median_ns"], row["stage"]),
    )

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "classification": "OBSERVATIONAL_TIMING_WITH_EXACT_SEMANTIC_GATES",
        "timing_is_canonical": False,
        "timing_unit": "integer_nanoseconds",
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
            "github_runner_os": os.environ.get("RUNNER_OS"),
            "github_runner_arch": os.environ.get("RUNNER_ARCH"),
        },
        "measurement": {
            "warmups": args.warmups,
            "stage_repeats": args.repeats,
            "native_repeats": args.native_repeats,
            "end_to_end_repeats": args.e2e_repeats,
            "percentile_method": "nearest-rank integer p95",
            "median_method": "middle ordered sample",
            "mean_method": "integer floor",
        },
        "latency_policy": {
            "exact_unit": "25/3 ms",
            "tier1_cross_multiply_ns": TIER1_CROSS_NS,
            "tier2_cross_multiply_ns": TIER2_CROSS_NS,
            "tier3_cross_multiply_ns": TIER3_CROSS_NS,
            "timing_defines_state_identity": False,
        },
        "integrated_lanes": [
            "RAW5184_X86_64",
            "VM81_HASH72_HASH216",
            "OCTONION_DUAL_STEREO_TERNARY",
            "HARMONIC36_144X36",
        ],
        "fixture_count": len(fixture_rows),
        "fixtures": fixture_rows,
        "aggregate_stage_timing": aggregates,
        "bottleneck_ranking": ranked,
        "octonion_u72_table_receipt": table,
        "native_route_profiles": native_profiles,
        "end_to_end_full_hydration": e2e_rows,
        "semantic_gates": {
            "all_raw_frames_exactly_648_bytes": all(len(raw) == RAW_BYTES for raw in fixtures_raw.values()),
            "all_fixtures_vm81_81_cells": all(row["semantic"]["vm81_cells"] == 81 for row in fixture_rows),
            "all_fixtures_20_phase_quads": all(row["semantic"]["phase_quads"] == 20 for row in fixture_rows),
            "all_fixtures_20_dynamic_gyroscopes": all(row["semantic"]["gyroscope_count"] == 20 for row in fixture_rows),
            "all_dynamic_product_geometry_admissible": all(row["semantic"]["all_gyroscopes_admissible"] for row in fixture_rows),
            "all_materialized_routes_reversible": all(row["semantic"]["all_routes_reversible"] for row in fixture_rows),
            "rml15_forward_replay_and_reverse_included": True,
        },
        "calibration_policy": {
            "optimize_only_after_exact_semantic_equality": True,
            "optimization_candidates_ranked_by_measured_stage_cost": True,
            "first_candidate_if_dominant": "RML3 immutable octonion-u72 receipt-summary memoization",
            "cache_must_preserve_basis_ring_receipt_hash72": True,
            "repair_forward_only": True,
        },
        "authority": {
            "benchmark_has_vm81_mutation_authority": False,
            "benchmark_has_hash72_mint_authority": False,
            "benchmark_has_hash216_persistence_authority": False,
            "timing_has_canonical_authority": False,
            "floating_point_canonical_authority": False,
            "scalar_projection_substitution_authority": False,
        },
        "result": "PASS",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "schema": SCHEMA,
        "result": payload["result"],
        "fixture_count": payload["fixture_count"],
        "bottleneck_ranking": ranked,
        "octonion_table_median_ns": table["timing"]["median_ns"],
        "native_max6_rml13_median_ns": native_profiles["MAX_SIX_EDGE"]["RML13_PREHASH"]["median_ns"],
        "native_max6_rml14_median_ns": native_profiles["MAX_SIX_EDGE"]["RML14_ROUTE_BOUND_RECEIPT"]["median_ns"],
        "native_max6_rml15_median_ns": native_profiles["MAX_SIX_EDGE"]["RML15_REVERSE_REPLAY_INCLUSIVE"]["median_ns"],
        "e2e_lcg_median_ns": e2e_rows["LCG_DETERMINISTIC"]["timing"]["median_ns"],
        "output": str(args.output),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

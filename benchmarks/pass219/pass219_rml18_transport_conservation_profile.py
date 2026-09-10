#!/usr/bin/env python3
"""Pass 219 RML18 dependency-scoped RML17 conservation profiler.

Profiles the frozen RML17 conservation membrane before any RML18 acceleration.
Timing is observational only. No timing value participates in the RML17
operator contract, candidate admission, VM81, Hash72, or Hash216 authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
from typing import Any, Mapping

from hhs_runtime.pass219.discrete_transport_conservation import (
    ADDRESS_COUNT,
    audit_composed_transport_conservation,
    audit_rml16_route_conservation,
    audit_transport_address,
    audit_transport_address_manifold,
)
from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    CHANNELS,
    PRODUCT_RELATIONS,
    advance_gyroscope,
    build_gyroscope_state,
    expected_product_phase,
)

PASS = 219
ITERATION = "RML18_TRANSPORT_CONSERVATION_PROFILE"
SCHEMA = "HHS_PASS219_RML18_TRANSPORT_CONSERVATION_PROFILE_V1"
SIGNS = {"xy": 1, "yx": -1, "zw": 1, "wz": -1}
ROUTE_SHAPE = (("x", 1), ("y", -2), ("z", 17), ("w", -18))


def _time(callable_):
    begin = time.perf_counter_ns()
    value = callable_()
    return value, time.perf_counter_ns() - begin


def _median(values: list[int]) -> int:
    ordered = sorted(values)
    return ordered[len(ordered) // 2]


def _source(index: int) -> dict[str, Any]:
    primitives = {
        "x": (7 + 5 * index) % 72,
        "y": (19 + 7 * index) % 72,
        "z": (31 + 11 * index) % 72,
        "w": (43 + 13 * index) % 72,
    }
    phases = {
        "x": primitives["x"],
        "y": primitives["y"],
        "z": primitives["z"],
        "w": primitives["w"],
        "xy": expected_product_phase(primitives["x"], SIGNS["xy"]),
        "yx": expected_product_phase(primitives["y"], SIGNS["yx"]),
        "zw": expected_product_phase(primitives["z"], SIGNS["zw"]),
        "wz": expected_product_phase(primitives["w"], SIGNS["wz"]),
    }
    state = build_gyroscope_state(phases, SIGNS, state_id=f"rml18:profile:source:{index}")
    if state["admissible_product_geometry"] is not True:
        raise AssertionError("RML18_PROFILE_SOURCE_NOT_ADMISSIBLE")
    return state


def _target(source: Mapping[str, Any], index: int) -> Mapping[str, Any]:
    current: Mapping[str, Any] = source
    for generator, delta in ROUTE_SHAPE:
        product = next(
            product
            for product, relation in PRODUCT_RELATIONS.items()
            if relation["generator"] == generator
        )
        steps = {channel: 0 for channel in CHANNELS}
        steps[generator] = delta
        steps[product] = delta
        current = advance_gyroscope(
            current,
            steps,
            transition_id=f"rml18:profile:target:{index}:{generator}:{delta}",
        )["next_state"]
    if current["admissible_product_geometry"] is not True:
        raise AssertionError("RML18_PROFILE_TARGET_NOT_ADMISSIBLE")
    return current


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--route-cases", type=int, default=6)
    args = parser.parse_args()
    if args.route_cases < 2:
        raise SystemExit("RML18_PROFILE_REQUIRES_AT_LEAST_TWO_ROUTE_CASES")

    representative_addresses = (0, 1, 80, 81, 5183, ADDRESS_COUNT // 2, ADDRESS_COUNT - 1)
    address_times: list[int] = []
    for address in representative_addresses:
        audit, elapsed = _time(lambda address=address: audit_transport_address(address))
        if audit["zero_discrete_divergence"] is not True or audit["reciprocal_edge_flux_balance"] is not True:
            raise AssertionError("RML18_PROFILE_RML17_ADDRESS_GATE_FAILED")
        address_times.append(elapsed)

    full_audit, full_elapsed = _time(audit_transport_address_manifold)
    if full_audit["result"] != "PASS" or full_audit["visited_address_count"] != ADDRESS_COUNT:
        raise AssertionError("RML18_PROFILE_FROZEN_RML17_FULL_AUDIT_FAILED")

    route_times: list[int] = []
    composition_times: list[int] = []
    route_audit_hashes: list[str] = []
    for index in range(args.route_cases):
        source = _source(index)
        middle = _target(source, index)
        target = _target(middle, index + args.route_cases)

        route_audit, elapsed = _time(
            lambda source=source, middle=middle, index=index: audit_rml16_route_conservation(
                source, middle, route_id=f"rml18:profile:route:{index}"
            )
        )
        if route_audit["result"] != "PASS":
            raise AssertionError("RML18_PROFILE_FROZEN_RML17_ROUTE_AUDIT_FAILED")
        route_times.append(elapsed)
        route_audit_hashes.append(route_audit["audit_sha256"])

        composition_audit, elapsed = _time(
            lambda source=source, middle=middle, target=target, index=index: audit_composed_transport_conservation(
                [source, middle, target], composition_id=f"rml18:profile:composition:{index}"
            )
        )
        if composition_audit["result"] != "PASS":
            raise AssertionError("RML18_PROFILE_FROZEN_RML17_COMPOSITION_AUDIT_FAILED")
        composition_times.append(elapsed)

    route_median = _median(route_times)
    composition_median = _median(composition_times)
    representative_median = _median(address_times)
    ranking = sorted(
        [
            {"surface": "RML17_FULL_ADDRESS_MANIFOLD", "median_ns": full_elapsed, "samples": 1},
            {"surface": "RML17_COMPOSED_ROUTE_AUDIT", "median_ns": composition_median, "samples": len(composition_times)},
            {"surface": "RML17_ROUTE_AUDIT", "median_ns": route_median, "samples": len(route_times)},
            {"surface": "RML17_SINGLE_ADDRESS_AUDIT", "median_ns": representative_median, "samples": len(address_times)},
        ],
        key=lambda row: (-row["median_ns"], row["surface"]),
    )

    payload = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "frozen_rml17_merge_commit": "eea9fcf5fa90589cb9adf2b26260af50e10fb377",
        "frozen_rml17_tree_sha256": "7f6271f39bda52a24946ac7d2786f8be8b93a3dd",
        "address_count": ADDRESS_COUNT,
        "representative_address_count": len(representative_addresses),
        "route_case_count": args.route_cases,
        "timing": {
            "full_address_manifold_ns": full_elapsed,
            "full_address_manifold_per_address_floor_ns": full_elapsed // ADDRESS_COUNT,
            "single_address_median_ns": representative_median,
            "route_audit_median_ns": route_median,
            "composed_route_audit_median_ns": composition_median,
        },
        "ranking": ranking,
        "rml17_full_audit_sha256": full_audit["audit_sha256"],
        "route_audit_sha256": route_audit_hashes,
        "semantic_equality_baseline_passed": True,
        "timing_is_canonical": False,
        "candidate_admission_from_timing": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "floating_point_authority": False,
        "result": "PASS",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

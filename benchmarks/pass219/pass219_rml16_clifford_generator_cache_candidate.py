#!/usr/bin/env python3
"""RML16 candidate benchmark for immutable Cl(0,8) generator reuse.

The candidate changes no canonical state and does not modify the RML10/RML11
source implementation. It temporarily substitutes an lru-cached wrapper around
RML10's pure build_cl08_generators() function inside the RML11 module, then
requires exact Python-object equality against the uncached reference for every
timed lift, classifier, RML12 edge, shortest plan, and full route bundle.

Timing is observational only. A latency win is rejected unless semantic
identity has already been proven for the corresponding invocation.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import json
from pathlib import Path
import time
from typing import Any, Callable, Mapping

from hhs_runtime.pass219 import phase_clifford_intertwiner as clifford
from hhs_runtime.pass219 import reciprocal_route_optimizer as route
from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    CHANNELS,
    PRODUCT_RELATIONS,
    advance_gyroscope,
    build_gyroscope_state,
    expected_product_phase,
)

PASS = 219
ITERATION = "RML16_IMMUTABLE_CL08_GENERATOR_CACHE_CANDIDATE"
SCHEMA = "HHS_PASS219_RML16_IMMUTABLE_CL08_GENERATOR_CACHE_CANDIDATE_V1"
SIGNS = {"xy": 1, "yx": -1, "zw": 1, "wz": -1}
ROUTE_SHAPE = (("x", 1), ("y", -2), ("z", 17), ("w", -18))


def _summary(values: list[int]) -> dict[str, int]:
    ordered = sorted(int(value) for value in values)
    if not ordered:
        raise ValueError("EMPTY_RML16_CANDIDATE_SAMPLE_SET")
    rank95 = (95 * len(ordered) + 99) // 100
    return {
        "samples": len(ordered),
        "min_ns": ordered[0],
        "median_ns": ordered[len(ordered) // 2],
        "mean_floor_ns": sum(ordered) // len(ordered),
        "p95_ns": ordered[max(0, rank95 - 1)],
        "max_ns": ordered[-1],
    }


def _time(fn: Callable[[], Any]) -> tuple[Any, int]:
    begin = time.perf_counter_ns()
    value = fn()
    return value, time.perf_counter_ns() - begin


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
    state = build_gyroscope_state(phases, SIGNS, state_id=f"rml16:cl08-cache:source:{index}")
    if state["admissible_product_geometry"] is not True:
        raise AssertionError("RML16_CL08_CACHE_SOURCE_NOT_ADMISSIBLE")
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
            transition_id=f"rml16:cl08-cache:target:{index}:{generator}:{delta}",
        )["next_state"]
    return current


def _speed_row(reference: dict[str, int], candidate: dict[str, int]) -> dict[str, int | bool]:
    baseline = reference["median_ns"]
    optimized = candidate["median_ns"]
    return {
        "reference_median_ns": baseline,
        "candidate_median_ns": optimized,
        "candidate_faster": optimized < baseline,
        "speedup_basis_points_floor": baseline * 10000 // max(1, optimized),
        "latency_reduction_basis_points_floor": max(0, baseline - optimized) * 10000 // max(1, baseline),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--states", type=int, default=8)
    args = parser.parse_args()
    if args.states < 4:
        raise SystemExit("RML16_CL08_CACHE_REQUIRES_AT_LEAST_FOUR_STATES")

    original_builder = clifford.build_cl08_generators
    cached_builder = lru_cache(maxsize=1)(original_builder)

    # Warm only already-validated invariant RML11 caches. The candidate cache is
    # deliberately populated once below and then measured on cross-request hits.
    clifford.build_one_gyroscope_clifford_channel_actions()
    cached_generators, fill_ns = _time(cached_builder)
    reference_generators = original_builder()
    if cached_generators != reference_generators:
        raise AssertionError("RML16_CL08_GENERATOR_CACHE_FILL_IDENTITY_DRIFT")
    if not isinstance(cached_generators, tuple) or any(not isinstance(row, tuple) for matrix in cached_generators for row in matrix):
        raise AssertionError("RML16_CL08_GENERATOR_CACHE_NOT_IMMUTABLE_TUPLE_GRAPH")

    reference_samples: dict[str, list[int]] = {
        "RML11_CLIFFORD_LIFT": [],
        "RML11_CLIFFORD_CLASSIFIER": [],
        "RML12_COUPLED_EDGE": [],
        "RML12_SHORTEST_PLAN": [],
        "RML12_FULL_BUNDLE": [],
    }
    candidate_samples = {name: [] for name in reference_samples}
    equality_counts = {name: 0 for name in reference_samples}

    try:
        for state_index in range(args.states):
            source = _source(state_index)
            target = _target(source, state_index)

            for generator, delta in ROUTE_SHAPE:
                product = next(
                    product
                    for product, relation in PRODUCT_RELATIONS.items()
                    if relation["generator"] == generator
                )
                steps = {channel: 0 for channel in CHANNELS}
                steps[generator] = delta
                steps[product] = delta
                tag = f"rml16:cl08-cache:{state_index}:{generator}:{delta}"

                clifford.build_cl08_generators = original_builder
                ref_lift, elapsed = _time(
                    lambda source=source, steps=steps, tag=tag: clifford.build_phase_transport_clifford_lift(
                        source, steps, transport_id=f"{tag}:lift"
                    )
                )
                reference_samples["RML11_CLIFFORD_LIFT"].append(elapsed)
                clifford.build_cl08_generators = cached_builder
                opt_lift, elapsed = _time(
                    lambda source=source, steps=steps, tag=tag: clifford.build_phase_transport_clifford_lift(
                        source, steps, transport_id=f"{tag}:lift"
                    )
                )
                candidate_samples["RML11_CLIFFORD_LIFT"].append(elapsed)
                if opt_lift != ref_lift:
                    raise AssertionError("RML16_CL08_CACHE_LIFT_IDENTITY_DRIFT")
                equality_counts["RML11_CLIFFORD_LIFT"] += 1

                clifford.build_cl08_generators = original_builder
                ref_class, elapsed = _time(
                    lambda source=source, generator=generator, delta=delta, tag=tag: clifford.classify_coupled_generator_clifford(
                        source,
                        generator=generator,
                        signed_steps=delta,
                        transition_id=f"{tag}:class",
                    )
                )
                reference_samples["RML11_CLIFFORD_CLASSIFIER"].append(elapsed)
                clifford.build_cl08_generators = cached_builder
                opt_class, elapsed = _time(
                    lambda source=source, generator=generator, delta=delta, tag=tag: clifford.classify_coupled_generator_clifford(
                        source,
                        generator=generator,
                        signed_steps=delta,
                        transition_id=f"{tag}:class",
                    )
                )
                candidate_samples["RML11_CLIFFORD_CLASSIFIER"].append(elapsed)
                if opt_class != ref_class:
                    raise AssertionError("RML16_CL08_CACHE_CLASSIFIER_IDENTITY_DRIFT")
                equality_counts["RML11_CLIFFORD_CLASSIFIER"] += 1

                clifford.build_cl08_generators = original_builder
                ref_edge, elapsed = _time(
                    lambda source=source, generator=generator, delta=delta, tag=tag: route.build_coupled_route_edge(
                        source,
                        generator=generator,
                        signed_steps=delta,
                        edge_id=f"{tag}:edge",
                    )
                )
                reference_samples["RML12_COUPLED_EDGE"].append(elapsed)
                clifford.build_cl08_generators = cached_builder
                opt_edge, elapsed = _time(
                    lambda source=source, generator=generator, delta=delta, tag=tag: route.build_coupled_route_edge(
                        source,
                        generator=generator,
                        signed_steps=delta,
                        edge_id=f"{tag}:edge",
                    )
                )
                candidate_samples["RML12_COUPLED_EDGE"].append(elapsed)
                if opt_edge != ref_edge:
                    raise AssertionError("RML16_CL08_CACHE_EDGE_IDENTITY_DRIFT")
                equality_counts["RML12_COUPLED_EDGE"] += 1

            clifford.build_cl08_generators = original_builder
            ref_plan, elapsed = _time(
                lambda source=source, target=target, state_index=state_index: route.build_reciprocal_route_plan(
                    source,
                    target,
                    route_id=f"rml16:cl08-cache:{state_index}:plan",
                    delta_policy=route.SHORTEST_POLICY,
                )
            )
            reference_samples["RML12_SHORTEST_PLAN"].append(elapsed)
            clifford.build_cl08_generators = cached_builder
            opt_plan, elapsed = _time(
                lambda source=source, target=target, state_index=state_index: route.build_reciprocal_route_plan(
                    source,
                    target,
                    route_id=f"rml16:cl08-cache:{state_index}:plan",
                    delta_policy=route.SHORTEST_POLICY,
                )
            )
            candidate_samples["RML12_SHORTEST_PLAN"].append(elapsed)
            if opt_plan != ref_plan:
                raise AssertionError("RML16_CL08_CACHE_PLAN_IDENTITY_DRIFT")
            equality_counts["RML12_SHORTEST_PLAN"] += 1

            clifford.build_cl08_generators = original_builder
            ref_bundle, elapsed = _time(
                lambda source=source, target=target, state_index=state_index: route.build_and_select_reciprocal_route(
                    source,
                    target,
                    route_id=f"rml16:cl08-cache:{state_index}:bundle",
                )
            )
            reference_samples["RML12_FULL_BUNDLE"].append(elapsed)
            clifford.build_cl08_generators = cached_builder
            opt_bundle, elapsed = _time(
                lambda source=source, target=target, state_index=state_index: route.build_and_select_reciprocal_route(
                    source,
                    target,
                    route_id=f"rml16:cl08-cache:{state_index}:bundle",
                )
            )
            candidate_samples["RML12_FULL_BUNDLE"].append(elapsed)
            if opt_bundle != ref_bundle:
                raise AssertionError("RML16_CL08_CACHE_BUNDLE_IDENTITY_DRIFT")
            equality_counts["RML12_FULL_BUNDLE"] += 1
    finally:
        clifford.build_cl08_generators = original_builder

    reference = {name: _summary(values) for name, values in reference_samples.items()}
    candidate = {name: _summary(values) for name, values in candidate_samples.items()}
    speed = {name: _speed_row(reference[name], candidate[name]) for name in reference}
    cache_info = cached_builder.cache_info()

    if not all(row["candidate_faster"] for row in speed.values()):
        raise AssertionError(f"RML16_CL08_CACHE_NO_BENEFIT:{speed}")

    payload = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "state_count": args.states,
        "route_shape": [[generator, delta] for generator, delta in ROUTE_SHAPE],
        "candidate": "PROCESS_LOCAL_IMMUTABLE_BUILD_CL08_GENERATORS_LRU_CACHE",
        "generator_cache_fill_ns": fill_ns,
        "generator_tuple_exact_equal_to_uncached_reference": True,
        "generator_tuple_immutable": True,
        "semantic_identity_equality_counts": equality_counts,
        "reference_timing": reference,
        "candidate_timing": candidate,
        "speed": speed,
        "cache_info": {
            "hits": cache_info.hits,
            "misses": cache_info.misses,
            "maxsize": cache_info.maxsize,
            "currsize": cache_info.currsize,
        },
        "public_rml10_abi_changed": False,
        "public_rml11_abi_changed": False,
        "public_rml12_abi_changed": False,
        "candidate_integrated_into_production": False,
        "timing_is_canonical": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "floating_point_canonical_authority": False,
        "scalar_projection_substitution_authority": False,
        "result": "PASS",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"schema": SCHEMA, "result": "PASS", "speed": speed, "cache_info": payload["cache_info"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

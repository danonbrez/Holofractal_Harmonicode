#!/usr/bin/env python3
"""RML16 candidate for exact signed-permutation Clifford multiplication.

The RML10 Cl(0,8) generators and the RML11 transport products generated from
them are exact signed-permutation matrices.  This candidate detects that
closed matrix class and composes row permutations/signs directly, while
falling back to the frozen dense exact RML11 `_matmul` for any matrix outside
the class.

The production RML10/RML11/RML12 source is not modified.  Every candidate
lift/classifier/edge/plan/bundle must be exactly equal to the unmodified
reference before timing can be accepted.
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
ITERATION = "RML16_SIGNED_PERMUTATION_CLIFFORD_MATMUL_CANDIDATE"
SCHEMA = "HHS_PASS219_RML16_SIGNED_PERMUTATION_CLIFFORD_MATMUL_CANDIDATE_V1"
SIGNS = {"xy": 1, "yx": -1, "zw": 1, "wz": -1}
ROUTE_SHAPE = (("x", 1), ("y", -2), ("z", 17), ("w", -18))


def _summary(values: list[int]) -> dict[str, int]:
    ordered = sorted(int(value) for value in values)
    if not ordered:
        raise ValueError("EMPTY_RML16_SIGNED_PERMUTATION_SAMPLE_SET")
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
    state = build_gyroscope_state(phases, SIGNS, state_id=f"rml16:signed-perm:source:{index}")
    if state["admissible_product_geometry"] is not True:
        raise AssertionError("RML16_SIGNED_PERMUTATION_SOURCE_NOT_ADMISSIBLE")
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
            transition_id=f"rml16:signed-perm:target:{index}:{generator}:{delta}",
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
        raise SystemExit("RML16_SIGNED_PERMUTATION_REQUIRES_AT_LEAST_FOUR_STATES")

    original_matmul = clifford._matmul
    counters = {"fast_path_calls": 0, "fallback_calls": 0}

    @lru_cache(maxsize=512)
    def descriptor(matrix: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, int], ...] | None:
        n = len(matrix)
        if n <= 0 or any(len(row) != n for row in matrix):
            return None
        result: list[tuple[int, int]] = []
        used_columns: set[int] = set()
        for row in matrix:
            nonzero = [(column, value) for column, value in enumerate(row) if value != 0]
            if len(nonzero) != 1:
                return None
            column, value = nonzero[0]
            if value not in (-1, 1) or column in used_columns:
                return None
            used_columns.add(column)
            result.append((column, value))
        if len(used_columns) != n:
            return None
        return tuple(result)

    def signed_permutation_matmul(left: Any, right: Any) -> Any:
        left_descriptor = descriptor(left)
        right_descriptor = descriptor(right)
        if left_descriptor is None or right_descriptor is None or len(left_descriptor) != len(right_descriptor):
            counters["fallback_calls"] += 1
            return original_matmul(left, right)
        n = len(left_descriptor)
        rows: list[tuple[int, ...]] = []
        for left_column, left_sign in left_descriptor:
            right_column, right_sign = right_descriptor[left_column]
            value = left_sign * right_sign
            rows.append(tuple(value if column == right_column else 0 for column in range(n)))
        counters["fast_path_calls"] += 1
        return tuple(rows)

    # Prove the fast operation itself on all invariant channel actions before
    # composing it into any higher RML11/RML12 result.
    actions = clifford._channel_action_matrices()
    identity = clifford._identity(16)
    operation_checks = 0
    for left in tuple(actions.values()) + (identity,):
        for right in tuple(actions.values()) + (identity,):
            if signed_permutation_matmul(left, right) != original_matmul(left, right):
                raise AssertionError("RML16_SIGNED_PERMUTATION_PRIMITIVE_PRODUCT_DRIFT")
            operation_checks += 1

    reference_samples: dict[str, list[int]] = {
        "RML11_CLIFFORD_LIFT": [],
        "RML11_CLIFFORD_CLASSIFIER": [],
        "RML12_COUPLED_EDGE": [],
        "RML12_SHORTEST_PLAN": [],
        "RML12_FULL_BUNDLE": [],
    }
    candidate_samples = {name: [] for name in reference_samples}
    equality_counts = {name: 0 for name in reference_samples}

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
            tag = f"rml16:signed-perm:{state_index}:{generator}:{delta}"

            clifford._matmul = original_matmul
            ref_lift, elapsed = _time(
                lambda: clifford.build_phase_transport_clifford_lift(source, steps, transport_id=f"{tag}:lift")
            )
            reference_samples["RML11_CLIFFORD_LIFT"].append(elapsed)
            clifford._matmul = signed_permutation_matmul
            opt_lift, elapsed = _time(
                lambda: clifford.build_phase_transport_clifford_lift(source, steps, transport_id=f"{tag}:lift")
            )
            candidate_samples["RML11_CLIFFORD_LIFT"].append(elapsed)
            if opt_lift != ref_lift:
                raise AssertionError("RML16_SIGNED_PERMUTATION_LIFT_IDENTITY_DRIFT")
            equality_counts["RML11_CLIFFORD_LIFT"] += 1

            clifford._matmul = original_matmul
            ref_class, elapsed = _time(
                lambda: clifford.classify_coupled_generator_clifford(
                    source, generator=generator, signed_steps=delta, transition_id=f"{tag}:class"
                )
            )
            reference_samples["RML11_CLIFFORD_CLASSIFIER"].append(elapsed)
            clifford._matmul = signed_permutation_matmul
            opt_class, elapsed = _time(
                lambda: clifford.classify_coupled_generator_clifford(
                    source, generator=generator, signed_steps=delta, transition_id=f"{tag}:class"
                )
            )
            candidate_samples["RML11_CLIFFORD_CLASSIFIER"].append(elapsed)
            if opt_class != ref_class:
                raise AssertionError("RML16_SIGNED_PERMUTATION_CLASSIFIER_IDENTITY_DRIFT")
            equality_counts["RML11_CLIFFORD_CLASSIFIER"] += 1

            clifford._matmul = original_matmul
            ref_edge, elapsed = _time(
                lambda: route.build_coupled_route_edge(source, generator=generator, signed_steps=delta, edge_id=f"{tag}:edge")
            )
            reference_samples["RML12_COUPLED_EDGE"].append(elapsed)
            clifford._matmul = signed_permutation_matmul
            opt_edge, elapsed = _time(
                lambda: route.build_coupled_route_edge(source, generator=generator, signed_steps=delta, edge_id=f"{tag}:edge")
            )
            candidate_samples["RML12_COUPLED_EDGE"].append(elapsed)
            if opt_edge != ref_edge:
                raise AssertionError("RML16_SIGNED_PERMUTATION_EDGE_IDENTITY_DRIFT")
            equality_counts["RML12_COUPLED_EDGE"] += 1

        clifford._matmul = original_matmul
        ref_plan, elapsed = _time(
            lambda: route.build_reciprocal_route_plan(
                source, target, route_id=f"rml16:signed-perm:{state_index}:plan", delta_policy=route.SHORTEST_POLICY
            )
        )
        reference_samples["RML12_SHORTEST_PLAN"].append(elapsed)
        clifford._matmul = signed_permutation_matmul
        opt_plan, elapsed = _time(
            lambda: route.build_reciprocal_route_plan(
                source, target, route_id=f"rml16:signed-perm:{state_index}:plan", delta_policy=route.SHORTEST_POLICY
            )
        )
        candidate_samples["RML12_SHORTEST_PLAN"].append(elapsed)
        if opt_plan != ref_plan:
            raise AssertionError("RML16_SIGNED_PERMUTATION_PLAN_IDENTITY_DRIFT")
        equality_counts["RML12_SHORTEST_PLAN"] += 1

        clifford._matmul = original_matmul
        ref_bundle, elapsed = _time(
            lambda: route.build_and_select_reciprocal_route(
                source, target, route_id=f"rml16:signed-perm:{state_index}:bundle"
            )
        )
        reference_samples["RML12_FULL_BUNDLE"].append(elapsed)
        clifford._matmul = signed_permutation_matmul
        opt_bundle, elapsed = _time(
            lambda: route.build_and_select_reciprocal_route(
                source, target, route_id=f"rml16:signed-perm:{state_index}:bundle"
            )
        )
        candidate_samples["RML12_FULL_BUNDLE"].append(elapsed)
        if opt_bundle != ref_bundle:
            raise AssertionError("RML16_SIGNED_PERMUTATION_BUNDLE_IDENTITY_DRIFT")
        equality_counts["RML12_FULL_BUNDLE"] += 1

    clifford._matmul = original_matmul
    reference = {name: _summary(values) for name, values in reference_samples.items()}
    candidate = {name: _summary(values) for name, values in candidate_samples.items()}
    speed = {name: _speed_row(reference[name], candidate[name]) for name in reference}
    descriptor_info = descriptor.cache_info()

    if counters["fast_path_calls"] <= 0:
        raise AssertionError("RML16_SIGNED_PERMUTATION_FAST_PATH_UNUSED")
    if not all(row["candidate_faster"] for row in speed.values()):
        raise AssertionError(f"RML16_SIGNED_PERMUTATION_NO_BENEFIT:{speed}")

    payload = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "state_count": args.states,
        "route_shape": [[generator, delta] for generator, delta in ROUTE_SHAPE],
        "candidate": "EXACT_SIGNED_PERMUTATION_COMPOSITION_WITH_DENSE_FALLBACK",
        "primitive_exact_product_checks": operation_checks,
        "semantic_identity_equality_counts": equality_counts,
        "reference_timing": reference,
        "candidate_timing": candidate,
        "speed": speed,
        "fast_path_calls": counters["fast_path_calls"],
        "fallback_calls": counters["fallback_calls"],
        "descriptor_cache": {
            "hits": descriptor_info.hits,
            "misses": descriptor_info.misses,
            "maxsize": descriptor_info.maxsize,
            "currsize": descriptor_info.currsize,
        },
        "fallback_preserves_dense_exact_matmul": True,
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
    print(json.dumps({
        "schema": SCHEMA,
        "result": "PASS",
        "speed": speed,
        "fast_path_calls": counters["fast_path_calls"],
        "fallback_calls": counters["fallback_calls"],
        "descriptor_cache": payload["descriptor_cache"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

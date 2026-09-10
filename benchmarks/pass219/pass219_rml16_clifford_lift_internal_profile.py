#!/usr/bin/env python3
"""RML16 internal profiler for the frozen RML11 Clifford lift.

This benchmark instruments helper boundaries at runtime without editing the
RML10/RML11/RML12 implementation.  Every profiled lift is compared against an
uninstrumented production lift with the same source, signed steps, and
transport id before timing evidence is accepted.

Reported timing is observational only and has no canonical authority.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import time
from typing import Any, Callable, Mapping

from hhs_runtime.pass219 import phase_clifford_intertwiner as clifford
from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    CHANNELS,
    PRODUCT_RELATIONS,
    advance_gyroscope,
    build_gyroscope_state,
    expected_product_phase,
)

PASS = 219
ITERATION = "RML16_CLIFFORD_LIFT_INTERNAL_PROFILE"
SCHEMA = "HHS_PASS219_RML16_CLIFFORD_LIFT_INTERNAL_PROFILE_V1"
SIGNS = {"xy": 1, "yx": -1, "zw": 1, "wz": -1}
ROUTE_SHAPE = (("x", 1), ("y", -2), ("z", 17), ("w", -18))

HELPERS = (
    "_require_state",
    "_normalize_signed_steps",
    "_channel_action_matrices",
    "build_cl08_generators",
    "_chirality_volume",
    "_identity",
    "decompose_signed_phase_step",
    "_matrix_power_order4",
    "_matmul",
    "_matrix_hash",
    "_commutes",
    "_anticommutes",
    "_scale",
    "build_one_gyroscope_clifford_channel_actions",
    "_sha256",
    "_canonical",
)


def _summary(values: list[int]) -> dict[str, int]:
    ordered = sorted(int(v) for v in values)
    if not ordered:
        return {"samples": 0, "min_ns": 0, "median_ns": 0, "mean_floor_ns": 0, "p95_ns": 0, "max_ns": 0}
    rank95 = (95 * len(ordered) + 99) // 100
    return {
        "samples": len(ordered),
        "min_ns": ordered[0],
        "median_ns": ordered[len(ordered) // 2],
        "mean_floor_ns": sum(ordered) // len(ordered),
        "p95_ns": ordered[max(0, rank95 - 1)],
        "max_ns": ordered[-1],
    }


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
    state = build_gyroscope_state(phases, SIGNS, state_id=f"rml16:clifford-profile:source:{index}")
    if state["admissible_product_geometry"] is not True:
        raise AssertionError("RML16_CLIFFORD_PROFILE_SOURCE_NOT_ADMISSIBLE")
    return state


def _cases(state_count: int) -> list[tuple[str, Mapping[str, Any], dict[str, int]]]:
    cases: list[tuple[str, Mapping[str, Any], dict[str, int]]] = []
    for state_index in range(state_count):
        state: Mapping[str, Any] = _source(state_index)
        for generator, delta in ROUTE_SHAPE:
            product = next(
                product
                for product, relation in PRODUCT_RELATIONS.items()
                if relation["generator"] == generator
            )
            steps = {channel: 0 for channel in CHANNELS}
            steps[generator] = delta
            steps[product] = delta
            case_id = f"rml16:clifford-profile:{state_index}:{generator}:{delta}"
            cases.append((case_id, state, steps))
            state = advance_gyroscope(
                state,
                steps,
                transition_id=f"{case_id}:advance",
            )["next_state"]
    return cases


class _ExclusiveProfiler:
    def __init__(self) -> None:
        self.stack: list[dict[str, int | str]] = []
        self.inclusive: dict[str, list[int]] = defaultdict(list)
        self.exclusive: dict[str, list[int]] = defaultdict(list)
        self.originals: dict[str, Callable[..., Any]] = {}

    def _wrap(self, name: str, fn: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            frame: dict[str, int | str] = {"name": name, "child_ns": 0}
            self.stack.append(frame)
            start = time.perf_counter_ns()
            try:
                return fn(*args, **kwargs)
            finally:
                elapsed = time.perf_counter_ns() - start
                completed = self.stack.pop()
                child_ns = int(completed["child_ns"])
                exclusive = max(0, elapsed - child_ns)
                self.inclusive[name].append(elapsed)
                self.exclusive[name].append(exclusive)
                if self.stack:
                    self.stack[-1]["child_ns"] = int(self.stack[-1]["child_ns"]) + elapsed
        wrapped.__name__ = getattr(fn, "__name__", name)
        wrapped.__doc__ = getattr(fn, "__doc__", None)
        return wrapped

    def install(self) -> None:
        for name in HELPERS:
            fn = getattr(clifford, name)
            self.originals[name] = fn
            setattr(clifford, name, self._wrap(name, fn))

    def restore(self) -> None:
        for name, fn in self.originals.items():
            setattr(clifford, name, fn)

    def report(self, total_ns: int) -> dict[str, Any]:
        rows: list[dict[str, Any]] = []
        for name in HELPERS:
            inclusive_values = self.inclusive.get(name, [])
            exclusive_values = self.exclusive.get(name, [])
            inclusive_total = sum(inclusive_values)
            exclusive_total = sum(exclusive_values)
            rows.append(
                {
                    "helper": name,
                    "calls": len(inclusive_values),
                    "inclusive_ns_total": inclusive_total,
                    "exclusive_ns_total": exclusive_total,
                    "exclusive_share_basis_points": exclusive_total * 10000 // max(1, total_ns),
                    "inclusive_per_call": _summary(inclusive_values),
                    "exclusive_per_call": _summary(exclusive_values),
                }
            )
        rows.sort(key=lambda row: (-row["exclusive_ns_total"], row["helper"]))
        exclusive_sum = sum(row["exclusive_ns_total"] for row in rows)
        return {
            "instrumented_total_ns": total_ns,
            "wrapped_helper_exclusive_ns_total": exclusive_sum,
            "unattributed_top_level_ns": max(0, total_ns - exclusive_sum),
            "unattributed_share_basis_points": max(0, total_ns - exclusive_sum) * 10000 // max(1, total_ns),
            "ranking": rows,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--states", type=int, default=8)
    args = parser.parse_args()
    if args.states < 4:
        raise SystemExit("RML16_CLIFFORD_PROFILE_REQUIRES_AT_LEAST_FOUR_STATES")

    # Warm only invariant caches already present in the frozen RML11 source.
    clifford._channel_action_matrices()
    clifford._chirality_volume()
    clifford.build_one_gyroscope_clifford_channel_actions()

    cases = _cases(args.states)
    references: dict[str, dict[str, Any]] = {}
    reference_elapsed: list[int] = []
    for case_id, state, steps in cases:
        start = time.perf_counter_ns()
        references[case_id] = clifford.build_phase_transport_clifford_lift(
            state,
            steps,
            transport_id=case_id,
        )
        reference_elapsed.append(time.perf_counter_ns() - start)

    profiler = _ExclusiveProfiler()
    profiled_elapsed: list[int] = []
    equality_count = 0
    profiler.install()
    try:
        start_all = time.perf_counter_ns()
        for case_id, state, steps in cases:
            start = time.perf_counter_ns()
            actual = clifford.build_phase_transport_clifford_lift(
                state,
                steps,
                transport_id=case_id,
            )
            profiled_elapsed.append(time.perf_counter_ns() - start)
            if actual != references[case_id]:
                raise AssertionError(f"RML16_CLIFFORD_INTERNAL_PROFILE_IDENTITY_DRIFT:{case_id}")
            equality_count += 1
        instrumented_total = time.perf_counter_ns() - start_all
    finally:
        profiler.restore()

    report = profiler.report(instrumented_total)
    ranking = report["ranking"]
    if not ranking:
        raise AssertionError("RML16_CLIFFORD_INTERNAL_PROFILE_EMPTY")

    payload = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "state_count": args.states,
        "case_count": len(cases),
        "route_shape": [[generator, delta] for generator, delta in ROUTE_SHAPE],
        "reference_lift_timing": _summary(reference_elapsed),
        "profiled_lift_timing": _summary(profiled_elapsed),
        "semantic_identity_equality_count": equality_count,
        "semantic_identity_verified": equality_count == len(cases),
        "profile": report,
        "dominant_exclusive_helper": ranking[0]["helper"],
        "dominant_exclusive_share_basis_points": ranking[0]["exclusive_share_basis_points"],
        "production_source_modified_by_profiler": False,
        "public_rml10_abi_changed": False,
        "public_rml11_abi_changed": False,
        "public_rml12_abi_changed": False,
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
        "reference_lift_median_ns": payload["reference_lift_timing"]["median_ns"],
        "profiled_lift_median_ns": payload["profiled_lift_timing"]["median_ns"],
        "dominant_exclusive_helper": payload["dominant_exclusive_helper"],
        "dominant_exclusive_share_basis_points": payload["dominant_exclusive_share_basis_points"],
        "top_five": ranking[:5],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Pass 219 RML16 residual internal attribution profiler.

Profiles the three coequal residual cold-route surfaces established after the
signed-permutation Clifford successor:

* RML11 Clifford classifier
* RML11 Clifford lift
* RML7 Hopf classifier

The profiler is observational only. It changes no production source, does not
select an optimization, and confers no VM81, Hash72, Hash216, floating-point,
scalar-projection, persistence, or timing authority.
"""
from __future__ import annotations

import argparse
import cProfile
import json
from pathlib import Path
import pstats
import time
from typing import Any, Callable, Mapping

# Import the canonical RML16 route surface so the validated exact
# signed-permutation successor is installed before residual attribution.
import hhs_runtime.pass219.reciprocal_route_cache as _rml16_route_cache  # noqa: F401
from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    CHANNELS,
    PRODUCT_RELATIONS,
    build_gyroscope_state,
    expected_product_phase,
)
from hhs_runtime.pass219.phase_clifford_intertwiner import (
    build_one_gyroscope_clifford_channel_actions,
    build_phase_transport_clifford_lift,
    classify_coupled_generator_clifford,
)
from hhs_runtime.pass219.discrete_hopf_projection import classify_coupled_generator_hopf

PASS = 219
ITERATION = "RML16_RESIDUAL_INTERNAL_PROFILE"
SCHEMA = "HHS_PASS219_RML16_RESIDUAL_INTERNAL_PROFILE_V1"
SIGNS = {"xy": 1, "yx": -1, "zw": 1, "wz": -1}
ROUTE_SHAPE = (("x", 1), ("y", -2), ("z", 17), ("w", -18))
PARENT_HEAD = "f41f7cec2e126d2d2114bc3463dfbc0e9b7518ec"


def _percentile95(values: list[int]) -> int:
    ordered = sorted(values)
    rank = (95 * len(ordered) + 99) // 100
    return ordered[max(0, rank - 1)]


def _summary(values: list[int]) -> dict[str, int]:
    ordered = sorted(int(value) for value in values)
    if not ordered:
        raise ValueError("EMPTY_RESIDUAL_PROFILE_SAMPLE_SET")
    return {
        "samples": len(ordered),
        "min_ns": ordered[0],
        "median_ns": ordered[len(ordered) // 2],
        "mean_floor_ns": sum(ordered) // len(ordered),
        "p95_ns": _percentile95(ordered),
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
    state = build_gyroscope_state(
        phases,
        SIGNS,
        state_id=f"rml16:residual:source:{index}",
    )
    if state["admissible_product_geometry"] is not True:
        raise AssertionError("RML16_RESIDUAL_SOURCE_NOT_ADMISSIBLE")
    return state


def _cases(state_count: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for state_index in range(state_count):
        state = _source(state_index)
        for generator, delta in ROUTE_SHAPE:
            product = next(
                product
                for product, relation in PRODUCT_RELATIONS.items()
                if relation["generator"] == generator
            )
            steps = {channel: 0 for channel in CHANNELS}
            steps[generator] = delta
            steps[product] = delta
            rows.append(
                {
                    "state_index": state_index,
                    "state": state,
                    "generator": generator,
                    "delta": delta,
                    "steps": steps,
                }
            )
    return rows


def _pass219_rows(profiler: cProfile.Profile) -> list[dict[str, Any]]:
    stats = pstats.Stats(profiler)
    raw_rows: list[dict[str, Any]] = []
    total_self_ns = 0
    for (filename, line, funcname), (_cc, calls, self_s, cumulative_s, _callers) in stats.stats.items():
        normalized = filename.replace("\\", "/")
        if "/hhs_runtime/pass219/" not in normalized:
            continue
        self_ns = int(self_s * 1_000_000_000)
        cumulative_ns = int(cumulative_s * 1_000_000_000)
        total_self_ns += self_ns
        raw_rows.append(
            {
                "helper": f"{Path(normalized).name}:{line}:{funcname}",
                "file": normalized.split("/hhs_runtime/pass219/", 1)[-1],
                "line": int(line),
                "function": funcname,
                "calls": int(calls),
                "self_ns_floor": self_ns,
                "cumulative_ns_floor": cumulative_ns,
            }
        )
    if not raw_rows or total_self_ns <= 0:
        raise AssertionError("RML16_RESIDUAL_NO_PASS219_PROFILE_ROWS")
    for row in raw_rows:
        row["self_share_basis_points_floor"] = row["self_ns_floor"] * 10000 // total_self_ns
    return sorted(
        raw_rows,
        key=lambda row: (-row["self_ns_floor"], -row["cumulative_ns_floor"], row["helper"]),
    )


def _profile_surface(
    *,
    name: str,
    cases: list[dict[str, Any]],
    invoke: Callable[[dict[str, Any], str], Mapping[str, Any]],
    semantic_gate: Callable[[Mapping[str, Any]], bool],
) -> dict[str, Any]:
    unprofiled_ns: list[int] = []
    semantic_equal_count = 0
    for index, case in enumerate(cases):
        begin = time.perf_counter_ns()
        result = invoke(case, f"rml16:residual:{name}:timed:{index}")
        unprofiled_ns.append(time.perf_counter_ns() - begin)
        if not semantic_gate(result):
            raise AssertionError(f"RML16_RESIDUAL_SEMANTIC_GATE_FAILED:{name}:timed:{index}")
        semantic_equal_count += 1

    profiler = cProfile.Profile()
    profiler.enable()
    profiled_semantic_count = 0
    for index, case in enumerate(cases):
        result = invoke(case, f"rml16:residual:{name}:profiled:{index}")
        if not semantic_gate(result):
            raise AssertionError(f"RML16_RESIDUAL_SEMANTIC_GATE_FAILED:{name}:profiled:{index}")
        profiled_semantic_count += 1
    profiler.disable()

    ranking = _pass219_rows(profiler)
    return {
        "surface": name,
        "unprofiled_timing": _summary(unprofiled_ns),
        "semantic_equal_count": semantic_equal_count,
        "profiled_semantic_equal_count": profiled_semantic_count,
        "dominant_helper": ranking[0]["helper"],
        "dominant_helper_self_share_basis_points_floor": ranking[0]["self_share_basis_points_floor"],
        "helper_ranking": ranking[:20],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--states", type=int, default=8)
    args = parser.parse_args()
    if args.states < 4:
        raise SystemExit("RML16_RESIDUAL_PROFILE_REQUIRES_AT_LEAST_FOUR_STATES")

    # Warm only the inherited immutable RML11 action/generator construction.
    # Request identities remain unique and no exact-request route bundle cache is used.
    build_one_gyroscope_clifford_channel_actions()

    cases = _cases(args.states)
    source_hashes = {case["state"]["state_sha256"] for case in cases}
    if len(source_hashes) != args.states:
        raise AssertionError("RML16_RESIDUAL_SOURCE_IDENTITIES_NOT_UNIQUE")

    def lift(case: dict[str, Any], tag: str) -> Mapping[str, Any]:
        return build_phase_transport_clifford_lift(
            case["state"],
            case["steps"],
            transport_id=tag,
        )

    def clifford(case: dict[str, Any], tag: str) -> Mapping[str, Any]:
        return classify_coupled_generator_clifford(
            case["state"],
            generator=case["generator"],
            signed_steps=case["delta"],
            transition_id=tag,
        )

    def hopf(case: dict[str, Any], tag: str) -> Mapping[str, Any]:
        return classify_coupled_generator_hopf(
            case["state"],
            generator=case["generator"],
            signed_steps=case["delta"],
            transition_id=tag,
        )

    surfaces = [
        _profile_surface(
            name="RML11_CLIFFORD_CLASSIFIER",
            cases=cases,
            invoke=clifford,
            semantic_gate=lambda result: result.get("target_product_geometry_admissible") is True,
        ),
        _profile_surface(
            name="RML11_CLIFFORD_LIFT",
            cases=cases,
            invoke=lift,
            semantic_gate=lambda result: result.get("ordered_reverse_factor_inverse_verified") is True,
        ),
        _profile_surface(
            name="RML7_HOPF_CLASSIFIER",
            cases=cases,
            invoke=hopf,
            semantic_gate=lambda result: result.get("explicit_inverse_restores_exact_hopf_base") is True,
        ),
    ]

    surface_ranking = sorted(
        (
            {
                "surface": row["surface"],
                "median_ns": row["unprofiled_timing"]["median_ns"],
                "dominant_helper": row["dominant_helper"],
                "dominant_helper_self_share_basis_points_floor": row[
                    "dominant_helper_self_share_basis_points_floor"
                ],
            }
            for row in surfaces
        ),
        key=lambda row: (-row["median_ns"], row["surface"]),
    )

    payload = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "parent_head": PARENT_HEAD,
        "state_count": args.states,
        "case_count": len(cases),
        "route_shape": [[generator, delta] for generator, delta in ROUTE_SHAPE],
        "all_source_state_hashes_unique": True,
        "rml16_signed_permutation_successor_loaded_before_profile": True,
        "surface_ranking": surface_ranking,
        "surfaces": surfaces,
        "optimization_selected_by_profiler": False,
        "production_source_modified_by_profiler": False,
        "exact_request_route_cache_used": False,
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
    print(json.dumps({"schema": SCHEMA, "result": "PASS", "surface_ranking": surface_ranking}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

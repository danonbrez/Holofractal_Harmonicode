#!/usr/bin/env python3
"""Pass 219 RML16 dependency-scoped cold RML12 route profiler.

This benchmark intentionally varies source state identity while repeating the
same four mechanical route shapes. Therefore the exact-request bundle cache
cannot turn these samples into hits. It ranks existing deterministic RML12,
RML7, RML11, and RML5 subcomputations before any additional optimization.

Timing is observational only and has no canonical authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
from typing import Any, Callable, Mapping

from hhs_runtime.pass219.discrete_hopf_projection import (
    classify_coupled_generator_hopf,
    hopf_project_embedding,
)
from hhs_runtime.pass219.discrete_s7_embedding import build_discrete_s7_embedding
from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    CHANNELS,
    PRODUCT_RELATIONS,
    advance_gyroscope,
    build_gyroscope_state,
    expected_product_phase,
)
from hhs_runtime.pass219.gyroscope_admission_membrane import construct_admissible_reciprocal_path
from hhs_runtime.pass219.phase_clifford_intertwiner import (
    build_one_gyroscope_clifford_channel_actions,
    build_phase_transport_clifford_lift,
    classify_coupled_generator_clifford,
)
from hhs_runtime.pass219.reciprocal_route_optimizer import (
    SHORTEST_POLICY,
    _reverse_route_exact,
    build_and_select_reciprocal_route,
    build_coupled_route_edge,
    build_reciprocal_route_plan,
)

PASS = 219
ITERATION = "RML16_COLD_ROUTE_SUBSTAGE_BENCHMARK"
SCHEMA = "HHS_PASS219_RML16_COLD_ROUTE_SUBSTAGE_BENCHMARK_V1"
SIGNS = {"xy": 1, "yx": -1, "zw": 1, "wz": -1}
ROUTE_SHAPE = (("x", 1), ("y", -2), ("z", 17), ("w", -18))


def _percentile95(values: list[int]) -> int:
    ordered = sorted(values)
    rank = (95 * len(ordered) + 99) // 100
    return ordered[max(0, rank - 1)]


def _summary(values: list[int]) -> dict[str, int]:
    ordered = sorted(int(value) for value in values)
    if not ordered:
        raise ValueError("EMPTY_SUBSTAGE_SAMPLE_SET")
    return {
        "samples": len(ordered),
        "min_ns": ordered[0],
        "median_ns": ordered[len(ordered) // 2],
        "mean_floor_ns": sum(ordered) // len(ordered),
        "p95_ns": _percentile95(ordered),
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
    state = build_gyroscope_state(phases, SIGNS, state_id=f"rml16:cold:source:{index}")
    if state["admissible_product_geometry"] is not True:
        raise AssertionError("RML16_COLD_SOURCE_NOT_ADMISSIBLE")
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
            transition_id=f"rml16:cold:target:{index}:{generator}:{delta}",
        )["next_state"]
    if current["admissible_product_geometry"] is not True:
        raise AssertionError("RML16_COLD_TARGET_NOT_ADMISSIBLE")
    return current


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--states", type=int, default=8)
    args = parser.parse_args()
    if args.states < 4:
        raise SystemExit("RML16_COLD_ROUTE_REQUIRES_AT_LEAST_FOUR_STATES")

    # Warm only RML11's already-existing immutable matrix/action caches. The
    # benchmark is about a new route request in a warm process, not Python import
    # or first-ever Cl(0,8) construction latency.
    build_one_gyroscope_clifford_channel_actions()

    samples: dict[str, list[int]] = {
        "ADVANCE_GYROSCOPE": [],
        "S7_EMBEDDING": [],
        "S4_HOPF_PROJECTION_ONLY": [],
        "RML7_HOPF_CLASSIFIER": [],
        "RML11_CLIFFORD_LIFT": [],
        "RML11_CLIFFORD_CLASSIFIER": [],
        "RML12_COUPLED_EDGE": [],
        "RML5_REFERENCE_PATH": [],
        "RML12_SHORTEST_PLAN": [],
        "RML12_REVERSE_PROOF": [],
        "RML12_FULL_SHORTEST_PLUS_COMPLEMENTARY_BUNDLE": [],
    }
    semantic = {
        "states_admissible": True,
        "targets_reached": True,
        "hopf_inverse_restores": True,
        "clifford_targets_admissible": True,
        "edges_reversible": True,
        "plans_reversible": True,
        "bundles_select_exact_route": True,
    }

    source_hashes: list[str] = []
    for state_index in range(args.states):
        source = _source(state_index)
        target = _target(source, state_index)
        source_hashes.append(source["state_sha256"])

        for generator, delta in ROUTE_SHAPE:
            product = next(
                product
                for product, relation in PRODUCT_RELATIONS.items()
                if relation["generator"] == generator
            )
            steps = {channel: 0 for channel in CHANNELS}
            steps[generator] = delta
            steps[product] = delta
            tag = f"rml16:cold:{state_index}:{generator}:{delta}"

            transition, elapsed = _time(
                lambda source=source, steps=steps, tag=tag: advance_gyroscope(
                    source, steps, transition_id=f"{tag}:advance"
                )
            )
            samples["ADVANCE_GYROSCOPE"].append(elapsed)
            if transition["next_state"]["admissible_product_geometry"] is not True:
                semantic["targets_reached"] = False

            embedding, elapsed = _time(lambda source=source: build_discrete_s7_embedding(source))
            samples["S7_EMBEDDING"].append(elapsed)
            hopf_point, elapsed = _time(lambda embedding=embedding: hopf_project_embedding(embedding))
            samples["S4_HOPF_PROJECTION_ONLY"].append(elapsed)
            if hopf_point["exact_unit_s4_identity_verified"] is not True:
                semantic["hopf_inverse_restores"] = False

            hopf, elapsed = _time(
                lambda source=source, generator=generator, delta=delta, tag=tag: classify_coupled_generator_hopf(
                    source,
                    generator=generator,
                    signed_steps=delta,
                    transition_id=f"{tag}:hopf",
                )
            )
            samples["RML7_HOPF_CLASSIFIER"].append(elapsed)
            if hopf["explicit_inverse_restores_exact_hopf_base"] is not True:
                semantic["hopf_inverse_restores"] = False

            lift, elapsed = _time(
                lambda source=source, steps=steps, tag=tag: build_phase_transport_clifford_lift(
                    source, steps, transport_id=f"{tag}:lift"
                )
            )
            samples["RML11_CLIFFORD_LIFT"].append(elapsed)
            if lift["ordered_reverse_factor_inverse_verified"] is not True:
                semantic["clifford_targets_admissible"] = False

            clifford, elapsed = _time(
                lambda source=source, generator=generator, delta=delta, tag=tag: classify_coupled_generator_clifford(
                    source,
                    generator=generator,
                    signed_steps=delta,
                    transition_id=f"{tag}:clifford",
                )
            )
            samples["RML11_CLIFFORD_CLASSIFIER"].append(elapsed)
            if clifford["target_product_geometry_admissible"] is not True:
                semantic["clifford_targets_admissible"] = False

            edge_result, elapsed = _time(
                lambda source=source, generator=generator, delta=delta, tag=tag: build_coupled_route_edge(
                    source,
                    generator=generator,
                    signed_steps=delta,
                    edge_id=f"{tag}:edge",
                )
            )
            samples["RML12_COUPLED_EDGE"].append(elapsed)
            if edge_result[0]["exact_inverse_restores_source_phase_state"] is not True:
                semantic["edges_reversible"] = False

        reference, elapsed = _time(
            lambda source=source, target=target, state_index=state_index: construct_admissible_reciprocal_path(
                source,
                target,
                path_id=f"rml16:cold:{state_index}:reference",
            )
        )
        samples["RML5_REFERENCE_PATH"].append(elapsed)
        if reference["target_reached_exactly"] is not True:
            semantic["targets_reached"] = False

        shortest, elapsed = _time(
            lambda source=source, target=target, state_index=state_index: build_reciprocal_route_plan(
                source,
                target,
                route_id=f"rml16:cold:{state_index}:shortest-plan",
                delta_policy=SHORTEST_POLICY,
            )
        )
        samples["RML12_SHORTEST_PLAN"].append(elapsed)
        if shortest["reverse_edge_sequence_restores_source_exactly"] is not True:
            semantic["plans_reversible"] = False

        reverse_ok, elapsed = _time(
            lambda target=target, shortest=shortest, source=source, state_index=state_index: _reverse_route_exact(
                target,
                shortest["edges"],
                source,
                route_id=f"rml16:cold:{state_index}:reverse-only",
            )
        )
        samples["RML12_REVERSE_PROOF"].append(elapsed)
        if reverse_ok is not True:
            semantic["plans_reversible"] = False

        bundle, elapsed = _time(
            lambda source=source, target=target, state_index=state_index: build_and_select_reciprocal_route(
                source,
                target,
                route_id=f"rml16:cold:{state_index}:bundle",
            )
        )
        samples["RML12_FULL_SHORTEST_PLUS_COMPLEMENTARY_BUNDLE"].append(elapsed)
        if bundle["selection"]["selected_route_sha256"] not in {
            bundle["shortest_candidate"]["route_sha256"],
            bundle["complementary_candidate"]["route_sha256"],
        }:
            semantic["bundles_select_exact_route"] = False

    if len(set(source_hashes)) != args.states:
        raise AssertionError("RML16_COLD_SOURCE_IDENTITIES_NOT_UNIQUE")
    if not all(semantic.values()):
        raise AssertionError(f"RML16_COLD_ROUTE_SEMANTIC_GATE_FAILED:{semantic}")

    summaries = {name: _summary(values) for name, values in samples.items()}
    ranking = sorted(
        (
            {"surface": name, "median_ns": row["median_ns"], "samples": row["samples"]}
            for name, row in summaries.items()
        ),
        key=lambda row: (-row["median_ns"], row["surface"]),
    )
    edge_median = summaries["RML12_COUPLED_EDGE"]["median_ns"]
    diagnostics = {
        "clifford_classifier_vs_edge_basis_points_floor": summaries["RML11_CLIFFORD_CLASSIFIER"]["median_ns"] * 10000 // max(1, edge_median),
        "clifford_lift_vs_edge_basis_points_floor": summaries["RML11_CLIFFORD_LIFT"]["median_ns"] * 10000 // max(1, edge_median),
        "hopf_classifier_vs_edge_basis_points_floor": summaries["RML7_HOPF_CLASSIFIER"]["median_ns"] * 10000 // max(1, edge_median),
        "advance_vs_edge_basis_points_floor": summaries["ADVANCE_GYROSCOPE"]["median_ns"] * 10000 // max(1, edge_median),
        "repeated_route_shape_count": len(ROUTE_SHAPE),
        "unique_source_state_count": args.states,
        "exact_request_route_cache_hits_possible_by_design": False,
    }

    payload = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "state_count": args.states,
        "route_shape": [[generator, delta] for generator, delta in ROUTE_SHAPE],
        "all_source_state_hashes_unique": True,
        "substage_timing": summaries,
        "ranking": ranking,
        "diagnostics": diagnostics,
        "semantic_gates": semantic,
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
    print(json.dumps({"schema": SCHEMA, "result": "PASS", "ranking": ranking, "diagnostics": diagnostics}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

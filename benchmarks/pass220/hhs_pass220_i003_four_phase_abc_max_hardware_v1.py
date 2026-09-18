#!/usr/bin/env python3
"""Pass 220 I003 post-calibration query-comparison harness.

This module is NOT the max-hardware calibration authority.  I003.1 moved that
measurement to the cold x86_64 raw-byte Bash workload before any HHS/runtime
build or service execution.

A = I002 holographic compositional ranking
B = inherited Pass 219 Lane 5 three-Hash72-segment ranking
C = exact cyclic Hash216-symbol comparison

All three arms receive the same deterministic query/candidate identities.
Timing is observational and post-calibration only.
"""
from __future__ import annotations

import json
import os
import time
from fractions import Fraction
from hashlib import sha256
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass219_lane5_hash216_gpu_phase_interlace_1_37 import (
    Hash216CompositionCandidate,
    Pass219Lane5Hash216GPUPhaseInterlaceOptimizer,
)
from hhs_runtime.hhs_pass220_holographic_hash216_query_v1 import (
    DEFAULT_PRIMES,
    HASH72_ALPHABET,
    compose_hash216,
    prime_modular_fingerprint,
    rank_and_sample_candidates,
)

SCHEMA = "HHS_PASS_220_I003_POST_CALIBRATION_QUERY_COMPARISON_V1"
PHASES = (("xy", 0, 36), ("yx", 36, 0), ("zw", 18, 54), ("wz", 54, 18))
ARMS = ("A", "B", "C")
BASE_COUNTS = (8, 16, 32, 64, 128, 256, 512, 1024, 2048)
ORDER_ROTATION = (("A", "B", "C"), ("B", "C", "A"), ("C", "A", "B"))
HASH72_INDEX = {symbol: index for index, symbol in enumerate(HASH72_ALPHABET)}

DEFAULT_LEG_BUDGET_NS = 15_000_000
DEFAULT_GLOBAL_BUDGET_NS = 1_800_000_000
DEFAULT_MAX_CANDIDATES = 8192
DEFAULT_REPEATS = 3


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if not value:
        return default
    parsed = int(value)
    return parsed if parsed > 0 else default


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: Any) -> str:
    return sha256(_canonical(value)).hexdigest()


def _word(seed: int) -> str:
    return "".join(HASH72_ALPHABET[(seed + index) % 72] for index in range(72))


def _hash216(seed: int) -> str:
    return compose_hash216(_word(seed), _word(seed + 1), _word(seed + 2))


def _phase_signature(phase_slot: int, exact: bool = True) -> tuple[tuple[str, int], ...]:
    base = (("yx", -1), ("x+y", 0), ("xy", 1), ("wz", -1), ("z+w", 0), ("zw", 1))
    if exact:
        return base + (("phase", phase_slot),)
    return base[:-1] + (("zw", 0), ("phase", phase_slot))


def build_dataset(phase: str, phase_slot: int, inverse_phase_slot: int, candidate_count: int) -> dict[str, Any]:
    seed = phase_slot + candidate_count * 17 + inverse_phase_slot * 31
    query_hash216 = _hash216(seed)
    query_scalar = seed * 5184 + candidate_count
    perspective_roots = tuple(_digest({"phase": phase, "view": index, "query": query_hash216}) for index in range(4))
    fibonacci_states = ((1, 1), (2, 1), (3, 1), (5, 1), (8, 1), (13, 1), (21, 1), (34, 1), (55, 1))
    query = {
        "hash216": query_hash216,
        "prime_fingerprint": prime_modular_fingerprint(query_scalar, DEFAULT_PRIMES),
        "fibonacci_square_states": fibonacci_states,
        "phase_signature": _phase_signature(phase_slot, True),
        "perspective_roots": perspective_roots,
    }
    candidates = []
    for ordinal in range(candidate_count):
        exact = ordinal == 0
        scalar = query_scalar if exact else query_scalar + ordinal * 97 + 1
        roots = perspective_roots if exact else perspective_roots[: (ordinal % len(perspective_roots)) + 1]
        candidates.append({
            "candidate_id": f"{phase}:{candidate_count}:{ordinal}",
            "hash216": query_hash216 if exact else _hash216(seed + ordinal + 1),
            "prime_fingerprint": prime_modular_fingerprint(scalar, DEFAULT_PRIMES),
            "fibonacci_square_states": fibonacci_states if ordinal % 3 else fibonacci_states[:-1] + ((56, 1),),
            "phase_signature": _phase_signature(phase_slot, exact or ordinal % 5 == 0),
            "perspective_roots": roots,
            "jump_span": 1 + (ordinal % 8),
            "lineage_signature": _digest({"phase": phase, "ordinal": ordinal, "hash216": query_hash216}),
        })
    identity = {
        "phase": phase,
        "phase_slot": phase_slot,
        "inverse_phase_slot": inverse_phase_slot,
        "candidate_count": candidate_count,
        "query_hash216": query_hash216,
        "candidate_ids": tuple(item["candidate_id"] for item in candidates),
        "candidate_hash216": tuple(item["hash216"] for item in candidates),
        "candidate_metadata_roots": tuple(_digest(item) for item in candidates),
    }
    return {"query": query, "candidates": candidates, "dataset_digest": _digest(identity)}


def cyclic_hash216_distance(query: str, candidate: str) -> int:
    if len(query) != 216 or len(candidate) != 216:
        raise ValueError("raw Hash216 distance requires 216 symbols")
    total = 0
    for left, right in zip(query, candidate):
        a = HASH72_INDEX[left]
        b = HASH72_INDEX[right]
        delta = abs(a - b)
        total += min(delta, 72 - delta)
    return total


def raw_rank(query_hash216: str, candidates: Sequence[Mapping[str, Any]], top_k: int) -> dict[str, Any]:
    ranked = [
        {
            "candidate_id": item["candidate_id"],
            "hash216": item["hash216"],
            "distance": cyclic_hash216_distance(query_hash216, item["hash216"]),
            "source_ordinal": ordinal,
        }
        for ordinal, item in enumerate(candidates)
    ]
    ranked.sort(key=lambda item: (item["distance"], item["hash216"], item["candidate_id"], item["source_ordinal"]))
    return {"ranked": ranked[: min(top_k, len(ranked))], "candidate_count": len(ranked)}


def _lane5_candidates(candidates: Sequence[Mapping[str, Any]]) -> list[Hash216CompositionCandidate]:
    return [
        Hash216CompositionCandidate(
            candidate_id=str(item["candidate_id"]),
            hash216=str(item["hash216"]),
            validated=True,
            jump_span=int(item.get("jump_span", 1)),
            lineage_signature=str(item.get("lineage_signature", item["hash216"])),
        )
        for item in candidates
    ]


def _time_call(fn, *, budget_ns: int, repeats: int) -> tuple[int, int, Any]:
    started = time.perf_counter_ns()
    completed = 0
    last = None
    for _ in range(repeats):
        if time.perf_counter_ns() - started >= budget_ns:
            break
        last = fn()
        completed += 1
    elapsed = time.perf_counter_ns() - started
    return elapsed, completed, last


def _arm_a(dataset: Mapping[str, Any], repeats: int, budget_ns: int, sample_seed: int) -> dict[str, Any]:
    query = dataset["query"]
    candidates = dataset["candidates"]
    elapsed, completed, last = _time_call(
        lambda: rank_and_sample_candidates(query, candidates, sample_ordinal=sample_seed),
        budget_ns=budget_ns,
        repeats=repeats,
    )
    return {"elapsed_ns": elapsed, "completed": completed, "result": last}


def _arm_b(
    optimizer: Pass219Lane5Hash216GPUPhaseInterlaceOptimizer,
    dataset: Mapping[str, Any],
    repeats: int,
    budget_ns: int,
    *,
    tick: int,
    cycle_index: int,
) -> dict[str, Any]:
    query = dataset["query"]
    candidates = _lane5_candidates(dataset["candidates"])
    elapsed, completed, last = _time_call(
        lambda: optimizer.search_hash216(
            query_hash216=str(query["hash216"]),
            candidates=candidates,
            tick=tick,
            cycle_index=cycle_index,
            top_k=len(candidates),
        ),
        budget_ns=budget_ns,
        repeats=repeats,
    )
    return {"elapsed_ns": elapsed, "completed": completed, "result": last}


def _arm_c(dataset: Mapping[str, Any], repeats: int, budget_ns: int) -> dict[str, Any]:
    query = dataset["query"]
    candidates = dataset["candidates"]
    elapsed, completed, last = _time_call(
        lambda: raw_rank(str(query["hash216"]), candidates, len(candidates)),
        budget_ns=budget_ns,
        repeats=repeats,
    )
    return {"elapsed_ns": elapsed, "completed": completed, "result": last}


def _counts(max_candidates: int) -> tuple[int, ...]:
    values = list(BASE_COUNTS)
    current = values[-1] * 2
    while current <= max_candidates:
        values.append(current)
        current *= 2
    return tuple(values)


def run(
    *,
    optimizer: Pass219Lane5Hash216GPUPhaseInterlaceOptimizer | None = None,
    leg_budget_ns: int | None = None,
    global_budget_ns: int | None = None,
    max_candidates: int | None = None,
    repeats: int | None = None,
) -> dict[str, Any]:
    leg_budget = leg_budget_ns or _env_int("HHS_PASS220_I003_LEG_BUDGET_NS", DEFAULT_LEG_BUDGET_NS)
    global_budget = global_budget_ns or _env_int("HHS_PASS220_I003_GLOBAL_BUDGET_NS", DEFAULT_GLOBAL_BUDGET_NS)
    max_n = max_candidates or _env_int("HHS_PASS220_I003_MAX_CANDIDATES", DEFAULT_MAX_CANDIDATES)
    repeat_count = repeats or _env_int("HHS_PASS220_I003_REPEATS", DEFAULT_REPEATS)
    own_optimizer = optimizer is None
    lane5 = optimizer or Pass219Lane5Hash216GPUPhaseInterlaceOptimizer(backend="CPU_REFERENCE")
    started_global = time.perf_counter_ns()
    samples = []
    phase_max = {}
    try:
        for phase_index, (phase, phase_slot, inverse_phase_slot) in enumerate(PHASES):
            max_closed = 0
            for rank_index, count in enumerate(_counts(max_n), start=1):
                if time.perf_counter_ns() - started_global >= global_budget:
                    break
                dataset = build_dataset(phase, phase_slot, inverse_phase_slot, count)
                order = ORDER_ROTATION[(rank_index - 1) % len(ORDER_ROTATION)]
                arm_results: dict[str, Any] = {}
                for arm in order:
                    if arm == "A":
                        result = _arm_a(dataset, repeat_count, leg_budget, phase_index * 1000 + rank_index)
                    elif arm == "B":
                        result = _arm_b(
                            lane5,
                            dataset,
                            repeat_count,
                            leg_budget,
                            tick=phase_slot + rank_index,
                            cycle_index=rank_index,
                        )
                    else:
                        result = _arm_c(dataset, repeat_count, leg_budget)
                    result["dataset_digest"] = dataset["dataset_digest"]
                    result["complete"] = result["completed"] == repeat_count and result["elapsed_ns"] <= leg_budget
                    arm_results[arm] = result
                same_dataset = len({arm_results[arm]["dataset_digest"] for arm in ARMS}) == 1
                all_complete = same_dataset and all(arm_results[arm]["complete"] for arm in ARMS)
                if all_complete:
                    max_closed = count
                samples.append({
                    "phase": phase,
                    "phase_slot": phase_slot,
                    "inverse_phase_slot": inverse_phase_slot,
                    "rank_index": rank_index,
                    "candidate_count": count,
                    "order": order,
                    "dataset_digest": dataset["dataset_digest"],
                    "same_dataset_verified": same_dataset,
                    "all_arms_complete": all_complete,
                    "arms": {
                        arm: {
                            "elapsed_ns": arm_results[arm]["elapsed_ns"],
                            "completed": arm_results[arm]["completed"],
                            "complete": arm_results[arm]["complete"],
                        }
                        for arm in ARMS
                    },
                })
                if not all_complete:
                    break
            phase_max[phase] = max_closed
    finally:
        if own_optimizer:
            lane5.close()
    elapsed_global = time.perf_counter_ns() - started_global
    return {
        "schema": SCHEMA,
        "hardware_calibration_authority": False,
        "post_calibration_integration_only": True,
        "cold_raw_byte_calibration_required_for_hardware_claim": True,
        "phases": [phase for phase, _, _ in PHASES],
        "arm_definitions": {
            "A": "I002_HOLOGRAPHIC_COMPOSITION_RANKING",
            "B": "PASS219_1_37_THREE_HASH72_SEGMENT_LANE5_RANKING",
            "C": "RAW_EXACT_CYCLIC_HASH216_SYMBOL_DISTANCE",
        },
        "order_rotation": ["ABC", "BCA", "CAB"],
        "leg_budget_ns": leg_budget,
        "global_budget_ns": global_budget,
        "max_candidates_requested": max_n,
        "repeats": repeat_count,
        "samples": samples,
        "phase_max_hardware_closed_n": phase_max,
        "global_max_hardware_closed_n": min(phase_max.values()) if phase_max else 0,
        "elapsed_global_ns": elapsed_global,
        "within_global_time_bound": elapsed_global <= global_budget,
        "same_dataset_required": True,
        "timing_observational_only": True,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "result": "PASS" if samples and all(sample["same_dataset_verified"] for sample in samples) else "FAIL",
    }


def main() -> int:
    result = run()
    print(json.dumps(result, sort_keys=True))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

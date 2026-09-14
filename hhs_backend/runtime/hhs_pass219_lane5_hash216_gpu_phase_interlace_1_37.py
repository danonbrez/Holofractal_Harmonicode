"""Lane 5 Hash216 GPU/vector-store phase-interlace optimizer, Pass 219 1.37.

The optimizer is candidate-only. It searches validated Hash216 records as three
ordered Hash72 vectors, shards/ranks work through the exact 20,020-slot Lane 5
phase fabric, and delegates candidate execution to the inherited Pass 207 GPU
runtime. Canonical VM81/Hash72/Hash216 mutation remains outside this module.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass207_vm81_gpu_runtime_v1 import (
    HASH72_ALPHABET,
    Pass207VM81GPURuntime,
)
from hhs_python.runtime.hhs_pass205_continuation_bridge import (
    CELL_COUNT,
    Pass205NativeBridge,
)
from hhs_python.runtime.hhs_pass219_lane5_phase_interlace_bridge import (
    CYCLE,
    Pass219Lane5PhaseInterlaceBridge,
)

SCHEMA = "HHS_PASS_219_LANE5_HASH216_GPU_PHASE_INTERLACE_OPTIMIZER_1_37"
HASH72_LEN = 72
HASH216_LEN = 216

# Consecutive primes strictly after the four fixed phase-cycle prime factors.
PRIME_CELLS = (
    17, 19, 23, 29, 31, 37, 41, 43, 47, 53,
    59, 61, 67, 71, 73, 79, 83, 89, 97, 101,
    103, 107, 109, 113,
)


@dataclass(frozen=True)
class Hash216CompositionCandidate:
    candidate_id: str
    hash216: str
    validated: bool
    jump_span: int = 1
    lineage_signature: str = ""


def _validate_hash216(value: str) -> str:
    if not isinstance(value, str) or len(value) != HASH216_LEN:
        raise ValueError("Hash216 value must contain exactly 216 symbols")
    alphabet = set(HASH72_ALPHABET)
    bad = next((symbol for symbol in value if symbol not in alphabet), None)
    if bad is not None:
        raise ValueError(f"invalid Hash216 symbol: {bad!r}")
    return value


def split_hash216(value: str) -> tuple[str, str, str]:
    canonical = _validate_hash216(value)
    return (
        canonical[:HASH72_LEN],
        canonical[HASH72_LEN : 2 * HASH72_LEN],
        canonical[2 * HASH72_LEN :],
    )


def _fingerprint(query_hash216: str, cycle_index: int) -> bytes:
    if int(cycle_index) < 0:
        raise ValueError("cycle_index must be nonnegative")
    digest = hashlib.sha256()
    digest.update(b"HHS-P219-LANE5-1.37\0")
    digest.update(_validate_hash216(query_hash216).encode("ascii"))
    digest.update(int(cycle_index).to_bytes(8, "little", signed=False))
    return digest.digest()


def derive_prime_matrix(query_hash216: str, cycle_index: int) -> tuple[list[list[int]], list[int]]:
    """Derive an upper-triangular consecutive-prime routing fingerprint."""
    digest = _fingerprint(query_hash216, cycle_index)
    window = 10
    start = int.from_bytes(digest[:4], "little") % (len(PRIME_CELLS) - window + 1)
    selected = PRIME_CELLS[start : start + window]
    matrix = [[0 for _ in range(4)] for _ in range(4)]
    ordinal = 0
    for row in range(4):
        for column in range(row, 4):
            matrix[row][column] = selected[ordinal]
            ordinal += 1
    offsets = [
        int.from_bytes(digest[4 + index * 4 : 8 + index * 4], "little") % CYCLE
        for index in range(4)
    ]
    return matrix, offsets


class Pass219Lane5Hash216GPUPhaseInterlaceOptimizer:
    """Read-only Hash216 search optimizer over the exact Lane 5 phase fabric."""

    def __init__(
        self,
        *,
        backend: str = "CPU_REFERENCE",
        require_physical_gpu: bool = False,
    ) -> None:
        self.phase = Pass219Lane5PhaseInterlaceBridge()
        self.native = Pass205NativeBridge()
        self.gpu = Pass207VM81GPURuntime(
            backend=backend,
            require_physical_gpu=require_physical_gpu,
        )

    def close(self) -> None:
        self.gpu.close()

    def __enter__(self) -> "Pass219Lane5Hash216GPUPhaseInterlaceOptimizer":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def status(self) -> dict[str, Any]:
        authority = self.phase.authority()
        return {
            "schema": SCHEMA,
            "phase_interlace": authority,
            "gpu": self.gpu.status(),
            "full_cycle": CYCLE,
            "validated_hash216_read_only": True,
            "hash216_search_lanes": 3,
            "four_lane_phase_interlace": True,
            "candidate_only": True,
            "gpu_may_commit_hash72": False,
            "gpu_may_commit_hash216": False,
            "canonical_vm81_mutation_authority": False,
            "requires_exact_cpu_vm81_replay": True,
        }

    def native_state_hash216(self, words: Sequence[int]) -> str:
        if len(words) != CELL_COUNT:
            raise ValueError(f"native state requires exactly {CELL_COUNT} uint64 words")
        return _validate_hash216(self.native.state_root(words))

    def search_hash216(
        self,
        *,
        query_hash216: str,
        candidates: Sequence[Hash216CompositionCandidate],
        tick: int,
        cycle_index: int,
        top_k: int = 32,
    ) -> dict[str, Any]:
        if int(tick) < 0:
            raise ValueError("tick must be nonnegative")
        query = _validate_hash216(query_hash216)
        if not candidates:
            return {
                "schema": SCHEMA,
                "query_hash216": query,
                "candidate_count": 0,
                "ranked": [],
                "candidate_only": True,
            }

        ids: set[str] = set()
        hashes: set[str] = set()
        canonical: list[Hash216CompositionCandidate] = []
        for candidate in candidates:
            if not candidate.validated:
                raise ValueError(f"unvalidated Hash216 candidate: {candidate.candidate_id}")
            if not candidate.candidate_id or candidate.candidate_id in ids:
                raise ValueError("candidate IDs must be nonempty and unique")
            if int(candidate.jump_span) <= 0:
                raise ValueError("jump_span must be positive")
            value = _validate_hash216(candidate.hash216)
            if value in hashes:
                raise ValueError("duplicate Hash216 candidate")
            ids.add(candidate.candidate_id)
            hashes.add(value)
            canonical.append(candidate)

        matrix, offsets = derive_prime_matrix(query, cycle_index)
        route = self.phase.prime_route(tick, matrix, offsets)
        phase_address = self.phase.phase_address(tick)
        query_segments = split_hash216(query)
        candidate_segments = [split_hash216(candidate.hash216) for candidate in canonical]

        distances = [0 for _ in canonical]
        segment_rankings: list[dict[str, Any]] = []
        candidate_ids = [candidate.candidate_id for candidate in canonical]
        for segment_index in range(3):
            ranking = self.gpu.rank_hash72_vectors(
                query_hash72=query_segments[segment_index],
                candidate_hash72=[segments[segment_index] for segments in candidate_segments],
                candidate_ids=candidate_ids,
                top_k=len(canonical),
            )
            segment_rankings.append(ranking)
            for item in ranking["ranked"]:
                distances[int(item["source_ordinal"])] += int(item["distance"])

        ranked = []
        routed_slots = [int(value) for value in route["routed_slot"]]
        for ordinal, candidate in enumerate(canonical):
            stream = ordinal % 4
            ranked.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "candidate_hash216": candidate.hash216,
                    "hash216_distance": int(distances[ordinal]),
                    "jump_span": int(candidate.jump_span),
                    "lineage_signature": candidate.lineage_signature,
                    "source_ordinal": ordinal,
                    "phase_stream": stream,
                    "routed_slot": routed_slots[stream],
                }
            )
        ranked.sort(
            key=lambda item: (
                item["hash216_distance"],
                -item["jump_span"],
                item["routed_slot"],
                item["candidate_hash216"],
                item["candidate_id"],
                item["source_ordinal"],
            )
        )
        bounded = max(0, min(int(top_k), len(ranked)))
        return {
            "schema": SCHEMA,
            "query_hash216": query,
            "candidate_count": len(canonical),
            "top_k": bounded,
            "cycle_index": int(cycle_index),
            "tick": int(tick),
            "phase_address": phase_address,
            "prime_matrix": matrix,
            "prime_offsets": offsets,
            "prime_route": route,
            "hash216_segment_rankings": segment_rankings,
            "ranked": ranked[:bounded],
            "candidate_only": True,
            "validated_hash216_read_only": True,
            "gpu_may_commit_hash72": False,
            "gpu_may_commit_hash216": False,
            "canonical_vm81_mutation_authority": False,
            "requires_exact_cpu_vm81_replay": True,
        }

    def search_native_states(
        self,
        *,
        query_state: Sequence[int],
        candidate_states: Sequence[tuple[str, Sequence[int], int]],
        tick: int,
        cycle_index: int,
        top_k: int = 32,
    ) -> dict[str, Any]:
        query_hash216 = self.native_state_hash216(query_state)
        candidates = [
            Hash216CompositionCandidate(
                candidate_id=candidate_id,
                hash216=self.native_state_hash216(words),
                validated=True,
                jump_span=int(jump_span),
                lineage_signature=self.native_state_hash216(words),
            )
            for candidate_id, words, jump_span in candidate_states
        ]
        return self.search_hash216(
            query_hash216=query_hash216,
            candidates=candidates,
            tick=tick,
            cycle_index=cycle_index,
            top_k=top_k,
        )

    def verify_candidate_batch(
        self,
        *,
        states: Sequence[Sequence[int]],
        projections: Sequence[Sequence[Sequence[int]]],
        deltas: Sequence[Sequence[Mapping[str, int]]],
    ) -> dict[str, Any]:
        result = self.gpu.execute(states=states, projections=projections, deltas=deltas)
        if not result.get("verified_against_cpu"):
            raise RuntimeError("candidate batch did not close against exact Pass 205 CPU replay")
        if result.get("gpu_may_commit_hash72"):
            raise RuntimeError("GPU candidate path exposed Hash72 commit authority")
        if not result.get("vm81_single_admission_authority"):
            raise RuntimeError("VM81 singleton admission authority was not preserved")
        return result


__all__ = [
    "Hash216CompositionCandidate",
    "Pass219Lane5Hash216GPUPhaseInterlaceOptimizer",
    "derive_prime_matrix",
    "split_hash216",
]

from __future__ import annotations

import pytest

from hhs_backend.runtime.hhs_pass205_accelerator_translation_v1 import (
    Pass205AcceleratorTranslation,
)
from hhs_backend.runtime.hhs_pass219_lane5_hash216_gpu_phase_interlace_1_37 import (
    Hash216CompositionCandidate,
    Pass219Lane5Hash216GPUPhaseInterlaceOptimizer,
    derive_prime_matrix,
)
from hhs_python.runtime.hhs_pass219_lane5_phase_interlace_bridge import (
    Pass219Lane5PhaseInterlaceBridge,
)


def _state(seed: int) -> list[int]:
    mask = (1 << 64) - 1
    return [
        ((seed + 1) * 0x9E3779B97F4A7C15 + cell * 0x517CC1B727220A95) & mask
        for cell in range(81)
    ]


def test_lane5_phase_interlace_native_cycle_and_negative_routes() -> None:
    bridge = Pass219Lane5PhaseInterlaceBridge()
    authority = bridge.authority()
    assert bridge.version() == 0x00010025
    assert authority["full_cycle"] == 20_020
    assert authority["quarter_cycle"] == 5_005
    assert authority["base_periods"] == [5, 7, 11, 13]
    assert authority["validated_hash216_read_only"] == 1
    assert authority["pass207_gpu_vector_search_bound"] == 1
    assert authority["canonical_vm81_mutation_authority"] == 0
    assert authority["canonical_hash72_authority"] == 0
    assert authority["canonical_hash216_authority"] == 0

    expected = [
        [0, 0, 0, 0],
        [1, 3, 3, 1],
        [2, 2, 2, 2],
        [3, 1, 1, 3],
    ]
    for quarter, phases in enumerate(expected):
        address = bridge.phase_address(quarter * 5_005)
        assert address["quarter_index"] == quarter
        assert address["phases"] == phases
    assert bridge.phase_address(20_020)["phases"] == [0, 0, 0, 0]

    seen = set()
    for tick in range(20_020):
        address = bridge.phase_address(tick)
        key = tuple(address["residues"] + address["phases"])
        assert key not in seen
        seen.add(key)
    assert len(seen) == 20_020

    query = "0" * 216
    matrix, offsets = derive_prime_matrix(query, 3)
    route = bridge.prime_route(1_234, matrix, offsets)
    assert route["prime_cells_validated"] is True
    assert route["upper_triangular"] is True
    assert route["invertible_mod_cycle"] is True
    assert route["candidate_only"] is True
    assert route["canonical_mutation_authority"] is False
    assert route["requires_exact_cpu_vm81_replay"] is True

    bad = [row[:] for row in matrix]
    bad[0][0] = 5
    with pytest.raises(ValueError, match="prime route rejected"):
        bridge.prime_route(1_234, bad, offsets)


def test_lane5_hash216_gpu_search_uses_native_hashes_and_is_candidate_only() -> None:
    states = [_state(11), _state(29), _state(47), _state(71)]
    with Pass219Lane5Hash216GPUPhaseInterlaceOptimizer(backend="CPU_REFERENCE") as optimizer:
        hashes = [optimizer.native_state_hash216(state) for state in states]
        assert all(len(value) == 216 for value in hashes)
        assert len(set(hashes)) == len(hashes)

        candidates = [
            Hash216CompositionCandidate("exact", hashes[0], True, jump_span=1, lineage_signature="l0"),
            Hash216CompositionCandidate("jump-8", hashes[1], True, jump_span=8, lineage_signature="l1"),
            Hash216CompositionCandidate("jump-32", hashes[2], True, jump_span=32, lineage_signature="l2"),
            Hash216CompositionCandidate("jump-64", hashes[3], True, jump_span=64, lineage_signature="l3"),
        ]
        first = optimizer.search_hash216(
            query_hash216=hashes[0],
            candidates=candidates,
            tick=1_234,
            cycle_index=7,
            top_k=4,
        )
        second = optimizer.search_hash216(
            query_hash216=hashes[0],
            candidates=candidates,
            tick=1_234,
            cycle_index=7,
            top_k=4,
        )
        assert first["ranked"] == second["ranked"]
        assert first["ranked"][0]["candidate_id"] == "exact"
        assert first["ranked"][0]["hash216_distance"] == 0
        assert first["candidate_only"] is True
        assert first["validated_hash216_read_only"] is True
        assert first["gpu_may_commit_hash72"] is False
        assert first["gpu_may_commit_hash216"] is False
        assert first["canonical_vm81_mutation_authority"] is False
        assert first["requires_exact_cpu_vm81_replay"] is True
        assert len(first["hash216_segment_rankings"]) == 3

        with pytest.raises(ValueError, match="unvalidated"):
            optimizer.search_hash216(
                query_hash216=hashes[0],
                candidates=[Hash216CompositionCandidate("bad", hashes[1], False)],
                tick=0,
                cycle_index=0,
            )
        with pytest.raises(ValueError, match="duplicate Hash216"):
            optimizer.search_hash216(
                query_hash216=hashes[0],
                candidates=[
                    Hash216CompositionCandidate("a", hashes[1], True),
                    Hash216CompositionCandidate("b", hashes[1], True),
                ],
                tick=0,
                cycle_index=0,
            )
        with pytest.raises(ValueError, match="216 symbols"):
            optimizer.search_hash216(
                query_hash216="short",
                candidates=candidates,
                tick=0,
                cycle_index=0,
            )


def test_lane5_candidate_execution_still_requires_pass207_cpu_equality() -> None:
    translation = Pass205AcceleratorTranslation()
    states = [_state(101), _state(211)]
    projections = [translation.native.project_full(state) for state in states]
    deltas = [
        [
            {"cell": 0, "control_g": 7, "xor_mask": (1 << 0) | (1 << 63)},
            {"cell": 40, "control_g": 72, "xor_mask": (1 << 5) | (1 << 17)},
        ],
        [
            {"cell": 80, "control_g": 242, "xor_mask": (1 << 1) | (1 << 62)},
            {"cell": 8, "control_g": 3, "xor_mask": (1 << 9)},
        ],
    ]
    with Pass219Lane5Hash216GPUPhaseInterlaceOptimizer(backend="CPU_REFERENCE") as optimizer:
        result = optimizer.verify_candidate_batch(
            states=states,
            projections=projections,
            deltas=deltas,
        )
        assert result["verified_against_cpu"] is True
        assert result["gpu_may_commit_hash72"] is False
        assert result["vm81_single_admission_authority"] is True
        assert result["logical_lane_dispatches"] == 2 * 5_184

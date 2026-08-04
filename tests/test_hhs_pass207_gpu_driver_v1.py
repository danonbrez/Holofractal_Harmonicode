from __future__ import annotations

from hhs_backend.runtime.hhs_pass205_accelerator_translation_v1 import (
    Pass205AcceleratorTranslation,
)
from hhs_backend.runtime.hhs_pass207_vm81_gpu_runtime_v1 import (
    HASH72_ALPHABET,
    Pass207VM81GPURuntime,
)
from hhs_python.runtime.hhs_pass207_gpu_driver_bridge import (
    LOGICAL_LANES,
    Pass207GPUDriver,
    build_native_library,
)


def _state(seed: int) -> list[int]:
    mask = (1 << 64) - 1
    return [
        ((seed + 1) * 0x9E3779B97F4A7C15 + cell * 0x517CC1B727220A95) & mask
        for cell in range(81)
    ]


def _hash72(offset: int) -> str:
    return "".join(HASH72_ALPHABET[(index + offset) % 72] for index in range(72))


def test_pass207_native_build_and_exhaustive_lane_bijection() -> None:
    assert build_native_library(force=True).exists()
    seen: set[int] = set()
    for lane in range(LOGICAL_LANES):
        cell, hyperthread = Pass207GPUDriver.lane_decode(lane)
        assert Pass207GPUDriver.lane_address(cell, hyperthread) == lane
        phase_row, phase_column = Pass207GPUDriver.lane_phase_coordinate(lane)
        assert phase_row * 72 + phase_column == lane
        seen.add(lane)
    assert len(seen) == 5184


def test_pass207_vm81_5184_lane_dispatch_cache_and_vector_ranking() -> None:
    translation = Pass205AcceleratorTranslation()
    states = [_state(11), _state(29)]
    projections = [translation.native.project_full(state) for state in states]
    deltas = [
        [
            {"cell": 0, "control_g": 7, "xor_mask": (1 << 0) | (1 << 31) | (1 << 63)},
            {"cell": 40, "control_g": 72, "xor_mask": (1 << 5) | (1 << 17)},
        ],
        [
            {"cell": 80, "control_g": 242, "xor_mask": (1 << 1) | (1 << 33) | (1 << 62)},
            {"cell": 8, "control_g": 3, "xor_mask": (1 << 9)},
        ],
    ]
    batch = translation.pack_batch(states=states, projections=projections, deltas=deltas)
    oracle = translation.execute_cpu_reference(batch)

    with Pass207VM81GPURuntime(backend="CPU_REFERENCE") as runtime:
        first = runtime.execute_batch(batch)
        second = runtime.execute_batch(batch)
        assert first["child_states"] == oracle["child_states"]
        assert first["child_projections"] == oracle["child_projections"]
        assert first["frontiers"] == oracle["frontiers"]
        assert first["logical_lane_dispatches"] == 2 * 5184
        assert first["verified_against_cpu"] is True
        assert first["gpu_may_commit_hash72"] is False
        assert second["driver"]["cache_input_hit"] is True
        assert second["driver"]["cache_hits"] >= 2
        assert second["driver"]["logical_hyperthreads_per_cell"] == 64
        assert second["driver"]["logical_lanes_per_batch"] == 5184
        assert second["driver"]["stable_lane_identity"] is True
        assert second["driver"]["disjoint_lane_writes"] is True
        assert second["driver"]["canonical_reduction_order"] is True

        query = _hash72(0)
        candidates = [_hash72(36), _hash72(1), _hash72(0), _hash72(1)]
        ids = ["opposite", "near-b", "exact", "near-a"]
        ranking_a = runtime.rank_hash72_vectors(
            query_hash72=query,
            candidate_hash72=candidates,
            candidate_ids=ids,
            top_k=4,
        )
        ranking_b = runtime.rank_hash72_vectors(
            query_hash72=query,
            candidate_hash72=candidates,
            candidate_ids=ids,
            top_k=4,
        )
        assert [item["candidate_id"] for item in ranking_a["ranked"]] == [
            "exact",
            "near-a",
            "near-b",
            "opposite",
        ]
        assert ranking_a["ranked"] == ranking_b["ranked"]
        assert runtime.status()["driver"]["vector_dispatch_count"] == 2

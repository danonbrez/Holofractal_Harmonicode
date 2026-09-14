from __future__ import annotations

from dataclasses import replace

import pytest

from hhs_backend.runtime.hhs_pass219_lane5_hash216_composition_jump_store_1_38 import (
    Pass219Lane5Hash216CompositionJumpStore,
)


def _state(seed: int) -> list[int]:
    mask = (1 << 64) - 1
    return [
        ((seed + 1) * 0x9E3779B97F4A7C15 + cell * 0x517CC1B727220A95) & mask
        for cell in range(81)
    ]


def _steps(count: int, salt: int) -> list[list[dict[str, int]]]:
    result = []
    for index in range(count):
        bit_a = (index * 7 + salt) % 64
        bit_b = (index * 13 + salt + 3) % 64
        mask = (1 << bit_a) | (1 << bit_b)
        result.append([
            {
                "cell": (index * 11 + salt) % 81,
                "control_g": (index * 17 + salt * 5) % 243,
                "xor_mask": mask,
            }
        ])
    return result


def test_lane5_validated_composition_jump_search_and_direct_reuse() -> None:
    parent = _state(38)
    with Pass219Lane5Hash216CompositionJumpStore(backend="CPU_REFERENCE") as store:
        short = store.build_validated_jump(
            jump_id="jump-8",
            parent_state=parent,
            steps=_steps(8, 3),
            tick=5005,
            cycle_index=11,
            layer_index=1,
        )
        long = store.build_validated_jump(
            jump_id="jump-16",
            parent_state=parent,
            steps=_steps(16, 7),
            tick=15015,
            cycle_index=11,
            layer_index=2,
        )
        store.insert(short)
        receipt = store.insert(long)
        assert receipt["accepted"] is True
        assert receipt["candidate_only"] is True
        assert receipt["canonical_mutation_authority"] is False
        assert store.verify_jump_replay(parent_state=parent, jump=short) is True
        assert store.verify_jump_replay(parent_state=parent, jump=long) is True

        ranked = store.search(
            current_state=parent,
            goal_hash216=long.child_hash216,
            tick=1234,
            cycle_index=12,
            top_k=2,
        )
        assert ranked["ranked"][0]["candidate_id"] == "jump-16"
        assert ranked["ranked"][0]["hash216_distance"] == 0
        assert ranked["composition_jump_store"] is True
        assert ranked["direct_candidate_reuse_allowed"] is True

        reused = store.reuse(current_state=parent, jump_id="jump-16")
        assert reused["child_state"] == list(long.child_state)
        assert reused["represented_transitions"] == 16
        assert reused["intermediate_transitions_executed_on_reuse"] == 0
        assert reused["candidate_only"] is True
        assert reused["canonical_vm81_mutation_authority"] is False
        assert reused["requires_signed_environmental_vm81_admission"] is True

        benchmark = store.benchmark_reuse(
            current_state=parent,
            jump_id="jump-16",
            repetitions=64,
        )
        assert benchmark["represented_transitions"] == 1024
        assert benchmark["intermediate_transitions_executed_on_reuse"] == 0
        assert benchmark["candidate_reuse_validations"] == 64


def test_lane5_composition_jump_tamper_and_parent_mismatch_fail_closed() -> None:
    parent = _state(91)
    with Pass219Lane5Hash216CompositionJumpStore(backend="CPU_REFERENCE") as store:
        jump = store.build_validated_jump(
            jump_id="sealed",
            parent_state=parent,
            steps=_steps(4, 9),
            tick=20019,
            cycle_index=4,
            layer_index=3,
        )
        tampered_words = list(jump.child_state)
        tampered_words[0] ^= 1
        tampered = replace(jump, child_state=tuple(tampered_words))
        with pytest.raises(ValueError, match="child state/root mismatch"):
            store.insert(tampered)

        store.insert(jump)
        wrong_parent = list(parent)
        wrong_parent[0] ^= 1
        with pytest.raises(ValueError, match="parent does not match"):
            store.reuse(current_state=wrong_parent, jump_id="sealed")

        tampered_seal = replace(jump, jump_id="bad-seal", composition_hash216=jump.child_hash216)
        with pytest.raises(ValueError, match="immutable Hash216 seal mismatch"):
            store.insert(tampered_seal)


def test_lane5_composition_status_preserves_authority_boundary() -> None:
    with Pass219Lane5Hash216CompositionJumpStore(backend="CPU_REFERENCE") as store:
        status = store.status()
        assert status["full_cycle"] == 20020
        assert status["validated_hash216_jump_store"] is True
        assert status["exact_registration_replay_required"] is True
        assert status["direct_candidate_reuse_allowed"] is True
        assert status["candidate_only"] is True
        assert status["gpu_may_commit_hash72"] is False
        assert status["gpu_may_commit_hash216"] is False
        assert status["canonical_vm81_mutation_authority"] is False
        assert status["requires_signed_environmental_vm81_admission"] is True

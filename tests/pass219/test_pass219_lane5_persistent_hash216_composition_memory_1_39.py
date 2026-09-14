from __future__ import annotations

import sqlite3

import pytest

from hhs_backend.runtime.hhs_pass219_lane5_persistent_hash216_composition_memory_1_39 import (
    Pass219Lane5PersistentHash216CompositionMemory,
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
        bit_b = (index * 13 + salt + 5) % 64
        result.append([
            {
                "cell": (index * 11 + salt) % 81,
                "control_g": (index * 19 + salt * 7) % 243,
                "xor_mask": (1 << bit_a) | (1 << bit_b),
            }
        ])
    return result


def test_persistent_composition_survives_restart_and_searches_exactly(tmp_path) -> None:
    root = tmp_path / "lane5-memory"
    key = bytes(range(32))
    parent = _state(139)

    with Pass219Lane5PersistentHash216CompositionMemory(
        root,
        vector_key=key,
        backend="CPU_REFERENCE",
    ) as memory:
        jump = memory.jump_store.build_validated_jump(
            jump_id="persist-16",
            parent_state=parent,
            steps=_steps(16, 13),
            tick=15015,
            cycle_index=37,
            layer_index=4,
        )
        expected_child = list(jump.child_state)
        expected_child_hash216 = jump.child_hash216
        stored = memory.persist_validated_jump(parent_state=parent, jump=jump)
        assert stored["idempotent"] is False
        assert stored["encrypted_snapshot"] is True
        assert stored["restart_rehydratable"] is True
        assert stored["candidate_only"] is True
        assert stored["canonical_vm81_mutation_authority"] is False
        assert stored["canonical_hash216_authority"] is False
        assert stored["canonical_persistence_authority"] is False

        duplicate = memory.persist_validated_jump(parent_state=parent, jump=jump)
        assert duplicate["idempotent"] is True

        status = memory.status()
        assert status["persistent_records"] == 1
        assert status["quarantined_records"] == 0
        assert status["journal_mode"].lower() == "wal"
        assert status["synchronous_full"] is True
        assert status["snapshot_bytes"] == 648
        assert status["vector_store"]["journal_mode"].lower() == "wal"
        assert status["vector_store"]["plaintext_persisted"] is False
        assert status["vector_store"]["authenticated_encryption"] == "AES_GCM"
        first_vector_root = status["vector_store"]["logical_root_sha256"]

    with Pass219Lane5PersistentHash216CompositionMemory(
        root,
        vector_key=key,
        backend="CPU_REFERENCE",
    ) as reopened:
        status = reopened.status()
        assert status["persistent_records"] == 1
        assert status["quarantined_records"] == 0
        assert status["vector_store"]["logical_root_sha256"] == first_vector_root

        ranked = reopened.search(
            current_state=parent,
            goal_hash216=expected_child_hash216,
            tick=1234,
            cycle_index=38,
            top_k=8,
        )
        assert ranked["persistent_composition_memory"] is True
        assert ranked["restart_rehydrated_candidates"] == 1
        assert ranked["ranked"][0]["candidate_id"] == "persist-16"
        assert ranked["ranked"][0]["hash216_distance"] == 0

        reused = reopened.reuse(current_state=parent, jump_id="persist-16")
        assert reused["child_state"] == expected_child
        assert reused["child_hash216"] == expected_child_hash216
        assert reused["represented_transitions"] == 16
        assert reused["intermediate_transitions_executed_on_reuse"] == 0
        assert reused["encrypted_snapshot"] is True
        assert reused["restart_rehydrated"] is True
        assert reused["candidate_only"] is True
        assert reused["canonical_vm81_mutation_authority"] is False
        assert reused["gpu_may_commit_hash72"] is False
        assert reused["gpu_may_commit_hash216"] is False
        assert reused["canonical_persistence_authority"] is False
        assert reused["requires_signed_environmental_vm81_admission"] is True
        assert reused["native_receipt"]["accepted"] is True
        assert reused["native_receipt"]["restart_rehydratable"] is True


def test_persistent_metadata_tamper_quarantines_across_restart(tmp_path) -> None:
    root = tmp_path / "tamper-memory"
    key = bytes(reversed(range(32)))
    parent = _state(71)

    with Pass219Lane5PersistentHash216CompositionMemory(
        root,
        vector_key=key,
        backend="CPU_REFERENCE",
    ) as memory:
        jump = memory.jump_store.build_validated_jump(
            jump_id="tamper-me",
            parent_state=parent,
            steps=_steps(8, 17),
            tick=5005,
            cycle_index=9,
            layer_index=2,
        )
        memory.persist_validated_jump(parent_state=parent, jump=jump)
        replacement_hash216 = jump.child_hash216

    database_path = root / "lane5_composition_memory.sqlite3"
    connection = sqlite3.connect(database_path)
    try:
        connection.execute(
            "UPDATE lane5_composition_memory SET metadata_hash216=? WHERE jump_id=?",
            (replacement_hash216, "tamper-me"),
        )
        connection.commit()
    finally:
        connection.close()

    with Pass219Lane5PersistentHash216CompositionMemory(
        root,
        vector_key=key,
        backend="CPU_REFERENCE",
    ) as reopened:
        status = reopened.status()
        assert status["persistent_records"] == 1
        assert status["quarantined_records"] == 1
        ranked = reopened.search(
            current_state=parent,
            goal_hash216=jump.child_hash216,
            tick=0,
            cycle_index=10,
        )
        assert ranked["restart_rehydrated_candidates"] == 0
        assert ranked["ranked"] == []
        with pytest.raises(ValueError, match="quarantined"):
            reopened.reuse(current_state=parent, jump_id="tamper-me")
        assert reopened.status()["vector_store"]["quarantined"] == 1


def test_persistent_parent_mismatch_and_manual_quarantine_fail_closed(tmp_path) -> None:
    root = tmp_path / "parent-memory"
    key = bytes([41]) * 32
    parent = _state(23)

    with Pass219Lane5PersistentHash216CompositionMemory(
        root,
        vector_key=key,
        backend="CPU_REFERENCE",
    ) as memory:
        jump = memory.jump_store.build_validated_jump(
            jump_id="parent-bound",
            parent_state=parent,
            steps=_steps(4, 5),
            tick=20019,
            cycle_index=3,
            layer_index=1,
        )
        memory.persist_validated_jump(parent_state=parent, jump=jump)
        wrong_parent = list(parent)
        wrong_parent[0] ^= 1
        with pytest.raises(ValueError, match="parent does not match"):
            memory.reuse(current_state=wrong_parent, jump_id="parent-bound")
        memory.quarantine("parent-bound")
        assert memory.status()["quarantined_records"] == 1

    with Pass219Lane5PersistentHash216CompositionMemory(
        root,
        vector_key=key,
        backend="CPU_REFERENCE",
    ) as reopened:
        assert reopened.status()["quarantined_records"] == 1
        with pytest.raises(ValueError, match="quarantined"):
            reopened.reuse(current_state=parent, jump_id="parent-bound")

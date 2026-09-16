from __future__ import annotations

from dataclasses import replace
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

    database_path = root / "lane5_composition_memory.sqlite3"
    connection = sqlite3.connect(database_path)
    try:
        connection.execute(
            "UPDATE lane5_composition_memory SET quarantined=0 WHERE jump_id=?",
            ("parent-bound",),
        )
        connection.commit()
    finally:
        connection.close()

    with Pass219Lane5PersistentHash216CompositionMemory(
        root,
        vector_key=key,
        backend="CPU_REFERENCE",
    ) as reopened:
        assert reopened.status()["quarantined_records"] == 1
        with pytest.raises(ValueError, match="quarantined"):
            reopened.reuse(current_state=parent, jump_id="parent-bound")


def test_external_jump_requires_exact_replay_provenance(tmp_path) -> None:
    root = tmp_path / "replay-memory"
    parent = _state(31)
    with Pass219Lane5PersistentHash216CompositionMemory(root, vector_key=bytes([7]) * 32) as memory:
        jump = memory.jump_store.build_validated_jump(
            jump_id="replay-source",
            parent_state=parent,
            steps=_steps(6, 11),
            tick=101,
            cycle_index=12,
            layer_index=2,
        )
        forged_steps = list(jump.steps)
        first_step = list(forged_steps[0])
        cell, control, mask = first_step[0]
        first_step[0] = (cell, control, mask ^ (1 << 63))
        forged_steps[0] = tuple(first_step)
        forged = replace(jump, jump_id="replay-forged", steps=tuple(forged_steps))
        with pytest.raises(ValueError, match="exact replay provenance"):
            memory.persist_validated_jump(parent_state=parent, jump=forged)
        assert memory.status()["persistent_records"] == 0


def test_fractional_vm5184_words_are_rejected_before_hashing_or_persistence(tmp_path) -> None:
    root = tmp_path / "fractional-memory"
    parent = _state(43)
    with Pass219Lane5PersistentHash216CompositionMemory(root, vector_key=bytes([8]) * 32) as memory:
        jump = memory.jump_store.build_validated_jump(
            jump_id="fractional",
            parent_state=parent,
            steps=_steps(4, 3),
            tick=9,
            cycle_index=2,
            layer_index=1,
        )
        fractional_parent = list(parent)
        fractional_parent[0] = float(fractional_parent[0]) + 0.75
        with pytest.raises(ValueError, match="exact integer"):
            memory.persist_validated_jump(parent_state=fractional_parent, jump=jump)

        fractional_child = list(jump.child_state)
        fractional_child[1] = float(fractional_child[1]) + 0.25
        forged = replace(jump, child_state=tuple(fractional_child))
        with pytest.raises(ValueError, match="exact integer"):
            memory.persist_validated_jump(parent_state=parent, jump=forged)
        assert memory.status()["persistent_records"] == 0


def test_abi_coordinate_overflow_is_rejected_before_ctypes_wrap(tmp_path) -> None:
    root = tmp_path / "overflow-memory"
    parent = _state(47)
    with Pass219Lane5PersistentHash216CompositionMemory(root, vector_key=bytes([9]) * 32) as memory:
        jump = memory.jump_store.build_validated_jump(
            jump_id="overflow",
            parent_state=parent,
            steps=_steps(4, 7),
            tick=19,
            cycle_index=5,
            layer_index=1,
        )
        stored = memory.persist_validated_jump(parent_state=parent, jump=jump)
        record = memory.records()[0]
        with pytest.raises(ValueError, match="cycle_index outside unsigned ABI range"):
            memory.abi.validate_descriptor(
                parent_hash216=record.parent_hash216,
                child_hash216=record.child_hash216,
                composition_hash216=record.composition_hash216,
                metadata_hash216=record.metadata_hash216,
                vector_object_id=stored["vector_object_id"],
                jump_span=record.jump_span,
                phase_slot=record.phase_slot,
                cycle_index=1 << 64,
                layer_index=record.layer_index,
            )
        with pytest.raises(ValueError, match="jump_span outside unsigned ABI range"):
            memory.abi.validate_descriptor(
                parent_hash216=record.parent_hash216,
                child_hash216=record.child_hash216,
                composition_hash216=record.composition_hash216,
                metadata_hash216=record.metadata_hash216,
                vector_object_id=stored["vector_object_id"],
                jump_span=1 << 32,
                phase_slot=record.phase_slot,
                cycle_index=record.cycle_index,
                layer_index=record.layer_index,
            )


def test_malformed_row_is_quarantined_without_aborting_other_rehydration(tmp_path) -> None:
    root = tmp_path / "malformed-memory"
    key = bytes([10]) * 32
    parent = _state(53)
    with Pass219Lane5PersistentHash216CompositionMemory(root, vector_key=key) as memory:
        bad = memory.jump_store.build_validated_jump(
            jump_id="bad-row",
            parent_state=parent,
            steps=_steps(4, 13),
            tick=17,
            cycle_index=6,
            layer_index=1,
        )
        good = memory.jump_store.build_validated_jump(
            jump_id="good-row",
            parent_state=parent,
            steps=_steps(5, 15),
            tick=18,
            cycle_index=7,
            layer_index=1,
        )
        memory.persist_validated_jump(parent_state=parent, jump=bad)
        memory.persist_validated_jump(parent_state=parent, jump=good)
        good_hash = good.child_hash216

    database_path = root / "lane5_composition_memory.sqlite3"
    connection = sqlite3.connect(database_path)
    try:
        connection.execute(
            "UPDATE lane5_composition_memory SET trace_roots_json=? WHERE jump_id=?",
            ("{malformed-json", "bad-row"),
        )
        connection.commit()
    finally:
        connection.close()

    with Pass219Lane5PersistentHash216CompositionMemory(root, vector_key=key) as reopened:
        status = reopened.status()
        assert status["persistent_records"] == 2
        assert status["quarantined_records"] == 1
        ranked = reopened.search(
            current_state=parent,
            goal_hash216=good_hash,
            tick=22,
            cycle_index=8,
        )
        assert ranked["ranked"][0]["candidate_id"] == "good-row"
        assert ranked["ranked"][0]["hash216_distance"] == 0
        with pytest.raises(KeyError, match="unknown persistent composition jump"):
            reopened.reuse(current_state=parent, jump_id="bad-row")


def test_duplicate_destinations_are_deduplicated_before_optimizer(tmp_path) -> None:
    root = tmp_path / "duplicate-destination-memory"
    parent = _state(59)
    with Pass219Lane5PersistentHash216CompositionMemory(root, vector_key=bytes([11]) * 32) as memory:
        steps = _steps(6, 21)
        route_a = memory.jump_store.build_validated_jump(
            jump_id="route-a",
            parent_state=parent,
            steps=steps,
            tick=33,
            cycle_index=9,
            layer_index=2,
        )
        route_b = memory.jump_store.build_validated_jump(
            jump_id="route-b",
            parent_state=parent,
            steps=steps,
            tick=33,
            cycle_index=10,
            layer_index=2,
        )
        assert route_a.child_hash216 == route_b.child_hash216
        assert route_a.composition_hash216 != route_b.composition_hash216
        memory.persist_validated_jump(parent_state=parent, jump=route_a)
        memory.persist_validated_jump(parent_state=parent, jump=route_b)

        ranked = memory.search(
            current_state=parent,
            goal_hash216=route_a.child_hash216,
            tick=34,
            cycle_index=11,
            top_k=8,
        )
        assert ranked["persistent_routes_considered"] == 2
        assert ranked["restart_rehydrated_candidates"] == 1
        assert len(ranked["ranked"]) == 1
        assert ranked["ranked"][0]["candidate_id"] == "route-a"
        assert ranked["ranked"][0]["hash216_distance"] == 0


def test_reuse_failure_quarantines_cached_record_immediately(tmp_path, monkeypatch) -> None:
    root = tmp_path / "reuse-failure-memory"
    parent = _state(61)
    with Pass219Lane5PersistentHash216CompositionMemory(root, vector_key=bytes([12]) * 32) as memory:
        jump = memory.jump_store.build_validated_jump(
            jump_id="reuse-failure",
            parent_state=parent,
            steps=_steps(4, 25),
            tick=41,
            cycle_index=12,
            layer_index=3,
        )
        memory.persist_validated_jump(parent_state=parent, jump=jump)

        def _fail_retrieve(*_args, **_kwargs):
            raise ValueError("synthetic authenticated retrieval failure")

        monkeypatch.setattr(memory.vector_store, "retrieve", _fail_retrieve)
        with pytest.raises(ValueError, match="synthetic authenticated retrieval failure"):
            memory.reuse(current_state=parent, jump_id="reuse-failure")

        assert memory.records()[0].quarantined is True
        ranked = memory.search(
            current_state=parent,
            goal_hash216=jump.child_hash216,
            tick=42,
            cycle_index=13,
        )
        assert ranked["restart_rehydrated_candidates"] == 0
        assert ranked["ranked"] == []

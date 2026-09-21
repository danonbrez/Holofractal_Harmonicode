from __future__ import annotations

import sqlite3

import pytest

from hhs_backend.runtime.hhs_pass219_lane5_thread_lineage_normalization_1_60 import (
    Pass219Lane5ThreadLineageMemory,
    ThreadLineageMemoryError,
    ZERO_OFFSETS,
    ZERO_SERIALIZATION_5184,
    normalized_genesis_witness,
)
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import serialize_offsets_5184


def _h(memory: Pass219Lane5ThreadLineageMemory, label: str) -> str:
    return memory.native.hash216_bytes(("PASS219-1.60-TEST:" + label).encode("ascii"))


def _threads(memory: Pass219Lane5ThreadLineageMemory):
    lineage = _h(memory, "lineage-shared")
    a = memory.register_thread(
        evolution_hash216=_h(memory, "evolution-a"),
        lineage_hash216=lineage,
        pqc_witness_hash216=_h(memory, "pqc-a"),
        capabilities=("read", "infer", "files"),
    )
    b = memory.register_thread(
        evolution_hash216=_h(memory, "evolution-b"),
        lineage_hash216=lineage,
        pqc_witness_hash216=_h(memory, "pqc-b"),
        capabilities=("read", "infer"),
    )
    return a, b


def test_normalized_genesis_is_81_zero_offsets_in_fixed_5184_transcription():
    witness = normalized_genesis_witness()
    assert len(ZERO_OFFSETS) == 81
    assert ZERO_OFFSETS == (0,) * 81
    assert len(ZERO_SERIALIZATION_5184) == 5184
    assert witness["all_qudit_offsets_zero"] is True
    assert witness["same_transcription_operation_roundtrip"] is True
    assert witness["underlying_transition_logic_modified"] is False
    assert witness["floating_point_canonical_authority"] is False


def test_thread_root_is_deterministic_projection_of_complete_boundary(tmp_path):
    with Pass219Lane5ThreadLineageMemory(tmp_path) as memory:
        lineage = _h(memory, "lineage")
        kwargs = dict(
            evolution_hash216=_h(memory, "evolution"),
            lineage_hash216=lineage,
            pqc_witness_hash216=_h(memory, "pqc"),
            capabilities=("read", "infer"),
            bigint_serialization_5184=ZERO_SERIALIZATION_5184,
        )
        left = memory.register_thread(**kwargs)
        right = memory.derive_boundary(**kwargs)
        assert left == right
        assert left.normalized_zero is True
        assert left.thread_root_hash216 != left.scope_hash216
        assert left.palindrome_hash216 != left.lineage_hash216
        assert left.virtual_root.endswith("/lineage/" + lineage)


def test_pqc_bigint_and_scope_changes_change_thread_geometry(tmp_path):
    with Pass219Lane5ThreadLineageMemory(tmp_path) as memory:
        lineage = _h(memory, "lineage")
        base = dict(
            evolution_hash216=_h(memory, "evolution"),
            lineage_hash216=lineage,
            pqc_witness_hash216=_h(memory, "pqc-a"),
            capabilities=("read",),
            bigint_serialization_5184=ZERO_SERIALIZATION_5184,
        )
        a = memory.derive_boundary(**base)
        b = memory.derive_boundary(**{**base, "pqc_witness_hash216": _h(memory, "pqc-b")})
        c = memory.derive_boundary(**{**base, "capabilities": ("read", "infer")})
        nonzero = serialize_offsets_5184((1,) + (0,) * 80)
        d = memory.derive_boundary(**{**base, "bigint_serialization_5184": nonzero})
        assert len({a.thread_root_hash216, b.thread_root_hash216, c.thread_root_hash216, d.thread_root_hash216}) == 4


def test_same_physical_server_does_not_grant_cross_thread_read(tmp_path):
    with Pass219Lane5ThreadLineageMemory(tmp_path) as memory:
        a, b = _threads(memory)
        same_object = _h(memory, "same-content")
        rec_a = memory.index_object(
            thread_root_hash216=a.thread_root_hash216,
            object_hash216=same_object,
            object_type="vector",
            object_ref="jump-a",
        )
        rec_b = memory.index_object(
            thread_root_hash216=b.thread_root_hash216,
            object_hash216=same_object,
            object_type="vector",
            object_ref="jump-b",
        )
        assert rec_a.virtual_path != rec_b.virtual_path
        assert [r.object_ref for r in memory.authorized_index(
            requester_thread_root_hash216=a.thread_root_hash216,
            required_capabilities=("read",),
        )] == ["jump-a"]
        with pytest.raises(ThreadLineageMemoryError, match="not explicitly admitted"):
            memory.authorized_index(
                requester_thread_root_hash216=a.thread_root_hash216,
                target_thread_root_hash216=b.thread_root_hash216,
                required_capabilities=("read",),
            )


def test_explicit_shared_scope_is_intersection_not_union(tmp_path):
    with Pass219Lane5ThreadLineageMemory(tmp_path) as memory:
        a, b = _threads(memory)
        memory.index_object(
            thread_root_hash216=b.thread_root_hash216,
            object_hash216=_h(memory, "b-object"),
            object_type="checkpoint",
            object_ref="checkpoint-b",
        )
        with pytest.raises(ThreadLineageMemoryError, match="widen"):
            memory.create_shared_scope(
                source_thread_root_hash216=a.thread_root_hash216,
                target_thread_root_hash216=b.thread_root_hash216,
                capabilities=("files",),
            )
        bridge = memory.create_shared_scope(
            source_thread_root_hash216=a.thread_root_hash216,
            target_thread_root_hash216=b.thread_root_hash216,
            capabilities=("read",),
        )
        assert bridge["scope_expansion"] is False
        assert bridge["capabilities"] == ("read",)
        records = memory.authorized_index(
            requester_thread_root_hash216=a.thread_root_hash216,
            target_thread_root_hash216=b.thread_root_hash216,
            required_capabilities=("read",),
        )
        assert [r.object_ref for r in records] == ["checkpoint-b"]
        with pytest.raises(ThreadLineageMemoryError, match="exceeds"):
            memory.authorized_index(
                requester_thread_root_hash216=a.thread_root_hash216,
                target_thread_root_hash216=b.thread_root_hash216,
                required_capabilities=("infer",),
            )


def test_cross_thread_bridge_rejects_different_evolutionary_lineage(tmp_path):
    with Pass219Lane5ThreadLineageMemory(tmp_path) as memory:
        a, _ = _threads(memory)
        c = memory.register_thread(
            evolution_hash216=_h(memory, "evolution-c"),
            lineage_hash216=_h(memory, "different-lineage"),
            pqc_witness_hash216=_h(memory, "pqc-c"),
            capabilities=("read",),
        )
        with pytest.raises(ThreadLineageMemoryError, match="matching evolutionary lineage"):
            memory.create_shared_scope(
                source_thread_root_hash216=a.thread_root_hash216,
                target_thread_root_hash216=c.thread_root_hash216,
                capabilities=("read",),
            )


def test_namespace_filter_is_applied_before_candidate_population(tmp_path):
    with Pass219Lane5ThreadLineageMemory(tmp_path) as memory:
        a, b = _threads(memory)
        for index in range(4):
            memory.index_object(
                thread_root_hash216=a.thread_root_hash216,
                object_hash216=_h(memory, f"a-{index}"),
                object_type="vector",
                object_ref=f"a-{index}",
            )
            memory.index_object(
                thread_root_hash216=b.thread_root_hash216,
                object_hash216=_h(memory, f"b-{index}"),
                object_type="vector",
                object_ref=f"b-{index}",
            )
        records = memory.authorized_index(
            requester_thread_root_hash216=a.thread_root_hash216,
            required_capabilities=("read",),
        )
        assert {r.object_ref for r in records} == {f"a-{i}" for i in range(4)}
        assert all(r.thread_root_hash216 == a.thread_root_hash216 for r in records)


def test_restart_preserves_per_thread_index_partition(tmp_path):
    root = tmp_path / "memory"
    with Pass219Lane5ThreadLineageMemory(root) as memory:
        a, b = _threads(memory)
        memory.index_object(
            thread_root_hash216=a.thread_root_hash216,
            object_hash216=_h(memory, "persist-a"),
            object_type="state",
            object_ref="persist-a",
        )
        a_root, b_root = a.thread_root_hash216, b.thread_root_hash216

    with Pass219Lane5ThreadLineageMemory(root) as memory:
        assert memory.thread(a_root).thread_root_hash216 == a_root
        assert memory.thread(b_root).thread_root_hash216 == b_root
        records = memory.authorized_index(
            requester_thread_root_hash216=a_root,
            required_capabilities=("read",),
        )
        assert [r.object_ref for r in records] == ["persist-a"]
        status = memory.status()
        assert status["journal_mode"].lower() == "wal"
        assert status["synchronous_full"] is True
        assert status["logical_thread_indexes"] is True
        assert status["namespace_prefilter_before_vector_rank"] is True


def test_float_metadata_and_malformed_pqc_fail_closed(tmp_path):
    with Pass219Lane5ThreadLineageMemory(tmp_path) as memory:
        a, _ = _threads(memory)
        with pytest.raises(ThreadLineageMemoryError, match="floating-point"):
            memory.index_object(
                thread_root_hash216=a.thread_root_hash216,
                object_hash216=_h(memory, "float-object"),
                object_type="vector",
                object_ref="float-object",
                metadata={"score": 0.5},
            )
        with pytest.raises(ThreadLineageMemoryError, match="pqc_witness_hash216"):
            memory.register_thread(
                evolution_hash216=_h(memory, "evolution-x"),
                lineage_hash216=_h(memory, "lineage-x"),
                pqc_witness_hash216="not-a-hash216",
                capabilities=("read",),
            )


def test_sql_index_is_composite_thread_partition(tmp_path):
    with Pass219Lane5ThreadLineageMemory(tmp_path) as memory:
        columns = {
            row[1]
            for row in memory.db.execute("PRAGMA table_info(lane5_thread_index)").fetchall()
        }
        assert {
            "scope_hash216", "thread_root_hash216", "lineage_hash216",
            "object_hash216", "metadata_hash216",
        }.issubset(columns)
        index_sql = memory.db.execute(
            "SELECT sql FROM sqlite_master WHERE name='lane5_thread_index_partition'"
        ).fetchone()[0]
        assert "scope_hash216" in index_sql
        assert "thread_root_hash216" in index_sql
        assert "lineage_hash216" in index_sql

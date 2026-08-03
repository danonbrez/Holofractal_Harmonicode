from __future__ import annotations

import importlib
import json
import os
import pathlib
import sqlite3
import sys
from concurrent.futures import ThreadPoolExecutor

import pytest

from hhs_python.runtime.hhs_pass205_continuation_bridge import (
    CELL_COUNT,
    CONTROL_COUNT,
    Q_COUNT,
    STATE_BITS,
    Pass205NativeBridge,
)
from hhs_backend.runtime.hhs_pass205_accelerator_translation_v1 import (
    BACKENDS,
    Pass205AcceleratorTranslation,
)
from hhs_backend.runtime.hhs_pass205_continuation_runtime_v1 import (
    ContinuationRejected,
    Pass205ContinuationRuntime,
)


def _event(cell: int, mask: int, control: int = 0) -> dict[str, int]:
    return {"cell": cell, "control_g": control, "xor_mask": mask}


def test_native_dimensions_and_complete_q_bijection() -> None:
    native = Pass205NativeBridge()
    assert STATE_BITS == 5184
    assert Q_COUNT == 1_259_712
    assert native.q_address(0, 0) == 0
    assert native.q_address(5183, 242) == 1_259_711
    for s in range(STATE_BITS):
        for g in range(CONTROL_COUNT):
            q = native.q_address(s, g)
            assert q == 243 * s + g
            assert native.q_decode(q) == (s, g)
    with pytest.raises(ValueError):
        native.q_address(STATE_BITS, 0)
    with pytest.raises(ValueError):
        native.q_address(0, CONTROL_COUNT)
    with pytest.raises(ValueError):
        native.q_decode(Q_COUNT)


def test_native_sparse_projection_equals_full_and_order_is_lineage_sensitive() -> None:
    native = Pass205NativeBridge()
    parent = [((index + 1) * 0x102030405060708) & ((1 << 64) - 1) for index in range(CELL_COUNT)]
    parent_projection = native.project_full(parent)
    events_a = [_event(2, 0x11, 5), _event(70, 0x8000000000000000, 242)]
    events_b = list(reversed(events_a))
    child_a, frontier_bits, _, _ = native.apply_delta(parent, events_a)
    child_b, _, _, _ = native.apply_delta(parent, events_b)
    assert child_a == child_b
    frontier = [index for index, value in enumerate(frontier_bits) if value]
    assert native.validate_frontier(events_a, frontier)
    assert native.project_sparse(child_a, parent_projection, frontier) == native.project_full(child_a)
    assert native.delta_root(events_a) != native.delta_root(events_b)
    assert native.hydration_root(events_a) != native.hydration_root(events_b)
    incomplete = frontier[:-1]
    assert not native.validate_frontier(events_a, incomplete)


def test_native_token_binds_parent_content_roots_receipt_and_generation() -> None:
    native = Pass205NativeBridge()
    root = native.hash216_bytes(b"root")
    other = native.hash216_bytes(b"other")
    receipt = native.hash216_bytes(b"receipt")[:72]
    base = native.build_token(
        parent_root=root,
        content_root=root,
        delta_root=root,
        hydration_root=root,
        dependency_root=root,
        projection_root=root,
        learning_root=root,
        parent_receipt=receipt,
        generation=1,
    )
    changed_parent = native.build_token(
        parent_root=other,
        content_root=root,
        delta_root=root,
        hydration_root=root,
        dependency_root=root,
        projection_root=root,
        learning_root=root,
        parent_receipt=receipt,
        generation=1,
    )
    changed_generation = native.build_token(
        parent_root=root,
        content_root=root,
        delta_root=root,
        hydration_root=root,
        dependency_root=root,
        projection_root=root,
        learning_root=root,
        parent_receipt=receipt,
        generation=2,
    )
    assert base["continuation_root216"] != changed_parent["continuation_root216"]
    assert base["continuation_root216"] != changed_generation["continuation_root216"]
    assert base["receipt_hash72"] != changed_parent["receipt_hash72"]


def test_runtime_advance_branch_replay_reverse_and_hidden_lineage(tmp_path: pathlib.Path) -> None:
    runtime = Pass205ContinuationRuntime(tmp_path / "pass205.sqlite3")
    genesis = runtime.snapshot(runtime.genesis_root216)
    first = runtime.advance(
        parent_root216=genesis["continuation_root216"],
        expected_parent_receipt_hash72=genesis["receipt_hash72"],
        events=[_event(0, 1, 72), _event(40, 4, 216)],
    )
    branch_a = runtime.branch(
        parent_root216=first["continuation_root216"],
        events=[_event(7, 8, 1)],
    )
    branch_b = runtime.branch(
        parent_root216=first["continuation_root216"],
        events=[_event(7, 16, 1)],
    )
    assert branch_a["continuation_root216"] != branch_b["continuation_root216"]
    assert runtime.verify(first["continuation_root216"])["ok"]
    assert runtime.replay(branch_a["continuation_root216"])["ok"]
    inverse = runtime.reverse(first["continuation_root216"])
    assert inverse["content_root216"] == genesis["content_root216"]
    assert inverse["continuation_root216"] != genesis["continuation_root216"]
    assert inverse["parent_root216"] == first["continuation_root216"]
    graph = runtime.graph(first["continuation_root216"])
    assert set(graph["children_root216"]) >= {
        branch_a["continuation_root216"], branch_b["continuation_root216"]
    }


def test_runtime_rejects_wrong_parent_receipt_and_incomplete_frontier(tmp_path: pathlib.Path) -> None:
    runtime = Pass205ContinuationRuntime(tmp_path / "pass205.sqlite3")
    genesis = runtime.snapshot(runtime.genesis_root216)
    with pytest.raises(ContinuationRejected, match="parent Hash72 receipt mismatch"):
        runtime.advance(
            parent_root216=genesis["continuation_root216"],
            expected_parent_receipt_hash72="0" * 72,
            events=[_event(4, 1, 5)],
        )
    _, bits, _, _ = runtime.native.apply_delta(genesis["state_words"], [_event(4, 1, 5)])
    required = [index for index, enabled in enumerate(bits) if enabled]
    with pytest.raises(ContinuationRejected, match="dependency frontier"):
        runtime.advance(
            parent_root216=genesis["continuation_root216"],
            events=[_event(4, 1, 5)],
            frontier_cells=required[:-1],
        )


def test_vector_retrieval_exact_rerank_and_hydrate_target(tmp_path: pathlib.Path) -> None:
    runtime = Pass205ContinuationRuntime(tmp_path / "pass205.sqlite3")
    root = runtime.genesis_root216
    snapshots = []
    for index in range(12):
        parent = runtime.snapshot(root)
        child = runtime.advance(
            parent_root216=root,
            expected_parent_receipt_hash72=parent["receipt_hash72"],
            events=[_event(index, 1 << (index % 32), index % 243)],
        )
        snapshots.append(child)
        root = child["continuation_root216"]
    target = list(snapshots[5]["state_words"])
    target[55] ^= 0x100
    retrieval = runtime.retrieve(target_state_words=target, top_k=32)
    selected = runtime.snapshot(retrieval["selected_parent_root216"])
    exact_cost = sum((int(a) ^ int(b)).bit_count() for a, b in zip(selected["state_words"], target))
    assert retrieval["exact_delta_cost"] == exact_cost
    hydrated = runtime.hydrate_target(target_state_words=target, controls_by_cell={"55": 7})
    assert hydrated["snapshot"]["state_words"] == target
    assert runtime.verify(hydrated["snapshot"]["continuation_root216"])["ok"]


def test_incompatible_vector_candidate_is_rejected(tmp_path: pathlib.Path) -> None:
    runtime = Pass205ContinuationRuntime(tmp_path / "pass205.sqlite3")
    genesis = runtime.snapshot(runtime.genesis_root216)
    with runtime._transaction() as connection:
        connection.execute(
            "UPDATE vectors SET constraint_root216=? WHERE continuation_root216=?",
            (runtime.native.hash216_bytes(b"incompatible"), genesis["continuation_root216"]),
        )
    with pytest.raises(ContinuationRejected, match="no continuation-compatible snapshot"):
        runtime.retrieve(target_state_words=genesis["state_words"])


def test_tampered_state_and_parent_lineage_fail_closed(tmp_path: pathlib.Path) -> None:
    runtime = Pass205ContinuationRuntime(tmp_path / "pass205.sqlite3")
    genesis = runtime.snapshot(runtime.genesis_root216)
    child = runtime.advance(
        parent_root216=genesis["continuation_root216"],
        events=[_event(8, 0x80, 9)],
    )
    tampered = list(child["state_words"])
    tampered[8] ^= 1
    with runtime._transaction() as connection:
        connection.execute(
            "UPDATE snapshots SET state_json=? WHERE continuation_root216=?",
            (json.dumps(tampered), child["continuation_root216"]),
        )
    result = runtime.verify(child["continuation_root216"])
    assert not result["ok"]
    assert "CONTENT_ROOT_MISMATCH" in result["reasons"]


def test_single_mutation_authority_supports_conflict_safe_branch_candidates(tmp_path: pathlib.Path) -> None:
    runtime = Pass205ContinuationRuntime(tmp_path / "pass205.sqlite3")
    genesis = runtime.snapshot(runtime.genesis_root216)

    def branch(index: int) -> str:
        result = runtime.advance(
            parent_root216=genesis["continuation_root216"],
            expected_parent_receipt_hash72=genesis["receipt_hash72"],
            events=[_event(index, 1 << (index % 32), index)],
        )
        return result["continuation_root216"]

    with ThreadPoolExecutor(max_workers=8) as executor:
        roots = list(executor.map(branch, range(8)))
    assert len(set(roots)) == 8
    assert all(runtime.verify(root)["ok"] for root in roots)


def test_accelerator_translation_round_trip_batch_isolation_and_cpu_oracle() -> None:
    native = Pass205NativeBridge()
    translation = Pass205AcceleratorTranslation()
    states = [
        [0] * CELL_COUNT,
        [index for index in range(CELL_COUNT)],
        [((index + 3) * 17) & ((1 << 64) - 1) for index in range(CELL_COUNT)],
    ]
    projections = [native.project_full(state) for state in states]
    deltas = [
        [_event(0, 1, 0), _event(80, 2, 242)],
        [_event(5, 4, 72)],
        [_event(40, 8, 216)],
    ]
    batch = translation.pack_batch(states=states, projections=projections, deltas=deltas)
    assert translation.unpack_states(batch.state_soa, batch.batch_size) == states
    assert translation.unpack_projections(batch.projection_soa, batch.batch_size) == projections
    result = translation.execute_cpu_reference(batch)
    assert result["ok"]
    for index, events in enumerate(deltas):
        expected, _, _, _ = native.apply_delta(states[index], events)
        assert result["child_states"][index] == expected
    assert batch.transfer_bytes < batch.dense_transfer_bytes
    for backend in BACKENDS:
        descriptor = translation.dispatch_descriptor(backend, batch)
        assert descriptor["deterministic_integer_only"]
        assert descriptor["gpu_may_commit_hash72"] is False


def test_api_router_exposes_contract_surfaces_and_visual_studio(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    monkeypatch.setenv("HHS_PASS205_DB", str(tmp_path / "api.sqlite3"))
    sys.modules.pop("hhs_backend.api.pass205_continuation_routes", None)
    routes = importlib.import_module("hhs_backend.api.pass205_continuation_routes")
    paths = {route.path for route in routes.router.routes}
    expected = {
        "/api/runtime/continuation/status",
        "/api/runtime/continuation/snapshots/{continuation_root216:path}",
        "/api/runtime/continuation/graph/{continuation_root216:path}",
        "/api/runtime/continuation/projections/{continuation_root216:path}",
        "/api/runtime/continuation/retrieve",
        "/api/runtime/continuation/hydrate",
        "/api/runtime/continuation/advance",
        "/api/runtime/continuation/branch",
        "/api/runtime/continuation/reverse",
        "/api/runtime/continuation/replay",
        "/api/runtime/continuation/verify",
        "/api/runtime/continuation/studio",
    }
    assert expected <= paths
    assert "VM5184 × G243" in routes.STUDIO_HTML
    assert "Advance committed state" in routes.STUDIO_HTML


def test_runtime_status_declares_no_float_authority_and_gpu_commit_boundary(tmp_path: pathlib.Path) -> None:
    runtime = Pass205ContinuationRuntime(tmp_path / "pass205.sqlite3")
    status = runtime.status()
    assert status["state_bits"] == 5184
    assert status["hydration_projection_count"] == 1_259_712
    assert status["projection_channel_count"] == 32
    assert status["native_abi"]["canonical_float_fields"] == 0
    assert status["single_vm81_mutation_authority"]
    assert status["single_ordered_hash72_commit_stream"]
    assert status["cache_hit_bypasses_admission"] is False
    assert status["accelerator_translation"]["physical_gpu_backend_active"] is False

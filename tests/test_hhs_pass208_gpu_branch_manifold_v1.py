from __future__ import annotations

import pathlib

import pytest

from hhs_backend.runtime.hhs_pass205_continuation_runtime_v1 import (
    Pass205ContinuationRuntime,
)
from hhs_backend.runtime.hhs_pass208_gpu_branch_manifold_v1 import (
    Pass208GPUBranchManifold,
    Pass208GPUManifoldRejected,
)


def test_gpu_branch_manifold_expands_and_commits_through_vm81(tmp_path: pathlib.Path) -> None:
    continuation = Pass205ContinuationRuntime(tmp_path / "pass205.sqlite3")
    manifold = Pass208GPUBranchManifold(
        enabled=True,
        backend="CPU_REFERENCE",
        require_physical_gpu=False,
        max_branches=8,
        cache_capacity_bytes=32 * 1024 * 1024,
        cache_capacity_entries=32,
    )
    try:
        parent = continuation.snapshot(continuation.genesis_root216)
        branches = [
            [{"cell": 0, "control_g": 7, "xor_mask": 1}],
            [{"cell": 0, "control_g": 7, "xor_mask": 2}],
            [
                {"cell": 0, "control_g": 7, "xor_mask": 3},
                {"cell": 40, "control_g": 72, "xor_mask": 1 << 17},
            ],
        ]
        target = list(parent["state_words"])
        target[0] ^= 2

        expansion = manifold.expand(
            parent_snapshot=parent,
            branches=branches,
            bytecode_hydration_lattice_root216=parent["constraint_root216"],
            target_state_words=target,
        )
        assert expansion["ok"] is True
        assert expansion["branch_count"] == 3
        assert expansion["logical_lane_dispatches"] == 3 * 5184
        assert expansion["verified_against_cpu"] is True
        assert expansion["gpu_may_commit_hash72"] is False
        assert expansion["selected_candidate"]["branch_ordinal"] == 1
        assert expansion["selected_candidate"]["objective_distance"] == 0
        assert len({candidate["branch_candidate_root216"] for candidate in expansion["candidates"]}) == 3
        assert all(
            candidate["bytecode_hydration_lattice_root216"] == parent["constraint_root216"]
            for candidate in expansion["candidates"]
        )

        committed = manifold.expand_and_commit(
            continuation_runtime=continuation,
            parent_root216=parent["continuation_root216"],
            expected_parent_receipt_hash72=parent["receipt_hash72"],
            branches=branches,
            bytecode_hydration_lattice_root216=parent["constraint_root216"],
            target_state_words=target,
        )
        snapshot = committed["committed_snapshot"]
        selected = committed["manifold"]["selected_candidate"]
        assert committed["ok"] is True
        assert committed["selected_branch_recomputed_by_singleton_vm81"] is True
        assert committed["gpu_committed_hash72"] is False
        assert snapshot["state_words"] == selected["child_state_words"]
        assert snapshot["content_root216"] == selected["child_content_root216"]
        assert snapshot["projection_root216"] == selected["child_projection_root216"]
        assert continuation.verify(snapshot["continuation_root216"])["ok"] is True
    finally:
        manifold.close()


def test_gpu_branch_manifold_rejects_alternate_lattice_root(tmp_path: pathlib.Path) -> None:
    continuation = Pass205ContinuationRuntime(tmp_path / "pass205.sqlite3")
    manifold = Pass208GPUBranchManifold(
        enabled=True,
        backend="CPU_REFERENCE",
        require_physical_gpu=False,
        max_branches=2,
    )
    try:
        parent = continuation.snapshot(continuation.genesis_root216)
        alternate_root = "x" * 216
        assert alternate_root != parent["constraint_root216"]
        with pytest.raises(Pass208GPUManifoldRejected, match="must equal"):
            manifold.expand(
                parent_snapshot=parent,
                branches=[[{"cell": 0, "control_g": 0, "xor_mask": 1}]],
                bytecode_hydration_lattice_root216=alternate_root,
            )
    finally:
        manifold.close()


def test_gpu_branch_manifold_is_disabled_by_default() -> None:
    manifold = Pass208GPUBranchManifold(enabled=False)
    status = manifold.status()
    assert status["enabled"] is False
    assert status["driver"] is None
    assert status["same_kernel_bytecode_hydration_lattice"] is True
    with pytest.raises(Pass208GPUManifoldRejected, match="disabled"):
        manifold.expand(
            parent_snapshot={},
            branches=[[{"cell": 0, "control_g": 0, "xor_mask": 1}]],
        )

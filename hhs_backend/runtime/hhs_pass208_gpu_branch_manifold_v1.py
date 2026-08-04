"""Pass 208 GPU neural branch expansion manifold for the VM81 hydration lattice.

The GPU is a parallel candidate-expansion surface inside the inherited kernel
bytecode lattice. It is not a second model authority, VM, receipt clock, or
persistence path. Every branch inherits one committed Pass 205 parent,
constraint/bytecode root, ordered q-address hydration, and Hash216 lineage.
Only an exact CPU-verified branch may be submitted back to Pass 205's singleton
VM81 admission and Hash72 commit path.
"""
from __future__ import annotations

import json
import os
import threading
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass207_vm81_gpu_runtime_v1 import (
    Pass207GPURejected,
    Pass207VM81GPURuntime,
)

SCHEMA = "HHS_PASS_208_GPU_BRANCH_MANIFOLD_V1"
CONTRACT = "HHS-P208-DIGITALOCEAN-PHYSICAL-GPU-NEURAL-BRANCH-MANIFOLD-VM81-HYDRATION-LATTICE-H72-H216"
UINT64_MASK = (1 << 64) - 1


class Pass208GPUManifoldRejected(RuntimeError):
    pass


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")


def _validate_root216(value: str, field: str) -> str:
    result = str(value)
    if len(result) != 216:
        raise Pass208GPUManifoldRejected(f"{field} must contain exactly 216 symbols")
    return result


def _validate_state(words: Sequence[int]) -> list[int]:
    if len(words) != 81:
        raise Pass208GPUManifoldRejected("target state requires exactly 81 uint64 words")
    result = [int(value) for value in words]
    if any(value < 0 or value > UINT64_MASK for value in result):
        raise Pass208GPUManifoldRejected("target state word outside uint64")
    return result


def _normalize_events(events: Sequence[Mapping[str, Any]]) -> list[dict[str, int]]:
    if not events or len(events) > 81:
        raise Pass208GPUManifoldRejected("each branch requires between 1 and 81 delta events")
    normalized: list[dict[str, int]] = []
    seen: set[int] = set()
    for ordinal, event in enumerate(events):
        try:
            cell = int(event["cell"])
            control_g = int(event["control_g"])
            xor_mask = int(event["xor_mask"])
        except (KeyError, TypeError, ValueError) as exc:
            raise Pass208GPUManifoldRejected(f"invalid branch event at ordinal {ordinal}") from exc
        if cell < 0 or cell >= 81 or cell in seen:
            raise Pass208GPUManifoldRejected("invalid or duplicate branch cell")
        if control_g < 0 or control_g >= 243:
            raise Pass208GPUManifoldRejected("branch control_g outside [0,242]")
        if xor_mask <= 0 or xor_mask > UINT64_MASK:
            raise Pass208GPUManifoldRejected("branch xor_mask outside nonzero uint64")
        seen.add(cell)
        normalized.append({"cell": cell, "control_g": control_g, "xor_mask": xor_mask})
    return normalized


def _popcount_distance(left: Sequence[int], right: Sequence[int]) -> int:
    return sum((int(a) ^ int(b)).bit_count() for a, b in zip(left, right))


class Pass208GPUBranchManifold:
    """Bounded branch expansion inside one inherited VM81 hydration lattice."""

    def __init__(
        self,
        *,
        enabled: bool | None = None,
        backend: str | None = None,
        require_physical_gpu: bool | None = None,
        device_index: int | None = None,
        max_branches: int | None = None,
        cache_capacity_bytes: int | None = None,
        cache_capacity_entries: int | None = None,
    ) -> None:
        self.enabled = _env_bool("HHS_PASS208_GPU_ENABLED", False) if enabled is None else bool(enabled)
        self.backend = backend or os.environ.get("HHS_PASS207_GPU_BACKEND", "AUTO")
        self.require_physical_gpu = (
            _env_bool("HHS_PASS207_REQUIRE_PHYSICAL_GPU", False)
            if require_physical_gpu is None
            else bool(require_physical_gpu)
        )
        self.device_index = int(
            os.environ.get("HHS_PASS207_GPU_DEVICE_INDEX", "0")
            if device_index is None
            else device_index
        )
        self.max_branches = int(
            os.environ.get("HHS_PASS208_MAX_BRANCHES", "256")
            if max_branches is None
            else max_branches
        )
        self.cache_capacity_bytes = int(
            os.environ.get("HHS_PASS207_CACHE_BYTES", str(512 * 1024 * 1024))
            if cache_capacity_bytes is None
            else cache_capacity_bytes
        )
        self.cache_capacity_entries = int(
            os.environ.get("HHS_PASS207_CACHE_ENTRIES", "512")
            if cache_capacity_entries is None
            else cache_capacity_entries
        )
        if self.max_branches < 1:
            raise Pass208GPUManifoldRejected("HHS_PASS208_MAX_BRANCHES must be positive")
        self._lock = threading.RLock()
        self._runtime: Pass207VM81GPURuntime | None = None
        if self.enabled:
            self._runtime = Pass207VM81GPURuntime(
                backend=self.backend,
                device_index=self.device_index,
                cache_capacity_bytes=self.cache_capacity_bytes,
                cache_capacity_entries=self.cache_capacity_entries,
                require_physical_gpu=self.require_physical_gpu,
            )

    def close(self) -> None:
        with self._lock:
            if self._runtime is not None:
                self._runtime.close()
                self._runtime = None

    def _active_runtime(self) -> Pass207VM81GPURuntime:
        if not self.enabled or self._runtime is None:
            raise Pass208GPUManifoldRejected("Pass 208 GPU branch manifold is disabled")
        return self._runtime

    def status(self) -> dict[str, Any]:
        driver = self._runtime.status() if self._runtime is not None else None
        return {
            "schema": SCHEMA,
            "contract": CONTRACT,
            "ok": True,
            "enabled": self.enabled,
            "backend_requested": self.backend,
            "require_physical_gpu": self.require_physical_gpu,
            "device_index": self.device_index,
            "max_branches": self.max_branches,
            "gpu_interpretation": "NEURAL_NETWORK_BRANCH_TREE_EXPANSION_MANIFOLD",
            "same_kernel_bytecode_hydration_lattice": True,
            "separate_model_authority": False,
            "branch_candidate_only": True,
            "gpu_may_commit_hash72": False,
            "singleton_vm81_commit_authority": True,
            "driver": driver,
        }

    def expand(
        self,
        *,
        parent_snapshot: Mapping[str, Any],
        branches: Sequence[Sequence[Mapping[str, Any]]],
        bytecode_hydration_lattice_root216: str | None = None,
        target_state_words: Sequence[int] | None = None,
    ) -> dict[str, Any]:
        runtime = self._active_runtime()
        if not branches:
            raise Pass208GPUManifoldRejected("at least one branch is required")
        if len(branches) > self.max_branches:
            raise Pass208GPUManifoldRejected(
                f"branch count {len(branches)} exceeds configured maximum {self.max_branches}"
            )
        parent_root = _validate_root216(
            str(parent_snapshot["continuation_root216"]), "parent_continuation_root216"
        )
        constraint_root = _validate_root216(
            str(parent_snapshot["constraint_root216"]), "constraint_root216"
        )
        lattice_root = _validate_root216(
            bytecode_hydration_lattice_root216 or constraint_root,
            "bytecode_hydration_lattice_root216",
        )
        if lattice_root != constraint_root:
            raise Pass208GPUManifoldRejected(
                "branch bytecode hydration lattice root must equal the committed parent constraint root"
            )
        parent_state = _validate_state(parent_snapshot["state_words"])
        parent_projection = parent_snapshot["projection_channels"]
        normalized = [_normalize_events(events) for events in branches]
        target = _validate_state(target_state_words) if target_state_words is not None else None

        accelerator_batch = runtime.translation.pack_batch(
            states=[parent_state for _ in normalized],
            projections=[parent_projection for _ in normalized],
            deltas=normalized,
        )
        executed = runtime.execute_batch(accelerator_batch)
        native = runtime.translation.native
        candidates: list[dict[str, Any]] = []
        for branch_ordinal, events in enumerate(normalized):
            hydration_start = accelerator_batch.hydration_offsets[branch_ordinal]
            hydration_end = accelerator_batch.hydration_offsets[branch_ordinal + 1]
            hydration_q = accelerator_batch.hydration_q[hydration_start:hydration_end]
            child_state = executed["child_states"][branch_ordinal]
            child_projection = executed["child_projections"][branch_ordinal]
            frontier = executed["frontiers"][branch_ordinal]
            content_root = native.state_root(child_state)
            projection_root = native.projection_root(child_projection)
            delta_root = native.delta_root(events)
            hydration_root = native.hydration_root(events)
            dependency_root = native.frontier_root(frontier)
            objective_distance = (
                _popcount_distance(child_state, target)
                if target is not None
                else sum(int(event["xor_mask"]).bit_count() for event in events)
            )
            branch_payload = {
                "schema": "HHS_PASS_208_GPU_BRANCH_CANDIDATE_V1",
                "parent_continuation_root216": parent_root,
                "parent_receipt_hash72": str(parent_snapshot["receipt_hash72"]),
                "bytecode_hydration_lattice_root216": lattice_root,
                "branch_ordinal": branch_ordinal,
                "ordered_delta_events": events,
                "ordered_hydration_q_addresses": hydration_q,
                "dependency_frontier": frontier,
                "delta_root216": delta_root,
                "hydration_root216": hydration_root,
                "dependency_root216": dependency_root,
                "child_content_root216": content_root,
                "child_projection_root216": projection_root,
                "objective_distance": objective_distance,
                "candidate_only": True,
                "gpu_may_commit_hash72": False,
            }
            branch_payload["branch_candidate_root216"] = native.hash216_bytes(
                _canonical_bytes(branch_payload)
            )
            branch_payload["child_state_words"] = child_state
            branch_payload["child_projection_channels"] = child_projection
            candidates.append(branch_payload)

        ranked = sorted(
            candidates,
            key=lambda item: (
                int(item["objective_distance"]),
                str(item["branch_candidate_root216"]),
                int(item["branch_ordinal"]),
            ),
        )
        manifold_root = native.hash216_bytes(
            _canonical_bytes({
                "schema": SCHEMA,
                "parent_continuation_root216": parent_root,
                "bytecode_hydration_lattice_root216": lattice_root,
                "ordered_branch_candidate_roots216": [
                    item["branch_candidate_root216"] for item in candidates
                ],
                "ranked_branch_candidate_roots216": [
                    item["branch_candidate_root216"] for item in ranked
                ],
            })
        )
        return {
            "schema": "HHS_PASS_208_GPU_BRANCH_EXPANSION_RESULT_V1",
            "contract": CONTRACT,
            "ok": True,
            "manifold_root216": manifold_root,
            "parent_continuation_root216": parent_root,
            "bytecode_hydration_lattice_root216": lattice_root,
            "branch_count": len(candidates),
            "logical_lane_dispatches": len(candidates) * 5184,
            "objective": "TARGET_POPCOUNT_DISTANCE" if target is not None else "DELTA_POPCOUNT_COST",
            "stable_rank_order": [
                "objective_distance",
                "branch_candidate_root216",
                "branch_ordinal",
            ],
            "candidates": candidates,
            "ranked_candidates": ranked,
            "selected_candidate": ranked[0],
            "physical_gpu": bool(executed["driver"]["physical_gpu"]),
            "verified_against_cpu": True,
            "gpu_may_commit_hash72": False,
            "singleton_vm81_commit_authority": True,
            "driver": executed["driver"],
        }

    def expand_and_commit(
        self,
        *,
        continuation_runtime: Any,
        parent_root216: str,
        branches: Sequence[Sequence[Mapping[str, Any]]],
        expected_parent_receipt_hash72: str | None = None,
        bytecode_hydration_lattice_root216: str | None = None,
        target_state_words: Sequence[int] | None = None,
        selected_branch_ordinal: int | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            parent = continuation_runtime.snapshot(parent_root216)
            if expected_parent_receipt_hash72 is not None and (
                expected_parent_receipt_hash72 != parent["receipt_hash72"]
            ):
                raise Pass208GPUManifoldRejected("parent Hash72 receipt mismatch")
            expansion = self.expand(
                parent_snapshot=parent,
                branches=branches,
                bytecode_hydration_lattice_root216=bytecode_hydration_lattice_root216,
                target_state_words=target_state_words,
            )
            if selected_branch_ordinal is None:
                selected = expansion["selected_candidate"]
            else:
                matches = [
                    candidate for candidate in expansion["candidates"]
                    if int(candidate["branch_ordinal"]) == int(selected_branch_ordinal)
                ]
                if len(matches) != 1:
                    raise Pass208GPUManifoldRejected("selected branch ordinal is unavailable")
                selected = matches[0]
            committed = continuation_runtime.advance(
                parent_root216=parent_root216,
                events=selected["ordered_delta_events"],
                expected_parent_receipt_hash72=parent["receipt_hash72"],
                frontier_cells=selected["dependency_frontier"],
            )
            if committed["content_root216"] != selected["child_content_root216"]:
                raise Pass208GPUManifoldRejected("selected branch committed content root diverged")
            if committed["projection_root216"] != selected["child_projection_root216"]:
                raise Pass208GPUManifoldRejected("selected branch committed projection root diverged")
            if committed["dependency_root216"] != selected["dependency_root216"]:
                raise Pass208GPUManifoldRejected("selected branch committed dependency root diverged")
            return {
                "schema": "HHS_PASS_208_GPU_BRANCH_COMMIT_RESULT_V1",
                "contract": CONTRACT,
                "ok": True,
                "manifold": expansion,
                "selected_branch_candidate_root216": selected["branch_candidate_root216"],
                "committed_snapshot": committed,
                "selected_branch_recomputed_by_singleton_vm81": True,
                "gpu_committed_hash72": False,
            }


PASS208_GPU_BRANCH_MANIFOLD = Pass208GPUBranchManifold()

"""Lane 5 recursive persistent Hash216 composition graph, Pass 219 1.40.

The graph composes already validated and already persisted 1.39 candidate jumps.
Connectivity is exact Hash216 equality. Frontier ranking is delegated to the
inherited 1.37/Pass207 GPU/vector search fabric. Every traversed edge is
rehydrated and authenticated through 1.39; no represented VM81 transition is
re-executed during route reuse. The terminal state remains candidate-only until
signed environmental VM81 admission.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass219_lane5_hash216_gpu_phase_interlace_1_37 import (
    Hash216CompositionCandidate,
    split_hash216,
)
from hhs_backend.runtime.hhs_pass219_lane5_persistent_hash216_composition_memory_1_39 import (
    Pass219Lane5PersistentHash216CompositionMemory,
    PersistentHash216CompositionRecord,
)
from hhs_python.runtime.hhs_pass219_lane5_recursive_composition_graph_bridge import (
    CYCLE,
    QUARTER,
    Pass219Lane5RecursiveCompositionGraphBridge,
)

SCHEMA = "HHS_PASS_219_LANE5_RECURSIVE_HASH216_COMPOSITION_GRAPH_1_40"


def _canonical(value: Any) -> bytes:
    if isinstance(value, float):
        raise ValueError("floating-point recursive composition metadata forbidden")
    if isinstance(value, Mapping):
        for item in value.values():
            if isinstance(item, float):
                raise ValueError("floating-point recursive composition metadata forbidden")
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


@dataclass(frozen=True)
class RecursiveCompositionPath:
    start_hash216: str
    goal_hash216: str
    terminal_hash216: str
    jump_ids: tuple[str, ...]
    edge_composition_hash216: tuple[str, ...]
    edge_metadata_hash216: tuple[str, ...]
    total_span: int
    phase_slot: int
    cycle_index: int
    path_hash216: str
    ordered_lineage_identity: str
    exact_target: bool


@dataclass(frozen=True)
class _Frontier:
    state: tuple[int, ...]
    node_hash216: str
    jump_ids: tuple[str, ...]
    records: tuple[PersistentHash216CompositionRecord, ...]
    visited: tuple[str, ...]
    total_span: int
    distance: int


class Pass219Lane5RecursiveHash216CompositionGraph:
    """Bounded recursive search over durable 1.39 composition memory."""

    def __init__(
        self,
        state_root: str | Path,
        *,
        vector_key: bytes | None = None,
        backend: str = "CPU_REFERENCE",
        require_physical_gpu: bool = False,
    ) -> None:
        self.memory = Pass219Lane5PersistentHash216CompositionMemory(
            state_root,
            vector_key=vector_key,
            backend=backend,
            require_physical_gpu=require_physical_gpu,
        )
        self.native = self.memory.native
        self.abi = Pass219Lane5RecursiveCompositionGraphBridge()

    def __enter__(self) -> "Pass219Lane5RecursiveHash216CompositionGraph":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self.memory.close()

    def status(self) -> dict[str, Any]:
        memory = self.memory.status()
        records = [record for record in self.memory.records() if not record.quarantined]
        vertices = {record.parent_hash216 for record in records} | {
            record.child_hash216 for record in records
        }
        return {
            "schema": SCHEMA,
            "authority": self.abi.authority(),
            "persistent_memory": memory,
            "active_edges": len(records),
            "active_vertices": len(vertices),
            "full_cycle": CYCLE,
            "quarter_cycle": QUARTER,
            "persistent_composition_graph": True,
            "recursive_multi_hop_search": True,
            "exact_hash216_adjacency_required": True,
            "hash216_path_seal_required": True,
            "gpu_vector_frontier_ranking": True,
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "gpu_may_commit_hash72": False,
            "gpu_may_commit_hash216": False,
            "canonical_persistence_authority": False,
            "requires_signed_environmental_vm81_admission": True,
        }

    def _records_by_parent(
        self,
        *,
        layer_index: int | None,
    ) -> dict[str, list[PersistentHash216CompositionRecord]]:
        result: dict[str, list[PersistentHash216CompositionRecord]] = {}
        for record in self.memory.records():
            if record.quarantined:
                continue
            if layer_index is not None and record.layer_index != int(layer_index):
                continue
            result.setdefault(record.parent_hash216, []).append(record)
        for records in result.values():
            records.sort(key=lambda item: (item.child_hash216, -item.jump_span, item.jump_id))
        return result

    @staticmethod
    def _dedupe_children(
        records: Sequence[PersistentHash216CompositionRecord],
    ) -> list[PersistentHash216CompositionRecord]:
        selected: dict[str, PersistentHash216CompositionRecord] = {}
        for record in records:
            prior = selected.get(record.child_hash216)
            if prior is None or (-record.jump_span, record.jump_id) < (-prior.jump_span, prior.jump_id):
                selected[record.child_hash216] = record
        return sorted(selected.values(), key=lambda item: (item.child_hash216, item.jump_id))

    def _rank_outgoing(
        self,
        *,
        goal_hash216: str,
        records: Sequence[PersistentHash216CompositionRecord],
        tick: int,
        cycle_index: int,
        top_k: int,
    ) -> list[tuple[PersistentHash216CompositionRecord, dict[str, Any]]]:
        unique = self._dedupe_children(records)
        if not unique:
            return []
        candidates = [
            Hash216CompositionCandidate(
                candidate_id=record.jump_id,
                hash216=record.child_hash216,
                validated=True,
                jump_span=record.jump_span,
                lineage_signature=record.composition_hash216,
            )
            for record in unique
        ]
        ranking = self.memory.jump_store.optimizer.search_hash216(
            query_hash216=goal_hash216,
            candidates=candidates,
            tick=int(tick),
            cycle_index=int(cycle_index),
            top_k=max(1, min(int(top_k), len(candidates))),
        )
        by_id = {record.jump_id: record for record in unique}
        return [(by_id[item["candidate_id"]], item) for item in ranking["ranked"]]

    def _path_material(
        self,
        *,
        start_hash216: str,
        goal_hash216: str,
        terminal_hash216: str,
        records: Sequence[PersistentHash216CompositionRecord],
        phase_slot: int,
        cycle_index: int,
    ) -> tuple[str, str]:
        edges = [
            {
                "jump_id": record.jump_id,
                "parent_hash216": record.parent_hash216,
                "child_hash216": record.child_hash216,
                "composition_hash216": record.composition_hash216,
                "metadata_hash216": record.metadata_hash216,
                "jump_span": record.jump_span,
                "layer_index": record.layer_index,
            }
            for record in records
        ]
        lineage_bytes = _canonical(edges)
        ordered_lineage_identity = sha256(
            b"HHS-P219-LANE5-ORDERED-COMPOSITION-LINEAGE-1.40\0" + lineage_bytes
        ).hexdigest()
        payload = {
            "schema": "HHS_PASS_219_LANE5_RECURSIVE_COMPOSITION_PATH_SEAL_1_40",
            "start_hash216": start_hash216,
            "goal_hash216": goal_hash216,
            "terminal_hash216": terminal_hash216,
            "cycle_index": int(cycle_index),
            "phase_slot": int(phase_slot),
            "ordered_edges": edges,
        }
        path_hash216 = self.native.hash216_bytes(_canonical(payload))
        return path_hash216, ordered_lineage_identity

    def _seal_path(
        self,
        *,
        start_hash216: str,
        goal_hash216: str,
        terminal_hash216: str,
        records: Sequence[PersistentHash216CompositionRecord],
        tick: int,
        cycle_index: int,
    ) -> tuple[RecursiveCompositionPath, dict[str, Any]]:
        if not records:
            raise ValueError("recursive composition path must contain at least one persistent edge")
        if records[0].parent_hash216 != start_hash216:
            raise ValueError("recursive composition path start does not match first edge parent")
        visited = {start_hash216}
        prior = start_hash216
        for record in records:
            if record.parent_hash216 != prior:
                raise ValueError("recursive composition path exact Hash216 adjacency failure")
            if record.child_hash216 in visited:
                raise ValueError("recursive composition path revisits a Hash216 vertex")
            visited.add(record.child_hash216)
            prior = record.child_hash216
        if prior != terminal_hash216:
            raise ValueError("recursive composition terminal does not match final edge child")
        phase_slot = int(tick) % CYCLE
        effective_cycle = int(cycle_index) + int(tick) // CYCLE
        path_hash216, lineage = self._path_material(
            start_hash216=start_hash216,
            goal_hash216=goal_hash216,
            terminal_hash216=terminal_hash216,
            records=records,
            phase_slot=phase_slot,
            cycle_index=effective_cycle,
        )
        total_span = sum(record.jump_span for record in records)
        receipt = self.abi.validate_path(
            start_hash216=start_hash216,
            goal_hash216=goal_hash216,
            terminal_hash216=terminal_hash216,
            path_hash216=path_hash216,
            ordered_lineage_identity=lineage,
            hop_count=len(records),
            total_span=total_span,
            phase_slot=phase_slot,
            cycle_index=effective_cycle,
        )
        if not receipt["accepted"] or receipt["canonical_mutation_authority"]:
            raise RuntimeError("native recursive composition graph membrane rejected candidate route")
        path = RecursiveCompositionPath(
            start_hash216=start_hash216,
            goal_hash216=goal_hash216,
            terminal_hash216=terminal_hash216,
            jump_ids=tuple(record.jump_id for record in records),
            edge_composition_hash216=tuple(record.composition_hash216 for record in records),
            edge_metadata_hash216=tuple(record.metadata_hash216 for record in records),
            total_span=total_span,
            phase_slot=phase_slot,
            cycle_index=effective_cycle,
            path_hash216=path_hash216,
            ordered_lineage_identity=lineage,
            exact_target=terminal_hash216 == goal_hash216,
        )
        return path, receipt

    @staticmethod
    def _path_dict(path: RecursiveCompositionPath) -> dict[str, Any]:
        return {
            "start_hash216": path.start_hash216,
            "goal_hash216": path.goal_hash216,
            "terminal_hash216": path.terminal_hash216,
            "jump_ids": list(path.jump_ids),
            "edge_composition_hash216": list(path.edge_composition_hash216),
            "edge_metadata_hash216": list(path.edge_metadata_hash216),
            "hop_count": len(path.jump_ids),
            "total_span": path.total_span,
            "phase_slot": path.phase_slot,
            "cycle_index": path.cycle_index,
            "path_hash216": path.path_hash216,
            "ordered_lineage_identity": path.ordered_lineage_identity,
            "exact_target": path.exact_target,
        }

    def reuse_path(
        self,
        *,
        current_state: Sequence[int],
        jump_ids: Sequence[str],
        goal_hash216: str,
        tick: int,
        cycle_index: int,
    ) -> dict[str, Any]:
        split_hash216(goal_hash216)
        if not jump_ids:
            raise ValueError("recursive composition reuse requires at least one jump")
        start_state = tuple(int(value) for value in current_state)
        start_hash216 = self.native.state_root(start_state)
        current = start_state
        current_hash216 = start_hash216
        visited = {start_hash216}
        records_by_id = {record.jump_id: record for record in self.memory.records()}
        traversed: list[PersistentHash216CompositionRecord] = []
        edge_receipts: list[dict[str, Any]] = []
        for jump_id in jump_ids:
            try:
                record = records_by_id[str(jump_id)]
            except KeyError as exc:
                raise KeyError(f"unknown recursive composition edge: {jump_id}") from exc
            if record.quarantined:
                raise ValueError("recursive composition edge is quarantined")
            if record.parent_hash216 != current_hash216:
                raise ValueError("recursive composition exact Hash216 adjacency failure")
            if record.child_hash216 in visited:
                raise ValueError("recursive composition path revisits a Hash216 vertex")
            reused = self.memory.reuse(current_state=current, jump_id=record.jump_id)
            child_state = tuple(int(value) for value in reused["child_state"])
            child_hash216 = self.native.state_root(child_state)
            if child_hash216 != record.child_hash216:
                raise RuntimeError("recursive composition persistent child Hash216 mismatch")
            if int(reused["intermediate_transitions_executed_on_reuse"]) != 0:
                raise RuntimeError("persistent edge unexpectedly executed represented transitions")
            traversed.append(record)
            edge_receipts.append(reused)
            visited.add(child_hash216)
            current = child_state
            current_hash216 = child_hash216
        path, native_receipt = self._seal_path(
            start_hash216=start_hash216,
            goal_hash216=goal_hash216,
            terminal_hash216=current_hash216,
            records=traversed,
            tick=tick,
            cycle_index=cycle_index,
        )
        return {
            "schema": "HHS_PASS_219_LANE5_RECURSIVE_COMPOSITION_REUSE_1_40",
            "path": self._path_dict(path),
            "terminal_state": list(current),
            "edge_retrievals": len(traversed),
            "represented_transitions": path.total_span,
            "intermediate_vm81_transitions_executed": 0,
            "edge_receipts": edge_receipts,
            "native_path_receipt": native_receipt,
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "gpu_may_commit_hash72": False,
            "gpu_may_commit_hash216": False,
            "canonical_persistence_authority": False,
            "requires_signed_environmental_vm81_admission": True,
        }

    def search(
        self,
        *,
        current_state: Sequence[int],
        goal_hash216: str,
        tick: int,
        cycle_index: int,
        max_hops: int = 8,
        beam_width: int = 16,
        layer_index: int | None = None,
    ) -> dict[str, Any]:
        split_hash216(goal_hash216)
        if int(tick) < 0 or int(cycle_index) < 0:
            raise ValueError("tick and cycle_index must be nonnegative")
        if int(max_hops) < 1 or int(beam_width) < 1:
            raise ValueError("max_hops and beam_width must be positive")
        start_state = tuple(int(value) for value in current_state)
        start_hash216 = self.native.state_root(start_state)
        by_parent = self._records_by_parent(layer_index=layer_index)
        frontier = [
            _Frontier(
                state=start_state,
                node_hash216=start_hash216,
                jump_ids=(),
                records=(),
                visited=(start_hash216,),
                total_span=0,
                distance=1 << 62,
            )
        ]
        best: _Frontier | None = None
        expanded_edges = 0
        authenticated_edge_retrievals = 0

        for depth in range(1, int(max_hops) + 1):
            next_frontier: list[_Frontier] = []
            absolute_tick = int(tick) + depth - 1
            local_tick = absolute_tick % CYCLE
            local_cycle = int(cycle_index) + absolute_tick // CYCLE
            for node in frontier:
                outgoing = by_parent.get(node.node_hash216, [])
                ranked = self._rank_outgoing(
                    goal_hash216=goal_hash216,
                    records=outgoing,
                    tick=local_tick,
                    cycle_index=local_cycle,
                    top_k=int(beam_width),
                )
                for record, rank in ranked:
                    expanded_edges += 1
                    if record.child_hash216 in node.visited:
                        continue
                    reused = self.memory.reuse(current_state=node.state, jump_id=record.jump_id)
                    authenticated_edge_retrievals += 1
                    child_state = tuple(int(value) for value in reused["child_state"])
                    child_hash216 = self.native.state_root(child_state)
                    if child_hash216 != record.child_hash216:
                        raise RuntimeError("recursive graph expansion child Hash216 mismatch")
                    candidate = _Frontier(
                        state=child_state,
                        node_hash216=child_hash216,
                        jump_ids=node.jump_ids + (record.jump_id,),
                        records=node.records + (record,),
                        visited=node.visited + (child_hash216,),
                        total_span=node.total_span + record.jump_span,
                        distance=int(rank["hash216_distance"]),
                    )
                    next_frontier.append(candidate)
                    if best is None or (
                        candidate.distance,
                        len(candidate.jump_ids),
                        -candidate.total_span,
                        candidate.jump_ids,
                    ) < (
                        best.distance,
                        len(best.jump_ids),
                        -best.total_span,
                        best.jump_ids,
                    ):
                        best = candidate
            if not next_frontier:
                break
            exact = [item for item in next_frontier if item.node_hash216 == goal_hash216]
            if exact:
                exact.sort(key=lambda item: (-item.total_span, item.jump_ids))
                best = exact[0]
                break
            next_frontier.sort(
                key=lambda item: (
                    item.distance,
                    -item.total_span,
                    item.node_hash216,
                    item.jump_ids,
                )
            )
            frontier = next_frontier[: int(beam_width)]

        if best is None:
            return {
                "schema": SCHEMA,
                "start_hash216": start_hash216,
                "goal_hash216": goal_hash216,
                "found": False,
                "exact_target": False,
                "expanded_edges": expanded_edges,
                "authenticated_edge_retrievals": authenticated_edge_retrievals,
                "candidate_only": True,
            }

        path, native_receipt = self._seal_path(
            start_hash216=start_hash216,
            goal_hash216=goal_hash216,
            terminal_hash216=best.node_hash216,
            records=best.records,
            tick=tick,
            cycle_index=cycle_index,
        )
        return {
            "schema": SCHEMA,
            "start_hash216": start_hash216,
            "goal_hash216": goal_hash216,
            "found": True,
            "exact_target": path.exact_target,
            "path": self._path_dict(path),
            "terminal_state": list(best.state),
            "expanded_edges": expanded_edges,
            "authenticated_edge_retrievals": authenticated_edge_retrievals,
            "represented_transitions": path.total_span,
            "intermediate_vm81_transitions_executed": 0,
            "native_path_receipt": native_receipt,
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "gpu_may_commit_hash72": False,
            "gpu_may_commit_hash216": False,
            "canonical_persistence_authority": False,
            "requires_signed_environmental_vm81_admission": True,
        }


__all__ = [
    "RecursiveCompositionPath",
    "Pass219Lane5RecursiveHash216CompositionGraph",
]

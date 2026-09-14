"""Lane 5 validated Hash216 composition-jump vector store, Pass 219 1.38.

Registration performs exact sequential Pass 205 replay once and seals the ordered
Hash216 transition trace. Reuse is direct candidate retrieval from the validated
read-only store: it verifies the parent identity, child identity, immutable
composition seal, and native 1.38 descriptor without replaying each intermediate
transition. Reused states remain candidate-only and cannot bypass signed VM81
admission or acquire canonical Hash72/Hash216 authority.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass219_lane5_hash216_gpu_phase_interlace_1_37 import (
    Hash216CompositionCandidate,
    Pass219Lane5Hash216GPUPhaseInterlaceOptimizer,
)
from hhs_python.runtime.hhs_pass205_continuation_bridge import (
    CELL_COUNT,
    Pass205NativeBridge,
)
from hhs_python.runtime.hhs_pass219_lane5_composition_jump_bridge import (
    CYCLE,
    Pass219Lane5CompositionJumpBridge,
)

SCHEMA = "HHS_PASS_219_LANE5_HASH216_COMPOSITION_JUMP_STORE_1_38"

EventTriple = tuple[int, int, int]
StepEvents = tuple[EventTriple, ...]
TraceRoots = tuple[tuple[str, str, str, str], ...]


@dataclass(frozen=True)
class ValidatedHash216CompositionJump:
    jump_id: str
    parent_hash216: str
    child_hash216: str
    composition_hash216: str
    jump_span: int
    cycle_index: int
    layer_index: int
    phase_slot: int
    steps: tuple[StepEvents, ...]
    trace_roots: TraceRoots
    child_state: tuple[int, ...]
    validated: bool = True
    candidate_only: bool = True


def _canonical_event(event: Mapping[str, int] | Sequence[int]) -> EventTriple:
    if isinstance(event, Mapping):
        triple = (int(event["cell"]), int(event["control_g"]), int(event["xor_mask"]))
    else:
        if len(event) != 3:
            raise ValueError("composition event sequence must contain cell, control_g, xor_mask")
        triple = tuple(int(value) for value in event)  # type: ignore[assignment]
    cell, control, mask = triple
    if not (0 <= cell < CELL_COUNT):
        raise ValueError("composition event cell outside VM81")
    if not (0 <= control < 243):
        raise ValueError("composition event control_g outside G243")
    if not (0 < mask < (1 << 64)):
        raise ValueError("composition event xor_mask outside nonzero uint64")
    return cell, control, mask


def _event_mapping(event: EventTriple) -> dict[str, int]:
    return {"cell": event[0], "control_g": event[1], "xor_mask": event[2]}


def _seal_payload(
    *,
    parent_hash216: str,
    child_hash216: str,
    jump_span: int,
    cycle_index: int,
    layer_index: int,
    phase_slot: int,
    trace_roots: TraceRoots,
) -> bytes:
    pieces = [
        "HHS-P219-LANE5-COMPOSITION-JUMP-1.38",
        parent_hash216,
        child_hash216,
        str(int(jump_span)),
        str(int(cycle_index)),
        str(int(layer_index)),
        str(int(phase_slot)),
    ]
    for ordinal, roots in enumerate(trace_roots):
        pieces.append(str(ordinal))
        pieces.extend(roots)
    return "\n".join(pieces).encode("ascii")


class Pass219Lane5Hash216CompositionJumpStore:
    """Validated read-only jump cache bound to the 1.37 GPU/vector search fabric."""

    def __init__(
        self,
        *,
        backend: str = "CPU_REFERENCE",
        require_physical_gpu: bool = False,
    ) -> None:
        self.native = Pass205NativeBridge()
        self.optimizer = Pass219Lane5Hash216GPUPhaseInterlaceOptimizer(
            backend=backend,
            require_physical_gpu=require_physical_gpu,
        )
        self.abi = Pass219Lane5CompositionJumpBridge()
        self._by_id: dict[str, ValidatedHash216CompositionJump] = {}
        self._by_parent: dict[str, list[str]] = {}

    def close(self) -> None:
        self.optimizer.close()

    def __enter__(self) -> "Pass219Lane5Hash216CompositionJumpStore":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def status(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "authority": self.abi.authority(),
            "optimizer": self.optimizer.status(),
            "stored_jump_count": len(self._by_id),
            "validated_hash216_jump_store": True,
            "exact_registration_replay_required": True,
            "direct_candidate_reuse_allowed": True,
            "full_cycle": CYCLE,
            "candidate_only": True,
            "gpu_may_commit_hash72": False,
            "gpu_may_commit_hash216": False,
            "canonical_vm81_mutation_authority": False,
            "requires_signed_environmental_vm81_admission": True,
        }

    def _composition_seal(
        self,
        *,
        parent_hash216: str,
        child_hash216: str,
        jump_span: int,
        cycle_index: int,
        layer_index: int,
        phase_slot: int,
        trace_roots: TraceRoots,
    ) -> str:
        return self.native.hash216_bytes(
            _seal_payload(
                parent_hash216=parent_hash216,
                child_hash216=child_hash216,
                jump_span=jump_span,
                cycle_index=cycle_index,
                layer_index=layer_index,
                phase_slot=phase_slot,
                trace_roots=trace_roots,
            )
        )

    def build_validated_jump(
        self,
        *,
        jump_id: str,
        parent_state: Sequence[int],
        steps: Sequence[Sequence[Mapping[str, int] | Sequence[int]]],
        tick: int,
        cycle_index: int,
        layer_index: int = 0,
    ) -> ValidatedHash216CompositionJump:
        if not jump_id:
            raise ValueError("jump_id must be nonempty")
        if len(parent_state) != CELL_COUNT:
            raise ValueError(f"parent_state must contain exactly {CELL_COUNT} words")
        if len(steps) < 2:
            raise ValueError("composition jump must represent at least two exact transitions")
        if min(int(tick), int(cycle_index), int(layer_index)) < 0:
            raise ValueError("tick, cycle_index, and layer_index must be nonnegative")

        canonical_steps = tuple(
            tuple(_canonical_event(event) for event in step)
            for step in steps
        )
        if any(not step for step in canonical_steps):
            raise ValueError("composition steps must be nonempty")

        current = [int(value) for value in parent_state]
        parent_hash216 = self.native.state_root(current)
        trace: list[tuple[str, str, str, str]] = []
        for step in canonical_steps:
            events = [_event_mapping(event) for event in step]
            child, frontier_bits, _, _ = self.native.apply_delta(current, events)
            frontier = [index for index, enabled in enumerate(frontier_bits) if enabled]
            if not self.native.validate_frontier(events, frontier):
                raise RuntimeError("exact Pass 205 frontier validation failed during jump registration")
            trace.append(
                (
                    self.native.delta_root(events),
                    self.native.hydration_root(events),
                    self.native.frontier_root(frontier),
                    self.native.state_root(child),
                )
            )
            current = child

        child_hash216 = self.native.state_root(current)
        phase_slot = int(tick) % CYCLE
        trace_roots = tuple(trace)
        composition_hash216 = self._composition_seal(
            parent_hash216=parent_hash216,
            child_hash216=child_hash216,
            jump_span=len(canonical_steps),
            cycle_index=int(cycle_index),
            layer_index=int(layer_index),
            phase_slot=phase_slot,
            trace_roots=trace_roots,
        )
        jump = ValidatedHash216CompositionJump(
            jump_id=jump_id,
            parent_hash216=parent_hash216,
            child_hash216=child_hash216,
            composition_hash216=composition_hash216,
            jump_span=len(canonical_steps),
            cycle_index=int(cycle_index),
            layer_index=int(layer_index),
            phase_slot=phase_slot,
            steps=canonical_steps,
            trace_roots=trace_roots,
            child_state=tuple(current),
        )
        self._validate_record(jump)
        return jump

    def _validate_record(self, jump: ValidatedHash216CompositionJump) -> dict[str, Any]:
        if not jump.validated or not jump.candidate_only:
            raise ValueError("composition jump must be validated and candidate-only")
        if jump.jump_span != len(jump.steps) or jump.jump_span != len(jump.trace_roots):
            raise ValueError("composition jump span/trace mismatch")
        if self.native.state_root(jump.child_state) != jump.child_hash216:
            raise ValueError("composition jump child state/root mismatch")
        expected = self._composition_seal(
            parent_hash216=jump.parent_hash216,
            child_hash216=jump.child_hash216,
            jump_span=jump.jump_span,
            cycle_index=jump.cycle_index,
            layer_index=jump.layer_index,
            phase_slot=jump.phase_slot,
            trace_roots=jump.trace_roots,
        )
        if expected != jump.composition_hash216:
            raise ValueError("composition jump immutable Hash216 seal mismatch")
        receipt = self.abi.validate_descriptor(
            parent_hash216=jump.parent_hash216,
            child_hash216=jump.child_hash216,
            composition_hash216=jump.composition_hash216,
            jump_span=jump.jump_span,
            phase_slot=jump.phase_slot,
            cycle_index=jump.cycle_index,
            layer_index=jump.layer_index,
        )
        if not receipt["accepted"] or receipt["canonical_mutation_authority"]:
            raise RuntimeError("native composition-jump membrane rejected candidate authority boundary")
        return receipt

    def insert(self, jump: ValidatedHash216CompositionJump) -> dict[str, Any]:
        if jump.jump_id in self._by_id:
            raise ValueError(f"duplicate composition jump id: {jump.jump_id}")
        if any(existing.composition_hash216 == jump.composition_hash216 for existing in self._by_id.values()):
            raise ValueError("duplicate composition Hash216 seal")
        receipt = self._validate_record(jump)
        self._by_id[jump.jump_id] = jump
        self._by_parent.setdefault(jump.parent_hash216, []).append(jump.jump_id)
        return receipt

    def verify_jump_replay(
        self,
        *,
        parent_state: Sequence[int],
        jump: ValidatedHash216CompositionJump,
    ) -> bool:
        if self.native.state_root(parent_state) != jump.parent_hash216:
            return False
        current = [int(value) for value in parent_state]
        roots: list[tuple[str, str, str, str]] = []
        for step in jump.steps:
            events = [_event_mapping(event) for event in step]
            child, frontier_bits, _, _ = self.native.apply_delta(current, events)
            frontier = [index for index, enabled in enumerate(frontier_bits) if enabled]
            roots.append(
                (
                    self.native.delta_root(events),
                    self.native.hydration_root(events),
                    self.native.frontier_root(frontier),
                    self.native.state_root(child),
                )
            )
            current = child
        return (
            tuple(current) == jump.child_state
            and self.native.state_root(current) == jump.child_hash216
            and tuple(roots) == jump.trace_roots
            and self._composition_seal(
                parent_hash216=jump.parent_hash216,
                child_hash216=jump.child_hash216,
                jump_span=jump.jump_span,
                cycle_index=jump.cycle_index,
                layer_index=jump.layer_index,
                phase_slot=jump.phase_slot,
                trace_roots=tuple(roots),
            ) == jump.composition_hash216
        )

    def search(
        self,
        *,
        current_state: Sequence[int],
        goal_hash216: str,
        tick: int,
        cycle_index: int,
        layer_index: int | None = None,
        top_k: int = 32,
    ) -> dict[str, Any]:
        parent_hash216 = self.native.state_root(current_state)
        jump_ids = self._by_parent.get(parent_hash216, [])
        jumps = [self._by_id[jump_id] for jump_id in jump_ids]
        if layer_index is not None:
            jumps = [jump for jump in jumps if jump.layer_index == int(layer_index)]
        candidates = [
            Hash216CompositionCandidate(
                candidate_id=jump.jump_id,
                hash216=jump.child_hash216,
                validated=True,
                jump_span=jump.jump_span,
                lineage_signature=jump.composition_hash216,
            )
            for jump in jumps
        ]
        result = self.optimizer.search_hash216(
            query_hash216=goal_hash216,
            candidates=candidates,
            tick=tick,
            cycle_index=cycle_index,
            top_k=top_k,
        )
        result["composition_jump_store"] = True
        result["parent_hash216"] = parent_hash216
        result["direct_candidate_reuse_allowed"] = True
        return result

    def reuse(
        self,
        *,
        current_state: Sequence[int],
        jump_id: str,
    ) -> dict[str, Any]:
        try:
            jump = self._by_id[jump_id]
        except KeyError as exc:
            raise KeyError(f"unknown composition jump: {jump_id}") from exc
        current_root = self.native.state_root(current_state)
        if current_root != jump.parent_hash216:
            raise ValueError("composition jump parent does not match current canonical state identity")
        receipt = self._validate_record(jump)
        return {
            "schema": "HHS_PASS_219_LANE5_COMPOSITION_JUMP_REUSE_1_38",
            "jump_id": jump.jump_id,
            "parent_hash216": jump.parent_hash216,
            "child_hash216": jump.child_hash216,
            "composition_hash216": jump.composition_hash216,
            "child_state": list(jump.child_state),
            "jump_span": jump.jump_span,
            "represented_transitions": jump.jump_span,
            "intermediate_transitions_executed_on_reuse": 0,
            "phase_slot": jump.phase_slot,
            "cycle_index": jump.cycle_index,
            "layer_index": jump.layer_index,
            "native_receipt": receipt,
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "gpu_may_commit_hash72": False,
            "gpu_may_commit_hash216": False,
            "requires_signed_environmental_vm81_admission": True,
        }

    def benchmark_reuse(
        self,
        *,
        current_state: Sequence[int],
        jump_id: str,
        repetitions: int,
    ) -> dict[str, int | str | bool]:
        if int(repetitions) <= 0:
            raise ValueError("repetitions must be positive")
        jump = self._by_id[jump_id]
        for _ in range(int(repetitions)):
            self.reuse(current_state=current_state, jump_id=jump_id)
        represented = jump.jump_span * int(repetitions)
        return {
            "schema": "HHS_PASS_219_LANE5_COMPOSITION_JUMP_WORK_COMPRESSION_1_38",
            "repetitions": int(repetitions),
            "jump_span": jump.jump_span,
            "represented_transitions": represented,
            "intermediate_transitions_executed_on_reuse": 0,
            "candidate_reuse_validations": int(repetitions),
            "candidate_only": True,
        }


__all__ = [
    "ValidatedHash216CompositionJump",
    "Pass219Lane5Hash216CompositionJumpStore",
    "replace",
]

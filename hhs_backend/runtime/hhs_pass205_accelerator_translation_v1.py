"""Deterministic accelerator translation layer for Pass 205.

This module packs canonical VM5184 state, 32-channel projections, ordered
continuation deltas, and q-address hydration frontiers into fixed-width SoA/CSR
buffers suitable for CUDA, HIP, Vulkan Compute, WebGPU, or Metal dispatch.
It includes a CPU reference executor used as the equality oracle. No floating
point field participates in canonical state, dispatch, reduction, or replay.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from hhs_python.runtime.hhs_pass205_continuation_bridge import (
    BITS_PER_CELL,
    CELL_COUNT,
    CONTROL_COUNT,
    PROJECTION_CHANNELS,
    UINT64_MASK,
    Pass205NativeBridge,
)

SCHEMA = "HHS_PASS_205_ACCELERATOR_TRANSLATION_V1"
BACKENDS = ("CPU_REFERENCE", "CUDA", "HIP", "VULKAN_COMPUTE", "WEBGPU", "METAL")


@dataclass(frozen=True)
class AcceleratorBatch:
    state_soa: list[list[int]]
    projection_soa: list[list[list[int]]]
    delta_offsets: list[int]
    delta_cells: list[int]
    delta_controls: list[int]
    delta_xor_masks: list[int]
    hydration_offsets: list[int]
    hydration_q: list[int]
    batch_size: int
    transfer_bytes: int
    dense_transfer_bytes: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "state_layout": "uint64 SoA[cell][batch]",
            "projection_layout": "uint32 SoA[channel][cell][batch]",
            "delta_layout": "CSR offsets + uint32 cell + uint8 control_g + uint64 XOR mask",
            "hydration_layout": "CSR offsets + uint32 q",
            "state_soa": self.state_soa,
            "projection_soa": self.projection_soa,
            "delta_offsets": self.delta_offsets,
            "delta_cells": self.delta_cells,
            "delta_controls": self.delta_controls,
            "delta_xor_masks": self.delta_xor_masks,
            "hydration_offsets": self.hydration_offsets,
            "hydration_q": self.hydration_q,
            "batch_size": self.batch_size,
            "transfer_bytes": self.transfer_bytes,
            "dense_transfer_bytes": self.dense_transfer_bytes,
            "transfer_reduction_ratio": (
                self.dense_transfer_bytes / self.transfer_bytes if self.transfer_bytes else 1
            ),
            "canonical_float_fields": 0,
        }


def _validate_state(words: Sequence[int]) -> list[int]:
    if len(words) != CELL_COUNT:
        raise ValueError(f"state must contain {CELL_COUNT} uint64 words")
    result = [int(value) for value in words]
    if any(value < 0 or value > UINT64_MASK for value in result):
        raise ValueError("state word outside uint64")
    return result


def _validate_projection(projection: Sequence[Sequence[int]]) -> list[list[int]]:
    if len(projection) != PROJECTION_CHANNELS:
        raise ValueError(f"projection must contain {PROJECTION_CHANNELS} channels")
    result: list[list[int]] = []
    for row in projection:
        if len(row) != CELL_COUNT:
            raise ValueError(f"projection channel must contain {CELL_COUNT} cells")
        values = [int(value) for value in row]
        if any(value < 0 or value > 0xFFFFFFFF for value in values):
            raise ValueError("projection word outside uint32")
        result.append(values)
    return result


def _validate_events(events: Sequence[Mapping[str, int]]) -> list[dict[str, int]]:
    result: list[dict[str, int]] = []
    seen: set[int] = set()
    for event in events:
        cell = int(event["cell"])
        control = int(event["control_g"])
        mask = int(event["xor_mask"])
        if cell < 0 or cell >= CELL_COUNT or cell in seen:
            raise ValueError("invalid or duplicate delta cell")
        if control < 0 or control >= CONTROL_COUNT:
            raise ValueError("invalid control_g")
        if mask <= 0 or mask > UINT64_MASK:
            raise ValueError("invalid xor mask")
        seen.add(cell)
        result.append({"cell": cell, "control_g": control, "xor_mask": mask})
    return result


class Pass205AcceleratorTranslation:
    def __init__(self) -> None:
        self.native = Pass205NativeBridge()

    def pack_batch(
        self,
        *,
        states: Sequence[Sequence[int]],
        projections: Sequence[Sequence[Sequence[int]]],
        deltas: Sequence[Sequence[Mapping[str, int]]],
    ) -> AcceleratorBatch:
        if not (len(states) == len(projections) == len(deltas)):
            raise ValueError("states, projections, and deltas must have equal batch size")
        batch_size = len(states)
        canonical_states = [_validate_state(state) for state in states]
        canonical_projections = [_validate_projection(value) for value in projections]
        canonical_deltas = [_validate_events(value) for value in deltas]

        state_soa = [
            [canonical_states[batch][cell] for batch in range(batch_size)]
            for cell in range(CELL_COUNT)
        ]
        projection_soa = [
            [
                [canonical_projections[batch][channel][cell] for batch in range(batch_size)]
                for cell in range(CELL_COUNT)
            ]
            for channel in range(PROJECTION_CHANNELS)
        ]

        delta_offsets = [0]
        delta_cells: list[int] = []
        delta_controls: list[int] = []
        delta_xor_masks: list[int] = []
        hydration_offsets = [0]
        hydration_q: list[int] = []
        for events in canonical_deltas:
            for event in events:
                delta_cells.append(event["cell"])
                delta_controls.append(event["control_g"])
                delta_xor_masks.append(event["xor_mask"])
                for bit in range(BITS_PER_CELL):
                    if event["xor_mask"] & (1 << bit):
                        s = event["cell"] * BITS_PER_CELL + bit
                        hydration_q.append(self.native.q_address(s, event["control_g"]))
            delta_offsets.append(len(delta_cells))
            hydration_offsets.append(len(hydration_q))

        transfer_bytes = (
            CELL_COUNT * batch_size * 8
            + PROJECTION_CHANNELS * CELL_COUNT * batch_size * 4
            + len(delta_offsets) * 4
            + len(delta_cells) * 4
            + len(delta_controls)
            + len(delta_xor_masks) * 8
            + len(hydration_offsets) * 4
            + len(hydration_q) * 4
        )
        dense_transfer_bytes = batch_size * (
            CELL_COUNT * 8
            + PROJECTION_CHANNELS * CELL_COUNT * 4
            + CELL_COUNT * (4 + 1 + 8)
            + CELL_COUNT * BITS_PER_CELL * 4
        )
        return AcceleratorBatch(
            state_soa=state_soa,
            projection_soa=projection_soa,
            delta_offsets=delta_offsets,
            delta_cells=delta_cells,
            delta_controls=delta_controls,
            delta_xor_masks=delta_xor_masks,
            hydration_offsets=hydration_offsets,
            hydration_q=hydration_q,
            batch_size=batch_size,
            transfer_bytes=transfer_bytes,
            dense_transfer_bytes=dense_transfer_bytes,
        )

    @staticmethod
    def unpack_states(state_soa: Sequence[Sequence[int]], batch_size: int) -> list[list[int]]:
        if len(state_soa) != CELL_COUNT:
            raise ValueError("state SoA cell dimension mismatch")
        return [
            [int(state_soa[cell][batch]) for cell in range(CELL_COUNT)]
            for batch in range(batch_size)
        ]

    @staticmethod
    def unpack_projections(
        projection_soa: Sequence[Sequence[Sequence[int]]], batch_size: int
    ) -> list[list[list[int]]]:
        if len(projection_soa) != PROJECTION_CHANNELS:
            raise ValueError("projection SoA channel dimension mismatch")
        return [
            [
                [int(projection_soa[channel][cell][batch]) for cell in range(CELL_COUNT)]
                for channel in range(PROJECTION_CHANNELS)
            ]
            for batch in range(batch_size)
        ]

    def execute_cpu_reference(self, batch: AcceleratorBatch) -> dict[str, Any]:
        parent_states = self.unpack_states(batch.state_soa, batch.batch_size)
        parent_projections = self.unpack_projections(batch.projection_soa, batch.batch_size)
        child_states: list[list[int]] = []
        child_projections: list[list[list[int]]] = []
        continuation_frontiers: list[list[int]] = []
        for batch_index in range(batch.batch_size):
            start = batch.delta_offsets[batch_index]
            end = batch.delta_offsets[batch_index + 1]
            events = [
                {
                    "cell": batch.delta_cells[index],
                    "control_g": batch.delta_controls[index],
                    "xor_mask": batch.delta_xor_masks[index],
                }
                for index in range(start, end)
            ]
            child, frontier_bits, _, _ = self.native.apply_delta(parent_states[batch_index], events)
            frontier = [index for index, enabled in enumerate(frontier_bits) if enabled]
            sparse = self.native.project_sparse(child, parent_projections[batch_index], frontier)
            full = self.native.project_full(child)
            if sparse != full:
                raise RuntimeError("accelerator CPU oracle sparse/full projection mismatch")
            child_states.append(child)
            child_projections.append(sparse)
            continuation_frontiers.append(frontier)
        return {
            "schema": "HHS_PASS_205_ACCELERATOR_CPU_REFERENCE_RESULT_V1",
            "ok": True,
            "batch_size": batch.batch_size,
            "child_states": child_states,
            "child_projections": child_projections,
            "frontiers": continuation_frontiers,
            "canonical_float_fields": 0,
        }

    @staticmethod
    def dispatch_descriptor(backend: str, batch: AcceleratorBatch) -> dict[str, Any]:
        selected = backend.upper()
        if selected not in BACKENDS:
            raise ValueError(f"unsupported Pass 205 accelerator backend: {backend}")
        return {
            "schema": "HHS_PASS_205_ACCELERATOR_DISPATCH_DESCRIPTOR_V1",
            "backend": selected,
            "batch_size": batch.batch_size,
            "workgroup_shape": [32, 1, 1],
            "state_word_type": "uint64",
            "projection_word_type": "uint32",
            "delta_cell_type": "uint32",
            "delta_control_type": "uint8",
            "delta_mask_type": "uint64",
            "hydration_address_type": "uint32",
            "deterministic_integer_only": True,
            "canonical_float_fields": 0,
            "requires_result_verification_against_hash216": True,
            "gpu_may_propose_candidate": True,
            "gpu_may_commit_hash72": False,
            "vm81_single_admission_authority": True,
        }


PASS205_ACCELERATOR_TRANSLATION = Pass205AcceleratorTranslation()

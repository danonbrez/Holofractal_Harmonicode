#!/usr/bin/env python3
"""Pass 205 exact GPU translation-layer design validation.

This validates accelerator buffer translation and deterministic scheduling on the
CPU. It does not claim that a physical GPU kernel was executed.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple

import pass205_multimodal_continuation_design_validation as hhs


def validate(seed: int = 216, batches: int = 256) -> Dict[str, object]:
    rng = random.Random(seed ^ 0x6A5055)
    parents: List[Tuple[int, ...]] = []
    children: List[Tuple[int, ...]] = []
    deltas: List[Tuple[Tuple[int, int], ...]] = []
    controls: List[int] = []
    dirty_sets: List[Tuple[int, ...]] = []
    projections: List[Tuple[Tuple[int, ...], ...]] = []
    features: List[Tuple[int, ...]] = []

    state = hhs.initial_state(seed)
    projection = hhs.build_projection(state)
    for _ in range(batches):
        events = tuple(
            hhs.Event(cell, rng.randrange(hhs.CONTROLS))
            for cell in rng.sample(range(hhs.CELLS), 4)
        )
        child, _, dirty = hhs.evolve_state(state, events, full_scan=False)
        child_projection = hhs.update_projection(projection, child, dirty)
        parents.append(state)
        children.append(child)
        deltas.append(hhs.delta_between(state, child))
        controls.append(events[0].control)
        dirty_sets.append(tuple(dirty))
        projections.append(child_projection)
        features.append(hhs.full_features(child))
        state = child
        projection = child_projection

    state_soa = bytearray()
    for cell in range(hhs.CELLS):
        for batch in range(batches):
            state_soa += children[batch][cell].to_bytes(8, "little")
    assert len(state_soa) == batches * hhs.CELLS * 8
    assert len(state_soa) % 8 == 0
    rebuilt_states: List[List[int]] = [[0] * hhs.CELLS for _ in range(batches)]
    cursor = 0
    for cell in range(hhs.CELLS):
        for batch in range(batches):
            rebuilt_states[batch][cell] = int.from_bytes(state_soa[cursor:cursor + 8], "little")
            cursor += 8
    assert all(tuple(rebuilt_states[i]) == children[i] for i in range(batches))

    frontier_offsets = [0]
    frontier_cells: List[int] = []
    frontier_masks: List[int] = []
    q_offsets = [0]
    q_values: List[int] = []
    for delta, control in zip(deltas, controls):
        for cell, mask in delta:
            frontier_cells.append(cell)
            frontier_masks.append(mask)
        frontier_offsets.append(len(frontier_cells))
        q_values.extend(hhs.hydration_addresses(delta, control))
        q_offsets.append(len(q_values))
    assert frontier_offsets[-1] == len(frontier_cells)
    assert q_offsets[-1] == len(q_values)
    assert all(0 <= q < hhs.HYDRATION_CAPACITY for q in q_values)

    for batch in range(batches):
        start, end = frontier_offsets[batch], frontier_offsets[batch + 1]
        pairs = list(zip(frontier_cells[start:end], frontier_masks[start:end]))
        for order in (pairs, list(reversed(pairs)), sorted(pairs)):
            assert hhs.apply_delta(parents[batch], order) == children[batch]

    projection_soa = bytearray()
    for channel in range(hhs.CHANNELS):
        for cell in range(hhs.CELLS):
            for batch in range(batches):
                projection_soa += projections[batch][cell][channel].to_bytes(4, "little")
    assert len(projection_soa) == batches * hhs.CELLS * hhs.CHANNELS * 4
    assert len(projection_soa) % 4 == 0
    rebuilt_projection = [
        [[0] * hhs.CHANNELS for _ in range(hhs.CELLS)]
        for _ in range(batches)
    ]
    cursor = 0
    for channel in range(hhs.CHANNELS):
        for cell in range(hhs.CELLS):
            for batch in range(batches):
                rebuilt_projection[batch][cell][channel] = int.from_bytes(
                    projection_soa[cursor:cursor + 4], "little"
                )
                cursor += 4
    assert all(
        tuple(tuple(row) for row in rebuilt_projection[i]) == projections[i]
        for i in range(batches)
    )

    reference = tuple(sum(feature[i] for feature in features) for i in range(16))
    partitions: List[Tuple[int, ...]] = []
    for start in range(0, batches, 17):
        chunk = features[start:start + 17]
        partitions.append(tuple(sum(feature[i] for feature in chunk) for i in range(16)))
    rng.shuffle(partitions)
    shuffled = tuple(sum(part[i] for part in partitions) for i in range(16))
    assert shuffled == reference

    dense_transfer = batches * (
        hhs.CELLS * 8 + hhs.CELLS * hhs.CHANNELS * 4
    )
    sparse_transfer = (
        (batches + 1) * 4
        + len(frontier_cells) * 12
        + (batches + 1) * 4
        + len(q_values) * 4
        + sum(len(dirty) for dirty in dirty_sets) * hhs.CHANNELS * 4
    )
    assert sparse_transfer < dense_transfer

    witness = hhs.h216(
        b"GPU-TRANSLATION",
        bytes(state_soa),
        bytes(projection_soa),
        b"".join(v.to_bytes(4, "little") for v in frontier_offsets),
        b"".join(v.to_bytes(4, "little") for v in frontier_cells),
        b"".join(v.to_bytes(8, "little") for v in frontier_masks),
        b"".join(v.to_bytes(4, "little") for v in q_offsets),
        b"".join(v.to_bytes(4, "little") for v in q_values),
    )
    return {
        "schema": "HHS_PASS_205_GPU_TRANSLATION_DESIGN_VALIDATION_V1",
        "classification": "HHS_PASS_205_GPU_TRANSLATION_DESIGN_VALIDATION_PASSED",
        "execution_scope": "translation and deterministic scheduling validated on CPU; no physical GPU claimed",
        "seed": seed,
        "batches": batches,
        "state_layout": "uint64 SoA[cell][batch]",
        "projection_layout": "uint32 SoA[channel][cell][batch]",
        "frontier_layout": "CSR offsets + uint32 cells + uint64 XOR masks",
        "hydration_layout": "CSR offsets + uint32 q addresses",
        "frontier_entries": len(frontier_cells),
        "hydration_entries": len(q_values),
        "dirty_projection_entries": sum(len(dirty) for dirty in dirty_sets),
        "dense_transfer_bytes": dense_transfer,
        "sparse_transfer_bytes": sparse_transfer,
        "transfer_reduction": dense_transfer / sparse_transfer,
        "mean_frontier_cells": len(frontier_cells) / batches,
        "mean_q_addresses": len(q_values) / batches,
        "translation_witness216": witness.hex(),
        "tests": {
            "gpu_state_soa_roundtrip": "PASS",
            "gpu_projection_soa_roundtrip": "PASS",
            "gpu_sparse_frontier_csr": "PASS",
            "gpu_schedule_independence": "PASS",
            "gpu_deterministic_ml_reduction": "PASS",
            "gpu_sparse_transfer_reduction": "PASS"
        }
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=216)
    parser.add_argument("--batches", type=int, default=256)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("PASS205_GPU_TRANSLATION_DESIGN_VALIDATION_RECEIPT.json")
    )
    args = parser.parse_args()
    result = validate(args.seed, args.batches)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

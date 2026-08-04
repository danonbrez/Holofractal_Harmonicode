"""Pass 207 VM81 GPU hyperthread runtime integration.

This layer binds the Pass 205 SoA/CSR accelerator translation to the additive
Pass 207 native driver. The GPU owns no canonical mutation authority: it may
calculate candidates in 5,184 stable logical lanes, but every physical result
must equal the exact CPU oracle before it can be presented to the singleton
VM81 admission path.
"""
from __future__ import annotations

import hashlib
import os
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass205_accelerator_translation_v1 import (
    AcceleratorBatch,
    Pass205AcceleratorTranslation,
)
from hhs_python.runtime.hhs_pass207_gpu_driver_bridge import (
    CELL_COUNT,
    LOGICAL_LANES,
    PROJECTION_CHANNELS,
    Pass207GPUDriver,
)

SCHEMA = "HHS_PASS_207_VM81_GPU_HYPERTHREAD_RUNTIME_V1"
CONTRACT = "HHS-P207-VM81-5184-GPU-HYPERTHREAD-DRIVER-VECTOR-BUFFER-CACHE-H72-H216"
HASH72_ALPHABET = (
    "0123456789"
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "-+*/()<>!?"
)
HASH72_INDEX = {symbol: index for index, symbol in enumerate(HASH72_ALPHABET)}


class Pass207GPURejected(RuntimeError):
    pass


def _fixed_key(*parts: bytes) -> bytes:
    digest = hashlib.sha256()
    for part in parts:
        digest.update(len(part).to_bytes(8, "little"))
        digest.update(part)
    return digest.digest()


def _u32_bytes(values: Sequence[int]) -> bytes:
    return b"".join(int(value).to_bytes(4, "little", signed=False) for value in values)


def _u64_bytes(values: Sequence[int]) -> bytes:
    return b"".join(int(value).to_bytes(8, "little", signed=False) for value in values)


def _u8_bytes(values: Sequence[int]) -> bytes:
    return bytes(int(value) for value in values)


def _flatten_state(batch: AcceleratorBatch) -> list[int]:
    return [int(value) for row in batch.state_soa for value in row]


def _flatten_projection(batch: AcceleratorBatch) -> list[int]:
    return [int(value) for channel in batch.projection_soa for row in channel for value in row]


def _batch_keys(batch: AcceleratorBatch) -> tuple[bytes, bytes]:
    input_key = _fixed_key(
        b"HHS_PASS207_INPUT_SOA_V1",
        _u64_bytes(_flatten_state(batch)),
        _u32_bytes(_flatten_projection(batch)),
    )
    output_key = _fixed_key(
        b"HHS_PASS207_OUTPUT_SOA_V1",
        input_key,
        _u32_bytes(batch.delta_offsets),
        _u32_bytes(batch.delta_cells),
        _u8_bytes(batch.delta_controls),
        _u64_bytes(batch.delta_xor_masks),
        _u32_bytes(batch.hydration_offsets),
        _u32_bytes(batch.hydration_q),
    )
    return input_key, output_key


def _hash72_values(value: str) -> list[int]:
    if len(value) != 72:
        raise ValueError("Hash72 value must contain exactly 72 symbols")
    try:
        return [HASH72_INDEX[symbol] for symbol in value]
    except KeyError as exc:
        raise ValueError(f"invalid Hash72 symbol: {exc.args[0]!r}") from exc


class Pass207VM81GPURuntime:
    """Deterministic candidate executor for VM81 continuation workloads."""

    def __init__(
        self,
        *,
        backend: str | None = None,
        device_index: int = 0,
        cache_capacity_bytes: int = 256 * 1024 * 1024,
        cache_capacity_entries: int = 256,
        require_physical_gpu: bool = False,
    ) -> None:
        selected_backend = backend or os.environ.get("HHS_PASS207_GPU_BACKEND", "AUTO")
        self.translation = Pass205AcceleratorTranslation()
        self.driver = Pass207GPUDriver(
            backend=selected_backend,
            device_index=device_index,
            cache_capacity_bytes=cache_capacity_bytes,
            cache_capacity_entries=cache_capacity_entries,
            verify_against_cpu=True,
            require_physical_gpu=require_physical_gpu,
        )

    def close(self) -> None:
        self.driver.close()

    def __enter__(self) -> "Pass207VM81GPURuntime":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def status(self) -> dict[str, Any]:
        status = self.driver.status()
        return {
            "schema": SCHEMA,
            "contract": CONTRACT,
            "driver": status,
            "vm81_cells": CELL_COUNT,
            "logical_hyperthreads_per_cell": 64,
            "logical_lanes_per_batch": LOGICAL_LANES,
            "state_layout": "uint64 SoA[cell][batch]",
            "projection_layout": "uint32 SoA[channel][cell][batch]",
            "delta_layout": "CSR offsets + uint32 cell + uint8 control_g + uint64 XOR mask",
            "hydration_layout": "CSR offsets + uint32 q",
            "canonical_float_fields": 0,
            "parallel_candidate_calculation_allowed": True,
            "parallel_canonical_authorities_allowed": False,
            "gpu_may_commit_hash72": False,
            "vm81_single_admission_authority": True,
            "vector_store_buffer_cache": True,
        }

    def execute_batch(self, batch: AcceleratorBatch) -> dict[str, Any]:
        if batch.batch_size <= 0:
            raise Pass207GPURejected("batch must contain at least one continuation candidate")
        input_key, output_key = _batch_keys(batch)
        result = self.driver.dispatch(
            state_soa=batch.state_soa,
            projection_soa=batch.projection_soa,
            delta_offsets=batch.delta_offsets,
            delta_cells=batch.delta_cells,
            delta_controls=batch.delta_controls,
            delta_xor_masks=batch.delta_xor_masks,
            hydration_offsets=batch.hydration_offsets,
            hydration_q=batch.hydration_q,
            input_cache_key=input_key,
            output_cache_key=output_key,
            reuse_cached_inputs=True,
            retain_outputs=True,
        )
        reference = self.translation.execute_cpu_reference(batch)
        if result.child_states != reference["child_states"]:
            raise Pass207GPURejected("GPU child state differs from exact Pass 205 CPU oracle")
        if result.child_projections != reference["child_projections"]:
            raise Pass207GPURejected("GPU projection differs from exact Pass 205 CPU oracle")
        if result.frontiers != reference["frontiers"]:
            raise Pass207GPURejected("GPU dependency frontier differs from exact Pass 205 CPU oracle")
        if not all(result.hydration_valid):
            raise Pass207GPURejected("GPU hydration q-address validation failed")
        return {
            "schema": "HHS_PASS_207_VM81_GPU_BATCH_RESULT_V1",
            "ok": True,
            "candidate_only": True,
            "batch_size": batch.batch_size,
            "logical_lane_dispatches": batch.batch_size * LOGICAL_LANES,
            "child_states": result.child_states,
            "child_projections": result.child_projections,
            "frontiers": result.frontiers,
            "hydration_valid": result.hydration_valid,
            "input_cache_key_sha256": input_key.hex(),
            "output_cache_key_sha256": output_key.hex(),
            "verified_against_cpu": True,
            "gpu_may_commit_hash72": False,
            "vm81_single_admission_authority": True,
            "driver": result.status,
        }

    def execute(
        self,
        *,
        states: Sequence[Sequence[int]],
        projections: Sequence[Sequence[Sequence[int]]],
        deltas: Sequence[Sequence[Mapping[str, int]]],
    ) -> dict[str, Any]:
        batch = self.translation.pack_batch(
            states=states,
            projections=projections,
            deltas=deltas,
        )
        return self.execute_batch(batch)

    def rank_hash72_vectors(
        self,
        *,
        query_hash72: str,
        candidate_hash72: Sequence[str],
        candidate_ids: Sequence[str] | None = None,
        top_k: int = 32,
    ) -> dict[str, Any]:
        if not candidate_hash72:
            return {
                "schema": "HHS_PASS_207_GPU_VECTOR_RANK_V1",
                "query_hash72": query_hash72,
                "ranked": [],
                "candidate_count": 0,
                "top_k": 0,
            }
        if candidate_ids is not None and len(candidate_ids) != len(candidate_hash72):
            raise ValueError("candidate_ids and candidate_hash72 must have equal length")
        query = _hash72_values(query_hash72)
        matrix = [_hash72_values(value) for value in candidate_hash72]
        identifiers = list(candidate_ids) if candidate_ids is not None else list(candidate_hash72)
        matrix_key = _fixed_key(
            b"HHS_PASS207_HASH72_VECTOR_MATRIX_V1",
            b"".join(value.encode("ascii") for value in candidate_hash72),
        )
        distances = self.driver.vector_distance72(
            query,
            matrix,
            matrix_cache_key=matrix_key,
            reuse_cached_matrix=True,
        )
        ranked = sorted(
            (
                {
                    "candidate_id": identifiers[index],
                    "candidate_hash72": candidate_hash72[index],
                    "distance": int(distance),
                    "source_ordinal": index,
                }
                for index, distance in enumerate(distances)
            ),
            key=lambda item: (
                item["distance"],
                item["candidate_hash72"],
                item["candidate_id"],
                item["source_ordinal"],
            ),
        )
        bounded_top_k = max(0, min(int(top_k), len(ranked)))
        return {
            "schema": "HHS_PASS_207_GPU_VECTOR_RANK_V1",
            "query_hash72": query_hash72,
            "candidate_count": len(ranked),
            "top_k": bounded_top_k,
            "matrix_cache_key_sha256": matrix_key.hex(),
            "ranked": ranked[:bounded_top_k],
            "stable_tie_break": [
                "distance",
                "candidate_hash72",
                "candidate_id",
                "source_ordinal",
            ],
            "gpu_may_commit_hash72": False,
        }

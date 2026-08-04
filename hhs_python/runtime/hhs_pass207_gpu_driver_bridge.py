"""High-level Python wrapper for the Pass 207 native VM81 GPU driver."""
from __future__ import annotations

import ctypes

from .hhs_pass207_gpu_driver_native import *
from .hhs_pass207_gpu_driver_native import (
    _LIB,
    _cache_key,
    _decode_text,
    _status_name,
    _validate_u64,
)

class Pass207GPUDriver:
    def __init__(
        self,
        *,
        backend: str = "AUTO",
        device_index: int = 0,
        cache_capacity_bytes: int = 256 * 1024 * 1024,
        cache_capacity_entries: int = 256,
        verify_against_cpu: bool = True,
        require_physical_gpu: bool = False,
    ) -> None:
        backend_map = {
            "AUTO": BACKEND_AUTO,
            "CPU_REFERENCE": BACKEND_CPU_REFERENCE,
            "OPENCL": BACKEND_OPENCL,
        }
        try:
            selected = backend_map[backend.upper()]
        except KeyError as exc:
            raise ValueError(f"unsupported Pass 207 backend: {backend}") from exc
        config = _LIB.hhs_pass207_gpu_default_config()
        config.requested_backend = selected
        config.device_index = int(device_index)
        config.cache_capacity_bytes = int(cache_capacity_bytes)
        config.cache_capacity_entries = int(cache_capacity_entries)
        config.verify_against_cpu = int(bool(verify_against_cpu))
        config.require_physical_gpu = int(bool(require_physical_gpu))
        handle = c_void_p()
        code = int(_LIB.hhs_pass207_gpu_create(ctypes.byref(config), ctypes.byref(handle)))
        if code != STATUS_OK or not handle.value:
            raise RuntimeError(f"Pass 207 GPU driver creation failed: {_status_name(code)}")
        self._handle = handle

    def close(self) -> None:
        if getattr(self, "_handle", None) is not None and self._handle.value:
            _LIB.hhs_pass207_gpu_destroy(self._handle)
            self._handle = c_void_p()

    def __enter__(self) -> "Pass207GPUDriver":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    @staticmethod
    def lane_address(cell: int, hyperthread: int) -> int:
        ok = c_uint8(0)
        lane = int(_LIB.hhs_pass207_lane_address(int(cell), int(hyperthread), ctypes.byref(ok)))
        if not ok.value:
            raise ValueError(f"invalid VM81 lane cell={cell}, hyperthread={hyperthread}")
        return lane

    @staticmethod
    def lane_decode(lane: int) -> tuple[int, int]:
        cell = c_uint8(0)
        hyperthread = c_uint8(0)
        if not _LIB.hhs_pass207_lane_decode(int(lane), ctypes.byref(cell), ctypes.byref(hyperthread)):
            raise ValueError(f"invalid VM81 lane: {lane}")
        return int(cell.value), int(hyperthread.value)

    @staticmethod
    def lane_phase_coordinate(lane: int) -> tuple[int, int]:
        row = c_uint8(0)
        column = c_uint8(0)
        if not _LIB.hhs_pass207_lane_phase_coordinate(int(lane), ctypes.byref(row), ctypes.byref(column)):
            raise ValueError(f"invalid VM81 lane: {lane}")
        return int(row.value), int(column.value)

    def status(self) -> dict[str, Any]:
        status = HHSPass207GPUStatus()
        code = int(_LIB.hhs_pass207_gpu_get_status(self._handle, ctypes.byref(status)))
        if code != STATUS_OK:
            raise RuntimeError(f"Pass 207 status failed: {_status_name(code)}")
        return {
            "schema": "HHS_PASS_207_GPU_STATUS_V1",
            "selected_backend": int(status.selected_backend),
            "backend_name": _decode_text(status.backend_name),
            "device_name": _decode_text(status.device_name),
            "physical_gpu": bool(status.physical_gpu),
            "deterministic_integer_only": bool(status.deterministic_integer_only),
            "verified_against_cpu": bool(status.verified_against_cpu),
            "logical_hyperthreads_per_cell": int(status.logical_hyperthreads_per_cell),
            "logical_lanes_per_batch": int(status.logical_lanes_per_batch),
            "physical_workgroup_size": int(status.physical_workgroup_size),
            "stable_lane_identity": bool(status.stable_lane_identity),
            "disjoint_lane_writes": bool(status.disjoint_lane_writes),
            "canonical_reduction_order": bool(status.canonical_reduction_order),
            "dispatch_count": int(status.dispatch_count),
            "vector_dispatch_count": int(status.vector_dispatch_count),
            "cache_input_hit": bool(status.cache_input_hit),
            "cache_output_retained": bool(status.cache_output_retained),
            "cache_hits": int(status.cache_hits),
            "cache_misses": int(status.cache_misses),
            "cache_evictions": int(status.cache_evictions),
            "cache_resident_bytes": int(status.cache_resident_bytes),
            "cache_entries": int(status.cache_entries),
            "input_bytes_uploaded": int(status.input_bytes_uploaded),
            "output_bytes_downloaded": int(status.output_bytes_downloaded),
            "last_error": _decode_text(status.last_error),
            "gpu_may_commit_hash72": False,
            "vm81_single_admission_authority": True,
        }

    def dispatch(
        self,
        *,
        state_soa: Sequence[Sequence[int]],
        projection_soa: Sequence[Sequence[Sequence[int]]],
        delta_offsets: Sequence[int],
        delta_cells: Sequence[int],
        delta_controls: Sequence[int],
        delta_xor_masks: Sequence[int],
        hydration_offsets: Sequence[int],
        hydration_q: Sequence[int],
        input_cache_key: bytes | str | None = None,
        output_cache_key: bytes | str | None = None,
        reuse_cached_inputs: bool = True,
        retain_outputs: bool = True,
    ) -> DriverResult:
        if len(state_soa) != CELL_COUNT:
            raise ValueError(f"state_soa requires {CELL_COUNT} cells")
        batch_size = len(state_soa[0]) if state_soa else 0
        if batch_size <= 0 or any(len(row) != batch_size for row in state_soa):
            raise ValueError("state_soa batch dimension mismatch")
        if len(projection_soa) != PROJECTION_CHANNELS:
            raise ValueError(f"projection_soa requires {PROJECTION_CHANNELS} channels")
        if any(len(channel) != CELL_COUNT for channel in projection_soa):
            raise ValueError("projection_soa cell dimension mismatch")
        if any(len(row) != batch_size for channel in projection_soa for row in channel):
            raise ValueError("projection_soa batch dimension mismatch")
        if len(delta_offsets) != batch_size + 1 or len(hydration_offsets) != batch_size + 1:
            raise ValueError("CSR offsets must contain batch_size + 1 entries")
        if not (len(delta_cells) == len(delta_controls) == len(delta_xor_masks)):
            raise ValueError("delta CSR arrays must have equal length")

        state_flat = [_validate_u64(value) for row in state_soa for value in row]
        projection_flat = [int(value) for channel in projection_soa for row in channel for value in row]
        if any(value < 0 or value > 0xFFFFFFFF for value in projection_flat):
            raise ValueError("projection value outside uint32")
        cells = [int(value) for value in delta_cells]
        controls = [int(value) for value in delta_controls]
        masks = [_validate_u64(value) for value in delta_xor_masks]
        q_values = [int(value) for value in hydration_q]

        state_array = (c_uint64 * len(state_flat))(*state_flat)
        projection_array = (c_uint32 * len(projection_flat))(*projection_flat)
        delta_offsets_array = (c_uint32 * len(delta_offsets))(*map(int, delta_offsets))
        delta_cells_array = (c_uint32 * max(1, len(cells)))(*(cells or [0]))
        delta_controls_array = (c_uint8 * max(1, len(controls)))(*(controls or [0]))
        delta_masks_array = (c_uint64 * max(1, len(masks)))(*(masks or [0]))
        hydration_offsets_array = (c_uint32 * len(hydration_offsets))(*map(int, hydration_offsets))
        hydration_q_array = (c_uint32 * max(1, len(q_values)))(*(q_values or [0]))
        input_key_bytes = _cache_key(input_cache_key)
        output_key_bytes = _cache_key(output_cache_key)
        input_key_array = (c_uint8 * CACHE_KEY_BYTES)(*input_key_bytes)
        output_key_array = (c_uint8 * CACHE_KEY_BYTES)(*output_key_bytes)

        child_state_array = (c_uint64 * (CELL_COUNT * batch_size))()
        child_projection_array = (c_uint32 * (PROJECTION_CHANNELS * CELL_COUNT * batch_size))()
        frontier_array = (c_uint8 * (CELL_COUNT * batch_size))()
        hydration_valid_array = (c_uint8 * batch_size)()

        native_batch = HHSPass207Batch(
            batch_size=batch_size,
            state_soa=state_array,
            projection_soa=projection_array,
            delta_offsets=delta_offsets_array,
            delta_cells=delta_cells_array,
            delta_controls=delta_controls_array,
            delta_xor_masks=delta_masks_array,
            hydration_offsets=hydration_offsets_array,
            hydration_q=hydration_q_array,
            delta_count=len(cells),
            hydration_count=len(q_values),
            input_cache_key=input_key_array,
            output_cache_key=output_key_array,
            reuse_cached_inputs=int(bool(reuse_cached_inputs)),
            retain_outputs=int(bool(retain_outputs)),
        )
        native_output = HHSPass207BatchOutput(
            child_state_soa=child_state_array,
            child_projection_soa=child_projection_array,
            frontier_soa=frontier_array,
            hydration_valid=hydration_valid_array,
        )
        code = int(_LIB.hhs_pass207_gpu_dispatch(
            self._handle,
            ctypes.byref(native_batch),
            ctypes.byref(native_output),
        ))
        if code != STATUS_OK:
            status = self.status()
            raise RuntimeError(
                f"Pass 207 GPU dispatch failed: {_status_name(code)}: {status['last_error']}"
            )

        child_states = [
            [int(child_state_array[cell * batch_size + batch]) for cell in range(CELL_COUNT)]
            for batch in range(batch_size)
        ]
        child_projections = [
            [
                [
                    int(child_projection_array[(channel * CELL_COUNT + cell) * batch_size + batch])
                    for cell in range(CELL_COUNT)
                ]
                for channel in range(PROJECTION_CHANNELS)
            ]
            for batch in range(batch_size)
        ]
        frontiers = [
            [cell for cell in range(CELL_COUNT) if frontier_array[cell * batch_size + batch]]
            for batch in range(batch_size)
        ]
        return DriverResult(
            child_states=child_states,
            child_projections=child_projections,
            frontiers=frontiers,
            hydration_valid=[bool(value) for value in hydration_valid_array],
            status=self.status(),
        )

    def vector_distance72(
        self,
        query: Sequence[int],
        candidates: Sequence[Sequence[int]],
        *,
        matrix_cache_key: bytes | str | None = None,
        reuse_cached_matrix: bool = True,
    ) -> list[int]:
        query_values = [int(value) for value in query]
        if len(query_values) != 72 or any(value < 0 or value >= 72 for value in query_values):
            raise ValueError("query must contain exactly 72 values in [0, 71]")
        candidate_rows = [[int(value) for value in row] for row in candidates]
        if not candidate_rows or any(len(row) != 72 for row in candidate_rows):
            raise ValueError("candidates must contain one or more 72-value rows")
        if any(value < 0 or value >= 72 for row in candidate_rows for value in row):
            raise ValueError("candidate values must be in [0, 71]")
        query_array = (c_uint8 * 72)(*query_values)
        flat = [value for row in candidate_rows for value in row]
        matrix_array = (c_uint8 * len(flat))(*flat)
        key_array = (c_uint8 * CACHE_KEY_BYTES)(*_cache_key(matrix_cache_key))
        output = (c_uint32 * len(candidate_rows))()
        code = int(_LIB.hhs_pass207_gpu_vector_distance72(
            self._handle,
            query_array,
            matrix_array,
            len(candidate_rows),
            key_array,
            int(bool(reuse_cached_matrix)),
            output,
        ))
        if code != STATUS_OK:
            raise RuntimeError(f"Pass 207 vector dispatch failed: {_status_name(code)}")
        return [int(value) for value in output]

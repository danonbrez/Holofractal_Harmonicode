"""Fixed-width ctypes bridge for Pass 213 Iteration 10 native dispatch."""
from __future__ import annotations

import ctypes
from pathlib import Path
from typing import Sequence

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import CompiledROMEntry
from hhs_backend.runtime.hhs_pass213_native_dispatch_common_v1 import (
    DISPATCH_ABI_VERSION, MAX_OPERANDS, MAX_RESULTS, _NATIVE_DISPATCH_IDS,
    Pass213NativeDispatchIntegrityError,
    Pass213NativeDispatchValidationError,
)

class _NativeRequest(ctypes.Structure):
    _fields_ = [
        ("abi_version", ctypes.c_uint32),
        ("opcode", ctypes.c_uint32),
        ("input_count", ctypes.c_uint32),
        ("result_capacity", ctypes.c_uint32),
        ("vm81_cell_id", ctypes.c_uint32),
        ("operation_slot", ctypes.c_uint32),
        ("g243_control_id", ctypes.c_uint32),
        ("reserved0", ctypes.c_uint32),
        ("request_sequence", ctypes.c_uint64),
        ("modulus", ctypes.c_uint64),
        ("operands", ctypes.c_uint64 * MAX_OPERANDS),
    ]


class _NativeResponse(ctypes.Structure):
    _fields_ = [
        ("abi_version", ctypes.c_uint32),
        ("status", ctypes.c_uint32),
        ("result_count", ctypes.c_uint32),
        ("opcode", ctypes.c_uint32),
        ("request_sequence", ctypes.c_uint64),
        ("results", ctypes.c_uint64 * MAX_RESULTS),
    ]


class NativeDispatchKernel:
    """ctypes bridge to the fixed-width allocation-free C execution ABI."""

    def __init__(self, *, library_path: str | Path) -> None:
        self.library_path = str(Path(library_path))
        self._lib = ctypes.CDLL(self.library_path)
        self._lib.hhs_pass213_native_dispatch_execute.argtypes = [
            ctypes.POINTER(_NativeRequest), ctypes.POINTER(_NativeResponse)
        ]
        self._lib.hhs_pass213_native_dispatch_execute.restype = ctypes.c_int
        self._lib.hhs_pass213_native_dispatch_error_string.argtypes = [ctypes.c_int]
        self._lib.hhs_pass213_native_dispatch_error_string.restype = ctypes.c_char_p

    def execute(
        self,
        *,
        entry: CompiledROMEntry,
        operands: Sequence[int],
        request_sequence: int,
        modulus: int,
    ) -> tuple[int, ...]:
        try:
            opcode = _NATIVE_DISPATCH_IDS[entry.native_dispatch_id]
        except KeyError as exc:
            raise Pass213NativeDispatchValidationError(
                "PASS213_NATIVE_DISPATCH_ID_UNSUPPORTED"
            ) from exc
        native = _NativeRequest()
        native.abi_version = DISPATCH_ABI_VERSION
        native.opcode = opcode
        native.input_count = len(operands)
        native.result_capacity = MAX_RESULTS
        native.vm81_cell_id = entry.vm81_cell_id
        native.operation_slot = entry.operation_slot
        native.g243_control_id = entry.g243_control_id
        native.request_sequence = request_sequence
        native.modulus = modulus
        for index, value in enumerate(operands):
            native.operands[index] = value
        response = _NativeResponse()
        status = self._lib.hhs_pass213_native_dispatch_execute(
            ctypes.byref(native), ctypes.byref(response)
        )
        if status != 0 or response.status != 0:
            message = self._lib.hhs_pass213_native_dispatch_error_string(status)
            decoded = message.decode("ascii", errors="replace") if message else str(status)
            raise Pass213NativeDispatchValidationError(
                f"PASS213_NATIVE_DISPATCH_EXECUTION_FAILED:{decoded}"
            )
        if (
            response.abi_version != DISPATCH_ABI_VERSION
            or response.opcode != opcode
            or response.request_sequence != request_sequence
            or not 1 <= response.result_count <= MAX_RESULTS
        ):
            raise Pass213NativeDispatchIntegrityError(
                "PASS213_NATIVE_DISPATCH_NATIVE_RESPONSE_MISMATCH"
            )
        return tuple(int(response.results[index]) for index in range(response.result_count))




__all__ = ["NativeDispatchKernel"]

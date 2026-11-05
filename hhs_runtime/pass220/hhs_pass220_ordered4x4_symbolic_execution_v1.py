"""Native exact symbolic program interpreter bridge for the frozen 4x4 source.

Only operator graph execution, not HHS matrix value derivation or VM81
admission. Identical code path to the registered C exact ABI; no scalar math.
"""
from __future__ import annotations
import ctypes
from dataclasses import dataclass
from pathlib import Path

from hhs_runtime.pass220.hhs_pass220_ordered_4x4_neg4_matrix_tensor_v1 import (
    SOURCE_PATH, SOURCE_SHA256, MatrixTensorHIRReject, stage_hir,
)

class _Execution(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("steps", ctypes.c_uint32),
        ("maximum_stack_depth", ctypes.c_uint32),
        ("matrices_bound", ctypes.c_uint32),
        ("symbols_bound", ctypes.c_uint32),
        ("source_identity_verified", ctypes.c_uint8),
        ("operator_types_verified", ctypes.c_uint8),
        ("ordered_program_verified", ctypes.c_uint8),
        ("exact_symbolic_program_executed", ctypes.c_uint8),
        ("deterministic_symbolic_replay_verified", ctypes.c_uint8),
        ("expression_equality_proved", ctypes.c_uint8),
        ("matrix_power_value_derived", ctypes.c_uint8),
        ("matrix_times_numeric_evaluated", ctypes.c_uint8),
        ("quotient_value_derived", ctypes.c_uint8),
        ("typed_s_substituted", ctypes.c_uint8),
        ("typed_v_substituted", ctypes.c_uint8),
        ("vm81_admission_executed", ctypes.c_uint8),
        ("canonical_vm81_mutation_authority", ctypes.c_uint8),
        ("hash72_commit_authority", ctypes.c_uint8),
        ("hash216_commit_authority", ctypes.c_uint8),
        ("reserved", ctypes.c_uint8 * 1),
        ("source_sha256", ctypes.c_uint8 * 32),
        ("program_sha256", ctypes.c_uint8 * 32),
        ("result_node_sha256", ctypes.c_uint8 * 32),
        ("ordered_node_roots", (ctypes.c_uint8 * 32) * 15),
    ]

@dataclass(frozen=True)
class SymbolicOperatorExecution:
    source_sha256: str
    program_sha256: str
    ordered_node_roots: tuple[str, ...]
    result_root_sha256: str
    operator_steps: int
    maximum_stack_depth: int
    matrices_bound: int
    symbols_bound: int
    exact_symbolic_program_executed: bool
    deterministic_symbolic_replay_verified: bool
    expression_equality_proved: bool
    matrix_power_value_derived: bool
    vm81_admission_executed: bool
    hash72_commit_authority: bool
    hash216_commit_authority: bool

class NativeOrdered4x4SymbolicExecutor:
    def __init__(self, library_path: str | Path):
        lib = ctypes.CDLL(str(library_path))
        self._program = lib.hhs_exact_pass220_ordered4x4_program
        self._program.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
        ]
        self._program.restype = ctypes.c_int
        self._execute = lib.hhs_exact_pass220_ordered4x4_execute_symbolic
        self._execute.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
            ctypes.POINTER(_Execution),
        ]
        self._execute.restype = ctypes.c_int

    def execute(self, *, root: str | Path | None = None) -> SymbolicOperatorExecution:
        source_hir = stage_hir(root)
        repo = Path(root).resolve() if root is not None else Path(__file__).resolve().parents[2]
        source = (repo / SOURCE_PATH).read_bytes()
        source_buf = (ctypes.c_uint8 * len(source)).from_buffer_copy(source)
        program_buf = (ctypes.c_uint8 * 15)()
        n = ctypes.c_size_t()
        if self._program(program_buf, 15, ctypes.byref(n)) != 0 or n.value != 15:
            raise MatrixTensorHIRReject("NATIVE_OPERATOR_PROGRAM_UNAVAILABLE")
        out = _Execution()
        status = self._execute(source_buf, len(source), program_buf, n.value, ctypes.byref(out))
        if status != 0:
            raise MatrixTensorHIRReject(f"NATIVE_OPERATOR_EXECUTION_REJECTED:{status}")
        if (bytes(out.source_sha256).hex() != SOURCE_SHA256
                or source_hir["source_sha256"] != SOURCE_SHA256):
            raise MatrixTensorHIRReject("NATIVE_SYMBOLIC_SOURCE_IDENTITY_DRIFT")
        if not (out.operator_types_verified == 1
                and out.ordered_program_verified == 1
                and out.exact_symbolic_program_executed == 1
                and out.deterministic_symbolic_replay_verified == 1
                and out.source_identity_verified == 1
                and out.steps == 15 and out.matrices_bound == 4
                and out.symbols_bound == 2 and out.maximum_stack_depth == 3):
            raise MatrixTensorHIRReject("NATIVE_SYMBOLIC_OPERATOR_EXECUTION_INCOMPLETE")
        forbidden = (
            out.expression_equality_proved, out.matrix_power_value_derived,
            out.matrix_times_numeric_evaluated, out.quotient_value_derived,
            out.typed_s_substituted, out.typed_v_substituted,
            out.vm81_admission_executed, out.canonical_vm81_mutation_authority,
            out.hash72_commit_authority, out.hash216_commit_authority,
        )
        if any(forbidden):
            raise MatrixTensorHIRReject("NATIVE_SYMBOLIC_OPERATOR_AUTHORITY_ESCALATION")
        roots = tuple(bytes(root).hex() for root in out.ordered_node_roots)
        result = bytes(out.result_node_sha256).hex()
        if len(roots) != 15 or roots[-1] != result or any(x == "0"*64 for x in roots):
            raise MatrixTensorHIRReject("NATIVE_SYMBOLIC_OPERATOR_ROOT_DRIFT")
        return SymbolicOperatorExecution(
            source_sha256=bytes(out.source_sha256).hex(),
            program_sha256=bytes(out.program_sha256).hex(),
            ordered_node_roots=roots,
            result_root_sha256=result,
            operator_steps=int(out.steps),
            maximum_stack_depth=int(out.maximum_stack_depth),
            matrices_bound=int(out.matrices_bound),
            symbols_bound=int(out.symbols_bound),
            exact_symbolic_program_executed=True,
            deterministic_symbolic_replay_verified=True,
            expression_equality_proved=False,
            matrix_power_value_derived=False,
            vm81_admission_executed=False,
            hash72_commit_authority=False,
            hash216_commit_authority=False,
        )

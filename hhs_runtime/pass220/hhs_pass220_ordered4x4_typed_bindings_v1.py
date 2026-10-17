"""Native exact 5184-character addressed tensor binding for HHS 4x4 symbolic HIR.

No scalar conversion and no Python math. This invokes the inherited
source-locked native operator graph and never claims signed VM81 admission.
"""
from __future__ import annotations
import ctypes
from dataclasses import dataclass
from pathlib import Path

from hhs_runtime.pass220.hhs_pass220_ordered_4x4_neg4_matrix_tensor_v1 import (
    SOURCE_PATH, MatrixTensorHIRReject, stage_hir,
)

LEN = 5184
PARENT = 216
OPS = 15


@dataclass(frozen=True)
class AddressedTensorBinding:
    symbol: str
    vm81_cell: int
    vm81_operation: int
    harmonicode_5184: str
    predecessor_hash216: str


class _Binding(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("symbol", ctypes.c_uint8),
        ("cell81", ctypes.c_uint8),
        ("operation64", ctypes.c_uint8),
        ("reserved", ctypes.c_uint8),
        ("state_utf8", ctypes.POINTER(ctypes.c_uint8)),
        ("state_bytes", ctypes.c_size_t),
        ("predecessor_hash216", ctypes.POINTER(ctypes.c_uint8)),
        ("predecessor_bytes", ctypes.c_size_t),
    ]


class _Result(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("ordered_opcodes", ctypes.c_uint32),
        ("maximum_stack_depth", ctypes.c_uint32),
        ("s_codepoints", ctypes.c_uint32),
        ("v_codepoints", ctypes.c_uint32),
        ("s_serialized_bytes", ctypes.c_uint32),
        ("v_serialized_bytes", ctypes.c_uint32),
        ("s_vm5184_address", ctypes.c_uint16),
        ("v_vm5184_address", ctypes.c_uint16),
        ("source_identity_verified", ctypes.c_uint8),
        ("ordered_type_graph_executed", ctypes.c_uint8),
        ("deterministic_bound_graph_replay_verified", ctypes.c_uint8),
        ("typed_bindings_shape_verified", ctypes.c_uint8),
        ("native_predecessor_identity_matched", ctypes.c_uint8),
        ("native_binding_authenticity_verified", ctypes.c_uint8),
        ("s_value_scalarized", ctypes.c_uint8),
        ("v_value_scalarized", ctypes.c_uint8),
        ("matrix_times_value_derived", ctypes.c_uint8),
        ("matrix_quotient_value_derived", ctypes.c_uint8),
        ("matrix_power_value_derived", ctypes.c_uint8),
        ("equation_equality_proved", ctypes.c_uint8),
        ("vm81_admission_executed", ctypes.c_uint8),
        ("hash72_commit_authority", ctypes.c_uint8),
        ("hash216_commit_authority", ctypes.c_uint8),
        ("canonical_vm81_mutation_authority", ctypes.c_uint8),
        ("binding_roots_sha256", (ctypes.c_uint8 * 32) * 2),
        ("ordered_node_roots", (ctypes.c_uint8 * 32) * OPS),
        ("result_root_sha256", ctypes.c_uint8 * 32),
    ]


@dataclass(frozen=True)
class NativeBoundTensorHIRResult:
    binding_roots_sha256: tuple[str, str]
    ordered_node_roots_sha256: tuple[str, ...]
    result_root_sha256: str
    s_address: int
    v_address: int
    s_utf8_bytes: int
    v_utf8_bytes: int
    ordered_steps: int
    source_verified: bool
    bound_symbolic_execution_verified: bool
    deterministic_bound_replay_verified: bool
    native_binding_authenticity_verified: bool
    matrix_value_derived: bool
    equation_equality_proved: bool
    vm81_admission_executed: bool
    hash72_commit_authority: bool
    hash216_commit_authority: bool


def _pack(binding: AddressedTensorBinding, expected_symbol: str):
    if not isinstance(binding, AddressedTensorBinding):
        raise MatrixTensorHIRReject("ADDRESSED_TENSOR_BINDING_REQUIRED")
    if binding.symbol != expected_symbol:
        raise MatrixTensorHIRReject("HHS_SOURCE_SYMBOL_ROLE_MISMATCH")
    if (type(binding.vm81_cell) is not int or
        not 0 <= binding.vm81_cell < 81 or
        type(binding.vm81_operation) is not int or
        not 0 <= binding.vm81_operation < 64):
        raise MatrixTensorHIRReject("VM5184_NATIVE_ADDRESS_REQUIRED")
    text = binding.harmonicode_5184
    if not isinstance(text, str) or len(text) != LEN:
        raise MatrixTensorHIRReject("HARMONICODE_5184_CHARACTERS_REQUIRED")
    try:
        serialized = text.encode("utf-8", "strict")
    except UnicodeError as exc:
        raise MatrixTensorHIRReject("HARMONICODE_UTF8_INVALID") from exc
    predecessor = binding.predecessor_hash216
    if (not isinstance(predecessor, str) or len(predecessor) != PARENT or
        any(ord(c) < 33 or ord(c) > 126 for c in predecessor)):
        raise MatrixTensorHIRReject("PREDECESSOR_HASH216_SHAPE_REQUIRED")
    raw_state = (ctypes.c_uint8 * len(serialized)).from_buffer_copy(serialized)
    raw_parent = (ctypes.c_uint8 * PARENT).from_buffer_copy(predecessor.encode("ascii"))
    body = _Binding(
        ctypes.sizeof(_Binding), ord(expected_symbol), binding.vm81_cell,
        binding.vm81_operation, 0, raw_state, len(serialized),
        raw_parent, PARENT,
    )
    return body, raw_state, raw_parent


class NativeOrdered4x4BoundExecutor:
    def __init__(self, library_path: str | Path):
        self._library = ctypes.CDLL(str(library_path))
        self._execute = self._library.hhs_exact_pass220_ordered4x4_execute_bound
        self._execute.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
            ctypes.POINTER(_Binding), ctypes.POINTER(_Binding),
            ctypes.POINTER(_Result),
        ]
        self._execute.restype = ctypes.c_int

    def execute(
        self, s: AddressedTensorBinding, v: AddressedTensorBinding,
        *, root: str | Path | None = None,
    ) -> NativeBoundTensorHIRResult:
        source_hir = stage_hir(root)
        repo = Path(root).resolve() if root is not None else Path(__file__).resolve().parents[2]
        if s.predecessor_hash216 != v.predecessor_hash216:
            raise MatrixTensorHIRReject("NATIVE_PREDECESSOR_LINEAGE_MISMATCH")
        s_binding, s_bytes, s_parent = _pack(s, "s")
        v_binding, v_bytes, v_parent = _pack(v, "v")
        source = (repo / SOURCE_PATH).read_bytes()
        source_buf = (ctypes.c_uint8 * len(source)).from_buffer_copy(source)
        out = _Result()
        result = self._execute(
            source_buf, len(source), ctypes.byref(s_binding),
            ctypes.byref(v_binding), ctypes.byref(out),
        )
        # Hold all pointer backing allocations alive through the ABI boundary.
        _ = (s_bytes, s_parent, v_bytes, v_parent, source_buf, source_hir)
        if result != 0:
            raise MatrixTensorHIRReject(f"NATIVE_TENSOR_BOUND_HIR_REJECTED:{result}")
        if not (out.source_identity_verified == 1 and
                out.ordered_type_graph_executed == 1 and
                out.deterministic_bound_graph_replay_verified == 1 and
                out.typed_bindings_shape_verified == 1 and
                out.native_predecessor_identity_matched == 1 and
                out.ordered_opcodes == OPS and
                out.s_codepoints == LEN and out.v_codepoints == LEN and
                out.s_vm5184_address == 64*s.vm81_cell+s.vm81_operation and
                out.v_vm5184_address == 64*v.vm81_cell+v.vm81_operation):
            raise MatrixTensorHIRReject("BOUND_NATIVE_TENSOR_GRAPH_INCOMPLETE")
        forbidden = (
            out.native_binding_authenticity_verified,
            out.s_value_scalarized, out.v_value_scalarized,
            out.matrix_times_value_derived, out.matrix_quotient_value_derived,
            out.matrix_power_value_derived, out.equation_equality_proved,
            out.vm81_admission_executed, out.hash72_commit_authority,
            out.hash216_commit_authority, out.canonical_vm81_mutation_authority,
        )
        if any(forbidden):
            raise MatrixTensorHIRReject("BOUND_NATIVE_TENSOR_AUTHORITY_ESCALATION")
        roots = tuple(bytes(x).hex() for x in out.ordered_node_roots)
        final = bytes(out.result_root_sha256).hex()
        if len(roots) != OPS or roots[-1] != final:
            raise MatrixTensorHIRReject("BOUND_NATIVE_TENSOR_ROOT_DRIFT")
        return NativeBoundTensorHIRResult(
            binding_roots_sha256=tuple(bytes(x).hex() for x in out.binding_roots_sha256),
            ordered_node_roots_sha256=roots,
            result_root_sha256=final,
            s_address=int(out.s_vm5184_address),
            v_address=int(out.v_vm5184_address),
            s_utf8_bytes=int(out.s_serialized_bytes),
            v_utf8_bytes=int(out.v_serialized_bytes),
            ordered_steps=int(out.ordered_opcodes),
            source_verified=True,
            bound_symbolic_execution_verified=True,
            deterministic_bound_replay_verified=True,
            native_binding_authenticity_verified=False,
            matrix_value_derived=False,
            equation_equality_proved=False,
            vm81_admission_executed=False,
            hash72_commit_authority=False,
            hash216_commit_authority=False,
        )

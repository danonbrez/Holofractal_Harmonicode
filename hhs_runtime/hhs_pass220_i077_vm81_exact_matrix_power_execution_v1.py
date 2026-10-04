"""Pass 220 I077 Python binding for VM81 ExactMatrixPower execution.

This module is transport glue over the additive native exact ABI. It does not
recompute HARMONICODE matrix-power semantics in Python.
"""
from __future__ import annotations

import ctypes
from dataclasses import dataclass
from pathlib import Path

SCHEMA = "HHS_PASS_220_I077_VM81_EXACT_MATRIX_POWER_EXECUTION_V1"

NODE_M_WZ_X2 = 0
NODE_M_XY_X4 = 1
CELL_OCCURRENCES = 8
HASH72_STRLEN = 73
HASH216_STRLEN = 217
SHA256_HEX_STRLEN = 65


class I077ExecutionError(RuntimeError):
    pass


class _Descriptor(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("node_count", ctypes.c_uint32),
        ("rows", ctypes.c_uint32),
        ("columns", ctypes.c_uint32),
        ("cell_occurrences_per_node", ctypes.c_uint32),
        ("unique_cell_roots", ctypes.c_uint32),
        ("exact_matrix_power_hir_required", ctypes.c_uint8),
        ("native_symbolic_executor", ctypes.c_uint8),
        ("rectangular_4x2_supported", ctypes.c_uint8),
        ("source_identity_required", ctypes.c_uint8),
        ("ordered_topology_required", ctypes.c_uint8),
        ("vm81_transport_admission", ctypes.c_uint8),
        ("hash72_execution_receipt", ctypes.c_uint8),
        ("hash216_transition_identity", ctypes.c_uint8),
        ("deterministic_replay", ctypes.c_uint8),
        ("matrix_power_value_derivation", ctypes.c_uint8),
        ("host_matrixpower_authority", ctypes.c_uint8),
        ("host_square_matrix_requirement_authority", ctypes.c_uint8),
        ("numeric_exponent_evaluation_authority", ctypes.c_uint8),
        ("floating_point_authority", ctypes.c_uint8),
        ("canonical_state_persistence_authority", ctypes.c_uint8),
        ("canonical_vm81_mutation_authority", ctypes.c_uint8),
        ("canonical_hash72_commit_authority", ctypes.c_uint8),
        ("canonical_hash216_commit_authority", ctypes.c_uint8),
        ("external_egress_authority", ctypes.c_uint8),
        ("reserved0", ctypes.c_uint8 * 2),
    ]


class _Execution(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("decision", ctypes.c_uint32),
        ("reason", ctypes.c_uint32),
        ("node_id", ctypes.c_uint32),
        ("rows", ctypes.c_uint32),
        ("columns", ctypes.c_uint32),
        ("exponent_token_degree", ctypes.c_uint32),
        ("cell_occurrence_count", ctypes.c_uint32),
        ("unique_cell_root_count", ctypes.c_uint32),
        ("cell_tokens", ctypes.c_uint8 * CELL_OCCURRENCES),
        ("source_identity_exact", ctypes.c_uint8),
        ("ordered_topology_verified", ctypes.c_uint8),
        ("exact_symbolic_node_executed", ctypes.c_uint8),
        ("host_matrixpower_used", ctypes.c_uint8),
        ("square_matrix_requirement_imported", ctypes.c_uint8),
        ("numeric_exponent_evaluated", ctypes.c_uint8),
        ("matrix_power_value_derived", ctypes.c_uint8),
        ("exact_vm81_admission_verified", ctypes.c_uint8),
        ("atomic_frame_commit_verified", ctypes.c_uint8),
        ("hash72_receipt_verified", ctypes.c_uint8),
        ("hash216_transition_identity_verified", ctypes.c_uint8),
        ("deterministic_replay_verified", ctypes.c_uint8),
        ("canonical_state_persisted", ctypes.c_uint8),
        ("floating_point_authority", ctypes.c_uint8),
        ("reserved0", ctypes.c_uint8),
        ("vm5184_address", ctypes.c_uint16),
        ("reserved1", ctypes.c_uint16),
        ("vm81_steps", ctypes.c_uint64),
        ("replay_vm81_steps", ctypes.c_uint64),
        ("source_node", ctypes.c_char * 64),
        ("exponent_token", ctypes.c_char * 8),
        ("source_node_sha256", ctypes.c_char * SHA256_HEX_STRLEN),
        ("ordered_cells_sha256", ctypes.c_char * SHA256_HEX_STRLEN),
        ("change_hash72", ctypes.c_char * HASH72_STRLEN),
        ("receipt_hash72", ctypes.c_char * HASH72_STRLEN),
        ("replay_hash72", ctypes.c_char * HASH72_STRLEN),
        ("proof_hash216", ctypes.c_char * HASH216_STRLEN),
        ("transition_hash216", ctypes.c_char * HASH216_STRLEN),
    ]


@dataclass(frozen=True)
class VM81ExactMatrixPowerExecution:
    schema: str
    node_id: int
    source_node: str
    rows: int
    columns: int
    exponent_token: str
    exponent_token_degree: int
    cell_tokens: tuple[int, ...]
    source_node_sha256: str
    ordered_cells_sha256: str
    vm5184_address: int
    vm81_steps: int
    replay_vm81_steps: int
    change_hash72: str
    receipt_hash72: str
    replay_hash72: str
    proof_hash216: str
    transition_hash216: str
    source_identity_exact: bool
    ordered_topology_verified: bool
    exact_symbolic_node_executed: bool
    exact_vm81_admission_verified: bool
    atomic_frame_commit_verified: bool
    hash72_receipt_verified: bool
    hash216_transition_identity_verified: bool
    deterministic_replay_verified: bool
    matrix_power_value_derived: bool
    host_matrixpower_used: bool
    square_matrix_requirement_imported: bool
    numeric_exponent_evaluated: bool
    canonical_state_persisted: bool
    floating_point_authority: bool


def _decode(value: bytes) -> str:
    return value.split(b"\0", 1)[0].decode("ascii")


class VM81ExactMatrixPowerExecutor:
    def __init__(self, exact_abi_library: str | Path):
        self.library_path = str(Path(exact_abi_library))
        self._lib = ctypes.CDLL(self.library_path)
        self._lib.hhs_exact_pass220_i077_version.argtypes = []
        self._lib.hhs_exact_pass220_i077_version.restype = ctypes.c_uint32
        self._lib.hhs_exact_pass220_i077_descriptor.argtypes = [
            ctypes.POINTER(_Descriptor)
        ]
        self._lib.hhs_exact_pass220_i077_descriptor.restype = ctypes.c_int
        self._lib.hhs_exact_pass220_i077_execute.argtypes = [
            ctypes.c_uint32,
            ctypes.POINTER(_Execution),
        ]
        self._lib.hhs_exact_pass220_i077_execute.restype = ctypes.c_int
        self.version = int(self._lib.hhs_exact_pass220_i077_version())

        descriptor = _Descriptor()
        status = int(
            self._lib.hhs_exact_pass220_i077_descriptor(
                ctypes.byref(descriptor)
            )
        )
        if status != 0:
            raise I077ExecutionError(f"I077_DESCRIPTOR_REJECTED:{status}")
        self.descriptor = {
            "node_count": int(descriptor.node_count),
            "rows": int(descriptor.rows),
            "columns": int(descriptor.columns),
            "cell_occurrences_per_node": int(
                descriptor.cell_occurrences_per_node
            ),
            "unique_cell_roots": int(descriptor.unique_cell_roots),
            "native_symbolic_executor": bool(
                descriptor.native_symbolic_executor
            ),
            "rectangular_4x2_supported": bool(
                descriptor.rectangular_4x2_supported
            ),
            "vm81_transport_admission": bool(
                descriptor.vm81_transport_admission
            ),
            "hash72_execution_receipt": bool(
                descriptor.hash72_execution_receipt
            ),
            "hash216_transition_identity": bool(
                descriptor.hash216_transition_identity
            ),
            "deterministic_replay": bool(descriptor.deterministic_replay),
            "matrix_power_value_derivation": bool(
                descriptor.matrix_power_value_derivation
            ),
            "host_matrixpower_authority": bool(
                descriptor.host_matrixpower_authority
            ),
            "host_square_matrix_requirement_authority": bool(
                descriptor.host_square_matrix_requirement_authority
            ),
            "numeric_exponent_evaluation_authority": bool(
                descriptor.numeric_exponent_evaluation_authority
            ),
            "floating_point_authority": bool(
                descriptor.floating_point_authority
            ),
            "canonical_state_persistence_authority": bool(
                descriptor.canonical_state_persistence_authority
            ),
            "canonical_vm81_mutation_authority": bool(
                descriptor.canonical_vm81_mutation_authority
            ),
            "canonical_hash72_commit_authority": bool(
                descriptor.canonical_hash72_commit_authority
            ),
            "canonical_hash216_commit_authority": bool(
                descriptor.canonical_hash216_commit_authority
            ),
            "external_egress_authority": bool(
                descriptor.external_egress_authority
            ),
        }

    def execute(self, node_id: int) -> VM81ExactMatrixPowerExecution:
        native = _Execution()
        status = int(
            self._lib.hhs_exact_pass220_i077_execute(
                int(node_id),
                ctypes.byref(native),
            )
        )
        if status != 0 or native.decision != 1:
            raise I077ExecutionError(
                f"I077_EXECUTION_REJECTED:{status}:{native.reason}"
            )
        return VM81ExactMatrixPowerExecution(
            schema=SCHEMA,
            node_id=int(native.node_id),
            source_node=_decode(bytes(native.source_node)),
            rows=int(native.rows),
            columns=int(native.columns),
            exponent_token=_decode(bytes(native.exponent_token)),
            exponent_token_degree=int(native.exponent_token_degree),
            cell_tokens=tuple(int(v) for v in native.cell_tokens),
            source_node_sha256=_decode(bytes(native.source_node_sha256)),
            ordered_cells_sha256=_decode(bytes(native.ordered_cells_sha256)),
            vm5184_address=int(native.vm5184_address),
            vm81_steps=int(native.vm81_steps),
            replay_vm81_steps=int(native.replay_vm81_steps),
            change_hash72=_decode(bytes(native.change_hash72)),
            receipt_hash72=_decode(bytes(native.receipt_hash72)),
            replay_hash72=_decode(bytes(native.replay_hash72)),
            proof_hash216=_decode(bytes(native.proof_hash216)),
            transition_hash216=_decode(bytes(native.transition_hash216)),
            source_identity_exact=bool(native.source_identity_exact),
            ordered_topology_verified=bool(native.ordered_topology_verified),
            exact_symbolic_node_executed=bool(
                native.exact_symbolic_node_executed
            ),
            exact_vm81_admission_verified=bool(
                native.exact_vm81_admission_verified
            ),
            atomic_frame_commit_verified=bool(
                native.atomic_frame_commit_verified
            ),
            hash72_receipt_verified=bool(native.hash72_receipt_verified),
            hash216_transition_identity_verified=bool(
                native.hash216_transition_identity_verified
            ),
            deterministic_replay_verified=bool(
                native.deterministic_replay_verified
            ),
            matrix_power_value_derived=bool(
                native.matrix_power_value_derived
            ),
            host_matrixpower_used=bool(native.host_matrixpower_used),
            square_matrix_requirement_imported=bool(
                native.square_matrix_requirement_imported
            ),
            numeric_exponent_evaluated=bool(
                native.numeric_exponent_evaluated
            ),
            canonical_state_persisted=bool(native.canonical_state_persisted),
            floating_point_authority=bool(native.floating_point_authority),
        )

    def execute_all(self) -> tuple[VM81ExactMatrixPowerExecution, ...]:
        return tuple(
            self.execute(node_id)
            for node_id in range(self.descriptor["node_count"])
        )


__all__ = [
    "I077ExecutionError",
    "NODE_M_WZ_X2",
    "NODE_M_XY_X4",
    "VM81ExactMatrixPowerExecution",
    "VM81ExactMatrixPowerExecutor",
]

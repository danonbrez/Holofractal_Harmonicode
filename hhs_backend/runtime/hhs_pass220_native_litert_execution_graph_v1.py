"""Pass 220 LiteRT2 native operator graph lowered into NumPy1/HARMONICODE.

C11 owns graph topology validation. NumPy1 owns numerical execution. This
module only binds tensor names/values to the two native compatibility surfaces.
"""
from __future__ import annotations

import ctypes
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_installer.canonical import hash216
from hhs_runtime.hhs_pass220_numpy_harmonicode_array_v1 import (
    HHSNumPyArray,
    HHSNumPyEngine,
)

SCHEMA = "HHS_PASS_220_LITERT2_NATIVE_EXECUTION_GRAPH_V1"
MAX_TENSORS = 32
MAX_OPS = 64
MAX_RANK = 8
HASH216_BYTES = 216

TENSOR_INPUT = 0x01
TENSOR_OUTPUT = 0x02
TENSOR_CONSTANT = 0x04

DTYPE_INT64 = 1
DTYPE_FLOAT64 = 2

OP_ADD = 1
OP_SUBTRACT = 2
OP_MULTIPLY = 3

_DTYPE_CODE = {"int64": DTYPE_INT64, "float64": DTYPE_FLOAT64}
_OP_CODE = {"add": OP_ADD, "subtract": OP_SUBTRACT, "multiply": OP_MULTIPLY}


class NativeLiteRTGraphError(RuntimeError):
    pass


class _Tensor(ctypes.Structure):
    _fields_ = [
        ("tensor_id", ctypes.c_uint32),
        ("dtype", ctypes.c_uint32),
        ("rank", ctypes.c_uint32),
        ("flags", ctypes.c_uint32),
        ("dims", ctypes.c_uint64 * MAX_RANK),
    ]


class _Operation(ctypes.Structure):
    _fields_ = [
        ("operation_id", ctypes.c_uint32),
        ("kind", ctypes.c_uint32),
        ("left_tensor_id", ctypes.c_uint32),
        ("right_tensor_id", ctypes.c_uint32),
        ("output_tensor_id", ctypes.c_uint32),
        ("reserved0", ctypes.c_uint32),
    ]


class _Descriptor(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("graph_id", ctypes.c_uint32),
        ("tensor_count", ctypes.c_uint32),
        ("operation_count", ctypes.c_uint32),
        ("input_count", ctypes.c_uint32),
        ("output_count", ctypes.c_uint32),
        ("reserved0", ctypes.c_uint32),
        ("graph_identity_hash216", ctypes.c_char * (HASH216_BYTES + 1)),
        ("tensors", _Tensor * MAX_TENSORS),
        ("operations", _Operation * MAX_OPS),
    ]


class _Registration(ctypes.Structure):
    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("version", ctypes.c_uint32),
        ("graph_id", ctypes.c_uint32),
        ("tensor_count", ctypes.c_uint32),
        ("operation_count", ctypes.c_uint32),
        ("input_count", ctypes.c_uint32),
        ("output_count", ctypes.c_uint32),
        ("reserved0", ctypes.c_uint32),
        ("graph_fingerprint64", ctypes.c_uint64),
        ("graph_identity_hash216", ctypes.c_char * (HASH216_BYTES + 1)),
        ("tensors", _Tensor * MAX_TENSORS),
        ("operations", _Operation * MAX_OPS),
        ("topology_authority", ctypes.c_uint8),
        ("numeric_execution_authority", ctypes.c_uint8),
        ("vm81_mutation_authority", ctypes.c_uint8),
        ("hash72_commit_authority", ctypes.c_uint8),
        ("hash216_persistence_authority", ctypes.c_uint8),
        ("host_float_canonical_authority", ctypes.c_uint8),
        ("numpy1_numeric_lowering_required", ctypes.c_uint8),
        ("reserved1", ctypes.c_uint8),
    ]


@dataclass(frozen=True)
class LiteRT2TensorSpec:
    name: str
    dtype: str
    shape: tuple[int, ...]
    input: bool = False
    output: bool = False
    constant: bool = False


@dataclass(frozen=True)
class LiteRT2OperationSpec:
    name: str
    kind: str
    left: str
    right: str
    output: str


@dataclass(frozen=True)
class LiteRT2ExecutionResult:
    schema: str
    model_identity_hash216: str
    graph_identity_hash216: str
    graph_fingerprint64: int
    outputs: Mapping[str, HHSNumPyArray]
    witness: Mapping[str, Any]


def _u32(domain: str, value: str) -> int:
    result = int.from_bytes(
        sha256(f"{domain}\0{value}".encode("utf-8")).digest()[:4],
        "big",
    )
    return result or 1


def _flags(spec: LiteRT2TensorSpec) -> int:
    value = 0
    if spec.input:
        value |= TENSOR_INPUT
    if spec.output:
        value |= TENSOR_OUTPUT
    if spec.constant:
        value |= TENSOR_CONSTANT
    return value


class NativeLiteRTExecutionGraph:
    def __init__(
        self,
        *,
        graph_library: str | Path,
        numpy1_library: str | Path,
        model_identity_hash216: str,
        graph_name: str,
        tensors: Sequence[LiteRT2TensorSpec],
        operations: Sequence[LiteRT2OperationSpec],
        constants: Mapping[str, Any] | None = None,
    ):
        if len(model_identity_hash216) != HASH216_BYTES:
            raise NativeLiteRTGraphError(
                "HHS_LITERT2_MODEL_HASH216_WIDTH_INVALID"
            )
        if not 1 <= len(tensors) <= MAX_TENSORS:
            raise NativeLiteRTGraphError("HHS_LITERT2_TENSOR_COUNT_INVALID")
        if not 1 <= len(operations) <= MAX_OPS:
            raise NativeLiteRTGraphError("HHS_LITERT2_OPERATION_COUNT_INVALID")
        if len({item.name for item in tensors}) != len(tensors):
            raise NativeLiteRTGraphError("HHS_LITERT2_DUPLICATE_TENSOR_NAME")
        if len({item.name for item in operations}) != len(operations):
            raise NativeLiteRTGraphError("HHS_LITERT2_DUPLICATE_OPERATION_NAME")

        self.model_identity_hash216 = model_identity_hash216
        self.graph_name = graph_name
        self.tensor_specs = tuple(tensors)
        self.operation_specs = tuple(operations)
        self.constants = dict(constants or {})
        self.numpy = HHSNumPyEngine(numpy1_library)

        self._lib = ctypes.CDLL(str(Path(graph_library)))
        self._lib.hhs_litert_native_graph_version.restype = ctypes.c_uint32
        self._lib.hhs_litert_native_graph_register.argtypes = [
            ctypes.POINTER(_Descriptor),
            ctypes.POINTER(_Registration),
        ]
        self._lib.hhs_litert_native_graph_register.restype = ctypes.c_int
        self._lib.hhs_litert_native_graph_validate_registration.argtypes = [
            ctypes.POINTER(_Registration),
        ]
        self._lib.hhs_litert_native_graph_validate_registration.restype = ctypes.c_int
        if int(self._lib.hhs_litert_native_graph_version()) != 1:
            raise NativeLiteRTGraphError(
                "HHS_LITERT2_NATIVE_GRAPH_VERSION_MISMATCH"
            )

        self._tensor_by_name = {item.name: item for item in self.tensor_specs}
        self._tensor_ids = {
            item.name: _u32(
                "HHS-P220-LITERT2-TENSOR",
                f"{model_identity_hash216}:{graph_name}:{item.name}",
            )
            for item in self.tensor_specs
        }
        if len(set(self._tensor_ids.values())) != len(self._tensor_ids):
            raise NativeLiteRTGraphError("HHS_LITERT2_TENSOR_ID_COLLISION")

        self.graph_identity_hash216 = hash216(
            {
                "schema": SCHEMA,
                "model_identity_hash216": model_identity_hash216,
                "graph_name": graph_name,
                "tensors": [
                    {
                        "name": item.name,
                        "dtype": item.dtype,
                        "shape": list(item.shape),
                        "flags": _flags(item),
                    }
                    for item in self.tensor_specs
                ],
                "operations": [
                    {
                        "name": item.name,
                        "kind": item.kind,
                        "left": item.left,
                        "right": item.right,
                        "output": item.output,
                    }
                    for item in self.operation_specs
                ],
            },
            domain="HHS-P220-LITERT2-GRAPH",
        )
        if len(self.graph_identity_hash216) != HASH216_BYTES:
            raise NativeLiteRTGraphError(
                "HHS_LITERT2_GRAPH_HASH216_WIDTH_INVALID"
            )
        self._registration = self._register()

    def _register(self) -> _Registration:
        descriptor = _Descriptor()
        descriptor.struct_size = ctypes.sizeof(_Descriptor)
        descriptor.version = 1
        descriptor.graph_id = _u32(
            "HHS-P220-LITERT2-GRAPH-ID",
            f"{self.model_identity_hash216}:{self.graph_name}",
        )
        descriptor.tensor_count = len(self.tensor_specs)
        descriptor.operation_count = len(self.operation_specs)
        descriptor.input_count = sum(item.input for item in self.tensor_specs)
        descriptor.output_count = sum(item.output for item in self.tensor_specs)
        descriptor.graph_identity_hash216 = self.graph_identity_hash216.encode(
            "ascii"
        )

        for index, item in enumerate(self.tensor_specs):
            dtype = str(item.dtype).lower()
            if dtype not in _DTYPE_CODE:
                raise NativeLiteRTGraphError(
                    f"HHS_LITERT2_EXECUTION_DTYPE_NOT_ADMITTED:{item.dtype}"
                )
            if len(item.shape) > MAX_RANK:
                raise NativeLiteRTGraphError(
                    "HHS_LITERT2_TENSOR_RANK_INVALID"
                )
            if any(
                isinstance(dim, bool) or not isinstance(dim, int) or dim <= 0
                for dim in item.shape
            ):
                raise NativeLiteRTGraphError(
                    "HHS_LITERT2_TENSOR_DIMENSION_INVALID"
                )
            if item.input and item.constant:
                raise NativeLiteRTGraphError(
                    "HHS_LITERT2_TENSOR_INPUT_CONSTANT_CONFLICT"
                )
            native = descriptor.tensors[index]
            native.tensor_id = self._tensor_ids[item.name]
            native.dtype = _DTYPE_CODE[dtype]
            native.rank = len(item.shape)
            native.flags = _flags(item)
            for dim_index, dim in enumerate(item.shape):
                native.dims[dim_index] = dim

        for index, item in enumerate(self.operation_specs):
            kind = str(item.kind).lower()
            if kind not in _OP_CODE:
                raise NativeLiteRTGraphError(
                    f"HHS_LITERT2_OPERATION_NOT_ADMITTED:{item.kind}"
                )
            for tensor_name in (item.left, item.right, item.output):
                if tensor_name not in self._tensor_by_name:
                    raise NativeLiteRTGraphError(
                        f"HHS_LITERT2_UNKNOWN_TENSOR:{tensor_name}"
                    )
            native = descriptor.operations[index]
            native.operation_id = _u32(
                "HHS-P220-LITERT2-OP",
                f"{self.graph_identity_hash216}:{item.name}",
            )
            native.kind = _OP_CODE[kind]
            native.left_tensor_id = self._tensor_ids[item.left]
            native.right_tensor_id = self._tensor_ids[item.right]
            native.output_tensor_id = self._tensor_ids[item.output]

        registration = _Registration()
        status = int(
            self._lib.hhs_litert_native_graph_register(
                ctypes.byref(descriptor),
                ctypes.byref(registration),
            )
        )
        if status != 0:
            raise NativeLiteRTGraphError(
                f"HHS_LITERT2_GRAPH_REGISTRATION_REJECTED:{status}"
            )
        validation = int(
            self._lib.hhs_litert_native_graph_validate_registration(
                ctypes.byref(registration)
            )
        )
        if validation != 0:
            raise NativeLiteRTGraphError(
                f"HHS_LITERT2_GRAPH_REGISTRATION_INVALID:{validation}"
            )
        return registration

    @property
    def graph_fingerprint64(self) -> int:
        return int(self._registration.graph_fingerprint64)

    def _array_for_spec(self, spec: LiteRT2TensorSpec, value: Any) -> HHSNumPyArray:
        array = self.numpy.array(value, dtype=spec.dtype)
        if array.shape != spec.shape:
            raise NativeLiteRTGraphError(
                f"HHS_LITERT2_INPUT_SHAPE_MISMATCH:{spec.name}:"
                f"{array.shape}!={spec.shape}"
            )
        return array

    def execute(self, inputs: Mapping[str, Any]) -> LiteRT2ExecutionResult:
        values: dict[str, HHSNumPyArray] = {}
        input_names = {item.name for item in self.tensor_specs if item.input}
        if set(inputs) != input_names:
            raise NativeLiteRTGraphError(
                "HHS_LITERT2_INPUT_SET_MISMATCH:"
                f"expected={sorted(input_names)}:observed={sorted(inputs)}"
            )

        for spec in self.tensor_specs:
            if spec.input:
                values[spec.name] = self._array_for_spec(
                    spec, inputs[spec.name]
                )
            elif spec.constant:
                if spec.name not in self.constants:
                    raise NativeLiteRTGraphError(
                        f"HHS_LITERT2_CONSTANT_MISSING:{spec.name}"
                    )
                values[spec.name] = self._array_for_spec(
                    spec, self.constants[spec.name]
                )

        operation_witnesses: list[dict[str, Any]] = []
        for op in self.operation_specs:
            try:
                left = values[op.left]
                right = values[op.right]
            except KeyError as exc:
                raise NativeLiteRTGraphError(
                    f"HHS_LITERT2_TOPOLOGY_VALUE_UNAVAILABLE:{exc.args[0]}"
                ) from exc
            if op.kind == "add":
                result = self.numpy.add(left, right)
            elif op.kind == "subtract":
                result = self.numpy.subtract(left, right)
            elif op.kind == "multiply":
                result = self.numpy.multiply(left, right)
            else:
                raise NativeLiteRTGraphError(
                    f"HHS_LITERT2_OPERATION_NOT_ADMITTED:{op.kind}"
                )
            output_spec = self._tensor_by_name[op.output]
            if result.dtype != output_spec.dtype or result.shape != output_spec.shape:
                raise NativeLiteRTGraphError(
                    f"HHS_LITERT2_NUMPY1_OUTPUT_CONTRACT_MISMATCH:{op.output}"
                )
            values[op.output] = result
            operation_witnesses.append(
                {
                    "operation": op.name,
                    "kind": op.kind,
                    "left": op.left,
                    "right": op.right,
                    "output": op.output,
                    "dtype": result.dtype,
                    "shape": list(result.shape),
                    "float64_ieee_bits": (
                        [f"{bits:016x}" for bits in result.ieee_bits()]
                        if result.dtype == "float64"
                        else None
                    ),
                    "bigint_5184_sha256": [
                        sha256(item.encode("ascii")).hexdigest()
                        for item in result.bigint_5184()
                    ],
                }
            )

        outputs = {
            item.name: values[item.name]
            for item in self.tensor_specs
            if item.output
        }
        witness = {
            "schema": SCHEMA + "_EXECUTION_WITNESS",
            "model_identity_hash216": self.model_identity_hash216,
            "graph_identity_hash216": self.graph_identity_hash216,
            "graph_fingerprint64": self.graph_fingerprint64,
            "operations": operation_witnesses,
            "numeric_authority": "NUMPY1_HARMONICODE",
            "host_float_canonical_authority": False,
            "vm81_mutation_authority": False,
            "hash72_commit_authority": False,
            "hash216_persistence_authority": False,
        }
        witness["witness_hash216"] = hash216(
            witness,
            domain="HHS-P220-LITERT2-EXECUTION-WITNESS",
        )
        return LiteRT2ExecutionResult(
            schema=SCHEMA,
            model_identity_hash216=self.model_identity_hash216,
            graph_identity_hash216=self.graph_identity_hash216,
            graph_fingerprint64=self.graph_fingerprint64,
            outputs=outputs,
            witness=witness,
        )


def litert2_contract() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "native_graph_topology_authority": True,
        "native_graph_numeric_authority": False,
        "numpy1_numeric_authority": True,
        "admitted_execution_dtypes": ("int64", "float64"),
        "admitted_operations": ("add", "subtract", "multiply"),
        "float32_litert_metadata_registrable": True,
        "float32_canonical_execution_admitted": False,
        "quantized_litert_metadata_registrable": True,
        "quantized_canonical_execution_admitted": False,
        "host_float_canonical_authority": False,
        "vm81_mutation_authority": False,
        "hash72_commit_authority": False,
        "hash216_persistence_authority": False,
    }


__all__ = [
    "LiteRT2ExecutionResult",
    "LiteRT2OperationSpec",
    "LiteRT2TensorSpec",
    "NativeLiteRTExecutionGraph",
    "NativeLiteRTGraphError",
    "litert2_contract",
]

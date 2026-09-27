"""Pass 220 NumPy1: HARMONICODE-native NumPy compatibility array engine.

NumPy is an ingress/egress contract. Canonical interior scalar arithmetic uses
exact integers/rationals and inherited HHS IEEE/phase/BigInt constructors.
The C11 native kernel owns shape broadcasting and row-major index projection.
"""
from __future__ import annotations

import ctypes
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
import struct
from typing import Any, Iterable, Sequence, Tuple

from hhs_runtime.hhs_pass220_desi_lane5_parallel_exact_egress_v1 import (
    fraction_to_binary64_bits,
)
from hhs_runtime.hhs_pass220_g3_4711_symbolic_numeric_constructor_v1 import (
    build_solver_constructor,
    validate_solver_constructor,
)
from hhs_runtime.hhs_pass220_g3_ieee_scalar_involution_v1 import (
    exact_dyadic,
    split_fields,
)
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    VM81_CELLS,
    deserialize_offsets_5184,
    offsets_to_bigint,
    serialize_offsets_5184,
)

SCHEMA = "HHS_PASS_220_NUMPY1_HARMONICODE_ARRAY_ENGINE_V1"
MAX_RANK = 8
SUPPORTED_DTYPES = ("int64", "float64")

_METHOD_OK = 0
_ERR_BROADCAST = 4


class HHSNumPyCompatibilityError(ValueError):
    pass


class _NativeShape(ctypes.Structure):
    _fields_ = [
        ("rank", ctypes.c_uint32),
        ("dims", ctypes.c_uint64 * MAX_RANK),
    ]


def _shape_record(shape: Sequence[int]) -> _NativeShape:
    values = tuple(int(value) for value in shape)
    if len(values) > MAX_RANK:
        raise HHSNumPyCompatibilityError("HHS_NUMPY1_RANK_EXCEEDS_NATIVE_LIMIT")
    if any(value <= 0 for value in values):
        raise HHSNumPyCompatibilityError("HHS_NUMPY1_ZERO_OR_NEGATIVE_DIMENSION")
    record = _NativeShape()
    record.rank = len(values)
    for index, value in enumerate(values):
        record.dims[index] = value
    return record


class NativeArrayKernel:
    def __init__(self, library_path: str | Path):
        self.library_path = str(Path(library_path))
        self._lib = ctypes.CDLL(self.library_path)
        self._lib.hhs_numpy_native_array_kernel_version.restype = ctypes.c_uint32
        self._lib.hhs_numpy_native_broadcast_shape.argtypes = [
            ctypes.POINTER(_NativeShape),
            ctypes.POINTER(_NativeShape),
            ctypes.POINTER(_NativeShape),
        ]
        self._lib.hhs_numpy_native_broadcast_shape.restype = ctypes.c_int
        self._lib.hhs_numpy_native_element_count.argtypes = [
            ctypes.POINTER(_NativeShape),
            ctypes.POINTER(ctypes.c_uint64),
        ]
        self._lib.hhs_numpy_native_element_count.restype = ctypes.c_int
        self._lib.hhs_numpy_native_project_broadcast_index.argtypes = [
            ctypes.POINTER(_NativeShape),
            ctypes.c_uint64,
            ctypes.POINTER(_NativeShape),
            ctypes.POINTER(ctypes.c_uint64),
        ]
        self._lib.hhs_numpy_native_project_broadcast_index.restype = ctypes.c_int
        if int(self._lib.hhs_numpy_native_array_kernel_version()) != 1:
            raise HHSNumPyCompatibilityError(
                "HHS_NUMPY1_NATIVE_ARRAY_KERNEL_VERSION_MISMATCH"
            )

    def broadcast_shape(
        self,
        left: Sequence[int],
        right: Sequence[int],
    ) -> Tuple[int, ...]:
        lhs = _shape_record(left)
        rhs = _shape_record(right)
        out = _NativeShape()
        status = int(
            self._lib.hhs_numpy_native_broadcast_shape(
                ctypes.byref(lhs),
                ctypes.byref(rhs),
                ctypes.byref(out),
            )
        )
        if status == _ERR_BROADCAST:
            raise HHSNumPyCompatibilityError(
                f"operands could not be broadcast together with shapes {tuple(left)} {tuple(right)}"
            )
        if status != _METHOD_OK:
            raise HHSNumPyCompatibilityError(
                f"HHS_NUMPY1_NATIVE_BROADCAST_FAILED:{status}"
            )
        return tuple(int(out.dims[i]) for i in range(int(out.rank)))

    def element_count(self, shape: Sequence[int]) -> int:
        record = _shape_record(shape)
        out = ctypes.c_uint64()
        status = int(
            self._lib.hhs_numpy_native_element_count(
                ctypes.byref(record),
                ctypes.byref(out),
            )
        )
        if status != _METHOD_OK:
            raise HHSNumPyCompatibilityError(
                f"HHS_NUMPY1_NATIVE_ELEMENT_COUNT_FAILED:{status}"
            )
        return int(out.value)

    def project_index(
        self,
        output_shape: Sequence[int],
        output_linear_index: int,
        input_shape: Sequence[int],
    ) -> int:
        out_shape = _shape_record(output_shape)
        in_shape = _shape_record(input_shape)
        result = ctypes.c_uint64()
        status = int(
            self._lib.hhs_numpy_native_project_broadcast_index(
                ctypes.byref(out_shape),
                int(output_linear_index),
                ctypes.byref(in_shape),
                ctypes.byref(result),
            )
        )
        if status != _METHOD_OK:
            raise HHSNumPyCompatibilityError(
                f"HHS_NUMPY1_NATIVE_INDEX_PROJECTION_FAILED:{status}"
            )
        return int(result.value)


def _ieee64_bits_from_float(value: float) -> int:
    if not isinstance(value, float):
        raise HHSNumPyCompatibilityError("HHS_NUMPY1_FLOAT64_INGRESS_REQUIRES_FLOAT")
    return int.from_bytes(struct.pack(">d", value), "big", signed=False)


def _float_from_ieee64_bits(bits: int) -> float:
    return struct.unpack(">d", int(bits).to_bytes(8, "big", signed=False))[0]


def _exact_fraction_from_binary64_bits(bits: int) -> Fraction:
    fields = split_fields(int(bits), "binary64")
    result = exact_dyadic(fields, "binary64")
    if result is None:
        raise HHSNumPyCompatibilityError(
            "HHS_NUMPY1_NONFINITE_FLOAT64_NOT_YET_ADMITTED"
        )
    return Fraction(result[0], result[1])


def _integer_to_base9_offsets(value: int) -> Tuple[int, ...]:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise HHSNumPyCompatibilityError(
            "HHS_NUMPY1_BIGINT_OFFSET_SOURCE_MUST_BE_NONNEGATIVE_INTEGER"
        )
    remaining = value
    digits = []
    for _ in range(VM81_CELLS):
        digits.append(remaining % 9)
        remaining //= 9
    if remaining:
        raise HHSNumPyCompatibilityError(
            "HHS_NUMPY1_BIGINT_OFFSET_SOURCE_EXCEEDS_VM81_BASE9_CAPACITY"
        )
    return tuple(digits)


def _base9_offsets_to_integer(offsets: Sequence[int]) -> int:
    if len(tuple(offsets)) != VM81_CELLS:
        raise HHSNumPyCompatibilityError(
            "HHS_NUMPY1_VM81_OFFSET_WIDTH_REQUIRED"
        )
    result = 0
    multiplier = 1
    for digit in offsets:
        if isinstance(digit, bool) or not isinstance(digit, int) or not 0 <= digit <= 8:
            raise HHSNumPyCompatibilityError(
                "HHS_NUMPY1_VM81_OFFSET_DIGIT_INVALID"
            )
        result += digit * multiplier
        multiplier *= 9
    return result


def _int64_zigzag(value: int) -> int:
    if not -(1 << 63) <= value < (1 << 63):
        raise HHSNumPyCompatibilityError("HHS_NUMPY1_INT64_INGRESS_OUT_OF_RANGE")
    return value << 1 if value >= 0 else ((-value) << 1) - 1


def _zigzag_to_int64(value: int) -> int:
    return value >> 1 if value % 2 == 0 else -((value + 1) >> 1)


def _wrap_int64(value: int) -> int:
    unsigned = value & ((1 << 64) - 1)
    return unsigned if unsigned < (1 << 63) else unsigned - (1 << 64)


@dataclass(frozen=True)
class HHSNumPyScalar:
    dtype: str
    exact_value: Fraction
    pre_round_exact: Fraction
    ieee_bits: int | None
    bigint_5184: str
    scalar_bigint_projection: int
    ingress_spelling: str

    @classmethod
    def from_float64(cls, value: float) -> "HHSNumPyScalar":
        bits = _ieee64_bits_from_float(value)
        exact = _exact_fraction_from_binary64_bits(bits)
        offsets = _integer_to_base9_offsets(bits)
        serialized = serialize_offsets_5184(offsets)
        return cls(
            dtype="float64",
            exact_value=exact,
            pre_round_exact=exact,
            ieee_bits=bits,
            bigint_5184=serialized,
            scalar_bigint_projection=offsets_to_bigint(offsets),
            ingress_spelling=repr(value),
        )

    @classmethod
    def from_float64_bits(
        cls,
        bits: int,
        *,
        pre_round_exact: Fraction | None = None,
    ) -> "HHSNumPyScalar":
        if isinstance(bits, bool) or not isinstance(bits, int) or not 0 <= bits < (1 << 64):
            raise HHSNumPyCompatibilityError("HHS_NUMPY1_BINARY64_BITS_INVALID")
        exact = _exact_fraction_from_binary64_bits(bits)
        offsets = _integer_to_base9_offsets(bits)
        serialized = serialize_offsets_5184(offsets)
        return cls(
            dtype="float64",
            exact_value=exact,
            pre_round_exact=Fraction(
                exact if pre_round_exact is None else pre_round_exact
            ),
            ieee_bits=bits,
            bigint_5184=serialized,
            scalar_bigint_projection=offsets_to_bigint(offsets),
            ingress_spelling=f"0x{bits:016x}",
        )

    @classmethod
    def from_int64(cls, value: int) -> "HHSNumPyScalar":
        if isinstance(value, bool) or not isinstance(value, int):
            raise HHSNumPyCompatibilityError("HHS_NUMPY1_INT64_INGRESS_REQUIRES_INT")
        wrapped = _wrap_int64(value)
        zigzag = _int64_zigzag(wrapped)
        offsets = _integer_to_base9_offsets(zigzag)
        serialized = serialize_offsets_5184(offsets)
        exact = Fraction(wrapped, 1)
        return cls(
            dtype="int64",
            exact_value=exact,
            pre_round_exact=exact,
            ieee_bits=None,
            bigint_5184=serialized,
            scalar_bigint_projection=offsets_to_bigint(offsets),
            ingress_spelling=str(value),
        )

    def recover_ingress_identity(self) -> int:
        offsets = deserialize_offsets_5184(self.bigint_5184)
        identity = _base9_offsets_to_integer(offsets)
        if self.dtype == "float64":
            return identity
        if self.dtype == "int64":
            return _zigzag_to_int64(identity)
        raise HHSNumPyCompatibilityError("HHS_NUMPY1_DTYPE_UNSUPPORTED")

    def to_python_scalar(self) -> int | float:
        if self.dtype == "float64":
            assert self.ieee_bits is not None
            return _float_from_ieee64_bits(self.ieee_bits)
        if self.dtype == "int64":
            return int(self.exact_value)
        raise HHSNumPyCompatibilityError("HHS_NUMPY1_DTYPE_UNSUPPORTED")

    def palindromic_symbolic_witness(self) -> dict[str, Any]:
        if self.dtype != "float64" or self.ieee_bits is None:
            return {
                "schema": "HHS_PASS_220_NUMPY1_INT64_BIGINT_WITNESS_V1",
                "dtype": self.dtype,
                "bigint_5184": self.bigint_5184,
                "scalar_bigint_projection": self.scalar_bigint_projection,
                "recovered_int64": self.recover_ingress_identity(),
                "host_float_arithmetic_used": False,
            }
        offsets = deserialize_offsets_5184(self.bigint_5184)
        constructor = build_solver_constructor(
            (
                "NUMPY_FLOAT64_EXACT="
                f"{self.exact_value.numerator}/{self.exact_value.denominator};"
                f"PRE_ROUND={self.pre_round_exact.numerator}/"
                f"{self.pre_round_exact.denominator}"
            ),
            self.ieee_bits.to_bytes(8, "big"),
            "binary64",
            offsets,
        )
        validation = validate_solver_constructor(constructor)
        return {
            "schema": "HHS_PASS_220_NUMPY1_FLOAT64_PALINDROMIC_WITNESS_V1",
            "dtype": "float64",
            "ieee_bits": f"{self.ieee_bits:016x}",
            "bigint_5184": self.bigint_5184,
            "scalar_bigint_projection": self.scalar_bigint_projection,
            "recovered_ieee_bits": f"{self.recover_ingress_identity():016x}",
            "constructor": constructor,
            "validation": validation,
            "host_float_arithmetic_used": False,
        }


def _flatten_rectangular(value: Any) -> tuple[Tuple[int, ...], list[Any]]:
    if isinstance(value, HHSNumPyArray):
        return value.shape, [item for item in value._data]
    if not isinstance(value, (list, tuple)):
        return (), [value]
    if not value:
        raise HHSNumPyCompatibilityError(
            "HHS_NUMPY1_EMPTY_ARRAY_NOT_YET_ADMITTED"
        )
    child_shapes = []
    flat: list[Any] = []
    for item in value:
        child_shape, child_flat = _flatten_rectangular(item)
        child_shapes.append(child_shape)
        flat.extend(child_flat)
    if any(shape != child_shapes[0] for shape in child_shapes[1:]):
        raise HHSNumPyCompatibilityError(
            "setting an array element with a sequence"
        )
    return (len(value),) + child_shapes[0], flat


def _rebuild_nested(shape: Sequence[int], values: Sequence[Any]) -> Any:
    shape_tuple = tuple(shape)
    if not shape_tuple:
        return values[0]
    if len(shape_tuple) == 1:
        return list(values)
    stride = 1
    for dim in shape_tuple[1:]:
        stride *= dim
    return [
        _rebuild_nested(shape_tuple[1:], values[index * stride : (index + 1) * stride])
        for index in range(shape_tuple[0])
    ]


def _promoted_dtype(left: str, right: str) -> str:
    if left == "float64" or right == "float64":
        return "float64"
    return "int64"


def _binary_scalar(
    left: HHSNumPyScalar,
    right: HHSNumPyScalar,
    operation: str,
) -> HHSNumPyScalar:
    dtype = _promoted_dtype(left.dtype, right.dtype)
    a = left.exact_value
    b = right.exact_value
    if operation == "add":
        exact = a + b
    elif operation == "subtract":
        exact = a - b
    elif operation == "multiply":
        exact = a * b
    else:
        raise HHSNumPyCompatibilityError(
            f"HHS_NUMPY1_OPERATION_UNSUPPORTED:{operation}"
        )

    if dtype == "int64":
        if exact.denominator != 1:
            raise HHSNumPyCompatibilityError("HHS_NUMPY1_INT64_NONINTEGER_RESULT")
        wrapped = _wrap_int64(exact.numerator)
        scalar = HHSNumPyScalar.from_int64(wrapped)
        return HHSNumPyScalar(
            **{
                **scalar.__dict__,
                "pre_round_exact": exact,
            }
        )

    bits = fraction_to_binary64_bits(exact)
    return HHSNumPyScalar.from_float64_bits(bits, pre_round_exact=exact)


class HHSNumPyArray:
    def __init__(
        self,
        *,
        engine: "HHSNumPyEngine",
        shape: Sequence[int],
        dtype: str,
        data: Sequence[HHSNumPyScalar],
    ):
        self._engine = engine
        self.shape = tuple(int(value) for value in shape)
        self.dtype = dtype
        self._data = tuple(data)
        expected = 1 if not self.shape else engine.kernel.element_count(self.shape)
        if expected != len(self._data):
            raise HHSNumPyCompatibilityError("HHS_NUMPY1_ARRAY_SIZE_MISMATCH")

    @property
    def ndim(self) -> int:
        return len(self.shape)

    @property
    def size(self) -> int:
        return len(self._data)

    def tolist(self) -> Any:
        values = [item.to_python_scalar() for item in self._data]
        return _rebuild_nested(self.shape, values)

    def ieee_bits(self) -> Tuple[int, ...]:
        if self.dtype != "float64":
            raise HHSNumPyCompatibilityError("HHS_NUMPY1_IEEE_BITS_FLOAT64_ONLY")
        return tuple(int(item.ieee_bits) for item in self._data if item.ieee_bits is not None)

    def bigint_5184(self) -> Tuple[str, ...]:
        return tuple(item.bigint_5184 for item in self._data)

    def __add__(self, other: Any) -> "HHSNumPyArray":
        return self._engine.add(self, other)

    def __sub__(self, other: Any) -> "HHSNumPyArray":
        return self._engine.subtract(self, other)

    def __mul__(self, other: Any) -> "HHSNumPyArray":
        return self._engine.multiply(self, other)


class HHSNumPyEngine:
    def __init__(self, native_library_path: str | Path):
        self.kernel = NativeArrayKernel(native_library_path)

    def array(self, value: Any, *, dtype: str) -> HHSNumPyArray:
        dtype_name = str(dtype)
        if dtype_name not in SUPPORTED_DTYPES:
            raise HHSNumPyCompatibilityError(
                f"HHS_NUMPY1_DTYPE_UNSUPPORTED:{dtype_name}"
            )
        shape, flat = _flatten_rectangular(value)
        scalars = []
        for item in flat:
            if dtype_name == "float64":
                scalars.append(
                    item
                    if isinstance(item, HHSNumPyScalar) and item.dtype == "float64"
                    else HHSNumPyScalar.from_float64(float(item))
                )
            else:
                if isinstance(item, bool):
                    raise HHSNumPyCompatibilityError(
                        "HHS_NUMPY1_BOOL_TO_INT64_NOT_YET_ADMITTED"
                    )
                scalars.append(
                    item
                    if isinstance(item, HHSNumPyScalar) and item.dtype == "int64"
                    else HHSNumPyScalar.from_int64(int(item))
                )
        return HHSNumPyArray(
            engine=self,
            shape=shape,
            dtype=dtype_name,
            data=scalars,
        )

    def asarray(self, value: Any, *, dtype: str | None = None) -> HHSNumPyArray:
        if isinstance(value, HHSNumPyArray):
            if dtype is None or dtype == value.dtype:
                return value
            return self.array(value.tolist(), dtype=dtype)
        if dtype is None:
            raise HHSNumPyCompatibilityError(
                "HHS_NUMPY1_EXPLICIT_DTYPE_REQUIRED"
            )
        return self.array(value, dtype=dtype)

    def _coerce_operand(
        self,
        value: Any,
        *,
        preferred_dtype: str,
    ) -> HHSNumPyArray:
        if isinstance(value, HHSNumPyArray):
            return value
        if preferred_dtype == "float64":
            return self.array(value, dtype="float64")
        return self.array(value, dtype="int64")

    def _binary(
        self,
        left: Any,
        right: Any,
        operation: str,
    ) -> HHSNumPyArray:
        if not isinstance(left, HHSNumPyArray):
            if isinstance(right, HHSNumPyArray):
                left = self._coerce_operand(left, preferred_dtype=right.dtype)
            else:
                left = self.array(left, dtype="float64")
        right = self._coerce_operand(right, preferred_dtype=left.dtype)

        out_shape = self.kernel.broadcast_shape(left.shape, right.shape)
        out_count = 1 if not out_shape else self.kernel.element_count(out_shape)
        result = []
        for output_index in range(out_count):
            li = self.kernel.project_index(out_shape, output_index, left.shape)
            ri = self.kernel.project_index(out_shape, output_index, right.shape)
            result.append(
                _binary_scalar(left._data[li], right._data[ri], operation)
            )
        return HHSNumPyArray(
            engine=self,
            shape=out_shape,
            dtype=_promoted_dtype(left.dtype, right.dtype),
            data=result,
        )

    def add(self, left: Any, right: Any) -> HHSNumPyArray:
        return self._binary(left, right, "add")

    def subtract(self, left: Any, right: Any) -> HHSNumPyArray:
        return self._binary(left, right, "subtract")

    def multiply(self, left: Any, right: Any) -> HHSNumPyArray:
        return self._binary(left, right, "multiply")


def numpy1_contract(engine: HHSNumPyEngine) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "numpy_external_contract_target": True,
        "supported_dtypes": SUPPORTED_DTYPES,
        "supported_operations": ("array", "asarray", "add", "subtract", "multiply"),
        "native_broadcast_kernel": True,
        "native_broadcast_kernel_version": 1,
        "float64_ingress_preserves_ieee_bits": True,
        "float64_internal_pre_round_symbolic_exact": True,
        "float64_rounding": "INTEGER_ONLY_NEAREST_EVEN_BINARY64",
        "float64_palindromic_full_phase_constructor": "PASS220_I033",
        "bigint_serialization_characters_per_scalar": 5184,
        "bigint_serialization_is_value_bound": True,
        "bigint_value_binding": "IEEE_OR_ZIGZAG_INTEGER_TO_BASE9_VM81_OFFSETS",
        "host_float_arithmetic_canonical_authority": False,
        "numpy_internal_dependency_required": False,
        "vm81_mutation_authority": False,
        "hash72_commit_authority": False,
        "hash216_persistence_authority": False,
    }


__all__ = [
    "HHSNumPyArray",
    "HHSNumPyCompatibilityError",
    "HHSNumPyEngine",
    "HHSNumPyScalar",
    "NativeArrayKernel",
    "numpy1_contract",
]

from __future__ import annotations

import ctypes
from ctypes import POINTER, c_uint32

from hhs_python.runtime import hhs_exact_ctypes_bridge as exact_mod
from hhs_python.runtime.hhs_pass168_ctypes_bridge import (
    HHS_EXACT_STATUS_OK,
    HHSPass168Matrix3,
    HHSPass168Rational,
    matrix_dict,
    rational_dict,
)

_LIB = exact_mod._RUNTIME_LIB
_LIB.hhs_pass168_compare_rational.argtypes = [
    HHSPass168Rational,
    HHSPass168Rational,
    HHSPass168Rational,
    HHSPass168Rational,
    POINTER(HHSPass168Rational),
]
_LIB.hhs_pass168_compare_rational.restype = ctypes.c_int
_LIB.hhs_pass168_compare_matrix.argtypes = [
    HHSPass168Rational,
    POINTER(HHSPass168Matrix3),
    HHSPass168Rational,
    POINTER(HHSPass168Matrix3),
    POINTER(HHSPass168Matrix3),
]
_LIB.hhs_pass168_compare_matrix.restype = ctypes.c_int
_LIB.hhs_pass168_comparator_conformance.argtypes = [POINTER(c_uint32)]
_LIB.hhs_pass168_comparator_conformance.restype = ctypes.c_int


def compare_rational(
    left_gain: HHSPass168Rational,
    left_value: HHSPass168Rational,
    right_gain: HHSPass168Rational,
    right_value: HHSPass168Rational,
) -> dict[str, int]:
    output = HHSPass168Rational()
    status = int(_LIB.hhs_pass168_compare_rational(
        left_gain, left_value, right_gain, right_value, ctypes.byref(output)
    ))
    if status != HHS_EXACT_STATUS_OK:
        raise RuntimeError(f"Pass168 rational comparator failed: {status}")
    return rational_dict(output)


def compare_matrix(
    left_gain: HHSPass168Rational,
    left_value: HHSPass168Matrix3,
    right_gain: HHSPass168Rational,
    right_value: HHSPass168Matrix3,
) -> list[list[dict[str, int]]]:
    output = HHSPass168Matrix3()
    status = int(_LIB.hhs_pass168_compare_matrix(
        left_gain,
        ctypes.byref(left_value),
        right_gain,
        ctypes.byref(right_value),
        ctypes.byref(output),
    ))
    if status != HHS_EXACT_STATUS_OK:
        raise RuntimeError(f"Pass168 matrix comparator failed: {status}")
    return matrix_dict(output)


def conformance() -> int:
    count = c_uint32()
    status = int(_LIB.hhs_pass168_comparator_conformance(ctypes.byref(count)))
    if status != HHS_EXACT_STATUS_OK:
        raise RuntimeError(f"Pass168 comparator conformance failed: {status}")
    return int(count.value)

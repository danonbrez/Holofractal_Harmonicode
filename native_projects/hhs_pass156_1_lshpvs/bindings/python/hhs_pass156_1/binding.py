from __future__ import annotations

import ctypes
from enum import IntEnum
from pathlib import Path


class Status(IntEnum):
    OK = 0
    INVALID_ARGUMENT = 1
    DIVIDE_BY_ZERO = 2
    OVERFLOW = 3
    NON_HERMITIAN = 4
    SINGULAR_PROPAGATOR = 5
    NORM_MISMATCH = 6
    ROTATION_RECONSTRUCTION_MISMATCH = 7
    VM81_REJECTED = 8


class Library:
    def __init__(self, path: str | Path):
        self._lib = ctypes.CDLL(str(path))
        self._lib.hhs_lshpvs_rotation_decompose.argtypes = [
            ctypes.c_int64,
            ctypes.c_int64,
            ctypes.POINTER(ctypes.c_int64),
            ctypes.POINTER(ctypes.c_int64),
        ]
        self._lib.hhs_lshpvs_rotation_decompose.restype = ctypes.c_int

    def decompose_rotation(self, n: int, modulus: int) -> tuple[int, int]:
        quotient = ctypes.c_int64()
        residue = ctypes.c_int64()
        status = Status(
            self._lib.hhs_lshpvs_rotation_decompose(
                n,
                modulus,
                ctypes.byref(quotient),
                ctypes.byref(residue),
            )
        )
        if status is not Status.OK:
            raise ValueError(status.name)
        return quotient.value, residue.value

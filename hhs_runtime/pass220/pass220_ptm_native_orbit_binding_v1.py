"""ctypes transport binding for the Pass 220 native integer orbit/factor coprocessor.

The native C library owns transition and factor enumeration. This is a read-only
exact-integer transport: no floats, no invented Ncalc tensor matrix values.
"""
from __future__ import annotations

import ctypes
from pathlib import Path

MAX_U64 = (1 << 64) - 1


class NativeOrbitError(RuntimeError):
    pass


class _State(ctypes.Structure):
    _fields_ = [
        ("input", ctypes.c_uint64),
        ("offset", ctypes.c_uint64),
        ("state", ctypes.c_uint64),
        ("p", ctypes.c_uint64),
        ("q", ctypes.c_uint64),
        ("product", ctypes.c_uint64),
    ]


_STATE_CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(_State), ctypes.c_void_p)
_FACTOR_CB = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.POINTER(_State), ctypes.c_int,
    ctypes.c_uint64, ctypes.c_uint32, ctypes.c_void_p
)


def _uint(value: int, *, positive: bool = False) -> int:
    if type(value) is not int or not (1 if positive else 0) <= value <= MAX_U64:
        raise ValueError("PTM_NATIVE_UINT64_RANGE")
    return value


class NativeOrbitIndex:
    def __init__(self, library_path: str | Path):
        self.library_path = str(Path(library_path))
        self._lib = ctypes.CDLL(self.library_path)
        self._lib.hhs_ptm_orbit_visit_v1.argtypes = [
            ctypes.c_uint64, ctypes.c_uint64, _STATE_CB, ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint64),
        ]
        self._lib.hhs_ptm_orbit_visit_v1.restype = ctypes.c_int
        self._lib.hhs_ptm_factor_visit_v1.argtypes = [
            ctypes.POINTER(_State), _FACTOR_CB, ctypes.c_void_p,
        ]
        self._lib.hhs_ptm_factor_visit_v1.restype = ctypes.c_int
        self._lib.hhs_ptm_cell_address_v1.argtypes = [
            ctypes.c_uint64, ctypes.c_uint64, ctypes.c_uint64,
            ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64),
        ]
        self._lib.hhs_ptm_cell_address_v1.restype = ctypes.c_int
        self._lib.hhs_ptm_decode_cell_address_v1.argtypes = [
            ctypes.c_uint64, ctypes.c_uint64,
            ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64),
            ctypes.POINTER(ctypes.c_uint64),
        ]
        self._lib.hhs_ptm_decode_cell_address_v1.restype = ctypes.c_int

    def visit(self, start: int, *, max_states: int = 10000, include_factors: bool = True):
        start = _uint(start, positive=True)
        max_states = _uint(max_states, positive=True)
        rows = []
        positions = []
        failed = []

        @_FACTOR_CB
        def on_factor(state, side, prime, exponent, _context):
            try:
                if side not in (0, 1) or prime < 2 or exponent < 1:
                    failed.append("PTM_NATIVE_FACTOR_PAYLOAD")
                    return 1
                positions.append((
                    int(state.contents.input), int(state.contents.offset),
                    int(state.contents.state), "p" if side == 0 else "q",
                    int(prime), int(exponent),
                ))
                return 0
            except Exception as exc:
                failed.append(str(exc))
                return 1

        @_STATE_CB
        def on_state(ptr, _context):
            try:
                item = ptr.contents
                n = int(item.state)
                if int(item.p) != n - 1 or int(item.q) != n + 1 or int(item.product) != n * n - 1:
                    failed.append("PTM_NATIVE_PRODUCT_INVARIANT")
                    return 1
                rows.append(tuple(int(getattr(item, field)) for field in
                                  ("input", "offset", "state", "p", "q", "product")))
                if include_factors:
                    status = self._lib.hhs_ptm_factor_visit_v1(ptr, on_factor, None)
                    if status:
                        failed.append(f"PTM_NATIVE_FACTOR_STATUS:{status}")
                        return 1
                return 0
            except Exception as exc:
                failed.append(str(exc))
                return 1

        visited = ctypes.c_uint64()
        status = self._lib.hhs_ptm_orbit_visit_v1(
            start, max_states, on_state, None, ctypes.byref(visited)
        )
        if status or failed or visited.value != len(rows):
            raise NativeOrbitError(f"PTM_NATIVE_ORBIT_STATUS:{status}:{failed}")
        if not rows or rows[-1][2] != 1:
            raise NativeOrbitError("PTM_NATIVE_ORBIT_NOT_TERMINAL")
        return {
            "input": start,
            "states": tuple(rows),
            "factor_positions": tuple(positions),
            "native_integer_execution": True,
            "native_ncalc_execution": False,
        }

    def address(self, length: int, row: int, column: int, local_cell: int) -> int:
        args = tuple(_uint(x) for x in (length, row, column, local_cell))
        out = ctypes.c_uint64()
        status = self._lib.hhs_ptm_cell_address_v1(*args, ctypes.byref(out))
        if status:
            raise NativeOrbitError(f"PTM_NATIVE_ADDRESS_STATUS:{status}")
        return int(out.value)

    def decode_address(self, length: int, address: int) -> tuple[int, int, int]:
        length = _uint(length, positive=True)
        address = _uint(address)
        row = ctypes.c_uint64()
        column = ctypes.c_uint64()
        local_cell = ctypes.c_uint64()
        status = self._lib.hhs_ptm_decode_cell_address_v1(
            length, address, ctypes.byref(row), ctypes.byref(column),
            ctypes.byref(local_cell)
        )
        if status:
            raise NativeOrbitError(f"PTM_NATIVE_DECODE_STATUS:{status}")
        return (int(row.value), int(column.value), int(local_cell.value))

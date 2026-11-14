#!/usr/bin/env python3
"""Module 196 shared-library load/export smoke; no canonical admission claim."""
import ctypes
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIBRARY = ROOT / "hhs_runtime" / "builds" / "libhhs_runtime.so"

def test_module196_linked_abi() -> None:
    assert LIBRARY.is_file(), f"missing native runtime: {LIBRARY}"
    lib = ctypes.CDLL(str(LIBRARY))
    route = lib.hhs_exact_pass220_module196_rna_route_v1
    route.argtypes = [ctypes.c_uint64, ctypes.c_uint64] + [ctypes.c_void_p]*5 + [ctypes.c_uint8, ctypes.c_int8] + [ctypes.c_void_p]*4
    route.restype = ctypes.c_int
    # Missing candidate/program/frame/transition must be rejected without
    # crossing the VM81 or RNA cell-wall boundary.
    assert route(100, 101, None, None, None, None, None, 0, 0,
                 None, None, None, None) == 1
    # The pre-existing 0..190 selector must remain callable.
    legacy = lib.hhs_exact_pass220_course_module_execute_route
    legacy.argtypes = [ctypes.c_uint32]+[ctypes.c_void_p]*4+[ctypes.c_uint8,ctypes.c_int8]+[ctypes.c_void_p]*3
    legacy.restype = ctypes.c_int
    assert legacy(0, None, None, None, None, 0, 0, None, None, None) == 1
    assert legacy(190, None, None, None, None, 0, 0, None, None, None) == 1
    assert legacy(191, None, None, None, None, 0, 0, None, None, None) == 2

if __name__ == "__main__":
    test_module196_linked_abi()
    print("module196_linked_runtime_export_and_legacy_selector=PASS")

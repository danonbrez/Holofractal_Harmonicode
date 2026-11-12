#!/usr/bin/env python3
"""Native ABI smoke test: all course circuit service-port selectors are callable."""
from __future__ import annotations

import ctypes
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIBRARY = ROOT / "hhs_runtime/builds/libhhs_runtime.so"


def test_all_native_course_module_ports() -> None:
    if not LIBRARY.is_file():
        raise AssertionError(f"Native runtime ABI has not been built: {LIBRARY}")
    lib = ctypes.CDLL(str(LIBRARY))
    fn = lib.hhs_exact_pass220_course_module_execute_route
    fn.argtypes = [ctypes.c_uint32] + [ctypes.c_void_p] * 9
    fn.restype = ctypes.c_int
    # Each valid module selector exists and enters the inherited argument
    # validation when the caller omits the already-lowered program/frame.
    for module in range(191):
        assert fn(module, *([None] * 9)) == 1, module
    assert fn(191, *([None] * 9)) == 2
    assert fn(0xFFFFFFFF, *([None] * 9)) == 2


if __name__ == "__main__":
    test_all_native_course_module_ports()
    print("native_course_module_port_selection=PASS; module_count=191")

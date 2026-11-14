"""Exercise exact native C source extraction for every M000–M190 circuit."""
from __future__ import annotations

import ctypes
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/course/HARMONICODE_Algebra_Course_Expanded_0_190.md"
INDEX = ROOT / "contracts/pass220/HARMONICODE_COURSE_EXPANSION_INDEX_V1.json"
LIBRARY = ROOT / "hhs_runtime/builds/libhhs_runtime.so"


def test_native_course_source_exact_bytes() -> None:
    rows = json.loads(INDEX.read_text(encoding="utf-8"))["modules"]
    lines = SOURCE.read_bytes().splitlines(keepends=True)
    assert len(rows) == 191
    lib = ctypes.CDLL(str(LIBRARY))
    extract = lib.hhs_exact_pass220_course_module_source
    extract.argtypes = [
        ctypes.c_uint32, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_size_t),
    ]
    extract.restype = ctypes.c_int
    path = str(SOURCE).encode("utf-8")
    for i, module in enumerate(rows):
        stop = rows[i + 1]["start_line"] - 1 if i < 190 else len(lines)
        expected = b"".join(lines[module["start_line"] - 1:stop])
        assert expected, module["id"]
        size = ctypes.c_size_t()
        assert extract(i, path, None, 0, ctypes.byref(size)) == 3
        assert size.value == len(expected), module["id"]
        buffer = ctypes.create_string_buffer(size.value)
        assert extract(i, path, buffer, size.value, ctypes.byref(size)) == 0
        assert buffer.raw == expected, module["id"]
    assert extract(191, path, None, 0, ctypes.byref(ctypes.c_size_t())) == 2


if __name__ == "__main__":
    test_native_course_source_exact_bytes()
    print("native_course_exact_source_bytes=PASS; modules=191")

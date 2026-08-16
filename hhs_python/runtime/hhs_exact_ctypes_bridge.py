from __future__ import annotations

import ctypes
import os
import pathlib
import platform
import subprocess
from ctypes import POINTER, Structure, c_size_t, c_uint8, c_uint16, c_uint32, c_uint64

HHS_EXACT_HASH72_LEN = 72
HHS_EXACT_HASH72_COORDS = 5184
HHS_EXACT_VM81_CELLS = 81
HHS_EXACT_VM81_FRAME_BYTES = 648
HHS_EXACT_PHASE_BASIS_COUNT = 8
HHS_EXACT_X86_MAX_INSTRUCTION_BYTES = 15

HHS_EXACT_STATUS_OK = 0


class HHSExactPhaseProduct(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("abi_version", c_uint32),
        ("left_basis", c_uint8),
        ("right_basis", c_uint8),
        ("phase", c_uint8),
        ("raw_additive_phase", c_uint8),
        ("orientation", c_uint8),
        ("closure", c_uint8),
        ("ordered_tag", c_uint16),
    ]


class HHSExactVM81Frame(Structure):
    _fields_ = [("words", c_uint64 * HHS_EXACT_VM81_CELLS)]


class HHSExactX86InstructionBytes(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("abi_version", c_uint32),
        ("length", c_uint8),
        ("bytes", c_uint8 * HHS_EXACT_X86_MAX_INSTRUCTION_BYTES),
    ]


class HHSExactABIDescriptor(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("abi_version", c_uint32),
        ("hash72_len", c_uint32),
        ("hash72_coords", c_uint32),
        ("vm81_cells", c_uint32),
        ("vm81_word_bits", c_uint32),
        ("vm81_frame_bits", c_uint32),
        ("vm81_frame_bytes", c_uint32),
        ("phase_basis_count", c_uint32),
        ("phase_pair_count", c_uint32),
        ("x86_max_instruction_bytes", c_uint32),
        ("legacy_v1_layout_preserved", c_uint32),
    ]


def _resolve_runtime_library() -> pathlib.Path:
    root = pathlib.Path(__file__).resolve().parents[2]
    runtime_dir = root / "hhs_runtime" / "builds"
    system = platform.system().lower()
    if system == "windows":
        libname = "hhs_runtime.dll"
    elif system == "darwin":
        libname = "libhhs_runtime.dylib"
    else:
        libname = "libhhs_runtime.so"
    libpath = runtime_dir / libname
    if not libpath.exists():
        auto_build = os.environ.get("HHS_DISABLE_C_AUTOBUILD", "").lower() not in {
            "1", "true", "yes", "on"
        }
        if auto_build:
            subprocess.run(
                ["make", "c-abi"],
                cwd=str(root),
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
    if not libpath.exists():
        raise FileNotFoundError(f"HHS runtime shared library not found: {libpath}")
    return libpath


_RUNTIME_LIB = ctypes.CDLL(str(_resolve_runtime_library()))

_RUNTIME_LIB.hhs_exact_abi_version.argtypes = []
_RUNTIME_LIB.hhs_exact_abi_version.restype = c_uint32
_RUNTIME_LIB.hhs_exact_abi_descriptor.argtypes = [POINTER(HHSExactABIDescriptor)]
_RUNTIME_LIB.hhs_exact_abi_descriptor.restype = ctypes.c_int
_RUNTIME_LIB.hhs_exact_abi_validate.argtypes = []
_RUNTIME_LIB.hhs_exact_abi_validate.restype = ctypes.c_int

_RUNTIME_LIB.hhs_exact_hash72_coord_encode.argtypes = [c_uint8, c_uint8, POINTER(c_uint16)]
_RUNTIME_LIB.hhs_exact_hash72_coord_encode.restype = ctypes.c_int
_RUNTIME_LIB.hhs_exact_hash72_coord_decode.argtypes = [c_uint16, POINTER(c_uint8), POINTER(c_uint8)]
_RUNTIME_LIB.hhs_exact_hash72_coord_decode.restype = ctypes.c_int

_RUNTIME_LIB.hhs_exact_vm5184_address_encode.argtypes = [c_uint8, c_uint8, c_uint8, POINTER(c_uint16)]
_RUNTIME_LIB.hhs_exact_vm5184_address_encode.restype = ctypes.c_int
_RUNTIME_LIB.hhs_exact_vm5184_address_decode.argtypes = [c_uint16, POINTER(c_uint8), POINTER(c_uint8), POINTER(c_uint8)]
_RUNTIME_LIB.hhs_exact_vm5184_address_decode.restype = ctypes.c_int

_RUNTIME_LIB.hhs_exact_phase_product.argtypes = [c_uint8, c_uint8, POINTER(HHSExactPhaseProduct)]
_RUNTIME_LIB.hhs_exact_phase_product.restype = ctypes.c_int

_RUNTIME_LIB.hhs_exact_vm81_frame_import_le.argtypes = [POINTER(c_uint8), c_size_t, POINTER(HHSExactVM81Frame)]
_RUNTIME_LIB.hhs_exact_vm81_frame_import_le.restype = ctypes.c_int
_RUNTIME_LIB.hhs_exact_vm81_frame_export_le.argtypes = [POINTER(HHSExactVM81Frame), POINTER(c_uint8), c_size_t, POINTER(c_size_t)]
_RUNTIME_LIB.hhs_exact_vm81_frame_export_le.restype = ctypes.c_int

_RUNTIME_LIB.hhs_x86_64_ingress_exact.argtypes = [POINTER(c_uint8), c_size_t, POINTER(HHSExactX86InstructionBytes)]
_RUNTIME_LIB.hhs_x86_64_ingress_exact.restype = ctypes.c_int
_RUNTIME_LIB.hhs_x86_64_egress_exact.argtypes = [POINTER(HHSExactX86InstructionBytes), POINTER(c_uint8), c_size_t, POINTER(c_size_t)]
_RUNTIME_LIB.hhs_x86_64_egress_exact.restype = ctypes.c_int
_RUNTIME_LIB.hhs_x86_64_bytecode_copy_exact.argtypes = [POINTER(c_uint8), c_size_t, POINTER(c_uint8), c_size_t, POINTER(c_size_t)]
_RUNTIME_LIB.hhs_x86_64_bytecode_copy_exact.restype = ctypes.c_int


class HHSExactRuntimeBridge:
    @staticmethod
    def validate() -> bool:
        return _RUNTIME_LIB.hhs_exact_abi_validate() == HHS_EXACT_STATUS_OK

    @staticmethod
    def descriptor() -> dict[str, int]:
        value = HHSExactABIDescriptor()
        status = _RUNTIME_LIB.hhs_exact_abi_descriptor(ctypes.byref(value))
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"exact ABI descriptor failed: {status}")
        return {name: int(getattr(value, name)) for name, _ in value._fields_}

    @staticmethod
    def hash72_coord(position: int, symbol_index: int) -> int:
        coord = c_uint16()
        status = _RUNTIME_LIB.hhs_exact_hash72_coord_encode(position, symbol_index, ctypes.byref(coord))
        if status != HHS_EXACT_STATUS_OK:
            raise ValueError((position, symbol_index, status))
        return int(coord.value)

    @staticmethod
    def hash72_decode(coord: int) -> tuple[int, int]:
        position = c_uint8()
        symbol = c_uint8()
        status = _RUNTIME_LIB.hhs_exact_hash72_coord_decode(coord, ctypes.byref(position), ctypes.byref(symbol))
        if status != HHS_EXACT_STATUS_OK:
            raise ValueError((coord, status))
        return int(position.value), int(symbol.value)

    @staticmethod
    def vm5184_address(cell81: int, left_basis8: int, right_basis8: int) -> int:
        address = c_uint16()
        status = _RUNTIME_LIB.hhs_exact_vm5184_address_encode(
            cell81, left_basis8, right_basis8, ctypes.byref(address)
        )
        if status != HHS_EXACT_STATUS_OK:
            raise ValueError((cell81, left_basis8, right_basis8, status))
        return int(address.value)

    @staticmethod
    def vm5184_decode(address: int) -> tuple[int, int, int]:
        cell = c_uint8()
        left = c_uint8()
        right = c_uint8()
        status = _RUNTIME_LIB.hhs_exact_vm5184_address_decode(
            address, ctypes.byref(cell), ctypes.byref(left), ctypes.byref(right)
        )
        if status != HHS_EXACT_STATUS_OK:
            raise ValueError((address, status))
        return int(cell.value), int(left.value), int(right.value)

    @staticmethod
    def phase_product(left_basis: int, right_basis: int) -> dict[str, int]:
        product = HHSExactPhaseProduct()
        status = _RUNTIME_LIB.hhs_exact_phase_product(left_basis, right_basis, ctypes.byref(product))
        if status != HHS_EXACT_STATUS_OK:
            raise ValueError((left_basis, right_basis, status))
        return {name: int(getattr(product, name)) for name, _ in product._fields_}

    @staticmethod
    def frame_roundtrip(raw: bytes) -> bytes:
        if len(raw) != HHS_EXACT_VM81_FRAME_BYTES:
            raise ValueError("VM81 exact frame must be exactly 648 bytes")
        source = (c_uint8 * len(raw)).from_buffer_copy(raw)
        frame = HHSExactVM81Frame()
        status = _RUNTIME_LIB.hhs_exact_vm81_frame_import_le(source, len(raw), ctypes.byref(frame))
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"frame ingress failed: {status}")
        output = (c_uint8 * HHS_EXACT_VM81_FRAME_BYTES)()
        written = c_size_t()
        status = _RUNTIME_LIB.hhs_exact_vm81_frame_export_le(
            ctypes.byref(frame), output, len(output), ctypes.byref(written)
        )
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"frame egress failed: {status}")
        return bytes(output[: written.value])

    @staticmethod
    def x86_instruction_roundtrip(raw: bytes) -> bytes:
        if not 1 <= len(raw) <= HHS_EXACT_X86_MAX_INSTRUCTION_BYTES:
            raise ValueError("x86_64 instruction length must be 1..15 bytes")
        source = (c_uint8 * len(raw)).from_buffer_copy(raw)
        instruction = HHSExactX86InstructionBytes()
        status = _RUNTIME_LIB.hhs_x86_64_ingress_exact(source, len(raw), ctypes.byref(instruction))
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"x86_64 ingress failed: {status}")
        output = (c_uint8 * HHS_EXACT_X86_MAX_INSTRUCTION_BYTES)()
        written = c_size_t()
        status = _RUNTIME_LIB.hhs_x86_64_egress_exact(
            ctypes.byref(instruction), output, len(output), ctypes.byref(written)
        )
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"x86_64 egress failed: {status}")
        return bytes(output[: written.value])

    @staticmethod
    def x86_bytecode_roundtrip(raw: bytes) -> bytes:
        if not raw:
            return b""
        source = (c_uint8 * len(raw)).from_buffer_copy(raw)
        output = (c_uint8 * len(raw))()
        written = c_size_t()
        status = _RUNTIME_LIB.hhs_x86_64_bytecode_copy_exact(
            source, len(raw), output, len(output), ctypes.byref(written)
        )
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"x86_64 bytecode copy failed: {status}")
        return bytes(output[: written.value])


__all__ = [
    "HHSExactRuntimeBridge",
    "HHSExactABIDescriptor",
    "HHSExactPhaseProduct",
    "HHSExactVM81Frame",
    "HHSExactX86InstructionBytes",
]

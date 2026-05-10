# ============================================================================
# hhs_python/runtime/hhs_ctypes_bridge.py
# HARMONICODE / HHS
# CANONICAL PYTHON ↔ C ABI BRIDGE
#
# PURPOSE
# -------
# Deterministic runtime bridge between:
#
#   Python orchestration
#       ↓
#   hhs_runtime_abi.h
#       ↓
#   Deterministic VM substrate
#
# This file is the canonical ctypes bridge for:
#
#   - runtime execution
#   - receipt-chain control
#   - tensor transport
#   - graph memory ingestion
#   - replay systems
#   - websocket serialization
#   - multimodal routing
#
# ============================================================================

from __future__ import annotations

import ctypes
import pathlib
import platform

from ctypes import (
    Structure,
    POINTER,
    c_uint8,
    c_uint32,
    c_uint64,
    c_int64,
    c_float,
    c_double,
    c_char,
    c_size_t
)

# ============================================================================
# CONSTANTS
# ============================================================================

HASH72_LEN = 72
HASH72_STRLEN = 73

HHS_RUNTIME_MAGIC = 0x48485381

# ============================================================================
# SHARED LIBRARY RESOLUTION
# ============================================================================

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
        raise FileNotFoundError(
            f"HHS runtime shared library not found:\n{libpath}"
        )

    return libpath


# ============================================================================
# HASH72
# ============================================================================

class HHSHash72(ctypes.Array):

    _type_ = c_char
    _length_ = HASH72_STRLEN


# ============================================================================
# TRANSPORT VECTOR
# ============================================================================

class HHSTransportVector(Structure):

    _fields_ = [

        ("transport_flux", c_int64),
        ("orientation_flux", c_int64),
        ("constraint_flux", c_int64),

    ]


# ============================================================================
# TENSOR STATE
# ============================================================================

class HHSTensorState(Structure):

    _fields_ = [

        ("xy", c_int64),
        ("yx", c_int64),

        ("transport", c_int64),
        ("orientation", c_int64),
        ("constraint", c_int64),

    ]


# ============================================================================
# GENOMIC STATE
# ============================================================================

class HHSGenomicState(Structure):

    _fields_ = [

        ("genomic", c_uint8 * 4),

    ]


# ============================================================================
# MANIFOLD STATE
# ============================================================================

class HHSManifoldState(Structure):

    _fields_ = [

        ("manifold", (c_double * 9) * 9),

    ]


# ============================================================================
# RECEIPT
# ============================================================================

class HHSReceipt(Structure):

    _fields_ = [

        ("parent_receipt", HHSHash72),
        ("current_receipt", HHSHash72),

        ("step", c_uint64),
        ("opcode", c_uint64),

        ("witness_flags", c_uint64),

        ("entropy_delta", c_int64),
        ("closure_delta", c_int64),

    ]


# ============================================================================
# RUNTIME STATE
# ============================================================================

class HHSRuntimeState(Structure):

    _fields_ = [

        ("runtime_magic", c_uint64),

        ("abi_major", c_uint32),
        ("abi_minor", c_uint32),
        ("abi_patch", c_uint32),

        ("step", c_uint64),

        ("orbit_id", c_uint64),

        ("witness_flags", c_uint64),

        ("flux", HHSTransportVector),

        ("prev_hash72", HHSHash72),
        ("state_hash72", HHSHash72),
        ("receipt_hash72", HHSHash72),

        ("lo_shu_slot", c_uint8),
        ("closure_class", c_uint8),

        ("converged", c_uint8),
        ("halted", c_uint8),

        ("tensor", HHSTensorState),

        ("genomic", HHSGenomicState),

        ("manifold", HHSManifoldState),

    ]


# ============================================================================
# VECTOR CACHE RECORD
# ============================================================================

class HHSVectorCacheRecord(Structure):

    _fields_ = [

        ("hash72", HHSHash72),

        ("vector", c_float * 72),

        ("witness_flags", c_uint64),

        ("replay_count", c_uint64),

        ("prediction_hits", c_uint64),

    ]


# ============================================================================
# GRAPH NODE
# ============================================================================

class HHSGraphNode(Structure):

    _fields_ = [

        ("node_id", c_uint64),

        ("parent_node_id", c_uint64),

        ("hash72", HHSHash72),

        ("witness_flags", c_uint64),

        ("timestamp", c_uint64),

    ]


# ============================================================================
# GRAPH EDGE
# ============================================================================

class HHSGraphEdge(Structure):

    _fields_ = [

        ("source_id", c_uint64),

        ("target_id", c_uint64),

        ("edge_type", c_uint32),

        ("weight", c_float),

    ]


# ============================================================================
# LOAD LIBRARY
# ============================================================================

_RUNTIME_LIB = ctypes.CDLL(str(_resolve_runtime_library()))

# ============================================================================
# ABI FUNCTION SIGNATURES
# ============================================================================

_RUNTIME_LIB.hhs_runtime_init.argtypes = [
    POINTER(HHSRuntimeState)
]

_RUNTIME_LIB.hhs_runtime_init.restype = None

# --------------------------------------------------------------------------

_RUNTIME_LIB.hhs_runtime_reset.argtypes = [
    POINTER(HHSRuntimeState)
]

_RUNTIME_LIB.hhs_runtime_reset.restype = None

# --------------------------------------------------------------------------

_RUNTIME_LIB.hhs_runtime_step.argtypes = [
    POINTER(HHSRuntimeState),
    POINTER(HHSTensorState)
]

_RUNTIME_LIB.hhs_runtime_step.restype = None

# --------------------------------------------------------------------------

_RUNTIME_LIB.hhs_runtime_halt.argtypes = [
    POINTER(HHSRuntimeState)
]

_RUNTIME_LIB.hhs_runtime_halt.restype = None

# --------------------------------------------------------------------------

_RUNTIME_LIB.hhs_receipt_commit.argtypes = [
    POINTER(HHSRuntimeState),
    POINTER(HHSReceipt)
]

_RUNTIME_LIB.hhs_receipt_commit.restype = None

# --------------------------------------------------------------------------

_RUNTIME_LIB.hhs_receipt_reset.argtypes = [
    POINTER(HHSReceipt)
]

_RUNTIME_LIB.hhs_receipt_reset.restype = None

# --------------------------------------------------------------------------

_RUNTIME_LIB.hhs_validate_abi.argtypes = [
    POINTER(HHSRuntimeState)
]

_RUNTIME_LIB.hhs_validate_abi.restype = ctypes.c_int

# --------------------------------------------------------------------------

_RUNTIME_LIB.hhs_sizeof_runtime_state.argtypes = []

_RUNTIME_LIB.hhs_sizeof_runtime_state.restype = c_size_t

# --------------------------------------------------------------------------

_RUNTIME_LIB.hhs_sizeof_receipt.argtypes = []

_RUNTIME_LIB.hhs_sizeof_receipt.restype = c_size_t

# --------------------------------------------------------------------------

_RUNTIME_LIB.hhs_sizeof_tensor_state.argtypes = []

_RUNTIME_LIB.hhs_sizeof_tensor_state.restype = c_size_t

# ============================================================================
# PYTHON RUNTIME WRAPPER
# ============================================================================

class HHSRuntimeBridge:

    """
    Canonical Python interface to the deterministic VM substrate.
    """

    def __init__(self):

        self.state = HHSRuntimeState()

        self.tensor = HHSTensorState()

        self.receipt = HHSReceipt()

        self.runtime_init()

    # ----------------------------------------------------------------------

    def runtime_init(self):

        _RUNTIME_LIB.hhs_runtime_init(
            ctypes.byref(self.state)
        )

    # ----------------------------------------------------------------------

    def runtime_reset(self):

        _RUNTIME_LIB.hhs_runtime_reset(
            ctypes.byref(self.state)
        )

    # ----------------------------------------------------------------------

    def runtime_step(self):

        _RUNTIME_LIB.hhs_runtime_step(
            ctypes.byref(self.state),
            ctypes.byref(self.tensor)
        )

    # ----------------------------------------------------------------------

    def runtime_halt(self):

        _RUNTIME_LIB.hhs_runtime_halt(
            ctypes.byref(self.state)
        )

    # ----------------------------------------------------------------------

    def receipt_commit(self):

        _RUNTIME_LIB.hhs_receipt_commit(
            ctypes.byref(self.state),
            ctypes.byref(self.receipt)
        )

    # ----------------------------------------------------------------------

    def validate_abi(self) -> bool:

        result = _RUNTIME_LIB.hhs_validate_abi(
            ctypes.byref(self.state)
        )

        return bool(result)

    # ----------------------------------------------------------------------

    @property
    def step(self) -> int:

        return int(self.state.step)

    # ----------------------------------------------------------------------

    @property
    def converged(self) -> bool:

        return bool(self.state.converged)

    # ----------------------------------------------------------------------

    @property
    def halted(self) -> bool:

        return bool(self.state.halted)

    # ----------------------------------------------------------------------

    @property
    def state_hash72(self) -> str:

        return bytes(self.state.state_hash72) \
            .decode("utf-8", errors="ignore") \
            .rstrip("\x00")

    # ----------------------------------------------------------------------

    @property
    def receipt_hash72(self) -> str:

        return bytes(self.state.receipt_hash72) \
            .decode("utf-8", errors="ignore") \
            .rstrip("\x00")

    # ----------------------------------------------------------------------

    def export_runtime_dict(self):

        return {

            "step":
                int(self.state.step),

            "orbit_id":
                int(self.state.orbit_id),

            "witness_flags":
                int(self.state.witness_flags),

            "transport_flux":
                int(self.state.flux.transport_flux),

            "orientation_flux":
                int(self.state.flux.orientation_flux),

            "constraint_flux":
                int(self.state.flux.constraint_flux),

            "state_hash72":
                self.state_hash72,

            "receipt_hash72":
                self.receipt_hash72,

            "converged":
                self.converged,

            "halted":
                self.halted,
        }


# ============================================================================
# ABI SELF-TEST
# ============================================================================

def abi_self_test():

    runtime = HHSRuntimeBridge()

    ok = runtime.validate_abi()

    if not ok:
        raise RuntimeError(
            "HHS ABI validation failed"
        )

    print("HHS ABI VALIDATED")

    print(
        "RuntimeState:",
        _RUNTIME_LIB.hhs_sizeof_runtime_state()
    )

    print(
        "Receipt:",
        _RUNTIME_LIB.hhs_sizeof_receipt()
    )

    print(
        "Tensor:",
        _RUNTIME_LIB.hhs_sizeof_tensor_state()
    )

    runtime.runtime_step()

    print(runtime.export_runtime_dict())


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    abi_self_test()
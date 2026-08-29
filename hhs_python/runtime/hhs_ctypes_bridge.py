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
import os
import pathlib
import platform
import subprocess

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

        auto_build = (
            os.environ.get(
                "HHS_DISABLE_C_AUTOBUILD",
                ""
            ).lower()
            not in {"1", "true", "yes", "on"}
        )

        if auto_build:

            try:
                subprocess.run(
                    ["make", "c-abi"],
                    cwd=str(root),
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

            except Exception as exc:
                raise FileNotFoundError(
                    "HHS runtime shared library was not found "
                    "and automatic C ABI build failed:\n"
                    f"{libpath}\n{exc}"
                ) from exc

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
# HASH72 u^72 DIGITAL DNA RING STATE
# ============================================================================

class HHSHash72RingState(Structure):

    _fields_ = [
        ("positions", c_uint8 * HASH72_LEN),
        ("rotation_profile", c_int64 * HASH72_LEN),
        ("dna", HHSHash72),
        ("trace_count", c_uint64),
        ("zero_sum", c_uint8),
        ("last_index", c_uint8),
        ("last_delta", c_int64),
    ]

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
# SRCG SELF-SOLVING RECURSIVE CONSTRAINT GATE STATE
# ============================================================================

class HHSSRCGState(Structure):

    _fields_ = [
        ("A", c_double),
        ("B", c_double),
        ("phi", c_double),
        ("delta", c_double),
        ("learning_rate", c_double),
        ("drift_threshold", c_double),
        ("last_valid_A", c_double),
        ("last_valid_B", c_double),
        ("trace_count", c_uint64),
        ("unit_unity_valid", c_uint8),
        ("lo_shu_valid", c_uint8),
        ("quartic_carrier_preserved", c_uint8),
        ("rolled_back", c_uint8),
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
_RUNTIME_LIB.hhs_hash72_ring_init.argtypes = [
    POINTER(HHSHash72RingState)
]
_RUNTIME_LIB.hhs_hash72_ring_init.restype = None

_RUNTIME_LIB.hhs_hash72_ring_rotate.argtypes = [
    POINTER(HHSHash72RingState),
    c_uint8,
    c_int64,
]
_RUNTIME_LIB.hhs_hash72_ring_rotate.restype = c_uint8

_RUNTIME_LIB.hhs_hash72_dna_validate.argtypes = [
    POINTER(HHSHash72RingState)
]
_RUNTIME_LIB.hhs_hash72_dna_validate.restype = c_uint8

_RUNTIME_LIB.hhs_hash72_tensor_project.argtypes = [
    POINTER(HHSHash72RingState),
    POINTER(c_uint8)
]
_RUNTIME_LIB.hhs_hash72_tensor_project.restype = None

_RUNTIME_LIB.hhs_hash72_reverse_state.argtypes = [
    POINTER(HHSHash72RingState),
    POINTER(HHSHash72RingState),
]
_RUNTIME_LIB.hhs_hash72_reverse_state.restype = c_uint8

# --------------------------------------------------------------------------


_RUNTIME_LIB.hhs_sizeof_runtime_state.argtypes = []

_RUNTIME_LIB.hhs_sizeof_runtime_state.restype = c_size_t

# --------------------------------------------------------------------------

_RUNTIME_LIB.hhs_sizeof_receipt.argtypes = []

_RUNTIME_LIB.hhs_sizeof_receipt.restype = c_size_t

# --------------------------------------------------------------------------

_RUNTIME_LIB.hhs_sizeof_tensor_state.argtypes = []

_RUNTIME_LIB.hhs_sizeof_tensor_state.restype = c_size_t

_RUNTIME_LIB.hhs_sizeof_hash72_ring_state.argtypes = []
_RUNTIME_LIB.hhs_sizeof_hash72_ring_state.restype = c_size_t



_RUNTIME_LIB.hhs_srcg_init.argtypes = [
    POINTER(HHSSRCGState),
    c_double,
    c_double,
    c_double,
    c_double,
]
_RUNTIME_LIB.hhs_srcg_init.restype = None

_RUNTIME_LIB.hhs_srcg_step.argtypes = [
    POINTER(HHSSRCGState),
]
_RUNTIME_LIB.hhs_srcg_step.restype = c_uint8

_RUNTIME_LIB.hhs_srcg_validate.argtypes = [
    POINTER(HHSSRCGState),
]
_RUNTIME_LIB.hhs_srcg_validate.restype = c_uint8

_RUNTIME_LIB.hhs_sizeof_srcg_state.argtypes = []
_RUNTIME_LIB.hhs_sizeof_srcg_state.restype = c_size_t

# ============================================================================
# HASH72 u^72 DIGITAL DNA RING WRAPPER
# ============================================================================

def _hash72_to_str(value) -> str:
    return bytes(value).decode("utf-8", errors="ignore").rstrip("\x00")


class HHSHash72RingBridge:

    """Python bridge to the kernel-native C Hash72 u^72 Digital DNA ring.

    This object preserves the distinction between the receipt digest shell and
    the positional rotation-profile identity of the Hash72 ring.
    """

    def __init__(self):
        self.ring = HHSHash72RingState()
        _RUNTIME_LIB.hhs_hash72_ring_init(ctypes.byref(self.ring))

    @property
    def dna(self) -> str:
        return _hash72_to_str(self.ring.dna)

    @property
    def zero_sum(self) -> bool:
        return bool(self.ring.zero_sum)

    def validate(self) -> bool:
        return bool(_RUNTIME_LIB.hhs_hash72_dna_validate(ctypes.byref(self.ring)))

    def rotate(self, index: int, delta: int) -> bool:
        return bool(_RUNTIME_LIB.hhs_hash72_ring_rotate(ctypes.byref(self.ring), index % HASH72_LEN, int(delta)))

    def tensor_project(self) -> list[int]:
        tensor = (c_uint8 * 81)()
        _RUNTIME_LIB.hhs_hash72_tensor_project(ctypes.byref(self.ring), tensor)
        return [int(x) for x in tensor]

    def reverse_state(self) -> "HHSHash72RingBridge":
        out = HHSHash72RingBridge.__new__(HHSHash72RingBridge)
        out.ring = HHSHash72RingState()
        ok = _RUNTIME_LIB.hhs_hash72_reverse_state(ctypes.byref(self.ring), ctypes.byref(out.ring))
        if not ok:
            raise RuntimeError("Hash72 reverse_state failed DNA validation")
        return out

    def export(self) -> dict:
        return {
            "dna": self.dna,
            "zero_sum": self.zero_sum,
            "trace_count": int(self.ring.trace_count),
            "last_index": int(self.ring.last_index),
            "last_delta": int(self.ring.last_delta),
            "positions": [int(x) for x in self.ring.positions],
            "rotation_profile": [int(x) for x in self.ring.rotation_profile],
        }



# ============================================================================
# SRCG SELF-SOLVING RECURSIVE CONSTRAINT GATE WRAPPER
# ============================================================================

class HHSSRCGBridge:

    """Python bridge to the C-kernel SRCG primitive instruction.

    The bridge keeps A/B as a paired manifold state and exposes traceable
    rollback metadata without flattening higher-level quartic carriers.
    """

    def __init__(self, A: float, B: float, learning_rate: float = 0.125, drift_threshold: float = 1.001):
        self.state = HHSSRCGState()
        _RUNTIME_LIB.hhs_srcg_init(
            ctypes.byref(self.state),
            float(A),
            float(B),
            float(learning_rate),
            float(drift_threshold),
        )

    def step(self) -> bool:
        return bool(_RUNTIME_LIB.hhs_srcg_step(ctypes.byref(self.state)))

    def validate(self) -> bool:
        return bool(_RUNTIME_LIB.hhs_srcg_validate(ctypes.byref(self.state)))

    def export(self) -> dict:
        return {
            "schema": "HHS_SRCG_C_KERNEL_STATE_V1",
            "A": float(self.state.A),
            "B": float(self.state.B),
            "phi": float(self.state.phi),
            "delta": float(self.state.delta),
            "learning_rate": float(self.state.learning_rate),
            "drift_threshold": float(self.state.drift_threshold),
            "last_valid_A": float(self.state.last_valid_A),
            "last_valid_B": float(self.state.last_valid_B),
            "trace_count": int(self.state.trace_count),
            "unit_unity_valid": bool(self.state.unit_unity_valid),
            "lo_shu_valid": bool(self.state.lo_shu_valid),
            "quartic_carrier_preserved": bool(self.state.quartic_carrier_preserved),
            "rolled_back": bool(self.state.rolled_back),
            "valid": self.validate(),
        }

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

    def step(self, instruction=None):
        """Compatibility alias for orchestrators that dispatch instructions.

        The current C ABI owns deterministic VM advancement. The optional
        instruction envelope is accepted for higher-level dispatch continuity
        and reserved for future opcode/tensor binding without changing callers.
        """

        _ = instruction
        self.runtime_step()
        return self.export_runtime_dict()

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

    print(
        "Hash72Ring:",
        _RUNTIME_LIB.hhs_sizeof_hash72_ring_state()
    )

    ring = HHSHash72RingBridge()
    assert ring.validate()
    before = ring.dna
    assert ring.rotate(0, 5)
    after = ring.dna
    original = ring.reverse_state()
    assert original.validate()
    print({"hash72_ring_before": before, "hash72_ring_after": after, "hash72_ring_reversed": original.dna})

    runtime.runtime_step()

    print(runtime.export_runtime_dict())


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    abi_self_test()
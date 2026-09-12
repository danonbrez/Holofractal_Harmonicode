from __future__ import annotations

import ctypes
from ctypes import Structure, c_char, c_size_t, c_uint8, c_uint32

from hhs_python.runtime import hhs_uqcel_ctypes_bridge as uq
from hhs_python.runtime.hhs_exact_ctypes_bridge import HHSExactVM81Frame

HHS_EXACT_PASS192_FIB_MAX_DESCRIPTOR_BYTES = 2048
HHS_EXACT_PASS219_UCE_FIBONACCI_DEPTH = 10
HHS_EXACT_STATUS_INVARIANT_FAILURE = 5


class HHSExactPass192FibonacciCompressionV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("depth", c_uint32),
        ("lo_shu_cell_count", c_uint32),
        ("magnitude_row_count", c_uint32),
        ("shared_schedule_count", c_uint32),
        ("expanded_schedule_count", c_uint32),
        ("outer_modulus", c_uint32),
        ("membrane_modulus", c_uint32),
        ("membrane_residue", c_uint32),
        ("descriptor_length", c_uint32),
        ("compression_applied", c_uint8),
        ("shared_schedule_deduplicated", c_uint8),
        ("membrane_preserved", c_uint8),
        ("outer_modulus_preserved", c_uint8),
    ]


class HHSExactPass219ComposedAdmissionV1(Structure):
    """Historical layout retained for readers/tests; no longer a mutation bridge."""

    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("uqcel", uq.HHSExactUQCELAdmissionV1),
        ("fibonacci", HHSExactPass192FibonacciCompressionV1),
        ("final_receipt_hash72", c_char * 73),
        ("final_hash216_triplet", c_char * 217),
        ("final_hash216_identity", c_char * 217),
    ]


_LIB = uq._LIB
_LIB.hhs_exact_pass192_fibonacci_version.argtypes = []
_LIB.hhs_exact_pass192_fibonacci_version.restype = c_uint32
_LIB.hhs_exact_pass192_fibonacci_compress.argtypes = [
    c_uint32,
    ctypes.POINTER(c_uint8),
    c_size_t,
    ctypes.POINTER(c_size_t),
    ctypes.POINTER(HHSExactPass192FibonacciCompressionV1),
]
_LIB.hhs_exact_pass192_fibonacci_compress.restype = ctypes.c_int
_LIB.hhs_exact_pass192_fibonacci_validate_descriptor.argtypes = [
    c_uint32,
    ctypes.POINTER(c_uint8),
    c_size_t,
]
_LIB.hhs_exact_pass192_fibonacci_validate_descriptor.restype = ctypes.c_int
# Deliberately DO NOT bind hhs_exact_pass219_admit_composed.  Pass 219 1.31
# hides that mutator from the dynamic ABI; production canonical requests use
# hhs_exact_pass219_vm81_pqc_admit_signed instead.


def _char_field(value: bytes) -> str:
    return value.split(b"\x00", 1)[0].decode("ascii")


def _fib_dict(value: HHSExactPass192FibonacciCompressionV1) -> dict[str, int | bool]:
    return {
        "struct_size": int(value.struct_size),
        "version": int(value.version),
        "depth": int(value.depth),
        "lo_shu_cell_count": int(value.lo_shu_cell_count),
        "magnitude_row_count": int(value.magnitude_row_count),
        "shared_schedule_count": int(value.shared_schedule_count),
        "expanded_schedule_count": int(value.expanded_schedule_count),
        "outer_modulus": int(value.outer_modulus),
        "membrane_modulus": int(value.membrane_modulus),
        "membrane_residue": int(value.membrane_residue),
        "descriptor_length": int(value.descriptor_length),
        "compression_applied": bool(value.compression_applied),
        "shared_schedule_deduplicated": bool(value.shared_schedule_deduplicated),
        "membrane_preserved": bool(value.membrane_preserved),
        "outer_modulus_preserved": bool(value.outer_modulus_preserved),
    }


def compress_pass192_fibonacci(depth: int) -> dict[str, object]:
    if not isinstance(depth, int) or depth < 0:
        raise ValueError("depth must be a non-negative integer")
    output = (c_uint8 * HHS_EXACT_PASS192_FIB_MAX_DESCRIPTOR_BYTES)()
    written = c_size_t()
    metadata = HHSExactPass192FibonacciCompressionV1()
    status = int(_LIB.hhs_exact_pass192_fibonacci_compress(
        depth, output, len(output), ctypes.byref(written), ctypes.byref(metadata)
    ))
    descriptor = bytes(output[: written.value])
    validation_status = status
    if status == uq.HHS_EXACT_STATUS_OK:
        owner = (c_uint8 * len(descriptor)).from_buffer_copy(descriptor)
        validation_status = int(_LIB.hhs_exact_pass192_fibonacci_validate_descriptor(
            depth, owner, len(descriptor)
        ))
    return {
        "status": status,
        "validation_status": validation_status,
        "descriptor": descriptor,
        "compression": _fib_dict(metadata),
    }


class HHSExactPass219RuntimeBridge:
    """Historical Python compatibility surface after external-authority closure.

    This class may still validate UQCEL and materialize the inherited Pass 192
    compression descriptor, but it cannot commit a VM81 frame or mint canonical
    Hash72/Hash216 receipts.  Positive canonical mutation is intentionally
    available only through the signed Pass 219 PQC firewall ABI.
    """

    @staticmethod
    def admit_vm81(
        raw_frame: bytes, *, P: int, p: int, q: int, delta: int, A: int, B: int,
        cell81: int, left_basis8: int, right_basis8: int,
        profile: int = uq.HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1,
        source_hash: bytes = uq.HHS_EXACT_UQCEL_SOURCE_SHA256,
        previous_hash72: str = "0" * uq.HHS_EXACT_HASH72_LEN,
    ) -> dict[str, object]:
        if len(raw_frame) != uq.HHS_EXACT_VM81_FRAME_BYTES:
            raise ValueError("VM81 exact frame must be exactly 648 bytes")
        input_value, owners = uq._build_input(
            P=P, p=p, q=q, delta=delta, A=A, B=B,
            cell81=cell81, left_basis8=left_basis8, right_basis8=right_basis8,
            profile=profile, source_hash=source_hash, previous_hash72=previous_hash72,
        )
        _ = owners

        raw_owner = (c_uint8 * len(raw_frame)).from_buffer_copy(raw_frame)
        candidate = HHSExactVM81Frame()
        ingress = int(_LIB.hhs_exact_vm81_frame_import_le(
            raw_owner, len(raw_frame), ctypes.byref(candidate)
        ))
        if ingress != uq.HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"VM81 frame ingress failed: {ingress}")

        validation = uq.HHSExactUQCELAdmissionV1()
        validation_status = int(_LIB.hhs_exact_uqcel_validate(
            ctypes.byref(input_value), ctypes.byref(validation)
        ))
        base = uq._admission_dict(validation)

        # Preserve exact validation failures as diagnostics. No candidate frame
        # is ever committed on this compatibility surface.
        if validation_status != uq.HHS_EXACT_STATUS_OK:
            return {
                "status": validation_status,
                "admitted": False,
                "validated_candidate": False,
                "compatibility_mutation_disabled": True,
                "admission": base,
                "committed_frame": bytes(uq.HHS_EXACT_VM81_FRAME_BYTES),
            }

        fibonacci_result = compress_pass192_fibonacci(HHS_EXACT_PASS219_UCE_FIBONACCI_DEPTH)
        base["fibonacci"] = fibonacci_result["compression"]
        base["pass219_composed_version"] = 0
        base["base_receipt_hash72"] = ""
        base["base_hash216_triplet"] = ""
        base["base_hash216_identity"] = ""
        base["receipt_hash72"] = ""
        base["hash216_triplet"] = ""
        base["hash216_identity"] = ""
        base["frame_committed"] = False

        # A valid legacy candidate is intentionally not a canonical admission.
        return {
            "status": HHS_EXACT_STATUS_INVARIANT_FAILURE,
            "validation_status": validation_status,
            "admitted": False,
            "validated_candidate": True,
            "compatibility_mutation_disabled": True,
            "requires_signed_pqc_admission": True,
            "admission": base,
            "committed_frame": bytes(uq.HHS_EXACT_VM81_FRAME_BYTES),
        }


__all__ = [
    "HHSExactPass219RuntimeBridge",
    "HHSExactPass192FibonacciCompressionV1",
    "HHSExactPass219ComposedAdmissionV1",
    "compress_pass192_fibonacci",
    "HHS_EXACT_PASS219_UCE_FIBONACCI_DEPTH",
    "HHS_EXACT_STATUS_INVARIANT_FAILURE",
]

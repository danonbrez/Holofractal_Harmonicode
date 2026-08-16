from __future__ import annotations

import ctypes
from ctypes import POINTER, Structure, c_char, c_int64, c_size_t, c_uint8, c_uint16, c_uint32, c_uint64

from hhs_python.runtime import hhs_exact_ctypes_bridge as exact_mod
from hhs_python.runtime.hhs_exact_ctypes_bridge import HHSExactVM81Frame

HHS_EXACT_HASH72_LEN = 72
HHS_EXACT_VM81_FRAME_BYTES = 648
HHS_EXACT_STATUS_OK = 0
HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN = 6
HHS_EXACT_STATUS_CONSTRAINT_REJECTED = 7
HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1 = 1
HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1 = 2
HHS_EXACT_UQCEL_DECISION_ADMIT = 1
HHS_EXACT_UQCEL_DECISION_REJECT = 2
HHS_EXACT_UQCEL_DECISION_UNSUPPORTED_DOMAIN = 3
HHS_EXACT_UQCEL_SOURCE_SHA256 = bytes.fromhex(
    "7eb0cc5707a4a58a5a8e4879e0e2e3bdab22c15fe4503fb3a3b0e16596343d42"
)


class HHSExactBigUIntView(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("byte_length", c_uint32),
        ("bytes_be", POINTER(c_uint8)),
    ]


class HHSExactUQCELInputV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("uqcel_version", c_uint32),
        ("profile", c_uint32),
        ("flags", c_uint32),
        ("P", HHSExactBigUIntView),
        ("p", HHSExactBigUIntView),
        ("q", HHSExactBigUIntView),
        ("delta", HHSExactBigUIntView),
        ("A", HHSExactBigUIntView),
        ("B", HHSExactBigUIntView),
        ("cell81", c_uint8),
        ("left_basis8", c_uint8),
        ("right_basis8", c_uint8),
        ("reserved0", c_uint8),
        ("source_envelope_sha256", c_uint8 * 32),
        ("previous_hash72", c_char * 73),
    ]


class HHSExactUQCELAdmissionV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("uqcel_version", c_uint32),
        ("profile", c_uint32),
        ("decision", c_uint32),
        ("reject_reason", c_uint32),
        ("reserved0", c_uint32),
        ("required_mask", c_uint64),
        ("satisfied_mask", c_uint64),
        ("failed_mask", c_uint64),
        ("residual_mask", c_uint64),
        ("vm5184_address", c_uint16),
        ("ordered_tag", c_uint16),
        ("qr_bit", c_uint8),
        ("expected_lane", c_uint8),
        ("expected_phase", c_uint8),
        ("observed_phase", c_uint8),
        ("source_hash_match", c_uint8),
        ("bigint_domain_exact", c_uint8),
        ("frame_committed", c_uint8),
        ("reserved1", c_uint8),
        ("primitive_metric_numerator", c_int64),
        ("primitive_metric_denominator", c_uint64),
        ("full_cycle_metric_exponent", c_int64),
        ("metric_power", c_uint64),
        ("change_hash72", c_char * 73),
        ("receipt_hash72", c_char * 73),
        ("hash216_triplet", c_char * 217),
        ("hash216_identity", c_char * 217),
    ]


_LIB = exact_mod._RUNTIME_LIB
_LIB.hhs_exact_uqcel_version.argtypes = []
_LIB.hhs_exact_uqcel_version.restype = c_uint32
_LIB.hhs_exact_uqcel_source_sha256.argtypes = [POINTER(c_uint8)]
_LIB.hhs_exact_uqcel_source_sha256.restype = ctypes.c_int
_LIB.hhs_exact_uqcel_validate.argtypes = [
    POINTER(HHSExactUQCELInputV1),
    POINTER(HHSExactUQCELAdmissionV1),
]
_LIB.hhs_exact_uqcel_validate.restype = ctypes.c_int
_LIB.hhs_exact_vm81_admit_uqcel.argtypes = [
    POINTER(HHSExactUQCELInputV1),
    POINTER(HHSExactVM81Frame),
    POINTER(HHSExactVM81Frame),
    POINTER(HHSExactUQCELAdmissionV1),
]
_LIB.hhs_exact_vm81_admit_uqcel.restype = ctypes.c_int


def _int_to_min_bytes(value: int) -> bytes:
    if not isinstance(value, int) or value < 0:
        raise ValueError("UQCEL BigUInt values must be non-negative integers")
    return value.to_bytes(max(1, (value.bit_length() + 7) // 8), "big")


def _char_field(value: bytes) -> str:
    return value.split(b"\x00", 1)[0].decode("ascii")


def _admission_dict(value: HHSExactUQCELAdmissionV1) -> dict[str, int | str | bool]:
    return {
        "struct_size": int(value.struct_size),
        "uqcel_version": int(value.uqcel_version),
        "profile": int(value.profile),
        "decision": int(value.decision),
        "reject_reason": int(value.reject_reason),
        "required_mask": int(value.required_mask),
        "satisfied_mask": int(value.satisfied_mask),
        "failed_mask": int(value.failed_mask),
        "residual_mask": int(value.residual_mask),
        "vm5184_address": int(value.vm5184_address),
        "ordered_tag": int(value.ordered_tag),
        "qr_bit": int(value.qr_bit),
        "expected_lane": int(value.expected_lane),
        "expected_phase": int(value.expected_phase),
        "observed_phase": int(value.observed_phase),
        "source_hash_match": bool(value.source_hash_match),
        "bigint_domain_exact": bool(value.bigint_domain_exact),
        "frame_committed": bool(value.frame_committed),
        "primitive_metric_numerator": int(value.primitive_metric_numerator),
        "primitive_metric_denominator": int(value.primitive_metric_denominator),
        "full_cycle_metric_exponent": int(value.full_cycle_metric_exponent),
        "metric_power": int(value.metric_power),
        "change_hash72": _char_field(bytes(value.change_hash72)),
        "receipt_hash72": _char_field(bytes(value.receipt_hash72)),
        "hash216_triplet": _char_field(bytes(value.hash216_triplet)),
        "hash216_identity": _char_field(bytes(value.hash216_identity)),
    }


def _build_input(
    *, P: int, p: int, q: int, delta: int, A: int, B: int,
    cell81: int, left_basis8: int, right_basis8: int, profile: int,
    source_hash: bytes, previous_hash72: str,
) -> tuple[HHSExactUQCELInputV1, list[object]]:
    if len(source_hash) != 32:
        raise ValueError("source_hash must contain exactly 32 bytes")
    previous = previous_hash72.encode("ascii")
    if len(previous) != HHS_EXACT_HASH72_LEN:
        raise ValueError("previous_hash72 must contain exactly 72 ASCII symbols")

    input_value = HHSExactUQCELInputV1()
    input_value.struct_size = ctypes.sizeof(input_value)
    input_value.uqcel_version = int(_LIB.hhs_exact_uqcel_version())
    input_value.profile = profile
    input_value.flags = 0
    owners: list[object] = []
    for field_name, integer in (("P", P), ("p", p), ("q", q), ("delta", delta), ("A", A), ("B", B)):
        raw = _int_to_min_bytes(integer)
        owner = (c_uint8 * len(raw)).from_buffer_copy(raw)
        owners.append(owner)
        view = HHSExactBigUIntView()
        view.struct_size = ctypes.sizeof(view)
        view.byte_length = len(raw)
        view.bytes_be = ctypes.cast(owner, POINTER(c_uint8))
        setattr(input_value, field_name, view)
    input_value.cell81 = cell81
    input_value.left_basis8 = left_basis8
    input_value.right_basis8 = right_basis8
    for index, octet in enumerate(source_hash):
        input_value.source_envelope_sha256[index] = octet
    input_value.previous_hash72 = previous
    return input_value, owners


class HHSUQCELRuntimeBridge:
    @staticmethod
    def source_sha256() -> bytes:
        output = (c_uint8 * 32)()
        status = int(_LIB.hhs_exact_uqcel_source_sha256(output))
        if status != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"UQCEL source hash retrieval failed: {status}")
        return bytes(output)

    @staticmethod
    def validate(
        *, P: int, p: int, q: int, delta: int, A: int, B: int,
        cell81: int, left_basis8: int, right_basis8: int,
        profile: int = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1,
        source_hash: bytes = HHS_EXACT_UQCEL_SOURCE_SHA256,
        previous_hash72: str = "0" * HHS_EXACT_HASH72_LEN,
    ) -> dict[str, object]:
        input_value, owners = _build_input(
            P=P, p=p, q=q, delta=delta, A=A, B=B,
            cell81=cell81, left_basis8=left_basis8, right_basis8=right_basis8,
            profile=profile, source_hash=source_hash, previous_hash72=previous_hash72,
        )
        _ = owners
        admission = HHSExactUQCELAdmissionV1()
        status = int(_LIB.hhs_exact_uqcel_validate(ctypes.byref(input_value), ctypes.byref(admission)))
        return {"status": status, "admission": _admission_dict(admission)}

    @staticmethod
    def admit_vm81(
        raw_frame: bytes, *, P: int, p: int, q: int, delta: int, A: int, B: int,
        cell81: int, left_basis8: int, right_basis8: int,
        profile: int = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1,
        source_hash: bytes = HHS_EXACT_UQCEL_SOURCE_SHA256,
        previous_hash72: str = "0" * HHS_EXACT_HASH72_LEN,
    ) -> dict[str, object]:
        if len(raw_frame) != HHS_EXACT_VM81_FRAME_BYTES:
            raise ValueError("VM81 exact frame must be exactly 648 bytes")
        input_value, owners = _build_input(
            P=P, p=p, q=q, delta=delta, A=A, B=B,
            cell81=cell81, left_basis8=left_basis8, right_basis8=right_basis8,
            profile=profile, source_hash=source_hash, previous_hash72=previous_hash72,
        )
        _ = owners
        raw_owner = (c_uint8 * len(raw_frame)).from_buffer_copy(raw_frame)
        candidate = HHSExactVM81Frame()
        ingress = int(_LIB.hhs_exact_vm81_frame_import_le(raw_owner, len(raw_frame), ctypes.byref(candidate)))
        if ingress != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"VM81 frame ingress failed: {ingress}")
        committed = HHSExactVM81Frame()
        admission = HHSExactUQCELAdmissionV1()
        status = int(_LIB.hhs_exact_vm81_admit_uqcel(
            ctypes.byref(input_value), ctypes.byref(candidate), ctypes.byref(committed), ctypes.byref(admission)
        ))
        output = (c_uint8 * HHS_EXACT_VM81_FRAME_BYTES)()
        written = c_size_t()
        egress = int(_LIB.hhs_exact_vm81_frame_export_le(
            ctypes.byref(committed), output, len(output), ctypes.byref(written)
        ))
        if egress != HHS_EXACT_STATUS_OK:
            raise RuntimeError(f"VM81 frame egress failed: {egress}")
        data = bytes(output[: written.value])
        admission_dict = _admission_dict(admission)
        return {
            "status": status,
            "admitted": status == HHS_EXACT_STATUS_OK and admission_dict["decision"] == HHS_EXACT_UQCEL_DECISION_ADMIT,
            "admission": admission_dict,
            "committed_frame": data,
        }


__all__ = [
    "HHSUQCELRuntimeBridge",
    "HHSExactBigUIntView",
    "HHSExactUQCELInputV1",
    "HHSExactUQCELAdmissionV1",
    "HHS_EXACT_STATUS_OK",
    "HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN",
    "HHS_EXACT_STATUS_CONSTRAINT_REJECTED",
    "HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1",
    "HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1",
    "HHS_EXACT_UQCEL_SOURCE_SHA256",
]

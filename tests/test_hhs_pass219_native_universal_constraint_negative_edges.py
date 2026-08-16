from __future__ import annotations

import ctypes
import hashlib
from ctypes import POINTER, c_uint8
from pathlib import Path

from hhs_python.runtime import hhs_uqcel_ctypes_bridge as uqcel_mod
from hhs_python.runtime.hhs_uqcel_ctypes_bridge import (
    HHSExactUQCELAdmissionV1,
    HHSUQCELRuntimeBridge,
    HHS_EXACT_STATUS_CONSTRAINT_REJECTED,
)

ROOT = Path(__file__).resolve().parents[1]


def _git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def test_even_quadratic_reciprocity_input_fails_closed() -> None:
    P = 4
    p = 2
    q = 3
    p2 = P * P
    result = HHSUQCELRuntimeBridge.admit_vm81(
        bytes(648),
        P=P,
        p=p,
        q=q,
        delta=p2 - p * q,
        A=p2,
        B=p2,
        cell81=0,
        left_basis8=0,
        right_basis8=1,
    )
    assert result["status"] == HHS_EXACT_STATUS_CONSTRAINT_REJECTED
    assert result["admission"]["reject_reason"] == 6
    assert result["committed_frame"] == bytes(648)


def test_noncanonical_biguint_leading_zero_fails_closed() -> None:
    input_value, owners = uqcel_mod._build_input(
        P=4,
        p=3,
        q=5,
        delta=1,
        A=16,
        B=16,
        cell81=0,
        left_basis8=0,
        right_basis8=1,
        profile=1,
        source_hash=uqcel_mod.HHS_EXACT_UQCEL_SOURCE_SHA256,
        previous_hash72="0" * 72,
    )
    _ = owners
    noncanonical = (c_uint8 * 2)(0, 4)
    input_value.P.byte_length = 2
    input_value.P.bytes_be = ctypes.cast(noncanonical, POINTER(c_uint8))
    admission = HHSExactUQCELAdmissionV1()
    status = int(uqcel_mod._LIB.hhs_exact_uqcel_validate(
        ctypes.byref(input_value), ctypes.byref(admission)
    ))
    assert status == HHS_EXACT_STATUS_CONSTRAINT_REJECTED
    assert admission.reject_reason == 2
    assert admission.decision == 2


def test_biguint_transport_bound_fails_closed_without_truncation() -> None:
    input_value, owners = uqcel_mod._build_input(
        P=4,
        p=3,
        q=5,
        delta=1,
        A=16,
        B=16,
        cell81=0,
        left_basis8=0,
        right_basis8=1,
        profile=1,
        source_hash=uqcel_mod.HHS_EXACT_UQCEL_SOURCE_SHA256,
        previous_hash72="0" * 72,
    )
    _ = owners
    oversized = (c_uint8 * 649)(*([1] + [0] * 648))
    input_value.P.byte_length = 649
    input_value.P.bytes_be = ctypes.cast(oversized, POINTER(c_uint8))
    admission = HHSExactUQCELAdmissionV1()
    status = int(uqcel_mod._LIB.hhs_exact_uqcel_validate(
        ctypes.byref(input_value), ctypes.byref(admission)
    ))
    assert status == HHS_EXACT_STATUS_CONSTRAINT_REJECTED
    assert admission.reject_reason == 2


def test_invalid_previous_hash72_cannot_commit_candidate_frame() -> None:
    result = HHSUQCELRuntimeBridge.admit_vm81(
        bytes([0xA5]) * 648,
        P=4,
        p=3,
        q=5,
        delta=1,
        A=16,
        B=16,
        cell81=0,
        left_basis8=0,
        right_basis8=1,
        previous_hash72="~" * 72,
    )
    assert result["status"] == HHS_EXACT_STATUS_CONSTRAINT_REJECTED
    assert result["admitted"] is False
    assert result["committed_frame"] == bytes(648)


def test_frozen_exact_v1_1_sources_are_original_git_blobs() -> None:
    assert _git_blob_sha(ROOT / "hhs_runtime/include/hhs_runtime_exact_abi_v1_1_base.h") == (
        "8b9e76a17f3fe05403312a7a643af34db3792b6e"
    )
    assert _git_blob_sha(ROOT / "hhs_runtime/c/hhs_runtime_exact_abi_v1_1_base.inc") == (
        "9d4c35d83b395ae372f5e7b5ddbd0e242600a1ad"
    )

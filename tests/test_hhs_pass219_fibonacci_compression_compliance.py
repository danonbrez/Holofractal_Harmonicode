from __future__ import annotations

from fractions import Fraction
from pathlib import Path

from hhs_python.runtime.hhs_pass219_composed_ctypes_bridge import (
    HHSExactPass219RuntimeBridge,
    compress_pass192_fibonacci,
)
from hhs_python.runtime.hhs_uqcel_ctypes_bridge import (
    HHSUQCELRuntimeBridge,
    HHS_EXACT_STATUS_CONSTRAINT_REJECTED,
    HHS_EXACT_STATUS_OK,
    HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN,
    HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1,
)
from hhs_runtime.pass219_fibonacci_compression_reference_v1 import (
    OUTER_HYDRATION_MODULUS,
    build_witness,
    expanded_cell_schedules,
    fibonacci_prefix,
    reference_invariants,
    source_membrane_depth,
)

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = b"HHS-P192-NESTED-MODULAR-FIBONACCI-COMPRESSION-V1"


def _frame() -> bytes:
    return bytes((index * 17 + 11) & 0xFF for index in range(648))


def _read_u32(raw: bytes, cursor: int) -> tuple[int, int]:
    return int.from_bytes(raw[cursor : cursor + 4], "big"), cursor + 4


def _read_big(raw: bytes, cursor: int) -> tuple[int, int]:
    length = int.from_bytes(raw[cursor : cursor + 2], "big")
    cursor += 2
    value = int.from_bytes(raw[cursor : cursor + length], "big")
    return value, cursor + length


def _parse_descriptor(raw: bytes) -> dict[str, int]:
    assert raw.startswith(DOMAIN)
    cursor = len(DOMAIN)
    names = (
        "version",
        "seed0",
        "seed1",
        "depth",
        "cells",
        "shared",
        "outer_modulus",
        "membrane_modulus",
        "membrane_residue",
    )
    values: dict[str, int] = {}
    for name in names:
        values[name], cursor = _read_u32(raw, cursor)
    values["f_depth"], cursor = _read_big(raw, cursor)
    values["f_next"], cursor = _read_big(raw, cursor)
    assert cursor == len(raw)
    return values


def test_pass192_reference_is_bound_to_native_uce_membrane_depth() -> None:
    assert source_membrane_depth() == 10
    witness = build_witness(10)
    assert witness.f_depth == 144
    assert witness.f_next == 233
    assert witness.transition == Fraction(144, 233)
    assert witness.cumulative_scale == Fraction(1, 144)
    assert witness.membrane_modulus == 11
    assert witness.membrane_residue == 10
    assert all(reference_invariants().values())


def test_exact_c_descriptor_reconstructs_pass192_terminal_and_membrane_witness() -> None:
    result = compress_pass192_fibonacci(source_membrane_depth())
    assert result["status"] == HHS_EXACT_STATUS_OK
    assert result["validation_status"] == HHS_EXACT_STATUS_OK
    metadata = result["compression"]
    parsed = _parse_descriptor(result["descriptor"])
    assert metadata["compression_applied"] is True
    assert metadata["shared_schedule_deduplicated"] is True
    assert metadata["membrane_preserved"] is True
    assert metadata["outer_modulus_preserved"] is True
    assert metadata["lo_shu_cell_count"] == 9
    assert metadata["shared_schedule_count"] == 1
    assert metadata["expanded_schedule_count"] == 9
    assert parsed["seed0"] == 1 and parsed["seed1"] == 2
    assert parsed["depth"] == 10
    assert parsed["f_depth"] == 144 and parsed["f_next"] == 233
    assert parsed["membrane_modulus"] == 11
    assert parsed["membrane_residue"] == 10
    assert parsed["outer_modulus"] == OUTER_HYDRATION_MODULUS


def test_compressed_shared_schedule_is_lossless_and_smaller_than_naive_cell_expansion() -> None:
    depth = source_membrane_depth()
    compact = compress_pass192_fibonacci(depth)["descriptor"]
    schedules = expanded_cell_schedules(depth)
    assert len(schedules) == 9
    assert all(schedule == fibonacci_prefix(depth) for schedule in schedules)
    naive = bytearray()
    for schedule in schedules:
        for value in schedule:
            encoded = value.to_bytes(max(1, (value.bit_length() + 7) // 8), "big")
            naive.extend(len(encoded).to_bytes(2, "big"))
            naive.extend(encoded)
    assert len(compact) < len(naive)


def test_outer_hydration_modulus_is_namespace_not_destructive_local_reduction() -> None:
    descriptor = _parse_descriptor(compress_pass192_fibonacci(10)["descriptor"])
    assert descriptor["outer_modulus"] == 1_259_713
    assert descriptor["f_depth"] == 144
    assert descriptor["f_next"] == 233
    assert descriptor["membrane_residue"] == 10
    assert descriptor["f_depth"] != descriptor["f_depth"] % 1  # local value is not a modulus-zero alias


def test_canonical_pass219_admission_composes_fibonacci_before_commit_and_lineage() -> None:
    raw = _frame()
    low_level = HHSUQCELRuntimeBridge.admit_vm81(
        raw, P=4, p=3, q=5, delta=1, A=16, B=16,
        cell81=41, left_basis8=0, right_basis8=1,
    )
    composed = HHSExactPass219RuntimeBridge.admit_vm81(
        raw, P=4, p=3, q=5, delta=1, A=16, B=16,
        cell81=41, left_basis8=0, right_basis8=1,
    )
    assert low_level["status"] == HHS_EXACT_STATUS_OK
    assert composed["status"] == HHS_EXACT_STATUS_OK
    assert composed["admitted"] is True
    assert composed["committed_frame"] == raw
    admission = composed["admission"]
    fib = admission["fibonacci"]
    assert fib["depth"] == 10
    assert fib["lo_shu_cell_count"] == 9
    assert fib["shared_schedule_count"] == 1
    assert fib["compression_applied"] is True
    assert admission["base_receipt_hash72"] == low_level["admission"]["receipt_hash72"]
    assert admission["receipt_hash72"] != admission["base_receipt_hash72"]
    assert admission["hash216_triplet"][144:] == admission["receipt_hash72"]
    assert len(admission["hash216_identity"]) == 216


def test_composed_gate_preserves_rejection_and_unsupported_fail_closed_behavior() -> None:
    rejected = HHSExactPass219RuntimeBridge.admit_vm81(
        _frame(), P=4, p=3, q=5, delta=2, A=16, B=16,
        cell81=41, left_basis8=0, right_basis8=1,
    )
    assert rejected["status"] == HHS_EXACT_STATUS_CONSTRAINT_REJECTED
    assert rejected["admitted"] is False
    assert rejected["committed_frame"] == bytes(648)
    assert rejected["admission"]["fibonacci"]["compression_applied"] is False

    unresolved = HHSExactPass219RuntimeBridge.admit_vm81(
        _frame(), P=4, p=3, q=5, delta=1, A=16, B=16,
        cell81=41, left_basis8=0, right_basis8=1,
        profile=HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1,
    )
    assert unresolved["status"] == HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN
    assert unresolved["admitted"] is False
    assert unresolved["committed_frame"] == bytes(648)


def test_new_fibonacci_authority_contains_no_float_or_transcendental_path() -> None:
    for relative in (
        "hhs_runtime/include/hhs_pass192_fibonacci_compression_1_9.h",
        "hhs_runtime/c/hhs_pass192_fibonacci_compression_1_9.inc",
        "hhs_runtime/pass219_fibonacci_compression_reference_v1.py",
        "hhs_python/runtime/hhs_pass219_composed_ctypes_bridge.py",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        for forbidden in ("double", "<math.h>", "sqrt(", "sin(", "cos(", "pow(", "log(", "exp("):
            assert forbidden not in text

from __future__ import annotations

from hhs_python.runtime.hhs_pass219_composed_ctypes_bridge import (
    HHSExactPass219RuntimeBridge,
    HHS_EXACT_STATUS_INVARIANT_FAILURE,
    compress_pass192_fibonacci,
)
from hhs_python.runtime.hhs_uqcel_ctypes_bridge import (
    HHSUQCELRuntimeBridge,
    HHS_EXACT_STATUS_CONSTRAINT_REJECTED,
    HHS_EXACT_STATUS_OK,
    HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN,
    HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1,
)

ZERO_FRAME = bytes(648)
ZERO72 = "0" * 72


def _frame() -> bytes:
    return bytes((index * 29 + 7) & 0xFF for index in range(648))


def _validate(**overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "P": 4,
        "p": 3,
        "q": 5,
        "delta": 1,
        "A": 16,
        "B": 16,
        "cell81": 41,
        "left_basis8": 0,
        "right_basis8": 1,
        "previous_hash72": ZERO72,
    }
    values.update(overrides)
    return HHSUQCELRuntimeBridge.validate(**values)  # type: ignore[arg-type]


def _compat_admit(**overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "P": 4,
        "p": 3,
        "q": 5,
        "delta": 1,
        "A": 16,
        "B": 16,
        "cell81": 41,
        "left_basis8": 0,
        "right_basis8": 1,
        "previous_hash72": ZERO72,
    }
    values.update(overrides)
    return HHSExactPass219RuntimeBridge.admit_vm81(  # type: ignore[arg-type]
        _frame(), **values
    )


def test_valid_uqcel_candidate_remains_exactly_validatable_without_commit() -> None:
    result = _validate()
    admission = result["admission"]
    assert result["status"] == HHS_EXACT_STATUS_OK
    assert admission["decision"] == 1
    assert admission["reject_reason"] == 0
    assert admission["required_mask"] == 0x3FF
    assert admission["satisfied_mask"] & 0x3FF == 0x3FF
    assert admission["failed_mask"] == 0
    assert admission["frame_committed"] is False


def test_bigint_validation_remains_exact_without_narrowing() -> None:
    P = (1 << 130) + 1
    p = 3
    q = 5
    p2 = P * P
    result = _validate(P=P, p=p, q=q, delta=p2 - p * q, A=p2, B=p2, cell81=80)
    assert result["status"] == HHS_EXACT_STATUS_OK
    assert result["admission"]["decision"] == 1
    assert result["admission"]["frame_committed"] is False


def test_validation_rejections_preserve_exact_reason_codes() -> None:
    wrong_delta = _validate(delta=2)
    assert wrong_delta["status"] == HHS_EXACT_STATUS_CONSTRAINT_REJECTED
    assert wrong_delta["admission"]["reject_reason"] == 3

    wrong_symmetry = _validate(A=17)
    assert wrong_symmetry["status"] == HHS_EXACT_STATUS_CONSTRAINT_REJECTED
    assert wrong_symmetry["admission"]["reject_reason"] == 4

    wrong_qr = _validate(P=5, p=3, q=7, delta=4, A=25, B=25, left_basis8=0, right_basis8=1)
    assert wrong_qr["status"] == HHS_EXACT_STATUS_CONSTRAINT_REJECTED
    assert wrong_qr["admission"]["reject_reason"] == 7


def test_full_symbolic_residual_remains_unsupported_not_approximately_admitted() -> None:
    result = _validate(profile=HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1)
    assert result["status"] == HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN
    assert result["admission"]["decision"] == 3
    assert result["admission"]["reject_reason"] == 9
    assert result["admission"]["residual_mask"] == 0x1F


def test_legacy_python_composed_call_cannot_mutate_or_mint_receipts() -> None:
    result = _compat_admit()
    admission = result["admission"]
    assert result["status"] == HHS_EXACT_STATUS_INVARIANT_FAILURE
    assert result["validation_status"] == HHS_EXACT_STATUS_OK
    assert result["validated_candidate"] is True
    assert result["compatibility_mutation_disabled"] is True
    assert result["requires_signed_pqc_admission"] is True
    assert result["admitted"] is False
    assert result["committed_frame"] == ZERO_FRAME
    assert admission["frame_committed"] is False
    assert admission["receipt_hash72"] == ""
    assert admission["hash216_triplet"] == ""
    assert admission["hash216_identity"] == ""


def test_legacy_compatibility_surface_preserves_validation_rejection_without_commit() -> None:
    result = _compat_admit(delta=2)
    assert result["status"] == HHS_EXACT_STATUS_CONSTRAINT_REJECTED
    assert result["compatibility_mutation_disabled"] is True
    assert result["admitted"] is False
    assert result["committed_frame"] == ZERO_FRAME
    assert result["admission"]["reject_reason"] == 3


def test_pass192_descriptor_remains_exact_and_non_authoritative() -> None:
    result = compress_pass192_fibonacci(10)
    assert result["status"] == HHS_EXACT_STATUS_OK
    assert result["validation_status"] == HHS_EXACT_STATUS_OK
    metadata = result["compression"]
    assert metadata["depth"] == 10
    assert metadata["lo_shu_cell_count"] == 9
    assert metadata["magnitude_row_count"] == 5
    assert metadata["shared_schedule_count"] == 1
    assert metadata["expanded_schedule_count"] == 45
    assert metadata["compression_applied"] is True
    assert metadata["shared_schedule_deduplicated"] is True
    assert metadata["membrane_preserved"] is True
    assert metadata["outer_modulus_preserved"] is True

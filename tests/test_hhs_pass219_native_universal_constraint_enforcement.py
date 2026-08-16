from __future__ import annotations

from pathlib import Path

from hhs_python.runtime.hhs_uqcel_ctypes_bridge import (
    HHSUQCELRuntimeBridge,
    HHS_EXACT_STATUS_CONSTRAINT_REJECTED,
    HHS_EXACT_STATUS_OK,
    HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN,
    HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1,
    HHS_EXACT_UQCEL_SOURCE_SHA256,
)
from hhs_runtime.pass219_native_universal_constraint_v1 import (
    CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SHA256,
    CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SOURCE,
    build_integer_symmetric_witness,
    expected_phase_basis_pair,
    reference_invariants,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "contracts" / "pass219" / "PASS_219_NATIVE_UNIVERSAL_CONSTRAINT_ENVELOPE_1_8_0.harmonicode"
ZERO72 = "0" * 72


def _frame() -> bytes:
    return bytes((index * 29 + 7) & 0xFF for index in range(648))


def _call(P: int, p: int, q: int, *, profile: int = 1, **overrides: object) -> dict[str, object]:
    witness = build_integer_symmetric_witness(P, p, q)
    left, right = expected_phase_basis_pair(witness)
    values: dict[str, object] = {
        "P": witness.P,
        "p": witness.p,
        "q": witness.q,
        "delta": witness.delta,
        "A": witness.A,
        "B": witness.B,
        "cell81": 41,
        "left_basis8": left,
        "right_basis8": right,
        "profile": profile,
        "source_hash": HHS_EXACT_UQCEL_SOURCE_SHA256,
        "previous_hash72": ZERO72,
    }
    values.update(overrides)
    return HHSUQCELRuntimeBridge.admit_vm81(_frame(), **values)  # type: ignore[arg-type]


def test_native_uce_fixture_and_c_source_hash_are_exact() -> None:
    raw = FIXTURE.read_bytes()
    assert raw.decode("utf-8") == CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SOURCE
    assert CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SHA256 == HHS_EXACT_UQCEL_SOURCE_SHA256
    assert HHSUQCELRuntimeBridge.source_sha256() == HHS_EXACT_UQCEL_SOURCE_SHA256


def test_xy_and_yx_profiles_admit_and_commit_exact_vm81_frame() -> None:
    xy = _call(4, 3, 5)
    yx = _call(5, 3, 7)
    for result, bit, phase, tag in ((xy, 0, 0, 0x5859), (yx, 1, 36, 0x5958)):
        admission = result["admission"]
        assert result["status"] == HHS_EXACT_STATUS_OK
        assert result["admitted"] is True
        assert result["committed_frame"] == _frame()
        assert admission["frame_committed"] is True
        assert admission["qr_bit"] == bit
        assert admission["expected_phase"] == phase
        assert admission["observed_phase"] == phase
        assert admission["ordered_tag"] == tag


def test_bigint_p_above_uint64_is_admitted_without_narrowing() -> None:
    P = (1 << 130) + 1
    p = 3
    q = 5
    p2 = P * P
    result = HHSUQCELRuntimeBridge.admit_vm81(
        _frame(),
        P=P,
        p=p,
        q=q,
        delta=p2 - p * q,
        A=p2,
        B=p2,
        cell81=80,
        left_basis8=0,
        right_basis8=1,
    )
    assert result["status"] == HHS_EXACT_STATUS_OK
    assert result["admitted"] is True
    assert result["committed_frame"] == _frame()


def test_wrong_delta_rejects_and_never_commits_candidate() -> None:
    witness = build_integer_symmetric_witness(4, 3, 5)
    result = _call(4, 3, 5, delta=witness.delta + 1)
    assert result["status"] == HHS_EXACT_STATUS_CONSTRAINT_REJECTED
    assert result["admitted"] is False
    assert result["admission"]["reject_reason"] == 3
    assert result["committed_frame"] == bytes(648)


def test_wrong_a_or_b_rejects_symmetric_projection() -> None:
    witness = build_integer_symmetric_witness(4, 3, 5)
    result = _call(4, 3, 5, A=witness.A + 1)
    assert result["status"] == HHS_EXACT_STATUS_CONSTRAINT_REJECTED
    assert result["admission"]["reject_reason"] == 4
    assert result["committed_frame"] == bytes(648)


def test_wrong_qr_orientation_rejects_before_vm81_commit() -> None:
    result = _call(5, 3, 7, left_basis8=0, right_basis8=1)
    assert result["status"] == HHS_EXACT_STATUS_CONSTRAINT_REJECTED
    assert result["admission"]["reject_reason"] == 7
    assert result["committed_frame"] == bytes(648)


def test_source_expression_hash_mismatch_fails_closed() -> None:
    bad_hash = bytes([HHS_EXACT_UQCEL_SOURCE_SHA256[0] ^ 1]) + HHS_EXACT_UQCEL_SOURCE_SHA256[1:]
    result = _call(4, 3, 5, source_hash=bad_hash)
    assert result["status"] == HHS_EXACT_STATUS_CONSTRAINT_REJECTED
    assert result["admission"]["reject_reason"] == 1
    assert result["committed_frame"] == bytes(648)


def test_full_symbolic_profile_is_unresolved_not_approximately_admitted() -> None:
    result = _call(4, 3, 5, profile=HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1)
    admission = result["admission"]
    assert result["status"] == HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN
    assert result["admitted"] is False
    assert admission["decision"] == 3
    assert admission["reject_reason"] == 9
    assert admission["residual_mask"] == 0xF
    assert result["committed_frame"] == bytes(648)


def test_hash72_hash216_receipt_lineage_is_deterministic_and_typed() -> None:
    first = _call(5, 3, 7)
    second = _call(5, 3, 7)
    a = first["admission"]
    b = second["admission"]
    assert a["change_hash72"] == b["change_hash72"]
    assert a["receipt_hash72"] == b["receipt_hash72"]
    assert a["hash216_triplet"] == b["hash216_triplet"]
    assert a["hash216_identity"] == b["hash216_identity"]
    assert len(a["change_hash72"]) == 72
    assert len(a["receipt_hash72"]) == 72
    assert len(a["hash216_triplet"]) == 216
    assert len(a["hash216_identity"]) == 216
    assert a["hash216_triplet"][:72] == ZERO72
    assert a["hash216_triplet"][72:144] == a["change_hash72"]
    assert a["hash216_triplet"][144:] == a["receipt_hash72"]


def test_uqcel_metric_and_required_constraint_mask_are_exact() -> None:
    result = _call(4, 3, 5)
    admission = result["admission"]
    assert admission["primitive_metric_numerator"] == -11
    assert admission["primitive_metric_denominator"] == 12
    assert admission["full_cycle_metric_exponent"] == -66
    assert admission["metric_power"] == 5256
    assert admission["required_mask"] == 0x3FF
    assert admission["satisfied_mask"] & 0x3FF == 0x3FF
    assert admission["failed_mask"] == 0


def test_new_authority_sources_contain_no_approximate_numeric_operations() -> None:
    for relative in (
        "hhs_runtime/pass219_native_universal_constraint_v1.py",
        "hhs_runtime/include/hhs_runtime_uqcel_1_8.h",
        "hhs_runtime/c/hhs_runtime_uqcel_1_8_bigint.inc",
        "hhs_runtime/c/hhs_runtime_uqcel_1_8_validate.inc",
        "hhs_runtime/c/hhs_runtime_uqcel_1_8_receipt.inc",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        for forbidden in ("float(", "double", "<math.h>", "sqrt(", "sin(", "cos(", "pow(", "log(", "exp("):
            assert forbidden not in text


def test_independent_reference_invariants_are_all_true() -> None:
    assert all(reference_invariants().values())

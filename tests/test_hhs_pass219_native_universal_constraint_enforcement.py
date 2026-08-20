from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

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
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_integrated_manifold_engine_v2 import (
    verify_integrated_manifold_search,
)
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_manifold_kernel_v1 import (
    MANIFOLD_SOURCE,
    lo_shu_manifold_reduction,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "contracts" / "pass219" / "PASS_219_NATIVE_UNIVERSAL_CONSTRAINT_ENVELOPE_1_8_0.harmonicode"
PASS191_EVIDENCE = (
    ROOT
    / "native_projects"
    / "hhs_pass191_dyadic_quartic_phase_lattice"
    / "evidence"
    / "PASS_191_INTEGRATED_PROOF_SEARCH.json"
)
PASS191_COMPLETION = (
    ROOT
    / "native_projects"
    / "hhs_pass191_dyadic_quartic_phase_lattice"
    / "evidence"
    / "PASS_191_INTEGRATED_COMPLETION_RECEIPT.json"
)
EXPECTED_PASS191_AUTHORITY_PATH = [
    "PASS_189_HQLH_51648192_CONTEXTUAL_FABRIC",
    "PASS_191_EXACT_MANIFOLD_RESIDUAL_KERNEL",
    "PASS_186_X86_64_Q144_NONCOMMUTATIVE_ABI",
    "PASS_175_HASH216_VM5184_G243_HYDRATION",
    "PASS_174_SINGLETON_VM81_COMMIT_AUTHORITY",
    "HASH72_DETERMINISTIC_REPLAY",
]
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


def _presentation_normalize(source: str) -> str:
    """Normalize source-glyph spelling only; do not rewrite the algebra."""
    return (
        source.replace("P³", "P^3")
        .replace("P²", "P^2")
        .replace("t³", "t^3")
        .replace("∆", "Delta")
        .replace("√", "Sqrt")
        .replace("u⁷²", "u^72")
        .replace("x²", "x^2")
    )


def _pass191_evidence() -> dict[str, object]:
    return json.loads(PASS191_EVIDENCE.read_text(encoding="utf-8"))


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
    assert admission["residual_mask"] == 0x1F
    assert admission["residual_mask"] & 0x10 == 0x10
    assert result["committed_frame"] == bytes(648)


def test_full_symbolic_a_b_are_lhs_rhs_not_integer_symmetric_aliases() -> None:
    result = _call(
        4,
        3,
        5,
        profile=HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1,
        A=17,
        B=19,
    )
    admission = result["admission"]
    assert result["status"] == HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN
    assert result["admitted"] is False
    assert admission["decision"] == 3
    assert admission["reject_reason"] == 9
    assert admission["residual_mask"] & 0x10 == 0x10
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


def test_native_uce_is_existing_pass191_manifold_source_not_new_runtime_logic() -> None:
    assert _presentation_normalize(MANIFOLD_SOURCE) == (
        CANONICAL_NATIVE_UNIVERSAL_CONSTRAINT_SOURCE.rstrip("\n")
    )


def test_inherited_pass191_lo_shu_reduction_closes_exactly() -> None:
    reduction = lo_shu_manifold_reduction()
    assert reduction["matrix"] == [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
    assert all(reduction["checks"].values())


def test_inherited_pass191_full_manifold_receipt_replays() -> None:
    payload = _pass191_evidence()
    verified = verify_integrated_manifold_search(payload)
    assert verified == {
        "ok": True,
        "classification": "HHS_PASS_191_UNIFIED_MANIFOLD_VM81_PROOF_SEARCH_EXECUTED",
        "integrated_manifold_search_hash72": payload["integrated_manifold_search_hash72"],
        "projected_cardinality": 1_259_712,
        "contextual_cardinality": 51_648_192,
        "visited": 51_648_192,
        "exact_chain_hits": 837,
        "theorem_status": "OBSTRUCTED",
        "frontier_size": 16,
    }
    assert payload["authority_path"] == EXPECTED_PASS191_AUTHORITY_PATH


def test_inherited_frontier_closes_only_through_singleton_vm81_authority() -> None:
    payload = _pass191_evidence()
    hydration = payload["vm81_hash216_frontier_hydration"]
    assert all(hydration["checks"].values())
    assert hydration["candidate_execution"]["classification"] == "HHS_PASS_175_CANDIDATES_VM81_COMMITTED"
    assert hydration["candidate_execution"]["singleton_vm81_commit_authority"] is True
    assert hydration["deterministic_replay"]["classification"] == "HHS_PASS_175_DETERMINISTIC_REPLAY_VERIFIED"
    assert hydration["runtime_status_after"]["hash72_commit_streams"] == 1


def test_inherited_retained_candidates_are_exact_chain_certificates() -> None:
    payload = _pass191_evidence()
    certificates = payload["unified_manifold_epoch"]["deep_candidate_certificates"]
    assert len(certificates) == 16
    for certificate in certificates:
        assert certificate["chain_decision"] == {
            "proposition": "t^3-t = Delta = m^2-m",
            "scope": "EXACT_CONTEXT_CANDIDATE",
            "status": "PROVED",
        }
        assert certificate["residuals"]["cubic_minus_delta"] == 0
        assert certificate["residuals"]["delta_minus_idempotent"] == 0
        assert all(certificate["checks"].values())


def test_inherited_pass191_completion_receipt_matches_kernel_authority_path() -> None:
    receipt = json.loads(PASS191_COMPLETION.read_text(encoding="utf-8"))
    assert receipt["classification"] == "HHS_PASS_191_UNIFIED_MANIFOLD_VM81_PROOF_SEARCH_EXECUTED"
    assert receipt["authority_path"] == EXPECTED_PASS191_AUTHORITY_PATH
    assert receipt["contextual_cardinality"] == 51_648_192
    assert receipt["visited"] == 51_648_192
    assert receipt["exact_chain_hits"] == 837
    assert receipt["frontier_size"] == 16
    assert receipt["manifold_checksum_fnv1a64"] == "5f89e7e466d337ed"


def test_tampered_inherited_manifold_state_is_rejected_by_inherited_verifier() -> None:
    payload = _pass191_evidence()
    tampered = copy.deepcopy(payload)
    tampered["unified_manifold_epoch"]["deep_candidate_certificates"][0]["residuals"][
        "cubic_minus_delta"
    ] = 1
    with pytest.raises(AssertionError):
        verify_integrated_manifold_search(tampered)

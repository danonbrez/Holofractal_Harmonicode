from __future__ import annotations

import copy
import hashlib
from fractions import Fraction
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass219b_global_zero_sum_closure_proof_v1 import (
    HYDRATION_STATE_COUNT,
    PARENT_MONOLITHIC_SHA256,
    PHASE_PROJECTED_STATE_COUNT,
    PHASE_QUANTIZATION_OBJECT,
    PHASE_QUANTIZATION_SHA256,
    GlobalZeroSumClosureError,
    prove_global_zero_sum_closure,
    verify_global_zero_sum_closure,
)

ROOT = Path(__file__).resolve().parents[2]
EXTENSION = ROOT / "contracts" / "pass219" / "PASS_219_GLOBAL_RECURSIVE_ZERO_SUM_CLOSURE_1_16_0.harmonicode"
MONOLITHIC = ROOT / "contracts" / "pass219" / "PASS_219_MONOLITHIC_UQCEL_RESIDUAL_BOUNDARY_1_15_0.tex"
UQCEL_HEADER = ROOT / "hhs_runtime" / "include" / "hhs_runtime_uqcel_1_8.h"
UQCEL_VALIDATOR = ROOT / "hhs_runtime" / "c" / "hhs_runtime_uqcel_1_8_validate.inc"
UQCEL_RECEIPT = ROOT / "hhs_runtime" / "c" / "hhs_runtime_uqcel_1_8_receipt.inc"
I6_HEADER = ROOT / "hhs_runtime" / "include" / "hhs_pass219b_global_zero_sum_closure_1_0.h"
I6_RUNTIME = ROOT / "hhs_runtime" / "c" / "hhs_pass219b_global_zero_sum_closure_1_0.inc"
EXPECTED_EXTENSION_SHA256 = "28d89e625af38f7fbc2e2df61050043a6716c803458f2b5e6912a62f384ceb2d"


def _f(fd: dict[str, int]) -> Fraction:
    return Fraction(fd["numerator"], fd["denominator"])


def test_source_objects_and_append_only_boundary_are_frozen() -> None:
    raw = EXTENSION.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_EXTENSION_SHA256
    text = raw.decode("utf-8")
    assert "NUMERATOR_OBJECT=N" in text
    assert "DENOMINATOR_OBJECT=D" in text
    assert "N/D⁴=D⁴" in text
    assert "projection_id=PI-UCE-N-D-HYDRATION-I6-v1" in text
    assert "UQCEL_V1_ABI=UNCHANGED" in text
    assert "UQCEL_FULL_SYMBOLIC_V1=UNSUPPORTED_DOMAIN" in text
    assert "GLOBAL_LEGACY_INTERPOSITION=NO" in text
    assert "I6 SHALL NOT modify, resize, shadow, replace, or reinterpret" in text
    assert hashlib.sha256(MONOLITHIC.read_bytes()).hexdigest() == PARENT_MONOLITHIC_SHA256
    assert hashlib.sha256(PHASE_QUANTIZATION_OBJECT.encode("utf-8")).hexdigest() == PHASE_QUANTIZATION_SHA256


@pytest.mark.parametrize("P", [4, 5, 6, 8, 10, 100, 1024, Fraction(9, 2), Fraction(-7, 3)])
def test_exact_zero_sum_closure_family(P) -> None:
    proof = prove_global_zero_sum_closure(center_P=P)
    verify = verify_global_zero_sum_closure(proof)
    assert verify["status"] == "ADDITIVE_GLOBAL_RELATION_BRIDGE_VALIDATED"
    assert verify["legacy_full_symbolic_v1_preserved_unsupported"] is True

    family = proof["closure_family"]
    assert _f(family["delta"]) == 1
    assert _f(family["p"]) == Fraction(P) - 1
    assert _f(family["q"]) == Fraction(P) + 1
    assert _f(family["P_squared_minus_pq"]) == 1
    assert _f(family["xy_projection"]) == 1
    assert _f(family["zw_projection"]) == 1
    assert _f(family["x_plus_y_plus_z_plus_w"]) == 0
    assert family["phase_carrier_sum_basis_1_I"] == [0, 0]
    assert _f(family["membrane_residue"]) == 1

    phase = proof["phase_quantization_binding"]
    assert phase["recursive_relation"] == "N/D^4=D^4"
    assert phase["structural_projection_registered"] is True
    assert phase["scalar_cancellation_allowed"] is False

    hydration = proof["hydration_bridge"]
    assert hydration["lo_shu_sudoku_qudit_bound"] is True
    assert hydration["hydration_state_count"] == HYDRATION_STATE_COUNT == 51_648_192
    assert hydration["phase_projected_state_count"] == PHASE_PROJECTED_STATE_COUNT == 4_183_503_552

    authority = proof["projection_authority"]
    assert authority["i6_projection_is_additive"] is True
    assert authority["uqcel_integer_symmetric_reused_as_subprojection"] is True
    assert authority["legacy_full_symbolic_v1_preserved_unsupported"] is True
    assert authority["projection_equality_is_not_native_identity"] is True
    assert authority["canonical_mutation_authority"] is False


def test_zero_center_is_excluded_by_inherited_four_phase_normalization_domain() -> None:
    with pytest.raises(Exception):
        prove_global_zero_sum_closure(center_P=0)


def _assert_tamper_rejected(path: str, value) -> None:
    proof = prove_global_zero_sum_closure(center_P=4)
    bad = copy.deepcopy(proof)
    obj = bad
    keys = path.split(".")
    for key in keys[:-1]:
        obj = obj[key]
    obj[keys[-1]] = value
    bad_without_root = copy.deepcopy(bad)
    bad_without_root.pop("proof_root_hash72", None)
    from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
    bad["proof_root_hash72"] = _hash("hhs_pass219b_global_relation_bridge_v3", bad_without_root)
    with pytest.raises(GlobalZeroSumClosureError):
        verify_global_zero_sum_closure(bad)


def test_tampered_center_sum_rejected_after_rehash() -> None:
    _assert_tamper_rejected("closure_family.x_plus_y_plus_z_plus_w", {"numerator": 1, "denominator": 1})


def test_tampered_p_rejected_after_rehash_and_inherited_replay() -> None:
    _assert_tamper_rejected("closure_family.p", {"numerator": 9, "denominator": 1})


def test_tampered_phase_identity_rejected_after_rehash() -> None:
    _assert_tamper_rejected("phase_quantization_binding.source_sha256", "00" * 32)


def test_scalar_cancellation_cannot_be_introduced() -> None:
    _assert_tamper_rejected("phase_quantization_binding.scalar_cancellation_allowed", True)


def test_projection_cannot_gain_mutation_authority() -> None:
    _assert_tamper_rejected("projection_authority.canonical_mutation_authority", True)


def test_projection_cannot_claim_native_identity() -> None:
    _assert_tamper_rejected("projection_authority.projection_equality_is_not_native_identity", False)


def test_runtime_bridge_is_additive_and_has_no_commit_surface() -> None:
    header = I6_HEADER.read_text(encoding="utf-8")
    runtime = I6_RUNTIME.read_text(encoding="utf-8")

    assert "HHSExactPass219BGlobalRelationInputV1" in header
    assert "HHSExactPass219BGlobalRelationHydrationWitnessV1" in header
    assert "hhs_exact_pass219b_global_relation_hydration_verify" in header
    assert "hhs_exact_pass219b_global_relation_hydration_admit" not in header

    for inherited_call in (
        "hhs_exact_uqcel_validate",
        "hhs_exact_pass219_native_phase_witness",
        "hhs_exact_pass219_coordinate_from_pass189",
        "hhs_exact_pass219_coordinate_to_pass189",
        "hhs_exact_pass219_trinary_phase_gate",
        "hhs_exact_pass219b_phase_cell",
        "hhs_exact_pass219b_phase_locality_plan",
        "hhs_exact_pass219b_phase_locality_verify_realization",
    ):
        assert inherited_call in runtime

    assert "hhs_exact_vm81_admit_uqcel" not in runtime
    assert "hhs_exact_pass219_rna_admit_composed" not in runtime
    assert "frame_committed" not in header
    assert "canonical_mutation_authority" in header


def test_inherited_uqcel_v1_full_symbolic_boundary_remains_intact() -> None:
    header = UQCEL_HEADER.read_text(encoding="utf-8")
    validator = UQCEL_VALIDATOR.read_text(encoding="utf-8")
    receipt = UQCEL_RECEIPT.read_text(encoding="utf-8")

    assert "HHS_UQCEL_CONSTRAINT_CORE_REQUIRED UINT64_C(0x03FF)" in header
    assert "HHS_UQCEL_RESIDUAL_FULL_SOURCE UINT64_C(0x001F)" in header
    assert "HHS_UQCEL_CONSTRAINT_GLOBAL_ZERO_SUM_CLOSURE" not in header
    assert "HHS_UQCEL_CONSTRAINT_GLOBAL_RELATION_BRIDGE" not in header

    guard = "if (input->profile == HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1)"
    assert guard in validator
    assert "HHS_EXACT_UQCEL_DECISION_UNSUPPORTED_DOMAIN" in validator
    assert "HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN" in validator
    assert "The aggregate monolithic residual remains set." in validator
    compatibility_ab_check = validator.index("hhs_exact_big_equal_view_buffer(&input->A, &p_squared)")
    assert validator.index(guard) < compatibility_ab_check

    assert "HHSExactStatus hhs_exact_vm81_admit_uqcel" in receipt
    assert "hhs_exact_vm81_finalize_uqcel" not in receipt

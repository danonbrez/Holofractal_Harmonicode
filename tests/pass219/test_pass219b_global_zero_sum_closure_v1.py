from __future__ import annotations

import copy
import hashlib
from fractions import Fraction
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass219b_global_zero_sum_closure_proof_v1 import (
    CLOSURE_EXTENSION_SHA256,
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


def _f(fd: dict[str, int]) -> Fraction:
    return Fraction(fd["numerator"], fd["denominator"])


def test_source_objects_are_byte_frozen() -> None:
    raw = EXTENSION.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CLOSURE_EXTENSION_SHA256
    text = raw.decode("utf-8")
    assert "NUMERATOR_OBJECT=N" in text
    assert "DENOMINATOR_OBJECT=D" in text
    assert "N/D⁴=D⁴" in text
    assert "1=u⁷²" in text
    assert "x+y+z+w=0" in text
    assert "Lo Shu/Sudoku qudit" in text
    assert "VM81 cell81" in text
    assert "SHALL NOT remain UNSUPPORTED_DOMAIN" in text
    assert hashlib.sha256(MONOLITHIC.read_bytes()).hexdigest() == PARENT_MONOLITHIC_SHA256
    assert hashlib.sha256(PHASE_QUANTIZATION_OBJECT.encode("utf-8")).hexdigest() == PHASE_QUANTIZATION_SHA256


@pytest.mark.parametrize("P", [4, 5, 6, 8, 10, 100, 1024, Fraction(9, 2), Fraction(-7, 3)])
def test_exact_zero_sum_closure_family(P) -> None:
    proof = prove_global_zero_sum_closure(center_P=P)
    verify = verify_global_zero_sum_closure(proof)
    assert verify["status"] == "GLOBAL_RELATION_BRIDGE_VALIDATED"
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
    assert phase["recursive_relation_structurally_proven"] is True
    assert phase["scalar_cancellation_allowed"] is False

    hydration = proof["hydration_bridge"]
    assert hydration["lo_shu_sudoku_qudit_bound"] is True
    assert hydration["cell_count81"] == 81
    assert hydration["lo_shu_group_count41"] == 41
    assert hydration["trit_count3"] == 3
    assert hydration["vm5184_slot_count"] == 5184
    assert hydration["hydration_state_count"] == HYDRATION_STATE_COUNT == 51_648_192
    assert hydration["phase_projected_state_count"] == PHASE_PROJECTED_STATE_COUNT == 4_183_503_552
    assert proof["global_enforcement"]["global_relation_bridge_proven"] is True


def test_zero_center_is_excluded_by_inherited_four_phase_normalization_domain() -> None:
    with pytest.raises(Exception):
        prove_global_zero_sum_closure(center_P=0)


def test_tampered_center_sum_proof_rejected() -> None:
    proof = prove_global_zero_sum_closure(center_P=4)
    bad = copy.deepcopy(proof)
    bad["closure_family"]["x_plus_y_plus_z_plus_w"] = {"numerator": 1, "denominator": 1}
    with pytest.raises(GlobalZeroSumClosureError):
        verify_global_zero_sum_closure(bad)


def test_tampered_phase_sum_proof_rejected() -> None:
    proof = prove_global_zero_sum_closure(center_P=4)
    bad = copy.deepcopy(proof)
    bad["closure_family"]["phase_carrier_sum_basis_1_I"] = [1, 0]
    with pytest.raises(GlobalZeroSumClosureError):
        verify_global_zero_sum_closure(bad)


def test_recursive_relation_cannot_be_rewritten_as_scalar_cancellation() -> None:
    proof = prove_global_zero_sum_closure(center_P=4)
    bad = copy.deepcopy(proof)
    bad["phase_quantization_binding"]["scalar_cancellation_allowed"] = True
    with pytest.raises(GlobalZeroSumClosureError):
        verify_global_zero_sum_closure(bad)


def test_phase_quantization_identity_is_required() -> None:
    proof = prove_global_zero_sum_closure(center_P=4)
    bad = copy.deepcopy(proof)
    bad["phase_quantization_binding"]["source_sha256"] = "00" * 32
    with pytest.raises(GlobalZeroSumClosureError):
        verify_global_zero_sum_closure(bad)


def test_hydration_bridge_is_required() -> None:
    proof = prove_global_zero_sum_closure(center_P=4)
    bad = copy.deepcopy(proof)
    bad["hydration_bridge"]["vm5184_slot_count"] = 5183
    with pytest.raises(GlobalZeroSumClosureError):
        verify_global_zero_sum_closure(bad)


def test_full_symbolic_uqcel_is_structural_bridge_not_unsupported_residual() -> None:
    header = UQCEL_HEADER.read_text(encoding="utf-8")
    validator = UQCEL_VALIDATOR.read_text(encoding="utf-8")
    assert "HHS_UQCEL_CONSTRAINT_GLOBAL_ZERO_SUM_CLOSURE" in header
    assert "HHS_UQCEL_CONSTRAINT_CENTER_DELTA_SYMMETRY" in header
    assert "HHS_UQCEL_CONSTRAINT_GLOBAL_RELATION_BRIDGE" in header
    assert "HHS_UQCEL_CONSTRAINT_FULL_SYMBOLIC_REQUIRED UINT64_C(0x1F9F)" in header
    assert "hhs_exact_pass219b_global_tensor_source_sha256" in validator
    assert "out_admission->residual_mask = 0U;" in validator
    assert "HHS_EXACT_UQCEL_DECISION_UNSUPPORTED_DOMAIN" not in validator
    assert "HHS_UQCEL_CONSTRAINT_AB_SYMMETRIC" in validator
    full_start = validator.index("if (full_symbolic) {")
    bridge = validator.rindex("HHS_UQCEL_CONSTRAINT_GLOBAL_RELATION_BRIDGE")
    admit = validator.rindex("HHS_EXACT_UQCEL_DECISION_ADMIT")
    assert full_start < bridge < admit
